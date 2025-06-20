from contextlib import redirect_stdout, redirect_stderr
import io
import chess
import chess.pgn


# the below function is used to check if the PGN format is correct or not
def checkPGNFormat(pgn):
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        try:
            game = chess.pgn.read_game(io.StringIO(pgn))
        except Exception as e:
            pass
    console_output = output.getvalue().lower()
    if "illegal san:" in console_output or "illegal move" in console_output:
        return False
    else:
        game = chess.pgn.read_game(io.StringIO(pgn))
        gameString = str(game)
        if game is None:
            return False
        elif "1." not in gameString:
            return False
    return True


# the below function is used to check if the moves are legal or not
def validatePGN(pgn):
    if not checkPGNFormat(pgn):
        return False
    game = chess.pgn.read_game(io.StringIO(pgn))
    board = chess.Board()
    for move in game.mainline_moves():
        if board.is_legal(move):
            board.push(move)
        else:
            return False
    return True  

