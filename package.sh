#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# On Linux, PyInstaller requires objdump from binutils
if [ "$(uname)" = "Linux" ] && ! command -v objdump &>/dev/null; then
    echo "Error: 'objdump' not found. Install binutils first:"
    echo "  sudo apt install binutils      # Debian/Ubuntu"
    echo "  sudo dnf install binutils      # Fedora"
    echo "  sudo pacman -S binutils        # Arch"
    exit 1
fi

# Ensure virtual environment exists
if [ ! -x "$VENV_DIR/bin/python" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --quiet --upgrade pip
fi

PYTHON="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"

echo "Installing dependencies..."
"$PIP" install --quiet -r "$SCRIPT_DIR/requirements.txt"
"$PIP" install --quiet "pyinstaller>=6.0"

echo "Packaging DrNotes..."
"$PYTHON" -m PyInstaller \
    --name DrNotes \
    --windowed \
    --noconfirm \
    --clean \
    --distpath "$SCRIPT_DIR/dist" \
    --workpath "$SCRIPT_DIR/build" \
    --specpath "$SCRIPT_DIR" \
    --collect-all PySide6 \
    --hidden-import markdown \
    --hidden-import pymdownx \
    --hidden-import pymdownx.highlight \
    --hidden-import pymdownx.superfences \
    --hidden-import pymdownx.tasklist \
    --hidden-import pymdownx.tilde \
    --hidden-import markdown.extensions.tables \
    --hidden-import markdown.extensions.nl2br \
    --hidden-import markdown.extensions.sane_lists \
    --hidden-import pygments.formatters.html \
    --hidden-import pygments.styles.tango \
    --hidden-import pygments.styles.github_dark \
    --collect-all pygments \
    "$SCRIPT_DIR/src/drnotes/__main__.py"

echo ""
echo "Done! Packaged app is in: $SCRIPT_DIR/dist/DrNotes/"
