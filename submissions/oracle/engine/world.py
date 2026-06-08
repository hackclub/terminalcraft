"""
This module will manage the state of the game world, including all kingdoms,
the current date, and global variables like world tension.
"""
import json
import random
from engine.kingdom import Kingdom
from engine.events import EVENT_TYPE_MAP, CATASTROPHE_TYPE_LIST
from engine.prophecy import generate_prophecy
from engine.hero import create_hero, HERO_TEMPLATES
class World:
    """Represents the entire game world."""
    def __init__(self, kingdom_data_path='data/kingdom_data.json', event_data_path='data/event_data.json'):
        self.kingdoms = []
        self.current_year = 1
        self.global_tension = 0.0
        self.active_prophecies = []
        self.tension_threshold = 50.0
        self.last_catastrophe_year = -999
        self._kingdom_data_path = kingdom_data_path
        self._event_data_path = event_data_path
        self.event_templates = []
        self.available_heroes = []
        self.active_heroes = []
        self._setup_world()
    def _setup_world(self):
        """Loads initial world state from data files."""
        with open(self._kingdom_data_path, 'r') as f:
            kingdom_data = json.load(f)["kingdoms"]
            for kd in kingdom_data:
                self.kingdoms.append(Kingdom(**kd))
        for event_class in EVENT_TYPE_MAP.values():
            self.event_templates.append(event_class())
        for k1 in self.kingdoms:
            for k2 in self.kingdoms:
                if k1 != k2:
                    k1.relationships[k2.name] = 0
    def get_kingdom_by_name(self, name):
        """Finds a kingdom object by its name."""
        for kingdom in self.kingdoms:
            if kingdom.name.lower() == name.lower():
                return kingdom
        return None
    def encourage_alliance(self, k1, k2):
        """Directly boosts relationship between two kingdoms."""
        k1.relationships[k2.name] = min(100, k1.relationships.get(k2.name, 0) + 40)
        k2.relationships[k1.name] = min(100, k2.relationships.get(k1.name, 0) + 40)
    def sow_discord(self, k1, k2):
        """Directly harms relationship between two kingdoms."""
        k1.relationships[k2.name] = max(-100, k1.relationships.get(k2.name, 0) - 40)
        k2.relationships[k1.name] = max(-100, k2.relationships.get(k1.name, 0) - 40)
    def _trigger_random_event(self, renderer):
        """Randomly triggers an event from the list of templates."""
        if random.random() < 0.25 and self.event_templates:
            event_template = random.choice(self.event_templates)
            num_targets = 2 if 'kingdom2' in event_template.description_template else 1
            alive_kingdoms = [k for k in self.kingdoms if k.is_alive]
            if len(alive_kingdoms) < num_targets:
                return 
            targets = random.sample(alive_kingdoms, num_targets)
            event_template.execute(self, renderer, targets)
    def _check_prophecies(self, renderer):
        """Check and trigger any fulfilled prophecies."""
        fulfilled_prophecies = []
        for prophecy in self.active_prophecies:
            if prophecy.check_and_trigger(self, renderer):
                fulfilled_prophecies.append(prophecy)
        self.active_prophecies = [p for p in self.active_prophecies if not p.is_fulfilled]
    def _check_for_catastrophe(self, renderer):
        """Checks if global tension has reached a threshold and triggers a catastrophe."""
        if self.global_tension >= self.tension_threshold and (self.current_year - self.last_catastrophe_year) > 20:
            alive_kingdoms = [k for k in self.kingdoms if k.is_alive]
            if not alive_kingdoms:
                return
            renderer.display_message("The Oracle's vision blurs... the world strains under the weight of immense tension!", 'red')
            catastrophe_class = random.choice(CATASTROPHE_TYPE_LIST)
            catastrophe = catastrophe_class()
            num_targets = catastrophe.num_targets
            if len(alive_kingdoms) < num_targets:
                return 
            targets = random.sample(alive_kingdoms, num_targets)
            catastrophe.execute(self, renderer, targets)
            self.global_tension = max(0, self.global_tension - 40.0)
            self.last_catastrophe_year = self.current_year
    def _spawn_hero(self, renderer):
        """A small chance to spawn a new hero each year."""
        if random.random() < 0.1 and len(self.available_heroes) < 3:
            existing_hero_names = [h.name for h in self.active_heroes] + [h.name for h in self.available_heroes]
            available_templates = {k: v for k, v in HERO_TEMPLATES.items() if v['name'] not in existing_hero_names}
            if not available_templates:
                return
            template_name = random.choice(list(available_templates.keys()))
            new_hero = create_hero(template_name)
            self.available_heroes.append(new_hero)
            renderer.display_message(f"A new legend is born! {new_hero.name}, {new_hero.title}, has appeared.", 'yellow')
    def _update_heroes(self, renderer):
        """Update active heroes, checking their lifespan."""
        retired_heroes = []
        for hero in self.active_heroes:
            hero.tick()
            if hero.lifespan <= 0:
                retired_heroes.append(hero)
        for hero in retired_heroes:
            self.active_heroes.remove(hero)
            if hero.location:
                hero.location.heroes.remove(hero)
                renderer.display_message(f"{hero.name} has passed into legend after years of service to {hero.location.name}.", 'cyan')
    def tick(self, renderer):
        """Advances the game state by one turn (e.g., a year)."""
        self._check_for_catastrophe(renderer)
        self._update_heroes(renderer)
        for kingdom in self.kingdoms:
            kingdom.update(self)
        self._check_prophecies(renderer)
        self._trigger_random_event(renderer)
        self._spawn_hero(renderer)
        if self.current_year % 10 == 0 and len(self.active_prophecies) < 3:
            new_prophecy = generate_prophecy(self)
            if new_prophecy:
                self.active_prophecies.append(new_prophecy)
                renderer.display_message(f"A new prophecy echoes in the ether: \"{new_prophecy.text}\"", "magenta")
        self.current_year += 1