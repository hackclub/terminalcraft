import random
import requests
from rich.console import Console
from rich.table import Table

console = Console()

def get_words():
    url = "https://raw.githubusercontent.com/dwyl/english-words/master/words.txt"
    response = requests.get(url)
    words = response.text.splitlines()
    return [word.lower() for word in words if len(word) == 5]

def check_guess(guess, target):
    result = []
    for i in range(len(guess)):
        if guess[i] == target[i]:
            result.append(("green", guess[i].upper()))
        elif guess[i] in target:
            result.append(("yellow", guess[i].lower()))
        else:
            result.append(("dim", guess[i].lower()))
    return result

def build_table():
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Guess #", style="bold cyan")
    table.add_column("Guess", justify="center")
    table.add_column("Feedback", justify="center")
    return table

def play_game():
    words = get_words()
    target_word = random.choice(words)
    
    console.print("[bold cyan]Welcome to Wordle![/bold cyan]", justify="center")
    console.print("[bold magenta]Guess the 5-letter word.[/bold magenta]", justify="center")
    console.print("\n[italic]Feedback guide:[/italic]")
    console.print("[green]Correct letter, correct position[/green]")
    console.print("[yellow]Correct letter, wrong position[/yellow]")
    console.print("[dim]Incorrect letter[/dim]\n")
    
    attempts = 6
    table = build_table()

    console.print(table)
    
    while attempts > 0:
        guess = console.input(f"\n{attempts} attempts left. Your guess: ").strip().lower()
        
        if len(guess) != 5:
            console.print("[bold red]Please enter a 5-letter word.[/bold red]")
            continue
        
        if guess not in words:
            console.print("[bold red]Not a valid word, try again.[/bold red]")
            continue
        
        result = check_guess(guess, target_word)
        
        feedback = ""
        for color, letter in result:
            feedback += f"[{color}] {letter} [/]{' ' * 2}"
        
        table.add_row(str(6 - attempts), guess, feedback)
        
        console.clear()
        console.print(table)
        
        if guess == target_word:
            console.print("\n[bold green]You got it! Well done![/bold green]")
            break
        
        attempts -= 1
    
    if attempts == 0:
        console.print(f"\n[bold red]Game over! The word was: {target_word}[/bold red]")

if __name__ == "__main__":
    play_game()
