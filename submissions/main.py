import os
import sys

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    clear_screen()
    print("=== Game Selection Menu ===")
    print("1. Forest of Shadows")
    print("2. Snake")
    print("3. Tetris")
    print("4. Exit")
    print("========================")

def main():
    while True:
        print_menu()
        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            clear_screen()
            print("Starting Forest of Shadows...\n")
            import forest
            forest.main()
        elif choice == "2":
            clear_screen()
            print("Starting Snake...\n")
            import snake
            snake.main()
        elif choice == "3":
            clear_screen()
            print("Starting Tetris...\n")
            import tetris
            game = tetris.TetrisGame()
            game.run()
        elif choice == "4":
            print("\nThanks for playing! Goodbye!")
            sys.exit()
        else:
            print("\nInvalid choice. Please try again.")
            input("Press Enter to continue...")
            continue

        # After game ends, wait for user input before showing menu again
        print("\nGame ended.")
        input("Press Enter to return to main menu...")

if __name__ == "__main__":
    main() 
