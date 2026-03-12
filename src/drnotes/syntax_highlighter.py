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

    def _setup_formats(self, dark: bool = False):
        self._rules.clear()
        rules = self._rules

        if dark:
            heading_color  = "#79c0ff"
            body_color     = "#e6edf3"
            strike_color   = "#8b949e"
            code_color     = "#ffa657"
            link_color     = "#58a6ff"
            image_color    = "#d2a8ff"
            quote_color    = "#8b949e"
            list_color     = "#ff7b72"
            hr_color       = "#30363d"
        else:
            heading_color  = "#0550AE"
            body_color     = "#24292F"
            strike_color   = "#6E7781"
            code_color     = "#953800"
            link_color     = "#0969DA"
            image_color    = "#8250DF"
            quote_color    = "#57606A"
            list_color     = "#CF222E"
            hr_color       = "#D0D7DE"

        # headings
        rules.append((re.compile(r"^#{1,6}\s.*$", re.MULTILINE), self._fmt(heading_color, bold=True)))

        # bold
        rules.append((re.compile(r"\*\*(.+?)\*\*"), self._fmt(body_color, bold=True)))
        rules.append((re.compile(r"__(.+?)__"), self._fmt(body_color, bold=True)))

        # italic
        rules.append((re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)"), self._fmt(body_color, italic=True)))
        rules.append((re.compile(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)"), self._fmt(body_color, italic=True)))

        # strikethrough
        rules.append((re.compile(r"~~.+?~~"), self._fmt(strike_color)))

        # inline code
        rules.append((re.compile(r"`[^`]+`"), self._fmt(code_color)))

        # links  [text](url)
        rules.append((re.compile(r"\[([^\]]+)\]\([^)]+\)"), self._fmt(link_color)))

        # images  ![alt](url)
        rules.append((re.compile(r"!\[([^\]]*)\]\([^)]+\)"), self._fmt(image_color)))

        # blockquotes
        rules.append((re.compile(r"^>\s.*$", re.MULTILINE), self._fmt(quote_color, italic=True)))

        # unordered lists
        rules.append((re.compile(r"^\s*[-*+]\s", re.MULTILINE), self._fmt(list_color)))

        # ordered lists
        rules.append((re.compile(r"^\s*\d+\.\s", re.MULTILINE), self._fmt(list_color)))

        # checklists
        rules.append((re.compile(r"^\s*-\s\[[ xX]\]", re.MULTILINE), self._fmt(list_color, bold=True)))

        # horizontal rules
        rules.append((re.compile(r"^(-{3,}|\*{3,}|_{3,})\s*$", re.MULTILINE), self._fmt(hr_color)))

        # fenced code block markers
        rules.append((re.compile(r"^```.*$", re.MULTILINE), self._fmt(code_color)))

    def set_dark_mode(self, dark: bool):
        self._setup_formats(dark)
        self.rehighlight()

    # -- main callback ---------------------------------------------------------

    def highlightBlock(self, text: str):
        for pattern, fmt in self._rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)
