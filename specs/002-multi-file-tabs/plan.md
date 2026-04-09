# Implementation Plan: Tabbed Note Editing

**Branch**: `002-multi-file-tabs` | **Date**: 2026-04-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-multi-file-tabs/spec.md`

**Note**: This plan covers the addition of closable multi-file tabs to
the existing DrNotes desktop application.

## Summary

DrNotes will replace its single-document editor area with a tabbed
workspace that can keep multiple markdown files open at once. Each tab
will own its own editor and preview state, while `MainWindow` will
route existing toolbar, search, theme, autosave, and status-bar flows
to whichever tab is active. Duplicate opens will focus the existing
tab, closing a tab will preserve recent edits using the existing atomic
save path, and closing the final tab will return the UI to a clean
no-file-open state.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: PySide6 >=6.6.0, markdown >=3.5, pymdown-extensions >=10.0, Pygments >=2.17  
**Storage**: Plain `.md` files on the local filesystem; QSettings for global preferences and last-opened file  
**Testing**: `pytest` for lightweight non-GUI regression checks plus manual GUI validation for tab flows  
**Target Platform**: Linux, macOS, Windows  
**Project Type**: Cross-platform desktop application  
**Performance Goals**: Launch remains under 3 seconds; switching among at least 5 open notes feels immediate; editing and preview stay responsive for notes up to 10,000 lines  
**Constraints**: Fully offline; no data loss on tab close; single-window scope; preserve existing atomic saves, search navigation, and view modes  
**Scale/Scope**: Single-user note-taking app; one window with at least 5 simultaneous open-note tabs; feature touches the main window plus editor/preview composition and settings-aware UI state

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Local-First, Plain Files | PASS | Tabs only manage open `.md` files already stored on disk; no new storage layer or metadata database is introduced. |
| II. Cross-Platform Compatibility | PASS | The design relies on Qt tab widgets and existing Python code paths already shared across Linux, macOS, and Windows. |
| III. Simplicity & Focus | PASS | The feature is a direct editing workflow improvement and stays within the current desktop note-taking scope. |
| IV. Data Integrity | PASS | Modified tabs will continue to save through the existing atomic write path and will save before close. |
| V. Responsive & Offline | PASS | No network calls or background services are added; the design keeps all tab behavior local to the current process. |

**Gate Result**: PASS - no constitution violations identified before research.

**Post-Design Check**: PASS - the Phase 1 design keeps one workspace per
open file, reuses existing widgets, and introduces no conflicts with
local-first, offline, or data-integrity requirements.

## Project Structure

### Documentation (this feature)

```text
specs/002-multi-file-tabs/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── tabbed-workspace.md
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/drnotes/
├── main_window.py          # Main window orchestration, timers, status updates
├── settings.py             # Persisted preferences and last-opened file state
└── widgets/
    ├── __init__.py          # Widget exports
    ├── editor.py            # MarkdownEditor behavior and file save/open logic
    ├── preview.py           # PreviewPanel rendering and checkbox bridge
    ├── toolbar.py           # Formatting toolbar actions
    └── workspace_tabs.py    # Planned tab container + per-tab workspace composition

tests/
├── test_preview_template.py
└── test_workspace_tabs.py   # Planned tab-management regression coverage
```

**Structure Decision**: Keep the current single-project desktop layout
under `src/drnotes/`. Add one focused widget module for the tabbed
workspace rather than spreading tab state across `MainWindow`,
`MarkdownEditor`, and `PreviewPanel`.

## Phase 0: Research

See [research.md](research.md) for design decisions covering:

- Qt tab container choice
- Per-tab workspace ownership
- Active-tab signal routing
- Duplicate tab detection
- Tab title disambiguation for same-name files
- Close and last-tab empty-state behavior

## Phase 1: Design & Contracts

See [data-model.md](data-model.md), [quickstart.md](quickstart.md), and
[contracts/tabbed-workspace.md](contracts/tabbed-workspace.md).

The design introduces a dedicated per-tab workspace model so each open
file keeps its own editor text, preview state, modified flag, and file
identity while the main window owns global actions such as theme,
view-mode, and status-bar updates.

## Complexity Tracking

> No constitution violations to justify. All principles satisfied.
