# Proposal

## Why

Allow users working in the GUI to correct a mistaken completion or continue work by returning a completed task to the open state without switching to the CLI or editing data manually.

## What Changes

- Add GUI support to reopen tasks (transition `done -> open`)
  - Invoke existing CLI command `reopen <id>`
  - Already-open task: succeed and surface CLI message
  - Nonexistent id: show CLI stderr and keep data unchanged
- Preserve existing statuses (`open`, `done`) and data format
- Do not change existing CLI behaviors (add/done/list/clear)
- Avoid unrelated UI refactors; minimal additions only

## Capabilities

### New Capabilities
- gui-reopen: Provide a GUI action to reopen a completed task by delegating to the CLI `reopen <id>` and refreshing the list view.

### Modified Capabilities
- (none)

## Impact

- GUI (Tkinter, `src/task_gui.py`): add a Reopen action adjacent to Done that calls `run_cli([... "reopen", id])`, validates id like Done, handles stderr/exit codes, and refreshes the list on success.
- Tests: add GUI-level tests if present; otherwise rely on manual smoke and existing CLI tests.
