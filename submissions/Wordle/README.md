# Wordle Game

A terminal-based Wordle game where you guess a 5-letter word in 6 attempts, with feedback on each guess showing whether your letters are in the correct position (green), present but in the wrong position (yellow), or not in the word at all (dim).

## Features

- Play the classic Wordle game in the terminal.
- Get color-coded feedback for each guess (Green for correct position, Yellow for correct letter but wrong position, Dim for incorrect letter).
- Fetches a list of 5-letter words dynamically from an online source.
- Includes a feedback guide to help you understand how your guesses are evaluated.
  
## Requirements

- Python 3.x
- `requests` library (to fetch the word list from the web)
- `rich` library (for stylish terminal output)

## Installation

1. Make sure you have Python 3.x installed on your system.
2. Install the required libraries by running:
    ```bash
    pip install requests rich
    ```

## How to Play

1. Clone or download the repository:
    ```bash
    git clone https://github.com/Abeer6171/wordle-game.git
    ```
2. Navigate to the project directory:
    ```bash
    cd wordle-game
    ```
3. Run the game:
    ```bash
    python wordle_game.py
    ```

4. Enter a 5-letter word when prompted. The game will give you feedback for each guess:
    - **Green**: Correct letter in the correct position.
    - **Yellow**: Correct letter in the wrong position.
    - **Dim**: Incorrect letter.

You have **6 attempts** to guess the correct word. Good luck!
