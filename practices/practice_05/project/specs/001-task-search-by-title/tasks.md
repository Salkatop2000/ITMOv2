---

description: "Actionable tasks for backend/CLI search implementation"
---

# Tasks: Task Search (Unified)




## Team ownership

Logic:
- CLI search
- validation
- filtering
- result format
- CLI tests

UI:
- search field
- debounce
- states
- clear/Esc
- retry
- GUI/integration/E2E tests

## Cross-team contract
- contains only
- case-insensitive
- trim
- max 256
- >256 = validation error
- empty query не вызывает search
- search поверх активных фильтров
- preserve existing list order (currently id ASC)
- result id/title/status
- existing commands/storage/list behavior unchanged

## Format: `[ID] [P?] [Story] Description`

- [P]: Can run in parallel (different files, no dependencies)
- [Story]: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Foundational (Blocking Prerequisites)

**Purpose**: Ensure baseline invariants and helpers exist; MUST complete before user stories

- [ ] T001 Add search CLI subparser scaffolding in src/task_cli.py (no logic yet); ensure no behavior change to existing commands
- [ ] T002 Define error message constants for validation in src/task_cli.py (e.g., "Query must be 1..256 chars after trim")
- [ ] T003 [P] Add internal helper normalize_query(query: str) -> tuple[str, bool] in src/task_cli.py (trim, lower, note trimmed flag) without usage yet
- [ ] T005 Ensure list ordering contract is documented in a code comment in src/task_cli.py (preserve existing list order; currently id ASC)

Checkpoint: Helpers and CLI wiring placeholders exist; no behavior changes.

---

## Phase 2: User Story 1 - Найти задачу по подстроке названия (Priority: P1) 🎯 MVP



### Tests (requested):

- [ ] T006 [P] [US1] Write contract tests for CLI search happy path in tests/contract/test_search_cli.py (contains match, case-insensitive, preserve existing list order)

### Implementation:

- [ ] T007 [US1] Implement search command handler in src/task_cli.py with args: --query (required), --status [open|done|all] default=all
- [ ] T008 [US1] Integrate normalize_query (no truncate/clamp); validate 1..256 after trim; on invalid print error to stderr and exit code 2 (no search performed)
- [ ] T009 [US1] Reuse existing load_tasks and preserve existing list order; apply status filter consistent with list; then apply case-insensitive contains
- [ ] T010 [US1] Output results line-per-task in same format as list: "{id:>3} | {status:<4} | {title}"

Checkpoint: US1 works independently and tests pass.

---

## Phase 3: User Story 2 - Частичный поиск (Priority: P2)



### Tests (requested):

- [ ] T011 [P] [US2] Extend tests to cover substring at start/middle/end and multiple matches ordering in tests/contract/test_search_cli.py

### Implementation:

- [ ] T012 [US2] Verify and adjust matching logic to use normalized contains on titles; ensure no regex usage; preserve existing list order (currently id ASC)

Checkpoint: US2 behaviors verified without breaking US1.

---

## Phase 4: User Story 3 - Поиск без учета регистра и trim (Priority: P2)



### Tests (requested):

- [ ] T013 [P] [US3] Add tests covering uppercase/lowercase and leading/trailing spaces in tests/contract/test_search_cli.py

### Implementation:

- [ ] T014 [US3] Ensure titles are compared case-insensitively; apply trim to query before validation; titles preserved original in output

Checkpoint: US3 behaviors verified without breaking US1/US2.

---

## Phase 5: User Story 4 - Обработка пустого и слишком длинного запроса (Priority: P3)



### Tests (requested):

- [ ] T015 [P] [US4] Add tests for invalid queries (empty after trim; >256) expecting stderr message and non-zero exit in tests/contract/test_search_cli.py

### Implementation:

- [ ] T016 [US4] Implement validation: after trim length <1 or >256 → print error to stderr and exit with code 2; do not perform search
- [ ] T017 [US4] Ensure no change to other commands' exit codes or outputs (regression guard)

Checkpoint: US4 validation verified without breaking earlier stories.

---

## Phase 6: Regression & Cross-Cutting (Logic)


- [ ] T018 [P] Run and, if needed, adapt existing tests/tests/test_task_cli.py to ensure list/add/done/reopen/clear unaffected (no code changes; test updates only if assertions depend on global parser usage)
- [ ] T019 Ensure search results preserve existing list order (currently id ASC) by reusing list order; add explicit assertion in tests/contract/test_search_cli.py
- [ ] T020 Document in src/task_cli.py comments: search preserves existing list ordering and respects active status filter

---

## Phase 7: UI Integration (Blocking for GUI)

Purpose: Implement UI search integration after CLI search is available.

- [ ] T101 [US1] Add search input field (placeholder: "Поиск по названию…") in src/task_gui.py; wire basic events (on change, clear button, Esc).
- [ ] T102 [US1] Implement debounce via Tkinter `after` in src/task_gui.py (e.g., 250–300ms); cancel previous timer on new keystroke.
- [ ] T103 [US1] Apply trim at UI boundary in src/task_gui.py before invoking CLI; ensure empty/whitespace-only query is not sent.
- [ ] T104 [US4] Add UI validation for query length >256 in src/task_gui.py: show validation message and do not call CLI.
- [ ] T105 [US1] Implement empty query guard in src/task_gui.py: on empty → call list (preserve filters), do not call search.
- [ ] T106 [US1] Implement clear button and Esc handler in src/task_gui.py: clear query and call list; preserve filters and sorting.
- [ ] T107 [US1] Ensure active status filter from GUI is passed to CLI search in src/task_gui.py (reuse existing filter control).
- [ ] T108 [US2] Implement loading state indicator during search in src/task_gui.py (disable actions or show spinner in results area).
- [ ] T109 [US2] Implement empty state rendering in src/task_gui.py: show "Нет задач по запросу …" when CLI outputs "No tasks.".
- [ ] T110 [US3] Implement error state with Retry in src/task_gui.py: show error banner; Retry reruns the last non-empty query.
- [ ] T111 [US3] Store last non-empty query and status in src/task_gui.py to support Retry behavior.
- [ ] T112 [US1] Ensure search preserves existing list order and filters in UI rendering in src/task_gui.py (no re-sorting on client).

---

## Phase 8: UI Tests (Integration/E2E)

- [ ] T201 [Optional] [P] [US1] Add integration tests for GUI search in tests/integration/test_gui_search.py (debounce, empty guard, clear/Esc, filters preserved, order preserved). Optional/Backlog for current scope.
- [ ] T202 [Optional] [US2] Add tests for UI loading and empty states in tests/integration/test_gui_search.py. Optional/Backlog for current scope.
- [ ] T203 [Optional] [US3] Add tests for UI error and Retry behavior in tests/integration/test_gui_search.py. Optional/Backlog for current scope.
- [ ] T204 [Optional] [US4] Add tests for UI validation: query >256 prevents CLI call in tests/integration/test_gui_search.py. Optional/Backlog for current scope.
- [ ] T205 [Optional] E2E test covering end-to-end flow in tests/e2e/test_search_e2e.py (CLI+GUI) using temporary data file. Optional/Backlog for current scope.
- [ ] T206 [Optional] Regression: ensure existing GUI actions (list/add/done/reopen/clear) still function in tests/integration/test_gui_search.py. Optional/Backlog for current scope.

## Convergence Decision

- Date/Status: 2026-10-29 — Decision recorded
- Decision: T201–T206 = optional/backlog for current educational scope; do not implement now; do not add a Tkinter GUI testing framework.
- Rationale: plan.md allows GUI integration tests as optional; current scope does not require introducing a GUI testing framework.
- Verification result: 17 passed (CLI + existing tests). Manual GUI/E2E verification remains part of final checks.

---

## Dependencies & Execution Order

1. Foundational Phase (T001–T005)
2. US1 (T006 → T010)
3. US2 (T011 → T012)
4. US3 (T013 → T014)
5. US4 (T015 → T017)
6. Regression & Cross-Cutting (T018–T020)

Parallel opportunities:
- T003 and T004 can run in parallel after T001–T002
- Test tasks T006, T011, T013, T015 can run in parallel when corresponding implementation is pending, following TDD if desired
- Documentation/comment tasks (T005, T020) can run in parallel with tests

## Implementation Strategy

MVP First: Complete US1 only (T001–T010). Validate independently via tests/contract/test_search_cli.py. Then proceed to US2–US4.
