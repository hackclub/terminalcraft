"""
This module defines the base Event class and various subclasses
(e.g., War, Famine, Diplomatic) that affect the game world.
"""
import random
from colorama import Fore
from abc import ABC, abstractmethod
class GameEvent(ABC):
    """Base class for all events in the game."""
    def __init__(self, name, description, num_targets=1):
        self.name = name
        self.description = description
        self.num_targets = num_targets
    @abstractmethod
    def execute(self, world, renderer, targets):
        """The logic that occurs when the event happens."""
        pass
class GoodHarvest(GameEvent):
    """A bountiful harvest increases food reserves."""
    def __init__(self):
        super().__init__("GoodHarvest", "A bountiful harvest increases food reserves.")
    def execute(self, world, renderer, targets):
        target_kingdom = targets[0]
        if not target_kingdom.is_alive: return
        food_bonus = int(target_kingdom.population * 0.5)
        target_kingdom.food_reserves += food_bonus
        renderer.display_message(f"{self.description} in {target_kingdom.name}! Their granaries overflow.", 'green')
class BanditRaid(GameEvent):
    """Bandits raid a kingdom, reducing wealth and stability."""
    def __init__(self):
        super().__init__("BanditRaid", "Bandits raid a kingdom, reducing wealth and stability.")
    def execute(self, world, renderer, targets):
        target_kingdom = targets[0]
        if not target_kingdom.is_alive: return
        wealth_lost = int(target_kingdom.wealth * 0.1)
        target_kingdom.wealth -= wealth_lost
        target_kingdom.stability -= 5
        renderer.display_message(f"{self.description} plagues {target_kingdom.name}! Gold is stolen and the people are frightened.", 'yellow')
class RoyalWedding(GameEvent):
    """A royal wedding improves relations and stability between two kingdoms."""
    def __init__(self):
        super().__init__("RoyalWedding", "A royal wedding improves relations and stability between two kingdoms.", 2)
    def execute(self, world, renderer, targets):
        k1, k2 = targets[0], targets[1]
        if not k1.is_alive or not k2.is_alive: return
        k1.stability += 10
        k2.stability += 10
        renderer.display_message(f"{self.description} between {k1.name} and {k2.name} brings joy and unity!", 'cyan')
class CatastropheEvent(GameEvent):
    """Base class for world-shaking catastrophe events triggered by high tension."""
    pass
class TheMadKing(CatastropheEvent):
    """A kingdom's ruler goes insane, wrecking stability and declaring a foolish war."""
    def __init__(self):
        super().__init__("TheMadKing", "A kingdom's ruler goes insane, wrecking stability and declaring a foolish war.")
    def execute(self, world, renderer, targets):
        target = targets[0]
        if not target.is_alive: return
        renderer.display_message(f"CATASTROPHE: A madness descends upon the ruler of {target.name}!", 'red')
        target.stability = max(5, target.stability - 50)
        target.wealth = int(target.wealth * 0.5)
        renderer.display_message(f"Their mind broken, they squander the treasury and terrorize the court. Stability in {target.name} has plummeted.", 'red')
class TheGreatPlague(CatastropheEvent):
    """A deadly plague sweeps through a kingdom."""
    def __init__(self):
        super().__init__("TheGreatPlague", "A deadly plague sweeps through a kingdom.")
    def execute(self, world, renderer, targets):
        target = targets[0]
        if not target.is_alive: return
        renderer.display_message(f"CATASTROPHE: The Great Plague has come to {target.name}!", 'red')
        original_pop = target.population
        target.population = int(original_pop * 0.5) 
        renderer.display_message(f"A sickening miasma settles. {original_pop - target.population:,} souls are lost to the pestilence.", 'red')
class TheSchism(CatastropheEvent):
    """A kingdom is violently split in two, creating a new, hostile kingdom."""
    def __init__(self):
        super().__init__("TheSchism", "A kingdom is violently split in two, creating a new, hostile kingdom.")
    def execute(self, world, renderer, targets):
        from engine.kingdom import Kingdom 
        original_kingdom = targets[0]
        if not original_kingdom.is_alive or len(world.kingdoms) >= 8: 
            return
        renderer.display_message(f"CATASTROPHE: A bitter schism tears {original_kingdom.name} apart!", 'red')
        new_kingdom_name = f"{original_kingdom.name} Rebels"
        new_kingdom = Kingdom(
            name=new_kingdom_name,
            traits=[random.choice(["Fanatical", "Vengeful", "Zealous"])],
            population=int(original_kingdom.population * 0.4),
            stability=40,
            military_strength=int(original_kingdom.military_strength * 0.5),
            food_reserves=int(original_kingdom.food_reserves * 0.3),
            wealth=int(original_kingdom.wealth * 0.2)
        )
        original_kingdom.population = int(original_kingdom.population * 0.6)
        original_kingdom.military_strength = int(original_kingdom.military_strength * 0.5)
        original_kingdom.stability = max(20, original_kingdom.stability - 30)
        world.kingdoms.append(new_kingdom)
        renderer.display_message(f"The {new_kingdom_name} have risen, carving out their own domain from the chaos.", 'red')
EVENT_TYPE_MAP = {
    'GoodHarvest': GoodHarvest,
    'BanditRaid': BanditRaid,
    'RoyalWedding': RoyalWedding,
}
class TheGreatFamine(CatastropheEvent):
    """A devastating famine strikes a kingdom, wiping out food stores and population."""
    def __init__(self):
        super().__init__("The Great Famine", "A crippling famine that decimates the population.")
    def execute(self, world, renderer, targets):
        target = targets[0]
        if not target.is_alive: return
        renderer.display_message(f"CATASTROPHE: The fields turn to dust and the granaries are empty in {target.name}!", 'red')
        original_pop = target.population
        target.food_reserves = 0
        target.population = int(original_pop * 0.7) 
        target.stability -= 20
        renderer.display_message(f"The Great Famine claims {original_pop - target.population:,} souls. The kingdom is on the brink of collapse.", 'red')
class CivilWar(CatastropheEvent):
    """A brutal internal conflict tears a kingdom apart."""
    def __init__(self):
        super().__init__("Civil War", "A bitter internal conflict that shatters a kingdom.")
    def execute(self, world, renderer, targets):
        target = targets[0]
        if not target.is_alive: return
        renderer.display_message(f"CATASTROPHE: Brother turns against brother in a bloody Civil War in {target.name}!", 'red')
        target.stability = 10 
        target.military_strength = int(target.military_strength * 0.3)
        target.wealth = int(target.wealth * 0.4)
        renderer.display_message(f"The armies of {target.name} are broken, its treasury looted, and its people divided.", 'red')
class DragonsIre(CatastropheEvent):
    """A mythical dragon awakens and unleashes its fury upon a kingdom."""
    def __init__(self):
        super().__init__("Dragon's Ire", "The awakening of a dragon that brings ruin.")
    def execute(self, world, renderer, targets):
        target = targets[0]
        if not target.is_alive: return
        renderer.display_message(f"CATASTROPHE: A great Dragon, ancient and terrible, descends upon {target.name}!", 'red')
        target.population = int(target.population * 0.5)
        target.military_strength = int(target.military_strength * 0.2)
        target.wealth = 0
        target.stability = 5
        renderer.display_message(f"Fields are scorched, cities turned to ash, and the treasury is now the dragon's hoard. {target.name} is left in ruins.", 'red')
EVENT_TYPE_MAP = {
    'GoodHarvest': GoodHarvest,
    'BanditRaid': BanditRaid,
    'RoyalWedding': RoyalWedding,
}
CATASTROPHE_TYPE_LIST = [TheMadKing, TheGreatPlague, TheSchism, TheGreatFamine, CivilWar, DragonsIre]