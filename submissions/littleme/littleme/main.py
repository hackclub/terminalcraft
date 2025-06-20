import typer
import time
import random
from rich.console import Console
import pyfiglet
from littleme.llm import ask
from littleme.prompts import build
from littleme.memory import save, load, mwipe
from littleme.journal import create as createj, add as addj, get, show as showj




app = typer.Typer()
console = Console()

book = typer.Typer()
app.add_typer(book, name="journal")



@app.command()
def talk(input):
    prompt = build(input)
    response = ask(prompt)

    console.print(f"[bold cyan]Little Me:[/bold cyan] {response}")
    save(input, response)


@app.command()
def art(txt):
    fig = pyfiglet.Figlet(font='slant')
    print(fig.renderText(txt))


@app.command()
def wipe():
    mwipe()
    console.print("[bold red]Memory wiped![/bold red]")



@app.command()
def history():
    memory = load()
    if not memory:
        console.print("[bold red] No history found!!![/bold red]")
        return

    for entry in memory[-10:]:
        console.print(f"[bold green]You:[/bold green] {entry['input']}")
        console.print(f"[bold blue]Little Me:[/bold blue] {entry['response']}")
        console.print(f"[dim]Timestamp: {entry['timestamp']}[/dim]\n")


@book.command("create")
def create(name):
    if createj(name):
        console.print(f"[bold green]Journal '{name}' created successfully![/bold green]")
    else:
        console.print(f"[bold red]Journal '{name}' already exists![/bold red]")

@book.command("add")
def add(name, entry):
    data = addj(name, entry)
    if data is None:
        console.print(f"[bold red]Journal '{name}' does not exist![/bold red]")
    else:
        console.print(f"[bold green]Entry added to '{name}' journal![/bold green]")

@book.command("show")
def show(name):
    data = showj(name)
    if data is None:
        console.print(f"[bold red]Journal '{name}' does not exist![/bold red]")
    else:
        console.print(f"[bold orange3]Journal '{name}' contents:[/bold orange3]")
        for i, j in enumerate(data, 1):
            console.print(f"[bold blue]#{i}[/bold blue] - [dim]{j['Time']}[/dim]")
            console.print(f"{j['Contnent']}\n")


@app.command()
def timer(sec):
    console.print(f"[bold yellow]Starting timer for {sec} seconds...[/bold yellow]")
    for i in range(int(sec), 0, -1):
        console.print(f"[bold green]{i} seconds remaining...[/bold green]")
        time.sleep(1)
    console.print("[bold green]Time's up![/bold green]")

@app.command()
def help():
    console.print("[bold magenta]Welcome to Little Me Terminal![/bold magenta]")
    console.print("[bold yellow]Available Commands:[/bold yellow]")
    console.print("[bold green]talk <text> [/bold green] - Talk to Little Me")
    console.print("[bold green]art <content>[/bold green] - Generate ASCII art")
    console.print("[bold green]wipe[/bold green] - Wipe memory")
    console.print("[bold green]history[/bold green] - Show recent interactions")
    console.print("[bold green]journal create <name>[/bold green] - Create a new journal")
    console.print("[bold green]journal add <name> <entry> [/bold green] - Add an entry to a journal")
    console.print("[bold green]journal show <name>[/bold green] - Show contents of a journal")
    console.print("[bold green]Control[/bold green] - Let Little Me take control (just for fun!)")
    console.print("[bold green]timer <seconds>[/bold green] - Set a timer")
    console.print("[bold green]greet[/bold green] - Greeting from Little Me")
    console.print("[bold green]calc <expression>[/bold green] - Calculate a expression")
    console.print("[bold green]idea[/bold green] - Get a random idea")
    console.print("[bold green]fortune[/bold green] - Get a random fortune")
    console.print("[bold green]glitch[/bold green] - Show a glitch effect")
    console.print("[bold green]play[/bold green] - Play a guessing game")
    console.print("[bold green]roll[/bold green] - Roll a dice")
    console.print("[bold green]help[/bold green] - Show this help message")
    console.print("use '' for multiple words")
    console.print("[bold magenta] there is also a secret command, try to find it! [/bold magenta]")

@app.command()
def greet():
    console.print("[bold cyan] Hello! I'm Little Me, your CLI version![/bold cyan]")
    console.print("[bold orange3] I can help you in many things, type help to see [/bold orange3]")
    console.print("[bold yellow] Lets have some fun!!!!!!!!1 [/bold yellow] ")


@app.command()
def calc(e):
    try:
        r = eval(e)
        console.print(f"[bold green]Result: {r}[/bold green]")
        console.print("Littlme Me is a math genius! Not like you, hahahhaha")
    except:
        console.print("[bold red] Error: Invalid expression! [/bold red]")
        console.print(" Your math is not matthing!!!! lol")


@app.command()
def idea():
    i = ask(build("Give me a random idea"))
    console.print(f"[bold cyan] Little Me [/bold cyan]:{i}") 


@app.command()
def fortune():
    r = ask(build("Give me a random fortune (keep it in less then 3 lines)"))
    console.print(f"[bold cyan] Little Me: [/bold cyan] {r}")
    

@app.command()
def unlock():
    console.print("[bold magenta] Wowwww you have unlocked the secret command! [/bold magenta]")
    art = """
    ███╗   ██╗██╗   ██╗██╗      ██████╗  ██████╗ ██╗  ██╗
    ████╗  ██║██║   ██║██║     ██╔═══██╗██╔═══██╗██║ ██╔╝
    ██╔██╗ ██║██║   ██║██║     ██║   ██║██║   ██║█████╔╝ 
    ██║╚██╗██║██║   ██║██║     ██║   ██║██║   ██║██╔═██╗ 
    ██║ ╚████║╚██████╔╝███████╗╚██████╔╝╚██████╔╝██║  ██╗
    ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝
    """

    console.print(f"\n[bold green]{art}[/bold green]")
    console.print("[bold orange3] Share this achivemtent with your friends and on slack ( btw dont tell them the secret key) ! [/bold orange3]")


@app.command()
def glitch():
    c = "█▓▒░<>!?@#$%&*"
    for _ in range(20):
        line = ''.join(random.choice(c) for _ in range(50))
        console.print(f"[green]{line}[/green]")
        time.sleep(0.1)
    console.print("[bold red] Glitching complete! [/bold red]")
    
@app.command()
def play():
    console.print("[bold yellow]Welcome to the Guess the Number game![/bold yellow]")
    console.print("[bold green]I'm thinking of a number between 1 and 10. Can you guess it?[/bold green]")
    number = random.randint(1, 10)
    g = input("[bold cyan]Enter your guess: [/bold cyan]")
    if not int(g) == number:
        console.print("[bold red]Wrong guess! Better luck next time![/bold red]")
        console.print(f"[bold blue]The number was: {number}[/bold blue]")
    else:
        console.print("[bold green]Congratulations! You guessed it right![/bold green]")
        console.print("[bold yellow]You are a genius! Little Me is impressed![/bold yellow]")


@app.command()
def roll():
    console.print("[bold yellow]Rolling a dice...[/bold yellow]")
    time.sleep(1)
    result = random.randint(1, 6)
    console.print(f"[bold green]You rolled a {result}![/bold green]")


@app.command()
def control():
    console.print("[bold magenta] Little Me is taking control hahahah!! [/bold magenta]")
    console.print("[bold red] Get ready to see the evil side of me 😈😈😈😈 [/bold red]")
    console.print("[bold red] Starting the attacccccccckkkkkkkkkk [/bold red]")
    time.sleep(2)
    steps = [
        "Looking for your browser history",
        "finding your most embarrassing moments",
        "Spying on your desktop",
        "Reading you private messages",
        "Connecting to your webcam",
        "Port access given to International Hackers",
        "Searching the dark web", 
        "No one can STOP ME NOW, hahahhaha"
    ]
    for i in steps:
        console.log(f"[bold red]{i} [/bold red]")
        time.sleep(1.1)

    console.log(" [bold green] Little me has exited your system lol, good luck [/bold green]")




def main():
    app()

if __name__ == "__main__":
    app()