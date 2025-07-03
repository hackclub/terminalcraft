"""
Mastermind and Bulls & Cows Puzzle for The Signal Cartographer
Players use logical deduction to crack numeric codes
"""

from typing import Any, Dict, List, Tuple, Optional
import random
import time

from ..puzzle_base import BasePuzzle, PuzzleResult, PuzzleDifficulty, generate_puzzle_id
from .logic_library import LogicLibrary, LogicPuzzleData
from .logic_tools import LogicSolver, LogicResult


class MastermindPuzzle(BasePuzzle):
    """
    Mastermind puzzle where players guess a secret code using
    logical deduction from Bulls and Cows feedback
    """
    
    def __init__(self, 
                 difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL,
                 signal_data: Any = None,
                 code_length: int = None):
        """
        Initialize Mastermind puzzle
        
        Args:
            difficulty: Puzzle difficulty level
            signal_data: Associated signal data
            code_length: Length of the secret code (overrides difficulty default)
        """
        
        self.logic_library = LogicLibrary()
        self.logic_solver = LogicSolver()
        self.secret_code: List[int] = []
        self.guesses: List[Tuple[List[int], int, int]] = []  # (guess, bulls, cows)
        self.code_length = code_length or self._get_code_length_for_difficulty(difficulty)
        self.max_value = self._get_max_value_for_difficulty(difficulty)
        
        # Calculate difficulty parameters
        max_attempts = max(6, 12 - difficulty.value)
        time_limit = None
        if difficulty.value >= 3:
            time_limit = 360 - (difficulty.value - 3) * 60  # 360, 300, 240, 180 seconds
        
        super().__init__(
            puzzle_id=generate_puzzle_id(),
            name=f"Mastermind Code Breaker",
            description=f"Crack the {self.code_length}-digit code using logical deduction",
            difficulty=difficulty,
            max_attempts=max_attempts,
            time_limit=time_limit,
            signal_data=signal_data
        )
    
    def _get_code_length_for_difficulty(self, difficulty: PuzzleDifficulty) -> int:
        """Get appropriate code length based on difficulty"""
        if difficulty == PuzzleDifficulty.TRIVIAL:
            return 3
        elif difficulty == PuzzleDifficulty.EASY:
            return 3
        elif difficulty == PuzzleDifficulty.NORMAL:
            return 4
        elif difficulty == PuzzleDifficulty.HARD:
            return 4
        else:  # EXPERT, NIGHTMARE
            return 5
    
    def _get_max_value_for_difficulty(self, difficulty: PuzzleDifficulty) -> int:
        """Get maximum digit value based on difficulty"""
        if difficulty == PuzzleDifficulty.TRIVIAL:
            return 4
        elif difficulty == PuzzleDifficulty.EASY:
            return 5
        elif difficulty == PuzzleDifficulty.NORMAL:
            return 6
        elif difficulty == PuzzleDifficulty.HARD:
            return 7
        else:  # EXPERT, NIGHTMARE
            return 8
    
    def _initialize_puzzle(self) -> None:
        """Initialize the Mastermind puzzle"""
        # Generate secret code
        if self.difficulty.value <= 2:
            # Easier puzzles allow repeated digits
            self.secret_code = [random.randint(1, self.max_value) for _ in range(self.code_length)]
        else:
            # Harder puzzles use unique digits
            available_digits = list(range(1, self.max_value + 1))
            self.secret_code = random.sample(available_digits, min(self.code_length, len(available_digits)))
        
        self.solution = str(self.secret_code)
        
        # Generate hints
        self._generate_hints()
        
        # Calculate max score
        self.max_score = 500 + (self.difficulty.value - 1) * 250
    
    def _generate_hints(self):
        """Generate hints for the puzzle"""
        # Hint 1: Basic rules
        self.add_hint(1, f"Code has {self.code_length} digits. Numbers 1-{self.max_value} allowed.", 50)
        
        # Hint 2: Bulls and Cows explanation
        self.add_hint(2, "Bulls = correct digit in correct position. Cows = correct digit in wrong position.", 100)
        
        # Hint 3: First digit hint (for harder difficulties)
        if self.difficulty.value >= 3:
            first_digit = self.secret_code[0]
            self.add_hint(3, f"The first digit is {first_digit}", 150)
        
        # Hint 4: One complete digit and position
        if self.difficulty.value >= 4:
            pos = random.randint(0, len(self.secret_code) - 1)
            digit = self.secret_code[pos]
            self.add_hint(4, f"Position {pos + 1} contains digit {digit}", 200)
        
        # Hint 5: Reveal half the code
        if self.difficulty.value >= 4:
            half_length = self.code_length // 2
            revealed = self.secret_code[:half_length]
            self.add_hint(5, f"First {half_length} digits: {revealed}", 300)
    
    def validate_input(self, player_input: str) -> Tuple[bool, str]:
        """Validate player's guess"""
        player_input = player_input.strip()
        
        # Parse input as list of digits
        try:
            if ' ' in player_input or ',' in player_input:
                # Space or comma separated
                digits_str = player_input.replace(',', ' ').split()
                guess = [int(d) for d in digits_str]
            else:
                # Continuous digits
                guess = [int(d) for d in player_input if d.isdigit()]
            
            # Validate guess format
            if len(guess) != self.code_length:
                return False, f"Guess must have exactly {self.code_length} digits"
            
            if any(d < 1 or d > self.max_value for d in guess):
                return False, f"All digits must be between 1 and {self.max_value}"
            
            # Calculate bulls and cows
            bulls, cows = self._calculate_bulls_cows(guess, self.secret_code)
            
            # Store the guess
            self.guesses.append((guess, bulls, cows))
            
            # Check if solved
            if bulls == self.code_length:
                return True, f"🎉 Cracked! The code is {self.secret_code}. Perfect deduction!"
            else:
                feedback = f"Guess {guess}: {bulls} Bulls, {cows} Cows"
                if len(self.guesses) < self.max_attempts:
                    feedback += f" | {self.max_attempts - len(self.guesses)} attempts remaining"
                return False, feedback
        
        except ValueError:
            return False, f"Invalid input. Enter {self.code_length} digits (1-{self.max_value})"
    
    def _calculate_bulls_cows(self, guess: List[int], solution: List[int]) -> Tuple[int, int]:
        """Calculate bulls and cows for the guess"""
        bulls = sum(1 for i in range(len(guess)) if guess[i] == solution[i])
        
        # Count cows (right numbers in wrong positions)
        guess_counts = {}
        solution_counts = {}
        
        for i in range(len(guess)):
            if guess[i] != solution[i]:  # Not a bull
                guess_counts[guess[i]] = guess_counts.get(guess[i], 0) + 1
                solution_counts[solution[i]] = solution_counts.get(solution[i], 0) + 1
        
        cows = 0
        for digit in guess_counts:
            if digit in solution_counts:
                cows += min(guess_counts[digit], solution_counts[digit])
        
        return bulls, cows
    
    def get_current_display(self) -> List[str]:
        """Get the current puzzle display"""
        lines = []
        
        # Header
        lines.append(f"[bold cyan]🎯 MASTERMIND CODE BREAKER[/bold cyan]")
        lines.append("=" * 60)
        lines.append("")
        
        # Puzzle info
        lines.append(f"[yellow]Code Length:[/yellow] {self.code_length} digits")
        lines.append(f"[yellow]Digit Range:[/yellow] 1 to {self.max_value}")
        lines.append(f"[yellow]Difficulty:[/yellow] {self.difficulty.name}")
        unique_note = "Unique digits" if self.difficulty.value > 2 else "Digits may repeat"
        lines.append(f"[yellow]Constraints:[/yellow] {unique_note}")
        lines.append("")
        
        # Rules explanation
        lines.append("[cyan]═══ RULES ═══[/cyan]")
        lines.append("• [green]Bulls[/green]: Correct digit in correct position")
        lines.append("• [yellow]Cows[/yellow]: Correct digit in wrong position")
        lines.append("• Use logical deduction to crack the secret code")
        lines.append("")
        
        # Guess history
        lines.append("[cyan]═══ GUESS HISTORY ═══[/cyan]")
        if not self.guesses:
            lines.append("No guesses yet. Make your first guess!")
        else:
            for i, (guess, bulls, cows) in enumerate(self.guesses, 1):
                guess_str = " ".join(map(str, guess))
                bulls_indicator = "🟢" * bulls + "⚫" * (self.code_length - bulls)
                cows_indicator = "🟡" * cows
                lines.append(f"{i:2d}. [{guess_str}] → {bulls}🟢 {cows}🟡 {bulls_indicator}{cows_indicator}")
        
        lines.append("")
        
        # Logic analysis (if guesses exist)
        if len(self.guesses) >= 2:
            lines.append("[cyan]═══ DEDUCTION ANALYSIS ═══[/cyan]")
            analysis = self._analyze_guesses()
            for insight in analysis:
                lines.append(f"• {insight}")
            lines.append("")
        
        # Instructions
        lines.append("[green]Instructions:[/green]")
        lines.append(f"• Enter {self.code_length} digits separated by spaces or as one number")
        lines.append(f"• Example: '1 2 3 4' or '1234' for 4-digit code")
        lines.append("• Use [yellow]HINT[/yellow] command for logical deduction help")
        lines.append("• Analyze Bulls/Cows feedback to deduce the code")
        
        return lines
    
    def _analyze_guesses(self) -> List[str]:
        """Analyze guess patterns to provide deduction insights"""
        insights = []
        
        if len(self.guesses) < 2:
            return insights
        
        # Find confirmed positions (consistent bulls)
        confirmed_positions = {}
        for pos in range(self.code_length):
            digit_candidates = {}
            for guess, bulls, cows in self.guesses:
                if bulls > 0:
                    # This guess has at least one bull
                    digit_candidates[guess[pos]] = digit_candidates.get(guess[pos], 0) + 1
            
            # Look for patterns
            if digit_candidates:
                most_common = max(digit_candidates, key=digit_candidates.get)
                if digit_candidates[most_common] >= 2:
                    insights.append(f"Position {pos + 1} likely contains {most_common}")
        
        # Find impossible digits
        impossible_digits = set()
        for guess, bulls, cows in self.guesses:
            if bulls == 0 and cows == 0:
                # None of these digits are in the code
                impossible_digits.update(guess)
        
        if impossible_digits:
            insights.append(f"Digits not in code: {sorted(impossible_digits)}")
        
        # Find confirmed digits (from cows)
        confirmed_digits = set()
        for guess, bulls, cows in self.guesses:
            if cows > 0:
                # Some digits are correct but in wrong positions
                confirmed_digits.update(guess)
        
        if confirmed_digits and not impossible_digits:
            insights.append(f"Code contains some of: {sorted(confirmed_digits)}")
        
        # Suggest strategy based on progress
        total_attempts = len(self.guesses)
        if total_attempts >= 3:
            if all(bulls <= 1 for _, bulls, _ in self.guesses):
                insights.append("Try varying digit positions more systematically")
            elif any(bulls >= 2 for _, bulls, _ in self.guesses):
                insights.append("You're close! Focus on adjusting positions")
        
        return insights
    
    def get_progress_display(self) -> List[str]:
        """Get progress indicators"""
        lines = []
        
        lines.append("[cyan]═══ DEDUCTION PROGRESS ═══[/cyan]")
        lines.append(f"[yellow]Attempts:[/yellow] {len(self.guesses)}/{self.max_attempts}")
        lines.append(f"[yellow]Current Score:[/yellow] {self.current_score}/{self.max_score}")
        
        if self.time_limit:
            elapsed = self._get_elapsed_time()
            remaining = max(0, self.time_limit - elapsed)
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            lines.append(f"[yellow]Time Remaining:[/yellow] {minutes:02d}:{seconds:02d}")
        
        if self.hints_used > 0:
            lines.append(f"[yellow]Hints Used:[/yellow] {self.hints_used}")
        
        # Progress analysis
        if self.guesses:
            best_bulls = max(bulls for _, bulls, _ in self.guesses)
            best_cows = max(cows for _, cows, _ in self.guesses)
            lines.append(f"[yellow]Best Bulls:[/yellow] {best_bulls}/{self.code_length}")
            lines.append(f"[yellow]Best Cows:[/yellow] {best_cows}")
            
            progress_percent = int((best_bulls / self.code_length) * 100)
            lines.append(f"[yellow]Progress:[/yellow] {progress_percent}% cracked")
        
        return lines
    
    def _on_puzzle_start(self) -> None:
        """Called when puzzle starts"""
        self.current_progress['secret_code'] = self.secret_code
        self.current_progress['code_length'] = self.code_length
        self.current_progress['max_value'] = self.max_value
        self.current_progress['start_time'] = time.time()
    
    def _on_puzzle_complete(self, result: PuzzleResult) -> None:
        """Called when puzzle completes"""
        self.current_progress['completion_time'] = time.time()
        self.current_progress['final_score'] = result.score
        self.current_progress['code_cracked'] = result.success
        self.current_progress['total_guesses'] = len(self.guesses)
        self.current_progress['guesses_history'] = self.guesses


class BullsAndCowsPuzzle(MastermindPuzzle):
    """
    Bulls and Cows variant - simpler version with shorter codes
    and more forgiving difficulty curve
    """
    
    def __init__(self, 
                 difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL,
                 signal_data: Any = None):
        """
        Initialize Bulls and Cows puzzle
        """
        # Override code length for Bulls and Cows (typically shorter)
        code_length = 3 if difficulty.value <= 3 else 4
        
        super().__init__(difficulty, signal_data, code_length)
        
        # Update name and description
        self.name = "Bulls & Cows Code Breaker"
        self.description = f"Crack the {self.code_length}-digit code using Bulls & Cows feedback"
        
        # More attempts for Bulls and Cows
        self.max_attempts = max(8, 15 - difficulty.value)
    
    def _get_code_length_for_difficulty(self, difficulty: PuzzleDifficulty) -> int:
        """Override for Bulls and Cows - shorter codes"""
        if difficulty.value <= 2:
            return 3
        elif difficulty.value <= 4:
            return 4
        else:
            return 4  # Max 4 for Bulls and Cows
    
    def _get_max_value_for_difficulty(self, difficulty: PuzzleDifficulty) -> int:
        """Override for Bulls and Cows - smaller range"""
        if difficulty.value <= 2:
            return 5
        elif difficulty.value <= 4:
            return 6
        else:
            return 7  # Max 7 for Bulls and Cows
    
    def get_current_display(self) -> List[str]:
        """Override display for Bulls and Cows branding"""
        lines = super().get_current_display()
        
        # Replace header
        lines[0] = f"[bold cyan]🐂 BULLS & COWS CODE BREAKER[/bold cyan]"
        
        return lines 