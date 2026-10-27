#!/usr/bin/env python3
"""
Minimal Task Tracker CLI.

Responsibilities split in a single file:
- JSON storage helpers
- Task operations
- CLI parsing and command handling

Data file default: <project_root>/data/tasks.json
Can be overridden via --data argument for tests and ad-hoc runs.
"""
import argparse
import json
import os
import sys
from typing import List, Dict, Optional


# Determine project root (parent of this file's directory) and default data file
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DATA_FILE = os.path.join(ROOT_DIR, "data", "tasks.json")


# ---------------------
# JSON storage helpers
# ---------------------
def _ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


def load_tasks(path: str) -> List[Dict]:
    """Load tasks list from JSON file. Create file with [] if missing.

    Returns an in-memory list of tasks (each a dict with id, title, status).
    """
    if not os.path.exists(path):
        _ensure_parent_dir(path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure it's a list; if not, reset to []
            if not isinstance(data, list):
                return []
            return data
    except json.JSONDecodeError:
        # Corrupted JSON -> treat as empty for robustness in demo project
        return []


def save_tasks(path: str, tasks: List[Dict]) -> None:
    _ensure_parent_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


# ---------------------
# Task operations
# ---------------------
def _next_id(tasks: List[Dict]) -> int:
    if not tasks:
        return 1
    return max((t.get("id", 0) for t in tasks), default=0) + 1


def add_task(path: str, title: str) -> Dict:
    tasks = load_tasks(path)
    task = {"id": _next_id(tasks), "title": title, "status": "open"}
    tasks.append(task)
    save_tasks(path, tasks)
    return task


def list_tasks(path: str, status: Optional[str]) -> List[Dict]:
    tasks = load_tasks(path)
    if status and status in {"open", "done"}:
        tasks = [t for t in tasks if t.get("status") == status]
    # Sort by id for stable listing
    tasks.sort(key=lambda t: t.get("id", 0))
    return tasks


def mark_done(path: str, task_id: int) -> str:
    """Mark task as done.

    Returns a status string:
    - "updated": changed from open to done
    - "already": task existed and was already done
    - raises KeyError if not found
    """
    tasks = load_tasks(path)
    for t in tasks:
        if t.get("id") == task_id:
            if t.get("status") == "done":
                return "already"
            t["status"] = "done"
            save_tasks(path, tasks)
            return "updated"
    raise KeyError(task_id)


def clear_tasks(path: str, status: str) -> int:
    """Clear tasks by status. Returns number of removed tasks.

    status can be: "done", "open", or "all".
    """
    tasks = load_tasks(path)
    before = len(tasks)
    if status == "all":
        tasks = []
    else:
        tasks = [t for t in tasks if t.get("status") != status]
    removed = before - len(tasks)
    save_tasks(path, tasks)
    return removed


# ---------------------
# CLI parsing / handling
# ---------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Task Tracker CLI")
    parser.add_argument(
        "--data",
        dest="data_file",
        default=DEFAULT_DATA_FILE,
        help="Path to tasks JSON file (default: %(default)s)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # add command
    p_add = subparsers.add_parser("add", help="Add a new task")
    p_add.add_argument("title", help="Task title")

    # list command
    p_list = subparsers.add_parser("list", help="List tasks")
    p_list.add_argument(
        "--status",
        choices=["open", "done", "all"],
        default="all",
        help="Filter by status",
    )

    # done command
    p_done = subparsers.add_parser("done", help="Mark a task as done")
    p_done.add_argument("id", type=int, help="Task id")

    # clear command
    p_clear = subparsers.add_parser("clear", help="Clear tasks by status")
    p_clear.add_argument(
        "--status",
        choices=["open", "done", "all"],
        default="done",
        help="Which tasks to remove (default: done)",
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    data_file = args.data_file

    if args.command == "add":
        task = add_task(data_file, args.title)
        # Print the created task as JSON on a single line
        print(json.dumps(task, ensure_ascii=False))
        return 0

    if args.command == "list":
        status = None if args.status == "all" else args.status
        tasks = list_tasks(data_file, status)
        if not tasks:
            print("No tasks.")
            return 0
        for t in tasks:
            print(f"{t['id']:>3} | {t['status']:<4} | {t['title']}")
        return 0

    if args.command == "done":
        try:
            result = mark_done(data_file, args.id)
        except KeyError:
            print(f"Task {args.id} not found", file=sys.stderr)
            return 1
        if result == "already":
            print(f"Task {args.id} is already done")
            return 0
        print(f"Task {args.id} marked as done")
        return 0

    if args.command == "clear":
        removed = clear_tasks(data_file, args.status)
        print(f"Removed {removed} task(s)")
        return 0

    # Should not reach here
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
