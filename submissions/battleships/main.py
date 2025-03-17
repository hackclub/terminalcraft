import random
import os
import time

GRID_SIZE = 10
SHIP_SIZES = [5, 4, 3, 3, 2]

def initialize_grid():
    return [[' ' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

def print_grid(grid):
    print("   A B C D E F G H I J")
    for i in range(GRID_SIZE):
        print(f"{i+1}  " + " ".join(grid[i]) if i < 9 else f"{i+1} " + " ".join(grid[i]))

def is_valid_placement(grid, row, col, size, direction):
    if direction == "right":
        if col + size > GRID_SIZE or any(grid[row][col + i] != ' ' for i in range(size)):
            return False
        if any(col + i - 1 >= 0 and grid[row][col + i - 1] != ' ' for i in range(size)) or \
           any(col + i + 1 < GRID_SIZE and grid[row][col + i + 1] != ' ' for i in range(size)):
            return False
        if (row - 1 >= 0 and any(grid[row - 1][col + i] != ' ' for i in range(size))) or \
           (row + 1 < GRID_SIZE and any(grid[row + 1][col + i] != ' ' for i in range(size))):
            return False
        return True
    elif direction == "left":
        if col - size < -1 or any(grid[row][col - i] != ' ' for i in range(size)):
            return False
        if any(col - i + 1 < GRID_SIZE and grid[row][col - i + 1] != ' ' for i in range(size)) or \
           any(col - i - 1 >= 0 and grid[row][col - i - 1] != ' ' for i in range(size)):
            return False
        if (row - 1 >= 0 and any(grid[row - 1][col - i] != ' ' for i in range(size))) or \
           (row + 1 < GRID_SIZE and any(grid[row + 1][col - i] != ' ' for i in range(size))):
            return False
        return True
    elif direction == "down":
        if row + size > GRID_SIZE or any(grid[row + i][col] != ' ' for i in range(size)):
            return False
        if any(col - 1 >= 0 and grid[row + i][col - 1] != ' ' for i in range(size)) or \
           any(col + 1 < GRID_SIZE and grid[row + i][col + 1] != ' ' for i in range(size)):
            return False
        if (row - 1 >= 0 and any(grid[row - 1][col] != ' ' for i in range(size))) or \
           (row + size < GRID_SIZE and any(grid[row + size][col] != ' ' for i in range(size))):
            return False
        return True
    elif direction == "up":
        if row - size < -1 or any(grid[row - i][col] != ' ' for i in range(size)):
            return False
        if any(col - 1 >= 0 and grid[row - i][col - 1] != ' ' for i in range(size)) or \
           any(col + 1 < GRID_SIZE and grid[row - i][col + 1] != ' ' for i in range(size)):
            return False
        if (row + 1 < GRID_SIZE and any(grid[row + 1][col] != ' ' for i in range(size))) or \
           (row - size >= 0 and any(grid[row - size][col] != ' ' for i in range(size))):
            return False
        return True
    return False

def place_ship(grid, size, manual=False):
    placed = False
    while not placed:
        if manual:
            valid_coords = True
            while valid_coords:
                try:
                    print(f"Placing ship of size {size}.")
                    start_pos = input("Enter the starting position of your ship: ").strip().upper()
                    direction = input("Enter the direction (up, down, left, right): ").strip().lower()
                    clear_screen()
                    col = ord(start_pos[0]) - 65
                    row = int(start_pos[1:]) - 1
                    valid_coords = False
                except (IndexError, ValueError):
                    print("Invalid starting coordinate. Please try again.")
        else:
            direction = random.choice(["up", "down", "left", "right"])
            start_pos = f"{chr(random.randint(65, 74))}{random.randint(1, 10)}"
            col = ord(start_pos[0]) - 65
            row = int(start_pos[1:]) - 1

        if is_valid_placement(grid, row, col, size, direction):
            if direction == "right":
                for i in range(size):
                    grid[row][col + i] = '-'
            elif direction == "left":
                for i in range(size):
                    grid[row][col - i] = '-'
            elif direction == "down":
                for i in range(size):
                    grid[row + i][col] = '|'
            elif direction == "up":
                for i in range(size):
                    grid[row - i][col] = '|'
            placed = True
        else:
            print("\nInvalid placement. Ensure there's at least one empty field between ships.")
        print("\nYour current Board: \n")
        print_grid(player_board)

def shoot(grid, row, col):
    if grid[row][col] == '-' or grid[row][col] == '|':
        grid[row][col] = '*'
        return True
    elif grid[row][col] == ' ':
        grid[row][col] = 'o'
        return False
    return None

def all_ships_sunk(grid):
    return all(cell not in ('-', '|') for row in grid for cell in row)

def get_user_shot():
    while True:
        try:
            shot = input("Enter your shot: ").strip().upper()
            col = ord(shot[0]) - 65
            row = int(shot[1:]) - 1
            if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                return row, col, shot
            else:
                print("Invalid shot. Please try again.")
        except (IndexError, ValueError):
            print("Invalid shot. Please try again.")

def opponent_shot():
    while True:
        row, col = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
        if opponent_board[row][col] == ' ':
            return row, col

def print_boards():
    print("\nYour Board: \n")
    print_grid(player_board)
    print("\nOpponent's Board: \n")
    print_grid(opponent_board_visible)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

player_board = initialize_grid()
opponent_board = initialize_grid()
opponent_board_visible = initialize_grid()

clear_screen()

manual_placement = input("Do you want to place your ships manually? (y/n): ").strip().lower() == 'y'

for ship_size in SHIP_SIZES:
    place_ship(player_board, ship_size, manual=manual_placement)

for ship_size in SHIP_SIZES:
    place_ship(opponent_board, ship_size, manual=False)

game_over = False
while not game_over:
    clear_screen()
    print_boards()

    print("\nYour turn!")
    row, col, shot = get_user_shot()

    clear_screen()
    print(f"You shot at {shot}.")
    if shoot(opponent_board, row, col):
        print("Your shot hit!")
        opponent_board_visible[row][col] = '*'
    else:
        print("Your shot missed!")
        opponent_board_visible[row][col] = 'o'

    if all_ships_sunk(opponent_board):
        print("\nYou win! All opponent ships are sunk.")
        game_over = True
        break

    time.sleep(0.2)
    print("\nThe opponent is thinking...")
    time.sleep(1)

    row, col = opponent_shot()
    print(f"Opponent shots at {chr(col + 65)}{row + 1}.")
    if shoot(player_board, row, col):
        print("Opponent's shot hit!")
    else:
        print("Opponent's shot missed!")

    if all_ships_sunk(player_board):
        print("\nThe opponent wins! All your ships are sunk.")
        game_over = True
        break

    input("\nEnter to continue: ")
    clear_screen()
