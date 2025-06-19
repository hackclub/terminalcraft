import random
class RepairMinigame:
    def __init__(self, submarine, crew_manager):
        self.submarine = submarine
        self.crew_manager = crew_manager
        self.active_system = None
        self.sequence = None
        self.time_limit = 0
    def start(self, system_name):
        messages = []
        system_to_repair = self.submarine.get_system(system_name)
        if not system_to_repair:
            return [f"[red]System '{system_name}' not found.[/red]"]
        if system_to_repair.health >= system_to_repair.max_health:
            return [f"[yellow]{system_to_repair.name} is already at full health.[/yellow]"]
        engineer = self.crew_manager.get_assigned_engineer()
        if not engineer:
            return ["[bold red]No engineer assigned to repairs![/bold red]"]
        if self.submarine.resources['spare_parts']['level'] <= 0:
            return ["[bold red]No spare parts available for repairs![/bold red]"]
        self.active_system = system_to_repair
        sequence_length = 4 + engineer.level
        self.time_limit = 10 - (engineer.level // 2)
        self.sequence = "".join(random.choices("wasd", k=sequence_length))
        messages.append(f"[bold yellow]Initiating repair sequence for {self.active_system.name}...[/bold yellow]")
        messages.append(f"Quick, {engineer.name}! Input the following sequence: [bold cyan]{self.sequence}[/bold cyan]")
        messages.append(f"You have {self.time_limit} seconds.")
        return messages
    def evaluate(self, user_input, time_taken):
        messages = []
        if not self.active_system or not self.sequence:
            return ["[red]No active repair minigame.[/red]"]
        engineer = self.crew_manager.get_assigned_engineer()
        if time_taken > self.time_limit:
            messages.append("[bold red]Too slow! The system damage worsens![/bold red]")
            self.active_system.take_damage(5)
        elif user_input == self.sequence:
            self.submarine.resources['spare_parts']['level'] -= 1
            base_repair = 15
            skill_multiplier = engineer.get_skill_bonus("stat_modifier", "repair_amount")
            if skill_multiplier == 0: skill_multiplier = 1.0
            repair_amount = (base_repair + (engineer.level * 2)) * skill_multiplier
            self.active_system.repair(repair_amount, 1)
            messages.append(f"[bold green]Success! {engineer.name} expertly repairs the {self.active_system.name}. Health restored by {repair_amount:.1f}%![/bold green]")
            self.crew_manager.broadcast_event('successful_repair', engineer=engineer)
            engineer.gain_experience(20)
        else:
            self.submarine.resources['spare_parts']['level'] -= 1
            messages.append("[bold red]Incorrect sequence! The repair attempt fails, wasting parts.[/bold red]")
        self.active_system = None
        self.sequence = None
        self.time_limit = 0
        return messages