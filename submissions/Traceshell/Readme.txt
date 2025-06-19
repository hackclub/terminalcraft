🚀 TraceShell v2.0 – Advanced Activity Tracking & Productivity Analytics

TraceShell is a powerful, privacy-focused activity tracker that monitors your computer usage and gives smart insights to help you work better. It tracks apps, windows, URLs, and gives optional AI tips.

✨ Features: Application Monitoring – Track time spent in each app. Window Title Capture – See what files or tabs you used. URL Tracking – Automatically logs visited sites. Cross-Platform – Works on Windows, macOS, and Linux.

Detailed Analytics: Daily and weekly time reports. Breakdown of app usage. Find your most productive hours. Full session logs with time.

AI-Powered Insights (Optional): Get AI tips to improve your focus. Understand patterns in your habits. Receive smart productivity scores.

Privacy First: Everything is stored locally on your computer. No cloud or online sync. You decide how long to keep data. You can choose what it tracks and what it ignores.

Quick Start: Install dependencies with "pip install requests psutil". On Linux/macOS, make it executable with "chmod +x traceshell.py".

To start tracking: python traceshell.py start
To see activity: python traceshell.py show
To check status: python traceshell.py status
To stop tracking: python traceshell.py stop

Core Commands: start – begin tracking, stop – stop it, status – show if it's running, show – see your activity, cleanup – delete old data.

Time Options: show (today), show --period yesterday, show --period week, show --date YYYY-MM-DD (example: 2024-12-25).

Detailed Analysis: --detail "Google Chrome" shows browser time, --detail "VS Code" --period week shows weekly coding time, --detail "Microsoft Word" --date 2024-12-20 shows Word usage that day.

AI Insights: Set your OpenAI key with export OPENAI_API_KEY="your-api-key-here". Then use --ai flag like this: show --ai or show --period week --ai.

Filter Results: show --type app, show --type file, show --type url. You can also limit with --limit 20.

Example Output:
Today’s Tracked Time: 6h 42m
Top Apps:

Chrome – 2h 15m (github: 45m, stackoverflow: 32m, reddit: 28m)

VS Code – 1h 48m (main.py: 1h 2m, config.json: 26m, readme.md: 20m)

Slack – 45m (dev channel: 25m, DMs: 20m)

Detailed VS Code Stats:
main.py – 62m total across 6 sessions
config.json – 26m across 4 sessions

Configuration File Path: ~/.traceshell/
Files: config.json, trace.db, daemon.pid

Sample config.json:
tracking: apps true, interval 2, min_duration 5, detailed true
ai: enabled true
privacy: retention_days 30
performance: buffer_size 500, batch_size 10

Advanced Features:
Background Daemon – runs quietly.
Smart URL Tracking – grabs URLs from browsers.
Session Logs – see exact time blocks of work.
Cross-Platform: Win uses Win32, macOS uses AppleScript, Linux uses xprop/xdotool

AI Setup:

Get your API key at openai.com/api

Set it with export OPENAI_API_KEY="your-api-key-here"

Run: python traceshell.py show --ai

Troubleshooting:
Daemon won’t start? Check ~/.traceshell/ permissions.
No data? Check if daemon is running and use --limit 5 to test.
AI not working? Check your API key with echo $OPENAI_API_KEY.
Database issues? Use cleanup, or delete trace.db and restart.

Requirements:
Python 3.7+
Libraries: requests, psutil
Linux: needs xprop and xdotool
macOS: allow accessibility
Windows: no extras needed

Privacy:
YES tracked: app names, window titles, URLs, file paths
NOT tracked: file contents, keystrokes, screenshots, passwords
Everything stays on your computer unless you turn on AI features

Made for devs who wanna know where their time goes.
Start using TraceShell and learn how you really spend your hours 🧠⌛💻🔥