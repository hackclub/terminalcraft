#!/usr/bin/env python3
"""TerminalOS - A complete OS experience in your terminal."""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from desktop.desktop import TerminalOSApp

def main():
    """Main entry point for TerminalOS."""
    app = TerminalOSApp()
    app.run()

if __name__ == "__main__":
    main()