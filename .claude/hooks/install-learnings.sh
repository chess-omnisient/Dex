#!/bin/bash
# Stop-hook wrapper for pending session-learning install.
# Fail-open when python3 is missing (Linux replica / stripped PATH).
# The Python program owns stdin, threshold detection, and the Stop block.
# Run the sibling .py next to this wrapper (shipped tree), not a copy
# under the vault path — harness tests point CLAUDE_PROJECT_DIR at a
# sandbox that has the notes, not the hook files.

command -v python3 >/dev/null 2>&1 || exit 0
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$SCRIPT_DIR/install-learnings.py"
