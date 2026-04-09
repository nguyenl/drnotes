# Data Model: Tabbed Note Editing

## Overview

The feature introduces runtime UI state for multiple open notes within
one window. No new persistent note format is added; note content
remains stored as plain markdown files on disk.

## Entities

### OpenNoteTab

- **Purpose**: Represents one open note in the tab strip.
- **Fields**:
  - `file_path`: absolute path to the markdown file
  - `relative_path`: path relative to the notes root for display
  - `display_title`: user-visible tab label
  - `tooltip_path`: full path shown on hover
  - `is_active`: whether this tab is currently selected
  - `is_modified`: whether the editor contains unsaved changes
- **Validation rules**:
  - `file_path` must be unique among open tabs
  - `file_path` must reference a markdown file that the app can read
  - `display_title` must be updated when open tabs create a same-name
    collision

### WorkspaceViewState

- **Purpose**: Captures per-tab editing and preview state that should
  remain stable while the tab stays open.
- **Fields**:
  - `editor_text`: current markdown text in memory
  - `cursor_position`: current editor cursor location
  - `editor_scroll_fraction`: editor scroll position
  - `preview_scroll_fraction`: preview scroll position
  - `view_mode`: editor-only, preview-only, or split
- **Validation rules**:
  - `view_mode` must remain one of the application's existing modes
  - scroll fractions must stay within `0.0` to `1.0`

### TabRegistry

- **Purpose**: Maintains the relationship between open file paths and
  their workspace tabs.
- **Fields**:
  - `open_paths`: ordered collection of currently open file paths
  - `active_path`: file path of the selected tab, if any
  - `path_to_tab`: lookup from file path to tab/workspace reference
- **Validation rules**:
  - a file path may appear at most once
  - `active_path` must be empty when no tabs are open
  - `active_path` must match one member of `open_paths` when tabs exist

## Relationships

- One `TabRegistry` contains many `OpenNoteTab` records.
- Each `OpenNoteTab` owns one `WorkspaceViewState`.
- The active workspace shown in the main window is determined by
  `TabRegistry.active_path`.

## State Transitions

### Tab Lifecycle

1. `Closed` -> `OpenInactive`
   Trigger: a file is opened while another tab is active.
2. `Closed` -> `OpenActive`
   Trigger: a file is opened when no tabs exist, or the newly opened
   tab becomes selected immediately.
3. `OpenInactive` -> `OpenActive`
   Trigger: the user selects the tab or reopens the same file.
4. `OpenActive` -> `Modified`
   Trigger: the user edits the note content.
5. `Modified` -> `OpenActive`
   Trigger: autosave or manual save completes successfully.
6. `OpenActive` -> `Closed`
   Trigger: the user closes the tab and any pending changes are saved.

### Final Tab Close

1. `OpenActive` -> `Closed`
   Trigger: the last tab is closed.
2. `Closed` -> `NoActiveNote`
   Result: path label, status bar, and workspace area return to the
   application's empty state.
