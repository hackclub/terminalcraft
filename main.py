import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def welcome():
    print("Welcome to the Classic Games CLI!")
    print("Please choose a game to play:")

def selection():
    print("1. Tic Tac Toe")
    print("2. Madlibs")
    print("3. Crossword Puzzles")
    print("4. Sudoku")
    print("5. Exit")
    return input("Enter your choice: ")

def tic_tac_toe():
    print("Starting Tic Tac Toe...")
    # Simple Tic Tac Toe implementation
    board = [' ' for _ in range(9)]
    def print_board():
        for i in range(3):
            print('|'.join(board[i*3:(i+1)*3]))
            if i < 2:
                print('-' * 5)
    def check_winner(player):
        win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
        return any(board[a] == board[b] == board[c] == player for a, b, c in win_conditions)
    current_player = 'X'
    for _ in range(9):
        print_board()
        move = int(input(f"Player {current_player}, enter your move (1-9): ")) - 1
        if board[move] == ' ':
            board[move] = current_player
            if check_winner(current_player):
                print_board()
                print(f"Player {current_player} wins!")
                return
            current_player = 'O' if current_player == 'X' else 'X'
        else:
            print("Invalid move. Try again.")
    print_board()
    print("It's a tie!")

def madlibs():
    def madlib1():
        story = "Today I went to the {place}. I saw a {adjective} {noun}."
        place = input("Enter a place: ")
        adjective = input("Enter an adjective: ")
        noun = input("Enter a noun: ")
        print(story.format(place=place, adjective=adjective, noun=noun))

    def madlib2():
        story = "The {adjective} {noun} jumped over the {adjective2} {noun2}."
        adjective = input("Enter an adjective: ")
        noun = input("Enter a noun: ")
        adjective2 = input("Enter another adjective: ")
        noun2 = input("Enter another noun: ")
        print(story.format(adjective=adjective, noun=noun, adjective2=adjective2, noun2=noun2))

    def madlib3():
        story = "My favorite {noun} is {adjective} and {verb} all the time."
        noun = input("Enter a noun: ")
        adjective = input("Enter an adjective: ")
        verb = input("Enter a verb: ")
        print(story.format(noun=noun, adjective=adjective, verb=verb))

    while True:
        print("Choose a Madlib story:")
        print("Is under construction")
        print("1. Story 1")
        print("2. Story 2")
        print("3. Story 3")
        print("4. Back to main menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            madlib1()
        elif choice == '2':
            madlib2()
        elif choice == '3':
            madlib3()
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")
        input("Press Enter to continue...")
        clear_screen()

def crossword_puzzles():
    print("Starting Crossword Puzzles...")
    # Placeholder for Crossword Puzzles implementation
    print("Crossword Puzzles game is under development.")

def sudoku():
    print("Starting Sudoku...")
    # Placeholder for Sudoku implementation
    print("Sudoku game is under development.")

def main():
    clear_screen()
    welcome()
    while True:
        choice = selection()
        clear_screen()
        if choice == '1':
            tic_tac_toe()
        elif choice == '2':
            madlibs()
        elif choice == '3':
            crossword_puzzles()
        elif choice == '4':
            sudoku()
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
        input("Press Enter to return to the main menu...")
        clear_screen()
        welcome()

if __name__ == "__main__":
    main()
