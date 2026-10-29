# Quickstart: Validate Task Search (v1)

Preconditions

- Platform: Linux with Python 3 and Tkinter available.
- Data file: default path used by GUI and CLI is data/tasks.json.
- Launch GUI: python src/task_gui.py from project root.
- Note: This document records manual E2E checks. In this environment, interactive GUI control is not available to the agent; scenarios are marked NOT RUN when interaction is required.

Scenario 1: Search by partial title
- Steps:
  1. Launch GUI; ensure Data file points to a writable file (default).
  2. Add tasks: "Fix login", "Improve login UX", "Misc".
  3. In Search, type: login.
  4. Observe results.
- Expected:
  - Two results shown: Fix login, Improve login UX, order preserved by id.
- Actual:
  - NOT RUN (no interactive GUI session available in this environment).
- Result: NOT RUN

Scenario 2: Case-insensitive search
- Steps:
  1. Use existing data with a task titled "Fix Login".
  2. In Search, type: LOGIN (uppercase).
  3. Observe results.
- Expected:
  - Task "Fix Login" is found; same as lowercase.
- Actual: NOT RUN
- Result: NOT RUN

Scenario 3: Trim leading/trailing spaces
- Steps:
  1. Have a task with title containing login.
  2. In Search, type: space-space LOGIN space-space (e.g., "  LOGIN  ").
- Expected:
  - Same results as "login"; whitespace ignored.
- Actual: NOT RUN
- Result: NOT RUN

Scenario 4: No results state
- Steps:
  1. Enter a unique query such as zzzzz.
- Expected:
  - Empty state message: "Нет задач по запросу \"zzzzz\"".
- Actual: NOT RUN
- Result: NOT RUN

Scenario 5: Empty/whitespace-only query guard
- Steps:
  1. Clear Search to empty (or enter only spaces).
- Expected:
  - Search not sent; list restored with filters preserved.
- Actual: NOT RUN
- Result: NOT RUN

Scenario 6: Query length >256 validation
- Steps:
  1. Paste a 257-character string into Search.
- Expected:
  - Validation error shown; CLI search not invoked.
- Actual: NOT RUN
- Result: NOT RUN

Scenario 7: Active status filter + search
- Steps:
  1. Set Filter to open.
  2. Ensure at least one matching open and one matching done task exist.
  3. Search for a term matching both.
- Expected:
  - Only open tasks displayed when filter=open; switching to done shows done-only.
- Actual: NOT RUN
- Result: NOT RUN

Scenario 8: Preserve existing order of results
- Steps:
  1. Add multiple matching tasks in known id order.
  2. Search for a common substring.
- Expected:
  - Results order matches list order (id ascending), not re-sorted.
- Actual: NOT RUN
- Result: NOT RUN

Scenario 9: Clear button
- Steps:
  1. After a search, press Clear.
- Expected:
  - Search field is cleared; list restored; filters/sort preserved; no empty search call.
- Actual: NOT RUN
- Result: NOT RUN

Scenario 10: Escape key clears search
- Steps:
  1. After a search, press Esc in Search field.
- Expected:
  - Same as Clear.
- Actual: NOT RUN
- Result: NOT RUN

Scenario 11: Loading state
- Steps:
  1. Type a query; observe status label during debounce/search.
- Expected:
  - Temporary state "Searching…" shown; cleared after results.
- Actual: NOT RUN
- Result: NOT RUN

Scenario 12: Error and Retry
- Steps:
  1. Induce a recoverable error (e.g., temporarily point Data file to an invalid path).
  2. Perform a search; observe error; restore valid path; press Retry.
- Expected:
  - Error banner/message shown; Retry reruns last query and shows results when issue fixed.
- Actual: NOT RUN
- Result: NOT RUN

Scenario 13: Regression — List/Refresh, Add, Done, Reopen, Clear
- Steps:
  1. Use GUI controls to list, add a task, mark done, reopen, and clear by status.
- Expected:
  - Behaviors match CLI; no regressions; messages/errors as per existing flows.
- Actual: NOT RUN
- Result: NOT RUN

E2E Verdict

- Overall: NOT RUN
- Rationale: Interactive Tkinter GUI control is not available to this agent/session. Tkinter import and root creation succeed, but manual interaction is not possible here. CLI contract tests cover the search behavior; GUI integration remains to be demonstrated interactively on a local desktop session.
