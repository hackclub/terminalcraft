# Python Typing Speed Test

A terminal-based typing speed test application implemented in Python using curses. Test and improve your typing speed with different difficulty levels and track your progress.

## Features

- Three difficulty levels:
  - Easy: Simple sentences with 60-second time limit
  - Medium: Complex sentences with 45-second time limit
  - Hard: Challenging sentences with 30-second time limit
- Real-time feedback with color-coded typing
- Sound effects for typing feedback (optional)
- High score tracking
- WPM (Words Per Minute) calculation
- Accuracy percentage
- Performance ratings
- Persistent high scores

## Controls

- Type the displayed sentence
- `Enter` - Complete test early
- `Backspace` - Correct mistakes
- `Esc` - Quit current test
- Number keys (1-6) for menu navigation

## Requirements

- Python 3.6+
- curses library (included with Python on Unix systems)
- Windows users need to install windows-curses:
  ```bash
  pip install windows-curses
  ```

## Installation

1. Clone the repository or download the `type.py` file
2. Install required packages (Windows only):
   ```bash
   pip install windows-curses  # Windows only
   ```

## How to Play

1. Run the program:
   ```bash
   python type.py
   ```

2. From the main menu, you can:
   - Start Typing Test (1)
   - Select Difficulty (2)
   - View Instructions (3)
   - Toggle Sound (4)
   - View High Scores (5)
   - Quit (6)

## Scoring System

- **WPM (Words Per Minute)**: Calculated as (characters typed / 5) / minutes
- **Accuracy**: Percentage of correctly typed characters
- **Performance Ratings**:
  - Excellent: 60+ WPM with 95%+ accuracy
  - Great: 40+ WPM with 90%+ accuracy
  - Good: 20+ WPM with 80%+ accuracy

## Game Interface

