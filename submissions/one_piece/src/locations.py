#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
@dataclass
class Location:
    """Class representing a location in Impel Down."""
    id: str
    name: str
    description: str
    level: int
    _options: List[Dict[str, Any]] = field(default_factory=list)
    def get_options(self, game_state: Dict[str, Any], inventory: List[Any]) -> List[Dict[str, Any]]:
        """Get the available options based on the current game state."""
        valid_options = []
        for option in self._options:
            requirements_met = True
            if 'requires_item' in option:
                item_id = option['requires_item']
                has_item = any(item.id == item_id for item in inventory)
                if not has_item:
                    requirements_met = False
            if 'requires_disguise' in option and option['requires_disguise']:
                if not game_state.get('disguised', False):
                    requirements_met = False
            if 'requires_flag' in option:
                flag = option['requires_flag']
                if not game_state.get('flags', {}).get(flag, False):
                    requirements_met = False
            if 'min_level' in option and game_state['current_level'] > option['min_level']:
                requirements_met = False
            if 'max_level' in option and game_state['current_level'] < option['max_level']:
                requirements_met = False
            if requirements_met:
                valid_options.append(option)
        return valid_options
LOCATIONS = {
    "level_6_cell": Location(
        id="level_6_cell",
        name="Level 6 - Cell Block",
        description="""
The deepest level of Impel Down, known as "Eternal Hell". 
The air is damp and cold. Several cells have been damaged in the riot.
Bodies of guards and prisoners litter the floor.
Distant sounds of combat echo through the hall.
        """,
        level=6,
        _options=[
            {
                'text': "Move to central corridor",
                'action': 'move',
                'target_location': 'level_6_corridor'
            },
            {
                'text': "Search the nearby cells",
                'action': 'story',
                'event_id': 'search_level_6_cells'
            }
        ]
    ),
    "level_6_corridor": Location(
        id="level_6_corridor",
        name="Level 6 - Main Corridor",
        description="""
The main corridor of Level 6 is in chaos. 
Alarm lights flash red, and the emergency siren wails overhead.
Several high-profile prisoners are fighting against guards.
You notice a stairwell at the far end that might lead upward.
        """,
        level=6,
        _options=[
            {
                'text': "Return to cell block",
                'action': 'move',
                'target_location': 'level_6_cell'
            },
            {
                'text': "Head to the stairwell",
                'action': 'move',
                'target_location': 'level_6_stairs'
            },
            {
                'text': "Approach Sir Crocodile",
                'action': 'story',
                'event_id': 'meet_crocodile'
            }
        ]
    ),
    "level_6_stairs": Location(
        id="level_6_stairs",
        name="Level 6 - Stairwell",
        description="""
You've reached the stairwell leading up to Level 5.
The heavy security door has been damaged, leaving a gap just wide enough to squeeze through.
Several guards lie unconscious nearby, their weapons scattered.
        """,
        level=6,
        _options=[
            {
                'text': "Return to the corridor",
                'action': 'move',
                'target_location': 'level_6_corridor'
            },
            {
                'text': "Climb up to Level 5",
                'action': 'move',
                'target_location': 'level_5_entrance',
                'new_level': 5
            },
            {
                'text': "Search the guards",
                'action': 'story',
                'event_id': 'search_level_6_guards'
            }
        ]
    ),
    "level_5_entrance": Location(
        id="level_5_entrance",
        name="Level 5 - Entrance",
        description="""
You've entered Level 5, the "Freezing Hell".
A blast of freezing air hits you like a physical force. The temperature is well below zero.
Your breath creates clouds in front of your face, and you feel your extremities going numb.
Bodies of prisoners who couldn't withstand the cold lie frozen on the ground.
        """,
        level=5,
        _options=[
            {
                'text': "Return to Level 6",
                'action': 'move',
                'target_location': 'level_6_stairs',
                'new_level': 6
            },
            {
                'text': "Move deeper into Level 5",
                'action': 'move',
                'target_location': 'level_5_cells'
            },
            {
                'text': "Search for warm clothing",
                'action': 'story',
                'event_id': 'search_for_warm_clothes'
            }
        ]
    ),
    "level_5_cells": Location(
        id="level_5_cells",
        name="Level 5 - Freezing Cells",
        description="""
The main cell area of Level 5 is a vast, open chamber.
Prisoners are kept in minimally insulated cells, exposed to the extreme cold.
Many are huddled in corners, barely moving to conserve body heat.
The guards here wear thick, insulated uniforms.
        """,
        level=5,
        _options=[
            {
                'text': "Head back to the entrance",
                'action': 'move',
                'target_location': 'level_5_entrance'
            },
            {
                'text': "Go to the wolf unit",
                'action': 'move',
                'target_location': 'level_5_wolves'
            },
            {
                'text': "Investigate a suspicious crack in the wall",
                'action': 'move',
                'target_location': 'level_5.5_entrance',
                'requires_flag': 'found_newkama'
            },
            {
                'text': "Talk to the shivering prisoner",
                'action': 'story',
                'event_id': 'meet_bon_clay'
            }
        ]
    ),
    "level_5_wolves": Location(
        id="level_5_wolves",
        name="Level 5 - Wolf Unit",
        description="""
This area of Level 5 houses the prison's wolf unit.
Vicious wolves, trained to hunt down escapees, pace in their kennels.
Currently, most of the wolves appear agitated by the prison's state of emergency.
Some kennels are open, the wolves nowhere to be seen.
        """,
        level=5,
        _options=[
            {
                'text': "Return to the cell area",
                'action': 'move',
                'target_location': 'level_5_cells'
            },
            {
                'text': "Proceed to the staircase to Level 4",
                'action': 'move',
                'target_location': 'level_5_stairs'
            },
            {
                'text': "Try to lure a wolf",
                'action': 'story',
                'event_id': 'tame_wolf'
            }
        ]
    ),
    "level_5_stairs": Location(
        id="level_5_stairs",
        name="Level 5 - Stairwell",
        description="""
You've reached the stairwell leading up to Level 4.
The heat from above creates a bizarre temperature gradient - freezing below, scorching above.
Steam rises where the two extremes meet, creating a misty barrier.
The security door here is intact but unguarded.
        """,
        level=5,
        _options=[
            {
                'text': "Return to the wolf unit",
                'action': 'move',
                'target_location': 'level_5_wolves'
            },
            {
                'text': "Climb up to Level 4",
                'action': 'move',
                'target_location': 'level_4_entrance',
                'new_level': 4
            },
            {
                'text': "Try to force the security door",
                'action': 'story',
                'event_id': 'force_level5_door'
            }
        ]
    ),
    "level_5.5_entrance": Location(
        id="level_5.5_entrance",
        name="Level 5.5 - Hidden Entrance",
        description="""
You've discovered a secret level between Levels 5 and 4 - "Newkama Land".
The temperature here is comfortably warm, a stark contrast to the freezing Level 5.
Colorful decorations and makeshift furniture fill the hidden chamber.
This appears to be a sanctuary for prisoners who've escaped from their cells.
        """,
        level=55,
        _options=[
            {
                'text': "Return to Level 5",
                'action': 'move',
                'target_location': 'level_5_cells',
                'new_level': 5
            },
            {
                'text': "Explore Newkama Land",
                'action': 'move',
                'target_location': 'level_5.5_main'
            }
        ]
    ),
    "level_5.5_main": Location(
        id="level_5.5_main",
        name="Level 5.5 - Newkama Land",
        description="""
The main area of Newkama Land is surprisingly lively.
People in flamboyant clothing dance and sing despite being in the world's most secure prison.
Food and drinks are being shared, and there's an atmosphere of defiant celebration.
At the center, on a makeshift throne, sits a large person with an even larger purple afro.
        """,
        level=55,
        _options=[
            {
                'text': "Return to the entrance",
                'action': 'move',
                'target_location': 'level_5.5_entrance'
            },
            {
                'text': "Approach the person with the afro",
                'action': 'story',
                'event_id': 'meet_ivankov'
            },
            {
                'text': "Ask about a way to Level 4",
                'action': 'move',
                'target_location': 'level_5.5_exit',
                'requires_flag': 'ivankov_alliance'
            }
        ]
    ),
    "level_5.5_exit": Location(
        id="level_5.5_exit",
        name="Level 5.5 - Secret Passage",
        description="""
Ivankov has shown you a secret passage that bypasses much of Level 4.
The narrow tunnel appears to have been dug by hand over many years.
It's well-hidden and seems to lead directly upward.
        """,
        level=55,
        _options=[
            {
                'text': "Return to Newkama Land",
                'action': 'move',
                'target_location': 'level_5.5_main'
            },
            {
                'text': "Take the secret passage to Level 3",
                'action': 'move',
                'target_location': 'level_3_entrance',
                'new_level': 3,
                'requires_flag': 'ivankov_alliance'
            }
        ]
    ),
    "level_4_entrance": Location(
        id="level_4_entrance",
        name="Level 4 - Entrance",
        description="""
You've entered Level 4, the "Blazing Hell".
Intense heat immediately assaults your senses. The air is scorching and dry.
A massive cauldron of boiling blood sits in the center, used to punish prisoners.
Guards in heat-resistant uniforms patrol the walkways.
        """,
        level=4,
        _options=[
            {
                'text': "Return to Level 5",
                'action': 'move',
                'target_location': 'level_5_stairs',
                'new_level': 5
            },
            {
                'text': "Move to the central area",
                'action': 'move',
                'target_location': 'level_4_central'
            }
        ]
    ),
    "level_4_central": Location(
        id="level_4_central",
        name="Level 4 - Central Area",
        description="""
The central area of Level 4 is dominated by the massive pot of boiling blood.
Prisoners labor around it, carrying rocks from one side to another as punishment.
The riot has reached this level too - several guards are fighting escaped prisoners.
You notice Chief Guard Sadi directing her Demon Guards to restore order.
        """,
        level=4,
        _options=[
            {
                'text': "Head back to the entrance",
                'action': 'move',
                'target_location': 'level_4_entrance'
            },
            {
                'text': "Go to the kitchen area",
                'action': 'move',
                'target_location': 'level_4_kitchen'
            },
            {
                'text': "Try to sneak past the Demon Guards",
                'action': 'story',
                'event_id': 'sneak_past_demons'
            }
        ]
    ),
    "level_4_kitchen": Location(
        id="level_4_kitchen",
        name="Level 4 - Prison Kitchen",
        description="""
The prison's kitchen makes use of Level 4's extreme heat for cooking.
Massive pots and ovens line the walls, currently abandoned in the chaos.
Food is scattered everywhere, and several weapons seem to have been improvised from kitchen tools.
The stairwell to Level 3 is visible through the back door.
        """,
        level=4,
        _options=[
            {
                'text': "Return to the central area",
                'action': 'move',
                'target_location': 'level_4_central'
            },
            {
                'text': "Head to the stairwell",
                'action': 'move',
                'target_location': 'level_4_stairs'
            },
            {
                'text': "Search for useful items",
                'action': 'story',
                'event_id': 'search_kitchen'
            }
        ]
    ),
    "level_4_stairs": Location(
        id="level_4_stairs",
        name="Level 4 - Stairwell",
        description="""
You've reached the stairwell leading up to Level 3.
The security door here has been forced open, likely by escaping prisoners.
Several unconscious guards lie on the ground, suggesting a recent battle.
The air from above feels less oppressive than the scorching heat of Level 4.
        """,
        level=4,
        _options=[
            {
                'text': "Return to the kitchen",
                'action': 'move',
                'target_location': 'level_4_kitchen'
            },
            {
                'text': "Climb up to Level 3",
                'action': 'move',
                'target_location': 'level_3_entrance',
                'new_level': 3
            }
        ]
    ),
    "level_3_entrance": Location(
        id="level_3_entrance",
        name="Level 3 - Entrance",
        description="""
You've entered Level 3, the "Starvation Hell".
The air is dry and stale. Everything here seems designed to drain energy and hope.
Empty cells line the walls, their doors hanging open from the riot.
Sand covers the floor, making each step more exhausting than it should be.
        """,
        level=3,
        _options=[
            {
                'text': "Return to Level 4",
                'action': 'move',
                'target_location': 'level_4_stairs',
                'new_level': 4
            },
            {
                'text': "Proceed through the sandy corridor",
                'action': 'move',
                'target_location': 'level_3_corridor'
            }
        ]
    ),
    "level_3_corridor": Location(
        id="level_3_corridor",
        name="Level 3 - Main Corridor",
        description="""
The main corridor of Level 3 stretches before you, seemingly endless.
The floor is covered in deep sand, making progress slow and tiring.
Emaciated prisoners wander aimlessly, too weak from starvation to pose a threat.
You can see a guard post ahead, and the stairs to Level 2 beyond it.
        """,
        level=3,
        _options=[
            {
                'text': "Head back to the entrance",
                'action': 'move',
                'target_location': 'level_3_entrance'
            },
            {
                'text': "Approach the guard post",
                'action': 'move',
                'target_location': 'level_3_guard_post'
            }
        ]
    ),
    "level_3_guard_post": Location(
        id="level_3_guard_post",
        name="Level 3 - Guard Post",
        description="""
The guard post controls access to the stairwell leading up to Level 2.
It's currently manned by two alert guards who haven't fled their post despite the riot.
They're watching the approach carefully, weapons ready.
A security Den Den Mushi is mounted on the wall, likely connected to other levels.
        """,
        level=3,
        _options=[
            {
                'text': "Return to the main corridor",
                'action': 'move',
                'target_location': 'level_3_corridor'
            },
            {
                'text': "Try to approach in disguise",
                'action': 'move',
                'target_location': 'level_3_stairs',
                'requires_disguise': True
            },
            {
                'text': "Attack the guards directly",
                'action': 'story',
                'event_id': 'attack_level3_guards'
            },
            {
                'text': "Try to sneak past the guards",
                'action': 'story',
                'event_id': 'sneak_level3_guards'
            }
        ]
    ),
    "level_3_stairs": Location(
        id="level_3_stairs",
        name="Level 3 - Stairwell",
        description="""
You've reached the stairwell leading up to Level 2.
Unlike the previous levels, this area seems relatively untouched by the riot.
The security door is locked but can be opened from this side.
You can hear bestial roars echoing from above - Level 2's fearsome beasts.
        """,
        level=3,
        _options=[
            {
                'text': "Return to the guard post",
                'action': 'move',
                'target_location': 'level_3_guard_post'
            },
            {
                'text': "Climb up to Level 2",
                'action': 'move',
                'target_location': 'level_2_entrance',
                'new_level': 2
            }
        ]
    ),
    "level_2_entrance": Location(
        id="level_2_entrance",
        name="Level 2 - Entrance",
        description="""
You've entered Level 2, the "Beast Hell".
Roars, hisses, and screeches echo throughout the level, creating a cacophony of animal sounds.
The floor is stained with what appears to be blood, both fresh and old.
Signs of struggle are everywhere - the beasts have broken free of their enclosures.
        """,
        level=2,
        _options=[
            {
                'text': "Return to Level 3",
                'action': 'move',
                'target_location': 'level_3_stairs',
                'new_level': 3
            },
            {
                'text': "Proceed carefully through Beast Hell",
                'action': 'move',
                'target_location': 'level_2_beast_area'
            }
        ]
    ),
    "level_2_beast_area": Location(
        id="level_2_beast_area",
        name="Level 2 - Beast Area",
        description="""
The main area of Level 2 is a nightmarish zoo of deadly creatures.
Manticores, sphinx, and other beasts roam freely, some fighting each other, others hunting prisoners.
The riot has clearly allowed many beasts to escape their cages.
Several bloody guard uniforms are scattered about, but no bodies - the beasts were thorough.
        """,
        level=2,
        _options=[
            {
                'text': "Head back to the entrance",
                'action': 'move',
                'target_location': 'level_2_entrance'
            },
            {
                'text': "Try to reach the stairwell",
                'action': 'move',
                'target_location': 'level_2_puzzle_door'
            },
            {
                'text': "Hide from the approaching beasts",
                'action': 'story',
                'event_id': 'hide_from_beasts'
            }
        ]
    ),
    "level_2_puzzle_door": Location(
        id="level_2_puzzle_door",
        name="Level 2 - Puzzle Door",
        description="""
The path to the Level 1 stairwell is blocked by an elaborate puzzle door.
It appears designed to prevent the beasts from reaching the upper level.
The puzzle involves rotating dials with marine symbols to form a specific pattern.
You notice some blood smears on certain symbols - perhaps previous escapees left a clue?
        """,
        level=2,
        _options=[
            {
                'text': "Return to the beast area",
                'action': 'move',
                'target_location': 'level_2_beast_area'
            },
            {
                'text': "Try to solve the puzzle",
                'action': 'story',
                'event_id': 'solve_puzzle_door'
            },
            {
                'text': "Look for another way around",
                'action': 'story',
                'event_id': 'find_puzzle_bypass'
            }
        ]
    ),
    "level_2_stairs": Location(
        id="level_2_stairs",
        name="Level 2 - Stairwell",
        description="""
You've reached the stairwell leading up to Level 1.
The sounds of the beasts are more distant here, replaced by the echoing footsteps of guards above.
The final stretch of your escape is just ahead, but it may be the most heavily guarded.
        """,
        level=2,
        _options=[
            {
                'text': "Return to the puzzle door",
                'action': 'move',
                'target_location': 'level_2_puzzle_door'
            },
            {
                'text': "Climb up to Level 1",
                'action': 'move',
                'target_location': 'level_1_entrance',
                'new_level': 1
            }
        ]
    ),
    "level_1_entrance": Location(
        id="level_1_entrance",
        name="Level 1 - Entrance",
        description="""
You've entered Level 1, the "Crimson Hell".
The entire level is a forest of red trees with blade-like leaves that can slice flesh.
Blood stains many of the trees, evidence of prisoners who failed to navigate carefully.
This level is closest to the surface and freedom - but also to the warden's office.
        """,
        level=1,
        _options=[
            {
                'text': "Return to Level 2",
                'action': 'move',
                'target_location': 'level_2_stairs',
                'new_level': 2
            },
            {
                'text': "Navigate through the forest of blades",
                'action': 'move',
                'target_location': 'level_1_forest'
            }
        ]
    ),
    "level_1_forest": Location(
        id="level_1_forest",
        name="Level 1 - Blade Forest",
        description="""
The dense forest of blade-like trees stretches in all directions.
Moving too quickly or carelessly would result in dozens of cuts.
You can see surveillance Den Den Mushi watching from some of the trees.
In the distance, you spot what appears to be a large gathering of guards.
        """,
        level=1,
        _options=[
            {
                'text': "Head back to the entrance",
                'action': 'move',
                'target_location': 'level_1_entrance'
            },
            {
                'text': "Move carefully toward the guard gathering",
                'action': 'move',
                'target_location': 'level_1_checkpoint'
            },
            {
                'text': "Try to find a less monitored path",
                'action': 'story',
                'event_id': 'find_forest_path'
            }
        ]
    ),
    "level_1_checkpoint": Location(
        id="level_1_checkpoint",
        name="Level 1 - Main Checkpoint",
        description="""
You've reached the main checkpoint of Level 1, the last barrier before the exit.
Dozens of guards have formed a blockade, checking everyone attempting to pass.
Vice Warden Hannyabal appears to be directing the checkpoint operations.
Beyond the checkpoint, you can see daylight - the exit to the outside world.
        """,
        level=1,
        _options=[
            {
                'text': "Return to the blade forest",
                'action': 'move',
                'target_location': 'level_1_forest'
            },
            {
                'text': "Try to pass the checkpoint in disguise",
                'action': 'move',
                'target_location': 'level_1_final',
                'requires_disguise': True
            },
            {
                'text': "Look for Magellan",
                'action': 'story',
                'event_id': 'spot_magellan'
            },
            {
                'text': "Create a diversion",
                'action': 'story',
                'event_id': 'create_diversion'
            }
        ]
    ),
    "level_1_final": Location(
        id="level_1_final",
        name="Level 1 - Final Stretch",
        description="""
You've made it past the checkpoint and can see the exit gate ahead.
The gate leads to the lift that will take you to the surface and freedom.
Several smaller guard posts remain, but they're understaffed due to the riot.
The air tastes different here - fresher, with a hint of the sea.
        """,
        level=1,
        _options=[
            {
                'text': "Return to the checkpoint",
                'action': 'move',
                'target_location': 'level_1_checkpoint'
            },
            {
                'text': "Make a run for the exit",
                'action': 'story',
                'event_id': 'final_dash'
            },
            {
                'text': "Wait for the perfect moment",
                'action': 'story',
                'event_id': 'wait_for_moment'
            }
        ]
    ),
    "marine_ship": Location(
        id="marine_ship",
        name="Stolen Marine Ship",
        description="""
You've commandeered a small Marine vessel docked near Impel Down.
The ship is speeding away from the underwater prison, carrying you to freedom.
Marine battleships will be in pursuit soon, but for now, you've escaped.
The open sea stretches before you, full of both danger and possibility.
        """,
        level=0,
        _options=[]  
    ),
    "sea_king": Location(
        id="sea_king",
        name="Riding the Sea King",
        description="""
Through an incredible turn of events, you're riding on the back of a massive Sea King.
The creature speeds through the water, seemingly guided by your mysterious ally.
Impel Down is rapidly shrinking behind you as you race toward the horizon.
No Marine ship could hope to catch you at this speed.
        """,
        level=0,
        _options=[]  
    ),
    "sacrificial_end": Location(
        id="sacrificial_end",
        name="Gates of Justice",
        description="""
You stand at the Gates of Justice, the massive doors that control access to Impel Down.
Behind you, your allies are escaping. Before you, an army of Marines and Magellan himself.
You've chosen to stay behind, to give the others a chance at freedom.
Your journey ends here, but your sacrifice will not be forgotten.
        """,
        level=0,
        _options=[]  
    ),
    "luffy_rescue": Location(
        id="luffy_rescue",
        name="Level 2 - Unexpected Rescue",
        description="""
Trapped in Level 2 with no way forward or back, you've resigned yourself to recapture.
Suddenly, a commotion erupts nearby. Guards are shouting about a new intruder.
"GOMU GOMU NO BAZOOKA!" A voice shouts, followed by the sound of bodies flying.
A young man in a straw hat appears, grinning widely. "Hey! Wanna get out of here?"
        """,
        level=2,
        _options=[]  
    )
}
def get_location(location_id: str) -> Optional[Location]:
    """Get a location by its ID."""
    return LOCATIONS.get(location_id) 