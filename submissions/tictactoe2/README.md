# Tic Tac Toe 2

Tic Tac Toe 2 is a twist on the classic Tic Tac Toe game, with a mini tictactoe board inside each square of a larger tictactoe board.

## About:
  - The game has a "big board" made up of 9 mini boards (each a 3x3 grid) where winning a mini board claims that square on the big board.
  - Classic tictactoe rules apply for each mini board and the overall big board.
  - Each move in a mini board sends your opponent to the corresponding mini board.
  - Win three in a row on the big board to win.
  - You can play 2 player or against a computer

## Installation Instructions:
  1. Clone the repository:
       ```sh
       git clone https://github.com/Bai756/tictactoe2.git
       ```
  2. Navigate to the project directory:
       ```sh
       cd tictactoe2
       ```
  3. If you are on windows, make a venv and install windows-curses:
       ```sh
       pip install windows-curses
       ```

## How to Play:
  1. Start the game:
       ```sh
       python3 main.py
       ```
  2. Follow the on-screen instructions to play the game. Use the arrow keys to move and enter to select.
