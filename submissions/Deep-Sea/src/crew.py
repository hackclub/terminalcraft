from src.skill import ALL_SKILL_TREES
class CrewMember:
    def __init__(self, name, expertise):
        self.name = name
        self.expertise = expertise
        self.panic = 0
        self.fatigue = 0
        self.sanity = 100
        self.task = None
        self.morale = 70
        self.relationships = {}
        self.skill_tree = ALL_SKILL_TREES.get(self.expertise, {})
        self.skills = {}
        self.skill_points = 0
        self.experience = 0
        self.level = 1
    def gain_experience(self, amount):
        messages = []
        self.experience += amount
        messages.append(f"{self.name} gained {amount} XP.")
        if self.experience >= self.level * 100:
            messages.append(self.level_up())
        return messages
    def update(self):
        self.fatigue += 1
        self.fatigue = min(100, self.fatigue)
    def level_up(self):
        self.level += 1
        self.skill_points += 1
        self.experience = 0
        return f"[bold green]{self.name} has reached level {self.level}! They have {self.skill_points} skill point(s).[/bold green]"
    def learn_skill(self, skill_name):
        skill_to_learn = self.skill_tree.get(skill_name)
        if not skill_to_learn:
            return f"[red]Skill '{skill_name}' does not exist for {self.expertise}.[/red]"
        if skill_name in self.skills:
            return f"[yellow]{self.name} already knows {skill_name}.[/yellow]"
        if self.skill_points <= 0:
            return f"[red]{self.name} has no skill points to spend.[/red]"
        for prereq in skill_to_learn.prerequisites:
            if prereq not in self.skills:
                return f"[red]Cannot learn {skill_name}. Prerequisite '{prereq}' is missing.[/red]"
        self.skill_points -= 1
        self.skills[skill_name] = skill_to_learn
        return f"[bold green]{self.name} has learned {skill_name}! ({skill_to_learn.description})[/bold green]"
    def get_skill_bonus(self, effect_type, stat_name):
        total_bonus = 0
        for skill in self.skills.values():
            if skill.effect.get('type') == effect_type and skill.effect.get('stat') == stat_name:
                total_bonus += skill.effect.get('value', 0)
        return total_bonus
    def adjust_morale(self, amount):
        messages = []
        old_morale = self.morale
        self.morale = max(0, min(100, self.morale + amount))
        if self.morale < 30 and old_morale >= 30:
            messages.append(f"[bold red]{self.name}'s morale is dangerously low![/bold red]")
        elif self.morale > 80 and old_morale <= 80:
            messages.append(f"[bold green]{self.name} is in high spirits![/bold green]")
        return messages
    def adjust_relationship(self, member_name, amount):
        if member_name in self.relationships:
            self.relationships[member_name] += amount
class CrewManager:
    def __init__(self, submarine):
        self.submarine = submarine
        self.crew = {
            "Jonas": CrewMember("Jonas", "Engineer"),
            "Dr. Aris": CrewMember("Dr. Aris", "Scientist"),
            "Echo": CrewMember("Echo", "Pilot"),
        }
        for member in self.crew.values():
            member.relationships = {name: 0 for name in self.crew if name != member.name}
    def get_member(self, crew_name):
        return self.crew.get(crew_name)
    def assign_task(self, crew_name, task):
        member = self.get_member(crew_name)
        if member:
            member.task = task
            return f"{member.name} has been assigned to {task}."
    def get_assigned_engineer(self):
        for member in self.crew.values():
            if member.expertise == "Engineer" and member.task == "repair":
                return member
        return None
    def update(self):
        for member in self.crew.values():
            member.update()
            if member.task == "repair":
                member.fatigue += 1
            elif member.task == "research":
                member.fatigue += 1
            elif member.task == "combat":
                member.fatigue += 2
        return []
        if self.submarine.resources['oxygen']['level'] <= 0:
            return ["[bold red]CRITICAL: Oxygen levels are at zero. Life Support is struggling to keep up![/bold red]"]
    def get_combat_power(self):
        power = 0
        for member in self.crew.values():
            if member.task == "combat":
                power += 5
                if member.expertise == "Pilot":
                    power += 5
                elif member.expertise == "Engineer":
                    power += 2
        return power
    def get_status_report(self):
        report = ["\n[bold]Crew Status[/bold]"]
        for member in self.crew.values():
            task_status = f"(Task: {member.task})" if member.task else ""
            report.append(f"  - {member.name} ({member.expertise}, Lvl: {member.level}): Morale: {member.morale}%, Sanity: {member.sanity}%, SP: {member.skill_points} {task_status}")
        return report
    def get_skill_tree_report(self, crew_name):
        member = self.get_member(crew_name)
        if not member:
            return [f"[red]Crew member '{crew_name}' not found.[/red]"]
        report = []
        report.append(f"\n[bold]{member.name}'s ({member.expertise}) Skill Tree[/bold]")
        report.append(f"Skill Points available: {member.skill_points}")
        skills_by_tier = {}
        for skill_name, skill_obj in member.skill_tree.items():
            if skill_obj.tier not in skills_by_tier:
                skills_by_tier[skill_obj.tier] = []
            skills_by_tier[skill_obj.tier].append((skill_name, skill_obj))
        for tier in sorted(skills_by_tier.keys()):
            report.append(f"\n[bold]-- Tier {tier} --[/bold]")
            for skill_name, skill_obj in skills_by_tier[tier]:
                prereqs_met = all(p in member.skills for p in skill_obj.prerequisites)
                if skill_name in member.skills:
                    status_color = "green"
                    status_text = "(Learned)"
                elif prereqs_met:
                    status_color = "cyan"
                    status_text = "(Available)"
                else:
                    status_color = "red"
                    status_text = "(Locked)"
                prereq_str = f"(req: {', '.join(skill_obj.prerequisites)})" if skill_obj.prerequisites else ""
                report.append(f"  - [{status_color}]{skill_name}[/{status_color}]: {skill_obj.description} {prereq_str} {status_text}")
        return report
    def broadcast_event(self, event, **kwargs):
        """Broadcasts a game event to all crew members to adjust morale and relationships."""
        messages = []
        if event == "monster_defeated":
            for member in self.crew.values():
                messages.extend(member.adjust_morale(15))
            messages.append("[cyan]The crew is buoyed by their victory against the creature.[/cyan]")
        elif event == "hull_damage":
            amount = kwargs.get('amount', 5)
            for member in self.crew.values():
                messages.extend(member.adjust_morale(-amount))
            messages.append("[red]The shudder of the hull rattles the crew's nerves.[/red]")
        elif event == "mission_objective_complete":
            for member in self.crew.values():
                messages.extend(member.adjust_morale(25))
            messages.append("[bold green]Mission objective complete! A wave of determination washes over the crew.[/bold green]")
        elif event == "successful_repair":
            engineer = kwargs.get('engineer')
            if engineer:
                for member in self.crew.values():
                    if member is not engineer:
                        member.adjust_relationship(engineer.name, 5)
                        engineer.adjust_relationship(member.name, 5)
                messages.append(f"[cyan]{engineer.name}'s expert repairs have impressed the crew.[/cyan]")
        elif event == "life_support_failure":
            for member in self.crew.values():
                messages.extend(member.adjust_morale(-20))
                member.sanity -= 10
            messages.append("[bold red]The crew is suffocating! Life support has failed, and morale is plummeting.[/bold red]")
        return messages
    def get_relationships_report(self):
        report = ["\n[bold]Crew Relationships[/bold]"]
        for member in self.crew.values():
            relations = []
            for other_name, value in member.relationships.items():
                if value > 10:
                    color = "green"
                elif value < -10:
                    color = "red"
                else:
                    color = "yellow"
                relations.append(f"[{color}]{other_name}: {value}[/{color}]")
            report.append(f"  - {member.name}: {', '.join(relations)}")
        return report