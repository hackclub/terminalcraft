import random
import time
import math
import os
import pickle
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set, Callable, Union
from collections import defaultdict
from colorama import init, Fore, Back, Style
import shutil

init(autoreset=True)

class GameState:
    def __init__(self):
        self.player = Player()
        self.universe = Universe()
        self.current_planet = self.universe.planets[0]
        self.day = 1
        self.max_days = 100
        self.game_over = False
        self.victory = False

class ItemType(Enum):
    FOOD = "Food"
    MEDICINE = "Medicine"
    ELECTRONICS = "Electronics"
    WEAPONS = "Weapons"
    LUXURY = "Luxury Goods"
    MINERALS = "Minerals"
    FUEL = "Fuel"
    TECHNOLOGY = "Technology"

class Item:
    def __init__(self, type: ItemType, base_price: int):
        self.type = type
        self.base_price = base_price
        
    def get_price(self, modifier: float) -> int:
        return max(1, int(self.base_price * modifier))
        
    def __str__(self) -> str:
        return self.type.value

class PlanetType(Enum):
    AGRICULTURAL = "Agricultural"
    INDUSTRIAL = "Industrial"
    MINING = "Mining"
    RESORT = "Resort"
    TECH = "Tech Hub"
    MILITARY = "Military Base"

class Planet:
    def __init__(self, name: str, type: PlanetType, x: int, y: int):
        self.name = name
        self.type = type
        self.x = x
        self.y = y
        self.market = Market(self)
        self.refresh_market()
        
    def refresh_market(self):
        self.market.refresh_prices()
        
    def distance_to(self, other_planet) -> float:
        return math.sqrt((self.x - other_planet.x) ** 2 + (self.y - other_planet.y) ** 2)
        
    def __str__(self) -> str:
        return f"{self.name} ({self.type.value})"

class Market:
    def __init__(self, planet: Planet):
        self.planet = planet
        self.items = {
            ItemType.FOOD: Item(ItemType.FOOD, 100),
            ItemType.MEDICINE: Item(ItemType.MEDICINE, 200),
            ItemType.ELECTRONICS: Item(ItemType.ELECTRONICS, 300),
            ItemType.WEAPONS: Item(ItemType.WEAPONS, 500),
            ItemType.LUXURY: Item(ItemType.LUXURY, 1000),
            ItemType.MINERALS: Item(ItemType.MINERALS, 250),
            ItemType.FUEL: Item(ItemType.FUEL, 10),
            ItemType.TECHNOLOGY: Item(ItemType.TECHNOLOGY, 1500)
        }
        self.price_modifiers = {}
        
    def refresh_prices(self):
        base_modifiers = {
            PlanetType.AGRICULTURAL: {
                ItemType.FOOD: 0.6,
                ItemType.MEDICINE: 0.9,
                ItemType.ELECTRONICS: 1.2,
                ItemType.WEAPONS: 1.1,
                ItemType.LUXURY: 1.3,
                ItemType.MINERALS: 1.2,
                ItemType.FUEL: 1.1,
                ItemType.TECHNOLOGY: 1.4
            },
            PlanetType.INDUSTRIAL: {
                ItemType.FOOD: 1.2,
                ItemType.MEDICINE: 1.0,
                ItemType.ELECTRONICS: 0.8,
                ItemType.WEAPONS: 0.7,
                ItemType.LUXURY: 1.0,
                ItemType.MINERALS: 0.9,
                ItemType.FUEL: 0.9,
                ItemType.TECHNOLOGY: 0.8
            },
            PlanetType.MINING: {
                ItemType.FOOD: 1.3,
                ItemType.MEDICINE: 1.1,
                ItemType.ELECTRONICS: 1.0,
                ItemType.WEAPONS: 0.9,
                ItemType.LUXURY: 1.2,
                ItemType.MINERALS: 0.5,
                ItemType.FUEL: 1.0,
                ItemType.TECHNOLOGY: 1.1
            },
            PlanetType.RESORT: {
                ItemType.FOOD: 0.9,
                ItemType.MEDICINE: 0.8,
                ItemType.ELECTRONICS: 1.1,
                ItemType.WEAPONS: 1.5,
                ItemType.LUXURY: 0.7,
                ItemType.MINERALS: 1.3,
                ItemType.FUEL: 1.2,
                ItemType.TECHNOLOGY: 1.3
            },
            PlanetType.TECH: {
                ItemType.FOOD: 1.1,
                ItemType.MEDICINE: 0.9,
                ItemType.ELECTRONICS: 0.6,
                ItemType.WEAPONS: 0.8,
                ItemType.LUXURY: 1.0,
                ItemType.MINERALS: 1.1,
                ItemType.FUEL: 0.8,
                ItemType.TECHNOLOGY: 0.7
            },
            PlanetType.MILITARY: {
                ItemType.FOOD: 1.0,
                ItemType.MEDICINE: 1.2,
                ItemType.ELECTRONICS: 1.1,
                ItemType.WEAPONS: 0.6,
                ItemType.LUXURY: 1.4,
                ItemType.MINERALS: 1.0,
                ItemType.FUEL: 0.7,
                ItemType.TECHNOLOGY: 1.2
            }
        }
        
        base = base_modifiers[self.planet.type]
        
        for item_type in ItemType:
            fluctuation = random.uniform(0.8, 1.2)
            self.price_modifiers[item_type] = base[item_type] * fluctuation
            
    def get_buy_price(self, item_type: ItemType) -> int:
        return self.items[item_type].get_price(self.price_modifiers[item_type])
        
    def get_sell_price(self, item_type: ItemType) -> int:
        return int(self.get_buy_price(item_type) * 0.85)

class Ship:
    def __init__(self, name: str, cargo_capacity: int, fuel_capacity: int, speed: int):
        self.name = name
        self.cargo_capacity = cargo_capacity
        self.fuel_capacity = fuel_capacity
        self.current_fuel = fuel_capacity
        self.speed = speed
        self.cargo = {}
        
    def get_cargo_space_used(self) -> int:
        return sum(self.cargo.values())
        
    def get_cargo_space_available(self) -> int:
        return self.cargo_capacity - self.get_cargo_space_used()
        
    def add_cargo(self, item_type: ItemType, amount: int) -> bool:
        if self.get_cargo_space_available() < amount:
            return False
            
        if item_type in self.cargo:
            self.cargo[item_type] += amount
        else:
            self.cargo[item_type] = amount
        return True
        
    def remove_cargo(self, item_type: ItemType, amount: int) -> bool:
        if item_type not in self.cargo or self.cargo[item_type] < amount:
            return False
            
        self.cargo[item_type] -= amount
        if self.cargo[item_type] == 0:
            del self.cargo[item_type]
        return True
        
    def __str__(self) -> str:
        return f"{self.name} (Cargo: {self.get_cargo_space_used()}/{self.cargo_capacity}, Fuel: {self.current_fuel}/{self.fuel_capacity})"

class Player:
    def __init__(self):
        self.credits = 1000
        self.ship = Ship("Starter Ship", 50, 100, 10)
        self.debt = 0
        self.has_special_cargo = False
        
    def can_afford(self, amount: int) -> bool:
        return self.credits >= amount
        
    def pay(self, amount: int) -> bool:
        if not self.can_afford(amount):
            return False
        self.credits -= amount
        return True
        
    def receive(self, amount: int):
        self.credits += amount
        
    def __str__(self) -> str:
        return f"Credits: {self.credits}, Debt: {self.debt}"

class Universe:
    def __init__(self):
        self.planets = self._generate_planets()
        self.events = self._generate_events()
        
    def _generate_planets(self) -> List[Planet]:
        planet_names = [
            "Terra Nova", "Proxima", "Kepler", "Osiris", "Pandora",
            "Centauri", "Elysium", "Hyperion", "Novus", "Thalassa"
        ]
        
        planet_types = list(PlanetType)
        
        planets = []
        for i in range(10):
            name = planet_names[i]
            type = random.choice(planet_types)
            x = random.randint(0, 100)
            y = random.randint(0, 100)
            planets.append(Planet(name, type, x, y))
            
        return planets
        
    def _generate_events(self) -> Dict[int, str]:
        events = {
            10: "A trade embargo has been imposed! All prices have increased by 20%.",
            25: "A new hyperspace route has been discovered! Travel costs reduced by 30% for 5 days.",
            40: "Economic boom! Selling prices increased by 25% for 3 days.",
            60: "Pirate activity reported! There's a 20% chance of losing cargo during travel for 7 days.",
            75: "Trade festival! Buy prices reduced by 15% for 5 days.",
            90: "Fuel shortage! Fuel costs increased by 50% for 10 days."
        }
        return events

class Game:
    def __init__(self):
        self.state = None
        self.event_effects = {}
        
    def new_game(self):
        self.state = GameState()
        self.event_effects = {}
        self._main_loop()
        
    def load_game(self, filename: str) -> bool:
        try:
            with open(filename, 'rb') as f:
                saved_data = pickle.load(f)
                self.state = saved_data['state']
                self.event_effects = saved_data['event_effects']
            return True
        except Exception as e:
            print(f"Error loading game: {e}")
            return False
            
    def save_game(self, filename: str) -> bool:
        try:
            with open(filename, 'wb') as f:
                saved_data = {
                    'state': self.state,
                    'event_effects': self.event_effects
                }
                pickle.dump(saved_data, f)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
            
    def _main_loop(self):
        while not self.state.game_over:
            self._check_events()
            self._display_status()
            self._handle_player_input()
            
            if self.state.day >= self.state.max_days:
                self._end_game()
                
        self._display_game_over()
        
    def _check_events(self):
        if self.state.day in self.state.universe.events:
            event_msg = self.state.universe.events[self.state.day]
            print(f"\n*** EVENT: {event_msg} ***\n")
            
            if "trade embargo" in event_msg.lower():
                self.event_effects["price_multiplier"] = 1.2
                self.event_effects["price_multiplier_end"] = self.state.day + 5
            elif "hyperspace route" in event_msg.lower():
                self.event_effects["travel_cost_multiplier"] = 0.7
                self.event_effects["travel_cost_multiplier_end"] = self.state.day + 5
            elif "economic boom" in event_msg.lower():
                self.event_effects["sell_price_multiplier"] = 1.25
                self.event_effects["sell_price_multiplier_end"] = self.state.day + 3
            elif "pirate activity" in event_msg.lower():
                self.event_effects["pirate_chance"] = 0.2
                self.event_effects["pirate_chance_end"] = self.state.day + 7
            elif "trade festival" in event_msg.lower():
                self.event_effects["buy_price_multiplier"] = 0.85
                self.event_effects["buy_price_multiplier_end"] = self.state.day + 5
            elif "fuel shortage" in event_msg.lower():
                self.event_effects["fuel_cost_multiplier"] = 1.5
                self.event_effects["fuel_cost_multiplier_end"] = self.state.day + 10
        
        keys_to_remove = []
        for effect, end_day in list(self.event_effects.items()):
            if effect.endswith("_end") and self.state.day >= end_day:
                base_effect = effect.replace("_end", "")
                keys_to_remove.append(base_effect)
                keys_to_remove.append(effect)
                
        for key in keys_to_remove:
            if key in self.event_effects:
                del self.event_effects[key]
        
    def _display_status(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        draw_ship_ascii()
        print_header(f"SPACE TRADER - Day {self.state.day}/{self.state.max_days}")
        
        print_info("Location", str(self.state.current_planet), Fore.GREEN)
        print_info("Credits", f"{self.state.player.credits:,}", Fore.YELLOW)
        
        if self.state.player.debt > 0:
            print_info("Debt", f"{self.state.player.debt:,}", Fore.RED)
        
        print("\n" + Fore.CYAN + "=== Ship Status ===" + Style.RESET_ALL)
        print_info("Ship", str(self.state.player.ship))
        print_info("Cargo Space", f"{self.state.player.ship.get_cargo_space_used()}/{self.state.player.ship.cargo_capacity}")
        print_info("Fuel", f"{self.state.player.ship.current_fuel}/{self.state.player.ship.fuel_capacity}")
        
        if self.state.player.ship.cargo:
            print("\n" + Fore.CYAN + "=== Cargo ===" + Style.RESET_ALL)
            for item_type, amount in self.state.player.ship.cargo.items():
                print_info(f"  {item_type.value}", f"{amount} units")
        else:
            print("\n" + Fore.CYAN + "=== Cargo ===" + Style.RESET_ALL)
            print("  Empty")
        
        print("\n" + Fore.CYAN + "=== Market Prices ===" + Style.RESET_ALL)
        for item_type in ItemType:
            buy_price = self._get_modified_buy_price(item_type)
            sell_price = self._get_modified_sell_price(item_type)
            print(f"  {item_type.value}:")
            print(f"    Buy: {Fore.RED}{buy_price:,}{Style.RESET_ALL} credits")
            print(f"    Sell: {Fore.GREEN}{sell_price:,}{Style.RESET_ALL} credits")
        
        if self.event_effects:
            print("\n" + Fore.YELLOW + "=== Active Events ===" + Style.RESET_ALL)
            for effect in self.event_effects:
                if not effect.endswith("_end"):
                    days_left = self.event_effects[effect + "_end"] - self.state.day
                    effect_name = effect.replace("_", " ").title()
                    print_info(f"  {effect_name}", f"{days_left} days remaining")
        
    def _handle_player_input(self):
        print("\n" + Fore.CYAN + "=== Actions ===" + Style.RESET_ALL)
        print_menu_option("1", "Buy Goods", Fore.GREEN)
        print_menu_option("2", "Sell Goods", Fore.YELLOW)
        print_menu_option("3", "Travel to Another Planet", Fore.BLUE)
        print_menu_option("4", "Refuel Ship", Fore.MAGENTA)
        print_menu_option("5", "Take Loan", Fore.RED)
        print_menu_option("6", "Repay Loan", Fore.GREEN)
        print_menu_option("7", "Special Missions", Fore.YELLOW)
        print_menu_option("8", "Save Game", Fore.CYAN)
        print_menu_option("9", "Quit Game", Fore.RED)
        
        choice = input(f"\n{Fore.CYAN}Enter your choice (1-9):{Style.RESET_ALL} ").strip()
        
        if choice == "1":
            self._buy_goods()
        elif choice == "2":
            self._sell_goods()
        elif choice == "3":
            self._travel()
        elif choice == "4":
            self._refuel()
        elif choice == "5":
            self._take_loan()
        elif choice == "6":
            self._repay_loan()
        elif choice == "7":
            self._special_missions()
        elif choice == "8":
            filename = input("Enter save file name: ").strip()
            if self.save_game(filename):
                print(f"Game saved to {filename}")
            else:
                print("Failed to save game")
        elif choice == "9":
            confirm = input("Are you sure you want to quit? (y/n): ").strip().lower()
            if confirm == "y":
                self._end_game()
        else:
            print("Invalid choice")
            
        input("\nPress Enter to continue...")
        
    def _buy_goods(self):
        print("\n=== BUY GOODS ===")
        
        print("\nAvailable Items:")
        for i, item_type in enumerate(ItemType, 1):
            buy_price = self._get_modified_buy_price(item_type)
            print(f"{i}. {item_type.value}: {buy_price} credits each")
            
        print(f"{len(ItemType) + 1}. Back")
        
        try:
            choice = int(input("\nEnter your choice (1-7): ").strip())
            
            if choice == len(ItemType) + 1:
                return
                
            if 1 <= choice <= len(ItemType):
                item_type = list(ItemType)[choice - 1]
                max_amount = min(
                    self.state.player.ship.get_cargo_space_available(),
                    self.state.player.credits // self._get_modified_buy_price(item_type)
                )
                
                if max_amount <= 0:
                    print("You can't afford any units or don't have enough cargo space!")
                    return
                    
                print(f"You can buy up to {max_amount} units")
                amount = int(input(f"How many units of {item_type.value} do you want to buy? "))
                
                if amount <= 0:
                    print("Transaction cancelled")
                    return
                    
                if amount > max_amount:
                    print(f"You can only buy {max_amount} units")
                    return
                    
                total_cost = amount * self._get_modified_buy_price(item_type)
                
                if not self.state.player.pay(total_cost):
                    print("You don't have enough credits!")
                    return
                    
                self.state.player.ship.add_cargo(item_type, amount)
                print(f"Bought {amount} units of {item_type.value} for {total_cost} credits")
            else:
                print("Invalid choice")
        except ValueError:
            print("Please enter a valid number")
        
    def _sell_goods(self):
        print("\n=== SELL GOODS ===")
        
        if not self.state.player.ship.cargo:
            print("You don't have any cargo to sell!")
            return
            
        print("\nCargo to Sell:")
        cargo_items = list(self.state.player.ship.cargo.items())
        
        for i, (item_type, amount) in enumerate(cargo_items, 1):
            sell_price = self._get_modified_sell_price(item_type)
            total = sell_price * amount
            print(f"{i}. {item_type.value}: {amount} units @ {sell_price} credits = {total} credits")
            
        print(f"{len(cargo_items) + 1}. Back")
        
        try:
            choice = int(input("\nEnter your choice (1-{0}): ".format(len(cargo_items) + 1)).strip())
            
            if choice == len(cargo_items) + 1:
                return
                
            if 1 <= choice <= len(cargo_items):
                item_type, current_amount = cargo_items[choice - 1]
                
                max_amount = current_amount
                sell_price = self._get_modified_sell_price(item_type)
                
                print(f"You have {max_amount} units to sell")
                amount = int(input(f"How many units of {item_type.value} do you want to sell? "))
                
                if amount <= 0:
                    print("Transaction cancelled")
                    return
                    
                if amount > max_amount:
                    print(f"You only have {max_amount} units")
                    return
                    
                total_earned = amount * sell_price
                
                self.state.player.ship.remove_cargo(item_type, amount)
                self.state.player.receive(total_earned)
                
                print(f"Sold {amount} units of {item_type.value} for {total_earned} credits")
            else:
                print("Invalid choice")
        except ValueError:
            print("Please enter a valid number")
        
    def _travel(self):
        print("\n=== TRAVEL ===")
        
        planets = self.state.universe.planets
        
        print("\nAvailable Destinations:")
        for i, planet in enumerate(planets, 1):
            if planet == self.state.current_planet:
                continue
                
            distance = self.state.current_planet.distance_to(planet)
            fuel_needed = self._calculate_fuel_needed(distance)
            
            print(f"{i}. {planet} - Distance: {distance:.1f} - Fuel: {fuel_needed}")
            
        print(f"{len(planets) + 1}. Back")
        
        try:
            choice = int(input("\nEnter your choice (1-{0}): ".format(len(planets) + 1)).strip())
            
            if choice == len(planets) + 1:
                return
                
            if 1 <= choice <= len(planets):
                destination = planets[choice - 1]
                
                if destination == self.state.current_planet:
                    print("You are already on this planet!")
                    return
                    
                distance = self.state.current_planet.distance_to(destination)
                fuel_needed = self._calculate_fuel_needed(distance)
                
                if self.state.player.ship.current_fuel < fuel_needed:
                    print(f"Not enough fuel! You need {fuel_needed} units but only have {self.state.player.ship.current_fuel}")
                    return
                    
                pirate_chance = self.event_effects.get("pirate_chance", 0)
                if random.random() < pirate_chance:
                    self._pirate_attack()
                
                self.state.player.ship.current_fuel -= fuel_needed
                self.state.current_planet = destination
                self.state.current_planet.refresh_market()
                self.state.day += 1
                
                print(f"Traveled to {destination}")
            else:
                print("Invalid choice")
        except ValueError:
            print("Please enter a valid number")
            
    def _pirate_attack(self):
        print("\n*** PIRATE ATTACK! ***")
        
        if not self.state.player.ship.cargo:
            print("The pirates found nothing to steal and left disappointed.")
            return
            
        cargo_items = list(self.state.player.ship.cargo.items())
        stolen_item_type, amount = random.choice(cargo_items)
        stolen_amount = max(1, amount // 3)
        
        self.state.player.ship.remove_cargo(stolen_item_type, stolen_amount)
        
        print(f"The pirates have stolen {stolen_amount} units of {stolen_item_type.value}!")
        time.sleep(2)
        
    def _refuel(self):
        print("\n=== REFUEL SHIP ===")
        
        missing_fuel = self.state.player.ship.fuel_capacity - self.state.player.ship.current_fuel
        
        if missing_fuel <= 0:
            print("Your fuel tank is already full!")
            return
            
        fuel_price = self._get_fuel_price()
        max_affordable = self.state.player.credits // fuel_price
        max_refuel = min(missing_fuel, max_affordable)
        
        print(f"Fuel price: {fuel_price} credits per unit")
        print(f"Missing fuel: {missing_fuel} units")
        print(f"Maximum affordable: {max_affordable} units")
        
        try:
            amount = int(input(f"How many units do you want to buy (0-{max_refuel})? "))
            
            if amount <= 0:
                print("Refueling cancelled")
                return
                
            if amount > max_refuel:
                print(f"You can only buy {max_refuel} units")
                return
                
            total_cost = amount * fuel_price
                
            if not self.state.player.pay(total_cost):
                print("You don't have enough credits!")
                return
                
            self.state.player.ship.current_fuel += amount
            print(f"Refueled {amount} units for {total_cost} credits")
        except ValueError:
            print("Please enter a valid number")
        
    def _take_loan(self):
        print("\n=== TAKE LOAN ===")
        
        if self.state.player.debt > 0:
            print(f"You already have an outstanding debt of {self.state.player.debt} credits")
            return
            
        print("Available loans:")
        print("1. Small Loan: 5,000 credits")
        print("2. Medium Loan: 10,000 credits")
        print("3. Large Loan: 20,000 credits")
        print("4. Back")
        
        try:
            choice = int(input("\nEnter your choice (1-4): ").strip())
            
            loan_amounts = {1: 5000, 2: 10000, 3: 20000}
            
            if choice == 4:
                return
                
            if choice in loan_amounts:
                loan_amount = loan_amounts[choice]
                interest = int(loan_amount * 0.2)
                total_debt = loan_amount + interest
                
                self.state.player.debt = total_debt
                self.state.player.receive(loan_amount)
                
                print(f"You took a loan of {loan_amount} credits")
                print(f"You need to repay {total_debt} credits (including {interest} interest)")
            else:
                print("Invalid choice")
        except ValueError:
            print("Please enter a valid number")
        
    def _repay_loan(self):
        print("\n=== REPAY LOAN ===")
        
        if self.state.player.debt <= 0:
            print("You don't have any debt to repay")
            return
            
        print(f"Current debt: {self.state.player.debt} credits")
        print(f"Available credits: {self.state.player.credits}")
        
        max_repay = min(self.state.player.debt, self.state.player.credits)
        
        try:
            amount = int(input(f"How much do you want to repay (0-{max_repay})? "))
            
            if amount <= 0:
                print("Repayment cancelled")
                return
                
            if amount > max_repay:
                print(f"You can only repay {max_repay} credits")
                return
                
            self.state.player.pay(amount)
            self.state.player.debt -= amount
            
            print(f"Repaid {amount} credits")
            
            if self.state.player.debt <= 0:
                print("Congratulations! You've paid off your debt")
        except ValueError:
            print("Please enter a valid number")
            
    def _special_missions(self):
        print("\n=== SPECIAL MISSIONS ===")
        
        if self.state.player.has_special_cargo:
            print("You already have a special cargo mission in progress!")
            return
            
        if self.state.day % 10 != 0:
            print(f"No special missions available today. Check back on day {(self.state.day // 10 + 1) * 10}")
            return
            
        available_planets = [p for p in self.state.universe.planets if p != self.state.current_planet]
        destination = random.choice(available_planets)
        
        reward = 2000 + (self.state.day * 50)
        
        print(f"Special delivery mission available:")
        print(f"Deliver diplomatic package to {destination}")
        print(f"Reward: {reward} credits")
        print("\nWarning: The package will take 10 cargo spaces")
        print("1. Accept mission")
        print("2. Decline mission")
        
        choice = input("\nEnter your choice (1-2): ").strip()
        
        if choice == "1":
            if self.state.player.ship.get_cargo_space_available() < 10:
                print("You don't have enough cargo space for this mission!")
                return
                
            self.state.player.has_special_cargo = True
            self.state.player.special_cargo_destination = destination
            self.state.player.special_cargo_reward = reward
            self.state.player.ship.add_cargo(ItemType.ELECTRONICS, 10)
            
            print("Mission accepted! Deliver the package to complete the mission")
        elif choice == "2":
            print("Mission declined")
        else:
            print("Invalid choice")
            
    def _check_special_mission(self):
        if self.state.player.has_special_cargo and self.state.current_planet == self.state.player.special_cargo_destination:
            print("\n*** SPECIAL MISSION COMPLETED! ***")
            
            self.state.player.ship.remove_cargo(ItemType.ELECTRONICS, 10)
            
            reward = self.state.player.special_cargo_reward
            self.state.player.receive(reward)
            
            print(f"You've earned {reward} credits for completing the delivery!")
            
            self.state.player.has_special_cargo = False
            self.state.player.special_cargo_destination = None
            self.state.player.special_cargo_reward = 0
            
            time.sleep(2)
            
    def _calculate_fuel_needed(self, distance: float) -> int:
        base_fuel = int(distance / self.state.player.ship.speed)
        travel_multiplier = self.event_effects.get("travel_cost_multiplier", 1.0)
        return max(1, int(base_fuel * travel_multiplier))
        
    def _get_fuel_price(self) -> int:
        base_price = 10
        multiplier = self.event_effects.get("fuel_cost_multiplier", 1.0)
        return max(1, int(base_price * multiplier))
        
    def _get_modified_buy_price(self, item_type: ItemType) -> int:
        base_price = self.state.current_planet.market.get_buy_price(item_type)
        price_multiplier = self.event_effects.get("price_multiplier", 1.0)
        buy_multiplier = self.event_effects.get("buy_price_multiplier", 1.0)
        
        return max(1, int(base_price * price_multiplier * buy_multiplier))
        
    def _get_modified_sell_price(self, item_type: ItemType) -> int:
        base_price = self.state.current_planet.market.get_sell_price(item_type)
        price_multiplier = self.event_effects.get("price_multiplier", 1.0)
        sell_multiplier = self.event_effects.get("sell_price_multiplier", 1.0)
        
        return max(1, int(base_price * price_multiplier * sell_multiplier))
        
    def _end_game(self):
        self.state.game_over = True
    
    def _display_game_over(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        game_over_text = """
        ▄▄ ▄▄ ▄▄ ▄▄ ▄▄ ▄▄ ▄▄ ▄▄ ▄▄ ▄▄ ▄▄
         GAME OVER - FINAL RESULTS
        ▀▀ ▀▀ ▀▀ ▀▀ ▀▀ ▀▀ ▀▀ ▀▀ ▀▀ ▀▀ ▀▀
        """
        print(Fore.YELLOW + game_over_text + Style.RESET_ALL)
        
        net_worth = self.state.player.credits
        
        for item_type, amount in self.state.player.ship.cargo.items():
            net_worth += amount * self.state.current_planet.market.get_sell_price(item_type)
        
        net_worth -= self.state.player.debt
        
        print_info("Days played", f"{self.state.day}/{self.state.max_days}")
        print_info("Final credits", f"{self.state.player.credits:,}", Fore.YELLOW)
        
        if self.state.player.ship.cargo:
            print("\n" + Fore.CYAN + "=== Final Cargo ===" + Style.RESET_ALL)
            for item_type, amount in self.state.player.ship.cargo.items():
                sell_price = self.state.current_planet.market.get_sell_price(item_type)
                value = amount * sell_price
                print_info(f"  {item_type.value}", f"{amount} units (worth {value:,} credits)")
        
        if self.state.player.debt > 0:
            print_info("\nOutstanding debt", f"{self.state.player.debt:,} credits", Fore.RED)
        
        print_info("\nFinal net worth", f"{net_worth:,} credits", Fore.GREEN)
        
        if net_worth >= 50000:
            rank_color = Fore.YELLOW
            rank = "🌟 Galactic Trade Magnate"
        elif net_worth >= 30000:
            rank_color = Fore.GREEN
            rank = "💫 Respected Merchant"
        elif net_worth >= 15000:
            rank_color = Fore.CYAN
            rank = "⭐ Established Trader"
        elif net_worth >= 5000:
            rank_color = Fore.BLUE
            rank = "🚀 Skilled Hauler"
        elif net_worth >= 0:
            rank_color = Fore.WHITE
            rank = "🛸 Novice Trader"
        else:
            rank_color = Fore.RED
            rank = "💀 Indebted Space Vagrant"
        
        print_info("\nFinal rank", rank, rank_color)
        print("\n" + Fore.YELLOW + "Thanks for playing Space Trader!" + Style.RESET_ALL)
        
        input(f"\n{Fore.CYAN}Press Enter to exit...{Style.RESET_ALL}")

def init_ui():
    init(autoreset=True)
    
def get_terminal_width():
    width, _ = shutil.get_terminal_size()
    return width

def print_header(text, char="="):
    width = get_terminal_width()
    print(Fore.CYAN + char * width)
    print(Fore.YELLOW + text.center(width))
    print(Fore.CYAN + char * width)

def print_menu_option(number, text, color=Fore.WHITE):
    print(f"{Fore.CYAN}[{number}]{Style.RESET_ALL} {color}{text}")

def print_info(label, value, color=Fore.WHITE):
    print(f"{Fore.CYAN}{label}:{Style.RESET_ALL} {color}{value}")

def print_warning(text):
    print(f"{Fore.YELLOW}⚠ {text}")

def print_success(text):
    print(f"{Fore.GREEN}✓ {text}")

def print_error(text):
    print(f"{Fore.RED}✗ {text}")

def draw_ship_ascii():
    ship = f"""
{Fore.CYAN}    /\\
   /  \\
  /    \\
 /      \\
/________\\{Style.RESET_ALL}
    """
    print(ship)

if __name__ == "__main__":
    init_ui()
    
    title_art = """
 _____                      _____           _           
/  ___|                    |_   _|         | |          
\ `--.  _ __   __ _  ___ ___ | |_ __ __ _| | ___ _ __ 
 `--. \| '_ \ / _` |/ __/ _ \| | '__/ _` | |/ _ \ '__|
/\__/ /| |_) | (_| | (_|  __/| | | | (_| | |  __/ |   
\____/ | .__/ \__,_|\___\___\\_\_/  \__,_|_|\___|_|   
       | |                                            
       |_|                                            
"""
    print(Fore.CYAN + title_art + Style.RESET_ALL)
    
    print_menu_option("1", "New Game", Fore.GREEN)
    print_menu_option("2", "Load Game", Fore.YELLOW)
    print_menu_option("3", "Exit", Fore.RED)
    
    choice = input(f"\n{Fore.CYAN}Enter your choice (1-3):{Style.RESET_ALL} ").strip()
    
    game = Game()
    
    if choice == "1":
        game.new_game()
    elif choice == "2":
        filename = input(f"{Fore.CYAN}Enter save file name:{Style.RESET_ALL} ").strip()
        if game.load_game(filename):
            print_success(f"Game loaded from {filename}")
            game._main_loop()
        else:
            print_error("Failed to load game")
    elif choice == "3":
        print(Fore.YELLOW + "\nGoodbye!" + Style.RESET_ALL)
    else:
        print_error("Invalid choice")
