import numpy as np
import curses

# Initialize the board and game state
ROWS, COLS = 3, 3
board = np.array(["-"] * 9)
game_on = True
current_player = None  # will be set after player selection

def display_board(stdscr):
    """Display the current board with position numbers."""
    stdscr.clear()
    try:
        height, width = stdscr.getmaxyx()
        if height < ROWS + 3 or width < COLS * 4:
            raise ValueError("Window too small")
        stdscr.addstr(0, 0, f"{board[0]} | {board[1]} | {board[2]}      1 | 2 | 3")
        stdscr.addstr(1, 0, f"{board[3]} | {board[4]} | {board[5]}      4 | 5 | 6")
        stdscr.addstr(2, 0, f"{board[6]} | {board[7]} | {board[8]}      7 | 8 | 9")
    except ValueError as e:
        stdscr.clear()
        stdscr.addstr(0, 0, str(e))
        stdscr.addstr(1, 0, "Please resize the window and press any key to continue.")
    stdscr.refresh()

def choose_players(stdscr):
    """Prompt Player 1 to choose a marker, and assign the other to Player 2."""
    while True:
        stdscr.addstr(4, 0, "Select Player 1 marker (X or O): ")
        stdscr.refresh()
        p1 = stdscr.getkey().upper().strip()
        if p1 in ("X", "O"):
            p2 = "O" if p1 == "X" else "X"
            stdscr.addstr(5, 0, f"Player 1: {p1}, Player 2: {p2}")
            stdscr.refresh()
            stdscr.getch()
            return p1
        stdscr.addstr(5, 0, "Invalid input. Please choose X or O.")
        stdscr.refresh()

def get_move(stdscr, player):
    """Prompt the current player for a valid move and return the board index."""
    while True:
        stdscr.addstr(4, 0, f"Current Player {player}, choose a position (1-9): ")
        stdscr.refresh()
        move = stdscr.getkey().strip()
        if move not in map(str, range(1, 10)):
            stdscr.addstr(5, 0, "Invalid input. Enter a number from 1 to 9.")
            stdscr.refresh()
            continue

        idx = int(move) - 1
        if board[idx] != "-":
            stdscr.addstr(5, 0, "That position is already taken. Try again.")
            stdscr.refresh()
            continue

        return idx

def check_winner():
    """Check for a win or tie.
    
    Returns:
        'X' or 'O' if there is a winner,
        'Tie' if the board is full with no winner,
        None if the game should continue.
    """
    win_combinations = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
        (0, 4, 8), (2, 4, 6)              # diagonals
    ]
    
    for a, b, c in win_combinations:
        if board[a] == board[b] == board[c] != "-":
            return board[a]
    
    if "-" not in board:
        return "Tie"
    
    return None

def flip_player(player):
    """Return the opposite player's marker."""
    return "O" if player == "X" else "X"

def main(stdscr):
    global current_player, game_on
    stdscr.clear()
    stdscr.addstr(0, 0, "Welcome to Tic Tac Toe!")
    display_board(stdscr)
    current_player = choose_players(stdscr)
    
    while game_on:
        idx = get_move(stdscr, current_player)
        board[idx] = current_player
        display_board(stdscr)
        
        result = check_winner()
        if result:
            if result == "Tie":
                stdscr.addstr(4, 0, "It's a tie!")
            else:
                stdscr.addstr(4, 0, f"Congratulations {result}, you win!")
            stdscr.refresh()
            stdscr.getch()
            game_on = False
        else:
            current_player = flip_player(current_player)

def play():
    curses.wrapper(play)