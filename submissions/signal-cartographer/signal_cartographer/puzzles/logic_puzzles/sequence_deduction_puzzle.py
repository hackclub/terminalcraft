"""
Sequence Deduction Puzzle for The Signal Cartographer
Players analyze mathematical sequences to predict the next values
"""

from typing import Any, Dict, List, Tuple, Optional
import random
import time

from ..puzzle_base import BasePuzzle, PuzzleResult, PuzzleDifficulty, generate_puzzle_id
from .logic_library import LogicLibrary, LogicPuzzleData
from .logic_tools import LogicSolver, SequenceAnalyzer, LogicResult


class SequenceDeductionPuzzle(BasePuzzle):
    """
    Sequence deduction puzzle where players identify mathematical patterns
    and predict the next value in a sequence
    """
    
    def __init__(self, 
                 difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL,
                 signal_data: Any = None,
                 sequence_type: str = None):
        """
        Initialize sequence deduction puzzle
        
        Args:
            difficulty: Puzzle difficulty level
            signal_data: Associated signal data
            sequence_type: Specific sequence type (overrides random selection)
        """
        
        self.logic_library = LogicLibrary()
        self.sequence_analyzer = SequenceAnalyzer()
        self.sequence_type = sequence_type
        self.sequence: List[int] = []
        self.hidden_sequence: List[int] = []
        self.visible_length = 0
        self.next_value = 0
        self.choices: List[int] = []
        
        # Calculate difficulty parameters
        max_attempts = max(3, 6 - difficulty.value)
        time_limit = None
        if difficulty.value >= 3:
            time_limit = 240 - (difficulty.value - 3) * 40  # 240, 200, 160, 120 seconds
        
        super().__init__(
            puzzle_id=generate_puzzle_id(),
            name=f"Sequence Pattern Analysis",
            description=f"Identify mathematical patterns and predict next values",
            difficulty=difficulty,
            max_attempts=max_attempts,
            time_limit=time_limit,
            signal_data=signal_data
        )
    
    def _initialize_puzzle(self) -> None:
        """Initialize the sequence deduction puzzle"""
        # Select sequence type based on difficulty
        if not self.sequence_type:
            self.sequence_type = self._select_sequence_type()
        
        # Get or generate sequence
        self._generate_sequence()
        
        # Determine visible length based on difficulty
        self.visible_length = self._get_visible_length()
        
        # Set up the puzzle
        self.hidden_sequence = self.sequence[:self.visible_length]
        self.next_value = self.sequence[self.visible_length]
        self.solution = str(self.next_value)
        
        # Generate multiple choice options
        self._generate_choices()
        
        # Generate hints
        self._generate_hints()
        
        # Calculate max score
        self.max_score = 400 + (self.difficulty.value - 1) * 200
    
    def _select_sequence_type(self) -> str:
        """Select appropriate sequence type based on difficulty"""
        if self.difficulty == PuzzleDifficulty.TRIVIAL:
            return random.choice(["arithmetic", "geometric", "powers_of_2"])
        elif self.difficulty == PuzzleDifficulty.EASY:
            return random.choice(["arithmetic", "geometric", "fibonacci", "squares"])
        elif self.difficulty == PuzzleDifficulty.NORMAL:
            return random.choice(["fibonacci", "primes", "squares", "triangular", "powers_of_2"])
        elif self.difficulty == PuzzleDifficulty.HARD:
            return random.choice(["primes", "triangular", "signal_themed", "alternating"])
        else:  # EXPERT, NIGHTMARE
            return random.choice(["signal_themed", "alternating", "fibonacci", "primes"])
    
    def _generate_sequence(self):
        """Generate or get sequence based on type"""
        if self.sequence_type in self.logic_library.sequences:
            # Use predefined sequence
            self.sequence = self.logic_library.sequences[self.sequence_type].copy()
        else:
            # Generate new sequence
            self.sequence = self._create_custom_sequence(self.sequence_type)
        
        # Ensure sequence is long enough
        while len(self.sequence) < 10:
            if self.sequence_type == "arithmetic":
                diff = self.sequence[-1] - self.sequence[-2]
                self.sequence.append(self.sequence[-1] + diff)
            elif self.sequence_type == "geometric":
                ratio = self.sequence[-1] // self.sequence[-2] if self.sequence[-2] != 0 else 2
                self.sequence.append(self.sequence[-1] * ratio)
            elif self.sequence_type == "fibonacci":
                self.sequence.append(self.sequence[-1] + self.sequence[-2])
            else:
                # Extend with pattern or random
                self.sequence.append(self.sequence[-1] + random.randint(1, 5))
    
    def _create_custom_sequence(self, seq_type: str) -> List[int]:
        """Create custom sequence based on type"""
        if seq_type == "arithmetic":
            start = random.randint(1, 10)
            step = random.randint(2, 5)
            return [start + i * step for i in range(10)]
        elif seq_type == "geometric":
            start = random.randint(1, 3)
            ratio = random.randint(2, 3)
            return [start * (ratio ** i) for i in range(8)]
        elif seq_type == "fibonacci":
            a, b = random.randint(1, 3), random.randint(1, 3)
            sequence = [a, b]
            for _ in range(8):
                sequence.append(sequence[-1] + sequence[-2])
            return sequence
        elif seq_type == "powers":
            base = random.randint(2, 4)
            return [base ** i for i in range(1, 9)]
        else:
            # Random pattern
            return [random.randint(1, 20) for _ in range(10)]
    
    def _get_visible_length(self) -> int:
        """Get number of visible sequence elements based on difficulty"""
        if self.difficulty == PuzzleDifficulty.TRIVIAL:
            return 4
        elif self.difficulty == PuzzleDifficulty.EASY:
            return 4
        elif self.difficulty == PuzzleDifficulty.NORMAL:
            return 5
        elif self.difficulty == PuzzleDifficulty.HARD:
            return 5
        else:  # EXPERT, NIGHTMARE
            return 6
    
    def _generate_choices(self):
        """Generate multiple choice options"""
        self.choices = [self.next_value]
        
        # Add plausible wrong answers
        base_value = self.next_value
        
        # Add nearby values
        for offset in [-3, -2, -1, 1, 2, 3]:
            wrong_value = base_value + offset
            if wrong_value > 0 and wrong_value not in self.choices:
                self.choices.append(wrong_value)
        
        # Add pattern-breaking values
        if len(self.hidden_sequence) >= 2:
            last_diff = self.hidden_sequence[-1] - self.hidden_sequence[-2]
            # Wrong arithmetic continuation
            wrong_arith = self.hidden_sequence[-1] + last_diff + random.randint(1, 3)
            if wrong_arith not in self.choices:
                self.choices.append(wrong_arith)
            
            # Wrong geometric continuation
            if self.hidden_sequence[-2] != 0:
                ratio = self.hidden_sequence[-1] / self.hidden_sequence[-2]
                wrong_geom = int(self.hidden_sequence[-1] * ratio * random.uniform(0.8, 1.2))
                if wrong_geom > 0 and wrong_geom not in self.choices:
                    self.choices.append(wrong_geom)
        
        # Limit to 6 choices and shuffle
        self.choices = self.choices[:6]
        random.shuffle(self.choices)
        
        # Create choice mapping
        self.choice_mapping = {str(i+1): choice for i, choice in enumerate(self.choices)}
    
    def _generate_hints(self):
        """Generate hints for the puzzle"""
        # Hint 1: Sequence type hint
        type_hint = self._get_sequence_type_hint()
        self.add_hint(1, type_hint, 50)
        
        # Hint 2: Pattern analysis
        if self.difficulty.value >= 2:
            pattern_hint = self._analyze_pattern_hint()
            self.add_hint(2, pattern_hint, 100)
        
        # Hint 3: Mathematical operation
        if self.difficulty.value >= 3:
            operation_hint = self._get_operation_hint()
            self.add_hint(3, operation_hint, 150)
        
        # Hint 4: Next value range
        if self.difficulty.value >= 4:
            range_hint = f"The next value is between {self.next_value - 5} and {self.next_value + 5}"
            self.add_hint(4, range_hint, 200)
        
        # Hint 5: Direct answer
        if self.difficulty.value >= 4:
            self.add_hint(5, f"The next value is {self.next_value}", 250)
    
    def _get_sequence_type_hint(self) -> str:
        """Get hint about sequence type"""
        if self.sequence_type == "arithmetic":
            return "This is an arithmetic sequence (constant difference)"
        elif self.sequence_type == "geometric":
            return "This is a geometric sequence (constant ratio)"
        elif self.sequence_type == "fibonacci":
            return "Each term is the sum of the two previous terms"
        elif self.sequence_type == "primes":
            return "This sequence contains only prime numbers"
        elif self.sequence_type == "squares":
            return "This sequence consists of perfect squares"
        elif self.sequence_type == "powers_of_2":
            return "This sequence consists of powers of 2"
        elif self.sequence_type == "triangular":
            return "This sequence consists of triangular numbers"
        else:
            return "Look for mathematical relationships between consecutive terms"
    
    def _analyze_pattern_hint(self) -> str:
        """Analyze pattern to provide specific hint"""
        if len(self.hidden_sequence) < 2:
            return "Need more terms to analyze pattern"
        
        # Check differences
        differences = [self.hidden_sequence[i+1] - self.hidden_sequence[i] 
                      for i in range(len(self.hidden_sequence)-1)]
        
        if all(d == differences[0] for d in differences):
            return f"Constant difference of {differences[0]} between consecutive terms"
        
        # Check ratios
        if all(x != 0 for x in self.hidden_sequence[:-1]):
            ratios = [self.hidden_sequence[i+1] / self.hidden_sequence[i] 
                     for i in range(len(self.hidden_sequence)-1)]
            if all(abs(r - ratios[0]) < 0.1 for r in ratios):
                return f"Constant ratio of approximately {ratios[0]:.1f} between terms"
        
        # Check Fibonacci pattern
        if len(self.hidden_sequence) >= 3:
            fib_check = all(self.hidden_sequence[i] == self.hidden_sequence[i-1] + self.hidden_sequence[i-2]
                           for i in range(2, len(self.hidden_sequence)))
            if fib_check:
                return "Each term equals the sum of the two previous terms"
        
        return "Look for patterns in differences, ratios, or special number properties"
    
    def _get_operation_hint(self) -> str:
        """Get specific mathematical operation hint"""
        if len(self.hidden_sequence) < 2:
            return "Analyze the mathematical relationship"
        
        last_val = self.hidden_sequence[-1]
        second_last = self.hidden_sequence[-2]
        
        diff = last_val - second_last
        if second_last != 0:
            ratio = last_val / second_last
            
            if self.sequence_type == "arithmetic" or all(
                self.hidden_sequence[i+1] - self.hidden_sequence[i] == diff 
                for i in range(len(self.hidden_sequence)-1)
            ):
                return f"Add {diff} to get the next term"
            elif self.sequence_type == "geometric" or abs(ratio - round(ratio)) < 0.1:
                return f"Multiply by {int(ratio)} to get the next term"
        
        if self.sequence_type == "fibonacci":
            return f"Add {self.hidden_sequence[-1]} + {self.hidden_sequence[-2]} = {self.next_value}"
        
        return "Apply the pattern you've identified to find the next term"
    
    def validate_input(self, player_input: str) -> Tuple[bool, str]:
        """Validate player's answer"""
        player_input = player_input.strip()
        
        # Check multiple choice number
        if player_input.isdigit() and player_input in self.choice_mapping:
            selected_value = self.choice_mapping[player_input]
            if selected_value == self.next_value:
                return True, f"🎯 Correct! The next value is {self.next_value}!"
            else:
                return False, f"Incorrect. {selected_value} doesn't follow the pattern."
        
        # Check direct numeric input
        try:
            input_value = int(player_input)
            if input_value == self.next_value:
                return True, f"🎯 Excellent! The next value is {self.next_value}!"
            else:
                return False, f"Incorrect. {input_value} doesn't follow the pattern."
        except ValueError:
            return False, f"Invalid input. Enter a number or choice 1-{len(self.choices)}."
    
    def get_current_display(self) -> List[str]:
        """Get the current puzzle display"""
        lines = []
        
        # Header
        lines.append(f"[bold cyan]🔢 SEQUENCE PATTERN ANALYSIS[/bold cyan]")
        lines.append("=" * 60)
        lines.append("")
        
        # Puzzle info
        lines.append(f"[yellow]Sequence Type:[/yellow] {self.sequence_type.replace('_', ' ').title()}")
        lines.append(f"[yellow]Difficulty:[/yellow] {self.difficulty.name}")
        lines.append(f"[yellow]Pattern Length:[/yellow] {self.visible_length} visible terms")
        lines.append("")
        
        # Display sequence
        lines.append("[cyan]═══ SEQUENCE PATTERN ═══[/cyan]")
        sequence_display = " → ".join(map(str, self.hidden_sequence))
        lines.append(f"Sequence: {sequence_display} → ?")
        lines.append("")
        
        # Pattern analysis (for easier difficulties)
        if self.difficulty.value <= 3:
            lines.append("[cyan]═══ PATTERN ANALYSIS ═══[/cyan]")
            if len(self.hidden_sequence) >= 2:
                # Show differences
                differences = [self.hidden_sequence[i+1] - self.hidden_sequence[i] 
                              for i in range(len(self.hidden_sequence)-1)]
                lines.append(f"Differences: {' → '.join(map(str, differences))}")
                
                # Show ratios if applicable
                if all(x != 0 for x in self.hidden_sequence[:-1]):
                    ratios = [round(self.hidden_sequence[i+1] / self.hidden_sequence[i], 2) 
                             for i in range(len(self.hidden_sequence)-1)]
                    lines.append(f"Ratios: {' → '.join(map(str, ratios))}")
            lines.append("")
        
        # Multiple choice options
        lines.append("[cyan]═══ NEXT VALUE OPTIONS ═══[/cyan]")
        for i, choice in enumerate(self.choices, 1):
            lines.append(f"[white]{i}.[/white] {choice}")
        lines.append("")
        
        # Instructions
        lines.append("[green]Instructions:[/green]")
        lines.append("• Analyze the mathematical pattern in the sequence")
        lines.append(f"• Enter the number (1-{len(self.choices)}) or type the value directly")
        lines.append("• Use [yellow]HINT[/yellow] command for pattern analysis help")
        lines.append("• Look for arithmetic, geometric, or special number patterns")
        
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
            lines.append(f"[yellow]Analysis Tools Used:[/yellow] {self.hints_used}")
        
        # Sequence analysis
        lines.append(f"[yellow]Sequence Length:[/yellow] {len(self.hidden_sequence)} terms")
        lines.append(f"[yellow]Pattern Type:[/yellow] {self.sequence_type.title()}")
        
        # Show automated analysis result
        analysis_result = self.sequence_analyzer.analyze_sequence(self.hidden_sequence)
        if analysis_result.success:
            confidence_percent = int(analysis_result.confidence * 100)
            lines.append(f"[yellow]Pattern Confidence:[/yellow] {confidence_percent}%")
        
        return lines
    
    def _on_puzzle_start(self) -> None:
        """Called when puzzle starts"""
        self.current_progress['sequence_type'] = self.sequence_type
        self.current_progress['full_sequence'] = self.sequence
        self.current_progress['visible_sequence'] = self.hidden_sequence
        self.current_progress['next_value'] = self.next_value
        self.current_progress['start_time'] = time.time()
    
    def _on_puzzle_complete(self, result: PuzzleResult) -> None:
        """Called when puzzle completes"""
        self.current_progress['completion_time'] = time.time()
        self.current_progress['final_score'] = result.score
        self.current_progress['pattern_solved'] = result.success
        self.current_progress['analysis_methods_used'] = self.hints_used 