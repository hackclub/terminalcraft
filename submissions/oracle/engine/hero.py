"""
This module defines the Hero class and the templates for legendary individuals
who can appear in the world and be recruited by kingdoms.
"""
import random
class Hero:
    """Represents a single Legendary Hero."""
    def __init__(self, name, title, effect, lifespan):
        self.name = name
        self.title = title
        self.effect = effect  
        self.lifespan = lifespan  
        self.location = None  
    def tick(self):
        """Reduces the hero's remaining lifespan by one year."""
        self.lifespan -= 1
HERO_TEMPLATES = {
    'The Tactician': {
        'name': 'Kaelen the Fox',
        'title': 'The Tactician',
        'effect': {'military_bonus': 2000},
        'lifespan': 20
    },
    'The Diplomat': {
        'name': 'Lyra Silver-Tongue',
        'title': 'The Diplomat',
        'effect': {'diplomacy_bonus': 20}, 
        'lifespan': 25
    },
    'The Architect': {
        'name': 'Boric the Builder',
        'title': 'The Architect',
        'effect': {'wonder_speed_modifier': 1.5}, 
        'lifespan': 30
    }
}
def create_hero(template_name):
    """Factory function to create a hero instance from a template."""
    template = HERO_TEMPLATES.get(template_name)
    if not template:
        return None
    return Hero(template['name'], template['title'], template['effect'], template['lifespan'])