# Git Helper CLI

AI generated README

A simple CLI app to help you with common git tasks.

**Note:** Repository URLs for cloning and setting origin are validated to ensure they are from GitHub, GitLab, or Bitbucket.

## Installation

```bash
sudo npm install -g git-helper-crabbys@1.0.0
#or
npm install -g git-helper-crabbys@1.0.0

```

## Usage

### Interactive Mode

Run the command without any arguments to launch the interactive menu:

```bash
git-helper
```

Follow the prompts to create, clone, push, or sync repositories easily.

### Direct Commands (Flags)

You can also use flags for a faster, non-interactive workflow.

```bash
# Show help
git-helper --help

# Initialize a repo in the current directory
git-helper init

# Clone a repository
git-helper clone https://github.com/user/repo.git

# Stage files, commit, and push
git-helper push -m "Your commit message"

# Sync with remote (pull, commit all, push)
git-helper sync

# Commit staged changes
git-helper commit -m "Your commit message"

# View diff of working directory
git-helper diff

# View diff of staged changes
git-helper diff --staged

# Manage branches (interactive)
git-helper branch

# Rebase current branch onto another branch (e.g., main)
git-helper rebase main

# Set the remote origin URL
git-helper origin https://github.com/user/repo.git

# Create a standard .gitignore file
git-helper gitignore

# Configure your credentials
git-helper config --username <your-user> --token <your-pat>
```
Your Personal Access Token is stored securely in your system's native keyring.
