# StandLog -command line journal

A beautiful, developer-centric terminal journal and standup logger.  
**Cross-platform:** Works on Linux, macOS, and Windows.

---

## ✨ Features

- 📝 **Daily Standup Logging**: Log what you did, what you'll do, blockers, and tags.
- 📊 **Weekly Stats & Streaks**: Visualize your progress and blockers.
- 🔥 **Activity Heatmap**: See your logging streaks and activity by month.
- 📤 **Export**: Save your logs as Markdown or JSON.
- ⏰ **Reminders**: Get context-aware reminders (calendar, git, uptime) if you forget to log.
- 💬 **Feedback**: Leave and view feedback/encouragement on entries.
- 🔒 **Encryption**: Secure your logs with a passphrase.
- 🏅 **Badges**: Earn achievements for feedback, streaks, and more.
- 💻 **Cross-platform**: No reliance on pre-installed tools; all features work on Windows, macOS, and Linux.

---

## 📸 Screenshots / video Demos

- ![Main Menu](https://github.com/rakesh-uwu/standlog/blob/main/asset/home.png)

### video link: https://youtu.be/8AKgYASbgck

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/standlog.git
cd standlog
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

## For linux/mac os
```bash
python3 main.py
```
## For windows
```bash
python main.py
```
---

## 🛠️ Tools & Libraries Used

- [Rich](https://github.com/Textualize/rich) — Beautiful terminal formatting and widgets
- [Cryptography](https://cryptography.io/) — Secure encryption for your logs
- [Yagmail](https://github.com/kootenpv/yagmail) — Email integration (optional)
- [SoundDevice](https://python-sounddevice.readthedocs.io/) — Voice notes (optional)
- [Scipy](https://scipy.org/) — Audio processing (optional)
- [ICS](https://github.com/C4ptainCrunch/ics.py) — Calendar integration (optional)

All dependencies are listed in `requirements.txt`. No system tools are required for core features.  
Optional features (like git/uptime reminders) are only shown if available.

---

## 🖥️ Platform Support

- **Linux, macOS, Windows** — All features work cross-platform.
- No reliance on pre-installed system tools.  
- If a feature (like git or uptime) is not available, it is skipped gracefully.

---

## 📚 Features & How to Use

### Main Menu

- **Show weekly stats**: View your last 7 logs and most common blockers.
- **Export as Markdown/JSON**: Save your logs for backup or sharing.
- **Reminder**: Get a context-aware nudge if you forget to log.
- **Leave/View feedback**: Add or read encouragement on any entry.
- **Enable/Disable encryption**: Secure your logs with a passphrase.
- **Visualize journal (heatmap)**: See your activity and streaks.
- **ASCII Animation & Quote**: Enjoy a random ASCII animation and motivational quote.
- **Back**: Return to the previous menu or exit.

### Logging a Standup

1. Run the app.
2. Enter your daily standup details when prompted.
3. Use the viewer menu to explore stats, export, or view feedback.

### Encryption

- Enable encryption to protect your logs with a passphrase.
- Disable encryption to store logs in plain text.

### Feedback & Badges

- Leave feedback on any entry.
- Earn badges for activity, streaks, and feedback.

---

## 📝 Contributing

Pull requests and suggestions are welcome!

---

## 📦 Project Structure

- `main.py`: Main entry point and splash/menu UI
- `ui/viewer.py`: Viewer menu, stats, export, reminders, feedback, heatmap, animation
- `requirements.txt`: All dependencies
- `data/entries/`: Log storage (created automatically)

---


