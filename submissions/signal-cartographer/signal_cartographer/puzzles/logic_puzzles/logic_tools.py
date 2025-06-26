"""
Logic Tools and Analysis Utilities
Provides logical reasoning tools and puzzle solving algorithms
"""

from typing import Dict, List, Tuple, Optional, Any, Set
import random
from dataclasses import dataclass


@dataclass
class LogicResult:
    """Data structure for logic analysis results"""
    success: bool
    explanation: str
    confidence: float  # 0.0 to 1.0
    alternative_solutions: List[Any]
    analysis_steps: List[str]


class SequenceAnalyzer:
    """Analyze and solve mathematical sequence puzzles"""
    
    def __init__(self):
        self.known_patterns = {
            "arithmetic": self._analyze_arithmetic,
            "geometric": self._analyze_geometric,
            "fibonacci": self._analyze_fibonacci,
            "polynomial": self._analyze_polynomial,
            "prime": self._analyze_prime,
            "factorial": self._analyze_factorial
        }
    
    def analyze_sequence(self, sequence: List[int]) -> LogicResult:
        """Analyze a sequence to determine its pattern"""
        if len(sequence) < 3:
            return LogicResult(False, "Insufficient data", 0.0, [], ["Need at least 3 elements"])
        
        results = []
        analysis_steps = []
        
        # Try each pattern type
        for pattern_name, analyzer in self.known_patterns.items():
            try:
                result = analyzer(sequence)
                if result.success:
                    results.append((pattern_name, result))
                analysis_steps.extend(result.analysis_steps)
            except Exception as e:
                analysis_steps.append(f"Error analyzing {pattern_name}: {str(e)}")
        
        if not results:
            return LogicResult(False, "No clear pattern detected", 0.0, [], analysis_steps)
        
        # Sort by confidence
        results.sort(key=lambda x: x[1].confidence, reverse=True)
        best_pattern, best_result = results[0]
        
        return LogicResult(
            True,
            f"Detected {best_pattern} pattern: {best_result.explanation}",
            best_result.confidence,
            [alt[1] for alt in results[1:]],
            analysis_steps
        )
    
    def _analyze_arithmetic(self, sequence: List[int]) -> LogicResult:
        """Analyze arithmetic progression"""
        if len(sequence) < 2:
            return LogicResult(False, "Need at least 2 elements", 0.0, [], [])
        
        differences = [sequence[i+1] - sequence[i] for i in range(len(sequence)-1)]
        
        if all(d == differences[0] for d in differences):
            diff = differences[0]
            next_val = sequence[-1] + diff
            return LogicResult(
                True,
                f"Arithmetic with common difference {diff}, next: {next_val}",
                0.95,
                [next_val],
                [f"Differences: {differences}", f"Common difference: {diff}"]
            )
        
        return LogicResult(False, "Not arithmetic", 0.0, [], [f"Differences not constant: {differences}"])
    
    def _analyze_geometric(self, sequence: List[int]) -> LogicResult:
        """Analyze geometric progression"""
        if len(sequence) < 2 or any(x == 0 for x in sequence):
            return LogicResult(False, "Invalid for geometric", 0.0, [], [])
        
        ratios = [sequence[i+1] / sequence[i] for i in range(len(sequence)-1)]
        
        # Check if ratios are approximately equal (allowing small floating point errors)
        if all(abs(r - ratios[0]) < 0.001 for r in ratios):
            ratio = ratios[0]
            next_val = int(sequence[-1] * ratio)
            return LogicResult(
                True,
                f"Geometric with ratio {ratio:.2f}, next: {next_val}",
                0.90,
                [next_val],
                [f"Ratios: {ratios}", f"Common ratio: {ratio}"]
            )
        
        return LogicResult(False, "Not geometric", 0.0, [], [f"Ratios not constant: {ratios}"])
    
    def _analyze_fibonacci(self, sequence: List[int]) -> LogicResult:
        """Analyze Fibonacci-like sequence"""
        if len(sequence) < 3:
            return LogicResult(False, "Need at least 3 elements", 0.0, [], [])
        
        # Check if each element is sum of previous two
        fibonacci_checks = []
        for i in range(2, len(sequence)):
            expected = sequence[i-1] + sequence[i-2]
            fibonacci_checks.append(sequence[i] == expected)
        
        if all(fibonacci_checks):
            next_val = sequence[-1] + sequence[-2]
            return LogicResult(
                True,
                f"Fibonacci-like sequence, next: {next_val}",
                0.85,
                [next_val],
                ["Each term = sum of previous two", f"Next: {sequence[-1]} + {sequence[-2]} = {next_val}"]
            )
        
        return LogicResult(False, "Not Fibonacci-like", 0.0, [], ["Not all terms are sum of previous two"])
    
    def _analyze_polynomial(self, sequence: List[int]) -> LogicResult:
        """Analyze polynomial sequences (squares, cubes, etc.)"""
        if len(sequence) < 4:
            return LogicResult(False, "Need at least 4 elements", 0.0, [], [])
        
        # Check for perfect squares
        squares = [i*i for i in range(1, 20)]
        if sequence[:len(sequence)] == squares[:len(sequence)]:
            next_val = (len(sequence) + 1) ** 2
            return LogicResult(
                True,
                f"Perfect squares sequence, next: {next_val}",
                0.90,
                [next_val],
                ["Pattern: n²", f"Next: {len(sequence)+1}² = {next_val}"]
            )
        
        # Check for cubes
        cubes = [i*i*i for i in range(1, 15)]
        if sequence[:len(sequence)] == cubes[:len(sequence)]:
            next_val = (len(sequence) + 1) ** 3
            return LogicResult(
                True,
                f"Perfect cubes sequence, next: {next_val}",
                0.90,
                [next_val],
                ["Pattern: n³", f"Next: {len(sequence)+1}³ = {next_val}"]
            )
        
        return LogicResult(False, "Not a simple polynomial", 0.0, [], ["Not squares or cubes"])
    
    def _analyze_prime(self, sequence: List[int]) -> LogicResult:
        """Analyze prime number sequence"""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        
        if all(seq_val in primes for seq_val in sequence):
            # Find position in prime sequence
            try:
                last_index = primes.index(sequence[-1])
                if last_index + 1 < len(primes):
                    next_val = primes[last_index + 1]
                    return LogicResult(
                        True,
                        f"Prime number sequence, next: {next_val}",
                        0.80,
                        [next_val],
                        ["All numbers are prime", f"Next prime after {sequence[-1]} is {next_val}"]
                    )
            except ValueError:
                pass
        
        return LogicResult(False, "Not prime sequence", 0.0, [], ["Not all numbers are prime"])
    
    def _analyze_factorial(self, sequence: List[int]) -> LogicResult:
        """Analyze factorial sequence"""
        factorials = [1, 1, 2, 6, 24, 120, 720, 5040]
        
        if sequence[:len(sequence)] == factorials[:len(sequence)]:
            if len(sequence) < len(factorials):
                next_val = factorials[len(sequence)]
                return LogicResult(
                    True,
                    f"Factorial sequence, next: {next_val}",
                    0.85,
                    [next_val],
                    ["Pattern: n!", f"Next: {len(sequence)}! = {next_val}"]
                )
        
        return LogicResult(False, "Not factorial", 0.0, [], ["Not factorial sequence"])
    
    def predict_next(self, sequence: List[int], pattern_type: str = None) -> Optional[int]:
        """Predict next value in sequence"""
        if pattern_type:
            if pattern_type in self.known_patterns:
                result = self.known_patterns[pattern_type](sequence)
                if result.success and result.alternative_solutions:
                    return result.alternative_solutions[0]
        else:
            result = self.analyze_sequence(sequence)
            if result.success and result.alternative_solutions:
                return result.alternative_solutions[0]
        
        return None


class LogicSolver:
    """Collection of logic puzzle solving algorithms"""
    
    def __init__(self):
        self.sequence_analyzer = SequenceAnalyzer()
    
    def solve_mastermind(self, guesses: List[Tuple[List[int], int, int]], 
                        constraints: Dict[str, Any]) -> LogicResult:
        """Solve Mastermind puzzle given previous guesses"""
        length = constraints.get("length", 4)
        max_value = constraints.get("max_value", 6)
        
        # Generate all possible solutions
        possible_solutions = []
        for attempt in range(1000):  # Limit attempts to avoid infinite loops
            candidate = [random.randint(1, max_value) for _ in range(length)]
            
            # Check if candidate is consistent with all guesses
            is_valid = True
            for guess, bulls, cows in guesses:
                predicted_bulls, predicted_cows = self._calculate_bulls_cows(guess, candidate)
                if predicted_bulls != bulls or predicted_cows != cows:
                    is_valid = False
                    break
            
            if is_valid and candidate not in possible_solutions:
                possible_solutions.append(candidate[:])
            
            if len(possible_solutions) >= 10:  # Enough solutions found
                break
        
        if possible_solutions:
            return LogicResult(
                True,
                f"Found {len(possible_solutions)} possible solution(s)",
                0.8,
                possible_solutions,
                [f"Analyzed {len(guesses)} previous guesses", f"Solutions: {possible_solutions[:3]}..."]
            )
        else:
            return LogicResult(
                False,
                "No consistent solution found",
                0.0,
                [],
                ["No solution matches all guess feedback"]
            )
    
    def _calculate_bulls_cows(self, guess: List[int], solution: List[int]) -> Tuple[int, int]:
        """Calculate bulls and cows for Mastermind"""
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
    
    def solve_circuit_logic(self, circuit_type: str, inputs: Dict[str, int]) -> LogicResult:
        """Solve digital logic circuit puzzles"""
        try:
            if circuit_type == "and_gate":
                output = inputs.get('A', 0) & inputs.get('B', 0)
                explanation = f"AND gate: {inputs.get('A', 0)} AND {inputs.get('B', 0)} = {output}"
                
            elif circuit_type == "or_gate":
                output = inputs.get('A', 0) | inputs.get('B', 0)
                explanation = f"OR gate: {inputs.get('A', 0)} OR {inputs.get('B', 0)} = {output}"
                
            elif circuit_type == "not_gate":
                output = 1 - inputs.get('A', 0)
                explanation = f"NOT gate: NOT {inputs.get('A', 0)} = {output}"
                
            elif circuit_type == "xor_gate":
                output = inputs.get('A', 0) ^ inputs.get('B', 0)
                explanation = f"XOR gate: {inputs.get('A', 0)} XOR {inputs.get('B', 0)} = {output}"
                
            elif circuit_type == "complex_circuit":
                # A AND B -> temp1, temp1 OR C -> temp2, temp2 OR D -> output
                a, b, c, d = inputs.get('A', 0), inputs.get('B', 0), inputs.get('C', 0), inputs.get('D', 0)
                temp1 = a & b
                temp2 = temp1 | c
                output = temp2 | d
                explanation = f"Complex: ({a} AND {b}) OR {c} OR {d} = {output}"
                
            else:
                return LogicResult(False, f"Unknown circuit type: {circuit_type}", 0.0, [], [])
            
            return LogicResult(
                True,
                explanation,
                0.95,
                [output],
                [f"Input values: {inputs}", f"Circuit type: {circuit_type}", f"Output: {output}"]
            )
            
        except Exception as e:
            return LogicResult(False, f"Error solving circuit: {str(e)}", 0.0, [], [])
    
    def solve_grid_puzzle(self, grid: List[List[str]], puzzle_type: str) -> LogicResult:
        """Solve grid-based logic puzzles"""
        try:
            if puzzle_type == "sudoku_mini":
                return self._solve_mini_sudoku(grid)
            elif puzzle_type == "logic_grid_3x3":
                return self._solve_color_grid(grid)
            elif puzzle_type == "signal_grid":
                return self._solve_signal_grid(grid)
            else:
                return LogicResult(False, f"Unknown grid type: {puzzle_type}", 0.0, [], [])
                
        except Exception as e:
            return LogicResult(False, f"Error solving grid: {str(e)}", 0.0, [], [])
    
    def _solve_mini_sudoku(self, grid: List[List[str]]) -> LogicResult:
        """Solve 4x4 mini Sudoku"""
        # Simple brute force for 4x4
        for row in range(4):
            for col in range(4):
                if grid[row][col] == "?":
                    for num in ["1", "2", "3", "4"]:
                        if self._is_valid_sudoku_move(grid, row, col, num):
                            return LogicResult(
                                True,
                                f"Position ({row},{col}) should be {num}",
                                0.85,
                                [num],
                                [f"Checking position {row},{col}", f"Valid number: {num}"]
                            )
        
        return LogicResult(False, "No valid moves found", 0.0, [], ["Grid analysis complete"])
    
    def _is_valid_sudoku_move(self, grid: List[List[str]], row: int, col: int, num: str) -> bool:
        """Check if Sudoku move is valid"""
        # Check row
        for c in range(4):
            if c != col and grid[row][c] == num:
                return False
        
        # Check column
        for r in range(4):
            if r != row and grid[r][col] == num:
                return False
        
        return True
    
    def _solve_color_grid(self, grid: List[List[str]]) -> LogicResult:
        """Solve color pattern grid"""
        colors = ["R", "G", "B"]
        
        for row in range(len(grid)):
            for col in range(len(grid[0])):
                if grid[row][col] == "?":
                    for color in colors:
                        # Simple pattern check - no adjacent same colors
                        if self._is_valid_color_placement(grid, row, col, color):
                            return LogicResult(
                                True,
                                f"Position ({row},{col}) should be {color}",
                                0.80,
                                [color],
                                [f"Color placement at {row},{col}", f"Valid color: {color}"]
                            )
        
        return LogicResult(False, "No valid color found", 0.0, [], [])
    
    def _is_valid_color_placement(self, grid: List[List[str]], row: int, col: int, color: str) -> bool:
        """Check if color placement is valid"""
        # Check adjacent cells (simple rule)
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < len(grid) and 0 <= new_col < len(grid[0]) and 
                grid[new_row][new_col] == color):
                return False
        
        return True
    
    def _solve_signal_grid(self, grid: List[List[str]]) -> LogicResult:
        """Solve signal-themed grid puzzle"""
        # Look for missing letters to spell SIGNAL
        target_letters = set("SIGNAL")
        found_letters = set()
        
        for row in grid:
            for cell in row:
                if cell != "?" and cell in target_letters:
                    found_letters.add(cell)
        
        missing_letters = target_letters - found_letters
        
        if missing_letters:
            missing_letter = list(missing_letters)[0]
            # Find first empty position
            for row in range(len(grid)):
                for col in range(len(grid[0])):
                    if grid[row][col] == "?":
                        return LogicResult(
                            True,
                            f"Position ({row},{col}) needs letter {missing_letter}",
                            0.75,
                            [missing_letter],
                            [f"Missing letters: {missing_letters}", f"Placing: {missing_letter}"]
                        )
        
        return LogicResult(False, "Signal grid complete or unsolvable", 0.0, [], [])
    
    def generate_hint(self, puzzle_type: str, current_state: Dict[str, Any]) -> str:
        """Generate helpful hint for logic puzzle"""
        if puzzle_type == "mastermind":
            return "Try using process of elimination based on previous guess feedback"
        elif puzzle_type == "sequence":
            return "Look for arithmetic, geometric, or Fibonacci patterns"
        elif puzzle_type == "circuit":
            return "Trace signal flow through each logic gate step by step"
        elif puzzle_type == "grid":
            return "Use constraint elimination to find valid placements"
        else:
            return "Apply logical reasoning to eliminate impossible solutions" 