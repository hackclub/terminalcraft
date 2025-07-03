"""
Pattern Fragment Puzzle for The Signal Cartographer
Players identify complete patterns from partial fragments
"""

from typing import Any, Dict, List, Tuple, Optional
import random
import time

from ..puzzle_base import BasePuzzle, PuzzleResult, PuzzleDifficulty, generate_puzzle_id
from .pattern_library import PatternLibrary, PatternData
from .pattern_matcher import PatternMatcher


class PatternFragmentPuzzle(BasePuzzle):
    """
    Pattern fragment puzzle where players identify complete patterns
    from partial fragments or corrupted versions
    """
    
    def __init__(self, 
                 difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL,
                 signal_data: Any = None,
                 fragment_type: str = "partial"):
        """
        Initialize pattern fragment puzzle
        
        Args:
            difficulty: Puzzle difficulty level
            signal_data: Associated signal data
            fragment_type: Type of fragment (partial, corrupted, rotated, noisy)
        """
        
        self.pattern_library = PatternLibrary()
        self.pattern_matcher = PatternMatcher()
        self.fragment_type = fragment_type
        self.target_pattern: Optional[PatternData] = None
        self.fragment_pattern: List[str] = []
        self.choices: List[str] = []
        self.fragment_percentage = 0.0
        
        # Calculate difficulty parameters
        max_attempts = max(3, 8 - difficulty.value)
        time_limit = None
        if difficulty.value >= 3:
            time_limit = 240 - (difficulty.value - 3) * 40  # 240, 200, 160, 120 seconds
        
        super().__init__(
            puzzle_id=generate_puzzle_id(),
            name=f"Pattern Fragment Analysis",
            description=f"Identify the complete pattern from {fragment_type} fragment",
            difficulty=difficulty,
            max_attempts=max_attempts,
            time_limit=time_limit,
            signal_data=signal_data
        )
    
    def _initialize_puzzle(self) -> None:
        """Initialize the pattern fragment puzzle"""
        # Select target pattern based on difficulty
        difficulty_range = self._get_difficulty_range()
        available_patterns = []
        
        for pattern in self.pattern_library.patterns.values():
            if difficulty_range[0] <= pattern.difficulty <= difficulty_range[1]:
                available_patterns.append(pattern)
        
        if not available_patterns:
            # Fallback to any pattern
            available_patterns = list(self.pattern_library.patterns.values())
        
        self.target_pattern = random.choice(available_patterns)
        
        # Create fragment based on type
        self.fragment_pattern = self._create_fragment()
        
        # Generate multiple choice options
        self._generate_choices()
        
        # Set solution
        self.solution = self.target_pattern.name
        
        # Add hints
        self._generate_hints()
        
        # Calculate max score
        self.max_score = 400 + (self.difficulty.value - 1) * 200
    
    def _get_difficulty_range(self) -> Tuple[int, int]:
        """Get pattern difficulty range based on puzzle difficulty"""
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
    
    def _create_fragment(self) -> List[str]:
        """Create a fragment of the target pattern based on fragment type"""
        if not self.target_pattern:
            return []
        
        original = self.target_pattern.ascii_art.copy()
        
        if self.fragment_type == "partial":
            return self._create_partial_fragment(original)
        elif self.fragment_type == "corrupted":
            return self._create_corrupted_fragment(original)
        elif self.fragment_type == "rotated":
            return self._create_rotated_fragment(original)
        elif self.fragment_type == "noisy":
            return self._create_noisy_fragment(original)
        else:
            return self._create_partial_fragment(original)  # Default
    
    def _create_partial_fragment(self, pattern: List[str]) -> List[str]:
        """Create a partial fragment by removing sections"""
        fragment = pattern.copy()
        height = len(fragment)
        width = max(len(line) for line in fragment) if fragment else 0
        
        # Calculate how much to remove based on difficulty
        removal_rate = 0.3 + (self.difficulty.value - 1) * 0.1  # 30% to 70%
        self.fragment_percentage = 1.0 - removal_rate
        
        # Choose removal strategy
        strategy = random.choice(["top_bottom", "left_right", "center", "random_blocks"])
        
        if strategy == "top_bottom":
            # Remove top or bottom portion
            if random.choice([True, False]):
                # Remove top
                keep_lines = int(height * (1 - removal_rate))
                fragment = fragment[-keep_lines:]
            else:
                # Remove bottom
                keep_lines = int(height * (1 - removal_rate))
                fragment = fragment[:keep_lines]
        
        elif strategy == "left_right":
            # Remove left or right portion
            if random.choice([True, False]):
                # Remove left
                keep_chars = int(width * (1 - removal_rate))
                fragment = [line[-keep_chars:] if len(line) >= keep_chars else line for line in fragment]
            else:
                # Remove right
                keep_chars = int(width * (1 - removal_rate))
                fragment = [line[:keep_chars] for line in fragment]
        
        elif strategy == "center":
            # Remove center portion
            remove_height = int(height * removal_rate)
            remove_width = int(width * removal_rate)
            start_y = (height - remove_height) // 2
            start_x = (width - remove_width) // 2
            
            for i in range(len(fragment)):
                if start_y <= i < start_y + remove_height:
                    line = list(fragment[i].ljust(width))
                    for j in range(start_x, min(start_x + remove_width, len(line))):
                        line[j] = ' '
                    fragment[i] = ''.join(line).rstrip()
        
        elif strategy == "random_blocks":
            # Remove random blocks
            for _ in range(int(removal_rate * 10)):  # Number of blocks to remove
                if fragment and width > 0:
                    block_height = random.randint(1, max(1, height // 4))
                    block_width = random.randint(1, max(1, width // 4))
                    start_y = random.randint(0, max(0, height - block_height))
                    start_x = random.randint(0, max(0, width - block_width))
                    
                    for i in range(start_y, min(start_y + block_height, len(fragment))):
                        line = list(fragment[i].ljust(width))
                        for j in range(start_x, min(start_x + block_width, len(line))):
                            line[j] = ' '
                        fragment[i] = ''.join(line).rstrip()
        
        return fragment
    
    def _create_corrupted_fragment(self, pattern: List[str]) -> List[str]:
        """Create corrupted fragment with character substitutions"""
        fragment = pattern.copy()
        corruption_rate = 0.1 + (self.difficulty.value - 1) * 0.05  # 10% to 30%
        
        corrupted = []
        for line in fragment:
            corrupted_line = ""
            for char in line:
                if char != ' ' and random.random() < corruption_rate:
                    # Replace with similar looking character
                    if char == '*':
                        corrupted_line += random.choice(['○', '●', '+', '•'])
                    elif char in '|-':
                        corrupted_line += random.choice(['~', '=', '_'])
                    else:
                        corrupted_line += random.choice(['?', '#', '@'])
                else:
                    corrupted_line += char
            corrupted.append(corrupted_line)
        
        self.fragment_percentage = 1.0 - corruption_rate
        return corrupted
    
    def _create_rotated_fragment(self, pattern: List[str]) -> List[str]:
        """Create rotated version of the pattern"""
        rotation = random.choice([90, 180, 270])
        self.current_progress['rotation_applied'] = rotation
        
        if rotation == 90:
            return self._rotate_90(pattern)
        elif rotation == 180:
            return [line[::-1] for line in reversed(pattern)]
        elif rotation == 270:
            rotated_90 = self._rotate_90(pattern)
            return [line[::-1] for line in reversed(rotated_90)]
        
        return pattern
    
    def _rotate_90(self, pattern: List[str]) -> List[str]:
        """Rotate pattern 90 degrees clockwise"""
        if not pattern:
            return []
        
        height = len(pattern)
        width = max(len(line) for line in pattern)
        
        # Pad all lines to same width
        padded = [line.ljust(width) for line in pattern]
        
        rotated = []
        for col in range(width):
            new_line = ""
            for row in range(height - 1, -1, -1):
                new_line += padded[row][col]
            rotated.append(new_line.rstrip())
        
        return rotated
    
    def _create_noisy_fragment(self, pattern: List[str]) -> List[str]:
        """Create noisy fragment with random interference"""
        fragment = pattern.copy()
        noise_rate = 0.05 + (self.difficulty.value - 1) * 0.03  # 5% to 17%
        
        noisy = []
        for line in fragment:
            noisy_line = ""
            for char in line:
                if char == ' ' and random.random() < noise_rate:
                    noisy_line += random.choice(['.', ':', '~', '•'])
                elif char != ' ' and random.random() < noise_rate * 0.5:
                    noisy_line += ' '  # Remove character (create gaps)
                else:
                    noisy_line += char
            noisy.append(noisy_line)
        
        self.fragment_percentage = 1.0 - noise_rate
        return noisy
    
    def _generate_choices(self):
        """Generate multiple choice options"""
        self.choices = [self.target_pattern.name]
        
        # Add incorrect options from same category if possible
        similar_patterns = []
        target_tags = set(self.target_pattern.tags)
        
        for pattern_name, pattern_data in self.pattern_library.patterns.items():
            if pattern_name != self.target_pattern.name:
                # Check if pattern has any common tags
                common_tags = target_tags.intersection(set(pattern_data.tags))
                if common_tags:
                    similar_patterns.append(pattern_name)
        
        # Add some similar patterns and some random ones
        num_choices = min(6, 4 + self.difficulty.value)
        num_incorrect = num_choices - 1
        
        similar_count = min(len(similar_patterns), num_incorrect // 2)
        incorrect_choices = random.sample(similar_patterns, similar_count) if similar_patterns else []
        
        # Fill remaining with random patterns
        remaining_patterns = [name for name in self.pattern_library.patterns.keys() 
                            if name not in incorrect_choices and name != self.target_pattern.name]
        remaining_count = num_incorrect - len(incorrect_choices)
        
        if remaining_patterns and remaining_count > 0:
            incorrect_choices.extend(random.sample(remaining_patterns, 
                                                 min(remaining_count, len(remaining_patterns))))
        
        self.choices.extend(incorrect_choices)
        random.shuffle(self.choices)
        
        # Store choice mapping
        self.choice_mapping = {str(i+1): choice for i, choice in enumerate(self.choices)}
    
    def _generate_hints(self):
        """Generate hints for the puzzle"""
        if not self.target_pattern:
            return
        
        # Hint 1: Fragment type
        self.add_hint(1, f"This is a {self.fragment_type} fragment showing {self.fragment_percentage:.0%} of the original", 30)
        
        # Hint 2: Pattern category
        if self.target_pattern.tags:
            main_tag = self.target_pattern.tags[0]
            self.add_hint(2, f"This pattern belongs to the '{main_tag}' category", 50)
        
        # Hint 3: Pattern difficulty
        difficulty_desc = ["very simple", "simple", "moderate", "complex", "very complex"][self.target_pattern.difficulty - 1]
        self.add_hint(3, f"The complete pattern is {difficulty_desc} in structure", 75)
        
        # Hint 4: Pattern description
        if self.difficulty.value >= 3:
            self.add_hint(4, f"Description: {self.target_pattern.description}", 100)
        
        # Hint 5: Direct answer
        if self.difficulty.value >= 4:
            self.add_hint(5, f"The complete pattern is: {self.target_pattern.name}", 150)
    
    def validate_input(self, player_input: str) -> Tuple[bool, str]:
        """Validate player's pattern identification"""
        player_input = player_input.strip()
        
        # Check multiple choice number
        if player_input.isdigit():
            choice_num = player_input
            if choice_num in self.choice_mapping:
                selected_pattern = self.choice_mapping[choice_num]
                if selected_pattern.lower() == self.solution.lower():
                    return True, f"Correct! The complete pattern is {self.solution}!"
                else:
                    return False, f"Incorrect. {selected_pattern} is not the original pattern."
            else:
                return False, f"Invalid choice. Please select 1-{len(self.choices)}."
        
        # Check direct name input
        if player_input.lower() == self.solution.lower():
            return True, f"Excellent! You identified {self.solution} from the fragment!"
        
        # Check partial matches
        if player_input.lower() in self.solution.lower():
            return False, f"Close! '{player_input}' is part of the pattern name."
        
        return False, f"'{player_input}' is not correct. Study the fragment more carefully."
    
    def get_current_display(self) -> List[str]:
        """Get the current puzzle display"""
        lines = []
        
        # Header
        lines.append(f"[bold cyan]🧩 PATTERN FRAGMENT ANALYSIS[/bold cyan]")
        lines.append("=" * 60)
        lines.append("")
        
        # Fragment info
        fragment_desc = self.fragment_type.replace('_', ' ').title()
        lines.append(f"[yellow]Fragment Type:[/yellow] {fragment_desc}")
        lines.append(f"[yellow]Difficulty:[/yellow] {self.difficulty.name}")
        
        if hasattr(self, 'fragment_percentage'):
            lines.append(f"[yellow]Fragment Completeness:[/yellow] {self.fragment_percentage:.0%}")
        
        rotation = self.current_progress.get('rotation_applied')
        if rotation:
            lines.append(f"[yellow]Rotation Applied:[/yellow] {rotation}°")
        
        lines.append("")
        
        # Display fragment
        lines.append("[cyan]═══ PATTERN FRAGMENT ═══[/cyan]")
        if self.fragment_pattern:
            lines.extend(self.fragment_pattern)
        lines.append("")
        
        # Display choices
        lines.append("[cyan]═══ PATTERN OPTIONS ═══[/cyan]")
        for i, choice in enumerate(self.choices, 1):
            lines.append(f"[white]{i}.[/white] {choice}")
        lines.append("")
        
        # Instructions
        lines.append("[green]Instructions:[/green]")
        lines.append("• Analyze the fragment to identify the complete pattern")
        lines.append(f"• Enter the number (1-{len(self.choices)}) of the correct pattern")
        lines.append("• Or type the pattern name directly")
        lines.append("• Use [yellow]HINT[/yellow] command for assistance")
        
        return lines
    
    def get_progress_display(self) -> List[str]:
        """Get progress indicators"""
        lines = []
        
        lines.append("[cyan]═══ ANALYSIS PROGRESS ═══[/cyan]")
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
        
        return lines
    
    def _on_puzzle_start(self) -> None:
        """Called when puzzle starts"""
        self.current_progress['fragment_type'] = self.fragment_type
        self.current_progress['target_pattern'] = self.target_pattern.name if self.target_pattern else None
        self.current_progress['start_time'] = time.time()
    
    def _on_puzzle_complete(self, result: PuzzleResult) -> None:
        """Called when puzzle completes"""
        self.current_progress['completion_time'] = time.time()
        self.current_progress['final_score'] = result.score
        self.current_progress['fragment_solved'] = result.success 