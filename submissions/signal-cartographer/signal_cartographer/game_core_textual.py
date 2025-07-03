"""
Main game controller for The Signal Cartographer
Manages overall game state and coordinates between systems
"""

import sys
import asyncio
from typing import Optional

from .aethertap_textual import AetherTapTextual
from .signal_system import SignalDetector
from .command_parser import CommandParser


class SignalCartographer:
    """
    Main game controller that manages the AetherTap interface
    and coordinates all game systems.
    """
    
    def __init__(self):
        # Initialize core systems
        self.signal_detector = SignalDetector()
        self.command_parser = CommandParser()
        self.aethertap = None
        self.running = False
        
        # Game state
        self.current_sector = "ALPHA-1"
        self.frequency_range = (100.0, 200.0)
        self.focused_signal = None
        
    def run(self):
        """Start the main game loop with textual interface"""
        try:
            # Initialize the AetherTap textual interface
            self.aethertap = AetherTapTextual(self)
            
            # Setup command parser with game state
            self.command_parser.set_game_state(self)
            
            # Show welcome message and run the app
            self.aethertap.show_startup_sequence()
            
            # Run the textual application
            self.aethertap.run_sync()
            
        except Exception as e:
            print(f"Interface error: {e}")
            print("Falling back to text mode...")
            self._run_text_mode()
    
    async def run_async(self):
        """Run the game asynchronously"""
        try:
            # Initialize the AetherTap textual interface
            self.aethertap = AetherTapTextual(self)
            
            # Setup command parser with game state
            self.command_parser.set_game_state(self)
            
            # Show welcome message and run the app
            self.aethertap.show_startup_sequence()
            
            # Run the textual application asynchronously
            await self.aethertap.run()
            
        except Exception as e:
            print(f"Interface error: {e}")
            print("Falling back to text mode...")
            self._run_text_mode()
    
    def process_command(self, command_str: str) -> Optional[str]:
        """Process a command entered by the player"""
        try:
            result = self.command_parser.parse_and_execute(command_str)
            return result
                
        except Exception as e:
            error_msg = f"Command error: {e}"
            if self.aethertap:
                self.aethertap.show_error(error_msg)
            return error_msg
    
    def quit_game(self):
        """Cleanly quit the game"""
        self.running = False
        if self.aethertap:
            self.aethertap.shutdown()
    
    def _run_text_mode(self):
        """Fallback text-only mode when textual interface is not available"""
        print("\n" + "=" * 60)
        print("  THE SIGNAL CARTOGRAPHER: ECHOES FROM THE VOID")
        print("  Text Mode - Limited Interface")
        print("=" * 60)
        
        # Setup command parser
        self.command_parser.set_game_state(self)
        self.running = True
        
        print("\nWelcome to the AetherTap text interface.")
        print("Type 'help' for available commands, 'quit' to exit.")
        print("")
        
        while self.running:
            try:
                command = input("AetherTap> ").strip()
                if command:
                    if command.lower() in ['quit', 'exit', 'q']:
                        self.running = False
                        print("AetherTap shutting down...")
                        break
                    
                    result = self.command_parser.parse_and_execute(command)
                    if result:
                        print(result)
                        print()
                        
            except KeyboardInterrupt:
                self.running = False
                print("\nSignal lost... AetherTap shutting down.")
            except EOFError:
                self.running = False
                print("\nConnection terminated.")

    # Game state methods for command parser
    def get_current_sector(self) -> str:
        return self.current_sector
    
    def set_current_sector(self, sector: str):
        self.current_sector = sector
        if self.aethertap:
            self.aethertap.update_map(sector)
        
    def get_frequency_range(self) -> tuple:
        return self.frequency_range
    
    def set_frequency_range(self, freq_range: tuple):
        self.frequency_range = freq_range
        if self.aethertap:
            # Update spectrum display with new frequency range
            signals = self.signal_detector.scan_sector(self.current_sector, freq_range)
            self.aethertap.update_spectrum(signals, freq_range)
        
    def get_focused_signal(self):
        return self.focused_signal
    
    def set_focused_signal(self, signal):
        self.focused_signal = signal
        if self.aethertap:
            self.aethertap.focus_signal(signal)
