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
class Game:
    def __init__(self):
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
        self.output_messages = []
        self.minigame_active = False
    def start_game(self):
        self.output_messages.append("[bold cyan]Welcome to Deep-Sea Submarine Exploration Simulator![/bold cyan]")
        self.output_messages.append("You are the captain of a deep-sea research submarine.")
        self.output_messages.append("Your mission: explore the abyss, conduct research, and survive.")
        return self.get_output_messages()
    def update(self):
        if not self.is_running: return []
        messages = []
        self.depth += 10
        messages.extend(self.submarine.update(self.depth))
        messages.extend(self.crew_manager.update())
        messages.extend(self.hazard_manager.update(self.depth))
        messages.extend(self.encounter_manager.update(self.depth))
        research_points = 0
        for member in self.crew_manager.crew.values():
            if member.task == "research" and member.expertise == "Scientist":
                research_points += self.research_manager.research_points_per_turn
        if research_points > 0:
            messages.extend(self.research_manager.update_research(research_points))
        messages.extend(self.environment_manager.update())
        game_state = {
            'depth': self.depth,
            'nearby_pois': self.map.get_pois_near_depth(self.depth),
            'inventory': self.research_manager.samples
        }
        messages.extend(self.mission_manager.update(game_state))
        if self.encounter_manager.active_monster:
            messages.extend(self.encounter_manager.active_monster.attack(self.submarine, self.crew_manager))
        if self.submarine.hull_integrity <= 0:
            messages.append("[bold red]Hull breach! The submarine is crushed by the pressure...[/bold red]")
            self.is_running = False
        self.output_messages.extend(messages)
        return self.get_output_messages()
    def get_status_report(self):
        report = []
        report.append(f"\n--- Depth: {self.depth}m ---")
        report.extend(self.submarine.get_status_report())
        report.extend(self.crew_manager.get_status_report())
        nearby_pois = self.map.get_pois_near_depth(self.depth)
        if nearby_pois:
            report.append("\n[bold]Nearby Points of Interest:[/bold]")
            for poi in nearby_pois:
                visited_marker = "[green](Visited)[/green]" if poi.visited else ""
                report.append(f"  - {poi.name} at {poi.depth}m {visited_marker}")
        return report
    def get_output_messages(self):
        messages = self.output_messages[:]
        self.output_messages.clear()
        return messages
    def process_minigame_input(self, user_input, time_taken):
        if not self.minigame_active:
            return []
        messages = self.repair_minigame.evaluate(user_input, time_taken)
        self.output_messages.extend(messages)
        self.minigame_active = False
        return self.get_output_messages()
    def process_command(self, command_text):
        action = command_text.lower().split()
        if not action: return self.get_output_messages()
        command = action[0]
        if command == "quit":
            self.is_running = False
        elif command == "status":
            self.output_messages.extend(self.get_status_report())
        elif command == "help":
            self.output_messages.append("\n[bold]Command Reference[/bold]")
            self.output_messages.append("  [cyan]Core Commands[/cyan]")
            self.output_messages.append("    - help: Displays this list of commands.")
            self.output_messages.append("    - quit: Exits the game.")
            self.output_messages.append("    - status: Shows a full report of the submarine's status.")
            self.output_messages.append("    - inventory: Displays all scientific samples and materials.")
            self.output_messages.append("  [cyan]Submarine Management[/cyan]")
            self.output_messages.append("    - system [on/off/toggle] [system_name]: Change a system's power state.")
            self.output_messages.append("    - repair [system_name]: Repair a damaged system.")
            self.output_messages.append("    - silent: Toggle silent running mode.")
            self.output_messages.append("  [cyan]Crew Management[/cyan]")
            self.output_messages.append("    - assign [crew_name] [task]: Assign a crew member to a task.")
            self.output_messages.append("    - skill [crew_name] [view/learn] [skill_name]: View or learn a skill.")
            self.output_messages.append("    - relationships: View crew relationships.")
            self.output_messages.append("  [cyan]Exploration & Navigation[/cyan]")
            self.output_messages.append("    - map: Displays the map.")
            self.output_messages.append("    - journal: Shows active quests.")
            self.output_messages.append("    - lore [entry_number]: Read a lore entry.")
            self.output_messages.append("  [cyan]Crafting & Research[/cyan]")
            self.output_messages.append("    - craft [item_name] [quantity]: Craft an item.")
            self.output_messages.append("    - research [project_name]: Start a research project.")
            self.output_messages.append("    - upgrades: View available upgrades.")
            self.output_messages.append("    - upgrade [upgrade_name]: Apply an upgrade.")
            self.output_messages.append("  [cyan]Interaction[/cyan]")
            self.output_messages.append("    - fight: Attack a hostile creature.")
            self.output_messages.append("    - trade [buy/sell] [item] [quantity]: Trade with an outpost.")
        elif command == "system" and len(action) > 2:
            verb = action[1]
            system_name_str = " ".join(action[2:]).title()
            system = self.submarine.get_system(system_name_str)
            if system:
                if system.name in self.submarine.essential_systems and verb in ["off", "toggle"]:
                    self.output_messages.append(f"[bold red]Cannot deactivate essential system: {system.name}[/bold red]")
                elif verb == "on":
                    self.output_messages.extend(system.activate())
                elif verb == "off":
                    self.output_messages.extend(system.deactivate())
                elif verb == "toggle":
                    if system.is_active:
                        self.output_messages.extend(system.deactivate())
                    else:
                        self.output_messages.extend(system.activate())
                else:
                    self.output_messages.append(f"Unknown system command: {verb}. Use 'on', 'off', or 'toggle'.")
            else:
                self.output_messages.append(f"System '{system_name_str}' not found.")
        elif command == "assign" and len(action) > 2:
            crew_name = action[1].capitalize()
            task = action[2]
            self.output_messages.extend(self.crew_manager.assign_task(crew_name, task))
        elif command == "upgrade" and len(action) > 1:
            upgrade_name = action[1]
            self.output_messages.extend(self.research_manager.apply_upgrade(upgrade_name))
        elif command == "repair" and len(action) > 1:
            system_name_input = " ".join(action[1:])
            system_key = next((key for key in self.submarine.systems if key.lower() == system_name_input.lower()), None)
            if system_key:
                messages = self.repair_minigame.start(system_key)
                self.output_messages.extend(messages)
                if messages and "Initiating" in messages[0]:
                    self.minigame_active = True
            else:
                self.output_messages.append(f"[red]System '{system_name_input}' not found.[/bold red]")
        elif command == "inventory":
            self.output_messages.append("\n[bold]Submarine Inventory[/bold]")
            self.output_messages.append("\n[cyan]Materials & Samples[/cyan]")
            if not self.research_manager.samples:
                self.output_messages.append("  No materials or samples collected.")
            else:
                for item, quantity in self.research_manager.samples.items():
                    self.output_messages.append(f"  - {item.replace('_', ' ').title()}: {quantity}")
        elif command == "upgrades":
            self.output_messages.extend(self.research_manager.get_recipes_report())
        elif command == "fight":
            if self.encounter_manager.active_monster:
                damage = 10 
                damage += self.crew_manager.get_combat_power()
                if self.research_manager.upgrades["torpedo_system"]["applied"]:
                    damage += 10
                self.output_messages.extend(self.encounter_manager.active_monster.take_damage(damage))
                if self.encounter_manager.active_monster.health <= 0:
                    self.output_messages.append(f"[bold green]The {self.encounter_manager.active_monster.name} is defeated![/bold green]")
                    self.output_messages.extend(self.crew_manager.broadcast_event("monster_defeated"))
                    for item, quantity in self.encounter_manager.active_monster.loot.items():
                        self.output_messages.extend(self.research_manager.add_sample(item, quantity))
                    self.encounter_manager.active_monster = None
            else:
                self.output_messages.append("[bold yellow]There is nothing to fight.[/bold yellow]")
        elif command == "skill" and len(action) > 1:
            crew_name = action[1].capitalize()
            member = self.crew_manager.get_member(crew_name)
            if not member:
                self.output_messages.append(f"[red]Crew member '{crew_name}' not found.[/red]")
            elif len(action) > 2:
                verb = action[2]
                if verb == "learn" and len(action) > 3:
                    skill_name = action[3]
                    self.output_messages.extend(member.learn_skill(skill_name))
                elif verb == "view":
                    self.output_messages.extend(self.crew_manager.get_skill_tree_report(crew_name))
                else:
                    self.output_messages.append(f"Unknown skill command '{verb}'. Use 'view' or 'learn'.")
            else:
                self.output_messages.extend(self.crew_manager.get_skill_tree_report(crew_name))
        elif command == "module" and len(action) > 1:
            module_name = action[1]
            if module_name == "extra_battery":
                module = Module(module_name, "Increases max power by 20.", lambda sub: sub.systems["Reactor"].__setitem__('power_output', sub.systems["Reactor"].__getitem__('power_output') + 20))
                self.output_messages.extend(self.submarine.install_module(module_name, module))
        elif command == "trade" and len(action) > 3:
            if self.encounter_manager.active_outpost:
                item = action[2]
                quantity = int(action[3])
                self.output_messages.extend(self.encounter_manager.active_outpost.trade(self.submarine, item, quantity, action[1]))
            else:
                self.output_messages.append("[bold red]There is no outpost to trade with.[/bold red]")
        elif command == "silent":
            self.output_messages.extend(self.submarine.toggle_silent_running())
        elif command == "relationships":
            self.output_messages.extend(self.crew_manager.get_relationships_report())
        elif command == "map":
            self.output_messages.extend(self.map.get_map_report(self.depth))
        elif command == "journal":
            self.output_messages.extend(self.mission_manager.get_journal_report())
        elif command == "lore":
            if len(action) > 1:
                try:
                    index = int(action[1])
                    self.output_messages.extend(self.lore_manager.get_lore_entry_report(index))
                except (ValueError, IndexError):
                    self.output_messages.append("[red]Invalid lore entry number.[/red]")
            else:
                self.output_messages.extend(self.lore_manager.get_lore_index_report())
        elif command == "craft":
            if len(action) > 1:
                item_name = " ".join(action[1:-1]) if len(action) > 2 and action[-1].isdigit() else " ".join(action[1:])
                quantity = int(action[-1]) if len(action) > 2 and action[-1].isdigit() else 1
                self.output_messages.extend(self.research_manager.craft_item(item_name, quantity))
            else:
                self.output_messages.extend(self.research_manager.get_recipes_report())
        elif command == "research":
            if len(action) > 1:
                project_name = " ".join(action[1:])
                self.output_messages.extend(self.research_manager.start_research(project_name))
            else:
                self.output_messages.extend(self.research_manager.get_research_projects_report())
        else:
            self.output_messages.append("Unknown command. Type 'help' for a list of commands.")
        return self.get_output_messages()