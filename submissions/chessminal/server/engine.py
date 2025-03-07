from stockfish import Stockfish


def getEngineAnalysis(FENs):
    stockfish = Stockfish(path="/usr/games/stockfish", depth=8, parameters={"Threads": 1, "Minimum Thinking Time": 1, "Hash": 32, "Slow Mover": 1})
    response = []
    for count, FEN in enumerate(FENs):
        if (count == 0):
            bestmove = False
        else:
            stockfish.set_fen_position(FENs[count-1])
            bestmove = stockfish.get_best_move()   

        stockfish.set_fen_position(FEN)
        eval = stockfish.get_evaluation()
        compiled = {'move_no': count, 'fen': FEN, 'best_move': bestmove, 'eval': eval}
        response.append(compiled)

    return response