from rich.console import Console
console = Console()
class Objective:
    def __init__(self, obj_type, target, description, completed=False):
        self.type = obj_type  
        self.target = target 
        self.description = description
        self.completed = completed
class Quest:
    def __init__(self, quest_id, title, description, objectives, rewards=None, faction=None, next_quest=None, lore_unlock=None):
        self.id = quest_id
        self.title = title
        self.description = description
        self.objectives = objectives
        self.rewards = rewards if rewards else {}
        self.faction = faction
        self.next_quest = next_quest
        self.lore_unlock = lore_unlock
        self.completed = False
    def is_complete(self):
        return all(obj.completed for obj in self.objectives)
ALL_QUESTS = {
    "main_1": Quest(
        "main_1", "The Anomaly", "Strange energy readings have been detected. Find their source.",
        [Objective("reach_depth", 1000, "Descend to 1000m to get a clearer signal.")],
        next_quest="main_2"
    ),
    "main_2": Quest(
        "main_2", "The Anomaly", "The signal seems to be coming from a nearby wreck. Investigate it.",
        [Objective("visit_poi", "Unidentified Wreck", "Find and visit the source of the signal."),
         Objective("collect_item", "Strange Logbook", "Recover the logbook from the wreck.")],
        rewards={"experience": 200},
        lore_unlock="log_anomaly_1"
    ),
    "faction_sci_1": Quest(
        "faction_sci_1", "Geological Survey", "The Science Guild wants samples from active hydrothermal vents.",
        [Objective("visit_poi", "Unidentified Hydrothermal Vents", "Locate a hydrothermal vent field."),
         Objective("collect_item", "Vent Samples", "Collect samples for the guild.")],
        rewards={"spare_parts": 5, "experience": 150},
        faction="Science Guild"
    )
}
class MissionManager:
    def __init__(self, research_manager, crew_manager, lore_manager):
        self.research_manager = research_manager
        self.crew_manager = crew_manager
        self.lore_manager = lore_manager
        self.active_quests = {}
        self.completed_quests = set()
        self.add_quest("main_1") 
    def add_quest(self, quest_id):
        messages = []
        if quest_id in ALL_QUESTS and quest_id not in self.active_quests and quest_id not in self.completed_quests:
            self.active_quests[quest_id] = ALL_QUESTS[quest_id]
            messages.append(f"\n[bold yellow]New Quest Started: {self.active_quests[quest_id].title}[/bold yellow]")
        return messages
    def update(self, game_state):
        messages = []
        quests_to_complete = []
        for quest_id, quest in list(self.active_quests.items()):
            for objective in quest.objectives:
                if not objective.completed:
                    messages.extend(self.check_objective(objective, game_state))
            if quest.is_complete():
                quests_to_complete.append(quest_id)
        for quest_id in quests_to_complete:
            messages.extend(self.complete_quest(quest_id))
        return messages
    def check_objective(self, objective, game_state):
        messages = []
        completed = False
        if objective.type == 'reach_depth' and game_state['depth'] >= objective.target:
            completed = True
        elif objective.type == 'visit_poi':
            for poi in game_state['nearby_pois']:
                if objective.target in poi.name and not poi.visited:
                    poi.visited = True 
                    messages.append(f"[cyan]You have arrived at the {poi.name}.[/cyan]")
                    completed = True
                    break
        elif objective.type == 'collect_item' and self.research_manager.has_item(objective.target):
            completed = True
        if completed:
            objective.completed = True
            messages.append(f"[bold green]Objective Complete:[/bold green] {objective.description}")
            messages.extend(self.crew_manager.broadcast_event('mission_objective_complete'))
        return messages
    def complete_quest(self, quest_id):
        messages = []
        quest = self.active_quests.pop(quest_id)
        quest.completed = True
        self.completed_quests.add(quest_id)
        messages.append(f"\n[bold green]Quest Complete: {quest.title}[/bold green]")
        if quest.rewards.get("experience"):
            for member in self.crew_manager.crew.values():
                messages.extend(member.gain_experience(quest.rewards["experience"]))
        if quest.rewards.get("spare_parts"):
            self.research_manager.submarine.resources['spare_parts']['level'] += quest.rewards["spare_parts"]
            messages.append(f"[yellow]Added {quest.rewards['spare_parts']} spare parts.[/yellow]")
        if quest.next_quest:
            messages.extend(self.add_quest(quest.next_quest))
        if quest.lore_unlock:
            lore_messages = self.lore_manager.unlock_lore(quest.lore_unlock)
            if lore_messages:
                messages.extend(lore_messages)
        return messages
    def get_journal_report(self):
        report = ["\n[bold]Captain's Log[/bold]"]
        if not self.active_quests:
            report.append("No active quests.")
            return report
        for quest in self.active_quests.values():
            faction_tag = f" ([italic]{quest.faction}[/italic])" if quest.faction else ""
            report.append(f"\n[cyan]{quest.title}{faction_tag}[/cyan]")
            report.append(f"  [dim]{quest.description}[/dim]")
            for obj in quest.objectives:
                status = "[green](Completed)[/green]" if obj.completed else ""
                report.append(f"  - {obj.description} {status}")
        return report