import random

def run():
    word_list = ["python", "hangman", "programming", "computer", "science"]
    word = random.choice(word_list)
    word_length = len(word)
    
    # ASCII art for hangman
    hangman_stages = [
        """
        +---+
        |   |
        O   |
        |   |
        |   |
        |   |
        =========
        """,
        """
        +---+
        |   |
        O   |
        |   |
        |   |
        |   |
        =========
        """,
        """
        +---+
        |   |
        O   |
        |   |
        |   |
        |   |
        =========
        """,
        """
        +---+
        |   |
        O   |
        |   |
        |   |
        |   |
        =========
        """,
        """
        +---+
        |   |
        O   |
        /|  |
        |   |
        |   |
        =========
        """,
        """
        +---+
        |   |
        O   |
        /|\ |
        |   |
        |   |
        =========
        """,
        """
        +---+
        |   |
        O   |
        /|\ |
        /  |
        |   |
        =========
        """,
        """
        +---+
        |   |
        O   |
        /|\ |
        / \ |
        |   |
        =========
        """
    ]
    
    lives = 6
    guessed_letters = []
    display = "_" * word_length
    
    while lives > 0:
        print(hangman_stages[lives])
        print(display)
        guess = input("Guess a letter: ").lower()
        
        if guess in word:
            index = word.find(guess)
            while index != -1:
                display = display[:index] + guess + display[index + 1:]
                index = word.find(guess, index + 1)
        else:
            lives -= 1
            guessed_letters.append(guess)
            
        if "_" not in display:
            print(hangman_stages[lives])
            print(display)
            print("You win!")
            break
        
    if lives == 0:
        print(hangman_stages[lives])
        print("You lose! The word was:", word)
