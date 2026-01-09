import random
import os

def loadWords(filename):
    """ Returns a list of words from a given file """
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get script's directory
    file_path = os.path.join(script_dir, filename)  # Construct full file path
    with open(file_path, 'r') as file:
        return file.read().strip().split("\n")

def chooseWord(wordlist):
    """ Chooses a random word from the list """
    return random.choice(wordlist)

def isWordGuessed(secretWord, lettersGuessed):
    return all(letter in lettersGuessed for letter in secretWord)

def getGuessedWord(secretWord, lettersGuessed):
    return " ".join(letter if letter in lettersGuessed else "_" for letter in secretWord)

def getAvailableLetters(lettersGuessed):
    import string
    return ''.join(letter for letter in string.ascii_lowercase if letter not in lettersGuessed)

def hangman(secretWord):
    print("Welcome to Hangman! A hangman needs to be saved, thankfully he loves someone with good vocab, so if you can guess the word. He'll regain faith in humanity!")
    print(f"Hangman: I am thinking of a word that is {len(secretWord)} letters long.")
    
    mistakeMade = 0
    lettersGuessed = []
    
    while 8 - mistakeMade > 0: 
        print("-------------")
        if isWordGuessed(secretWord, lettersGuessed):
            print("Congratulations, you saved him!")
            break
        else:
            print(f"You have {8 - mistakeMade} guesses left.")
            print("Available letters:", getAvailableLetters(lettersGuessed))
            guess = input("Please guess a letter: ").lower()
            
            if guess in lettersGuessed:
                print("Oops! You've already guessed that letter:", getGuessedWord(secretWord, lettersGuessed))
            elif guess in secretWord:
                lettersGuessed.append(guess)
                print("Good guess:", getGuessedWord(secretWord, lettersGuessed))
            else:
                lettersGuessed.append(guess)
                mistakeMade += 1
                print("Oops! That letter is not in my word:", getGuessedWord(secretWord, lettersGuessed))
            
        if 8 - mistakeMade == 0:
            print("-------------")
            print(f"Sorry, you ran out of guesses. The hangman hanged himself. The word was {secretWord}.")
            break

def play():
    wordlist = loadWords("words.txt")
    secretWord = chooseWord(wordlist).lower()
    hangman(secretWord)
