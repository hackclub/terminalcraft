class Habitat:
    """Represents a habitat for animals with environmental conditions."""
    def __init__(self, name, species_type, capacity, base_temp, base_enrichment):
        self.name = name
        self.species_type = species_type
        self.capacity = capacity
        self.animals = []
        self.cleanliness = 100
        self.temperature = base_temp
        self.enrichment = base_enrichment 
        self.security = 50 
    def has_space(self):
        """Checks if there is space for another animal."""
        return len(self.animals) < self.capacity
    def can_breed(self):
        """Checks if the habitat contains a pair of mature, opposite-gender animals."""
        mature_males = [a for a in self.animals if a.is_mature() and a.gender == 'Male']
        mature_females = [a for a in self.animals if a.is_mature() and a.gender == 'Female']
        return len(mature_males) > 0 and len(mature_females) > 0
    def add_animal(self, animal):
        """Adds an animal to the habitat."""
        if self.has_space():
            self.animals.append(animal)
            animal.habitat = self
            return True
        return False
    def update(self):
        """Updates the habitat's status."""
        self.cleanliness -= len(self.animals) * 2
        self.cleanliness = max(0, self.cleanliness)
    def get_suitability(self, animal_prefs):
        """Calculates how suitable the habitat is for an animal's preferences."""
        temp_min, temp_max = animal_prefs['temperature']
        temp_suitability = 100 if temp_min <= self.temperature <= temp_max else 20
        enrichment_suitability = min(100, (self.enrichment / animal_prefs['enrichment']) * 100)
        return (temp_suitability + enrichment_suitability) / 2
    def get_security_upgrade_cost(self):
        """Calculates the cost for the next security upgrade."""
        if self.security >= 100:
            return None 
        return 250 * (1 + (self.security // 10)) 
    def upgrade_security(self, finance):
        """Upgrades the habitat's security to reduce escape risk."""
        cost = self.get_security_upgrade_cost()
        if cost is None:
            print(f"{self.name}'s security is already at maximum.")
            return False
        if finance.money >= cost:
            finance.add_expense(cost, f"{self.name} Security Upgrade")
            self.security = min(100, self.security + 10)
            print(f"{self.name}'s security has been upgraded to {self.security}% for ${cost}.")
            return True
        else:
            print(f"Not enough money to upgrade {self.name}'s security. Cost: ${cost}")
            return False
    def to_dict(self):
        """Converts the habitat's state to a dictionary for saving."""
        return {
            'name': self.name,
            'species_type': self.species_type,
            'capacity': self.capacity,
            'cleanliness': self.cleanliness,
            'temperature': self.temperature,
            'enrichment': self.enrichment,
            'security': self.security
        }