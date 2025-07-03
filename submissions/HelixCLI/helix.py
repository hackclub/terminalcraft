import re
import os, json, sys, time, random
from dotenv import load_dotenv
from groq import Groq
from rich import print, box
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.spinner import Spinner
from rich.panel import Panel
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.syntax import Syntax
from rich.text import Text
from colorama import init, Fore, Back, Style


init(autoreset=True)
console = Console()
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    console.print("[bold red]ERROR:[/] add key in .env ;-;")
    sys.exit(1)

groq = Groq(api_key=API_KEY)

try:
    with open('data.json', 'r', encoding='utf-8') as f:
        DATA = json.load(f)
    GENES = DATA["genes"]
    CODON = DATA["codon_table"]
except Exception as e:
    console.print(f"[bold red]Failed to load data.json:[/] {e}")
    sys.exit(1)
## todo - make thiss DNA logo rotate
def show_banner():
    banner = """[bold blue]
 /$$   /$$           /$$ /$$            /$$$$$$  /$$       /$$$$$$  (==(     )==) 
| $$  | $$          | $$|__/           /$$__  $$| $$      |_  $$_/   `-.`. ,',-'
| $$  | $$  /$$$$$$ | $$ /$$ /$$   /$$| $$  \__/| $$        | $$        _,-,
| $$$$$$$$ /$$__  $$| $$| $$|  $$ /$$/| $$      | $$        | $$    ,-',' `.`-.
| $$__  $$| $$$$$$$$| $$| $$ \  $$$$/ | $$      | $$        | $$   (==(     )==)
| $$  | $$| $$_____/| $$| $$  >$$  $$ | $$    $$| $$        | $$    `-.`. ,',-'
| $$  | $$|  $$$$$$$| $$| $$ /$$/\  $$|  $$$$$$/| $$$$$$$$ /$$$$$$     ,-'",
|__/  |__/ \_______/|__/|__/|__/  \__/ \______/ |________/|______/  ,-',' `.`-.
                                                                   (==(     )==)

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=                                                           
"""
    console.print(banner)


def format_bold(text):
    return re.sub(r"\*\*(.*?)\*\*", r"[bold]\1[/]", text)

def spinner_task(fn, *args, **kwargs):
    with console.status("[bold green]Processing..[/]"):
        return fn(*args, **kwargs)

def loading_bar(task_name="Working..", total=30):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        transient=True,
    ) as progress:
        task = progress.add_task(task_name, total=total)
        for _ in range(total):
            time.sleep(0.03)
            progress.advance(task)
        return True
        

def view_gene_info():
    os.system('cls' if os.name == 'nt' else 'clear')
    show_banner()

    name = Prompt.ask("Enter Gene Symbol").strip().upper()
    local_info = GENES.get(name, {}).get("info", {})
    
    if local_info:
        summary = (
            f"- Name: {local_info.get('name', '')}\n"
            f"- Symbol: {name}\n"
            f"- Chromosome: {local_info.get('chromosome', '')}\n"
            f"- Location: {local_info.get('location', '')}\n"
            f"- Function: {local_info.get('function', '')}\n"
            f"- Protein: {local_info.get('protein', '')}\n"
            f"- Associated Disease: {local_info.get('disease', '')}\n"
            f"- Pathway: {local_info.get('pathway', '')}"
        )
    else:
        prompt_text = (
            f"Give structured summary of the gene '{name}' in the format below with no extra commentary:\n\n"
            f"- Name:\n"
            f"- Symbol:\n"
            f"- Chromosome:\n"
            f"- Location:\n"
            f"- Function:\n"
            f"- Protein:\n"
            f"- Associated Disease:\n"
            f"- Pathway:\n"
        )
        with Live(Spinner("dots", text="Fetching gene summary…"), refresh_per_second=10):
            response = groq.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role": "user", "content": prompt_text}]
            )
        summary = response.choices[0].message.content.strip()

    # external facts from groq
    fact_prompt = (
        f"List 5 short bullet-point facts about the human gene '{name}' "
        f"including role, regulation, disease connection, etc. "
        f"Highlight keywords in **bold**. No introductions or conclusions."
    )
    with Live(Spinner("dots", text="Getting extra gene facts…"), refresh_per_second=10):
        facts_response = groq.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": fact_prompt}]
        )
    facts_raw = facts_response.choices[0].message.content.strip()
    bullet_lines = [line.strip("-• ") for line in facts_raw.splitlines() if line.strip()]
    formatted_facts = "\n".join([f"- {format_bold(line)}" for line in bullet_lines[:6]])

    # show summ and facts - fetch from groq ofc
    console.print(Panel(summary, title=f"[bold yellow]{name} Summary", border_style="yellow"))
    console.print(Panel(formatted_facts, title="[bold green]More Facts & Insights", border_style="green"))

def view_gene_structure():
    console.clear()
    show_banner()

    name = Prompt.ask("Enter Gene Symbol").strip().upper()

    if name in GENES:
        gene_data = GENES[name]
        sequence = gene_data["sequence"]
    else:
        # fetch gene sequence from groq
        prompt = (
            f"Provide the DNA sequence of the human gene '{name}' (only exons and introns), "
            f"in plain text (uppercase letters A/T/G/C only) with no additional comments."
        )
        with Live(Spinner("dots", text="Fetching gene structure..."), refresh_per_second=10):
            response = groq.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role": "user", "content": prompt}]
            )
        sequence = re.sub(r"[^ATGC]", "", response.choices[0].message.content.upper())

        if not sequence or len(sequence) < 30:
            console.print(f"[bold red]Gene '{name}' not found or AI returned invalid sequence.[/]")
            return

    loading_bar(task_name="Rendering Structure")
    console.clear()
    show_banner()

    length = len(sequence)
    gc_count = sequence.count("G") + sequence.count("C")
    at_count = sequence.count("A") + sequence.count("T")
    gc_content = round((gc_count / length) * 100, 2)
    at_content = round((at_count / length) * 100, 2)

    structure = f"""
[bold magenta] ┌─────────────────────────────────────────────────────────────┐[/bold magenta]
[bold magenta] │[/bold magenta] 5' ▶  [blue]PROMOTER[/blue] ━▶ [green]5' UTR[/green] ━▶ [yellow]EXON 1[/yellow] ━▶ [cyan]INTRON[/cyan] ━▶ [yellow]EXON 2[/yellow] ━▶ [green]3' UTR[/green] ◀ 3' [bold magenta]│[/bold magenta]
[bold magenta] └─────────────────────────────────────────────────────────────┘[/bold magenta]

[bold white]  DNA[/bold white] ➝ [blue]Transcription[/blue] ➝ [green]mRNA[/green] ➝ [yellow]Translation[/yellow] ➝ [red]Protein[/red]
"""

    console.print(Panel.fit(structure, title=f"{name} Structure", border_style="bright_blue", padding=(1, 2)))

    stats_table = Table.grid(padding=1)
    stats_table.add_column(justify="right", style="bold white")
    stats_table.add_column()
    stats_table.add_row("Length", f"{length} bp")
    stats_table.add_row("GC Content", f"{gc_content}%")
    stats_table.add_row("AT Content", f"{at_content}%")

    console.print(Panel(stats_table, title="Sequence Info", border_style="green"))

    syntax = Syntax(sequence, "text", theme="monokai", line_numbers=True, word_wrap=False)
    console.print(Panel(syntax, title=f"{name} - Full Sequence", border_style="magenta"))

def transcribe(seq: str) -> str:
    return seq.replace("T", "U")

def translate(seq: str) -> str:
    protein = "".join(CODON.get(seq[i:i+3], "?") for i in range(0, len(seq), 3))
    return protein

def translation_menu():
    choice = Prompt.ask("1) DNA→RNA  2) DNA→Protein  Q) Back", choices=["1", "2", "Q"])
    if choice == "Q":
        return

    name = Prompt.ask("Enter Gene Symbol").strip().upper()

    if name in GENES:
        seq = GENES[name]["sequence"]
    else:
        # fetch gene sequence from groq if not found in data.json
        prompt = (
            f"Give only the DNA sequence of the human gene '{name}' (exons + introns) "
            f"in uppercase using A/T/G/C only. No extra text or formatting."
        )
        with Live(Spinner("dots", text="Fetching gene sequence..."), refresh_per_second=10):
            response = groq.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role": "user", "content": prompt}]
            )
        seq = re.sub(r"[^ATGC]", "", response.choices[0].message.content.upper())

        if not seq or len(seq) < 30:
            console.print(f"[bold red]Invalid or empty sequence for gene '{name}'.[/]")
            return

    loading_bar(task_name="Translating" if choice == "2" else "Transcribing")

    if choice == "1":
        result = transcribe(seq)
        title = f"{name} → RNA"
    else:
        result = translate(seq)
        title = f"{name} → Protein"

    syntax_block = Syntax(result, "text", theme="monokai", word_wrap=True)
    console.print(Panel(syntax_block, title=f"[green]{title}", border_style="cyan"))

def simulate_mutation():
    name = Prompt.ask("Enter Gene Symbol").strip().upper()

    if name in GENES:
        base_seq = GENES[name]["sequence"]
    else:
        # fetch gene sequence from groq
        prompt = (
            f"Give only the DNA sequence of the human gene '{name}' (exons + introns) "
            f"in uppercase using A/T/G/C only. No extra text or formatting."
        )
        with Live(Spinner("dots", text="Getting gene sequence..."), refresh_per_second=10):
            response = groq.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role": "user", "content": prompt}]
            )
        base_seq = re.sub(r"[^ATGC]", "", response.choices[0].message.content.upper())

        if not base_seq or len(base_seq) < 30:
            console.print(f"[bold red]Invalid or empty sequence for gene '{name}'.[/]")
            return

    seq = list(base_seq)
    mut = Prompt.ask("Mutation type", choices=["insertion", "deletion", "substitution"])
    pos = IntPrompt.ask("Position (1-based)", default=random.randint(1, len(seq)))

    if pos < 1 or pos > len(seq):
        console.print("[bold red]Invalid position![/]")
        return

    pos0 = pos - 1
    loading_bar(task_name="Simulating mutation")
    orig = seq[pos0]

    if mut == "insertion":
        base = Prompt.ask("Base to insert", choices=["A", "T", "C", "G"])
        seq.insert(pos0, base)
        desc = f"Inserted {base} at position {pos}"
    elif mut == "deletion":
        seq.pop(pos0)
        desc = f"Deleted {orig} at position {pos}"
    else: 
        base = Prompt.ask("Substitute with", choices=["A", "T", "C", "G"], default=orig)
        seq[pos0] = base
        desc = f"Substituted {orig} → {base} at position {pos}"

    new_seq = "".join(seq)
    highlighted_seq = (
        new_seq[:pos0] +
        f"[black on red]{new_seq[pos0]}[/]" +
        new_seq[pos0 + 1:]
    )

    # do proper formating
    text_obj = Text.from_markup(highlighted_seq)

    console.print(Panel.fit(
        text_obj,
        title=f"[red]Mutation Result[/] — {desc}",
        border_style="red",
        padding=(1, 2)
    ))

def bio_assistant():
    console.print(Panel("[bold blue]Ask your biology question below:[/]"))
    prompt_text = Prompt.ask("→")
    prompt = f"Answer this biology question professionally, clearly, and concisely, with no intro or outro text: {prompt_text}"
    with Live(Spinner("dots", text="Thinking…"), refresh_per_second=10):
        response = groq.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": prompt}]
        )
    answer = response.choices[0].message.content.strip()
    console.print(Panel(answer, title="[cyan]Bio‑Assistant Reply"))

## main menu
def main_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    show_banner()

    console.print()

    table = Table(show_header=False, box=box.SIMPLE_HEAVY, padding=(0, 1))
    table.add_column(style="bold green", justify="right", no_wrap=True)
    table.add_column(style="bold white")

    table.add_row("1)", "View Gene Info")
    table.add_row("2)", "View Gene Structure")
    table.add_row("3)", "DNA Translation & Transcription")
    table.add_row("4)", "Simulate Mutation")
    table.add_row("5)", "Helix AI")
    table.add_row("Q)", "Quit :(")

    console.print(table)
    console.print()

def main():
    while True:
        main_menu()
        choice = Prompt.ask("Select an option", choices=["1","2","3","4","5","Q"])
        if choice == "1":
            view_gene_info()
        elif choice == "2":
            view_gene_structure()
        elif choice == "3":
            translation_menu()
        elif choice == "4":
            simulate_mutation()
        elif choice == "5":
            bio_assistant()
        else:
            console.print("[bold yellow]Exiting Helix CLI. Goodbye :( [/]")
            sys.exit(0)
        console.print()
        Prompt.ask("[grey]Press Enter to return to menu[/]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt: ## readded after conflct ;p
        console.print("\n[bold red]Interrupted. Exiting..[/]")