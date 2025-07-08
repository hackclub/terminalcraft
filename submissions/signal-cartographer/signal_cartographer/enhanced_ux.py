"""
Enhanced User Experience Module for The Signal Cartographer
Implements Day 13-14 UX improvements: better feedback, autocompletion, visual indicators
"""

import time
import difflib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class FeedbackType(Enum):
    """Types of user feedback"""
    SUCCESS = "success"
    ERROR = "error" 
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"
    PROGRESS = "progress"


@dataclass
class CommandFeedback:
    """Enhanced command feedback with context and suggestions"""
    message: str
    feedback_type: FeedbackType
    context_info: str = ""
    suggestions: List[str] = None
    progress_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []


class CommandAutocompletion:
    """Advanced command autocompletion system"""
    
    def __init__(self):
        self.commands = {
            # Core commands
            'scan': {
                'description': 'Scan for signals in sectors',
                'syntax': 'SCAN [sector]',
                'examples': ['SCAN', 'SCAN ALPHA-1', 'SCAN BETA-2'],
                'parameters': ['ALPHA-1', 'BETA-2', 'GAMMA-3', 'DELTA-4', 'EPSILON-5']
            },
            'focus': {
                'description': 'Focus on a specific signal',
                'syntax': 'FOCUS <signal_id>',
                'examples': ['FOCUS SIG_1', 'FOCUS SIG_2'],
                'parameters': []  # Will be populated dynamically
            },
            'analyze': {
                'description': 'Analyze the focused signal',
                'syntax': 'ANALYZE [tool]',
                'examples': ['ANALYZE', 'ANALYZE fourier', 'ANALYZE pattern_recognition'],
                'parameters': ['fourier', 'pattern_recognition', 'cryptographic', 'spectral', 'ascii_manipulation', 'constellation_mapping', 'temporal_sequencing']
            },
            'help': {
                'description': 'Show help information',
                'syntax': 'HELP [command]',
                'examples': ['HELP', 'HELP SCAN', 'HELP ANALYZE'],
                'parameters': []  # Will be populated with command names
            },
            'status': {
                'description': 'Show system status',
                'syntax': 'STATUS',
                'examples': ['STATUS'],
                'parameters': []
            },
            'save': {
                'description': 'Save game state',
                'syntax': 'SAVE [filename]',
                'examples': ['SAVE', 'SAVE mysave', 'SAVE backup'],
                'parameters': []
            },
            'load': {
                'description': 'Load game state',
                'syntax': 'LOAD [filename]',
                'examples': ['LOAD', 'LOAD mysave', 'LOAD backup'],
                'parameters': []
            },
            'upgrades': {
                'description': 'View or purchase upgrades',
                'syntax': 'UPGRADES [BUY upgrade_name]',
                'examples': ['UPGRADES', 'UPGRADES BUY scanner_sensitivity'],
                'parameters': ['BUY', 'scanner_sensitivity', 'signal_amplifier', 'frequency_filter', 'deep_space_antenna']
            },
            'achievements': {
                'description': 'View achievement progress',
                'syntax': 'ACHIEVEMENTS',
                'examples': ['ACHIEVEMENTS'],
                'parameters': []
            },
            'progress': {
                'description': 'View progression summary',
                'syntax': 'PROGRESS',
                'examples': ['PROGRESS'],
                'parameters': []
            },
            'performance': {
                'description': 'View performance statistics',
                'syntax': 'PERFORMANCE [action]',
                'examples': ['PERFORMANCE', 'PERFORMANCE CLEANUP', 'PERFORMANCE CLEAR'],
                'parameters': ['CLEANUP', 'CLEAR']
            },
            'clear': {
                'description': 'Clear command log',
                'syntax': 'CLEAR',
                'examples': ['CLEAR'],
                'parameters': []
            },
            'quit': {
                'description': 'Exit the game',
                'syntax': 'QUIT',
                'examples': ['QUIT', 'EXIT'],
                'parameters': []
            }
        }
        
        # Update help parameters with command names
        self.commands['help']['parameters'] = list(self.commands.keys())
    
    def get_completions(self, partial_input: str, game_state=None) -> List[str]:
        """Get autocompletion suggestions for partial input"""
        if not partial_input.strip():
            return list(self.commands.keys())
        
        parts = partial_input.strip().split()
        
        if len(parts) == 1:
            # Complete command name
            command_part = parts[0].lower()
            matches = []
            
            # Exact matches first
            for cmd in self.commands.keys():
                if cmd.startswith(command_part):
                    matches.append(cmd.upper())
            
            # Fuzzy matches if no exact matches
            if not matches:
                close_matches = difflib.get_close_matches(command_part, self.commands.keys(), n=3, cutoff=0.6)
                matches = [cmd.upper() for cmd in close_matches]
            
            return matches
        
        elif len(parts) >= 2:
            # Complete parameters
            command = parts[0].lower()
            if command in self.commands:
                param_part = parts[-1].lower()
                
                # Get dynamic parameters based on game state
                available_params = self._get_dynamic_parameters(command, game_state)
                available_params.extend(self.commands[command]['parameters'])
                
                matches = [param.upper() for param in available_params if param.lower().startswith(param_part)]
                return matches
        
        return []
    
    def _get_dynamic_parameters(self, command: str, game_state) -> List[str]:
        """Get dynamic parameters based on current game state"""
        if not game_state:
            return []
        
        params = []
        
        if command == 'focus':
            # Get available signal IDs from last scan
            if hasattr(game_state, 'last_scan_signals'):
                current_sector = game_state.get_current_sector()
                if current_sector in game_state.last_scan_signals:
                    signals = game_state.last_scan_signals[current_sector]
                    params.extend([f"SIG_{i+1}" for i in range(len(signals))])
        
        elif command == 'scan':
            # Add discovered sectors
            if hasattr(game_state, 'discovered_sectors'):
                params.extend(game_state.discovered_sectors)
        
        return params
    
    def get_command_help(self, command: str) -> Optional[Dict[str, Any]]:
        """Get detailed help for a specific command"""
        cmd_lower = command.lower()
        if cmd_lower in self.commands:
            return self.commands[cmd_lower]
        return None


class VisualIndicators:
    """Enhanced visual indicators and progress bars"""
    
    @staticmethod
    def create_progress_bar(progress: float, width: int = 20, style: str = "modern") -> str:
        """Create enhanced progress bars with different styles"""
        if style == "modern":
            filled = int(progress * width)
            bar = "█" * filled + "░" * (width - filled)
            return f"|{bar}| {progress:.1%}"
        
        elif style == "detailed":
            filled = int(progress * width)
            partial = (progress * width) % 1
            
            # Use different characters for partial fill
            if partial > 0.75:
                partial_char = "▉"
            elif partial > 0.5:
                partial_char = "▊"
            elif partial > 0.25:
                partial_char = "▌"
            elif partial > 0:
                partial_char = "▎"
            else:
                partial_char = ""
            
            full_blocks = "█" * filled
            empty_blocks = "░" * (width - filled - (1 if partial_char else 0))
            
            return f"|{full_blocks}{partial_char}{empty_blocks}| {progress:.1%}"
        
        elif style == "ascii":
            filled = int(progress * width)
            bar = "=" * filled + "-" * (width - filled)
            return f"[{bar}] {progress:.1%}"
        
        return f"{progress:.1%}"
    
    @staticmethod
    def get_status_icon(status: str) -> str:
        """Get appropriate icon for status"""
        status_icons = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'scanning': '🔍',
            'analyzing': '🔬',
            'complete': '✓',
            'pending': '⏳',
            'active': '🟢',
            'inactive': '🔴',
            'unknown': '❓'
        }
        return status_icons.get(status.lower(), '•')
    
    @staticmethod
    def format_command_feedback(feedback: CommandFeedback) -> str:
        """Format command feedback with visual enhancements"""
        icon = VisualIndicators.get_status_icon(feedback.feedback_type.value)
        
        # Color coding based on feedback type
        color_map = {
            FeedbackType.SUCCESS: "green",
            FeedbackType.ERROR: "red", 
            FeedbackType.WARNING: "yellow",
            FeedbackType.INFO: "cyan",
            FeedbackType.HINT: "magenta",
            FeedbackType.PROGRESS: "blue"
        }
        
        color = color_map.get(feedback.feedback_type, "white")
        
        result = f"[{color}]{icon} {feedback.message}[/{color}]"
        
        if feedback.context_info:
            result += f"\n[dim]   Context: {feedback.context_info}[/dim]"
        
        if feedback.suggestions:
            result += f"\n[dim]   💡 Suggestions: {', '.join(feedback.suggestions)}[/dim]"
        
        if feedback.progress_info:
            if 'progress' in feedback.progress_info:
                progress_bar = VisualIndicators.create_progress_bar(
                    feedback.progress_info['progress'], 
                    style=feedback.progress_info.get('style', 'modern')
                )
                result += f"\n[dim]   Progress: {progress_bar}[/dim]"
        
        return result


class ContextualHelp:
    """Context-sensitive help system"""
    
    def __init__(self):
        self.autocompletion = CommandAutocompletion()
    
    def get_contextual_help(self, game_state, current_command: str = "") -> List[str]:
        """Get help based on current game state and situation"""
        help_lines = []
        
        # Analyze current game state
        context = self._analyze_game_context(game_state)
        
        # Provide relevant suggestions
        if context['needs_scan']:
            help_lines.append("🔍 [bold yellow]Next Step:[/bold yellow] Use [cyan]SCAN[/cyan] to search for signals")
            help_lines.append("   Try: [dim]SCAN[/dim] or [dim]SCAN BETA-2[/dim] for different sectors")
        
        elif context['has_signals_unfocused']:
            signal_ids = ", ".join([f"SIG_{i+1}" for i in range(context['signal_count'])])
            help_lines.append(f"🎯 [bold yellow]Signals Found:[/bold yellow] Use [cyan]FOCUS[/cyan] to examine signals")
            help_lines.append(f"   Try: [dim]FOCUS {signal_ids.split(',')[0]}[/dim]")
        
        elif context['has_focused_signal']:
            help_lines.append("🔬 [bold yellow]Signal Focused:[/bold yellow] Use [cyan]ANALYZE[/cyan] to decode the signal")
            help_lines.append("   Try: [dim]ANALYZE[/dim] or [dim]ANALYZE fourier[/dim]")
        
        elif context['analysis_in_progress']:
            help_lines.append("⚡ [bold yellow]Analysis Active:[/bold yellow] Use [cyan]ADVANCE[/cyan] to continue")
            help_lines.append("   Or try: [dim]RESET[/dim] to start over, [dim]TOOLS[/dim] to change method")
        
        # Command-specific help
        if current_command:
            cmd_help = self._get_command_specific_help(current_command, context)
            if cmd_help:
                help_lines.extend(cmd_help)
        
        # Progressive help based on experience
        experience_level = self._assess_experience_level(game_state)
        if experience_level == 'beginner':
            help_lines.append("📚 [dim]New to AetherTap? Try: [cyan]HELP[/cyan] for full command list[/dim]")
        elif experience_level == 'intermediate':
            help_lines.append("🚀 [dim]Pro tip: Use [cyan]UPGRADES[/cyan] to enhance your equipment[/dim]")
        elif experience_level == 'advanced':
            help_lines.append("⭐ [dim]Expert mode: Try [cyan]PERFORMANCE[/cyan] to monitor system efficiency[/dim]")
        
        return help_lines
    
    def _analyze_game_context(self, game_state) -> Dict[str, Any]:
        """Analyze current game context for help suggestions"""
        context = {
            'needs_scan': False,
            'has_signals_unfocused': False,
            'has_focused_signal': False,
            'analysis_in_progress': False,
            'signal_count': 0
        }
        
        if not game_state:
            context['needs_scan'] = True
            return context
        
        # Check for scanned signals
        current_sector = game_state.get_current_sector()
        if hasattr(game_state, 'last_scan_signals') and current_sector in game_state.last_scan_signals:
            signals = game_state.last_scan_signals[current_sector]
            context['signal_count'] = len(signals)
            
            if signals and not game_state.get_focused_signal():
                context['has_signals_unfocused'] = True
            elif game_state.get_focused_signal():
                context['has_focused_signal'] = True
        else:
            context['needs_scan'] = True
        
        # Check if analysis is in progress
        if hasattr(game_state, 'aethertap') and game_state.aethertap:
            # Check decoder pane state for analysis
            try:
                panes = game_state.aethertap.get_panes()
                decoder_pane = panes.get('decoder')
                if decoder_pane and hasattr(decoder_pane, 'analysis_active') and decoder_pane.analysis_active:
                    context['analysis_in_progress'] = True
                    context['has_focused_signal'] = False  # Override since analysis is active
            except:
                pass
        
        return context
    
    def _get_command_specific_help(self, command: str, context: Dict[str, Any]) -> List[str]:
        """Get help specific to the attempted command"""
        cmd_lower = command.lower()
        help_lines = []
        
        if cmd_lower == 'focus' and context['signal_count'] == 0:
            help_lines.append("❌ [red]No signals to focus on. Run [cyan]SCAN[/cyan] first.[/red]")
        
        elif cmd_lower == 'analyze' and not context['has_focused_signal']:
            help_lines.append("❌ [red]No signal focused. Use [cyan]FOCUS SIG_X[/cyan] first.[/red]")
        
        elif cmd_lower == 'scan':
            help_lines.append("🗺️ [dim]Available sectors: ALPHA-1, BETA-2, GAMMA-3, DELTA-4, EPSILON-5[/dim]")
        
        return help_lines
    
    def _assess_experience_level(self, game_state) -> str:
        """Assess user experience level based on gameplay"""
        if not game_state:
            return 'beginner'
        
        total_scans = getattr(game_state, 'total_scan_count', 0)
        
        if hasattr(game_state, 'progression'):
            stats = game_state.progression.get_progression_summary()['stats']
            total_analyses = stats['total_analyses']
            
            if total_analyses >= 20:
                return 'advanced'
            elif total_analyses >= 5:
                return 'intermediate'
        
        if total_scans >= 10:
            return 'intermediate'
        
        return 'beginner'


class StartupSequence:
    """Enhanced startup sequence with progress indicators"""
    
    @staticmethod
    def show_startup_progress(steps: List[str], delay: float = 0.1) -> List[str]:
        """Show startup progress with visual indicators"""
        startup_lines = []
        startup_lines.append("[bold cyan]🚀 AetherTap Signal Cartographer - Initializing...[/bold cyan]")
        startup_lines.append("")
        
        for i, step in enumerate(steps):
            progress = (i + 1) / len(steps)
            progress_bar = VisualIndicators.create_progress_bar(progress, width=30, style="detailed")
            
            icon = VisualIndicators.get_status_icon('active' if i < len(steps) - 1 else 'complete')
            startup_lines.append(f"{icon} {step}")
            startup_lines.append(f"    {progress_bar}")
            
            if i < len(steps) - 1:
                startup_lines.append("")
        
        startup_lines.append("")
        startup_lines.append("[bold green]✅ System Ready - Welcome to AetherTap![/bold green]")
        startup_lines.append("[dim]Type [cyan]HELP[/cyan] for commands or [cyan]SCAN[/cyan] to begin exploring.[/dim]")
        
        return startup_lines


# Global instances for easy access
autocompletion = CommandAutocompletion()
visual_indicators = VisualIndicators()
contextual_help = ContextualHelp()
startup_sequence = StartupSequence()


def create_enhanced_feedback(message: str, feedback_type: FeedbackType, 
                           context: str = "", suggestions: List[str] = None,
                           progress: float = None) -> CommandFeedback:
    """Helper function to create enhanced feedback"""
    progress_info = None
    if progress is not None:
        progress_info = {'progress': progress, 'style': 'detailed'}
    
    return CommandFeedback(
        message=message,
        feedback_type=feedback_type,
        context_info=context,
        suggestions=suggestions or [],
        progress_info=progress_info
    )


def format_enhanced_message(message: str, msg_type: str = "info", 
                          suggestions: List[str] = None) -> str:
    """Quick helper to format messages with enhancements"""
    feedback_types = {
        'success': FeedbackType.SUCCESS,
        'error': FeedbackType.ERROR,
        'warning': FeedbackType.WARNING,
        'info': FeedbackType.INFO,
        'hint': FeedbackType.HINT,
        'progress': FeedbackType.PROGRESS
    }
    
    feedback = create_enhanced_feedback(
        message=message,
        feedback_type=feedback_types.get(msg_type, FeedbackType.INFO),
        suggestions=suggestions or []
    )
    
    return visual_indicators.format_command_feedback(feedback) 