# Python Minesweeper Game

A terminal-based Minesweeper game implemented in Python using the curses library. This classic puzzle game challenges players to clear a board containing hidden mines without detonating any of them.

## Features

- Three difficulty levels:
  - Beginner (9x9 grid with 10 mines)
  - Intermediate (16x16 grid with 40 mines)
  - Expert (22x22 grid with 99 mines)
- Grid-based interface with borders and coordinates
- WASD controls for movement
- First click is always safe
- Flag system to mark potential mines
- Auto-reveal for empty cells
- High visibility with Unicode characters
- Game state persistence

## Controls

- `W` - Move cursor up
- `A` - Move cursor left
- `S` - Move cursor down
- `D` - Move cursor right
- `Space` - Reveal cell
- `F` - Toggle flag on cell
- `Q` - Quit game


## Installation

1. Clone the repository or download the `mine.py` file
2. Install required packages (Windows only):
   ```bash
   pip install windows-curses  # Windows only
   ```

## How to Play

1. Run the game:
   ```bash
   python mine.py
   ```

2. Select difficulty level (1-3)
3. Use WASD keys to move the cursor
4. Press Space to reveal a cell
5. Press F to place/remove a flag
6. Clear all non-mine cells to win!

## Game Rules

1. The board contains hidden mines
2. Numbers reveal how many mines are adjacent to a cell
3. Use flags to mark suspected mines
4. Reveal all non-mine cells to win
5. Revealing a mine ends the game
