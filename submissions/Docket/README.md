# 📦 Docket - A TUI for Managing Docker Containers & Images

Docket is a terminal-based user interface (TUI) for managing Docker containers and images using a simple, keyboard-driven approach. It leverages `tview` and `tcell` to provide an interactive and intuitive experience for Docker users.

## ✨ Features

- View running containers and available images in a structured table format
- Start, stop, delete, and rename containers easily
- Create new containers from images
- Keyboard shortcuts for quick actions
- Responsive and color-coded UI

## 🛠 Installation

### If you are not on Windows or arch linux:

Ensure you have Go and Docker installed. Then, clone the repo and build it:

```sh
git clone https://github.com/yourusername/docket.git
cd docket
go build -o docket
```

Run the application:

```sh
./docket
```

### If you are on arch linux

```sh
yay -S docket
```

> If you are on windows, download the installer from the releases section and install it.

## ⌨️ Keyboard Shortcuts

| Key        | Action                               |
| ---------- | ------------------------------------ |
| `d`        | Delete selected container/image      |
| `r`        | Run a container                      |
| `s`        | Stop a container                     |
| `e`        | Edit container name                  |
| `c`        | Create container from selected image |
| `Ctrl + →` | Switch to Images tab                 |
| `Ctrl + ←` | Switch to Containers tab             |

## 📜 Usage

Once you launch Docket, you'll see two tabs:

1. **Containers Tab** – Lists running containers and allows starting, stopping, deleting, or renaming them.
2. **Images Tab** – Shows available images and lets you create new containers from them.

Navigate with arrow keys and press the assigned shortcut to perform an action.

## 🏗 Dependencies

- `tview`
- `tcell`
- Docker (CLI must be accessible)

## 💡 Contributing

Feel free to open issues or PRs to improve Docket! 🎉
