# TermiCards

A simple terminal-based flashcard application to help you study.

## Features

* Create and manage decks of flashcards.
* Add cards with front (question/term) and back (answer/definition).
* Study decks using different modes:
    * Standard flipping
    * Spaced Repetition
    * Quiz Mode
* Import and export decks from/to CSV files.
* Search for cards across all decks.

## Requirements

* Python 3.x
* `curses` library (standard on Linux/macOS)
* `windows-curses` library (if on Windows): `pip install windows-curses`

## How to Run

1.  **Install dependencies:**
    *   If you are on Windows and don't have `windows-curses` installed, open your terminal and run:
        ```shell
        pip install windows-curses
        ```
2.  **Run the application:**
    Open your terminal in the project directory and run:
    ```shell
    python quiz.py
    ```

## Usage

Navigate the application using the arrow keys and Enter. Press 'q' or Esc to exit menus or the application.
