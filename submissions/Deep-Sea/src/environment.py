import random
class EnvironmentManager:
    def __init__(self, submarine):
        self.submarine = submarine
        self.events = {
            "strong_current": {"description": "A strong current pulls the submarine, increasing power consumption.", "effect": self.strong_current},
            "hydrothermal_vent": {"description": "The submarine passes near a hydrothermal vent, causing minor hull damage.", "effect": self.hydrothermal_vent},
            "magnetic_anomaly": {"description": "A magnetic anomaly interferes with the sonar.", "effect": self.magnetic_anomaly}
        }
    def update(self):
        messages = []
        if random.random() < 0.1:
            event_name = random.choice(list(self.events.keys()))
            event = self.events[event_name]
            messages.append(f"[bold yellow]Environmental Hazard: {event['description']}[/bold yellow]")
            messages.extend(event['effect']())
        return messages
    def strong_current(self):
        self.submarine.resources["fuel"]["level"] -= 5
        return []
    def hydrothermal_vent(self):
        self.submarine.hull_integrity -= 5
        return []
    def magnetic_anomaly(self):
        messages = []
        if self.submarine.systems["Sonar"].is_active:
            self.submarine.systems["Sonar"].deactivate()
            messages.append("[bold red]Sonar has been knocked offline by magnetic interference![/bold red]")
        return messages