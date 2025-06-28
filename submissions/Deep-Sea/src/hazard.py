import random
class HazardManager:
    def __init__(self, submarine, crew_manager):
        self.submarine = submarine
        self.crew_manager = crew_manager
    def update(self, depth):
        messages = []
        messages.extend(self.simulate_pressure_hazards(depth))
        messages.extend(self.simulate_system_failures())
        return messages
    def simulate_pressure_hazards(self, depth):
        messages = []
        if depth > 500 and random.random() < 0.2: 
            pressure_damage = random.randint(10, 20)
            self.submarine.hull_integrity -= pressure_damage
            if pressure_damage > 0:
                messages.append(f"[bold red]Hull integrity compromised by pressure! Damage: {pressure_damage}%[/bold red]")
                for member in self.crew_manager.crew.values():
                    member.sanity -= pressure_damage // 2
                messages.extend(self.increase_panic(10))
        return messages
    def simulate_system_failures(self):
        messages = []
        if random.random() < 0.1: 
            non_essential_systems = [s for s in self.submarine.systems.keys() if s not in self.submarine.essential_systems]
            if not non_essential_systems:
                return messages
            system_name = random.choice(non_essential_systems)
            system = self.submarine.systems.get(system_name)
            if system and system.is_active:
                system.deactivate()
                messages.append(f"[bold red]System failure! {system.name.capitalize()} has gone offline![/bold red]")
                if self.submarine.hull_integrity < 50:
                    for member in self.crew_manager.crew.values():
                        panic_chance = (50 - self.submarine.hull_integrity) / 100 + (100 - member.sanity) / 200
                        if random.random() < panic_chance:
                            member.panic += random.randint(5, 15)
                            member.panic = min(100, member.panic)
                            messages.append(f"[bold red]{member.name} is panicking![/bold red]")
                messages.extend(self.increase_panic(5))
        return messages
    def increase_panic(self, amount):
        for member in self.crew_manager.crew.values():
            member.panic = min(100, member.panic + amount)
        return ["[bold yellow]The crew is starting to panic![/bold yellow]"]