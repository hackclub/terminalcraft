# Terminal Games

This is a terminal-based collection of two classic games implemented in Python using the curses library. The collection includes a Typing Speed Test and Minesweeper, each with multiple difficulty levels and interactive gameplay.

## Features

### Typing Speed Test
- **Difficulty Levels**: Easy, Medium, Hard
- **Real-time Feedback**: Color-coded typing feedback
- **Sound Effects**: Optional sound feedback for typing
- **High Score Tracking**: Persistent storage of best scores
- **Performance Metrics**: Words Per Minute (WPM) and accuracy calculation
- **User Interface**: Interactive menu system

### Minesweeper
- **Difficulty Levels**: Beginner, Intermediate, Expert
- **Grid-based Gameplay**: Navigate using WASD keys
- **Flag System**: Mark suspected mines
- **Auto-reveal**: Automatically reveal empty cells
- **User Interface**: Clear grid layout with borders

## Controls

### Typing Speed Test
- Type the displayed sentence
- `Enter` - Complete test early
- `Backspace` - Correct mistakes
- `Esc` - Quit current test
- Number keys (1-6) for menu navigation

### Minesweeper
- `W` - Move cursor up
- `A` - Move cursor left
- `S` - Move cursor down
- `D` - Move cursor right
- `Space` - Reveal cell
- `F` - Toggle flag on cell
- `Q` - Quit game


## Installation

1. Clone the repository or download the `games.py` file.
2. Install required packages:
   ```bash
   pip install curses  # Windows only
   ```

## How to Play

1. Run the program:
   ```bash
   python games.py
   ```

2. From the main menu, select a game to play:
   - Typing Speed Test (1)
   - Minesweeper (2)
   - Quit (3)

3. Follow the on-screen instructions for each game.

## Game Interface

### Typing Speed Test
- Displays a sentence to type
- Shows real-time typing feedback
- Calculates and displays WPM and accuracy

### Minesweeper
- Displays a grid with hidden mines
- Use flags to mark potential mines
- Clear all non-mine cells to win

## Tips for Better Scores

- **Typing Speed Test**: Focus on accuracy first, then speed. Practice regularly.
- **Minesweeper**: Use flags wisely and start with corners or edges.
