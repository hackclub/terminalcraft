import json
import random
import time
from blessed import Terminal

t = Terminal()
print(t.clear)
drawCheck = False
reverseCheck = False
skipCheck = False

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
		print("Hint: Must be more than 1 player and less than 15 players!")
		logo()
		numPlayers = int(input("Enter the number of players: "))
		if numPlayers > 14: raise ValueError
		if numPlayers <= 1: raise ValueError
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
		print("Please enter a number less than 15")
		logo()
		return getPlayerCount()

def startGame(deck):
	discard = []
	# print(deck)
	discard.append(deck.pop())
	discard[0] = "Kwild"
	if discard[0][:1] == "K":
		x = random.randrange(1, 4)
		if(x == 1):
			discard[0] = "R" + discard[0][1:]
		elif(x == 2):
			discard[0] = "G" + discard[0][1:]
		elif(x == 3):
			discard[0] = "B" + discard[0][1:]
		elif(x == 4):
			discard[0] = "Y" + discard[0][1:]
	return deck, discard

def logo():
	# print("blah")
	with t.location(0,0):
		print(t.bright_cyan("  .--.--.                                                   ,--,                                 ,----..                                \n /  /    '.   ,--,                                        ,--.'|                                /   /   \\                         ,---, \n|  :  /`. / ,--.'|         ,---,                     ,--, |  | :                __  ,-.        |   :     :             __  ,-.  ,---.'| \n;  |  |--`  |  |,      ,-+-. /  |  ,----._,.       ,'_ /| :  : '              ,' ,'/ /|        .   |  ;. /           ,' ,'/ /|  |   | : \n|  :  ;_    `--'_     ,--.'|'   | /   /  ' /  .--. |  | : |  ' |     ,--.--.  '  | |' |        .   ; /--`   ,--.--.  '  | |' |  |   | | \n \\  \\    `. ,' ,'|   |   |  ,\"' ||   :     |,'_ /| :  . | '  | |    /       \\ |  |   ,'        ;   | ;     /       \\ |  |   ,',--.__| | \n  `----.   \\'  | |   |   | /  | ||   | .\\  .|  ' | |  . . |  | :   .--.  .-. |'  :  /          |   : |    .--.  .-. |'  :  / /   ,'   | \n  __ \\  \\  ||  | :   |   | |  | |.   ; ';  ||  | ' |  | | '  : |__  \\__\\/: . .|  | '           .   | '___  \\__\\/: . .|  | ' .   '  /  | \n /  /`--'  /'  : |__ |   | |  |/ '   .   . |:  | : ;  ; | |  | '.'| ,\" .--.; |;  : |           '   ; : .'| ,\" .--.; |;  : | '   ; |:  | \n'--'.     / |  | '.'||   | |--'   `---`-'| |'  :  `--'   \\;  :    ;/  /  ,.  ||  , ;           '   | '/  :/  /  ,.  ||  , ; |   | '/  ' \n  `--'---'  ;  :    ;|   |/       .'__/\\_: |:  ,      .-./|  ,   /;  :   .'   \\---'            |   :    /;  :   .'   \\---'  |   :    :| \n            |  ,   / '---'        |   :    : `--`----'     ---`-' |  ,     .-./                 \\   \\ .' |  ,     .-./       \\   \\  /   \n             ---`-'                \\   \\  /                        `--`---'                      `---`    `--`---'            `----'    \n                                    `--`-'                                                                                              \n                                                                                                                                        \n                                                                                                                                        \n                                                                                                                                        \n"))

def findColor(input):
	match input:
		case "R":
			return "Red"
		case "G":
			return "Green"
		case "B":
			return "Blue"
		case "Y":
			return "Yellow"
		case "K":
			return "Wild"

def findType(input):
		# j = json.load(open("cardFont.json"))
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

def jsonType(input):
		j = json.load(open("cardFont.json"))
		match input:
			case "0":
				return j["0"]
			case "1":
				return j["1"]
			case "2":
				return j["2"]
			case "3":
				return j["3"]
			case "4":
				return j["4"]
			case "5":
				return j["5"]
			case "6":
				return j["6"]
			case "7":
				return j["7"]
			case "8":
				return j["8"]
			case "9":
				return j["9"]
			case "skip":
				return j["skip"]
			case "reverse":
				return j["reverse"]
			case "draw2":
				return j["draw"]
			case "wild":
				return j["wild"]
			case "wild_draw4":
				return j["draw"]

def machineType(input):
	match input:
			case "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9":
				return int(input)
			case "skip":
				return 11
			case "reverse":
				return 12
			case "draw2":
				return 13
			case "wild":
				return 14
			case "wild_draw4":
				return 15

def reshuffleDeck(gameDeck, discard):
	logo()
	logo()
	if len(discard) > 1:
		if gameDeck == None: gameDeck = discard[:-1]
		else: gameDeck = gameDeck + discard[:-1]
	else:
		if gameDeck == None: gameDeck = discard[0]
		else: gameDeck = gameDeck + discard[0]
	discard = [discard[-1]]
	random.shuffle(gameDeck)
	for each in range(len(gameDeck)):
		if machineType(gameDeck[each][1:]) == 14 or machineType(gameDeck[each][1:]) == 15:
			gameDeck[each] = "K" + gameDeck[each][1:]
	# print(gameDeck)
	return gameDeck, discard

def showPlayerCards(currentPlayer, gameDeck, discard, playerMatch):
	global drawCheck
	global skipCheck
	# print(drawCheck)
	print(t.clear)
	logo()
	with t.location(0, t.height - 1):
		input("Waiting for " + t.bold(currentPlayer["name"]) + " to hit Enter!")
	print(t.clear)
	with t.location(0, t.height -1):
		hand = []
		color = []
		type = []
		typeM = []
		handSize = True
		print("Showing the cards of " + t.on_bright_white(t.bold(t.black(" " + currentPlayer["name"] + " "))))
		# print(discard)
		printCard(discard)
		logo()
		for card in currentPlayer["hand"]:
			color.append(findColor(card[0]))
			type.append(findType(card[1:]))
			typeM.append(machineType(card[1:]))
			hand.append(findColor(card[0]) + " " + findType(card[1:]))
		for each in range(len(hand)):
			if color[each].lower() == "red": print(t.red(str(each + 1) + ". " + t.bold(color[each] + " " + type[each][:-4])))
			elif color[each].lower() == "blue": print(t.blue(str(each + 1) + ". " + t.bold(color[each] + " " + type[each][:-4])))
			elif color[each].lower() == "green": print(t.green(str(each + 1) + ". " + t.bold(color[each] + " " + type[each][:-4])))
			elif color[each].lower() == "yellow": print(t.yellow(str(each + 1) + ". " + t.bold(color[each] + " " + type[each][:-4])))
			elif color[each].lower() == "wild": print(str(each + 1) + ". " + t.bold(type[each][:-4]))
			else: print(str(each + 1) + ". " + hand[each])
			logo()
		logo()
		print("\n")

		validPlay = False
		action = False
		for each in typeM:
			if each == machineType(discard[-1][1:]): validPlay = True
			if each == 14 or each == 15: validPlay = True
		for each in color:
				if each == findColor(discard[-1][0]): validPlay = True
				if each == "Wild": validPlay = True

		if machineType(discard[-1][1:]) == 11 and skipCheck == True: 
			validPlay = False
			action = True
			print("Your turn has been skipped!")
			input("Press enter to acknowledge\a")
			skipCheck = False
		if machineType(discard[-1][1:]) == 13 and drawCheck == True: 
			validPlay = False
			action = True
			print("Draw 2 in place")
			print("Drawing two cards!")
			input("Press enter to acknowledge\a")
			currentPlayer["hand"].append(gameDeck.pop())
			currentPlayer["hand"].append(gameDeck.pop())
			drawCheck = False
		if machineType(discard[-1][1:]) == 15 and drawCheck == True: 
			validPlay = False
			action = True
			print("Draw 4 in place")
			print("Drawing four cards!")
			input("Press enter to acknowledge\a")
			currentPlayer["hand"].append(gameDeck.pop())
			currentPlayer["hand"].append(gameDeck.pop())
			currentPlayer["hand"].append(gameDeck.pop())
			currentPlayer["hand"].append(gameDeck.pop())
			drawCheck = False

		if validPlay == True: 
			choice, wild, playerMatch = playCard(currentPlayer["hand"], discard, playerMatch)
			# print(wild)
			if (wild != None):
				currentPlayer["hand"][choice-1] = wild + currentPlayer["hand"][choice-1][1:]

			lenBefore = len(currentPlayer["hand"])
			discard.append(currentPlayer["hand"].pop(choice-1))
			lenAfter = len(currentPlayer["hand"])
		else: 
			if action == False:
				print("No playable cards!") 
				print("Drawing one card!")
				input("Press enter to acknowledge")
				currentPlayer["hand"].append(gameDeck.pop())

		if len(currentPlayer["hand"]) <= 0: 
			handSize = False

		return handSize, currentPlayer, playerMatch

def playCard(hand, discard, playerMatch):
	global drawCheck
	global reverseCheck
	global skipCheck
	logo()
	colorD = findColor(discard[-1][0])
	typeD = machineType(discard[-1][1:])
	wild = None
	try:
		choice = int(input("Choose a card to play: "))
		if choice > len(hand) or choice < 1:
			raise ValueError
		color = findColor(hand[choice-1][0])
		type = machineType(hand[choice-1][1:])
		# choice = 1
		if type == 13:
			drawCheck = True
			return choice, wild, playerMatch
		elif type == 14:
			wild = chooseWild()
			return choice, wild, playerMatch
		elif type == 15:
			drawCheck = True
			wild = chooseWild()
			return choice, wild, playerMatch
		elif type == 12:
			reverseCheck = not reverseCheck
			if reverseCheck == True: playerMatch -= 2
			if reverseCheck == False: playerMatch += 2
			return choice, wild, playerMatch
		elif type == 11:
			skipCheck = True
			return choice, wild, playerMatch
		elif color != colorD and type!=typeD:
			raise ValueError
		else:
			return choice, wild, playerMatch
	except ValueError:
		print("Not a valid choice")
		choice, wild, playerMatch = playCard(hand, discard, playerMatch)
		return choice, wild, playerMatch

def chooseWild():
	try:
		print(t.bold("Hint: Use the first letter of the color"))
		wild = input("What color do you want: ")
		if wild != None and wild != "": 
			wild = wild[0].upper()
		else: raise ValueError
		if wild != "R" and wild != "B" and wild != "G" and wild != "Y": raise ValueError
		else: return wild
	except ValueError:
		print("Not a valid color")
		return chooseWild()

def printCard(discard):
	color = findColor(discard[-1][0]).lower()
	text = jsonType(discard[-1][1:])
	for each in range(len(text)):
		with t.location(int(t.width/2), int(t.height/2) + each):
			if color == "red": print(t.red(text[each]))
			elif color == "blue": print(t.blue(text[each]))
			elif color == "green": print(t.green(text[each]))
			elif color == "yellow": print(t.yellow(text[each]))
			elif color == "wild": print(text)
		


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
	
	handSize = True
	playerWin = []
	playerMatch = 1

	# print(discard)
	# time.sleep(5)
	with t.location(0, t.height - 1):
		while handSize is True:
			while reverseCheck is False:
				if handSize is False and playerWin != []: break
				for each in range(len(players)):
					if gameDeck == None or len(gameDeck) < 4: 
						gameDeck, discard = reshuffleDeck(discard, gameDeck)
					# if playerMatch != players[each]["number"] and playerMatch == playerMatch[-2]["number"] and each == 1: 
					# 	playerMatch = players[2]["number"]

					canRun = True
					if playerMatch != players[each]["number"]: 
						canRun = False
					if canRun == True:
						playerMatch += 1
						if playerMatch > players[-1]["number"]: playerMatch = 1
						handSize, players[each], playerMatch = showPlayerCards(players[each], gameDeck, discard, playerMatch)
						if playerMatch == 0: playerMatch = players[-1]["number"]
						if playerMatch == -1: playerMatch = players[-2]["number"]
						if reverseCheck is True: 
							print("The order has been reversed!\a")
							input("Press enter to acknowledge")
							break
						if handSize is False:
							playerWin = players[each]
							break
			while reverseCheck is True:
				if handSize is False and playerWin != []: break
				for each in reversed(range(len(players))):
					if gameDeck == None or len(gameDeck) < 4: 
						gameDeck, discard = reshuffleDeck(discard, gameDeck)
					# if playerMatch != players[each]["number"] and playerMatch == 2 and each == players[-1]["number"]: 
					# 	playerMatch = players[-2]["number"]
					canRun = True
					if playerMatch != players[each]["number"]: 
						canRun = False
					if canRun == True:
						playerMatch -= 1
						if playerMatch < players[1]["number"]: playerMatch = players[-1]["number"]
						handSize, players[each], playerMatch = showPlayerCards(players[each], gameDeck, discard, playerMatch)
						if playerMatch == players[-1]["number"] + 1: playerMatch = 1
						if playerMatch == players[-1]["number"] + 2 : playerMatch = 2 
						if reverseCheck is False: 
							print("The order has been reversed!\a")
							input("Press enter to acknowledge")
							break
						if handSize is False:
							playerWin = players[each]
							break
					logo()
				# input("Blah")
	print(t.clear)
	logo()
	with t.location(0, t.height - 1):
		print(t.bold(playerWin["name"] + " won the game!!!\a"))
		input("Press " +t.bold("Enter") + " to end the game!")
	



main()

# print (gameDeck, discard)







# print ("GAME DECK:")
# print(gameDeck)
# print("\n\n\n")

# print ("PLAYERS:")
# for player in players:
# 	print(player["name"] + ": " + str(player["hand"]))





