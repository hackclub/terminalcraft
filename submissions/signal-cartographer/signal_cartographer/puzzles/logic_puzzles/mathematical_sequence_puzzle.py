"""
Mathematical Sequence Puzzle for The Signal Cartographer
Players analyze and predict advanced mathematical sequences
"""

from typing import Any, Dict, List, Tuple, Optional
import random
import time
import math

from ..puzzle_base import BasePuzzle, PuzzleResult, PuzzleDifficulty, generate_puzzle_id
from .logic_library import LogicLibrary
from .logic_tools import SequenceAnalyzer


class MathematicalSequencePuzzle(BasePuzzle):
    """
    Advanced mathematical sequence puzzle with complex patterns
    """
    
    def __init__(self, 
                 difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL,
                 signal_data: Any = None,
                 sequence_category: str = "arithmetic"):
        """
        Initialize mathematical sequence puzzle
        
        Args:
            difficulty: Puzzle difficulty level
            signal_data: Associated signal data
            sequence_category: Category of sequence (arithmetic, geometric, polynomial, special)
        """
        
        self.logic_library = LogicLibrary()
        self.sequence_analyzer = SequenceAnalyzer()
        self.sequence_category = sequence_category
        self.sequence: List[int] = []
        self.pattern_description = ""
        self.pattern_formula = ""
        self.next_terms: List[int] = []
        self.analysis_steps: List[str] = []
        
        # Calculate difficulty parameters
        max_attempts = max(3, 6 - difficulty.value)
        time_limit = None
        if difficulty.value >= 3:
            time_limit = 360 - (difficulty.value - 3) * 60  # 360, 300, 240, 180 seconds
        
        super().__init__(
            puzzle_id=generate_puzzle_id(),
            name=f"Mathematical Sequence - {sequence_category.title()}",
            description=f"Analyze and predict mathematical sequences",
            difficulty=difficulty,
            max_attempts=max_attempts,
            time_limit=time_limit,
            signal_data=signal_data
        )
    
    def _initialize_puzzle(self) -> None:
        """Initialize the mathematical sequence puzzle"""
        # Generate sequence based on category and difficulty
        if self.sequence_category == "arithmetic":
            self._generate_arithmetic_sequence()
        elif self.sequence_category == "geometric":
            self._generate_geometric_sequence()
        elif self.sequence_category == "polynomial":
            self._generate_polynomial_sequence()
        elif self.sequence_category == "special":
            self._generate_special_sequence()
        else:
            self._generate_arithmetic_sequence()  # Default
        
        # Generate analysis steps
        self._analyze_sequence()
        
        # Generate hints
        self._generate_hints()
        
        # Calculate max score
        self.max_score = 700 + (self.difficulty.value - 1) * 300
    
    def _generate_arithmetic_sequence(self):
        """Generate arithmetic progression sequences"""
        patterns = {
            1: {  # Simple arithmetic
                "start": random.randint(1, 10),
                "diff": random.randint(2, 5),
                "terms": 6,
                "formula": "a_n = a_1 + (n-1)d"
            },
            2: {  # Modified arithmetic
                "start": random.randint(5, 15),
                "diff": random.choice([3, 7, 11, 13]),
                "terms": 7,
                "formula": "a_n = a_1 + (n-1)d"
            },
            3: {  # Arithmetic with pattern
                "start": random.randint(10, 20),
                "diff": random.choice([6, 8, 12, 15]),
                "terms": 8,
                "formula": "a_n = a_1 + (n-1)d"
            }
        }
        
        level = min(self.difficulty.value // 2 + 1, 3)
        pattern = patterns[level]
        
        # Generate sequence
        start = pattern["start"]
        diff = pattern["diff"]
        terms = pattern["terms"]
        
        self.sequence = []
        for i in range(terms):
            self.sequence.append(start + i * diff)
        
        # Calculate next terms
        self.next_terms = [
            start + terms * diff,
            start + (terms + 1) * diff
        ]
        
        self.pattern_description = f"Arithmetic sequence with first term {start} and common difference {diff}"
        self.pattern_formula = pattern["formula"]
        self.solution = str(self.next_terms[0])
    
    def _generate_geometric_sequence(self):
        """Generate geometric progression sequences"""
        patterns = {
            1: {  # Simple geometric
                "start": random.choice([2, 3, 5]),
                "ratio": random.choice([2, 3]),
                "terms": 5,
                "formula": "a_n = a_1 * r^(n-1)"
            },
            2: {  # Moderate geometric
                "start": random.choice([1, 2, 4]),
                "ratio": random.choice([3, 4, 5]),
                "terms": 6,
                "formula": "a_n = a_1 * r^(n-1)"
            },
            3: {  # Complex geometric
                "start": random.choice([1, 3, 7]),
                "ratio": random.choice([2, 3]),
                "terms": 7,
                "formula": "a_n = a_1 * r^(n-1)"
            }
        }
        
        level = min(self.difficulty.value // 2 + 1, 3)
        pattern = patterns[level]
        
        # Generate sequence
        start = pattern["start"]
        ratio = pattern["ratio"]
        terms = pattern["terms"]
        
        self.sequence = []
        for i in range(terms):
            self.sequence.append(start * (ratio ** i))
        
        # Calculate next terms
        self.next_terms = [
            start * (ratio ** terms),
            start * (ratio ** (terms + 1))
        ]
        
        self.pattern_description = f"Geometric sequence with first term {start} and common ratio {ratio}"
        self.pattern_formula = pattern["formula"]
        self.solution = str(self.next_terms[0])
    
    def _generate_polynomial_sequence(self):
        """Generate polynomial-based sequences"""
        patterns = {
            1: {  # Quadratic: n^2 + c
                "type": "quadratic",
                "formula": "a_n = n² + c",
                "constant": random.randint(1, 5)
            },
            2: {  # Cubic: n^3 + n
                "type": "cubic_linear",
                "formula": "a_n = n³ + n",
                "constant": 0
            },
            3: {  # Complex polynomial: n^2 + 2n + 1
                "type": "quadratic_linear",
                "formula": "a_n = n² + 2n + 1",
                "constant": 1
            }
        }
        
        level = min(self.difficulty.value // 2 + 1, 3)
        pattern = patterns[level]
        
        self.sequence = []
        
        if pattern["type"] == "quadratic":
            c = pattern["constant"]
            for n in range(1, 7):
                self.sequence.append(n*n + c)
            
            # Next terms
            self.next_terms = [7*7 + c, 8*8 + c]
            self.pattern_description = f"Quadratic sequence: n² + {c}"
            
        elif pattern["type"] == "cubic_linear":
            for n in range(1, 6):
                self.sequence.append(n*n*n + n)
            
            # Next terms
            self.next_terms = [6*6*6 + 6, 7*7*7 + 7]
            self.pattern_description = "Cubic + linear: n³ + n"
            
        elif pattern["type"] == "quadratic_linear":
            for n in range(1, 6):
                self.sequence.append(n*n + 2*n + 1)
            
            # Next terms
            self.next_terms = [6*6 + 2*6 + 1, 7*7 + 2*7 + 1]
            self.pattern_description = "Quadratic + linear: n² + 2n + 1"
        
        self.pattern_formula = pattern["formula"]
        self.solution = str(self.next_terms[0])
    
    def _generate_special_sequence(self):
        """Generate special mathematical sequences"""
        special_types = {
            1: "triangular",
            2: "square_pyramidal", 
            3: "catalan",
            4: "lucas"
        }
        
        seq_type = special_types.get(self.difficulty.value, "triangular")
        
        if seq_type == "triangular":
            # Triangular numbers: n(n+1)/2
            self.sequence = [n*(n+1)//2 for n in range(1, 7)]
            self.next_terms = [7*8//2, 8*9//2]
            self.pattern_description = "Triangular numbers: T_n = n(n+1)/2"
            self.pattern_formula = "T_n = n(n+1)/2"
            
        elif seq_type == "square_pyramidal":
            # Square pyramidal: n(n+1)(2n+1)/6
            self.sequence = [n*(n+1)*(2*n+1)//6 for n in range(1, 6)]
            self.next_terms = [6*7*13//6, 7*8*15//6]
            self.pattern_description = "Square pyramidal numbers"
            self.pattern_formula = "P_n = n(n+1)(2n+1)/6"
            
        elif seq_type == "catalan":
            # Catalan numbers
            def catalan(n):
                if n <= 1:
                    return 1
                c = [0] * (n + 1)
                c[0], c[1] = 1, 1
                for i in range(2, n + 1):
                    for j in range(i):
                        c[i] += c[j] * c[i-1-j]
                return c[n]
            
            self.sequence = [catalan(n) for n in range(6)]
            self.next_terms = [catalan(6), catalan(7)]
            self.pattern_description = "Catalan numbers"
            self.pattern_formula = "C_n = (2n)! / ((n+1)! * n!)"
            
        elif seq_type == "lucas":
            # Lucas numbers (similar to Fibonacci)
            lucas = [2, 1]
            for i in range(2, 8):
                lucas.append(lucas[i-1] + lucas[i-2])
            
            self.sequence = lucas[:6]
            self.next_terms = lucas[6:8]
            self.pattern_description = "Lucas numbers: L_n = L_{n-1} + L_{n-2}"
            self.pattern_formula = "L_n = L_{n-1} + L_{n-2}, L_0=2, L_1=1"
        
        self.solution = str(self.next_terms[0])
    
    def _analyze_sequence(self):
        """Analyze the sequence and generate analysis steps"""
        self.analysis_steps = []
        
        # Basic sequence info
        self.analysis_steps.append(f"Sequence: {', '.join(map(str, self.sequence))}")
        
        # Calculate differences
        if len(self.sequence) >= 3:
            diffs = [self.sequence[i+1] - self.sequence[i] for i in range(len(self.sequence)-1)]
            self.analysis_steps.append(f"First differences: {', '.join(map(str, diffs))}")
            
            # Second differences for polynomial detection
            if len(diffs) >= 3:
                second_diffs = [diffs[i+1] - diffs[i] for i in range(len(diffs)-1)]
                self.analysis_steps.append(f"Second differences: {', '.join(map(str, second_diffs))}")
        
        # Calculate ratios for geometric detection
        if all(x > 0 for x in self.sequence):
            ratios = [self.sequence[i+1] / self.sequence[i] for i in range(len(self.sequence)-1)]
            self.analysis_steps.append(f"Ratios: {', '.join(f'{r:.2f}' for r in ratios)}")
        
        # Pattern analysis
        self.analysis_steps.append(f"Pattern type: {self.sequence_category}")
        self.analysis_steps.append(f"Description: {self.pattern_description}")
    
    def _generate_hints(self):
        """Generate hints for the puzzle"""
        # Hint 1: Sequence category
        self.add_hint(1, f"Category: {self.sequence_category.title()} sequence", 100)
        
        # Hint 2: Analysis method
        if self.difficulty.value >= 2:
            method_hints = {
                "arithmetic": "Look at the differences between consecutive terms",
                "geometric": "Look at the ratios between consecutive terms",
                "polynomial": "Check first and second differences",
                "special": "This is a well-known mathematical sequence"
            }
            self.add_hint(2, method_hints.get(self.sequence_category, "Analyze the pattern"), 150)
        
        # Hint 3: Formula type
        if self.difficulty.value >= 3:
            self.add_hint(3, f"Formula pattern: {self.pattern_formula}", 200)
        
        # Hint 4: Pattern description
        if self.difficulty.value >= 4:
            self.add_hint(4, self.pattern_description, 250)
        
        # Hint 5: Direct answer
        if self.difficulty.value >= 4:
            self.add_hint(5, f"Next term: {self.solution}", 350)
    
    def validate_input(self, player_input: str) -> Tuple[bool, str]:
        """Validate player's answer"""
        try:
            player_value = int(player_input.strip())
            correct_value = int(self.solution)
            
            if player_value == correct_value:
                return True, f"🎯 Correct! The next term is {correct_value}."
            
            # Check if they got the second next term instead
            if len(self.next_terms) > 1 and player_value == self.next_terms[1]:
                return False, f"That's the term after next! The immediate next term is {correct_value}."
            
            # Check if close (for calculation errors)
            if abs(player_value - correct_value) <= max(1, correct_value * 0.1):
                return False, f"Very close! Check your calculation. Expected: {correct_value}"
            
            return False, f"Incorrect. The next term should be {correct_value}."
            
        except ValueError:
            return False, "Please enter a valid number."
    
    def get_current_display(self) -> List[str]:
        """Get the current puzzle display"""
        lines = []
        
        # Header
        lines.append(f"[bold cyan]🔢 MATHEMATICAL SEQUENCE - {self.sequence_category.upper()}[/bold cyan]")
        lines.append("=" * 60)
        lines.append("")
        
        # Puzzle info
        lines.append(f"[yellow]Category:[/yellow] {self.sequence_category.title()}")
        lines.append(f"[yellow]Difficulty:[/yellow] {self.difficulty.name}")
        lines.append("")
        
        # Display sequence
        lines.append("[cyan]═══ SEQUENCE ANALYSIS ═══[/cyan]")
        lines.append("")
        
        # Show sequence with question mark for next term
        sequence_display = ", ".join(map(str, self.sequence))
        lines.append(f"Sequence: [green]{sequence_display}[/green], [red]?[/red]")
        lines.append("")
        
        # Show analysis steps for harder difficulties
        if self.difficulty.value >= 3:
            lines.append("[cyan]═══ ANALYSIS STEPS ═══[/cyan]")
            for step in self.analysis_steps[:3]:  # Show first 3 steps
                lines.append(f"• {step}")
            lines.append("")
        
        # Pattern information
        if self.difficulty.value <= 2:
            lines.append("[cyan]═══ PATTERN HINTS ═══[/cyan]")
            if self.sequence_category == "arithmetic":
                lines.append("• Arithmetic sequences have constant differences")
                lines.append("• Look for: a, a+d, a+2d, a+3d, ...")
            elif self.sequence_category == "geometric":
                lines.append("• Geometric sequences have constant ratios")
                lines.append("• Look for: a, a×r, a×r², a×r³, ...")
            elif self.sequence_category == "polynomial":
                lines.append("• Polynomial sequences involve powers of n")
                lines.append("• Check second differences for quadratic patterns")
            else:
                lines.append("• Special sequences follow unique mathematical rules")
            lines.append("")
        
        # Instructions
        lines.append("[green]Instructions:[/green]")
        lines.append("• Analyze the pattern in the sequence")
        lines.append("• Determine the mathematical rule")
        lines.append("• Calculate the next term in the sequence")
        lines.append("• Use [yellow]HINT[/yellow] for guidance on analysis methods")
        
        return lines
    
    def get_progress_display(self) -> List[str]:
        """Get progress indicators"""
        lines = []
        
        lines.append("[cyan]═══ SEQUENCE ANALYSIS PROGRESS ═══[/cyan]")
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
        
        lines.append(f"[yellow]Sequence Category:[/yellow] {self.sequence_category.title()}")
        lines.append(f"[yellow]Terms Given:[/yellow] {len(self.sequence)}")
        
        # Show pattern complexity
        complexity_levels = {
            "arithmetic": "Linear Pattern",
            "geometric": "Exponential Pattern", 
            "polynomial": "Polynomial Pattern",
            "special": "Special Mathematical Sequence"
        }
        complexity = complexity_levels.get(self.sequence_category, "Unknown Pattern")
        lines.append(f"[yellow]Pattern Type:[/yellow] {complexity}")
        
        return lines
    
    def start(self) -> bool:
        """Start the puzzle (compatibility method)"""
        return self.start_puzzle()
    
    def _on_puzzle_start(self) -> None:
        """Called when puzzle starts"""
        self.current_progress['sequence_category'] = self.sequence_category
        self.current_progress['sequence'] = self.sequence
        self.current_progress['analysis_steps'] = self.analysis_steps
        self.current_progress['start_time'] = time.time()
    
    def _on_puzzle_complete(self, result: PuzzleResult) -> None:
        """Called when puzzle completes"""
        self.current_progress['completion_time'] = time.time()
        self.current_progress['final_score'] = result.score
        self.current_progress['pattern_identified'] = result.success
        self.current_progress['pattern_description'] = self.pattern_description 