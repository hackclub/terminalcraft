#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
@dataclass
class Item:
    """Class representing an item that can be collected and used."""
    id: str
    name: str
    description: str
    usable_at: Set[str] = field(default_factory=set)
    def can_use_at(self, location_id: str) -> bool:
        """Check if the item can be used at the given location."""
        if not self.usable_at:
            return True
        return location_id in self.usable_at
    def use(self, game_state: Dict[str, Any], location: Any) -> Dict[str, Any]:
        """Use the item at the current location."""
        result = {'message': f"You use {self.name}, but nothing happens."}
        if self.id == "guard_uniform":
            result = {
                'message': "You put on the guard uniform. The fit isn't perfect, but it should fool anyone who doesn't look too closely.",
                'disguise': True
            }
        elif self.id == "seastone_key":
            if location.id == "level_6_cell":
                result = {
                    'message': "You use the key to unlock the remaining cells. The prisoners rush out, creating even more chaos.",
                    'add_flag': 'freed_level6_prisoners',
                    'consume': True
                }
            elif location.id.endswith("_stairs"):
                result = {
                    'message': "You use the key to unlock the security door, bypassing any electronic locks.",
                    'consume': True
                }
            else:
                result = {
                    'message': "There's nothing here that this key would unlock."
                }
        elif self.id == "den_den_mushi":
            result = {
                'message': "You use the Den Den Mushi to listen in on guard communications. They're reporting that the main elevator is under lockdown, but the east stairwell is less guarded.",
                'add_flag': 'know_east_stairwell'
            }
        elif self.id == "warm_coat":
            if location.level == 5:
                result = {
                    'message': "You put on the warm coat. The biting cold is now more bearable.",
                    'health': 10,
                    'add_flag': 'cold_protected'
                }
            else:
                result = {
                    'message': "You put on the warm coat, but it's unnecessary in this level's temperature."
                }
        elif self.id == "food_ration":
            result = {
                'message': "You eat the food ration, regaining some strength.",
                'health': 20,
                'consume': True
            }
        elif self.id == "explosive_tag":
            result = {
                'message': "You plant the explosive tag and detonate it, creating a powerful explosion!",
                'consume': True
            }
            if location.id == "level_2_puzzle_door":
                result['message'] += " The puzzle door is blown off its hinges!"
                result['move_to'] = "level_2_stairs"
            elif location.id == "level_1_checkpoint":
                result['message'] += " The explosion creates chaos among the guards, allowing you to slip through!"
                result['move_to'] = "level_1_final"
            else:
                result['message'] += " The explosion creates a diversion, but doesn't open any new paths."
        elif self.id == "blackleg_manual":
            result = {
                'message': "You study the fighting techniques in the manual, learning how to deliver powerful kicks.",
                'add_flag': 'know_blackleg',
                'consume': True
            }
        elif self.id == "transponder_snail":
            result = {
                'message': "You use the transponder snail to make a call.",
                'consume': True
            }
            if 'bon_clay_alliance' in game_state.get('flags', {}):
                result['message'] += " Bon Clay answers and tells you he'll create a diversion at the main gate!"
                result['add_flag'] = 'bon_clay_diversion'
            elif 'crocodile_alliance' in game_state.get('flags', {}):
                result['message'] += " Crocodile tells you to meet him at the east dock, where he's secured a small boat."
                result['add_flag'] = 'crocodile_boat'
            else:
                result['message'] += " No one answers. The snail looks at you apologetically."
        elif self.id == "poison_antidote":
            if 'poisoned' in game_state.get('flags', {}):
                result = {
                    'message': "You quickly inject yourself with the antidote. The burning sensation subsides as the poison is neutralized.",
                    'health': 30,
                    'remove_flag': 'poisoned',
                    'consume': True
                }
            else:
                result = {
                    'message': "You're not poisoned right now. Better save this for when you need it."
                }
        return result
ITEMS = {
    "guard_uniform": Item(
        id="guard_uniform",
        name="Guard Uniform",
        description="A standard Impel Down guard uniform. Could be used for disguise.",
        usable_at=set()  
    ),
    "seastone_key": Item(
        id="seastone_key",
        name="Seastone Key",
        description="A master key made of Seastone that can unlock most cells and security doors in Impel Down.",
        usable_at={"level_6_cell", "level_5_stairs", "level_4_stairs", "level_3_stairs", "level_2_stairs"}
    ),
    "den_den_mushi": Item(
        id="den_den_mushi",
        name="Surveillance Den Den Mushi",
        description="A small surveillance snail that can be used to eavesdrop on guard communications.",
        usable_at=set()  
    ),
    "warm_coat": Item(
        id="warm_coat",
        name="Warm Guard Coat",
        description="A thick coat worn by guards in Level 5. Provides protection against the extreme cold.",
        usable_at={"level_5_entrance", "level_5_cells", "level_5_wolves", "level_5_stairs"}
    ),
    "food_ration": Item(
        id="food_ration",
        name="Guard's Food Ration",
        description="A substantial meal prepared for the guards. Can restore your strength.",
        usable_at=set()  
    ),
    "explosive_tag": Item(
        id="explosive_tag",
        name="Explosive Tag",
        description="A small but powerful explosive device. Could create a diversion or breach a door.",
        usable_at={"level_2_puzzle_door", "level_1_checkpoint", "level_1_forest"}
    ),
    "blackleg_manual": Item(
        id="blackleg_manual",
        name="'Blackleg' Style Fighting Manual",
        description="A manual detailing the kick-based fighting style used by a famous pirate cook.",
        usable_at=set()  
    ),
    "transponder_snail": Item(
        id="transponder_snail",
        name="Transponder Snail",
        description="A communication device that can be used to contact allies outside the prison.",
        usable_at=set()  
    ),
    "poison_antidote": Item(
        id="poison_antidote",
        name="Magellan's Poison Antidote",
        description="A specialized antidote effective against Magellan's deadly venom.",
        usable_at=set()  
    )
}
def get_item(item_id: str) -> Optional[Item]:
    """Get an item by its ID."""
    return ITEMS.get(item_id) 