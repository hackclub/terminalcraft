from src.systems import Reactor, Engine, Sonar, LifeSupport
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
        messages = []
        self.systems["Reactor"].update()
        self.power_generated = self.systems["Reactor"].power_output
        self.power_consumed = sum(sys.power_draw for sys in self.systems.values() if sys.is_active and not sys.is_broken)
        if self.power_consumed > self.power_generated:
            messages.append("[bold red]POWER GRID OVERLOAD! Non-essential systems shutting down.[/bold red]")
            for name, system in self.systems.items():
                if name not in self.essential_systems and system.is_active:
                    system.deactivate()
                    messages.append(f"[yellow]{name} has been shut down to conserve power.[/yellow]")
                    self.power_consumed = sum(sys.power_draw for sys in self.systems.values() if sys.is_active and not sys.is_broken)
                    if self.power_consumed <= self.power_generated:
                        break
        o2_produced = self.systems["Life Support"].get_oxygen_production()
        o2_consumed = self.resources["oxygen"]["rate"]
        self.resources["oxygen"]["level"] += (o2_produced + o2_consumed)
        self.resources["oxygen"]["level"] = min(self.resources["oxygen"]["capacity"], self.resources["oxygen"]["level"])
        self.resources["oxygen"]["level"] = max(0, self.resources["oxygen"]["level"])
        if self.resources["oxygen"]["level"] == 0:
            messages.append("[bold red]CRITICAL: OXYGEN DEPLETED! Hull integrity failing...[/bold red]")
            self.take_damage(5)
        fuel_consumed = self.systems["Engine"].get_fuel_consumption()
        self.resources["fuel"]["level"] -= fuel_consumed
        self.resources["fuel"]["level"] = max(0, self.resources["fuel"]["level"])
        if self.resources["fuel"]["level"] == 0 and self.systems["Engine"].is_active:
            messages.append("[bold red]Out of fuel! The engine sputters and dies.[/bold red]")
            self.systems["Engine"].deactivate()
        base_noise = sum(sys.get_noise() for sys in self.systems.values() if hasattr(sys, 'get_noise'))
        if self.silent_running:
            base_noise //= 2
        self.noise_level = base_noise
        self.take_damage(depth // 100)
        return messages
    def take_damage(self, amount):
        self.hull_integrity -= amount
        if self.crew_manager:
            self.crew_manager.broadcast_event('hull_damage', amount=amount)
        self.hull_integrity = max(0, self.hull_integrity)
    def get_system(self, name):
        return self.systems.get(name)
    def toggle_system(self, system_name):
        messages = []
        if system_name in self.essential_systems:
            messages.append(f"[red]Cannot manually toggle essential system: {system_name}.[/red]")
            return messages
        system = self.get_system(system_name)
        if not system:
            messages.append(f"[red]System '{system_name}' not found.[/red]")
            return messages
        if system.is_active:
            system.deactivate()
            messages.append(f"[cyan]{system.name} is now Offline.[/cyan]")
        else:
            system.activate()
            messages.append(f"[cyan]{system.name} is now Online.[/cyan]")
        return messages
    def toggle_silent_running(self):
        messages = []
        self.silent_running = not self.silent_running
        if self.silent_running:
            messages.append("[bold blue]Silent running enabled. Non-essential systems offline.[/bold blue]")
            for name, system in self.systems.items():
                if name not in self.essential_systems and system.is_active:
                    system.deactivate()
                    messages.append(f"[yellow]{name} has been shut down for silent running.[/yellow]")
        else:
            messages.append("[bold blue]Silent running disabled. Systems must be manually reactivated.[/bold blue]")
        return messages
    def get_status_report(self):
        report = []
        report.append("\n[bold]Submarine Status Report[/bold]")
        report.append(f"Hull Integrity: {self.hull_integrity}/{self.max_hull_integrity}%")
        report.append("\n[bold]Power Grid[/bold]")
        report.append(f"  - Generated: {self.power_generated:.0f} MW")
        report.append(f"  - Consumed: {self.power_consumed:.0f} MW")
        power_color = "green" if self.power_generated >= self.power_consumed else "red"
        report.append(f"  - Net: [bold {power_color}]{self.power_generated - self.power_consumed:.0f} MW[/bold {power_color}]")
        report.append("\n[bold]Onboard Resources[/bold]")
        for name, data in self.resources.items():
            report.append(f"  - {name.replace('_', ' ').title()}: {data['level']}/{data['capacity']}")
        report.append("\n[bold]Systems[/bold]")
        for system in self.systems.values():
            report.append(system.get_status())
        report.append(f"\nNoise Level: {self.noise_level}")
        return report