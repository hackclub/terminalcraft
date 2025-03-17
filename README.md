# Singular Card

Singular Card is a digital card game that is played in a terminal made for TerminalCraft YSWS ran by Hack Club

## What are the rules?

This game is a recreation of Uno. Up to 14 people can play with hands of 7, ending when a player has no more cards in their hand. 

You can play a card if:

- The card you intend to use has the same color as the card last played
- The card has the same numerical or 'game modifier' type as the card last played
- The card is a "Wild" card
	- This also means you can change the color of this card to any of the four main colors (Red, Green, Blue, Yellow)

You may be restricted from playing a card during your turn if:

- You have no playable cards
	- This will cause you to draw 1 card
- The last played card was a Draw 2 or Draw 4 and you are the next person up after it was played
	- This will cause you to draw 2 or 4 cards, respectively
- The last played card was a Skip and you are the next person up after it was played

Unlike original Uno, you are unable to place a Draw card on top of another Draw card, nor can you increment by number, nor can you jump in and place a card if it isn't your turn, nor can you stack skips to prevent your turn from being skipped. The dev decides the house rules this time! These may be added in the future if time allows for it.


## How to run the game?

This project is built in Python! Running it should be relatively simple.

> It is assumed you have Python3 installed on your computer. Most Unix-like operating systems have Python included but may be outdated. This project was created while using Python 3.13.2 on macOS installed via Homebrew (brew.sh), and tested on an `Ubuntu noble 24.04 aarch64` server using Python 3.12.3


1. Clone the repository
```sh
git clone "https://github.com/HammerPot/SingularCard"
```
2. Navigate to the directory the repository was cloned into
```sh
cd SingularCard
```
3. Install the required packages via pip
```sh
pip install -r requirements.txt
```
> Note this may vary depending on the operating system and environment you are using. Many Linux distros require you to use the system package manager to install Python packages and different versions of Python may have different ways the pip command is named or utilized. Check with your system's documentation to learn best practices with installing Python packages.
4. Run `main.py` from within the repository's directory
```sh
python3 main.py
```
> Once again note that this may also vary depending on the operating system and environment you are using. You may need to specify the path where Python is stored if it isn't in your PATH. Different systems may also name the python command differently. Check with your system's documentation to learn how to run Python on your system.