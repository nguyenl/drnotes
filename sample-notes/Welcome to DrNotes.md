# Welcome to DrNotes

This is a sample note showcasing all supported markdown features and mermaid diagrams.

---

## Text Formatting

Here is **bold text**, *italic text*, and ***bold italic*** together. You can also use ~~strikethrough~~ for deleted content. Inline `code` looks like this.

Links work too: [Visit GitHub](https://github.com) and images can be embedded:

![Placeholder](https://via.placeholder.com/400x100.png?text=DrNotes+Sample+Image)

---

## Headings

### Third Level
#### Fourth Level
##### Fifth Level
###### Sixth Level

---

## Lists

### Unordered List

- First item
- Second item
  - Nested item A
  - Nested item B
    - Deeply nested
- Third item

### Ordered List

1. Step one
2. Step two
   1. Sub-step 2a
   2. Sub-step 2b
3. Step three

### Checklists

- [x] Write the product requirements document
- [x] Set up the project structure
- [x] Implement the markdown editor
- [x] Add full-text search
- [x] Package the app for distribution
  - [x] Linux
  - [x] macOS
  - [x] Windows

---

## Blockquotes

> "The best way to predict the future is to invent it."
> — Alan Kay

> Blockquotes can be nested:
>
> > This is a nested blockquote.
> >
> > > And a third level.

---

## Tables

| Feature         | Status      | Priority  |
|-----------------|-------------|-----------|
| Markdown Editor | Done        | Must have |
| Live Preview    | Done        | Must have |
| Mermaid Support | Done        | Must have |
| Full-text Search| Planned     | Future    |
| PDF Export      | Not started | Future    |

| Left Aligned | Center Aligned | Right Aligned |
|:-------------|:--------------:|--------------:|
| Row 1        | Data           |          100  |
| Row 2        | More data      |        2,500  |
| Row 3        | Even more      |       48,000  |

---

## Code Blocks

### Python

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Note:
    title: str
    path: Path
    tags: list[str]

    def word_count(self) -> int:
        text = self.path.read_text(encoding="utf-8")
        return len(text.split())

    def __str__(self) -> str:
        return f"[{', '.join(self.tags)}] {self.title} ({self.word_count()} words)"


if __name__ == "__main__":
    note = Note("Ideas", Path("ideas.md"), ["brainstorm", "draft"])
    print(note)
```

### JavaScript

```javascript
class MarkdownRenderer {
  constructor(element) {
    this.el = element;
    this.plugins = new Map();
  }

  use(name, plugin) {
    this.plugins.set(name, plugin);
    return this; // chainable
  }

  async render(source) {
    let html = this.#parseMarkdown(source);
    for (const [name, plugin] of this.plugins) {
      html = await plugin.transform(html);
    }
    this.el.innerHTML = html;
  }

  #parseMarkdown(src) {
    return src
      .replace(/^### (.+)$/gm, "<h3>$1</h3>")
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.+?)\*/g, "<em>$1</em>");
  }
}
```

### Rust

```rust
use std::collections::HashMap;
use std::fs;

#[derive(Debug)]
struct NoteIndex {
    notes: HashMap<String, Vec<String>>,
}

impl NoteIndex {
    fn new() -> Self {
        Self { notes: HashMap::new() }
    }

    fn add(&mut self, tag: &str, path: &str) {
        self.notes
            .entry(tag.to_string())
            .or_default()
            .push(path.to_string());
    }

    fn search(&self, tag: &str) -> Option<&Vec<String>> {
        self.notes.get(tag)
    }
}

fn main() -> std::io::Result<()> {
    let mut index = NoteIndex::new();
    for entry in fs::read_dir("./notes")? {
        let path = entry?.path();
        if path.extension().map_or(false, |e| e == "md") {
            index.add("all", path.to_str().unwrap());
        }
    }
    println!("{:#?}", index);
    Ok(())
}
```

### SQL

```sql
CREATE TABLE notes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    content     TEXT NOT NULL,
    folder_id   INTEGER REFERENCES folders(id),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT n.title,
       f.name AS folder,
       LENGTH(n.content) AS size_chars
  FROM notes n
  JOIN folders f ON f.id = n.folder_id
 WHERE n.updated_at > DATE('now', '-7 days')
 ORDER BY n.updated_at DESC
 LIMIT 20;
```

### Bash

```bash
#!/usr/bin/env bash
set -euo pipefail

NOTES_DIR="${1:-$HOME/notes}"
QUERY="$2"

echo "Searching '$QUERY' in $NOTES_DIR ..."
grep -rn --include="*.md" --color=always "$QUERY" "$NOTES_DIR" | while IFS= read -r line; do
    file=$(echo "$line" | cut -d: -f1)
    lineno=$(echo "$line" | cut -d: -f2)
    echo "  [$file:$lineno] $(echo "$line" | cut -d: -f3-)"
done

echo "Done. $(grep -rl --include='*.md' "$QUERY" "$NOTES_DIR" | wc -l) files matched."
```

---

## Mermaid Diagrams

### Flowchart

```mermaid
flowchart TD
    A[Open DrNotes] --> B{Notes directory set?}
    B -- Yes --> C[Load directory tree]
    B -- No --> D[Prompt user to choose directory]
    D --> C
    C --> E[Display file tree]
    E --> F[User selects a note]
    F --> G[Load into editor]
    G --> H[Render preview]
    H --> I{User edits?}
    I -- Yes --> J[Update preview live]
    J --> K[Auto-save after 5s idle]
    K --> I
    I -- No --> L[User selects another note]
    L --> F
```

### Sequence Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant E as Editor
    participant P as Preview
    participant FS as Filesystem

    U->>E: Type markdown text
    E->>P: content_changed signal (debounced 300ms)
    P->>P: Render markdown → HTML
    P->>P: Initialize mermaid diagrams

    U->>P: Click checkbox in preview
    P->>E: checkbox_toggled(index, checked)
    E->>E: Update source: [ ] ↔ [x]
    E->>FS: Auto-save (5s idle)

    U->>E: Ctrl+S
    E->>FS: Write file immediately
    FS-->>E: OK
```

### Class Diagram

```mermaid
classDiagram
    class MainWindow {
        -Settings settings
        -DirectoryTree tree
        -MarkdownEditor editor
        -PreviewPanel preview
        -FormattingToolbar toolbar
        +closeEvent()
    }
    class DirectoryTree {
        -QFileSystemModel model
        -QTreeView tree
        +set_root(path)
        +file_selected Signal
    }
    class MarkdownEditor {
        -EditorCore editor
        -FindReplaceBar find_bar
        +open_file(path)
        +save_current()
        +content_changed Signal
    }
    class PreviewPanel {
        -QWebEngineView view
        -Bridge bridge
        +update_content(markdown)
        +checkbox_toggled Signal
    }
    class FormattingToolbar {
        +wrap_requested Signal
        +line_prefix_requested Signal
        +block_requested Signal
    }

    MainWindow --> DirectoryTree
    MainWindow --> MarkdownEditor
    MainWindow --> PreviewPanel
    MainWindow --> FormattingToolbar
```

### Gantt Chart

```mermaid
gantt
    title DrNotes Development Timeline
    dateFormat  YYYY-MM-DD
    section Core
        Project setup           :done,    setup,  2026-01-06, 2d
        Settings & persistence  :done,    settings, after setup, 2d
        Directory tree widget   :done,    tree,   after settings, 3d
    section Editor
        Text editor with lines  :done,    editor, after tree, 4d
        Syntax highlighting     :done,    syntax, after editor, 2d
        List continuation       :done,    lists,  after syntax, 2d
        Find & replace          :done,    find,   after lists, 2d
    section Preview
        Markdown rendering      :done,    render, after tree, 3d
        Mermaid support         :done,    mermaid, after render, 3d
        Interactive checkboxes  :done,    checks, after mermaid, 2d
    section Future
        Full-text search        :         search, 2026-03-01, 5d
        PDF export              :         pdf,    after search, 4d
        Theming                 :         theme,  after pdf, 3d
```

### State Diagram

```mermaid
stateDiagram-v2
    [*] --> NoFileOpen

    NoFileOpen --> FileOpen: User selects file
    FileOpen --> Editing: User types

    state FileOpen {
        [*] --> Clean
        Clean --> Modified: Text changed
        Modified --> Clean: File saved
        Modified --> Modified: More edits
    }

    Editing --> FileOpen: Auto-save triggers
    FileOpen --> FileOpen: Switch to another file (auto-save first)
    FileOpen --> [*]: Close app (save & persist state)
```

### Entity Relationship Diagram

```mermaid
erDiagram
    NOTES_ROOT ||--o{ FOLDER : contains
    FOLDER ||--o{ FOLDER : "sub-folder"
    FOLDER ||--o{ NOTE : contains
    NOTE {
        string filename
        string content
        date modified
        string encoding
    }
    FOLDER {
        string name
        string path
    }
    NOTES_ROOT {
        string path
    }
```

### Pie Chart

```mermaid
pie title Lines of Code by Module
    "Editor" : 320
    "Preview" : 180
    "Directory Tree" : 140
    "Main Window" : 170
    "Toolbar" : 65
    "Settings" : 55
    "Syntax Highlighter" : 60
```

---

## Horizontal Rules

The three syntaxes all produce a rule:

---

***

___

---

## Unicode & Internationalization

DrNotes supports a wide range of Unicode characters:

### Accented & Latin Extended

- French: L'été est une saison magnifique. Ça va très bien, merci!
- German: Ärger mit Übungen — größte Straße in München
- Spanish: ¡Feliz año nuevo! ¿Cómo estás?
- Portuguese: Obrigação, coração, não,ações
- Polish: Zażółć gęślą jaźń
- Czech: Příliš žluťoučký kůň úpěl ďábelské ódy
- Turkish: Şehir içi ulaşımda değişiklik

### CJK Characters

- Chinese: 学而不思则罔，思而不学则殆。
- Japanese: 吾輩は猫である。名前はまだ無い。
- Korean: 모든 인간은 태어날 때부터 자유로우며

### Cyrillic & Greek

- Russian: Съешь ещё этих мягких французских булок, да выпей чаю.
- Ukrainian: Ґанок, їжак, єнот — ці слова мають цікаві літери.
- Greek: Ο καιρός είναι ωραίος σήμερα. Η φιλοσοφία αρχίζει με θαυμασμό.

### RTL Scripts

- Arabic: مرحباً بالعالم — هذا اختبار للنصوص العربية
- Hebrew: שלום עולם — זהו מבחן לטקסט בעברית

### Symbols & Emoji

- Arrows: ← → ↑ ↓ ↔ ⇒ ⇐ ⇔
- Math: ∀x ∈ ℝ: x² ≥ 0, ∑(i=1..n) = n(n+1)/2, √2 ≈ 1.414, ∞ × 0 ≠ 1
- Currency: $ € £ ¥ ₹ ₩ ₿ ₽
- Box drawing: ┌──┬──┐ │  │  │ └──┴──┘
- Music: ♩ ♪ ♫ ♬ 𝄞
- Misc: © ® ™ § ¶ † ‡ • ‰ ° ′ ″

### Mixed Script Table

| Language   | Greeting       | Thank you      |
|------------|----------------|----------------|
| English    | Hello          | Thank you      |
| French     | Bonjour        | Merci          |
| German     | Hallo          | Danke          |
| Japanese   | こんにちは     | ありがとう     |
| Korean     | 안녕하세요     | 감사합니다     |
| Russian    | Здравствуйте   | Спасибо        |
| Arabic     | مرحباً         | شكراً          |
| Hindi      | नमस्ते          | धन्यवाद        |
| Thai       | สวัสดี          | ขอบคุณ         |

---

## Miscellaneous

Here is a paragraph with a line break
created by trailing two spaces.

> **Tip:** Use `Ctrl+F` to open Find & Replace, and `Ctrl+S` to save.

That covers all the major markdown features supported by DrNotes!
