"""
Puzzle & Decoding Systems for The Signal Cartographer
Phase 11 Implementation

This module provides interactive puzzle systems that enhance the analysis tools
with engaging gameplay mechanics including pattern recognition, cryptography,
logic puzzles, and audio pattern interpretation.
"""

from .puzzle_base import BasePuzzle, PuzzleState, PuzzleResult, PuzzleDifficulty
from .puzzle_manager import PuzzleManager
from .difficulty import DifficultyScaler

__all__ = [
    'BasePuzzle',
    'PuzzleState', 
    'PuzzleResult',
    'PuzzleDifficulty',
    'PuzzleManager',
    'DifficultyScaler'
]

__version__ = "1.0.1"
__author__ = "Maverick"
