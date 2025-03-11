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

# print ("UNSHUFFLED DECK:")
# print(rawDeck)
# print("\n\n\n")

# players = [ # list of players (make it dynamic from user input later!!)
#     {"name": "Player 1", "hand": []},
#     {"name": "Player 2", "hand": []},
#     {"name": "Player 3", "hand": []},
#     {"name": "Player 4", "hand": []}
# ]

def getPlayerCount():
	players = []
	try:
		numPlayers = int(input("Enter the number of players: "))
		for each in range(numPlayers):
			playerName = input("Enter player " + str(each + 1) + "'s name: ")
			players.append({"name": playerName, "hand": []})

		return players
	except ValueError:
		print("Please enter a number")
		getPlayerCount()

players = getPlayerCount()

print(players)
newDeck = shuffleDeck(rawDeck) # shuffles the deck and assigns it
# print ("SHUFFLED DECK:")
# print(newDeck)
# print("\n\n\n")

hands, gameDeck = setupGame(players, 7, newDeck) # sets up the game and assigns the modified deck

# print ("GAME DECK:")
# print(gameDeck)
# print("\n\n\n")

# print ("PLAYERS:")
# for player in players:
# 	print(player["name"] + ": " + str(player["hand"]))




