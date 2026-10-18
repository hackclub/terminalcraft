import os
import sys
from Games import TicTacToe, Connect4, Sudoku, Snake, Hangman, Battleship, Chess

def clear_screen():
    """Clears the terminal screen for a better user experience."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main_menu():
    """Displays the game hub menu and handles user input."""
    while True:
        clear_screen()
        print("🎮 Welcome to TGameHub! 🎮")
        print("1. Play Tic Tac Toe")
        print("2. Play Snake")
        print("3. Play Hangman")
        print("4. Play Connect 4")
        print("5. Play Battleship")
        print("6. Play Sudoku")
        print("7. Play Chess")
        print("9. Exit")
        print("10. Help")
        choice = input("Choose an option (0-7): ").strip()

        if choice == '1':
            TicTacToe.play()
        elif choice == '2':
            Snake.play()
        elif choice == '3':
            Hangman.play()
        elif choice == '4':
            Connect4.play()
        elif choice == '5':
            Battleship.play()
        elif choice == '6':
            Sudoku.play()
        elif choice == '7':
            Chess.play()
        elif choice == '9':
            print("Thanks for playing! Goodbye. 👋")
            sys.exit()
        elif choice == '10':
            print("TGameHub is a collection of classic games written in Python.")
            print("Use the menu to select a game and play.")
            print("Please keep the terminal window size large and zoom out as much as possible to avoid display errors")
            print("If you need help with a specific game, please refer to Readme.md")
        else:
            print("❌ Invalid choice. Please enter a number from 0 to 7.")
            input("Press Enter to try again...")

if __name__ == "__main__":
    main_menu()