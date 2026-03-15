# Data Model: Establishing Baseline Specs

**Date**: 2026-03-15
**Status**: Complete (documenting existing data model)

## Entities

### Note

A single markdown file on the local filesystem.

| Attribute | Type | Description |
|-----------|------|-------------|
| path | Absolute file path | Unique identifier; the file's location on disk |
| content | UTF-8 text | Raw markdown content of the note |
| modified | Boolean | Whether in-memory content differs from disk |

**Lifecycle**: Created via "+ Note" button or context menu → edited in
the markdown editor → auto-saved after 5s idle or manually via Ctrl+S
→ deleted via context menu with confirmation.

**Constraints**:
- MUST be a `.md` file
- MUST be within the configured notes root directory
- MUST use UTF-8 encoding

### Notes Directory

The user-selected root folder containing all notes and subfolders.

| Attribute | Type | Description |
|-----------|------|-------------|
| root_path | Absolute directory path | Top-level directory for all notes |

**Lifecycle**: Selected on first launch via file dialog → persisted in
settings → changeable via File menu → QFileSystemModel watches for
changes.

**Constraints**:
- MUST be a valid, readable directory
- MUST be user-writable (for creating/renaming/deleting notes)

### User Settings

Persisted user preferences stored via QSettings.

| Setting | Type | Default | Persisted |
|---------|------|---------|-----------|
| notes_root | string | "" (prompts on first launch) | Yes |
| last_file | string | "" | Yes |
| window_geometry | bytes | System default | Yes |
| window_state | bytes | System default | Yes |
| splitter_state | bytes | Equal split | Yes |
| view_mode | string | "split" | Yes |
| dark_mode | bool | false | Yes |
| emacs_mode | bool | false | Yes |
| font_size | int | 11 | Yes |

**Lifecycle**: Initialized with defaults on first run → updated
whenever the user changes a preference → restored on application
startup.

## Relationships

```text
Notes Directory (1) ──contains──> (many) Note
User Settings (1) ──references──> (1) Notes Directory
User Settings (1) ──references──> (0..1) Note (last_file)
```

## State Transitions

### Note States

```text
[Not Exists] ──create──> [Saved on Disk]
[Saved on Disk] ──open──> [Open in Editor, Unmodified]
[Open in Editor, Unmodified] ──edit──> [Open in Editor, Modified]
[Open in Editor, Modified] ──save/auto-save──> [Open in Editor, Unmodified]
[Open in Editor, *] ──close/open other──> [Saved on Disk]
[Saved on Disk] ──delete──> [Not Exists]
[Saved on Disk] ──rename──> [Saved on Disk] (new path)
[Saved on Disk] ──move──> [Saved on Disk] (new parent directory)
```

### View Mode States

```text
[Editor Only] ──Ctrl+Alt+2──> [Preview Only]
[Editor Only] ──Ctrl+Alt+3──> [Split View]
[Preview Only] ──Ctrl+Alt+1──> [Editor Only]
[Preview Only] ──Ctrl+Alt+3──> [Split View]
[Split View] ──Ctrl+Alt+1──> [Editor Only]
[Split View] ──Ctrl+Alt+2──> [Preview Only]
```
