import os
import shutil
from pathlib import Path

from PySide6.QtCore import QDir, Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFileSystemModel,
    QHBoxLayout,
    QInputDialog,
    QMenu,
    QMessageBox,
    QPushButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)


class DirectoryTree(QWidget):
    """Left-panel file/folder browser restricted to .md files."""

    file_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._root_path = ""
        self._setup_ui()

    # -- UI setup --------------------------------------------------------------

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # button bar
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(4, 4, 4, 4)
        self._new_file_btn = QPushButton("+ Note")
        self._new_folder_btn = QPushButton("+ Folder")
        self._new_file_btn.clicked.connect(self._create_new_file)
        self._new_folder_btn.clicked.connect(self._create_new_folder)
        btn_layout.addWidget(self._new_file_btn)
        btn_layout.addWidget(self._new_folder_btn)
        layout.addLayout(btn_layout)

        # filesystem model
        self._model = QFileSystemModel()
        self._model.setNameFilters(["*.md"])
        self._model.setNameFilterDisables(False)
        self._model.setFilter(
            QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot
        )

        # tree view
        self._tree = QTreeView()
        self._tree.setModel(self._model)
        self._tree.setHeaderHidden(True)
        for col in (1, 2, 3):
            self._tree.hideColumn(col)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._show_context_menu)
        self._tree.clicked.connect(self._on_clicked)
        self._tree.setDragDropMode(QTreeView.DragDropMode.InternalMove)
        self._tree.setDragEnabled(True)
        self._tree.setAcceptDrops(True)
        self._tree.setDropIndicatorShown(True)
        self._tree.setAnimated(True)
        self._tree.setIndentation(16)

        layout.addWidget(self._tree)

    # -- public API ------------------------------------------------------------

    def set_root(self, path: str):
        self._root_path = path
        self._model.setRootPath(path)
        self._tree.setRootIndex(self._model.index(path))

    # -- helpers ---------------------------------------------------------------

    def _selected_path(self) -> str | None:
        indexes = self._tree.selectedIndexes()
        if indexes:
            return self._model.filePath(indexes[0])
        return None

    def _selected_dir(self) -> str:
        path = self._selected_path()
        if path and os.path.isfile(path):
            return os.path.dirname(path)
        return path or self._root_path

    # -- slots -----------------------------------------------------------------

    def _on_clicked(self, index):
        path = self._model.filePath(index)
        if os.path.isfile(path) and path.endswith(".md"):
            self.file_selected.emit(path)

    def _show_context_menu(self, position):
        menu = QMenu(self)

        new_file = QAction("New Note", self)
        new_file.triggered.connect(self._create_new_file)
        menu.addAction(new_file)

        new_folder = QAction("New Folder", self)
        new_folder.triggered.connect(self._create_new_folder)
        menu.addAction(new_folder)

        if self._selected_path():
            menu.addSeparator()
            rename = QAction("Rename", self)
            rename.triggered.connect(self._rename_selected)
            menu.addAction(rename)

            delete = QAction("Delete", self)
            delete.triggered.connect(self._delete_selected)
            menu.addAction(delete)

        menu.exec(self._tree.viewport().mapToGlobal(position))

    # -- file operations -------------------------------------------------------

    def _create_new_file(self):
        parent_dir = self._selected_dir()
        name, ok = QInputDialog.getText(self, "New Note", "Note name:")
        if ok and name:
            if not name.endswith(".md"):
                name += ".md"
            filepath = os.path.join(parent_dir, name)
            if not os.path.exists(filepath):
                Path(filepath).write_text("", encoding="utf-8")
                self.file_selected.emit(filepath)

    def _create_new_folder(self):
        parent_dir = self._selected_dir()
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if ok and name:
            os.makedirs(os.path.join(parent_dir, name), exist_ok=True)

    def _rename_selected(self):
        path = self._selected_path()
        if not path:
            return
        old_name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(self, "Rename", "New name:", text=old_name)
        if ok and new_name and new_name != old_name:
            new_path = os.path.join(os.path.dirname(path), new_name)
            if os.path.exists(new_path):
                reply = QMessageBox.question(
                    self,
                    "Overwrite?",
                    f"'{new_name}' already exists. Overwrite it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            os.rename(path, new_path)

    def _delete_selected(self):
        path = self._selected_path()
        if not path:
            return
        name = os.path.basename(path)
        reply = QMessageBox.question(
            self,
            "Delete",
            f"Delete '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
