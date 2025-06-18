from config import RESEARCH_PROJECTS
from utils import Colors
import time
class ResearchManager:
    """Manages the zoo's research and development projects."""
    def __init__(self):
        self.completed_projects = set()
        self.available_projects = set(RESEARCH_PROJECTS.keys())
    def is_unlocked(self, project_name):
        """Checks if a research project has been completed."""
        return project_name in self.completed_projects
    def complete_project(self, project_name):
        """Marks a project as completed."""
        self.completed_projects.add(project_name)
        self.available_projects.discard(project_name)
    def manage_research(self, zoo):
        """Provides an interface to manage and purchase research projects."""
        print(f"\n{Colors.HEADER}--- Research & Development ---{Colors.RESET}")
        print(f"Available Funds: {Colors.GREEN}${zoo.finance.money:.2f}{Colors.RESET}")
        available_to_research = [p for p in self.available_projects if p not in self.completed_projects]
        if not available_to_research:
            print("\n  All available research projects have been completed!")
            input("\nPress Enter to return to the main menu...")
            return
        print("\nAvailable Research Projects:")
        project_list = list(available_to_research)
        for i, project_name in enumerate(project_list):
            project_data = RESEARCH_PROJECTS[project_name]
            print(f"  {i+1}. {project_name} - Cost: ${project_data['cost']:.2f}")
            print(f"     {Colors.YELLOW}{project_data['description']}{Colors.RESET}")
        try:
            choice_idx = int(input("\nEnter the number of the project to research (or 0 to go back): "))
            if choice_idx == 0:
                return
            if 1 <= choice_idx <= len(project_list):
                project_name = project_list[choice_idx - 1]
                project_data = RESEARCH_PROJECTS[project_name]
                if zoo.finance.money >= project_data['cost']:
                    zoo.finance.add_expense(project_data['cost'], f"Research: {project_name}")
                    self.complete_project(project_name)
                    print(f"\n{Colors.GREEN}Research for '{project_name}' completed!{Colors.RESET}")
                else:
                    print(f"\n{Colors.RED}Not enough money to research '{project_name}'.{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}Invalid choice.{Colors.RESET}")
        except ValueError:
            print(f"\n{Colors.RED}Invalid input. Please enter a number.{Colors.RESET}")
        input("\nPress Enter to continue...")