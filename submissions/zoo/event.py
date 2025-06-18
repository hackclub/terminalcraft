import random
from config import RANDOM_EVENTS
from utils import Colors
def trigger_event(zoo):
    """Checks for and triggers a random event based on configured chances."""
    for event_name, event_config in RANDOM_EVENTS.items():
        if random.random() < event_config['chance']:
            if _is_event_possible(zoo, event_name):
                print(f"\n{Colors.EVENT}--- Random Event ---{Colors.RESET}")
                _handle_event(zoo, event_name, event_config)
                return 
def _is_event_possible(zoo, event_name):
    """Check if the conditions for an event are met."""
    if event_name == 'surprise_birth':
        return any(h.can_breed() for h in zoo.habitats)
    if event_name == 'habitat_malfunction':
        return bool(zoo.habitats)
    return True 
def _handle_event(zoo, event_name, config):
    """Directs the event to the correct handler based on its effect type."""
    effect = config['effect']
    effect_type = effect['type']
    if effect_type in ['donation', 'financial_loss']:
        _handle_financial_event(zoo, config)
    elif effect_type in ['health_decline', 'new_animal']:
        _handle_animal_event(zoo, config)
    elif effect_type == 'habitat_damage':
        _handle_habitat_event(zoo, config)
    elif effect_type == 'visitor_boost':
        _handle_reputation_event(zoo, config)
    else:
        print(f"Warning: Unhandled event effect type '{effect_type}'")
def _handle_financial_event(zoo, config):
    """Handles events that directly affect finances."""
    effect = config['effect']
    min_val, max_val = effect['amount']
    amount = random.randint(min_val, max_val)
    if effect['type'] == 'donation':
        zoo.finance.add_income(amount, 'Event Donation')
        print(config['message'] + f" They donated ${amount}!" )
    elif effect['type'] == 'financial_loss':
        zoo.finance.add_expense(amount, 'Event Loss')
        print(config['message'] + f" You lost ${amount}." )
def _handle_animal_event(zoo, config):
    """Handles events related to animals."""
    effect = config['effect']
    if effect['type'] == 'new_animal':
        possible_habitats = [h for h in zoo.habitats if h.can_breed() and h.has_space()]
        if possible_habitats:
            habitat = random.choice(possible_habitats)
            species = habitat.species_type
            zoo._birth_animal(species, habitat)
            print(config['message'].format(species=species))
    elif effect['type'] == 'health_decline':
        species = effect.get('species', 'all')
        amount = effect['amount']
        if species == 'all':
            for animal in zoo.animals:
                animal.health = max(10, animal.health - amount)
            print(config['message'].format(species='animals'))
        else:
            for animal in zoo.animals:
                if animal.species == species:
                    animal.health = max(10, animal.health - amount)
            print(config['message'].format(species=species))
def _handle_habitat_event(zoo, config):
    """Handles events that damage habitats."""
    effect = config['effect']
    target_habitat = random.choice(zoo.habitats)
    system = random.choice(['temperature', 'enrichment'])
    cost = random.randint(*effect['cost'])
    print(config['message'].format(habitat_name=target_habitat.name, system=system))
    print(f"Repairs will cost ${cost}.")
    zoo.finance.add_expense(cost, f"{target_habitat.name} Repair")
def _handle_reputation_event(zoo, config):
    """Handles events that affect visitor numbers or reputation."""
    effect = config['effect']
    if effect['type'] == 'visitor_boost':
        zoo.visitor_boost = {'multiplier': effect['multiplier'], 'duration': effect['duration']}
        print(config['message'] + f" Expect more visitors for the next {effect['duration']} days!")