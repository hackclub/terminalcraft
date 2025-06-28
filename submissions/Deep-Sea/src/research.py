from rich.console import Console
console = Console()
class ResearchManager:
    def __init__(self, submarine):
        self.submarine = submarine
        self.samples = {"salvaged_metal": 10, "component_scraps": 5} 
        self.active_project = None
        self.project_progress = 0
        self.research_points_per_turn = 5 
        self.research_projects = {
            "alien_metallurgy": {
                "description": "Study salvaged alien alloys to unlock advanced hull upgrades.",
                "cost_rp": 100,
                "reward": {"type": "unlock_upgrade", "name": "advanced_hull"}
            },
            "xeno-biology": {
                "description": "Analyze creature samples to develop potent anti-monster weaponry.",
                "cost_rp": 150,
                "reward": {"type": "unlock_recipe", "name": "depth_charges"}
            }
        }
        self.crafting_recipes = {
            "spare_part": {
                "description": "A crucial component for repairing the submarine.",
                "cost": {"salvaged_metal": 2, "component_scraps": 1},
                "output": 1
            }
        }
        self.upgrades = {
            "advanced_hull": {
                "description": "A breakthrough in material science, increasing max hull by 50.",
                "cost": {"salvaged_metal": 20, "component_scraps": 10},
                "applied": False,
                "locked": True
            },
            "reinforced_hull": {
                "description": "Increases max hull integrity by 20.",
                "cost": {"Vampire Squid": 1, "Abyssal Dragonfish": 1},
                "applied": False
            },
            "improved_sonar": {
                "description": "Increases sonar encounter chance.",
                "cost": {"Bioluminescent Jellyfish": 2, "Glow-in-the-dark Shark": 1},
                "applied": False
            },
            "efficient_engine": {
                "description": "Reduces engine power draw by 1.",
                "cost": {"Giant Isopod": 2, "Colossal Squid": 1},
                "applied": False
            },
            "torpedo_system": {
                "description": "Increases combat damage by 10.",
                "cost": {"Colossal Squid Heart": 1, "Goblin Shark Heart": 1},
                "applied": False
            }
        }
    def add_sample(self, sample_type, quantity=1):
        self.samples[sample_type] = self.samples.get(sample_type, 0) + quantity
        return [f"[bold cyan]Collected {quantity}x {sample_type}[/bold cyan]"]
    def get_research_projects_report(self):
        report = ["\n[bold]Available Research Projects[/bold]"]
        for name, details in self.research_projects.items():
            if self.active_project and self.active_project['name'] == name:
                progress = f"({self.project_progress}/{details['cost_rp']} RP)"
                report.append(f"  - [cyan]{name.replace('_', ' ').title()}: {details['description']} [IN PROGRESS {progress}][/cyan]")
            else:
                report.append(f"  - {name.replace('_', ' ').title()}: {details['description']} (Cost: {details['cost_rp']} RP)")
        return report
    def start_research(self, project_name):
        messages = []
        if self.active_project:
            messages.append(f"[yellow]Cannot start new research. Project '{self.active_project['name']}' is already underway.[/yellow]")
            return messages
        if project_name not in self.research_projects:
            messages.append(f"[red]Unknown research project: {project_name}[/red]")
            return messages
        self.active_project = {'name': project_name, **self.research_projects[project_name]}
        self.project_progress = 0
        messages.append(f"[bold green]Research started on: {project_name.replace('_', ' ').title()}[/bold green]")
        return messages
    def update_research(self, points):
        messages = []
        if not self.active_project:
            return messages
        self.project_progress += points
        messages.append(f"Made progress on '{self.active_project['name']}': {self.project_progress}/{self.active_project['cost_rp']} RP")
        if self.project_progress >= self.active_project['cost_rp']:
            messages.extend(self.complete_research())
        return messages
    def complete_research(self):
        messages = []
        project = self.active_project
        messages.append(f"[bold magenta]Research Complete: {project['name'].replace('_', ' ').title()}![/bold magenta]")
        reward = project['reward']
        if reward['type'] == 'unlock_upgrade':
            upgrade_name = reward['name']
            if upgrade_name in self.upgrades:
                self.upgrades[upgrade_name]['locked'] = False
                messages.append(f"New upgrade available: {upgrade_name.replace('_', ' ').title()}")
        elif reward['type'] == 'unlock_recipe':
            messages.append(f"New crafting recipe unlocked: {reward['name'].replace('_', ' ').title()}")
        self.active_project = None
        self.project_progress = 0
        return messages
    def has_item(self, item_name):
        return self.samples.get(item_name, 0) > 0
    def get_recipes_report(self):
        report = ["\n[bold]Crafting Blueprints[/bold]"]
        for name, details in self.crafting_recipes.items():
            cost_str = ", ".join([f"{v} {k}" for k, v in details["cost"].items()])
            report.append(f"  - {name.replace('_', ' ').title()}: {details['description']} (Cost: {cost_str})")
        return report
    def craft_item(self, item_name, quantity=1):
        messages = []
        if item_name not in self.crafting_recipes:
            messages.append(f"[red]Unknown crafting recipe: {item_name}[/red]")
            return messages
        recipe = self.crafting_recipes[item_name]
        total_cost = {item: amount * quantity for item, amount in recipe["cost"].items()}
        can_afford = all(self.samples.get(item, 0) >= amount for item, amount in total_cost.items())
        if can_afford:
            for item, amount in total_cost.items():
                self.samples[item] -= amount
            output_item = recipe.get("output_item", item_name)
            output_quantity = recipe["output"] * quantity
            if output_item == "spare_part":
                self.submarine.resources['spare_parts']['level'] += output_quantity
                messages.append(f"[bold green]Successfully crafted {output_quantity}x Spare Part(s)![/bold green]")
            else:
                messages.extend(self.add_sample(output_item, output_quantity))
        else:
            messages.append(f"[red]Not enough materials to craft {item_name}.[/red]")
            for item, amount in total_cost.items():
                if self.samples.get(item, 0) < amount:
                    messages.append(f"  - Missing: {amount - self.samples.get(item, 0)} {item}")
        return messages
    def apply_upgrade(self, upgrade_name):
        messages = []
        if upgrade_name not in self.upgrades:
            messages.append(f"[bold red]Unknown upgrade: {upgrade_name}[/bold red]")
            return messages
        upgrade = self.upgrades[upgrade_name]
        if upgrade["applied"]:
            messages.append(f"[bold yellow]Upgrade '{upgrade_name}' has already been applied.[/bold yellow]")
            return messages
        cost = upgrade["cost"]
        can_afford = all(self.samples.get(item, 0) >= amount for item, amount in cost.items())
        if can_afford:
            messages.append(f"[bold green]Applying '{upgrade_name}' upgrade![/bold green]")
            if upgrade_name == "reinforced_hull":
                self.submarine.max_hull_integrity += 20
            elif upgrade_name == "improved_sonar":
                pass
            elif upgrade_name == "efficient_engine":
                self.submarine.systems["Engine"].power_draw -= 1
            elif upgrade_name == "torpedo_system":
                pass
            upgrade["applied"] = True
        else:
            messages.append(f"[bold red]Not enough samples for '{upgrade_name}' upgrade.[/bold red]")
        return messages