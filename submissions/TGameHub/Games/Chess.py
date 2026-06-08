import curses
import chess

def init_curses():
    """Initialize curses settings."""
    curses.initscr()
    curses.start_color()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)  # Hide cursor
    win = curses.newwin(20, 40, 0, 0)
    win.keypad(True)

    # Define colors
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # White pieces
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Black pieces
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Highlighted selection
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Cursor position
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)    # King in check

    return win

def draw_board(win, board, cursor_pos, selected_square, message=""):
    """Render the chess board in curses with color."""
    win.clear()
    king_square = None

    if board.is_check():
        king_square = board.king(board.turn)  # Get king's position

    for rank in range(8):
        for file in range(8):
            square = chess.square(file, 7 - rank)
            piece = board.piece_at(square)
            char = piece.symbol() if piece else "."

            # Choose default color
            color = curses.color_pair(1) if piece and piece.color == chess.WHITE else curses.color_pair(2)

            # Highlight king if in check
            if square == king_square:
                color = curses.color_pair(5) | curses.A_BOLD

            # Highlight selected piece
            if selected_square == square:
                win.addstr(rank + 1, file * 4 + 2, char, curses.color_pair(3) | curses.A_BOLD)
            # Highlight cursor position
            elif (file, rank) == cursor_pos:
                win.addstr(rank + 1, file * 4 + 2, char, curses.color_pair(4) | curses.A_BOLD)
            else:
                win.addstr(rank + 1, file * 4 + 2, char, color)

    win.addstr(10, 2, "Use arrow keys to move, Enter to select/move", curses.A_DIM)
    win.addstr(12, 2, message, curses.A_BOLD if message else curses.A_DIM)
    win.refresh()

def main(win):
    board = chess.Board()
    cursor_pos = (0, 7)  # Start cursor at a8
    selected_square = None
    message = ""

    draw_board(win, board, cursor_pos, selected_square, message)

    while not board.is_game_over():
        key = win.getch()

        if key == curses.KEY_UP:
            cursor_pos = (cursor_pos[0], max(0, cursor_pos[1] - 1))
        elif key == curses.KEY_DOWN:
            cursor_pos = (cursor_pos[0], min(7, cursor_pos[1] + 1))
        elif key == curses.KEY_LEFT:
            cursor_pos = (max(0, cursor_pos[0] - 1), cursor_pos[1])
        elif key == curses.KEY_RIGHT:
            cursor_pos = (min(7, cursor_pos[0] + 1), cursor_pos[1])
        elif key == 10:  # Enter key
            square = chess.square(cursor_pos[0], 7 - cursor_pos[1])

            if selected_square is None:
                if board.piece_at(square) and (board.turn == board.piece_at(square).color):
                    selected_square = square  # Select piece
                    message = "Piece selected!"
                else:
                    message = "Invalid selection!"
            else:
                move = chess.Move(selected_square, square)
                if move in board.legal_moves:
                    board.push(move)
                    message = "Move played!"
                    selected_square = None  # Reset selection
                else:
                    message = "Illegal move! Try again."

        draw_board(win, board, cursor_pos, selected_square, message)

    win.addstr(14, 10, "Game Over!", curses.A_BOLD)
    win.getch()

def play():
    curses.wrapper(main)