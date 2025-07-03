"""
Rule Inference Puzzle for The Signal Cartographer
Players deduce logical rules from examples and apply them
"""

from typing import Any, Dict, List, Tuple, Optional
import random
import time

from ..puzzle_base import BasePuzzle, PuzzleResult, PuzzleDifficulty, generate_puzzle_id
from .logic_library import LogicLibrary
from .logic_tools import LogicSolver


class RuleInferencePuzzle(BasePuzzle):
    """
    Rule inference puzzle where players must deduce patterns from examples
    and apply them to new situations
    """
    
    def __init__(self, 
                 difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL,
                 signal_data: Any = None,
                 rule_type: str = "pattern"):
        """
        Initialize rule inference puzzle
        
        Args:
            difficulty: Puzzle difficulty level
            signal_data: Associated signal data
            rule_type: Type of rule (pattern, sequence, transformation, conditional)
        """
        
        self.logic_library = LogicLibrary()
        self.logic_solver = LogicSolver()
        self.rule_type = rule_type
        self.examples: List[Tuple[str, str]] = []  # (input, output) pairs
        self.test_cases: List[str] = []  # inputs to apply rule to
        self.rule_description = ""
        self.hidden_rule = {}
        
        # Calculate difficulty parameters
        max_attempts = max(3, 7 - difficulty.value)
        time_limit = None
        if difficulty.value >= 3:
            time_limit = 300 - (difficulty.value - 3) * 50  # 300, 250, 200, 150 seconds
        
        super().__init__(
            puzzle_id=generate_puzzle_id(),
            name=f"Rule Inference - {rule_type.title()}",
            description=f"Deduce logical rules from examples",
            difficulty=difficulty,
            max_attempts=max_attempts,
            time_limit=time_limit,
            signal_data=signal_data
        )
    
    def _initialize_puzzle(self) -> None:
        """Initialize the rule inference puzzle"""
        # Select rule type based on difficulty and variant
        if self.rule_type == "pattern":
            self._generate_pattern_rule()
        elif self.rule_type == "sequence":
            self._generate_sequence_rule()
        elif self.rule_type == "transformation":
            self._generate_transformation_rule()
        elif self.rule_type == "conditional":
            self._generate_conditional_rule()
        else:
            self._generate_pattern_rule()  # Default
        
        # Generate hints
        self._generate_hints()
        
        # Calculate max score
        self.max_score = 500 + (self.difficulty.value - 1) * 250
    
    def _generate_pattern_rule(self):
        """Generate pattern-based rule inference"""
        patterns = {
            1: {  # Easy - simple string patterns
                "rule": "Add 'X' to end if input has even length",
                "examples": [("AB", "ABX"), ("ABCD", "ABCDX"), ("A", "A"), ("ABC", "ABC")],
                "test": "SIGNAL",
                "answer": "SIGNALX"
            },
            2: {  # Medium - character transformation
                "rule": "Replace vowels with numbers: A=1, E=2, I=3, O=4, U=5",
                "examples": [("HELLO", "H2LL4"), ("CAT", "C1T"), ("BYTE", "BYT2")],
                "test": "AUDIO",
                "answer": "15D34"
            },
            3: {  # Hard - position-based rules
                "rule": "Reverse string if first char is consonant, otherwise add first char to end",
                "examples": [("BRAIN", "NIARB"), ("AUDIO", "AUDIOA"), ("HELP", "PLEH")],
                "test": "ECHO",
                "answer": "ECHOE"
            }
        }
        
        difficulty_level = min(self.difficulty.value // 2 + 1, 3)
        pattern = patterns[difficulty_level]
        
        self.rule_description = pattern["rule"]
        self.examples = pattern["examples"]
        self.test_cases = [pattern["test"]]
        self.solution = pattern["answer"]
        self.hidden_rule = {"type": "pattern", "level": difficulty_level}
    
    def _generate_sequence_rule(self):
        """Generate sequence-based rule inference"""
        sequences = {
            1: {  # Easy - arithmetic progression
                "rule": "Add 3 to each number",
                "examples": [("1", "4"), ("5", "8"), ("10", "13"), ("7", "10")],
                "test": "15",
                "answer": "18"
            },
            2: {  # Medium - fibonacci-like
                "rule": "Sum of previous two digits",
                "examples": [("12", "3"), ("23", "5"), ("34", "7"), ("45", "9")],
                "test": "67",
                "answer": "13"
            },
            3: {  # Hard - modular arithmetic
                "rule": "Result = (input * 2 + 1) mod 10",
                "examples": [("3", "7"), ("5", "1"), ("8", "7"), ("2", "5")],
                "test": "9",
                "answer": "9"
            }
        }
        
        difficulty_level = min(self.difficulty.value // 2 + 1, 3)
        sequence = sequences[difficulty_level]
        
        self.rule_description = sequence["rule"]
        self.examples = sequence["examples"]
        self.test_cases = [sequence["test"]]
        self.solution = sequence["answer"]
        self.hidden_rule = {"type": "sequence", "level": difficulty_level}
    
    def _generate_transformation_rule(self):
        """Generate transformation-based rule inference"""
        transformations = {
            1: {  # Easy - case transformation
                "rule": "Uppercase if input length > 3, otherwise lowercase",
                "examples": [("cat", "cat"), ("HELLO", "HELLO"), ("DOG", "dog"), ("SIGNAL", "SIGNAL")],
                "test": "Code",
                "answer": "CODE"
            },
            2: {  # Medium - character shifting
                "rule": "Shift each letter forward by its position (A+1=B, B+2=D, etc.)",
                "examples": [("ABC", "BDF"), ("CAT", "DDW"), ("HI", "IK")],
                "test": "BAD",
                "answer": "BCD"
            },
            3: {  # Hard - complex transformation
                "rule": "Encode: consonants -> next consonant, vowels -> previous vowel",
                "examples": [("CAT", "DBU"), ("HELLO", "IAMMO"), ("BYTE", "CZUA")],
                "test": "CODE",
                "answer": "DPDA"
            }
        }
        
        difficulty_level = min(self.difficulty.value // 2 + 1, 3)
        transformation = transformations[difficulty_level]
        
        self.rule_description = transformation["rule"]
        self.examples = transformation["examples"]
        self.test_cases = [transformation["test"]]
        self.solution = transformation["answer"]
        self.hidden_rule = {"type": "transformation", "level": difficulty_level}
    
    def _generate_conditional_rule(self):
        """Generate conditional logic rule inference"""
        conditions = {
            1: {  # Easy - simple if-then
                "rule": "If input contains 'A', output 'YES', otherwise 'NO'",
                "examples": [("CAT", "YES"), ("DOG", "NO"), ("WAVE", "YES"), ("BUZZ", "NO")],
                "test": "SIGNAL",
                "answer": "YES"
            },
            2: {  # Medium - multiple conditions
                "rule": "If length >= 4 and starts with consonant, output 'VALID', else 'INVALID'",
                "examples": [("HELLO", "VALID"), ("CAT", "INVALID"), ("AUDIO", "INVALID"), ("BYTE", "VALID")],
                "test": "CODE",
                "answer": "VALID"
            },
            3: {  # Hard - complex logic
                "rule": "Count vowels and consonants. If vowels > consonants, output 'V', if equal 'E', else 'C'",
                "examples": [("AUDIO", "V"), ("HELLO", "C"), ("BYTE", "E"), ("IDEA", "V")],
                "test": "WAVE",
                "answer": "E"
            }
        }
        
        difficulty_level = min(self.difficulty.value // 2 + 1, 3)
        condition = conditions[difficulty_level]
        
        self.rule_description = condition["rule"]
        self.examples = condition["examples"]
        self.test_cases = [condition["test"]]
        self.solution = condition["answer"]
        self.hidden_rule = {"type": "conditional", "level": difficulty_level}
    
    def _generate_hints(self):
        """Generate hints for the puzzle"""
        # Hint 1: Basic rule category
        category_hints = {
            "pattern": "Look for string manipulation patterns",
            "sequence": "Analyze numerical relationships",
            "transformation": "Examine character transformations",
            "conditional": "Consider conditional logic rules"
        }
        self.add_hint(1, f"Rule Category: {category_hints.get(self.rule_type, 'Pattern analysis')}", 75)
        
        # Hint 2: Number of examples
        if self.difficulty.value >= 2:
            self.add_hint(2, f"Study all {len(self.examples)} examples carefully", 100)
        
        # Hint 3: Specific guidance
        if self.difficulty.value >= 3:
            specific_hints = {
                "pattern": "Check input length and character properties",
                "sequence": "Look for mathematical operations",
                "transformation": "Examine position-based changes",
                "conditional": "Test different input characteristics"
            }
            self.add_hint(3, specific_hints.get(self.rule_type, "Look for patterns"), 150)
        
        # Hint 4: Rule insight
        if self.difficulty.value >= 4:
            rule_parts = self.rule_description.split()
            partial_hint = " ".join(rule_parts[:len(rule_parts)//2]) + "..."
            self.add_hint(4, f"Rule starts with: {partial_hint}", 200)
        
        # Hint 5: Full rule
        if self.difficulty.value >= 4:
            self.add_hint(5, f"Complete rule: {self.rule_description}", 300)
    
    def validate_input(self, player_input: str) -> Tuple[bool, str]:
        """Validate player's answer"""
        player_input = player_input.strip()
        
        # Check direct answer
        if player_input.upper() == self.solution.upper():
            return True, f"🎯 Correct! You successfully deduced the rule and applied it."
        
        # Check if close for partial credit feedback
        if len(player_input) == len(self.solution):
            similarity = sum(1 for a, b in zip(player_input.upper(), self.solution.upper()) if a == b)
            if similarity >= len(self.solution) * 0.7:
                return False, f"Very close! {similarity}/{len(self.solution)} characters correct."
        
        return False, f"Incorrect. The expected answer was '{self.solution}'. Review the examples for the pattern."
    
    def get_current_display(self) -> List[str]:
        """Get the current puzzle display"""
        lines = []
        
        # Header
        lines.append(f"[bold cyan]🧠 RULE INFERENCE - {self.rule_type.upper()}[/bold cyan]")
        lines.append("=" * 60)
        lines.append("")
        
        # Puzzle info
        lines.append(f"[yellow]Task:[/yellow] Deduce the rule from examples and apply it")
        lines.append(f"[yellow]Difficulty:[/yellow] {self.difficulty.name}")
        lines.append("")
        
        # Examples
        lines.append("[cyan]═══ EXAMPLES ═══[/cyan]")
        lines.append("Study these input → output examples:")
        lines.append("")
        
        for i, (input_val, output_val) in enumerate(self.examples, 1):
            lines.append(f"[white]{i}.[/white] [green]{input_val}[/green] → [blue]{output_val}[/blue]")
        
        lines.append("")
        
        # Test case
        lines.append("[cyan]═══ APPLY THE RULE ═══[/cyan]")
        lines.append("What should be the output for this input?")
        lines.append("")
        lines.append(f"Input: [green]{self.test_cases[0]}[/green]")
        lines.append("Output: [red]???[/red]")
        lines.append("")
        
        # Instructions
        lines.append("[green]Instructions:[/green]")
        lines.append("• Analyze the pattern in the examples")
        lines.append(f"• Determine the rule that transforms input → output")
        lines.append(f"• Apply the rule to '{self.test_cases[0]}'")
        lines.append("• Use [yellow]HINT[/yellow] if you need guidance")
        
        return lines
    
    def get_progress_display(self) -> List[str]:
        """Get progress indicators"""
        lines = []
        
        lines.append("[cyan]═══ DEDUCTION PROGRESS ═══[/cyan]")
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
        
        lines.append(f"[yellow]Rule Type:[/yellow] {self.rule_type.title()}")
        lines.append(f"[yellow]Examples Count:[/yellow] {len(self.examples)}")
        
        return lines
    
    def start(self) -> bool:
        """Start the puzzle (compatibility method)"""
        return self.start_puzzle()
    
    def _on_puzzle_start(self) -> None:
        """Called when puzzle starts"""
        self.current_progress['rule_type'] = self.rule_type
        self.current_progress['examples'] = self.examples
        self.current_progress['test_case'] = self.test_cases[0]
        self.current_progress['start_time'] = time.time()
    
    def _on_puzzle_complete(self, result: PuzzleResult) -> None:
        """Called when puzzle completes"""
        self.current_progress['completion_time'] = time.time()
        self.current_progress['final_score'] = result.score
        self.current_progress['rule_deduced'] = result.success
        self.current_progress['hidden_rule'] = self.hidden_rule 