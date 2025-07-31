#!/usr/bin/env python3
"""
Standalone entry point for TermiCast executable
This avoids relative import issues with PyInstaller
"""

import sys
import os

# Add the current directory to the Python path so we can import termicast
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import and run the main CLI function
from termicast.cli import main

if __name__ == "__main__":
    main() 