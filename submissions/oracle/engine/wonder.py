"""
This module defines the Great Wonders that can be built by kingdoms.
"""
class GreatWonder:
    """Represents a single Great Wonder project."""
    def __init__(self, name, description, cost, effect):
        self.name = name
        self.description = description
        self.cost = cost
        self.progress = 0
        self.effect = effect 
    def is_complete(self):
        return self.progress >= self.cost
WONDER_TEMPLATES = {
    'The Grand Library': {
        'description': 'A vast repository of knowledge, bringing enlightenment and stability to the realm.',
        'cost': 50000,
        'effect': {'stability_bonus': 10}
    },
    'The Colossus': {
        'description': 'A towering statue that projects the kingdom\'s power, intimidating rivals and inspiring its soldiers.',
        'cost': 75000,
        'effect': {'military_modifier': 1.25} 
    },
    'The Star-Forge': {
        'description': 'A mysterious forge said to harness the power of a fallen star, producing immense wealth.',
        'cost': 100000,
        'effect': {'wealth_modifier': 1.2} 
    }
}
def create_wonder(name):
    """Factory function to create a wonder instance from a template."""
    template = WONDER_TEMPLATES.get(name)
    if not template:
        return None
    return GreatWonder(name, template['description'], template['cost'], template['effect'])