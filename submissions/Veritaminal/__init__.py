"""
Veritaminal - Terminal-Based Document Verification Game

A game where players act as border control agents, verifying AI-generated 
documents to approve or deny travelers.
"""

__version__ = '1.0.1'

from game.main import main

# When importing veritaminal, make the main function available at package level
__all__ = ['main']
