import json
import os
import subprocess
import sys
from pathlib import Path


CLI = [sys.executable, str(Path(__file__).parents[1] / "src" / "task_cli.py")]


def run_cli(args, data_file):
    env = os.environ.copy()
    cmd = CLI + ["--data", str(data_file)] + args
    return subprocess.run(cmd, capture_output=True, text=True)


def read_tasks(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_add_task_assigns_id_and_open(tmp_path):
    data = tmp_path / "tasks.json"
    r = run_cli(["add", "Prepare report"], data)
    assert r.returncode == 0, r.stderr
    created = json.loads(r.stdout)
    assert created["id"] == 1
    assert created["title"] == "Prepare report"
    assert created["status"] == "open"
    # persisted
    tasks = read_tasks(data)
    assert tasks == [created]


def test_auto_increment_id(tmp_path):
    data = tmp_path / "tasks.json"
    run_cli(["add", "First"], data)
    run_cli(["add", "Second"], data)
    tasks = read_tasks(data)
    ids = [t["id"] for t in tasks]
    assert ids == [1, 2]


def test_list_all_and_filter_by_status(tmp_path):
    data = tmp_path / "tasks.json"
    run_cli(["add", "A"], data)
    run_cli(["add", "B"], data)
    # mark first done
    r = run_cli(["done", "1"], data)
    assert r.returncode == 0
    # list all
    r_all = run_cli(["list"], data)
    out_all = r_all.stdout.strip().splitlines()
    assert len(out_all) == 2
    # list open
    r_open = run_cli(["list", "--status", "open"], data)
    out_open = r_open.stdout.strip().splitlines()
    assert len(out_open) == 1
    assert "open" in out_open[0]
    # list done
    r_done = run_cli(["list", "--status", "done"], data)
    out_done = r_done.stdout.strip().splitlines()
    assert len(out_done) == 1
    assert "done" in out_done[0]


def test_done_existing_task(tmp_path):
    data = tmp_path / "tasks.json"
    run_cli(["add", "Task"], data)
    r = run_cli(["done", "1"], data)
    assert r.returncode == 0
    assert "marked as done" in r.stdout
    tasks = read_tasks(data)
    assert tasks[0]["status"] == "done"


def test_done_nonexistent_task(tmp_path):
    data = tmp_path / "tasks.json"
    r = run_cli(["done", "999"], data)
    assert r.returncode != 0
    assert "not found" in r.stderr


def test_done_already_done(tmp_path):
    data = tmp_path / "tasks.json"
    run_cli(["add", "Task"], data)
    assert run_cli(["done", "1"], data).returncode == 0
    r = run_cli(["done", "1"], data)
    assert r.returncode == 0
    assert "already done" in r.stdout


def test_clear_done_and_all(tmp_path):
    data = tmp_path / "tasks.json"
    run_cli(["add", "A"], data)
    run_cli(["add", "B"], data)
    # mark one as done
    assert run_cli(["done", "1"], data).returncode == 0
    # clear done only
    r_clear_done = run_cli(["clear", "--status", "done"], data)
    assert r_clear_done.returncode == 0
    tasks = read_tasks(data)
    assert len(tasks) == 1
    assert tasks[0]["status"] == "open"
    # clear all
    r_clear_all = run_cli(["clear", "--status", "all"], data)
    assert r_clear_all.returncode == 0
    tasks = read_tasks(data)
    assert tasks == []
