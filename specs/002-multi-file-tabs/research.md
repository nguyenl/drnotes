# Research: Tabbed Note Editing

## Decision 1: Use `QTabWidget` for the open-note strip

- **Decision**: Implement the open-note strip with Qt's built-in
  `QTabWidget` and enable closable tabs.
- **Rationale**: The application already uses standard Qt widgets, and
  `QTabWidget` provides selection, close buttons, overflow handling,
  and cross-platform behavior without adding custom drawing or event
  code.
- **Alternatives considered**:
  - A custom tab bar: rejected because it adds UI complexity and more
    platform-specific polish work.
  - A list of open files separate from the editor: rejected because it
    would not match the requested tabbed workflow.

## Decision 2: Give each tab its own editor/preview workspace

- **Decision**: Each tab will own a workspace composed of one
  `MarkdownEditor` and one `PreviewPanel`.
- **Rationale**: The existing single-document design keeps important
  state inside the editor and preview widgets, including modified
  status, find/replace UI, preview scroll state, and checkbox updates.
  Preserving those widgets per tab avoids complicated state swapping.
- **Alternatives considered**:
  - Reusing one editor and swapping file contents: rejected because it
    would lose per-note UI state and make duplicate-open handling more
    fragile.
  - Splitting editor and preview ownership across separate registries:
    rejected because it increases synchronization risk.

## Decision 3: Route toolbar and menu actions through the active tab

- **Decision**: `MainWindow` will dispatch formatting, find, save,
  preview refresh, and checkbox handling to the currently active
  workspace instead of staying permanently wired to one editor.
- **Rationale**: The existing toolbar and menus are global window
  controls, so the least disruptive change is to make them target the
  active workspace on demand.
- **Alternatives considered**:
  - Reconnecting every action signal on each tab switch: rejected
    because it is error-prone and harder to maintain.
  - Duplicating toolbars per tab: rejected because it clutters the UI
    and conflicts with the current layout.

## Decision 4: Track open tabs by canonical file path

- **Decision**: Keep a one-tab-per-file registry keyed by absolute file
  path so reopening an existing note activates its tab instead of
  creating a duplicate.
- **Rationale**: The feature spec explicitly forbids duplicate tabs for
  the same note, and the absolute path is the most stable identifier in
  this local-filesystem application.
- **Alternatives considered**:
  - Matching by file name only: rejected because different folders can
    contain notes with the same name.
  - Allowing duplicates and letting the user manage them manually:
    rejected because it weakens the requested behavior.

## Decision 5: Disambiguate same-name files with contextual tab labels

- **Decision**: Default tab text will use the file name, and when two
  open files share that name, each tab label will add a short relative
  path suffix while keeping the full path available as a tooltip.
- **Rationale**: This keeps most tabs compact while still giving users
  a clear way to tell same-name notes apart.
- **Alternatives considered**:
  - Always showing the full path in the tab title: rejected because it
    makes tabs too wide.
  - Leaving duplicate names unchanged: rejected because it fails the
    distinguishability requirement.

## Decision 6: Save modified content before tab close and clear the UI when no tabs remain

- **Decision**: Closing a tab will invoke the existing save path for
  modified content before removal, and closing the last remaining tab
  will reset the path label, status bar, and preview/editor area to an
  explicit empty state.
- **Rationale**: The constitution requires data integrity, and the
  feature spec requires a clear no-file-open state after the final tab
  closes.
- **Alternatives considered**:
  - Asking for confirmation on every tab close: rejected because the
    existing product leans on autosave rather than close prompts.
  - Leaving stale editor content visible after the final close:
    rejected because it misrepresents which note is active.
