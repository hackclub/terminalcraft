
import random
import time

def word_chain_game():
    players = ['Player 1', 'Player 2']
    current_player = random.choice(players)
    other_player = [player for player in players if player != current_player][0]

    print(f"{current_player} will start the game.")

    timer = int(input("Enter the timer in seconds: "))
    start_time = time.time()

    words = set()
    while True:
        print(f"\n{current_player}'s turn:")
        word = input("Enter a word: ")

        if word in words:
            print("Word already entered. Try again.")
            continue

        words.add(word)

        if time.time() - start_time > timer:
            print(f"Time's up! {current_player} loses.")
            if current_player == 'Player 1':
                return (0, 2)
            else:
                return (2, 0)

        if current_player == 'Player 1':
            current_player = 'Player 2'
            other_player = 'Player 1'
        else:
            current_player = 'Player 1'
            other_player = 'Player 2'

        last_letter = word[-1]
        print(f"\n{current_player}'s turn: Enter a word starting with '{last_letter}':")

#points = word_chain_game()
#print(f"Final points: Player 1 - {points[0]}, Player 2 - {points[1]}")
def descripton():
    _b = '''
This description does the following:

1. Randomly selects a player to start the game.
2. Asks the current player to enter a word.
3. Checks if the word has already been entered.
4. Adds the word to the set of entered words.
5. Checks if the timer has expired.
6. Switches the current player.
7. Asks the new current player to enter a word starting with the last letter of the previous word.
8. Returns a tuple containing the points for each player.'''
    print(_b)