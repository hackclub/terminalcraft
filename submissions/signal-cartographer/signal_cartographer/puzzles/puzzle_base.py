"""
Base puzzle framework for The Signal Cartographer
Provides abstract base classes and core functionality for all puzzle types
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import time
import random
import uuid


class PuzzleState(Enum):
    """Enumeration of puzzle states"""
    INACTIVE = "inactive"           # Puzzle not yet started
    ACTIVE = "active"              # Puzzle in progress
    COMPLETED = "completed"        # Puzzle successfully solved
    FAILED = "failed"              # Puzzle failed (too many attempts, etc.)
    PAUSED = "paused"              # Puzzle temporarily paused
    TIMED_OUT = "timed_out"        # Puzzle exceeded time limit
    ABANDONED = "abandoned"        # Player abandoned puzzle


class PuzzleDifficulty(Enum):
    """Enumeration of puzzle difficulty levels"""
    TRIVIAL = 1      # Tutorial level
    EASY = 2         # Beginner friendly
    NORMAL = 3       # Standard difficulty
    HARD = 4         # Challenging
    EXPERT = 5       # Very difficult
    NIGHTMARE = 6    # Extremely challenging


@dataclass
class PuzzleResult:
    """Result data from puzzle completion or attempt"""
    success: bool
    score: int
    time_taken: float
    attempts_used: int
    hints_used: int
    difficulty: PuzzleDifficulty
    completion_data: Dict[str, Any]
    message: str


@dataclass
class PuzzleHint:
    """Hint data for puzzles"""
    level: int              # Hint level (1=subtle, 5=obvious)
    text: str              # Hint text to display
    cost: int              # Score penalty for using hint
    unlocked: bool         # Whether hint is available


class BasePuzzle(ABC):
    """
    Abstract base class for all puzzles in The Signal Cartographer
    
    All puzzle implementations must inherit from this class and implement
    the required abstract methods.
    """
    
    def __init__(self, 
                 puzzle_id: str,
                 name: str,
                 description: str,
                 difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL,
                 max_attempts: int = 5,
                 time_limit: Optional[float] = None,
                 signal_data: Any = None):
        """
        Initialize base puzzle
        
        Args:
            puzzle_id: Unique identifier for the puzzle
            name: Display name of the puzzle
            description: Description of what the puzzle involves
            difficulty: Difficulty level
            max_attempts: Maximum number of attempts allowed
            time_limit: Time limit in seconds (None for no limit)
            signal_data: Associated signal data that generated this puzzle
        """
        self.puzzle_id = puzzle_id
        self.name = name
        self.description = description
        self.difficulty = difficulty
        self.max_attempts = max_attempts
        self.time_limit = time_limit
        self.signal_data = signal_data
        
        # State tracking
        self.state = PuzzleState.INACTIVE
        self.attempts_made = 0
        self.hints_used = 0
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.current_score = 0
        self.max_score = 1000  # Base score, can be overridden
        
        # Solution and progress
        self.solution: Any = None
        self.current_progress: Dict[str, Any] = {}
        self.player_input: List[str] = []
        
        # Hints system
        self.available_hints: List[PuzzleHint] = []
        self.hint_threshold = 3  # Attempts before hints become available
        
        # Initialize puzzle-specific data
        self._initialize_puzzle()
    
    @abstractmethod
    def _initialize_puzzle(self) -> None:
        """Initialize puzzle-specific data and generate solution"""
        pass
    
    @abstractmethod
    def validate_input(self, player_input: str) -> Tuple[bool, str]:
        """
        Validate player input against the solution
        
        Args:
            player_input: Input provided by the player
            
        Returns:
            Tuple of (is_correct, feedback_message)
        """
        pass
    
    @abstractmethod
    def get_current_display(self) -> List[str]:
        """
        Get the current puzzle display for the UI
        
        Returns:
            List of strings representing the current puzzle state
        """
        pass
    
    @abstractmethod
    def get_progress_display(self) -> List[str]:
        """
        Get progress indicators for the puzzle
        
        Returns:
            List of strings showing current progress
        """
        pass
    
    def start_puzzle(self) -> bool:
        """
        Start the puzzle
        
        Returns:
            True if puzzle started successfully, False otherwise
        """
        if self.state != PuzzleState.INACTIVE:
            return False
        
        self.state = PuzzleState.ACTIVE
        self.start_time = time.time()
        self.attempts_made = 0
        self.hints_used = 0
        self.current_score = self.max_score
        self._on_puzzle_start()
        return True
    
    def submit_answer(self, answer: str) -> PuzzleResult:
        """
        Submit an answer attempt
        
        Args:
            answer: Player's answer
            
        Returns:
            PuzzleResult with validation results
        """
        if self.state != PuzzleState.ACTIVE:
            return PuzzleResult(
                success=False,
                score=0,
                time_taken=0,
                attempts_used=self.attempts_made,
                hints_used=self.hints_used,
                difficulty=self.difficulty,
                completion_data={},
                message="Puzzle is not active"
            )
        
        # Check time limit
        if self.time_limit and self._get_elapsed_time() > self.time_limit:
            self.state = PuzzleState.TIMED_OUT
            return self._create_failure_result("Time limit exceeded")
        
        self.attempts_made += 1
        self.player_input.append(answer)
        
        is_correct, feedback = self.validate_input(answer)
        
        if is_correct:
            return self._complete_puzzle(True, feedback)
        else:
            # Check if max attempts reached
            if self.attempts_made >= self.max_attempts:
                self.state = PuzzleState.FAILED
                return self._create_failure_result("Maximum attempts exceeded")
            
            # Reduce score for incorrect attempt
            penalty = max(50, self.max_score // (self.max_attempts * 2))
            self.current_score = max(0, self.current_score - penalty)
            
            return PuzzleResult(
                success=False,
                score=self.current_score,
                time_taken=self._get_elapsed_time(),
                attempts_used=self.attempts_made,
                hints_used=self.hints_used,
                difficulty=self.difficulty,
                completion_data={"feedback": feedback},
                message=f"Incorrect. {feedback} ({self.max_attempts - self.attempts_made} attempts remaining)"
            )
    
    def get_hint(self, level: int = 1) -> Optional[PuzzleHint]:
        """
        Get a hint for the puzzle
        
        Args:
            level: Hint level requested (1-5)
            
        Returns:
            PuzzleHint if available, None otherwise
        """
        if self.attempts_made < self.hint_threshold:
            return None
        
        available_hints = [h for h in self.available_hints if h.level == level and not h.unlocked]
        if not available_hints:
            return None
        
        hint = available_hints[0]
        hint.unlocked = True
        self.hints_used += 1
        
        # Apply score penalty
        self.current_score = max(0, self.current_score - hint.cost)
        
        return hint
    
    def pause_puzzle(self) -> bool:
        """Pause the puzzle"""
        if self.state == PuzzleState.ACTIVE:
            self.state = PuzzleState.PAUSED
            return True
        return False
    
    def resume_puzzle(self) -> bool:
        """Resume a paused puzzle"""
        if self.state == PuzzleState.PAUSED:
            self.state = PuzzleState.ACTIVE
            return True
        return False
    
    def abandon_puzzle(self) -> PuzzleResult:
        """Abandon the current puzzle"""
        self.state = PuzzleState.ABANDONED
        return self._create_failure_result("Puzzle abandoned")
    
    def reset_puzzle(self) -> bool:
        """Reset the puzzle to initial state"""
        self.state = PuzzleState.INACTIVE
        self.attempts_made = 0
        self.hints_used = 0
        self.start_time = None
        self.end_time = None
        self.current_score = self.max_score
        self.player_input.clear()
        self.current_progress.clear()
        
        # Reset hints
        for hint in self.available_hints:
            hint.unlocked = False
        
        self._initialize_puzzle()
        return True
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get current puzzle status summary"""
        return {
            "puzzle_id": self.puzzle_id,
            "name": self.name,
            "state": self.state.value,
            "difficulty": self.difficulty.value,
            "attempts_made": self.attempts_made,
            "max_attempts": self.max_attempts,
            "hints_used": self.hints_used,
            "current_score": self.current_score,
            "max_score": self.max_score,
            "elapsed_time": self._get_elapsed_time() if self.start_time else 0,
            "time_limit": self.time_limit,
            "progress": self.current_progress.copy()
        }
    
    def _complete_puzzle(self, success: bool, message: str) -> PuzzleResult:
        """Complete the puzzle with given result"""
        self.state = PuzzleState.COMPLETED if success else PuzzleState.FAILED
        self.end_time = time.time()
        
        if success:
            # Bonus for completing quickly
            time_bonus = self._calculate_time_bonus()
            # Bonus for using fewer attempts
            attempt_bonus = self._calculate_attempt_bonus()
            
            final_score = self.current_score + time_bonus + attempt_bonus
        else:
            final_score = 0
        
        completion_data = {
            "solution": self.solution,
            "player_inputs": self.player_input.copy(),
            "progress": self.current_progress.copy()
        }
        
        result = PuzzleResult(
            success=success,
            score=final_score,
            time_taken=self._get_elapsed_time(),
            attempts_used=self.attempts_made,
            hints_used=self.hints_used,
            difficulty=self.difficulty,
            completion_data=completion_data,
            message=message
        )
        
        self._on_puzzle_complete(result)
        return result
    
    def _create_failure_result(self, message: str) -> PuzzleResult:
        """Create a failure result"""
        return self._complete_puzzle(False, message)
    
    def _get_elapsed_time(self) -> float:
        """Get elapsed time since puzzle start"""
        if not self.start_time:
            return 0.0
        end_time = self.end_time or time.time()
        return end_time - self.start_time
    
    def _calculate_time_bonus(self) -> int:
        """Calculate time-based bonus score"""
        if not self.time_limit:
            return 0
        
        elapsed = self._get_elapsed_time()
        remaining_ratio = max(0, (self.time_limit - elapsed) / self.time_limit)
        return int(remaining_ratio * 200)  # Up to 200 bonus points
    
    def _calculate_attempt_bonus(self) -> int:
        """Calculate attempt-based bonus score"""
        remaining_attempts = self.max_attempts - self.attempts_made
        return remaining_attempts * 50  # 50 points per unused attempt
    
    def _on_puzzle_start(self) -> None:
        """Hook for puzzle-specific start logic"""
        pass
    
    def _on_puzzle_complete(self, result: PuzzleResult) -> None:
        """Hook for puzzle-specific completion logic"""
        pass
    
    def add_hint(self, level: int, text: str, cost: int = 25) -> None:
        """Add a hint to the puzzle"""
        hint = PuzzleHint(
            level=level,
            text=text,
            cost=cost,
            unlocked=False
        )
        self.available_hints.append(hint)
    
    def get_available_hint_levels(self) -> List[int]:
        """Get list of available hint levels"""
        if self.attempts_made < self.hint_threshold:
            return []
        
        return sorted(set(h.level for h in self.available_hints if not h.unlocked))


class PuzzleTemplate:
    """Template class for generating similar puzzles with variations"""
    
    def __init__(self, name: str, base_difficulty: PuzzleDifficulty):
        self.name = name
        self.base_difficulty = base_difficulty
        self.variations: List[Dict[str, Any]] = []
    
    def add_variation(self, variation_data: Dict[str, Any]) -> None:
        """Add a puzzle variation"""
        self.variations.append(variation_data)
    
    def generate_puzzle(self, signal_data: Any = None) -> Optional[BasePuzzle]:
        """Generate a puzzle instance from this template"""
        if not self.variations:
            return None
        
        variation = random.choice(self.variations)
        # Implementation depends on specific puzzle type
        return None


# Utility functions for puzzle generation
def generate_puzzle_id() -> str:
    """Generate a unique puzzle ID"""
    return f"puzzle_{uuid.uuid4().hex[:8]}"


def calculate_difficulty_score(difficulty: PuzzleDifficulty, 
                             completion_time: float,
                             attempts_used: int,
                             hints_used: int) -> int:
    """Calculate final score based on difficulty and performance"""
    base_score = difficulty.value * 200
    
    # Time modifier (faster = better)
    time_modifier = max(0.5, 2.0 - (completion_time / 60.0))  # 1-2x multiplier
    
    # Attempt modifier (fewer attempts = better)
    attempt_modifier = max(0.3, 1.0 - (attempts_used - 1) * 0.15)
    
    # Hint modifier (fewer hints = better)
    hint_modifier = max(0.5, 1.0 - hints_used * 0.1)
    
    return int(base_score * time_modifier * attempt_modifier * hint_modifier) 