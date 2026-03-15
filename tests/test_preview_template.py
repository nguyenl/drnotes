"""Tests for the preview panel HTML template.

Validates that the HTML template used by QWebEngineView.setHtml() stays
within the ~2 MB content limit and loads mermaid.min.js via an external
<script src> reference rather than inlining the full library.
"""

import re
from pathlib import Path

# Maximum bytes that QWebEngineView.setHtml() can reliably handle.
# Qt percent-encodes the content internally, so we use a conservative limit.
_SETHTML_MAX_BYTES = 2_000_000

# Locate the preview module without importing PySide6 (which needs a display).
_PREVIEW_PY = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "drnotes"
    / "widgets"
    / "preview.py"
)


def _read_source() -> str:
    return _PREVIEW_PY.read_text(encoding="utf-8")


# ── Tests ────────────────────────────────────────────────────────────────────


def test_template_does_not_inline_mermaid_js():
    """The template must reference mermaid.min.js externally, not inline it.

    Inlining the ~3 MB mermaid.min.js into _PAGE_TEMPLATE causes
    QWebEngineView.setHtml() to silently fail (blank page) because the
    content exceeds the ~2 MB limit.
    """
    source = _read_source()

    # There should be NO code path that reads mermaid.min.js and injects it
    # into the template string.  The pattern we're guarding against is:
    #   _PAGE_TEMPLATE = _PAGE_TEMPLATE.replace(..., f"<script>{_MERMAID_JS}</script>")
    assert "read_text" not in source or "<script>{_MERMAID_JS}</script>" not in source, (
        "mermaid.min.js must NOT be inlined into _PAGE_TEMPLATE — "
        "use <script src='mermaid.min.js'></script> with a baseUrl instead"
    )


def test_template_uses_script_src_for_mermaid():
    """The template should load mermaid via <script src=...>."""
    source = _read_source()
    assert re.search(r'<script\s+src=["\']mermaid\.min\.js["\']', source), (
        "Expected <script src='mermaid.min.js'> in the template"
    )


def test_sethtml_called_with_base_url():
    """setHtml must be called with a baseUrl so the browser can resolve
    the external mermaid.min.js reference."""
    source = _read_source()
    assert "setHtml(" in source
    # Look for setHtml being called with two arguments (template, base_url)
    # The pattern: setHtml(_PAGE_TEMPLATE, <something>)
    assert re.search(r"setHtml\(\s*_PAGE_TEMPLATE\s*,", source), (
        "setHtml() must be called with a baseUrl argument"
    )


def test_on_page_ready_checks_ok_parameter():
    """_on_page_ready must bail out when ok is False to avoid calling JS
    on a page that failed to load."""
    source = _read_source()
    # Find the _on_page_ready method body and verify it checks `ok`
    match = re.search(
        r"def _on_page_ready\(self,\s*ok:\s*bool\):(.*?)(?=\n    def |\nclass |\Z)",
        source,
        re.DOTALL,
    )
    assert match, "_on_page_ready method not found"
    body = match.group(1)
    assert "not ok" in body or "ok is False" in body or "if ok:" in body, (
        "_on_page_ready must check the ok parameter before marking page ready"
    )
