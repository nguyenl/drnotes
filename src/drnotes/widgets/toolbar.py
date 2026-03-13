from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import QToolBar


class FormattingToolbar(QToolBar):
    """Toolbar with markdown formatting buttons and keyboard shortcuts."""

    # signals carry (prefix, suffix) for wrap actions, or a single string for
    # line-prefix / block actions.  The main window connects these to the editor.
    wrap_requested = Signal(str, str)
    line_prefix_requested = Signal(str)
    block_requested = Signal(str)
    font_size_increase_requested = Signal()
    font_size_decrease_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("Formatting", parent)
        self.setMovable(False)
        self._build_actions()

    def _act(self, label: str, shortcut: str | None, callback,
             icon_name: str | None = None, tooltip: str | None = None):
        action = QAction(label, self)
        if icon_name:
            icon = QIcon.fromTheme(icon_name)
            if not icon.isNull():
                action.setIcon(icon)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        tip = tooltip or label
        if shortcut:
            tip = f"{tip} ({shortcut})"
        action.setToolTip(tip)
        action.triggered.connect(callback)
        self.addAction(action)
        return action

    def _build_actions(self):
        # -- inline formatting -------------------------------------------------
        self._act("B", "Ctrl+B", lambda: self.wrap_requested.emit("**", "**"),
                  "format-text-bold", "Bold")
        self._act("I", "Ctrl+I", lambda: self.wrap_requested.emit("*", "*"),
                  "format-text-italic", "Italic")
        self._act("S", "Ctrl+Shift+S", lambda: self.wrap_requested.emit("~~", "~~"),
                  "format-text-strikethrough", "Strikethrough")
        self._act("`", None, lambda: self.wrap_requested.emit("`", "`"),
                  tooltip="Inline Code")

        self.addSeparator()

        # -- headings ----------------------------------------------------------
        for level in range(1, 7):
            prefix = "#" * level + " "
            self._act(
                f"H{level}",
                f"Ctrl+{level}",
                # capture prefix by default arg
                lambda _=False, p=prefix: self.line_prefix_requested.emit(p),
                tooltip=f"Heading {level}",
            )

        self.addSeparator()

        # -- lists -------------------------------------------------------------
        self._act("UL", "Ctrl+Shift+U", lambda: self.line_prefix_requested.emit("- "),
                  "view-list-symbolic", "Unordered List")
        self._act("OL", "Ctrl+Shift+O", lambda: self.line_prefix_requested.emit("1. "),
                  tooltip="Ordered List")
        self._act("☐", "Ctrl+Shift+C", lambda: self.line_prefix_requested.emit("- [ ] "),
                  tooltip="Checklist")

        self.addSeparator()

        # -- block elements ----------------------------------------------------
        self._act("Code", "Ctrl+Shift+K", lambda: self.block_requested.emit("```\n\n```"),
                  tooltip="Code Block")
        self._act("Quote", "Ctrl+Shift+Q", lambda: self.line_prefix_requested.emit("> "),
                  tooltip="Blockquote")
        self._act("―", None, lambda: self.block_requested.emit("---"),
                  tooltip="Horizontal Rule")

        self.addSeparator()

        # -- links / images ----------------------------------------------------
        self._act("Link", "Ctrl+K", lambda: self.wrap_requested.emit("[", "](url)"),
                  "insert-link-symbolic", "Insert Link")
        self._act("Img", "Ctrl+Shift+I", lambda: self.wrap_requested.emit("![", "](path)"),
                  "insert-image", "Insert Image")

        self.addSeparator()

        # -- font size ---------------------------------------------------------
        self._act("A+", "Ctrl+=", lambda: self.font_size_increase_requested.emit(),
                  "zoom-in", "Increase Font Size")
        self._act("A\u2013", "Ctrl+-", lambda: self.font_size_decrease_requested.emit(),
                  "zoom-out", "Decrease Font Size")
