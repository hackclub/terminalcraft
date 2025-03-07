import chess
import io
import requests
from chessminal.classify_moves import countMoveCategories, classifyMoves


def changeFormat(pgn, infos, moves):
    game = chess.pgn.read_game(io.StringIO(pgn))
    board = game.board()
    default_fen = board.fen()
    for counter, (info, move) in enumerate(zip(infos, moves)):

        if (info['eval']['type']!='mate'):
            info['eval']['value']/=100
        if (not info['best_move']):
            info['best_move'] = (None)
        else:
            board.set_fen(infos[counter-1]['fen'])
            info['best_move'] = (board.san(chess.Move.from_uci(info['best_move'])))
            board.set_fen(default_fen)    
        info['move'] = move
    return infos

def review_game (pgn):
    game = chess.pgn.read_game(io.StringIO(pgn))
    board = game.board()
    moves = game.mainline_moves()
    moves_fens = [board.fen()]
    moves_san = [None]

    for move in moves:
        moves_san.append(board.san_and_push(move))
        moves_fens.append(board.fen())


    url="https://daamin.hackclub.app/api/engine"
    payload = {"fens": moves_fens}  
    response = requests.post(url, json=payload)
    analysis = response.json()
    analysis = changeFormat(pgn, analysis, moves_san)
    analysis = classifyMoves(analysis)
    analysis = countMoveCategories(analysis, pgn)
    return analysis
