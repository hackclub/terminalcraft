import random
import os

def print_board(board):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(' 1 | 2 | 3 | 4 | 5 | 6 | 7')
    for row in board:
        print(' | '.join(row))

def is_valid_move(board, column):
    return board[0][column] == ' '

def is_board_full(board):
    return all(cell != ' ' for row in board for cell in row)


def make_move(board, column, player):
    for row in range(5, -1, -1):
        if board[row][column] == ' ':
            board[row][column] = '🔴' if player == 'Player 1' else '🔵'
            break

def check_win(board, player):
    # Check horizontal locations for win
    for row in board:
        for col in range(7 - 3):
            if row[col] == row[col + 1] == row[col + 2] == row[col + 3] == ('🔴' if player == 'Player 1' else '🔵'):
                return True

    # Check vertical locations for win
    for col in range(7):
        for row in range(6 - 3):
            if board[row][col] == board[row + 1][col] == board[row + 2][col] == board[row + 3][col] == ('🔴' if player == 'Player 1' else '🔵'):
                return True

    # Check positive sloped diagonals
    for row in range(6 - 3):
        for col in range(7 - 3):
            if board[row][col] == board[row + 1][col + 1] == board[row + 2][col + 2] == board[row + 3][col + 3] == ('🔴' if player == 'Player 1' else '🔵'):
                return True

    # Check negative sloped diagonals
    for row in range(3, 6):
        for col in range(7 - 3):
            if board[row][col] == board[row - 1][col + 1] == board[row - 2][col + 2] == board[row - 3][col + 3] == ('🔴' if player == 'Player 1' else '🔵'):
                return True

def play_game():
    players = ['Player 1', 'Player 2']
    current_player = random.choice(players)
    other_player = [player for player in players if player != current_player][0]
    points = [0, 0]
    board = [[' ' for _ in range(7)] for _ in range(6)]

    while True:
        print_board(board)
        column = input(f"{current_player}, enter the column number: ")
        while not column.isdigit() or not 1 <= int(column) <= 7 or not is_valid_move(board, int(column) - 1):
            column = input("Invalid input. Please enter a valid column number: ")
        column = int(column) - 1
        make_move(board, column, current_player)
        if check_win(board, current_player):
            print_board(board)
            print(f"{current_player} wins!")
            points[0 if current_player == 'Player 1' else 1] = 3
            break
        if is_board_full(board):
            print_board(board)
            print("It's a draw!")
            points = [1, 1]  # Assign 1 point to each player for a draw
            break
            
        current_player, other_player = other_player, current_player

    return tuple(points)

#points = play_game()
#print(f"Final points: Player 1 - {points[0]}, Player 2 - {points[1]}")
def description():
    print(
'''
This game does the following:

1. Initializes a Connect 4 game board and randomly selects the first player.
2. Prints the game board and asks the current player to enter the column number to drop their piece.
3. Checks if the move is valid and makes the move.
4. Checks if the current player has won.
5. Switches the players and repeats the process until one player wins.
6. Returns a tuple containing the points for each player.''')