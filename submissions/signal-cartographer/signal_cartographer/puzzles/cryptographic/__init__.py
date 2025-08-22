"""
Cryptographic Puzzle Suite for The Signal Cartographer
Phase 11.2 Implementation

This module provides cryptographic puzzles and ciphers that work with the 
Cryptographic Analysis tool in the DecoderPane.
"""

from .caesar_cipher_puzzle import CaesarCipherPuzzle
from .vigenere_cipher_puzzle import VigenereCipherPuzzle
from .substitution_cipher_puzzle import SubstitutionCipherPuzzle
from .frequency_analysis_puzzle import FrequencyAnalysisPuzzle
from .cipher_library import CipherLibrary, CipherData
from .cipher_tools import CipherTools, FrequencyAnalyzer

__all__ = [
    'CaesarCipherPuzzle',
    'VigenereCipherPuzzle', 
    'SubstitutionCipherPuzzle',
    'FrequencyAnalysisPuzzle',
    'CipherLibrary',
    'CipherData',
    'CipherTools',
    'FrequencyAnalyzer'
]

__version__ = "1.0.0" 