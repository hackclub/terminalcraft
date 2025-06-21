"""
Noise Filter Puzzle for The Signal Cartographer
Players filter noise and interference to reveal underlying patterns
"""

from typing import Any, Dict, List, Tuple, Optional
import random
import time

from ..puzzle_base import BasePuzzle, PuzzleResult, PuzzleDifficulty, generate_puzzle_id
from .pattern_library import PatternLibrary, PatternData
from .pattern_matcher import PatternMatcher


class NoiseFilterPuzzle(BasePuzzle):
    """
    Noise filtering puzzle where players identify clean patterns
    from heavily corrupted/noisy versions
    """
    
    def __init__(self, 
                 difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL,
                 signal_data: Any = None,
                 noise_type: str = "interference"):
        """
        Initialize noise filter puzzle
        
        Args:
            difficulty: Puzzle difficulty level
            signal_data: Associated signal data
            noise_type: Type of noise (interference, static, corruption, scrambled)
        """
        
        self.pattern_library = PatternLibrary()
        self.pattern_matcher = PatternMatcher()
        self.noise_type = noise_type
        self.target_pattern: Optional[PatternData] = None
        self.noisy_pattern: List[str] = []
        self.choices: List[str] = []
        self.noise_level = 0.0
        self.filter_stages = []
        
        # Calculate difficulty parameters
        max_attempts = max(4, 8 - difficulty.value)  # More attempts due to complexity
        time_limit = None
        if difficulty.value >= 3:
            time_limit = 300 - (difficulty.value - 3) * 45  # 300, 255, 210, 165 seconds
        
        super().__init__(
            puzzle_id=generate_puzzle_id(),
            name=f"Noise Filter Analysis",
            description=f"Filter {noise_type} to reveal the underlying pattern",
            difficulty=difficulty,
            max_attempts=max_attempts,
            time_limit=time_limit,
            signal_data=signal_data
        )
    
    def _initialize_puzzle(self) -> None:
        """Initialize the noise filter puzzle"""
        # Select target pattern based on difficulty
        difficulty_range = self._get_difficulty_range()
        available_patterns = []
        
        for pattern in self.pattern_library.patterns.values():
            if difficulty_range[0] <= pattern.difficulty <= difficulty_range[1]:
                available_patterns.append(pattern)
        
        if not available_patterns:
            available_patterns = list(self.pattern_library.patterns.values())
        
        self.target_pattern = random.choice(available_patterns)
        
        # Calculate noise level based on difficulty
        self.noise_level = 0.15 + (self.difficulty.value - 1) * 0.1  # 15% to 55%
        
        # Create noisy version
        self.noisy_pattern = self._create_noisy_pattern()
        
        # Generate filter stages for progressive revelation
        self._generate_filter_stages()
        
        # Generate multiple choice options
        self._generate_choices()
        
        # Set solution
        self.solution = self.target_pattern.name
        
        # Add hints
        self._generate_hints()
        
        # Calculate max score (higher for noise filtering complexity)
        self.max_score = 600 + (self.difficulty.value - 1) * 300
    
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
    
    def _create_noisy_pattern(self) -> List[str]:
        """Create noisy version of target pattern based on noise type"""
        if not self.target_pattern:
            return []
        
        original = self.target_pattern.ascii_art.copy()
        
        if self.noise_type == "interference":
            return self._add_interference_noise(original)
        elif self.noise_type == "static":
            return self._add_static_noise(original)
        elif self.noise_type == "corruption":
            return self._add_corruption_noise(original)
        elif self.noise_type == "scrambled":
            return self._add_scrambling_noise(original)
        else:
            return self._add_interference_noise(original)  # Default
    
    def _add_interference_noise(self, pattern: List[str]) -> List[str]:
        """Add interference-style noise with random characters"""
        noisy = []
        interference_chars = ['.', ':', '~', '•', '○', '+', '-', '|', '/', '\\']
        
        for line in pattern:
            noisy_line = ""
            for char in line:
                if char == ' ' and random.random() < self.noise_level:
                    # Add interference in empty spaces
                    noisy_line += random.choice(interference_chars)
                elif char != ' ' and random.random() < self.noise_level * 0.4:
                    # Occasionally corrupt pattern characters
                    noisy_line += random.choice(interference_chars)
                else:
                    noisy_line += char
            noisy.append(noisy_line)
        
        return noisy
    
    def _add_static_noise(self, pattern: List[str]) -> List[str]:
        """Add static-style noise with dense random characters"""
        noisy = []
        static_chars = ['.', ':', '·', '•', '∘', '○']
        
        for line in pattern:
            noisy_line = ""
            for char in line:
                if random.random() < self.noise_level:
                    # Replace with static
                    noisy_line += random.choice(static_chars)
                else:
                    noisy_line += char
            noisy.append(noisy_line)
        
        return noisy
    
    def _add_corruption_noise(self, pattern: List[str]) -> List[str]:
        """Add corruption noise with character substitutions"""
        noisy = []
        corruption_map = {
            '*': ['○', '●', '+', '•', '◦'],
            '|': [':', '!', '│', '┃', '¦'],
            '-': ['~', '=', '_', '−', '─'],
            '+': ['*', 'x', '×', '┼', '╋'],
            '#': ['■', '▓', '█', '□', '▪']
        }
        
        for line in pattern:
            noisy_line = ""
            for char in line:
                if char in corruption_map and random.random() < self.noise_level:
                    noisy_line += random.choice(corruption_map[char])
                elif char != ' ' and random.random() < self.noise_level * 0.3:
                    # Random corruption
                    noisy_line += random.choice(['?', '#', '@', '%', '&'])
                else:
                    noisy_line += char
            noisy.append(noisy_line)
        
        return noisy
    
    def _add_scrambling_noise(self, pattern: List[str]) -> List[str]:
        """Add scrambling noise by shifting and distorting pattern"""
        noisy = []
        
        for i, line in enumerate(pattern):
            noisy_line = line
            
            # Random horizontal shifts
            if random.random() < self.noise_level:
                shift = random.randint(-2, 2)
                if shift > 0:
                    noisy_line = ' ' * shift + line
                elif shift < 0:
                    noisy_line = line[abs(shift):] if abs(shift) < len(line) else ''
            
            # Character displacement
            if len(noisy_line) > 3:
                chars = list(noisy_line)
                for _ in range(int(len(chars) * self.noise_level)):
                    if len(chars) >= 2:
                        pos1, pos2 = random.sample(range(len(chars)), 2)
                        chars[pos1], chars[pos2] = chars[pos2], chars[pos1]
                noisy_line = ''.join(chars)
            
            noisy.append(noisy_line)
        
        return noisy
    
    def _generate_filter_stages(self):
        """Generate progressive filter stages for hints"""
        if not self.target_pattern:
            return
        
        # Create increasingly clean versions
        original = self.target_pattern.ascii_art.copy()
        
        # Stage 1: Heavy noise (current)
        stage1 = self.noisy_pattern.copy()
        
        # Stage 2: Medium noise (50% less noise)
        stage2 = self._create_filtered_version(original, self.noise_level * 0.5)
        
        # Stage 3: Light noise (25% noise)  
        stage3 = self._create_filtered_version(original, self.noise_level * 0.25)
        
        # Stage 4: Clean pattern
        stage4 = original.copy()
        
        self.filter_stages = [
            ("Heavy Interference", stage1),
            ("Medium Filtering", stage2), 
            ("Light Filtering", stage3),
            ("Clean Signal", stage4)
        ]
    
    def _create_filtered_version(self, pattern: List[str], noise_level: float) -> List[str]:
        """Create a version with specified noise level"""
        temp_noise_level = self.noise_level
        self.noise_level = noise_level
        
        if self.noise_type == "interference":
            result = self._add_interference_noise(pattern)
        elif self.noise_type == "static":
            result = self._add_static_noise(pattern)
        elif self.noise_type == "corruption":
            result = self._add_corruption_noise(pattern)
        elif self.noise_type == "scrambled":
            result = self._add_scrambling_noise(pattern)
        else:
            result = self._add_interference_noise(pattern)
        
        self.noise_level = temp_noise_level
        return result
    
    def _generate_choices(self):
        """Generate multiple choice options"""
        self.choices = [self.target_pattern.name]
        
        # Add patterns from same categories
        similar_patterns = []
        target_tags = set(self.target_pattern.tags)
        
        for pattern_name, pattern_data in self.pattern_library.patterns.items():
            if pattern_name != self.target_pattern.name:
                common_tags = target_tags.intersection(set(pattern_data.tags))
                if common_tags:
                    similar_patterns.append(pattern_name)
        
        # Add choices
        num_choices = min(6, 4 + self.difficulty.value)
        num_incorrect = num_choices - 1
        
        # Prefer similar patterns
        if similar_patterns:
            similar_count = min(len(similar_patterns), num_incorrect)
            incorrect_choices = random.sample(similar_patterns, similar_count)
        else:
            incorrect_choices = []
        
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
        
        # Hint 1: Noise type and level
        self.add_hint(1, f"Filtering {self.noise_type} at {self.noise_level:.0%} interference level", 40)
        
        # Hint 2: Pattern category
        if self.target_pattern.tags:
            main_tag = self.target_pattern.tags[0]
            self.add_hint(2, f"The clean pattern belongs to '{main_tag}' category", 70)
        
        # Hint 3: Show medium filtered version
        if len(self.filter_stages) >= 2:
            self.add_hint(3, "Revealing medium-filtered version", 100)
        
        # Hint 4: Show light filtered version
        if len(self.filter_stages) >= 3:
            self.add_hint(4, "Revealing light-filtered version", 140)
        
        # Hint 5: Show clean pattern
        if len(self.filter_stages) >= 4:
            self.add_hint(5, "Revealing clean pattern", 200)
    
    def get_hint_display(self, hint_level: int) -> List[str]:
        """Get hint display with filtered pattern views"""
        hint_lines = super().get_hint_display(hint_level)
        
        # Add filtered pattern view for hints 3-5
        if hint_level >= 3 and hint_level <= 5:
            stage_index = hint_level - 2  # Map to filter stages
            if stage_index < len(self.filter_stages):
                stage_name, stage_pattern = self.filter_stages[stage_index]
                hint_lines.extend([
                    "",
                    f"[cyan]═══ {stage_name.upper()} ═══[/cyan]"
                ])
                hint_lines.extend(stage_pattern)
        
        return hint_lines
    
    def validate_input(self, player_input: str) -> Tuple[bool, str]:
        """Validate player's pattern identification"""
        player_input = player_input.strip()
        
        # Check multiple choice number
        if player_input.isdigit():
            choice_num = player_input
            if choice_num in self.choice_mapping:
                selected_pattern = self.choice_mapping[choice_num]
                if selected_pattern.lower() == self.solution.lower():
                    return True, f"Excellent! You filtered the noise to reveal {self.solution}!"
                else:
                    return False, f"Incorrect. {selected_pattern} is not the clean pattern."
            else:
                return False, f"Invalid choice. Please select 1-{len(self.choices)}."
        
        # Check direct name input
        if player_input.lower() == self.solution.lower():
            return True, f"Perfect! You successfully filtered the noise to identify {self.solution}!"
        
        # Check partial matches
        if player_input.lower() in self.solution.lower():
            return False, f"Close! '{player_input}' is part of the pattern name."
        
        return False, f"'{player_input}' is not correct. Try applying different filters to see the pattern more clearly."
    
    def get_current_display(self) -> List[str]:
        """Get the current puzzle display"""
        lines = []
        
        # Header
        lines.append(f"[bold cyan]🔧 NOISE FILTER ANALYSIS[/bold cyan]")
        lines.append("=" * 60)
        lines.append("")
        
        # Noise info
        noise_desc = self.noise_type.replace('_', ' ').title()
        lines.append(f"[yellow]Noise Type:[/yellow] {noise_desc}")
        lines.append(f"[yellow]Interference Level:[/yellow] {self.noise_level:.0%}")
        lines.append(f"[yellow]Difficulty:[/yellow] {self.difficulty.name}")
        lines.append("")
        
        # Display noisy pattern
        lines.append("[cyan]═══ CORRUPTED SIGNAL PATTERN ═══[/cyan]")
        if self.noisy_pattern:
            lines.extend(self.noisy_pattern)
        lines.append("")
        
        # Pattern analysis
        lines.append("[yellow]Pattern Analysis:[/yellow]")
        lines.append("• Signal heavily corrupted by interference")
        lines.append("• Apply noise filtering to reveal underlying pattern")
        lines.append("• Use hints to access progressive filter stages")
        lines.append("")
        
        # Display choices
        lines.append("[cyan]═══ CLEAN PATTERN OPTIONS ═══[/cyan]")
        for i, choice in enumerate(self.choices, 1):
            lines.append(f"[white]{i}.[/white] {choice}")
        lines.append("")
        
        # Instructions
        lines.append("[green]Instructions:[/green]")
        lines.append("• Analyze the noisy pattern to identify the clean original")
        lines.append(f"• Enter the number (1-{len(self.choices)}) of the correct pattern")
        lines.append("• Or type the pattern name directly")
        lines.append("• Use [yellow]HINT[/yellow] command to access noise filters")
        
        return lines
    
    def get_progress_display(self) -> List[str]:
        """Get progress indicators"""
        lines = []
        
        lines.append("[cyan]═══ FILTER PROGRESS ═══[/cyan]")
        lines.append(f"[yellow]Attempts:[/yellow] {self.attempts_made}/{self.max_attempts}")
        lines.append(f"[yellow]Current Score:[/yellow] {self.current_score}/{self.max_score}")
        
        if self.time_limit:
            elapsed = self._get_elapsed_time()
            remaining = max(0, self.time_limit - elapsed)
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            lines.append(f"[yellow]Time Remaining:[/yellow] {minutes:02d}:{seconds:02d}")
        
        if self.hints_used > 0:
            lines.append(f"[yellow]Filter Stages Accessed:[/yellow] {self.hints_used}")
            
        # Show available filter stages
        available_hints = self.get_available_hint_levels()
        if available_hints:
            filter_stages = []
            for level in available_hints:
                if level <= len(self.filter_stages):
                    stage_name = self.filter_stages[level-1][0] if level > 0 else "Analysis"
                    filter_stages.append(f"Level {level} ({stage_name})")
            if filter_stages:
                lines.append(f"[yellow]Available Filters:[/yellow] {', '.join(filter_stages)}")
        
        return lines
    
    def _on_puzzle_start(self) -> None:
        """Called when puzzle starts"""
        self.current_progress['noise_type'] = self.noise_type
        self.current_progress['noise_level'] = self.noise_level
        self.current_progress['target_pattern'] = self.target_pattern.name if self.target_pattern else None
        self.current_progress['start_time'] = time.time()
    
    def _on_puzzle_complete(self, result: PuzzleResult) -> None:
        """Called when puzzle completes"""
        self.current_progress['completion_time'] = time.time()
        self.current_progress['final_score'] = result.score
        self.current_progress['noise_filtered'] = result.success
        self.current_progress['filter_stages_used'] = self.hints_used 