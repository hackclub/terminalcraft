🚀 TraceShell v2.0 – Advanced Activity Tracking & Productivity Analytics

TraceShell is a powerful, privacy-focused activity tracker that monitors your computer usage and provides intelligent insights to help you optimize your productivity. It tracks applications, window titles, URLs, and provides optional AI-powered recommendations.

✨ Features

📊 Comprehensive Tracking
– Application Monitoring – Track time spent in each application with detailed session logs
– Window Title Capture – Monitor specific files, documents, and browser tabs
– URL Tracking – Automatically extract and log visited websites from browsers
– Cross-Platform Support – Works seamlessly on Windows, macOS, and Linux

📈 Advanced Analytics
– Detailed Time Reports – Daily, weekly, and custom date range analysis
– Application Breakdowns – See exactly what files and URLs you accessed
– Productivity Patterns – Discover your most productive hours and focus areas
– Session Tracking – Complete activity logs with timestamps and durations

🤖 AI-Powered Insights (Optional)
– Smart Productivity Analysis – Get AI-driven insights about your work patterns
– Focus Recommendations – Receive personalized tips to improve concentration
– Pattern Recognition – Understand your productivity habits with intelligent analysis

🛡️ Privacy First Design
– Local Storage Only – Everything stored securely on your computer
– No Cloud Sync – Your data never leaves your machine (except optional AI analysis)
– Configurable Retention – You control how long data is kept
– Selective Tracking – Choose what to track and what to ignore

🚀 Quick Start

Prerequisites
pip install requests psutil
chmod +x traceshell.py
export OPENAI_API_KEY="your-api-key-here"

Basic Commands
python traceshell.py start
python traceshell.py show
python traceshell.py status
python traceshell.py stop

📋 Command Reference

Core Commands
start – Launch the background tracking daemon
stop – Stop the tracking daemon safely
status – Show daemon status and recent activity
show – Display comprehensive activity reports
cleanup – Remove old data based on retention policy

Time Period Options
--period today – Today's activities (default)
--period yesterday – Yesterday's complete report
--period week – Past 7 days analysis
--date YYYY-MM-DD – Specific date report

Advanced Analysis
--detail APP_NAME – Deep dive into specific app usage
--type app/file/url – Filter by activity type
--ai – Include AI-powered insights
--limit N – Limit results to N items

💡 Usage Examples

Start tracking
python traceshell.py start

View today’s summary
python traceshell.py show

Get weekly report with AI
python traceshell.py show --period week --ai

Deep dive into Chrome
python traceshell.py --detail "Google Chrome"

Weekly VS Code usage
python traceshell.py --detail "VS Code" --period week

Specific date for Word
python traceshell.py --detail "Microsoft Word" --date 2024-12-20

Just app usage
python traceshell.py show --type app

Top 10 from yesterday
python traceshell.py show --period yesterday --limit 10

Specific date + AI
python traceshell.py show --date 2024-12-25 --ai

📊 Sample Output

Today's Activity Report
Total tracked time: 6h 42m
Applications used: 8

Google Chrome - 2h 15m

github.com/user/project (45m)

stackoverflow.com (32m)

reddit.com/r/programming (28m)

VS Code - 1h 48m

main.py (1h 2m)

config.json (26m)

readme.md (20m)

Slack - 45m

development channel (25m)

direct messages (20m)

⚙️ Configuration

File Locations
Config: ~/.traceshell/config.json
Database: ~/.traceshell/trace.db
PID File: ~/.traceshell/daemon.pid

Sample Config
"tracking": { "apps": true, "interval": 2, "min_duration": 5, "detailed": true }
"ai": { "enabled": true }
"privacy": { "retention_days": 30 }
"performance": { "buffer_size": 500, "batch_size": 10 }

🤖 AI Setup

Get your OpenAI API key
Set it like this:
export OPENAI_API_KEY="your-api-key-here"

Run with AI
python traceshell.py show --ai

🔧 System Requirements

Python 3.7+
Dependencies: requests, psutil

Linux – needs xprop and xdotool
macOS – needs accessibility permissions
Windows – no extra requirements

Platform Details
Windows – uses Win32 API
macOS – uses AppleScript
Linux – uses xprop and xdotool

🛠️ Troubleshooting

Daemon won’t start?
ls -la ~/.traceshell/
chmod 755 ~/.traceshell/
ps aux | grep traceshell

No data showing?
python traceshell.py status
python traceshell.py show --limit 5

AI not working?
echo $OPENAI_API_KEY
python traceshell.py show --ai

Reset DB
python traceshell.py cleanup
rm ~/.traceshell/trace.db
python traceshell.py start

🛡️ Privacy & Security

What is tracked:

Application names

Window titles

URLs

File paths

Timestamps

What is NOT tracked:

File contents

Keystrokes

Screenshots

Passwords

Network traffic

Data stays local in ~/.traceshell/
No cloud sync
You can delete it anytime

🎯 Use Cases

For Developers
– Track coding sessions
– Analyze work patterns
– Understand switching between tools

For Students
– Track study time
– Analyze habits
– Get AI-powered study tips

For Freelancers
– Track client work
– Log project activity
– Get insights for better time use

🔄 Version History

v2.0 – Major Update
– Better tracking + insights
– Detailed breakdowns
– AI integration
– Beautiful output
– Cross-platform improvements

v1.0 – First Release
– Basic app tracking
– Time reports
– Cross-platform daemon

Made for people who want to actually see where their time goes.
Use TraceShell and get smarter with your time. 🧠⌛💻