# Git-Glance
> A simple yet powerful CLI tool to glance over multiple Repositories
```
    ██████╗ ██╗████████╗      ██████╗ ██╗      █████╗ ███╗   ██╗ ██████╗███████╗
    ██╔════╝ ██║╚══██╔══╝     ██╔════╝ ██║     ██╔══██╗████╗  ██║██╔════╝██╔════╝
    ██║  ███╗██║   ██║  █████╗██║  ███╗██║     ███████║██╔██╗ ██║██║     █████╗  
    ██║   ██║██║   ██║  ╚════╝██║   ██║██║     ██╔══██║██║╚██╗██║██║     ██╔══╝  
    ╚██████╔╝██║   ██║        ╚██████╔╝███████╗██║  ██║██║ ╚████║╚██████╗███████╗
    ╚═════╝ ╚═╝   ╚═╝         ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝
```
## Features
- Quickly see the status of multiple Repositories
- Track/untrack Repositories by path and alias
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
#### Scan a Directory to Add a Repository
Recursively scans a directory for Git Repositories and adds them to be tracked
```bash
git-glance scan <a-directory>
```
#### Remove a Repository
Removes a Repository from the tracking list
```bash
git-glance remove --path <path>
# or
git-glance remove --alias <alias>
```
#### Fetch Remote Updates
Performs a `git-fetch` on all tracked Repositories to check for upstream changes
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
#### Remove Invalid or Deleted Git Repositories from the Tracking List
Goes through the tracking list for paths that don't exist or paths that are not Git Repositories
```bash
git-glance clean
```
#### Manage Git Config File
Reset or ask to show the git config file in a rich format
```bash
git-glance --reset True
# or
git-glance --show True
```
#### Rename Aliases
Rename the alias of a tracked Repository
```bash
git-glance <old-alias> <new-alias>
```
#### Open a Repository
Opens a tracked Repository in the system file manager
```bash
git-glance <alias>
```
#### Commit Summary
Show latest N commits for tracked Repositories or a single Repository (default N = 5)
```bash
git-glance commit-summary
# or
git-glance commit-summary --alias <alias>
# or 
git-glance commit-summary --alias <alias> --count <N-value>
```
#### Difference
Show uncommitted changes (diff) for one or all tracked Repositories
```bash
git-glance diff
# or
git-glance diff <alias>
```
#### Get Stale Repositories
Shows Repositories with no commits in the last N days (default N = 10)
```bash
git-glance stale
# or
git-glance --days <N-value>
```
#### Pull from Remote
Pull latest changes from remote for all or specific Repository
```bash
git-glance pull
# or
git-glance pull --only <alias>
```
#### Push to Remote
Push local commits to remote for all or specific Repository
```bash
git-glance push
# or
git-glance push --only <alias>
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