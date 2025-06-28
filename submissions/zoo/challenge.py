from zoo import Zoo
from animal import Animal
from habitat import Habitat
from config import ANIMAL_CONFIG, HABITAT_CONFIG
def get_rescue_zoo_challenge():
    """Configures and returns a Zoo object for the 'Rescue Zoo' challenge."""
    zoo = Zoo("Struggling Safari")
    zoo.finance.money = 500
    zoo.finance.add_expense(10000, "Initial Debt", on_day_zero=True)
    savannah_config = HABITAT_CONFIG['Savannah']
    savannah = Habitat("Dusty Plains", "Savannah", savannah_config['capacity'], savannah_config['base_temp'], savannah_config['base_enrichment'])
    savannah.cleanliness = 20
    savannah.enrichment = 10
    zoo.habitats.append(savannah)
    jungle_config = HABITAT_CONFIG['Jungle']
    jungle = Habitat("Overgrown Grove", "Jungle", jungle_config['capacity'], jungle_config['base_temp'], jungle_config['base_enrichment'])
    jungle.cleanliness = 30
    jungle.enrichment = 15
    zoo.habitats.append(jungle)
    zebra_config = ANIMAL_CONFIG['Zebra']
    leo_config = ANIMAL_CONFIG['Lion']
    zara = Animal('Zebra', 'Zara', zebra_config, age=5)
    zara.hunger = 40
    zara.happiness = 25
    savannah.add_animal(zara)
    zoo.animals.append(zara)
    leo = Animal('Lion', 'Leo', leo_config, age=8)
    leo.hunger = 30
    leo.happiness = 20
    jungle.add_animal(leo)
    zoo.animals.append(leo)
    zoo.challenge_data = {
        'name': 'Rescue Zoo',
        'description': 'Take over a failing zoo and turn its fortunes around!',
        'win_conditions': {
            'money': 20000,
            'reputation': 60 
        },
        'loss_conditions': {
            'money': 0
        }
    }
    return zoo
CHALLENGES = {
    '1': {
        'name': 'Rescue Zoo',
        'function': get_rescue_zoo_challenge
    }
}