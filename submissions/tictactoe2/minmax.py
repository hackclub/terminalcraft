import copy
from game_logic import check_draw_board, check_win, has_valid_moves

def evaluate_state(big_board, win_board, player, opponent):
    score = 0

    for i in range(3):
        for j in range(3):
            mini_board = big_board[i][j]
            if win_board[i * 3 + j] == player:
                score += 200
            elif win_board[i * 3 + j] == opponent:
                score -= 200
            elif win_board[i * 3 + j] == "D":
                score += 40
            else: # considers potential wins
                for row in mini_board:
                    if row.count(player) == 2 and row.count(" ") == 1:
                        score += 10
                    elif row.count(opponent) == 2 and row.count(" ") == 1:
                        score -= 10
                for col in range(3):
                    col_values = [mini_board[row][col] for row in range(3)]
                    if col_values.count(player) == 2 and col_values.count(" ") == 1:
                        score += 10
                    elif col_values.count(opponent) == 2 and col_values.count(" ") == 1:
                        score -= 10
                
                main_diag_values = [mini_board[k][k] for k in range(3)]
                if main_diag_values.count(player) == 2 and main_diag_values.count(" ") == 1:
                    score += 10
                elif main_diag_values.count(opponent) == 2 and main_diag_values.count(" ") == 1:
                    score -= 10
                
                opposite_diag_values = [mini_board[k][2 - k] for k in range(3)]
                if opposite_diag_values.count(player) == 2 and opposite_diag_values.count(" ") == 1:
                    score += 10
                elif opposite_diag_values.count(opponent) == 2 and opposite_diag_values.count(" ") == 1:
                    score -= 10

    # check the whole board
    win_board_list = [win_board[0:3], win_board[3:6], win_board[6:9]]
    for row in win_board_list:
        if row.count(player) == 2 and row.count(" ") == 1:
            score += 50
        elif row.count(opponent) == 2 and row.count(" ") == 1:
            score -= 50

    for col in range(3):
        col_values = [win_board_list[row][col] for row in range(3)]
        if col_values.count(player) == 2 and col_values.count(" ") == 1:
            score += 50
        elif col_values.count(opponent) == 2 and col_values.count(" ") == 1:
            score -= 50

    main_diag_values = [win_board_list[k][k] for k in range(3)]
    if main_diag_values.count(player) == 2 and main_diag_values.count(" ") == 1:
        score += 50
    elif main_diag_values.count(opponent) == 2 and main_diag_values.count(" ") == 1:
        score -= 50

    opposite_diag_values = [win_board_list[k][2 - k] for k in range(3)]
    if opposite_diag_values.count(player) == 2 and opposite_diag_values.count(" ") == 1:
        score += 50
    elif opposite_diag_values.count(opponent) == 2 and opposite_diag_values.count(" ") == 1:
        score -= 50
    
    winner = check_win(win_board_list)
    if winner == player:
        score += 10000
    elif winner == opponent:
        score -= 10000

    return score

def game_over(big_board, win_board):
    if check_win([win_board[0:3], win_board[3:6], win_board[6:9]]):
        return True
    
    for row in big_board:
        for board in row:
            if has_valid_moves(board):
                return False

    return True

def get_legal_moves(big_board, win_board, current_board):
    """
    `move` is a tuple (big_row, big_col, mini_row, mini_col).
    """
    legal_moves = []
    if current_board is not None and win_board[current_board] == " ":
        big_row = current_board // 3
        big_col = current_board % 3
        for mini_row in range(3):
            for mini_col in range(3):
                if big_board[big_row][big_col][mini_row][mini_col] == " ":
                    legal_moves.append((big_row, big_col, mini_row, mini_col))
    else:
        for big_row in range(3):
            for big_col in range(3):
                if win_board[big_row * 3 + big_col] == " ":
                    for mini_row in range(3):
                        for mini_col in range(3):
                            if big_board[big_row][big_col][mini_row][mini_col] == " ":
                                legal_moves.append((big_row, big_col, mini_row, mini_col))

    return legal_moves

def simulate_move(big_board, win_board, current_board, move, player):
    """
    Return new board states after applying a move.
    Make copies of old boards.
    """
    new_big_board = copy.deepcopy(big_board)
    new_win_board = win_board[:]  # shallow copy since board elements are primitives
    big_row, big_col, mini_row, mini_col = move
    new_big_board[big_row][big_col][mini_row][mini_col] = player

    next_active = mini_row * 3 + mini_col
    winner = check_win(new_big_board[big_row][big_col])
    if winner:
        new_win_board[big_row * 3 + big_col] = winner
        next_active = None
    elif check_draw_board(new_big_board[big_row][big_col]):
        new_win_board[big_row * 3 + big_col] = "D"
        next_active = None

    return new_big_board, new_win_board, next_active

def minimax(big_board, win_board, current_board, depth, alpha, beta, maximizing, player, opponent):
    if depth == 0 or game_over(big_board, win_board):
        return evaluate_state(big_board, win_board, player, opponent)
    
    legal_moves = get_legal_moves(big_board, win_board, current_board)
    
    if maximizing:
        max_eval = float('-inf')
        best_move = None
        for move in legal_moves:
            new_big_board, new_win_board, next_board = simulate_move(big_board, win_board, current_board, move, player)
            eval = minimax(new_big_board, new_win_board, next_board, depth - 1, alpha, beta, False, player, opponent)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        if depth == MAX_DEPTH:
            return best_move, max_eval
        return max_eval
    else:
        min_eval = float('inf')
        for move in legal_moves:
            new_big_board, new_win_board, next_board = simulate_move(big_board, win_board, current_board, move, opponent)
            eval = minimax(new_big_board, new_win_board, next_board, depth - 1, alpha, beta, True, player, opponent)
            if eval < min_eval:
                min_eval = eval
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

MAX_DEPTH = 5

def get_computer_move(big_board, win_board, current_board, computer_player, human_player):
    if win_board[current_board] != " ":
        current_board = None
    move, score = minimax(big_board, win_board, current_board, MAX_DEPTH, float('-inf'), float('inf'), True, computer_player, human_player)
    return move