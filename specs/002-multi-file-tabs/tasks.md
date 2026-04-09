# Tasks: Tabbed Note Editing

**Input**: Design documents from `/specs/002-multi-file-tabs/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: No automated test tasks were explicitly requested in the feature specification. Validation for this feature uses the manual scenarios in `specs/002-multi-file-tabs/quickstart.md`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Introduce the shared tabbed-workspace module and surface it through the widget package.

- [ ] T001 Create the tabbed workspace module scaffold in src/drnotes/widgets/workspace_tabs.py
- [ ] T002 [P] Export the tabbed workspace widget from src/drnotes/widgets/__init__.py

**Checkpoint**: The repo has a concrete home for tab-management logic and the new widget can be imported by the main window.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared workspace abstractions that every tabbed user story depends on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T003 Extend hosted-editor lifecycle helpers for tab workspaces in src/drnotes/widgets/editor.py
- [ ] T004 [P] Add preview empty-state and hosted-update helpers in src/drnotes/widgets/preview.py
- [ ] T005 Refactor main-window workspace plumbing to target an active tab workspace instead of one fixed editor/preview pair in src/drnotes/main_window.py

**Checkpoint**: `MainWindow` can talk to an active workspace abstraction and the editor/preview widgets support being hosted per tab.

---

## Phase 3: User Story 1 - Keep Multiple Notes Open (Priority: P1) 🎯 MVP

**Goal**: Users can open several notes at once, switch between them, and avoid duplicate tabs for the same file.

**Independent Test**: Open three notes from the tree, confirm each appears in its own tab, switch among them, and reopen one of the files to verify the existing tab is focused instead of duplicated.

### Implementation for User Story 1

- [ ] T006 [US1] Implement the file-path tab registry and duplicate-open detection in src/drnotes/widgets/workspace_tabs.py
- [ ] T007 [US1] Implement per-tab workspace creation and active-tab switching in src/drnotes/widgets/workspace_tabs.py
- [ ] T008 [US1] Route tree-based file opening through the tabbed workspace and refresh the active file labels in src/drnotes/main_window.py
- [ ] T009 [US1] Route toolbar, find, preview refresh, theme, view-mode, and font-size actions to the active tab workspace in src/drnotes/main_window.py

**Checkpoint**: User Story 1 should now support opening multiple notes and switching between them as a complete MVP increment.

---

## Phase 4: User Story 2 - Close Tabs Without Losing Work (Priority: P1)

**Goal**: Users can close any tab, keep remaining tabs available, and preserve recent edits while returning to a clear empty state after the final close.

**Independent Test**: Open multiple tabs, edit one note, close a non-active tab and the active tab, then close the final tab and verify edits are preserved and the UI clears correctly.

### Implementation for User Story 2

- [ ] T010 [US2] Enable closable tabs and close-request handling in src/drnotes/widgets/workspace_tabs.py
- [ ] T011 [US2] Save modified workspaces before tab removal and activate the next remaining tab in src/drnotes/widgets/workspace_tabs.py
- [ ] T012 [US2] Update active-tab save, autosave, and status-bar flows for tab close behavior in src/drnotes/main_window.py
- [ ] T013 [US2] Reset the path label, save indicator, and preview/editor presentation for the no-file-open state in src/drnotes/main_window.py and src/drnotes/widgets/preview.py

**Checkpoint**: User Story 2 should now let users close tabs safely without losing edits or leaving stale note content on screen.

---

## Phase 5: User Story 3 - Navigate Into Tabs From Other Flows (Priority: P2)

**Goal**: Existing navigation flows such as search results and repeated note opens work naturally with tabs, including same-name file disambiguation.

**Independent Test**: Open notes from the tree and search results, reopen an already open note, confirm focus moves to the correct tab, and verify same-name files are distinguishable.

### Implementation for User Story 3

- [ ] T014 [US3] Route search-result navigation through the tabbed open-or-focus flow and line targeting in src/drnotes/main_window.py
- [ ] T015 [P] [US3] Implement same-name tab-title disambiguation and full-path tooltips in src/drnotes/widgets/workspace_tabs.py
- [ ] T016 [US3] Keep active-tab path context and last-opened-file persistence synchronized with navigation events in src/drnotes/main_window.py and src/drnotes/settings.py

**Checkpoint**: User Story 3 should now preserve existing note-discovery workflows while making tab context clear.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish cross-story cleanup, documentation, and release validation.

- [ ] T017 [P] Update the user-facing tabbed-editing documentation in README.md and ARCHITECTURE.md
- [ ] T018 Run the manual validation flow in specs/002-multi-file-tabs/quickstart.md and capture any quickstart adjustments in specs/002-multi-file-tabs/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies, can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user story work.
- **User Story 1 (Phase 3)**: Depends on Foundational completion.
- **User Story 2 (Phase 4)**: Depends on User Story 1 because close behavior needs working multi-tab open/switch support.
- **User Story 3 (Phase 5)**: Depends on User Story 1 because navigation must target the existing open-or-focus tab flow.
- **Polish (Phase 6)**: Depends on the completion of the desired user stories.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational and is the MVP.
- **User Story 2 (P1)**: Depends on User Story 1's tab registry and active-workspace behavior.
- **User Story 3 (P2)**: Depends on User Story 1's open/focus behavior and integrates with existing search/navigation flows.

### Within Each User Story

- Shared workspace plumbing must exist before story-specific wiring.
- Tab container behavior should land before `MainWindow` integration that depends on it.
- Each story should be manually validated before starting the next dependent story.

### Parallel Opportunities

- T002 can run in parallel with T001 once the workspace widget name is agreed.
- T003 and T004 can run in parallel because they touch different hosted widgets.
- T015 can run in parallel with T014 because title disambiguation is isolated to the tab widget.
- T017 can run in parallel with final manual validation if the behavior is already stable.

---

## Parallel Example: User Story 1

```bash
# Parallelize the shared hosted-widget preparation:
Task: "Extend hosted-editor lifecycle helpers in src/drnotes/widgets/editor.py"
Task: "Add preview empty-state and hosted-update helpers in src/drnotes/widgets/preview.py"

# After the workspace container exists, parallelize isolated follow-up work:
Task: "Route search-result navigation through src/drnotes/main_window.py"
Task: "Implement same-name tab-title disambiguation in src/drnotes/widgets/workspace_tabs.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. **Stop and validate**: Confirm multiple files can remain open, switching works, and duplicate opens focus the existing tab.
5. Demo or ship the MVP if that scope is sufficient.

### Incremental Delivery

1. Ship multi-open and switching first with User Story 1.
2. Add safe close behavior and empty-state cleanup with User Story 2.
3. Add search/navigation integration and same-name tab disambiguation with User Story 3.
4. Finish with docs and quickstart validation.

### Parallel Team Strategy

1. One developer handles Phase 2 hosted-widget groundwork.
2. Once Phase 2 is done:
   - Developer A: User Story 1 main-window integration in src/drnotes/main_window.py
   - Developer B: User Story 1/2 tab-container logic in src/drnotes/widgets/workspace_tabs.py
3. After User Story 1 lands:
   - Developer A: User Story 2 close-state and status handling
   - Developer B: User Story 3 disambiguation and navigation polish

---

## Notes

- Total tasks: 18
- User Story task counts: US1 = 4, US2 = 4, US3 = 3
- Parallelizable tasks: T002, T004, T015, T017
- Suggested MVP scope: Phase 1 + Phase 2 + Phase 3 (User Story 1)
- All tasks follow the required checklist format with task IDs, optional labels, and exact file paths.
