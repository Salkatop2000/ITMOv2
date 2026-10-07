#!/usr/bin/env bash
set -euo pipefail

# Move to project root regardless of the current directory
SCRIPT_DIR="$(dirname "$0")"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

echo "Project root: $ROOT_DIR"

# Run tests if pytest is available
if command -v pytest >/dev/null 2>&1; then
  echo "Running tests..."
  pytest -q
else
  echo "pytest not found, skipping tests" >&2
fi

echo "Running CLI smoke checks..."

TMP_DIR="$(mktemp -d)"
DATA_FILE="$TMP_DIR/tasks.json"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

# Add a task
ADD_OUT=$(python3 src/task_cli.py --data "$DATA_FILE" add "Smoke task")
echo "Add output: $ADD_OUT"

# List tasks
LIST_OUT=$(python3 src/task_cli.py --data "$DATA_FILE" list)
echo "$LIST_OUT" | grep -q "Smoke task"

# Mark done
python3 src/task_cli.py --data "$DATA_FILE" done 1

# Verify done appears in list --status done
DONE_OUT=$(python3 src/task_cli.py --data "$DATA_FILE" list --status done)
echo "$DONE_OUT" | grep -q "done"

# Clear done tasks and ensure they are removed
python3 src/task_cli.py --data "$DATA_FILE" clear --status done
AFTER_CLEAR=$(python3 src/task_cli.py --data "$DATA_FILE" list --status done)
! echo "$AFTER_CLEAR" | grep -q "done"

echo "Smoke checks passed"
