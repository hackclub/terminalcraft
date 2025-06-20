import random
import traceback
from rich.console import Console
console = Console()
class System:
    def __init__(self, name, power_draw=0, health=100):
        self.name = name
        self.health = health
        self.max_health = 100
        self.power_draw = power_draw
        self._is_active = False
        self.is_broken = False
    @property
    def is_active(self):
        return self._is_active
    @is_active.setter
    def is_active(self, value):
        if self.name == "Life Support" and value is False:
            console.print(f"[bold red]DEBUG: Setting Life Support is_active to {value}. Call stack:[/bold red]")
            traceback.print_stack()
        self._is_active = value
    def take_damage(self, amount):
        self.health -= amount
        self.health = max(0, self.health)
        if self.health == 0:
            self.is_broken = True
            self.is_active = False
            console.print(f"[bold red]{self.name} is broken and has gone offline![/bold red]")
    def repair(self, amount, spare_parts_consumed):
        if self.is_broken:
            console.print(f"[yellow]{self.name} is broken. It needs full repair to function.[/yellow]")
        self.health += amount
        self.health = min(self.max_health, self.health)
        if self.health == self.max_health:
            self.is_broken = False
        return spare_parts_consumed
    def activate(self):
        if not self.is_broken:
            self.is_active = True
        else:
            console.print(f"[red]Cannot activate {self.name}, it is broken.[/red]")
    def deactivate(self):
        if self.name == "Life Support":
            console.print("[bold red]DEBUG: Deactivating Life Support. Call stack:[/bold red]")
            traceback.print_stack()
        self.is_active = False
    def get_status(self):
        status = "Active" if self.is_active else "Inactive"
        if self.is_broken:
            status = "[red]BROKEN[/red]"
        return f"  - {self.name}: Health {self.health}%, Status: {status}"
class Reactor(System):
    def __init__(self):
        super().__init__(name="Reactor", power_draw=0)
        self.power_output = 100
    def update(self):
        self.power_output = 100 * (self.health / self.max_health)
    def get_status(self):
        status = super().get_status()
        return f"{status}, Output: {self.power_output:.0f} MW"
class Engine(System):
    def __init__(self):
        super().__init__(name="Engine", power_draw=20)
        self.fuel_consumption_rate = 2 
        self.noise_output = 5 
    def get_fuel_consumption(self):
        if not self.is_active or self.is_broken:
            return 0
        efficiency = 1 + (1 - self.health / self.max_health)
        return self.fuel_consumption_rate * efficiency
    def get_noise(self):
        return self.noise_output if self.is_active else 0
class Sonar(System):
    def __init__(self):
        super().__init__(name="Sonar", power_draw=10)
        self.noise_output = 10
    def get_noise(self):
        return self.noise_output if self.is_active else 0
class LifeSupport(System):
    def __init__(self):
        super().__init__(name="Life Support", power_draw=5)
        self.oxygen_production_rate = 5 
    def get_oxygen_production(self):
        if not self.is_active or self.is_broken:
            return 0
        return self.oxygen_production_rate * (self.health / self.max_health)