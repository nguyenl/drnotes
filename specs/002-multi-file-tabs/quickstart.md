# Quickstart: Tabbed Note Editing

## Goal

Verify that DrNotes can keep multiple notes open at once with closable
tabs while preserving existing editing, preview, and navigation flows.

## Setup

1. Install the project in development mode:

```bash
pip install -e .
```

2. Launch the app:

```bash
drnotes
```

3. Choose a notes directory containing several markdown files,
   including at least two files with the same name in different
   folders if available.

## Validation Steps

1. Open one note from the file tree, then open two more notes.
   Confirm each note appears in its own tab.
2. Reopen an already open note from the tree.
   Confirm the existing tab becomes active and no duplicate tab is created.
3. Edit the active note, switch to another tab, then switch back.
   Confirm the edited content and working position remain available.
4. Use search-in-files to open a matching line in a note that is not
   yet open.
   Confirm a tab opens and the editor jumps to the selected line.
5. Use search-in-files on a note that is already open.
   Confirm the existing tab is focused and the editor jumps to the
   selected line.
6. Close a non-active tab.
   Confirm the remaining tabs stay open and the active tab does not change.
7. Close the active tab after making an edit.
   Confirm another tab becomes active immediately and the edit is still
   present when the file is reopened.
8. Close the final remaining tab.
   Confirm the path label, status bar, and workspace area return to a
   no-file-open state.
9. Open two same-name notes from different folders.
   Confirm the tab labels provide enough context to tell them apart.

## Regression Checks

1. Use the formatting toolbar on the active tab.
   Confirm only the active note changes.
2. Toggle dark mode, emacs mode, and view mode with tabs open.
   Confirm the active workspace updates correctly and newly opened tabs
   inherit the same global settings.
3. Wait 5 seconds after editing.
   Confirm autosave still updates the save indicator for the active tab.
