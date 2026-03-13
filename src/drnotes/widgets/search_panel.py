import os
import re

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class SearchPanel(QWidget):
    """Panel for searching text across all .md files in the notes directory."""

    result_selected = Signal(str, int)  # (file_path, line_number)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._root_path = ""
        self._setup_ui()
        self.hide()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # header row: title + close button
        header = QHBoxLayout()
        header.addWidget(QLabel("Search in Files"))
        close_btn = QPushButton("\u00d7")
        close_btn.setFixedWidth(24)
        close_btn.clicked.connect(self.hide)
        header.addStretch()
        header.addWidget(close_btn)
        layout.addLayout(header)

        # search input row
        input_row = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search all notes\u2026")
        self._search_input.returnPressed.connect(self._run_search)
        input_row.addWidget(self._search_input)

        self._case_cb = QCheckBox("Aa")
        self._case_cb.setToolTip("Case sensitive")
        input_row.addWidget(self._case_cb)

        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self._run_search)
        input_row.addWidget(search_btn)
        layout.addLayout(input_row)

        # status label
        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: #57606a; font-size: 11px;")
        layout.addWidget(self._status_label)

        # results tree
        self._results_tree = QTreeWidget()
        self._results_tree.setHeaderHidden(True)
        self._results_tree.setIndentation(16)
        self._results_tree.setAnimated(True)
        self._results_tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self._results_tree)

    # -- public API ------------------------------------------------------------

    def set_root(self, path: str):
        self._root_path = path

    def activate(self):
        self.show()
        self._search_input.setFocus()
        self._search_input.selectAll()

    # -- search logic ----------------------------------------------------------

    def _run_search(self):
        query = self._search_input.text()
        if not query or not self._root_path:
            return

        self._results_tree.clear()
        case_sensitive = self._case_cb.isChecked()
        flags = 0 if case_sensitive else re.IGNORECASE

        try:
            pattern = re.compile(re.escape(query), flags)
        except re.error:
            self._status_label.setText("Invalid search pattern")
            return

        total_matches = 0
        total_files = 0

        for dirpath, _dirs, filenames in os.walk(self._root_path):
            for filename in sorted(filenames):
                if not filename.endswith(".md"):
                    continue
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, encoding="utf-8") as f:
                        lines = f.readlines()
                except OSError:
                    continue

                file_matches = []
                for line_num, line in enumerate(lines, start=1):
                    if pattern.search(line):
                        file_matches.append((line_num, line.rstrip("\n")))

                if file_matches:
                    total_files += 1
                    total_matches += len(file_matches)
                    rel_path = os.path.relpath(filepath, self._root_path)
                    file_item = QTreeWidgetItem(
                        [f"{rel_path}  ({len(file_matches)})"]
                    )
                    file_item.setData(0, Qt.ItemDataRole.UserRole, filepath)
                    file_item.setData(0, Qt.ItemDataRole.UserRole + 1, 0)

                    for line_num, line_text in file_matches:
                        preview = line_text.strip()
                        if len(preview) > 120:
                            preview = preview[:120] + "\u2026"
                        match_item = QTreeWidgetItem(
                            [f"  {line_num}: {preview}"]
                        )
                        match_item.setData(
                            0, Qt.ItemDataRole.UserRole, filepath
                        )
                        match_item.setData(
                            0, Qt.ItemDataRole.UserRole + 1, line_num
                        )
                        file_item.addChild(match_item)

                    self._results_tree.addTopLevelItem(file_item)
                    file_item.setExpanded(True)

        if total_matches == 0:
            self._status_label.setText(f'No results for "{query}"')
        else:
            self._status_label.setText(
                f"{total_matches} match{'es' if total_matches != 1 else ''} "
                f"in {total_files} file{'s' if total_files != 1 else ''}"
            )

    # -- result navigation -----------------------------------------------------

    def _on_item_double_clicked(self, item: QTreeWidgetItem, _column: int):
        filepath = item.data(0, Qt.ItemDataRole.UserRole)
        line_num = item.data(0, Qt.ItemDataRole.UserRole + 1)
        if filepath:
            self.result_selected.emit(filepath, line_num or 1)
