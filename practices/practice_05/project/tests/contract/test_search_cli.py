import subprocess
import sys
from pathlib import Path
import json


CLI = [sys.executable, str(Path(__file__).parents[2] / "src" / "task_cli.py")]


def run_cli(args, data_file):
    cmd = CLI + ["--data", str(data_file)] + args
    return subprocess.run(cmd, capture_output=True, text=True)


def seed(data_file, titles):
    for t in titles:
        r = run_cli(["add", t], data_file)
        assert r.returncode == 0, r.stderr


def test_happy_path_contains_and_order_preserved(tmp_path):
    data = tmp_path / "tasks.json"
    seed(data, ["Fix login", "Improve login UX", "Misc"])
    r = run_cli(["search", "--query", "login"], data)
    assert r.returncode == 0
    lines = [ln for ln in r.stdout.splitlines() if ln.strip() and ln.strip() != "No tasks."]
    # Should contain first two tasks in order of list (id asc)
    assert len(lines) == 2
    assert lines[0].endswith("Fix login")
    assert lines[1].endswith("Improve login UX")


def test_case_insensitive_and_trim(tmp_path):
    data = tmp_path / "tasks.json"
    seed(data, ["Fix login"]) 
    r = run_cli(["search", "--query", "  LOGIN  "], data)
    assert r.returncode == 0
    lines = [ln for ln in r.stdout.splitlines() if ln.strip() and ln.strip() != "No tasks."]
    assert len(lines) == 1
    assert lines[0].endswith("Fix login")


def test_query_too_long_validation(tmp_path):
    data = tmp_path / "tasks.json"
    seed(data, ["A"]) 
    q = "x" * 257
    r = run_cli(["search", "--query", q], data)
    assert r.returncode != 0
    assert "1..256" in (r.stderr or "")


def test_empty_results(tmp_path):
    data = tmp_path / "tasks.json"
    seed(data, ["Alpha"]) 
    r = run_cli(["search", "--query", "zzz"], data)
    assert r.returncode == 0
    assert "No tasks." in r.stdout


def test_status_filter_applied(tmp_path):
    data = tmp_path / "tasks.json"
    # Add and mark one done
    run_cli(["add", "Login"], data)
    run_cli(["add", "Login page"], data)
    assert run_cli(["done", "1"], data).returncode == 0
    # search only open
    r_open = run_cli(["search", "--status", "open", "--query", "login"], data)
    assert r_open.returncode == 0
    lines_open = [ln for ln in r_open.stdout.splitlines() if ln.strip() and ln.strip() != "No tasks."]
    assert len(lines_open) == 1
    assert lines_open[0].endswith("Login page")
    # search only done
    r_done = run_cli(["search", "--status", "done", "--query", "login"], data)
    assert r_done.returncode == 0
    lines_done = [ln for ln in r_done.stdout.splitlines() if ln.strip() and ln.strip() != "No tasks."]
    assert len(lines_done) == 1
    assert lines_done[0].endswith("Login")
