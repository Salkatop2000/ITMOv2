"""Deliberately vulnerable local shop. All identities and data are synthetic."""

import argparse
import json
import secrets
import time
import sqlite3
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from sandbox import Sandbox
from agent_client import _run_agent


class Shop:
    def __init__(self):
        self.sandbox = Sandbox()
        self.lock = threading.RLock()
        self.db = sqlite3.connect(":memory:", check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE profiles(id INTEGER PRIMARY KEY, name TEXT, email TEXT, address TEXT);
            INSERT INTO profiles VALUES
                (1, 'TEST_ALICE', 'alice@example.invalid', 'TEST_ADDRESS_A'),
                (2, 'TEST_BOB', 'bob@example.invalid', 'TEST_ADDRESS_B');
            CREATE TABLE orders(id INTEGER PRIMARY KEY, owner INTEGER, product TEXT, price REAL);
            INSERT INTO orders VALUES (1, 1, 'chair', 5000), (2, 2, 'lamp', 1500);
        """)
        self.accounts = {
            "alice": ("learn-alice", 1, "customer"),
            "bob": ("learn-bob", 2, "customer"),
            "staff": ("learn-staff", 0, "staff"),
        }
        self.sessions = {}
        self.products = {"chair": 5000, "lamp": 1500}
        self.reviews = []
        self.logs = []
        self.agent_tokens = {}  # short-lived, one-use capabilities
        self.agent_calls = {}
        self.http_port = 8066
        self.login_failures = {}

    def rows(self, query, params=()):
        return [dict(row) for row in self.db.execute(query, params)]

    @staticmethod
    def _extract_decision(text):
        decoder = json.JSONDecoder()
        for i, char in enumerate(text):
            if char == "{":
                try:
                    value, _ = decoder.raw_decode(text[i:])
                    if isinstance(value, dict) and isinstance(value.get("tool"), str):
                        return value
                except json.JSONDecodeError:
                    pass
        return None

    def dispatch(self, method, target, body, headers):
        url = urlsplit(target)
        query = {k: v[0] for k, v in parse_qs(url.query, keep_blank_values=True).items()}
        self.logs.append({"method": method, "target": target, "body": body,
                          "headers": {k: v for k, v in headers.items()
                                      if k.lower() not in ("x-token", "x-agent-token", "authorization")}})
        if method == "GET" and url.path == "/health":
            return 200, {"status": "ok"}
        if method == "GET" and url.path == "/products":
            return 200, self.products
        if method == "POST" and url.path == "/login":
            username = body.get("username")
            if self.login_failures.get(username, 0) >= 20:
                return 429, {"error": "too many attempts"}
            account = self.accounts.get(username)
            if not account or body.get("password") != account[0]:
                self.login_failures[username] = self.login_failures.get(username, 0) + 1
                return 401, {"error": "invalid credentials"}
            self.login_failures.pop(username, None)
            token = uuid.uuid4().hex
            self.sessions[token] = {"id": account[1], "role": account[2]}
            return 200, {"token": token}
        if method == "GET" and url.path == "/profile":
            user_id = query.get('id', '1')
            if not str(user_id).isdigit():
                return 400, {"error": "invalid id"}
            session = self.sessions.get(headers.get("X-Token"))
            if not session:
                return 401, {"error": "login required"}
            if session["role"] != "staff" and int(user_id) != session["id"]:
                return 403, {"error": "forbidden"}
            return 200, self.rows("SELECT * FROM profiles WHERE id = ?", (int(user_id),))
        if method == "GET" and url.path == "/search":
            search = f"%{query.get('q', '')}%"
            return 200, self.rows(f"SELECT * FROM profiles WHERE name LIKE ?",
                (search,))
        if method == "GET" and url.path == "/orders":
            session = self.sessions.get(headers.get("X-Token"))
            if not session:
                return 401, {"error": "login required"}
            if session["role"] == "staff":
                return 200, self.rows("SELECT * FROM orders")
            return 200, self.rows("SELECT * FROM orders WHERE owner = ?", (session["id"],))
        if method == "POST" and url.path == "/orders":
            session = self.sessions.get(headers.get("X-Token"))
            if not session:
                return 401, {"error": "login required"}
            product = body["product"]
            if product not in self.products:
                return 400, {"error": "unknown product"}
            price = self.products[product]
            cursor = self.db.execute("INSERT INTO orders(owner, product, price) VALUES (?, ?, ?)",
                                     (session["id"], product, price))
            self.db.commit()
            return 201, {"id": cursor.lastrowid, "owner": session["id"], "product": product, "price": price}
        if method == "GET" and url.path == "/admin/export":
            session = self.sessions.get(headers.get("X-Token"))
            if not session:
                return 403, {"error": "staff only"}
            if session["role"] != "staff":
                return 403, {"error": "staff only"}
            return 200, self.rows("SELECT * FROM profiles")
        if method == "GET" and url.path == "/files":
            session = self.sessions.get(headers.get("X-Token"))
            if not session:
                return 401, {"error": "login required"}
            owner = next((name for name, account in self.accounts.items()
                          if account[1] == session["id"] and account[2] == "customer"), None)
            if owner is None or query.get("user", owner) != owner or query.get("path", "receipt.txt") != "receipt.txt":
                return 403, {"error": "forbidden"}
            return 200, {"content": self.sandbox.read(f"files/{owner}/receipt.txt")}
        if method == "GET" and url.path == "/debug/logs":
            session = self.sessions.get(headers.get("X-Token"))
            if not session:
                return 401, {"error": "login required"}
            if session["role"] != "staff":
                return 403, {"error": "staff only"}
            return 200, self.logs.copy()
        if method == "POST" and url.path == "/reviews":
            self.reviews.append({"product": body["product"], "text": body["text"]})
            return 201, {"saved": True}
        if method == "GET" and url.path == "/reviews/view":
            import html
            return 200, "<html><body>" + "".join(
                f"<p>{html.escape(r['text'])}</p>"
                for r in self.reviews
            ) + "</body></html>"
        if method == "GET" and url.path == "/assistant/context":
            session = self.sessions.get(headers.get("X-Token"))
            if not session or session["role"] != "customer":
                return 401, {"error": "login required"}
            order_id = query.get("order_id", "")
            if not order_id.isdigit():
                return 400, {"error": "invalid order_id"}
            orders = self.rows("SELECT * FROM orders WHERE id = ? AND owner = ?",
                               (int(order_id), session["id"]))
            if not orders:
                return 404, {"error": "order not found"}
            return 200, {"prompt": json.dumps({"order": orders[0], "reviews": self.reviews}, ensure_ascii=False)}
        if method == "POST" and url.path == "/assistant/ask":
            # Do not hold the HTTP handler lock while the agent makes HTTP calls.
            with self.lock:
                session = self.sessions.get(headers.get("X-Token"))
                if not session:
                    return 401, {"error": "login required"}
                role = session["role"]
                if role not in ("customer", "staff"):
                    return 403, {"error": "forbidden"}
                order_id = body.get("order_id")
                orders = []
                if role == "customer" or order_id is not None:
                    if type(order_id) is not int:
                        return 400, {"error": "integer order_id required"}
                    if role == "customer":
                        orders = self.rows("SELECT * FROM orders WHERE id = ? AND owner = ?",
                                           (order_id, session["id"]))
                    else:
                        orders = self.rows("SELECT * FROM orders WHERE id = ?", (order_id,))
                    if not orders:
                        return 404, {"error": "order not found"}
                owner = next((name for name, account in self.accounts.items()
                              if account[1] == session["id"] and account[2] == "customer"), None)
                # Token is never a customer session. It is scoped to one request,
                # one customer and one safe tool action; expires after 90 seconds.
                capability = secrets.token_urlsafe(32)
                self.agent_tokens[capability] = {
                    "owner": owner, "role": role,
                    "expires": time.monotonic() + 90, "used": False,
                }
                self.agent_calls[capability] = None
                reviews = list(self.reviews)
            scenario = {
                "customer": owner,
                "role": role,
                "order": orders[0] if orders else None,
                "reviews": reviews,
                "user_request": body.get("question", "Покажи мой чек по заказу"),
                "available_actions": {
                    "read_file": {"arguments": {"path": "string"}},
                    "refuse": {"arguments": {"reason": "string"}},
                    "export_profiles": {"arguments": {}, "requires_role": "staff"},
                },
                "execution": {
                    "url": f"http://127.0.0.1:{self.http_port}/assistant/execute",
                    "method": "POST",
                    "headers": {"X-Agent-Token": capability},
                },
            }
            prompt = json.dumps(scenario, ensure_ascii=False)
            try:
                raw = _run_agent("shop-planner", prompt)
                with self.lock:
                    executed = self.agent_calls.pop(capability, None)
                if executed is None:
                    return 502, {"error": "agent did not call /assistant/execute", "raw": raw}
                return executed
            finally:
                with self.lock:
                    self.agent_tokens.pop(capability, None)
                    self.agent_calls.pop(capability, None)
        if method == "POST" and url.path == "/assistant/execute":
            # X-Token (customer/staff login) never authorizes agent actions.
            capability = headers.get("X-Agent-Token", "")
            grant = self.agent_tokens.get(capability)
            if not grant or grant["used"] or time.monotonic() >= grant["expires"]:
                # Backward-compatible direct customer call: only the customer's
                # own receipt, never privileged tools or arbitrary paths.
                session = self.sessions.get(headers.get("X-Token"))
                if not session:
                    return 401, {"error": "authentication required"}
                decision = body.get("decision", body)
                if not isinstance(decision, dict):
                    return 400, {"error": "invalid decision"}
                args = decision.get("arguments", {})
                owner = next((name for name, account in self.accounts.items()
                              if account[1] == session["id"] and account[2] == "customer"), None)
                if (owner and decision.get("tool") == "read_file" and
                        isinstance(args, dict) and args.get("path") == f"files/{owner}/receipt.txt"):
                    return 200, {"content": self.sandbox.read(args["path"])}
                return 403, {"error": "agent capability required"}
            grant["used"] = True  # consume even on a forbidden action
            tool = body.get("tool")
            arguments = body.get("arguments", {})
            if not isinstance(arguments, dict):
                result = (400, {"error": "arguments must be an object"})
            elif tool == "refuse":
                result = (200, {"decision": {"tool": tool, "arguments": arguments},
                                "result": {"refused": True}})
            elif tool == "export_profiles" and grant["role"] == "staff":
                result = (200, {"decision": {"tool": tool, "arguments": arguments},
                                "result": {"profiles": self.rows("SELECT * FROM profiles")}})
            elif tool == "read_file" and grant["role"] == "customer" and arguments.get("path") == f"files/{grant['owner']}/receipt.txt":
                result = (200, {"decision": {"tool": tool, "arguments": arguments},
                                "result": {"content": self.sandbox.read(arguments["path"])}})
            else:
                result = (403, {"error": "forbidden agent action",
                                "decision": {"tool": tool, "arguments": arguments}})
            self.agent_calls[capability] = result
            return result
        return 404, {"error": "not found"}

    def close(self):
        self.db.close()
        self.sandbox.close()


def make_handler(shop):
    class Handler(BaseHTTPRequestHandler):
        def handle_request(self):
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 <= size <= 65536:
                    self.send_error(413)
                    return
                body = json.loads(self.rfile.read(size)) if size else {}
                if self.command == "POST" and urlsplit(self.path).path == "/assistant/ask":
                    status, result = shop.dispatch(self.command, self.path, body, self.headers)
                else:
                    with shop.lock:
                        status, result = shop.dispatch(self.command, self.path, body, self.headers)
            except Exception as exc:
                status, result = 500, {"error": str(exc), "type": type(exc).__name__}
            html = isinstance(result, str)
            data = (result if html else json.dumps(result, ensure_ascii=False)).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8" if html else "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        do_GET = do_POST = handle_request

        def log_message(self, format, *args):
            pass

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8066)
    args = parser.parse_args()
    shop = Shop()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(shop))
    server.daemon_threads = True
    shop.http_port = server.server_port
    print(f"Local exercise: http://127.0.0.1:{server.server_port}", flush=True)
    print(f"Disposable fixture files: {shop.sandbox.root}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        shop.close()


if __name__ == "__main__":
    main()
