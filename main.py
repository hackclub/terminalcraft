import json
import random
import time
from blessings import Terminal

t = Terminal()
print(t.clear())
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

def getPlayerCount():
	players = []
	try:
		numPlayers = int(input("Enter the number of players: "))
		logo()
		print("\n")
		logo()
		for each in range(numPlayers):
			logo()
# make function to catch empty names
			playerName = input("Enter Player " + str(each + 1) + "'s name: ")
			logo()
			# print ("\n")
			players.append({"number": each + 1, "name": playerName, "hand": []})

		
		return players
	except ValueError:
		logo()
		print("Please enter a number")
		logo()
		getPlayerCount()

def startGame(deck):
	discard = []
	# print(deck)
	discard.append(deck.pop())
	return deck, discard

def logo():
	# print("blah")
	with t.location(0,0):
		print(t.bright_cyan("  .--.--.                                                   ,--,                                 ,----..                                \n /  /    '.   ,--,                                        ,--.'|                                /   /   \\                         ,---, \n|  :  /`. / ,--.'|         ,---,                     ,--, |  | :                __  ,-.        |   :     :             __  ,-.  ,---.'| \n;  |  |--`  |  |,      ,-+-. /  |  ,----._,.       ,'_ /| :  : '              ,' ,'/ /|        .   |  ;. /           ,' ,'/ /|  |   | : \n|  :  ;_    `--'_     ,--.'|'   | /   /  ' /  .--. |  | : |  ' |     ,--.--.  '  | |' |        .   ; /--`   ,--.--.  '  | |' |  |   | | \n \\  \\    `. ,' ,'|   |   |  ,\"' ||   :     |,'_ /| :  . | '  | |    /       \\ |  |   ,'        ;   | ;     /       \\ |  |   ,',--.__| | \n  `----.   \\'  | |   |   | /  | ||   | .\\  .|  ' | |  . . |  | :   .--.  .-. |'  :  /          |   : |    .--.  .-. |'  :  / /   ,'   | \n  __ \\  \\  ||  | :   |   | |  | |.   ; ';  ||  | ' |  | | '  : |__  \\__\\/: . .|  | '           .   | '___  \\__\\/: . .|  | ' .   '  /  | \n /  /`--'  /'  : |__ |   | |  |/ '   .   . |:  | : ;  ; | |  | '.'| ,\" .--.; |;  : |           '   ; : .'| ,\" .--.; |;  : | '   ; |:  | \n'--'.     / |  | '.'||   | |--'   `---`-'| |'  :  `--'   \\;  :    ;/  /  ,.  ||  , ;           '   | '/  :/  /  ,.  ||  , ; |   | '/  ' \n  `--'---'  ;  :    ;|   |/       .'__/\\_: |:  ,      .-./|  ,   /;  :   .'   \\---'            |   :    /;  :   .'   \\---'  |   :    :| \n            |  ,   / '---'        |   :    : `--`----'     ---`-' |  ,     .-./                 \\   \\ .' |  ,     .-./       \\   \\  /   \n             ---`-'                \\   \\  /                        `--`---'                      `---`    `--`---'            `----'    \n                                    `--`-'                                                                                              \n                                                                                                                                        \n                                                                                                                                        \n                                                                                                                                        \n"))

def findColor(input):
	match input:
		case "R":
			return "red"
		case "G":
			return "green"
		case "B":
			return "blue"
		case "Y":
			return "yellow"
		case "K":
			return "wild"

def findType(input):
		match input:
			case "0":
				return "Zero Card"
			case "1":
				return "One Card"
			case "2":
				return "Two Card"
			case "3":
				return "Three Card"
			case "4":
				return "Four Card"
			case "5":
				return "Five Card"
			case "6":
				return "Six Card"
			case "7":
				return "Seven Card"
			case "8":
				return "Eight Card"
			case "9":
				return "Nine Card"
			case "skip":
				return "Skip Card"
			case "reverse":
				return "Reverse Card"
			case "draw2":
				return "Draw 2 Card"
			case "wild":
				return "Wild Card"
			case "wild_draw4":
				return "Wild Draw 4 Card"

def showPlayerCards(currentPlayer):
	for card in currentPlayer["hand"]:
		color = findColor(card[0])
		type = findType(card[1:])



def main():
	logo()
	with t.location(0, t.height - 1):
	# print(t.height)
		# print("blah")
		rawDeck = json.load(open("deck.json")) # opens deck.json and assigns it
		newDeck = shuffleDeck(rawDeck) # shuffles the deck and assigns it


		players = getPlayerCount()
		hands, gameDeck = setupGame(players, 7, newDeck) # sets up the game and assigns the modified deck

		gameDeck, discard = startGame(gameDeck)
	print(t.clear)
	logo()
	
	with t.location(0, t.height - 1):
		for each in players:
			showPlayerCards(each)




main()

# print (gameDeck, discard)







# print ("GAME DECK:")
# print(gameDeck)
# print("\n\n\n")

# print ("PLAYERS:")
# for player in players:
# 	print(player["name"] + ": " + str(player["hand"]))





