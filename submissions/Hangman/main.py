import os, sys, random, string
from typing import List # For parameter type hints of Lists of strings.
from sty import fg, ef # For cross-platform color coding.

OS_IS_WINDOWS = (sys.platform == "win32") # Needed for a check in the cross-platform clear screen function.

FRAMES_FILE, WORDS_FILE = "files/frames.txt", "files/words.txt"

CRES, SRES, RES = fg.rs, ef.rs, fg.rs + ef.rs # Resets: color-only, style-only, Both.
RED, BLU, GRN, YLW, MAG, CYAN = fg.red, fg.blue, fg.green, fg.yellow, fg.magenta, fg.cyan # Colors
BOLD, ITAL, UNDL = ef.bold, ef.italic, ef.underl # Styles

def group_frames(frame_list: List[str],  frame_exit: str) -> List[str]: # 
    result, buffer = [], "" # We need a buffer since we are going to append multiple lines at once.
    for line in frame_list:
            if line.strip() == frame_exit: # This assumes the frame end char is on its own line.
                result.append(buffer.rstrip("\n")) # Directly modify the passed in frame_list. Remove the extra \n.
                buffer = "" # Reset the buffer.
            else:
                buffer += line
    return result

def clear_screen():
    os.system("cls" if OS_IS_WINDOWS else "clear")

def title(color: str = RES, end: str = "\n"):
    clear_screen()
    print(color + "***************************")
    print(" H   A   N   G   M   A   N")
    print("***************************" + RES, end = end) # If end is passed in, \n must be specified.

def menu() -> bool:
    while (True):
        title(BLU + BOLD)
        print(f"\n{BOLD}{MAG}Welcome to hangman. Can you guess the hidden word?")
        print(f"\n1 - {SRES}{YLW}Play")
        print(f"{BOLD}{MAG}2 - {SRES}{YLW}Quit")
        answer = input(f"\n{SRES}{CYAN}Please choose an option. >>> {CRES}")

        # Allow for both 1 & 2 as answers and any variation of "Play" & "Quit".
        # The user's input was invalid.
        if answer != "1" and answer != "2" and answer.lower() != "play" and answer != "quit":
            print(f"\n{RED}Please input either 1 or 2, or type {BOLD}{CRES}\"Play\"{SRES}{RED} or {BOLD}{CRES}\"Quit\"")
            input(f"{SRES}{CYAN}Press any key to continue >>> {CRES}")
            continue

        # The user chose to play.    
        elif answer == "1" or answer.lower() == "play":
            return True
        
        # The user chose to end the program.
        elif answer == "2" or answer.lower() == "quit":
            print(f"{BOLD}{MAG}\nGoodbye!\n{RES}")
            return False

# This function checks if all the letters in an input string are in the allowed letter list.
def is_input_valid(input: str, allowed_chars: List[str]) -> bool:
    return all(char in allowed_chars for char in input)

# This function checks if a guessed letter is part of the word.
def is_guess_correct(guess: str, word: str) -> bool:
    return any(guess.lower() == letter.lower() for letter in word)

# Display the frame at the specified index with the option to change the end parameter of print().
def show_frame(index: int, frame_list: List[str], color: str = RES, end: str = "\n"):
    print(color + frame_list[index] + RES, end = end) # If end is passed in, \n must be specified.

# Return a string of the word with all letters hidden except those which have been correctly guessed.
def hidden_word(word: str, correct_guessed_letters: str, hidden_symbol: str = "_", letter_color: str = RES) -> str:
    return "".join(f"{letter_color}{letter} {RES}" if letter in correct_guessed_letters # Letter found.
                   else f"{hidden_symbol} {RES}" # Letter not found. Print the hidden symbol instead.
                   for letter in word # Do the above for every letter in the word.
                   ).rstrip(" ") # Get rid of the extra space at the end of the returned string.

# Return a string of all the letters guessed with seperators between each one.
def get_guessed_letters(guessed_letters: List[str], seperator: str = "|", letter_color: str = RES) -> str:
    # Print a letter followed by the seperator for every letter that they've guessed.
    return "".join(f"{letter_color}{letter} {RES}{seperator} {RES}" for letter in guessed_letters
                   ).rstrip(f" {RES}{seperator} {RES}") # Remove the extra seperator.

# Return whether or not a letter has already been guessed.
def already_guessed(char: str, guessed_letters: List[str]) -> bool:
    return (char in guessed_letters)

def play_game(allowed_letters: List[str], frame_list: List[str], allowed_guesses: int = 6):
    guess = "" # The player begins the game having not guessed the word.
    guesses = 0 # The player begins the game haveing not made any guesses.
    guessed_letters = [] # The player begins the game having not guessed any letters.
    correct_guessed_letters = [] # The player begins the word having not correctly guessed any letters.
    with open(WORDS_FILE, "r") as file:
        word = random.choice([line.rstrip("\n") for line in file]) # Set random word.
    
    while (guesses < allowed_guesses):
        frame_index = len(guessed_letters) - len(correct_guessed_letters) # Frame index = incorrect guesses.
        # In round display the title, hangman graphic, hidden word, guessed letters, and incorrect guesses left.
        title(BLU + BOLD, end = "\n\n")
        show_frame(frame_index, frame_list, BOLD + GRN if frame_index < 4 else BOLD + YLW, "\n\n") # Show the hangman graphic.
        print(hidden_word(word, correct_guessed_letters, f"{BOLD}_", GRN + BOLD + ITAL)) # Show word with missing letters.
        if guesses > 0: # Show the previously guessed letters if there are any.
            print(f"\n{BOLD}{MAG}Guessed Letters: {SRES}" + get_guessed_letters(guessed_letters, f"{BOLD}{MAG}|", YLW + ITAL))
        print(f"\n{BOLD}{MAG}Guesses Left: {SRES}{YLW}{ITAL}{str(allowed_guesses - guesses)}{RES}") # Show wrong guesses left.
        guess = input(f"{CYAN}\nWhat is your guess? >>> {CRES}") 

        is_valid_input = is_input_valid(guess.lower(), allowed_letters) and len(guess) == 1
        is_new_guess = not already_guessed(guess, guessed_letters)        
        if not is_new_guess: # They've already guessed this letter.
            print(f"\n{YLW}{BOLD}You already guessed that letter.{SRES}")
            input(f"{CYAN}Press any key to continue. >>> {CRES}")
        if not is_valid_input: # It's not a valid input and/or it's longer than one letter.
            print(f"\n{RED}{BOLD}Please input a valid letter.{SRES}")
            input(f"{CYAN}Press any key to continue. >>> {CRES}")

        if is_valid_input and is_new_guess: # Check whether it is a valid new guess.
            if is_guess_correct(guess, word): # Their guess is correct.
                guessed_letters.append(guess)
                correct_guessed_letters.append(guess)            
            if all(letter in correct_guessed_letters for letter in word): # This is the win state.
                    print(f"\n{GRN}{BOLD}Congratulations! {SRES}You successfully guessed the word.")
                    input(f"{CYAN}Press any key to continue. >>> {CRES}")
                    return
            elif is_guess_correct(guess, word): # They got it correct but there are still unguessed letters in the word.
                    print(f"\n{GRN}{BOLD}Congratulations! {SRES}You guessed one of the letters.")
                    input(f"{CYAN}Press any key to continue. >>> {CRES}")
            else: # The letter is not found in the word.
                print(f"{YLW}{BOLD}\n" + guess, f"{RED}was not part of the word.{SRES}")
                input(f"{CYAN}Press any key to continue. >>> {CRES}")
                guessed_letters.append(guess)
                guesses += 1

    frame_index = allowed_guesses # They used all their allowed_guesses and didn't guess the word. Show the last frame.
    # Recap by displaying the title, hangman graphic, hidden word, guessed letters, and the word itself.
    title(BLU + BOLD, end = "\n\n")
    show_frame(frame_index, frame_list, BOLD + RED, "\n\n") # Show the hangman graphic.
    print("\n" + hidden_word(word, correct_guessed_letters, f"{BOLD}{RED}_", GRN + BOLD + ITAL)) # Position of missed letters.
    print(f"{BOLD}{MAG}Guessed Letters: {SRES}" + get_guessed_letters(guessed_letters, f"{BOLD}{MAG}|", YLW + ITAL))
    print(f"\n{BOLD}{RED}You were hanged on account of terrible word guessing ability.")
    print(f"{MAG}The word was: {YLW}{ITAL}{UNDL}{word}{RES}") # Show them the word.
    print(f"{MAG}Better luck next time?")
    input(f"\n{CYAN}Press any key to continue. >>> {CRES}")
    
def main():
    letters = list(string.ascii_lowercase)
    frames = group_frames(open(FRAMES_FILE, "r").readlines(), "#") # Read the list of all lines then seperate into frames.

    while (True): # The game will go on indefinitely until they choose to quit.
        if menu(): play_game(letters, frames)
        else: sys.exit()

if __name__ == "__main__":
    main()
