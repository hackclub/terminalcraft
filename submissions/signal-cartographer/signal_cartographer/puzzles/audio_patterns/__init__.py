"""
Audio Pattern Framework for The Signal Cartographer
Phase 11.4 Implementation

This module provides audio-inspired puzzles including morse code,
rhythm patterns, pulse analysis, and harmonic challenges.
"""

from .morse_code_puzzle import MorseCodePuzzle
from .rhythm_pattern_puzzle import RhythmPatternPuzzle
from .pulse_sequence_puzzle import PulseSequencePuzzle
from .audio_conversion_puzzle import AudioConversionPuzzle
from .harmonic_pattern_puzzle import HarmonicPatternPuzzle
from .temporal_sequence_puzzle import TemporalSequencePuzzle
from .audio_library import AudioLibrary, AudioPatternData
from .audio_tools import AudioAnalyzer, PatternRecognizer

__all__ = [
    'MorseCodePuzzle',
    'RhythmPatternPuzzle',
    'PulseSequencePuzzle',
    'AudioConversionPuzzle',
    'HarmonicPatternPuzzle',
    'TemporalSequencePuzzle',
    'AudioLibrary',
    'AudioPatternData',
    'AudioAnalyzer',
    'PatternRecognizer'
]

__version__ = "1.0.0" 