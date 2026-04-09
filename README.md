# DrNotes

A cross-platform desktop markdown note-taking application that stores all data as plain `.md` files on your local filesystem. Mermaid diagrams and code syntax highlighting right inside the preview. No cloud, no databases, no lock-in — just your notes as files.

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)

# Screenshot

<img width="1736" height="1106" alt="image" src="https://github.com/user-attachments/assets/7d34719a-dffb-4f71-953c-1281875229c1" />

## Features

### Editor
- Closable tabs so multiple notes can stay open at the same time
- Markdown syntax highlighting with line numbers
- Undo/redo, find and replace
- Full-text search across all notes (`Ctrl+Shift+F`)
- Auto-save after 5 seconds of idle time
- Smart list continuation (ordered, unordered, and checklists)
- Tab/Shift+Tab for indent/outdent
- Formatting toolbar with icons (system theme) and keyboard shortcuts
- Adjustable font size (increase, decrease, reset) from menu, toolbar, or keyboard
- Toolbar buttons for view mode, dark/light mode, and emacs mode toggles

### Live Preview
- Fully rendered mermaid diagrams
- Side-by-side split view with synchronized scrolling
- CommonMark/GFM markdown rendering
- Interactive checklists — click to toggle, changes write back to the file
- Syntax-highlighted code blocks via Pygments
- Three view modes: Editor Only, Preview Only, Split View (switchable from menu or toolbar)

### Mermaid Diagrams
Fenced ` ```mermaid ` code blocks render as diagrams in the preview, including:
- Flowcharts
- Sequence diagrams
- Gantt charts
- Class diagrams
- State diagrams
- Entity-relationship diagrams
- Pie charts

Invalid syntax displays an inline error message rather than failing silently.

### File Organization
- Directory tree panel for browsing and managing notes
- Create, rename, and delete files and folders
- Drag-and-drop to move files between folders
- User-selectable notes root directory
- Reopening an already open note focuses its existing tab instead of opening a duplicate

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Bold | `Ctrl+B` |
| Italic | `Ctrl+I` |
| Strikethrough | `Ctrl+Shift+S` |
| Heading H1–H6 | `Ctrl+1` – `Ctrl+6` |
| Unordered list | `Ctrl+Shift+U` |
| Ordered list | `Ctrl+Shift+O` |
| Checklist | `Ctrl+Shift+C` |
| Code block | `Ctrl+Shift+K` |
| Link | `Ctrl+K` |
| Image | `Ctrl+Shift+I` |
| Blockquote | `Ctrl+Shift+Q` |
| Increase Font Size | `Ctrl+=` |
| Decrease Font Size | `Ctrl+-` |
| Reset Font Size | `Ctrl+0` |
| Search in Files | `Ctrl+Shift+F` |
| Editor Only | `Ctrl+Alt+1` |
| Preview Only | `Ctrl+Alt+2` |
| Split View | `Ctrl+Alt+3` |
| Dark Mode | `Ctrl+Alt+D` |
| Emacs Mode | `Ctrl+Alt+E` |

### Emacs Mode
Optional emacs-style keybindings for navigation, kill/yank, and mark-based selection (20+ bindings). Toggle from the View menu or the toolbar; the setting persists across sessions.

### Themes
Dark and light mode with a toggle in the View menu or the toolbar. The theme applies to the editor, UI chrome, and preview pane, and persists across sessions.

### Status Bar
Displays the current file path and last-saved timestamp, updating immediately on each save.

## Installation

**Requirements:** Python 3.10+

```bash
# Clone the repository
git clone https://github.com/your-username/drnotes.git
cd drnotes

# Create a virtual environment and install
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

pip install -e .
```

## Usage

```bash
# Run the application
drnotes

# Or run directly
python -m drnotes
```

On first launch, select a directory to use as your notes root. All notes are stored as plain `.md` files in that directory.

## Packaging

Build a standalone binary with PyInstaller:

```bash
pip install -e ".[package]"
bash package.sh
```

The output binary will be in the `dist/` directory.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| GUI | PySide6 (Qt) |
| Markdown | `markdown` + `pymdown-extensions` |
| Syntax highlighting | Pygments |
| Diagrams | Mermaid.js 10 (via embedded webview) |
| Packaging | PyInstaller |

## Project Structure

```
src/drnotes/
├── app.py                  # Application entry point
├── main_window.py          # Main window layout and orchestration
├── settings.py             # Persistent user settings (QSettings)
├── syntax_highlighter.py   # Markdown syntax highlighting rules
└── widgets/
    ├── editor.py           # Markdown editor with find/replace
    ├── preview.py          # HTML preview with Mermaid rendering
    ├── workspace_tabs.py   # Tabbed note workspace container
    ├── directory_tree.py   # File/folder browser
    ├── search_panel.py     # Cross-file text search
    └── toolbar.py          # Formatting toolbar
```
