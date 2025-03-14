# Termigit

Termigit is a terminal-based Git client built with Python and Textual, providing a user-friendly TUI (Text User Interface) for managing Git repositories.


## Features

- Browse and select local Git repositories
- View commit history
- Examine commit details and diffs
- View file blame information
- Switch between branches
- Navigate repository file structure
- Responsive terminal UI with keyboard navigation

## Requirements

- Python 3.7+
- Dependencies listed in requirements.txt:
  - textual >= 0.27.0
  - gitpython >= 3.1.30

## Installation

### Method 1: Install from source

1. Clone this repository:
```
git clone https://github.com/PawiX25/Termigit.git
cd Termigit
```

2. Install the package globally:
```
pip install -e .
```

### Method 2: Direct installation

```
pip install git+https://github.com/PawiX25/Termigit.git
```

## Usage

After installation, you can run Termigit from anywhere:

```
termigit
```

### Keyboard Navigation

| Key | Action | Description |
|-----|--------|-------------|
| `q` | Quit | Exit the application |
| `r` | Refresh | Refresh current view |
| `1` | History View | Switch to history view |
| `2` | Diff View | Switch to diff view |
| `3` | Blame View | Switch to blame view |
| `c` | Focus Commits | Focus on commit list |
| `d` | Focus Diff | Focus on diff view |
| `b` | Focus Branches | Focus on branch list |
| `f` | Focus Files | Focus on file tree |
| `g` | Focus Blame | Focus on blame view |
| `s` | Switch Branch | Switch to selected branch |

## Workflow

1. Navigate the repository tree to select a Git repository
2. Browse commits, files, and branches
3. Select commits to view diffs
4. Select files to view blame information
5. Use keyboard shortcuts to navigate between different views
