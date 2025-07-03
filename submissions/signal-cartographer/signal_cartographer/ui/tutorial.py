"""
Advanced Tutorial System for The Signal Cartographer
Provides comprehensive guidance on gameplay mechanics, button functions, and game systems.
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static, Button, RichLog
from textual.screen import Screen
from textual.binding import Binding

class TutorialMenuScreen(Screen):
    """Main tutorial menu with navigation to different tutorial sections"""
    
    BINDINGS = [
        Binding("escape", "back_to_game", "Return to Game"),
        Binding("ctrl+c", "quit", "Quit Game"),
        Binding("1", "gameplay_mechanics", "Gameplay Guide"),
        Binding("2", "button_functions", "Button Guide"),
        Binding("3", "game_systems", "Systems Guide"),
        Binding("4", "signal_analysis", "Analysis Guide"),
        Binding("h", "back_to_game", "Back to Game"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the tutorial menu"""
        yield Header(show_clock=False)
        with ScrollableContainer():
            yield Static(self._get_menu_content(), id="tutorial_menu")
        yield Footer()
    
    def _get_menu_content(self) -> str:
        """Get the main tutorial menu content"""
        return """[bold cyan]🎓 THE SIGNAL CARTOGRAPHER - TUTORIAL ACADEMY 🎓[/bold cyan]

[bold yellow]═══════════════════════════════════════════════════════════════════════════════[/bold yellow]

[bold green]Welcome to the Comprehensive Tutorial System![/bold green]

Choose a tutorial section to learn about different aspects of the game:

[bold cyan]📚 Available Tutorial Sections:[/bold cyan]

[bold white]1. 🎮 Gameplay Mechanics Tutorial[/bold white]
   → Learn the core game loop, signal discovery, and progression
   → Perfect for new players who want to understand the basics
   → Press [bold green]1[/bold green] or click to start

[bold white]2. ⌨️ Button Functions & Controls Guide[/bold white]
   → Complete reference for all hotkeys, commands, and interface controls
   → Learn function keys, shortcuts, and navigation tricks
   → Press [bold green]2[/bold green] or click to start

[bold white]3. 🔧 Game Systems Overview[/bold white]
   → Deep dive into the AetherTap interface, panes, and their functions
   → Understand how different systems work together
   → Press [bold green]3[/bold green] or click to start

[bold white]4. 🔬 Signal Analysis Walkthrough[/bold white]
   → Step-by-step guide to scanning, focusing, and analyzing signals
   → Interactive examples and pro tips for effective exploration
   → Press [bold green]4[/bold green] or click to start

[bold green]📖 Navigation Tips:[/bold green]
• Use number keys (1-4) to quickly jump to any tutorial
• Press [bold yellow]Escape[/bold yellow] or [bold yellow]H[/bold yellow] to return to the main game anytime
• Each tutorial section has its own navigation and examples
• You can return to this menu from any tutorial section

[bold green]💡 Recommended Learning Path:[/bold green]
For new players: [bold white]1 → 4 → 2 → 3[/bold white]
For experienced players: [bold white]2 → 3[/bold white]

[bold yellow]═══════════════════════════════════════════════════════════════════════════════[/bold yellow]

[bold green]🚀 Ready to become a master Signal Cartographer?[/bold green]
[dim]Choose a tutorial section above, or press Escape to return to AetherTap[/dim]"""

    def action_back_to_game(self):
        """Return to the main game screen"""
        self.app.pop_screen()
    
    def action_quit(self):
        """Quit the application"""
        self.app.exit()
    
    def action_gameplay_mechanics(self):
        """Open gameplay mechanics tutorial"""
        self.app.push_screen(GameplayMechanicsTutorial())
    
    def action_button_functions(self):
        """Open button functions tutorial"""
        self.app.push_screen(ButtonFunctionsTutorial())
    
    def action_game_systems(self):
        """Open game systems tutorial"""
        self.app.push_screen(GameSystemsTutorial())
    
    def action_signal_analysis(self):
        """Open signal analysis tutorial"""
        self.app.push_screen(SignalAnalysisTutorial())

class GameplayMechanicsTutorial(Screen):
    """Tutorial covering core gameplay mechanics"""
    
    BINDINGS = [
        Binding("escape", "back_to_menu", "Back to Menu"),
        Binding("ctrl+c", "quit", "Quit Game"),
        Binding("h", "back_to_game", "Back to Game"),
        Binding("m", "back_to_menu", "Tutorial Menu"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the gameplay mechanics tutorial"""
        yield Header(show_clock=False)
        with ScrollableContainer():
            yield Static(self._get_content(), id="gameplay_tutorial")
        yield Footer()
    
    def _get_content(self) -> str:
        """Get gameplay mechanics tutorial content"""
        return """[bold cyan]🎮 GAMEPLAY MECHANICS TUTORIAL 🎮[/bold cyan]

[bold yellow]═══════════════════════════════════════════════════════════════════════════════[/bold yellow]

[bold green]🎯 What is The Signal Cartographer?[/bold green]

You are an independent Signal Cartographer operating the "AetherTap" - a sophisticated terminal-based rig designed to detect, isolate, and analyze mysterious signals from deep space. These signals come from unknown sources and may contain:

• 🏛️ Remnants of ancient civilizations
• 🛸 Active communications from unknown entities  
• 🌌 Natural cosmic phenomena with hidden patterns
• ⚠️ Dangerous memetic hazards requiring careful analysis
• 🔮 Quantum echoes from parallel dimensions

[bold green]🔄 Core Game Loop[/bold green]

The fundamental gameplay follows this pattern:

[bold cyan]1. SCAN → 2. FOCUS → 3. ANALYZE → 4. DISCOVER[/bold cyan]

[bold white]1. 📡 SCANNING PHASE[/bold white]
- Use SCAN command to sweep frequency bands in different sectors
- Each sector has unique signal characteristics and complexity
- Signals appear as spikes on your spectrum analyzer
- More advanced sectors have stronger but fewer signals

[bold white]2. 🔍 FOCUSING PHASE[/bold white]
- Select interesting signals using FOCUS SIG_X commands
- Isolate signal from background noise
- View detailed signal properties and characteristics
- Each signal has unique signatures and modulation types

[bold white]3. 🛠️ ANALYSIS PHASE[/bold white]
- Use ANALYZE command to decode focused signals
- Different signals require different analysis techniques
- Some may be simple data, others complex puzzles
- Analysis reveals lore, coordinates, or upgrade schematics

[bold white]4. 🌟 DISCOVERY PHASE[/bold white]
- Decoded signals provide lore fragments about the universe
- Some signals give coordinates to new sectors to explore
- Others provide upgrade schematics to enhance your equipment
- Piece together larger mysteries from multiple signal fragments

[bold green]🗺️ Exploration & Progression[/bold green]

[bold cyan]Sector Types & Difficulty:[/bold cyan]
• [bold white]ALPHA Sectors[/bold white]: Beginner-friendly, multiple weak signals, good for learning
• [bold white]BETA Sectors[/bold white]: Intermediate, fewer but stronger signals, more complex analysis
• [bold white]GAMMA Sectors[/bold white]: Advanced, single powerful signals, deep mysteries

[bold cyan]Signal Characteristics:[/bold cyan]
• [bold white]Frequency[/bold white]: Where the signal appears on the spectrum (100-500 MHz typical)
• [bold white]Strength[/bold white]: How powerful the signal is (affects detection difficulty)
• [bold white]Stability[/bold white]: How much the signal drifts (stable signals easier to analyze)
• [bold white]Modulation[/bold white]: The encoding type (hints at analysis method needed)
• [bold white]Origin[/bold white]: Coordinates where the signal originated (if detectable)

[bold green]⚙️ Equipment & Upgrades[/bold green]

Your AetherTap rig can be enhanced with upgrades found through signal analysis:

[bold cyan]Scanner Upgrades:[/bold cyan]
• Increased range and sensitivity
• Wider frequency band coverage
• Better weak signal detection

[bold cyan]Filter Upgrades:[/bold cyan]
• Noise reduction capabilities
• Signal stabilization tools
• Interference elimination

[bold cyan]Decoder Upgrades:[/bold cyan]
• New analysis tools and algorithms
• Support for complex signal types
• Faster decoding capabilities

[bold green]🏆 Victory Conditions & Goals[/bold green]

The Signal Cartographer is about discovery and understanding:

• 📖 [bold white]Lore Collector[/bold white]: Discover and piece together story fragments
• 🗺️ [bold white]Cosmic Cartographer[/bold white]: Map signal sources across multiple sectors
• 🔬 [bold white]Master Analyst[/bold white]: Successfully decode complex signal types
• 🔧 [bold white]Tech Pioneer[/bold white]: Unlock and install advanced equipment upgrades
• 🌌 [bold white]Mystery Solver[/bold white]: Uncover the truth behind major signal phenomena

[bold green]💡 Beginner Strategy Tips[/bold green]

[bold cyan]Start Simple:[/bold cyan]
1. Begin with SCAN ALPHA-1 (has 3 beginner-friendly signals)
2. Focus on SIG_1 first (usually the easiest to analyze)
3. Always ANALYZE immediately after focusing
4. Read all lore fragments - they connect to build larger stories

[bold cyan]Build Your Skills:[/bold cyan]
1. Master the basic SCAN → FOCUS → ANALYZE loop in ALPHA sectors
2. Try different signals in the same sector to see variety
3. Explore BETA sectors when comfortable with basics
4. GAMMA sectors are for experienced cartographers

[bold cyan]Pay Attention To:[/bold cyan]
• Signal strength patterns across different sectors
• Recurring themes in lore fragments
• Coordinate data that might lead to new discoveries
• Equipment upgrade opportunities

[bold yellow]═══════════════════════════════════════════════════════════════════════════════[/bold yellow]

[bold green]🎓 Ready to start your journey as a Signal Cartographer?[/bold green]

[dim]Press M for Tutorial Menu | Press H to return to AetherTap | Press Escape for Tutorial Menu[/dim]"""

    def action_back_to_menu(self):
        """Return to tutorial menu"""
        self.app.pop_screen()
    
    def action_back_to_game(self):
        """Return to main game, bypassing menu"""
        # Pop back to main screen (this tutorial, then menu)
        self.app.pop_screen()  # Pop this tutorial
        self.app.pop_screen()  # Pop tutorial menu
    
    def action_quit(self):
        """Quit the application"""
        self.app.exit()

class ButtonFunctionsTutorial(Screen):
    """Tutorial covering all button functions and controls"""
    
    BINDINGS = [
        Binding("escape", "back_to_menu", "Back to Menu"),
        Binding("ctrl+c", "quit", "Quit Game"),
        Binding("h", "back_to_game", "Back to Game"),
        Binding("m", "back_to_menu", "Tutorial Menu"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the button functions tutorial"""
        yield Header(show_clock=False)
        with ScrollableContainer():
            yield Static(self._get_content(), id="buttons_tutorial")
        yield Footer()
    
    def _get_content(self) -> str:
        """Get button functions tutorial content"""
        return """[bold cyan]⌨️ BUTTON FUNCTIONS & CONTROLS GUIDE ⌨️[/bold cyan]

[bold yellow]═══════════════════════════════════════════════════════════════════════════════[/bold yellow]

[bold green]🎮 Complete Controls Reference[/bold green]

[bold cyan]📱 Function Keys (Work Anywhere in AetherTap):[/bold cyan]

[bold white]F1 - Focus Main Spectrum Analyzer[/bold white]
• Highlights the spectrum display panel (top-left)
• Use when you want to closely monitor signal detection
• Panel shows real-time frequency analysis and signal spikes
• Visual feedback when scanning different sectors

[bold white]F2 - Focus Signal Focus & Data Panel[/bold white]
• Highlights the signal details panel (top-right)
• Use when examining a specific focused signal
• Shows signal characteristics, stability, and properties
• Updates when you use FOCUS commands

[bold white]F3 - Focus Cartography & Navigation Panel[/bold white]
• Highlights the map display panel (middle-left)
• Use for spatial awareness and coordinate tracking
• Shows current sector and zoom level
• Displays discovered signal source locations

[bold white]F4 - Focus Decoder & Analysis Toolkit Panel[/bold white]
• Highlights the analysis workspace (middle-right)
• Use when working with decoded signal data
• Shows analysis results and puzzle interfaces
• Updates when you use ANALYZE commands

[bold white]F5 - Focus Captain's Log & Database Panel[/bold white]
• Highlights the log and database panel (bottom-left)
• Use to review command history and discoveries
• Shows system messages and status updates
• Contains all your exploration records

[bold cyan]🎛️ Global Hotkeys (Work From Any Panel):[/bold cyan]

[bold white]Ctrl+H - Open Tutorial System[/bold white]
• Opens this comprehensive tutorial menu
• Available from anywhere in the interface
• Quick access to all help documentation

[bold white]Ctrl+C - Safe Exit[/bold white]
• Properly exits the game with cleanup
• Saves any progress (when save system is implemented)
• Alternative to QUIT command

[bold white]Ctrl+P - Command Palette (if available)[/bold white]
• Quick command access (system dependent)
• May show available commands in some terminals

[bold cyan]💬 Command Input Box Controls:[/bold cyan]

The command input box (purple-bordered box at bottom-right) supports:

[bold white]Standard Text Input:[/bold white]
• Type commands directly (case-insensitive)
• Auto-focus when typing from anywhere
• Clear visual feedback when commands execute

[bold white]Command History:[/bold white]
• Up Arrow - Previous command
• Down Arrow - Next command (if implemented)
• Saves recently used commands for quick access

[bold white]Input Navigation:[/bold white]
• Home/Ctrl+A - Move to beginning of command
• End/Ctrl+E - Move to end of command
• Ctrl+U - Clear entire command line
• Backspace/Delete - Standard text editing

[bold green]📋 Complete Command Reference[/bold green]

[bold cyan]🔍 Scanning & Detection Commands:[/bold cyan]

[bold white]SCAN[/bold white] - Scan current sector (defaults to ALPHA-1)
[bold white]SCAN ALPHA-1[/bold white] - Training Zone (3 signals, Beginner difficulty)
[bold white]SCAN BETA-2[/bold white] - Exploration Zone (2 signals, Easy difficulty)
[bold white]SCAN GAMMA-3[/bold white] - Deep Space (1 signal, Medium difficulty)
[bold white]SCAN DELTA-4[/bold white] - Anomaly Field (2 signals, Hard difficulty) 🆕
[bold white]SCAN EPSILON-5[/bold white] - Singularity Core (1 signal, Expert difficulty) 🆕

[bold green]🆕 NEW ADVANCED SIGNAL TYPES:[/bold green]
• [bold white]Bio-Neural[/bold white] - Complex neural patterns from collective consciousness
• [bold white]Quantum-Echo[/bold white] - Dimensional interference from parallel realities  
• [bold white]Singularity-Resonance[/bold white] - Immense power from gravitational singularity

[bold cyan]🎯 Signal Focusing Commands:[/bold cyan]

[bold white]FOCUS SIG_1[/bold white] - Focus on first detected signal
[bold white]FOCUS SIG_2[/bold white] - Focus on second detected signal  
[bold white]FOCUS SIG_3[/bold white] - Focus on third detected signal (if available)
[bold white]FOCUS NEXT[/bold white] - Focus on next available signal (if implemented)
[bold white]FOCUS PREV[/bold white] - Focus on previous signal (if implemented)

[bold cyan]🔬 Analysis Commands:[/bold cyan]

[bold white]ANALYZE[/bold white] - Analyze currently focused signal
[bold white]ANALYZE DEEP[/bold white] - Perform deep analysis (if implemented)
[bold white]ANALYZE QUICK[/bold white] - Perform quick scan (if implemented)

[bold cyan]📊 Information Commands:[/bold cyan]

[bold white]STATUS[/bold white] - Show current system status and focused signal
[bold white]INFO[/bold white] - Show detailed system information (if implemented)
[bold white]SIGNALS[/bold white] - List all detected signals in current scan (if implemented)
[bold white]HISTORY[/bold white] - Show command history (if implemented)

[bold cyan]🛠️ System Commands:[/bold cyan]

[bold white]HELP[/bold white] - Open this tutorial system
[bold white]CLEAR[/bold white] - Clear the command log for a fresh start
[bold white]RESET[/bold white] - Reset interface to default state (if implemented)
[bold white]QUIT[/bold white] - Exit the game safely
[bold white]EXIT[/bold white] - Alternative quit command

[bold green]💡 Pro Tips for Efficient Control[/bold green]

[bold cyan]Function Key Workflows:[/bold cyan]
• Scan: F1 → SCAN → Watch spectrum update
• Focus: F2 → FOCUS SIG_X → See signal details
• Analyze: F4 → ANALYZE → View results
• Review: F5 → Check command history

[bold cyan]Keyboard Shortcuts:[/bold cyan]
• Use Tab completion (if available) for command suggestions
• Ctrl+H is faster than typing HELP
• Function keys are faster than clicking panels
• Command history saves typing for repeated commands

[bold cyan]Command Tips:[/bold cyan]
• Commands are case-insensitive (SCAN = scan = Scan)
• Use short forms when available (Q for QUIT)
• STATUS is useful to check your current state
• CLEAR helps when log gets cluttered

[bold yellow]═══════════════════════════════════════════════════════════════════════════════[/bold yellow]

[bold green]⌨️ Master these controls to become an efficient Signal Cartographer![/bold green]

[dim]Press M for Tutorial Menu | Press H to return to AetherTap | Press Escape for Tutorial Menu[/dim]"""

    def action_back_to_menu(self):
        """Return to tutorial menu"""
        self.app.pop_screen()
    
    def action_back_to_game(self):
        """Return to main game, bypassing menu"""
        self.app.pop_screen()  # Pop this tutorial
        self.app.pop_screen()  # Pop tutorial menu
    
    def action_quit(self):
        """Quit the application"""
        self.app.exit()

class GameSystemsTutorial(Screen):
    """Tutorial covering game systems and interface"""
    
    BINDINGS = [
        Binding("escape", "back_to_menu", "Back to Menu"),
        Binding("ctrl+c", "quit", "Quit Game"),
        Binding("h", "back_to_game", "Back to Game"),
        Binding("m", "back_to_menu", "Tutorial Menu"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the game systems tutorial"""
        yield Header(show_clock=False)
        with ScrollableContainer():
            yield Static(self._get_content(), id="systems_tutorial")
        yield Footer()
    
    def _get_content(self) -> str:
        """Get game systems tutorial content"""
        return """[bold cyan]🔧 GAME SYSTEMS OVERVIEW 🔧[/bold cyan]

[bold yellow]═══════════════════════════════════════════════════════════════════════════════[/bold yellow]

[bold green]🖥️ The AetherTap Interface System[/bold green]

Your AetherTap terminal rig is a sophisticated 6-panel interface designed for professional signal analysis. Each panel serves a specific purpose in the signal cartography workflow.

[bold cyan]📊 Panel 1: Main Spectrum Analyzer (MSA) - Top Left[/bold cyan]

[bold white]Purpose:[/bold white]
• Real-time frequency spectrum visualization
• Primary signal detection display
• Background noise monitoring

[bold white]What You See:[/bold white]
• ASCII-based frequency graph showing signal strength
• Signal spikes labeled as SIG_1, SIG_2, SIG_3
• Background noise patterns
• Frequency range indicators (MHz)

[bold white]Updates When:[/bold white]
• SCAN commands are executed
• Different sectors are scanned
• Signal detection algorithms run

[bold white]Visual Indicators:[/bold white]
• Higher ASCII characters = stronger signals
• Different patterns = different signal types
• Empty areas = no signals in that frequency range
• Noise floor = baseline cosmic background

[bold cyan]🔍 Panel 2: Signal Focus & Data (SFD) - Top Right[/bold cyan]

[bold white]Purpose:[/bold white]
• Detailed analysis of isolated signals
• Signal characteristic measurement
• Focus target management

[bold white]What You See:[/bold white]
• Signal ID and classification
• Frequency precision (exact MHz)
• Signal strength measurements
• Stability indicators
• Modulation type classification
• ASCII signature patterns

[bold white]Updates When:[/bold white]
• FOCUS commands target a specific signal
• Signal isolation is performed
• Signal characteristics are measured

[bold white]Key Information:[/bold white]
• Frequency: Exact transmission frequency
• Strength: Signal power level (0.0-1.0)
• Stability: How much the signal drifts
• Modulation: Encoding type (AM, FM, Pulsed, etc.)
• Origin: Source coordinates (if detectable)

[bold cyan]🗺️ Panel 3: Cartography & Navigation (CNP) - Middle Left[/bold cyan]

[bold white]Purpose:[/bold white]
• Spatial awareness and positioning
• Signal source mapping
• Sector navigation tracking

[bold white]What You See:[/bold white]
• Current sector designation (ALPHA-1, BETA-2, etc.)
• Zoom level indicators
• Discovered signal source markers
• Coordinate grid references

[bold white]Updates When:[/bold white]
• Sector scanning changes location
• Signal sources are plotted
• Navigation commands are used

[bold white]Navigation Features:[/bold white]
• Sector boundaries and relationships
• Signal source triangulation
• Exploration progress tracking
• Coordinate reference system

[bold cyan]🛠️ Panel 4: Decoder & Analysis Toolkit (DAT) - Middle Right[/bold cyan]

[bold white]Purpose:[/bold white]
• Signal decoding workspace
• Analysis result display
• Puzzle and cipher interface

[bold white]What You See:[/bold white]
• Analysis algorithm output
• Decoded signal content
• Puzzle interfaces (when implemented)
• Tool selection indicators

[bold white]Updates When:[/bold white]
• ANALYZE commands are executed
• Signal decoding is performed
• Analysis tools are switched

[bold white]Analysis Types:[/bold white]
• Basic signal decoding
• Pattern matching analysis
• Cryptographic decryption
• Lore fragment extraction
• Coordinate discovery

[bold cyan]📜 Panel 5: Captain's Log & Database (CLD) - Bottom Left[/bold cyan]

[bold white]Purpose:[/bold white]
• Command history tracking
• System status monitoring
• Discovery database management

[bold white]What You See:[/bold white]
• Real-time command feedback
• System status messages
• Discovery notifications
• Error and warning messages
• Exploration progress

[bold white]Updates When:[/bold white]
• Any command is executed
• System events occur
• Discoveries are made
• Errors or warnings arise

[bold white]Information Types:[/bold white]
• Command execution confirmations
• Signal detection notifications
• Analysis results summaries
• System status updates
• Navigation confirmations

[bold cyan]💻 Panel 6: Command Input Interface (CLI) - Bottom Right[/bold cyan]

[bold white]Purpose:[/bold white]
• Primary user input method
• Command execution interface
• Real-time command feedback

[bold white]Visual Design:[/bold white]
• Prominent purple/violet border for visibility
• Clear input prompt
• Command echo and validation
• Execution status indicators

[bold white]Features:[/bold white]
• Command syntax validation
• Real-time typing feedback
• Command history (partially implemented)
• Auto-focus for immediate typing

[bold green]🔄 System Interaction Flow[/bold green]

[bold cyan]Data Flow Between Panels:[/bold cyan]

1. [bold white]Command Input[/bold white] → Sends commands to game controller
2. [bold white]Game Controller[/bold white] → Processes commands and updates data
3. [bold white]Spectrum Analyzer[/bold white] → Updates with new scan results
4. [bold white]Signal Focus[/bold white] → Updates with focused signal data
5. [bold white]Cartography[/bold white] → Updates with position/location data
6. [bold white]Decoder[/bold white] → Updates with analysis results
7. [bold white]Captain's Log[/bold white] → Records all activities and results

[bold cyan]Real-Time Updates:[/bold cyan]
• All panels update simultaneously when relevant commands execute
• Visual feedback occurs immediately upon command entry
• System maintains consistency across all displays
• Status information flows between related panels

[bold green]⚙️ Advanced System Features[/bold green]

[bold cyan]Panel Focus System:[/bold cyan]
• Function keys (F1-F5) highlight specific panels
• Focused panels may show enhanced detail
• Visual indicators show which panel is active
• Focus affects where certain information appears

[bold cyan]Data Persistence:[/bold cyan]
• Command history maintained during session
• Discovery data accumulated over time
• Signal database builds as exploration continues
• System state preserved between commands

[bold cyan]Error Handling:[/bold cyan]
• Invalid commands show helpful error messages
• System state validation prevents impossible actions
• Graceful degradation when features unavailable
• Clear feedback for successful vs. failed operations

[bold green]🎯 Optimization Tips[/bold green]

[bold cyan]Efficient Panel Usage:[/bold cyan]
• Monitor F1 (Spectrum) during scanning operations
• Check F2 (Signal Focus) after FOCUS commands
• Review F4 (Decoder) after ANALYZE commands
• Use F5 (Log) to review recent activity

[bold cyan]Workflow Optimization:[/bold cyan]
• Keep Command Input (F6 equivalent) always accessible
• Use STATUS command to check current system state
• Clear logs periodically with CLEAR command
• Monitor all panels for comprehensive awareness

[bold yellow]═══════════════════════════════════════════════════════════════════════════════[/bold yellow]

[bold green]🔧 Understanding these systems will make you a more effective Signal Cartographer![/bold green]

[dim]Press M for Tutorial Menu | Press H to return to AetherTap | Press Escape for Tutorial Menu[/dim]"""

    def action_back_to_menu(self):
        """Return to tutorial menu"""
        self.app.pop_screen()
    
    def action_back_to_game(self):
        """Return to main game, bypassing menu"""
        self.app.pop_screen()  # Pop this tutorial
        self.app.pop_screen()  # Pop tutorial menu
    
    def action_quit(self):
        """Quit the application"""
        self.app.exit()

class SignalAnalysisTutorial(Screen):
    """Interactive tutorial for signal analysis walkthrough"""
    
    BINDINGS = [
        Binding("escape", "back_to_menu", "Back to Menu"),
        Binding("ctrl+c", "quit", "Quit Game"),
        Binding("h", "back_to_game", "Back to Game"),
        Binding("m", "back_to_menu", "Tutorial Menu"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the signal analysis tutorial"""
        yield Header(show_clock=False)
        with ScrollableContainer():
            yield Static(self._get_content(), id="analysis_tutorial")
        yield Footer()
    
    def _get_content(self) -> str:
        """Get signal analysis tutorial content"""
        return """[bold cyan]🔬 SIGNAL ANALYSIS WALKTHROUGH 🔬[/bold cyan]

[bold yellow]═══════════════════════════════════════════════════════════════════════════════[/bold yellow]

[bold green]🎯 Master the Art of Signal Cartography[/bold green]

This walkthrough provides step-by-step examples and advanced techniques for effective signal analysis. Follow these scenarios to become an expert Signal Cartographer.

[bold green]📋 Scenario 1: Your First Signal Discovery[/bold green]

[bold cyan]Step-by-Step Walkthrough:[/bold cyan]

[bold white]Step 1: Initial Scan[/bold white]
Command: [bold yellow]SCAN[/bold yellow]
Expected Result:
• Spectrum Analyzer (F1) shows frequency spikes
• Log shows "3 signals detected in ALPHA-1"
• Signals labeled as SIG_1, SIG_2, SIG_3
• Each signal has different characteristics

[bold white]Step 2: Focus on First Signal[/bold white]
Command: [bold yellow]FOCUS SIG_1[/bold yellow]
Expected Result:
• Signal Focus panel (F2) updates with SIG_1 details
• Shows frequency (e.g., 125.4 MHz)
• Shows strength (e.g., 0.65)
• Shows stability (e.g., 0.89)
• Log confirms "Focused on SIG_1"

[bold white]Step 3: Analyze the Signal[/bold white]
Command: [bold yellow]ANALYZE[/bold yellow]
Expected Result:
• Decoder panel (F4) shows analysis results
• May reveal decoded text or lore fragment
• Could show signal classification
• Log shows analysis completion

[bold white]Step 4: Review Discovery[/bold white]
Use: [bold yellow]F5[/bold yellow] to check Captain's Log
Review:
• Full command sequence executed
• All results and discoveries
• Any lore or coordinates found

[bold green]📊 Scenario 2: Comparing Signal Types[/bold green]

[bold cyan]Advanced Analysis Technique:[/bold cyan]

[bold white]Compare Multiple Signals in Same Sector:[/bold white]

1. [bold yellow]SCAN ALPHA-1[/bold yellow] - Detect all signals
2. [bold yellow]FOCUS SIG_1[/bold yellow] - Note characteristics
3. [bold yellow]ANALYZE[/bold yellow] - Record results
4. [bold yellow]FOCUS SIG_2[/bold yellow] - Compare characteristics
5. [bold yellow]ANALYZE[/bold yellow] - Compare results
6. [bold yellow]FOCUS SIG_3[/bold yellow] - Complete the set
7. [bold yellow]ANALYZE[/bold yellow] - Full sector analysis

[bold white]What to Look For:[/bold white]
• Signal strength variations (some stronger than others)
• Frequency distribution patterns
• Stability differences (some signals more stable)
• Analysis result types (lore vs. coordinates vs. technical data)

[bold white]Analysis Notes:[/bold white]
• SIG_1 typically: Lower frequency, stable, beginner-friendly
• SIG_2 typically: Mid-frequency, moderate stability, intermediate
• SIG_3 typically: Higher frequency, variable stability, advanced content

[bold green]🗺️ Scenario 3: Cross-Sector Exploration[/bold green]

[bold cyan]Systematic Sector Analysis:[/bold cyan]

[bold white]Phase 1: Alpha Sector Survey[/bold white]
1. [bold yellow]SCAN ALPHA-1[/bold yellow] - 3 signals, beginner level
2. Analyze all signals in sequence
3. Note any coordinate data discovered
4. [bold yellow]SCAN ALPHA-2[/bold yellow] - Different signal types
5. Compare signal characteristics across Alpha sectors

[bold white]Phase 2: Beta Sector Challenge[/bold white]
1. [bold yellow]SCAN BETA-1[/bold yellow] - 2 stronger signals
2. Notice increased signal strength requirements
3. [bold yellow]SCAN BETA-2[/bold yellow] - Advanced signal types
4. Compare complexity with Alpha sectors

[bold white]Phase 3: Gamma Sector Mastery[/bold white]
1. [bold yellow]SCAN GAMMA-1[/bold yellow] - Single powerful signal
2. Attempt analysis of high-complexity signal
3. [bold yellow]SCAN GAMMA-2[/bold yellow] - Expert level
4. [bold yellow]SCAN GAMMA-3[/bold yellow] - Master level challenge

[bold white]Cross-Sector Comparison:[/bold white]
• Alpha: Multiple weak signals, easier analysis
• Beta: Fewer strong signals, moderate complexity
• Gamma: Single powerful signals, maximum complexity

[bold green]🔍 Advanced Analysis Techniques[/bold green]

[bold cyan]Signal Quality Assessment:[/bold cyan]

[bold white]Strength Analysis:[/bold white]
• 0.0-0.3: Weak signals, basic content
• 0.4-0.6: Moderate signals, intermediate content
• 0.7-0.9: Strong signals, advanced content
• 0.9-1.0: Powerful signals, expert content

[bold white]Stability Evaluation:[/bold white]
• 0.9-1.0: Highly stable, easy to analyze
• 0.7-0.8: Moderately stable, some drift
• 0.5-0.6: Unstable, challenging analysis
• Below 0.5: Highly unstable, expert level

[bold white]Frequency Pattern Recognition:[/bold white]
• Low frequencies (100-200 MHz): Often ancient signals
• Mid frequencies (200-350 MHz): Typically active communications
• High frequencies (350-500 MHz): Usually advanced/alien tech

[bold cyan]Strategic Analysis Approaches:[/bold cyan]

[bold white]Breadth-First Strategy:[/bold white]
• Scan multiple sectors quickly
• Focus on strongest signals in each
• Build broad understanding of signal types
• Good for exploration and discovery

[bold white]Depth-First Strategy:[/bold white]
• Focus on one sector completely
• Analyze every signal thoroughly
• Extract all possible information
• Good for completionist playstyle

[bold white]Targeted Strategy:[/bold white]
• Look for specific signal characteristics
• Focus on signals matching search criteria
• Optimize for specific discoveries
• Good for advanced players with goals

[bold green]🎭 Scenario 4: Mystery Signal Investigation[/bold green]

[bold cyan]Detective Work Example:[/bold cyan]

[bold white]The Mystery:[/bold white]
You've detected a signal that appears in multiple sectors with similar characteristics. Investigation required!

[bold white]Investigation Steps:[/bold white]
1. [bold yellow]SCAN ALPHA-1[/bold yellow] - Find the signal
2. [bold yellow]FOCUS[/bold yellow] and [bold yellow]ANALYZE[/bold yellow] - Document characteristics
3. [bold yellow]SCAN BETA-2[/bold yellow] - Look for similar patterns
4. Compare signal signatures and analysis results
5. [bold yellow]SCAN GAMMA-3[/bold yellow] - Check for pattern continuation
6. Piece together the larger mystery

[bold white]Clues to Look For:[/bold white]
• Similar frequency ranges across sectors
• Matching stability patterns
• Related lore content in analysis results
• Coordinate data pointing to common sources
• ASCII signature similarities

[bold green]💡 Pro Tips & Advanced Techniques[/bold green]

[bold cyan]Efficient Workflow:[/bold cyan]
• Use STATUS command to check current state
• Use function keys (F1-F5) to monitor panels during analysis
• Keep notes on interesting signal characteristics
• Use CLEAR command to clean log when it gets cluttered

[bold cyan]Pattern Recognition:[/bold cyan]
• Signals in same sector often related thematically
• Cross-sector signals may be part of larger mysteries
• Signal characteristics can hint at required analysis approach
• Lore fragments often connect across multiple signals

[bold cyan]Troubleshooting:[/bold cyan]
• If FOCUS fails: Ensure you've scanned first
• If ANALYZE gives no results: Try focusing on a different signal
• If signals seem weak: Try different sectors
• If confused: Use STATUS to check current state

[bold green]🏆 Analysis Mastery Challenges[/bold green]

[bold cyan]Beginner Challenge:[/bold cyan]
• Successfully analyze all 3 signals in ALPHA-1
• Understand the different signal types
• Read all lore fragments discovered

[bold cyan]Intermediate Challenge:[/bold cyan]
• Analyze signals across all Alpha and Beta sectors
• Find patterns in signal characteristics
• Piece together related lore fragments

[bold cyan]Advanced Challenge:[/bold cyan]
• Successfully analyze all Gamma sector signals
• Discover connections between different sectors
• Uncover the deeper mysteries behind the signals

[bold cyan]Master Challenge:[/bold cyan]
• Achieve complete analysis of all available signals
• Understand the full scope of the cosmic mystery
• Become a true master Signal Cartographer

[bold yellow]═══════════════════════════════════════════════════════════════════════════════[/bold yellow]

[bold green]🔬 Now you have the knowledge to uncover the deepest mysteries of the void![/bold green]

[dim]Press M for Tutorial Menu | Press H to return to AetherTap | Press Escape for Tutorial Menu[/dim]"""

    def action_back_to_menu(self):
        """Return to tutorial menu"""
        self.app.pop_screen()
    
    def action_back_to_game(self):
        """Return to main game, bypassing menu"""
        self.app.pop_screen()  # Pop this tutorial
        self.app.pop_screen()  # Pop tutorial menu
    
    def action_quit(self):
        """Quit the application"""
        self.app.exit() 