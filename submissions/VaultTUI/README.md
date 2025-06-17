# 🔐 VaultTUI

A secure, offline password and secrets vault with both **Command Line Interface (CLI)** and **Text User Interface (TUI)** built in Python. Easily store, search, view, and delete credentials — all encrypted with a master password.

---

## ✨ Features

- 🧪 AES256 Encryption using `cryptography.fernet`
- 🧠 Master password-based access
- 🖥️ Interactive TUI built with `textual`
- 🧾 CLI for quick access and scripting
- 🔍 Fuzzy search functionality
- 📝 Add, View, Delete entries
- 👁️ Masked password input & output toggle
- ⌨️ Keyboard Shortcuts in TUI
- 💾 Backup/Restore support (WIP)

---

## 🗂 Directory Structure

```

VaultTUI/
├── main.py              # Launches the TUI
├── cli.py               # Handles CLI commands
├── vault.py             # Vault data operations
├── utils.py             # Encryption, validation, helpers
├── tui.css              # Textual UI styling
├── requirements.txt
└── README.md

````

---

## 🚀 Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
````

### 2. Run TUI

```bash
python main.py
```

### 3. Run CLI

```bash
python cli.py add github --username myuser --password mypass
python cli.py view github
python cli.py delete github
python cli.py search git
```

---

## 🔐 Master Password

The master password is used to generate the encryption key. It must be **memorized** — if you forget it, your vault can't be decrypted!

> ⚠️ Never share your master password. Keep backups of your vault file separately and securely.

---

## ⌨️ TUI Keyboard Shortcuts

| Key     | Action                |
| ------- | --------------------- |
| `ESC`   | Exit the app          |
| `/`     | Open search form      |
| `Enter` | Submit form actions   |
| `Home`  | Return to home screen |

---

## 🔒 Security Notes

* All entries are encrypted using **Fernet symmetric encryption (AES 128 CBC + HMAC)**.
* The vault is stored locally as an encrypted `.vault` file.
* No internet access is required — fully offline by design.

---
## 📜 License

MIT License. Feel free to fork, improve, and use it for personal or educational purposes.

---

## 🧠 Author

Made by **Devaansh Pathak** as a Python + TUI learning project.
Inspired by privacy-first tools and minimalist interfaces.

---
