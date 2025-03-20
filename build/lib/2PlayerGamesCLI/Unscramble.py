
import random
import time
import os
description ='''
    
This game does the following:

    1. Randomly selects a player to enter the words.
    2. Asks the current player to enter a word.
    3. Scrambles the word.
    4. Asks the other player to unscramble the word.
    5. Checks if the answer is correct and within the time limit.
    6. Updates the points and switches the players if the answer is correct.
    7. Reduces the timer by 20 percent for each turn.
    8. Returns a tuple containing the points for each player.
    
Important: Base timer is the time given to solve each word.
           you have the flexibility of your own choice you can decide for difficult words
           but you will give each other some hits decided between you . 
           so you probably will set the timer to couple minutes.


          '''
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def scramble_word(word):
    
    scrambled_word = list(word)
    random.shuffle(scrambled_word)
    return ''.join(scrambled_word)

def scrambled_word_game():
    print(description)
    
    players = ['Player 1', 'Player 2']
    current_player = random.choice(players)
    other_player = [player for player in players if player != current_player][0]
    
    try:
        base_timer = int(input("Enter the base timer in seconds: "))
    except:
        print('Error! pls type a numeric value')
        base_timer = int(input("Enter the base timer in seconds: "))
    
    clear_screen()
    print(f"{current_player} will enter the words.")

    points = [0, 0]
    while True:
        word = input(f"\n{current_player}, enter a word: ")
        scrambled_word = scramble_word(word)

        clear_screen()
        print(f"\n{other_player}'s turn: Unscramble the word '{scrambled_word}':")
        start_time = time.time()
        answer = input("Enter your answer: ")
        end_time = time.time()

        timer = base_timer + (len(word) - 3) * 5
        if end_time - start_time > timer:
            print(f"Time's up! {other_player} loses.")
            points[0 if current_player == 'Player 1' else 1] += 2
            break

        if answer.lower() == word.lower():
            print("Correct!")
            current_player, other_player = other_player, current_player
            base_timer *= 0.8  # Reduce the timer by 20% for each turn
        else:
            print(f"Incorrect. The correct answer is '{word}'.")
            points[0 if current_player == 'Player 1' else 1] += 2
            break

    return tuple(points)

#points = scrambled_word_game()
#print(f"Final points: Player 1 - {points[0]}, Player 2 - {points[1]}")

    
