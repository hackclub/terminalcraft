import time
import sys
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import questionary
from art_generators import MatrixGenerator, ParticleExplosionGenerator, MandelbrotGenerator, DigitalRainGenerator, VoronoiGenerator, KaleidoscopeGenerator, DayNightCycleGenerator, ForestSimulationGenerator, SeaWavesGenerator, GameOfLifeGenerator, SpinningCubeGenerator, RandomWalkersGenerator, RainGenerator
def get_art_options():
    return {
        "matrix": ("Matrix", MatrixGenerator),
        "particle-explosion": ("Particle Explosion", ParticleExplosionGenerator),
        "infinite-zoom": ("Infinite Zoom", MandelbrotGenerator),
        "digital-rain": ("Digital Rain", DigitalRainGenerator),
        "voronoi": ("Voronoi Diagram", VoronoiGenerator),
        "kaleidoscope": ("Kaleidoscope", KaleidoscopeGenerator),
        "day-night-cycle": ("Day/Night Cycle", DayNightCycleGenerator),
        "forest": ("Forest Simulation", ForestSimulationGenerator),
        "sea-waves": ("Sea Waves", SeaWavesGenerator),
        "game-of-life": ("Game of Life", GameOfLifeGenerator),
        "spinning-cube": ("Spinning 3D Cube", SpinningCubeGenerator),
        "random-walkers": ("Random Walkers", RandomWalkersGenerator),
        "rain": ("Rain", RainGenerator),
    }
def run_generator(generator_class, name, console):
    console.print(f"\nStarting [bold magenta]{name}[/bold magenta]... Press Ctrl+C to exit.")
    time.sleep(1)
    try:
        width, height = console.size
        generator = generator_class(width, height - 1)
        generator.run()
    except Exception:
        console.print("\n[bold red]An unexpected error occurred while running the simulation.[/bold red]")
        console.print_exception(show_locals=True)
        console.input("\n[yellow]Press Enter to return to the menu.[/yellow]")
def interactive_menu():
    console = Console()
    console.print(Panel.fit("[bold cyan]Welcome to the Terminal Procedural Art Generator![/bold cyan]", style="bold blue on black"))
    art_options = get_art_options()
    menu_options = {}
    for i, (key, value) in enumerate(art_options.items(), 1):
        menu_options[str(i)] = (key, value[0], value[1])
    while True:
        table = Table(title="[bold green]Choose an Art Generator[/bold green]", style="bold white on black", title_style="bold green", header_style="bold yellow")
        table.add_column("Option", style="cyan", no_wrap=True)
        table.add_column("Art Mode", style="magenta")
        for key, (_, name, _) in menu_options.items():
            table.add_row(key, name)
        table.add_row("Q", "Quit")
        console.print(table)
        choice = questionary.text(
            "Enter your choice (number or Q to quit):"
        ).ask()
        if choice is None or choice.upper() == "Q":
            console.print("[bold yellow]Goodbye![/bold yellow]")
            break
        generator_class = None
        name = None
        if choice in menu_options:
            _, name, generator_class = menu_options[choice]
        if generator_class:
            run_generator(generator_class, name, console)
            console.clear()
            console.print(Panel.fit("[bold cyan]Welcome to the Terminal Procedural Art Generator![/bold cyan]", style="bold blue on black"))
        else:
            console.print("[bold red]Invalid option. Please try again.[/bold red]")
def main():
    console = Console()
    art_options = get_art_options()
    parser = argparse.ArgumentParser(description="Terminal Procedural Art Generator")
    parser.add_argument("art_mode", nargs="?", help="Art mode to run directly")
    parser.add_argument("--list", action="store_true", help="List available art modes")
    args = parser.parse_args()
    if args.list:
        console.print(Panel.fit("[bold cyan]Available Art Modes[/bold cyan]", style="bold blue on black"))
        for key, (name, _) in art_options.items():
            console.print(f"[cyan]{key}[/cyan]: [magenta]{name}[/magenta]")
        return
    if args.art_mode:
        if args.art_mode in art_options:
            name, generator_class = art_options[args.art_mode]
            run_generator(generator_class, name, console)
        else:
            console.print(f"[bold red]Unknown art mode: {args.art_mode}[/bold red]")
            console.print("[yellow]Available modes:[/yellow]")
            for key in art_options.keys():
                console.print(f"[cyan]{key}[/cyan]")
    else:
        interactive_menu()
if __name__ == "__main__":
    main()