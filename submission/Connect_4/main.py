board = [
    ["", "", "", "", "", "", ""],
    ["", "", "", "", "", "", ""],
    ["", "", "", "", "", "", ""],
    ["", "", "", "", "", "", ""],
    ["", "", "", "", "", "", ""],
    ["", "", "", "", "", "", ""],
]

def print_board(board):
    for row in board:
        for col in row:
            if col == "":
                print("_", end=" ")
            else:
                print(col, end=" ")
        print()

def is_valid_move(board, col):
    return board[0][col] == ""

def get_next_empty_row(board, col):
    """Finds the lowest empty row in a column"""
    for row in range(len(board) - 1, -1, -1):
        if board[row][col] == "":
            return row
    return None

def make_move(board, col, player):
    row = get_next_empty_row(board, col)
    if row is not None:
        board[row][col] = player

def undo_move(board, col, row):
    board[row][col] = ""

def is_winner(board, player):
    # Check horizontal
    for row in board:
        for col in range(len(row) - 3):
            if row[col] == player and row[col + 1] == player and row[col + 2] == player and row[col + 3] == player:
                return True

    # Check vertical
    for col in range(len(board[0])):
        for row in range(len(board) - 3):
            if board[row][col] == player and board[row + 1][col] == player and board[row + 2][col] == player and board[row + 3][col] == player:
                return True

    # Check diagonal (positive slope)
    for col in range(len(board[0]) - 3):
        for row in range(len(board) - 3):
            if board[row][col] == player and board[row + 1][col + 1] == player and board[row + 2][col + 2] == player and board[row + 3][col + 3] == player:
                return True

    # Check diagonal (negative slope)
    for col in range(3, len(board[0])):
        for row in range(len(board) - 3):
            if board[row][col] == player and board[row + 1][col - 1] == player and board[row + 2][col - 2] == player and board[row + 3][col - 3] == player:
                return True

    return False

def is_board_full(board):
    for row in board:
        if any(cell == "" for cell in row):
            return False
    return True

def minimax(depth, maximizing_player):
    global board
    if is_winner(board, 'X'):
        return -1
    if is_winner(board, 'O'):
        return 1
    if is_board_full(board):
        return 0

    if depth == 10:
        return 0
    
    if maximizing_player:
        max_eval = float('-inf')
        for i in range(7):
            row = get_next_empty_row(board, i)
            if row != None:
                if board[row][i] == "":
                    make_move(board, i, "O")
                    evaluation = minimax(depth + 1, False)
                    undo_move(board, i, row)
                    max_eval = max(max_eval, evaluation)
        return max_eval
    else:
        min_eval = float('inf')
        for i in range(7):
            row = get_next_empty_row(board, i)
            if row != None:
                if board[row][i] == "":
                    make_move(board, i, "O")
                    evaluation = minimax(depth + 1, True)
                    undo_move(board, i, row)
                    min_eval = min(min_eval, evaluation)
        return min_eval

def find_best_move():
    best_eval = float('-inf')
    best_move = -1
    for i in range(7):
        row = get_next_empty_row(board, i)
        if board[row][i] == "":
            make_move(board, i, "O" 'O')
            evaluation = minimax(0, False)
            undo_move(board, i, row)
            if evaluation > best_eval:
                best_eval = evaluation
                best_move = i
    return best_move

def run():
    global board
    current_player = "X"
    while True:
        print_board(board)
        if current_player == "X":
            col_str = input(f"{current_player}'s turn. Choose a column (1-7): ")
            try:
                col = int(col_str) - 1
                if 0 <= col <= 6 and is_valid_move(board, col):
                    make_move(board, col, current_player)
                    if is_winner(board, current_player):
                        print_board(board)
                        print(f"{current_player} wins!")
                        break
                    elif is_board_full(board):
                        print_board(board)
                        print("It's a tie!")
                        break
                    current_player = "O" if current_player == "X" else "X"
                else:
                    print("Invalid column. Please choose a number between 1 and 7.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        else:
            col = find_best_move()
            make_move(board, col, current_player)
            if is_winner(board, current_player):
                print_board(board)
                print(f"{current_player} wins!")
                break
            elif is_board_full(board):
                print_board(board)
                print("It's a tie!")
                break
            current_player = "O" if current_player == "X" else "X"
