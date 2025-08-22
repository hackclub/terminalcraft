"""
Main game controller for The Signal Cartographer
Manages overall game state and coordinates between systems
"""

import sys
import asyncio
from typing import Optional

from .aethertap_textual import AetherTapTextual
from .signal_system import SignalDetector
from .command_parser_enhanced import EnhancedCommandParser
from .progression_system import ProgressionSystem


class SignalCartographer:
    """
    Main game controller that manages the AetherTap interface
    and coordinates all game systems.
    """
    
    def __init__(self):
        # Initialize core systems
        self.signal_detector = SignalDetector()
        self.command_parser = EnhancedCommandParser()
        self.aethertap = None
        self.running = False
        
        # Initialize progression system
        self.progression = ProgressionSystem()
        
        # Game state
        self.current_sector = "ALPHA-1"
        self.frequency_range = (100.0, 200.0)
        self.focused_signal = None
        
        # Progress tracking (legacy - now handled by progression system)
        self.total_scan_count = 0
        self.total_analysis_count = 0
        self.discovered_sectors = []
        self.found_signals = {}
        self.analyzed_signals = []
        
        # Session tracking
        import datetime
        self.session_start = datetime.datetime.now().isoformat()
        self.play_time_minutes = 0
        self.last_command = ""
        
        # Initialize save system
        from .utils.save_system import SaveSystem
        self.save_system = SaveSystem()
        self.save_system.set_game_state(self)
        
    def run(self):
        """Start the main game loop with textual interface"""
        try:
            # Initialize the AetherTap textual interface
            self.aethertap = AetherTapTextual(self)
            
            # Setup command parser with game state
            self.command_parser.set_game_state(self)
            
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
    
    # Progression system integration methods
    def on_scan_completed(self, sector: str, signals_found: int):
        """Called when a scan is completed"""
        self.progression.increment_stat('total_scans')
        self.progression.increment_stat('signals_found', signals_found)
        
        # Track sector discovery
        if sector not in self.discovered_sectors:
            self.discovered_sectors.append(sector)
            self.progression.update_stat('sectors_discovered', len(self.discovered_sectors))
            
        # Special achievement for reaching EPSILON-5
        if sector == 'EPSILON-5':
            self.progression._unlock_achievement('deep_space_pioneer')
    
    def on_signal_focused(self, signal):
        """Called when a signal is focused"""
        if signal and hasattr(signal, 'modulation'):
            self.progression.update_stat('unique_signals', signal.modulation)
    
    def on_analysis_completed(self, signal):
        """Called when an analysis is completed"""
        self.progression.increment_stat('total_analyses')
        self.progression.earn_analysis_points(1)  # 1 point per analysis
        
        # Track analyzed signals
        if signal and hasattr(signal, 'id') and signal.id not in self.analyzed_signals:
            self.analyzed_signals.append(signal.id)
        
        # Check for achievement unlocks
        if self.progression.stats['total_analyses'] == 1:
            return "🎉 Achievement Unlocked: First Contact - Analyze your first signal!"
        elif self.progression.stats['total_analyses'] == 10:
            return "🎉 Upgrade Available: Scanner Sensitivity unlocked!"
        
        return None
    
    def get_upgrade_effects(self) -> dict:
        """Get current upgrade effects for game systems"""
        effects = {
            'signal_strength_boost': 0.0,
            'noise_reduction': 0.0,
            'detection_range': 0,
            'sector_range': 0
        }
        
        purchased = self.progression.get_purchased_upgrades()
        for upgrade in purchased:
            if upgrade.id == 'signal_amplifier':
                effects['signal_strength_boost'] = upgrade.effect_value
            elif upgrade.id == 'frequency_filter':
                effects['noise_reduction'] = upgrade.effect_value
            elif upgrade.id == 'scanner_sensitivity':
                effects['detection_range'] = int(upgrade.effect_value)
            elif upgrade.id == 'deep_space_antenna':
                effects['sector_range'] = int(upgrade.effect_value)
        
        return effects
    
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
        old_sector = self.current_sector
        self.current_sector = sector
        if self.aethertap:
            self.aethertap.update_map(sector)
        
        # Auto-save when changing sectors
        if old_sector != sector and hasattr(self, 'save_system'):
            self.save_system.auto_save()
        
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
        
        # Track signal focusing for progression
        self.on_signal_focused(signal)

    async def action_help(self) -> None:
        """Show help via hotkey"""
        self._show_help()
    
    def _handle_command(self, command: str) -> None:
        """Handle commands from input"""
        original_command = command
        command = command.upper().strip()
        
        # Always show the command in log with >> prefix for immediate feedback
        self.log_pane.update_content(f">> {original_command}")
        
        try:
            if command == "HELP" or command == "H":
                self._show_help()
            elif command == "SCAN":
                self._handle_scan()
            elif command.startswith("FOCUS"):
                self._handle_focus(command)
            elif command == "ANALYZE":
                self._handle_analyze()
            elif command == "STATUS":
                self._handle_status()
            elif command == "CLEAR":
                self.log_pane.clear_logs()
            elif command == "QUIT" or command == "EXIT":
                self.action_quit()
            else:
                self.log_pane.update_content(f"Unknown command: {original_command}")
                self.log_pane.update_content("Type HELP for available commands")
                
        except Exception as e:
            self.log_pane.update_content(f"Error executing {original_command}: {str(e)}")
    
    def _show_help(self):
        """Show help information"""
        help_lines = [
            "╔══════════════════════════════════════════════════════════════╗",
            "║                    AETHERTAP COMMAND GUIDE                   ║", 
            "╚══════════════════════════════════════════════════════════════╝",
            "",
            "🔍 SIGNAL DETECTION:",
            "  SCAN [sector]     - Scan for signals (default: ALPHA-1)",
            "  SCAN BETA-2       - Scan Beta-2 sector (5 signals)",
            "  SCAN GAMMA-3      - Scan Gamma-3 sector (7 signals)",
            "",
            "🎯 SIGNAL ANALYSIS:",
            "  FOCUS SIG_1       - Focus on first detected signal",
            "  FOCUS SIG_2       - Focus on second detected signal", 
            "  ANALYZE           - Analyze currently focused signal",
            "",
            "📊 SYSTEM COMMANDS:",
            "  STATUS            - Show system status",
            "  HELP              - Show this help guide",
            "  CLEAR             - Clear command log",
            "  QUIT              - Exit AetherTap",
            "",
            "⌨️  HOTKEYS:",
            "  Ctrl+H            - Quick Help",
            "  F1-F5             - Switch between panels",
            "  Ctrl+C            - Quick Quit",
            "",
            "💡 TIP: Start with 'SCAN' to detect signals!",
            ""
        ]
        
        for line in help_lines:
            self.log_pane.update_content(line)
