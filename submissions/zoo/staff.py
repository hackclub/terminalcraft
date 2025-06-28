class Staff:
    """Represents a staff member with skills and fatigue."""
    def __init__(self, name, role, salary, base_skill=30):
        self.name = name
        self.role = role
        self.salary = salary
        self.skill = base_skill  
        self.fatigue = 0   
    def work(self):
        """Makes the staff member work, increasing fatigue."""
        self.fatigue = min(100, self.fatigue + 15)
    def rest(self):
        """Allows the staff member to rest, decreasing fatigue."""
        self.fatigue = max(0, self.fatigue - 40)
    def train(self, skill_gain=10):
        """Improves the staff's skill by a given amount."""
        self.skill = min(100, self.skill + skill_gain)
        print(f"{self.name}'s skill has increased to {self.skill:.0f}.")
    def get_effectiveness(self):
        """Calculates the current effectiveness based on skill and fatigue."""
        return self.skill * (1 - self.fatigue / 150.0)
    def to_dict(self):
        """Converts the staff's state to a dictionary for saving."""
        return {
            'name': self.name,
            'role': self.role,
            'skill': self.skill,
            'fatigue': self.fatigue
        }