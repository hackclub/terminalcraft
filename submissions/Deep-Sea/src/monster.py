class Monster:
    def __init__(self, name, health, attack_power, loot):
        self.name = name
        self.health = health
        self.attack_power = attack_power
        self.loot = loot
    def attack(self, submarine, crew_manager):
        messages = []
        submarine.hull_integrity -= self.attack_power
        messages.append(f"[bold red]The {self.name} attacks! Hull integrity is now at {submarine.hull_integrity}%[/bold red]")
        for member in crew_manager.crew.values():
            member.sanity -= self.attack_power
        return messages
    def take_damage(self, amount):
        self.health -= amount
        return [f"[bold green]The {self.name} takes {amount} damage.[/bold green]"]