"""tidle, an idle game in the terminal."""
import os
import pickle as pkl
import time
import math
import signal

# constants

FOLDER = os.path.join(os.path.expanduser("~"), "TidleSaves")

# misc functions


def to_roman(num):
    """Converts an integer to a Roman numeral."""
    roman_map = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")
    ]
    result = ""
    for value, symbol in roman_map:
        while num >= value:
            result += symbol
            num -= value
    return result

# basic colors

COLORS = {
    "ticks": "\033[38;5;220m",  # Yellow-Orange
    "cycles": "\033[38;5;27m",  # Deep Blue
    "processes": "\033[38;5;34m",  # Green
    "loops": "\033[38;5;129m",  # Purple
    "optimization rate": "\033[38;5;214m",  # Bright Orange
}

# classes

class Achievement:
    """An achievement in the game."""

    def __init__(self, name, description, condition, hidden=False, counts_to_completion=True):
        self.name = name
        self.description = description
        self.condition = condition
        self.hidden = hidden
        self.counts_to_completion = counts_to_completion
        self.has_achieved = False

    def check(self):
        self.has_achieved = self.condition() if not self.has_achieved else True
        return self.has_achieved


class Command:
    """A command in the game."""

    def __init__(self, name, description, function):
        self.name = name
        self.description = description
        self.function = function

    def execute(self, *args):
        self.function(*args)

# Game class

class Game:
    def __init__(self):
        # currencies
        # exchange rate is 100x
        # (ex: 100 ticks = 1 cycle, 100 cycles = 1 process, 100 processes = 1 loop)
        self.optimization = 1  # rebirth multiplier
        self.resources = {
            "ticks": 0,
            "cycles": 0,
            "processes": 0,
            "loops": 0
        }
        self.auto_resources = {
            "ticks": 0,
            "cycles": 0,
            "processes": 0,
            "loops": 0
        }
        self.ticks_per_generation = 1  # ticks per click
        self.last_time = time.time()
        self.playtime = 0.0
        self.manual_ticks = 0

        # other variables
        self.achievement_objs = [
            Achievement("First Tick", "Generated your first tick.", self.check_first_tick),
            Achievement("First Cycle", "Generated your first cycle.", self.check_first_cycle),
            Achievement("First Process", "Generated your first process.", self.check_first_process),
            Achievement("First Loop", "Generated your first loop.", self.check_first_loop),
            Achievement("Tick Master", "Accumulate 100 ticks", self.check_tick_master),
            Achievement("Cycle Master", "Accumulate 100 cycles", self.check_cycle_master),
            Achievement("Process Master", "Accumulate 100 processes", self.check_process_master),
            Achievement("Loop Master", "Accumulate 100 loops", self.check_loop_master),
            Achievement("Pro Generator", "Upgrade your generation efficiency", self.check_pro_generator),
            Achievement("Optimization Master", "Refactor once", self.check_optimization_master),
            Achievement("Optimization Expert", "Refactor twice", self.check_optimization_expert),
            Achievement("Optimization God", "Refactor thrice", self.check_optimization_god),
            Achievement("Optimization Overload", "Refactor four times", self.check_optimization_overload),
            Achievement("Optimization Ascendant", "Refactor five times", self.check_optimization_ascendant),
            Achievement("That's Good", "Refactor six times", self.check_thats_good, True),
            Achievement("Ok, that's good.", "Refactor seven times", self.check_ok_thats_good, True),
            Achievement("Alright that's good.", "Refactor eight times", self.check_alright_thats_good, True),
            Achievement("That's good, that's good!", "Refactor nine times", self.check_thats_good_thats_good, True),
            Achievement("THAT'S ENOUGH REFACTORS!", "Refactor ten times", self.check_thats_enough_refactors, True),
            Achievement("The Answer", "have exactly 42 loops", self.check_the_answer, True),
            Achievement("Go outside", "play for an hour", self.check_go_outside),
            Achievement("Go to bed", "play for 8 hours", self.check_go_to_bed),
            Achievement("Get a life", "play for 24 hours", self.check_get_a_life),
            Achievement("You need help", "play for 48 hours", self.check_you_need_help),
            Achievement("It's Over 9000!", "have exactly 9001 ticks", self.check_its_over_9000, True),
            Achievement("Old Fashioned", "manually generate 100 ticks", self.check_old_fashioned),
            Achievement("Automation", "generate 100 or more ticks per second automatically", self.check_automation),
            Achievement("Slave to the System", "manually generate 1000 ticks", self.check_slave_to_the_system),
            Achievement("Perpetual Motion", "generate 50 or more cycles per second automatically", self.check_perpetual_motion),
            Achievement("Machine Learning", "generate 25 or more processes per second automatically", self.check_machine_learning),
            Achievement("While True", "generate 10 or more loops per second automatically", self.check_while_true),
            Achievement("Completionist", "unlock all other achievements", self.check_completionist),
            Achievement("One with the Machine", "accumulate 1 billion total resources", self.check_one_with_the_machine),
            Achievement("The Machine", "accumulate 1 trillion total resources", self.check_the_machine),
            Achievement("Skynet approved", "have all your auto generators for each resource at 10 or higher", self.check_skynet_approved),
            Achievement("Pi", "have exactly 314 ticks", self.check_pi, True),
            Achievement("Euler's Number", "have exactly 271 ticks", self.check_eulers_number, True),
            Achievement("Golden Ratio", "have exactly 1618 ticks", self.check_golden_ratio, True),
            Achievement("The Speed of Light", "have exactly 299792458 ticks", self.check_the_speed_of_light, True),
            Achievement("Trust me.", "have exactly 7274 ticks", self.check_trust_me, True),
            Achievement("Ghost recon", "Get every hidden achievement", self.check_ghost_recon),
            Achievement("Perfectly Balanced", "Have exactly 100 of each resource", self.check_perfectly_balanced, True),
        ]

        self.commands = [
            Command("generate", "Generate a tick.", self.generate_tick),
            Command("help", "Displays all commands and their descriptions.", self.help),
            Command("medals", "Displays all achievements and their descriptions.", self.achievements),
            Command("exit", "Save and exit the game.", self.exit),
            Command("save", "Save the game.", self.save),
            Command("exchange", "Exchange currencies. Arguments: currency1, currency2, amount of currency1 to exchange.",
                    self.exchange),
            Command("clear", "Clear the terminal.", self.clear),
            Command("store", "Open the store.", self.store),
            Command("delete", "Delete your save file permanently", self.delete_save),
            Command("stats", "Display all stats.", self.stats)
        ]

        self.upgrades = [
            {"name": "Generator Efficiency", "description": "Increases ticks per generation.", "base_cost": 10,
             "currency": "ticks",
             "effect": self.increase_ticks_per_generation},
            {"name": "Auto Generator", "description": "Increases auto-generated ticks.", "base_cost": 50,
             "currency": "ticks",
             "effect": self.increase_auto_ticks},
            {"name": "Cycle Booster", "description": "Generates cycles over time.", "base_cost": 10,
             "currency": "cycles",
             "effect": self.increase_auto_cycles},
            {"name": "Process Enhancer", "description": "Generates processes over time.", "base_cost": 10,
             "currency": "processes",
             "effect": self.increase_auto_processes},
            {"name": "Loop Accelerator", "description": "Speeds up loop generation.", "base_cost": 10,
             "currency": "loops",
             "effect": self.increase_auto_loops},
            {"name": "Refactorize", "description": "Increases optimization rate, but resets all resources and upgrades.", "base_cost": 1000, "currency": "loops",
             "effect": self.rebirth}
        ]

    # ACHIEVEMENTS

    def check_perfectly_balanced(self):
        return all([self.resources[resource] == 100 for resource in self.resources])

    def check_first_tick(self):
        return self.resources["ticks"] >= 1

    def check_first_cycle(self):
        return self.resources["cycles"] >= 1

    def check_first_process(self):
        return self.resources["processes"] >= 1

    def check_first_loop(self):
        return self.resources["loops"] >= 1

    def check_tick_master(self):
        return self.resources["ticks"] >= 100

    def check_cycle_master(self):
        return self.resources["cycles"] >= 100

    def check_process_master(self):
        return self.resources["processes"] >= 100

    def check_loop_master(self):
        return self.resources["loops"] >= 100

    def check_pro_generator(self):
        return self.ticks_per_generation >= 2

    def check_optimization_master(self):
        return self.optimization >= 2

    def check_optimization_expert(self):
        return self.optimization >= 3

    def check_optimization_god(self):
        return self.optimization >= 4

    def check_optimization_overload(self):
        return self.optimization >= 5

    def check_optimization_ascendant(self):
        return self.optimization >= 6

    def check_thats_good(self):
        return self.optimization >= 7

    def check_ok_thats_good(self):
        return self.optimization >= 8

    def check_alright_thats_good(self):
        return self.optimization >= 9

    def check_thats_good_thats_good(self):
        return self.optimization >= 10

    def check_thats_enough_refactors(self):
        return self.optimization >= 11

    def check_the_answer(self):
        return self.resources["loops"] == 42

    def check_go_outside(self):
        return self.playtime >= 3600

    def check_go_to_bed(self):
        return self.playtime >= 28800

    def check_get_a_life(self):
        return self.playtime >= 86400

    def check_you_need_help(self):
        return self.playtime >= 172800

    def check_its_over_9000(self):
        return self.resources["ticks"] == 9001

    def check_old_fashioned(self):
        return self.manual_ticks >= 100

    def check_automation(self):
        return self.auto_resources["ticks"] >= 100

    def check_slave_to_the_system(self):
        return self.manual_ticks >= 1000

    def check_perpetual_motion(self):
        return self.auto_resources["cycles"] >= 50

    def check_machine_learning(self):
        return self.auto_resources["processes"] >= 25

    def check_while_true(self):
        return self.auto_resources["loops"] >= 10

    def check_completionist(self):
        return all([achievement.check() for achievement in [achievement for achievement in self.achievement_objs if achievement.name != "Completionist"]])

    def check_one_with_the_machine(self):
        return sum([self.resources[resource] for resource in self.resources]) >= 1_000_000_000

    def check_the_machine(self):
        return sum([self.resources[resource] for resource in self.resources]) >= 1_000_000_000_000

    def check_skynet_approved(self):
        return all([self.auto_resources[resource] >= 10 for resource in self.auto_resources])

    def check_pi(self):
        return self.resources["ticks"] == 314159

    def check_eulers_number(self):
        return self.resources["ticks"] == 271828

    def check_golden_ratio(self):
        return self.resources["ticks"] == 1618

    def check_the_speed_of_light(self):
        return self.resources["ticks"] == 299792458

    def check_trust_me(self):
        return self.resources["ticks"] == 7274

    def check_ghost_recon(self):
        return all([achievement.check() for achievement in [achievement for achievement in self.achievement_objs if achievement.hidden]])

    def increase_ticks_per_generation(self):
        self.ticks_per_generation += 1

    def increase_auto_ticks(self):
        self.auto_resources["ticks"] += 1

    def increase_auto_cycles(self):
        self.auto_resources["cycles"] += 1

    def increase_auto_processes(self):
        self.auto_resources["processes"] += 1

    def increase_auto_loops(self):
        self.auto_resources["loops"] = int(self.auto_resources["loops"] + 1)

    # COMMANDS

    def stats(self):
        print(f"Playtime: {self.playtime:.2f} seconds")
        print(f"Manual ticks generated: {self.manual_ticks}")
        print(f"Optimization rate: {self.optimization}")
        print(f"Ticks per generation: {self.ticks_per_generation}")

    def delete_save(self):
        really_delete = input("Are you sure you want to delete your save? It's irreversible. (y/n) ")
        if really_delete.lower() == "y":
            os.remove(os.path.join(FOLDER, "game.pkl"))
            print("Save deleted, see you another time.")
            exit()

    def clear(self):
        os.system("clear" if os.name == "posix" else "cls")

    def help(self):
        print("Commands:")
        for command in self.commands:
            print(f"{command.name}: {command.description}")

    def achievements(self):
        # make progress bar for 100% completion
        completed = len([achievement for achievement in self.achievement_objs if achievement.check() or achievement.has_achieved])
        total = len(self.achievement_objs)
        hiddens = 0
        print(f"Achievements: {completed}/{total} ({completed / total * 100:.2f}%)")
        for achievement in self.achievement_objs:
            # hide achievements that are not achieved and are hidden
            if not achievement.hidden or achievement.check() or achievement.has_achieved:
                print(f"{achievement.name}: {achievement.description} | {'achieved' if achievement.check() or achievement.has_achieved else 'not achieved'}")
            else:
                hiddens += 1
        print("????: Hidden achievement | not achieved\n" * hiddens)

    def generate_tick(self):
        self.resources["ticks"] += math.floor(self.ticks_per_generation * self.optimization)
        self.manual_ticks += 1

    def save(self):
        with open(os.path.join(FOLDER, "game.pkl"), "wb") as f:
            pkl.dump(self, f)
        print("Game saved.")

    def exit(self):
        self.save()
        exit()

    def exchange(self, currency1, currency2, amount):
        """
        Converts `amount` of `currency1` into `currency2`, assuming a 100x exchange rate per tier.
        The player must have enough of `currency1` to exchange.
        """
        tiers = ["ticks", "cycles", "processes", "loops"]
        try:
            amount = int(amount)
        except ValueError:
            print("Invalid amount.")
            return

        if currency1 not in tiers or currency2 not in tiers:
            print("Invalid currency.")
            return

        index1, index2 = tiers.index(currency1), tiers.index(currency2)

        if index1 >= index2:
            print("Invalid exchange direction. You can only exchange currency to a higher tier.")
            return

        exchange_rate = 100 ** (index2 - index1)
        required_currency1 = amount * exchange_rate

        if self.resources[currency1] < required_currency1:
            print("Insufficient currency to exchange.")
            return

        # Deduct currency1 and add currency2
        self.resources[currency1] -= required_currency1
        self.resources[currency2] += amount

    def store(self):
        """Handles the in-game shop where players can buy upgrades."""

        def to_roman(num):
            """Converts an integer to a Roman numeral."""
            roman_map = [
                (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
                (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
                (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")
            ]
            result = ""
            for value, symbol in roman_map:
                while num >= value:
                    result += symbol
                    num -= value
            return result

        # Ensure upgrade levels persist across store visits
        if not hasattr(self, "upgrade_levels"):
            self.upgrade_levels = {upgrade["name"]: 0 for upgrade in self.upgrades}

        while True:
            print("\nStore - Buy upgrades to improve efficiency:")
            for i, upgrade in enumerate(self.upgrades):
                level = self.upgrade_levels[upgrade["name"]]
                cost = int(upgrade["base_cost"] * (1.5 ** level))  # Prices increase exponentially
                roman_level = to_roman(level + 1)  # Convert level to Roman numerals
                print(
                    f"{i + 1}. {upgrade['name']} {roman_level} ({upgrade['description']}) - Cost: {cost} {upgrade['currency']}")

            print("Type the number of the upgrade to purchase, or 'exit' to leave.")
            choice = input("||> ")

            if choice.lower() == "exit":
                break

            try:
                choice = int(choice) - 1
                if 0 <= choice < len(self.upgrades):
                    upgrade = self.upgrades[choice]
                    level = self.upgrade_levels[upgrade["name"]]
                    cost = int(upgrade["base_cost"] * (1.5 ** level))

                    if self.resources[upgrade["currency"]] >= cost:
                        self.resources[upgrade["currency"]] -= cost
                        upgrade["effect"]()
                        self.upgrade_levels[upgrade["name"]] += 1  # Upgrade quality increases
                        print(f"Purchased {upgrade['name']} {to_roman(level + 1)}! Upgrades are now more expensive.")
                    else:
                        print("Not enough currency!")
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid input. Enter a number or 'exit'.")

    def rebirth(self):
        """Resets the game, increasing the optimization rate."""
        self.optimization += 1
        self.resources = {
            "ticks": 0,
            "cycles": 0,
            "processes": 0,
            "loops": 0
        }
        self.auto_resources = {
            "ticks": 0,
            "cycles": 0,
            "processes": 0,
            "loops": 0
        }
        self.ticks_per_generation = 1
        # reset all upgrades (except refactoring)
        self.upgrade_levels = {upgrade["name"]: 0 for upgrade in self.upgrades if upgrade["name"] != "Refactorize"}

# main loop
def main():
    print("Welcome to tidle!")
    # ensure folder exists
    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)
    try:
        with open(os.path.join(FOLDER, "game.pkl"), "rb") as f:
            game = pkl.load(f)
    except FileNotFoundError:
        game = Game()

    def safe_shutdown(sig, frame):
        """Saves the game and exits."""
        print("Cya soon!")
        game.save()
        exit()

    signal.signal(signal.SIGINT, safe_shutdown)

    while True:
        # update the user on their currencies
        all_resources = game.resources
        all_resources["optimization rate"] = game.optimization
        print("\033[0m | ".join([f"{COLORS[currency]}{currency}: {game.resources[currency]}" for currency in game.resources]) + "\033[0m")
        # get auto rates
        print("RPS (Resources Per Second):")
        print("\033[0m | ".join([f"{COLORS[currency]}{currency}: {game.auto_resources[currency]}" for currency in game.auto_resources]) + "\033[0m")
        command = input("||> ").split()
        # break the input into command and arguments
        try:
            command_name = command[0]
            command_args = command[1:]
        except IndexError:
            print("No command entered.")
            continue
        # it's command time
        if command_name in [command.name for command in game.commands]:
            for command in game.commands:
                if command.name == command_name:
                    current_time = time.time()
                    time_elapsed = current_time - game.last_time
                    game.last_time = current_time
                    game.playtime += time_elapsed
                    for resource in game.auto_resources:
                        game.resources[resource] += math.floor(game.auto_resources[resource] * time_elapsed)
                    before_achievement_states = {}
                    for achievement in game.achievement_objs:
                        before_achievement_states[achievement.name] = achievement.check()
                    command.execute(*command_args)
                    # check for achievements
                    for achievement in game.achievement_objs:
                        if achievement.check() != before_achievement_states[achievement.name]:
                            print(f"Achievement unlocked: {achievement.name} - {achievement.description}")
                    break
        else:
            print("Invalid command.")
        print("\n")

if __name__ == "__main__":
    main()