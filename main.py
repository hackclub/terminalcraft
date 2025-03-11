import json
import random
import curses
# curses.initscr()


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
		print("\n")
		for each in range(numPlayers):
			playerName = input("Enter Player " + str(each + 1) + "'s name: ")
			# print ("\n")
			players.append({"name": playerName, "hand": []})

		
		return players
	except ValueError:
		print("Please enter a number")
		getPlayerCount()

def startGame(deck):
	discard = []
	print(deck)
	discard.append(deck.pop())
	return deck, discard


print(r"""

                                                                                                                                        
                                                                                                                                        
  .--.--.                                                   ,--,                                 ,----..                                
 /  /    '.   ,--,                                        ,--.'|                                /   /   \                         ,---, 
|  :  /`. / ,--.'|         ,---,                     ,--, |  | :                __  ,-.        |   :     :             __  ,-.  ,---.'| 
;  |  |--`  |  |,      ,-+-. /  |  ,----._,.       ,'_ /| :  : '              ,' ,'/ /|        .   |  ;. /           ,' ,'/ /|  |   | : 
|  :  ;_    `--'_     ,--.'|'   | /   /  ' /  .--. |  | : |  ' |     ,--.--.  '  | |' |        .   ; /--`   ,--.--.  '  | |' |  |   | | 
 \  \    `. ,' ,'|   |   |  ,"' ||   :     |,'_ /| :  . | '  | |    /       \ |  |   ,'        ;   | ;     /       \ |  |   ,',--.__| | 
  `----.   \'  | |   |   | /  | ||   | .\  .|  ' | |  . . |  | :   .--.  .-. |'  :  /          |   : |    .--.  .-. |'  :  / /   ,'   | 
  __ \  \  ||  | :   |   | |  | |.   ; ';  ||  | ' |  | | '  : |__  \__\/: . .|  | '           .   | '___  \__\/: . .|  | ' .   '  /  | 
 /  /`--'  /'  : |__ |   | |  |/ '   .   . |:  | : ;  ; | |  | '.'| ," .--.; |;  : |           '   ; : .'| ," .--.; |;  : | '   ; |:  | 
'--'.     / |  | '.'||   | |--'   `---`-'| |'  :  `--'   \;  :    ;/  /  ,.  ||  , ;           '   | '/  :/  /  ,.  ||  , ; |   | '/  ' 
  `--'---'  ;  :    ;|   |/       .'__/\_: |:  ,      .-./|  ,   /;  :   .'   \---'            |   :    /;  :   .'   \---'  |   :    :| 
            |  ,   / '---'        |   :    : `--`----'     ---`-' |  ,     .-./                 \   \ .' |  ,     .-./       \   \  /   
             ---`-'                \   \  /                        `--`---'                      `---`    `--`---'            `----'    
                                    `--`-'                                                                                              

	  

""")


rawDeck = json.load(open("deck.json")) # opens deck.json and assigns it
newDeck = shuffleDeck(rawDeck) # shuffles the deck and assigns it


players = getPlayerCount()
hands, gameDeck = setupGame(players, 7, newDeck) # sets up the game and assigns the modified deck

gameDeck, discard = startGame(gameDeck)



# print (gameDeck, discard)







# print ("GAME DECK:")
# print(gameDeck)
# print("\n\n\n")

# print ("PLAYERS:")
# for player in players:
# 	print(player["name"] + ": " + str(player["hand"]))





