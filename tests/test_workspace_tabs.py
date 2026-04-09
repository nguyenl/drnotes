from drnotes.widgets.workspace_tabs import _tab_label


def test_tab_label_uses_basename_when_unique():
    counts = {"note.md": 1}
    assert _tab_label("folder/note.md", counts, modified=False) == "note.md"


def test_tab_label_uses_relative_path_when_names_collide():
    counts = {"note.md": 2}
    assert _tab_label("project-a/note.md", counts, modified=False) == "project-a/note.md"


def test_tab_label_marks_modified_tabs():
    counts = {"note.md": 1}
    assert _tab_label("folder/note.md", counts, modified=True) == "* note.md"
