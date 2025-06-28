"""
Time Drift
A CLI-based sci-fi temporal puzzle adventure where you play as a chrono-drifter
stuck in a 7-day time loop. Every decision ripples through time.
Break the loop, or doom every timeline.
"""
import os
import sys
import time
import random
import json
import pickle
from datetime import datetime
from collections import defaultdict
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
MAX_DAYS = 7
LOCATIONS = [
    "Research Lab",
    "Temporal Engine Room",
    "Residential Quarters",
    "Command Center",
    "Maintenance Bay",
    "Observation Deck",
    "Quantum Archives"
]
TIME_PERIODS = ["Morning", "Afternoon", "Evening", "Night"]
class GameState:
    def __init__(self):
        self.current_loop = 1
        self.current_day = 1
        self.current_time = 0  
        self.current_location = "Research Lab"
        self.inventory = []
        self.knowledge = set()  
        self.timeline_changes = []  
        self.character_states = {}  
        self.temporal_anomalies = {}  
        self.persistent_objects = {}  
        self.visited_locations = set()  
        self.loop_memories = defaultdict(list)  
        self.causality_violations = 0  
        self.stability_factor = 100  
        self.time_fragments = 0  
        self.objectives_completed = set()  
        self.active_objectives = set()  
        self.timeline_branches = {}  
        self.current_branch = "alpha"  
        self.temporal_echoes = {  
            "Research Lab": [
                {"type": "past", "day": 1, "time_period": "Morning", "discovered": False, 
                 "description": "You see yourself entering the lab for the first time, unaware of the time loop that awaits."},
                {"type": "future", "day": 5, "time_period": "Evening", "discovered": False, 
                 "description": "Dr. Nova frantically working on calculations, muttering about 'timeline collapse'"}
            ],
            "Command Center": [
                {"type": "future", "day": 3, "time_period": "Night", "discovered": False, 
                 "description": "A glimpse of the Command Center in ruins, timelines collapsing as the loop destabilizes."}
            ],
            "Temporal Engine Room": [
                {"type": "past", "day": 1, "time_period": "Afternoon", "discovered": False, 
                 "description": "Engineer Pulse making a critical adjustment to the engine that may have caused the loop."},
                {"type": "future", "day": 2, "time_period": "Evening", "discovered": False, 
                 "description": "The engine core pulsing with an otherworldly energy, moments before a catastrophic failure."}
            ],
            "Quantum Archives": [
                {"type": "past", "day": 1, "time_period": "Evening", "discovered": False, 
                 "description": "Archivist Echo hiding a strange device in a secret compartment behind the main console."}
            ],
            "Observation Deck": [
                {"type": "future", "day": 3, "time_period": "Morning", "discovered": False, 
                 "description": "The stars outside shifting in impossible patterns as reality begins to fracture."}
            ],
            "Maintenance Bay": [
                {"type": "past", "day": 2, "time_period": "Afternoon", "discovered": False, 
                 "description": "A maintenance worker accidentally dropping a strange crystal that briefly distorts the space around it."}
            ],
            "Residential Quarters": [
                {"type": "future", "day": 4, "time_period": "Night", "discovered": False, 
                 "description": "Your quarters in disarray, walls covered with timeline calculations and warnings written in your own handwriting."}
            ]
        }  
        self.paradox_points = 0  
        self.time_rifts = {}  
        self.quantum_states = {}  
        self.temporal_skills = {  
            "echo_vision": False,
            "paradox_manipulation": False,
            "quantum_entanglement": False,
            "temporal_projection": False,
            "rift_creation": False
        }
        self.parallel_selves = []  
    def advance_time(self):
        """Advance time by one period"""
        self.current_time += 1
        if self.current_time >= len(TIME_PERIODS):
            self.current_time = 0
            self.current_day += 1
            if self.current_day > MAX_DAYS:
                self.reset_loop()
                return True  
        return False  
    def reset_loop(self):
        """Reset the time loop but maintain player knowledge"""
        self.loop_memories[self.current_loop] = {
            "visited": list(self.visited_locations),
            "knowledge": list(self.knowledge),
            "timeline_changes": self.timeline_changes.copy(),
            "inventory": self.inventory.copy()
        }
        self.current_loop += 1
        self.current_day = 1
        self.current_time = 0
        self.current_location = "Research Lab"
        self.visited_locations = set()
        self.inventory = [item for item in self.inventory if item in self.persistent_objects]
        self.timeline_changes = []
        for character in self.character_states:
            if "base_pattern" in self.character_states[character]:
                self.character_states[character]["current"] = self.character_states[character]["base_pattern"].copy()
    def add_knowledge(self, info):
        """Add new knowledge that persists across loops"""
        self.knowledge.add(info)
    def add_timeline_change(self, change, causality_impact=1):
        """Record a change to the timeline with its causality impact"""
        self.timeline_changes.append({
            "day": self.current_day,
            "time": TIME_PERIODS[self.current_time],
            "location": self.current_location,
            "change": change,
            "impact": causality_impact
        })
        self.stability_factor -= causality_impact
        if causality_impact > 0:
            self.causality_violations += 1
    def create_temporal_anomaly(self, location, description):
        """Create a temporal anomaly at a location"""
        if location not in self.temporal_anomalies:
            self.temporal_anomalies[location] = []
        self.temporal_anomalies[location].append({
            "created_loop": self.current_loop,
            "created_day": self.current_day,
            "description": description,
            "resolved": False
        })
    def make_object_persistent(self, item):
        """Make an object persist across time loops"""
        self.persistent_objects[item] = {
            "origin_loop": self.current_loop,
            "origin_day": self.current_day,
            "description": f"A {item} that seems to exist outside normal temporal flow"
        }
    def discover_echo(self, location):
        """Discover a temporal echo at the current location"""
        if location in self.temporal_echoes:
            for echo in self.temporal_echoes[location]:
                if not echo["discovered"]:
                    echo["discovered"] = True
                    self.paradox_points += 2
                    return echo
        return None
    def add_temporal_echo(self, location, echo_type, day, time_period, description):
        """Add a new temporal echo to a location"""
        if location not in self.temporal_echoes:
            self.temporal_echoes[location] = []
        self.temporal_echoes[location].append({
            "type": echo_type,  
            "day": day,
            "time_period": time_period,
            "discovered": False,
            "description": description
        })
    def create_time_rift(self, origin, destination):
        """Create a time rift between two locations"""
        if not self.temporal_skills["rift_creation"]:
            return False, "You haven't unlocked the rift creation skill yet."
        if self.paradox_points < 5:
            return False, "Not enough paradox points. Requires 5 points."
        rift_id = f"rift_{len(self.time_rifts) + 1}"
        self.time_rifts[rift_id] = {
            "origin": origin,
            "destination": destination,
            "stability": 3,  
            "created_loop": self.current_loop,
            "created_day": self.current_day
        }
        self.paradox_points -= 5
        return True, f"Created time rift from {origin} to {destination}."
    def use_time_rift(self, rift_id):
        """Use a time rift to travel between locations"""
        if rift_id not in self.time_rifts:
            return False, "That time rift doesn't exist."
        rift = self.time_rifts[rift_id]
        if rift["origin"] != self.current_location:
            return False, f"You must be at {rift['origin']} to use this rift."
        if rift["stability"] <= 0:
            return False, "This rift has collapsed and can no longer be used."
        self.current_location = rift["destination"]
        rift["stability"] -= 1
        if rift["stability"] <= 0:
            return True, f"You travel through the rift to {rift['destination']}. The rift collapses behind you."
        return True, f"You travel through the rift to {rift['destination']}. The rift flickers, weakening with use."
    def set_quantum_state(self, object_name, state):
        """Set the quantum state of an object"""
        if not self.temporal_skills["quantum_entanglement"]:
            return False, "You haven't unlocked the quantum entanglement skill yet."
        if self.paradox_points < 3:
            return False, "Not enough paradox points. Requires 3 points."
        self.quantum_states[object_name] = {
            "state": state,
            "set_loop": self.current_loop,
            "set_day": self.current_day,
            "location": self.current_location
        }
        self.paradox_points -= 3
        return True, f"Set {object_name} to quantum state: {state}."
    def unlock_temporal_skill(self, skill):
        """Unlock a new temporal skill"""
        if skill not in self.temporal_skills:
            return False, "That skill doesn't exist."
        if self.temporal_skills[skill]:
            return False, "You've already unlocked this skill."
        skill_costs = {
            "echo_vision": 5,
            "paradox_manipulation": 10,
            "quantum_entanglement": 15,
            "temporal_projection": 20,
            "rift_creation": 25
        }
        if self.paradox_points < skill_costs[skill]:
            return False, f"Not enough paradox points. Requires {skill_costs[skill]} points."
        self.temporal_skills[skill] = True
        self.paradox_points -= skill_costs[skill]
        return True, f"Unlocked the {skill} skill!"
    def create_parallel_self(self, name, specialty):
        """Create a parallel version of yourself"""
        if not self.temporal_skills["temporal_projection"]:
            return False, "You haven't unlocked the temporal projection skill yet."
        if self.paradox_points < 10:
            return False, "Not enough paradox points. Requires 10 points."
        specialties = {
            "engineer": "Can repair temporal anomalies and access restricted areas",
            "scientist": "Can analyze quantum states and decode complex information",
            "explorer": "Can find hidden objects and discover temporal echoes more easily",
            "guardian": "Can protect against timeline destabilization and reduce causality violations"
        }
        if specialty not in specialties:
            return False, f"Invalid specialty. Choose from: {', '.join(specialties.keys())}"
        self.parallel_selves.append({
            "name": name,
            "specialty": specialty,
            "description": specialties[specialty],
            "created_loop": self.current_loop,
            "created_day": self.current_day,
            "uses_remaining": 3
        })
        self.paradox_points -= 10
        return True, f"Created parallel self '{name}' with {specialty} specialty."
    def create_timeline_branch(self, branch_name, branch_point):
        """Create a new timeline branch"""
        self.timeline_branches[branch_name] = {
            "created_loop": self.current_loop,
            "branch_point": branch_point,
            "parent_branch": self.current_branch,
            "changes": []
        }
    def switch_timeline_branch(self, branch_name):
        """Switch to a different timeline branch"""
        if branch_name in self.timeline_branches:
            self.current_branch = branch_name
            return True
        return False
    def add_temporal_echo(self, location, day, time_period, description, echo_type="past"):
        """Add a temporal echo (glimpse of past or future) to a location"""
        if location not in self.temporal_echoes:
            self.temporal_echoes[location] = []
        self.temporal_echoes[location].append({
            "day": day,
            "time_period": time_period,
            "description": description,
            "type": echo_type,  
            "discovered": False
        })
    def discover_echo(self, location, echo_index):
        """Mark a temporal echo as discovered and gain paradox points"""
        if location in self.temporal_echoes and 0 <= echo_index < len(self.temporal_echoes[location]):
            if not self.temporal_echoes[location][echo_index]["discovered"]:
                self.temporal_echoes[location][echo_index]["discovered"] = True
                self.paradox_points += 2
                return True
        return False
    def create_time_rift(self, source_location, target_location, stability_cost=5):
        """Create a time rift between two locations for fast travel"""
        if self.temporal_skills["rift_creation"] and self.paradox_points >= 3:
            rift_id = f"{source_location}-{target_location}"
            self.time_rifts[rift_id] = {
                "source": source_location,
                "target": target_location,
                "stability": 100,  
                "created_loop": self.current_loop,
                "created_day": self.current_day
            }
            self.paradox_points -= 3
            self.stability_factor -= stability_cost
            return True
        return False
    def use_time_rift(self, rift_id):
        """Use a time rift to travel instantly between locations"""
        if rift_id in self.time_rifts and self.time_rifts[rift_id]["stability"] > 0:
            if self.current_location == self.time_rifts[rift_id]["source"]:
                self.current_location = self.time_rifts[rift_id]["target"]
                self.time_rifts[rift_id]["stability"] -= 10  
                return True
        return False
    def set_quantum_state(self, object_name, state_value):
        """Set the quantum state of an object or location"""
        if self.temporal_skills["quantum_entanglement"]:
            self.quantum_states[object_name] = state_value
            return True
        return False
    def unlock_temporal_skill(self, skill_name, paradox_cost=5):
        """Unlock a new temporal skill using paradox points"""
        if skill_name in self.temporal_skills and not self.temporal_skills[skill_name]:
            if self.paradox_points >= paradox_cost:
                self.temporal_skills[skill_name] = True
                self.paradox_points -= paradox_cost
                return True
        return False
    def create_parallel_self(self, description, special_ability):
        """Create a parallel version of yourself that can assist you"""
        if self.temporal_skills["temporal_projection"] and self.paradox_points >= 7:
            self.parallel_selves.append({
                "created_loop": self.current_loop,
                "created_day": self.current_day,
                "description": description,
                "ability": special_ability,
                "stability": 3  
            })
            self.paradox_points -= 7
            self.stability_factor -= 10  
            return True
        return False
class Event:
    def __init__(self, id, title, description, location, day, time_period, 
                 requirements=None, choices=None, consequences=None, 
                 knowledge_reward=None, repeatable=False):
        self.id = id
        self.title = title
        self.description = description
        self.location = location
        self.day = day
        self.time_period = time_period
        self.requirements = requirements or {}
        self.choices = choices or []
        self.consequences = consequences or {}
        self.knowledge_reward = knowledge_reward
        self.repeatable = repeatable
        self.triggered = False
    def is_available(self, game_state):
        """Check if this event is available based on requirements"""
        if not self.repeatable and self.triggered:
            return False
        if game_state.current_day != self.day or \
           TIME_PERIODS[game_state.current_time] != self.time_period or \
           game_state.current_location != self.location:
            return False
        if "knowledge" in self.requirements:
            for k in self.requirements["knowledge"]:
                if k not in game_state.knowledge:
                    return False
        if "inventory" in self.requirements:
            for item in self.requirements["inventory"]:
                if item not in game_state.inventory:
                    return False
        if "timeline_changes" in self.requirements:
            changes_met = False
            for change in game_state.timeline_changes:
                if change["change"] in self.requirements["timeline_changes"]:
                    changes_met = True
                    break
            if not changes_met:
                return False
        return True
    def trigger(self, game_state):
        """Trigger this event"""
        self.triggered = True
        if self.knowledge_reward:
            game_state.add_knowledge(self.knowledge_reward)
    def get_choices(self):
        """Get available choices for this event"""
        return self.choices
    def process_choice(self, choice_id, game_state):
        """Process a player's choice"""
        if choice_id not in self.consequences:
            return "That choice is not available."
        consequence = self.consequences[choice_id]
        if "add_items" in consequence:
            for item in consequence["add_items"]:
                game_state.inventory.append(item)
        if "remove_items" in consequence:
            for item in consequence["remove_items"]:
                if item in game_state.inventory:
                    game_state.inventory.remove(item)
        if "knowledge" in consequence:
            for k in consequence["knowledge"]:
                game_state.add_knowledge(k)
        if "timeline_change" in consequence:
            impact = consequence.get("causality_impact", 1)
            game_state.add_timeline_change(consequence["timeline_change"], impact)
        if "anomaly" in consequence:
            game_state.create_temporal_anomaly(
                game_state.current_location,
                consequence["anomaly"]
            )
        if "make_persistent" in consequence:
            for item in consequence["make_persistent"]:
                if item in game_state.inventory:
                    game_state.make_object_persistent(item)
        if "create_branch" in consequence:
            branch_info = consequence["create_branch"]
            game_state.create_timeline_branch(
                branch_info["name"],
                f"Day {game_state.current_day}, {TIME_PERIODS[game_state.current_time]}"
            )
        return consequence.get("text", "You made a choice.")
class Character:
    def __init__(self, id, name, description, base_location, schedule=None):
        self.id = id
        self.name = name
        self.description = description
        self.base_location = base_location
        self.schedule = schedule or {}  
        self.knowledge = {}  
        self.inventory = []  
        self.relationships = {}  
        self.state = "neutral"  
    def get_location(self, day, time_period):
        """Get character's location at a specific time"""
        if str(day) in self.schedule and time_period in self.schedule[str(day)]:
            return self.schedule[str(day)][time_period]
        return self.base_location
    def update_schedule(self, day, time_period, new_location):
        """Update character's schedule"""
        if str(day) not in self.schedule:
            self.schedule[str(day)] = {}
        self.schedule[str(day)][time_period] = new_location
class Location:
    def __init__(self, name, description, connections=None, objects=None):
        self.name = name
        self.description = description
        self.connections = connections or []  
        self.objects = objects or {}  
        self.anomalies = []  
    def add_anomaly(self, anomaly):
        """Add a temporal anomaly to this location"""
        self.anomalies.append(anomaly)
    def remove_anomaly(self, anomaly_index):
        """Remove a temporal anomaly from this location"""
        if 0 <= anomaly_index < len(self.anomalies):
            del self.anomalies[anomaly_index]
            return True
        return False
class TimelineVisualizer:
    @staticmethod
    def generate_timeline_diagram(game_state):
        """Generate a text-based diagram of the current timeline"""
        diagram = []
        diagram.append(f"{Colors.BOLD}{Colors.CYAN}TIMELINE: LOOP {game_state.current_loop} - BRANCH {game_state.current_branch.upper()}{Colors.RESET}")
        diagram.append("")
        stability = game_state.stability_factor
        meter = "[" + "#" * (stability // 10) + "-" * (10 - stability // 10) + "]"
        stability_color = Colors.GREEN if stability > 70 else Colors.YELLOW if stability > 40 else Colors.RED
        diagram.append(f"Timeline Stability: {stability_color}{meter} {stability}%{Colors.RESET}")
        diagram.append("")
        for day in range(1, MAX_DAYS + 1):
            day_header = f"{Colors.BOLD}DAY {day}{Colors.RESET}"
            if day < game_state.current_day:
                day_header += f" {Colors.DIM}(Past){Colors.RESET}"
            elif day == game_state.current_day:
                day_header += f" {Colors.BRIGHT_GREEN}(Current){Colors.RESET}"
            else:
                day_header += f" {Colors.DIM}(Future){Colors.RESET}"
            diagram.append(day_header)
            day_changes = [c for c in game_state.timeline_changes if c["day"] == day]
            if day_changes:
                for change in day_changes:
                    impact_color = Colors.GREEN if change["impact"] < 2 else Colors.YELLOW if change["impact"] < 4 else Colors.RED
                    diagram.append(f"  {change['time']} @ {change['location']}: {impact_color}{change['change']}{Colors.RESET}")
            else:
                diagram.append(f"  {Colors.DIM}No recorded changes{Colors.RESET}")
            diagram.append("")
        if game_state.timeline_branches:
            diagram.append(f"{Colors.BOLD}{Colors.MAGENTA}TIMELINE BRANCHES:{Colors.RESET}")
            for branch, data in game_state.timeline_branches.items():
                current_marker = "*" if branch == game_state.current_branch else ""
                diagram.append(f"  {current_marker}{branch.upper()}: Branched from {data['parent_branch'].upper()} at {data['branch_point']}")
        return "\n".join(diagram)
    @staticmethod
    def generate_causality_web(game_state):
        """Generate a visualization of cause-effect relationships"""
        web = []
        web.append(f"{Colors.BOLD}{Colors.CYAN}CAUSALITY WEB{Colors.RESET}")
        web.append("")
        low_impact = []
        medium_impact = []
        high_impact = []
        for change in game_state.timeline_changes:
            if change["impact"] < 2:
                low_impact.append(change)
            elif change["impact"] < 4:
                medium_impact.append(change)
            else:
                high_impact.append(change)
        if high_impact:
            web.append(f"{Colors.BOLD}{Colors.RED}CRITICAL CAUSALITY VIOLATIONS:{Colors.RESET}")
            for change in high_impact:
                web.append(f"  Day {change['day']} {change['time']} @ {change['location']}: {change['change']}")
            web.append("")
        if medium_impact:
            web.append(f"{Colors.BOLD}{Colors.YELLOW}SIGNIFICANT TIMELINE ALTERATIONS:{Colors.RESET}")
            for change in medium_impact:
                web.append(f"  Day {change['day']} {change['time']} @ {change['location']}: {change['change']}")
            web.append("")
        if low_impact:
            web.append(f"{Colors.BOLD}{Colors.GREEN}MINOR TIMELINE ADJUSTMENTS:{Colors.RESET}")
            for change in low_impact:
                web.append(f"  Day {change['day']} {change['time']} @ {change['location']}: {change['change']}")
        return "\n".join(web)
class GameEngine:
    def __init__(self):
        self.state = GameState()
        self.events = {}
        self.characters = {}
        self.locations = {}
        self.save_file = "timedrift_save.pkl"
    def initialize_game(self):
        """Initialize the game world"""
        for loc_name in LOCATIONS:
            connections = [l for l in LOCATIONS if l != loc_name]  
            self.locations[loc_name] = Location(loc_name, f"The {loc_name.lower()}", connections)
        self.characters["dr_nova"] = Character(
            "dr_nova", "Dr. Nova", "The lead scientist of the temporal research project",
            "Research Lab",
            {"1": {"Morning": "Research Lab", "Afternoon": "Command Center", "Evening": "Residential Quarters", "Night": "Residential Quarters"},
             "2": {"Morning": "Research Lab", "Afternoon": "Research Lab", "Evening": "Observation Deck", "Night": "Residential Quarters"}}
        )
        self.characters["engineer_pulse"] = Character(
            "engineer_pulse", "Engineer Pulse", "The chief engineer responsible for the temporal engine",
            "Temporal Engine Room",
            {"1": {"Morning": "Temporal Engine Room", "Afternoon": "Maintenance Bay", "Evening": "Command Center", "Night": "Residential Quarters"},
             "2": {"Morning": "Maintenance Bay", "Afternoon": "Temporal Engine Room", "Evening": "Temporal Engine Room", "Night": "Residential Quarters"}}
        )
        self.characters["archivist_echo"] = Character(
            "archivist_echo", "Archivist Echo", "The keeper of the quantum archives and temporal records",
            "Quantum Archives",
            {"1": {"Morning": "Quantum Archives", "Afternoon": "Quantum Archives", "Evening": "Observation Deck", "Night": "Residential Quarters"},
             "2": {"Morning": "Command Center", "Afternoon": "Quantum Archives", "Evening": "Quantum Archives", "Night": "Residential Quarters"}}
        )
        self.events["intro"] = Event(
            "intro",
            "Temporal Displacement",
            "You wake up disoriented in the Research Lab. The last thing you remember is a blinding flash from the temporal engine. Something has gone terribly wrong with the experiment.",
            "Research Lab", 1, "Morning",
            choices=[
                "Examine the lab equipment",
                "Check your personal log",
                "Look for other researchers"
            ],
            consequences={
                0: {"text": "The equipment shows signs of a massive temporal surge. According to the readings, the date is exactly the same as when the experiment started.", 
                    "knowledge": ["temporal surge occurred"]},
                1: {"text": "Your log indicates today is the day of the critical temporal experiment. But you distinctly remember completing it already.", 
                    "knowledge": ["experiencing time loop"]},
                2: {"text": "The lab is empty. Through the window, you can see people going about their routines exactly as they did on the day of the experiment.", 
                    "knowledge": ["alone in time loop"]}
            }
        )
        self.events["engine_malfunction"] = Event(
            "engine_malfunction",
            "Temporal Engine Malfunction",
            "The temporal engine is emitting an unusual quantum signature. Engineer Pulse is frantically trying to stabilize it.",
            "Temporal Engine Room", 1, "Afternoon",
            requirements={"knowledge": ["temporal surge occurred"]},
            choices=[
                "Offer to help Engineer Pulse",
                "Secretly sabotage the stabilization effort",
                "Observe carefully to understand the malfunction"
            ],
            consequences={
                0: {"text": "Engineer Pulse appreciates your help. Together, you manage to reduce the quantum fluctuations, but the engine is still unstable.", 
                    "knowledge": ["engine can be stabilized"], 
                    "timeline_change": "Helped stabilize the temporal engine", 
                    "causality_impact": 1},
                1: {"text": "You subtly alter the calibration settings. The engine's instability increases dramatically, creating a small temporal anomaly in the room.", 
                    "knowledge": ["engine sabotage possible"], 
                    "timeline_change": "Sabotaged the temporal engine", 
                    "causality_impact": 3, 
                    "anomaly": "A shimmering area where time seems to flow backwards"},
                2: {"text": "You notice that the engine's quantum matrix is misaligned. This information might be useful in understanding how to break the time loop.", 
                    "knowledge": ["quantum matrix misalignment"]}
            }
        )
        self.events["archive_discovery"] = Event(
            "archive_discovery",
            "Secrets in the Archives",
            "The Quantum Archives contain records of all temporal experiments. Perhaps there's information here about your situation.",
            "Quantum Archives", 1, "Evening",
            choices=[
                "Search for records of similar temporal incidents",
                "Look for information about the experiment's lead scientist",
                "Investigate classified temporal protocols"
            ],
            consequences={
                0: {"text": "You find records of a theoretical phenomenon called 'Temporal Recursion Loop.' The symptoms match what you're experiencing.", 
                    "knowledge": ["temporal recursion loop theory"]},
                1: {"text": "Dr. Nova's file contains concerning information. They've been conducting unauthorized temporal experiments for months.", 
                    "knowledge": ["dr nova unauthorized experiments"]},
                2: {"text": "You discover Protocol Omega - a classified procedure for resetting the timeline in case of catastrophic temporal fractures. It requires a special key.", 
                    "knowledge": ["protocol omega exists"], 
                    "add_items": ["protocol omega document"]}
            }
        )
    def save_game(self):
        """Save the current game state"""
        with open(self.save_file, 'wb') as f:
            pickle.dump({
                'state': self.state,
                'events': self.events,
                'characters': self.characters,
                'locations': self.locations
            }, f)
        return "Game saved successfully."
    def load_game(self):
        """Load a saved game"""
        try:
            with open(self.save_file, 'rb') as f:
                data = pickle.load(f)
                self.state = data['state']
                self.events = data['events']
                self.characters = data['characters']
                self.locations = data['locations']
            return "Game loaded successfully."
        except FileNotFoundError:
            return "No saved game found."
        except Exception as e:
            return f"Error loading game: {str(e)}"
    def get_available_events(self):
        """Get events available at the current time and location"""
        available = []
        for event_id, event in self.events.items():
            if event.is_available(self.state):
                available.append(event)
        return available
    def get_characters_at_location(self):
        """Get characters at the current location"""
        present = []
        for char_id, character in self.characters.items():
            location = character.get_location(self.state.current_day, TIME_PERIODS[self.state.current_time])
            if location == self.state.current_location:
                present.append(character)
        return present
    def process_command(self, command):
        """Process a player command"""
        cmd_parts = command.lower().split()
        if not cmd_parts:
            return "Please enter a command."
        cmd = cmd_parts[0]
        args = cmd_parts[1:]
        if cmd in ["go", "move", "travel"]:
            if not args:
                return "Go where? Available locations: " + ", ".join(self.locations[self.state.current_location].connections)
            destination = " ".join(args)
            matched_location = None
            for loc in self.locations[self.state.current_location].connections:
                if loc.lower().startswith(destination):
                    matched_location = loc
                    break
            if matched_location:
                self.state.current_location = matched_location
                self.state.visited_locations.add(matched_location)
                return self.describe_current_location()
            else:
                return f"You can't go to {destination} from here. Available locations: " + ", ".join(self.locations[self.state.current_location].connections)
        elif cmd in ["wait", "advance", "time"]:
            loop_reset = self.state.advance_time()
            if loop_reset:
                return f"{Colors.BOLD}{Colors.CYAN}The time loop has reset. You find yourself back at the beginning of Day 1.{Colors.RESET}\n" + self.describe_current_location()
            else:
                return f"Time advances to {TIME_PERIODS[self.state.current_time]}.\n" + self.describe_current_location()
        elif cmd in ["inventory", "items", "i"]:
            if not self.state.inventory:
                return "Your inventory is empty."
            return "Inventory: " + ", ".join(self.state.inventory)
        elif cmd in ["knowledge", "know", "k"]:
            if not self.state.knowledge:
                return "You haven't learned anything significant yet."
            return "Knowledge:\n" + "\n".join([f"- {k}" for k in self.state.knowledge])
        elif cmd in ["examine", "look", "x"]:
            if not args:
                return self.describe_current_location()
            target = " ".join(args)
            for character in self.get_characters_at_location():
                if character.name.lower().startswith(target.lower()):
                    return f"{Colors.BOLD}{character.name}{Colors.RESET}: {character.description}"
            for obj_name, obj_desc in self.locations[self.state.current_location].objects.items():
                if obj_name.lower().startswith(target.lower()):
                    return f"{obj_name}: {obj_desc}"
            return f"You don't see {target} here."
        elif cmd in ["talk", "speak", "ask"]:
            if not args:
                return "Talk to whom? Available characters: " + ", ".join([c.name for c in self.get_characters_at_location()])
            target = " ".join(args)
            for character in self.get_characters_at_location():
                if character.name.lower().startswith(target.lower()):
                    return f"You speak with {character.name}. They seem to have no memory of previous time loops."
            return f"There's no one named {target} here."
        elif cmd in ["interact", "event", "e"]:
            available_events = self.get_available_events()
            if not available_events:
                return "There are no special events available here at this time."
            if not args or not args[0].isdigit():
                event_list = "Available events:\n"
                for i, event in enumerate(available_events):
                    event_list += f"{i+1}. {event.title}\n"
                event_list += "\nUse 'event <number>' to interact with an event."
                return event_list
            event_index = int(args[0]) - 1
            if 0 <= event_index < len(available_events):
                event = available_events[event_index]
                event.trigger(self.state)
                choices_text = "\n".join([f"{i+1}. {choice}" for i, choice in enumerate(event.get_choices())])
                return f"{Colors.BOLD}{event.title}{Colors.RESET}\n\n{event.description}\n\nChoices:\n{choices_text}\n\nUse 'choose <number>' to make a choice."
            else:
                return "Invalid event number."
        elif cmd in ["choose", "select", "c"]:
            available_events = self.get_available_events()
            triggered_events = [e for e in available_events if e.triggered]
            if not triggered_events:
                return "There is no active event to make choices for."
            if not args or not args[0].isdigit():
                return "Choose which option? Use 'choose <number>'."
            choice_index = int(args[0]) - 1
            event = triggered_events[0]  
            if 0 <= choice_index < len(event.get_choices()):
                result = event.process_choice(choice_index, self.state)
                return f"{result}\n\n{self.describe_current_location()}"
            else:
                return "Invalid choice number."
        elif cmd in ["timeline", "tl"]:
            return TimelineVisualizer.generate_timeline_diagram(self.state)
        elif cmd in ["causality", "web", "cw"]:
            return TimelineVisualizer.generate_causality_web(self.state)
        elif cmd in ["memories", "loops", "mem"]:
            if not self.state.loop_memories:
                return "You have no memories from previous loops yet."
            memory_text = f"{Colors.BOLD}{Colors.CYAN}MEMORIES FROM PREVIOUS LOOPS{Colors.RESET}\n\n"
            for loop_num, memories in self.state.loop_memories.items():
                memory_text += f"{Colors.BOLD}Loop {loop_num}:{Colors.RESET}\n"
                memory_text += f"Visited: {', '.join(memories['visited'])}\n"
                memory_text += f"Learned: {', '.join(memories['knowledge'])}\n"
                memory_text += f"Changes: {len(memories['timeline_changes'])} timeline alterations\n\n"
            return memory_text
        elif cmd == "save":
            return self.save_game()
        elif cmd == "load":
            return self.load_game()
        elif cmd in ["help", "?"]:
            return self.show_help()
        elif cmd in ["quit", "exit"]:
            return "QUIT"
        elif cmd == "rewind":
            if self.state.time_fragments < 3:
                return "You need at least 3 time fragments to rewind time."
            self.state.time_fragments -= 3
            self.state.current_time = max(0, self.state.current_time - 1)
            return f"You focus your temporal energy and rewind time to {TIME_PERIODS[self.state.current_time]}.\n" + self.describe_current_location()
        elif cmd == "glimpse":
            if self.state.time_fragments < 2:
                return "You need at least 2 time fragments to glimpse the future."
            self.state.time_fragments -= 2
            return "You focus your temporal energy and catch glimpses of possible futures. The images are unclear, but you sense important events will occur at the Command Center tomorrow."
        elif cmd in ["echoes", "echo"]:
            location = self.state.current_location
            if location not in self.state.temporal_echoes or not self.state.temporal_echoes[location]:
                return f"There are no temporal echoes detected at {location}."
            if not args:
                echo_list = f"{Colors.BOLD}{Colors.MAGENTA}TEMPORAL ECHOES AT {location.upper()}{Colors.RESET}\n\n"
                for i, echo in enumerate(self.state.temporal_echoes[location]):
                    status = "[DISCOVERED]" if echo["discovered"] else "[UNDISCOVERED]"
                    echo_type = "PAST" if echo["type"] == "past" else "FUTURE"
                    echo_list += f"{i+1}. {status} {echo_type} ECHO: Day {echo['day']}, {echo['time_period']}\n"
                echo_list += "\nUse 'echo <number>' to focus on a specific echo."
                return echo_list
            if args[0].isdigit():
                echo_index = int(args[0]) - 1
                if 0 <= echo_index < len(self.state.temporal_echoes[location]):
                    echo = self.state.temporal_echoes[location][echo_index]
                    if not echo["discovered"]:
                        discovered = self.state.discover_echo(location, echo_index)
                        if discovered:
                            past_effects = [
                                "The air around you seems to grow thick with memory as you reach back through time.",
                                "Colors fade to sepia as the temporal echo materializes around you.",
                                "You hear distant voices and sounds from another time as the echo forms.",
                                "The room seems to shift and change, revealing its past configuration."
                            ]
                            future_effects = [
                                "Reality shimmers with possibility as you glimpse what may come to pass.",
                                "The air crackles with potential futures as the echo takes shape.",
                                "Time seems to stretch forward, pulling you into a moment yet to come.",
                                "The boundaries between now and then blur as you perceive what might be."
                            ]
                            import random
                            if echo["type"] == "past":
                                effect = random.choice(past_effects)
                            else:
                                effect = random.choice(future_effects)
                            return f"{Colors.BOLD}{Colors.MAGENTA}You've discovered a new temporal echo!{Colors.RESET}\n\n" + \
                                   f"{effect}\n\n" + \
                                   f"As you focus your temporal senses, you perceive: {echo['description']}\n\n" + \
                                   f"You gained 2 paradox points from this discovery."
                    return f"{Colors.BOLD}{Colors.MAGENTA}TEMPORAL ECHO{Colors.RESET}\n\n" + \
                           f"Type: {echo['type'].upper()}\n" + \
                           f"When: Day {echo['day']}, {echo['time_period']}\n\n" + \
                           f"{echo['description']}"
                else:
                    return "Invalid echo number."
            return "Use 'echo <number>' to focus on a specific echo."
        elif cmd in ["paradox", "points", "pp"]:
            if not args:
                skill_status = ""
                skill_info = {
                    "echo_vision": {"cost": 5, "description": "Allows you to see temporal echoes more clearly"},
                    "paradox_manipulation": {"cost": 10, "description": "Enables manipulation of paradox energy"},
                    "quantum_entanglement": {"cost": 15, "description": "Allows you to alter quantum states of objects"},
                    "temporal_projection": {"cost": 20, "description": "Create parallel versions of yourself"},
                    "rift_creation": {"cost": 25, "description": "Create rifts between different locations"}
                }
                for skill, status in self.state.temporal_skills.items():
                    skill_display = skill.replace('_', ' ').title()
                    status_text = f"{Colors.GREEN}Unlocked{Colors.RESET}" if status else f"{Colors.RED}Locked - {skill_info[skill]['cost']} points{Colors.RESET}"
                    skill_status += f"- {skill_display}: {status_text}\n  {skill_info[skill]['description']}\n"
                return f"{Colors.BOLD}{Colors.CYAN}PARADOX POINTS: {self.state.paradox_points}{Colors.RESET}\n\n" + \
                       f"Paradox points are gained by discovering temporal echoes and resolving anomalies.\n" + \
                       f"They can be spent to unlock and use temporal skills.\n\n" + \
                       f"{Colors.BOLD}TEMPORAL SKILLS:{Colors.RESET}\n{skill_status}\n" + \
                       f"Use 'paradox unlock <skill_name>' to unlock a skill."
            if args[0] == "unlock" and len(args) > 1:
                skill_name = "_".join(args[1:]).lower()
                if skill_name in self.state.temporal_skills:
                    if self.state.temporal_skills[skill_name]:
                        return f"You have already unlocked the {skill_name.replace('_', ' ')} skill."
                    result = self.state.unlock_temporal_skill(skill_name)
                    if result:
                        skill_effects = {
                            "echo_vision": "The world around you seems to shimmer with ghostly images from other times.",
                            "paradox_manipulation": "You feel temporal energy coursing through your fingertips, ready to be shaped.",
                            "quantum_entanglement": "Your perception shifts, allowing you to see the quantum possibilities of objects around you.",
                            "temporal_projection": "You sense versions of yourself from alternate timelines, waiting to be called forth.",
                            "rift_creation": "The fabric of spacetime feels malleable to you now, ready to be torn and reshaped."
                        }
                        special_effect = skill_effects.get(skill_name, "")
                        return f"{Colors.BOLD}{Colors.CYAN}You've unlocked the {skill_name.replace('_', ' ')} skill!{Colors.RESET}\n\n" + \
                               f"You feel a surge of temporal energy as new abilities become available to you.\n" + \
                               (f"{special_effect}\n\n" if special_effect else "") + \
                               f"You now have {self.state.paradox_points} paradox points remaining."
                    else:
                        return f"You need at least 5 paradox points to unlock this skill. You currently have {self.state.paradox_points}."
                else:
                    return f"Unknown skill: {skill_name}. Available skills: " + ", ".join([s.replace('_', ' ') for s in self.state.temporal_skills.keys()])
        elif cmd in ["rift", "rifts"]:
            if not args:
                if not self.state.time_rifts:
                    return "You haven't created any time rifts yet."
                rift_list = f"{Colors.BOLD}{Colors.CYAN}ACTIVE TIME RIFTS{Colors.RESET}\n\n"
                for rift_id, rift in self.state.time_rifts.items():
                    rift_list += f"{rift_id}: {rift['origin']} → {rift['destination']} (Stability: {rift['stability']})\n"
                rift_list += "\nUse 'rift use <rift_id>' to travel through a rift."
                rift_list += "\nUse 'rift create <target>' to create a new rift (requires rift_creation skill)."
                return rift_list
            if args[0] == "create" and len(args) > 1:
                if not self.state.temporal_skills["rift_creation"]:
                    return "You need to unlock the rift creation skill first. Use 'paradox unlock rift_creation'."
                target = " ".join(args[1:])
                matched_location = None
                for loc in LOCATIONS:
                    if loc.lower().startswith(target.lower()):
                        matched_location = loc
                        break
                if matched_location:
                    success, message = self.state.create_time_rift(self.state.current_location, matched_location)
                    if success:
                        return f"{Colors.BOLD}{Colors.CYAN}You've created a time rift to {matched_location}!{Colors.RESET}\n\n" + \
                               f"The fabric of reality tears open, creating a shimmering portal.\n" + \
                               f"This has reduced timeline stability by 5 points.\n" + \
                               f"You now have {self.state.paradox_points} paradox points remaining."
                    else:
                        return message
                else:
                    return f"Unknown location: {target}. Available locations: " + ", ".join(LOCATIONS)
            if args[0] == "use" and len(args) > 1:
                rift_id = " ".join(args[1:])
                if rift_id in self.state.time_rifts:
                    success, message = self.state.use_time_rift(rift_id)
                    if success:
                        special_effects = {
                            "Research Lab": "The air crackles with scientific energy.",
                            "Temporal Engine Room": "You feel the pulse of temporal energy all around you.",
                            "Quantum Archives": "Reality seems slightly fluid here, as if multiple timelines converge.",
                            "Observation Deck": "The view of spacetime stretches out before you in all directions."
                        }
                        destination = self.state.time_rifts[rift_id]["destination"]
                        special_effect = special_effects.get(destination, "")
                        return f"{Colors.BOLD}{Colors.CYAN}You step through the time rift...{Colors.RESET}\n\n" + \
                               (f"{special_effect}\n\n" if special_effect else "") + \
                               self.describe_current_location()
                    else:
                        return message
                else:
                    return f"No rift with ID '{rift_id}' exists."
        elif cmd in ["quantum", "q"]:
            if not self.state.temporal_skills["quantum_entanglement"]:
                return "You need to unlock the quantum entanglement skill first. Use 'paradox unlock quantum_entanglement'."
            if not args:
                if not self.state.quantum_states:
                    return "You haven't set any quantum states yet."
                quantum_list = f"{Colors.BOLD}{Colors.CYAN}QUANTUM STATES{Colors.RESET}\n\n"
                for obj_name, obj_data in self.state.quantum_states.items():
                    quantum_list += f"{obj_name}: {obj_data['state']}\n"
                return quantum_list
            if len(args) >= 2:
                obj_name = args[0]
                state_value = " ".join(args[1:])
                success, message = self.state.set_quantum_state(obj_name, state_value)
                if success:
                    return f"{Colors.BOLD}{Colors.CYAN}You've set the quantum state of {obj_name} to '{state_value}'.{Colors.RESET}\n\n" + \
                           f"The object seems to shimmer briefly as its quantum state changes."
                else:
                    return message
        elif cmd in ["parallel", "self", "clone"]:
            if not self.state.temporal_skills["temporal_projection"]:
                return "You need to unlock the temporal projection skill first. Use 'paradox unlock temporal_projection'."
            if not args:
                if not self.state.parallel_selves:
                    return "You haven't created any parallel selves yet."
                parallel_list = f"{Colors.BOLD}{Colors.CYAN}YOUR PARALLEL SELVES{Colors.RESET}\n\n"
                for i, self_data in enumerate(self.state.parallel_selves):
                    parallel_list += f"{i+1}. {self_data['name']} ({self_data['specialty']})\n"
                    parallel_list += f"   Description: {self_data['description']}\n"
                    parallel_list += f"   Uses remaining: {self_data['uses_remaining']}\n"
                parallel_list += "\nUse 'parallel create <name> <specialty>' to create a new parallel self."
                parallel_list += "\nUse 'parallel use <number>' to use a parallel self's ability."
                parallel_list += "\n\nAvailable specialties: engineer, scientist, explorer, guardian"
                return parallel_list
            if args[0] == "create" and len(args) > 2:
                name = args[1]
                specialty = args[2].lower()
                success, message = self.state.create_parallel_self(name, specialty)
                if success:
                    return f"{Colors.BOLD}{Colors.CYAN}You've created a parallel version of yourself!{Colors.RESET}\n\n" + \
                           f"A shimmering copy of you named {name} with {specialty} specialty appears briefly before fading into the temporal background.\n" + \
                           f"This has reduced timeline stability by 10 points.\n" + \
                           f"You now have {self.state.paradox_points} paradox points remaining."
                else:
                    return message
            if args[0] == "use" and len(args) > 1 and args[1].isdigit():
                self_index = int(args[1]) - 1
                if 0 <= self_index < len(self.state.parallel_selves):
                    parallel_self = self.state.parallel_selves[self_index]
                    if parallel_self["uses_remaining"] > 0:
                        parallel_self["uses_remaining"] -= 1
                        if parallel_self["uses_remaining"] <= 0:
                            self.state.parallel_selves.pop(self_index)
                        effects = {
                            "engineer": "The temporal anomalies in this area are temporarily stabilized.",
                            "scientist": "You gain insight into the quantum states of nearby objects.",
                            "explorer": "You discover a hidden object: a time fragment.",
                            "guardian": "Your timeline stability is increased by 5 points."
                        }
                        if parallel_self["specialty"] == "explorer":
                            self.state.time_fragments += 1
                        elif parallel_self["specialty"] == "guardian":
                            self.state.stability_factor += 5
                        return f"{Colors.BOLD}{Colors.CYAN}Your parallel self appears and uses their ability!{Colors.RESET}\n\n" + \
                               f"{parallel_self['name']} materializes briefly.\n" + \
                               f"Effect: {effects[parallel_self['specialty']]}"
                    else:
                        self.state.parallel_selves.pop(self_index)
                        return "This parallel self has become too unstable and dissipates into the timestream."
                else:
                    return "Invalid parallel self number."
        else:
            return f"Unknown command: {command}. Type 'help' for a list of commands."
    def describe_current_location(self):
        """Generate a description of the current location"""
        location = self.locations[self.state.current_location]
        desc = f"{Colors.BOLD}{Colors.CYAN}{location.name} - Day {self.state.current_day}, {TIME_PERIODS[self.state.current_time]}{Colors.RESET}\n\n"
        desc += f"{location.description}\n\n"
        characters = self.get_characters_at_location()
        if characters:
            desc += f"{Colors.BOLD}Characters present:{Colors.RESET}\n"
            for character in characters:
                desc += f"- {character.name}: {character.description}\n"
            desc += "\n"
        if location.objects:
            desc += f"{Colors.BOLD}Objects of interest:{Colors.RESET}\n"
            for obj_name in location.objects:
                desc += f"- {obj_name}\n"
            desc += "\n"
        if location.anomalies:
            desc += f"{Colors.BOLD}{Colors.MAGENTA}Temporal Anomalies:{Colors.RESET}\n"
            for anomaly in location.anomalies:
                desc += f"- {anomaly}\n"
            desc += "\n"
        desc += f"{Colors.BOLD}Exits:{Colors.RESET} " + ", ".join(location.connections)
        available_events = self.get_available_events()
        if available_events:
            desc += f"\n\n{Colors.BOLD}{Colors.GREEN}There are special events available here. Use 'event' to see them.{Colors.RESET}"
        return desc
    def show_help(self):
        """Show help text"""
        help_text = f"{Colors.BOLD}{Colors.CYAN}TIME DRIFT - COMMANDS{Colors.RESET}\n\n"
        help_text += f"{Colors.BOLD}{Colors.GREEN}BASIC COMMANDS:{Colors.RESET}\n"
        basic_commands = [
            ("go/move/travel <location>", "Move to a connected location"),
            ("wait/advance/time", "Advance time to the next period"),
            ("inventory/items/i", "Check your inventory"),
            ("knowledge/know/k", "Review what you've learned"),
            ("examine/look/x [target]", "Examine your surroundings or a specific object/person"),
            ("talk/speak/ask <character>", "Talk to a character"),
            ("event/e [number]", "List or interact with available events"),
            ("choose/select/c <number>", "Make a choice in an active event"),
            ("timeline/tl", "View your timeline and changes made"),
            ("causality/web/cw", "View the causality web of your actions"),
            ("memories/loops/mem", "Review memories from previous time loops"),
            ("save", "Save your game"),
            ("load", "Load a saved game"),
            ("help/?", "Show this help text"),
            ("quit/exit", "Quit the game")
        ]
        for cmd, desc in basic_commands:
            help_text += f"{Colors.BOLD}{cmd}{Colors.RESET}: {desc}\n"
        help_text += f"\n{Colors.BOLD}{Colors.MAGENTA}TEMPORAL ABILITIES:{Colors.RESET}\n"
        temporal_abilities = [
            ("rewind", "Use 3 time fragments to rewind time by one period"),
            ("glimpse", "Use 2 time fragments to glimpse potential futures")
        ]
        for cmd, desc in temporal_abilities:
            help_text += f"{Colors.BOLD}{cmd}{Colors.RESET}: {desc}\n"
        help_text += f"\n{Colors.BOLD}{Colors.CYAN}ADVANCED TEMPORAL COMMANDS:{Colors.RESET}\n"
        advanced_commands = [
            ("echoes/echo [number]", "View and interact with temporal echoes in your location"),
            ("paradox/points/pp [unlock <skill>]", "View and spend paradox points to unlock skills"),
            ("rift/rifts [create/use <target>]", "Create and use time rifts between locations"),
            ("quantum/q [object] [state]", "Manipulate the quantum state of objects"),
            ("parallel/self/clone [create/use]", "Create and utilize parallel versions of yourself")
        ]
        for cmd, desc in advanced_commands:
            help_text += f"{Colors.BOLD}{cmd}{Colors.RESET}: {desc}\n"
        help_text += f"\n{Colors.BOLD}{Colors.YELLOW}TIPS:{Colors.RESET}\n"
        help_text += "- Your knowledge persists across time loops\n"
        help_text += "- Some objects can be made to persist across loops\n"
        help_text += "- Your actions create ripples in the timeline that may have consequences\n"
        help_text += "- Pay attention to character schedules and patterns\n"
        help_text += "- Collect time fragments by resolving temporal anomalies\n"
        help_text += "- Discover temporal echoes to gain paradox points\n"
        help_text += "- Unlock temporal skills to manipulate reality in new ways\n"
        help_text += "- Create time rifts to travel instantly between locations\n"
        help_text += "- Use parallel selves to perform actions in multiple places\n"
        return help_text
def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    title = f"""
{Colors.CYAN}{Colors.BOLD}████████╗██╗███╗   ███╗███████╗      ██████╗ ██████╗ ██╗███████╗████████╗
╚══██╔══╝██║████╗ ████║██╔════╝      ██╔══██╗██╔══██╗██║██╔════╝╚══██╔══╝
   ██║   ██║██╔████╔██║█████╗  █████╗██║  ██║██████╔╝██║█████╗     ██║   
   ██║   ██║██║╚██╔╝██║██╔══╝  ╚════╝██║  ██║██╔══██╗██║██╔══╝     ██║   
   ██║   ██║██║ ╚═╝ ██║███████╗      ██████╔╝██║  ██║██║██║        ██║   
   ╚═╝   ╚═╝╚═╝     ╚═╝╚══════╝      ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝        ╚═╝   
{Colors.RESET}"""
    print(title)
    print(f"{Colors.BOLD}A CLI-based sci-fi temporal puzzle adventure{Colors.RESET}")
    print("You're a chrono-drifter stuck in a 7-day time loop.")
    print("Every decision ripples through time.")
    print(f"{Colors.BOLD}Break the loop, or doom every timeline.{Colors.RESET}")
    print("\nType 'help' for commands.\n")
    game = GameEngine()
    game.initialize_game()
    print(game.describe_current_location())
    while True:
        try:
            command = input(f"\n{Colors.BOLD}[Day {game.state.current_day}, {TIME_PERIODS[game.state.current_time]}] > {Colors.RESET}").strip()
            if not command:
                continue
            result = game.process_command(command)
            if result == "QUIT":
                print("Thanks for playing Time Drift!")
                break
            print("\n" + result)
        except KeyboardInterrupt:
            print("\n\nGame interrupted. Thanks for playing!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("The timeline seems unstable. Please try again.")
if __name__ == "__main__":
    main()