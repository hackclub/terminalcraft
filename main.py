import json
import random


def shuffleDeck(deck):
	# takes in a json object of a deck and shuffles it
	red = deck["standard"]["color"]["red"]
	green = deck["standard"]["color"]["green"]
	blue = deck["standard"]["color"]["blue"]
	yellow = deck["standard"]["color"]["yellow"]
	black = deck["standard"]["color"]["black"]

	fullDeck = red + green + blue + yellow + black
	random.shuffle(fullDeck)

	return fullDeck

def setupGame(players, count, deck): # takes in a list of players and the count of cards to deal as well as the shuffled deck
	for i in range(count):
		for player in players:
			player["hand"].append(deck.pop(0));

	return players, deck

rawDeck = json.load(open("deck.json")) # opens deck.json and assigns it


players = [ # list of players (make it dynamic from user input later!!)
    {"name": "Player 1", "hand": []},
    {"name": "Player 2", "hand": []},
    {"name": "Player 3", "hand": []},
    {"name": "Player 4", "hand": []}
]

newDeck = shuffleDeck(rawDeck) # shuffles the deck and assigns it

hands, gameDeck = setupGame(players, 7, newDeck) # sets up the game and assigns the modified deck


