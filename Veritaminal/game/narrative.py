"""
Narrative module for Veritaminal

Handles the story state, narrative branching, and game-over conditions.
"""

import logging
from .api import generate_narrative_update

logger = logging.getLogger(__name__)

class NarrativeManager:
    """
    Manages the narrative elements and story branching.
    """
    def __init__(self):
        """
        Initialize the narrative manager with default story state.
        """
        self.story_state = {
            "corruption": 0,       # Increases when approving invalid documents
            "trust": 0,            # Decreases when denying valid documents
            "day": 1,              # Current day in the game
            "events": [],          # List of narrative events that have occurred
            "ending_path": "neutral"  # Current ending path: "neutral", "corrupt", "strict"
        }
        
        # Narrative milestones trigger special events at specific points
        self.milestones = {
            "corruption_warning": False,   # Warning about corruption
            "trust_warning": False,        # Warning about losing trust
            "promotion_offered": False,    # Player offered a promotion
            "family_visit": False,         # Family member visits
            "inspector_visit": False       # Superior officer inspects
        }
    
    def update_state(self, decision, is_correct, document):
        """
        Update the story state based on player decision.
        
        Args:
            decision (str): Player decision ("approve" or "deny").
            is_correct (bool): Whether the decision was correct.
            document (dict): The document being processed.
            
        Returns:
            str: Narrative update describing the consequences.
        """
        # Update story metrics based on decision
        if decision == "approve" and not is_correct:
            self.story_state["corruption"] += 1
            self._update_ending_path()
        elif decision == "deny" and not is_correct:
            self.story_state["trust"] -= 1
            self._update_ending_path()
            
        # Check for narrative milestones
        narrative_update = self._check_milestones()
        
        # If no milestone was triggered, generate a standard update
        if not narrative_update:
            narrative_update = generate_narrative_update(
                self.story_state, 
                decision, 
                is_correct
            )
        
        # Add the day number to events
        self.story_state["events"].append({
            "day": self.story_state["day"],
            "decision": decision,
            "is_correct": is_correct,
            "document": document,
            "narrative": narrative_update
        })
        
        # Return the narrative update to display to the player
        return narrative_update
    
    def _update_ending_path(self):
        """
        Update the ending path based on current state.
        """
        if self.story_state["corruption"] >= 3:
            self.story_state["ending_path"] = "corrupt"
        elif self.story_state["trust"] <= -3:
            self.story_state["ending_path"] = "strict"
        else:
            self.story_state["ending_path"] = "neutral"
    
    def _check_milestones(self):
        """
        Check if any narrative milestones have been triggered.
        
        Returns:
            str or None: Narrative update if a milestone was triggered, None otherwise.
        """
        # Check corruption warning
        if self.story_state["corruption"] >= 2 and not self.milestones["corruption_warning"]:
            self.milestones["corruption_warning"] = True
            return "Your supervisor pulls you aside: \"There are rumors about agents taking bribes. I trust you're not involved?\""
        
        # Check trust warning
        if self.story_state["trust"] <= -2 and not self.milestones["trust_warning"]:
            self.milestones["trust_warning"] = True
            return "A coworker whispers: \"You're getting a reputation for being overly strict. People are talking.\""
        
        # Check for promotion milestone
        if self.story_state["day"] == 5 and not self.milestones["promotion_offered"]:
            self.milestones["promotion_offered"] = True
            return "The chief administrator calls you in: \"We're considering you for a promotion. Keep up the good work.\""
        
        # No milestone triggered
        return None
    
    def advance_day(self):
        """
        Advance to the next day in the game.
        
        Returns:
            str: Narrative update for the new day.
        """
        self.story_state["day"] += 1
        
        if self.story_state["day"] == 3:
            return "Day 3: New regulations have been implemented. All permits must now have valid seals."
        elif self.story_state["day"] == 7:
            return "Day 7: Border tensions are rising. Security has been tightened."
        else:
            return f"Day {self.story_state['day']}: Another day at the border checkpoint begins."
    
    def check_game_over(self):
        """
        Check if the game should end based on the current state.
        
        Returns:
            tuple: (is_game_over, ending_type, ending_message)
        """
        # Check corruption game over
        if self.story_state["corruption"] >= 5:
            return (True, "bad", "You're arrested on corruption charges. Your career is over.")
        
        # Check trust game over
        if self.story_state["trust"] <= -5:
            return (True, "bad", "You're fired for creating diplomatic incidents with your strict rejections.")
        
        # Check winning condition (Day 10 reached)
        if self.story_state["day"] >= 10:
            if self.story_state["ending_path"] == "corrupt":
                return (True, "corrupt", "You've enriched yourself through bribes, but at what cost to your integrity?")
            elif self.story_state["ending_path"] == "strict":
                return (True, "strict", "Your strict adherence to rules has made the border secure, but many innocent travelers suffered.")
            else:
                return (True, "good", "You've maintained a perfect balance of security and compassion. You're promoted to chief inspector.")
        
        # Game continues
        return (False, None, None)
    
    def get_state_summary(self):
        """
        Get a summary of the current story state.
        
        Returns:
            str: Summary of the story state.
        """
        corruption_level = "High" if self.story_state["corruption"] >= 3 else "Moderate" if self.story_state["corruption"] >= 1 else "Low"
        trust_level = "Low" if self.story_state["trust"] <= -3 else "Moderate" if self.story_state["trust"] <= -1 else "High"
        
        return f"Day: {self.story_state['day']} | Corruption: {corruption_level} | Trust: {trust_level} | Path: {self.story_state['ending_path'].title()}"
