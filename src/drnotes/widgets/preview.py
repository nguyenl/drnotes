import base64

import markdown
from pygments.formatters import HtmlFormatter
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QVBoxLayout, QWidget

# ---------------------------------------------------------------------------
# HTML shell loaded once; content is hot-swapped via JS to preserve scroll
# ---------------------------------------------------------------------------

_PAGE_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 14px;
    line-height: 1.6;
    color: #24292f;
    background: #ffffff;
    padding: 16px 24px;
    max-width: 900px;
    margin: 0 auto;
}
h1, h2, h3, h4, h5, h6 {
    margin-top: 24px; margin-bottom: 16px;
    font-weight: 600; line-height: 1.25;
}
h1 { font-size: 2em; padding-bottom: .3em; border-bottom: 1px solid #d0d7de; }
h2 { font-size: 1.5em; padding-bottom: .3em; border-bottom: 1px solid #d0d7de; }
h3 { font-size: 1.25em; }
code {
    background: #f6f8fa; border-radius: 6px;
    padding: .2em .4em; font-size: 85%;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
}
pre {
    background: #f6f8fa; border-radius: 6px;
    padding: 16px; overflow: auto; line-height: 1.45;
}
pre code { background: transparent; padding: 0; font-size: 100%; }
blockquote {
    color: #57606a; border-left: 4px solid #d0d7de;
    padding: 0 16px; margin: 0 0 16px 0;
}
table { border-collapse: collapse; width: 100%; margin-bottom: 16px; }
th, td { border: 1px solid #d0d7de; padding: 6px 13px; }
th { background: #f6f8fa; font-weight: 600; }
img { max-width: 100%; }
a { color: #0969da; text-decoration: none; }
a:hover { text-decoration: underline; }
hr { border: none; border-top: 1px solid #d0d7de; margin: 24px 0; }
ul, ol { padding-left: 2em; }
li { margin-top: .25em; }
.task-list-item { list-style-type: none; margin-left: -1.5em; }
.task-list-item input[type="checkbox"] { margin-right: .5em; cursor: pointer; }
.mermaid { text-align: center; margin: 16px 0; }
.mermaid-error { color: #cf222e; background: #fff5f5; padding: 8px 12px;
    border-radius: 6px; border: 1px solid #cf222e; white-space: pre-wrap; }
body.sync-scroll { scrollbar-width: none; -ms-overflow-style: none; }
body.sync-scroll::-webkit-scrollbar { display: none; }
/* dark mode */
body.dark { color: #e6edf3; background: #0d1117; }
body.dark h1, body.dark h2 { border-bottom-color: #30363d; }
body.dark code { background: #161b22; }
body.dark pre { background: #161b22; }
body.dark blockquote { color: #8b949e; border-left-color: #30363d; }
body.dark th, body.dark td { border-color: #30363d; }
body.dark th { background: #161b22; }
body.dark a { color: #58a6ff; }
body.dark hr { border-top-color: #30363d; }
body.dark .mermaid-error { color: #ff7b72; background: #1a0a0a; border-color: #ff7b72; }
/* syntax highlighting */
.highlight { border-radius: 6px; overflow: auto; }
.highlight pre { margin: 0; padding: 16px; line-height: 1.45; background: transparent; }
.highlight pre code { padding: 0; font-size: 100%; }
%%PYGMENTS_CSS%%
</style>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script src="qrc:///qtwebchannel/qwebchannel.js"></script>
<script>
var bridge = null;
var _scrollSyncEnabled = false;
var _lastScrollFraction = 0;
var _darkMode = false;
document.addEventListener("DOMContentLoaded", function() {
    mermaid.initialize({ startOnLoad: false, theme: "default" });
    if (typeof qt !== "undefined") {
        new QWebChannel(qt.webChannelTransport, function(channel) {
            bridge = channel.objects.bridge;
        });
    }
});

window.addEventListener('wheel', function(e) {
    if (_scrollSyncEnabled && bridge) {
        e.preventDefault();
        bridge.on_wheel(e.deltaY);
    }
}, { passive: false });

function setFontSize(px) {
    document.body.style.fontSize = px + "px";
}

function setDarkMode(enabled) {
    _darkMode = enabled;
    if (enabled) {
        document.body.classList.add('dark');
        mermaid.initialize({ startOnLoad: false, theme: 'dark' });
    } else {
        document.body.classList.remove('dark');
        mermaid.initialize({ startOnLoad: false, theme: 'default' });
    }
}

function setScrollSync(enabled) {
    _scrollSyncEnabled = enabled;
    if (enabled) {
        document.body.classList.add('sync-scroll');
    } else {
        document.body.classList.remove('sync-scroll');
    }
}

function setScrollFraction(f) {
    _lastScrollFraction = f;
    var maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    if (maxScroll > 0) {
        window.scrollTo(0, maxScroll * f);
    }
}

function updateContent(b64) {
    var html = new TextDecoder().decode(Uint8Array.from(atob(b64), function(c) { return c.charCodeAt(0); }));
    var el = document.getElementById("content");
    el.innerHTML = html;

    // render mermaid diagrams
    var diagrams = el.querySelectorAll(".mermaid-source");
    diagrams.forEach(function(pre, i) {
        var src = pre.textContent;
        var container = document.createElement("div");
        container.className = "mermaid";
        container.id = "mermaid-" + i;
        container.textContent = src;
        pre.replaceWith(container);
    });
    if (diagrams.length > 0) {
        mermaid.run({ querySelector: ".mermaid" }).catch(function(err) {
            el.querySelectorAll(".mermaid").forEach(function(d) {
                if (!d.querySelector("svg")) {
                    d.className = "mermaid-error";
                    d.textContent = "Mermaid error: " + err;
                }
            });
        });
    }

    // wire interactive checkboxes
    var cbs = el.querySelectorAll(".task-list-item input[type=\\"checkbox\\"]");
    cbs.forEach(function(cb, idx) {
        cb.disabled = false;
        cb.addEventListener("change", function() {
            if (bridge) bridge.toggle_checkbox(idx, cb.checked);
        });
    });

    // restore scroll position after content update
    if (_scrollSyncEnabled) {
        requestAnimationFrame(function() {
            setScrollFraction(_lastScrollFraction);
        });
    }
}
</script>
</head>
<body><div id="content"></div></body>
</html>
"""

# Inject Pygments syntax-highlighting CSS for light and dark themes
_PYGMENTS_CSS = "\n".join([
    HtmlFormatter(style="tango").get_style_defs(".highlight"),
    ".highlight { background: #f6f8fa; }",
    HtmlFormatter(style="github-dark").get_style_defs("body.dark .highlight"),
    "body.dark .highlight { background: #161b22; }",
])
_PAGE_TEMPLATE = _PAGE_TEMPLATE.replace("%%PYGMENTS_CSS%%", _PYGMENTS_CSS)


# ---------------------------------------------------------------------------
# Bridge object exposed to JS via QWebChannel
# ---------------------------------------------------------------------------


class _Bridge(QObject):
    checkbox_toggled = Signal(int, bool)
    wheel_event = Signal(float)

    @Slot(int, bool)
    def toggle_checkbox(self, index: int, checked: bool):
        self.checkbox_toggled.emit(index, checked)

    @Slot(float)
    def on_wheel(self, delta_y: float):
        self.wheel_event.emit(delta_y)


# ---------------------------------------------------------------------------
# Mermaid-aware custom fence formatter for pymdownx.superfences
# ---------------------------------------------------------------------------


def _mermaid_fence(source, language, css_class, options, md, **kwargs):
    """Render mermaid fenced blocks as a <pre> that JS will upgrade."""
    import html as _html

    escaped = _html.escape(source, quote=True)
    return f'<pre class="mermaid-source">{escaped}</pre>'


# ---------------------------------------------------------------------------
# PreviewPanel widget
# ---------------------------------------------------------------------------


class PreviewPanel(QWidget):
    """Renders markdown to HTML in a QWebEngineView with mermaid support."""

    checkbox_toggled = Signal(int, bool)
    wheel_event = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._page_ready = False
        self._scroll_sync = False
        self._dark_mode = False
        self._font_size_px: int | None = None
        self._pending: str | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._view = QWebEngineView()
        layout.addWidget(self._view)

        # web channel for checkbox interaction
        self._bridge = _Bridge()
        self._bridge.checkbox_toggled.connect(self.checkbox_toggled)
        self._bridge.wheel_event.connect(self.wheel_event)

        self._channel = QWebChannel()
        self._channel.registerObject("bridge", self._bridge)
        self._view.page().setWebChannel(self._channel)

        # load the shell page
        self._view.page().loadFinished.connect(self._on_page_ready)
        self._view.setHtml(_PAGE_TEMPLATE)

        # markdown renderer
        self._md = markdown.Markdown(
            extensions=[
                "pymdownx.highlight",
                "pymdownx.superfences",
                "pymdownx.tasklist",
                "tables",
                "pymdownx.tilde",
                "nl2br",
                "sane_lists",
            ],
            extension_configs={
                "pymdownx.highlight": {
                    "use_pygments": True,
                    "css_class": "highlight",
                    "guess_lang": False,
                },
                "pymdownx.superfences": {
                    "custom_fences": [
                        {
                            "name": "mermaid",
                            "class": "mermaid",
                            "format": _mermaid_fence,
                        }
                    ]
                },
                "pymdownx.tasklist": {
                    "custom_checkbox": False,
                    "clickable_checkbox": False,
                },
            },
        )

    # -- public API ------------------------------------------------------------

    def update_content(self, markdown_text: str):
        html = self._render(markdown_text)
        if self._page_ready:
            self._push(html)
        else:
            self._pending = html

    def set_scroll_fraction(self, fraction: float):
        if self._page_ready:
            self._view.page().runJavaScript(f"setScrollFraction({fraction});")

    def set_scroll_sync(self, enabled: bool):
        self._scroll_sync = enabled
        if self._page_ready:
            self._view.page().runJavaScript(
                f"setScrollSync({'true' if enabled else 'false'});"
            )

    # -- internals -------------------------------------------------------------

    def set_font_size(self, editor_pt: int):
        """Set preview font size proportional to the editor point size."""
        self._font_size_px = round(editor_pt * 14 / 11)
        if self._page_ready:
            self._view.page().runJavaScript(f"setFontSize({self._font_size_px});")

    def set_dark_mode(self, enabled: bool):
        self._dark_mode = enabled
        if self._page_ready:
            js = "true" if enabled else "false"
            self._view.page().runJavaScript(f"setDarkMode({js});")

    def _on_page_ready(self, ok: bool):
        self._page_ready = True
        if self._dark_mode:
            self._view.page().runJavaScript("setDarkMode(true);")
        if self._scroll_sync:
            self._view.page().runJavaScript("setScrollSync(true);")
        if self._font_size_px is not None:
            self._view.page().runJavaScript(f"setFontSize({self._font_size_px});")
        if self._pending is not None:
            self._push(self._pending)
            self._pending = None

    def _render(self, text: str) -> str:
        self._md.reset()
        return self._md.convert(text)

    def _push(self, html: str):
        b64 = base64.b64encode(html.encode("utf-8")).decode("ascii")
        self._view.page().runJavaScript(f"updateContent('{b64}');")
