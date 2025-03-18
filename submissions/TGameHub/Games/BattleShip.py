import curses
import random

BOARD_SIZE = 5
SHIPS = 3

def init_board():
    return [["~" for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def place_ships(board):
    placed = 0
    while placed < SHIPS:
        x, y = random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1)
        if board[y][x] == "~":
            board[y][x] = "S"
            placed += 1

def draw_board(stdscr, player_board, hit_board, cursor):
    stdscr.clear()
    try:
        height, width = stdscr.getmaxyx()
        if height < BOARD_SIZE + 10 or width < BOARD_SIZE * 4:
            raise ValueError("Window too small")
        stdscr.addstr("Your Board:\n")
        for row in player_board:
            stdscr.addstr(" ".join(row) + "\n")
        
        stdscr.addstr("\nTarget Board:\n")
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                char = hit_board[y][x] if hit_board[y][x] in ("X", "O") else "~"
                if (y, x) == cursor:
                    stdscr.addstr(f"[{char}] ")
                else:
                    stdscr.addstr(f" {char}  ")
            stdscr.addstr("\n")
        
        stdscr.addstr("\nUse arrow keys to move, Enter to fire.\n")
    except ValueError as e:
        stdscr.clear()
        stdscr.addstr(0, 0, str(e))
        stdscr.addstr(1, 0, "Please resize the window, ignore the error and rerun main.py.")
    stdscr.refresh()

def player_turn(stdscr, hit_board, ai_board):
    cursor = [0, 0]
    while True:
        draw_board(stdscr, player_board, hit_board, tuple(cursor))
        key = stdscr.getch()
        if key == curses.KEY_UP and cursor[0] > 0:
            cursor[0] -= 1
        elif key == curses.KEY_DOWN and cursor[0] < BOARD_SIZE - 1:
            cursor[0] += 1
        elif key == curses.KEY_LEFT and cursor[1] > 0:
            cursor[1] -= 1
        elif key == curses.KEY_RIGHT and cursor[1] < BOARD_SIZE - 1:
            cursor[1] += 1
        elif key == 10:  # Enter key
            y, x = cursor
            if hit_board[y][x] == "~":
                hit_board[y][x] = "X" if ai_board[y][x] == "S" else "O"
                break

def ai_turn(player_board):
    while True:
        y, x = random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1)
        if player_board[y][x] not in ("X", "O"):
            player_board[y][x] = "X" if player_board[y][x] == "S" else "O"
            break

def check_win(board):
    return all(cell != "S" for row in board for cell in row)

def game(stdscr):
    global player_board
    curses.curs_set(0)
    stdscr.clear()
    
    player_board = init_board()
    ai_board = init_board()
    hit_board = init_board()
    
    place_ships(player_board)
    place_ships(ai_board)
    
    while True:
        player_turn(stdscr, hit_board, ai_board)
        if check_win(ai_board):
            stdscr.addstr("\nYou win! Press any key to exit.\n")
            stdscr.getch()
            break
        
        ai_turn(player_board)
        if check_win(player_board):
            stdscr.addstr("\nAI wins! Press any key to exit.\n")
            stdscr.getch()
            break

def play():
    curses.wrapper(game)

if __name__ == "__main__":
    play()