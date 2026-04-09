# Feature Specification: Tabbed Note Editing

**Feature Branch**: `002-multi-file-tabs`
**Created**: 2026-04-08
**Status**: Draft
**Input**: User description: "Add tabs so that I can open multiple files at the same time. Each tab can be closed."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Keep Multiple Notes Open (Priority: P1)

A user opens several notes during one editing session and keeps them
available at the same time, switching between them without losing
their place or reopening files from the notes list.

**Why this priority**: The core value of the request is being able to
work across more than one note at once. Without this, the feature does
not exist.

**Independent Test**: Open three different notes, confirm that each
appears as its own tab, switch among them, and verify that each note's
content and context remain available without reopening the file.

**Acceptance Scenarios**:

1. **Given** one note is already open, **When** the user opens a
   second note, **Then** the second note opens in a new tab and the
   first note remains open in its own tab.
2. **Given** multiple tabs are open, **When** the user selects a
   different tab, **Then** that tab becomes the active note and the
   editing area updates to show that note's content.
3. **Given** a note is already open in a tab, **When** the user opens
   that same note again from navigation or search, **Then** the
   existing tab becomes active instead of creating a duplicate tab.
4. **Given** multiple notes are open, **When** the user looks at the
   tab strip, **Then** each open note is identifiable as a separate
   tab.

---

### User Story 2 - Close Tabs Without Losing Work (Priority: P1)

A user closes notes they no longer need in the current session while
keeping the remaining notes open and their working context intact.

**Why this priority**: Closable tabs are required for tabs to stay
manageable during real use. Without close behavior, the feature would
quickly become cluttered and frustrating.

**Independent Test**: Open multiple notes, edit one of them, close a
non-active tab and the active tab, and verify the remaining tabs stay
open and the edited note content is not lost.

**Acceptance Scenarios**:

1. **Given** multiple tabs are open, **When** the user closes one
   tab, **Then** only that tab is removed and the other open tabs
   remain available.
2. **Given** the active tab is closed while other tabs remain,
   **When** the close action completes, **Then** another open tab
   becomes active immediately.
3. **Given** a tab contains recent edits, **When** the user closes
   that tab, **Then** the note's latest content is preserved before
   the tab disappears.
4. **Given** the last remaining tab is closed, **When** no tabs are
   left open, **Then** the application returns to a clear no-file-open
   state instead of showing stale note content.

---

### User Story 3 - Navigate Into Tabs From Other Flows (Priority: P2)

A user continues using existing navigation features, such as note-tree
selection and search results, and those flows open or focus tabs
without changing how the user discovers notes.

**Why this priority**: Tabs should improve existing workflows rather
than forcing users to learn a different way to open files.

**Independent Test**: Open one note from the note tree, open another
from search results, reopen the first note from the tree, and confirm
that navigation activates the correct tab without creating duplicates.

**Acceptance Scenarios**:

1. **Given** the user opens a note from the notes list, **When** that
   note is not already open, **Then** it opens in a new tab and
   becomes active.
2. **Given** the user opens a search result for a note that is already
   open, **When** the result is activated, **Then** the existing tab
   becomes active and the note jumps to the selected match location.
3. **Given** the user switches tabs after opening notes from different
   entry points, **When** the active tab changes, **Then** the visible
   file path and note context update to match the active note.

### Edge Cases

- What happens when the user tries to open the same note multiple
  times from different entry points? The system reuses the existing
  tab instead of opening duplicates.
- What happens when two open notes have the same file name in
  different folders? The tab presentation provides enough context for
  the user to tell them apart.
- What happens when the user closes the final remaining tab? The
  application shows a clear empty state with no active note selected.
- What happens when many tabs are open and they no longer fit in the
  available width? The tab strip remains navigable so every open tab
  can still be reached and closed.
- What happens when an open note is removed or renamed outside the
  application? The tab remains understandable to the user and does not
  silently redirect to different note content.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to keep multiple note files open
  at the same time within one application window.
- **FR-002**: System MUST represent each open note as its own tab in a
  visible tab strip.
- **FR-003**: System MUST open a newly selected note in a new tab when
  that note is not already open.
- **FR-004**: System MUST activate the existing tab instead of opening
  a duplicate when the user selects a note that is already open.
- **FR-005**: System MUST let users close any open tab directly from
  the tab itself.
- **FR-006**: System MUST preserve the latest note content before a
  tab closes so that closing a tab does not discard recent edits.
- **FR-007**: System MUST keep the remaining open tabs available after
  any individual tab is closed.
- **FR-008**: System MUST assign a new active tab immediately after
  the active tab is closed if other tabs remain open.
- **FR-009**: System MUST return to a no-file-open state when the last
  remaining tab is closed.
- **FR-010**: System MUST update the visible editing context,
  including the displayed file identity, to match the currently active
  tab.
- **FR-011**: System MUST support opening or activating tabs from
  existing note-entry flows, including direct note navigation and
  search results.
- **FR-012**: System MUST preserve location-based navigation when a
  note is opened from a search result so the user lands on the
  selected match within the active tab.
- **FR-013**: System MUST provide enough tab labeling or contextual
  detail for users to distinguish open notes that share the same file
  name.

### Key Entities *(include if feature involves data)*

- **Open Tab**: A user-visible workspace entry for one open note,
  including the note identity, display label, active state, and close
  availability.
- **Active Note Context**: The currently selected note state reflected
  in the editor, preview, visible path information, and navigation
  position.

## Assumptions

- Tabs apply to note files only; folders, searches, and settings do
  not open as tabs.
- The feature is limited to opening, switching, and closing tabs
  within the current application window.
- Restoring all previously open tabs on the next launch is out of
  scope unless requested separately.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can keep at least five notes open at once and
  switch between them without reopening those notes from the notes
  list.
- **SC-002**: In validation testing, opening a note that is already
  open results in activating the existing tab in 100% of tested cases.
- **SC-003**: In validation testing, users can close any open tab in a
  single close action while leaving other open tabs available.
- **SC-004**: In validation testing, closing tabs does not cause note
  content loss in any tested editing scenario.
