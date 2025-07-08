"""
Layout management for the AetherTap interface
"""

import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static, RichLog
from textual.screen import Screen
from textual.binding import Binding

from .panes import SpectrumPane, SignalFocusPane, CartographyPane, DecoderPane, LogPane
from .input_handler import CommandInput, AetherTapInputHandler
from .colors import AetherTapColors
# Help screen is defined in this file

class AetherTapLayout(Container):
    """Main layout container for the AetherTap interface"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spectrum_pane = None
        self.signal_focus_pane = None
        self.cartography_pane = None
        self.decoder_pane = None
        self.log_pane = None
        self.command_input = None
    
    def compose(self) -> ComposeResult:
        """Compose the layout"""
        # Top row: Spectrum and Signal Focus
        with Horizontal(id="top_row"):
            self.spectrum_pane = SpectrumPane(id="spectrum_pane")
            yield self.spectrum_pane
            self.signal_focus_pane = SignalFocusPane(id="signal_focus_pane")
            yield self.signal_focus_pane
        
        # Middle row: Cartography and Decoder
        with Horizontal(id="middle_row"):
            self.cartography_pane = CartographyPane(id="cartography_pane")
            yield self.cartography_pane
            self.decoder_pane = DecoderPane(id="decoder_pane")
            yield self.decoder_pane
        
        # Bottom section: Log and Command Input
        with Vertical(id="bottom_section"):
            self.log_pane = LogPane(id="log_pane")
            yield self.log_pane
            self.command_input = CommandInput(id="command_input")
            yield self.command_input

class AetherTapScreen(Screen):
    """Main screen for the AetherTap interface"""
    
    def __init__(self, game_controller=None, **kwargs):
        super().__init__(**kwargs)
        self.game_controller = game_controller
        self.aethertap_layout = None
    
    def compose(self) -> ComposeResult:
        """Compose the screen"""
        yield Header(show_clock=True)
        self.aethertap_layout = AetherTapLayout()
        yield self.aethertap_layout
        yield Footer()
    
    async def on_mount(self) -> None:
        """Initialize the screen after mounting"""
        # Set window title
        self.title = "AetherTap - Signal Cartographer"
        
        # Wait a moment for widgets to be fully mounted
        await asyncio.sleep(0.1)
        
        # Initialize panes with default content
        await self._initialize_panes()
        
        # Set up command input after panes are initialized
        if self.aethertap_layout and self.aethertap_layout.command_input:
            self.aethertap_layout.command_input.command_handler = self._handle_command
            # Focus on the command input to enable immediate typing
            self.aethertap_layout.command_input.focus()
            # Make sure it's visible
            if self.aethertap_layout.log_pane:
                self.aethertap_layout.log_pane.add_log_entry("")
                self.aethertap_layout.log_pane.add_log_entry("🎮 READY TO PLAY! Type commands in the PURPLE BOX below!")
                self.aethertap_layout.log_pane.add_log_entry("👉 Try: SCAN → FOCUS SIG_1 → ANALYZE")
                self.aethertap_layout.log_pane.add_log_entry("")
    
    def _handle_command(self, command: str):
        """Handle command input"""
        if not command.strip():
            return
            
        parts = command.strip().split()
        command_name = parts[0].lower()
        
        # Show command being executed immediately
        if self.aethertap_layout and self.aethertap_layout.log_pane:
            self.aethertap_layout.log_pane.add_log_entry(f"")
            self.aethertap_layout.log_pane.add_log_entry(f"🚀 EXECUTING: {command.upper()}")
            self.aethertap_layout.log_pane.add_log_entry(f"▶️ " + "="*40)
        
        # Handle basic commands
        if command_name in ['quit', 'exit', 'q']:
            self.app.exit()
        elif command_name == 'help':
            self._show_help()
        elif command_name == 'clear':
            self._clear_logs()
        else:
            # Pass to game's command parser
            if self.game_controller:
                result = self.game_controller.process_command(command)
                if result and self.aethertap_layout and self.aethertap_layout.log_pane:
                    # Show result with clear formatting
                    self.aethertap_layout.log_pane.add_log_entry(f"✅ RESULT:")
                    for line in result.split('\n'):
                        if line.strip():
                            self.aethertap_layout.log_pane.add_log_entry(f"   {line}")
                    self.aethertap_layout.log_pane.add_log_entry(f"◀️ " + "="*40)
                    
                    # Update displays based on command type
                    if command_name == 'scan':
                        # Update spectrum display
                        signals = self.game_controller.signal_detector.scan_sector(
                            self.game_controller.current_sector, self.game_controller.frequency_range
                        )
                        if self.aethertap_layout.spectrum_pane:
                            self.aethertap_layout.spectrum_pane.update_spectrum(
                                signals, self.game_controller.frequency_range
                            )
                        
                        # Update cartography display with new sector and signals
                        if self.aethertap_layout.cartography_pane:
                            self.aethertap_layout.cartography_pane.update_map(
                                self.game_controller.current_sector, signals=signals
                            )
                        
                        self.aethertap_layout.log_pane.add_log_entry(f"📊 Spectrum display updated!")
                        self.aethertap_layout.log_pane.add_log_entry(f"🗺️ Cartography updated for sector {self.game_controller.current_sector}!")
                        
                    elif command_name == 'focus':
                        # Update signal focus display
                        focused = self.game_controller.get_focused_signal()
                        if self.aethertap_layout.signal_focus_pane:
                            self.aethertap_layout.signal_focus_pane.focus_signal(focused)
                        self.aethertap_layout.log_pane.add_log_entry(f"🔍 Signal focus display updated!")
                        
                    elif command_name in ['save', 'load']:
                        # Update save status display
                        self._update_save_status()
                        
                    elif command_name == 'analyze':
                        # Update decoder display with enhanced analysis using new tools
                        if self.game_controller.focused_signal:
                            # Use the enhanced decoder pane with tool selection
                            if self.aethertap_layout.decoder_pane:
                                # Check if we have additional parameters for tool selection
                                if len(parts) > 1:
                                    tool_name = parts[1].lower()
                                    # Select the specified analysis tool
                                    self.aethertap_layout.decoder_pane.select_tool(tool_name)
                                    self.aethertap_layout.decoder_pane.start_analysis(self.game_controller.focused_signal)
                                    
                                    # Auto-log tool selection and analysis start
                                    tool_data = self.aethertap_layout.decoder_pane.analysis_tools.get(tool_name, {})
                                    complexity = tool_data.get('complexity', 0)
                                    signal_id = getattr(self.game_controller.focused_signal, 'id', 'Unknown')
                                    
                                    self.aethertap_layout.log_pane.add_log_entry(
                                        content=f"Started {tool_name} analysis on signal {signal_id}. Complexity: {complexity}/5",
                                        category='analysis',
                                        title=f"Analysis Started: {tool_name}",
                                        tags=['analysis', 'start', tool_name, f'complexity_{complexity}'],
                                        signal_refs=[signal_id]
                                    )
                                    
                                    self.aethertap_layout.log_pane.add_log_entry(f"🛠️ Started {tool_name} analysis!")
                                else:
                                    # Show tool selection interface
                                    self.aethertap_layout.decoder_pane._display_tool_selection()
                                    self.aethertap_layout.log_pane.add_log_entry(f"🛠️ Decoder toolkit ready - select analysis tool!")
                                    self.aethertap_layout.log_pane.add_log_entry(f"💡 Try: ANALYZE pattern_recognition, ANALYZE cryptographic, etc.")
                        else:
                            self.aethertap_layout.log_pane.add_log_entry(f"⚠️ No signal focused. Use FOCUS SIG_X first!")
                        
                    elif command_name == 'advance' and len(parts) == 1:
                        # Advance current analysis stage
                        if self.aethertap_layout.decoder_pane and self.aethertap_layout.decoder_pane.current_tool:
                            prev_stage = self.aethertap_layout.decoder_pane.analysis_stage
                            self.aethertap_layout.decoder_pane.advance_analysis()
                            new_stage = self.aethertap_layout.decoder_pane.analysis_stage
                            max_stages = self.aethertap_layout.decoder_pane.max_stages
                            tool_name = self.aethertap_layout.decoder_pane.current_tool
                            validation_status = self.aethertap_layout.decoder_pane.validation_status
                            
                            # Auto-log analysis progress
                            if validation_status == "completed":
                                self.aethertap_layout.log_pane.add_log_entry(
                                    content=f"Analysis completed using {tool_name} tool. All {max_stages} stages processed successfully.",
                                    category='analysis',
                                    title=f"Analysis Complete: {tool_name}",
                                    tags=['analysis', 'complete', tool_name, 'success']
                                )
                                self.aethertap_layout.log_pane.add_log_entry(f"✅ Analysis Complete! Results available in decoder pane.")
                            else:
                                stage_names = self.aethertap_layout.decoder_pane.analysis_tools[tool_name]['stages']
                                current_stage_name = stage_names[new_stage-1] if new_stage <= len(stage_names) else 'completion'
                                
                                self.aethertap_layout.log_pane.add_log_entry(
                                    content=f"Advanced {tool_name} analysis to stage {new_stage}: {current_stage_name}",
                                    category='analysis',
                                    title=f"Analysis Stage {new_stage}: {current_stage_name}",
                                    tags=['analysis', 'progress', tool_name, current_stage_name]
                                )
                                self.aethertap_layout.log_pane.add_log_entry(f"⚙️ Advanced to stage {new_stage}/{max_stages}: {current_stage_name}")
                        else:
                            self.aethertap_layout.log_pane.add_log_entry(f"⚠️ No analysis in progress. Start with ANALYZE <tool_name>")
                    
                    elif command_name == 'tools':
                        # Show decoder tool selection
                        if self.aethertap_layout.decoder_pane:
                            self.aethertap_layout.decoder_pane._display_tool_selection()
                            self.aethertap_layout.log_pane.add_log_entry(f"🛠️ Analysis tools displayed")
                        
                    elif command_name == 'reset' and len(parts) == 1:
                        # Reset current analysis
                        if self.aethertap_layout.decoder_pane:
                            prev_tool = self.aethertap_layout.decoder_pane.current_tool
                            prev_stage = self.aethertap_layout.decoder_pane.analysis_stage
                            
                            self.aethertap_layout.decoder_pane.reset_analysis()
                            
                            # Auto-log reset action
                            if prev_tool:
                                self.aethertap_layout.log_pane.add_log_entry(
                                    content=f"Reset {prev_tool} analysis from stage {prev_stage}. Ready for new analysis.",
                                    category='system',
                                    title=f"Analysis Reset: {prev_tool}",
                                    tags=['reset', 'analysis', prev_tool]
                                )
                            
                            self.aethertap_layout.log_pane.add_log_entry(f"🔄 Analysis reset - decoder ready for new analysis")
                        else:
                            self.aethertap_layout.log_pane.add_log_entry(f"⚠️ No decoder pane available")
                    
                    elif command_name == 'log':
                        # Enhanced log commands for Phase 10.5 features
                        if len(parts) > 1:
                            log_command = parts[1].lower()
                            if log_command == 'search' and len(parts) > 2:
                                query = ' '.join(parts[2:])
                                category = 'all'
                                if len(parts) > 3 and parts[3] in self.aethertap_layout.log_pane.log_categories:
                                    category = parts[3]
                                self.aethertap_layout.log_pane.set_view('search', query=query, category=category)
                                self.aethertap_layout.log_pane.add_log_entry(f"🔍 Search results for '{query}' in {category}")
                            elif log_command == 'category' and len(parts) > 2:
                                category = parts[2].lower()
                                self.aethertap_layout.log_pane.set_view('category', category=category)
                                self.aethertap_layout.log_pane.add_log_entry(f"📂 Showing {category} entries")
                            elif log_command == 'bookmarks':
                                self.aethertap_layout.log_pane.set_view('bookmarks')
                                self.aethertap_layout.log_pane.add_log_entry(f"🔖 Showing bookmarked entries")
                            elif log_command == 'timeline':
                                self.aethertap_layout.log_pane.set_view('timeline')
                                self.aethertap_layout.log_pane.add_log_entry(f"⏰ Showing discovery timeline")
                            elif log_command == 'stats':
                                self.aethertap_layout.log_pane.set_view('statistics')
                                self.aethertap_layout.log_pane.add_log_entry(f"📊 Showing database statistics")
                            else:
                                self.aethertap_layout.log_pane.add_log_entry(f"⚠️ Unknown log command: {log_command}")
                        else:
                            self.aethertap_layout.log_pane.set_view('recent')
                            self.aethertap_layout.log_pane.add_log_entry(f"📚 Showing recent log entries")
                        
                    elif command_name == 'bookmark' and len(parts) >= 2:
                        # Add bookmark to log entry
                        entry_id = parts[1].upper()
                        note = ' '.join(parts[2:]) if len(parts) > 2 else ""
                        self.aethertap_layout.log_pane.add_bookmark(entry_id, note)
                        self.aethertap_layout.log_pane.add_log_entry(f"🔖 Bookmarked {entry_id}")
                        
                    elif command_name == 'export' and len(parts) > 1:
                        # Export log data
                        format_type = parts[1].lower()
                        try:
                            if hasattr(self.aethertap_layout.log_pane, 'export_data'):
                                exported_data = self.aethertap_layout.log_pane.export_data(format_type)
                                # Save to file
                                filename = f"signal_cartographer_export_{format_type}.txt"
                                with open(filename, 'w', encoding='utf-8') as f:
                                    f.write(exported_data)
                                self.aethertap_layout.log_pane.add_log_entry(f"💾 Exported to {filename} ({len(exported_data)} chars)")
                            else:
                                self.aethertap_layout.log_pane.add_log_entry(f"❌ Export function not available")
                        except Exception as e:
                            self.aethertap_layout.log_pane.add_log_entry(f"❌ Export failed: {str(e)}")
                            self.aethertap_layout.log_pane.add_log_entry(f"💡 Available formats: text, json, timeline, bookmarks")
                else:
                    self.aethertap_layout.log_pane.add_log_entry(f"⚠️  No result returned for command: {command}")
            else:
                if self.aethertap_layout and self.aethertap_layout.log_pane:
                    self.aethertap_layout.log_pane.add_log_entry(f"❌ Unknown command: {command_name}")
                    self.aethertap_layout.log_pane.add_log_entry(f"💡 Type 'help' for available commands")
    
    def _show_help(self):
        """Display help information - now launches comprehensive help screen"""
        if self.aethertap_layout and self.aethertap_layout.log_pane:
            self.aethertap_layout.log_pane.add_log_entry("")
            self.aethertap_layout.log_pane.add_log_entry("🚀 Launching comprehensive help guide...")
            self.aethertap_layout.log_pane.add_log_entry("📖 Use Enter or Escape to return to AetherTap")
            self.aethertap_layout.log_pane.add_log_entry("")
        
        # Launch the detailed help screen
        self.app.push_screen(HelpScreen())
    
    def _clear_logs(self):
        """Clear the log pane"""
        if self.aethertap_layout and self.aethertap_layout.log_pane:
            self.aethertap_layout.log_pane.clear_logs()
    
    def _update_save_status(self):
        """Update save status information in the log"""
        if self.game_controller and hasattr(self.game_controller, 'save_system'):
            save_info = self.game_controller.save_system.get_last_save_info()
            if save_info:
                if self.aethertap_layout and self.aethertap_layout.log_pane:
                    self.aethertap_layout.log_pane.add_log_entry(
                        f"💾 Last saved: {save_info.get('time', 'Unknown')} to {save_info.get('file', 'autosave.json')}"
                    )

    async def _initialize_panes(self):
        """Initialize all panes with default content"""
        if self.aethertap_layout:
            # Show startup sequence in log
            if self.aethertap_layout.log_pane:
                    startup_messages = [
                        "=" * 60,
                        "  THE SIGNAL CARTOGRAPHER: ECHOES FROM THE VOID",
                    "  AetherTap Terminal Interface v1.2 - ENHANCED",
                        "=" * 60,
                        "",
                    "🔧 System Status:",
                    "✅ Quantum resonance chambers initialized",
                    "✅ Signal detection arrays calibrated",
                    "✅ Frequency databases loaded",
                    "✅ AetherTap ready for operation",
                    "",
                    "🎮 COMMAND INPUT IS THE PURPLE BOX AT BOTTOM!",
                    "👆 Look for the purple-bordered input box below ↓",
                    "",
                    "🚀 GETTING STARTED:",
                    "1. Type 'SCAN' in the purple box → Press Enter",
                    "2. Type 'FOCUS SIG_1' → Press Enter",
                    "3. Type 'ANALYZE' → Press Enter",  
                    "4. Press F1-F5 to switch between panels",
                    "5. Press Ctrl+H for full help guide",
                    "",
                    "💡 Watch how all 6 panels update as you type commands!",
                    "=" * 60
                    ]
                    
                    for message in startup_messages:
                        self.aethertap_layout.log_pane.add_log_entry(message)
                
            # Initialize spectrum pane
            if self.aethertap_layout.spectrum_pane:
                self.aethertap_layout.spectrum_pane.update_spectrum([], (100, 200))
            
            # Initialize signal focus pane
            if self.aethertap_layout.signal_focus_pane:
                self.aethertap_layout.signal_focus_pane.focus_signal(None)
            
            # Initialize cartography pane
            if self.aethertap_layout.cartography_pane:
                self.aethertap_layout.cartography_pane.update_map("Alpha-1")
            
            # Initialize decoder pane
            if self.aethertap_layout.decoder_pane:
                self.aethertap_layout.decoder_pane.update_content(["No active analysis tool"])

class HelpScreen(Screen):
    """Comprehensive help screen with detailed gameplay instructions"""
    
    BINDINGS = [
        Binding("enter", "back_to_game", "Return to Game"),
        Binding("escape", "back_to_game", "Return to Game"),
        Binding("ctrl+c", "quit", "Quit Game"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the help screen"""
        yield Header(show_clock=False)
        with ScrollableContainer():
            yield Static(self._get_help_content(), id="help_content")
        yield Footer()
    
    def _get_help_content(self) -> str:
        """Get comprehensive help content"""
        return """[bold cyan]🚀 THE SIGNAL CARTOGRAPHER - COMPLETE PLAYER GUIDE 🚀[/bold cyan]

[bold yellow]═══════════════════════════════════════════════════════════════════════════════[/bold yellow]

[bold green]🎯 GAME OBJECTIVE[/bold green]
You are a Signal Cartographer exploring the void of space, detecting and analyzing mysterious signals from unknown sources. Your mission is to scan different sectors, focus on interesting signals, and analyze them to uncover their secrets.

[bold green]🖥️ INTERFACE OVERVIEW[/bold green]
The AetherTap interface has 6 main panels:

[bold white]📊 Main Spectrum Analyzer (Top Left)[/bold white]
- Shows detected signals as frequency spikes
- Updates when you run SCAN commands
- Different sectors have different signal patterns

[bold white]🔍 Signal Focus & Data (Top Right)[/bold white]  
- Shows detailed information about a focused signal
- Updates when you use FOCUS commands
- Displays signal strength, frequency, and characteristics

[bold white]🗺️ Cartography & Navigation (Middle Left)[/bold white]
- Shows your current sector and zoom level
- Visual map of signal locations
- Updates based on your scanning activity

[bold white]🛠️ Decoder & Analysis Toolkit (Middle Right)[/bold white]
- Shows results of signal analysis
- Updates when you run ANALYZE commands
- Reveals hidden information about signals

[bold white]📜 Captain's Log & Database (Bottom Left)[/bold white]
- Shows command history and system messages
- Real-time feedback for all your actions
- System status and notifications

[bold white]💻 Command Input (Bottom Right - PURPLE BOX)[/bold white]
- Where you type all commands
- Has a bright purple/violet border
- Shows feedback when commands execute

[bold green]⌨️ ESSENTIAL COMMANDS[/bold green]

[bold cyan]📡 SCANNING COMMANDS:[/bold cyan]
[white]SCAN[/white] - Scan current sector (Alpha-1 by default)
[white]SCAN ALPHA-1[/white] - Scan Alpha-1 sector (3 signals - good for beginners)
[white]SCAN BETA-2[/white] - Scan Beta-2 sector (2 stronger signals)
[white]SCAN GAMMA-3[/white] - Scan Gamma-3 sector (1 powerful signal)
[white]SCAN DELTA-4[/white] - Scan Delta-4 sector (2 advanced signals - NEW!)
[white]SCAN EPSILON-5[/white] - Scan Epsilon-5 sector (1 expert signal - NEW!)

[bold cyan]🔍 SIGNAL ANALYSIS:[/bold cyan]
[white]FOCUS SIG_1[/white] - Focus on the first detected signal
[white]FOCUS SIG_2[/white] - Focus on the second detected signal
[white]FOCUS SIG_3[/white] - Focus on the third detected signal (if available)

[bold cyan]🛠️ ENHANCED ANALYSIS TOOLKIT (Phase 10.4):[/bold cyan]
[white]ANALYZE[/white] - Show available analysis tools
[white]ANALYZE pattern_recognition[/white] - Use Pattern Recognition Engine
[white]ANALYZE cryptographic[/white] - Use Cryptographic Analysis Suite
[white]ANALYZE spectral[/white] - Use Spectral Decomposition Tool
[white]ANALYZE ascii_manipulation[/white] - Use ASCII Data Processor
[white]ANALYZE constellation_mapping[/white] - Use Constellation Mapper
[white]ANALYZE temporal_sequencing[/white] - Use Temporal Sequence Analyzer
[white]ADVANCE[/white] - Advance to next analysis stage
[white]TOOLS[/white] - Show decoder tool selection
[white]RESET[/white] - Reset current analysis

[bold cyan]📚 ENHANCED LOG & DATABASE (Phase 10.5):[/bold cyan]
[white]LOG[/white] - Show recent log entries
[white]LOG search <query>[/white] - Search log entries (e.g., LOG search signal)
[white]LOG category <category>[/white] - Filter by category (discovery, analysis, etc.)
[white]LOG bookmarks[/white] - Show bookmarked entries
[white]LOG timeline[/white] - Show discovery timeline
[white]LOG stats[/white] - Show database statistics
[white]BOOKMARK <entry_id> [note][/white] - Bookmark a log entry
[white]EXPORT <format>[/white] - Export data (text, json, timeline, bookmarks)

[bold cyan]📋 SYSTEM COMMANDS:[/bold cyan]
[white]STATUS[/white] - Show current system status and focused signal
[white]HELP[/white] - Show this comprehensive help (same as Ctrl+H)
[white]CLEAR[/white] - Clear the command log for a fresh start
[white]QUIT[/white] - Exit the game safely

[bold green]🎮 HOTKEYS & NAVIGATION[/bold green]

[bold cyan]Function Keys (Work Anywhere):[/bold cyan]
[white]F1[/white] - Focus on Main Spectrum Analyzer panel
[white]F2[/white] - Focus on Signal Focus & Data panel
[white]F3[/white] - Focus on Cartography & Navigation panel
[white]F4[/white] - Focus on Decoder & Analysis Toolkit panel
[white]F5[/white] - Focus on Captain's Log & Database panel

[bold cyan]Control Keys:[/bold cyan]
[white]Ctrl+H[/white] - Open this detailed help screen
[white]Ctrl+C[/white] - Quit the game safely
[white]Enter[/white] - (In help screen) Return to main game
[white]Escape[/white] - (In help screen) Return to main game

[bold green]🎯 HOW TO PLAY - STEP BY STEP[/bold green]

[bold cyan]Step 1: Start Scanning[/bold cyan]
Type: [white]SCAN[/white]
- This detects signals in the current sector
- Watch the Spectrum Analyzer panel update with signal spikes
- You'll see signals labeled as SIG_1, SIG_2, etc.

[bold cyan]Step 2: Focus on a Signal[/bold cyan]
Type: [white]FOCUS SIG_1[/white]
- This locks onto the first detected signal
- The Signal Focus panel shows detailed information
- You'll see frequency, strength, and characteristics

[bold cyan]Step 3: Analyze the Signal[/bold cyan]
Type: [white]ANALYZE[/white]
- This shows the enhanced analysis toolkit with 6 specialized tools
- Choose a tool: [white]ANALYZE pattern_recognition[/white] or [white]ANALYZE cryptographic[/white]
- Use [white]ADVANCE[/white] to progress through analysis stages
- Each tool has 4 stages: scan → analyze → process → complete

[bold cyan]Step 4: Use Enhanced Features[/bold cyan]
[white]Multi-Stage Analysis:[/white]
- Each analysis tool has 4 stages you advance through
- Watch progress bars and stage indicators in the Decoder pane
- Use [white]ADVANCE[/white] to move to the next stage
- Use [white]RESET[/white] to start over if needed

[white]Enhanced Logging:[/white]
- All actions are automatically logged with categories
- Use [white]LOG search signal[/white] to find signal-related entries
- Use [white]LOG timeline[/white] to see your discovery progression
- Bookmark important findings with [white]BOOKMARK LOG_0001[/white]

[bold cyan]Step 5: Explore Different Analysis Tools[/bold cyan]
Try different analysis approaches:
- [white]pattern_recognition[/white] - Find recurring patterns (complexity 3/5)
- [white]cryptographic[/white] - Decrypt encoded messages (complexity 4/5)  
- [white]spectral[/white] - Analyze frequency components (complexity 5/5)
- [white]ascii_manipulation[/white] - Process ASCII data (complexity 2/5)
- [white]constellation_mapping[/white] - Map to star patterns (complexity 4/5)
- [white]temporal_sequencing[/white] - Analyze time patterns (complexity 3/5)

[bold cyan]Step 6: Explore Different Sectors (5-Tier Difficulty Progression)[/bold cyan]
🟢 [white]SCAN ALPHA-1[/white] - Training Zone (3 signals, Beginner difficulty)
🟡 [white]SCAN BETA-2[/white] - Exploration Zone (2 signals, Easy difficulty)
🟠 [white]SCAN GAMMA-3[/white] - Deep Space (1 signal, Medium difficulty) 
🔴 [white]SCAN DELTA-4[/white] - Anomaly Field (2 signals, Hard difficulty) - NEW!
🟣 [white]SCAN EPSILON-5[/white] - Singularity Core (1 signal, Expert difficulty) - NEW!

[bold yellow]🚀 NEW SIGNAL TYPES:[/bold yellow]
- [white]Bio-Neural[/white] - Complex neural patterns from collective consciousness
- [white]Quantum-Echo[/white] - Dimensional interference from parallel realities
- [white]Singularity-Resonance[/white] - Immense power from gravitational singularity

[bold cyan]Step 7: Use Hotkeys for Quick Navigation[/bold cyan]
- Press F1-F5 to quickly switch between panels
- Use this to monitor different aspects of your analysis
  
[bold green]💡 PRO TIPS[/bold green]

🔹 [white]Start with ALPHA-1[/white] - It has 3 signals, perfect for learning
🔹 [white]Always SCAN before FOCUS[/white] - You need signals to focus on
🔹 [white]Use STATUS[/white] to check what signal you're currently focused on
🔹 [white]Try different analysis tools[/white] - Each reveals different aspects
🔹 [white]Use ADVANCE[/white] to progress through analysis stages step by step
🔹 [white]Check LOG timeline[/white] to track your discovery progression
🔹 [white]Use LOG search[/white] to find specific information quickly
🔹 [white]Bookmark important discoveries[/white] with BOOKMARK command
🔹 [white]Export your data[/white] with EXPORT to save findings
🔹 [white]Try different sectors[/white] - Each has unique signal characteristics
🔹 [white]Watch all panels[/white] - They update in real-time as you work
🔹 [white]Use CLEAR[/white] if your log gets too cluttered
🔹 [white]Press F5[/white] to see your command history anytime

[bold green]🚨 TROUBLESHOOTING[/bold green]

[bold red]Can't see signals?[/bold red] → Run SCAN first
[bold red]FOCUS not working?[/bold red] → Make sure you scanned and signals exist
[bold red]ANALYZE gives no results?[/bold red] → Focus on a signal first
[bold red]Can't type commands?[/bold red] → Click in the purple command box
[bold red]Panels not updating?[/bold red] → Commands are case-sensitive, try uppercase

[bold green]🌟 ADVANCED GAMEPLAY[/bold green]

Once you master the basics, try:
- Scanning all three sectors and comparing signal types
- Analyzing multiple signals in the same sector
- Using function keys to monitor multiple panels simultaneously
- Looking for patterns in signal characteristics across sectors
- Discovering hidden messages in analyzed signals

[bold yellow]═══════════════════════════════════════════════════════════════════════════════[/bold yellow]

[bold green]Ready to explore the void? Press ENTER to return to AetherTap![/bold green]

[dim]Press Enter or Escape to return to the main game interface[/dim]"""

    def action_back_to_game(self):
        """Return to the main game screen"""
        self.app.pop_screen()
    
    def action_quit(self):
        """Quit the application"""
        self.app.exit()

class AetherTapApp(App):
    """Main Textual application for AetherTap"""
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+h", "help", "Help"),
        Binding("f1", "focus_spectrum", "Focus Spectrum"),
        Binding("f2", "focus_signal", "Focus Signal"),
        Binding("f3", "focus_map", "Focus Map"),
        Binding("f4", "focus_decoder", "Focus Decoder"),
        Binding("f5", "focus_log", "Focus Log"),
    ]
    
    CSS = """
    Screen {
        background: #0d1117;
    }
    
    Container {
        border: solid #30363d;
        margin: 0;
        padding: 1;
    }
    
    .pane-title {
        background: #21262d;
        height: 1;
        text-align: center;
        border-bottom: solid #30363d;
        color: #58a6ff;
    }
    
    RichLog {
        background: #0d1117;
        color: #c9d1d9;
        border: none;
        scrollbar-background: #21262d;
        scrollbar-color: #58a6ff;
        min-height: 5;
    }
    
    /* All panes now have scrolling capability */
    BasePane {
        border: solid #58a6ff;
        margin: 0;
        overflow-y: auto;
        scrollbar-background: #21262d;
        scrollbar-color: #58a6ff;
        scrollbar-size: 1 1;
    }
    
    /* Individual pane styling with scrolling */
    SpectrumPane {
        border: solid #58a6ff;
        margin: 0;
        overflow-y: auto;
        scrollbar-background: #21262d;
        scrollbar-color: #58a6ff;
        scrollbar-size: 1 1;
    }
    
    SignalFocusPane {
        border: solid #58a6ff;
        margin: 0;
        overflow-y: auto;
        scrollbar-background: #21262d;
        scrollbar-color: #58a6ff;
        scrollbar-size: 1 1;
    }
    
    CartographyPane {
        border: solid #58a6ff;
        margin: 0;
        overflow-y: auto;
        scrollbar-background: #21262d;
        scrollbar-color: #58a6ff;
        scrollbar-size: 1 1;
    }
    
    DecoderPane {
        border: solid #58a6ff;
        margin: 0;
        overflow-y: auto;
        scrollbar-background: #21262d;
        scrollbar-color: #58a6ff;
        scrollbar-size: 1 1;
    }
    
    #top_row, #middle_row {
        height: 30%;
        min-height: 10;
    }
    
    #bottom_section {
        height: 40%;
        min-height: 12;
    }
    
    #spectrum_pane, #signal_focus_pane, #cartography_pane, #decoder_pane {
        width: 50%;
        min-width: 30;
        overflow-y: auto;
        scrollbar-background: #21262d;
        scrollbar-color: #58a6ff;
        scrollbar-size: 1 1;
    }
    
    #log_pane {
        height: 60%;
        min-height: 6;
        overflow-y: auto;
        scrollbar-background: #21262d;
        scrollbar-color: #58a6ff;
        scrollbar-size: 1 1;
        border: solid #58a6ff;
        margin: 0;
    }
    
    /* Content widgets within scrollable panes */
    #spectrum_pane_content, #signal_focus_pane_content, #cartography_pane_content, #decoder_pane_content, #log_content {
        background: #0d1117;
        color: #c9d1d9;
        padding: 1;
        margin: 0;
        height: auto;
        min-height: 100%;
    }
    
    #command_input {
        height: 40%;
        min-height: 5;
        max-height: 8;
        border: solid #7c3aed;
        background: #1a1a2e;
        margin: 1;
        padding: 1;
    }
    
    CommandInput {
        background: #1a1a2e;
        color: #ffffff;
        border: solid #7c3aed;
        padding: 1;
        min-height: 3;
    }
    
    CommandInput:focus {
        border: solid #58a6ff;
        background: #0f1419;
    }
    
    Input {
        background: #1a1a2e;
        color: #ffffff;
        border: solid #7c3aed;
        padding: 1;
        min-height: 3;
    }
    
    Input:focus {
        border: solid #58a6ff;
        background: #0f1419;
    }
    
    Header {
        background: #21262d;
        color: #7c3aed;
        height: 1;
    }
    
    Footer {
        background: #21262d;
        color: #8b949e;
        height: 1;
    }
    
    /* Help Screen Styling */
    HelpScreen {
        background: #0d1117;
    }
    
    #help_content {
        background: #0d1117;
        color: #c9d1d9;
        padding: 2;
        margin: 1;
        border: solid #58a6ff;
    }
    
    ScrollableContainer {
        background: #0d1117;
        scrollbar-background: #21262d;
        scrollbar-color: #58a6ff;
        scrollbar-size: 1 1;
        overflow-y: auto;
    }
    
    /* Scrollable Pane Styling */
    ScrollablePane {
        border: solid #58a6ff;
        margin: 0;
        overflow-y: auto;
        scrollbar-background: #21262d;
        scrollbar-color: #58a6ff;
        scrollbar-size: 1 1;
    }
    
    /* Enhanced Log Pane Scrolling */
    LogPane {
        overflow-y: auto;
        scrollbar-background: #21262d;
        scrollbar-color: #58a6ff;
        scrollbar-size: 1 1;
        border: solid #58a6ff;
        margin: 0;
        height: auto;
    }
    """
    
    def __init__(self, game_controller=None, **kwargs):
        super().__init__(**kwargs)
        self.game_controller = game_controller
    
    async def on_mount(self) -> None:
        """Set up the application"""
        # Push the main screen
        await self.push_screen(AetherTapScreen(self.game_controller))
    
    def get_current_screen(self) -> AetherTapScreen:
        """Get the current AetherTap screen"""
        return self.screen
    
    def action_focus_spectrum(self):
        """Focus on the spectrum pane (F1)"""
        screen = self.get_current_screen()
        # Only work if we're on the main AetherTap screen
        if isinstance(screen, AetherTapScreen) and hasattr(screen, 'aethertap_layout') and screen.aethertap_layout and screen.aethertap_layout.spectrum_pane:
            screen.aethertap_layout.spectrum_pane.focus()
            if screen.aethertap_layout.log_pane:
                screen.aethertap_layout.log_pane.add_log_entry("Focused on Main Spectrum Analyzer [MSA]")
    
    def action_focus_signal(self):
        """Focus on the signal focus pane (F2)"""
        screen = self.get_current_screen()
        # Only work if we're on the main AetherTap screen
        if isinstance(screen, AetherTapScreen) and hasattr(screen, 'aethertap_layout') and screen.aethertap_layout and screen.aethertap_layout.signal_focus_pane:
            screen.aethertap_layout.signal_focus_pane.focus()
            if screen.aethertap_layout.log_pane:
                screen.aethertap_layout.log_pane.add_log_entry("Focused on Signal Focus & Data [SFD]")
    
    def action_focus_map(self):
        """Focus on the cartography pane (F3)"""
        screen = self.get_current_screen()
        # Only work if we're on the main AetherTap screen
        if isinstance(screen, AetherTapScreen) and hasattr(screen, 'aethertap_layout') and screen.aethertap_layout and screen.aethertap_layout.cartography_pane:
            screen.aethertap_layout.cartography_pane.focus()
            if screen.aethertap_layout.log_pane:
                screen.aethertap_layout.log_pane.add_log_entry("Focused on Cartography & Navigation [CNP]")
    
    def action_focus_decoder(self):
        """Focus on the decoder pane (F4)"""
        screen = self.get_current_screen()
        # Only work if we're on the main AetherTap screen
        if isinstance(screen, AetherTapScreen) and hasattr(screen, 'aethertap_layout') and screen.aethertap_layout and screen.aethertap_layout.decoder_pane:
            screen.aethertap_layout.decoder_pane.focus()
            if screen.aethertap_layout.log_pane:
                screen.aethertap_layout.log_pane.add_log_entry("Focused on Decoder & Analysis Toolkit [DAT]")
    
    def action_focus_log(self):
        """Focus on the log pane (F5)"""
        screen = self.get_current_screen()
        # Only work if we're on the main AetherTap screen
        if isinstance(screen, AetherTapScreen) and hasattr(screen, 'aethertap_layout') and screen.aethertap_layout and screen.aethertap_layout.log_pane:
            screen.aethertap_layout.log_pane.focus()
            if screen.aethertap_layout.log_pane:
                screen.aethertap_layout.log_pane.add_log_entry("Focused on Captain's Log & Database [CLD]")
    
    def action_quit(self):
        """Quit the application (Ctrl+C)"""
        self.exit()
    
    def action_help(self):
        """Show comprehensive help screen (Ctrl+H)"""
        self.push_screen(HelpScreen())
