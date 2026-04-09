import os
import re

from PySide6.QtCore import QDateTime, QTimer, Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QSplitter,
    QStackedLayout,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .editor import MarkdownEditor
from .preview import PreviewPanel


_CHECKBOX_RE = re.compile(r"- \[([ xX])\]")


def _canonical_path(path: str) -> str:
    return os.path.normcase(os.path.abspath(path))


def _safe_relpath(path: str, root: str) -> str:
    if not root:
        return os.path.basename(path)
    try:
        return os.path.relpath(path, root)
    except ValueError:
        return os.path.abspath(path)


def _tab_label(relative_path: str, basename_counts: dict[str, int], modified: bool) -> str:
    basename = os.path.basename(relative_path) or relative_path
    label = relative_path if basename_counts.get(basename, 0) > 1 else basename
    if modified:
        label = f"* {label}"
    return label


class NoteWorkspace(QWidget):
    """Per-tab note workspace containing one editor/preview pair."""

    title_state_changed = Signal()
    save_status_changed = Signal(str, str)

    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self._view_mode = "split"
        self._last_saved_text = "Not saved"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._editor = MarkdownEditor()
        self._preview = PreviewPanel()
        self._splitter.addWidget(self._editor)
        self._splitter.addWidget(self._preview)
        self._splitter.setSizes([500, 500])
        layout.addWidget(self._splitter)

        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(300)
        self._preview_timer.timeout.connect(self._refresh_preview)

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(5000)
        self._save_timer.timeout.connect(self._auto_save)

        self._editor.content_changed.connect(self._on_content_changed)
        self._editor.scroll_fraction_changed.connect(self._preview.set_scroll_fraction)
        self._preview.wheel_event.connect(self._editor.adjust_scroll_by)
        self._preview.checkbox_toggled.connect(self._on_checkbox_toggled)

        self.open_file(path)

    @property
    def file_path(self) -> str:
        return self._editor.current_file or ""

    @property
    def is_modified(self) -> bool:
        return self._editor.is_modified

    def last_saved_text(self) -> str:
        return self._last_saved_text

    def open_file(self, path: str) -> bool:
        opened = self._editor.open_file(path)
        if opened:
            self._refresh_preview()
            self.title_state_changed.emit()
        return opened

    def save_current(self) -> bool:
        saved = self._editor.save_current()
        if saved:
            now = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
            self._last_saved_text = f"Saved {now}"
            self.save_status_changed.emit(self.file_path, self._last_saved_text)
            self.title_state_changed.emit()
        return saved

    def show_find(self):
        self._editor.show_find()

    def goto_line(self, line: int):
        self._editor.goto_line(line)

    def insert_wrap(self, prefix: str, suffix: str):
        self._editor.insert_wrap(prefix, suffix)

    def insert_line_prefix(self, prefix: str):
        self._editor.insert_line_prefix(prefix)

    def insert_block(self, text: str):
        self._editor.insert_block(text)

    def set_dark_mode(self, dark: bool):
        self._editor.set_dark_mode(dark)
        self._preview.set_dark_mode(dark)

    def set_emacs_mode(self, enabled: bool):
        self._editor.set_emacs_mode(enabled)

    def set_font_size(self, size: int):
        self._editor.set_font_size(size)
        self._preview.set_font_size(size)

    def increase_font_size(self):
        self._editor.increase_font_size()
        self._preview.set_font_size(self.font_size())

    def decrease_font_size(self):
        self._editor.decrease_font_size()
        self._preview.set_font_size(self.font_size())

    def reset_font_size(self):
        self._editor.reset_font_size()
        self._preview.set_font_size(self.font_size())

    def font_size(self) -> int:
        return self._editor.font_size()

    def set_view_mode(self, mode: str):
        self._view_mode = mode
        if mode == "edit":
            self._editor.show()
            self._preview.hide()
        elif mode == "preview":
            self._editor.hide()
            self._preview.show()
        else:
            self._editor.show()
            self._preview.show()
        self._preview.set_scroll_sync(mode == "split")

    def _on_content_changed(self, _text: str):
        self._preview_timer.start()
        self._save_timer.start()
        self.title_state_changed.emit()

    def _refresh_preview(self):
        self._preview.update_content(self._editor.get_text())

    def _auto_save(self):
        self.save_current()

    def _on_checkbox_toggled(self, index: int, checked: bool):
        content = self._editor.get_text()
        matches = list(_CHECKBOX_RE.finditer(content))
        if index >= len(matches):
            return
        match = matches[index]
        new_char = "x" if checked else " "
        new_content = content[: match.start(1)] + new_char + content[match.end(1):]
        self._editor.set_text_content(new_content)


class WorkspaceTabs(QWidget):
    """Tabbed container for open note workspaces."""

    current_context_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._notes_root = ""
        self._dark_mode = False
        self._emacs_mode = False
        self._view_mode = "split"
        self._font_size = 11
        self._workspaces: dict[str, NoteWorkspace] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._stack = QStackedLayout()
        layout.addLayout(self._stack)

        self._empty_label = QLabel("No file open")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._stack.addWidget(self._empty_label)

        self._tabs = QTabWidget()
        self._tabs.setTabsClosable(True)
        self._tabs.setDocumentMode(True)
        self._tabs.tabCloseRequested.connect(self.close_tab)
        self._tabs.currentChanged.connect(self._on_current_changed)
        self._stack.addWidget(self._tabs)

        self._sync_visible_widget()

    def set_notes_root(self, path: str):
        self._notes_root = path
        self._retitle_tabs()
        self.current_context_changed.emit()

    def current_workspace(self) -> NoteWorkspace | None:
        widget = self._tabs.currentWidget()
        return widget if isinstance(widget, NoteWorkspace) else None

    def current_file_path(self) -> str:
        workspace = self.current_workspace()
        return workspace.file_path if workspace else ""

    def open_file(self, path: str) -> NoteWorkspace | None:
        key = _canonical_path(path)
        workspace = self._workspaces.get(key)
        if workspace is None:
            workspace = NoteWorkspace(path, self)
            workspace.set_dark_mode(self._dark_mode)
            workspace.set_emacs_mode(self._emacs_mode)
            workspace.set_font_size(self._font_size)
            workspace.set_view_mode(self._view_mode)
            workspace.title_state_changed.connect(self._retitle_tabs)
            workspace.save_status_changed.connect(self._on_workspace_saved)
            self._tabs.addTab(workspace, "")
            self._workspaces[key] = workspace
            self._retitle_tabs()
            self._sync_visible_widget()
        self._tabs.setCurrentWidget(workspace)
        self.current_context_changed.emit()
        return workspace

    def open_file_at_line(self, path: str, line: int) -> NoteWorkspace | None:
        workspace = self.open_file(path)
        if workspace is not None:
            workspace.goto_line(line)
        return workspace

    def close_tab(self, index: int):
        widget = self._tabs.widget(index)
        if not isinstance(widget, NoteWorkspace):
            return
        if widget.is_modified and not widget.save_current():
            return
        key = _canonical_path(widget.file_path)
        self._tabs.removeTab(index)
        self._workspaces.pop(key, None)
        widget.deleteLater()
        self._sync_visible_widget()
        self._retitle_tabs()
        self.current_context_changed.emit()

    def save_current(self) -> bool:
        workspace = self.current_workspace()
        if workspace is None:
            return False
        return workspace.save_current()

    def save_all(self):
        for workspace in list(self._workspaces.values()):
            workspace.save_current()

    def show_find(self):
        workspace = self.current_workspace()
        if workspace is not None:
            workspace.show_find()

    def insert_wrap(self, prefix: str, suffix: str):
        workspace = self.current_workspace()
        if workspace is not None:
            workspace.insert_wrap(prefix, suffix)

    def insert_line_prefix(self, prefix: str):
        workspace = self.current_workspace()
        if workspace is not None:
            workspace.insert_line_prefix(prefix)

    def insert_block(self, text: str):
        workspace = self.current_workspace()
        if workspace is not None:
            workspace.insert_block(text)

    def set_dark_mode(self, enabled: bool):
        self._dark_mode = enabled
        for workspace in self._workspaces.values():
            workspace.set_dark_mode(enabled)

    def set_emacs_mode(self, enabled: bool):
        self._emacs_mode = enabled
        for workspace in self._workspaces.values():
            workspace.set_emacs_mode(enabled)

    def set_view_mode(self, mode: str):
        self._view_mode = mode
        for workspace in self._workspaces.values():
            workspace.set_view_mode(mode)

    def set_font_size(self, size: int):
        size = max(6, min(72, size))
        self._font_size = size
        for workspace in self._workspaces.values():
            workspace.set_font_size(size)

    def increase_font_size(self):
        self.set_font_size(self._font_size + 1)

    def decrease_font_size(self):
        self.set_font_size(self._font_size - 1)

    def reset_font_size(self):
        self.set_font_size(11)

    def font_size(self) -> int:
        return self._font_size

    def _on_current_changed(self, _index: int):
        self.current_context_changed.emit()

    def _on_workspace_saved(self, path: str, _status_text: str):
        current = self.current_workspace()
        if current is not None and current.file_path == path:
            self.current_context_changed.emit()

    def _sync_visible_widget(self):
        self._stack.setCurrentWidget(self._tabs if self._tabs.count() else self._empty_label)

    def _retitle_tabs(self):
        relative_paths = {}
        basename_counts = {}
        for workspace in self._workspaces.values():
            rel = _safe_relpath(workspace.file_path, self._notes_root)
            relative_paths[workspace] = rel
            basename = os.path.basename(rel) or rel
            basename_counts[basename] = basename_counts.get(basename, 0) + 1

        for index in range(self._tabs.count()):
            workspace = self._tabs.widget(index)
            if not isinstance(workspace, NoteWorkspace):
                continue
            rel = relative_paths.get(workspace, os.path.basename(workspace.file_path))
            label = _tab_label(rel, basename_counts, workspace.is_modified)
            self._tabs.setTabText(index, label)
            self._tabs.setTabToolTip(index, workspace.file_path)
