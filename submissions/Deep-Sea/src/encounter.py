import random
from src.monster import Monster
from src.outpost import Outpost
from src.faction import Faction
class EncounterManager:
    def __init__(self, submarine, crew_manager, research_manager):
        self.submarine = submarine
        self.crew_manager = crew_manager
        self.research_manager = research_manager
        self.fauna = {
            "Glow-Whale": {"description": "A gentle giant that illuminates the abyss.", "aggressive": False, "loot": "whale_biomatter"},
            "Reaper-Leviathan": {"description": "A massive predator with a taste for metal.", "aggressive": True, "health": 100, "attack": 20, "loot": "leviathan_scale"},
            "Colossal Squid": {"description": "A legendary cephalopod of immense size and power.", "aggressive": True, "health": 150, "attack": 25, "loot": "colossal_squid_heart"},
            "Frilled Shark": {"description": "A living fossil with rows of needle-like teeth.", "aggressive": False, "loot": "shark_teeth"},
            "Goblin Shark": {"description": "A bizarre creature with a protruding jaw.", "aggressive": False, "loot": "shark_jaw"},
            "Phantom Jellyfish": {"description": "A mysterious jellyfish with a ghostly appearance.", "aggressive": False, "loot": "jellyfish_venom"}
        }
        self.outposts = {
            "hydro-corp": Outpost("Hydro-Corp Outpost", Faction("Hydro-Corp"))
        }
        self.active_monster = None
        self.active_outpost = None
    def update(self, depth):
        messages = []
        encounter_chance = 0.3
        if self.research_manager.upgrades["improved_sonar"]["applied"]:
            encounter_chance += self.submarine.noise_level / 100
        if self.submarine.systems["Sonar"].is_active and random.random() < encounter_chance:
            messages.extend(self.trigger_encounter(depth))
        return messages
    def trigger_encounter(self, depth):
        messages = []
        self.active_monster = None
        self.active_outpost = None
        encounter_type = random.choice(["fauna", "point_of_interest", "outpost"])
        if encounter_type == "fauna":
            species_name = random.choice(list(self.fauna.keys()))
            species_data = self.fauna[species_name]
            messages.append(f"[bold magenta]Sonar has detected a lifeform! It looks like a {species_name}.[/bold magenta]")
            if species_data["aggressive"]:
                messages.append(f"[bold red]The {species_name} is aggressive![/bold red]")
                loot = {species_data["loot"]: 1}
                self.active_monster = Monster(species_name, species_data["health"], species_data["attack"], loot)
            else:
                messages.extend(self.research_manager.add_sample(species_data["loot"], 1))
        elif encounter_type == "point_of_interest":
            messages.append("[bold yellow]Sonar has detected a strange geological formation.[/bold yellow]")
            if random.random() < 0.5:
                resource_type = random.choice(['fuel', 'spare_parts'])
                amount = random.randint(5, 20)
                self.submarine.resources[resource_type]['level'] += amount
                messages.append(f"[bold green]We salvaged {amount} units of {resource_type}![/bold green]")
        elif encounter_type == "outpost":
            outpost_name = random.choice(list(self.outposts.keys()))
            self.active_outpost = self.outposts[outpost_name]
            messages.append(f"[bold yellow]Sonar has detected an outpost: {self.active_outpost.name}[/bold yellow]")
        return messages