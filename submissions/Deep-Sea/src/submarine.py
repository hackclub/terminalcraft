from rich.console import Console
from src.systems import Reactor, Engine, Sonar, LifeSupport
console = Console()
class Submarine:
    def __init__(self):
        self.hull_integrity = 100
        self.crew_manager = None
        self.max_hull_integrity = 100
        self.resources = {
            "oxygen": {"level": 100, "capacity": 100, "rate": -5}, 
            "fuel": {"level": 100, "capacity": 100},
            "spare_parts": {"level": 10, "capacity": 50}
        }
        self.systems = {
            "Reactor": Reactor(),
            "Engine": Engine(),
            "Sonar": Sonar(),
            "Life Support": LifeSupport()
        }
        self.essential_systems = ["Reactor", "Life Support"]
        for system_name in self.essential_systems:
            self.systems[system_name].is_active = True
        self.power_generated = 0
        self.power_consumed = 0
        self.noise_level = 0
        self.silent_running = False
    def update(self, depth):
        self.systems["Reactor"].update()
        self.power_generated = self.systems["Reactor"].power_output
        self.power_consumed = sum(sys.power_draw for sys in self.systems.values() if sys.is_active and not sys.is_broken)
        if self.power_consumed > self.power_generated:
            console.print("[bold red]POWER GRID OVERLOAD! Non-essential systems shutting down.[/bold red]")
            for name, system in self.systems.items():
                if name not in self.essential_systems and system.is_active:
                    system.deactivate()
                    console.print(f"[yellow]{name} has been shut down to conserve power.[/yellow]")
                    self.power_consumed = sum(sys.power_draw for sys in self.systems.values() if sys.is_active and not sys.is_broken)
                    if self.power_consumed <= self.power_generated:
                        break
        o2_produced = self.systems["Life Support"].get_oxygen_production()
        o2_consumed = self.resources["oxygen"]["rate"]
        self.resources["oxygen"]["level"] += (o2_produced + o2_consumed)
        self.resources["oxygen"]["level"] = min(self.resources["oxygen"]["capacity"], self.resources["oxygen"]["level"])
        self.resources["oxygen"]["level"] = max(0, self.resources["oxygen"]["level"])
        if self.resources["oxygen"]["level"] == 0:
            console.print("[bold red]CRITICAL: OXYGEN DEPLETED! Hull integrity failing...[/bold red]")
            self.take_damage(5)
        fuel_consumed = self.systems["Engine"].get_fuel_consumption()
        self.resources["fuel"]["level"] -= fuel_consumed
        self.resources["fuel"]["level"] = max(0, self.resources["fuel"]["level"])
        if self.resources["fuel"]["level"] == 0 and self.systems["Engine"].is_active:
            console.print("[bold red]Out of fuel! The engine sputters and dies.[/bold red]")
            self.systems["Engine"].deactivate()
        base_noise = sum(sys.get_noise() for sys in self.systems.values() if hasattr(sys, 'get_noise'))
        if self.silent_running:
            base_noise //= 2
        self.noise_level = base_noise
        self.take_damage(depth // 100)
    def take_damage(self, amount):
        self.hull_integrity -= amount
        if self.crew_manager:
            self.crew_manager.broadcast_event('hull_damage', amount=amount)
        self.hull_integrity = max(0, self.hull_integrity)
    def get_system(self, name):
        return self.systems.get(name)
    def toggle_system(self, system_name):
        if system_name in self.essential_systems:
            console.print(f"[red]Cannot manually toggle essential system: {system_name}.[/red]")
            return
        system = self.get_system(system_name)
        if not system:
            console.print(f"[red]System '{system_name}' not found.[/red]")
            return
        if system.is_active:
            system.deactivate()
            console.print(f"[cyan]{system.name} is now Offline.[/cyan]")
        else:
            system.activate()
            console.print(f"[cyan]{system.name} is now Online.[/cyan]")
    def toggle_silent_running(self):
        self.silent_running = not self.silent_running
        if self.silent_running:
            console.print("[bold blue]Silent running enabled. Non-essential systems offline.[/bold blue]")
            for name, system in self.systems.items():
                if name not in self.essential_systems and system.is_active:
                    system.deactivate()
                    console.print(f"[yellow]{name} has been shut down for silent running.[/yellow]")
        else:
            console.print("[bold blue]Silent running disabled. Systems must be manually reactivated.[/bold blue]")
    def print_status(self):
        console.print("\n[bold]Submarine Status Report[/bold]")
        console.print(f"Hull Integrity: {self.hull_integrity}/{self.max_hull_integrity}%")
        console.print("\n[bold]Power Grid[/bold]")
        console.print(f"  - Generated: {self.power_generated:.0f} MW")
        console.print(f"  - Consumed: {self.power_consumed:.0f} MW")
        power_color = "green" if self.power_generated >= self.power_consumed else "red"
        console.print(f"  - Net: [bold {power_color}]{self.power_generated - self.power_consumed:.0f} MW[/bold {power_color}]")
        console.print("\n[bold]Onboard Resources[/bold]")
        for name, data in self.resources.items():
            console.print(f"  - {name.replace('_', ' ').title()}: {data['level']}/{data['capacity']}")
        console.print("\n[bold]Systems[/bold]")
        for system in self.systems.values():
            console.print(system.get_status())
        console.print(f"\nNoise Level: {self.noise_level}")