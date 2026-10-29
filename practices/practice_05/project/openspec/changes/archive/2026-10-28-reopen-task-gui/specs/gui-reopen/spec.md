# Spec Delta

## Purpose
Allow users to revert a completed task to open from the GUI by delegating to the existing CLI `reopen <id>` without changing storage, statuses, or other behaviors.

## ADDED Requirements

### Requirement: GUI can reopen a completed task
The GUI SHALL allow users to reopen a completed (done) task back to open using existing CLI behavior.

#### Scenario: Reopen a completed task from GUI
- **WHEN** the user enters a valid id for a task with status `done` and triggers Reopen
- **THEN** the GUI invokes CLI `reopen <id>`
- **AND** the command exits with code 0
- **AND** the GUI refreshes the list
- **AND** the task appears under `open` and not under `done`

#### Scenario: Reopen an already open task from GUI
- **WHEN** the user enters a valid id for a task with status `open` and triggers Reopen
- **THEN** the GUI invokes CLI `reopen <id>`
- **AND** the command exits with code 0
- **AND** the GUI shows the CLI message (informational)
- **AND** the list refresh preserves the task under `open`

#### Scenario: Reopen a nonexistent task from GUI
- **WHEN** the user enters an id that does not exist and triggers Reopen
- **THEN** the GUI invokes CLI `reopen <id>`
- **AND** the command exits with code 1
- **AND** the GUI displays the CLI stderr message to the user
- **AND** the stored task data remains unchanged

#### Scenario: Filters reflect reopened tasks
- **WHEN** a task is successfully reopened from the GUI
- **THEN** `list --status open` includes the task
- **AND** `list --status done` does not include the task
- **AND** existing list behavior remains unchanged

#### Scenario: Clear behavior is preserved
- **WHEN** a task is reopened from the GUI
- **THEN** `clear --status done` does not remove it
- **AND** existing clear behavior remains unchanged
