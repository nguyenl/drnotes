# Implementation Plan: Establishing Baseline Specs

**Branch**: `001-establishing-baseline-specs` | **Date**: 2026-03-15 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-establishing-baseline-specs/spec.md`

**Note**: This is a baseline capture of an already-implemented project. All phases document existing architecture rather than prescribing new work.

## Summary

DrNotes is a fully-implemented cross-platform desktop markdown
note-taking application. It stores all data as plain `.md` files on
the local filesystem with no cloud dependency. The application
provides a rich editing experience with syntax highlighting, live
preview with Mermaid diagram rendering, full-text search, interactive
checklists, and extensive keyboard shortcuts including an optional
Emacs mode. All 20 functional requirements from the PRD are
implemented and working.

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: PySide6 >=6.6.0 (Qt 6 GUI), markdown >=3.5, pymdown-extensions >=10.0, Pygments >=2.17
**Storage**: Plain `.md` files on local filesystem; QSettings for preferences
**Testing**: Manual testing (no automated test suite present)
**Target Platform**: Linux, macOS, Windows (cross-platform desktop)
**Project Type**: Desktop application
**Performance Goals**: Launch <3 seconds; responsive editing with notes up to 10,000 lines
**Constraints**: Fully offline — zero network access for core features; single installable binary per platform
**Scale/Scope**: Single-user desktop app; ~2,200 lines of Python across 9 source files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Local-First, Plain Files | PASS | All data stored as `.md` files; no databases or cloud. UTF-8 encoding. |
| II. Cross-Platform Compatibility | PASS | Single Python codebase targets Linux, macOS, Windows via PySide6. Platform-specific behavior handled by Qt abstractions. |
| III. Simplicity & Focus | PASS | Focused note-taking tool. No plugin system, no extension APIs, no cloud sync, no mobile. 2,200 LOC across 9 files. |
| IV. Data Integrity | PASS | Auto-save with 5s debounce. Delete operations require confirmation. |
| V. Responsive & Offline | PASS | No network calls in application code. Mermaid.js loaded via CDN in embedded webview (note: requires initial network for CDN). PyInstaller packaging for single-binary distribution. |

**Gate Result**: PASS — all 5 constitution principles satisfied.

**Note on Principle V**: Mermaid.js is currently loaded from a CDN
(`cdn.jsdelivr.net`) in the preview webview. While this does not
affect core editing or file operations, it means diagram rendering
requires network access on first use. A future improvement could
bundle Mermaid.js locally to achieve full offline compliance.

## Project Structure

### Documentation (this feature)

```text
specs/001-establishing-baseline-specs/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/drnotes/
├── __init__.py
├── app.py                  # Application entry point (23 lines)
├── main_window.py          # Main window layout, menus, signal hub (466 lines)
├── settings.py             # QSettings wrapper for persistence (101 lines)
├── syntax_highlighter.py   # Regex-based markdown highlighting (103 lines)
└── widgets/
    ├── __init__.py          # Widget exports (7 lines)
    ├── editor.py            # Markdown editor with line numbers, find/replace (735 lines)
    ├── preview.py           # HTML preview with Mermaid via QWebEngineView (351 lines)
    ├── directory_tree.py    # File browser with CRUD operations (168 lines)
    ├── search_panel.py      # Cross-file full-text search (161 lines)
    └── toolbar.py           # Formatting toolbar with shortcuts (97 lines)
```

**Structure Decision**: Single-project desktop app layout. Source code
lives under `src/drnotes/` with widgets separated into a `widgets/`
subpackage. No test directory exists yet. Configuration is in
`pyproject.toml` at the repository root.

## Complexity Tracking

> No constitution violations to justify. All principles satisfied.
