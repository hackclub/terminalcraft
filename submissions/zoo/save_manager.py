import json
import os
import datetime
from zoo import Zoo
from animal import Animal
from habitat import Habitat
from staff import Staff
from finance import Finance
from research import ResearchManager
from visitor import Visitor
from config import ANIMAL_CONFIG, HABITAT_CONFIG, STAFF_CONFIG, RESEARCH_PROJECTS, VISITOR_CONFIG
from utils import Colors
SAVE_FILE = "savegame.json"
def save_game(zoo):
    """Saves the current state of the zoo to a file."""
    if not os.path.exists('saves'):
        os.makedirs('saves')
    save_data = {
        'name': zoo.name,
        'game_date': zoo.game_date.isoformat(),
        'finance': zoo.finance.to_dict(),
        'animals': [a.to_dict() for a in zoo.animals],
        'habitats': [h.to_dict() for h in zoo.habitats],
        'staff': [s.to_dict() for s in zoo.staff],
        'visitors': [v.to_dict() for v in zoo.visitors],
        'research': list(zoo.research_manager.completed_projects),
        'visitor_boost': zoo.visitor_boost,
        'reputation_penalty': zoo.reputation_penalty
    }
    with open(os.path.join('saves', SAVE_FILE), 'w') as f:
        json.dump(save_data, f, indent=4)
    print("Game saved successfully!")
def load_game():
    """Loads a zoo state from a file, handling potential errors gracefully."""
    save_path = os.path.join('saves', SAVE_FILE)
    if not os.path.exists(save_path):
        return None
    try:
        with open(save_path, 'r') as f:
            save_data = json.load(f)
    except (json.JSONDecodeError, TypeError):
        print(f"\n{Colors.RED}Error: Could not read the save file. It may be corrupted.{Colors.RESET}")
        return None
    try:
        zoo = Zoo(save_data['name'])
        zoo.game_date = datetime.date.fromisoformat(save_data['game_date'])
        zoo.visitor_boost = save_data.get('visitor_boost')
        zoo.reputation_penalty = save_data.get('reputation_penalty')
        finance_data = save_data.get('finance', {})
        zoo.finance = Finance(initial_money=finance_data.get('money', 10000))
        zoo.finance.history = finance_data.get('history', [])
        zoo.research_manager = ResearchManager()
        for project_name in save_data.get('research', []):
            if project_name in zoo.research_manager.projects:
                zoo.research_manager.completed_projects.add(project_name)
        zoo.habitats = []
        for h_data in save_data.get('habitats', []):
            species_type = h_data.get('species_type')
            if species_type and species_type in HABITAT_CONFIG:
                config = HABITAT_CONFIG[species_type]
                habitat = Habitat(h_data['name'], species_type, h_data['capacity'], config['base_temp'], config['base_enrichment'])
                habitat.cleanliness = h_data.get('cleanliness', 100)
                habitat.temperature = h_data.get('temperature', config['base_temp'])
                habitat.enrichment = h_data.get('enrichment', config['base_enrichment'])
                habitat.security = h_data.get('security', 50) 
                zoo.habitats.append(habitat)
            else:
                print(f"{Colors.YELLOW}Warning: Could not load habitat '{h_data.get('name')}' of unknown type '{species_type}'.{Colors.RESET}")
        zoo.animals = []
        for a_data in save_data.get('animals', []):
            species = a_data.get('species')
            if species and species in ANIMAL_CONFIG:
                config = ANIMAL_CONFIG[species]
                animal = Animal(species, a_data['name'], config, age=a_data['age'], gender=a_data['gender'])
                animal.health = a_data.get('health', 100)
                animal.hunger = a_data.get('hunger', 0)
                animal.happiness = a_data.get('happiness', 100)
                habitat_name = a_data.get('habitat_name')
                if habitat_name:
                    for h in zoo.habitats:
                        if h.name == habitat_name:
                            h.add_animal(animal)
                            break
                zoo.animals.append(animal)
            else:
                print(f"{Colors.YELLOW}Warning: Could not load animal '{a_data.get('name')}' of unknown species '{species}'.{Colors.RESET}")
        zoo.staff = []
        for s_data in save_data.get('staff', []):
            role = s_data.get('role')
            if role and role in STAFF_CONFIG:
                config = STAFF_CONFIG[role]
                staff = Staff(s_data['name'], role, config['salary'], config.get('base_skill', 30))
                staff.skill = s_data.get('skill', config.get('base_skill', 30))
                staff.fatigue = s_data.get('fatigue', 0)
                zoo.staff.append(staff)
            else:
                print(f"{Colors.YELLOW}Warning: Could not load staff member '{s_data.get('name')}' with unknown role '{role}'.{Colors.RESET}")
        zoo.visitors = []
        for v_data in save_data.get('visitors', []):
            visitor_type = v_data.get('type')
            if visitor_type and visitor_type in VISITOR_CONFIG:
                zoo.visitors.append(Visitor(visitor_type, state=v_data))
            else:
                print(f"{Colors.YELLOW}Warning: Could not load visitor of unknown type '{visitor_type}'.{Colors.RESET}")
        print(f"\n{Colors.GREEN}Game loaded successfully! Welcome back to {zoo.name}.{Colors.RESET}")
        return zoo
    except (KeyError, TypeError, ValueError) as e:
        print(f"\n{Colors.RED}Error: Save file is invalid or corrupted. Starting a new game. (Details: {e}){Colors.RESET}")
        return None