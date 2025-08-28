"""
This module defines the Kingdom class, which will represent each individual kingdom
in the game world, with its own attributes, goals, and behaviors.
"""
import random
from engine.wonder import GreatWonder
from engine.hero import Hero
class Kingdom:
    """Represents a single kingdom in the world."""
    def __init__(self, name, traits, population, stability, military_strength, food_reserves, wealth):
        self.name = name
        self.traits = traits
        self.population = int(population)
        self.stability = int(stability)  
        self.military_strength = int(military_strength)
        self.food_reserves = int(food_reserves)  
        self.wealth = int(wealth)  
        self.relationships = {}  
        self.allies = []
        self.rivals = []
        self.is_alive = True
        self.wonders = []  
        self.wonder_project = None  
        self.heroes = [] 
    def __repr__(self):
        return f"Kingdom({self.name}, Pop: {self.population}, Stab: {self.stability})"
    def get_diplomatic_stance(self, kingdom_name):
        """Returns the diplomatic stance towards another kingdom as a string."""
        if kingdom_name in self.allies:
            return "Ally"
        if kingdom_name in self.rivals:
            return "Rival"
        return "Neutral"
    def _consume_food(self):
        """Population consumes food. Returns True if there's enough food, False if famine strikes."""
        consumption = self.population // 10
        self.food_reserves -= consumption
        if self.food_reserves < 0:
            famine_severity = abs(self.food_reserves)
            self.population -= famine_severity
            self.stability -= 10
            self.food_reserves = 0
            if self.population <= 0:
                self.is_alive = False
            return False
        return True
    def _collect_taxes(self):
        """Collect taxes from the population, modified by wonders."""
        tax_rate = 0.1 + (self.stability / 2000)
        new_wealth = int(self.population * tax_rate)
        for wonder in self.wonders:
            if 'wealth_modifier' in wonder.effect:
                new_wealth = int(new_wealth * wonder.effect['wealth_modifier'])
        self.wealth += new_wealth
        return new_wealth 
    def _update_stability(self):
        """Update stability based on various factors and wonders."""
        if self.stability > 50:
            self.stability -= 1
        elif self.stability < 50:
            self.stability += 1
        if self.food_reserves < self.population / 5:
            self.stability -= 5
        for wonder in self.wonders:
            if 'stability_bonus' in wonder.effect:
                self.stability += wonder.effect['stability_bonus']
        self.stability = max(0, min(100, self.stability))
    def _update_population(self):
        """Update population based on food and stability."""
        growth_rate = (self.stability / 5000) * (self.food_reserves / (self.population * 2))
        growth_rate = max(-0.05, min(0.05, growth_rate))
        self.population += int(self.population * growth_rate)
        if self.population <= 0:
            self.is_alive = False
            self.population = 0
    def _update_relationships(self, world):
        """Update diplomatic relationships with other kingdoms."""
        for other_kingdom in world.kingdoms:
            if other_kingdom == self or not other_kingdom.is_alive:
                continue
            if other_kingdom.name not in self.relationships:
                self.relationships[other_kingdom.name] = 0
            modifier = 0
            if 'Expansionist' in self.traits and 'Expansionist' in other_kingdom.traits: modifier -= 5
            if 'Peaceful' in self.traits and 'Peaceful' in other_kingdom.traits: modifier += 5
            if 'Xenophobic' in self.traits: modifier -= 3
            if 'Honorable' in self.traits and 'Deceitful' in other_kingdom.traits: modifier -= 10
            for hero in self.heroes:
                if 'diplomacy_bonus' in hero.effect:
                    modifier += hero.effect['diplomacy_bonus']
            self_military_power = self.military_strength + sum(h.effect.get('military_bonus', 0) for h in self.heroes)
            other_military_power = other_kingdom.military_strength + sum(h.effect.get('military_bonus', 0) for h in other_kingdom.heroes)
            power_difference = self_military_power - other_military_power
            if 'Expansionist' in self.traits and power_difference > 0: modifier -= 2
            if power_difference > 5000: modifier -= 3
            self.relationships[other_kingdom.name] = max(-100, min(100, self.relationships[other_kingdom.name] + modifier))
            if self.relationships[other_kingdom.name] > 75 and other_kingdom.name not in self.allies:
                self.allies.append(other_kingdom.name)
                if other_kingdom.name in self.rivals: self.rivals.remove(other_kingdom.name)
            elif self.relationships[other_kingdom.name] < -75 and other_kingdom.name not in self.rivals:
                self.rivals.append(other_kingdom.name)
                if other_kingdom.name in self.allies: self.allies.remove(other_kingdom.name)
            elif -25 < self.relationships[other_kingdom.name] < 25:
                if other_kingdom.name in self.allies: self.allies.remove(other_kingdom.name)
                if other_kingdom.name in self.rivals: self.rivals.remove(other_kingdom.name)
    def _update_wonders(self, world, income):
        """Update progress on wonder construction."""
        if self.wonder_project:
            investment = int(income * 0.2) 
            for hero in self.heroes:
                if 'wonder_speed_modifier' in hero.effect:
                    investment = int(investment * hero.effect['wonder_speed_modifier'])
            if self.wealth >= investment:
                self.wealth -= investment
                self.wonder_project.progress += investment
            if self.wonder_project.is_complete():
                completed_wonder = self.wonder_project
                self.wonders.append(completed_wonder)
                self.wonder_project = None
                if 'military_modifier' in completed_wonder.effect:
                    self.military_strength = int(self.military_strength * completed_wonder.effect['military_modifier'])
    def update(self, world):
        """Updates the kingdom's state for a new turn."""
        if not self.is_alive:
            return
        self._consume_food()
        income = self._collect_taxes()
        self._update_stability()
        self._update_population()
        self._update_relationships(world)
        self._update_wonders(world, income)
        if self.population <= 0 or self.stability <= 0:
            self.is_alive = False