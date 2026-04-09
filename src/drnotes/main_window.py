import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QActionGroup, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMenuBar,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

_QSS_DARK = """
QWidget { background-color: #0d1117; color: #e6edf3; }
QMenuBar { background-color: #161b22; }
QMenuBar::item:selected { background-color: #21262d; }
QMenu { background-color: #161b22; border: 1px solid #30363d; }
QMenu::item:selected { background-color: #21262d; }
QToolBar { background-color: #161b22; border: none; border-bottom: 1px solid #30363d; }
QToolButton { background: transparent; border: 1px solid transparent; padding: 2px 6px; }
QToolButton:hover { background-color: #21262d; border-color: #30363d; }
QSplitter::handle { background-color: #30363d; }
QStatusBar { background-color: #161b22; color: #8b949e; border-top: 1px solid #30363d; }
QStatusBar QLabel { color: #8b949e; padding: 0 4px; }
QTreeView { background-color: #0d1117; border: none; }
QTreeView::item:selected { background-color: #1f6feb; color: #e6edf3; }
QTreeView::item:hover:!selected { background-color: #161b22; }
QPlainTextEdit, QTextEdit { background-color: #0d1117; color: #e6edf3; border: none; }
QLineEdit { background-color: #161b22; color: #e6edf3; border: 1px solid #30363d; border-radius: 3px; padding: 2px 4px; }
QPushButton { background-color: #21262d; color: #e6edf3; border: 1px solid #30363d; padding: 3px 8px; border-radius: 3px; }
QPushButton:hover { background-color: #30363d; }
QCheckBox { color: #e6edf3; }
QScrollBar:vertical { background-color: #0d1117; width: 12px; }
QScrollBar::handle:vertical { background-color: #30363d; border-radius: 5px; min-height: 20px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background-color: #0d1117; height: 12px; }
QScrollBar::handle:horizontal { background-color: #30363d; border-radius: 5px; min-width: 20px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
"""

from .settings import Settings
from .widgets import DirectoryTree, FormattingToolbar, SearchPanel, WorkspaceTabs


_STATE_VERSION = 2  # bump when the window layout changes


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DrNotes")
        self.resize(1200, 800)

        self._settings = Settings()
        self._build_ui()
        self._build_menu()

        # apply stored view mode (must be after _build_menu so view actions exist)
        self._apply_view_mode(self._settings.view_mode)

        self._connect_signals()
        self._restore_state()

        # restore theme (must be after _build_menu so _dark_mode_action exists)
        if self._settings.dark_mode:
            self._dark_mode_action.setChecked(True)  # triggers _on_dark_mode_toggled
        if self._settings.emacs_mode:
            self._emacs_mode_action.setChecked(True)  # triggers _on_emacs_mode_toggled

        # restore font size
        saved_size = self._settings.font_size
        self._workspaces.set_font_size(saved_size)

        # first-launch: ask for notes directory
        if not self._settings.notes_root or not os.path.isdir(self._settings.notes_root):
            self._choose_notes_dir()
        else:
            self._tree.set_root(self._settings.notes_root)
            self._search_panel.set_root(self._settings.notes_root)
            self._workspaces.set_notes_root(self._settings.notes_root)

        # reopen last file
        last = self._settings.last_file
        if last and os.path.isfile(last):
            self._open_file(last)

    # =========================================================================
    # UI construction
    # =========================================================================

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # main splitter: left panel | right panel
        self._main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # left panel: filename label above directory tree
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        self._path_label = QLabel("  No file open")
        self._path_label.setFixedHeight(28)
        self._path_label.setStyleSheet("background: #f6f8fa; padding: 4px 8px; color: #57606a;")

        self._tree = DirectoryTree()
        self._tree.setMinimumWidth(180)

        self._search_panel = SearchPanel()

        left_layout.addWidget(self._path_label)
        left_layout.addWidget(self._tree)
        left_layout.addWidget(self._search_panel)
        self._main_splitter.addWidget(left_widget)

        # right panel: toolbar above editor + preview
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self._toolbar = FormattingToolbar(self)
        self._workspaces = WorkspaceTabs()

        right_layout.addWidget(self._toolbar)
        right_layout.addWidget(self._workspaces)
        self._main_splitter.addWidget(right_widget)

        self._main_splitter.setSizes([220, 980])

        root_layout.addWidget(self._main_splitter)

        # status bar: file path (left) | last saved (right)
        self._status_path_label = QLabel("No file open")
        self._status_save_label = QLabel("Not saved")
        self._status_save_label.setContentsMargins(0, 0, 6, 0)
        sb = self.statusBar()
        sb.addWidget(self._status_path_label, 1)
        sb.addPermanentWidget(self._status_save_label)

    def _build_menu(self):
        mb: QMenuBar = self.menuBar()

        # -- File menu ---------------------------------------------------------
        file_menu = mb.addMenu("&File")

        new_note = QAction("New Note", self)
        new_note.setShortcut(QKeySequence("Ctrl+N"))
        new_note.triggered.connect(self._tree._create_new_file)
        file_menu.addAction(new_note)

        save = QAction("Save", self)
        save.setShortcut(QKeySequence("Ctrl+S"))
        save.triggered.connect(self._save_file)
        file_menu.addAction(save)

        file_menu.addSeparator()

        change_dir = QAction("Change Notes Directory…", self)
        change_dir.triggered.connect(self._choose_notes_dir)
        file_menu.addAction(change_dir)

        file_menu.addSeparator()

        quit_action = QAction("Exit", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # -- Edit menu ---------------------------------------------------------
        edit_menu = mb.addMenu("&Edit")

        find = QAction("Find / Replace", self)
        find.setShortcut(QKeySequence("Ctrl+F"))
        find.triggered.connect(self._show_find)
        edit_menu.addAction(find)

        search_files = QAction("Search in Files", self)
        search_files.setShortcut(QKeySequence("Ctrl+Shift+F"))
        search_files.triggered.connect(self._search_panel.activate)
        edit_menu.addAction(search_files)

        # -- View menu ---------------------------------------------------------
        view_menu = mb.addMenu("&View")

        # View mode actions (checkable, mutually exclusive, shared with toolbar)
        self._view_group = QActionGroup(self)
        self._view_group.setExclusive(True)

        self._edit_only_action = self._make_view_action(
            "Editor Only", "Ctrl+Alt+1", "edit", "accessories-text-editor",
        )
        view_menu.addAction(self._edit_only_action)

        self._preview_only_action = self._make_view_action(
            "Preview Only", "Ctrl+Alt+2", "preview", "text-html",
        )
        view_menu.addAction(self._preview_only_action)

        self._split_view_action = self._make_view_action(
            "Split View", "Ctrl+Alt+3", "split", "view-dual-symbolic",
        )
        view_menu.addAction(self._split_view_action)

        view_menu.addSeparator()

        self._dark_mode_action = QAction("Dark Mode", self)
        self._dark_mode_action.setCheckable(True)
        self._dark_mode_action.setShortcut(QKeySequence("Ctrl+Alt+D"))
        self._dark_mode_action.setToolTip("Toggle Dark Mode (Ctrl+Alt+D)")
        self._set_action_icon(self._dark_mode_action, "weather-clear-night")
        self._dark_mode_action.toggled.connect(self._on_dark_mode_toggled)
        view_menu.addAction(self._dark_mode_action)

        self._emacs_mode_action = QAction("Emacs Mode", self)
        self._emacs_mode_action.setCheckable(True)
        self._emacs_mode_action.setShortcut(QKeySequence("Ctrl+Alt+E"))
        self._emacs_mode_action.setToolTip("Toggle Emacs Mode (Ctrl+Alt+E)")
        self._set_action_icon(self._emacs_mode_action, "input-keyboard")
        self._emacs_mode_action.toggled.connect(self._on_emacs_mode_toggled)
        view_menu.addAction(self._emacs_mode_action)

        view_menu.addSeparator()

        increase_font = QAction("Increase Font Size", self)
        increase_font.setShortcut(QKeySequence("Ctrl+="))
        increase_font.triggered.connect(self._increase_font_size)
        view_menu.addAction(increase_font)

        decrease_font = QAction("Decrease Font Size", self)
        decrease_font.setShortcut(QKeySequence("Ctrl+-"))
        decrease_font.triggered.connect(self._decrease_font_size)
        view_menu.addAction(decrease_font)

        reset_font = QAction("Reset Font Size", self)
        reset_font.setShortcut(QKeySequence("Ctrl+0"))
        reset_font.triggered.connect(self._reset_font_size)
        view_menu.addAction(reset_font)

        # Add view/mode actions to the formatting toolbar
        self._toolbar.addSeparator()
        self._toolbar.addAction(self._edit_only_action)
        self._toolbar.addAction(self._preview_only_action)
        self._toolbar.addAction(self._split_view_action)
        self._toolbar.addSeparator()
        self._toolbar.addAction(self._dark_mode_action)
        self._toolbar.addAction(self._emacs_mode_action)

    def _make_view_action(self, label: str, shortcut: str, mode: str,
                          icon_name: str) -> QAction:
        action = QAction(label, self)
        action.setCheckable(True)
        action.setShortcut(QKeySequence(shortcut))
        action.setToolTip(f"{label} ({shortcut})")
        self._set_action_icon(action, icon_name)
        action.triggered.connect(lambda: self._set_view_mode(mode))
        self._view_group.addAction(action)
        return action

    @staticmethod
    def _set_action_icon(action: QAction, icon_name: str):
        icon = QIcon.fromTheme(icon_name)
        if not icon.isNull():
            action.setIcon(icon)

    # =========================================================================
    # Signal wiring
    # =========================================================================

    def _connect_signals(self):
        # tree → open file
        self._tree.file_selected.connect(self._open_file)

        # workspace → path/status updates
        self._workspaces.current_context_changed.connect(self._update_workspace_context)

        # toolbar → active workspace
        self._toolbar.wrap_requested.connect(self._workspaces.insert_wrap)
        self._toolbar.line_prefix_requested.connect(self._workspaces.insert_line_prefix)
        self._toolbar.block_requested.connect(self._workspaces.insert_block)
        self._toolbar.font_size_increase_requested.connect(self._increase_font_size)
        self._toolbar.font_size_decrease_requested.connect(self._decrease_font_size)

        # search panel → open file at line
        self._search_panel.result_selected.connect(self._open_file_at_line)

    # =========================================================================
    # Slots
    # =========================================================================

    def _open_file(self, path: str):
        self._workspaces.open_file(path)

    def _open_file_at_line(self, path: str, line: int):
        self._workspaces.open_file_at_line(path, line)

    def _show_find(self):
        self._workspaces.show_find()

    def _update_workspace_context(self):
        current_path = self._workspaces.current_file_path()
        if current_path:
            rel = self._relative_to_root(current_path)
            self._path_label.setText(f"  {rel}")
            self._status_path_label.setText(current_path)
            workspace = self._workspaces.current_workspace()
            self._status_save_label.setText(
                workspace.last_saved_text() if workspace else "Not saved"
            )
            self._settings.last_file = current_path
        else:
            self._path_label.setText("  No file open")
            self._status_path_label.setText("No file open")
            self._status_save_label.setText("Not saved")
            self._settings.last_file = ""

    def _save_file(self):
        self._workspaces.save_current()
        self._update_workspace_context()

    # =========================================================================
    # Theme
    # =========================================================================

    def _on_dark_mode_toggled(self, enabled: bool):
        self._settings.dark_mode = enabled
        self._apply_theme(enabled)

    def _on_emacs_mode_toggled(self, enabled: bool):
        self._settings.emacs_mode = enabled
        self._workspaces.set_emacs_mode(enabled)

    def _increase_font_size(self):
        self._workspaces.increase_font_size()
        self._sync_font_size()

    def _decrease_font_size(self):
        self._workspaces.decrease_font_size()
        self._sync_font_size()

    def _reset_font_size(self):
        self._workspaces.reset_font_size()
        self._sync_font_size()

    def _sync_font_size(self):
        size = self._workspaces.font_size()
        self._settings.font_size = size

    def _apply_theme(self, dark: bool):
        QApplication.instance().setStyleSheet(_QSS_DARK if dark else "")
        if dark:
            self._path_label.setStyleSheet("background: #161b22; padding: 4px 8px; color: #8b949e;")
        else:
            self._path_label.setStyleSheet("background: #f6f8fa; padding: 4px 8px; color: #57606a;")
        self._workspaces.set_dark_mode(dark)

    # =========================================================================
    # View mode
    # =========================================================================

    def _set_view_mode(self, mode: str):
        self._settings.view_mode = mode
        self._apply_view_mode(mode)

    def _apply_view_mode(self, mode: str):
        # Sync the view-mode action group checked state
        action_map = {
            "edit": self._edit_only_action,
            "preview": self._preview_only_action,
            "split": self._split_view_action,
        }
        action = action_map.get(mode, self._split_view_action)
        action.setChecked(True)
        self._workspaces.set_view_mode(mode)

    # =========================================================================
    # Notes directory
    # =========================================================================

    def _choose_notes_dir(self):
        path = QFileDialog.getExistingDirectory(
            self, "Select Notes Directory", os.path.expanduser("~")
        )
        if path:
            self._settings.notes_root = path
            self._tree.set_root(path)
            self._search_panel.set_root(path)
            self._workspaces.set_notes_root(path)
            self._update_workspace_context()

    # =========================================================================
    # State persistence
    # =========================================================================

    def _restore_state(self):
        geo = self._settings.window_geometry
        if geo:
            self.restoreGeometry(geo)
        state = self._settings.window_state
        if state:
            self.restoreState(state, _STATE_VERSION)
        sp = self._settings.splitter_state
        if sp:
            self._main_splitter.restoreState(sp)

    def closeEvent(self, event):
        self._workspaces.save_all()
        self._settings.window_geometry = self.saveGeometry()
        self._settings.window_state = self.saveState(_STATE_VERSION)
        self._settings.splitter_state = self._main_splitter.saveState()
        super().closeEvent(event)

    def _relative_to_root(self, path: str) -> str:
        root = self._settings.notes_root
        if not root:
            return os.path.basename(path)
        try:
            return os.path.relpath(path, root)
        except ValueError:
            return os.path.abspath(path)
