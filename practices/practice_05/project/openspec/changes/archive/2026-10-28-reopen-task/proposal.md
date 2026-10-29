# Proposal

## Why

Add the ability to return a completed task back to the open state from the CLI. This closes a usability gap when a task was marked as done by mistake or needs further work, without requiring manual data edits.

## What Changes

- Introduce a new CLI command: `reopen <id>`
  - Primary transition: `done -> open`
  - If the task is already `open`, exit code 0 with message: `Task <id> is already open`
  - If the task does not exist, print `Task <id> not found` to stderr and exit with code 1
- Status model remains limited to existing statuses: `open` and `done`
- Storage format is unchanged (JSON list of task objects with `status`)
- Existing behavior of `add`, `done`, `list`, and `clear` remains unchanged
- GUI is out of scope

## Capabilities

### New Capabilities
- cli-reopen: Defines observable behavior for reopening tasks via CLI, including messages, exit codes, and interactions with list and clear

### Modified Capabilities
- (none)

## Impact

- CLI: `argparse` parser gains a new subcommand `reopen`
- Task ops: add a small operation symmetric to `done` to set status back to `open`
- Tests: add cases for reopen success, nonexistent id, already open, and preservation of existing list/clear behavior
