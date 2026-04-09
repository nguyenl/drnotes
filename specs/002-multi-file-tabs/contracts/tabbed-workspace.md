# UI Contract: Tabbed Workspace

## Purpose

Define the user-visible behavior that the tabbed workspace must honor
across note-tree, search, editing, and close flows.

## Open Note Contract

| Trigger | Precondition | Required Behavior |
|---------|--------------|-------------------|
| User selects a note from the tree | The note is not already open | Create a new tab for that note and make it active |
| User selects a note from the tree | The note is already open | Focus the existing tab instead of creating a duplicate |
| User opens a search result | The note is not already open | Create a new tab, make it active, and navigate to the matched line |
| User opens a search result | The note is already open | Focus the existing tab and navigate to the matched line |

## Active Tab Contract

| Trigger | Precondition | Required Behavior |
|---------|--------------|-------------------|
| User clicks a different tab | Another tab is active | Show the selected note's editor, preview, path label, and status context |
| Global formatting action fires | An active tab exists | Apply the action to the active tab only |
| Global save action fires | An active tab exists | Save the active tab using the existing atomic file-save behavior |

## Close Tab Contract

| Trigger | Precondition | Required Behavior |
|---------|--------------|-------------------|
| User closes a non-active tab | Other tabs remain open | Remove only that tab and keep the active tab unchanged |
| User closes the active tab | Other tabs remain open | Save recent edits if needed, remove the tab, and activate a remaining tab immediately |
| User closes the final tab | No other tabs remain | Save recent edits if needed, remove the tab, and return the UI to a no-file-open state |

## Tab Label Contract

| Condition | Required Behavior |
|-----------|-------------------|
| Open tabs have unique file names | Show concise file-name tab labels |
| Open tabs share the same file name | Add contextual path information so users can distinguish them |
| User hovers a tab | Full file path is available as additional context |
