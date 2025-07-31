"""
Logic Library System for Logic Puzzles
Stores logical patterns, sequences, and puzzle definitions
"""

from typing import Dict, List, Tuple, Optional, Any
import random
import string
from dataclasses import dataclass


@dataclass
class LogicPuzzleData:
    """Data structure for logic puzzle information"""
    name: str
    puzzle_type: str  # mastermind, circuit, sequence, etc.
    description: str
    difficulty: int  # 1-5
    pattern: List[Any]  # The solution pattern
    clues: List[str]  # Available clues
    constraints: Dict[str, Any]  # Puzzle constraints
    metadata: Dict[str, Any]


class LogicLibrary:
    """Library of logic patterns and reasoning challenges"""
    
    def __init__(self):
        self.puzzles: Dict[str, LogicPuzzleData] = {}
        self.sequences: Dict[str, List[Any]] = {}
        self.circuit_patterns: Dict[str, List[str]] = {}
        self.grid_templates: Dict[str, List[List[str]]] = {}
        self._initialize_library()
    
    def _initialize_library(self):
        """Initialize with sample logic puzzles and patterns"""
        
        # Mathematical sequences
        self.sequences = {
            "fibonacci": [1, 1, 2, 3, 5, 8, 13, 21, 34, 55],
            "primes": [2, 3, 5, 7, 11, 13, 17, 19, 23, 29],
            "squares": [1, 4, 9, 16, 25, 36, 49, 64, 81, 100],
            "powers_of_2": [1, 2, 4, 8, 16, 32, 64, 128, 256, 512],
            "triangular": [1, 3, 6, 10, 15, 21, 28, 36, 45, 55],
            "arithmetic_3": [3, 6, 9, 12, 15, 18, 21, 24, 27, 30],
            "geometric_2": [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024],
            "alternating": [1, -1, 1, -1, 1, -1, 1, -1, 1, -1],
            "signal_themed": [1, 4, 2, 8, 5, 9, 6, 12, 10, 15]  # Custom pattern
        }
        
        # ASCII Circuit patterns (simplified logic gates)
        self.circuit_patterns = {
            "and_gate": [
                "  A ────┐     ",
                "        │ AND ",
                "  B ────┘  ├──── OUT",
                "           │    ",
                "          ─┘    "
            ],
            "or_gate": [
                "  A ────┐     ",
                "        │ OR  ",
                "  B ────┘  ├──── OUT",
                "           │    ",
                "          ─┘    "
            ],
            "not_gate": [
                "  A ────┤>o──── OUT",
                "        NOT     "
            ],
            "xor_gate": [
                "  A ────┐     ",
                "        │ XOR ",
                "  B ────┘  ├──── OUT",
                "           │    ",
                "          ─┘    "
            ],
            "complex_circuit": [
                "A ─┬─── AND ─┬─── OR ──── OUT",
                "   │         │    │      ",
                "B ─┘    C ───┘    │      ",
                "              D ──┘      "
            ]
        }
        
        # Grid templates for logic puzzles
        self.grid_templates = {
            "sudoku_mini": [
                ["1", "?", "3", "?"],
                ["?", "3", "?", "1"],
                ["3", "?", "1", "?"],
                ["?", "1", "?", "3"]
            ],
            "logic_grid_3x3": [
                ["R", "?", "B"],
                ["?", "G", "?"],
                ["B", "?", "R"]
            ],
            "signal_grid": [
                ["S", "I", "?", "N"],
                ["?", "G", "N", "?"],
                ["N", "?", "L", "S"],
                ["A", "L", "?", "I"]
            ]
        }
        
        # Initialize sample puzzles
        self._create_mastermind_samples()
        self._create_sequence_samples()
        self._create_circuit_samples()
        self._create_grid_samples()
    
    def _create_mastermind_samples(self):
        """Create sample Mastermind/Bulls & Cows puzzles"""
        mastermind_samples = [
            ("MM_ALPHA", [1, 2, 3, 4], 4, ["Numbers 1-6 allowed"]),
            ("MM_BETA", [3, 1, 4, 2], 4, ["Numbers 1-6 allowed"]),
            ("MM_GAMMA", [5, 2, 6, 1], 4, ["Numbers 1-6 allowed"]),
            ("BC_SIMPLE", [1, 2, 3], 3, ["Numbers 1-5 allowed"]),
            ("BC_HARD", [4, 1, 5, 2, 3], 5, ["Numbers 1-7 allowed"])
        ]
        
        for name, pattern, length, clues in mastermind_samples:
            puzzle_type = "bulls_cows" if name.startswith("BC") else "mastermind"
            difficulty = 2 if length <= 3 else 3 if length <= 4 else 4
            
            self.puzzles[name] = LogicPuzzleData(
                name=name,
                puzzle_type=puzzle_type,
                description=f"{puzzle_type.title()} with {length} positions",
                difficulty=difficulty,
                pattern=pattern,
                clues=clues,
                constraints={"length": length, "max_value": max(pattern) + 1},
                metadata={"category": "deduction"}
            )
    
    def _create_sequence_samples(self):
        """Create sample sequence deduction puzzles"""
        sequence_samples = [
            ("SEQ_FIB", "fibonacci", 5, ["Each number is sum of previous two"]),
            ("SEQ_PRIME", "primes", 4, ["All numbers are prime"]),
            ("SEQ_SQUARE", "squares", 4, ["Perfect squares sequence"]),
            ("SEQ_POWER2", "powers_of_2", 5, ["Powers of 2"]),
            ("SEQ_CUSTOM", "signal_themed", 6, ["Signal processing pattern"])
        ]
        
        for name, seq_type, visible_length, clues in sequence_samples:
            sequence = self.sequences[seq_type]
            pattern = sequence[:visible_length + 2]  # Include answer
            
            self.puzzles[name] = LogicPuzzleData(
                name=name,
                puzzle_type="sequence",
                description=f"Mathematical sequence pattern",
                difficulty=2 if visible_length <= 4 else 3 if visible_length <= 5 else 4,
                pattern=pattern,
                clues=clues,
                constraints={"visible_length": visible_length, "sequence_type": seq_type},
                metadata={"category": "mathematical"}
            )
    
    def _create_circuit_samples(self):
        """Create sample circuit completion puzzles"""
        circuit_samples = [
            ("CIRCUIT_AND", "and_gate", "A=1,B=1", ["AND gate: output 1 if both inputs 1"]),
            ("CIRCUIT_OR", "or_gate", "A=0,B=1", ["OR gate: output 1 if any input 1"]),
            ("CIRCUIT_NOT", "not_gate", "A=1", ["NOT gate: inverts input"]),
            ("CIRCUIT_XOR", "xor_gate", "A=1,B=1", ["XOR gate: output 1 if inputs different"]),
            ("CIRCUIT_COMPLEX", "complex_circuit", "A=1,B=0,C=1,D=0", ["Multiple gates combined"])
        ]
        
        for name, circuit_type, inputs, clues in circuit_samples:
            pattern = self.circuit_patterns[circuit_type]
            difficulty = 2 if "simple" in circuit_type or len(clues[0]) < 30 else 4
            
            self.puzzles[name] = LogicPuzzleData(
                name=name,
                puzzle_type="circuit",
                description=f"Digital logic circuit analysis",
                difficulty=difficulty,
                pattern=pattern,
                clues=clues,
                constraints={"inputs": inputs, "circuit_type": circuit_type},
                metadata={"category": "digital_logic"}
            )
    
    def _create_grid_samples(self):
        """Create sample grid-based logic puzzles"""
        grid_samples = [
            ("GRID_SUDOKU", "sudoku_mini", "Complete 4x4 grid", ["Each row and column has 1,2,3,4"]),
            ("GRID_COLOR", "logic_grid_3x3", "Color pattern", ["R=Red, G=Green, B=Blue"]),
            ("GRID_SIGNAL", "signal_grid", "Signal matrix", ["Spell SIGNAL in grid"])
        ]
        
        for name, grid_type, desc, clues in grid_samples:
            pattern = self.grid_templates[grid_type]
            difficulty = 3 if "mini" in grid_type else 4
            
            self.puzzles[name] = LogicPuzzleData(
                name=name,
                puzzle_type="grid",
                description=desc,
                difficulty=difficulty,
                pattern=pattern,
                clues=clues,
                constraints={"grid_type": grid_type},
                metadata={"category": "spatial_logic"}
            )
    
    def get_puzzle(self, name: str) -> Optional[LogicPuzzleData]:
        """Get puzzle data by name"""
        return self.puzzles.get(name)
    
    def get_puzzles_by_type(self, puzzle_type: str) -> List[LogicPuzzleData]:
        """Get all puzzles of a specific type"""
        return [puzzle for puzzle in self.puzzles.values() if puzzle.puzzle_type == puzzle_type]
    
    def get_puzzles_by_difficulty(self, difficulty: int) -> List[LogicPuzzleData]:
        """Get all puzzles of a specific difficulty"""
        return [puzzle for puzzle in self.puzzles.values() if puzzle.difficulty == difficulty]
    
    def get_random_puzzle(self, puzzle_type: str = None, difficulty_range: Tuple[int, int] = (1, 5)) -> Optional[LogicPuzzleData]:
        """Get random puzzle optionally filtered by type and difficulty"""
        valid_puzzles = []
        
        for puzzle in self.puzzles.values():
            if puzzle_type and puzzle.puzzle_type != puzzle_type:
                continue
            if not (difficulty_range[0] <= puzzle.difficulty <= difficulty_range[1]):
                continue
            valid_puzzles.append(puzzle)
        
        return random.choice(valid_puzzles) if valid_puzzles else None
    
    def get_sequence(self, sequence_type: str) -> List[Any]:
        """Get sequence by type"""
        return self.sequences.get(sequence_type, [])
    
    def get_circuit_pattern(self, circuit_type: str) -> List[str]:
        """Get circuit pattern by type"""
        return self.circuit_patterns.get(circuit_type, [])
    
    def get_grid_template(self, grid_type: str) -> List[List[str]]:
        """Get grid template by type"""
        return self.grid_templates.get(grid_type, [])
    
    def generate_mastermind_pattern(self, length: int, max_value: int, difficulty: int) -> List[int]:
        """Generate new Mastermind pattern"""
        if difficulty <= 2:
            # Easier patterns with some repetition allowed
            return [random.randint(1, max_value) for _ in range(length)]
        else:
            # Harder patterns with unique values
            values = list(range(1, max_value + 1))
            return random.sample(values, min(length, len(values)))
    
    def generate_sequence_pattern(self, sequence_type: str, length: int) -> List[int]:
        """Generate new sequence pattern"""
        if sequence_type == "arithmetic":
            start = random.randint(1, 10)
            step = random.randint(2, 5)
            return [start + i * step for i in range(length)]
        elif sequence_type == "geometric":
            start = random.randint(1, 5)
            ratio = random.randint(2, 3)
            return [start * (ratio ** i) for i in range(length)]
        elif sequence_type == "fibonacci_like":
            a, b = random.randint(1, 3), random.randint(1, 3)
            sequence = [a, b]
            for _ in range(length - 2):
                sequence.append(sequence[-1] + sequence[-2])
            return sequence
        else:
            # Random pattern
            return [random.randint(1, 20) for _ in range(length)]
    
    def generate_logic_puzzle(self, puzzle_type: str, difficulty: int) -> LogicPuzzleData:
        """Generate a new logic puzzle on demand"""
        puzzle_name = f"GENERATED_{puzzle_type.upper()}_{random.randint(1000, 9999)}"
        
        if puzzle_type == "mastermind":
            length = 3 + difficulty
            max_value = 4 + difficulty
            pattern = self.generate_mastermind_pattern(length, max_value, difficulty)
            clues = [f"Find the {length}-digit code", f"Numbers 1-{max_value} allowed"]
            constraints = {"length": length, "max_value": max_value}
            
        elif puzzle_type == "sequence":
            seq_types = ["arithmetic", "geometric", "fibonacci_like"]
            seq_type = random.choice(seq_types)
            length = 4 + difficulty
            pattern = self.generate_sequence_pattern(seq_type, length)
            clues = [f"Find the pattern in this {seq_type} sequence"]
            constraints = {"sequence_type": seq_type, "length": length}
            
        else:
            # Default fallback
            pattern = [1, 2, 3, 4]
            clues = ["Simple logic puzzle"]
            constraints = {}
        
        return LogicPuzzleData(
            name=puzzle_name,
            puzzle_type=puzzle_type,
            description=f"Generated {puzzle_type} puzzle",
            difficulty=difficulty,
            pattern=pattern,
            clues=clues,
            constraints=constraints,
            metadata={"category": "generated", "generated": True}
        ) 