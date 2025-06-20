import random
from colorama import Fore, Style, init
init(autoreset=True)
class Colors:
    HEADER = Fore.MAGENTA + Style.BRIGHT
    BLUE = Fore.BLUE + Style.BRIGHT
    GREEN = Fore.GREEN + Style.BRIGHT
    YELLOW = Fore.YELLOW + Style.BRIGHT
    RED = Fore.RED + Style.BRIGHT
    EVENT = Fore.CYAN + Style.BRIGHT
    RESET = Style.RESET_ALL
def random_event(zoo):
    """Generates a random event."""
    events = [
        {'name': 'Animal Sickness', 'handler': handle_sickness},
        {'name': 'PR Boost', 'handler': handle_pr_boost},
    ]
    event = random.choice(events)
    print(f"\n*** RANDOM EVENT: {event['name']} ***")
    event['handler'](zoo)
def handle_sickness(zoo):
    """Handles an animal sickness event."""
    if zoo.animals:
        animal = random.choice(zoo.animals)
        animal.health -= 20
        print(f"{animal.name} the {animal.species} has fallen ill!")
    else:
        print("A sickness scare passed without incident.")
def handle_pr_boost(zoo):
    """Handles a PR boost event."""
    boost = random.randint(10, 30)
    zoo.finance.money += boost * 10
    print(f"Positive media coverage has boosted your reputation and income!")