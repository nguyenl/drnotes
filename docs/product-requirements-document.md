# Product Requirements Document: DrNotes

## Overview

DrNotes is a cross-platform desktop note-taking application that stores all data as plain markdown files on the local filesystem. It runs on Linux, macOS, and Windows, and is built in Python for portability. The app provides a rich editing experience with live preview, folder-based organization, and first-class support for Mermaid diagrams.

## Goals

- Provide a fast, local-first markdown note-taking experience with zero cloud dependency
- Store notes as standard `.md` files so they remain portable and accessible outside the app
- Support all three major desktop platforms (Linux, macOS, Windows) from a single Python codebase
- Offer a friendly, low-friction editing UX for common markdown constructs

## Non-Goals

- Cloud sync or multi-device collaboration (out of scope for v1)
- Mobile platforms
- Plugin or extension system
- End-to-end encryption

---

## User Interface

### Layout

The application window is split into two primary panels:

| Panel | Position | Description |
|-------|----------|-------------|
| **Directory Tree** | Left | Displays the relative folder structure of the user's notes directory. Supports expanding/collapsing folders, creating new folders, renaming, and deleting. |
| **Editor / Preview** | Right | A tabbed or split view containing the markdown editor and the rendered preview of the current note. |

### Directory Tree Panel (Left)

- Displays all folders and `.md` files within the configured notes root directory
- Tree is navigable via mouse click or keyboard arrows
- Supports the following operations on folders and files:
  - Create new folder
  - Create new note (`.md` file)
  - Rename folder or note
  - Delete folder or note (with confirmation prompt)
  - Drag-and-drop to move files between folders
- Reflects filesystem changes in real time (or on manual refresh)

### Editor / Preview Panel (Right)

- Two modes, togglable by the user:
  - **Edit mode**: A text editor for writing raw markdown
  - **Preview mode**: A rendered HTML view of the markdown content
- Optionally supports a **split view** showing the editor and preview side by side
- The currently open file name and path are displayed above the editor

### Status Bar (Bottom)

A persistent status bar spans the full width of the window at the bottom edge:

| Section | Position | Content |
|---------|----------|---------|
| **File path** | Left (stretches) | Absolute path of the currently open file, or "No file open" when none is selected |
| **Last saved** | Right (fixed) | Timestamp of the most recent save in `YYYY-MM-DD HH:MM:SS` format, or "Not saved" when the file has not yet been saved in this session |

- The status bar updates immediately whenever the file is saved (auto-save or Ctrl+S)
- The timestamp resets to "Not saved" each time a new file is opened
- The status bar respects the current dark/light theme

### Toolbar

The formatting toolbar also includes buttons for:
- **View modes**: Editor Only, Preview Only, and Split View (mutually exclusive, with checked state indicator)
- **Font Size**: Increase (A+) and Decrease (A–) buttons with system theme zoom icons
- **Dark / Light Mode**: Toggle button with system theme icon
- **Emacs Mode**: Toggle button with system theme icon

All toolbar buttons use system theme icons (via `QIcon.fromTheme`) when available, falling back to text labels on platforms without a matching icon theme.

### Dark / Light Mode

- A toggle in the View menu switches the entire application between dark and light themes
- The selected theme applies to both the editor/UI chrome and the markdown preview pane
- The chosen theme persists across sessions

### Emacs Mode

- A toggle in the View menu enables emacs-style keyboard navigation and editing in the text editor
- When active, the following emacs keybindings replace or augment the default Qt editor bindings:

| Key | Emacs action |
|-----|-------------|
| `Ctrl+F` | Move forward one character |
| `Ctrl+B` | Move backward one character |
| `Ctrl+N` | Move to next line |
| `Ctrl+P` | Move to previous line |
| `Ctrl+A` | Move to beginning of line |
| `Ctrl+E` | Move to end of line |
| `Alt+F` | Move forward one word |
| `Alt+B` | Move backward one word |
| `Ctrl+V` | Scroll down (page down) |
| `Alt+V` | Scroll up (page up) |
| `Ctrl+D` | Delete character forward |
| `Ctrl+H` | Delete character backward |
| `Ctrl+K` | Kill (cut) to end of line |
| `Ctrl+W` | Kill (cut) selected region |
| `Alt+D` | Kill word forward |
| `Alt+Backspace` | Kill word backward |
| `Alt+W` | Copy selected region |
| `Ctrl+Y` | Yank (paste) from clipboard |
| `Ctrl+Space` | Set / clear mark (begin selection) |
| `Ctrl+G` | Cancel mark and deselect |

- Navigation keys extend the selection when the mark is active (`Ctrl+Space`)
- The emacs mode setting persists across sessions

---

## Markdown Editor

### Core Editing Features

- Syntax highlighting for markdown
- Line numbers
- Undo / redo
- Find and replace within the current note
- Full-text search across all notes in the directory (`Ctrl+Shift+F`)
- Auto-indent and soft-wrap

### Formatting Toolbar / Shortcuts

The editor must provide toolbar buttons (with system theme icons where available, falling back to text labels) and keyboard shortcuts for the following common operations:

| Action | Shortcut (default) | Markdown Output |
|--------|-------------------|-----------------|
| Bold | `Ctrl+B` | `**text**` |
| Italic | `Ctrl+I` | `*text*` |
| Strikethrough | `Ctrl+Shift+S` | `~~text~~` |
| Heading (H1-H6) | `Ctrl+1` through `Ctrl+6` | `# ` through `###### ` |
| Unordered list | `Ctrl+Shift+U` | `- item` |
| Ordered list | `Ctrl+Shift+O` | `1. item` |
| Checklist | `Ctrl+Shift+C` | `- [ ] item` |
| Code block | `Ctrl+Shift+K` | `` ``` `` fenced block |
| Link | `Ctrl+K` | `[text](url)` |
| Image | `Ctrl+Shift+I` | `![alt](path)` |
| Blockquote | `Ctrl+Shift+Q` | `> text` |
| Horizontal rule | --- | `---` |
| Increase font size | `Ctrl+=` | — |
| Decrease font size | `Ctrl+-` | — |
| Reset font size | `Ctrl+0` | — |

### Checklist Behavior

- In preview mode, checkboxes are interactive — clicking a checkbox toggles its state and writes the change back to the `.md` file (`- [ ]` <-> `- [x]`)
- In edit mode, pressing `Enter` at the end of a checklist item automatically inserts a new `- [ ] ` on the next line

### List Behavior

- Pressing `Enter` at the end of a list item continues the list on the next line
- Pressing `Enter` on an empty list item ends the list
- `Tab` indents a list item; `Shift+Tab` outdents

---

## Mermaid Diagram Support

- Fenced code blocks tagged with ` ```mermaid ` are rendered as diagrams in preview mode
- Supported diagram types include (at minimum):
  - Flowcharts
  - Sequence diagrams
  - Gantt charts
  - Class diagrams
  - State diagrams
- Rendering errors (invalid Mermaid syntax) display an inline error message in the preview rather than silently failing

---

## Data Storage

- All notes are stored as plain `.md` files on the local filesystem
- The user selects a root notes directory on first launch; this can be changed in settings
- Folder structure within the notes directory is entirely user-controlled
- No proprietary metadata files or databases — the folder of `.md` files is the canonical data store
- File encoding: UTF-8

---

## Platform & Technology

| Aspect | Choice |
|--------|--------|
| Language | Python 3.10+ |
| GUI framework | TBD (candidates: PySide6/Qt, Tkinter + ttkbootstrap, or a webview-based approach such as pywebview) |
| Markdown rendering | TBD (candidates: `markdown` or `mistune` library, rendered to HTML) |
| Mermaid rendering | TBD (candidates: embedded webview with mermaid.js, or pre-rendering via mermaid CLI) |
| Packaging | PyInstaller, Briefcase, or Nuitka for single-binary distribution on each platform |

### Cross-Platform Requirements

- Native-feeling window chrome and file dialogs on each OS
- Keyboard shortcuts must respect platform conventions (e.g., `Cmd` on macOS vs `Ctrl` on Linux/Windows)
- File path handling must work with both `/` and `\` separators

---

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | User can create, open, edit, and save markdown notes | Must have |
| FR-02 | User can create, rename, and delete folders to organize notes | Must have |
| FR-03 | Directory tree panel displays the folder/file hierarchy of the notes root | Must have |
| FR-04 | Markdown editor provides syntax highlighting | Must have |
| FR-05 | Markdown preview renders standard CommonMark/GFM markdown to HTML | Must have |
| FR-06 | Mermaid code blocks render as diagrams in preview mode | Must have |
| FR-07 | Toolbar with icons and keyboard shortcuts for formatting (bold, italic, lists, checklists, etc.) | Must have |
| FR-08 | Checklists in preview mode are interactive and write state back to the file | Should have |
| FR-09 | Editor supports find and replace | Should have |
| FR-10 | User can choose and change the notes root directory | Must have |
| FR-11 | Drag-and-drop file/folder reordering in the directory tree | Nice to have |
| FR-12 | Split view showing editor and preview side by side | Should have |
| FR-13 | App remembers window size, position, and last-opened note across sessions | Should have |
| FR-14 | Auto-save or save-on-switch to prevent data loss | Should have |
| FR-15 | Dark / light mode toggle that persists across sessions | Should have |
| FR-16 | Emacs mode: emacs-style navigation, kill/yank, and mark-based selection in the editor | Should have |
| FR-17 | Status bar displays the currently open file's absolute path and the timestamp of the last save | Should have |
| FR-18 | Full-text search across all notes with results grouped by file, clickable to navigate to the match | Should have |
| FR-19 | Toolbar buttons for view mode (editor/preview/split), dark/light mode toggle, and emacs mode toggle with system theme icons | Should have |
| FR-20 | Adjustable editor font size via menu, toolbar, and keyboard shortcuts (Ctrl+=, Ctrl+-, Ctrl+0), persisted across sessions | Should have |

---

## Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | App launches in under 3 seconds on modern hardware |
| NFR-02 | Editing and preview are responsive with notes up to 10,000 lines |
| NFR-03 | No network access required — the app is fully offline-capable |
| NFR-04 | Single installable artifact per platform (no separate runtime install needed by the end user) |

---

## Future Considerations (Out of Scope for v1)

- Tag or metadata system (e.g., YAML front matter)
- Export to PDF or HTML
- Version history / git integration
- Theming and custom CSS for preview
- Plugin system for additional renderers or editor extensions
