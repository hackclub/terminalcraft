"""
Input handler for the AetherTap interface
"""

from typing import Optional, Callable, List
from textual.widgets import Input
from textual.events import Key
from textual import events

class CommandInput(Input):
    """Command input widget for AetherTap with autocompletion"""
    
    def __init__(self, command_handler: Optional[Callable] = None, **kwargs):
        super().__init__(
            placeholder="🎮 TYPE COMMANDS HERE → Try: SCAN, HELP, FOCUS SIG_1...", 
            **kwargs
        )
        self.command_handler = command_handler
        self.last_command = ""
        
        # Initialize autocompletion system
        try:
            from src.enhanced_ux import CommandAutocompletion
            self.autocomplete = CommandAutocompletion()
        except ImportError:
            # Fallback if enhanced UX not available
            self.autocomplete = None
        self.suggestion_index = 0
        self.current_suggestions = []
        self.original_input = ""
    
    async def on_key(self, event: events.Key) -> None:
        """Handle key events for autocompletion"""
        if event.key == "tab":
            # Handle tab completion
            event.prevent_default()
            await self._handle_tab_completion()
        elif event.key == "escape":
            # Clear suggestions
            self._clear_suggestions()
            event.prevent_default()
        # For all other keys, just clear suggestions and let the Input widget handle them naturally
        # Do NOT call super().on_key() as it doesn't exist in the Input class
        else:
            self._clear_suggestions()
    
    async def _handle_tab_completion(self):
        """Handle tab completion"""
        if not self.autocomplete:
            self.placeholder = "💡 Autocompletion not available"
            self.set_timer(2.0, self._reset_placeholder)
            return
            
        current_text = self.value
        
        if not self.current_suggestions:
            # First tab - get suggestions
            try:
                suggestions = self.autocomplete.get_completions(current_text)
                if suggestions:
                    self.current_suggestions = suggestions
                    self.suggestion_index = 0
                    self.original_input = current_text
                    # Apply first suggestion intelligently
                    completed_text = self._apply_completion(current_text, self.current_suggestions[0])
                    self.value = completed_text
                else:
                    # No suggestions available
                    self.placeholder = "💡 No suggestions available"
                    self.set_timer(2.0, self._reset_placeholder)
            except Exception as e:
                self.placeholder = f"💡 Autocompletion error: {str(e)}"
                self.set_timer(2.0, self._reset_placeholder)
        else:
            # Subsequent tabs - cycle through suggestions
            self.suggestion_index = (self.suggestion_index + 1) % len(self.current_suggestions)
            completed_text = self._apply_completion(self.original_input, self.current_suggestions[self.suggestion_index])
            self.value = completed_text
        
        # Move cursor to end
        self.cursor_position = len(self.value)
    
    def _apply_completion(self, original_text: str, suggestion: str) -> str:
        """Apply completion intelligently, preserving multi-word commands"""
        parts = original_text.strip().split()
        
        if len(parts) == 1:
            # Single word - replace entire text with suggestion
            return suggestion
        elif len(parts) >= 2:
            # Multi-word - keep all but last word, replace last word with suggestion
            completed_parts = parts[:-1] + [suggestion]
            return ' '.join(completed_parts)
        else:
            return suggestion
    
    def _clear_suggestions(self):
        """Clear current suggestions"""
        self.current_suggestions = []
        self.suggestion_index = 0
        self.original_input = ""
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command submission when Enter is pressed"""
        command = event.value.strip()
        if command:
            self.last_command = command
            
            # Clear suggestions
            self._clear_suggestions()
            
            # Show command being executed (immediate feedback)
            self.placeholder = f"🚀 EXECUTING: {command.upper()}..."
            
            # Call the command handler if set
            if self.command_handler:
                try:
                    self.command_handler(command)
                    # Success feedback
                    self.placeholder = f"✅ EXECUTED: {command.upper()} | Type next command..."
                except Exception as e:
                    # Error feedback  
                    self.placeholder = f"❌ ERROR: {str(e)} | Try again..."
            
            # Clear the input for next command
            self.value = ""
            
            # Reset placeholder after 4 seconds
            self.set_timer(4.0, self._reset_placeholder)
    
    async def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes to show suggestions"""
        current_text = event.value
        
        # Clear previous suggestions when text changes
        self._clear_suggestions()
        
        # Show live preview of completion
        if len(current_text) >= 1 and self.autocomplete:
            try:
                suggestions = self.autocomplete.get_completions(current_text)
                if suggestions:
                    # Show preview of what TAB will complete to
                    first_suggestion = suggestions[0]
                    preview_text = self._apply_completion(current_text, first_suggestion)
                    
                    # Show the preview with the part that would be added
                    if preview_text.lower().startswith(current_text.lower()):
                        remaining = preview_text[len(current_text):]
                        self.placeholder = f"💡 TAB → {current_text}[b]{remaining}[/b] | {len(suggestions)} options"
                    else:
                        # For multi-word commands, show full preview
                        self.placeholder = f"💡 TAB → {preview_text} | {len(suggestions)} options"
                else:
                    self.placeholder = "🎮 TYPE COMMANDS HERE → Try: SCAN, HELP, FOCUS SIG_1..."
            except Exception:
                self.placeholder = "🎮 TYPE COMMANDS HERE → Try: SCAN, HELP, FOCUS SIG_1..."
        else:
            self.placeholder = "🎮 TYPE COMMANDS HERE → Try: SCAN, HELP, FOCUS SIG_1..."
    
    def _reset_placeholder(self):
        """Reset placeholder to default"""
        self.placeholder = "🎮 TYPE COMMANDS HERE → Try: SCAN, HELP, FOCUS SIG_1..."

class AetherTapInputHandler:
    """Basic input handler for compatibility"""
    
    def __init__(self, app):
        self.app = app
        self.commands = {}
        
    def register_command_callback(self, command: str, callback: Callable):
        """Register a command callback"""
        self.commands[command] = callback
    
    async def handle_command(self, command: str):
        """Handle a command"""
        parts = command.split()
        if parts:
            cmd = parts[0].lower()
            if cmd in self.commands:
                await self.commands[cmd](parts[1:])
            else:
                await self._handle_default_command(cmd, parts[1:])
    
    async def _handle_default_command(self, command: str, args: list):
        """Handle unknown commands"""
        await self._add_log_entry(f"Unknown command: {command}")
    
    async def _show_help(self):
        """Show help"""
        help_text = """
Available Commands:
  SCAN [sector] - Scan for signals
  FOCUS <signal_id> - Focus on a signal
  ANALYZE - Analyze focused signal
  STATUS - Show system status
  HELP - Show this help
  QUIT - Exit application
"""
        await self._add_log_entry(help_text)
    
    async def _clear_logs(self):
        """Clear logs"""
        await self._add_log_entry("Logs cleared")
    
    async def _add_log_entry(self, message: str):
        """Add a log entry"""
        # This would be implemented to add to the log pane
        print(f"LOG: {message}") 