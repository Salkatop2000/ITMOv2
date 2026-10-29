# Design

## Context

The GUI (`src/task_gui.py`) is a thin Tkinter wrapper that calls the CLI (`src/task_cli.py`) via `run_cli` for list/add/done/clear. Tasks are stored in JSON (`data/tasks.json`) with statuses `open` and `done`. The list view is driven by CLI output and refreshed on actions.

## Goals / Non-Goals

**Goals:**
- Add a Reopen GUI action to transition `done -> open` by invoking `CLI reopen <id>`.
- Keep messaging and error handling consistent with CLI outputs.

**Non-Goals:**
- No new statuses or storage changes.
- No changes to existing CLI behavior.
- No unrelated GUI refactoring.

## Decisions

- Place a Reopen action adjacent to Done; reuse the existing id input.
- Validate id identical to Done (positive integer).
- Invoke `run_cli(data_path, ["reopen", id])` and rely on CLI for messages.
- On non-zero return code: show stderr in an error dialog; on success: refresh list.
- Do not duplicate business logic; the CLI remains the source of truth.

## Risks / Trade-offs

- Ensure exact CLI messages are surfaced appropriately (informational vs errors).
- Avoid regressions in Done/List/Clear flows; validate via smoke tests.
