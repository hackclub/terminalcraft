# FILEPATH: Untitled-1

# Tic Tac Toe board
board = [' ' for _ in range(9)]

print(board)

# Function to print the board
def print_board():
    print('---------')
    for i in range(3):
        print('|', board[i * 3], '|', board[i * 3 + 1], '|', board[i * 3 + 2], '|')
        print('---------')

# Function to check if the board is full
def is_board_full():
    return ' ' not in board

# Function to check if a player has won
def is_winner(player):
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]              # Diagonals
    ]
    for combination in winning_combinations:
        if board[combination[0]] == board[combination[1]] == board[combination[2]] == player:
            return True
    return False

# Function to make a move
def make_move(position, player):
    board[position] = player

# Function to undo a move
def undo_move(position):
    board[position] = ' '

# Minimax algorithm
def minimax(depth, maximizing_player):
    if is_winner('X'):
        return -1
    if is_winner('O'):
        return 1
    if is_board_full():
        return 0

    if maximizing_player:
        max_eval = float('-inf')
        for i in range(9):
            if board[i] == ' ':
                make_move(i, 'O')
                evaluation = minimax(depth + 1, False)
                undo_move(i)
                max_eval = max(max_eval, evaluation)
        return max_eval
    else:
        min_eval = float('inf')
        for i in range(9):
            if board[i] == ' ':
                make_move(i, 'X')
                evaluation = minimax(depth + 1, True)
                undo_move(i)
                min_eval = min(min_eval, evaluation)
        return min_eval

# Function to find the best move for the AI player
def find_best_move():
    best_eval = float('-inf')
    best_move = -1
    for i in range(9):
        if board[i] == ' ':
            make_move(i, 'O')
            evaluation = minimax(0, False)
            undo_move(i)
            if evaluation > best_eval:
                best_eval = evaluation
                best_move = i
    return best_move

# Main game loop
def run():
    print('Welcome to Tic Tac Toe!')
    print_board()
    while True:
        ai_move = find_best_move()
        make_move(ai_move, 'O')
        print_board()
        if is_winner('O'):
            print('AI wins!')
            break
        if is_board_full():
            print('It\'s a tie!')
            break
        position = int(input('Enter your move (0-8): '))
        if board[position] != ' ':
            print('Invalid move. Try again.')
            continue
        make_move(position, 'X')
        if is_winner('X'):
            print('You win!')
            break
        if is_board_full():
            print('It\'s a tie!')
            break
        

