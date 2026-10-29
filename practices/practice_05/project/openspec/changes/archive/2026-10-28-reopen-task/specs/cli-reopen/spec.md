# Spec Delta

## ADDED Requirements

### Requirement: Reopen a task

The CLI MUST support reopening an existing task with `reopen <id>`.

#### Scenario: Reopen a completed task

- **WHEN** the user runs `reopen <id>` for a task with status `done`
- **THEN** the task status becomes `open`
- **AND** the command exits with code 0
- **AND** stdout contains `Task <id> marked as open`

#### Scenario: Reopen an already open task

- **WHEN** the user runs `reopen <id>` for a task with status `open`
- **THEN** the task remains `open`
- **AND** the command exits with code 0
- **AND** stdout contains `Task <id> is already open`

#### Scenario: Reopen a nonexistent task

- **WHEN** the user runs `reopen <id>` for an ID that does not exist
- **THEN** the command exits with code 1
- **AND** stderr contains `Task <id> not found`
- **AND** the stored task data is unchanged

#### Scenario: Reopened task participates in existing filters

- **WHEN** a completed task is successfully reopened
- **THEN** it appears in `list --status open`
- **AND** it does not appear in `list --status done`
- **AND** existing `list` behavior remains unchanged

#### Scenario: Existing clear behavior is preserved

- **WHEN** a task is reopened
- **THEN** existing `clear --status open` and `clear --status done` semantics remain unchanged
