import time
from rich.console import Console
from src.submarine import Submarine
from src.crew import CrewManager
from src.hazard import HazardManager
from src.encounter import EncounterManager
from src.research import ResearchManager
from src.environment import EnvironmentManager
from src.mission import MissionManager
from src.module import Module
from src.minigame import RepairMinigame
from src.map import Map
from src.lore import LoreManager
console = Console()
class Game:
    def __init__(self, test_mode=False):
        self.submarine = Submarine()
        self.crew_manager = CrewManager(self.submarine)
        self.submarine.crew_manager = self.crew_manager  
        self.research_manager = ResearchManager(self.submarine)
        self.environment_manager = EnvironmentManager(self.submarine)
        self.hazard_manager = HazardManager(self.submarine, self.crew_manager)
        self.encounter_manager = EncounterManager(self.submarine, self.crew_manager, self.research_manager)
        self.lore_manager = LoreManager()
        self.mission_manager = MissionManager(self.research_manager, self.crew_manager, self.lore_manager)
        self.repair_minigame = RepairMinigame(self.submarine, self.crew_manager)
        self.map = Map()
        self.is_running = True
        self.depth = 0
        self.test_mode = test_mode
        if self.test_mode:
            self.test_commands = [
                "help",
                "status",
                "inventory",
                "relationships",
                "map",
                "journal",
                "lore",
                "upgrades",
                "craft",      
                "research",   
                "assign Echo pilot",
                "assign Jonas repair",
                'assign "Dr. Aris" research',
                "status",     
                "skill Echo view",
                "skill Jonas view",
                'skill "Dr. Aris" view',
                "system on Engine",
                "system toggle Sonar", 
                "status",
                "", "", "", "", "",  
                "scan",
                "system toggle Sonar", 
                "craft spare_part",
                "research alien_metallurgy",
                "upgrade improved_sonar",
                "inventory", 
                "upgrades",  
                "fight",      
                "silent",     
                "status",
                "", "", "", "", "",  
                "silent",     
                "system off Sonar",
                "system off Engine",
                "system off Life Support", 
                "system off Reactor",      
                "repair Engine", 
                "status",
                "quit"
            ]
            self.test_command_index = 0
    def run(self):
        console.print("[bold cyan]Welcome to Deep-Sea Submarine Exploration Simulator![/bold cyan]")
        console.print("You are the captain of a deep-sea research submarine.")
        console.print("Your mission: explore the abyss, conduct research, and survive.")
        while self.is_running:
            self.print_status()
            self.get_input()
            self.update()
            time.sleep(1)
    def update(self):
        if not self.is_running: return
        self.depth += 10 
        self.submarine.update(self.depth)
        self.crew_manager.update()
        self.hazard_manager.update(self.depth)
        self.encounter_manager.update(self.depth)
        research_points = 0
        for member in self.crew_manager.crew.values():
            if member.task == "research" and member.expertise == "Scientist":
                research_points += self.research_manager.research_points_per_turn
        if research_points > 0:
            self.research_manager.update_research(research_points)
        self.environment_manager.update()
        game_state = {
            'depth': self.depth,
            'nearby_pois': self.map.get_pois_near_depth(self.depth),
            'inventory': self.research_manager.samples
        }
        self.mission_manager.update(game_state)
        if self.encounter_manager.active_monster:
            self.encounter_manager.active_monster.attack(self.submarine, self.crew_manager)
        if self.submarine.hull_integrity <= 0:
            console.print("[bold red]Hull breach! The submarine is crushed by the pressure...[/bold red]")
            self.is_running = False
    def print_status(self):
        console.print(f"\n--- Depth: {self.depth}m ---")
        self.submarine.print_status()
        self.crew_manager.print_status()
        nearby_pois = self.map.get_pois_near_depth(self.depth)
        if nearby_pois:
            console.print("\n[bold]Nearby Points of Interest:[/bold]")
            for poi in nearby_pois:
                visited_marker = "[green](Visited)[/green]" if poi.visited else ""
                console.print(f"  - {poi.name} at {poi.depth}m {visited_marker}")
    def get_input(self):
        if self.test_mode:
            if self.test_command_index >= len(self.test_commands):
                self.is_running = False
                return
            command_str = self.test_commands[self.test_command_index]
            console.print(f"\n[bold yellow]Orders, Captain?: [/bold yellow]{command_str}")
            self.test_command_index += 1
            time.sleep(0.1) 
        else:
            command_str = console.input("\n[bold yellow]Orders, Captain?: [/bold yellow]")
        action = command_str.lower().split()
        if not action: return
        command = action[0]
        if command == "quit":
            self.is_running = False
        elif command == "status":
            self.submarine.print_status()
            self.crew_manager.print_status()
        elif command == "help":
            console.print("\n[bold]Command Reference[/bold]")
            console.print("  [cyan]Core Commands[/cyan]")
            console.print("    - help: Displays this list of commands.")
            console.print("    - quit: Exits the game.")
            console.print("    - status: Shows a full report of the submarine's status.")
            console.print("    - inventory: Displays all scientific samples and materials.")
            console.print("  [cyan]Submarine Management[/cyan]")
            console.print("    - system [on/off/toggle] [system_name]: Change a system's power state.")
            console.print("    - repair [system_name]: Repair a damaged system.")
            console.print("    - silent: Toggle silent running mode.")
            console.print("  [cyan]Crew Management[/cyan]")
            console.print("    - assign [crew_name] [task]: Assign a crew member to a task.")
            console.print("    - skill [crew_name] [view/learn] [skill_name]: View or learn a skill.")
            console.print("    - relationships: View crew relationships.")
            console.print("  [cyan]Exploration & Navigation[/cyan]")
            console.print("    - map: Displays the map.")
            console.print("    - journal: Shows active quests.")
            console.print("    - lore [entry_number]: Read a lore entry.")
            console.print("  [cyan]Crafting & Research[/cyan]")
            console.print("    - craft [item_name] [quantity]: Craft an item.")
            console.print("    - research [project_name]: Start a research project.")
            console.print("    - upgrades: View available upgrades.")
            console.print("    - upgrade [upgrade_name]: Apply an upgrade.")
            console.print("  [cyan]Interaction[/cyan]")
            console.print("    - fight: Attack a hostile creature.")
            console.print("    - trade [buy/sell] [item] [quantity]: Trade with an outpost.")
        elif command == "system" and len(action) > 2:
            verb = action[1]
            system_name_str = " ".join(action[2:]).title()
            system = self.submarine.get_system(system_name_str)
            if system:
                if system.name in self.submarine.essential_systems and verb in ["off", "toggle"]:
                    console.print(f"[bold red]Cannot deactivate essential system: {system.name}[/bold red]")
                    return
                if verb == "on":
                    system.activate()
                elif verb == "off":
                    system.deactivate()
                elif verb == "toggle":
                    if system.is_active:
                        system.deactivate()
                    else:
                        system.activate()
                else:
                    console.print(f"Unknown system command: {verb}. Use 'on', 'off', or 'toggle'.")
            else:
                console.print(f"System '{system_name_str}' not found.")
        elif command == "assign" and len(action) > 2:
            crew_name = action[1].capitalize()
            task = action[2]
            self.crew_manager.assign_task(crew_name, task)
        elif command == "upgrade" and len(action) > 1:
            upgrade_name = action[1]
            self.research_manager.apply_upgrade(upgrade_name)
        elif command == "repair" and len(action) > 1:
            system_name_input = " ".join(action[1:])
            system_key = next((key for key in self.submarine.systems if key.lower() == system_name_input), None)
            if system_key:
                if self.test_mode:
                    console.print(f"[bold cyan](TEST MODE) Attempting to repair {system_key}...[/bold cyan]")
                    if self.submarine.systems.get(system_key) and self.submarine.systems[system_key].health < 100 and self.submarine.resources['spare_parts']['level'] > 0:
                        self.submarine.systems[system_key].health = 100
                        self.submarine.resources['spare_parts']['level'] -= 1
                        console.print(f"[bold green](TEST MODE) {system_key} repaired.[/bold green]")
                    else:
                        console.print(f"[bold red](TEST MODE) Repair failed (no damage, no parts, or invalid system).[/bold red]")
                else:
                    self.repair_minigame.run(system_key)
            else:
                console.print(f"[red]System '{system_name_input}' not found.[/bold red]")
        elif command == "inventory":
            console.print("\n[bold]Submarine Inventory[/bold]")
            console.print("\n[cyan]Materials & Samples[/cyan]")
            if not self.research_manager.samples:
                console.print("  No materials or samples collected.")
            else:
                for item, quantity in self.research_manager.samples.items():
                    console.print(f"  - {item.replace('_', ' ').title()}: {quantity}")
        elif command == "upgrades":
            console.print("\n[bold]Available Submarine Upgrades[/bold]")
            for name, details in self.research_manager.upgrades.items():
                if not details.get("locked", False):
                    cost_str = ", ".join([f"{v} {k}" for k, v in details["cost"].items()])
                    applied_str = "[Applied]" if details["applied"] else ""
                    console.print(f"  - {name.replace('_', ' ').title()}: {details['description']} (Cost: {cost_str}) {applied_str}")
        elif command == "fight":
            if self.encounter_manager.active_monster:
                damage = 10 
                damage += self.crew_manager.get_combat_power()
                if self.research_manager.upgrades["torpedo_system"]["applied"]:
                    damage += 10
                self.encounter_manager.active_monster.take_damage(damage)
                if self.encounter_manager.active_monster.health <= 0:
                    console.print(f"[bold green]The {self.encounter_manager.active_monster.name} is defeated![/bold green]")
                    self.crew_manager.broadcast_event("monster_defeated")
                    for item, quantity in self.encounter_manager.active_monster.loot.items():
                        self.research_manager.add_sample(item, quantity)
                    self.encounter_manager.active_monster = None
            else:
                console.print("[bold yellow]There is nothing to fight.[/bold yellow]")
        elif command == "skill" and len(action) > 1:
            crew_name = action[1].capitalize()
            member = self.crew_manager.get_member(crew_name)
            if not member:
                console.print(f"[red]Crew member '{crew_name}' not found.[/red]")
                return
            if len(action) > 2:
                verb = action[2]
                if verb == "learn" and len(action) > 3:
                    skill_name = action[3]
                    member.learn_skill(skill_name)
                elif verb == "view":
                    self.crew_manager.print_skill_tree(crew_name)
                else:
                    console.print(f"Unknown skill command '{verb}'. Use 'view' or 'learn'.")
            else:
                self.crew_manager.print_skill_tree(crew_name)
        elif command == "module" and len(action) > 1:
            module_name = action[1]
            if module_name == "extra_battery":
                module = Module(module_name, "Increases max power by 20.", lambda sub: sub.systems["Reactor"].__setitem__('power_output', sub.systems["Reactor"].__getitem__('power_output') + 20))
                self.submarine.install_module(module_name, module)
        elif command == "trade" and len(action) > 3:
            if self.encounter_manager.active_outpost:
                item = action[2]
                quantity = int(action[3])
                self.encounter_manager.active_outpost.trade(self.submarine, item, quantity, action[1])
            else:
                console.print("[bold red]There is no outpost to trade with.[/bold red]")
        elif command == "silent":
            self.submarine.toggle_silent_running()
        elif command == "relationships":
            self.crew_manager.print_relationships()
        elif command == "map":
            self.map.print_map(self.depth)
        elif command == "journal":
            self.mission_manager.print_journal()
        elif command == "lore":
            if len(action) > 1:
                try:
                    index = int(action[1])
                    self.lore_manager.print_lore_entry(index)
                except ValueError:
                    console.print("[red]Invalid lore entry number.[/red]")
            else:
                self.lore_manager.print_lore_index()
        elif command == "craft":
            if len(action) > 1:
                item_name = action[1]
                quantity = 1
                if len(action) > 2:
                    try:
                        quantity = int(action[2])
                    except ValueError:
                        console.print("[red]Invalid quantity.[/red]")
                        return
                self.research_manager.craft_item(item_name, quantity)
            else:
                self.research_manager.print_recipes()
        elif command == "research":
            if len(action) > 1:
                project_name = action[1]
                self.research_manager.start_research(project_name)
            else:
                self.research_manager.print_research_projects()
        else:
            console.print("Unknown command. Type 'help' for a list of commands.")
if __name__ == "__main__":
    game = Game(test_mode=True)
    try:
        game.run()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[bold red]Emergency shutdown![/bold red]")