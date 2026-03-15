# Feature Specification: Establishing Baseline Specs

**Feature Branch**: `001-establishing-baseline-specs`
**Created**: 2026-03-15
**Status**: Complete (baseline capture of existing features)
**Input**: User description: "Analyze the project and port over specs that have already been completed."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and Organize Notes (Priority: P1)

A user launches DrNotes, selects a notes root directory, and begins
creating markdown notes organized into folders. They create new notes,
rename them, move them between folders via drag-and-drop, and delete
notes they no longer need.

**Why this priority**: Core note management is the fundamental value
proposition — without it, no other feature matters.

**Independent Test**: Open the app, select a directory, create a note,
write content, rename it, create a folder, drag the note into the
folder, and verify the file system reflects all changes.

**Acceptance Scenarios**:

1. **Given** no notes directory is configured, **When** the user
   launches the app, **Then** a dialog prompts them to select a root
   directory and the tree populates with its contents.
2. **Given** a notes directory is set, **When** the user clicks
   "+ Note", **Then** a new `.md` file is created and opened in the
   editor.
3. **Given** a note exists, **When** the user right-clicks and selects
   "Rename", **Then** the file is renamed on disk and the tree updates.
4. **Given** a note exists, **When** the user drags it into a
   different folder, **Then** the file moves on disk accordingly.
5. **Given** a note exists, **When** the user deletes it via context
   menu, **Then** a confirmation dialog appears before the file is
   removed.

---

### User Story 2 - Write and Format Markdown (Priority: P1)

A user writes markdown in the editor with syntax highlighting, using
toolbar buttons and keyboard shortcuts for formatting (bold, italic,
headings, lists, code blocks, links, images, blockquotes). Smart list
continuation and indent/outdent streamline editing.

**Why this priority**: Rich editing is the primary interaction loop
that users spend most of their time in.

**Independent Test**: Open a note, type markdown, use each toolbar
button and shortcut, verify formatting is applied correctly and syntax
highlighting updates in real time.

**Acceptance Scenarios**:

1. **Given** text is selected, **When** the user presses Ctrl+B,
   **Then** the text is wrapped with `**` markers.
2. **Given** the cursor is on a line, **When** the user presses
   Ctrl+1, **Then** the line is prefixed with `# `.
3. **Given** the cursor is at the end of a list item `- foo`,
   **When** the user presses Enter, **Then** a new line starting
   with `- ` is inserted.
4. **Given** the cursor is at the end of an ordered list item
   `1. foo`, **When** the user presses Enter, **Then** a new line
   starting with `2. ` is inserted.
5. **Given** a line is selected, **When** the user presses Tab,
   **Then** the line is indented by 4 spaces.

---

### User Story 3 - Preview Markdown with Live Rendering (Priority: P1)

A user views a live-rendered preview of their markdown alongside or
instead of the editor. The preview supports CommonMark/GFM rendering,
syntax-highlighted code blocks, interactive checklists, and Mermaid
diagrams. Three view modes are available: Editor Only, Preview Only,
and Split View with synchronized scrolling.

**Why this priority**: Live preview is the defining feature that
differentiates DrNotes from a plain text editor.

**Independent Test**: Open a note with varied markdown (headings,
code blocks, checklists, a Mermaid diagram), switch between view
modes, verify rendering is correct and scroll sync works in split
view.

**Acceptance Scenarios**:

1. **Given** a note with markdown is open, **When** the user switches
   to Split View (Ctrl+Alt+3), **Then** the editor and preview appear
   side by side with the preview reflecting the current content.
2. **Given** Split View is active, **When** the user scrolls the
   editor, **Then** the preview scrolls proportionally.
3. **Given** a note contains a `- [ ] task` item, **When** the user
   clicks the checkbox in the preview, **Then** the markdown file is
   updated to `- [x] task`.
4. **Given** a note contains a fenced mermaid code block with valid
   syntax, **When** the preview renders, **Then** a diagram is
   displayed.
5. **Given** a note contains a fenced mermaid code block with invalid
   syntax, **When** the preview renders, **Then** an inline error
   message is shown instead of failing silently.

---

### User Story 4 - Search and Navigate Notes (Priority: P2)

A user searches for text across all notes in their directory using
full-text search (Ctrl+Shift+F). Results are grouped by file with
line previews, and double-clicking a result opens the file at that
line. Within a single note, the user uses Find/Replace (Ctrl+F).

**Why this priority**: Search becomes essential as the note collection
grows, but is not needed for basic note-taking.

**Independent Test**: Create multiple notes with known content, use
Ctrl+Shift+F to search for a term, verify results are grouped by
file, double-click a result to navigate, then use Ctrl+F within a
note to find and replace text.

**Acceptance Scenarios**:

1. **Given** multiple notes exist, **When** the user presses
   Ctrl+Shift+F and enters a query, **Then** matching lines are
   displayed grouped by file with line numbers and previews.
2. **Given** search results are displayed, **When** the user
   double-clicks a result, **Then** the file opens and the editor
   scrolls to that line.
3. **Given** a note is open, **When** the user presses Ctrl+F,
   **Then** a find/replace bar appears with case-sensitive toggle.
4. **Given** the find bar is open with a match highlighted, **When**
   the user clicks "Replace All", **Then** all occurrences are
   replaced.

---

### User Story 5 - Customize Appearance and Editing Mode (Priority: P2)

A user customizes their experience by toggling dark/light mode,
adjusting font size, and optionally enabling Emacs-style keybindings.
All preferences persist across sessions.

**Why this priority**: Customization improves comfort for extended use
but is not required for core functionality.

**Independent Test**: Toggle dark mode, adjust font size up/down/reset,
enable Emacs mode, close and reopen the app, verify all settings
persist.

**Acceptance Scenarios**:

1. **Given** light mode is active, **When** the user presses
   Ctrl+Alt+D, **Then** dark mode applies to the editor, UI chrome,
   and preview pane.
2. **Given** font size is at default (11pt), **When** the user
   presses Ctrl+=, **Then** font size increases in both editor and
   preview.
3. **Given** font size has been changed, **When** the user presses
   Ctrl+0, **Then** font size resets to 11pt.
4. **Given** Emacs mode is disabled, **When** the user presses
   Ctrl+Alt+E, **Then** 20+ Emacs keybindings become active
   (Ctrl+F moves forward, Ctrl+K kills to end of line, etc.).
5. **Given** any of the above settings are changed, **When** the
   user closes and reopens the app, **Then** all settings are
   restored.

---

### User Story 6 - Auto-Save and Session Persistence (Priority: P2)

The application automatically saves the current note after 5 seconds
of idle time, remembers window geometry and the last-opened file, and
displays the current file path and last-saved timestamp in a status
bar.

**Why this priority**: Prevents data loss and provides a seamless
resume experience, but the user can manually save with Ctrl+S.

**Independent Test**: Edit a note and wait 5 seconds without typing,
verify the status bar shows the save timestamp, close and reopen the
app, verify the same file is open with the same window size and
position.

**Acceptance Scenarios**:

1. **Given** a note has unsaved changes, **When** 5 seconds pass
   without typing, **Then** the file is saved and the status bar
   timestamp updates.
2. **Given** a file is open, **When** the user looks at the status
   bar, **Then** the left side shows the absolute file path and
   the right side shows the last-saved timestamp.
3. **Given** the user closes the app, **When** they reopen it,
   **Then** the window geometry, splitter positions, and last-opened
   file are restored.

---

### Edge Cases

- What happens when the user selects a notes directory that contains
  no `.md` files? The tree displays empty; the user can create new
  notes.
- What happens when a file is deleted externally while open in the
  editor? QFileSystemModel detects the change and updates the tree;
  the editor retains the content in memory until the next file open.
- What happens when the user enters invalid regex in the search panel?
  The search gracefully handles the error without crashing.
- What happens when a Mermaid diagram has syntax errors? An inline
  error message is shown in the preview rather than failing silently.
- What happens when the user tries to rename a file to a name that
  already exists? A confirmation dialog warns the user that the target
  file exists and asks whether to overwrite. The rename proceeds only
  if the user explicitly confirms.

## Clarifications

### Session 2026-03-15

- Q: How should the Mermaid.js offline conflict be resolved (CDN vs constitution)? → A: Bundle Mermaid.js locally as a static asset in the package.
- Q: Should file saves use an atomic write pattern to prevent crash corruption? → A: Yes — implement write-to-temp + os.rename for all file saves.
- Q: What should happen when renaming a file to a name that already exists? → A: Show a confirmation dialog asking whether to overwrite the existing file.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to create, open, edit, and save
  markdown notes as plain `.md` files on the local filesystem. File
  saves MUST be atomic (write to temporary file, then rename) so that
  a crash during save does not corrupt the file.
- **FR-002**: System MUST allow users to create, rename, and delete
  folders to organize notes.
- **FR-003**: System MUST display a directory tree panel showing the
  folder/file hierarchy of the notes root, filtered to `.md` files.
- **FR-004**: System MUST provide markdown syntax highlighting in the
  editor with support for headings, bold, italic, strikethrough,
  inline code, links, images, blockquotes, lists, checklists, code
  block markers, and horizontal rules.
- **FR-005**: System MUST render markdown to HTML in a preview pane
  using CommonMark/GFM standards including tables, strikethrough,
  task lists, and syntax-highlighted code blocks.
- **FR-006**: System MUST render fenced mermaid code blocks as
  diagrams (flowcharts, sequence, Gantt, class, state, ER, pie) and
  display inline error messages for invalid syntax. Mermaid.js MUST
  be bundled locally as a static asset — no CDN or network access
  permitted for diagram rendering.
- **FR-007**: System MUST provide a formatting toolbar with buttons
  and keyboard shortcuts for bold, italic, strikethrough, headings
  (H1-H6), unordered/ordered/checklists, code block, link, image,
  blockquote, and horizontal rule.
- **FR-008**: System MUST make preview checklists interactive —
  clicking a checkbox toggles its state and writes the change back
  to the `.md` file.
- **FR-009**: System MUST provide find and replace within the current
  note with case-sensitive toggle, next/previous navigation, and
  replace/replace-all operations.
- **FR-010**: System MUST allow the user to select and change the
  notes root directory.
- **FR-011**: System MUST support drag-and-drop to move files between
  folders in the directory tree.
- **FR-012**: System MUST provide three view modes — Editor Only,
  Preview Only, and Split View — with synchronized scrolling in
  Split View.
- **FR-013**: System MUST persist window size, position, splitter
  state, and last-opened file across sessions.
- **FR-014**: System MUST auto-save the current note after 5 seconds
  of idle time.
- **FR-015**: System MUST provide a dark/light mode toggle that
  applies to editor, UI chrome, and preview, persisting across
  sessions.
- **FR-016**: System MUST provide an optional Emacs mode with 20+
  keybindings for navigation, kill/yank, and mark-based selection,
  persisting across sessions.
- **FR-017**: System MUST display a status bar showing the current
  file's absolute path and last-saved timestamp, updating immediately
  on each save.
- **FR-018**: System MUST provide full-text search across all notes
  with results grouped by file, showing line numbers and previews,
  and supporting navigation to the match location.
- **FR-019**: System MUST provide toolbar buttons for view mode
  switching, dark/light mode toggle, and Emacs mode toggle using
  system theme icons with text fallback.
- **FR-020**: System MUST provide adjustable font size via menu,
  toolbar, and keyboard shortcuts (Ctrl+=, Ctrl+-, Ctrl+0),
  persisting across sessions with min 6pt and max 72pt.

### Key Entities

- **Note**: A plain `.md` file on the local filesystem, identified by
  its absolute path. Contains UTF-8 encoded markdown text.
- **Notes Directory**: A user-selected root folder. All notes and
  subfolders within it are managed by the directory tree.
- **User Settings**: Persisted preferences including notes root, last
  file, window geometry, view mode, dark mode, emacs mode, and font
  size.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a note, write content, and find it
  again via search within 30 seconds of first launch.
- **SC-002**: The application launches in under 3 seconds on modern
  hardware.
- **SC-003**: The editor and preview remain responsive (no visible
  lag) with notes up to 10,000 lines.
- **SC-004**: No user data is lost during normal operation — auto-save
  ensures unsaved work is persisted within 5 seconds of the last edit.
- **SC-005**: The application works fully offline with zero network
  access required for all features.
- **SC-006**: All 20+ keyboard shortcuts produce the correct markdown
  formatting output on the first use.
- **SC-007**: Mermaid diagrams render correctly for all supported
  types (flowchart, sequence, Gantt, class, state, ER, pie).
- **SC-008**: Theme, font size, Emacs mode, view mode, and window
  geometry all persist correctly across application restarts.
- **SC-009**: Cross-file search returns all matching results grouped
  by file with accurate line numbers.
- **SC-010**: The application runs on Linux, macOS, and Windows from
  a single codebase without platform-specific user configuration.
