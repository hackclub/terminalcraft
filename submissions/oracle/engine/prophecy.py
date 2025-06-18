"""
This module handles the unique mechanic of generating and allowing the player
to rewrite prophecies, which have tangible effects on the game.
"""
import random
class Prophecy:
    """Represents a single, structured prophecy that can be rewritten."""
    def __init__(self, source, target, p_type, components):
        self.source_kingdom_name = source.name
        self.target_kingdom_name = target.name
        self.type = p_type  
        self.components = components  
        self.is_fulfilled = False
        self.text = self.generate_text()
    def generate_text(self):
        """Generates the prophecy's descriptive text from its components."""
        if self.type == 'wealth_vs_stability':
            return (f"When the coffers of {self.source_kingdom_name} swell to "
                    f"{self.components['threshold']:,} gold, the foundations of "
                    f"{self.target_kingdom_name} shall crack.")
        elif self.type == 'military_vs_population':
            return (f"Should the legions of {self.source_kingdom_name} grow to "
                    f"{self.components['threshold']:,}, the people of "
                    f"{self.target_kingdom_name} will abandon their homes in fear.")
        elif self.type == 'golden_age':
            return (f"If the people of {self.source_kingdom_name} know an era of peace (above {self.components['threshold']} stability), "
                    f"a golden age shall dawn upon {self.target_kingdom_name}.")
        elif self.type == 'iron_plague':
            return (f"When the war machine of {self.source_kingdom_name} surpasses {self.components['threshold']:,} soldiers, "
                    f"an iron plague shall rust the blades of {self.target_kingdom_name}.")
        elif self.type == 'betrayal':
            return (f"When unrest grips {self.source_kingdom_name} (below {self.components['threshold']} stability), "
                    f"a poisoned word will shatter the court of {self.target_kingdom_name}.")
        return "An unknowable fate is woven."
    def condition(self, world):
        """Checks if the prophecy's condition is met based on world state."""
        source = world.get_kingdom_by_name(self.source_kingdom_name)
        if not source or not source.is_alive:
            return False
        if self.type == 'wealth_vs_stability':
            return source.wealth >= self.components['threshold']
        elif self.type == 'military_vs_population':
            return source.military_strength >= self.components['threshold']
        elif self.type == 'golden_age':
            return source.stability >= self.components['threshold']
        elif self.type == 'iron_plague':
            return source.military_strength >= self.components['threshold']
        elif self.type == 'betrayal':
            return source.stability <= self.components['threshold']
        return False
    def effect(self, world, renderer):
        """Applies the prophecy's effect to the world."""
        target = world.get_kingdom_by_name(self.target_kingdom_name)
        if not target or not target.is_alive:
            return
        if self.type == 'wealth_vs_stability':
            target.stability += self.components['effect_value']
            renderer.display_message(f"PROPHECY FULFILLED: {self.source_kingdom_name}'s wealth has doomed {self.target_kingdom_name} to internal strife!", 'magenta')
        elif self.type == 'military_vs_population':
            target.population = int(target.population * self.components['effect_value'])
            renderer.display_message(f"PROPHECY FULFILLED: The might of {self.source_kingdom_name}'s army has terrified the populace of {self.target_kingdom_name}!", 'magenta')
        elif self.type == 'golden_age':
            target.wealth += self.components['effect_value']
            renderer.display_message(f"PROPHECY FULFILLED: A golden age dawns for {self.target_kingdom_name}, their coffers overflowing!", 'magenta')
        elif self.type == 'iron_plague':
            target.military_strength = int(target.military_strength * self.components['effect_value'])
            renderer.display_message(f"PROPHECY FULFILLED: An iron plague has decimated the armies of {self.target_kingdom_name}!", 'magenta')
        elif self.type == 'betrayal':
            target.stability += self.components['effect_value']
            renderer.display_message(f"PROPHECY FULFILLED: A bitter betrayal has shattered the stability of {self.target_kingdom_name}!", 'magenta')
    def check_and_trigger(self, world, renderer):
        """Checks the condition and triggers the effect if met."""
        if not self.is_fulfilled and self.condition(world):
            self.is_fulfilled = True
            self.effect(world, renderer)
            return True
        return False
    def rewrite_target(self, new_target_name):
        """Changes the target of the prophecy and regenerates its text."""
        self.target_kingdom_name = new_target_name
        self.text = self.generate_text()
def generate_prophecy(world):
    """Generates a new, cryptic prophecy based on the world state."""
    alive_kingdoms = [k for k in world.kingdoms if k.is_alive]
    if len(alive_kingdoms) < 2:
        return None
    templates = [
        gen_prophecy_wealth_vs_stability, 
        gen_prophecy_military_vs_population,
        gen_prophecy_golden_age,
        gen_prophecy_iron_plague,
        gen_prophecy_betrayal
    ]
    template_func = random.choice(templates)
    return template_func(world, alive_kingdoms)
def gen_prophecy_wealth_vs_stability(world, alive_kingdoms):
    k1 = random.choice(alive_kingdoms)
    k2 = random.choice([k for k in alive_kingdoms if k != k1])
    components = {
        'threshold': int(k1.wealth * 1.5),
        'effect_value': -25
    }
    return Prophecy(k1, k2, 'wealth_vs_stability', components)
def gen_prophecy_military_vs_population(world, alive_kingdoms):
    k1 = random.choice(alive_kingdoms)
    k2 = random.choice([k for k in alive_kingdoms if k != k1])
    components = {
        'threshold': int(k1.military_strength * 1.2),
        'effect_value': 0.8  
    }
    return Prophecy(k1, k2, 'military_vs_population', components)
def gen_prophecy_golden_age(world, alive_kingdoms):
    """Prophecy of a golden age for a stable kingdom."""
    k1 = random.choice(alive_kingdoms)
    components = {
        'threshold': 90,  
        'effect_value': 20000  
    }
    return Prophecy(k1, k1, 'golden_age', components)
def gen_prophecy_iron_plague(world, alive_kingdoms):
    """Prophecy of a plague that strikes a kingdom's military."""
    k1 = random.choice(alive_kingdoms)
    k2 = random.choice([k for k in alive_kingdoms if k != k1])
    components = {
        'threshold': int(k1.population * 0.2), 
        'effect_value': 0.4 
    }
    return Prophecy(k1, k2, 'iron_plague', components)
def gen_prophecy_betrayal(world, alive_kingdoms):
    """Prophecy of a diplomatic betrayal caused by instability."""
    k1 = random.choice(alive_kingdoms)
    k2 = random.choice([k for k in alive_kingdoms if k != k1])
    components = {
        'threshold': 30, 
        'effect_value': -30 
    }
    return Prophecy(k1, k2, 'betrayal', components)