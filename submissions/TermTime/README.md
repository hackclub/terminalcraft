# ⏳ Terminal Productivity Tracker

A lightweight and cross-platform terminal application that helps you manage tasks and stay focused using the Pomodoro technique.

---

## 🚀 Features

- ✅ Add, delete, and view tasks
- ⏱️ Start Pomodoro sessions with a visual timer and progress bar
- 📊 View detailed session statistics (total time and time per task)
- 📝 Logs sessions automatically
- 💻 Fully compatible with Windows, macOS, and Linux
- 🔒 Self-contained — no reliance on pre-installed tools

---

## 📚 How It Works

1. You create tasks from the terminal interface.
2. Start a Pomodoro session (25 minutes of focus followed by a 5-minute break) for any task.
3. A visual timer with a progress bar runs in the terminal.
4. Each session is logged to `log.txt` for tracking productivity.
5. Use the stats option to review your focus time and per-task breakdown.

---

## 🧰 Requirements

- Python 3.7 or higher
- Works on:
  - Windows (CMD, PowerShell)
  - macOS (Terminal)
  - Linux (any terminal)

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/nonop-on-github/TermTime.git
cd TermTime
````

### 2. Run the app

```bash
python main.py
```

> If you’re on a system where `python` runs version 2.x, use:

```bash
python3 main.py
```

---

## 📦 Files

| File         | Description                          |
| ------------ | ------------------------------------ |
| `main.py`    | Main application                     |
| `tasks.txt`  | Auto-created file storing your tasks |
| `log.txt`    | Log file storing Pomodoro history    |

---

## 🔍 Tips

* For testing, activate `DEBUG = True` in the code to shorten the Pomodoro duration.
* Your progress is stored in simple `.txt` files — perfect for syncing or backup.

---

## 🌍 Contributing

Pull requests are welcome! You can:

* Add break timer after each session
* Enhance the UI with ASCII art
* Create a session summary export
* Add config file support

Fork the project, make changes, and submit a pull request 🤝

---

## 🪪 License

This project is licensed under the MIT License
