<!-- Sync Impact Report
Version change: N/A → 1.0.0 (initial ratification)
Modified principles: N/A (first version)
Added sections:
  - Core Principles (5 principles)
  - Technology Constraints
  - Development Workflow
  - Governance
Removed sections: N/A
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ compatible (Constitution Check section is generic)
  - .specify/templates/spec-template.md ✅ compatible (no constitution-specific references)
  - .specify/templates/tasks-template.md ✅ compatible (no constitution-specific references)
Follow-up TODOs: None
-->

# DrNotes Constitution

## Core Principles

### I. Local-First, Plain Files

All user data MUST be stored as plain `.md` files on the local
filesystem. No cloud services, no databases, no proprietary metadata
formats. The user's folder of markdown files is the single canonical
data store. Files MUST use UTF-8 encoding.

**Rationale**: Users own their data unconditionally. Notes MUST remain
readable and portable outside of DrNotes by any text editor or tool
that understands markdown.

### II. Cross-Platform Compatibility

Every feature MUST work on Linux, macOS, and Windows from a single
Python codebase. Platform-specific behavior (keyboard modifiers, file
dialogs, path separators) MUST be handled transparently so users on
any platform have a native-feeling experience.

**Rationale**: DrNotes targets all three major desktop platforms.
Platform-specific code MUST be isolated behind abstractions so it
never leaks into feature logic.

### III. Simplicity & Focus

DrNotes is a focused markdown note-taking tool, not a platform.
Features MUST directly serve the note-taking workflow. No plugin
systems, no extension APIs, no cloud sync, no mobile targets in the
current scope. When in doubt, leave it out — YAGNI applies.

**Rationale**: Complexity is the primary risk to maintainability and
user experience. Every added feature increases surface area for bugs
and cognitive load.

### IV. Data Integrity

The application MUST NOT lose user data under any circumstance.
Auto-save MUST be enabled by default. File operations (rename, move,
delete) MUST confirm destructive actions with the user. Writes MUST
be atomic or recoverable — a crash during save MUST NOT corrupt the
file.

**Rationale**: For a local-first tool with no cloud backup, data loss
is catastrophic and unrecoverable.

### V. Responsive & Offline

The application MUST require zero network access for all core
functionality. Launch time MUST remain under 3 seconds on modern
hardware. The editor and preview MUST remain responsive with notes up
to 10,000 lines. Distribution MUST produce a single installable
artifact per platform with no separate runtime required by end users.

**Rationale**: A local note-taking app that is slow, network-dependent,
or hard to install fails its core value proposition.

## Technology Constraints

- **Language**: Python 3.10+
- **GUI Framework**: PySide6 (Qt 6)
- **Markdown Rendering**: `markdown` library with `pymdown-extensions`
- **Syntax Highlighting**: Pygments
- **Diagram Rendering**: Mermaid.js 10 via embedded QWebEngineView
- **Packaging**: PyInstaller for single-binary distribution
- **Network**: No outbound network calls permitted in the application.
  All rendering (including Mermaid diagrams) MUST use bundled or
  embedded assets.
- **Settings**: QSettings for persisting user preferences (theme, font
  size, window geometry, emacs mode, notes root path)

## Development Workflow

- **Branching**: Feature branches off `main`; merge via pull request.
- **Testing**: New features and bug fixes SHOULD include verification
  steps. Changes MUST NOT break existing functionality.
- **Code Style**: Follow existing project conventions. Use the project
  structure under `src/drnotes/` with widgets in `src/drnotes/widgets/`.
- **Commits**: Each commit SHOULD represent a single logical change
  with a clear, descriptive message.
- **Reviews**: All changes to core editing, file I/O, or data storage
  logic MUST be reviewed for data integrity implications before merge.

## Governance

This constitution defines the non-negotiable principles for the
DrNotes project. All feature proposals, pull requests, and
architectural decisions MUST be evaluated against these principles.

- **Amendments**: Any change to this constitution MUST be documented
  with a version bump, rationale, and migration plan if existing code
  is affected.
- **Versioning**: The constitution follows semantic versioning:
  - MAJOR: Principle removal or backward-incompatible redefinition
  - MINOR: New principle or materially expanded guidance
  - PATCH: Clarifications, wording, or non-semantic refinements
- **Compliance**: Feature specifications and implementation plans MUST
  include a constitution check confirming alignment with all active
  principles.
- **Conflicts**: When this constitution conflicts with other project
  documentation, this constitution takes precedence.

**Version**: 1.0.0 | **Ratified**: 2026-03-15 | **Last Amended**: 2026-03-15
