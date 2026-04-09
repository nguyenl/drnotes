# Architecture

This document describes the architecture of DrNotes, a cross-platform desktop markdown editor built with Python and PySide6 (Qt 6).

## High-Level Overview

DrNotes follows a **widget-composition** architecture. A single
`MainWindow` orchestrates independent widgets, wiring them together
with Qt signals and slots. Open notes live inside a tabbed workspace,
where each tab owns its own editor and preview pair. All state
persistence is delegated to a `Settings` wrapper around `QSettings`.

```mermaid
graph TD
    App[app.py<br>QApplication] --> MW[MainWindow<br>Orchestrator]
    MW --> DT[DirectoryTree<br>File Browser]
    MW --> SP[SearchPanel<br>Cross-File Search]
    MW --> TB[FormattingToolbar<br>Shortcuts]
    MW --> WT[WorkspaceTabs<br>Open Notes]
    WT --> NW[NoteWorkspace<br>Per-Tab Editor + Preview]
    NW --> ED[MarkdownEditor<br>Text Editing]
    NW --> PP[PreviewPanel<br>HTML Rendering]
    MW --> ST[Settings<br>QSettings]
    PP --> WE[QWebEngineView<br>Mermaid.js]
    ED --> SH[MarkdownHighlighter<br>Syntax Colors]
    DT --> FS[QFileSystemModel<br>Filesystem]
```

## Module Map

```
src/drnotes/
├── app.py                  # Entry point — creates QApplication + MainWindow
├── __main__.py             # python -m drnotes support
├── main_window.py          # MainWindow: layout, menus, signal wiring, timers
├── settings.py             # Settings: QSettings property wrapper
├── syntax_highlighter.py   # MarkdownHighlighter: regex-based syntax coloring
└── widgets/
    ├── __init__.py          # Re-exports public widget classes
    ├── editor.py            # MarkdownEditor, _EditorCore, _FindReplaceBar, _LineNumberArea
    ├── preview.py           # PreviewPanel, _Bridge, Mermaid fence formatter
    ├── workspace_tabs.py    # WorkspaceTabs, NoteWorkspace
    ├── directory_tree.py    # DirectoryTree: file browser with context menu
    ├── search_panel.py      # SearchPanel: cross-file full-text search
    └── toolbar.py           # FormattingToolbar: buttons + keyboard shortcuts
```

## Startup Sequence

```mermaid
sequenceDiagram
    participant App as app.py
    participant MW as MainWindow
    participant S as Settings
    participant DT as DirectoryTree
    participant WT as WorkspaceTabs

    App->>MW: __init__()
    MW->>S: load settings
    MW->>MW: _build_ui()
    MW->>MW: _build_menu()
    MW->>MW: _connect_signals()
    MW->>MW: _restore_state() [geometry, splitter]
    MW->>MW: apply dark/emacs mode from settings

    alt First launch or missing directory
        MW->>MW: _choose_notes_dir() [QFileDialog]
    else Existing root
        MW->>DT: set_root(path)
    end

    alt Last file exists
        MW->>WT: open_file(path)
    end

    App->>MW: show()
    App->>App: exec() [event loop]
```

## Signal Flow

The MainWindow acts as a mediator. Widgets never reference each other directly — all cross-widget communication flows through signals connected in `MainWindow._connect_signals()`.

```mermaid
flowchart LR
    subgraph Widgets
        DT[DirectoryTree]
        SP[SearchPanel]
        TB[FormattingToolbar]
        WT[WorkspaceTabs]
    end

    subgraph MainWindow
        MW((Signal Hub))
    end

    DT -- file_selected --> MW
    MW -- open_file --> WT

    TB -- formatting/view actions --> MW
    MW -- target active workspace --> WT

    SP -- result_selected --> MW
    MW -- open_file_at_line --> WT

    WT -- current_context_changed --> MW
```

### Key signal paths

| Trigger | Signal chain | Result |
|---------|-------------|--------|
| User clicks file in tree | `DirectoryTree.file_selected` → `MainWindow._open_file` → `WorkspaceTabs.open_file` | New tab opens or existing tab gains focus |
| User types in an active tab | `MarkdownEditor.content_changed` → per-workspace 300ms debounce → `PreviewPanel.update_content` | Only that tab's preview updates |
| User types in an active tab | `MarkdownEditor.content_changed` → per-workspace 5s debounce → `MarkdownEditor.save_current` | Only that tab auto-saves |
| User clicks toolbar button | `FormattingToolbar.*` → `MainWindow` → active `NoteWorkspace` | Markdown formatting applies to the active tab |
| User clicks checkbox in preview | `PreviewPanel.checkbox_toggled` → `NoteWorkspace._on_checkbox_toggled` → `MarkdownEditor.set_text_content` | Checklist source toggles inside the same tab |
| User switches tabs | `WorkspaceTabs.current_context_changed` → `MainWindow._update_workspace_context` | Path label and status bar follow the active note |
| User double-clicks search result | `SearchPanel.result_selected` → `MainWindow._open_file_at_line` → `WorkspaceTabs.open_file_at_line` | Existing tab focuses or a new tab opens at the target line |

## Widget Architecture

### MainWindow (`main_window.py`)

The central orchestrator. Responsibilities:

- **Layout**: Assembles a two-level splitter (left: directory tree, right: toolbar + tabbed workspace)
- **Menus**: File (new, save, change directory, exit), Edit (find/replace, search in files), View (view modes, dark mode, emacs mode)
- **Theme**: Applies a Qt stylesheet (`_QSS_DARK`) globally and propagates dark mode to child widgets
- **State persistence**: Saves/restores window geometry, splitter positions, and view mode on close/open
- **Active workspace routing**: Directs global toolbar and menu actions to whichever note tab is active

```mermaid
graph TD
    subgraph MainWindow Layout
        MS[Main Splitter - Horizontal]
        MS --> LP[Left Panel]
        MS --> RP[Right Panel]

        LP --> PL[Path Label]
        LP --> DT[DirectoryTree]
        LP --> SP[SearchPanel]

        RP --> TB[FormattingToolbar]
        RP --> WT[WorkspaceTabs]
    end

    SB[Status Bar] --- FP[File Path - left]
    SB --- LS[Last Saved - right]
```

### WorkspaceTabs (`widgets/workspace_tabs.py`)

`WorkspaceTabs` manages all currently open notes. It owns:

- A `QTabWidget` for the visible tab strip
- A placeholder empty state when no files are open
- One `NoteWorkspace` per open file
- File-path-based duplicate detection so one file maps to one tab
- Tab title disambiguation for same-name files in different folders

Each `NoteWorkspace` contains:

- One `MarkdownEditor`
- One `PreviewPanel`
- A horizontal splitter
- Its own preview-refresh debounce timer (300 ms)
- Its own auto-save timer (5 s)

This keeps editor state, preview state, and save timing local to each
open note instead of forcing `MainWindow` to swap one global editor
between files.

### MarkdownEditor (`widgets/editor.py`)

A composite widget containing three internal components:

```mermaid
graph TD
    ME[MarkdownEditor<br>QWidget] --> FB[_FindReplaceBar<br>QWidget]
    ME --> EC[_EditorCore<br>QPlainTextEdit]
    EC --> LN[_LineNumberArea<br>QWidget]
    EC --> MH[MarkdownHighlighter<br>QSyntaxHighlighter]
```

- **`_EditorCore`** (QPlainTextEdit): The text editing surface. Handles:
  - Smart list continuation on Enter (ordered, unordered, checklists)
  - Tab/Shift+Tab indent/outdent
  - Emacs mode keybindings (20+ bindings for navigation, kill/yank, mark selection)
  - Line number gutter rendering
  - Current-line highlighting
  - Formatting insertion helpers (`insert_wrap`, `insert_line_prefix`, `insert_block`)

- **`_FindReplaceBar`**: Togglable bar with find/replace inputs, case-sensitivity toggle, and next/prev/replace/replace-all buttons. Operates directly on the `_EditorCore` via `QTextDocument.find()`.

- **`_LineNumberArea`**: Custom paint widget for the gutter, delegates rendering back to `_EditorCore.line_number_area_paint_event()`.

### PreviewPanel (`widgets/preview.py`)

Renders markdown to HTML inside a `QWebEngineView`.

```mermaid
graph TD
    PP[PreviewPanel<br>QWidget] --> WV[QWebEngineView]
    PP --> BR[_Bridge<br>QObject]
    WV --> WC[QWebChannel]
    WC --> BR
    WV --> MJ["Mermaid.js 10<br>(Bundled Asset)"]

    subgraph Rendering Pipeline
        MD[Markdown Text]
        MD --> PY["Python markdown lib<br>+ pymdownx extensions"]
        PY --> HTML[HTML String]
        HTML --> B64[Base64 Encode]
        B64 --> JS["JS updateContent()<br>innerHTML swap"]
        JS --> MR["Mermaid.run()<br>Diagram rendering"]
        JS --> CB["Wire checkboxes<br>to Bridge"]
    end
```

**Rendering pipeline**:
1. Python `markdown` library converts markdown to HTML with extensions (superfences, tasklist, highlight, tables, tilde, nl2br, sane_lists)
2. Mermaid fenced blocks are rendered as `<pre class="mermaid-source">` by a custom superfences formatter
3. HTML is base64-encoded and injected via JavaScript `updateContent()` to avoid page reloads
4. JavaScript upgrades `.mermaid-source` elements into Mermaid diagrams via `mermaid.run()`
5. Checkboxes are wired to the `_Bridge` QObject via `QWebChannel`, which emits `checkbox_toggled` back to Python

**Scroll synchronization**: In split view, the editor emits a scroll fraction (0.0–1.0) that the preview applies proportionally. Wheel events on the preview are forwarded back to the editor via the bridge.

### DirectoryTree (`widgets/directory_tree.py`)

File browser built on `QFileSystemModel` + `QTreeView`.

- Filters to `.md` files only
- Supports drag-and-drop (internal move)
- Context menu: New Note, New Folder, Rename, Delete (with confirmation)
- Button bar at top for quick note/folder creation
- Emits `file_selected(path)` on click

### SearchPanel (`widgets/search_panel.py`)

Cross-file full-text search, togglable via `Ctrl+Shift+F`.

- Walks all `.md` files under the notes root using `os.walk()`
- Regex-based matching with optional case sensitivity
- Results displayed in a `QTreeWidget` grouped by file, with line numbers and previews
- Double-clicking a result emits `result_selected(path, line)`, which MainWindow routes to open the file and jump to the matching line
- Hidden by default; activated from the Edit menu or keyboard shortcut

### FormattingToolbar (`widgets/toolbar.py`)

A `QToolBar` that emits three signal types, connected by MainWindow to the editor:

| Signal | Purpose | Example |
|--------|---------|---------|
| `wrap_requested(prefix, suffix)` | Wrap selection | Bold: `**`, `**` |
| `line_prefix_requested(prefix)` | Prepend to line | H1: `# ` |
| `block_requested(text)` | Insert block at cursor | Code: `` ```\n\n``` `` |

### Settings (`settings.py`)

Thin property wrapper around `QSettings`. Persists:

| Property | Type | Default |
|----------|------|---------|
| `notes_root` | `str` | `""` |
| `last_file` | `str` | `""` |
| `window_geometry` | `bytes` | `b""` |
| `window_state` | `bytes` | `b""` |
| `splitter_state` | `bytes` | `b""` |
| `view_mode` | `str` | `"split"` |
| `dark_mode` | `bool` | `False` |
| `emacs_mode` | `bool` | `False` |

Storage location is platform-dependent (registry on Windows, plist on macOS, INI file on Linux under `~/.config`).

### MarkdownHighlighter (`syntax_highlighter.py`)

A `QSyntaxHighlighter` subclass with regex rules for markdown constructs: headings, bold, italic, strikethrough, inline code, links, images, blockquotes, lists, checklists, horizontal rules, and fenced code block markers. Maintains separate color palettes for light and dark themes.

## Data Flow: Checkbox Toggle

This sequence illustrates the round-trip between preview and editor when a user clicks a checkbox:

```mermaid
sequenceDiagram
    participant User
    participant JS as Preview (JavaScript)
    participant Bridge as _Bridge (QObject)
    participant MW as MainWindow
    participant ED as MarkdownEditor

    User->>JS: Click checkbox
    JS->>Bridge: toggle_checkbox(index, checked)
    Bridge->>MW: checkbox_toggled signal
    MW->>MW: Regex find nth "- [ ]" / "- [x]"
    MW->>ED: set_text_content(updated markdown)
    ED->>MW: content_changed signal
    MW->>JS: update_content (after 300ms debounce)
```

## Technology Choices

| Concern | Choice | Rationale |
|---------|--------|-----------|
| GUI framework | PySide6 (Qt 6) | Native look on all platforms, rich widget set, web engine for preview |
| Markdown → HTML | `markdown` + `pymdown-extensions` | Extensible, supports GFM features (tasklists, tables, fenced code) |
| Code highlighting | Pygments | Mature, 500+ language support, integrates with pymdownx.highlight |
| Diagram rendering | Mermaid.js 10 (CDN) | Industry standard, runs in the QWebEngineView with no extra dependencies |
| Editor ↔ Preview bridge | QWebChannel | Qt's built-in mechanism for Python ↔ JavaScript communication |
| Settings persistence | QSettings | Cross-platform, zero-config, native storage per OS |
| Packaging | PyInstaller | Single-binary output, well-tested with PySide6 |
