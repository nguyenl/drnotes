import re

from PySide6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat


class MarkdownHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Markdown text in a QPlainTextEdit."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules: list[tuple[re.Pattern, QTextCharFormat]] = []
        self._setup_formats()

    # -- helpers ---------------------------------------------------------------

    @staticmethod
    def _fmt(color: str, bold: bool = False, italic: bool = False) -> QTextCharFormat:
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        if bold:
            fmt.setFontWeight(QFont.Weight.Bold)
        if italic:
            fmt.setFontItalic(True)
        return fmt

    # -- format definitions ----------------------------------------------------

    def _setup_formats(self):
        rules = self._rules

        # headings
        rules.append((re.compile(r"^#{1,6}\s.*$", re.MULTILINE), self._fmt("#0550AE", bold=True)))

        # bold
        rules.append((re.compile(r"\*\*(.+?)\*\*"), self._fmt("#24292F", bold=True)))
        rules.append((re.compile(r"__(.+?)__"), self._fmt("#24292F", bold=True)))

        # italic
        rules.append((re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)"), self._fmt("#24292F", italic=True)))
        rules.append((re.compile(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)"), self._fmt("#24292F", italic=True)))

        # strikethrough
        rules.append((re.compile(r"~~.+?~~"), self._fmt("#6E7781")))

        # inline code
        rules.append((re.compile(r"`[^`]+`"), self._fmt("#953800")))

        # links  [text](url)
        rules.append((re.compile(r"\[([^\]]+)\]\([^)]+\)"), self._fmt("#0969DA")))

        # images  ![alt](url)
        rules.append((re.compile(r"!\[([^\]]*)\]\([^)]+\)"), self._fmt("#8250DF")))

        # blockquotes
        rules.append((re.compile(r"^>\s.*$", re.MULTILINE), self._fmt("#57606A", italic=True)))

        # unordered lists
        rules.append((re.compile(r"^\s*[-*+]\s", re.MULTILINE), self._fmt("#CF222E")))

        # ordered lists
        rules.append((re.compile(r"^\s*\d+\.\s", re.MULTILINE), self._fmt("#CF222E")))

        # checklists
        rules.append((re.compile(r"^\s*-\s\[[ xX]\]", re.MULTILINE), self._fmt("#CF222E", bold=True)))

        # horizontal rules
        rules.append((re.compile(r"^(-{3,}|\*{3,}|_{3,})\s*$", re.MULTILINE), self._fmt("#D0D7DE")))

        # fenced code block markers
        rules.append((re.compile(r"^```.*$", re.MULTILINE), self._fmt("#953800")))

    # -- main callback ---------------------------------------------------------

    def highlightBlock(self, text: str):
        for pattern, fmt in self._rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)
