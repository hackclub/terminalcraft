# Git-Glance
> A simple yet powerful CLI tool to glance over multiple repositories
```
    ██████╗ ██╗████████╗      ██████╗ ██╗      █████╗ ███╗   ██╗ ██████╗███████╗
    ██╔════╝ ██║╚══██╔══╝     ██╔════╝ ██║     ██╔══██╗████╗  ██║██╔════╝██╔════╝
    ██║  ███╗██║   ██║  █████╗██║  ███╗██║     ███████║██╔██╗ ██║██║     █████╗  
    ██║   ██║██║   ██║  ╚════╝██║   ██║██║     ██╔══██║██║╚██╗██║██║     ██╔══╝  
    ╚██████╔╝██║   ██║        ╚██████╔╝███████╗██║  ██║██║ ╚████║╚██████╗███████╗
    ╚═════╝ ╚═╝   ╚═╝         ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝
```
## Features
- Quickly see the status of multiple repositories
- Track/untrack repositories by path and alias
- See fetch/pull/push info, latest commit, author, and more
- Beautiful Rich + Tree UI Layout
- Simple CLI with Typer and Rich

## Requirements
- Python `>=3.7`
> [!IMPORTANT]
> **Git installed and available in `PATH`**

## Getting Started
### 1. Clone the Repository
```bash
git clone https://github.com/harsh-thota/Git-Glance.git
cd ~/path/to/git-glance
```
### 2. Create and Activate a Virtual Environment
#### Windows:
```bash
python -m venv .venv
.venv\Scripts\Activate
```
#### macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the Project in Editable Mode
```bash
pip install -e .
```

### 4. Verify it Works
Once installed, try running:
```bash
git-glance list
```
> If you see an error like "command not found", make sure your virtual environment is still activated and `~/.local/bin` (on macOS/Linyx) is in your `PATH`

You can check where `git-glance` CLI is installed ***I think***
```bash
which git-glance # Linux/macOS
where git-glance # Windows CMD/Powershell
```

## Usage
#### List Tracked Repositories
Shows a table of all Git Repositories currently being tracked
```bash
git-glance list
```
#### Add a New Repository
Adds a Git Repository to the tracking list
```bash
git-glance add <path-to-repo> <alias>
# Example: git-glance add ~/projects/my-cool-repo cool-repo
```
#### Remove a Repository
Removes a repo from the tracking list
```bash
git-glance remove --path <path>
# or
git-glance remove --alias <alias>
```
#### Fetch Remote Updates
Performs a `git-fetch` on all tracked repositories to check for upstream changes
```bash
git-glance fetch
```
#### Check Status of All Tracked Repositories
Displays a rich, color-coded summary table for all repos -- including branch, uncommitted changes, push/pull status, etc
```bash
git-glance status
```
#### Detailed View for a Single Repository
Shows detailed info for one repo inlcuding:
- Commit Hash and message
- Author and date
- Remote info
- Uncommitted/unpushed changes
- Whether its up-to-date with the remote
```bash
git-glance status --only <alias>
# Example: git-glance status --only cool-repo
```
### Help
Get list of all commands available to use
```bash
git-glance --help
```
Get help with a specific command
```bash
git-glance <command> --help
```