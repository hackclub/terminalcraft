"""
Enhanced Command Parser for AetherTap CLI interface
Includes Day 13-14 UX improvements: better feedback, autocompletion, contextual help
"""

import time
import difflib
from typing import Optional, Dict, Callable, Any, List

# Import enhanced UX components
try:
    from .enhanced_ux import (
        FeedbackType, CommandFeedback, CommandAutocompletion,
        VisualIndicators, create_enhanced_feedback, visual_indicators
    )
    UX_AVAILABLE = True
except ImportError:
    UX_AVAILABLE = False
    FeedbackType = None


class EnhancedCommandParser:
    """Enhanced command parser with improved UX features"""
    
    def __init__(self):
        self.game_state: Optional[Any] = None
        self.last_command_time = {}
        self.command_history = []
        self.autocompletion = CommandAutocompletion() if UX_AVAILABLE else None
        
        # Enhanced command registry with metadata
        self.commands: Dict[str, Dict[str, Any]] = {
            'help': {
                'func': self.cmd_help,
                'description': 'Show available commands and help',
                'usage': 'HELP [command]',
                'examples': ['HELP', 'HELP SCAN', 'HELP ANALYZE'],
                'category': 'info'
            },
            'scan': {
                'func': self.cmd_scan,
                'description': 'Scan for signals in current or specified sector',
                'usage': 'SCAN [sector]',
                'examples': ['SCAN', 'SCAN BETA-2', 'SCAN DELTA-4'],
                'category': 'exploration'
            },
            'focus': {
                'func': self.cmd_focus,
                'description': 'Focus on a specific signal for detailed analysis',
                'usage': 'FOCUS <signal_id>',
                'examples': ['FOCUS SIG_1', 'FOCUS SIG_2'],
                'category': 'analysis'
            },
            'analyze': {
                'func': self.cmd_analyze,
                'description': 'Analyze the currently focused signal',
                'usage': 'ANALYZE [tool]',
                'examples': ['ANALYZE', 'ANALYZE fourier', 'ANALYZE pattern_recognition'],
                'category': 'analysis'
            },
            'status': {
                'func': self.cmd_status,
                'description': 'Show current system status and progress',
                'usage': 'STATUS',
                'examples': ['STATUS'],
                'category': 'info'
            },
            'save': {
                'func': self.cmd_save,
                'description': 'Save current game state',
                'usage': 'SAVE [filename]',
                'examples': ['SAVE', 'SAVE my_progress', 'SAVE backup'],
                'category': 'system'
            },
            'load': {
                'func': self.cmd_load,
                'description': 'Load saved game state',
                'usage': 'LOAD [filename]',
                'examples': ['LOAD', 'LOAD my_progress'],
                'category': 'system'
            },
            'upgrades': {
                'func': self.cmd_upgrades,
                'description': 'View or purchase equipment upgrades',
                'usage': 'UPGRADES [BUY upgrade_name]',
                'examples': ['UPGRADES', 'UPGRADES BUY scanner_sensitivity'],
                'category': 'progression'
            },
            'achievements': {
                'func': self.cmd_achievements,
                'description': 'View achievement progress and unlocked rewards',
                'usage': 'ACHIEVEMENTS',
                'examples': ['ACHIEVEMENTS'],
                'category': 'progression'
            },
            'progress': {
                'func': self.cmd_progress,
                'description': 'View overall progression summary',
                'usage': 'PROGRESS',
                'examples': ['PROGRESS'],
                'category': 'progression'
            },
            'performance': {
                'func': self.cmd_performance,
                'description': 'View system performance statistics',
                'usage': 'PERFORMANCE [action]',
                'examples': ['PERFORMANCE', 'PERFORMANCE CLEANUP'],
                'category': 'system'
            },
            'clear': {
                'func': self.cmd_clear,
                'description': 'Clear the command log',
                'usage': 'CLEAR',
                'examples': ['CLEAR'],
                'category': 'system'
            },
            'quit': {
                'func': self.cmd_quit,
                'description': 'Exit AetherTap interface',
                'usage': 'QUIT',
                'examples': ['QUIT', 'EXIT'],
                'category': 'system'
            }
        }
        
        # Command aliases with enhanced feedback
        self.aliases = {
            'h': 'help',
            's': 'scan', 
            'f': 'focus',
            'a': 'analyze',
            'q': 'quit',
            'exit': 'quit',
            'perf': 'performance'
        }
    
    def set_game_state(self, game_state: Any):
        """Set reference to the main game state"""
        self.game_state = game_state
    
    def get_autocompletion_suggestions(self, partial_input: str) -> List[str]:
        """Get autocompletion suggestions for partial input"""
        if not self.autocompletion:
            return []
        return self.autocompletion.get_completions(partial_input, self.game_state)
    
    def parse_and_execute(self, command_str: str) -> str:
        """Parse and execute command with enhanced feedback"""
        if not command_str.strip():
            return self._format_feedback("No command entered.", FeedbackType.INFO, 
                                       suggestions=["Try 'HELP' for available commands"])
        
        # Add to command history
        self.command_history.append(command_str.strip())
        if len(self.command_history) > 50:  # Keep last 50 commands
            self.command_history = self.command_history[-50:]
        
        # Command throttling with enhanced feedback
        current_time = time.time()
        cmd_hash = hash(command_str.strip().lower())
        
        if cmd_hash in self.last_command_time:
            if current_time - self.last_command_time[cmd_hash] < 0.1:
                return self._format_feedback("Command rate limited. Please wait a moment.", 
                                           FeedbackType.WARNING,
                                           context="Prevents system overload")
        
        self.last_command_time[cmd_hash] = current_time
        
        try:
            # Parse command
            parts = command_str.strip().split()
            cmd_name = parts[0].lower()
            args = parts[1:]
            
            # Check for aliases
            if cmd_name in self.aliases:
                original_cmd = cmd_name
                cmd_name = self.aliases[cmd_name]
                # Provide alias feedback for new users
                if self._is_beginner():
                    return self._execute_with_alias_note(cmd_name, args, original_cmd)
            
            # Check for close matches if command not found
            if cmd_name not in self.commands:
                return self._handle_unknown_command(cmd_name, args)
            
            # Execute command with enhanced error handling
            return self._execute_command(cmd_name, args)
            
        except Exception as e:
            return self._format_feedback(f"Command parsing error: {str(e)}", 
                                       FeedbackType.ERROR,
                                       context="Internal system error",
                                       suggestions=["Try a simpler command", "Use 'HELP' for syntax"])
    
    def _execute_command(self, cmd_name: str, args: List[str]) -> str:
        """Execute command with enhanced error handling and feedback"""
        try:
            cmd_info = self.commands[cmd_name]
            result = cmd_info['func'](args)
            
            # Enhance result with contextual suggestions
            enhanced_result = self._enhance_command_result(cmd_name, result, args)
            return enhanced_result
            
        except Exception as e:
            return self._format_feedback(f"Command '{cmd_name.upper()}' failed: {str(e)}", 
                                       FeedbackType.ERROR,
                                       context=f"Error in {cmd_info.get('category', 'unknown')} command",
                                       suggestions=[f"Check syntax: {cmd_info.get('usage', 'N/A')}"])
    
    def _handle_unknown_command(self, cmd_name: str, args: List[str]) -> str:
        """Handle unknown commands with helpful suggestions"""
        # Find close matches
        all_commands = list(self.commands.keys()) + list(self.aliases.keys())
        close_matches = difflib.get_close_matches(cmd_name, all_commands, n=3, cutoff=0.6)
        
        if close_matches:
            suggestions = [f"'{match.upper()}'" for match in close_matches]
            return self._format_feedback(f"Unknown command: {cmd_name.upper()}", 
                                       FeedbackType.ERROR,
                                       context="Command not recognized",
                                       suggestions=[f"Did you mean: {', '.join(suggestions)}?"])
        else:
            return self._format_feedback(f"Unknown command: {cmd_name.upper()}", 
                                       FeedbackType.ERROR,
                                       suggestions=["Type 'HELP' for available commands"])
    
    def _enhance_command_result(self, cmd_name: str, result: str, args: List[str]) -> str:
        """Enhance command results with contextual information and next steps"""
        # Add contextual suggestions based on command and current state
        suggestions = self._get_contextual_suggestions(cmd_name, args)
        
        if suggestions and not "❌" in result and not "Error" in result:
            # Only add suggestions to successful commands
            suggestion_text = f"\n[dim]💡 Next: {', '.join(suggestions)}[/dim]"
            return result + suggestion_text
        
        return result
    
    def _get_contextual_suggestions(self, cmd_name: str, args: List[str]) -> List[str]:
        """Get contextual suggestions based on command and game state"""
        suggestions = []
        
        if not self.game_state:
            return suggestions
        
        if cmd_name == 'scan':
            if self._has_available_signals():
                suggestions.append("Try 'FOCUS SIG_1' to examine signals")
        
        elif cmd_name == 'focus':
            suggestions.append("Use 'ANALYZE' to decode the focused signal")
        
        elif cmd_name == 'analyze':
            if self._analysis_completed():
                suggestions.append("Try 'SCAN' to find more signals")
                if self._can_upgrade():
                    suggestions.append("Check 'UPGRADES' for equipment improvements")
        
        elif cmd_name == 'help' and not args:
            if self._is_beginner():
                suggestions.append("Start with 'SCAN' to begin exploring")
        
        return suggestions
    
    def _has_available_signals(self) -> bool:
        """Check if there are signals available to focus on"""
        if not hasattr(self.game_state, 'last_scan_signals'):
            return False
        
        current_sector = self.game_state.get_current_sector()
        return (current_sector in self.game_state.last_scan_signals and 
                len(self.game_state.last_scan_signals[current_sector]) > 0)
    
    def _analysis_completed(self) -> bool:
        """Check if current analysis is completed"""
        # This would need to check decoder pane state
        return True  # Placeholder
    
    def _can_upgrade(self) -> bool:
        """Check if user can purchase upgrades"""
        if hasattr(self.game_state, 'progression'):
            return len(self.game_state.progression.get_available_upgrades()) > 0
        return False
    
    def _is_beginner(self) -> bool:
        """Check if user is a beginner based on command history and progress"""
        total_commands = len(self.command_history)
        return total_commands < 10
    
    def _execute_with_alias_note(self, cmd_name: str, args: List[str], alias: str) -> str:
        """Execute command and note alias usage for beginners"""
        result = self._execute_command(cmd_name, args)
        alias_note = f"\n[dim]💡 Tip: '{alias}' is short for '{cmd_name.upper()}'[/dim]"
        return result + alias_note
    
    def _format_feedback(self, message: str, feedback_type, context: str = "", 
                        suggestions: List[str] = None) -> str:
        """Format enhanced feedback message"""
        if not UX_AVAILABLE:
            return message
        
        feedback = create_enhanced_feedback(
            message=message,
            feedback_type=feedback_type,
            context=context,
            suggestions=suggestions or []
        )
        return visual_indicators.format_command_feedback(feedback)
    
    # Enhanced implementations of existing commands would go here
    # For now, let's implement the key ones with enhanced feedback
    
    def cmd_help(self, args: list) -> str:
        """Enhanced help command with better formatting and context"""
        if args and args[0].lower() in self.commands:
            cmd = args[0].lower()
            cmd_info = self.commands[cmd]
            
            result = f"[bold cyan]Command: {cmd.upper()}[/bold cyan]\n"
            result += f"Description: {cmd_info['description']}\n"
            result += f"Usage: [yellow]{cmd_info['usage']}[/yellow]\n"
            result += f"Category: [{cmd_info['category']}]\n"
            
            if cmd_info.get('examples'):
                result += "Examples:\n"
                for example in cmd_info['examples']:
                    result += f"  [dim]{example}[/dim]\n"
            
            return result.strip()
        
        # Show categorized command list
        result = "[bold cyan]🎮 AetherTap Command Reference[/bold cyan]\n\n"
        
        categories = {}
        for cmd, info in self.commands.items():
            category = info.get('category', 'other')
            if category not in categories:
                categories[category] = []
            categories[category].append((cmd, info['description']))
        
        category_icons = {
            'exploration': '🔍',
            'analysis': '🔬', 
            'progression': '📈',
            'info': 'ℹ️',
            'system': '⚙️'
        }
        
        for category, commands in categories.items():
            icon = category_icons.get(category, '•')
            result += f"[bold yellow]{icon} {category.title()}[/bold yellow]\n"
            
            for cmd, desc in commands:
                result += f"  [cyan]{cmd.upper():<12}[/cyan] {desc}\n"
            result += "\n"
        
        result += "[dim]Type 'HELP <command>' for detailed information about a specific command.[/dim]"
        return result
    
    def cmd_scan(self, args: list) -> str:
        """Enhanced scan command - delegates to original but with better feedback"""
        # Import and use original command parser for actual functionality
        try:
            from .command_parser import CommandParser
            original_parser = CommandParser()
            original_parser.set_game_state(self.game_state)
            result = original_parser.cmd_scan(args)
            
            # Enhance the result
            if "Found" in result and "signals" in result:
                # Success case - add helpful next steps
                signal_count = result.count("SIG_")
                if signal_count > 0:
                    return self._format_feedback(result, FeedbackType.SUCCESS,
                                               context=f"Sector scan completed successfully",
                                               suggestions=[f"Try 'FOCUS SIG_1' to examine first signal"])
            elif "No signals" in result:
                # No signals found
                suggestions = ["Try scanning other sectors: ALPHA-1, BETA-2, GAMMA-3, DELTA-4, EPSILON-5"]
                return self._format_feedback(result, FeedbackType.INFO,
                                           context="Scan completed with no detections",
                                           suggestions=suggestions)
            
            return result
            
        except Exception as e:
            return self._format_feedback(f"Scan failed: {str(e)}", FeedbackType.ERROR,
                                       suggestions=["Check system status", "Try again"])
    
    def cmd_focus(self, args: list) -> str:
        """Enhanced focus command"""
        if not args:
            available_signals = self._get_available_signal_ids()
            if available_signals:
                return self._format_feedback("Signal ID required for focus operation", 
                                           FeedbackType.ERROR,
                                           context="No signal specified",
                                           suggestions=[f"Available signals: {', '.join(available_signals)}"])
            else:
                return self._format_feedback("No signals available to focus on", 
                                           FeedbackType.ERROR,
                                           context="No scan data found",
                                           suggestions=["Use 'SCAN' to search for signals first"])
        
        # Use original implementation
        try:
            from .command_parser import CommandParser
            original_parser = CommandParser()
            original_parser.set_game_state(self.game_state)
            result = original_parser.cmd_focus(args)
            
            if "Focused on" in result:
                return self._format_feedback(result, FeedbackType.SUCCESS,
                                           suggestions=["Use 'ANALYZE' to decode this signal"])
            elif "not found" in result:
                available_signals = self._get_available_signal_ids()
                return self._format_feedback(result, FeedbackType.ERROR,
                                           suggestions=[f"Available: {', '.join(available_signals)}"] if available_signals else ["Run 'SCAN' first"])
            
            return result
            
        except Exception as e:
            return self._format_feedback(f"Focus failed: {str(e)}", FeedbackType.ERROR)
    
    def _get_available_signal_ids(self) -> List[str]:
        """Get list of available signal IDs from last scan"""
        if not self.game_state or not hasattr(self.game_state, 'last_scan_signals'):
            return []
        
        current_sector = self.game_state.get_current_sector()
        if current_sector in self.game_state.last_scan_signals:
            signals = self.game_state.last_scan_signals[current_sector]
            return [f"SIG_{i+1}" for i in range(len(signals))]
        
        return []
    
    # Delegate other commands to original parser for now
    def cmd_analyze(self, args: list) -> str:
        return self._delegate_to_original('cmd_analyze', args)
    
    def cmd_status(self, args: list) -> str:
        return self._delegate_to_original('cmd_status', args)
    
    def cmd_save(self, args: list) -> str:
        return self._delegate_to_original('cmd_save', args)
    
    def cmd_load(self, args: list) -> str:
        return self._delegate_to_original('cmd_load', args)
    
    def cmd_upgrades(self, args: list) -> str:
        return self._delegate_to_original('cmd_upgrades', args)
    
    def cmd_achievements(self, args: list) -> str:
        return self._delegate_to_original('cmd_achievements', args)
    
    def cmd_progress(self, args: list) -> str:
        return self._delegate_to_original('cmd_progress', args)
    
    def cmd_performance(self, args: list) -> str:
        return self._delegate_to_original('cmd_performance', args)
    
    def cmd_clear(self, args: list) -> str:
        return self._delegate_to_original('cmd_clear', args)
    
    def cmd_quit(self, args: list) -> str:
        return self._delegate_to_original('cmd_quit', args)
    
    def _delegate_to_original(self, method_name: str, args: list) -> str:
        """Delegate command to original parser"""
        try:
            from .command_parser import CommandParser
            original_parser = CommandParser()
            original_parser.set_game_state(self.game_state)
            method = getattr(original_parser, method_name)
            return method(args)
        except Exception as e:
            return self._format_feedback(f"Command failed: {str(e)}", FeedbackType.ERROR) 