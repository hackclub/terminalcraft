import chess
import re
import math
from chessminal import openings as op

def player_info(pgn):
    white_player = re.search(r'\[White\s+"([^"]+)"', pgn)
    black_player = re.search(r'\[Black\s+"([^"]+)"', pgn)
    white_rating = re.search(r'\[WhiteElo\s+"([^"]+)"', pgn)
    black_rating = re.search(r'\[BlackElo\s+"([^"]+)"', pgn)
    white_player = white_player.group(1) if white_player else "White"
    black_player = black_player.group(1) if black_player else "Black"
    white_rating = white_rating.group(1) if white_rating else "??"
    black_rating = black_rating.group(1) if black_rating else "??"

    info = {
        "white_player": white_player,"white_rating":  white_rating,"black_player":  black_player, "black_rating": black_rating
    }
    return info

def isBookMove(fen):
    board = chess.Board()
    board.set_fen(fen)
    fen = board.board_fen()
    for opening in op.openings:
        if (opening['fen']==fen):
            return [True, opening['name']]
    return [False]

def gradeMove(eval_change):
    if (eval_change>=4.5):
        return ("blunder")
    elif (eval_change>=2.6):
        return ("mistake")
    elif (eval_change>=1.3):
        return ("inaccuracy")
    elif (eval_change>=0.8):
        return ("good")
    elif (eval_change>=0.1):
        return ("excellent")
    else:
        return ("best_move")
    
def isBestMove(move_info):
    return (move_info['best_move'] ==  move_info['move'])

def classifyMoves(analysis):
    evalDiffs= [None]
    openings = ["Starting Position"]
    
    for counter in range(1, len(analysis)): 

        current = analysis[counter]
        previous = analysis[counter-1]

        current_type = current['eval']['type']
        previous_type = previous['eval']['type']
    
        book_move = isBookMove(current['fen'])

        if (book_move[0]):
            evalDiffs.append('book_move')
            openings.append(book_move[1])
        else: 
            openings.append(None)
            if (isBestMove(current)):
                evalDiffs.append('best_move')
            elif (current_type=='cp' and previous_type=='cp'):
                resp = cp_and_cp(current, previous)
                evalDiffs.append(resp)
            elif (current_type=='cp' and previous_type=='mate'):
                resp = cp_and_mate(current, previous)
                evalDiffs.append(resp)
            elif (current_type=='mate' and previous_type=='mate'):
                resp = mate_and_mate(current, previous)
                evalDiffs.append(resp)
            elif (current_type=='mate' and previous_type=='cp'):
                resp = mate_and_cp(current, previous)
                evalDiffs.append(resp)

    for counter, (move_type, opening) in enumerate(zip(evalDiffs, openings)):
        analysis[counter]['opening'] = opening
        analysis[counter]['move_type'] = move_type
    analysis = correctBookMoves(analysis)
    return analysis
    
def cp_and_cp(current, previous):
    diff = previous['eval']['value'] - current['eval']['value']
    diff = math.floor(diff*100)/100
    return gradeMove(abs(diff)) 

def cp_and_mate(current, previous):
    current_eval = current['eval']['value']
    if (current_eval >= 20):
        return ("excellent")
    elif (current_eval >= 12):
        return ("good")
    elif (current_eval >= 9):
        return ("inaccuracy")
    elif (current_eval>=6):
        return ("mistake")
    else:
        return ("blunder")    

def mate_and_cp(current, previous):
    previous_eval = previous['eval']['value']
    if (previous_eval >= 30):
        return ("good")
    elif (previous_eval >= 20):
        return ("inaccuracy")
    elif (previous_eval >= 10):
        return ("mistake")
    else:
        return ("blunder")

def mate_and_mate(current, previous):
    current_mate_in = current['eval']['value']
    previous_mate_in = previous['eval']['value']
    player_color = "b" if current['move_no']%2==0 else "w"
    match player_color:
        case "w":
            if (previous_mate_in > 0):
                if (current_mate_in > 0):
                    return ("excellent")
                elif (current_mate_in < 0):
                    return ("blunder")
            elif (previous_mate_in < 0):
                return ("excellent")
        case "b":
            if (previous_mate_in < 0):
                if (current_mate_in < 0):
                    return ("excellent")
                elif (current_mate_in > 0):
                    return ("blunder")
            elif (previous_mate_in > 0):
                return ("excellent")
            
def countMoveCategories(analysedFENs, pgn):
    move_types_b = []
    move_types_w = []
    for FEN in analysedFENs:
        if FEN['move_no']%2==0:
            move_types_b.append(FEN['move_type'])
        else:
            move_types_w.append(FEN['move_type'])
    accuracy = [(move_types_w.count('best_move') + move_types_w.count('best_move') + move_types_w.count('excellent'))/len(move_types_w), (move_types_b.count('best_move') + move_types_b.count('good') + move_types_b.count('excellent'))/(len(move_types_b)-1)]
    analysedFENs = {
        "info": player_info(pgn),
        "accuracy": {
            "white": math.floor(accuracy[0]*100*100)/100,
            "black": math.floor(accuracy[1]*100*100)/100,
        },
        "number_of_move_types": {
                "w":{
                    "best_move" : move_types_w.count('best_move'),
                    "excellent" : move_types_w.count('excellent'),
                    "good" : move_types_w.count('good'),
                    "inaccuracy" : move_types_w.count('inaccuracy'),
                    "mistake" : move_types_w.count('mistake'),
                    "blunder" : move_types_w.count('blunder'),
                    "book_move" : move_types_w.count('book_move'),
                },
                "b": {
                    "best_move" : move_types_b.count('best_move'),
                    "excellent" : move_types_b.count('excellent'),
                    "good" : move_types_b.count('good'),
                    "inaccuracy" : move_types_b.count('inaccuracy'),
                    "mistake" : move_types_b.count('mistake'),
                    "blunder" : move_types_b.count('blunder'),
                    "book_move" : move_types_b.count('book_move'),
                }
            },
        "move_evaluations": analysedFENs
    }
    return analysedFENs

def correctBookMoves(analysis):
    # this is an algorithm to add 'book_move' title to the missed FENs
    # in the openings list, not all FENs are mentioned
    # however if a move leads to a book-move
    # it is also a book move
    # this algo fills up those missing moves and it also makes the subsequent move to have the same opening-name
    opening = []
    
    for position in (analysis):
        # ? this makes a list of lists containg, move_no and opening name
        opening.append([position['move_no'], position['opening']])
    
    opening_reversed = []

    for x in range(len(opening)-1, 0, -1):
        # ! makes a list that is the reversal of the first one, this one doesnt include the starting position though
        opening_reversed.append(opening[x])
    
    index = None
    for move in opening_reversed:
        # * this gets the index of the last book_move
        if (move[1]):
            index = move[0]
            break

    if (index):
        # ? checks if there is any book move and then 
        # ! makes all moves a book move until that move
        for count, position in enumerate(opening):
            if (position[0] <= index and not position[1]):
                position[1] = opening[count-1][1]

    opening[0][1] = None

    for (position, individualOpening) in zip(analysis, opening):
        # this adds the new openings to the analysis and returns that variable
        if (individualOpening[1]):
            position['move_type'] = 'book_move'
            position['opening'] = individualOpening[1]


    for count, move in enumerate(analysis):
        if (not move['opening']):
            move['opening'] = analysis[count-1]['opening']


    return analysis

