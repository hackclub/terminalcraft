from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.panel import Panel
from rich.text import Text
import sys
from chessminal.validation import validatePGN
from chessminal.game_review import review_game

def main():
    if len(sys.argv) > 1:
        pgn_file= sys.argv[1]
    else:
        print("ChessMinal is a CLI - App that allows you to review your chess games.")
        print("To review your Game: Run chessminal \'path/to/your/pgn/file\'. ")
        print("For more info: Visit github.com/daamin909/chessminal")
        exit(0)
    try:
        with open(pgn_file, "r") as f:
            pgn = f.read()
        validity = validatePGN(pgn)
    except Exception as e:
        print("File Not Found: Enter a valid path and try again.")
        print(e)
        exit(0)

    if (validity):
        reviewed_game = review_game(pgn)
    else:
        print("Invalid PGN: Please try again.")
        exit(0)


    console = Console()
    chess_text = Text("""
    ▄████▄    ██░ ██ ▓    █████       ██████      ██████  
    ▒██▀ ▀█    ▓██░ ██▒    ▓█   ▀▒     ██    ▒     ▒██    
    ▒▓█    ▄   ▒██▀▀██░    ▒███  ░     ▓██▄  ░     ▓██▄  ░  
    ▒▓▓▄ ▄██▒  ░▓█ ░██     ▒▓█  ▄      ▒   ██▒     ▒   ██▒ 
    ▒ ▓███▀    ░░▓█▒░██    ▓░▒████▒    ██████▒▒    ██████▒                                          
    """, style="bold green")

    console.print(chess_text)


    console = Console()

    table = Table(title="", style="bold green", border_style="bright_blue")
    table.add_column("White Player", justify="center", style="bold white")
    table.add_column("White Rating", justify="center", style="bold yellow")
    table.add_column("Black Player", justify="center", style="bold white")
    table.add_column("Black Rating", justify="center", style="bold yellow")

    table.add_row(
        reviewed_game["info"]["white_player"],
        reviewed_game["info"]["white_rating"],
        reviewed_game["info"]["black_player"],
        reviewed_game["info"]["black_rating"]
    )

    console.print(table)

    console.print(Panel("Accuracy", style="bold magenta"))
    with Progress() as progress:
        task1 = progress.add_task("[bold white]White Accuracy", total=100)
        task2 = progress.add_task("[bold white]Black Accuracy", total=100)
        progress.update(task1, advance=reviewed_game["accuracy"]["white"])
        progress.update(task2, advance=reviewed_game["accuracy"]["black"])

    console.print(Panel("Move Types", style="bold blue"))

    move_types = Table(border_style="green")
    move_types.add_column("Player", justify="center")
    move_types.add_column("Best Move", justify="center")
    move_types.add_column("Excellent", justify="center")
    move_types.add_column("Good", justify="center")
    move_types.add_column("Inaccuracy", justify="center")
    move_types.add_column("Mistake", justify="center")
    move_types.add_column("Blunder", justify="center")
    move_types.add_column("Book Moves", justify="center")

    w_moves = reviewed_game["number_of_move_types"]["w"]
    b_moves = reviewed_game["number_of_move_types"]["b"]

    move_types.add_row(
        "White",
        str(w_moves["best_move"]),
        str(w_moves["excellent"]),
        str(w_moves["good"]),
        str(w_moves["inaccuracy"]),
        str(w_moves["mistake"]),
        str(w_moves["blunder"]),
        str(w_moves["book_move"])
    )

    move_types.add_row(
        "Black",
        str(b_moves["best_move"]),
        str(b_moves["excellent"]),
        str(b_moves["good"]),
        str(b_moves["inaccuracy"]),
        str(b_moves["mistake"]),
        str(b_moves["blunder"]),
        str(b_moves["book_move"])
    )

    console.print(move_types)
    console.print(Panel("Moves Analysis", style="bold yellow"))

    moves_table = Table(title="", show_header=True, header_style="bold green")
    moves_table.add_column("Move #", justify="center", style="bold cyan")
    moves_table.add_column("Move", justify="center", style="bold yellow")
    moves_table.add_column("Eval", justify="center", style="bold magenta")
    moves_table.add_column("Type", justify="center", style="bold red")

    moves_table.add_column("Move #", justify="center", style="bold cyan")
    moves_table.add_column("Move", justify="center", style="bold yellow")
    moves_table.add_column("Eval", justify="center", style="bold magenta")
    moves_table.add_column("Type", justify="center", style="bold red")

    for i in range(0, len(reviewed_game["move_evaluations"]), 2):
        move1 = reviewed_game["move_evaluations"][i]
        move2 = reviewed_game["move_evaluations"][i + 1] if i + 1 < len(reviewed_game["move_evaluations"]) else {"move_no": "-", "move": "-", "eval":{"value": "-"}, "move_type": "-"}
        
        moves_table.add_row(
            str(move1["move_no"]), move1["move"], str(move1["eval"]['value']), move1["move_type"],
            str(move2["move_no"]), move2["move"], str(move2["eval"]['value']), move2["move_type"]
        )
    console.print(moves_table)


if __name__ =="__main__":
    main()