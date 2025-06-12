import random
import time
from rich.console import Console
console = Console()
class RepairMinigame:
    def __init__(self, submarine, crew_manager):
        self.submarine = submarine
        self.crew_manager = crew_manager
    def run(self, system_name):
        system_to_repair = self.submarine.get_system(system_name)
        if not system_to_repair:
            console.print(f"[red]System '{system_name}' not found.[/red]")
            return False
        if system_to_repair.health >= system_to_repair.max_health:
            console.print(f"[yellow]{system_to_repair.name} is already at full health.[/yellow]")
            return False
        console.print(f"[bold yellow]Initiating repair sequence for {system_to_repair.name}...[/bold yellow]")
        engineer = self.crew_manager.get_assigned_engineer()
        if not engineer:
            console.print("[bold red]No engineer assigned to repairs![/bold red]")
            return False
        if self.submarine.resources['spare_parts']['level'] <= 0:
            console.print("[bold red]No spare parts available for repairs![/bold red]")
            return False
        sequence_length = 4 + engineer.level
        time_limit = 10 - (engineer.level // 2)
        sequence = "".join(random.choices("wasd", k=sequence_length))
        console.print(f"Quick, {engineer.name}! Input the following sequence: [bold cyan]{sequence}[/bold cyan]")
        start_time = time.time()
        user_input = console.input(f"({time_limit}s)> ")
        end_time = time.time()
        if end_time - start_time > time_limit:
            console.print("[bold red]Too slow! The system damage worsens![/bold red]")
            system_to_repair.take_damage(5)
            return False
        if user_input == sequence:
            self.submarine.resources['spare_parts']['level'] -= 1
            base_repair = 15
            skill_multiplier = engineer.get_skill_bonus("stat_modifier", "repair_amount")
            if skill_multiplier == 0:  
                skill_multiplier = 1.0
            repair_amount = (base_repair + (engineer.level * 2)) * skill_multiplier
            system_to_repair.repair(repair_amount, 1)
            console.print(f"[bold green]Success! {engineer.name} expertly repairs the {system_to_repair.name}. Health restored by {repair_amount:.1f}%![/bold green]")
            self.crew_manager.broadcast_event('successful_repair', engineer=engineer)
            engineer.gain_experience(20)
            return True
        else:
            console.print("[bold red]Incorrect sequence! The repair attempt fails, wasting parts.[/bold red]")
            self.submarine.resources['spare_parts']['level'] -= 1
            return False
            return False