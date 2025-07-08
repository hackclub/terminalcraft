"""
Constellation Identification Puzzle for The Signal Cartographer
First concrete implementation of visual pattern matching system
"""

from typing import Any, Dict, List, Tuple, Optional
import random
import time

from ..puzzle_base import BasePuzzle, PuzzleState, PuzzleResult, PuzzleDifficulty, generate_puzzle_id
from .pattern_library import ConstellationLibrary, ConstellationData


class ConstellationIdentificationPuzzle(BasePuzzle):
    """
    Constellation identification puzzle that challenges players to identify
    star patterns and match them to known constellations
    """
    
    def __init__(self, 
                 difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL,
                 signal_data: Any = None,
                 puzzle_variant: str = "identification"):
        """
        Initialize constellation identification puzzle
        
        Args:
            difficulty: Puzzle difficulty level
            signal_data: Associated signal data
            puzzle_variant: Type of constellation puzzle (identification, completion, fragment)
        """
        
        self.constellation_library = ConstellationLibrary()
        self.puzzle_variant = puzzle_variant
        self.target_constellation: Optional[ConstellationData] = None
        self.display_constellation: Optional[ConstellationData] = None
        self.choices: List[str] = []
        self.noise_level = 0.0
        self.fragment_mode = False
        
        # Calculate difficulty parameters
        max_attempts = max(3, 7 - difficulty.value)
        time_limit = None
        if difficulty.value >= 4:  # Add time pressure for harder puzzles
            time_limit = 180 - (difficulty.value - 4) * 30  # 180, 150, 120 seconds
        
        super().__init__(
            puzzle_id=generate_puzzle_id(),
            name=f"Constellation {puzzle_variant.title()}",
            description=f"Identify the constellation pattern from the star field",
            difficulty=difficulty,
            max_attempts=max_attempts,
            time_limit=time_limit,
            signal_data=signal_data
        )
    
    def _initialize_puzzle(self) -> None:
        """Initialize the constellation puzzle with patterns and choices"""
        # Select target constellation based on difficulty
        difficulty_range = self._get_difficulty_range()
        self.target_constellation = self.constellation_library.get_random_constellation(difficulty_range)
        
        if not self.target_constellation:
            # Fallback to any constellation
            self.target_constellation = self.constellation_library.get_random_constellation((1, 5))
        
        # Create display version based on variant
        if self.puzzle_variant == "fragment":
            self.display_constellation = self.constellation_library.create_constellation_fragment(
                self.target_constellation.name, fragment_size=0.6
            )
            self.fragment_mode = True
        elif self.puzzle_variant == "noisy":
            self.display_constellation = self._add_noise_to_constellation(self.target_constellation)
        else:
            self.display_constellation = self.target_constellation
        
        # Generate multiple choice options
        self._generate_choices()
        
        # Set solution
        self.solution = self.target_constellation.name
        
        # Add appropriate hints
        self._generate_hints()
        
        # Calculate max score based on difficulty
        self.max_score = 500 + (self.difficulty.value - 1) * 250
    
    def _get_difficulty_range(self) -> Tuple[int, int]:
        """Get constellation difficulty range based on puzzle difficulty"""
        if self.difficulty == PuzzleDifficulty.TRIVIAL:
            return (1, 2)
        elif self.difficulty == PuzzleDifficulty.EASY:
            return (1, 3)
        elif self.difficulty == PuzzleDifficulty.NORMAL:
            return (2, 4)
        elif self.difficulty == PuzzleDifficulty.HARD:
            return (3, 5)
        else:  # EXPERT, NIGHTMARE
            return (4, 5)
    
    def _generate_choices(self):
        """Generate multiple choice options for constellation identification"""
        self.choices = [self.target_constellation.name]
        
        # Add incorrect options
        all_constellations = list(self.constellation_library.constellations.keys())
        all_constellations.remove(self.target_constellation.name)
        
        # Number of choices based on difficulty
        num_choices = min(6, 3 + self.difficulty.value)
        num_incorrect = num_choices - 1
        
        incorrect_choices = random.sample(all_constellations, min(num_incorrect, len(all_constellations)))
        self.choices.extend(incorrect_choices)
        
        # Shuffle the choices
        random.shuffle(self.choices)
        
        # Store choice mapping for validation
        self.choice_mapping = {str(i+1): choice for i, choice in enumerate(self.choices)}
    
    def _add_noise_to_constellation(self, constellation: ConstellationData, noise_level: float = None) -> ConstellationData:
        """Add noise/interference to constellation display"""
        if noise_level is None:
            noise_level = 0.1 + (self.difficulty.value - 1) * 0.05
        
        # Create noisy version of ASCII representation
        noisy_ascii = []
        for line in constellation.ascii_representation:
            noisy_line = ""
            for char in line:
                if char == ' ' and random.random() < noise_level:
                    noisy_line += random.choice(['.', ':', '~', '•'])
                elif char == '*' and random.random() < noise_level * 0.3:
                    noisy_line += random.choice(['○', '·', '+'])  # Dim the star
                else:
                    noisy_line += char
            noisy_ascii.append(noisy_line)
        
        # Create new constellation data with noise
        noisy_constellation = ConstellationData(
            name=f"{constellation.name}_noisy",
            stars=constellation.stars,
            connecting_lines=constellation.connecting_lines,
            ascii_representation=noisy_ascii,
            mythology=constellation.mythology,
            difficulty=constellation.difficulty + 1,
            brightness_levels=constellation.brightness_levels
        )
        
        self.noise_level = noise_level
        return noisy_constellation
    
    def _generate_hints(self):
        """Generate hints for the puzzle"""
        if not self.target_constellation:
            return
        
        # Hint 1: General description
        self.add_hint(1, f"This constellation is known as '{self.target_constellation.mythology}'", 25)
        
        # Hint 2: Difficulty level
        difficulty_desc = ["very simple", "simple", "moderate", "complex", "very complex"][self.target_constellation.difficulty - 1]
        self.add_hint(2, f"This is a {difficulty_desc} constellation pattern", 50)
        
        # Hint 3: Star count
        star_count = len(self.target_constellation.stars)
        self.add_hint(3, f"This constellation has {star_count} main stars", 75)
        
        # Hint 4: First letter (for harder puzzles)
        if self.difficulty.value >= 3:
            first_letter = self.target_constellation.name[0]
            self.add_hint(4, f"The constellation name starts with '{first_letter}'", 100)
        
        # Hint 5: Direct answer (major penalty)
        if self.difficulty.value >= 4:
            self.add_hint(5, f"The answer is {self.target_constellation.name}", 200)
    
    def validate_input(self, player_input: str) -> Tuple[bool, str]:
        """Validate player's constellation identification"""
        # Clean input
        player_input = player_input.strip()
        
        # Check if input is a number (multiple choice)
        if player_input.isdigit():
            choice_num = player_input
            if choice_num in self.choice_mapping:
                selected_constellation = self.choice_mapping[choice_num]
                if selected_constellation.lower() == self.solution.lower():
                    return True, f"Correct! You identified {self.solution}!"
                else:
                    return False, f"Incorrect. {selected_constellation} is not the right constellation."
            else:
                return False, f"Invalid choice number. Please select 1-{len(self.choices)}."
        
        # Check direct name input
        if player_input.lower() == self.solution.lower():
            return True, f"Correct! You identified {self.solution}!"
        
        # Check partial matches
        if player_input.lower() in self.solution.lower():
            return False, f"Close! '{player_input}' is part of the name, but not complete."
        
        return False, f"'{player_input}' is not correct. Try studying the star pattern more carefully."
    
    def get_current_display(self) -> List[str]:
        """Get the current puzzle display"""
        lines = []
        
        # Puzzle header
        lines.append(f"[bold cyan]🌟 CONSTELLATION IDENTIFICATION PUZZLE[/bold cyan]")
        lines.append("=" * 60)
        lines.append("")
        
        # Difficulty and variant info
        variant_desc = self.puzzle_variant.replace('_', ' ').title()
        lines.append(f"[yellow]Variant:[/yellow] {variant_desc}")
        lines.append(f"[yellow]Difficulty:[/yellow] {self.difficulty.name}")
        
        if self.fragment_mode:
            lines.append("[yellow]Mode:[/yellow] Fragment Analysis - partial constellation view")
        if self.noise_level > 0:
            lines.append(f"[yellow]Interference:[/yellow] {self.noise_level:.1%} signal noise")
        
        lines.append("")
        
        # Display the constellation
        lines.append("[cyan]═══ STAR FIELD ANALYSIS ═══[/cyan]")
        if self.display_constellation:
            lines.extend(self.display_constellation.ascii_representation)
        lines.append("")
        
        # Display choices
        lines.append("[cyan]═══ CONSTELLATION OPTIONS ═══[/cyan]")
        for i, choice in enumerate(self.choices, 1):
            lines.append(f"[white]{i}.[/white] {choice}")
        lines.append("")
        
        # Instructions
        lines.append("[green]Instructions:[/green]")
        lines.append("• Enter the number (1-{}) of the correct constellation".format(len(self.choices)))
        lines.append("• Or type the constellation name directly")
        lines.append("• Use [yellow]HINT[/yellow] command if you need help")
        
        return lines
    
    def get_progress_display(self) -> List[str]:
        """Get progress indicators for the puzzle"""
        lines = []
        
        lines.append("[cyan]═══ PUZZLE PROGRESS ═══[/cyan]")
        lines.append(f"[yellow]Attempts:[/yellow] {self.attempts_made}/{self.max_attempts}")
        lines.append(f"[yellow]Current Score:[/yellow] {self.current_score}/{self.max_score}")
        
        if self.time_limit:
            elapsed = self._get_elapsed_time()
            remaining = max(0, self.time_limit - elapsed)
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            lines.append(f"[yellow]Time Remaining:[/yellow] {minutes:02d}:{seconds:02d}")
        
        if self.hints_used > 0:
            lines.append(f"[yellow]Hints Used:[/yellow] {self.hints_used}")
        
        # Show available hint levels
        available_hints = self.get_available_hint_levels()
        if available_hints:
            hint_str = ", ".join(str(level) for level in available_hints)
            lines.append(f"[yellow]Available Hints:[/yellow] Level {hint_str}")
        
        return lines
    
    def _on_puzzle_start(self) -> None:
        """Called when puzzle starts"""
        self.current_progress['start_time'] = time.time()
        self.current_progress['constellation_displayed'] = self.display_constellation.name if self.display_constellation else None
        self.current_progress['choices_generated'] = len(self.choices)
    
    def _on_puzzle_complete(self, result: PuzzleResult) -> None:
        """Called when puzzle completes"""
        self.current_progress['completion_time'] = time.time()
        self.current_progress['final_score'] = result.score
        self.current_progress['identification_successful'] = result.success
        
        # Additional completion data
        if result.success:
            self.current_progress['correct_answer'] = self.solution
            self.current_progress['player_method'] = "choice_selection" if hasattr(self, 'choice_mapping') else "direct_input"


class ConstellationCompletionPuzzle(ConstellationIdentificationPuzzle):
    """
    Variant puzzle where players complete a partial constellation pattern
    """
    
    def __init__(self, difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL, signal_data: Any = None):
        super().__init__(difficulty, signal_data, "completion")
    
    def _initialize_puzzle(self) -> None:
        """Initialize completion puzzle with missing stars"""
        super()._initialize_puzzle()
        
        # Create version with missing stars
        if self.target_constellation:
            self.display_constellation = self._create_incomplete_constellation(self.target_constellation)
        
        # Update description and scoring
        self.description = "Complete the constellation by identifying missing star positions"
        self.max_score = 600 + (self.difficulty.value - 1) * 300  # Harder than identification
    
    def _create_incomplete_constellation(self, constellation: ConstellationData) -> ConstellationData:
        """Create constellation with some stars missing"""
        # Remove 20-40% of stars randomly
        removal_rate = 0.2 + (self.difficulty.value - 1) * 0.05
        stars_to_keep = max(3, int(len(constellation.stars) * (1 - removal_rate)))
        
        kept_indices = random.sample(range(len(constellation.stars)), stars_to_keep)
        incomplete_stars = [constellation.stars[i] for i in kept_indices]
        
        # Update ASCII representation
        incomplete_ascii = self._render_incomplete_ascii(constellation, kept_indices)
        
        return ConstellationData(
            name=f"{constellation.name}_incomplete",
            stars=incomplete_stars,
            connecting_lines=[],  # No lines for incomplete version
            ascii_representation=incomplete_ascii,
            mythology=constellation.mythology,
            difficulty=constellation.difficulty + 1,
            brightness_levels={i: constellation.brightness_levels.get(kept_indices[i], 3) 
                             for i in range(len(incomplete_stars))}
        )
    
    def _render_incomplete_ascii(self, original: ConstellationData, kept_indices: List[int]) -> List[str]:
        """Render incomplete constellation ASCII"""
        # Start with original ASCII
        lines = [list(line) for line in original.ascii_representation]
        
        # Remove stars that weren't kept
        for i, star_pos in enumerate(original.stars):
            if i not in kept_indices:
                x, y = star_pos
                if 0 <= y < len(lines) and 0 <= x < len(lines[y]):
                    lines[y][x] = '?'  # Mark missing star position
        
        return [''.join(line) for line in lines]


class ConstellationFragmentPuzzle(ConstellationIdentificationPuzzle):
    """
    Variant puzzle showing only a fragment of a constellation
    """
    
    def __init__(self, difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL, signal_data: Any = None):
        super().__init__(difficulty, signal_data, "fragment")
        self.fragment_mode = True 