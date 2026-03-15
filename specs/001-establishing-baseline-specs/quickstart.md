# Quickstart: DrNotes

**Date**: 2026-03-15

## Prerequisites

- Python 3.10 or later
- pip (Python package manager)
- A desktop environment with display server (X11, Wayland, macOS, or Windows)

## Install and Run

```bash
# Clone the repository
git clone https://github.com/your-username/drnotes.git
cd drnotes

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Install in development mode
pip install -e .

# Launch the application
drnotes
```

## First Launch

1. A dialog prompts you to select a **notes root directory** — this
   is where all your notes will be stored as `.md` files.
2. The directory tree on the left populates with any existing `.md`
   files in that directory.
3. Click **"+ Note"** to create your first note.

## Key Workflows

### Writing a Note

- Type markdown in the editor (left pane in split view)
- Use toolbar buttons or keyboard shortcuts for formatting:
  - `Ctrl+B` bold, `Ctrl+I` italic, `Ctrl+1`–`Ctrl+6` headings
  - `Ctrl+Shift+U` unordered list, `Ctrl+Shift+O` ordered list
  - `Ctrl+K` link, `Ctrl+Shift+K` code block
- The preview pane updates automatically after 300ms of idle time
- Notes auto-save after 5 seconds of idle time

### Searching Notes

- `Ctrl+Shift+F` opens the cross-file search panel
- Type a query to search all `.md` files in your notes directory
- Double-click a result to open the file at that line
- `Ctrl+F` opens find/replace within the current note

### Customizing the UI

- `Ctrl+Alt+D` toggles dark/light mode
- `Ctrl+=` / `Ctrl+-` / `Ctrl+0` to adjust/reset font size
- `Ctrl+Alt+E` toggles Emacs keybindings
- `Ctrl+Alt+1/2/3` switches between Editor Only / Preview Only /
  Split View

All preferences persist across sessions.

## Building a Standalone Binary

```bash
pip install -e ".[package]"
bash package.sh
# Output: dist/DrNotes/
```

## Verification Checklist

After installation, verify these work:

- [ ] App launches without errors
- [ ] Notes directory selection dialog appears on first launch
- [ ] Creating a new note creates a `.md` file on disk
- [ ] Typing markdown shows syntax highlighting
- [ ] Preview pane renders markdown correctly
- [ ] A fenced `mermaid` code block renders as a diagram
- [ ] `Ctrl+B` wraps selected text with `**`
- [ ] `Ctrl+Shift+F` opens search and returns results
- [ ] Dark mode toggle changes theme across all panes
- [ ] Closing and reopening restores window state and last file
