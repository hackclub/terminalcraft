import random
class Animal:
    """Represents an animal in the zoo with a lifecycle."""
    def __init__(self, species, name, config, age=None):
        self.species = species
        self.name = name
        self.food_cost = config['food_cost']
        self.appeal = config['appeal']
        self.preferences = config['preferences']
        self.lifespan = config['lifespan']  
        self.maturity_age = config['maturity_age']
        self.gender = random.choice(['Male', 'Female'])
        self.age = age if age is not None else self.maturity_age 
        if self.age == 0:
            self.appeal = self.appeal // 2 
        self.hunger = 0
        self.health = 100
        self.happiness = config['base_happiness']
        self.escape_risk = 0 
        self.habitat = None
    def feed(self):
        """Feeds the animal, increasing hunger satisfaction."""
        self.hunger = min(100, self.hunger + 50)
        self.happiness = min(100, self.happiness + 10)
        print(f"{self.name} the {self.species} has been fed.")
    def heal(self, amount):
        """Heals the animal, increasing health."""
        self.health = min(100, self.health + amount)
        print(f"{self.name} the {self.species} received medical care.")
    def update(self, habitat, zoo):
        """Updates the animal's status for the day, including aging."""
        self.age += 1
        self.hunger += 10
        self.hunger -= 5
        if self.hunger < 40:
            self.health -= 5
            self.happiness -= 10
        if habitat.cleanliness < 50:
            self.health -= 5
            self.happiness -= 5
        suitability = habitat.get_suitability(self.preferences)
        if suitability < 60:
            self.happiness -= (60 - suitability) / 5
        if 'Advanced Nutrition' in zoo.research_manager.completed_projects:
            self.health = min(100, self.health + 0.5)
            self.happiness = min(100, self.happiness + 0.2)
        self.happiness -= 2
        self.hunger = max(0, self.hunger)
        self.health = max(0, self.health)
        self.happiness = max(0, self.happiness)
        self._calculate_escape_risk()
    def _calculate_escape_risk(self):
        """Calculates the risk of the animal escaping."""
        risk = (100 - self.happiness) + (100 - self.health)
        self.escape_risk = max(0, min(100, risk // 4))
    def is_sick(self):
        """Check if the animal is sick."""
        return self.health < 70
    def is_dead(self):
        """Checks if the animal has died from poor health or old age."""
        return self.health <= 0 or self.age > self.lifespan
    def is_mature(self):
        """Checks if the animal is old enough to breed."""
        return self.age >= self.maturity_age
    def to_dict(self):
        """Converts the animal's state to a dictionary for saving."""
        return {
            'species': self.species,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'health': self.health,
            'hunger': self.hunger,
            'happiness': self.happiness,
                        'habitat_name': self.habitat.name if self.habitat else None
        }