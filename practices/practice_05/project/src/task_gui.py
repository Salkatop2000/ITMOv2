#!/usr/bin/env python3
"""
Minimal Tkinter GUI wrapper around src/task_cli.py.

- Uses subprocess to call the CLI with: list/add/done/clear
- Data file path editable at the top; optional Save Path (persist in data/gui_path.txt)
- Status filter: open/done/all

Keep logic small; reuse CLI behavior. ASCII only.
"""
import os
import subprocess
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


# Project root and defaults (mirror task_cli.py defaults)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI_PATH = os.path.join(ROOT_DIR, "src", "task_cli.py")
DEFAULT_DATA_FILE = os.path.join(ROOT_DIR, "data", "tasks.json")
SAVED_PATH_FILE = os.path.join(ROOT_DIR, "data", "gui_path.txt")


def _load_saved_path(default_path: str) -> str:
    try:
        with open(SAVED_PATH_FILE, "r", encoding="ascii") as f:
            p = f.read().strip()
            return p or default_path
    except FileNotFoundError:
        return default_path
    except Exception:
        return default_path


def _save_path(path: str) -> None:
    parent = os.path.dirname(SAVED_PATH_FILE)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    with open(SAVED_PATH_FILE, "w", encoding="ascii") as f:
        f.write(path)


def run_cli(data_path: str, args: list[str]) -> subprocess.CompletedProcess:
    # Always call the CLI via python3 with absolute CLI path
    cmd = ["python3", CLI_PATH, "--data", data_path] + args
    return subprocess.run(cmd, capture_output=True, text=True)


class App:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        master.title("Task GUI")

        self.status_options = ("open", "done", "all")
        self.data_var = tk.StringVar(value=_load_saved_path(DEFAULT_DATA_FILE))
        self.filter_var = tk.StringVar(value="all")
        self.add_var = tk.StringVar()
        self.id_var = tk.StringVar()

        # Top: data path entry and actions
        top = ttk.Frame(master)
        top.pack(fill=tk.X, padx=8, pady=6)
        ttk.Label(top, text="Data file:").pack(side=tk.LEFT)
        self.data_entry = ttk.Entry(top, textvariable=self.data_var, width=60)
        self.data_entry.pack(side=tk.LEFT, padx=6)
        ttk.Button(top, text="Refresh", command=self.refresh).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Save Path", command=self.save_path).pack(side=tk.LEFT, padx=4)

        # Middle: listbox and filter
        mid = ttk.Frame(master)
        mid.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        left = ttk.Frame(mid)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox = tk.Listbox(left, height=12)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.listbox.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.configure(yscrollcommand=sb.set)

        right = ttk.Frame(mid)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        ttk.Label(right, text="Filter").pack(anchor=tk.N)
        self.filter_cb = ttk.Combobox(right, state="readonly", values=self.status_options, textvariable=self.filter_var, width=8)
        self.filter_cb.pack(pady=2)
        self.filter_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        # Bottom: actions
        bottom = ttk.Frame(master)
        bottom.pack(fill=tk.X, padx=8, pady=6)

        # Add
        ttk.Label(bottom, text="Add:").pack(side=tk.LEFT)
        self.add_entry = ttk.Entry(bottom, textvariable=self.add_var, width=30)
        self.add_entry.pack(side=tk.LEFT, padx=4)
        ttk.Button(bottom, text="Add", command=self.do_add).pack(side=tk.LEFT, padx=4)

        # Done
        ttk.Label(bottom, text="Done id:").pack(side=tk.LEFT, padx=(12, 0))
        self.id_entry = ttk.Entry(bottom, textvariable=self.id_var, width=6)
        self.id_entry.pack(side=tk.LEFT, padx=4)
        ttk.Button(bottom, text="Done", command=self.do_done).pack(side=tk.LEFT, padx=4)

        # Clear by status
        ttk.Button(bottom, text="Clear by status", command=self.do_clear).pack(side=tk.RIGHT)

        # initial population
        self.refresh()

    def current_status(self) -> str:
        s = self.filter_var.get().strip()
        return s if s in self.status_options else "all"

    def refresh(self) -> None:
        status = self.current_status()
        data_path = self.data_var.get().strip() or DEFAULT_DATA_FILE
        args = ["list", "--status", status]
        res = run_cli(data_path, args)
        if res.returncode != 0:
            messagebox.showerror("List error", res.stderr or "Failed to list tasks")
            return
        lines = [ln for ln in res.stdout.splitlines() if ln.strip() and ln.strip() != "No tasks."]
        self.listbox.delete(0, tk.END)
        for ln in lines:
            self.listbox.insert(tk.END, ln)

    def save_path(self) -> None:
        p = self.data_var.get().strip() or DEFAULT_DATA_FILE
        try:
            _save_path(p)
        except Exception as e:
            messagebox.showerror("Save Path", f"Could not save path: {e}")
            return
        messagebox.showinfo("Save Path", "Data path saved")

    def do_add(self) -> None:
        title = (self.add_var.get() or "").strip()
        if not title:
            messagebox.showerror("Validation", "Title must be non-empty")
            return
        data_path = self.data_var.get().strip() or DEFAULT_DATA_FILE
        res = run_cli(data_path, ["add", title])
        if res.returncode != 0:
            messagebox.showerror("Add error", res.stderr or "Failed to add task")
            return
        self.add_var.set("")
        self.refresh()

    def do_done(self) -> None:
        raw = (self.id_var.get() or "").strip()
        if not raw.isdigit() or int(raw) <= 0:
            messagebox.showerror("Validation", "Id must be a positive integer")
            return
        data_path = self.data_var.get().strip() or DEFAULT_DATA_FILE
        res = run_cli(data_path, ["done", raw])
        if res.returncode != 0:
            messagebox.showerror("Done error", res.stderr or "Failed to mark done")
            return
        self.refresh()

    def do_clear(self) -> None:
        status = self.current_status()
        if status not in self.status_options:
            messagebox.showerror("Validation", "Invalid status")
            return
        data_path = self.data_var.get().strip() or DEFAULT_DATA_FILE
        res = run_cli(data_path, ["clear", "--status", status])
        if res.returncode != 0:
            messagebox.showerror("Clear error", res.stderr or "Failed to clear tasks")
            return
        self.refresh()


def main() -> None:
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
