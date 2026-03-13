import re

from PySide6.QtCore import QEvent, QRect, QSize, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
    QKeyEvent,
    QPainter,
    QTextCursor,
    QTextDocument,
    QTextFormat,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..syntax_highlighter import MarkdownHighlighter

# regex matching list prefixes:  "- ", "* ", "+ ", "1. ", "- [ ] ", "- [x] "
_LIST_RE = re.compile(
    r"^(?P<indent>\s*)"
    r"(?P<marker>[-*+](?:\s\[[ xX]\])?\s|\d+\.\s)"
)

# Ctrl/Alt keys claimed by emacs mode (used in ShortcutOverride filtering)
_EMACS_CTRL_KEYS = frozenset({
    Qt.Key.Key_F, Qt.Key.Key_B, Qt.Key.Key_N, Qt.Key.Key_P,
    Qt.Key.Key_A, Qt.Key.Key_E, Qt.Key.Key_D, Qt.Key.Key_K,
    Qt.Key.Key_W, Qt.Key.Key_Y, Qt.Key.Key_Space, Qt.Key.Key_G,
    Qt.Key.Key_V, Qt.Key.Key_H,
})
_EMACS_ALT_KEYS = frozenset({
    Qt.Key.Key_F, Qt.Key.Key_B, Qt.Key.Key_D,
    Qt.Key.Key_V, Qt.Key.Key_W, Qt.Key.Key_Backspace,
})


# =============================================================================
# Line-number gutter
# =============================================================================


class _LineNumberArea(QWidget):
    def __init__(self, editor: "_EditorCore"):
        super().__init__(editor)
        self._editor = editor

    def sizeHint(self):
        return QSize(self._editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self._editor.line_number_area_paint_event(event)


# =============================================================================
# Find / Replace bar
# =============================================================================


class _FindReplaceBar(QWidget):
    def __init__(self, editor: "_EditorCore", parent=None):
        super().__init__(parent)
        self._editor = editor
        self._setup_ui()
        self.hide()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)

        self._find_input = QLineEdit()
        self._find_input.setPlaceholderText("Find…")
        self._find_input.returnPressed.connect(self.find_next)
        layout.addWidget(self._find_input)

        self._replace_input = QLineEdit()
        self._replace_input.setPlaceholderText("Replace…")
        layout.addWidget(self._replace_input)

        self._case_cb = QCheckBox("Aa")
        self._case_cb.setToolTip("Case sensitive")
        layout.addWidget(self._case_cb)

        for label, slot in [
            ("Next", self.find_next),
            ("Prev", self.find_prev),
            ("Replace", self.replace_one),
            ("All", self.replace_all),
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(slot)
            layout.addWidget(btn)

        close_btn = QPushButton("\u00d7")
        close_btn.setFixedWidth(24)
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn)

    def activate(self):
        self.show()
        self._find_input.setFocus()
        self._find_input.selectAll()

    # -- search helpers --------------------------------------------------------

    def _flags(self, backward=False):
        flags = QTextDocument.FindFlag(0)
        if backward:
            flags |= QTextDocument.FindFlag.FindBackward
        if self._case_cb.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        return flags

    def find_next(self):
        text = self._find_input.text()
        if not text:
            return
        if not self._editor.find(text, self._flags()):
            cursor = self._editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self._editor.setTextCursor(cursor)
            self._editor.find(text, self._flags())

    def find_prev(self):
        text = self._find_input.text()
        if not text:
            return
        if not self._editor.find(text, self._flags(backward=True)):
            cursor = self._editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self._editor.setTextCursor(cursor)
            self._editor.find(text, self._flags(backward=True))

    def replace_one(self):
        if self._editor.textCursor().hasSelection():
            self._editor.textCursor().insertText(self._replace_input.text())
        self.find_next()

    def replace_all(self):
        text = self._find_input.text()
        if not text:
            return
        content = self._editor.toPlainText()
        if self._case_cb.isChecked():
            new = content.replace(text, self._replace_input.text())
        else:
            new = re.sub(re.escape(text), self._replace_input.text(), content, flags=re.IGNORECASE)
        if new != content:
            self._editor.selectAll()
            self._editor.textCursor().insertText(new)


# =============================================================================
# Core text editor (QPlainTextEdit with line numbers + list behaviour)
# =============================================================================


class _EditorCore(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        # emacs mode state — must be set before any Qt calls that trigger event()
        self._emacs_mode = False
        self._emacs_mark_active = False

        # monospace font
        font = QFont("Consolas, 'Courier New', monospace")
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setFixedPitch(True)
        font.setPointSize(11)
        self.setFont(font)
        self._update_tab_stop()
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)

        # syntax highlighter
        self._highlighter = MarkdownHighlighter(self.document())

        # theme colors (light defaults)
        self._gutter_bg = QColor("#f6f8fa")
        self._gutter_fg = QColor("#8b949e")
        self._cur_line_bg = QColor("#f0f4ff")

        # line-number area
        self._line_area = _LineNumberArea(self)
        self.blockCountChanged.connect(self._update_line_area_width)
        self.updateRequest.connect(self._update_line_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)
        self._update_line_area_width()

    def set_dark_mode(self, dark: bool):
        if dark:
            self._gutter_bg = QColor("#161b22")
            self._gutter_fg = QColor("#8b949e")
            self._cur_line_bg = QColor("#1c2128")
        else:
            self._gutter_bg = QColor("#f6f8fa")
            self._gutter_fg = QColor("#8b949e")
            self._cur_line_bg = QColor("#f0f4ff")
        self._highlighter.set_dark_mode(dark)
        self._line_area.update()
        self._highlight_current_line()

    def set_emacs_mode(self, enabled: bool):
        self._emacs_mode = enabled
        if not enabled:
            self._emacs_mark_active = False
            cursor = self.textCursor()
            cursor.setPosition(cursor.position())
            self.setTextCursor(cursor)

    # -- font size -------------------------------------------------------------

    _MIN_FONT_SIZE = 6
    _MAX_FONT_SIZE = 72

    def set_font_size(self, size: int):
        size = max(self._MIN_FONT_SIZE, min(self._MAX_FONT_SIZE, size))
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)
        self._update_tab_stop()
        self._update_line_area_width()

    def increase_font_size(self):
        self.set_font_size(self.font().pointSize() + 1)

    def decrease_font_size(self):
        self.set_font_size(self.font().pointSize() - 1)

    def reset_font_size(self):
        self.set_font_size(11)

    def _update_tab_stop(self):
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 4)

    # -- emacs keybinding handling ---------------------------------------------

    def event(self, e):
        if self._emacs_mode and e.type() == QEvent.Type.ShortcutOverride:
            ctrl = e.modifiers() & Qt.KeyboardModifier.ControlModifier
            alt = e.modifiers() & Qt.KeyboardModifier.AltModifier
            no_shift = not (e.modifiers() & Qt.KeyboardModifier.ShiftModifier)
            if ctrl and no_shift and e.key() in _EMACS_CTRL_KEYS:
                e.accept()
                return True
            if alt and no_shift and e.key() in _EMACS_ALT_KEYS:
                e.accept()
                return True
        return super().event(e)

    def _emacs_handle(self, event: QKeyEvent) -> bool:
        """Dispatch emacs keybindings. Returns True if the event was consumed."""
        key = event.key()
        ctrl = event.modifiers() & Qt.KeyboardModifier.ControlModifier
        alt = event.modifiers() & Qt.KeyboardModifier.AltModifier
        no_shift = not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier)

        if not no_shift:
            return False
        if not ctrl and not alt:
            return False

        cursor = self.textCursor()

        def _move(op):
            mode = (
                QTextCursor.MoveMode.KeepAnchor
                if self._emacs_mark_active
                else QTextCursor.MoveMode.MoveAnchor
            )
            cursor.movePosition(op, mode)
            self.setTextCursor(cursor)

        def _kill_to_clipboard(selected_text: str):
            QApplication.clipboard().setText(selected_text.replace("\u2029", "\n"))

        if ctrl and not alt:
            if key == Qt.Key.Key_F:
                _move(QTextCursor.MoveOperation.Right)
            elif key == Qt.Key.Key_B:
                _move(QTextCursor.MoveOperation.Left)
            elif key == Qt.Key.Key_N:
                _move(QTextCursor.MoveOperation.Down)
            elif key == Qt.Key.Key_P:
                _move(QTextCursor.MoveOperation.Up)
            elif key == Qt.Key.Key_A:
                _move(QTextCursor.MoveOperation.StartOfLine)
            elif key == Qt.Key.Key_E:
                _move(QTextCursor.MoveOperation.EndOfLine)
            elif key == Qt.Key.Key_D:
                # delete char forward, ignoring any mark selection
                pos = cursor.position()
                cursor.setPosition(pos)
                cursor.deleteChar()
                self.setTextCursor(cursor)
            elif key == Qt.Key.Key_H:
                # delete char backward
                pos = cursor.position()
                cursor.setPosition(pos)
                cursor.deletePreviousChar()
                self.setTextCursor(cursor)
            elif key == Qt.Key.Key_K:
                # kill to end of line (or kill newline if at EOL)
                pos = cursor.position()
                cursor.setPosition(pos)
                cursor.movePosition(
                    QTextCursor.MoveOperation.EndOfLine,
                    QTextCursor.MoveMode.KeepAnchor,
                )
                if cursor.position() == pos:
                    cursor.movePosition(
                        QTextCursor.MoveOperation.Right,
                        QTextCursor.MoveMode.KeepAnchor,
                    )
                if cursor.hasSelection():
                    _kill_to_clipboard(cursor.selectedText())
                    cursor.removeSelectedText()
                    self.setTextCursor(cursor)
            elif key == Qt.Key.Key_W:
                # kill region (cut)
                if cursor.hasSelection():
                    _kill_to_clipboard(cursor.selectedText())
                    cursor.removeSelectedText()
                    self.setTextCursor(cursor)
                self._emacs_mark_active = False
            elif key == Qt.Key.Key_Y:
                # yank (paste)
                cursor.insertText(QApplication.clipboard().text())
                self.setTextCursor(cursor)
                self._emacs_mark_active = False
            elif key == Qt.Key.Key_Space:
                # set or clear mark
                if self._emacs_mark_active:
                    self._emacs_mark_active = False
                    cursor.setPosition(cursor.position())
                    self.setTextCursor(cursor)
                else:
                    self._emacs_mark_active = True
                    cursor.setPosition(cursor.position())
                    self.setTextCursor(cursor)
            elif key == Qt.Key.Key_G:
                # cancel: deactivate mark and clear selection
                self._emacs_mark_active = False
                cursor.setPosition(cursor.position())
                self.setTextCursor(cursor)
            elif key == Qt.Key.Key_V:
                sb = self.verticalScrollBar()
                sb.setValue(sb.value() + sb.pageStep())
            else:
                return False
            return True

        elif alt and not ctrl:
            if key == Qt.Key.Key_F:
                _move(QTextCursor.MoveOperation.NextWord)
            elif key == Qt.Key.Key_B:
                _move(QTextCursor.MoveOperation.PreviousWord)
            elif key == Qt.Key.Key_D:
                # kill word forward
                cursor.movePosition(
                    QTextCursor.MoveOperation.NextWord,
                    QTextCursor.MoveMode.KeepAnchor,
                )
                if cursor.hasSelection():
                    _kill_to_clipboard(cursor.selectedText())
                    cursor.removeSelectedText()
                    self.setTextCursor(cursor)
            elif key == Qt.Key.Key_Backspace:
                # kill word backward
                cursor.movePosition(
                    QTextCursor.MoveOperation.PreviousWord,
                    QTextCursor.MoveMode.KeepAnchor,
                )
                if cursor.hasSelection():
                    _kill_to_clipboard(cursor.selectedText())
                    cursor.removeSelectedText()
                    self.setTextCursor(cursor)
            elif key == Qt.Key.Key_V:
                sb = self.verticalScrollBar()
                sb.setValue(sb.value() - sb.pageStep())
            elif key == Qt.Key.Key_W:
                # copy region (save to clipboard, deselect)
                if cursor.hasSelection():
                    _kill_to_clipboard(cursor.selectedText())
                    cursor.setPosition(cursor.position())
                    self.setTextCursor(cursor)
                self._emacs_mark_active = False
            else:
                return False
            return True

        return False

    # -- line numbers ----------------------------------------------------------

    def line_number_area_width(self) -> int:
        digits = max(1, len(str(self.blockCount())))
        return 10 + self.fontMetrics().horizontalAdvance("9") * digits

    def _update_line_area_width(self):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_area(self, rect, dy):
        if dy:
            self._line_area.scroll(0, dy)
        else:
            self._line_area.update(0, rect.y(), self._line_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_line_area_width()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self._line_area)
        painter.fillRect(event.rect(), self._gutter_bg)
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(self._gutter_fg)
                painter.drawText(
                    0,
                    top,
                    self._line_area.width() - 4,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    str(block_number + 1),
                )
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1
        painter.end()

    def _highlight_current_line(self):
        extra = []
        if not self.isReadOnly():
            sel = QTextEdit.ExtraSelection()
            sel.format.setBackground(self._cur_line_bg)
            sel.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            sel.cursor = self.textCursor()
            sel.cursor.clearSelection()
            extra.append(sel)
        self.setExtraSelections(extra)

    # -- key handling: list continuation, indent/outdent -----------------------

    def keyPressEvent(self, event: QKeyEvent):
        # emacs bindings take priority when emacs mode is active
        if self._emacs_mode and self._emacs_handle(event):
            return

        # Tab / Shift+Tab for indentation
        if event.key() == Qt.Key.Key_Tab and not event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self._outdent()
            else:
                self._indent()
            return

        if event.key() == Qt.Key.Key_Backtab:
            self._outdent()
            return

        # Enter: list continuation
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self._handle_list_enter():
                return

        super().keyPressEvent(event)

    def _current_line_text(self) -> str:
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
        return cursor.selectedText()

    def _handle_list_enter(self) -> bool:
        line = self._current_line_text()
        m = _LIST_RE.match(line)
        if not m:
            return False

        indent = m.group("indent")
        marker = m.group("marker")

        # if the line is *only* the marker (empty item), remove marker and end list
        content_after_marker = line[m.end():]
        if not content_after_marker.strip():
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
            self.setTextCursor(cursor)
            return True

        # continue the list
        # for ordered lists, increment the number
        if re.match(r"\d+\.\s", marker):
            num = int(marker.split(".")[0])
            new_marker = f"{num + 1}. "
        elif re.match(r"[-*+]\s\[[ xX]\]\s", marker):
            # checklist → new unchecked item
            new_marker = marker[0] + " [ ] "
        else:
            new_marker = marker

        cursor = self.textCursor()
        cursor.insertText(f"\n{indent}{new_marker}")
        self.setTextCursor(cursor)
        return True

    def _indent(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            cursor.setPosition(start)
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
            text = cursor.selectedText()
            # QPlainTextEdit uses \u2029 as paragraph separator
            indented = text.replace("\u2029", "\u2029    ")
            indented = "    " + indented
            cursor.insertText(indented)
        else:
            cursor.insertText("    ")

    def _outdent(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            cursor.setPosition(start)
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
            text = cursor.selectedText()
            lines = text.split("\u2029")
            dedented = []
            for line in lines:
                if line.startswith("    "):
                    dedented.append(line[4:])
                elif line.startswith("\t"):
                    dedented.append(line[1:])
                else:
                    dedented.append(line)
            cursor.insertText("\u2029".join(dedented))
        else:
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
            line = cursor.selectedText()
            if line.startswith("    "):
                cursor.insertText(line[4:])
            elif line.startswith("\t"):
                cursor.insertText(line[1:])

    # -- formatting insertion helpers ------------------------------------------

    def insert_wrap(self, prefix: str, suffix: str):
        """Wrap current selection (or insert placeholder) with prefix/suffix."""
        cursor = self.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"{prefix}{text}{suffix}")
        else:
            cursor.insertText(f"{prefix}{suffix}")
            cursor.movePosition(
                QTextCursor.MoveOperation.Left,
                QTextCursor.MoveMode.MoveAnchor,
                len(suffix),
            )
            self.setTextCursor(cursor)

    def insert_line_prefix(self, prefix: str):
        """Insert a prefix at the start of the current line."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.insertText(prefix)

    def insert_block(self, text: str):
        """Insert a block of text at the cursor, ensuring blank lines around it."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
        cursor.insertText(f"\n\n{text}\n")
        self.setTextCursor(cursor)


# =============================================================================
# Public MarkdownEditor widget (wraps core editor + find bar)
# =============================================================================


class MarkdownEditor(QWidget):
    """Composite widget: find/replace bar + core editor."""

    content_changed = Signal(str)
    scroll_fraction_changed = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_file: str | None = None
        self._modified = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._editor = _EditorCore(self)
        self._find_bar = _FindReplaceBar(self._editor, self)

        layout.addWidget(self._find_bar)
        layout.addWidget(self._editor)

        self._editor.textChanged.connect(self._on_text_changed)
        self._editor.verticalScrollBar().valueChanged.connect(self._on_scroll_changed)

    # -- public API ------------------------------------------------------------

    @property
    def current_file(self) -> str | None:
        return self._current_file

    @property
    def is_modified(self) -> bool:
        return self._modified

    def open_file(self, path: str):
        self.save_current()
        try:
            text = open(path, encoding="utf-8").read()
        except OSError:
            return
        self._current_file = path
        self._editor.setPlainText(text)
        self._modified = False

    def save_current(self):
        if self._current_file and self._modified:
            try:
                with open(self._current_file, "w", encoding="utf-8") as f:
                    f.write(self._editor.toPlainText())
            except OSError:
                pass
            self._modified = False

    def get_text(self) -> str:
        return self._editor.toPlainText()

    def set_text_content(self, text: str):
        """Replace editor content programmatically (e.g. checkbox toggle)."""
        pos = self._editor.textCursor().position()
        sb = self._editor.verticalScrollBar()
        scroll_val = sb.value()
        sb.valueChanged.disconnect(self._on_scroll_changed)
        self._editor.setPlainText(text)
        cursor = self._editor.textCursor()
        cursor.setPosition(min(pos, len(text)))
        self._editor.setTextCursor(cursor)
        sb.setValue(scroll_val)
        sb.valueChanged.connect(self._on_scroll_changed)

    def set_dark_mode(self, dark: bool):
        self._editor.set_dark_mode(dark)

    def set_emacs_mode(self, enabled: bool):
        self._editor.set_emacs_mode(enabled)

    def set_font_size(self, size: int):
        self._editor.set_font_size(size)

    def increase_font_size(self):
        self._editor.increase_font_size()

    def decrease_font_size(self):
        self._editor.decrease_font_size()

    def reset_font_size(self):
        self._editor.reset_font_size()

    def font_size(self) -> int:
        return self._editor.font().pointSize()

    def show_find(self):
        self._find_bar.activate()

    def goto_line(self, line: int):
        """Move cursor to the given line number (1-based) and center it."""
        block = self._editor.document().findBlockByLineNumber(line - 1)
        if block.isValid():
            cursor = QTextCursor(block)
            self._editor.setTextCursor(cursor)
            self._editor.centerCursor()

    # -- formatting passthrough ------------------------------------------------

    def insert_wrap(self, prefix: str, suffix: str):
        self._editor.insert_wrap(prefix, suffix)

    def insert_line_prefix(self, prefix: str):
        self._editor.insert_line_prefix(prefix)

    def insert_block(self, text: str):
        self._editor.insert_block(text)

    # -- internal --------------------------------------------------------------

    def _on_text_changed(self):
        self._modified = True
        self.content_changed.emit(self._editor.toPlainText())

    def _on_scroll_changed(self):
        sb = self._editor.verticalScrollBar()
        fraction = sb.value() / sb.maximum() if sb.maximum() > 0 else 0.0
        self.scroll_fraction_changed.emit(fraction)

    def adjust_scroll_by(self, delta_y: float):
        sb = self._editor.verticalScrollBar()
        lines = round(delta_y / 40.0)
        sb.setValue(sb.value() + lines)
