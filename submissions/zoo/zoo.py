import datetime
import time
import random
from collections import Counter
from animal import Animal
from habitat import Habitat
from staff import Staff
from visitor import Visitor
from finance import Finance
from research import ResearchManager
from event import trigger_event
from config import ANIMAL_CONFIG, HABITAT_CONFIG, STAFF_CONFIG, VISITOR_CONFIG, TICKET_PRICE, RESEARCH_PROJECTS, ESCAPE_CONFIG, VIP_VISITORS
from utils import Colors
class Zoo:
    """Represents the zoo itself."""
    def __init__(self, name):
        self.name = name
        self.finance = Finance(10000)
        self.research_manager = ResearchManager()
        self.game_date = datetime.date(2024, 1, 1)
        self.animals = []
        self.habitats = []
        self.staff = []
        self.visitors = []
        self.visitor_boost = None 
        self.reputation_penalty = None 
        self.fossil_quest_stage = 0
        self.fossil_analysis_start_date = None
        self.dinosaur_exhibit_active = False
        self.dinosaur_unlocked = False
        self.reputation = 50  
        self.vip_visit = None
        self.new_birth_this_day = False
    def next_day(self):
        """Simulates the passing of a day with more detailed mechanics."""
        self.game_date += datetime.timedelta(days=1)
        self.new_birth_this_day = False 
        self._start_vip_visit() 
        print(f"\nA new day dawns: {self.game_date.strftime('%Y-%m-%d')}")
        time.sleep(1)
        for s in self.staff:
            s.rest() 
        self._perform_staff_duties()
        self._update_animals_and_habitats()
        self._handle_animal_deaths()
        self._check_for_escapes()
        self._handle_breeding()
        self._simulate_visitors()
        self._process_finances()
        self._check_fossil_analysis()
        self._check_vip_objective() 
        trigger_event(self)
        if self.visitor_boost:
            self.visitor_boost['duration'] -= 1
            if self.visitor_boost['duration'] <= 0:
                self.visitor_boost = None
                print(f"\n{Colors.INFO}The positive press coverage has subsided. Visitor numbers are back to normal.{Colors.RESET}")
        if self.reputation_penalty:
            self.reputation_penalty['duration'] -= 1
            if self.reputation_penalty['duration'] <= 0:
                self.reputation_penalty = None
                print(f"\n{Colors.INFO}The zoo's reputation has recovered from the recent incident.{Colors.RESET}")
        time.sleep(2)
    def _perform_staff_duties(self):
        """Simulates staff performing their daily tasks."""
        zookeepers = [s for s in self.staff if s.role == 'Zookeeper']
        vets = [s for s in self.staff if s.role == 'Veterinarian']
        print("\nStaff are getting to work...")
        if zookeepers:
            for keeper in zookeepers:
                effectiveness = keeper.get_effectiveness()
                for animal in self.animals:
                    if animal.hunger < 60:
                        animal.hunger = min(100, animal.hunger + 20 + effectiveness * 0.5)
                for habitat in self.habitats:
                    if habitat.cleanliness < 70:
                        habitat.cleanliness = min(100, habitat.cleanliness + 15 + effectiveness * 0.3)
                keeper.work()
            print("Zookeepers have tended to the animals and habitats.")
        else:
            print("Warning: No zookeepers to feed animals or clean habitats!")
        if vets:
            for vet in vets:
                effectiveness = vet.get_effectiveness()
                for animal in self.animals:
                    if animal.is_sick():
                        animal.heal(15 + effectiveness * 0.4)
                vet.work()
        else:
            if any(a.is_sick() for a in self.animals):
                print(f"{Colors.RED}Warning: An animal is sick, but there are no veterinarians!{Colors.RESET}")
        time.sleep(1)
    def _update_animals_and_habitats(self):
        """Updates the state of all animals and habitats."""
        total_happiness = 0
        total_health = 0
        for habitat in self.habitats:
            habitat.update()
            if habitat.cleanliness < 30:
                self.reputation = max(0, self.reputation - 0.1) 
            for animal in habitat.animals:
                animal.update(habitat, self)
                total_happiness += animal.happiness
                total_health += animal.health
                if animal.escape_risk > 0:
                    animal.escape_risk -= 1
        if self.animals:
            avg_happiness = total_happiness / len(self.animals)
            if avg_happiness < 40:
                self.reputation = max(0, self.reputation - 0.2)
            elif avg_happiness > 80:
                self.reputation = min(100, self.reputation + 0.15)
    def _handle_animal_deaths(self):
        """Checks for and handles animal deaths."""
        for animal in self.animals[:]:
            if animal.is_dead():
                print(f"\nTragedy! {animal.name} the {animal.species} has passed away.")
                self.reputation = max(0, self.reputation - 5) 
                if animal.habitat:
                    animal.habitat.animals.remove(animal)
                self.animals.remove(animal)
                time.sleep(1)
    def _check_for_escapes(self):
        """Checks if any animals escape from their habitats."""
        for animal in self.animals[:]: 
            if not hasattr(animal, 'habitat') or not animal.habitat: continue
            security_modifier = (100 - animal.habitat.security) / 100 
            final_chance = ESCAPE_CONFIG['base_chance'] + (animal.escape_risk / 150) * security_modifier
            if random.random() < final_chance:
                self._handle_escape(animal)
    def _handle_escape(self, animal):
        """Handles the consequences of an animal escape."""
        print(f"\n{Colors.RED}!!! ANIMAL ESCAPE !!!{Colors.RESET}")
        print(f"{animal.name} the {animal.species} has escaped from {animal.habitat.name}! The zoo is in lockdown.")
        cost = random.randint(*ESCAPE_CONFIG['capture_cost'])
        self.finance.add_expense(cost, f"Capture Team for {animal.name}")
        print(f"A capture team has been dispatched. Cost: ${cost}")
        self.reputation_penalty = {
            'multiplier': ESCAPE_CONFIG['visitor_reduction_multiplier'],
            'duration': ESCAPE_CONFIG['penalty_duration']
        }
        print(f"The zoo's reputation has been damaged. Expect fewer visitors.")
        animal.habitat.animals.remove(animal)
        self.animals.remove(animal)
        time.sleep(3)
    def _simulate_visitors(self):
        """Simulates visitors of different types touring the zoo."""
        num_visitors = random.randint(20, 50) + len(self.animals) * 5
        if self.visitor_boost:
            num_visitors = int(num_visitors * self.visitor_boost['multiplier'])
        if self.reputation_penalty:
            num_visitors = int(num_visitors * self.reputation_penalty['multiplier'])
            self.reputation = max(0, self.reputation - 10) 
            self.reputation_penalty = None 
        if self.dinosaur_exhibit_active:
            print(f"{Colors.INFO}The 'Mystery Dinosaur' exhibit is drawing in extra crowds!{Colors.RESET}")
            num_visitors = int(num_visitors * 1.25)
        self.finance.add_income(num_visitors * TICKET_PRICE, 'Tickets')
        visitor_types = list(VISITOR_CONFIG.keys())
        visitor_weights = [config['spawn_weight'] for config in VISITOR_CONFIG.values()]
        self.visitors = []
        chosen_types = random.choices(visitor_types, weights=visitor_weights, k=num_visitors)
        for visitor_type in chosen_types:
            self.visitors.append(Visitor(visitor_type))
        print(f"\n{num_visitors} visitors are arriving at the zoo.")
        if not self.habitats:
            print("The visitors have nowhere to go!")
            for v in self.visitors:
                v.satisfaction = 20 
                v.thoughts.append("There was nothing to see at this zoo!")
            return
        avg_satisfaction = 0
        for visitor in self.visitors:
            num_habitats_to_visit = random.randint(1, min(len(self.habitats), 4))
            for habitat in random.sample(self.habitats, num_habitats_to_visit):
                visitor.visit_habitat(habitat)
            if self.dinosaur_exhibit_active:
                visitor.satisfaction = min(100, visitor.satisfaction + 15)
                visitor.thoughts.append("The mystery fossil exhibit was fascinating!")
            avg_satisfaction += visitor.satisfaction
        if self.visitors:
            final_avg_satisfaction = avg_satisfaction / len(self.visitors)
            if final_avg_satisfaction > 75:
                self.reputation = min(100, self.reputation + 0.25)
            elif final_avg_satisfaction < 40:
                self.reputation = max(0, self.reputation - 0.3)
        self._solicit_donations()
    def _solicit_donations(self):
        """Collects donations from visitors based on their type and satisfaction."""
        total_donations = 0
        for visitor in self.visitors:
            donation = visitor.get_donation()
            if donation > 0:
                total_donations += donation
        if total_donations > 0:
            self.finance.add_income(total_donations, "Donations")
            print(f"The zoo received ${total_donations:.2f} in donations today!")
    def _process_finances(self):
        """Calculates and processes daily income and expenses by category."""
        food_costs = sum(a.food_cost for a in self.animals)
        staff_salaries = sum(s.salary for s in self.staff)
        self.finance.add_expense(food_costs, 'Animal Food')
        self.finance.add_expense(staff_salaries, 'Staff Salaries')
        self.finance.process_day(self.game_date)
    def _handle_breeding(self):
        """Handles animal breeding logic for the day."""
        for habitat in self.habitats:
            if habitat.is_full():
                continue
            potential_parents = [a for a in habitat.animals if a.is_mature()]
            males = [p for p in potential_parents if p.gender == 'Male']
            females = [p for p in potential_parents if p.gender == 'Female']
            if not males or not females:
                continue
            for male in males:
                for female in females:
                    if male.species == female.species:
                        avg_happiness = (male.happiness + female.happiness) / 2
                        suitability = habitat.get_suitability(male.preferences)
                        breeding_chance = (avg_happiness * suitability) / 10000.0 
                        if random.random() < breeding_chance:
                            self._birth_animal(male.species, habitat)
                            break
    def _birth_animal(self, species, habitat):
        """Creates a new baby animal."""
        config = ANIMAL_CONFIG[species]
        name = f"{species}-baby-{random.randint(100, 999)}"
        baby = Animal(species, name, config, age=0)
        self.animals.append(baby)
        habitat.add_animal(baby)
        self.reputation = min(100, self.reputation + 2) 
        self.new_birth_this_day = True
        print(f"{Colors.GREEN}A new {species} has been born in the {habitat.name} habitat! Welcome, {name}!{Colors.RESET}")
    def _start_vip_visit(self):
        if self.vip_visit: 
            return
        if random.random() < VIP_VISITORS['chance']:
            vip_data = random.choice(VIP_VISITORS['vips'])
            objective_data = random.choice(vip_data['objectives'])
            self.vip_visit = {
                'name': vip_data['name'],
                'title': vip_data['title'],
                'objective': objective_data
            }
            objective_text = objective_data['text']
            if '{animal}' in objective_text:
                animal_species = random.choice(objective_data['params']['species'])
                objective_text = objective_text.format(animal=animal_species)
                self.vip_visit['objective']['target_species'] = animal_species
            if '{habitat}' in objective_text:
                habitat_type = random.choice(objective_data['params']['habitat_type'])
                objective_text = objective_text.format(habitat=habitat_type)
                self.vip_visit['objective']['target_habitat'] = habitat_type
            print(f"\n{Colors.PURPLE}--- VIP Visitor Alert! ---{Colors.RESET}")
            print(f"{self.vip_visit['name']}, {self.vip_visit['title']}, is visiting today!")
            print(f"Their goal: To {objective_text}")
            input("Press Enter to continue...")
    def _check_vip_objective(self):
        if not self.vip_visit:
            return
        objective = self.vip_visit['objective']
        obj_type = objective['type']
        params = objective['params']
        reward = objective['reward']
        success = False
        if obj_type == 'animal_happiness':
            target_species = self.vip_visit['objective']['target_species']
            for animal in self.animals:
                if animal.species == target_species and animal.happiness >= params['value']:
                    success = True
                    break
        elif obj_type == 'habitat_cleanliness':
            target_habitat = self.vip_visit['objective']['target_habitat']
            for habitat in self.habitats:
                if habitat.species_type == target_habitat and habitat.cleanliness >= params['value']:
                    success = True
                    break
        elif obj_type == 'see_baby_animal':
            if self.new_birth_this_day:
                success = True
        elif obj_type == 'animal_health':
            target_species = self.vip_visit['objective']['target_species']
            for animal in self.animals:
                if animal.species == target_species and animal.health >= params['value']:
                    success = True
                    break
        print(f"\n{Colors.PURPLE}--- VIP Visit Report ---{Colors.RESET}")
        if success:
            print(f"{self.vip_visit['name']} is delighted with your zoo!")
            print(f"You have been awarded ${reward['money']} and your reputation has increased by {reward['reputation']} points.")
            self.finance.add_income(reward['money'], f"VIP Bonus from {self.vip_visit['name']}")
            self.reputation = min(100, self.reputation + reward['reputation'])
        else:
            print(f"{self.vip_visit['name']} was not impressed. They hope for improvements on their next visit.")
            self.reputation = max(0, self.reputation - 2) 
        self.vip_visit = None 
        input("Press Enter to continue...")
    def display_summary(self):
        """Displays a summary of the zoo."""
        print("Habitats:")
        if not self.habitats:
            print("  No habitats yet.")
        for h in self.habitats:
            print(f"  - {h.name} ({h.name}): {len(h.animals)}/{h.capacity} animals")
        print("\nStaff:")
        if not self.staff:
            print("  No staff hired.")
        for s in self.staff:
            print(f"  - {s.name} ({s.role})")
    def build_habitat(self):
        """Builds a new habitat."""
        print(f"\n{Colors.HEADER}--- Habitat Construction ---{Colors.RESET}")
        print(f"Available Funds: {Colors.GREEN}${self.finance.money:.2f}{Colors.RESET}")
        print("\nAvailable Habitat Types:")
        habitat_types = []
        for name, config in HABITAT_CONFIG.items():
            if not config.get('quest_item'):
                habitat_types.append(name)
            elif name == 'Prehistoric Paddock' and self.dinosaur_unlocked:
                habitat_types.append(name)
        if not habitat_types:
            print("No habitats available for construction.")
            input("\nPress Enter to continue...")
            return
        for i, habitat_type in enumerate(habitat_types):
            cost = HABITAT_CONFIG[habitat_type]['cost']
            print(f"  {i+1}. {habitat_type} - Cost: ${cost:.2f}")
        try:
            choice_idx = int(input("\nEnter the number of the habitat to build (or 0 to cancel): "))
            if choice_idx == 0:
                return
            if 1 <= choice_idx <= len(habitat_types):
                habitat_type = habitat_types[choice_idx - 1]
                config = HABITAT_CONFIG[habitat_type]
                cost = config['cost']
                if self.finance.money >= cost:
                    name = input(f"Enter a name for your new {habitat_type} habitat: ")
                    if not name.strip():
                        print(f"{Colors.RED}Habitat name cannot be empty.{Colors.RESET}")
                    else:
                        habitat = Habitat(name.strip(), habitat_type, config['capacity'], config['base_temp'], config['base_enrichment'])
                        self.habitats.append(habitat)
                        self.finance.add_expense(cost, "Habitat Construction")
                        print(f"\n{Colors.GREEN}{name.strip()} the {habitat_type} habitat has been built!{Colors.RESET}")
                else:
                    print(f"\n{Colors.RED}Not enough money to build this habitat.{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}Invalid choice.{Colors.RESET}")
        except ValueError:
            print(f"\n{Colors.RED}Invalid input. Please enter a number.{Colors.RESET}")
        input("\nPress Enter to continue...")
    def buy_animal(self):
        """Buys a new animal for the zoo."""
        print(f"\n{Colors.HEADER}--- Animal Market ---{Colors.RESET}")
        print(f"Available Funds: {Colors.GREEN}${self.finance.money:.2f}{Colors.RESET}")
        available_animals = {}
        for name, config in ANIMAL_CONFIG.items():
            is_quest_item = config.get('quest_item', False)
            is_unlockable = config.get('unlockable', False)
            if not is_quest_item and not is_unlockable:
                available_animals[name] = config
        if self.research_manager.is_unlocked('Exotic Animal Acquisition'):
            unlocked_species = RESEARCH_PROJECTS['Exotic Animal Acquisition']['effect']['species']
            for species in unlocked_species:
                if species in ANIMAL_CONFIG:
                    available_animals[species] = ANIMAL_CONFIG[species]
        if self.dinosaur_unlocked:
            if 'Velociraptor' in ANIMAL_CONFIG:
                available_animals['Velociraptor'] = ANIMAL_CONFIG['Velociraptor']
        if not available_animals:
            print("\n  No animals are available for purchase right now.")
            input("\nPress Enter to return to the main menu...")
            return
        print("\nAvailable Animals for Purchase:")
        animal_list = list(available_animals.items())
        for i, (name, config) in enumerate(animal_list):
            print(f"  {i+1}. {name} ({config.get('habitat', 'N/A')}) - Cost: ${config['price']:.2f}")
        try:
            choice_idx = int(input("\nEnter the number of the animal to buy (or 0 to go back): "))
            if choice_idx == 0:
                return
            if 1 <= choice_idx <= len(animal_list):
                species, config = animal_list[choice_idx - 1]
                if self.finance.money >= config['price']:
                    animal_name = input(f"Name your new {species}: ")
                    if not animal_name.strip():
                        print(f"{Colors.RED}Animal name cannot be empty.{Colors.RESET}")
                    else:
                        suitable_habitat = None
                        for h in self.habitats:
                            if h.species_type == config.get('habitat') and h.has_space():
                                suitable_habitat = h
                                break
                        if suitable_habitat:
                            animal = Animal(species, animal_name.strip(), config)
                            suitable_habitat.add_animal(animal)
                            self.animals.append(animal)
                            self.finance.add_expense(config['price'], 'Animal Purchase')
                            print(f"\n{Colors.GREEN}{animal.name} the {species} has joined the zoo!{Colors.RESET}")
                        else:
                            print(f"\n{Colors.RED}No suitable habitat for a {species}. Build a {config.get('habitat_type', 'N/A')} habitat first.{Colors.RESET}")
                else:
                    print(f"\n{Colors.RED}Not enough money to buy a {species}.{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}Invalid choice.{Colors.RESET}")
        except ValueError:
            print(f"\n{Colors.RED}Invalid input. Please enter a number.{Colors.RESET}")
        input("\nPress Enter to continue...")
    def hire_staff(self):
        """Hires a new staff member."""
        print(f"\n{Colors.HEADER}--- Staff Recruitment ---{Colors.RESET}")
        print(f"Available Funds: {Colors.GREEN}${self.finance.money:.2f}{Colors.RESET}")
        print("\nAvailable Staff Roles:")
        staff_roles = list(STAFF_CONFIG.items())
        for i, (name, config) in enumerate(staff_roles):
            print(f"  {i+1}. {name} (Salary: ${config['salary']}) - {config['description']}")
        try:
            choice_idx = int(input("\nChoose a role to hire for (or 0 to cancel): "))
            if choice_idx == 0:
                return
            if 1 <= choice_idx <= len(staff_roles):
                role, config = staff_roles[choice_idx - 1]
                if self.finance.money >= config['salary']:
                    staff_name = input(f"Enter a name for the new {role}: ")
                    if not staff_name.strip():
                        print(f"{Colors.RED}Staff name cannot be empty.{Colors.RESET}")
                    else:
                        new_staff = Staff(staff_name.strip(), role, config['salary'], config.get('base_skill', 30))
                        self.staff.append(new_staff)
                        print(f"\n{Colors.GREEN}{new_staff.name} the {role} has been hired! Their salary will be deducted daily.{Colors.RESET}")
                else:
                    print(f"\n{Colors.RED}You cannot afford the first salary payment for this role.{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}Invalid choice.{Colors.RESET}")
        except ValueError:
            print(f"\n{Colors.RED}Invalid input. Please enter a number.{Colors.RESET}")
        input("\nPress Enter to continue...")
    def view_reports(self):
        """Views detailed reports."""
        print(f"\n{Colors.HEADER}--- Detailed Reports ---{Colors.RESET}")
        print("\nAnimal Status:")
        if not self.animals:
            print("  No animals in the zoo.")
        for a in self.animals:
            print(f"  - {a.name} ({a.species}, {a.gender}, Age: {a.age}): Health {a.health:.0f}, Hunger {100-a.hunger:.0f}, Happiness {a.happiness:.0f}, Escape Risk: {a.escape_risk:.1f}%")
        print("\nHabitat Status:")
        if not self.habitats:
            print("  No habitats in the zoo.")
        for h in self.habitats:
            print(f"  - {h.name}: Cleanliness {h.cleanliness:.0f}/100, Security: {h.security}/100, Temp: {h.temperature}°C, Enrichment: {h.enrichment}")
        print("\nStaff Details:")
        if not self.staff:
            print("  No staff hired.")
        for s in self.staff:
            print(f"  - {s.name} ({s.role}): Skill {s.skill:.0f}/100, Fatigue {s.fatigue:.0f}/100")
        print(f"\n{Colors.HEADER}Visitor Feedback:{Colors.RESET}")
        if not self.visitors:
            print("  No visitors today to provide feedback.")
        else:
            avg_satisfaction = sum(v.satisfaction for v in self.visitors) / len(self.visitors)
            print(f"  Average Visitor Satisfaction: {avg_satisfaction:.1f}/100")
            all_thoughts = [thought for v in self.visitors for thought in v.thoughts]
            if not all_thoughts:
                print("  Your visitors seem quiet today. No specific feedback.")
            else:
                print("  Most common thoughts from your visitors:")
                thought_counts = Counter(all_thoughts)
                for thought, count in thought_counts.most_common(5):
                    print(f'    - "{thought}" ({count} times)')
        input("\nPress Enter to return to the main menu...")
    def manage_habitats(self):
        """Provides an interface to manage habitats."""
        print(f"\n{Colors.HEADER}--- Habitat Management ---{Colors.RESET}")
        if not self.habitats:
            print("You have no habitats to manage.")
            time.sleep(2)
            return
        for i, h in enumerate(self.habitats):
            cost = h.get_security_upgrade_cost()
            cost_str = f"Cost: ${cost}" if cost is not None else "Max Level"
            print(f"{i+1}. {h.name} - Security: {h.security}/100 ({cost_str})")
        try:
            choice = int(input("\nSelect a habitat to upgrade security (or 0 to cancel): "))
            if 0 < choice <= len(self.habitats):
                habitat_to_upgrade = self.habitats[choice - 1]
                habitat_to_upgrade.upgrade_security(self.finance)
            elif choice != 0:
                print(f"{Colors.RED}Invalid selection.{Colors.RESET}")
        except ValueError:
            print(f"{Colors.RED}Invalid input.{Colors.RESET}")
        input("\nPress Enter to continue...")
    def manage_staff(self):
        """Provides an interface to manage staff."""
        print(f"\n{Colors.HEADER}--- Staff Management ---{Colors.RESET}")
        if not self.staff:
            print("You have no staff to manage.")
            time.sleep(2)
            return
        for i, s in enumerate(self.staff):
            print(f"{i+1}. {s.name} ({s.role}) - Skill: {s.skill:.0f}, Fatigue: {s.fatigue:.0f}")
        try:
            choice = int(input("Select a staff member to train (or 0 to cancel): "))
            if 0 < choice <= len(self.staff):
                staff_to_train = self.staff[choice - 1]
                cost = 500
                skill_gain = 10
                if self.research_manager.is_unlocked('Efficient Staff Training'):
                    research_effect = RESEARCH_PROJECTS['Efficient Staff Training']['effect']
                    cost *= research_effect['cost_reduction']
                    skill_gain *= research_effect['skill_gain']
                print(f"Training {staff_to_train.name} will cost ${cost:.2f}.")
                confirm = input("Proceed? (y/n): ").lower()
                if confirm == 'y':
                    if self.finance.money >= cost:
                        self.finance.add_expense(cost, 'Staff Training')
                        staff_to_train.train(skill_gain)
                    else:
                        print(f"{Colors.RED}Not enough money for training.{Colors.RESET}")
            elif choice != 0:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")
        time.sleep(2)
    def _check_fossil_analysis(self):
        """Checks if the fossil analysis is complete."""
        if self.fossil_quest_stage == 2 and self.fossil_analysis_start_date:
            days_passed = (self.game_date - self.fossil_analysis_start_date).days
            if days_passed >= 3:
                print(f"\n{Colors.EVENT}--- Fossil Analysis Complete! ---{Colors.RESET}")
                print("The results from the university are in! You should check the 'Investigate Fossil' menu.")
                self.fossil_quest_stage = 3
                self.fossil_analysis_start_date = None 
    def investigate_fossil(self):
        """Handles the investigation of the mysterious fossil."""
        if self.fossil_quest_stage == 1:
            print(f"\n{Colors.HEADER}--- Mysterious Fossil ---{Colors.RESET}")
            print("The mysterious fossil you found is waiting for your decision.")
            print("A preliminary analysis by a local university will cost $2,000.")
            print("This could reveal its origins or it could be just a big rock.")
            print("\n1. Fund the analysis ($2,000)")
            print("2. Ignore it for now")
            choice = input("What will you do? ")
            if choice == '1':
                if self.finance.money >= 2000:
                    self.finance.add_expense(2000, "Fossil Analysis")
                    print("\nYou've sent the fossil off for analysis. The results should be back in a few days.")
                    self.fossil_quest_stage = 2
                    self.fossil_analysis_start_date = self.game_date
                else:
                    print(f"{Colors.RED}You don't have enough money for the analysis.{Colors.RESET}")
            else:
                print("\nThe fossil remains in storage, a mystery waiting to be solved.")
        elif self.fossil_quest_stage == 2:
            print("\nThe fossil is currently being analyzed. Check back in a day or two.")
        elif self.fossil_quest_stage == 3:
            print(f"\n{Colors.HEADER}--- Fossil Analysis Results ---{Colors.RESET}")
            print("The analysis confirms the fossil is from a large, prehistoric creature, likely a dinosaur!")
            print("However, the DNA is too fragmented to identify the exact species. You have two options:")
            print("\n1. The Scientific Path: Fund a cutting-edge research project to sequence the DNA. (Cost: $10,000)")
            print("   This is risky and expensive, but could lead to a groundbreaking discovery.")
            print("2. The Entertainment Path: Clean and display the fossil as a 'Mystery Dinosaur' exhibit.")
            print("   This is cheaper and will immediately boost visitor interest.")
            choice = input("Choose a path: ")
            if choice == '1':
                print("\nYou've chosen the path of science! A new research project is now available.")
                self.fossil_quest_stage = 4 
            elif choice == '2':
                print("\nYou've opted for showmanship. The 'Mystery Dinosaur' exhibit is now on display!")
                self.fossil_quest_stage = 5 
                self.dinosaur_exhibit_active = True
            else:
                print("You decide to wait on the decision. The fossil remains in storage.")
        input("\nPress Enter to continue...")