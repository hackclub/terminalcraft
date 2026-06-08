"""
This module defines the Oracle, which is the player's persona.
It will handle all player actions, such as predictions, influences,
and prophecy manipulation, and manage the core 'Tension' mechanic.
"""
import random
from colorama import Fore
class Oracle:
    """Represents the player-controlled Oracle AI."""
    def predict_famine(self, kingdom):
        """Predicts the likelihood of a famine in a given kingdom."""
        food_per_capita = kingdom.food_reserves / (kingdom.population or 1)
        if food_per_capita < 2:
            return f"{Fore.RED}Famine is almost certain for {kingdom.name}. Their reserves are critically low."
        elif food_per_capita < 5:
            return f"{Fore.YELLOW}The risk of famine is high for {kingdom.name}. A single bad harvest could spell disaster."
        else:
            return f"{Fore.GREEN}The food stores of {kingdom.name} are bountiful. Famine is unlikely."
    def predict_war(self, k1, k2):
        """Predicts the outcome of a potential war between two kingdoms."""
        if k1 == k2:
            return f"{Fore.CYAN}A kingdom cannot go to war with itself... yet."
        k1_power = k1.military_strength * (k1.stability / 100)
        k2_power = k2.military_strength * (k2.stability / 100)
        if 'Expansionist' in k1.traits:
            k1_power *= 1.2
        if 'Cautious' in k1.traits:
            k1_power *= 0.9
        if 'Expansionist' in k2.traits:
            k2_power *= 1.2
        if 'Cautious' in k2.traits:
            k2_power *= 0.9
        power_ratio = k1_power / (k2_power or 1)
        if power_ratio > 1.5:
            return f"{Fore.GREEN}In a conflict, {k1.name} would likely achieve a decisive victory over {k2.name}."
        elif power_ratio > 1.1:
            return f"{Fore.YELLOW}{k1.name} holds a slight advantage over {k2.name}. The war would be costly."
        elif power_ratio < 0.66:
            return f"{Fore.GREEN}{k2.name} would likely crush {k1.name} with ease."
        elif power_ratio < 0.9:
            return f"{Fore.YELLOW}{k2.name} appears to have the upper hand against {k1.name}."
        else:
            return f"{Fore.CYAN}The armies of {k1.name} and {k2.name} are evenly matched. A war would lead to a bloody stalemate."
    def influence_harvest(self, world, kingdom):
        """Subtly influences a kingdom's harvest, increasing tension."""
        if not kingdom.is_alive:
            return f"{kingdom.name} is beyond your influence."
        kingdom.food_reserves = int(kingdom.food_reserves * 1.25)
        world.global_tension += 2.0
        return f"A blessing of fertility settles upon the fields of {kingdom.name}, but the world tenses."
    def influence_stability(self, world, kingdom):
        """Subtly influences a kingdom's stability, increasing tension."""
        if not kingdom.is_alive:
            return f"{kingdom.name} is beyond your influence."
        kingdom.stability = min(100, kingdom.stability + 10)
        world.global_tension += 3.0
        return f"A whisper of reassurance calms the hearts of {kingdom.name}'s people. The world feels the strain."