from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QToolBar


class FormattingToolbar(QToolBar):
    """Toolbar with markdown formatting buttons and keyboard shortcuts."""

    # signals carry (prefix, suffix) for wrap actions, or a single string for
    # line-prefix / block actions.  The main window connects these to the editor.
    wrap_requested = Signal(str, str)
    line_prefix_requested = Signal(str)
    block_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__("Formatting", parent)
        self.setMovable(False)
        self._build_actions()

    def _act(self, label: str, shortcut: str | None, callback):
        action = QAction(label, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(callback)
        self.addAction(action)
        return action

    def _build_actions(self):
        # -- inline formatting -------------------------------------------------
        self._act("B",  "Ctrl+B", lambda: self.wrap_requested.emit("**", "**"))
        self._act("I",  "Ctrl+I", lambda: self.wrap_requested.emit("*", "*"))
        self._act("S",  "Ctrl+Shift+S", lambda: self.wrap_requested.emit("~~", "~~"))
        self._act("`",  None, lambda: self.wrap_requested.emit("`", "`"))

        self.addSeparator()

        # -- headings ----------------------------------------------------------
        for level in range(1, 7):
            prefix = "#" * level + " "
            self._act(
                f"H{level}",
                f"Ctrl+{level}",
                # capture prefix by default arg
                lambda _=False, p=prefix: self.line_prefix_requested.emit(p),
            )

        self.addSeparator()

        # -- lists -------------------------------------------------------------
        self._act("UL",  "Ctrl+Shift+U", lambda: self.line_prefix_requested.emit("- "))
        self._act("OL",  "Ctrl+Shift+O", lambda: self.line_prefix_requested.emit("1. "))
        self._act("[ ]", "Ctrl+Shift+C", lambda: self.line_prefix_requested.emit("- [ ] "))

        self.addSeparator()

        # -- block elements ----------------------------------------------------
        self._act("Code", "Ctrl+Shift+K", lambda: self.block_requested.emit("```\n\n```"))
        self._act("Quote", "Ctrl+Shift+Q", lambda: self.line_prefix_requested.emit("> "))
        self._act("---", None, lambda: self.block_requested.emit("---"))

        self.addSeparator()

        # -- links / images ----------------------------------------------------
        self._act("Link", "Ctrl+K", lambda: self.wrap_requested.emit("[", "](url)"))
        self._act("Img",  "Ctrl+Shift+I", lambda: self.wrap_requested.emit("![", "](path)"))
