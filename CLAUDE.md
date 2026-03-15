# drnotes Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-15

## Active Technologies

- Python 3.10+ + PySide6 >=6.6.0 (Qt 6 GUI), markdown >=3.5, pymdown-extensions >=10.0, Pygments >=2.17 (001-establishing-baseline-specs)

## Project Structure

```text
src/drnotes/
├── app.py                  # Entry point
├── main_window.py          # Main window, menus, signal hub
├── settings.py             # QSettings wrapper
├── syntax_highlighter.py   # Markdown highlighting
└── widgets/
    ├── editor.py           # Markdown editor with find/replace
    ├── preview.py          # HTML preview with Mermaid
    ├── directory_tree.py   # File browser
    ├── search_panel.py     # Cross-file search
    └── toolbar.py          # Formatting toolbar
```

## Commands

```bash
pip install -e .            # Install in dev mode
drnotes                     # Run the application
python -m drnotes           # Alternative run
pip install -e ".[package]" # Install packaging deps
bash package.sh             # Build standalone binary
```

## Code Style

Python 3.10+: Follow standard conventions

## Recent Changes

- 001-establishing-baseline-specs: Added Python 3.10+ + PySide6 >=6.6.0 (Qt 6 GUI), markdown >=3.5, pymdown-extensions >=10.0, Pygments >=2.17

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
