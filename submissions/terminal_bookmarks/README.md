# Terminal Bookmarks

A command-line tool that helps you save, organize, and quickly access your most-used terminal commands. Never forget complex commands or waste time typing them again!

## Screenshots
![tb](./readme_assets/1.png)
![tb list](./readme_assets/2.png)

## Demo Video
<a href="https://hc-cdn.hel1.your-objectstorage.com/s/v3/2273d03b26d5f8268afdf974ee56ed1a898caa32_demo.mp4">
  <img src="./readme_assets/demo_thumbnail.png" alt="Demo Video" width="400"/>
</a>

## Features

- Save commands with descriptions and tags
- Quick search and filtering
- Organize with tags
- Execute saved commands easily
- Works on Windows, macOS, and Linux

## Quick Start

```bash
# Clone and install
git clone https://github.com/hackclub/terminalcraft.git
cd terminalcraft/submissions/terminal-bookmarks

# Set up virtual environment
# Windows:
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# Install package
pip install -e .
```

## Basic Usage

```bash
# View the home page
tb

## Help commands
tb --help

# Add a bookmark
tb add -t "Git Status" -c "git status" --tags git,status

# List bookmarks
tb list

# Run a bookmark
tb run "Git Status"

# Search bookmarks
tb search git
```

## Command Reference

### Adding Bookmarks
```bash
# Basic bookmark
tb add -t "Title" -c "command"

# With description and tags
tb add -t "Git Push" -c "git push origin main" \
       -d "Push to main branch" --tags git,workflow
```

### Listing Bookmarks
```bash
# List all
tb list

# Detailed view
tb list --detailed

# Filter by tag
tb list --tag git
```

### Running Bookmarks
```bash
# By title
tb run "Git Status"

# By ID
tb run abc123
```

### Managing Bookmarks
```bash
# Edit a bookmark
tb edit <id> -t "New Title"

# Delete a bookmark
tb delete <id>
```

## Configuration

Bookmarks are stored in:
- Windows: `%APPDATA%\terminal-bookmarks`
- macOS: `~/Library/Application Support/terminal-bookmarks`
- Linux: `~/.config/terminal-bookmarks`

## Supported Platforms
- Windows
- macOS
- Linux 

## Global Options
- `--help`: Show help message
- `--version`: Show version information 
