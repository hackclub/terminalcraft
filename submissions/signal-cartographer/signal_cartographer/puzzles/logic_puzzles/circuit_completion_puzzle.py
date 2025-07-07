"""
Circuit Completion Puzzle for The Signal Cartographer
Players analyze ASCII logic circuits and determine outputs
"""

from typing import Any, Dict, List, Tuple, Optional
import random
import time

from ..puzzle_base import BasePuzzle, PuzzleResult, PuzzleDifficulty, generate_puzzle_id
from .logic_library import LogicLibrary, LogicPuzzleData
from .logic_tools import LogicSolver, LogicResult


class CircuitCompletionPuzzle(BasePuzzle):
    """
    Circuit completion puzzle where players analyze digital logic circuits
    and determine the output values
    """
    
    def __init__(self, 
                 difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL,
                 signal_data: Any = None,
                 circuit_type: str = None):
        """
        Initialize circuit completion puzzle
        
        Args:
            difficulty: Puzzle difficulty level
            signal_data: Associated signal data
            circuit_type: Specific circuit type (overrides random selection)
        """
        
        self.logic_library = LogicLibrary()
        self.logic_solver = LogicSolver()
        self.circuit_type = circuit_type
        self.circuit_pattern: List[str] = []
        self.inputs: Dict[str, int] = {}
        self.correct_output: int = 0
        self.choices: List[int] = []
        
        # Calculate difficulty parameters
        max_attempts = max(3, 5 - difficulty.value)
        time_limit = None
        if difficulty.value >= 3:
            time_limit = 180 - (difficulty.value - 3) * 30  # 180, 150, 120, 90 seconds
        
        super().__init__(
            puzzle_id=generate_puzzle_id(),
            name=f"Digital Logic Circuit Analysis",
            description=f"Analyze logic circuits and determine output values",
            difficulty=difficulty,
            max_attempts=max_attempts,
            time_limit=time_limit,
            signal_data=signal_data
        )
    
    def _initialize_puzzle(self) -> None:
        """Initialize the circuit completion puzzle"""
        # Select circuit type based on difficulty
        if not self.circuit_type:
            self.circuit_type = self._select_circuit_type()
        
        # Get circuit pattern
        self.circuit_pattern = self.logic_library.get_circuit_pattern(self.circuit_type)
        
        # Generate inputs
        self._generate_inputs()
        
        # Calculate correct output
        self._calculate_output()
        
        # Set solution
        self.solution = str(self.correct_output)
        
        # Generate multiple choice options
        self._generate_choices()
        
        # Generate hints
        self._generate_hints()
        
        # Calculate max score
        self.max_score = 300 + (self.difficulty.value - 1) * 150
    
    def _select_circuit_type(self) -> str:
        """Select appropriate circuit type based on difficulty"""
        if self.difficulty == PuzzleDifficulty.TRIVIAL:
            return random.choice(["and_gate", "or_gate", "not_gate"])
        elif self.difficulty == PuzzleDifficulty.EASY:
            return random.choice(["and_gate", "or_gate", "not_gate", "xor_gate"])
        elif self.difficulty == PuzzleDifficulty.NORMAL:
            return random.choice(["and_gate", "or_gate", "xor_gate", "complex_circuit"])
        elif self.difficulty == PuzzleDifficulty.HARD:
            return random.choice(["xor_gate", "complex_circuit"])
        else:  # EXPERT, NIGHTMARE
            return "complex_circuit"
    
    def _generate_inputs(self):
        """Generate input values based on circuit type"""
        if self.circuit_type == "not_gate":
            self.inputs = {"A": random.randint(0, 1)}
        elif self.circuit_type in ["and_gate", "or_gate", "xor_gate"]:
            self.inputs = {
                "A": random.randint(0, 1),
                "B": random.randint(0, 1)
            }
        elif self.circuit_type == "complex_circuit":
            self.inputs = {
                "A": random.randint(0, 1),
                "B": random.randint(0, 1),
                "C": random.randint(0, 1),
                "D": random.randint(0, 1)
            }
        else:
            # Default two inputs
            self.inputs = {
                "A": random.randint(0, 1),
                "B": random.randint(0, 1)
            }
    
    def _calculate_output(self):
        """Calculate the correct output using logic solver"""
        result = self.logic_solver.solve_circuit_logic(self.circuit_type, self.inputs)
        if result.success and result.alternative_solutions:
            self.correct_output = result.alternative_solutions[0]
        else:
            # Fallback calculation
            self.correct_output = self._manual_calculation()
    
    def _manual_calculation(self) -> int:
        """Manual calculation as fallback"""
        if self.circuit_type == "and_gate":
            return self.inputs.get("A", 0) & self.inputs.get("B", 0)
        elif self.circuit_type == "or_gate":
            return self.inputs.get("A", 0) | self.inputs.get("B", 0)
        elif self.circuit_type == "not_gate":
            return 1 - self.inputs.get("A", 0)
        elif self.circuit_type == "xor_gate":
            return self.inputs.get("A", 0) ^ self.inputs.get("B", 0)
        elif self.circuit_type == "complex_circuit":
            # (A AND B) OR C OR D
            a, b, c, d = (self.inputs.get(k, 0) for k in ["A", "B", "C", "D"])
            return (a & b) | c | d
        else:
            return 0
    
    def _generate_choices(self):
        """Generate multiple choice options"""
        self.choices = [self.correct_output]
        
        # Add the opposite value
        opposite = 1 - self.correct_output
        if opposite not in self.choices:
            self.choices.append(opposite)
        
        # For multi-input circuits, add other possible combinations
        if len(self.inputs) > 1:
            # Add results from different logic operations
            a, b = (self.inputs.get(k, 0) for k in ["A", "B"])
            alternatives = [
                a & b,    # AND
                a | b,    # OR  
                a ^ b,    # XOR
                ~a & 1,   # NOT A
                ~b & 1    # NOT B
            ]
            
            for alt in alternatives:
                if alt not in self.choices and 0 <= alt <= 1:
                    self.choices.append(alt)
        
        # Ensure we have at least 2 choices
        if len(self.choices) == 1:
            self.choices.append(1 - self.choices[0])
        
        # Shuffle choices and create mapping
        random.shuffle(self.choices)
        self.choice_mapping = {str(i+1): choice for i, choice in enumerate(self.choices)}
    
    def _generate_hints(self):
        """Generate hints for the puzzle"""
        # Hint 1: Gate type explanation
        gate_hint = self._get_gate_explanation()
        self.add_hint(1, gate_hint, 30)
        
        # Hint 2: Input values
        input_str = ", ".join([f"{k}={v}" for k, v in self.inputs.items()])
        self.add_hint(2, f"Input values: {input_str}", 60)
        
        # Hint 3: Logic operation breakdown
        if self.difficulty.value >= 3:
            operation_hint = self._get_operation_breakdown()
            self.add_hint(3, operation_hint, 90)
        
        # Hint 4: Step-by-step calculation
        if self.difficulty.value >= 4:
            calculation_hint = self._get_step_by_step_calculation()
            self.add_hint(4, calculation_hint, 120)
        
        # Hint 5: Direct answer
        if self.difficulty.value >= 4:
            self.add_hint(5, f"The output is {self.correct_output}", 150)
    
    def _get_gate_explanation(self) -> str:
        """Get explanation of the gate type"""
        if self.circuit_type == "and_gate":
            return "AND gate: Output is 1 only if ALL inputs are 1"
        elif self.circuit_type == "or_gate":
            return "OR gate: Output is 1 if ANY input is 1"
        elif self.circuit_type == "not_gate":
            return "NOT gate: Output is the inverse of the input"
        elif self.circuit_type == "xor_gate":
            return "XOR gate: Output is 1 if inputs are DIFFERENT"
        elif self.circuit_type == "complex_circuit":
            return "Complex circuit: Multiple gates combined"
        else:
            return "Digital logic circuit with boolean operations"
    
    def _get_operation_breakdown(self) -> str:
        """Get breakdown of the logical operation"""
        if self.circuit_type == "and_gate":
            a, b = self.inputs.get("A", 0), self.inputs.get("B", 0)
            return f"AND operation: {a} AND {b}"
        elif self.circuit_type == "or_gate":
            a, b = self.inputs.get("A", 0), self.inputs.get("B", 0)
            return f"OR operation: {a} OR {b}"
        elif self.circuit_type == "not_gate":
            a = self.inputs.get("A", 0)
            return f"NOT operation: NOT {a}"
        elif self.circuit_type == "xor_gate":
            a, b = self.inputs.get("A", 0), self.inputs.get("B", 0)
            return f"XOR operation: {a} XOR {b}"
        elif self.circuit_type == "complex_circuit":
            return "Trace signal flow through each gate step by step"
        else:
            return "Apply the logic operation to the inputs"
    
    def _get_step_by_step_calculation(self) -> str:
        """Get step-by-step calculation"""
        if self.circuit_type == "and_gate":
            a, b = self.inputs.get("A", 0), self.inputs.get("B", 0)
            return f"Step: {a} AND {b} = {a & b}"
        elif self.circuit_type == "or_gate":
            a, b = self.inputs.get("A", 0), self.inputs.get("B", 0)
            return f"Step: {a} OR {b} = {a | b}"
        elif self.circuit_type == "not_gate":
            a = self.inputs.get("A", 0)
            return f"Step: NOT {a} = {1 - a}"
        elif self.circuit_type == "xor_gate":
            a, b = self.inputs.get("A", 0), self.inputs.get("B", 0)
            return f"Step: {a} XOR {b} = {a ^ b}"
        elif self.circuit_type == "complex_circuit":
            a, b, c, d = (self.inputs.get(k, 0) for k in ["A", "B", "C", "D"])
            temp1 = a & b
            temp2 = temp1 | c
            final = temp2 | d
            return f"Steps: ({a} AND {b})={temp1}, ({temp1} OR {c})={temp2}, ({temp2} OR {d})={final}"
        else:
            return "Follow the circuit logic step by step"
    
    def validate_input(self, player_input: str) -> Tuple[bool, str]:
        """Validate player's answer"""
        player_input = player_input.strip()
        
        # Check multiple choice number
        if player_input.isdigit() and player_input in self.choice_mapping:
            selected_value = self.choice_mapping[player_input]
            if selected_value == self.correct_output:
                return True, f"🔌 Correct! The circuit output is {self.correct_output}!"
            else:
                return False, f"Incorrect. Output {selected_value} doesn't match the logic."
        
        # Check direct binary input
        if player_input in ["0", "1"]:
            input_value = int(player_input)
            if input_value == self.correct_output:
                return True, f"🔌 Excellent! The circuit output is {self.correct_output}!"
            else:
                return False, f"Incorrect. Output {input_value} doesn't match the circuit logic."
        
        return False, f"Invalid input. Enter 0 or 1, or choice 1-{len(self.choices)}."
    
    def get_current_display(self) -> List[str]:
        """Get the current puzzle display"""
        lines = []
        
        # Header
        lines.append(f"[bold cyan]🔌 DIGITAL LOGIC CIRCUIT ANALYSIS[/bold cyan]")
        lines.append("=" * 60)
        lines.append("")
        
        # Puzzle info
        lines.append(f"[yellow]Circuit Type:[/yellow] {self.circuit_type.replace('_', ' ').title()}")
        lines.append(f"[yellow]Difficulty:[/yellow] {self.difficulty.name}")
        lines.append(f"[yellow]Input Count:[/yellow] {len(self.inputs)} signal(s)")
        lines.append("")
        
        # Display circuit diagram
        lines.append("[cyan]═══ CIRCUIT DIAGRAM ═══[/cyan]")
        for line in self.circuit_pattern:
            lines.append(line)
        lines.append("")
        
        # Display inputs
        lines.append("[cyan]═══ INPUT VALUES ═══[/cyan]")
        for input_name, value in self.inputs.items():
            signal_indicator = "HIGH" if value == 1 else "LOW"
            lines.append(f"Input {input_name}: {value} ({signal_indicator})")
        lines.append("")
        
        # Logic explanation (for easier difficulties)
        if self.difficulty.value <= 3:
            lines.append("[cyan]═══ LOGIC REFERENCE ═══[/cyan]")
            if self.circuit_type == "and_gate":
                lines.append("AND: Output = 1 only if ALL inputs = 1")
                lines.append("Truth table: 0&0=0, 0&1=0, 1&0=0, 1&1=1")
            elif self.circuit_type == "or_gate":
                lines.append("OR: Output = 1 if ANY input = 1")
                lines.append("Truth table: 0|0=0, 0|1=1, 1|0=1, 1|1=1")
            elif self.circuit_type == "not_gate":
                lines.append("NOT: Output = opposite of input")
                lines.append("Truth table: NOT 0 = 1, NOT 1 = 0")
            elif self.circuit_type == "xor_gate":
                lines.append("XOR: Output = 1 if inputs are different")
                lines.append("Truth table: 0^0=0, 0^1=1, 1^0=1, 1^1=0")
            lines.append("")
        
        # Output options
        lines.append("[cyan]═══ OUTPUT OPTIONS ═══[/cyan]")
        for i, choice in enumerate(self.choices, 1):
            signal_state = "HIGH" if choice == 1 else "LOW"
            lines.append(f"[white]{i}.[/white] {choice} ({signal_state})")
        lines.append("")
        
        # Instructions
        lines.append("[green]Instructions:[/green]")
        lines.append("• Analyze the logic circuit and input values")
        lines.append(f"• Enter the number (1-{len(self.choices)}) or type 0/1 directly")
        lines.append("• Use [yellow]HINT[/yellow] command for logic analysis help")
        lines.append("• Trace signal flow through each gate")
        
        return lines
    
    def get_progress_display(self) -> List[str]:
        """Get progress indicators"""
        lines = []
        
        lines.append("[cyan]═══ CIRCUIT PROGRESS ═══[/cyan]")
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
        
        # Circuit analysis
        lines.append(f"[yellow]Circuit Type:[/yellow] {self.circuit_type.replace('_', ' ').title()}")
        lines.append(f"[yellow]Gate Count:[/yellow] {self._count_gates()}")
        lines.append(f"[yellow]Complexity:[/yellow] {self._get_complexity_level()}")
        
        return lines
    
    def _count_gates(self) -> int:
        """Count number of logic gates in circuit"""
        if self.circuit_type in ["and_gate", "or_gate", "not_gate", "xor_gate"]:
            return 1
        elif self.circuit_type == "complex_circuit":
            return 3  # AND + OR + OR
        else:
            return 1
    
    def _get_complexity_level(self) -> str:
        """Get complexity level description"""
        if self.circuit_type in ["and_gate", "or_gate"]:
            return "Basic"
        elif self.circuit_type in ["not_gate", "xor_gate"]:
            return "Simple"
        elif self.circuit_type == "complex_circuit":
            return "Complex"
        else:
            return "Standard"
    
    def _on_puzzle_start(self) -> None:
        """Called when puzzle starts"""
        self.current_progress['circuit_type'] = self.circuit_type
        self.current_progress['inputs'] = self.inputs
        self.current_progress['correct_output'] = self.correct_output
        self.current_progress['start_time'] = time.time()
    
    def _on_puzzle_complete(self, result: PuzzleResult) -> None:
        """Called when puzzle completes"""
        self.current_progress['completion_time'] = time.time()
        self.current_progress['final_score'] = result.score
        self.current_progress['circuit_solved'] = result.success
        self.current_progress['analysis_methods_used'] = self.hints_used 