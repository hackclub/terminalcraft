"""
Symbol Recognition Puzzle for The Signal Cartographer
Players identify and match symbol sequences and patterns
"""

from typing import Any, Dict, List, Tuple, Optional
import random
import time

from ..puzzle_base import BasePuzzle, PuzzleResult, PuzzleDifficulty, generate_puzzle_id


class SymbolRecognitionPuzzle(BasePuzzle):
    """
    Symbol recognition puzzle where players identify repeating symbols,
    complete sequences, or find matching symbols in noise
    """
    
    def __init__(self, 
                 difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL,
                 signal_data: Any = None,
                 puzzle_type: str = "sequence"):
        """
        Initialize symbol recognition puzzle
        
        Args:
            difficulty: Puzzle difficulty level
            signal_data: Associated signal data
            puzzle_type: Type of puzzle (sequence, matching, counting)
        """
        
        self.puzzle_type = puzzle_type
        self.symbol_set = ['★', '◆', '▲', '●', '■', '♦', '♠', '♣', '♥', '○', '△', '□']
        self.sequence_length = 0
        self.target_sequence: List[str] = []
        self.display_pattern: List[str] = []
        self.choices: List[str] = []
        
        # Calculate difficulty parameters
        max_attempts = max(3, 6 - difficulty.value)
        time_limit = None
        if difficulty.value >= 3:
            time_limit = 150 - (difficulty.value - 3) * 30  # 150, 120, 90, 60 seconds
        
        super().__init__(
            puzzle_id=generate_puzzle_id(),
            name=f"Symbol Recognition - {puzzle_type.title()}",
            description=f"Analyze and identify symbol patterns",
            difficulty=difficulty,
            max_attempts=max_attempts,
            time_limit=time_limit,
            signal_data=signal_data
        )
    
    def _initialize_puzzle(self) -> None:
        """Initialize the symbol recognition puzzle"""
        # Calculate sequence length based on difficulty
        base_length = 4
        self.sequence_length = base_length + self.difficulty.value - 1  # 4 to 8 symbols
        
        # Generate puzzle based on type
        if self.puzzle_type == "sequence":
            self._initialize_sequence_puzzle()
        elif self.puzzle_type == "matching":
            self._initialize_matching_puzzle()
        elif self.puzzle_type == "counting":
            self._initialize_counting_puzzle()
        else:
            self._initialize_sequence_puzzle()  # Default
        
        # Add hints
        self._generate_hints()
        
        # Calculate max score
        self.max_score = 300 + (self.difficulty.value - 1) * 150
    
    def _initialize_sequence_puzzle(self):
        """Initialize sequence completion puzzle"""
        # Create a pattern sequence
        num_unique_symbols = min(4, 2 + self.difficulty.value // 2)
        pattern_symbols = random.sample(self.symbol_set, num_unique_symbols)
        
        # Generate repeating pattern
        pattern_length = random.randint(2, 4)
        base_pattern = random.choices(pattern_symbols, k=pattern_length)
        
        # Repeat pattern to create sequence
        full_sequence = []
        while len(full_sequence) < self.sequence_length:
            full_sequence.extend(base_pattern)
        
        self.target_sequence = full_sequence[:self.sequence_length]
        
        # Create display with missing symbol
        missing_position = random.randint(self.sequence_length // 2, self.sequence_length - 1)
        self.display_pattern = self.target_sequence.copy()
        self.display_pattern[missing_position] = '?'
        
        # Solution is the missing symbol
        self.solution = self.target_sequence[missing_position]
        
        # Generate choices
        self.choices = [self.solution]
        incorrect_choices = [sym for sym in pattern_symbols if sym != self.solution]
        self.choices.extend(incorrect_choices)
        
        # Add some random symbols
        extra_symbols = [sym for sym in self.symbol_set if sym not in pattern_symbols]
        if extra_symbols:
            self.choices.extend(random.sample(extra_symbols, min(2, len(extra_symbols))))
        
        random.shuffle(self.choices)
        self.choice_mapping = {str(i+1): choice for i, choice in enumerate(self.choices)}
    
    def _initialize_matching_puzzle(self):
        """Initialize symbol matching puzzle"""
        # Create a pattern with repeated symbols
        num_symbols = 3 + self.difficulty.value
        pattern_symbols = random.sample(self.symbol_set, min(6, num_symbols))
        
        # Create pattern with one symbol appearing more frequently
        target_symbol = random.choice(pattern_symbols)
        target_count = random.randint(3, 6)
        
        # Create pattern
        pattern = [target_symbol] * target_count
        other_symbols = [sym for sym in pattern_symbols if sym != target_symbol]
        
        # Add other symbols
        for _ in range(self.sequence_length - target_count):
            pattern.append(random.choice(other_symbols))
        
        random.shuffle(pattern)
        self.target_sequence = pattern
        self.display_pattern = [' '.join(pattern)]
        
        # Solution is the most frequent symbol
        self.solution = target_symbol
        
        # Generate choices (all symbols in the pattern)
        self.choices = list(set(pattern))
        random.shuffle(self.choices)
        self.choice_mapping = {str(i+1): choice for i, choice in enumerate(self.choices)}
    
    def _initialize_counting_puzzle(self):
        """Initialize symbol counting puzzle"""
        # Create pattern with symbols to count
        target_symbol = random.choice(self.symbol_set[:6])  # Use simpler symbols for counting
        target_count = random.randint(3, 8)
        
        # Create noise symbols
        noise_symbols = random.sample([s for s in self.symbol_set if s != target_symbol], 3)
        
        # Create pattern
        pattern = [target_symbol] * target_count
        # Add noise
        for _ in range(random.randint(5, 12)):
            pattern.append(random.choice(noise_symbols))
        
        random.shuffle(pattern)
        self.target_sequence = pattern
        self.display_pattern = [' '.join(pattern)]
        
        # Solution is the count
        self.solution = str(target_count)
        
        # Generate count choices
        self.choices = [str(target_count)]
        for _ in range(4):
            wrong_count = target_count + random.randint(-2, 2)
            if wrong_count > 0 and str(wrong_count) not in self.choices:
                self.choices.append(str(wrong_count))
        
        random.shuffle(self.choices)
        self.choice_mapping = {str(i+1): choice for i, choice in enumerate(self.choices)}
        
        # Store target symbol for display
        self.current_progress['target_symbol'] = target_symbol
    
    def _generate_hints(self):
        """Generate hints for the puzzle"""
        if self.puzzle_type == "sequence":
            self.add_hint(1, "Look for repeating patterns in the symbol sequence", 25)
            self.add_hint(2, f"The sequence has {len(set(self.target_sequence))} unique symbols", 50)
            if self.difficulty.value >= 3:
                pattern_len = self._find_pattern_length()
                self.add_hint(3, f"The repeating pattern is {pattern_len} symbols long", 75)
        
        elif self.puzzle_type == "matching":
            self.add_hint(1, "Find the symbol that appears most frequently", 25)
            self.add_hint(2, f"Count each symbol type in the pattern", 50)
        
        elif self.puzzle_type == "counting":
            target_sym = self.current_progress.get('target_symbol', '?')
            self.add_hint(1, f"Count how many '{target_sym}' symbols appear", 25)
            self.add_hint(2, "Ignore the other symbols - focus only on the target", 50)
    
    def _find_pattern_length(self) -> int:
        """Find the length of the repeating pattern"""
        if not self.target_sequence:
            return 0
        
        for length in range(2, len(self.target_sequence) // 2 + 1):
            is_pattern = True
            for i in range(length, len(self.target_sequence)):
                if self.target_sequence[i] != self.target_sequence[i % length]:
                    is_pattern = False
                    break
            if is_pattern:
                return length
        
        return len(self.target_sequence)
    
    def validate_input(self, player_input: str) -> Tuple[bool, str]:
        """Validate player's answer"""
        player_input = player_input.strip()
        
        # Check multiple choice number
        if player_input.isdigit():
            choice_num = player_input
            if choice_num in self.choice_mapping:
                selected_answer = self.choice_mapping[choice_num]
                if selected_answer == self.solution:
                    return True, f"Correct! The answer is {self.solution}!"
                else:
                    return False, f"Incorrect. {selected_answer} is not the right answer."
            else:
                return False, f"Invalid choice. Please select 1-{len(self.choices)}."
        
        # Check direct input
        if player_input == self.solution:
            return True, f"Excellent! The answer is {self.solution}!"
        
        return False, f"'{player_input}' is not correct. Analyze the pattern more carefully."
    
    def get_current_display(self) -> List[str]:
        """Get the current puzzle display"""
        lines = []
        
        # Header
        lines.append(f"[bold cyan]🔍 SYMBOL RECOGNITION PUZZLE[/bold cyan]")
        lines.append("=" * 60)
        lines.append("")
        
        # Puzzle info
        puzzle_desc = self.puzzle_type.replace('_', ' ').title()
        lines.append(f"[yellow]Type:[/yellow] {puzzle_desc}")
        lines.append(f"[yellow]Difficulty:[/yellow] {self.difficulty.name}")
        lines.append("")
        
        # Display pattern
        lines.append("[cyan]═══ SYMBOL PATTERN ═══[/cyan]")
        
        if self.puzzle_type == "sequence":
            # Display sequence with missing symbol
            lines.append("Pattern sequence:")
            lines.append(f"  {' '.join(self.display_pattern)}")
            lines.append("")
            lines.append("Find the missing symbol marked with '?'")
            
        elif self.puzzle_type == "matching":
            lines.append("Symbol pattern:")
            lines.extend([f"  {line}" for line in self.display_pattern])
            lines.append("")
            lines.append("Which symbol appears most frequently?")
            
        elif self.puzzle_type == "counting":
            target_sym = self.current_progress.get('target_symbol', '?')
            lines.append(f"Count the '{target_sym}' symbols:")
            lines.extend([f"  {line}" for line in self.display_pattern])
            lines.append("")
            lines.append(f"How many '{target_sym}' symbols are there?")
        
        lines.append("")
        
        # Display choices
        lines.append("[cyan]═══ ANSWER OPTIONS ═══[/cyan]")
        for i, choice in enumerate(self.choices, 1):
            lines.append(f"[white]{i}.[/white] {choice}")
        lines.append("")
        
        # Instructions
        lines.append("[green]Instructions:[/green]")
        lines.append(f"• Enter the number (1-{len(self.choices)}) of your answer")
        lines.append("• Or type the symbol/number directly")
        lines.append("• Use [yellow]HINT[/yellow] command if needed")
        
        return lines
    
    def get_progress_display(self) -> List[str]:
        """Get progress indicators"""
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
        
        return lines
    
    def _on_puzzle_start(self) -> None:
        """Called when puzzle starts"""
        self.current_progress['puzzle_type'] = self.puzzle_type
        self.current_progress['sequence_length'] = self.sequence_length
        self.current_progress['start_time'] = time.time()
    
    def _on_puzzle_complete(self, result: PuzzleResult) -> None:
        """Called when puzzle completes"""
        self.current_progress['completion_time'] = time.time()
        self.current_progress['final_score'] = result.score
        self.current_progress['symbol_recognition_success'] = result.success 