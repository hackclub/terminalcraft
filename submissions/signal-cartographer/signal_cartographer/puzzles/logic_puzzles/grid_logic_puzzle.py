"""
Grid Logic Puzzle for The Signal Cartographer
Players solve constraint-based grid puzzles with logical deduction
"""

from typing import Any, Dict, List, Tuple, Optional, Set
import random
import time

from ..puzzle_base import BasePuzzle, PuzzleResult, PuzzleDifficulty, generate_puzzle_id
from .logic_library import LogicLibrary
from .logic_tools import LogicSolver


class GridLogicPuzzle(BasePuzzle):
    """
    Grid-based logic puzzle with constraints and deduction requirements
    """
    
    def __init__(self, 
                 difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL,
                 signal_data: Any = None,
                 grid_type: str = "mini_sudoku"):
        """
        Initialize grid logic puzzle
        
        Args:
            difficulty: Puzzle difficulty level
            signal_data: Associated signal data
            grid_type: Type of grid puzzle (mini_sudoku, logic_grid, constraint_grid)
        """
        
        self.logic_library = LogicLibrary()
        self.logic_solver = LogicSolver()
        self.grid_type = grid_type
        self.grid_size = 4  # Default 4x4
        self.puzzle_grid: List[List[str]] = []
        self.solution_grid: List[List[str]] = []
        self.constraints: List[str] = []
        self.allowed_values: Set[str] = set()
        
        # Calculate difficulty parameters
        max_attempts = max(5, 10 - difficulty.value)
        time_limit = None
        if difficulty.value >= 3:
            time_limit = 480 - (difficulty.value - 3) * 80  # 480, 400, 320, 240 seconds
        
        super().__init__(
            puzzle_id=generate_puzzle_id(),
            name=f"Grid Logic - {grid_type.replace('_', ' ').title()}",
            description=f"Solve constraint-based grid puzzle",
            difficulty=difficulty,
            max_attempts=max_attempts,
            time_limit=time_limit,
            signal_data=signal_data
        )
    
    def _initialize_puzzle(self) -> None:
        """Initialize the grid logic puzzle"""
        # Generate grid based on type and difficulty
        if self.grid_type == "mini_sudoku":
            self._generate_mini_sudoku()
        elif self.grid_type == "logic_grid":
            self._generate_logic_grid()
        elif self.grid_type == "constraint_grid":
            self._generate_constraint_grid()
        else:
            self._generate_mini_sudoku()  # Default
        
        # Generate hints
        self._generate_hints()
        
        # Calculate max score
        self.max_score = 600 + (self.difficulty.value - 1) * 300
    
    def _generate_mini_sudoku(self):
        """Generate a 4x4 mini sudoku puzzle"""
        self.grid_size = 4
        self.allowed_values = {"1", "2", "3", "4"}
        
        # Create a valid solution first
        solution_patterns = [
            [["1", "2", "3", "4"],
             ["3", "4", "1", "2"],
             ["2", "3", "4", "1"],
             ["4", "1", "2", "3"]],
            
            [["2", "1", "4", "3"],
             ["4", "3", "2", "1"],
             ["1", "4", "3", "2"],
             ["3", "2", "1", "4"]],
            
            [["3", "4", "1", "2"],
             ["1", "2", "3", "4"],
             ["4", "1", "2", "3"],
             ["2", "3", "4", "1"]]
        ]
        
        self.solution_grid = random.choice(solution_patterns)
        
        # Create puzzle by removing values based on difficulty
        removal_count = {1: 6, 2: 8, 3: 10, 4: 12, 5: 14, 6: 15}
        remove_count = removal_count.get(self.difficulty.value, 10)
        
        # Copy solution and remove values
        self.puzzle_grid = [row[:] for row in self.solution_grid]
        positions = [(i, j) for i in range(4) for j in range(4)]
        random.shuffle(positions)
        
        for i in range(min(remove_count, len(positions))):
            row, col = positions[i]
            self.puzzle_grid[row][col] = "_"
        
        self.constraints = [
            "Each row must contain the numbers 1-4",
            "Each column must contain the numbers 1-4",
            "Each 2x2 box must contain the numbers 1-4"
        ]
        
        # Solution is the coordinate format for validation
        missing_cells = []
        for i in range(4):
            for j in range(4):
                if self.puzzle_grid[i][j] == "_":
                    missing_cells.append(f"{i+1}{j+1}={self.solution_grid[i][j]}")
        
        self.solution = ",".join(missing_cells)
    
    def _generate_logic_grid(self):
        """Generate a logic grid puzzle with clues"""
        self.grid_size = 3
        self.allowed_values = {"A", "B", "C"}
        
        # Categories for logic grid: Signals, Frequencies, Sectors
        signals = ["ALPHA", "BETA", "GAMMA"]
        frequencies = ["LOW", "MID", "HIGH"]
        sectors = ["SEC1", "SEC2", "SEC3"]
        
        # Create solution mapping
        signal_to_freq = dict(zip(signals, random.sample(frequencies, 3)))
        signal_to_sector = dict(zip(signals, random.sample(sectors, 3)))
        
        # Generate clues
        clues = []
        clues.append(f"ALPHA signal is not on {random.choice(frequencies)}")
        clues.append(f"The {random.choice(frequencies)} frequency signal is in {random.choice(sectors)}")
        clues.append(f"GAMMA signal is not in {random.choice(sectors)}")
        
        self.constraints = clues
        
        # Create grid representation
        self.puzzle_grid = [["_" for _ in range(3)] for _ in range(3)]
        self.solution_grid = [["_" for _ in range(3)] for _ in range(3)]
        
        # Fill solution grid
        for i, signal in enumerate(signals):
            freq_idx = frequencies.index(signal_to_freq[signal])
            sector_idx = sectors.index(signal_to_sector[signal])
            self.solution_grid[i][freq_idx] = "X"
            self.solution_grid[i][sector_idx] = "O"
        
        # Solution format: signal assignments
        self.solution = f"ALPHA={signal_to_freq['ALPHA']},{signal_to_sector['ALPHA']}"
    
    def _generate_constraint_grid(self):
        """Generate a constraint satisfaction grid"""
        self.grid_size = 3
        self.allowed_values = {"1", "2", "3"}
        
        # Create a Latin square with additional constraints
        base_patterns = [
            [["1", "2", "3"],
             ["2", "3", "1"],
             ["3", "1", "2"]],
            
            [["2", "1", "3"],
             ["3", "2", "1"],
             ["1", "3", "2"]],
            
            [["3", "1", "2"],
             ["1", "2", "3"],
             ["2", "3", "1"]]
        ]
        
        self.solution_grid = random.choice(base_patterns)
        
        # Create puzzle by removing some values
        remove_count = min(4 + self.difficulty.value, 7)
        self.puzzle_grid = [row[:] for row in self.solution_grid]
        
        positions = [(i, j) for i in range(3) for j in range(3)]
        random.shuffle(positions)
        
        for i in range(remove_count):
            row, col = positions[i]
            self.puzzle_grid[row][col] = "_"
        
        self.constraints = [
            "Each row must contain exactly one 1, one 2, and one 3",
            "Each column must contain exactly one 1, one 2, and one 3",
            "No number can be adjacent to itself (horizontally or vertically)"
        ]
        
        # Solution format for missing cells
        missing_cells = []
        for i in range(3):
            for j in range(3):
                if self.puzzle_grid[i][j] == "_":
                    missing_cells.append(f"{i+1}{j+1}={self.solution_grid[i][j]}")
        
        self.solution = ",".join(missing_cells)
    
    def _generate_hints(self):
        """Generate hints for the puzzle"""
        # Hint 1: Grid type explanation
        type_hints = {
            "mini_sudoku": "Standard sudoku rules apply to this 4x4 grid",
            "logic_grid": "Use logical deduction from the given clues",
            "constraint_grid": "Follow the constraint rules carefully"
        }
        self.add_hint(1, type_hints.get(self.grid_type, "Grid-based logic puzzle"), 100)
        
        # Hint 2: Constraint reminder
        if self.difficulty.value >= 2:
            self.add_hint(2, f"Remember: {self.constraints[0]}", 150)
        
        # Hint 3: Specific cell hint
        if self.difficulty.value >= 3:
            # Find an easy cell to solve
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if self.puzzle_grid[i][j] == "_":
                        correct_value = self.solution_grid[i][j]
                        self.add_hint(3, f"Cell ({i+1},{j+1}) should be {correct_value}", 200)
                        break
                else:
                    continue
                break
        
        # Hint 4: Strategy hint
        if self.difficulty.value >= 4:
            strategy_hints = {
                "mini_sudoku": "Look for rows/columns with only one missing number",
                "logic_grid": "Process elimination based on the clues",
                "constraint_grid": "Check adjacency constraints carefully"
            }
            self.add_hint(4, strategy_hints.get(self.grid_type, "Use logical deduction"), 250)
        
        # Hint 5: Partial solution
        if self.difficulty.value >= 4:
            solution_parts = self.solution.split(",")
            if len(solution_parts) > 2:
                partial = solution_parts[0]
                self.add_hint(5, f"One answer: {partial}", 300)
    
    def validate_input(self, player_input: str) -> Tuple[bool, str]:
        """Validate player's grid solution"""
        player_input = player_input.strip().upper()
        
        # Handle different input formats
        if self.grid_type == "mini_sudoku" or self.grid_type == "constraint_grid":
            # Format: "11=1,12=2,13=3" (row,col=value)
            return self._validate_coordinate_input(player_input)
        elif self.grid_type == "logic_grid":
            # Format: "ALPHA=LOW,SEC1"
            return self._validate_logic_assignment(player_input)
        
        return False, "Invalid input format"
    
    def _validate_coordinate_input(self, player_input: str) -> Tuple[bool, str]:
        """Validate coordinate-based input"""
        try:
            # Parse player input
            assignments = {}
            for assignment in player_input.split(","):
                if "=" not in assignment:
                    continue
                coord, value = assignment.strip().split("=")
                assignments[coord] = value
            
            # Check against solution
            solution_assignments = {}
            for assignment in self.solution.split(","):
                coord, value = assignment.split("=")
                solution_assignments[coord] = value
            
            correct_count = 0
            total_missing = len(solution_assignments)
            
            for coord, expected_value in solution_assignments.items():
                if coord in assignments and assignments[coord] == expected_value:
                    correct_count += 1
            
            if correct_count == total_missing:
                return True, f"🎯 Perfect! All {total_missing} cells correctly filled."
            elif correct_count >= total_missing * 0.8:
                return False, f"Very close! {correct_count}/{total_missing} cells correct."
            else:
                return False, f"Incorrect. {correct_count}/{total_missing} cells correct. Check constraints."
                
        except Exception:
            return False, "Invalid format. Use: 11=1,12=2 (row,col=value)"
    
    def _validate_logic_assignment(self, player_input: str) -> Tuple[bool, str]:
        """Validate logic grid assignment"""
        # Simplified validation for logic grid
        if player_input.upper() == self.solution.upper():
            return True, "🎯 Correct logic deduction!"
        else:
            return False, f"Incorrect assignment. Review the clues carefully."
    
    def get_current_display(self) -> List[str]:
        """Get the current puzzle display"""
        lines = []
        
        # Header
        lines.append(f"[bold cyan]🔲 GRID LOGIC - {self.grid_type.replace('_', ' ').upper()}[/bold cyan]")
        lines.append("=" * 60)
        lines.append("")
        
        # Puzzle info
        lines.append(f"[yellow]Grid Size:[/yellow] {self.grid_size}x{self.grid_size}")
        lines.append(f"[yellow]Difficulty:[/yellow] {self.difficulty.name}")
        lines.append("")
        
        # Display grid
        lines.append("[cyan]═══ PUZZLE GRID ═══[/cyan]")
        lines.append("")
        
        # Grid display with borders
        if self.grid_type == "mini_sudoku":
            lines.extend(self._display_sudoku_grid())
        elif self.grid_type == "logic_grid":
            lines.extend(self._display_logic_grid())
        else:
            lines.extend(self._display_constraint_grid())
        
        lines.append("")
        
        # Constraints
        lines.append("[cyan]═══ CONSTRAINTS ═══[/cyan]")
        for i, constraint in enumerate(self.constraints, 1):
            lines.append(f"[white]{i}.[/white] {constraint}")
        lines.append("")
        
        # Instructions
        lines.append("[green]Instructions:[/green]")
        if self.grid_type == "mini_sudoku":
            lines.append("• Fill empty cells (_) with numbers 1-4")
            lines.append("• Use format: 11=1,22=2 (row,col=value)")
        elif self.grid_type == "logic_grid":
            lines.append("• Use logical deduction from clues")
            lines.append("• Determine which signal has which properties")
        else:
            lines.append("• Fill empty cells following all constraints")
            lines.append("• Use format: 11=1,22=2 (row,col=value)")
        
        lines.append("• Use [yellow]HINT[/yellow] if you need guidance")
        
        return lines
    
    def _display_sudoku_grid(self) -> List[str]:
        """Display sudoku-style grid"""
        lines = []
        lines.append("  ┌─────┬─────┐")
        
        for i in range(4):
            row_display = f"{i+1} │ "
            for j in range(4):
                cell = self.puzzle_grid[i][j]
                if cell == "_":
                    row_display += "· "
                else:
                    row_display += f"[blue]{cell}[/blue] "
                if j == 1:
                    row_display += "│ "
            row_display += "│"
            lines.append(row_display)
            
            if i == 1:
                lines.append("  ├─────┼─────┤")
        
        lines.append("  └─────┴─────┘")
        lines.append("    1 2   3 4")
        return lines
    
    def _display_logic_grid(self) -> List[str]:
        """Display logic grid with clues"""
        lines = []
        lines.append("Logic Grid: Signal → Frequency, Sector")
        lines.append("")
        lines.append("ALPHA: ?, ?")
        lines.append("BETA:  ?, ?") 
        lines.append("GAMMA: ?, ?")
        lines.append("")
        lines.append("Available: LOW, MID, HIGH | SEC1, SEC2, SEC3")
        return lines
    
    def _display_constraint_grid(self) -> List[str]:
        """Display constraint grid"""
        lines = []
        lines.append("  ┌───┬───┬───┐")
        
        for i in range(3):
            row_display = f"{i+1} │ "
            for j in range(3):
                cell = self.puzzle_grid[i][j]
                if cell == "_":
                    row_display += "· "
                else:
                    row_display += f"[blue]{cell}[/blue] "
                row_display += "│ "
            lines.append(row_display)
            
            if i < 2:
                lines.append("  ├───┼───┼───┤")
        
        lines.append("  └───┴───┴───┘")
        lines.append("    1   2   3")
        return lines
    
    def get_progress_display(self) -> List[str]:
        """Get progress indicators"""
        lines = []
        
        lines.append("[cyan]═══ GRID PROGRESS ═══[/cyan]")
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
        
        lines.append(f"[yellow]Grid Type:[/yellow] {self.grid_type.replace('_', ' ').title()}")
        lines.append(f"[yellow]Grid Size:[/yellow] {self.grid_size}x{self.grid_size}")
        
        # Count filled cells
        filled_count = 0
        total_count = 0
        for row in self.puzzle_grid:
            for cell in row:
                total_count += 1
                if cell != "_":
                    filled_count += 1
        
        lines.append(f"[yellow]Cells Filled:[/yellow] {filled_count}/{total_count}")
        
        return lines
    
    def start(self) -> bool:
        """Start the puzzle (compatibility method)"""
        return self.start_puzzle()
    
    def _on_puzzle_start(self) -> None:
        """Called when puzzle starts"""
        self.current_progress['grid_type'] = self.grid_type
        self.current_progress['grid_size'] = self.grid_size
        self.current_progress['constraints'] = self.constraints
        self.current_progress['start_time'] = time.time()
    
    def _on_puzzle_complete(self, result: PuzzleResult) -> None:
        """Called when puzzle completes"""
        self.current_progress['completion_time'] = time.time()
        self.current_progress['final_score'] = result.score
        self.current_progress['grid_solved'] = result.success
        self.current_progress['solution_grid'] = self.solution_grid 