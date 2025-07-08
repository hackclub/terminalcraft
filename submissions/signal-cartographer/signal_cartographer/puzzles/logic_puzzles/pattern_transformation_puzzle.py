"""
Pattern Transformation Puzzle for The Signal Cartographer
Players analyze pattern transformations and predict the next state
"""

from typing import Any, Dict, List, Tuple, Optional
import random
import time

from ..puzzle_base import BasePuzzle, PuzzleResult, PuzzleDifficulty, generate_puzzle_id
from .logic_library import LogicLibrary
from .logic_tools import LogicSolver


class PatternTransformationPuzzle(BasePuzzle):
    """
    Pattern transformation puzzle where players analyze evolving patterns
    """
    
    def __init__(self, 
                 difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL,
                 signal_data: Any = None,
                 transformation_type: str = "rotation"):
        """
        Initialize pattern transformation puzzle
        
        Args:
            difficulty: Puzzle difficulty level
            signal_data: Associated signal data
            transformation_type: Type of transformation (rotation, reflection, growth, shift)
        """
        
        self.logic_library = LogicLibrary()
        self.logic_solver = LogicSolver()
        self.transformation_type = transformation_type
        self.pattern_states: List[List[str]] = []
        self.transformation_rule = ""
        self.pattern_size = 3  # Start with 3x3
        self.symbols = ["·", "●", "■", "▲", "♦"]
        
        # Calculate difficulty parameters
        max_attempts = max(3, 6 - difficulty.value)
        time_limit = None
        if difficulty.value >= 3:
            time_limit = 420 - (difficulty.value - 3) * 70  # 420, 350, 280, 210 seconds
        
        super().__init__(
            puzzle_id=generate_puzzle_id(),
            name=f"Pattern Transform - {transformation_type.title()}",
            description=f"Analyze pattern transformations",
            difficulty=difficulty,
            max_attempts=max_attempts,
            time_limit=time_limit,
            signal_data=signal_data
        )
    
    def _initialize_puzzle(self) -> None:
        """Initialize the pattern transformation puzzle"""
        # Adjust pattern size based on difficulty
        if self.difficulty.value <= 2:
            self.pattern_size = 3
        elif self.difficulty.value <= 4:
            self.pattern_size = 4
        else:
            self.pattern_size = 5
        
        # Generate transformation based on type and difficulty
        if self.transformation_type == "rotation":
            self._generate_rotation_pattern()
        elif self.transformation_type == "reflection":
            self._generate_reflection_pattern()
        elif self.transformation_type == "growth":
            self._generate_growth_pattern()
        elif self.transformation_type == "shift":
            self._generate_shift_pattern()
        elif self.transformation_type == "cellular":
            self._generate_cellular_pattern()
        else:
            self._generate_rotation_pattern()  # Default
        
        # Generate hints
        self._generate_hints()
        
        # Calculate max score
        self.max_score = 800 + (self.difficulty.value - 1) * 400
    
    def _generate_rotation_pattern(self):
        """Generate patterns that rotate elements"""
        # Create initial pattern
        initial = self._create_empty_grid()
        
        # Add some elements
        elements = random.sample(range(self.pattern_size * self.pattern_size), 
                                min(3 + self.difficulty.value, self.pattern_size * self.pattern_size // 2))
        
        for elem in elements:
            row, col = elem // self.pattern_size, elem % self.pattern_size
            initial[row][col] = random.choice(self.symbols[1:3])  # Use ● and ■
        
        self.pattern_states = [initial]
        
        # Generate rotated states
        current = initial
        for step in range(3):  # Show 3 transformation steps
            current = self._rotate_pattern_90(current)
            self.pattern_states.append([row[:] for row in current])
        
        # Next state (solution)
        next_state = self._rotate_pattern_90(current)
        self.solution_pattern = next_state
        
        self.transformation_rule = "90° clockwise rotation each step"
        self.solution = self._pattern_to_string(next_state)
    
    def _generate_reflection_pattern(self):
        """Generate patterns that reflect elements"""
        # Create initial asymmetric pattern
        initial = self._create_empty_grid()
        
        # Add elements to one side
        for i in range(self.pattern_size):
            for j in range(self.pattern_size // 2):
                if random.random() < 0.4:
                    initial[i][j] = random.choice(self.symbols[1:3])
        
        self.pattern_states = [initial]
        
        # Generate reflection states
        current = initial
        reflection_types = ["vertical", "horizontal", "diagonal"]
        self.reflection_type = random.choice(reflection_types)
        
        for step in range(3):
            current = self._reflect_pattern(current, self.reflection_type)
            self.pattern_states.append([row[:] for row in current])
        
        # Next state (solution)
        next_state = self._reflect_pattern(current, self.reflection_type)
        self.solution_pattern = next_state
        
        self.transformation_rule = f"{self.reflection_type} reflection each step"
        self.solution = self._pattern_to_string(next_state)
    
    def _generate_growth_pattern(self):
        """Generate patterns that grow or shrink"""
        # Start with a small central pattern
        initial = self._create_empty_grid()
        center = self.pattern_size // 2
        
        # Place initial seed
        initial[center][center] = "●"
        if self.pattern_size >= 3:
            initial[center-1][center] = "■"
            initial[center+1][center] = "■"
        
        self.pattern_states = [initial]
        
        # Generate growth states
        current = initial
        for step in range(3):
            current = self._grow_pattern(current)
            self.pattern_states.append([row[:] for row in current])
        
        # Next state (solution)
        next_state = self._grow_pattern(current)
        self.solution_pattern = next_state
        
        self.transformation_rule = "Pattern grows outward by one layer each step"
        self.solution = self._pattern_to_string(next_state)
    
    def _generate_shift_pattern(self):
        """Generate patterns that shift elements"""
        # Create initial pattern
        initial = self._create_empty_grid()
        
        # Add a line or shape that will shift
        if self.difficulty.value <= 2:
            # Simple horizontal line
            row = self.pattern_size // 2
            for col in range(self.pattern_size // 2):
                initial[row][col] = "●"
        else:
            # More complex shape
            for i in range(min(3, self.pattern_size)):
                initial[i][0] = "●"
                if i < self.pattern_size - 1:
                    initial[i][1] = "■"
        
        self.pattern_states = [initial]
        
        # Generate shift states
        current = initial
        self.shift_direction = random.choice(["right", "down", "diagonal"])
        
        for step in range(3):
            current = self._shift_pattern(current, self.shift_direction)
            self.pattern_states.append([row[:] for row in current])
        
        # Next state (solution)
        next_state = self._shift_pattern(current, self.shift_direction)
        self.solution_pattern = next_state
        
        self.transformation_rule = f"Pattern shifts {self.shift_direction} each step"
        self.solution = self._pattern_to_string(next_state)
    
    def _generate_cellular_pattern(self):
        """Generate cellular automata-style patterns"""
        # Simple rule: neighbors affect growth
        initial = self._create_empty_grid()
        
        # Seed pattern
        center = self.pattern_size // 2
        initial[center][center] = "●"
        if self.pattern_size >= 3:
            initial[center][center-1] = "●"
            initial[center][center+1] = "●"
        
        self.pattern_states = [initial]
        
        # Generate cellular evolution
        current = initial
        for step in range(3):
            current = self._evolve_cellular(current)
            self.pattern_states.append([row[:] for row in current])
        
        # Next state (solution)
        next_state = self._evolve_cellular(current)
        self.solution_pattern = next_state
        
        self.transformation_rule = "Cellular evolution: cells grow based on neighbors"
        self.solution = self._pattern_to_string(next_state)
    
    def _create_empty_grid(self) -> List[List[str]]:
        """Create empty grid filled with dots"""
        return [["·" for _ in range(self.pattern_size)] for _ in range(self.pattern_size)]
    
    def _rotate_pattern_90(self, pattern: List[List[str]]) -> List[List[str]]:
        """Rotate pattern 90 degrees clockwise"""
        size = len(pattern)
        rotated = self._create_empty_grid()
        
        for i in range(size):
            for j in range(size):
                rotated[j][size-1-i] = pattern[i][j]
        
        return rotated
    
    def _reflect_pattern(self, pattern: List[List[str]], reflection_type: str) -> List[List[str]]:
        """Reflect pattern according to type"""
        size = len(pattern)
        reflected = self._create_empty_grid()
        
        for i in range(size):
            for j in range(size):
                if reflection_type == "vertical":
                    reflected[i][size-1-j] = pattern[i][j]
                elif reflection_type == "horizontal":
                    reflected[size-1-i][j] = pattern[i][j]
                elif reflection_type == "diagonal":
                    reflected[j][i] = pattern[i][j]
        
        return reflected
    
    def _grow_pattern(self, pattern: List[List[str]]) -> List[List[str]]:
        """Grow pattern outward"""
        size = len(pattern)
        grown = [row[:] for row in pattern]  # Copy current pattern
        
        # Find all active cells
        active_cells = []
        for i in range(size):
            for j in range(size):
                if pattern[i][j] != "·":
                    active_cells.append((i, j))
        
        # Grow around active cells
        for i, j in active_cells:
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < size and 0 <= nj < size:
                        if grown[ni][nj] == "·" and random.random() < 0.3:
                            grown[ni][nj] = "■"
        
        return grown
    
    def _shift_pattern(self, pattern: List[List[str]], direction: str) -> List[List[str]]:
        """Shift pattern in given direction"""
        size = len(pattern)
        shifted = self._create_empty_grid()
        
        for i in range(size):
            for j in range(size):
                if pattern[i][j] != "·":
                    ni, nj = i, j
                    
                    if direction == "right":
                        nj = (j + 1) % size
                    elif direction == "down":
                        ni = (i + 1) % size
                    elif direction == "diagonal":
                        ni = (i + 1) % size
                        nj = (j + 1) % size
                    
                    shifted[ni][nj] = pattern[i][j]
        
        return shifted
    
    def _evolve_cellular(self, pattern: List[List[str]]) -> List[List[str]]:
        """Evolve cellular automata pattern"""
        size = len(pattern)
        evolved = self._create_empty_grid()
        
        for i in range(size):
            for j in range(size):
                # Count live neighbors
                live_neighbors = 0
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        ni, nj = i + di, j + dj
                        if 0 <= ni < size and 0 <= nj < size:
                            if pattern[ni][nj] != "·":
                                live_neighbors += 1
                
                # Simple evolution rule
                if pattern[i][j] != "·":
                    # Cell survives if it has 2-3 neighbors
                    if 2 <= live_neighbors <= 3:
                        evolved[i][j] = pattern[i][j]
                else:
                    # Empty cell becomes alive with exactly 3 neighbors
                    if live_neighbors == 3:
                        evolved[i][j] = "●"
        
        return evolved
    
    def _pattern_to_string(self, pattern: List[List[str]]) -> str:
        """Convert pattern to string representation"""
        return "|".join("".join(row) for row in pattern)
    
    def _string_to_pattern(self, pattern_str: str) -> List[List[str]]:
        """Convert string representation back to pattern"""
        rows = pattern_str.split("|")
        return [list(row) for row in rows]
    
    def _generate_hints(self):
        """Generate hints for the puzzle"""
        # Hint 1: Transformation type
        self.add_hint(1, f"Transformation type: {self.transformation_type.title()}", 120)
        
        # Hint 2: Transformation rule
        if self.difficulty.value >= 2:
            self.add_hint(2, f"Rule: {self.transformation_rule}", 180)
        
        # Hint 3: Pattern analysis
        if self.difficulty.value >= 3:
            analysis_hints = {
                "rotation": "Compare positions of elements between states",
                "reflection": f"Elements are mirrored {getattr(self, 'reflection_type', 'symmetrically')}",
                "growth": "New elements appear adjacent to existing ones",
                "shift": f"All elements move {getattr(self, 'shift_direction', 'consistently')}",
                "cellular": "Elements evolve based on neighbor count"
            }
            self.add_hint(3, analysis_hints.get(self.transformation_type, "Analyze element movement"), 250)
        
        # Hint 4: Pattern insight
        if self.difficulty.value >= 4:
            self.add_hint(4, "Focus on how each individual element transforms", 320)
        
        # Hint 5: Solution preview
        if self.difficulty.value >= 4:
            # Show partial next state
            partial_solution = self._get_partial_solution()
            self.add_hint(5, f"Partial next state: {partial_solution}", 450)
    
    def _get_partial_solution(self) -> str:
        """Get partial solution for hint"""
        if not hasattr(self, 'solution_pattern'):
            return "Processing..."
        
        # Show first row or corner of solution
        pattern = self.solution_pattern
        if len(pattern) > 0:
            first_row = "".join(pattern[0])
            return f"First row: {first_row}"
        return "Pattern analysis..."
    
    def validate_input(self, player_input: str) -> Tuple[bool, str]:
        """Validate player's pattern answer"""
        player_input = player_input.strip()
        
        # Try to parse as pattern string
        if "|" in player_input:
            try:
                player_pattern = self._string_to_pattern(player_input)
                if self._patterns_match(player_pattern, self.solution_pattern):
                    return True, "🎯 Perfect! You correctly predicted the pattern transformation."
                else:
                    similarity = self._calculate_pattern_similarity(player_pattern, self.solution_pattern)
                    if similarity > 0.7:
                        return False, f"Very close! Pattern similarity: {similarity:.1%}"
                    else:
                        return False, f"Incorrect pattern. Similarity: {similarity:.1%}"
            except:
                return False, "Invalid pattern format. Use format: ···|●■·|··· (rows separated by |)"
        
        # Try simplified input (describe the transformation)
        simplified_answers = {
            "rotation": ["rotate", "turn", "spin", "90", "clockwise"],
            "reflection": ["reflect", "mirror", "flip", "reverse"],
            "growth": ["grow", "expand", "spread", "larger"],
            "shift": ["shift", "move", "slide", getattr(self, 'shift_direction', '')],
            "cellular": ["evolve", "cellular", "neighbors", "generation"]
        }
        
        player_lower = player_input.lower()
        for trans_type, keywords in simplified_answers.items():
            if trans_type == self.transformation_type:
                if any(keyword in player_lower for keyword in keywords):
                    return True, f"🎯 Correct! The pattern follows {self.transformation_rule}."
        
        return False, f"Incorrect. Expected pattern transformation: {self.transformation_rule}"
    
    def _patterns_match(self, pattern1: List[List[str]], pattern2: List[List[str]]) -> bool:
        """Check if two patterns match exactly"""
        if len(pattern1) != len(pattern2):
            return False
        
        for i in range(len(pattern1)):
            if len(pattern1[i]) != len(pattern2[i]):
                return False
            for j in range(len(pattern1[i])):
                if pattern1[i][j] != pattern2[i][j]:
                    return False
        
        return True
    
    def _calculate_pattern_similarity(self, pattern1: List[List[str]], pattern2: List[List[str]]) -> float:
        """Calculate similarity between two patterns"""
        if len(pattern1) != len(pattern2):
            return 0.0
        
        total_cells = 0
        matching_cells = 0
        
        for i in range(len(pattern1)):
            if len(pattern1[i]) != len(pattern2[i]):
                continue
            for j in range(len(pattern1[i])):
                total_cells += 1
                if pattern1[i][j] == pattern2[i][j]:
                    matching_cells += 1
        
        return matching_cells / total_cells if total_cells > 0 else 0.0
    
    def get_current_display(self) -> List[str]:
        """Get the current puzzle display"""
        lines = []
        
        # Header
        lines.append(f"[bold cyan]🔄 PATTERN TRANSFORM - {self.transformation_type.upper()}[/bold cyan]")
        lines.append("=" * 60)
        lines.append("")
        
        # Puzzle info
        lines.append(f"[yellow]Transformation:[/yellow] {self.transformation_type.title()}")
        lines.append(f"[yellow]Difficulty:[/yellow] {self.difficulty.name}")
        lines.append("")
        
        # Display pattern sequence
        lines.append("[cyan]═══ PATTERN SEQUENCE ═══[/cyan]")
        lines.append("")
        
        # Show states side by side if possible, otherwise vertically
        if self.pattern_size <= 3:
            # Show horizontally
            for state_idx, state in enumerate(self.pattern_states):
                lines.append(f"[white]State {state_idx + 1}:[/white]")
                for row in state:
                    lines.append(f"  [green]{''.join(row)}[/green]")
                lines.append("")
        else:
            # Show vertically for larger patterns
            for state_idx, state in enumerate(self.pattern_states):
                lines.append(f"[white]State {state_idx + 1}:[/white]")
                for row in state:
                    lines.append(f"  [green]{''.join(row)}[/green]")
                lines.append("")
        
        # Next state question
        lines.append("[cyan]═══ PREDICT NEXT STATE ═══[/cyan]")
        lines.append("[white]State 5:[/white]")
        lines.append("  [red]? ? ?[/red]")
        lines.append("  [red]? ? ?[/red]")
        lines.append("  [red]? ? ?[/red]")
        lines.append("")
        
        # Instructions
        lines.append("[green]Instructions:[/green]")
        lines.append("• Analyze how the pattern changes between states")
        lines.append("• Identify the transformation rule")
        lines.append("• Predict what State 5 should look like")
        lines.append("• Format: ···|●■·|··· (rows separated by |)")
        lines.append("• Or describe the transformation in words")
        lines.append("• Use [yellow]HINT[/yellow] for guidance")
        
        return lines
    
    def get_progress_display(self) -> List[str]:
        """Get progress indicators"""
        lines = []
        
        lines.append("[cyan]═══ TRANSFORMATION ANALYSIS ═══[/cyan]")
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
        
        lines.append(f"[yellow]Transformation Type:[/yellow] {self.transformation_type.title()}")
        lines.append(f"[yellow]Pattern Size:[/yellow] {self.pattern_size}x{self.pattern_size}")
        lines.append(f"[yellow]States Shown:[/yellow] {len(self.pattern_states)}")
        
        # Transformation analysis
        if hasattr(self, 'transformation_rule'):
            lines.append(f"[yellow]Rule:[/yellow] {self.transformation_rule}")
        
        return lines
    
    def start(self) -> bool:
        """Start the puzzle (compatibility method)"""
        return self.start_puzzle()
    
    def _on_puzzle_start(self) -> None:
        """Called when puzzle starts"""
        self.current_progress['transformation_type'] = self.transformation_type
        self.current_progress['pattern_states'] = self.pattern_states
        self.current_progress['transformation_rule'] = self.transformation_rule
        self.current_progress['start_time'] = time.time()
    
    def _on_puzzle_complete(self, result: PuzzleResult) -> None:
        """Called when puzzle completes"""
        self.current_progress['completion_time'] = time.time()
        self.current_progress['final_score'] = result.score
        self.current_progress['pattern_predicted'] = result.success
        self.current_progress['solution_pattern'] = getattr(self, 'solution_pattern', None) 