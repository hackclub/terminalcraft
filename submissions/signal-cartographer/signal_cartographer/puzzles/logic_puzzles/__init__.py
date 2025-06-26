"""
Logic Puzzles Module for The Signal Cartographer
Exports all logic puzzle classes and supporting modules
"""

from .mastermind_puzzle import MastermindPuzzle
from .sequence_deduction_puzzle import SequenceDeductionPuzzle
from .circuit_completion_puzzle import CircuitCompletionPuzzle
from .rule_inference_puzzle import RuleInferencePuzzle
from .grid_logic_puzzle import GridLogicPuzzle
from .mathematical_sequence_puzzle import MathematicalSequencePuzzle
from .pattern_transformation_puzzle import PatternTransformationPuzzle

from .logic_library import LogicLibrary
from .logic_tools import LogicSolver, SequenceAnalyzer

__all__ = [
    # Main puzzle classes
    "MastermindPuzzle",
    "BullsAndCowsPuzzle", 
    "SequenceDeductionPuzzle",
    "CircuitCompletionPuzzle",
    "RuleInferencePuzzle",
    "GridLogicPuzzle",
    "MathematicalSequencePuzzle",
    "PatternTransformationPuzzle",
    
    # Supporting modules
    "LogicLibrary",
    "LogicSolver",
    "SequenceAnalyzer"
]

__version__ = "1.0.0" 