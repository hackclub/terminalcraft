# Vim Escape Challenge

A terminal-based educational game that helps you learn Vim commands while trying to "escape" from Vim. Navigate through 5 challenging levels to master Vim basics and advanced features.

## Features

- 5 progressive levels teaching Vim commands
- Interactive terminal interface using curses
- Covers essential Vim skills:
  - Basic movement (hjkl, w, b, e)
  - Text manipulation (d, c, y, p)
  - Search and navigation
  - Marks and registers
  - Macros
- Freeplay mode after completing all levels
- Status bar showing current mode and progress
- Hidden clues to discover

## Requirements

```sh
python 3.x
curses (included with Python on Unix/Linux/macOS)
```

For Windows users: Install windows-curses:
```sh
pip install windows-curses
```

## Installation

1. Clone this repository or download `vimgamething.py`
2. Ensure your terminal window is at least 60x15 characters

## Usage

Run the game:
```sh
python vimgamething.py
```

### Game Modes

- **Normal Mode**: Default mode for navigation and commands
- **Insert Mode**: Enter text (i)
- **Visual Mode**: Select text (v)
- **Command Mode**: Execute commands (:)

### Basic Commands

- `h/j/k/l`: Move cursor left/down/up/right
- `i`: Enter insert mode
- `v`: Enter visual mode
- `:`: Enter command mode
- `/`: Search for text
- `:q` or `:quit`: Exit the game

### Level Progression

1. **Level 1**: Basic movement and searching
2. **Level 2**: Text manipulation
3. **Level 3**: Advanced navigation
4. **Level 4**: Macros and registers
5. **Level 5**: Final challenge

Complete each level by finding 3 hidden clues and using `:next` to proceed.

### Freeplay Mode

After completing all levels, unlock Freeplay mode to practice Vim commands freely:
- `:freeplay`: Enter Freeplay mode
- `:reset`: Reset the practice buffer
- `:challenge`: Return to challenge mode

### AI Usage
- Generating README.MD
- Writing the text for clues
- Clue unlock message