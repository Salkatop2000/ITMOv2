#!/usr/bin/env python3
"""
MCP server exposing a single tool `task_count` over stdio using the official `mcp` package.

Params:
- status: one of {"open","done","all"} (default "all")
- path: JSON file path (default "data/tasks.json")

Returns structured JSON content: {"count": int, "status": str}
Raises MCPError for invalid status or file errors, so the host receives a protocol error.
"""
from __future__ import annotations

import json
import os
from typing import List, Dict, Any

from mcp import MCPError
from mcp.types import INVALID_PARAMS, INTERNAL_ERROR
from mcp.server import MCPServer


mcp = MCPServer("Task CLI MCP", log_level="INFO")


def _load_tasks(path: str) -> List[Dict[str, Any]]:
    """Load tasks from a JSON file. Expect a list of objects with `status` field.
    Raise MCPError on IO/parse errors.
    """
    if not os.path.exists(path):
        raise MCPError(code=INVALID_PARAMS, message=f"Tasks file not found: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise MCPError(code=INVALID_PARAMS, message=f"Invalid JSON in tasks file: {path}") from e
    except OSError as e:
        raise MCPError(code=INTERNAL_ERROR, message=f"Cannot read tasks file: {path}") from e
    if not isinstance(data, list):
        raise MCPError(code=INVALID_PARAMS, message=f"Tasks file must be a JSON array: {path}")
    return data


@mcp.tool()
def task_count(status: str = "all", path: str = "data/tasks.json") -> dict:
    """Подсчитать количество задач по статусу.

    status: open|done|all (по умолчанию all)
    path: путь к JSON-файлу задач (по умолчанию data/tasks.json)
    """
    valid_status = {"open", "done", "all"}
    if status not in valid_status:
        raise MCPError(code=INVALID_PARAMS, message=f"Invalid status: {status}")

    tasks = _load_tasks(path)

    def is_done(t: Dict[str, Any]) -> bool:
        return str(t.get("status", "")).lower() == "done"

    if status == "all":
        count = len(tasks)
    elif status == "done":
        count = sum(1 for t in tasks if is_done(t))
    else:  # status == "open"
        count = sum(1 for t in tasks if not is_done(t))

    return {"count": int(count), "status": status}


if __name__ == "__main__":
    # Serve over stdio
    mcp.run()
