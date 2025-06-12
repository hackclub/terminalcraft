"""
Command parser for the AetherTap CLI interface
Handles parsing and executing player commands
Enhanced with Day 13-14 UX improvements
"""

import time
import difflib
from typing import Optional, Dict, Callable, Any, List

# Performance optimization imports
try:
    from .performance_optimizations import (
        performance_monitor,
        debounce,
        memory_manager,
        render_cache,
        error_handler
    )
    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False
    
    def performance_monitor(func):
        return func
    
    def debounce(wait_time):
        def decorator(func):
            return func
        return decorator


class CommandParser:
    """
    Parses and executes commands entered in the CLI
    Enhanced with better feedback and user experience features
    """
    
    def __init__(self):
        self.game_state: Optional[Any] = None
        self.last_command_time = {}  # For command throttling
        self.command_history = []    # Track command history
        
        # Command registry
        self.commands: Dict[str, Callable] = {
            'help': self.cmd_help,
            'scan': self.cmd_scan,
            'focus': self.cmd_focus,
            'analyze': self.cmd_analyze,
            'status': self.cmd_status,
            'save': self.cmd_save,
            'load': self.cmd_load,
            'quit': self.cmd_quit,
            'exit': self.cmd_quit,
            'clear': self.cmd_clear,
            'upgrades': self.cmd_upgrades,
            'achievements': self.cmd_achievements,
            'progress': self.cmd_progress,
            'performance': self.cmd_performance,
            # Phase 11: Puzzle System Commands
            'puzzle': self.cmd_puzzle,
            'advance': self.cmd_advance,
            'reset': self.cmd_reset,
            'tools': self.cmd_tools,
            'answer': self.cmd_answer,
            'hint': self.cmd_hint,
        }
        
        # Command aliases
        self.aliases = {
            'h': 'help',
            's': 'scan',
            'f': 'focus',
            'a': 'analyze',
            'q': 'quit',
            'perf': 'performance',
        }
        
        # Enhanced command metadata for better help
        self.command_info = {
            'scan': {
                'description': 'Scan for signals in current or specified sector',
                'examples': ['SCAN', 'SCAN BETA-2', 'SCAN DELTA-4'],
                'category': 'exploration'
            },
            'focus': {
                'description': 'Focus on a specific signal for detailed analysis',
                'examples': ['FOCUS SIG_1', 'FOCUS SIG_2'],
                'category': 'analysis'
            },
            'analyze': {
                'description': 'Analyze the currently focused signal',
                'examples': ['ANALYZE', 'ANALYZE fourier'],
                'category': 'analysis'
            },
            'help': {
                'description': 'Show available commands and detailed help',
                'examples': ['HELP', 'HELP SCAN'],
                'category': 'info'
            },
            'upgrades': {
                'description': 'View or purchase equipment upgrades',
                'examples': ['UPGRADES', 'UPGRADES BUY scanner_sensitivity'],
                'category': 'progression'
            }
        }
    
    def set_game_state(self, game_state: Any):
        """Set reference to the main game state"""
        self.game_state = game_state
    
    def get_command_suggestions(self, partial_command: str) -> List[str]:
        """Get command suggestions for autocompletion"""
        if not partial_command:
            return list(self.commands.keys())
        
        partial = partial_command.lower()
        suggestions = []
        
        # Exact matches first
        for cmd in self.commands.keys():
            if cmd.startswith(partial):
                suggestions.append(cmd.upper())
        
        # Include aliases
        for alias, full_cmd in self.aliases.items():
            if alias.startswith(partial):
                suggestions.append(f"{alias.upper()} (={full_cmd.upper()})")
        
        # Fuzzy matches if no exact matches
        if not suggestions:
            close_matches = difflib.get_close_matches(partial, self.commands.keys(), n=3, cutoff=0.6)
            suggestions = [cmd.upper() for cmd in close_matches]
        
        return suggestions
    
    @performance_monitor
    def parse_and_execute(self, command_str: str) -> str:
        """Parse a command string and execute it with enhanced feedback"""
        if not command_str.strip():
            return self._format_suggestion("", "Type a command to begin", 
                                         ["Try 'HELP' for available commands", "Start with 'SCAN' to find signals"])
        
        # Add to command history
        self.command_history.append(command_str.strip())
        if len(self.command_history) > 50:
            self.command_history = self.command_history[-50:]
        
        # Command throttling - prevent spam
        current_time = time.time()
        cmd_hash = hash(command_str.strip().lower())
        
        if cmd_hash in self.last_command_time:
            if current_time - self.last_command_time[cmd_hash] < 0.1:  # 100ms throttle
                return self._format_error("Command rate limited", 
                                        "Too many rapid commands", 
                                        ["Wait a moment between commands"])
        
        self.last_command_time[cmd_hash] = current_time
        
        try:
            # Split command and arguments
            parts = command_str.strip().split()
            cmd_name = parts[0].lower()
            args = parts[1:]
            
            # Check for aliases
            original_cmd = cmd_name
            if cmd_name in self.aliases:
                cmd_name = self.aliases[cmd_name]
                # Show alias tip for beginners
                if len(self.command_history) < 10:
                    alias_tip = f"\n💡 Tip: '{original_cmd}' is short for '{cmd_name.upper()}'"
                    result = self._execute_command(cmd_name, args)
                    return result + alias_tip
            
            # Execute command
            if cmd_name in self.commands:
                result = self._execute_command(cmd_name, args)
                
                # Add contextual suggestions to successful commands
                suggestions = self._get_contextual_suggestions(cmd_name, args)
                if suggestions and not self._is_error_result(result):
                    suggestion_text = f"\n[dim]💡 Next: {', '.join(suggestions)}[/dim]"
                    return result + suggestion_text
                
                return result
            else:
                return self._handle_unknown_command(cmd_name)
                
        except Exception as e:
            if error_handler:
                return error_handler.handle_error(
                    e, "command_parsing",
                    lambda: self._format_error("Command parsing error", str(e), ["Try a simpler command"])
                )
            else:
                return self._format_error("Command parsing error", str(e), ["Try a simpler command"])
    
    def _execute_command(self, cmd_name: str, args: List[str]) -> str:
        """Execute command with enhanced error handling"""
        try:
            return self.commands[cmd_name](args)
        except Exception as e:
            return self._format_error(f"Command '{cmd_name.upper()}' failed", 
                                    str(e),
                                    [f"Check syntax with 'HELP {cmd_name.upper()}'"])
    
    def _handle_unknown_command(self, cmd_name: str) -> str:
        """Handle unknown commands with helpful suggestions"""
        # Find close matches
        all_commands = list(self.commands.keys()) + list(self.aliases.keys())
        close_matches = difflib.get_close_matches(cmd_name, all_commands, n=3, cutoff=0.6)
        
        if close_matches:
            suggestions = [f"'{match.upper()}'" for match in close_matches]
            return self._format_error(f"Unknown command: {cmd_name.upper()}", 
                                    "Command not recognized",
                                    [f"Did you mean: {', '.join(suggestions)}?"])
        else:
            return self._format_error(f"Unknown command: {cmd_name.upper()}", 
                                    "Command not found",
                                    ["Type 'HELP' for available commands"])
    
    def _get_contextual_suggestions(self, cmd_name: str, args: List[str]) -> List[str]:
        """Get contextual suggestions based on command and game state"""
        suggestions = []
        
        if not self.game_state:
            return suggestions
        
        try:
            if cmd_name == 'scan':
                if self._has_available_signals():
                    suggestions.append("FOCUS SIG_1 to examine signals")
            
            elif cmd_name == 'focus':
                suggestions.append("ANALYZE to decode the signal")
            
            elif cmd_name == 'analyze':
                if self._can_upgrade():
                    suggestions.append("UPGRADES to enhance equipment")
                suggestions.append("SCAN to find more signals")
            
            elif cmd_name == 'help' and not args:
                if self._is_beginner():
                    suggestions.append("SCAN to begin exploring")
        
        except Exception:
            pass  # Ignore errors in suggestion generation
        
        return suggestions
    
    def _has_available_signals(self) -> bool:
        """Check if there are signals available to focus on"""
        try:
            if not hasattr(self.game_state, 'last_scan_signals'):
                return False
            
            current_sector = self.game_state.get_current_sector()
            return (current_sector in self.game_state.last_scan_signals and 
                    len(self.game_state.last_scan_signals[current_sector]) > 0)
        except:
            return False
    
    def _can_upgrade(self) -> bool:
        """Check if user can purchase upgrades"""
        try:
            if hasattr(self.game_state, 'progression'):
                return len(self.game_state.progression.get_available_upgrades()) > 0
        except:
            pass
        return False
    
    def _is_beginner(self) -> bool:
        """Check if user is a beginner"""
        return len(self.command_history) < 10
    
    def _is_error_result(self, result: str) -> bool:
        """Check if result indicates an error"""
        error_indicators = ['error', 'failed', 'not found', '❌', 'Error']
        return any(indicator in result for indicator in error_indicators)
    
    def _format_error(self, title: str, detail: str, suggestions: List[str] = None) -> str:
        """Format error message with helpful information"""
        result = f"❌ [red]{title}[/red]"
        if detail:
            result += f"\n   [dim]{detail}[/dim]"
        if suggestions:
            result += f"\n   💡 Try: {', '.join(suggestions)}"
        return result
    
    def _format_success(self, message: str, suggestions: List[str] = None) -> str:
        """Format success message with next steps"""
        result = f"✅ [green]{message}[/green]"
        if suggestions:
            result += f"\n   💡 Next: {', '.join(suggestions)}"
        return result
    
    def _format_suggestion(self, title: str, detail: str, suggestions: List[str] = None) -> str:
        """Format suggestion message"""
        result = f"💡 [yellow]{title}[/yellow]" if title else ""
        if detail:
            result += f"\n   {detail}" if title else detail
        if suggestions:
            result += f"\n   Try: {', '.join(suggestions)}"
        return result
    
    def cmd_help(self, args: list) -> str:
        """Show available commands"""
        if args and args[0].lower() in self.commands:
            # Show help for specific command
            cmd = args[0].lower()
            help_text = {
                'scan': 'SCAN [sector] - Scan for signals in current or specified sector',
                'focus': 'FOCUS <signal_id> - Focus on a specific signal for analysis',
                'analyze': 'ANALYZE - Analyze the currently focused signal',
                'status': 'STATUS - Show current system status',
                'save': 'SAVE [filename] - Save current game state',
                'load': 'LOAD [filename] - Load saved game state',
                'help': 'HELP [command] - Show help for all commands or specific command',
                'quit': 'QUIT - Exit the AetherTap interface',
                'clear': 'CLEAR - Clear the command log',
                'upgrades': 'UPGRADES - Show or purchase upgrades',
                'achievements': 'ACHIEVEMENTS - Show achievement progress',
                'progress': 'PROGRESS - Show overall progression summary',
            }
            return help_text.get(cmd, f"No help available for {cmd}")
        
        # Show all commands
        return ("Available commands:\n" +
                "  SCAN [sector] - Scan for signals\n" +
                "  FOCUS <id> - Focus on signal\n" +
                "  ANALYZE - Analyze focused signal\n" +
                "  SAVE [file] - Save game state\n" +
                "  LOAD [file] - Load game state\n" +
                "  STATUS - Show system status\n" +
                "  HELP [cmd] - Show help\n" +
                "  QUIT - Exit interface\n" +
                "  UPGRADES - Show or purchase upgrades\n" +
                "  ACHIEVEMENTS - Show achievement progress\n" +
                "  PROGRESS - Show overall progression summary\n" +
                "Type HELP <command> for detailed information.")
    
    def cmd_scan(self, args: list) -> str:
        """Scan for signals"""
        if not self.game_state:
            return "System error: No game state available"
        
        # Determine sector to scan
        if args:
            sector = args[0].upper()
            target_sector = sector
        else:
            target_sector = self.game_state.get_current_sector()
        
        # Update current sector if changed
        if target_sector != self.game_state.get_current_sector():
            self.game_state.set_current_sector(target_sector)
        
        # Update scan count for progress tracking
        if not hasattr(self.game_state, 'total_scan_count'):
            self.game_state.total_scan_count = 0
        self.game_state.total_scan_count += 1
        
        # Perform scanning
        from .signal_system import SignalDetector
        detector = SignalDetector()
        signals = detector.scan_sector(target_sector)
        
        # Apply upgrade effects if available
        if hasattr(self.game_state, 'get_upgrade_effects'):
            effects = self.game_state.get_upgrade_effects()
            # Apply signal strength boost
            if effects['signal_strength_boost'] > 0:
                for signal in signals:
                    signal.strength = min(1.0, signal.strength * (1 + effects['signal_strength_boost']))
            # Apply noise reduction (could add more noise signals without filter)
            if effects['noise_reduction'] > 0:
                # Remove some noise signals based on filter strength
                signals = [s for s in signals if not (s.modulation in ['Static-Burst', 'Cosmic-Noise', 'Solar-Interference'] and effects['noise_reduction'] > 0.5)]
        
        # Store the scanned signals for the FOCUS command
        if not hasattr(self.game_state, 'last_scan_signals'):
            self.game_state.last_scan_signals = {}
        self.game_state.last_scan_signals[target_sector] = signals
        
        # Update the spectrum display and cartography pane
        if hasattr(self.game_state, 'aethertap') and self.game_state.aethertap:
            self.game_state.aethertap.update_spectrum(signals)
            # Update cartography pane with new sector and signals
            self.game_state.aethertap.update_map(target_sector, signals=signals)
        
        # Track discovered sectors
        if not hasattr(self.game_state, 'discovered_sectors'):
            self.game_state.discovered_sectors = []
        if target_sector not in self.game_state.discovered_sectors:
            self.game_state.discovered_sectors.append(target_sector)
        
        # Progression tracking
        if hasattr(self.game_state, 'on_scan_completed'):
            self.game_state.on_scan_completed(target_sector, len(signals))
        
        if signals:
            signal_list = ", ".join([f"SIG_{i+1}" for i in range(len(signals))])
            return f"Scan complete. Found {len(signals)} signals in {target_sector}: {signal_list}"
        else:
            return f"Scan complete. No signals detected in {target_sector}."
    
    def cmd_focus(self, args: list) -> str:
        """Focus on a specific signal"""
        if not args:
            return "Usage: FOCUS <signal_id> (e.g., FOCUS SIG_1)"
        
        signal_id = args[0].upper()
        
        # Try to find the real signal from the last scan
        if signal_id.startswith('SIG_'):
            try:
                signal_num = int(signal_id[4:])  # Extract number from SIG_N
                
                # Get the real signals from the last scan
                current_sector = self.game_state.get_current_sector()
                if (hasattr(self.game_state, 'last_scan_signals') and 
                    current_sector in self.game_state.last_scan_signals):
                    
                    signals = self.game_state.last_scan_signals[current_sector]
                    if 1 <= signal_num <= len(signals):
                        # Use the real signal from the scan
                        real_signal = signals[signal_num - 1]  # Convert to 0-indexed
                        real_signal.id = signal_id  # Update ID to match user input
                        
                        # Update game state
                        self.game_state.set_focused_signal(real_signal)
                        
                        # Update the focus pane if available
                        if hasattr(self.game_state, 'aethertap') and self.game_state.aethertap:
                            self.game_state.aethertap.focus_signal(real_signal)
                        
                        return (f"Signal {signal_id} focused.\n" +
                                f"Frequency: {real_signal.frequency:.1f} MHz\n" +
                                f"Modulation: {real_signal.modulation}\n" +
                                f"Strength: {real_signal.strength:.2f}")
                    else:
                        return f"Signal {signal_id} not found. Only {len(signals)} signals detected in current scan."
                else:
                    return f"No scan data available for {current_sector}. Use SCAN first to detect signals."
                
            except ValueError:
                return f"Invalid signal ID format: {signal_id}"
        else:
            return f"Signal {signal_id} not found. Use SCAN first to detect signals."
    
    def cmd_analyze(self, args: list) -> str:
        """Analyze the currently focused signal"""
        if not self.game_state or not self.game_state.get_focused_signal():
            return "No signal currently focused. Use FOCUS <signal_id> first."
        
        signal = self.game_state.get_focused_signal()
        
        # Check if specific tool is requested
        tool_name = args[0] if args else None
        
        # Update analysis count for progress tracking
        if not hasattr(self.game_state, 'total_analysis_count'):
            self.game_state.total_analysis_count = 0
        self.game_state.total_analysis_count += 1
        
        # Track analyzed signals
        if not hasattr(self.game_state, 'analyzed_signals'):
            self.game_state.analyzed_signals = []
        if signal.id not in self.game_state.analyzed_signals:
            self.game_state.analyzed_signals.append(signal.id)
        
        # Update decoder panel if available - with Phase 11 puzzle integration
        if hasattr(self.game_state, 'aethertap') and self.game_state.aethertap:
            # Get decoder pane through proper path
            panes = self.game_state.aethertap.get_panes()
            decoder_pane = panes.get('decoder')
            
            if decoder_pane and tool_name:
                # Tool-specific analysis with puzzle integration
                available_tools = ['pattern_recognition', 'cryptographic', 'spectral', 
                                 'ascii_manipulation', 'constellation_mapping', 'temporal_sequencing']
                
                if tool_name in available_tools:
                    decoder_pane.select_tool(tool_name)
                    decoder_pane.start_analysis(signal)
                    
                    # Start puzzle mode if available
                    if hasattr(decoder_pane, 'start_puzzle_mode'):
                        puzzle_started = decoder_pane.start_puzzle_mode()
                        if puzzle_started:
                            return (f"🎯 Interactive analysis started with {tool_name.replace('_', ' ').title()} tool.\n" +
                                   f"A puzzle challenge has been generated for signal {signal.id}.\n" +
                                   f"Use the decoder panel to solve the puzzle and complete analysis.")
                    
                    analysis_result = (f"🔧 Analysis started with {tool_name.replace('_', ' ').title()} tool.\n" +
                                     f"Signal {signal.id} loaded into analysis pipeline.\n" +
                                     f"Use ADVANCE command to progress through analysis stages.")
                else:
                    return (f"Unknown analysis tool: {tool_name}\n" +
                           f"Available tools: {', '.join(available_tools)}")
            elif decoder_pane:
                # Basic analysis
                analysis_result = (f"Signal {signal.id} Analysis:\n" +
                                 f"Frequency: {signal.frequency:.1f} MHz\n" +
                                 f"Strength: {signal.strength:.2f}\n" +
                                 f"Modulation: {signal.modulation}\n" +
                                 f"Sector: {signal.sector}")
                decoder_pane.start_analysis(signal)
            
            # Update interface if available
            if hasattr(self.game_state.aethertap, 'add_log_entry'):
                if tool_name:
                    self.game_state.aethertap.add_log_entry(analysis_result)
                else:
                    self.game_state.aethertap.add_log_entry(f"Basic analysis completed for signal {signal.id}")
        
        # Progression tracking
        achievement_msg = ""
        if hasattr(self.game_state, 'on_analysis_completed'):
            achievement_msg = self.game_state.on_analysis_completed(signal)
        
        # Basic analysis result for when no specific tool is used
        if not tool_name:
            base_result = (f"Analyzing signal {signal.id}...\n" +
                          f"Modulation type: {signal.modulation}\n" +
                          f"Signal appears to contain encoded data.\n" +
                          "Advanced decoding tools required for full analysis.\n\n" +
                          "💡 Tip: Use 'ANALYZE <tool>' for interactive analysis:\n" +
                          "   • ANALYZE pattern_recognition - Visual pattern puzzles\n" +
                          "   • ANALYZE cryptographic - Cipher and code puzzles\n" +
                          "   • ANALYZE spectral - Audio pattern challenges\n" +
                          "   • ANALYZE constellation_mapping - Star pattern games\n" +
                          "   • ANALYZE temporal_sequencing - Logic sequence puzzles\n" +
                          "   • ANALYZE ascii_manipulation - Text transformation puzzles")
        else:
            base_result = analysis_result
        
        # Add achievement notification if earned
        if achievement_msg:
            base_result += f"\n\n{achievement_msg}"
        
        return base_result
    
    def cmd_status(self, args: list) -> str:
        """Show current system status"""
        if not self.game_state:
            return "System error: No game state available"
        
        sector = self.game_state.get_current_sector()
        freq_range = self.game_state.get_frequency_range()
        focused = self.game_state.get_focused_signal()
        
        # Get progress stats
        scan_count = getattr(self.game_state, 'total_scan_count', 0)
        analysis_count = getattr(self.game_state, 'total_analysis_count', 0)
        discovered = getattr(self.game_state, 'discovered_sectors', [])
        
        status = f"=== AetherTap System Status ===\n"
        status += f"Current Sector: {sector}\n"
        status += f"Frequency Range: {freq_range[0]:.1f} - {freq_range[1]:.1f} MHz\n"
        status += f"Focused Signal: {focused.id if focused else 'None'}\n"
        status += f"Sectors Discovered: {len(discovered)}\n"
        status += f"Total Scans: {scan_count}\n"
        status += f"Total Analyses: {analysis_count}\n"
        status += f"System Status: Operational"
        
        return status
    
    def cmd_save(self, args: list) -> str:
        """Save the current game state"""
        if not self.game_state:
            return "System error: No game state available"
        
        # Import save system
        from .utils.save_system import SaveSystem
        save_system = SaveSystem()
        
        # Determine filename
        filename = None
        if args:
            filename = args[0]
            if not filename.endswith('.json'):
                filename += '.json'
        
        # Perform save
        success = save_system.save_game(self.game_state, filename)
        
        if success:
            save_name = filename if filename else "autosave.json"
            return f"Game saved successfully: {save_name}"
        else:
            return "Save failed. Check permissions and disk space."
    
    def cmd_load(self, args: list) -> str:
        """Load a saved game state"""
        if not self.game_state:
            return "System error: No game state available"
        
        # Import save system
        from .utils.save_system import SaveSystem
        save_system = SaveSystem()
        
        # Determine filename
        filename = None
        if args:
            filename = args[0]
            if not filename.endswith('.json'):
                filename += '.json'
        
        # Load save data
        save_data = save_system.load_game(filename)
        
        if save_data is None:
            save_name = filename if filename else "autosave.json"
            return f"Load failed: {save_name} not found or corrupted."
        
        # Apply save data
        success = save_system.apply_save_data(save_data, self.game_state)
        
        if success:
            save_name = filename if filename else "autosave.json"
            # Update interface if available
            if hasattr(self.game_state, 'aethertap') and self.game_state.aethertap:
                # Force refresh of the interface
                sector = self.game_state.get_current_sector()
                self.game_state.aethertap.update_map(sector)
                
                # Update focused signal display if any
                focused = self.game_state.get_focused_signal()
                if focused:
                    self.game_state.aethertap.focus_signal(focused)
            
            return f"Game loaded successfully: {save_name}"
        else:
            return "Load failed: Error applying save data."

    def cmd_quit(self, args: list) -> str:
        """Quit the game"""
        if self.game_state:
            self.game_state.quit_game()
        return "Shutting down AetherTap interface..."
    
    def cmd_clear(self, args: list) -> str:
        """Clear the command log"""
        if self.game_state and hasattr(self.game_state, 'aethertap') and self.game_state.aethertap:
            self.game_state.aethertap.log_entries = ["Command log cleared."]
            self.game_state.aethertap._update_log_pane()
        return "Command log cleared."
    
    def cmd_upgrades(self, args: list) -> str:
        """Show or purchase upgrades"""
        if not hasattr(self.game_state, 'progression'):
            return "Progression system not available."
        
        progression = self.game_state.progression
        
        if not args:
            # Show available upgrades
            result = "=== UPGRADE SYSTEM ===\n"
            result += f"Analysis Points: {progression.analysis_points}\n\n"
            
            # Available upgrades
            available = progression.get_available_upgrades()
            if available:
                result += "Available Upgrades:\n"
                for upgrade in available:
                    result += f"  {upgrade.icon} {upgrade.name} (Cost: {upgrade.cost} points)\n"
                    result += f"     {upgrade.description}\n"
            else:
                result += "No upgrades available. Complete more analyses to unlock upgrades.\n"
            
            # Purchased upgrades
            purchased = progression.get_purchased_upgrades()
            if purchased:
                result += "\nPurchased Upgrades:\n"
                for upgrade in purchased:
                    result += f"  ✅ {upgrade.icon} {upgrade.name} - ACTIVE\n"
            
            result += f"\nUsage: UPGRADES BUY <upgrade_name>"
            return result
        
        elif args[0].upper() == 'BUY' and len(args) > 1:
            # Purchase upgrade
            upgrade_name = '_'.join(args[1:]).lower()
            
            if progression.can_purchase_upgrade(upgrade_name):
                if progression.purchase_upgrade(upgrade_name):
                    upgrade = progression.upgrades[upgrade_name]
                    return f"✅ Upgrade purchased: {upgrade.name}!\n{upgrade.description}"
                else:
                    return "❌ Failed to purchase upgrade."
            else:
                return "❌ Cannot purchase upgrade. Check availability and cost."
        
        else:
            return "Usage: UPGRADES or UPGRADES BUY <upgrade_name>"
    
    def cmd_achievements(self, args: list) -> str:
        """Show achievement progress"""
        if not hasattr(self.game_state, 'progression'):
            return "Progression system not available."
        
        progression = self.game_state.progression
        
        result = "=== ACHIEVEMENTS ===\n"
        
        # Unlocked achievements
        unlocked = progression.get_unlocked_achievements()
        if unlocked:
            result += f"Unlocked ({len(unlocked)}/{len(progression.achievements)}):\n"
            for achievement in unlocked:
                unlock_date = achievement.unlock_date or "Unknown"
                result += f"  🏆 {achievement.icon} {achievement.name}\n"
                result += f"     {achievement.description}\n"
        
        # Progress on remaining achievements
        result += "\nProgress:\n"
        for achievement in progression.achievements.values():
            if not achievement.unlocked and not achievement.hidden:
                progress_pct = (achievement.progress / achievement.target) * 100
                result += f"  📊 {achievement.name}: {achievement.progress}/{achievement.target} ({progress_pct:.1f}%)\n"
        
        return result
    
    def cmd_progress(self, args: list) -> str:
        """Show overall progression summary"""
        if not hasattr(self.game_state, 'progression'):
            return "Progression system not available."
        
        summary = self.game_state.progression.get_progression_summary()
        
        result = "=== PROGRESSION SUMMARY ===\n"
        result += f"Analysis Points: {summary['analysis_points']}\n"
        result += f"Achievements: {summary['achievements_unlocked']}/{summary['total_achievements']}\n"
        result += f"Upgrades: {summary['upgrades_purchased']}/{summary['total_upgrades']}\n\n"
        
        result += "Statistics:\n"
        stats = summary['stats']
        result += f"  Total Scans: {stats['total_scans']}\n"
        result += f"  Total Analyses: {stats['total_analyses']}\n"
        result += f"  Sectors Discovered: {stats['sectors_discovered']}\n"
        result += f"  Unique Signals Found: {len(stats['unique_signals'])}\n"
        
        if summary['next_unlock']:
            result += f"\nNext Achievement: {summary['next_unlock']}"
        
        return result
    
    def cmd_performance(self, args: list) -> str:
        """Show performance statistics and controls"""
        try:
            from .performance_optimizations import (
                memory_manager,
                render_cache,
                error_handler
            )
            
            result = "=== PERFORMANCE STATISTICS ===\n"
            
            # Memory stats
            if memory_manager:
                mem_stats = memory_manager.get_memory_stats()
                result += f"Memory - Tracked Objects: {mem_stats['tracked_objects']}\n"
                result += f"Memory - Allocations: {mem_stats['allocation_count']}\n"
                result += f"Memory - Last Cleanup: {mem_stats['last_cleanup']:.1f}s ago\n"
            
            # Cache stats
            if render_cache:
                cache_stats = render_cache.get_stats()
                result += f"Cache - Size: {cache_stats['size']}/{cache_stats['max_size']}\n"
                result += f"Cache - Hit Rate: {cache_stats['hit_rate']:.1%}\n"
                result += f"Cache - Hits: {cache_stats['hit_count']}\n"
            
            # Error stats
            if error_handler:
                error_stats = error_handler.get_error_stats()
                result += f"Errors - Total: {error_stats['total_errors']}\n"
                if error_stats['error_counts']:
                    result += "Error Types:\n"
                    for error_type, count in error_stats['error_counts'].items():
                        result += f"  {error_type}: {count}\n"
            
            # Game performance stats
            if hasattr(self.game_state, 'total_scan_count'):
                result += f"Game - Total Scans: {self.game_state.total_scan_count}\n"
            
            if hasattr(self.game_state, 'progression'):
                stats = self.game_state.progression.get_progression_summary()['stats']
                result += f"Game - Total Analyses: {stats['total_analyses']}\n"
                result += f"Game - Sectors Discovered: {stats['sectors_discovered']}\n"
            
            # Commands
            if args and args[0].lower() == 'cleanup':
                # Perform manual cleanup
                cleanup_count = 0
                if memory_manager:
                    cleanup_count = memory_manager.cleanup()
                if render_cache:
                    cache_size_before = render_cache.get_stats()['size']
                    # Clear old cache entries
                    for _ in range(cache_size_before // 2):
                        render_cache._evict_oldest()
                    cache_size_after = render_cache.get_stats()['size']
                    result += f"\nCleanup completed. Cache reduced from {cache_size_before} to {cache_size_after} entries."
                result += f"\nMemory cleanup freed {cleanup_count} objects."
            
            elif args and args[0].lower() == 'clear':
                # Clear all caches
                if render_cache:
                    render_cache.clear()
                result += "\nAll caches cleared."
            
            else:
                result += "\nCommands: PERFORMANCE CLEANUP, PERFORMANCE CLEAR"
            
            return result
            
        except ImportError:
            return "Performance monitoring not available."
        except Exception as e:
            return f"Performance command error: {str(e)}"
    
    # Phase 11: Puzzle System Commands
    
    def cmd_puzzle(self, args: list) -> str:
        """Start puzzle mode for current analysis tool"""
        if not self.game_state or not hasattr(self.game_state, 'aethertap') or not self.game_state.aethertap:
            return "❌ AetherTap interface not available."
        
        panes = self.game_state.aethertap.get_panes()
        decoder_pane = panes.get('decoder')
        
        if not decoder_pane or not hasattr(decoder_pane, 'start_puzzle_mode'):
            return "❌ Puzzle system not available."
        
        if not decoder_pane.current_tool:
            return "❌ No analysis tool selected. Use ANALYZE <tool> first."
        
        if decoder_pane.start_puzzle_mode():
            return f"🎯 Puzzle mode activated for {decoder_pane.current_tool.replace('_', ' ').title()}!\nSolve the challenge to complete analysis."
        else:
            return "❌ Failed to start puzzle mode. Check if tool supports puzzles."
    
    def cmd_advance(self, args: list) -> str:
        """Advance analysis stage or puzzle progress"""
        if not self.game_state or not hasattr(self.game_state, 'aethertap') or not self.game_state.aethertap:
            return "❌ AetherTap interface not available."
        
        panes = self.game_state.aethertap.get_panes()
        decoder_pane = panes.get('decoder')
        
        if not decoder_pane:
            return "❌ Decoder pane not available."
        
        if hasattr(decoder_pane, 'puzzle_mode') and decoder_pane.puzzle_mode:
            return "🎯 Puzzle is active. Submit your answer to continue."
        elif decoder_pane.current_tool:
            decoder_pane.advance_analysis()
            return f"⚡ Analysis stage advanced for {decoder_pane.current_tool.replace('_', ' ').title()}."
        else:
            return "❌ No active analysis to advance. Use ANALYZE <tool> first."
    
    def cmd_reset(self, args: list) -> str:
        """Reset current analysis or puzzle"""
        if not self.game_state or not hasattr(self.game_state, 'aethertap') or not self.game_state.aethertap:
            return "❌ AetherTap interface not available."
        
        panes = self.game_state.aethertap.get_panes()
        decoder_pane = panes.get('decoder')
        
        if not decoder_pane:
            return "❌ Decoder pane not available."
        
        if hasattr(decoder_pane, 'reset_analysis'):
            decoder_pane.reset_analysis()
            return "🔄 Analysis reset. Ready for new tool selection."
        else:
            return "❌ Reset functionality not available."
    
    def cmd_tools(self, args: list) -> str:
        """Show available analysis tools"""
        if not self.game_state or not hasattr(self.game_state, 'aethertap') or not self.game_state.aethertap:
            return "❌ AetherTap interface not available."
        
        panes = self.game_state.aethertap.get_panes()
        decoder_pane = panes.get('decoder')
        
        if not decoder_pane:
            return "❌ Decoder pane not available."
        
        if hasattr(decoder_pane, 'analysis_tools'):
            tools = decoder_pane.analysis_tools
            result = "🛠️ AVAILABLE ANALYSIS TOOLS:\n\n"
            
            for tool_id, tool_data in tools.items():
                icon = tool_data['icon']
                name = tool_data['name']
                desc = tool_data['description']
                complexity = tool_data['complexity']
                
                result += f"{icon} {name}\n"
                result += f"   {desc}\n"
                result += f"   Complexity: {complexity}/5 | Command: ANALYZE {tool_id}\n\n"
            
            result += "💡 Use 'ANALYZE <tool_name>' to select and start analysis."
            return result
        else:
            return "❌ Tool information not available."
    
    def cmd_answer(self, args: list) -> str:
        """Submit answer to current puzzle"""
        if not args:
            return "❌ Answer required. Usage: ANSWER <your_answer>"
        
        if not self.game_state or not hasattr(self.game_state, 'aethertap') or not self.game_state.aethertap:
            return "❌ AetherTap interface not available."
        
        panes = self.game_state.aethertap.get_panes()
        decoder_pane = panes.get('decoder')
        
        if not decoder_pane or not hasattr(decoder_pane, 'submit_puzzle_answer'):
            return "❌ Puzzle system not available."
        
        if not hasattr(decoder_pane, 'puzzle_mode') or not decoder_pane.puzzle_mode:
            return "❌ No active puzzle. Start puzzle mode first with PUZZLE command."
        
        answer = ' '.join(args)
        success = decoder_pane.submit_puzzle_answer(answer)
        
        if success:
            return f"✅ Correct! Puzzle solved with answer: {answer}"
        else:
            return f"❌ Incorrect answer: {answer}. Try again or use HINT for help."
    
    def cmd_hint(self, args: list) -> str:
        """Get hint for current puzzle"""
        if not self.game_state or not hasattr(self.game_state, 'aethertap') or not self.game_state.aethertap:
            return "❌ AetherTap interface not available."
        
        panes = self.game_state.aethertap.get_panes()
        decoder_pane = panes.get('decoder')
        
        if not decoder_pane or not hasattr(decoder_pane, 'get_puzzle_hint'):
            return "❌ Puzzle system not available."
        
        if not hasattr(decoder_pane, 'puzzle_mode') or not decoder_pane.puzzle_mode:
            return "❌ No active puzzle. Start puzzle mode first with PUZZLE command."
        
        hint = decoder_pane.get_puzzle_hint()
        
        if hint:
            return f"💡 Hint: {hint.text}"
        else:
            return "❌ No hints available for this puzzle." 