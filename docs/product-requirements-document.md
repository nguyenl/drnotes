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

---

## Markdown Editor

### Core Editing Features

- Syntax highlighting for markdown
- Line numbers
- Undo / redo
- Find and replace within the current note
- Auto-indent and soft-wrap

### Formatting Toolbar / Shortcuts

The editor must provide toolbar buttons and/or keyboard shortcuts for the following common operations:

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
| FR-07 | Toolbar and keyboard shortcuts for formatting (bold, italic, lists, checklists, etc.) | Must have |
| FR-08 | Checklists in preview mode are interactive and write state back to the file | Should have |
| FR-09 | Editor supports find and replace | Should have |
| FR-10 | User can choose and change the notes root directory | Must have |
| FR-11 | Drag-and-drop file/folder reordering in the directory tree | Nice to have |
| FR-12 | Split view showing editor and preview side by side | Should have |
| FR-13 | App remembers window size, position, and last-opened note across sessions | Should have |
| FR-14 | Auto-save or save-on-switch to prevent data loss | Should have |

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

- Full-text search across all notes
- Tag or metadata system (e.g., YAML front matter)
- Export to PDF or HTML
- Version history / git integration
- Theming and custom CSS for preview
- Plugin system for additional renderers or editor extensions
