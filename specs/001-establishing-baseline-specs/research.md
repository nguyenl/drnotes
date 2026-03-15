# Research: Establishing Baseline Specs

**Date**: 2026-03-15
**Status**: Complete (documenting existing decisions)

This research document captures the technology decisions already made
and implemented in DrNotes. No open questions remain.

## GUI Framework

**Decision**: PySide6 (Qt 6)

**Rationale**: Qt provides native-feeling widgets on all three target
platforms (Linux, macOS, Windows), a rich widget set including
QWebEngineView for HTML preview, and QSettings for cross-platform
preference storage. PySide6 is the official Python binding maintained
by the Qt Company.

**Alternatives considered**:
- Tkinter + ttkbootstrap: Simpler but lacks web engine for Mermaid
  rendering and advanced text editing features.
- pywebview: Would require a full web stack for the editor; Qt's
  QPlainTextEdit provides better native text editing performance.

## Markdown Rendering

**Decision**: `markdown` library with `pymdown-extensions`

**Rationale**: The `markdown` library is the most mature Python
markdown parser. `pymdown-extensions` adds GFM-compatible features
(task lists, strikethrough, fenced code blocks with syntax
highlighting via Pygments) without requiring a separate renderer.

**Alternatives considered**:
- mistune: Faster parsing but fewer extensions and less mature
  ecosystem for the specific features needed (task lists, highlight).
- commonmark-py: Strict CommonMark compliance but lacking GFM
  extensions out of the box.

## Diagram Rendering

**Decision**: Mermaid.js 10 via embedded QWebEngineView

**Rationale**: Mermaid.js is the industry standard for text-based
diagrams. Running it in QWebEngineView avoids shelling out to a CLI
tool and provides real-time rendering within the preview pane.

**Alternatives considered**:
- Mermaid CLI (mmdc): Requires Node.js installation; adds complexity
  to packaging and slows rendering due to process spawning.
- PlantUML: Requires Java runtime; different syntax than Mermaid
  which is more widely adopted in markdown ecosystems.

## Syntax Highlighting (Code Blocks)

**Decision**: Pygments via `pymdownx.highlight`

**Rationale**: Pygments supports 500+ languages and integrates
directly with pymdown-extensions for seamless code block highlighting
in the preview. No additional dependencies needed.

**Alternatives considered**:
- highlight.js (client-side): Would require loading a JS library in
  the webview; Pygments generates CSS classes server-side which is
  simpler and more reliable.

## Settings Persistence

**Decision**: QSettings (platform-native storage)

**Rationale**: QSettings uses the platform-native storage mechanism
(Windows registry, macOS plist, Linux INI files). It requires zero
configuration and handles serialization automatically.

**Alternatives considered**:
- JSON config file: More portable but requires manual file management,
  path resolution, and error handling. QSettings handles all of this.
- SQLite: Overkill for key-value preferences.

## Packaging

**Decision**: PyInstaller

**Rationale**: PyInstaller produces a single-directory or single-file
binary that bundles the Python interpreter and all dependencies. It
has mature support for PySide6 and handles hidden imports well.

**Alternatives considered**:
- Briefcase (BeeWare): Less mature PySide6 support at time of
  selection.
- Nuitka: Compiles to C which can improve performance but adds
  significant build complexity and longer build times.

## Architecture Pattern

**Decision**: Signal-based mediator pattern with MainWindow as hub

**Rationale**: All 5 widgets (editor, preview, directory tree, search
panel, toolbar) communicate exclusively through Qt signals routed via
MainWindow. Widgets never reference each other directly. This keeps
widgets independently testable and loosely coupled.

**Alternatives considered**:
- Direct widget references: Simpler initially but creates tight
  coupling that makes testing and refactoring difficult.
- Event bus / message broker: Over-engineered for a 5-widget desktop
  app; Qt signals already provide this pattern natively.
