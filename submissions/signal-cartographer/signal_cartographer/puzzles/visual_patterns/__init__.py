"""
Visual Pattern Matching System for The Signal Cartographer
Phase 11.1 Implementation

This module provides visual pattern recognition puzzles that work with the 
Pattern Recognition Engine and Constellation Mapper tools.
"""

from .constellation_puzzle import ConstellationIdentificationPuzzle
from .pattern_fragment_puzzle import PatternFragmentPuzzle
from .symbol_recognition_puzzle import SymbolRecognitionPuzzle
from .noise_filter_puzzle import NoiseFilterPuzzle
from .pattern_library import PatternLibrary, ConstellationLibrary
from .pattern_matcher import PatternMatcher

__all__ = [
    'ConstellationIdentificationPuzzle',
    'PatternFragmentPuzzle', 
    'SymbolRecognitionPuzzle',
    'NoiseFilterPuzzle',
    'PatternLibrary',
    'ConstellationLibrary',
    'PatternMatcher'
]

__version__ = "1.0.0" 