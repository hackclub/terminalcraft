import random
import os
def clear_screen():
    # Check the operating system and clear the terminal accordingly
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For Linux/Mac
        os.system('clear')
def description():
    print('''
This game does the following:

1. Randomly selects a player to write the sentences.
2. Asks the selected player to input two truth sentences and one lie sentence.
3. Clears the screen, shuffles the sentences, and labels them 1, 2, and 3.
4. Asks the other player to guess the number of the lie sentence.
5. Checks if the guess is correct and awards points accordingly.
6. Returns a tuple containing the points for each player.''')


def game():
    players = ['Player1', 'Player2']
    sentence_player = random.choice(players)
    guess_player = [player for player in players if player != sentence_player][0]
    lie_sentence =''

    print(f"{sentence_player} will write the sentences.")
    print(f"{guess_player} will try to guess the lie.")

    sentences = []
    for i in range(3):
        if i < 2:
            sentence = input(f"{sentence_player}, enter truth sentence {i+1}: ")
        else:
            sentence = input(f"{sentence_player}, enter a lie sentence: ")
            lie_sentence = sentence
        sentences.append(sentence)

    clear_screen()

    random.shuffle(sentences)

    for i, sentence in enumerate(sentences):
        print(f"{i+1}. {sentence}")

    guess = input(f"{guess_player}, enter the number of the lie sentence: ")

    while not guess.isdigit() or not 1 <= int(guess) <= 3:
        guess = input("Invalid input. Please enter a number between 1 and 3: ")

    guess = int(guess)

    if sentences[guess-1] == lie_sentence:
        print(f"{guess_player} wins! {sentence_player} loses.")
        if guess_player == 'Player1':
            return (2,0)
        else:
            return(0,2)
    else:
        print(f"{sentence_player} wins! {guess_player} loses.")
        if guess_player == 'Player2':
            return (2,0)
        else:
            return(0,2)

#points = game()
#print(f"Final points: Player 1 - {points[0]}, Player 2 - {points[1]}")

