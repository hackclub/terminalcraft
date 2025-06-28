#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
@dataclass
class Character:
    """Class representing a character in the game."""
    name: str
    background: str
    description: str
    traits: Dict[str, Any] = field(default_factory=dict)
    def get_interaction(self, location_id: str, game_state: Dict[str, Any]) -> str:
        """Get character-specific dialogue for the current location."""
        if self.name == "Sir Crocodile":
            if location_id.startswith("level_5"):
                return "This cold is nothing. We need to keep moving."
            elif location_id.startswith("level_2"):
                return "I sense we're being followed. Be on guard."
            else:
                return "Don't slow me down. I won't wait for you."
        elif self.name == "Bon Clay":
            if location_id.startswith("level_5"):
                return "Brr! This is freezing! But don't worry, my ballet training prepared me for endurance!"
            elif location_id.startswith("level_3"):
                return "Ugh, this floor gives me the creeps. Stay close, friend!"
            elif location_id.startswith("level_1"):
                return "We're so close to freedom! Can you feel it? The sea is calling us!"
            else:
                return "Together, we can overcome anything! Un, deux, trois!"
        elif self.name == "Emporio Ivankov":
            if location_id.startswith("level_5.5"):
                return "Welcome to my kingdom, candy! Newkama Land is a paradise amidst hell!"
            else:
                return "HEE-HAW! With the power of hormones, anything is possible!"
        elif self.name == "Magellan":
            return "There is no escape from justice. Submit, and your suffering will be... minimized."
        elif self.name == "Hannyabal":
            return "As the future warden of Impel Down, I cannot allow you to escape! Though... if I caught you, I might get promoted..."
        else:
            return f"{self.name} nods silently."
def create_character(name: str, background: str, description: str) -> Character:
    """Factory function to create a character with the given attributes."""
    return Character(
        name=name,
        background=background,
        description=description
    )
CHARACTERS = {
    "crocodile": Character(
        name="Sir Crocodile",
        background="Shichibukai",
        description="Former Warlord of the Sea with the power of the Sand-Sand Fruit. Calculating and ruthless.",
        traits={"devil_fruit": "Logia - Sand", "strength": 9, "trustworthiness": 2}
    ),
    "bon_clay": Character(
        name="Bon Clay",
        background="Okama",
        description="Former Baroque Works Officer with the power of the Clone-Clone Fruit. Flamboyant but loyal.",
        traits={"devil_fruit": "Paramecia - Clone", "strength": 7, "trustworthiness": 9}
    ),
    "ivankov": Character(
        name="Emporio Ivankov",
        background="Revolutionary",
        description="Queen of Newkama Land with the power of the Hormone-Hormone Fruit. Eccentric but powerful.",
        traits={"devil_fruit": "Paramecia - Hormone", "strength": 8, "trustworthiness": 7}
    ),
    "magellan": Character(
        name="Magellan",
        background="Prison Warden",
        description="Chief Warden of Impel Down with the power of the Venom-Venom Fruit. Dutiful and deadly.",
        traits={"devil_fruit": "Paramecia - Venom", "strength": 10, "trustworthiness": 0}
    ),
    "hannyabal": Character(
        name="Hannyabal",
        background="Vice Warden",
        description="Vice Warden of Impel Down who dreams of becoming the warden. Ambitious but somewhat incompetent.",
        traits={"devil_fruit": None, "strength": 6, "trustworthiness": 3}
    ),
    "saldeath": Character(
        name="Saldeath",
        background="Chief Guard",
        description="Chief Guard who commands the Blugori. Small in stature but commands respect.",
        traits={"devil_fruit": None, "strength": 5, "trustworthiness": 1}
    ),
    "sadi": Character(
        name="Sadi",
        background="Chief Guard",
        description="Sadistic Chief Guard who enjoys torture. Leads the Demon Guards of Level 4.",
        traits={"devil_fruit": None, "strength": 7, "trustworthiness": 0}
    ),
    "jinbe": Character(
        name="Jinbe",
        background="Shichibukai",
        description="Fish-Man Shichibukai imprisoned for refusing to fight against Whitebeard. Honorable and strong.",
        traits={"devil_fruit": None, "strength": 9, "trustworthiness": 8}
    ),
    "luffy": Character(
        name="Monkey D. Luffy",
        background="Pirate Captain",
        description="Captain of the Straw Hat Pirates with the power of the Gum-Gum Fruit. Impulsive but determined.",
        traits={"devil_fruit": "Paramecia - Gum", "strength": 9, "trustworthiness": 10}
    )
}
def get_character(character_id: str) -> Optional[Character]:
    """Get a pre-defined character by their ID."""
    return CHARACTERS.get(character_id) 