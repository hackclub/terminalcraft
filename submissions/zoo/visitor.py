import random
from config import VISITOR_CONFIG
class Visitor:
    """Represents a visitor to the zoo with satisfaction and thoughts."""
    def __init__(self, visitor_type, state=None):
        self.type = visitor_type
        self.config = VISITOR_CONFIG[visitor_type]
        if state:
            self.satisfaction = state.get('satisfaction', 70)
            self.thoughts = state.get('thoughts', [])
        else:
            self.satisfaction = 70  
            self.thoughts = []
        self.interests = self.config.get("interests", [])
    def visit_habitat(self, habitat):
        """Simulates a visitor viewing a habitat and its animals, generating specific thoughts."""
        if not habitat.animals:
            self.satisfaction -= 10
            self.thoughts.append(f"I went to the {habitat.name} habitat, but it was empty.")
            return
        if habitat.cleanliness < 50:
            self.satisfaction -= 10
            self.thoughts.append(f"The {habitat.name} enclosure was quite smelly.")
        if habitat.enrichment < 40:
            self.satisfaction -= 8
            self.thoughts.append(f"The animals in {habitat.name} seemed bored.")
        for animal in habitat.animals:
            base_satisfaction_gain = 5
            if animal.happiness < 40:
                self.satisfaction -= 10
                self.thoughts.append(f"{animal.name} the {animal.species} looked stressed.")
            elif animal.health < 60:
                self.satisfaction -= 12
                self.thoughts.append(f"{animal.name} the {animal.species} didn't look very healthy.")
            else:
                base_satisfaction_gain += (animal.appeal + animal.happiness) // 20
                if base_satisfaction_gain > 8:
                    self.thoughts.append(f"Seeing {animal.name} the {animal.species} was a highlight!")
            if animal.species in self.interests:
                base_satisfaction_gain *= 1.5
                self.thoughts.append(f"As a {self.type}, I was thrilled to see the {animal.species}!")
            self.satisfaction += base_satisfaction_gain
        self.satisfaction = max(0, min(100, self.satisfaction))
    def get_donation(self):
        """Determines if a happy visitor will make a donation and returns the amount."""
        base_chance = self.config.get("donation_chance", 0.1)
        if self.satisfaction > 80 and random.random() < base_chance:
            min_donation, max_donation = self.config.get("donation_amount", (5, 25))
            return random.randint(min_donation, max_donation)
        return 0
    def to_dict(self):
        """Serializes the visitor's state to a dictionary."""
        return {
            'type': self.type,
            'satisfaction': self.satisfaction,
            'thoughts': self.thoughts
        }