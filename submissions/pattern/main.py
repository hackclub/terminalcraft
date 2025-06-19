import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import questionary
from art_generators import MatrixGenerator, ParticleExplosionGenerator, MandelbrotGenerator, DigitalRainGenerator, VoronoiGenerator, KaleidoscopeGenerator, DayNightCycleGenerator, ForestSimulationGenerator, SeaWavesGenerator, GameOfLifeGenerator, SpinningCubeGenerator, RandomWalkersGenerator, RainGenerator
def main():
    console = Console()
    console.print(Panel.fit("[bold cyan]Welcome to the Terminal Procedural Art Generator![/bold cyan]", style="bold blue on black"))
    art_options = {
        "1": ("Matrix", MatrixGenerator),
        "2": ("Particle Explosion", ParticleExplosionGenerator),
        "3": ("Infinite Zoom", MandelbrotGenerator),
        "4": ("Digital Rain", DigitalRainGenerator),
        "5": ("Voronoi Diagram", VoronoiGenerator),
        "6": ("Kaleidoscope", KaleidoscopeGenerator),
        "7": ("Day/Night Cycle", DayNightCycleGenerator),
        "8": ("Forest Simulation", ForestSimulationGenerator),
        "9": ("Sea Waves", SeaWavesGenerator),
        "10": ("Game of Life", GameOfLifeGenerator),
        "11": ("Spinning 3D Cube", SpinningCubeGenerator),
        "12": ("Random Walkers", RandomWalkersGenerator),
        "13": ("Rain", RainGenerator),
    }
    while True:
        from rich.table import Table
        table = Table(title="[bold green]Choose an Art Generator[/bold green]", style="bold white on black", title_style="bold green", header_style="bold yellow")
        table.add_column("Option", style="cyan", no_wrap=True)
        table.add_column("Art Mode", style="magenta")
        for key, (name, _) in art_options.items():
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
        if choice in art_options:
            name, generator_class = art_options[choice]
        if generator_class:
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
            console.clear()
            console.print(Panel.fit("[bold cyan]Welcome to the Terminal Procedural Art Generator![/bold cyan]", style="bold blue on black"))
        else:
            console.print("[bold red]Invalid option. Please try again.[/bold red]")
if __name__ == "__main__":
    main()