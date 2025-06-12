# chessminal - free game review in a terminal
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-2.1.4exi-brightgreen.svg)

A terminal application that grades your chess games from their PGN notation.

## How it works.
This app utilises [Stockfish](https://stockfishchess.org) chess engine that grades positions based on the Eval system. This app grades the difference between the eval values and uses a top-notch algorithm to grade moves into 6 categories ranked best to worst:-

- best_move
- book_move
- excellent_move
- good_move
- inaccuracy
- mistake
- blunder

## Installation
You can install chessminal via pip:
```sh
pip install chessminal
```
Ensure you have Python 3.x installed. The package automatically installs required dependencies.

## Usage
Once installed, you can run chessminal directly from the terminal. Run 👇🏻 for guide on how to use.
```sh
chessminal
```

### Game Review - Usage

Download your chess game's PGN file and run.
```sh
chessminal 'path/to/your/pgn/file'
```

## Example Game Review

<img width="1031" alt="image" src="https://github.com/user-attachments/assets/061c951a-2c7e-4d3c-ab5f-6099e4903142" />
