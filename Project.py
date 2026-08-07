import random
import os
import time
import sys
import json
from sys import platform
from datetime import datetime
COLORS = {
    "X": "\033[91m",       
    "O": "\033[94m",       
    "board": "\033[97m",   
    "highlight": "\033[103m\033[30m",  
    "title": "\033[95m",   
    "winner": "\033[92m",  
    "error": "\033[91m",   
    "prompt": "\033[96m",  
    "reset": "\033[0m",
    "cell_bg": "\033[100m", 
    "coder": "\033[93m",    
    "history": "\033[35m"   
}

HISTORY_FILE = "tic_tac_toe_history.json"
BOARD = {
    "top":    "╔═══╦═══╦═══╗",
    "middle": "╠═══╬═══╬═══╣",
    "bottom": "╚═══╩═══╩═══╝",
    "side":   "║",
    "space":  "   ",
    "fill":   " ",
}

SOUNDS = {
    "move": (1000, 100),
    "win": (2000, 500),
    "error": (300, 500),
    "draw": (500, 300)
}

def play_sound(sound_type):
    """Play system sound effects"""
    if sound_type in SOUNDS:
        freq, duration = SOUNDS[sound_type]
        if platform == "win32":
            import winsound
            winsound.Beep(freq, duration)
        else:
            sys.stdout.write('\a')
            sys.stdout.flush()

def animate_title():
    """Enhanced animated title screen"""
    os.system("cls" if os.name == "nt" else "clear")
    title = rf"""
{COLORS['coder']}
                    _   _      _ _        _    _            _    
                    | | | | ___| | | ___  / \  | | ___ _ __ | |_  
                    | |_| |/ _ \ | |/ _ \/ _ \ | |/ _ \ '_ \| __| 
                    |  _  |  __/ | |  __/ ___ \| |  __/ | | | |_  
                    |_| |_|\___|_|_|\___/_/   \_\_|\___|_| |_|\__| 

         ████████╗██╗ ██████╗    ████████╗ █████╗  ██████╗    ████████╗ ██████╗ ███████╗
         ╚══██╔══╝██║██╔════╝    ╚══██╔══╝██╔══██╗██╔════╝    ╚══██╔══╝██╔═══██╗██╔════╝
            ██║   ██║██║            ██║   ███████║██║            ██║   ██║   ██║█████╗  
            ██║   ██║██║            ██║   ██╔══██║██║            ██║   ██║   ██║██╔══╝  
            ██║   ██║╚██████╗       ██║   ██║  ██║╚██████╗       ██║   ╚██████╔╝███████╗  
            ╚═╝   ╚═╝ ╚═════╝       ╚═╝   ╚═╝  ╚═╝ ╚═════╝       ╚═╝    ╚═════╝ ╚══════╝

                                            ██╗  ██╗███████╗███████╗███████╗
                                            ██║  ██║██╔════╝██╔════╝██╔════╝
                                            ███████║█████╗  █████╗  ███████╗
                                            ██╔══██║██╔══╝  ██╔══╝  ╚════██║
                                            ██║  ██║███████╗███████╗███████║
                                            ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝ 

{COLORS['title']}
                ╔╦╗╔═╗╔═╗   ╔═╗╔═╗╔═╗╔═╗╔═╗╔═╗╔═╗
                ║║║║ ║║ ║   ║ ║║ ║║╔╝║ ║║ ║║║║║╣ 
                ╩ ╩╚═╝╚═╝   ╚═╝╚═╝╚╝ ╚═╝╚═╝╝╚╝╚═╝
{COLORS['reset']}
"""
    creator = "Created by: Sandesh Kadel and Sandip Joshi"
    
    colors = [COLORS['title'], COLORS['X'], COLORS['O'], COLORS['coder']]
    for i in range(5): 
        print(f"{colors[i%4]}{title}{COLORS['reset']}")
        print(f"{' '*25}{colors[(i+1)%4]}{creator}{COLORS['reset']}")
        time.sleep(0.5)
        if i < 4:
            os.system("cls" if os.name == "nt" else "clear")
    
    time.sleep(0.5)
    os.system("cls" if os.name == "nt" else "clear")

def draw_board(board, winning_line=None):
    """Draw the enhanced game board with colors"""
    os.system("cls" if os.name == "nt" else "clear")
    print(f"\n{COLORS['board']}      0   1   2  {COLORS['reset']}")
    print(f"    {BOARD['top']}")
    
    for row_idx, row in enumerate(board):
        line = []
        for col_idx, cell in enumerate(row):
            cell_bg = COLORS['cell_bg'] if (row_idx + col_idx) % 2 == 0 else ""
            cell_color = COLORS[cell] if cell in ("X", "O") else COLORS['board']
            
            if winning_line and (row_idx, col_idx) in winning_line:
                cell_display = f"{COLORS['highlight']} {cell} {COLORS['reset']}"
            else:
                cell_display = f"{cell_bg} {cell if cell != ' ' else ' '} {COLORS['reset']}"
            
            line.append(f"{cell_color}{cell_display}{COLORS['reset']}")
        
        print(f"  {row_idx} {COLORS['board']}{BOARD['side']}{COLORS['reset']}" + 
              f"{COLORS['board']}{BOARD['side']}{COLORS['reset']}".join(line) + 
              f" {COLORS['board']}{BOARD['side']}{COLORS['reset']}")
        
        if row_idx < 2:
            print(f"    {BOARD['middle']}")
    
    print(f"    {BOARD['bottom']}\n")

def get_player_names(game_mode):
    """Get player names with input validation"""
    names = {}
    while True:
        try:
            if game_mode == "1":
                names["X"] = input(f"{COLORS['X']}✖ Player 1 Name (X): {COLORS['reset']}").strip() or "Player 1"
                names["O"] = input(f"{COLORS['O']}◯ Player 2 Name (O): {COLORS['reset']}").strip() or "Player 2"
            else:
                names["X"] = input(f"{COLORS['X']}✖ Your Name: {COLORS['reset']}").strip() or "Player"
                names["O"] = "AI"
            return names
        except KeyboardInterrupt:
            sys.exit()
        except:
            print(f"{COLORS['error']}Invalid input! Please try again.{COLORS['reset']}")

def validate_move(move, board):
    """Validate player input with detailed error messages"""
    try:
        if move.lower() == "help":
            print(f"\n{COLORS['prompt']}Enter your move as 'row,col' (0-2). Example: '1,2'")
            print("Available moves:")
            for i in range(3):
                for j in range(3):
                    if board[i][j] == " ":
                        print(f" - {i},{j}")
            return None
        if move.lower() == "exit":
            sys.exit()
            
        row, col = map(int, move.split(","))
        if not (0 <= row <= 2 and 0 <= col <= 2):
            raise ValueError
        if board[row][col] != " ":
            return "occupied"
        return (row, col)
    except ValueError:
        print(f"{COLORS['error']}Invalid format! {COLORS['prompt']}Use 'row,col' (0-2). Example: '0,1' or type 'help'{COLORS['reset']}")
        return "invalid"
    except:
        return "error"

def get_winning_line(board, player):
    """Find the winning line for the given player"""
    winning_lines = [
        [(0, 0), (0, 1), (0, 2)],
        [(1, 0), (1, 1), (1, 2)],
        [(2, 0), (2, 1), (2, 2)],
        [(0, 0), (1, 0), (2, 0)],
        [(0, 1), (1, 1), (2, 1)],
        [(0, 2), (1, 2), (2, 2)],
        [(0, 0), (1, 1), (2, 2)],
        [(0, 2), (1, 1), (2, 0)]
    ]
    
    for line in winning_lines:
        if all(board[i][j] == player for (i, j) in line):
            return line
    return None

def show_victory_message(player, names):
    """Display a victory message for the winning player"""
    print(f"\n{COLORS['winner']}🎉 {names[player]} wins! 🎉{COLORS['reset']}")
    time.sleep(1)

def check_winner(board, player):
    """Check if the player has won"""
    for line in [
        [(0, 0), (0, 1), (0, 2)],
        [(1, 0), (1, 1), (1, 2)],
        [(2, 0), (2, 1), (2, 2)],
        [(0, 0), (1, 0), (2, 0)],
        [(0, 1), (1, 1), (2, 1)],
        [(0, 2), (1, 2), (2, 2)],
        [(0, 0), (1, 1), (2, 2)],
        [(0, 2), (1, 1), (2, 0)]
    ]:
        if all(board[i][j] == player for (i, j) in line):
            return True
    return False

def is_draw(board):
    """Check if the game is a draw"""
    return all(cell != " " for row in board for cell in row)

def optimal_move(board, player):
    """Find optimal move using minimax with alpha-beta pruning"""
    opponent = "O" if player == "X" else "X"
    best_score = -float('inf')
    best_move = None
    
    for i, j in [(i, j) for i in range(3) for j in range(3) if board[i][j] == " "]:
        board[i][j] = player
        if check_winner(board, player):
            board[i][j] = " "
            return (i, j)
        board[i][j] = " "

    for i, j in [(i, j) for i in range(3) for j in range(3) if board[i][j] == " "]:
        board[i][j] = opponent
        if check_winner(board, opponent):
            board[i][j] = " "
            return (i, j)
        board[i][j] = " "
    
    for i, j in [(i, j) for i in range(3) for j in range(3) if board[i][j] == " "]:
        board[i][j] = player
        score = minimax(board, False, player, opponent)
        board[i][j] = " "
        if score > best_score:
            best_score = score
            best_move = (i, j)
    
    return best_move

def minimax(board, is_maximizing, player, opponent, alpha=-float('inf'), beta=float('inf')):
    """Optimized minimax algorithm with alpha-beta pruning"""
    if check_winner(board, player):
        return 1
    if check_winner(board, opponent):
        return -1
    if is_draw(board):
        return 0

    if is_maximizing:
        max_eval = -float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = player
                    current_eval = minimax(board, False, player, opponent, alpha, beta)
                    board[i][j] = " "
                    max_eval = max(max_eval, current_eval)
                    alpha = max(alpha, current_eval)
                    if beta <= alpha:
                        break
        return max_eval
    else:
        min_eval = float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j] == " ":
                    board[i][j] = opponent
                    current_eval = minimax(board, True, player, opponent, alpha, beta)
                    board[i][j] = " "
                    min_eval = min(min_eval, current_eval)
                    beta = min(beta, current_eval)
                    if beta <= alpha:
                        break
        return min_eval

def enhanced_ai_move(board, difficulty, player):
    """Enhanced AI with opening book and difficulty levels"""
    empty_cells = [(i, j) for i in range(3) for j in range(3) if board[i][j] == " "]

    if difficulty == "easy":
        if random.random() < 0.7:
            return random.choice(empty_cells)
    elif difficulty == "medium":
        if random.random() < 0.4:
            return random.choice(empty_cells)

    if board[1][1] == " ":
        return (1, 1)
    
    corners = [(0,0), (0,2), (2,0), (2,2)]
    random.shuffle(corners)
    for corner in corners:
        if board[corner[0]][corner[1]] == " ":
            return corner
    
    return optimal_move(board, player)

def save_game_history(game_data):
    """Save game history to JSON file"""
    try:
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        history.append(game_data)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"{COLORS['error']}Error saving history: {e}{COLORS['reset']}")

def show_game_history():
    """Display game history with styling"""
    if not os.path.exists(HISTORY_FILE):
        print(f"{COLORS['error']}No game history found!{COLORS['reset']}")
        return
    
    try:
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
        
        print(f"\n{COLORS['history']}╔{'═'*78}╗")
        print(f"║{'GAME HISTORY':^78}║")
        print(f"╠{'═'*78}╣")
        
        for idx, game in enumerate(reversed(history[-10:]), 1): 
            print(f"║ {COLORS['history']}Game {idx}:")
            print(f"║   Players: {game['player_x']} (X) vs {game['player_o']} (O)")
            print(f"║   Date: {game['date']}")
            print(f"║   Result: {game['result']}")
            print(f"║   Moves: {' → '.join(game['moves'])}")
            print(f"║   Duration: {game['duration']}")
            print(f"╟{'─'*78}╢") if idx < len(history) else None
        print(f"╚{'═'*78}╝{COLORS['reset']}")
        
    except Exception as e:
        print(f"{COLORS['error']}Error loading history: {e}{COLORS['reset']}")

def game_loop(names, difficulty, game_mode):
    """Enhanced game loop with history tracking"""
    scores = {names["X"]: 0, names["O"]: 0}
    
    while True:
        board = [[" " for _ in range(3)] for _ in range(3)]
        current_player = "X"
        winning_line = None
        moves = []
        start_time = datetime.now()
        
        while True:
            draw_board(board)
            print(f"{COLORS['title']}Score: {names['X']}: {scores[names['X']]} | "
                  f"{names['O']}: {scores[names['O']]}{COLORS['reset']}")

            if game_mode == "2" and current_player == "O":
                row, col = enhanced_ai_move(board, difficulty, current_player)
                print(f"{COLORS['O']}{names['O']} chooses: {row},{col}{COLORS['reset']}")
                time.sleep(0.5)
            else:
                move = input(
                    f"{COLORS[current_player]}{names[current_player]}'s move (row,col): {COLORS['reset']}"
                ).strip().lower()
                
                if move == 'menu':
                    return
                
                result = validate_move(move, board)
                
                while result in ["invalid", "occupied", "error"]:
                    play_sound("error")
                    time.sleep(0.5)
                    draw_board(board)
                    move = input(
                        f"{COLORS[current_player]}{names[current_player]}'s move (row,col): {COLORS['reset']}"
                    ).strip().lower()
                    result = validate_move(move, board)
                
                if result is None:  
                    continue
                
                row, col = result

            board[row][col] = current_player
            moves.append(f"{current_player}{row}{col}")
            play_sound("move")

            if check_winner(board, current_player):
                winning_line = get_winning_line(board, current_player)
                scores[names[current_player]] += 1
                result = f"{names[current_player]} wins!"
                break
            elif is_draw(board):
                result = "Draw"
                break

            current_player = "O" if current_player == "X" else "X"

        draw_board(board, winning_line)
        if "wins" in result:
            show_victory_message(current_player, names)
            play_sound("win")
        else:
            print(f"{COLORS['prompt']}🤝 Game Draw! {COLORS['reset']}")
            play_sound("draw")
        game_data = {
            "player_x": names["X"],
            "player_o": names["O"],
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "result": result,
            "moves": moves,
            "duration": str(datetime.now() - start_time)
        }
        save_game_history(game_data)

        while True:
            print(f"\n{COLORS['prompt']}1. Play Again")
            print(f"2. Return to Main Menu")
            print(f"3. View Game History{COLORS['reset']}")
            choice = input(f"{COLORS['prompt']}Choose option (1-3): {COLORS['reset']}").strip()
            
            if choice == '1':
                break
            elif choice == '2':
                return
            elif choice == '3':
                show_game_history()
                input(f"{COLORS['prompt']}Press Enter to continue...{COLORS['reset']}")
            else:
                print(f"{COLORS['error']}Invalid choice!{COLORS['reset']}")

def main_menu():
    """Enhanced main menu system"""
    difficulty = "medium"
    names = {"X": "Player", "O": "AI"}
    
    while True:
        animate_title()
        print(f"{COLORS['title']}Main Menu:{COLORS['reset']}")
        print(f"1. {COLORS['X']}Player vs Player{COLORS['reset']}")
        print(f"2. {COLORS['O']}Player vs AI{COLORS['reset']}")
        print(f"3. {COLORS['prompt']}AI Difficulty ({difficulty.capitalize()}){COLORS['reset']}")
        print(f"4. {COLORS['history']}View Game History{COLORS['reset']}")
        print(f"5. {COLORS['error']}Exit{COLORS['reset']}")
        
        choice = input(f"{COLORS['prompt']}Choose option (1-5): {COLORS['reset']}").strip()
        
        if choice == "1":
            names = get_player_names("1")
            game_loop(names, difficulty, "1")
        elif choice == "2":
            names = get_player_names("2")
            game_loop(names, difficulty, "2")
        elif choice == "3":
            print(f"\n{COLORS['title']}AI Difficulty:{COLORS['reset']}")
            print(f"1. {COLORS['prompt']}Easy (Random moves){COLORS['reset']}")
            print(f"2. {COLORS['prompt']}Medium (Smart moves){COLORS['reset']}")
            print(f"3. {COLORS['prompt']}Hard (Unbeatable){COLORS['reset']}")
            diff_choice = input(f"{COLORS['prompt']}Select (1-3): {COLORS['reset']}").strip()
            if diff_choice in ["1", "2", "3"]:
                difficulty = ["easy", "medium", "hard"][int(diff_choice)-1]
            else:
                print(f"{COLORS['error']}Invalid choice!{COLORS['reset']}")
        elif choice == "4":
            show_game_history()
            input(f"{COLORS['prompt']}Press Enter to continue...{COLORS['reset']}")
        elif choice == "5":
            print(f"{COLORS['title']}Thanks for playing!{COLORS['reset']}")
            sys.exit()
        else:
            print(f"{COLORS['error']}Invalid choice!{COLORS['reset']}")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{COLORS['reset']}Game exited. Thanks for playing!")
        sys.exit(0)