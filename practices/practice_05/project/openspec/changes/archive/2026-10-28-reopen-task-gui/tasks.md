# Tasks

## 1. GUI Action

- [x] 1.1 Add Reopen button and handler next to Done; verify GUI shows it (manual UI check)
- [x] 1.2 Implement `do_reopen` to call `run_cli(["reopen", id])`; verify list refreshes and messages are shown

## 2. Tests

- [ ] 2.1 Add GUI test (if feasible) for successful reopen (done -> open); verify list reflects open
- [ ] 2.2 Add GUI test (if feasible) for nonexistent id; verify error dialog with stderr
- [ ] 2.3 Add GUI test (if feasible) for already open; verify informational message and no state change

## 3. Integration

- [x] 3.1 Manual smoke: add, done, reopen, list filters, clear done; verify flows unchanged except reopen availability
