from setuptools import setup

setup(
    name="chessminal",
    version="2.1.4",
    packages=["chessminal"],
    package_data={},
    include_package_data=True,
    install_requires=[
        "chess",
        "python-chess",
        "stockfish",
        "requests",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "chessminal=chessminal.main:main",
        ],
    },
    description="chess.com's paid Game Review feature for free in a terminal.",
    long_description="""
# chessminal - free game review in a terminal
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-2.1.4-brightgreen.svg)

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

![ss](https://i.imgur.com/RDb4pbu.png)
""",
    long_description_content_type="text/markdown",
)
