# Tasks: Establishing Baseline Specs

**Input**: Design documents from `/specs/001-establishing-baseline-specs/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md
**Status**: All tasks COMPLETE — this is a baseline capture of existing implementation.

**Tests**: No automated tests exist in the current codebase. Test tasks are not included as they were not requested.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure with `src/drnotes/` package and `src/drnotes/widgets/` subpackage
- [x] T002 Initialize Python project with pyproject.toml (PySide6, markdown, pymdown-extensions, Pygments dependencies)
- [x] T003 [P] Create application entry point in src/drnotes/app.py with QApplication setup
- [x] T004 [P] Create settings persistence wrapper in src/drnotes/settings.py with QSettings

**Checkpoint**: Project structure ready — widget and feature implementation can begin

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T005 Implement MainWindow shell with splitter layout (directory tree | editor/preview) in src/drnotes/main_window.py
- [x] T006 [P] Implement MarkdownHighlighter with regex-based syntax highlighting rules for 11+ markdown constructs in src/drnotes/syntax_highlighter.py
- [x] T007 [P] Create widget __init__.py exports in src/drnotes/widgets/__init__.py

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and Organize Notes (Priority: P1) MVP

**Goal**: Users can create, open, edit, save, rename, move, and delete markdown notes organized in folders.

**Independent Test**: Open the app, select a directory, create a note, write content, rename it, create a folder, drag the note into the folder, verify the file system reflects all changes.

### Implementation for User Story 1

- [x] T008 [P] [US1] Implement DirectoryTree widget with QFileSystemModel, .md filtering, and file/folder CRUD operations in src/drnotes/widgets/directory_tree.py
- [x] T009 [P] [US1] Implement core text editor (_EditorCore) with QPlainTextEdit, line numbers (_LineNumberArea), and monospace font in src/drnotes/widgets/editor.py
- [x] T010 [US1] Implement MarkdownEditor composite widget wrapping _EditorCore with file open/save operations in src/drnotes/widgets/editor.py
- [x] T011 [US1] Add context menu to DirectoryTree for New Note, New Folder, Rename, Delete operations in src/drnotes/widgets/directory_tree.py
- [x] T012 [US1] Enable drag-and-drop (InternalMove mode) for file reordering in DirectoryTree in src/drnotes/widgets/directory_tree.py
- [x] T013 [US1] Wire DirectoryTree.file_selected signal to MainWindow._open_file() for file opening in src/drnotes/main_window.py
- [x] T014 [US1] Add File menu with New Note (Ctrl+N), Save (Ctrl+S), Change Notes Directory, and Exit (Ctrl+Q) in src/drnotes/main_window.py
- [x] T015 [US1] Implement notes root directory selection dialog (_choose_notes_dir) in src/drnotes/main_window.py

**Checkpoint**: User Story 1 fully functional — users can manage notes and folders

---

## Phase 4: User Story 2 - Write and Format Markdown (Priority: P1)

**Goal**: Users can write markdown with syntax highlighting, toolbar formatting, smart list continuation, and indent/outdent.

**Independent Test**: Open a note, type markdown, use each toolbar button and shortcut, verify formatting is applied correctly and syntax highlighting updates in real time.

### Implementation for User Story 2

- [x] T016 [P] [US2] Implement FormattingToolbar with signals for wrap, line prefix, and block formatting operations in src/drnotes/widgets/toolbar.py
- [x] T017 [US2] Add formatting methods (insert_wrap, insert_line_prefix, insert_block) to MarkdownEditor in src/drnotes/widgets/editor.py
- [x] T018 [US2] Implement smart list continuation (ordered, unordered, checklist) on Enter key in _EditorCore.keyPressEvent in src/drnotes/widgets/editor.py
- [x] T019 [US2] Implement Tab/Shift+Tab indent/outdent (4-space) with multi-line selection support in _EditorCore.keyPressEvent in src/drnotes/widgets/editor.py
- [x] T020 [US2] Wire FormattingToolbar signals to MarkdownEditor formatting methods via MainWindow in src/drnotes/main_window.py
- [x] T021 [US2] Add toolbar buttons with system theme icons (QIcon.fromTheme) and text fallback for all formatting actions in src/drnotes/widgets/toolbar.py

**Checkpoint**: User Story 2 fully functional — users can format markdown efficiently

---

## Phase 5: User Story 3 - Preview Markdown with Live Rendering (Priority: P1)

**Goal**: Users can view live-rendered markdown preview with Mermaid diagrams, interactive checklists, and three view modes with scroll sync.

**Independent Test**: Open a note with varied markdown, switch between view modes, verify rendering is correct and scroll sync works in split view.

### Implementation for User Story 3

- [x] T022 [P] [US3] Implement PreviewPanel with QWebEngineView, _Bridge for JS-Python communication, and HTML template in src/drnotes/widgets/preview.py
- [x] T023 [US3] Implement markdown-to-HTML rendering pipeline with pymdownx extensions (highlight, superfences, tasklist, tables, tilde, nl2br, sane_lists) in src/drnotes/widgets/preview.py
- [x] T024 [US3] Add custom Mermaid fence formatter (_mermaid_fence) and JavaScript rendering with error handling in src/drnotes/widgets/preview.py
- [x] T025 [US3] Wire interactive checkbox toggling: JS bridge → MainWindow._on_checkbox_toggled() → regex-based markdown update in src/drnotes/main_window.py
- [x] T026 [US3] Implement bidirectional scroll synchronization between editor and preview in split view in src/drnotes/main_window.py
- [x] T027 [US3] Add View menu with three view modes (Editor Only Ctrl+Alt+1, Preview Only Ctrl+Alt+2, Split View Ctrl+Alt+3) in src/drnotes/main_window.py
- [x] T028 [US3] Implement 300ms debounce timer for preview updates on content change in src/drnotes/main_window.py

**Checkpoint**: User Story 3 fully functional — users can preview markdown with all rendering features

---

## Phase 6: User Story 4 - Search and Navigate Notes (Priority: P2)

**Goal**: Users can search across all notes and use find/replace within a single note.

**Independent Test**: Create multiple notes with known content, search for a term, verify grouped results, navigate to match, use find/replace within a note.

### Implementation for User Story 4

- [x] T029 [P] [US4] Implement SearchPanel with regex-based full-text search across all .md files, grouped results in QTreeWidget in src/drnotes/widgets/search_panel.py
- [x] T030 [P] [US4] Implement _FindReplaceBar with case-sensitive toggle, Next/Prev/Replace/Replace All using QTextDocument.find() in src/drnotes/widgets/editor.py
- [x] T031 [US4] Wire SearchPanel.result_selected signal to MainWindow for file opening and line navigation (goto_line) in src/drnotes/main_window.py
- [x] T032 [US4] Add Edit menu with Find/Replace (Ctrl+F) and Search in Files (Ctrl+Shift+F) in src/drnotes/main_window.py

**Checkpoint**: User Story 4 fully functional — users can search and navigate across all notes

---

## Phase 7: User Story 5 - Customize Appearance and Editing Mode (Priority: P2)

**Goal**: Users can toggle dark/light mode, adjust font size, and enable Emacs keybindings, with all settings persisting.

**Independent Test**: Toggle dark mode, adjust font size up/down/reset, enable Emacs mode, close and reopen the app, verify all settings persist.

### Implementation for User Story 5

- [x] T033 [US5] Implement dark/light theme application (_apply_theme) with GitHub-inspired QSS stylesheet in src/drnotes/main_window.py
- [x] T034 [US5] Add light and dark color palettes to MarkdownHighlighter with set_dark_mode() toggle in src/drnotes/syntax_highlighter.py
- [x] T035 [US5] Implement dark mode CSS class toggle in PreviewPanel with JavaScript in src/drnotes/widgets/preview.py
- [x] T036 [US5] Implement Emacs mode with 20+ keybindings (_emacs_handle) including mark state, kill/yank, and navigation in src/drnotes/widgets/editor.py
- [x] T037 [US5] Add font size controls (increase/decrease/reset, min 6pt, max 72pt) to MarkdownEditor in src/drnotes/widgets/editor.py
- [x] T038 [US5] Add font size synchronization between editor (pt) and preview (px, proportional) in src/drnotes/main_window.py
- [x] T039 [US5] Add View menu items for Dark Mode (Ctrl+Alt+D), Emacs Mode (Ctrl+Alt+E), and font size (Ctrl+=/-/0) in src/drnotes/main_window.py
- [x] T040 [US5] Add toolbar buttons for font size increase (A+) and decrease (A-) with system theme icons in src/drnotes/widgets/toolbar.py

**Checkpoint**: User Story 5 fully functional — users can fully customize their editing experience

---

## Phase 8: User Story 6 - Auto-Save and Session Persistence (Priority: P2)

**Goal**: The app auto-saves after idle time, persists window state, and shows file path and save timestamp in a status bar.

**Independent Test**: Edit a note and wait 5 seconds, verify status bar updates, close and reopen, verify state is restored.

### Implementation for User Story 6

- [x] T041 [US6] Implement 5-second auto-save debounce timer with _auto_save() slot in src/drnotes/main_window.py
- [x] T042 [US6] Implement status bar with file path label (left, stretches) and save timestamp label (right, fixed) in src/drnotes/main_window.py
- [x] T043 [US6] Implement session state persistence (window geometry, splitter state, last file) via Settings in src/drnotes/main_window.py
- [x] T044 [US6] Implement state restoration on startup (_restore_state) including reopening last file in src/drnotes/main_window.py

**Checkpoint**: User Story 6 fully functional — user data is safe and sessions persist seamlessly

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T045 [P] Create package.sh script for PyInstaller single-binary packaging
- [x] T046 [P] Create README.md with feature documentation, installation guide, and keyboard shortcuts
- [x] T047 [P] Create docs/product-requirements-document.md with full PRD
- [x] T048 Add Vulkan rendering workaround (environment variable) in src/drnotes/app.py
- [x] T049 [P] Implement atomic file writes (write-to-temp + os.replace) in save_current() in src/drnotes/widgets/editor.py
- [x] T050 [P] Bundle Mermaid.js locally as static asset in src/drnotes/assets/mermaid.min.js, replace CDN reference in src/drnotes/widgets/preview.py — NOTE: must load via `<script src>` with baseUrl, NOT inline into setHtml() (2MB content limit)
- [x] T051 Update package.sh to include assets directory via --add-data for PyInstaller bundling
- [x] T052 Add rename collision confirmation dialog for DirectoryTree in src/drnotes/widgets/directory_tree.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (Notes), US2 (Formatting), US3 (Preview): P1 stories can proceed in parallel
  - US4 (Search), US5 (Customization), US6 (Auto-save): P2 stories can proceed in parallel
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational — No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational — Requires editor from US1 (T009/T010)
- **User Story 3 (P1)**: Can start after Foundational — Requires editor from US1 for scroll sync
- **User Story 4 (P2)**: Can start after Foundational — Requires editor from US1 for find/replace
- **User Story 5 (P2)**: Can start after Foundational — Requires editor from US1 and preview from US3
- **User Story 6 (P2)**: Can start after Foundational — Requires MainWindow from US1

### Within Each User Story

- Models/widgets before services/wiring
- Core implementation before integration with MainWindow
- Story complete before moving to next priority

### Parallel Opportunities

- T003 + T004: Entry point and settings (Setup phase)
- T006 + T007: Highlighter and widget exports (Foundational)
- T008 + T009: DirectoryTree and EditorCore (US1)
- T016 + T017: Toolbar and editor formatting methods (US2)
- T022 + T023: PreviewPanel and rendering pipeline (US3)
- T029 + T030: SearchPanel and FindReplaceBar (US4)
- T045 + T046 + T047: Packaging, README, PRD (Polish)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Create and Organize Notes)
4. **STOP and VALIDATE**: Users can create, edit, save, and organize notes
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational -> Foundation ready
2. Add US1 (Notes) -> Test independently -> MVP!
3. Add US2 (Formatting) -> Test independently -> Rich editing
4. Add US3 (Preview) -> Test independently -> Live preview
5. Add US4 (Search) -> Test independently -> Searchable notes
6. Add US5 (Customization) -> Test independently -> Personalized UX
7. Add US6 (Auto-save) -> Test independently -> Bulletproof persistence
8. Each story adds value without breaking previous stories

---

## Notes

- All 52 tasks are marked COMPLETE — baseline capture + clarification fixes
- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- No automated test suite exists; testing has been manual
