import os
import re

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QAction, QKeySequence
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
from .widgets import DirectoryTree, FormattingToolbar, MarkdownEditor, PreviewPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DrNotes")
        self.resize(1200, 800)

        self._settings = Settings()
        self._build_ui()
        self._build_menu()
        self._connect_signals()
        self._restore_state()

        # restore theme (must be after _build_menu so _dark_mode_action exists)
        if self._settings.dark_mode:
            self._dark_mode_action.setChecked(True)  # triggers _on_dark_mode_toggled
        if self._settings.emacs_mode:
            self._emacs_mode_action.setChecked(True)  # triggers _on_emacs_mode_toggled

        # debounce timer for preview updates (300 ms idle)
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(300)
        self._preview_timer.timeout.connect(self._refresh_preview)

        # auto-save timer (5 s idle after change)
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(5000)
        self._save_timer.timeout.connect(self._auto_save)

        # first-launch: ask for notes directory
        if not self._settings.notes_root or not os.path.isdir(self._settings.notes_root):
            self._choose_notes_dir()
        else:
            self._tree.set_root(self._settings.notes_root)

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

        # toolbar
        self._toolbar = FormattingToolbar(self)
        self.addToolBar(self._toolbar)

        # file path label
        self._path_label = QLabel("  No file open")
        self._path_label.setFixedHeight(28)
        self._path_label.setStyleSheet("background: #f6f8fa; padding: 4px 8px; color: #57606a;")
        root_layout.addWidget(self._path_label)

        # main splitter: tree | (editor + preview)
        self._main_splitter = QSplitter(Qt.Orientation.Horizontal)

        self._tree = DirectoryTree()
        self._tree.setMinimumWidth(180)
        self._main_splitter.addWidget(self._tree)

        # right side: editor + preview in a vertical splitter (split view)
        self._right_splitter = QSplitter(Qt.Orientation.Horizontal)

        self._editor = MarkdownEditor()
        self._preview = PreviewPanel()

        self._right_splitter.addWidget(self._editor)
        self._right_splitter.addWidget(self._preview)
        self._right_splitter.setSizes([500, 500])

        self._main_splitter.addWidget(self._right_splitter)
        self._main_splitter.setSizes([220, 980])

        root_layout.addWidget(self._main_splitter)

        # apply stored view mode
        self._apply_view_mode(self._settings.view_mode)

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
        save.triggered.connect(self._editor.save_current)
        file_menu.addAction(save)

        file_menu.addSeparator()

        change_dir = QAction("Change Notes Directory…", self)
        change_dir.triggered.connect(self._choose_notes_dir)
        file_menu.addAction(change_dir)

        # -- Edit menu ---------------------------------------------------------
        edit_menu = mb.addMenu("&Edit")

        find = QAction("Find / Replace", self)
        find.setShortcut(QKeySequence("Ctrl+F"))
        find.triggered.connect(self._editor.show_find)
        edit_menu.addAction(find)

        # -- View menu ---------------------------------------------------------
        view_menu = mb.addMenu("&View")

        edit_only = QAction("Editor Only", self)
        edit_only.setShortcut(QKeySequence("Ctrl+Alt+1"))
        edit_only.triggered.connect(lambda: self._set_view_mode("edit"))
        view_menu.addAction(edit_only)

        preview_only = QAction("Preview Only", self)
        preview_only.setShortcut(QKeySequence("Ctrl+Alt+2"))
        preview_only.triggered.connect(lambda: self._set_view_mode("preview"))
        view_menu.addAction(preview_only)

        split = QAction("Split View", self)
        split.setShortcut(QKeySequence("Ctrl+Alt+3"))
        split.triggered.connect(lambda: self._set_view_mode("split"))
        view_menu.addAction(split)

        view_menu.addSeparator()

        self._dark_mode_action = QAction("Dark Mode", self)
        self._dark_mode_action.setCheckable(True)
        self._dark_mode_action.setShortcut(QKeySequence("Ctrl+Alt+D"))
        self._dark_mode_action.toggled.connect(self._on_dark_mode_toggled)
        view_menu.addAction(self._dark_mode_action)

        self._emacs_mode_action = QAction("Emacs Mode", self)
        self._emacs_mode_action.setCheckable(True)
        self._emacs_mode_action.setShortcut(QKeySequence("Ctrl+Alt+E"))
        self._emacs_mode_action.toggled.connect(self._on_emacs_mode_toggled)
        view_menu.addAction(self._emacs_mode_action)

    # =========================================================================
    # Signal wiring
    # =========================================================================

    def _connect_signals(self):
        # tree → open file
        self._tree.file_selected.connect(self._open_file)

        # editor → debounced preview + auto-save
        self._editor.content_changed.connect(self._on_content_changed)

        # toolbar → editor
        self._toolbar.wrap_requested.connect(self._editor.insert_wrap)
        self._toolbar.line_prefix_requested.connect(self._editor.insert_line_prefix)
        self._toolbar.block_requested.connect(self._editor.insert_block)

        # preview checkbox → update source
        self._preview.checkbox_toggled.connect(self._on_checkbox_toggled)

        # scroll sync: editor ↔ preview
        self._editor.scroll_fraction_changed.connect(self._preview.set_scroll_fraction)
        self._preview.wheel_event.connect(self._editor.adjust_scroll_by)

    # =========================================================================
    # Slots
    # =========================================================================

    def _open_file(self, path: str):
        self._editor.open_file(path)
        rel = os.path.relpath(path, self._settings.notes_root)
        self._path_label.setText(f"  {rel}")
        self._settings.last_file = path
        self._refresh_preview()

    def _on_content_changed(self, _text: str):
        self._preview_timer.start()
        self._save_timer.start()

    def _refresh_preview(self):
        self._preview.update_content(self._editor.get_text())

    def _auto_save(self):
        self._editor.save_current()

    def _on_checkbox_toggled(self, index: int, checked: bool):
        content = self._editor.get_text()
        pattern = re.compile(r"- \[([ xX])\]")
        matches = list(pattern.finditer(content))
        if index < len(matches):
            m = matches[index]
            new_char = "x" if checked else " "
            new_content = content[: m.start(1)] + new_char + content[m.end(1) :]
            self._editor.set_text_content(new_content)

    # =========================================================================
    # Theme
    # =========================================================================

    def _on_dark_mode_toggled(self, enabled: bool):
        self._settings.dark_mode = enabled
        self._apply_theme(enabled)

    def _on_emacs_mode_toggled(self, enabled: bool):
        self._settings.emacs_mode = enabled
        self._editor.set_emacs_mode(enabled)

    def _apply_theme(self, dark: bool):
        QApplication.instance().setStyleSheet(_QSS_DARK if dark else "")
        if dark:
            self._path_label.setStyleSheet("background: #161b22; padding: 4px 8px; color: #8b949e;")
        else:
            self._path_label.setStyleSheet("background: #f6f8fa; padding: 4px 8px; color: #57606a;")
        self._editor.set_dark_mode(dark)
        self._preview.set_dark_mode(dark)

    # =========================================================================
    # View mode
    # =========================================================================

    def _set_view_mode(self, mode: str):
        self._settings.view_mode = mode
        self._apply_view_mode(mode)

    def _apply_view_mode(self, mode: str):
        if mode == "edit":
            self._editor.show()
            self._preview.hide()
        elif mode == "preview":
            self._editor.hide()
            self._preview.show()
        else:  # split
            self._editor.show()
            self._preview.show()
        self._preview.set_scroll_sync(mode == "split")

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

    # =========================================================================
    # State persistence
    # =========================================================================

    def _restore_state(self):
        geo = self._settings.window_geometry
        if geo:
            self.restoreGeometry(geo)
        state = self._settings.window_state
        if state:
            self.restoreState(state)
        sp = self._settings.splitter_state
        if sp:
            self._main_splitter.restoreState(sp)

    def closeEvent(self, event):
        self._editor.save_current()
        self._settings.window_geometry = self.saveGeometry()
        self._settings.window_state = self.saveState()
        self._settings.splitter_state = self._main_splitter.saveState()
        super().closeEvent(event)
