#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# Try venv first; fall back to system python + user site-packages
if [ -x "$VENV_DIR/bin/python" ]; then
    PYTHON="$VENV_DIR/bin/python"
    PIP="$VENV_DIR/bin/pip"
elif python3 -m venv "$VENV_DIR" 2>/dev/null; then
    echo "Setting up virtual environment..."
    PYTHON="$VENV_DIR/bin/python"
    PIP="$VENV_DIR/bin/pip"
    "$PIP" install --quiet --upgrade pip
    "$PIP" install --quiet -r "$SCRIPT_DIR/requirements.txt"
    echo "Setup complete."
else
    # venv unavailable (missing python3-venv) — use system python
    rm -rf "$VENV_DIR"
    PYTHON=python3
    PIP="python3 -m pip"
    if ! "$PYTHON" -c "import PySide6" 2>/dev/null; then
        echo "Installing dependencies (user site-packages)..."
        $PIP install --user --break-system-packages -q -r "$SCRIPT_DIR/requirements.txt"
        echo "Setup complete."
    fi
fi

PYTHONPATH="$SCRIPT_DIR/src" exec "$PYTHON" -m drnotes "$@"
