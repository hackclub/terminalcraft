# THIS PROJECT LIVES AT https://github.com/spjoes/notes-cli AND MADE FOR TERMINAL-CRAFT

# 📝 Contextual Notes CLI (`notes`)

A terminal-based contextual note-taking app that links your thoughts directly to the files and projects you're working on. Easily add, view, and manage notes scoped to your current directory, specific files, or even line numbers - all from the command line.

---

## 🚀 Features

- 🧠 **Context-aware** notes scoped to the current directory or a specific file
- 🏷️ **Tag your notes** for easy categorization and searching
- 📄 **Link notes to files and line numbers**
- 📋 **List** and **filter** notes by file or tag
- ❌ **Delete notes** by ID or tag, with confirmation
- 📦 Fully **self-contained**, no external tools required
- 💻 Cross-platform: macOS, Linux, and Windows

---

## ✨ Quick Start

### 1. Clone the Repo

```bash
git clone https://github.com/spjoes/notes-cli.git
cd notes-cli
```

### 2. Build

#### ✅ Unix/macOS:
```bash
go build -o notes
```
#### ✅ Windows (CMD):
```bash
go build -o notes.exe
```

### 3. Use it!
```bash
notes add "Fix rendering issue"
notes list
notes delete a1b2c3d4
notes list
```

---

## 📚 Commands
### Add a Note
```bash
note add "Your message here" [--file path/to/file] [--line 42] [--tags tag1,tag2]
```

### List Notes
```bash
note list [--file filename] [--tag tag]
```

### Delete Note
```bash
note delete <note-id> [--yes]
note delete --tag <tag> [--yes]
```

---

## 📂 Note Storage Format
All notes are stored in a local .notes/notes.json file within your project directory.
Example entry:

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-1234567890ef",
  "message": "Fix layout bug",
  "file": "components/Header.tsx",
  "line": 88,
  "created_at": "2025-05-29T12:00:00Z",
  "tags": ["bug", "frontend"]
}
```

---

## 💡 Use Cases
- Track TODOs or bugs directly within your project

- Leave file-specific breadcrumbs during debugging

- Keep code review notes linked to file/line context

- Jot down ideas as you explore a repo

---

## 🔧 Development
Built with:
- [Go](https://golang.org/)
- [Cobra](https://github.com/spf13/cobra)

---

## 🌍 Contributing
Pull requests welcome! If you have suggestions, features, or bug reports, please open an issue.