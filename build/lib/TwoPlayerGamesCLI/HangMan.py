import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_hangman(attempts):
    stages = [
        '''
           -----
           |   |
           O   |
          /|\  |
          / \  |
               |
        =========
        ''',
        '''
           -----
           |   |
           O   |
          /|\  |
          /    |
               |
        =========
        ''',
        '''
           -----
           |   |
           O   |
          /|\  |
               |
               |
        =========
        ''',
        '''
           -----
           |   |
           O   |
          /|   |
               |
               |
        =========
        ''',
        '''
           -----
           |   |
           O   |
           |   |
               |
               |
        =========
        ''',
        '''
           -----
           |   |
           O   |
               |
               |
               |
        =========
        ''',
        '''
           -----
           |   |
               |
               |
               |
               |
        =========
        '''
    ]
    return stages[attempts]

def hangman_game():
    # Player 1 provides the word
    clear_screen()
    print('lets play hangman')
    print("Player 1: Enter the word to be guessed (No peeking, Player 2!).")
    secret_word = input("Enter the secret word: ").lower().strip()
    while not secret_word.isalpha():
        print("Invalid input. Please enter a valid word.")
        secret_word = input("Enter the secret word: ").lower().strip()

    clear_screen()
    print("Word is set. Player 2, it's your turn to guess!")

    # Initialize game variables
    guessed_word = ['_'] * len(secret_word)
    attempts = 6  # Allow 6 incorrect guesses
    guessed_letters = set()
    print(display_hangman(-1))

    while attempts > 0 and ''.join(guessed_word) != secret_word:
        print("\nWord: ", ' '.join(guessed_word))
        print(f"Attempts left: {attempts}")
        print(f"Guessed letters: {', '.join(sorted(guessed_letters))}")
        
        guess = input("Player 2, enter a letter: ").lower()

        # Validate input
        if len(guess) != 1 or not guess.isalpha():
            print("Invalid input. Please enter a single letter.")
            continue
        
        if guess in guessed_letters:
            print(f"You already guessed '{guess}'. Try a different letter.")
            continue

        # Add guess to guessed letters
        guessed_letters.add(guess)

        if guess in secret_word:
            print(f"Good job! '{guess}' is in the word.")
            for i in range(len(secret_word)):
                if secret_word[i] == guess:
                    guessed_word[i] = guess
        else:
            print(f"Oops! '{guess}' is not in the word.")
            attempts -= 1  # Decrease attempts on wrong guess
        
        clear_screen()
        print(display_hangman(attempts))

    # Determine points and winner
    if ''.join(guessed_word) == secret_word:
        print(f"Congratulations Player 2! You guessed the word: {secret_word}")
        return (0, 2)  # Player 2 wins
    else:
        print(f"Game over! The word was: {secret_word}")
        return (2, 0)  # Player 1 wins

# Run the game
#points = hangman_game()
#print(f"\nFinal Points: Player 1 - {points[0]}, Player 2 - {points[1]}")
