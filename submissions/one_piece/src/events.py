#!/usr/bin/env python3
import random
from typing import Dict, List, Any
from items import get_item
def trigger_random_event(game_state: Dict[str, Any], location: Any, inventory: List[Any]) -> Dict[str, Any]:
    """Trigger a random event based on the current location and game state."""
    level_events = RANDOM_EVENTS.get(game_state['current_level'], [])
    general_events = RANDOM_EVENTS.get(0, [])
    available_events = []
    for event in level_events + general_events:
        requirements_met = True
        if 'requires_flag' in event and event['requires_flag'] not in game_state.get('flags', {}):
            requirements_met = False
        if 'exclude_flag' in event and event['exclude_flag'] in game_state.get('flags', {}):
            requirements_met = False
        if 'requires_item' in event:
            has_item = any(item.id == event['requires_item'] for item in inventory)
            if not has_item:
                requirements_met = False
        if requirements_met:
            available_events.append(event)
    if not available_events:
        return {}
    chosen_event = random.choice(available_events)
    result = {'message': chosen_event['message']}
    if 'item_add' in chosen_event:
        item = get_item(chosen_event['item_add'])
        if item:
            result['item_add'] = item
    if 'item_remove' in chosen_event:
        for item in inventory:
            if item.id == chosen_event['item_remove']:
                result['item_remove'] = item
                break
    if 'health' in chosen_event:
        result['health'] = chosen_event['health']
    if 'add_flag' in chosen_event:
        game_state['flags'][chosen_event['add_flag']] = True
    if 'remove_flag' in chosen_event:
        if chosen_event['remove_flag'] in game_state['flags']:
            del game_state['flags'][chosen_event['remove_flag']]
    if 'game_over' in chosen_event:
        result['game_over'] = chosen_event['game_over']
    return result
RANDOM_EVENTS = {
    0: [
        {
            'message': """
A nearby explosion rocks the prison!
Debris falls from the ceiling, and you have to dodge quickly to avoid being crushed.
            """,
            'health': -10
        },
        {
            'message': """
You hear rapid footsteps approaching.
You hide just in time as a group of guards rushes past, not noticing you.
"Hurry! The warden wants all available personnel at Level 1!" one shouts.
            """
        },
        {
            'message': """
You stumble upon an injured guard slumped against the wall.
He doesn't seem to notice you as he's focusing on bandaging his wound.
Taking advantage of his distraction, you quietly search his belongings...
            """,
            'item_add': 'food_ration'
        },
        {
            'message': """
A familiar voice calls out, "Psst! Over here!"
You turn to see a prisoner you freed earlier. "Thanks for the help back there," they say.
"Take this. I found it while escaping. Might be useful to you."
            """,
            'item_add': 'explosive_tag',
            'requires_flag': 'freed_level6_prisoners'
        },
        {
            'message': """
A prison-wide announcement blares over the speakers:
"ATTENTION ALL PERSONNEL! MULTIPLE PRISONER ESCAPES CONFIRMED! 
ALL GUARDS REPORT TO YOUR EMERGENCY STATIONS IMMEDIATELY!"
            """
        },
        {
            'message': """
You hear a faint whisper from a nearby vent: "Hey, you looking to escape too?"
An eye peers at you through the grate. "There's a hidden passage in Level 5. 
Look for a crack in the eastern wall. That's where you'll find Newkama Land."
            """,
            'add_flag': 'heard_about_newkama'
        }
    ],
    6: [
        {
            'message': """
A massive prisoner with tattoos covering his body charges at you wildly!
You manage to sidestep and he crashes into the wall, knocking himself unconscious.
Searching his pockets, you find something interesting.
            """,
            'item_add': 'seastone_key'
        },
        {
            'message': """
You spot Shiryuu of the Rain, the head jailer, cutting down prisoners indiscriminately.
His sword moves like lightning as he laughs maniacally.
You press yourself against the wall and hold your breath as he passes by.
            """
        },
        {
            'message': """
Screams echo through the corridors as something terrible approaches.
The shadows seem to lengthen as Blackbeard himself strides through the level,
newly escaped and recruiting the most dangerous prisoners to his crew.
Thankfully, he doesn't notice you in the chaos.
            """
        }
    ],
    5: [
        {
            'message': """
The extreme cold is taking its toll on your body.
Your teeth chatter uncontrollably and your extremities are going numb.
You need to find warmth soon or you'll freeze.
            """,
            'health': -15,
            'exclude_flag': 'cold_protected'
        },
        {
            'message': """
A wolf suddenly leaps at you from behind a snowdrift!
You barely manage to fend it off, but not before it sinks its teeth into your arm.
            """,
            'health': -20
        },
        {
            'message': """
You find a guard frozen solid, his expression one of terror.
Whatever froze him did so instantly, but he's been dead for hours.
His coat seems to be in good condition...
            """,
            'item_add': 'warm_coat',
            'exclude_flag': 'cold_protected'
        },
        {
            'message': """
You notice strange marks on the wall - they look like they've been deliberately carved.
Upon closer inspection, they form an arrow pointing to a small crack in the wall.
The crack seems large enough to squeeze through...
            """,
            'add_flag': 'found_newkama'
        }
    ],
    4: [
        {
            'message': """
The intense heat is overwhelming!
Sweat pours down your face, and your throat is parched beyond belief.
You need water desperately.
            """,
            'health': -10
        },
        {
            'message': """
A gout of flame erupts from one of the furnaces, nearly engulfing you!
You dive out of the way, but your arm is singed by the intense heat.
            """,
            'health': -15
        },
        {
            'message': """
You spot one of the infamous Demon Guards patrolling nearby!
The massive, horned creature sniffs the air, as if sensing your presence.
You hold perfectly still until it moves on.
            """
        },
        {
            'message': """
In the chaos, someone has knocked over a barrel of water.
You manage to drink deeply before continuing on your way,
feeling refreshed despite the oppressive heat.
            """,
            'health': 15
        },
        {
            'message': """
You spot a book that seems out of place in this hellish environment.
It appears to have been dropped by a prisoner. The cover reads:
"The Art of the Black Leg - A Fighting Guide by 'Red Leg' Zeff"
            """,
            'item_add': 'blackleg_manual'
        }
    ],
    3: [
        {
            'message': """
The desert-like conditions of Level 3 are draining your strength.
Each step through the deep sand requires twice the effort.
Your throat is parched, and hunger gnaws at your stomach.
            """,
            'health': -10
        },
        {
            'message': """
You stumble upon a small cache of food and water!
It seems another escapee prepared this stash but never returned for it.
You gratefully consume some of the supplies.
            """,
            'health': 20
        },
        {
            'message': """
A group of starving prisoners spots you and charges desperately!
They're weak from hunger but dangerous in their desperation.
You manage to fight them off, but not without taking a few hits.
            """,
            'health': -15
        },
        {
            'message': """
You find a dead guard half-buried in the sand.
His communication device is still intact and functional.
            """,
            'item_add': 'den_den_mushi'
        }
    ],
    2: [
        {
            'message': """
A manticore appears around the corner, its human face twisted in a grotesque smile!
"Fresh meat!" it says in a disturbingly human voice before charging.
You manage to evade it by ducking into a side passage.
            """
        },
        {
            'message': """
You hear a hissing sound and look up to see a Basilisk crawling on the ceiling!
The massive reptile hasn't spotted you yet, but it's blocking your path forward.
You wait silently until it moves on.
            """
        },
        {
            'message': """
You accidentally step on something that crunches loudly.
Looking down, you see the bones of what was once probably a guard.
Among the remains, you spot something useful.
            """,
            'item_add': 'transponder_snail'
        },
        {
            'message': """
A sphinx pounces at you from behind!
"What's harder to keep than a promise?" it roars, batting at you with its paw.
You don't have time for riddles and barely escape its clutches, sustaining a nasty gash.
            """,
            'health': -25
        }
    ],
    1: [
        {
            'message': """
You brush against one of the blade trees, and its sharp leaves slice into your skin!
The cut is shallow but painful.
            """,
            'health': -10
        },
        {
            'message': """
You see Warden Magellan in the distance, surrounded by a cloud of poison!
He's heading in your direction, supervising the guards at the checkpoint.
You quickly duck out of sight before he can spot you.
            """
        },
        {
            'message': """
You nearly trip over something hidden beneath some fallen blade leaves.
It's a small vial labeled "Antidote - Property of Medical Unit".
This could be incredibly valuable if you encounter Magellan's poison.
            """,
            'item_add': 'poison_antidote'
        },
        {
            'message': """
A patrol of Blugori suddenly appears on the path ahead!
The blue gorilla-like creatures are sniffing the air, searching for escapees.
You hold your breath as they pass by your hiding spot.
            """
        },
        {
            'message': """
You feel a slight tremor, then hear a massive explosion from below!
Alarms blare even louder as the voice on the intercom shouts about
"intruders entering Level 4" and "all personnel on high alert".
            """,
            'add_flag': 'luffy_arrived'
        }
    ]
}
def process_story_event(event_id: str, game_state: Dict[str, Any], inventory: List[Any]) -> Dict[str, Any]:
    """Process a specific story event based on its ID."""
    return {'message': f"Story event '{event_id}' triggered."} 