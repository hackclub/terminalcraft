"""
Individual pane managers for the AetherTap interface - PHASE 10 ENHANCED
"""

from typing import List, Optional, Any, Dict, Tuple
from textual.widgets import Static, RichLog
from textual.containers import Container, Vertical, ScrollableContainer
from textual.app import ComposeResult
from rich.text import Text
from rich.console import Console
from textual.reactive import reactive
import random
import math
import time
import asyncio

from .colors import AetherTapColors

# Import performance optimizations
try:
    from ..performance_optimizations import (
        optimize_ascii_rendering, 
        performance_monitor, 
        memory_manager,
        cleanup_old_data,
        error_handler
    )
except ImportError:
    # Fallback if performance optimizations aren't available
    def optimize_ascii_rendering(func):
        return func
    def performance_monitor(func):
        return func
    memory_manager = None
    def cleanup_old_data(*args, **kwargs):
        return 0
    error_handler = None

# Phase 11: Import puzzle system components
try:
    from ..puzzles import PuzzleManager, PuzzleDifficulty
    from ..puzzles.visual_patterns import (
        ConstellationPuzzle, PatternFragmentPuzzle, SymbolRecognitionPuzzle,
        NoiseFilterPuzzle, PatternMatcher
    )
    from ..puzzles.cryptographic import (
        CaesarCipherPuzzle, VigenereCipherPuzzle, SubstitutionPuzzle,
        FrequencyAnalyzer
    )
    from ..puzzles.logic_puzzles import (
        MastermindPuzzle, CircuitCompletionPuzzle, SequenceDeductionPuzzle
    )
    from ..puzzles.audio_patterns import (
        MorseCodePuzzle, RhythmPatternPuzzle, PulseSequencePuzzle
    )
    PUZZLE_SYSTEM_AVAILABLE = True
except ImportError:
    PUZZLE_SYSTEM_AVAILABLE = False

class BasePane(ScrollableContainer):
    """Base class for all AetherTap panes - now scrollable"""
    
    def __init__(self, title: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title
        self.content_lines = []
        self.content_widget = None
        self.can_focus = True
        self.auto_scroll = False  # Disable auto-scroll for base panes - let users scroll manually
        initial_content = f"[bold cyan]{self.title}[/bold cyan]\n[dim]Initializing...[/dim]"
    
    def compose(self) -> ComposeResult:
        """Compose the scrollable pane"""
        self.content_widget = Static("", id=f"{self.id}_content")
        yield self.content_widget
    
    async def on_mount(self) -> None:
        """Initialize the pane after mounting"""
        if not self.content_widget:
            try:
                self.content_widget = self.query_one(f"#{self.id}_content")
            except:
                pass
        self._update_display()
    
    def add_content_line(self, line: str):
        """Add a line to the pane content"""
        self.content_lines.append(line)
        self._update_display()
    
    def clear_content(self):
        """Clear the pane content"""
        self.content_lines = []
        self._update_display()
    
    def set_content(self, lines: list):
        """Set the entire content"""
        self.content_lines = lines[:]
        self._update_display()
    
    def _update_display(self):
        """Update the display with current content"""
        try:
            if not self.content_widget:
                return
        except:
            return
        
        if self.content_widget:
            # Build content with proper line breaks for scrolling - MINIMAL PADDING
            content_lines = [f"[bold cyan]{self.title}[/bold cyan]"]
            
            if self.content_lines:
                content_lines.extend(self.content_lines)
            else:
                content_lines.append("[dim]No data[/dim]")
            
            # NO extra padding - join directly
            full_content = "\n".join(content_lines)
            self.content_widget.update(full_content)
            
            # No auto-scroll for base panes - users can scroll manually
    
    def _scroll_to_bottom(self):
        """Scroll to the bottom of the content"""
        try:
            # Get the maximum scroll position and scroll there
            self.scroll_end(animate=False)
        except:
            pass  # Ignore errors if scrolling isn't ready yet
    
    def update_content(self, lines: List[str]):
        """Update the content of this pane"""
        self.set_content(lines)

class SpectrumPane(BasePane):
    """Enhanced Main Spectrum Analyzer pane [MSA] - Phase 10.1"""
    
    def __init__(self, **kwargs):
        super().__init__("Main Spectrum Analyzer [MSA]", **kwargs)
        self.signals = []
        self.frequency_range = (100, 200)
        self.noise_level = 0.1
        self.animation_frame = 0
        self.signal_animations = {}
        self.noise_pattern = []
        self.last_update = time.time()
        
        # Generate persistent noise background
        self._generate_noise_background()
    
    def _generate_noise_background(self):
        """Generate persistent noise background pattern"""
        width = 64
        self.noise_pattern = []
        for i in range(width):
            # Create realistic noise using multiple frequency components
            noise_val = 0
            noise_val += 0.3 * math.sin(i * 0.1) * random.uniform(0.7, 1.3)
            noise_val += 0.2 * math.sin(i * 0.05) * random.uniform(0.8, 1.2)
            noise_val += 0.1 * random.uniform(-1, 1)
            noise_val = max(0, min(1, 0.1 + noise_val * 0.1))  # Keep noise level reasonable
            self.noise_pattern.append(noise_val)
        
    def update_spectrum(self, signals: List[Any], freq_range: tuple, noise: float = 0.1):
        """Update the spectrum display with enhanced visualization and animation"""
        self.signals = signals
        self.frequency_range = freq_range
        self.noise_level = noise
        
        # Initialize signal animations for new signals
        for signal in signals:
            if hasattr(signal, 'id') and signal.id not in self.signal_animations:
                self.signal_animations[signal.id] = {
                    'phase': random.random() * 2 * math.pi,
                    'pulse_rate': random.uniform(0.05, 0.15),
                    'drift_rate': random.uniform(-0.02, 0.02),
                    'stability_variance': getattr(signal, 'stability', 1.0)
                }
        
        # Generate enhanced spectrum display
        spectrum_lines = self._generate_enhanced_spectrum()
        self.update_content(spectrum_lines)
    
        # Increment animation frame
        self.animation_frame += 1
        self.last_update = time.time()
    
    def _generate_enhanced_spectrum(self) -> List[str]:
        """Generate enhanced ASCII art spectrum with animations and noise"""
        # Performance optimization: Limit update frequency to 20 FPS
        current_time = time.time()
        if hasattr(self, '_last_render_time') and current_time - self._last_render_time < 0.05:
            if hasattr(self, '_cached_spectrum'):
                return self._cached_spectrum
        
        lines = []
        width = 64
        height = 12
        
        if not self.signals:
            result = self._generate_no_signal_display(width)
            self._cached_spectrum = result
            self._last_render_time = current_time
            return result
        
        try:
            # Enhanced header with comprehensive information
            lines.append(f"[bold yellow]Frequency Range:[/bold yellow] {self.frequency_range[0]:.1f}-{self.frequency_range[1]:.1f} MHz")
            lines.append(f"[dim]Noise Floor:[/dim] {self.noise_level:.3f} | [dim]Sensitivity:[/dim] High | [dim]Bandwidth:[/dim] {self.frequency_range[1]-self.frequency_range[0]:.1f} MHz")
            lines.append("[cyan]" + "█" * width + "[/cyan]")
            
            # Generate spectrum visualization with enhanced graphics
            spectrum_data = self._calculate_spectrum_data(width, height)
            
            for row in range(height):
                line = ""
                row_intensity = (height - row) / height  # Higher rows = higher intensity
                
                for col in range(width):
                    intensity = spectrum_data[col]
                    char, color = self._get_spectrum_char(intensity, row_intensity)
                    if color:
                        line += f"[{color}]{char}[/{color}]"
                    else:
                        line += char
                
                lines.append(line)
            
            # Enhanced footer with signal information
            lines.append("[cyan]" + "█" * width + "[/cyan]")
            lines.append(f"[bold green]Active Signals:[/bold green] {len(self.signals)}")
            
            # Signal details bar
            signal_info = []
            for i, signal in enumerate(self.signals[:3]):  # Show first 3 signals
                signal_id = getattr(signal, 'id', f'SIG_{i+1}')
                freq = getattr(signal, 'frequency', 0)
                strength = getattr(signal, 'strength', 0)
                signal_info.append(f"[yellow]{signal_id}[/yellow]:{freq:.1f}MHz([white]{strength:.2f}[/white])")
            
            if signal_info:
                lines.append(" | ".join(signal_info))
            
            # Real-time status indicators
            lines.append(f"[dim]Frame:[/dim] {self.animation_frame} | [dim]Last Update:[/dim] {time.time() - self.last_update:.1f}s ago")
            
            # Cache the result for performance
            self._cached_spectrum = lines
            self._last_render_time = current_time
            
            return lines
            
        except Exception as e:
            # Graceful error handling
            error_lines = [
                f"[red]Spectrum rendering error:[/red] {str(e)}",
                "[yellow]Falling back to simplified display...[/yellow]",
                f"[dim]Signals detected:[/dim] {len(self.signals)}",
                "[dim]Use SCAN command to refresh[/dim]"
            ]
            self._cached_spectrum = error_lines
            return error_lines
    
    def _calculate_spectrum_data(self, width: int, height: int) -> List[float]:
        """Calculate spectrum intensity data for enhanced visualization with animation"""
        spectrum_data = []
        freq_step = (self.frequency_range[1] - self.frequency_range[0]) / width
        
        for col in range(width):
            freq = self.frequency_range[0] + col * freq_step
            intensity = self.noise_pattern[col % len(self.noise_pattern)]
            
            # Add signal contributions with enhanced animation
            for signal in self.signals:
                if hasattr(signal, 'frequency'):
                    signal_freq = signal.frequency
                    signal_strength = getattr(signal, 'strength', 0.5)
                    signal_id = getattr(signal, 'id', 'unknown')
                    
                    # Calculate distance from signal frequency
                    freq_distance = abs(freq - signal_freq)
                    if freq_distance < 5:  # Signal influence range
                        # Get animation parameters
                        anim = self.signal_animations.get(signal_id, {})
                        phase = anim.get('phase', 0)
                        pulse_rate = anim.get('pulse_rate', 0.1)
                        drift_rate = anim.get('drift_rate', 0)
                        stability = anim.get('stability_variance', 1.0)
                        
                        # Calculate animated signal strength with pulsing
                        time_factor = self.animation_frame * pulse_rate
                        pulse_modifier = 0.8 + 0.2 * math.sin(phase + time_factor)
                        
                        # Apply stability variance
                        stability_modifier = 1.0 + (1.0 - stability) * 0.3 * math.sin(time_factor * 0.7)
                        
                        # Calculate signal contribution with Gaussian falloff
                        signal_contribution = signal_strength * pulse_modifier * stability_modifier
                        signal_contribution *= math.exp(-0.5 * (freq_distance / 2.0) ** 2)
                        
                        intensity += signal_contribution
                        
                        # Update animation phase for next frame
                        anim['phase'] = phase + drift_rate
            
            spectrum_data.append(min(1.0, max(0.0, intensity)))
        
        return spectrum_data
    
    def _get_spectrum_char(self, intensity: float, row_intensity: float) -> Tuple[str, Optional[str]]:
        """Convert intensity to appropriate character and color with enhanced visualization"""
        # Determine if this row should show the signal based on intensity
        show_signal = intensity >= row_intensity
        
        if not show_signal:
            return "·", "dim"
        
        # Enhanced character selection based on signal strength with color coding
        if intensity > 0.9:
            return "█", "bright_red"
        elif intensity > 0.8:
            return "█", "red"
        elif intensity > 0.7:
            return "▓", "bright_yellow"
        elif intensity > 0.6:
            return "▓", "yellow"
        elif intensity > 0.5:
            return "▒", "bright_green"
        elif intensity > 0.4:
            return "▒", "green"
        elif intensity > 0.3:
            return "░", "bright_cyan"
        elif intensity > 0.2:
            return "░", "cyan"
        else:
            return "·", "blue"
    
    def _generate_no_signal_display(self, width: int) -> List[str]:
        """Generate enhanced display when no signals are detected"""
        lines = []
        lines.append(f"[bold yellow]Frequency Range:[/bold yellow] {self.frequency_range[0]:.1f}-{self.frequency_range[1]:.1f} MHz")
        lines.append(f"[dim]Noise Floor:[/dim] {self.noise_level:.3f} | [dim]Status:[/dim] Scanning... | [dim]Sensitivity:[/dim] Maximum")
        lines.append("[cyan]" + "█" * width + "[/cyan]")
        lines.append("")
        
        # Show animated scanning pattern
        scan_pos = (self.animation_frame // 2) % width
        scan_line = "·" * scan_pos + "▓▒░" + "·" * (width - scan_pos - 3)
        if scan_pos > width - 3:
            scan_line = "·" * width
        lines.append(f"[yellow]{scan_line}[/yellow]")
        
        for _ in range(6):
            # Show enhanced noise floor with subtle animation
            noise_line = ""
            for i in range(width):
                if random.random() < 0.05:
                    noise_line += random.choice(["·", "░"])
                else:
                    noise_line += "·"
            lines.append(f"[dim]{noise_line}[/dim]")
        
        lines.append("")
        lines.append("[cyan]" + "█" * width + "[/cyan]")
        lines.append("[bold red]No signals detected[/bold red]")
        lines.append("")
        lines.append("[yellow]>>> Run 'SCAN' command to detect signals <<<[/yellow]")
        lines.append("")
        lines.append("[green]Available sectors:[/green]")
        lines.append("  [cyan]ALPHA-1[/cyan] - Training sector (3 weak signals)")
        lines.append("  [cyan]BETA-2[/cyan] - Standard sector (2 medium signals)")
        lines.append("  [cyan]GAMMA-3[/cyan] - Deep space sector (1 strong signal)")
        lines.append("  [cyan]DELTA-4[/cyan] - Anomaly field (2 advanced signals) 🆕")
        lines.append("  [cyan]EPSILON-5[/cyan] - Singularity core (1 expert signal) 🆕")
        lines.append("")
        lines.append("[dim]Example:[/dim] Type 'SCAN BETA-2' to scan a different sector")
        lines.append(f"[dim]Animation Frame:[/dim] {self.animation_frame} | [dim]Noise Samples:[/dim] {len(self.noise_pattern)}")
        
        return lines

class SignalFocusPane(BasePane):
    """Enhanced Signal Focus & Data pane [SFD] - Phase 10.2"""
    
    def __init__(self, **kwargs):
        super().__init__("Signal Focus & Data [SFD]", **kwargs)
        self.focused_signal = None
        self.signal_history = []
        self.analysis_frame = 0
        self.last_analysis_time = time.time()
        
        # Signal classification systems (updated for content expansion)
        self.modulation_types = {
            'AM': {'name': 'Amplitude Modulation', 'complexity': 1},
            'FM': {'name': 'Frequency Modulation', 'complexity': 2}, 
            'PSK': {'name': 'Phase Shift Keying', 'complexity': 3},
            'QAM': {'name': 'Quadrature Amplitude', 'complexity': 4},
            'Pulsed': {'name': 'Pulse Modulated', 'complexity': 2},
            'Pulsed-Echo': {'name': 'Echo Pulse System', 'complexity': 2},
            'Phase-Shifted': {'name': 'Phase Shifted Signal', 'complexity': 3},
            'Bio-Resonant': {'name': 'Biological Resonance', 'complexity': 4},
            'Fragmented-Stream': {'name': 'Fragmented Data Stream', 'complexity': 3},
            'Quantum-Entangled': {'name': 'Quantum Entangled Signal', 'complexity': 5},
            'Whisper-Code': {'name': 'Whisper Code Protocol', 'complexity': 4},
            'Bio-Neural': {'name': 'Bio-Neural Patterns', 'complexity': 6},
            'Quantum-Echo': {'name': 'Quantum Echo Resonance', 'complexity': 7},
            'Singularity-Resonance': {'name': 'Singularity Resonance', 'complexity': 9},
            'Unknown': {'name': 'Unclassified Pattern', 'complexity': 1}
        }
        
        self.band_classifications = {
            'Low-Band': (50, 120),
            'Mid-Band': (120, 180), 
            'High-Band': (180, 250)
        }
    
    def focus_signal(self, signal: Any):
        """Enhanced signal focusing with comprehensive analysis"""
        self.focused_signal = signal
        self.analysis_frame += 1
        self.last_analysis_time = time.time()
        
        if signal:
            # Add to signal history for tracking
            if hasattr(signal, 'id'):
                signal_entry = {
                    'id': signal.id,
                    'timestamp': time.time(),
                    'frequency': getattr(signal, 'frequency', 0),
                    'strength': getattr(signal, 'strength', 0)
                }
                self.signal_history.append(signal_entry)
                
                # Keep only last 10 entries
                if len(self.signal_history) > 10:
                    self.signal_history = self.signal_history[-10:]
            
            self._display_enhanced_signal_details()
        else:
            self._display_focus_placeholder()
    
    def _display_focus_placeholder(self):
        """Enhanced placeholder display with focusing instructions"""
        placeholder_lines = [
            "[bold yellow]🎯 Signal Focus & Analysis System[/bold yellow]",
            "",
            "[dim]Status:[/dim] No signal focused",
            "[dim]Analysis Frame:[/dim] " + str(self.analysis_frame),
            "[dim]Signal History:[/dim] " + str(len(self.signal_history)) + " entries",
            "",
            "[cyan]═══ HOW TO FOCUS SIGNALS ═══[/cyan]",
            "",
            "[green]Step 1:[/green] Run '[yellow]SCAN[/yellow]' to detect signals",
            "[green]Step 2:[/green] Use '[yellow]FOCUS SIG_1[/yellow]' to focus on signal",
            "[green]Step 3:[/green] Signal analysis will appear here",
            "[green]Step 4:[/green] Use '[yellow]ANALYZE[/yellow]' for deep analysis",
            "",
            "[cyan]Available Focus Commands:[/cyan]",
            "• [yellow]FOCUS SIG_1[/yellow] - Focus first detected signal",
            "• [yellow]FOCUS SIG_2[/yellow] - Focus second detected signal", 
            "• [yellow]FOCUS SIG_3[/yellow] - Focus third detected signal",
            "• [yellow]ANALYZE[/yellow] - Analyze currently focused signal",
            "",
            "[cyan]Analysis Capabilities:[/cyan]",
            "• Signal strength & stability monitoring",
            "• Modulation type classification",
            "• ASCII signal signature generation",
            "• Frequency precision analysis",
            "• Origin coordinate estimation",
            "• Quality assessment & recommendations"
        ]
        self.update_content(placeholder_lines)
    
    def _display_enhanced_signal_details(self):
        """Display comprehensive signal analysis with visual indicators"""
        if not self.focused_signal:
            return
            
        lines = []
        signal = self.focused_signal
        
        # Header with signal identification
        lines.append(f"[bold cyan]🎯 SIGNAL ANALYSIS: {getattr(signal, 'id', 'UNKNOWN')}[/bold cyan]")
        lines.append("═" * 60)
        
        # Core signal properties with enhanced display
        frequency = getattr(signal, 'frequency', 0)
        strength = getattr(signal, 'strength', 0)
        stability = getattr(signal, 'stability', 1.0)
        modulation = getattr(signal, 'modulation', 'Unknown')
        
        lines.append(f"[yellow]Frequency:[/yellow] {frequency:.3f} MHz")
        lines.append(f"[yellow]Strength:[/yellow] {strength:.3f} ({self._get_strength_description(strength)})")
        lines.append(f"[yellow]Stability:[/yellow] {stability:.3f} ({self._get_stability_description(stability)})")
        lines.append(f"[yellow]Modulation:[/yellow] {modulation} - {self.modulation_types.get(modulation, {'name': 'Unknown'})['name']}")
        
        # Visual strength and stability indicators
        lines.append("")
        lines.append("[cyan]═══ SIGNAL METRICS ═══[/cyan]")
        lines.append(f"[green]Strength:[/green] {self._create_progress_bar(strength, 50, '█', '░')}")
        lines.append(f"[blue]Stability:[/blue] {self._create_progress_bar(stability, 50, '█', '░')}")
        
        # Signal classification system
        lines.append("")
        lines.append("[cyan]═══ CLASSIFICATION ═══[/cyan]")
        band_class = self._classify_frequency_band(frequency)
        power_level = self._classify_power_level(strength)
        complexity = self.modulation_types.get(modulation, {'complexity': 1})['complexity']
        
        lines.append(f"[yellow]Band Class:[/yellow] {band_class}")
        lines.append(f"[yellow]Power Level:[/yellow] {power_level}")
        lines.append(f"[yellow]Complexity:[/yellow] {'●' * complexity}{'○' * (5-complexity)} ({complexity}/9)")
        
        # Enhanced ASCII signal signature based on modulation type
        lines.append("")
        lines.append("[cyan]═══ SIGNAL SIGNATURE ═══[/cyan]")
        signature = self._generate_enhanced_signature(signal)
        lines.extend(signature)
        
        # Signal quality assessment and analysis recommendations
        lines.append("")
        lines.append("[cyan]═══ ANALYSIS ASSESSMENT ═══[/cyan]")
        quality_score = self._calculate_quality_score(signal)
        lines.append(f"[green]Overall Quality:[/green] {quality_score:.1f}/10.0")
        lines.append(f"[green]Assessment:[/green] {self._get_quality_assessment(quality_score)}")
        
        # Analysis recommendations
        recommendations = self._generate_recommendations(signal)
        if recommendations:
            lines.append("")
            lines.append("[yellow]📋 Recommendations:[/yellow]")
            lines.extend([f"  • {rec}" for rec in recommendations])
        
        # Signal origin and coordinate estimation
        lines.append("")
        lines.append("[cyan]═══ ORIGIN ANALYSIS ═══[/cyan]")
        origin_data = self._analyze_signal_origin(signal)
        lines.extend(origin_data)
        
        # Technical details and precision metrics
        lines.append("")
        lines.append("[cyan]═══ TECHNICAL DETAILS ═══[/cyan]")
        lines.append(f"[dim]Analysis Frame:[/dim] {self.analysis_frame}")
        lines.append(f"[dim]Focus Time:[/dim] {time.time() - self.last_analysis_time:.1f}s ago")
        lines.append(f"[dim]Signal History:[/dim] {len(self.signal_history)} entries")
        lines.append(f"[dim]Frequency Precision:[/dim] ±{self._calculate_frequency_precision(signal):.4f} MHz")
        
        self.update_content(lines)
    
    def _get_strength_description(self, strength: float) -> str:
        """Get descriptive text for signal strength"""
        if strength >= 0.9: return "Extremely Strong"
        elif strength >= 0.7: return "Strong"
        elif strength >= 0.5: return "Moderate" 
        elif strength >= 0.3: return "Weak"
        else: return "Very Weak"
    
    def _get_stability_description(self, stability: float) -> str:
        """Get descriptive text for signal stability"""
        if stability >= 0.95: return "Rock Solid"
        elif stability >= 0.85: return "Very Stable"
        elif stability >= 0.70: return "Stable"
        elif stability >= 0.50: return "Fluctuating"
        else: return "Highly Unstable"
    
    def _create_progress_bar(self, value: float, width: int, fill_char: str, empty_char: str) -> str:
        """Create a visual progress bar"""
        filled = int(value * width)
        empty = width - filled
        bar = fill_char * filled + empty_char * empty
        percentage = value * 100
        return f"│{bar}│ {percentage:.1f}%"
    
    def _classify_frequency_band(self, frequency: float) -> str:
        """Classify frequency into band categories"""
        for band, (low, high) in self.band_classifications.items():
            if low <= frequency <= high:
                return band
        return "Extended-Band"
    
    def _classify_power_level(self, strength: float) -> str:
        """Classify signal power level"""
        if strength >= 0.8: return "High Power"
        elif strength >= 0.5: return "Medium Power"
        elif strength >= 0.2: return "Low Power"
        else: return "Minimal Power"
    
    def _generate_enhanced_signature(self, signal: Any) -> List[str]:
        """Generate enhanced ASCII signal signatures based on modulation type"""
        modulation = getattr(signal, 'modulation', 'Unknown')
        strength = getattr(signal, 'strength', 0.5)
        
        signatures = {
            'AM': [
                "     ▁▂▄█▄▂▁     ▁▂▄█▄▂▁     ",
                "   ▁▂█████▂▁   ▁▂█████▂▁   ",
                " ▁▂███████▂▁ ▁▂███████▂▁ ",
                "▂██████████▂██████████▂",
                "Amplitude Modulated Carrier"
            ],
            'FM': [
                "▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂▃▄▅▆▇█▇▆▅▄▃▂▁",
                "▂▄▆█▆▄▂▁▂▄▆█▆▄▂▁▂▄▆█▆▄▂▁▂▄▆█",
                "█▆▄▂▁▂▄▆█▆▄▂▁▂▄▆█▆▄▂▁▂▄▆█▆▄▂",
                "Frequency Modulated Signal"
            ],
            'PSK': [
                "██▁▁██▁▁████▁▁██▁▁████▁▁██▁▁",
                "██  ██  ████  ██  ████  ██  ",
                "▀▀▄▄▀▀▄▄▀▀▀▀▄▄▀▀▄▄▀▀▀▀▄▄▀▀▄▄",
                "Phase Shift Keyed Data"
            ],
            'Pulsed': [
                "█ █ █   █ █   █ █ █   █ █   ",
                "█ █ █   █ █   █ █ █   █ █   ",
                "▀ ▀ ▀   ▀ ▀   ▀ ▀ ▀   ▀ ▀   ",
                "Pulsed Transmission Pattern"
            ],
            'Pulsed-Echo': [
                "█ ▄ ▁   █ ▄ ▁   █ ▄ ▁   █ ▄ ▁",
                "█ ▄ ▁   █ ▄ ▁   █ ▄ ▁   █ ▄ ▁",
                "▀ ▀ ▀   ▀ ▀ ▀   ▀ ▀ ▀   ▀ ▀ ▀",
                "Pulse-Echo Response System"
            ]
        }
        
        default_signature = [
            "▓▒░█▓▒░█▓▒░█▓▒░█▓▒░█▓▒░█▓▒░",
            "░▒▓█░▒▓█░▒▓█░▒▓█░▒▓█░▒▓█░▒▓",
            "▒▓█░▒▓█░▒▓█░▒▓█░▒▓█░▒▓█░▒▓█",
            "Unclassified Signal Pattern"
        ]
        
        signature = signatures.get(modulation, default_signature)
        
        # Add strength-based visual enhancement
        if strength > 0.8:
            signature = [f"[bright_red]{line}[/bright_red]" for line in signature[:-1]] + [signature[-1]]
        elif strength > 0.6:
            signature = [f"[yellow]{line}[/yellow]" for line in signature[:-1]] + [signature[-1]]
        elif strength > 0.4:
            signature = [f"[green]{line}[/green]" for line in signature[:-1]] + [signature[-1]]
        else:
            signature = [f"[dim]{line}[/dim]" for line in signature[:-1]] + [signature[-1]]
        
        # Add border
        border_line = "─" * 32
        return [border_line] + signature + [border_line]
    
    def _calculate_quality_score(self, signal: Any) -> float:
        """Calculate overall signal quality score"""
        strength = getattr(signal, 'strength', 0)
        stability = getattr(signal, 'stability', 1.0)
        modulation = getattr(signal, 'modulation', 'Unknown')
        
        # Base score from strength and stability
        score = (strength * 4) + (stability * 4)
        
        # Modulation complexity bonus
        complexity = self.modulation_types.get(modulation, {'complexity': 1})['complexity']
        score += (complexity / 5) * 2
        
        return min(10.0, score)
    
    def _get_quality_assessment(self, score: float) -> str:
        """Get quality assessment text"""
        if score >= 9.0: return "Exceptional - Ideal for analysis"
        elif score >= 7.5: return "Excellent - High confidence results"
        elif score >= 6.0: return "Good - Reliable analysis possible"
        elif score >= 4.5: return "Fair - Some analysis limitations"
        elif score >= 3.0: return "Poor - Enhanced filtering recommended"
        else: return "Critical - Signal enhancement required"
    
    def _generate_recommendations(self, signal: Any) -> List[str]:
        """Generate analysis recommendations based on signal properties"""
        recommendations = []
        strength = getattr(signal, 'strength', 0)
        stability = getattr(signal, 'stability', 1.0)
        modulation = getattr(signal, 'modulation', 'Unknown')
        
        if strength < 0.3:
            recommendations.append("Apply signal amplification filters")
            recommendations.append("Consider closer approach to source")
        
        if stability < 0.7:
            recommendations.append("Use stability enhancement protocols")
            recommendations.append("Multiple sampling recommended")
        
        if modulation == 'Unknown':
            recommendations.append("Run extended modulation analysis")
            recommendations.append("Check for non-standard encoding")
        
        complexity = self.modulation_types.get(modulation, {'complexity': 1})['complexity']
        if complexity >= 4:
            recommendations.append("Advanced decoding tools required")
            recommendations.append("Prepare for multi-stage analysis")
        
        if not recommendations:
            recommendations.append("Signal ready for standard analysis")
            recommendations.append("All parameters within normal range")
        
        return recommendations
    
    def _analyze_signal_origin(self, signal: Any) -> List[str]:
        """Analyze and estimate signal origin coordinates"""
        origin_lines = []
        
        # Mock coordinate analysis (in real implementation, this would use triangulation)
        frequency = getattr(signal, 'frequency', 0)
        strength = getattr(signal, 'strength', 0)
        
        # Estimate coordinates based on signal properties
        estimated_x = (frequency - 100) * 2.5
        estimated_y = strength * 100
        estimated_z = random.uniform(-50, 50)  # Mock Z coordinate
        
        origin_lines.append(f"[yellow]Estimated Coordinates:[/yellow]")
        origin_lines.append(f"  X: {estimated_x:.2f} units")
        origin_lines.append(f"  Y: {estimated_y:.2f} units") 
        origin_lines.append(f"  Z: {estimated_z:.2f} units")
        
        # Distance estimation
        distance = math.sqrt(estimated_x**2 + estimated_y**2 + estimated_z**2)
        origin_lines.append(f"[yellow]Distance:[/yellow] {distance:.1f} units")
        
        # Confidence assessment
        confidence = min(100, strength * 80 + 20)
        origin_lines.append(f"[yellow]Confidence:[/yellow] {confidence:.1f}%")
        
        # Direction indicator
        if estimated_x > 0:
            direction = "Starboard" 
        else:
            direction = "Port"
        origin_lines.append(f"[yellow]Direction:[/yellow] {direction} sector")
        
        return origin_lines
    
    def _calculate_frequency_precision(self, signal: Any) -> float:
        """Calculate frequency measurement precision"""
        strength = getattr(signal, 'strength', 0)
        stability = getattr(signal, 'stability', 1.0)
        
        # Higher strength and stability = better precision
        base_precision = 0.1
        precision = base_precision / (strength * stability + 0.1)
        return min(1.0, precision)

class CartographyPane(BasePane):
    """Enhanced Cartography & Navigation pane [CNP] - Phase 10.3"""
    
    def __init__(self, **kwargs):
        super().__init__("Cartography & Navigation [CNP]", **kwargs)
        self.current_sector = "ALPHA-1"
        self.known_locations = {}
        self.zoom_level = 1
        self.map_center_x = 0
        self.map_center_y = 0
        self.signal_sources = []
        self.anomalies = []
        self.exploration_data = {
            'sectors_discovered': ['ALPHA-1'],
            'total_sectors': 7,
            'signals_mapped': 0,
            'anomalies_found': 0,
            'exploration_percentage': 14.3
        }
        
        # Sector definitions with coordinates and difficulty
        self.sector_map = {
            'ALPHA-1': {'coords': (0, 0, 0), 'difficulty': 'Trainig', 'signals': 3, 'status': 'explored'},
            'BETA-2': {'coords': (50, 30, 10), 'difficulty': 'Standard', 'signals': 2, 'status': 'partially_explored'},
            'GAMMA-3': {'coords': (-30, 60, -20), 'difficulty': 'Deep Space', 'signals': 1, 'status': 'unexplored'},
            'DELTA-4': {'coords': (80, -40, 50), 'difficulty': 'High Risk', 'signals': 4, 'status': 'unexplored'},
            'EPSILON-5': {'coords': (-60, -30, 30), 'difficulty': 'Ancient', 'signals': 2, 'status': 'unexplored'},
            'ZETA-6': {'coords': (20, 90, -60), 'difficulty': 'Quantum', 'signals': 1, 'status': 'unexplored'},
            'ETA-7': {'coords': (0, 0, 100), 'difficulty': 'Void', 'signals': 5, 'status': 'unexplored'}
        }
        
        # Map marker types
        self.marker_types = {
            'signal': {'char': '📡', 'color': 'yellow'},
            'anomaly': {'char': '🌟', 'color': 'red'},
            'station': {'char': '🛰️', 'color': 'cyan'},
            'beacon': {'char': '🏮', 'color': 'green'},
            'hazard': {'char': '⚠️', 'color': 'bright_red'},
            'unknown': {'char': '❓', 'color': 'dim'}
        }
    
    def update_map(self, sector: str, locations: Dict[str, Any] = None, signals: List[Any] = None):
        """Enhanced map update with signal plotting and exploration tracking"""
        if sector in self.sector_map:
            self.current_sector = sector
            
            # Update exploration data
            if sector not in self.exploration_data['sectors_discovered']:
                self.exploration_data['sectors_discovered'].append(sector)
                self.exploration_data['exploration_percentage'] = (
                    len(self.exploration_data['sectors_discovered']) / 
                    self.exploration_data['total_sectors'] * 100
                )
            
            # Mark sector as at least partially explored
            if self.sector_map[sector]['status'] == 'unexplored':
                self.sector_map[sector]['status'] = 'partially_explored'
        
        if locations:
            self.known_locations.update(locations)
        
        if signals:
            self._update_signal_sources(signals)
        
        self._generate_enhanced_map_display()
    
    def _update_signal_sources(self, signals: List[Any]):
        """Update signal source plotting on the map"""
        self.signal_sources = []
        for signal in signals:
            if hasattr(signal, 'frequency') and hasattr(signal, 'strength'):
                # Convert signal properties to map coordinates
                freq = signal.frequency
                strength = signal.strength
                signal_id = getattr(signal, 'id', 'Unknown')
                
                # Mock coordinate calculation based on signal properties
                x = (freq - 150) * 0.5
                y = strength * 40
                z = random.uniform(-10, 10)
                
                signal_source = {
                    'id': signal_id,
                    'coords': (x, y, z),
                    'frequency': freq,
                    'strength': strength,
                    'marker_type': 'signal'
                }
                self.signal_sources.append(signal_source)
        
        self.exploration_data['signals_mapped'] = len(self.signal_sources)
    
    def zoom_in(self):
        """Increase zoom level for detailed view"""
        if self.zoom_level < 5:
            self.zoom_level += 1
            self._generate_enhanced_map_display()
    
    def zoom_out(self):
        """Decrease zoom level for wider view"""
        if self.zoom_level > 1:
            self.zoom_level -= 1
            self._generate_enhanced_map_display()
    
    def pan_map(self, dx: int, dy: int):
        """Pan the map view"""
        self.map_center_x += dx
        self.map_center_y += dy
        self._generate_enhanced_map_display()
    
    def _generate_enhanced_map_display(self):
        """Generate comprehensive ASCII star map with all enhanced features"""
        lines = []
        map_width = 60
        map_height = 20
        
        # Enhanced header with navigation information
        lines.append(f"[bold cyan]🗺️ STELLAR CARTOGRAPHY & NAVIGATION[/bold cyan]")
        lines.append("═" * 60)
        
        # Current position and navigation data
        current_coords = self.sector_map.get(self.current_sector, {'coords': (0, 0, 0)})['coords']
        lines.append(f"[yellow]Current Sector:[/yellow] {self.current_sector} | [yellow]Coordinates:[/yellow] {current_coords[0]:+.1f}, {current_coords[1]:+.1f}, {current_coords[2]:+.1f}")
        lines.append(f"[yellow]Zoom Level:[/yellow] {self.zoom_level}x | [yellow]View Center:[/yellow] ({self.map_center_x:+d}, {self.map_center_y:+d})")
        
        # Exploration progress
        exploration_pct = self.exploration_data['exploration_percentage']
        progress_bar = self._create_exploration_progress_bar(exploration_pct, 30)
        lines.append(f"[green]Exploration:[/green] {progress_bar} {exploration_pct:.1f}%")
        
        lines.append("─" * 60)
        
        # Generate star map grid
        star_map = self._generate_star_map_grid(map_width, map_height)
        
        # Add coordinate grid markers
        lines.append(self._generate_coordinate_header(map_width))
        
        for row_idx, row in enumerate(star_map):
            # Add Y coordinate marker every 5 rows
            if row_idx % 5 == 0:
                y_coord = (map_height // 2 - row_idx) * self.zoom_level + self.map_center_y
                row_line = f"{y_coord:+3d}│{row}│"
            else:
                row_line = f"   │{row}│"
            lines.append(row_line)
        
        lines.append("─" * (map_width + 8))
        
        # Map legend with all marker types
        lines.append(self._generate_map_legend())
        
        # Sector information panel
        lines.append("")
        lines.append("[cyan]═══ SECTOR DATABASE ═══[/cyan]")
        lines.extend(self._generate_sector_info())
        
        # Signal source tracking
        if self.signal_sources:
            lines.append("")
            lines.append("[cyan]═══ SIGNAL SOURCES ═══[/cyan]")
            lines.extend(self._generate_signal_tracking_info())
        
        # Navigation commands
        lines.append("")
        lines.append("[cyan]═══ NAVIGATION CONTROLS ═══[/cyan]")
        lines.append("[yellow]Zoom:[/yellow] + (zoom in) | - (zoom out)")
        lines.append("[yellow]Pan:[/yellow] ↑↓←→ (move view) | HOME (center)")
        lines.append("[yellow]Sectors:[/yellow] SCAN <sector> to explore")
        
        self.update_content(lines)
    
    def _generate_star_map_grid(self, width: int, height: int) -> List[str]:
        """Generate the main ASCII star map with markers and features"""
        star_map = []
        
        for row in range(height):
            line = ""
            for col in range(width):
                # Calculate actual coordinates for this position
                actual_x = (col - width // 2) * self.zoom_level + self.map_center_x
                actual_y = (height // 2 - row) * self.zoom_level + self.map_center_y
                
                char = self._get_map_character(actual_x, actual_y, col, row)
                line += char
            
            star_map.append(line)
        
        return star_map
    
    def _get_map_character(self, x: float, y: float, col: int, row: int) -> str:
        """Determine the character to display at this map position"""
        # Check for current sector marker
        current_coords = self.sector_map.get(self.current_sector, {'coords': (0, 0, 0)})['coords']
        if abs(x - current_coords[0]) < 2 and abs(y - current_coords[1]) < 2:
            return "[bright_green]⦿[/bright_green]"  # Current position
        
        # Check for other sector markers
        for sector, data in self.sector_map.items():
            sector_x, sector_y, _ = data['coords']
            if abs(x - sector_x) < 3 and abs(y - sector_y) < 3:
                if data['status'] == 'explored':
                    return "[green]●[/green]"
                elif data['status'] == 'partially_explored':
                    return "[yellow]◐[/yellow]"
                else:
                    return "[dim]◯[/dim]"
        
        # Check for signal sources
        for source in self.signal_sources:
            src_x, src_y, _ = source['coords']
            if abs(x - src_x) < 1.5 and abs(y - src_y) < 1.5:
                strength = source['strength']
                if strength > 0.7:
                    return "[bright_yellow]◆[/bright_yellow]"
                elif strength > 0.4:
                    return "[yellow]◇[/yellow]"
                else:
                    return "[dim]◇[/dim]"
        
        # Check for anomalies
        for anomaly in self.anomalies:
            ano_x, ano_y, _ = anomaly['coords']
            if abs(x - ano_x) < 2 and abs(y - ano_y) < 2:
                return "[red]✦[/red]"
        
        # Generate background stars and space
        if (x + y) % 17 == 0:
            return "[bright_white]✦[/bright_white]"  # Bright star
        elif (x * y) % 23 == 0:
            return "[white]·[/white]"  # Distant star
        elif (x + y * 2) % 31 == 0:
            return "[dim]·[/dim]"  # Very distant star
        elif abs(x) % 10 == 0 and abs(y) % 10 == 0:
            return "[dim]┼[/dim]"  # Grid reference
        else:
            return " "  # Empty space
    
    def _generate_coordinate_header(self, width: int) -> str:
        """Generate coordinate header for the map"""
        header = "   │"
        for col in range(0, width, 10):
            coord = (col - width // 2) * self.zoom_level + self.map_center_x
            header += f"{coord:+4.0f}     "
        header += "│"
        return f"[dim]{header}[/dim]"
    
    def _create_exploration_progress_bar(self, percentage: float, width: int) -> str:
        """Create exploration progress bar"""
        filled = int((percentage / 100) * width)
        empty = width - filled
        bar = "█" * filled + "░" * empty
        return f"│{bar}│"
    
    def _generate_map_legend(self) -> str:
        """Generate comprehensive map legend"""
        legend_lines = []
        legend_lines.append("[cyan]═══ MAP LEGEND ═══[/cyan]")
        legend_lines.append("[bright_green]⦿[/bright_green] Current Position  [green]●[/green] Explored Sector  [yellow]◐[/yellow] Partially Explored  [dim]◯[/dim] Unexplored")
        legend_lines.append("[bright_yellow]◆[/bright_yellow] Strong Signal     [yellow]◇[/yellow] Medium Signal    [dim]◇[/dim] Weak Signal        [red]✦[/red] Anomaly")
        legend_lines.append("[bright_white]✦[/bright_white] Major Star        [white]·[/white] Star             [dim]·[/dim] Distant Star       [dim]┼[/dim] Grid Reference")
        return "\n".join(legend_lines)
    
    def _generate_sector_info(self) -> List[str]:
        """Generate sector information display"""
        info_lines = []
        
        # Current sector detailed info
        current_sector_data = self.sector_map.get(self.current_sector, {})
        coords = current_sector_data.get('coords', (0, 0, 0))
        difficulty = current_sector_data.get('difficulty', 'Unknown')
        signals = current_sector_data.get('signals', 0)
        status = current_sector_data.get('status', 'unknown')
        
        info_lines.append(f"[yellow]Current: {self.current_sector}[/yellow]")
        info_lines.append(f"  Coordinates: ({coords[0]:+.1f}, {coords[1]:+.1f}, {coords[2]:+.1f})")
        info_lines.append(f"  Difficulty: {difficulty} | Signals: {signals} | Status: {status.title()}")
        
        # Nearby sectors
        info_lines.append("")
        info_lines.append("[yellow]Nearby Sectors:[/yellow]")
        
        # Calculate distances to other sectors
        distances = []
        current_coords = current_sector_data.get('coords', (0, 0, 0))
        
        for sector, data in self.sector_map.items():
            if sector != self.current_sector:
                sector_coords = data['coords']
                distance = math.sqrt(
                    (current_coords[0] - sector_coords[0])**2 +
                    (current_coords[1] - sector_coords[1])**2 +
                    (current_coords[2] - sector_coords[2])**2
                )
                distances.append((distance, sector, data))
        
        # Sort by distance and show closest 3
        distances.sort(key=lambda x: x[0])
        for distance, sector, data in distances[:3]:
            status_icon = {'explored': '✓', 'partially_explored': '~', 'unexplored': '?'}
            icon = status_icon.get(data['status'], '?')
            info_lines.append(f"  {icon} {sector}: {distance:.1f} units ({data['difficulty']})")
        
        return info_lines
    
    def _generate_signal_tracking_info(self) -> List[str]:
        """Generate signal source tracking information"""
        tracking_lines = []
        
        for i, source in enumerate(self.signal_sources[:5]):  # Show first 5 signals
            signal_id = source['id']
            coords = source['coords']
            frequency = source['frequency']
            strength = source['strength']
            
            # Calculate distance from current position
            current_coords = self.sector_map.get(self.current_sector, {'coords': (0, 0, 0)})['coords']
            distance = math.sqrt(
                (coords[0] - current_coords[0])**2 +
                (coords[1] - current_coords[1])**2 +
                (coords[2] - current_coords[2])**2
            )
            
            tracking_lines.append(f"[yellow]{signal_id}:[/yellow] {frequency:.1f}MHz | Str:{strength:.2f} | Dist:{distance:.1f}u")
            tracking_lines.append(f"  Position: ({coords[0]:+.1f}, {coords[1]:+.1f}, {coords[2]:+.1f})")
        
        if len(self.signal_sources) > 5:
            tracking_lines.append(f"... and {len(self.signal_sources) - 5} more signals")
        
        return tracking_lines

class DecoderPane(BasePane):
    """Enhanced Decoder & Analysis Toolkit pane [DAT] - Phase 10.4 with Phase 11 Puzzle Integration"""
    
    def __init__(self, **kwargs):
        super().__init__("Decoder & Analysis Toolkit [DAT]", **kwargs)
        self.current_tool = None
        self.analysis_data = None
        self.analysis_progress = 0
        self.analysis_stage = 0
        self.max_stages = 4
        self.tool_results = {}
        self.workspace_data = ""
        self.analysis_history = []
        self.validation_status = "pending"
        
        # Phase 11: Initialize puzzle system integration
        try:
            from ..puzzles import PuzzleManager, PuzzleDifficulty
            self.puzzle_manager = PuzzleManager()
            self.current_puzzle = None
            self.puzzle_mode = False
            self.puzzle_available = True
        except ImportError:
            self.puzzle_available = False
            self.puzzle_manager = None
        
        # Define the 6 specialized analysis tools
        self.analysis_tools = {
            'pattern_recognition': {
                'name': 'Pattern Recognition Engine',
                'description': 'Identify recurring patterns and sequences',
                'complexity': 3,
                'stages': ['scan', 'isolate', 'classify', 'validate'],
                'icon': '🔍'
            },
            'cryptographic': {
                'name': 'Cryptographic Analysis Suite',
                'description': 'Decrypt encoded signals and messages',
                'complexity': 4,
                'stages': ['frequency', 'cipher_detect', 'decode', 'verify'],
                'icon': '🔐'
            },
            'spectral': {
                'name': 'Spectral Decomposition Tool',
                'description': 'Analyze frequency components and harmonics',
                'complexity': 5,
                'stages': ['fourier', 'harmonic', 'reconstruct', 'synthesize'],
                'icon': '📊'
            },
            'ascii_manipulation': {
                'name': 'ASCII Data Processor',
                'description': 'Manipulate and transform ASCII patterns',
                'complexity': 2,
                'stages': ['parse', 'transform', 'arrange', 'output'],
                'icon': '📝'
            },
            'constellation_mapping': {
                'name': 'Constellation Mapper',
                'description': 'Map signal patterns to star configurations',
                'complexity': 4,
                'stages': ['coordinate', 'correlate', 'overlay', 'navigate'],
                'icon': '⭐'
            },
            'temporal_sequencing': {
                'name': 'Temporal Sequence Analyzer',
                'description': 'Analyze time-based signal variations',
                'complexity': 3,
                'stages': ['timeline', 'sequence', 'predict', 'extrapolate'],
                'icon': '⏱️'
            }
        }
        
        # Initialize workspace
        self._display_tool_selection()
    
    def select_tool(self, tool_name: str):
        """Select and initialize analysis tool"""
        if tool_name in self.analysis_tools:
            self.current_tool = tool_name
            self.analysis_progress = 0
            self.analysis_stage = 0
            self.tool_results = {}
            self.validation_status = "pending"
            self._display_tool_interface()
        else:
            self._display_tool_selection()
    
    def start_analysis(self, signal: Any):
        """Start analysis with currently selected tool"""
        if not self.current_tool:
            self._display_tool_selection()
            return
        
        self.analysis_data = signal
        self.analysis_stage = 1
        self.analysis_progress = 0
        self._run_analysis_stage()
    
    def advance_analysis(self):
        """Advance to next analysis stage"""
        if self.analysis_stage < self.max_stages:
            self.analysis_stage += 1
            self._run_analysis_stage()
        else:
            # Already at max stages, complete the analysis
            self._complete_analysis()
    
    def _run_analysis_stage(self):
        """Execute current analysis stage"""
        if not self.current_tool or not self.analysis_data:
            return
        
        tool_data = self.analysis_tools[self.current_tool]
        stages = tool_data['stages']
        
        if self.analysis_stage <= len(stages):
            stage_index = self.analysis_stage - 1
            current_stage = stages[stage_index]
            
            # Set progress to completed for this stage
            self.analysis_progress = 1.0
            self.workspace_data = f"Completed {current_stage} analysis"
            
            # Store stage result
            self.tool_results[current_stage] = f"Stage {self.analysis_stage}: {current_stage.title()} completed successfully"
            
            # Update display to show progress
            self._display_tool_interface()
            
            # If this was the last stage, mark as ready for completion
            if self.analysis_stage >= self.max_stages:
                self.workspace_data = "All stages completed - ready for finalization"
                self.validation_status = "ready_to_complete"
    
    def _complete_analysis(self):
        """Complete the analysis workflow"""
        self.validation_status = "completed"
        self.workspace_data = "✅ Analysis complete - results validated and logged"
        self.analysis_progress = 1.0
        
        # Add to history
        analysis_entry = {
            'tool': self.current_tool,
            'signal_id': getattr(self.analysis_data, 'id', 'Unknown'),
            'timestamp': time.time(),
            'results': self.tool_results.copy(),
            'completion_status': 'success'
        }
        self.analysis_history.append(analysis_entry)
        
        # Update the display to show completion
        self._display_tool_interface()
    
    def _display_tool_selection(self):
        """Display tool selection interface"""
        lines = []
        lines.append("[bold cyan]🛠️ DECODER & ANALYSIS TOOLKIT[/bold cyan]")
        lines.append("═" * 60)
        lines.append("")
        lines.append("[yellow]Select Analysis Tool:[/yellow]")
        lines.append("")
        
        for i, (tool_id, tool_data) in enumerate(self.analysis_tools.items(), 1):
            icon = tool_data['icon']
            name = tool_data['name']
            desc = tool_data['description']
            complexity = tool_data['complexity']
            complexity_bar = "●" * complexity + "○" * (9 - complexity)
            
            lines.append(f"[white]{i}.[/white] {icon} [yellow]{name}[/yellow]")
            lines.append(f"   {desc}")
            lines.append(f"   Complexity: {complexity_bar} ({complexity}/9)")
            lines.append("")
        
        lines.append("[cyan]═══ TOOL SELECTION ═══[/cyan]")
        lines.append("[green]Commands:[/green]")
        lines.append("• [yellow]ANALYZE pattern_recognition[/yellow] - Use Pattern Recognition")
        lines.append("• [yellow]ANALYZE cryptographic[/yellow] - Use Cryptographic Suite")
        lines.append("• [yellow]ANALYZE spectral[/yellow] - Use Spectral Analysis")
        lines.append("• [yellow]ANALYZE ascii_manipulation[/yellow] - Use ASCII Processor")
        lines.append("• [yellow]ANALYZE constellation_mapping[/yellow] - Use Constellation Mapper")
        lines.append("• [yellow]ANALYZE temporal_sequencing[/yellow] - Use Temporal Analyzer")
        lines.append("")
        lines.append("[dim]Select a tool to begin multi-stage analysis workflow[/dim]")
        
        self.update_content(lines)
    
    def _display_tool_interface(self):
        """Display interface for currently selected tool"""
        if not self.current_tool:
            self._display_tool_selection()
            return
        
        lines = []
        tool_data = self.analysis_tools[self.current_tool]
        
        lines.append(f"[bold cyan]{tool_data['icon']} {tool_data['name'].upper()}[/bold cyan]")
        lines.append("═" * 60)
        lines.append("")
        lines.append(f"[yellow]Description:[/yellow] {tool_data['description']}")
        lines.append(f"[yellow]Complexity Level:[/yellow] {tool_data['complexity']}/5")
        lines.append("")
        
        # Analysis stages visualization
        lines.append("[cyan]═══ ANALYSIS WORKFLOW ═══[/cyan]")
        stages = tool_data['stages']
        for i, stage in enumerate(stages, 1):
            if i < self.analysis_stage:
                status = "[green]✓[/green]"
            elif i == self.analysis_stage:
                status = "[yellow]►[/yellow]"
        else:
                status = "[dim]○[/dim]"
            
        lines.append(f"{status} Stage {i}: {stage.title()}")
        
        # Progress indicator
        if self.analysis_stage > 0:
            lines.append("")
            lines.append(f"[cyan]Current Stage Progress:[/cyan]")
            progress_bar = self._create_analysis_progress_bar(self.analysis_progress, 40)
            lines.append(progress_bar)
        
        # Tool-specific interface
        lines.append("")
        lines.append("[cyan]═══ TOOL INTERFACE ═══[/cyan]")
        lines.extend(self._get_tool_specific_interface())
        
        # Workspace area
        lines.append("")
        lines.append("[cyan]═══ WORKSPACE ═══[/cyan]")
        lines.extend(self._display_workspace())
        
        # Commands
        lines.append("")
        lines.append("[green]Available Commands:[/green]")
        if self.analysis_data and self.analysis_stage == 0:
            lines.append("• [yellow]ADVANCE[/yellow] - Start analysis")
        elif self.analysis_stage > 0 and self.analysis_stage < self.max_stages:
            lines.append("• [yellow]ADVANCE[/yellow] - Next stage")
        elif self.analysis_stage >= self.max_stages and self.validation_status != "completed":
            lines.append("• [yellow]ADVANCE[/yellow] - Complete analysis")
        elif self.validation_status == "completed":
            lines.append("• [green]✅ Analysis Complete![/green]")
            lines.append("• [yellow]RESET[/yellow] - Start new analysis")
        
        lines.append("• [yellow]RESET[/yellow] - Reset tool")
        lines.append("• [yellow]TOOLS[/yellow] - Return to tool selection")
        
        self.update_content(lines)
    
    def _get_tool_specific_interface(self) -> List[str]:
        """Get tool-specific interface elements"""
        if not self.current_tool:
            return ["No tool selected"]
        
        tool_interfaces = {
            'pattern_recognition': self._pattern_recognition_interface,
            'cryptographic': self._cryptographic_interface,
            'spectral': self._spectral_interface,
            'ascii_manipulation': self._ascii_manipulation_interface,
            'constellation_mapping': self._constellation_mapping_interface,
            'temporal_sequencing': self._temporal_sequencing_interface
        }
        
        interface_func = tool_interfaces.get(self.current_tool)
        if interface_func:
            return interface_func()
        else:
            return ["Interface loading..."]
    
    def _pattern_recognition_interface(self) -> List[str]:
        """Pattern Recognition tool interface"""
        lines = []
        lines.append("[yellow]🔍 Pattern Recognition Engine[/yellow]")
        lines.append("")
        
        if self.analysis_data:
            lines.append("Signal Pattern Analysis:")
            lines.append("┌────────────────────────────────┐")
            lines.append("│ ▓▒░█▓▒░█▓▒░█▓▒░█▓▒░█▓▒░█▓▒░ │")
            lines.append("│ ░▒▓█░▒▓█░▒▓█░▒▓█░▒▓█░▒▓█░▒▓ │")
            lines.append("│ ▒▓█░▒▓█░▒▓█░▒▓█░▒▓█░▒▓█░▒▓█ │")
            lines.append("└────────────────────────────────┘")
        lines.append("")
            
        if self.analysis_stage >= 2:
            lines.append("Detected Patterns:")
            lines.append("• Pattern A: ▓▒░█ (repeats 8 times)")
            lines.append("• Pattern B: █░▒▓ (alternating sequence)")
            lines.append("• Frequency: 125.5 Hz base pattern")
        else:
            lines.append("No signal data loaded")
            lines.append("Use FOCUS command to select signal for analysis")
        
        return lines
    
    def _cryptographic_interface(self) -> List[str]:
        """Cryptographic Analysis tool interface"""
        lines = []
        lines.append("[yellow]🔐 Cryptographic Analysis Suite[/yellow]")
        lines.append("")
        
        if self.analysis_data:
            lines.append("Encrypted Signal Data:")
            lines.append("┌─────────────────────────────────────┐")
            lines.append("│ KHOOR ZRUOG VLJ DOSKD EHWD JDPPD   │")
            lines.append("│ 01101000 01100101 01101100 01101100 │")
            lines.append("│ █▓▒░ ░▒▓█ ▓█░▒ ▒░█▓ ░█▓▒ ▓▒░█    │")
            lines.append("└─────────────────────────────────────┘")
            lines.append("")
            
            if self.analysis_stage >= 2:
                lines.append("Cipher Analysis:")
                lines.append("• Type: Caesar Cipher (shift=3)")
                lines.append("• Confidence: 94.7%")
                lines.append("• Key Pattern: ALPHA BETA GAMMA")
                
            if self.analysis_stage >= 3:
                lines.append("")
                lines.append("Decrypted Message:")
                lines.append("[green]'HELLO WORLD SIG ALPHA BETA GAMMA'[/green]")
        else:
            lines.append("No encrypted data to analyze")
            lines.append("Waiting for signal input...")
        
        return lines
    
    def _spectral_interface(self) -> List[str]:
        """Spectral Decomposition tool interface"""
        lines = []
        lines.append("[yellow]📊 Spectral Decomposition Tool[/yellow]")
        lines.append("")
        
        if self.analysis_data:
            lines.append("Frequency Domain Analysis:")
            lines.append("┌─Frequency─┬─Amplitude─┬─Phase─┐")
            lines.append("│   125 Hz  │   0.850   │ 45°   │")
            lines.append("│   250 Hz  │   0.420   │ 90°   │")
            lines.append("│   375 Hz  │   0.180   │ 135°  │")
            lines.append("│   500 Hz  │   0.095   │ 180°  │")
            lines.append("└───────────┴───────────┴───────┘")
        lines.append("")
            
        if self.analysis_stage >= 2:
            lines.append("Harmonic Structure:")
            lines.append("Primary: 125 Hz (fundamental)")
            lines.append("2nd: 250 Hz (octave)")
            lines.append("3rd: 375 Hz (perfect fifth)")
            lines.append("4th: 500 Hz (perfect fourth)")
        else:
            lines.append("No spectral data available")
            lines.append("Signal required for frequency analysis")
        
        return lines
    
    def _ascii_manipulation_interface(self) -> List[str]:
        """ASCII Manipulation tool interface"""
        lines = []
        lines.append("[yellow]📝 ASCII Data Processor[/yellow]")
        lines.append("")
        
        lines.append("ASCII Workspace:")
        lines.append("┌─Input────────────────────────────┐")
        lines.append("│ Signal data converted to ASCII:  │")
        lines.append("│ 83 73 71 78 65 76 80 72 65       │")
        lines.append("│ S  I  G  N  A  L  P  H  A         │")
        lines.append("└───────────────────────────────────┘")
        lines.append("")
        
        if self.analysis_stage >= 2:
            lines.append("┌─Transformed─────────────────────┐")
            lines.append("│ ROT13: FVTANY CUVGN             │")
            lines.append("│ Base64: U0lHTkFMUEhB            │")
            lines.append("│ Hex: 5349474E414C50484E         │")
            lines.append("└─────────────────────────────────┘")
        
        return lines

    def _constellation_mapping_interface(self) -> List[str]:
        """Constellation Mapping tool interface"""
        lines = []
        lines.append("[yellow]⭐ Constellation Mapper[/yellow]")
        lines.append("")
        
        if self.analysis_data:
            lines.append("Signal Constellation Map:")
            lines.append("┌─────────────────────────────────┐")
            lines.append("│        ✦     ·   ✦              │")
            lines.append("│    ·       ✦       ·   ✦       │")
            lines.append("│  ✦   ·       ◆       ·         │")
            lines.append("│      ✦   ·       ✦   ·   ✦     │")
            lines.append("│  ·       ✦       ·       ✦     │")
            lines.append("└─────────────────────────────────┘")
            lines.append("")
            
            if self.analysis_stage >= 2:
                lines.append("Matched Constellations:")
                lines.append("• Cygnus (82% match)")
                lines.append("• Andromeda (67% match)")
                lines.append("• Custom Pattern (94% match)")
        else:
            lines.append("No coordinate data for mapping")
            lines.append("Requires positioned signal sources")
        
        return lines
    
    def _temporal_sequencing_interface(self) -> List[str]:
        """Temporal Sequencing tool interface"""
        lines = []
        lines.append("[yellow]⏱️ Temporal Sequence Analyzer[/yellow]")
        lines.append("")
        
        if self.analysis_data:
            lines.append("Temporal Pattern Analysis:")
            lines.append("Time: 0s ──●──○────●──●──○────●──")
            lines.append("Time: 2s ──○──●────○──○──●────○──")
            lines.append("Time: 4s ──●──○────●──●──○────●──")
            lines.append("Time: 6s ──○──●────○──○──●────○──")
            lines.append("")
            
            if self.analysis_stage >= 2:
                lines.append("Sequence Properties:")
                lines.append("• Period: 2.0 seconds")
                lines.append("• Pattern: Alternating binary")
                lines.append("• Prediction: 95.2% accuracy")
        else:
            lines.append("No temporal data captured")
            lines.append("Requires time-series signal data")
        
        return lines
    
    def _display_workspace(self) -> List[str]:
        """Display analysis workspace"""
        lines = []
        
        if self.workspace_data:
            lines.append("Active Workspace Data:")
            lines.append(f"[dim]{self.workspace_data}[/dim]")
        else:
            lines.append("[dim]Workspace empty - analysis pending[/dim]")
        
        lines.append("")
        
        # Show results if available
        if self.tool_results:
            lines.append("Analysis Results:")
            for stage, result in self.tool_results.items():
                lines.append(f"• {stage}: {result}")
        
        return lines
    
    def _create_analysis_progress_bar(self, progress: float, width: int) -> str:
        """Create analysis progress bar"""
        filled = int(progress * width)
        empty = width - filled
        bar = "█" * filled + "░" * empty
        percentage = progress * 100
        return f"│{bar}│ {percentage:.1f}%"
    
    def reset_analysis(self):
        """Reset current analysis"""
        self.analysis_progress = 0
        self.analysis_stage = 0
        self.tool_results = {}
        self.workspace_data = ""
        self.validation_status = "pending"
        if self.current_tool:
            self._display_tool_interface()
        else:
            self._display_tool_selection()
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get summary of all completed analyses"""
        return {
            'total_analyses': len(self.analysis_history),
            'tools_used': list(set(entry['tool'] for entry in self.analysis_history)),
            'current_tool': self.current_tool,
            'current_stage': self.analysis_stage,
            'validation_status': self.validation_status
        }
    
    # Phase 11: Puzzle System Integration Methods
    def start_puzzle_mode(self):
        """Start interactive puzzle mode for current tool"""
        if not self.puzzle_available or not self.current_tool:
            return False
        
        try:
            puzzle = self._create_puzzle_for_tool(self.current_tool)
            if puzzle:
                self.current_puzzle = puzzle
                self.puzzle_mode = True
                puzzle.start_puzzle()
                self._display_tool_interface()
                return True
        except Exception as e:
            self.workspace_data = f"❌ Puzzle initialization failed: {str(e)}"
            self._display_tool_interface()
        
        return False
    
    def _create_puzzle_for_tool(self, tool_name: str):
        """Create appropriate puzzle for the selected tool"""
        if not self.puzzle_available:
            return None
        
        try:
            # Determine difficulty based on signal complexity
            difficulty = self._get_puzzle_difficulty()
            
            if tool_name == 'pattern_recognition':
                from ..puzzles.visual_patterns import ConstellationPuzzle
                return ConstellationPuzzle(difficulty)
            elif tool_name == 'cryptographic':
                from ..puzzles.cryptographic import CaesarCipherPuzzle
                return CaesarCipherPuzzle(difficulty)
            elif tool_name == 'spectral':
                from ..puzzles.audio_patterns import MorseCodePuzzle
                return MorseCodePuzzle(difficulty)
            elif tool_name == 'ascii_manipulation':
                from ..puzzles.visual_patterns import SymbolRecognitionPuzzle
                return SymbolRecognitionPuzzle(difficulty)
            elif tool_name == 'constellation_mapping':
                from ..puzzles.visual_patterns import PatternFragmentPuzzle
                return PatternFragmentPuzzle(difficulty)
            elif tool_name == 'temporal_sequencing':
                from ..puzzles.logic_puzzles import SequenceDeductionPuzzle
                return SequenceDeductionPuzzle(difficulty)
        except ImportError:
            pass
        
        return None
    
    def _get_puzzle_difficulty(self):
        """Determine puzzle difficulty based on signal properties"""
        if not self.analysis_data:
            from ..puzzles import PuzzleDifficulty
            return PuzzleDifficulty.EASY
        
        try:
            from ..puzzles import PuzzleDifficulty
            strength = getattr(self.analysis_data, 'strength', 0.5)
            complexity = getattr(self.analysis_data, 'complexity', 3)
            
            if complexity >= 7:
                return PuzzleDifficulty.NIGHTMARE
            elif complexity >= 5:
                return PuzzleDifficulty.HARD
            elif complexity >= 3:
                return PuzzleDifficulty.NORMAL
            else:
                return PuzzleDifficulty.EASY
        except ImportError:
            return None
    
    def submit_puzzle_answer(self, answer: str):
        """Submit answer to current puzzle"""
        if not self.puzzle_mode or not self.current_puzzle:
            return False
        
        try:
            result = self.current_puzzle.submit_answer(answer)
            if result.is_correct:
                self.workspace_data = f"✅ Puzzle solved! Score: {result.score}"
                self.puzzle_mode = False
                self.validation_status = "puzzle_completed"
            else:
                self.workspace_data = f"❌ Incorrect. {result.feedback}"
            
            self._display_tool_interface()
            return result.is_correct
        except Exception as e:
            self.workspace_data = f"❌ Answer submission failed: {str(e)}"
            self._display_tool_interface()
            return False
    
    def get_puzzle_hint(self):
        """Get hint for current puzzle"""
        if not self.puzzle_mode or not self.current_puzzle:
            return None
        
        try:
            hint = self.current_puzzle.get_hint()
            if hint:
                self.workspace_data = f"💡 Hint: {hint.text}"
                self._display_tool_interface()
                return hint
        except Exception as e:
            self.workspace_data = f"❌ Hint unavailable: {str(e)}"
            self._display_tool_interface()
        
        return None

class LogPane(ScrollableContainer):
    """Enhanced Captain's Log & Database pane [CLD] - Phase 10.5"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Captain's Log & Database [CLD]"
        self.log_entries: List[Dict[str, Any]] = []
        self.bookmarks: List[Dict[str, Any]] = []
        self.search_filter = ""
        self.category_filter = "all"
        self.current_view = "recent"  # recent, search, category, bookmarks, timeline
        self.cross_references: Dict[str, List[str]] = {}
        self.lore_fragments: List[Dict[str, Any]] = []
        self.discovery_timeline: List[Dict[str, Any]] = []
        
        # Define 8 log categories with icons
        self.log_categories = {
            'discovery': {'name': 'Discovery', 'icon': '🔍', 'color': 'yellow'},
            'analysis': {'name': 'Analysis', 'icon': '🔬', 'color': 'cyan'},
            'navigation': {'name': 'Navigation', 'icon': '🧭', 'color': 'green'},
            'communication': {'name': 'Communication', 'icon': '📡', 'color': 'blue'},
            'system': {'name': 'System', 'icon': '⚙️', 'color': 'white'},
            'warning': {'name': 'Warning', 'icon': '⚠️', 'color': 'red'},
            'lore': {'name': 'Lore Fragment', 'icon': '📜', 'color': 'magenta'},
            'personal': {'name': 'Personal Log', 'icon': '📝', 'color': 'dim'}
        }
        
        # Set scrollable properties
        self.can_focus = True
        self.auto_scroll = True  # Enable auto-scroll to bottom for new entries
        
        # Content widget for displaying the log
        self.content_widget = None
        
        # Initialize with welcome entry
        self._add_initial_entries()
    
    def compose(self) -> ComposeResult:
        """Compose the scrollable log pane"""
        self.content_widget = Static("", id="log_content")
        yield self.content_widget
    
    async def on_mount(self) -> None:
        """Initialize the pane after mounting"""
        # Ensure content widget is available
        if not self.content_widget:
            try:
                self.content_widget = self.query_one("#log_content")
            except:
                pass
        # Display initial content
        self._display_current_view()
    
    def update_content(self, lines: List[str]):
        """Update the content of this scrollable pane with proper formatting for scrolling"""
        if not self.content_widget:
            # Try to find the content widget
            try:
                self.content_widget = self.query_one("#log_content")
            except:
                # If we can't find it, we're probably in test mode
                return
        
        if self.content_widget:
            # Build content with MINIMAL padding for better UX
            content_lines = [f"[bold cyan]{self.title}[/bold cyan]"]
            
            if lines:
                content_lines.extend(lines)
            else:
                content_lines.append("[dim]No data[/dim]")
            
            # Join with newlines - NO extra padding for better UX
            full_content = "\n".join(content_lines)
            self.content_widget.update(full_content)
            
            # Auto-scroll to bottom for LogPane only (to show new entries)
            if self.auto_scroll:
                self.call_after_refresh(self._scroll_to_bottom_with_delay)
    
    def _add_initial_entries(self):
        """Add initial log entries for the system"""
        import datetime
        
        welcome_entry = {
            'id': 'INIT_001',
            'timestamp': time.time(),
            'category': 'system',
            'title': 'Captain\'s Log System Initialized',
            'content': 'Advanced logging and database system online. Ready for mission documentation.',
            'tags': ['initialization', 'system'],
            'metadata': {
                'signal_refs': [],
                'coordinates': None,
                'confidence': 1.0
            }
        }
        self.log_entries.append(welcome_entry)
        
        self._display_current_view()
    
    def add_log_entry(self, content: str, category: str = 'system', title: str = None, 
                     tags: List[str] = None, signal_refs: List[str] = None,
                     coordinates: Tuple[float, float, float] = None):
        """Add a new enhanced log entry with metadata and auto-scroll"""
        entry_id = f"LOG_{len(self.log_entries):04d}"
        
        # Auto-generate title if not provided
        if not title:
            if len(content) > 50:
                title = content[:47] + "..."
            else:
                title = content
        
        entry = {
            'id': entry_id,
            'timestamp': time.time(),
            'category': category,
            'title': title,
            'content': content,
            'tags': tags or [],
            'metadata': {
                'signal_refs': signal_refs or [],
                'coordinates': coordinates,
                'confidence': 1.0,
                'read_count': 0,
                'last_accessed': time.time()
            }
        }
        
        self.log_entries.append(entry)
        
        # Auto-detect cross-references
        self._detect_cross_references(entry)
        
        # Add to discovery timeline if it's a discovery
        if category == 'discovery':
            self._add_to_timeline(entry)
        
        # Update display with auto-scroll
        self._display_current_view()
        
        # Force scroll to bottom for new entries
        self.call_after_refresh(self._scroll_to_bottom_with_delay)
    
    def _scroll_to_bottom_with_delay(self):
        """Scroll to bottom with a small delay to ensure content is rendered"""
        def delayed_scroll():
            try:
                self.scroll_end(animate=True)  # Smooth animated scroll
            except:
                pass
        
        # Use a simple timer to delay the scroll
        if hasattr(self, 'set_timer'):
            self.set_timer(0.1, delayed_scroll)
        else:
            # Fallback - just scroll immediately
            self._scroll_to_bottom()
    
    def _scroll_to_bottom(self):
        """Scroll to the bottom of the content"""
        try:
            # Get the maximum scroll position and scroll there
            self.scroll_end(animate=False)
        except:
            pass  # Ignore errors if scrolling isn't ready yet
    
    def _detect_cross_references(self, entry: Dict[str, Any]):
        """Automatically detect cross-references in log entries"""
        content_lower = entry['content'].lower()
        entry_id = entry['id']
        
        # Look for signal references
        signal_patterns = ['sig_', 'signal', 'beacon', 'transmission']
        for pattern in signal_patterns:
            if pattern in content_lower:
                if 'signals' not in self.cross_references:
                    self.cross_references['signals'] = []
                if entry_id not in self.cross_references['signals']:
                    self.cross_references['signals'].append(entry_id)
        
        # Look for location references
        location_patterns = ['alpha', 'beta', 'gamma', 'sector', 'coordinates']
        for pattern in location_patterns:
            if pattern in content_lower:
                if 'locations' not in self.cross_references:
                    self.cross_references['locations'] = []
                if entry_id not in self.cross_references['locations']:
                    self.cross_references['locations'].append(entry_id)
        
        # Look for analysis references
        analysis_patterns = ['pattern', 'decode', 'cipher', 'frequency', 'analysis']
        for pattern in analysis_patterns:
            if pattern in content_lower:
                if 'analysis' not in self.cross_references:
                    self.cross_references['analysis'] = []
                if entry_id not in self.cross_references['analysis']:
                    self.cross_references['analysis'].append(entry_id)
    
    def _add_to_timeline(self, entry: Dict[str, Any]):
        """Add entry to discovery timeline"""
        timeline_entry = {
            'timestamp': entry['timestamp'],
            'entry_id': entry['id'],
            'title': entry['title'],
            'category': entry['category'],
            'significance': self._calculate_significance(entry)
        }
        self.discovery_timeline.append(timeline_entry)
        
        # Sort timeline by timestamp
        self.discovery_timeline.sort(key=lambda x: x['timestamp'])
    
    def _calculate_significance(self, entry: Dict[str, Any]) -> float:
        """Calculate the significance score for a timeline entry"""
        base_score = 1.0
        
        # Category weights
        category_weights = {
            'discovery': 3.0,
            'lore': 2.5,
            'analysis': 2.0,
            'communication': 1.8,
            'navigation': 1.5,
            'system': 1.0,
            'warning': 2.2,
            'personal': 0.8
        }
        
        category_weight = category_weights.get(entry['category'], 1.0)
        
        # Tag bonuses
        tag_bonuses = {
            'breakthrough': 2.0,
            'ancient': 1.8,
            'quantum': 1.5,
            'mystery': 1.3,
            'signal': 1.2
        }
        
        tag_bonus = 1.0
        for tag in entry.get('tags', []):
            tag_bonus *= tag_bonuses.get(tag, 1.0)
        
        return base_score * category_weight * tag_bonus
    
    def add_bookmark(self, entry_id: str, note: str = ""):
        """Add bookmark to an entry"""
        entry = self._find_entry_by_id(entry_id)
        if entry:
            bookmark = {
                'entry_id': entry_id,
                'title': entry['title'],
                'note': note,
                'timestamp': time.time(),
                'category': entry['category']
            }
            self.bookmarks.append(bookmark)
    
    def search_logs(self, query: str, category: str = "all") -> List[Dict[str, Any]]:
        """Enhanced search with category filtering"""
        self.search_filter = query.lower()
        self.category_filter = category
        
        matching_entries = []
        
        for entry in self.log_entries:
            # Category filter
            if category != "all" and entry['category'] != category:
                continue
            
            # Text search in title, content, and tags
            searchable_text = (
                entry['title'].lower() + " " +
                entry['content'].lower() + " " +
                " ".join(entry.get('tags', [])).lower()
            )
            
            if query.lower() in searchable_text:
                matching_entries.append(entry)
        
        return matching_entries
    
    def set_view(self, view_type: str, **kwargs):
        """Set the current view type for the log pane"""
        valid_views = ['recent', 'category', 'bookmarks', 'timeline', 'search', 'statistics', 'progression']
        
        if view_type in valid_views:
            self.current_view = view_type
            
            # Store any additional parameters
            if view_type == 'search':
                self.search_filter = kwargs.get('query', '')
                self.category_filter = kwargs.get('category', 'all')
            elif view_type == 'category':
                self.category_filter = kwargs.get('category', 'all')
            
            self._display_current_view()
    
    def _display_current_view(self):
        """Display content based on current view type"""
        if self.current_view == 'recent':
            self._display_recent_entries()
        elif self.current_view == 'category':
            self._display_category_view()
        elif self.current_view == 'bookmarks':
            self._display_bookmarks()
        elif self.current_view == 'timeline':
            self._display_timeline()
        elif self.current_view == 'search':
            self._display_search_results()
        elif self.current_view == 'statistics':
            self._display_statistics()
        elif self.current_view == 'progression':
            self._display_progression()
        else:
            self._display_recent_entries()
    
    def _display_progression(self):
        """Display progression information in the log pane"""
        lines = []
        
        # Try to get progression data from the game
        game_state = None
        try:
            # This is a bit hacky, but we need to access the game state
            # In a real implementation, this would be passed more cleanly
            from ..game_core import SignalCartographer
            import inspect
            
            # Find the game state in the call stack (hacky but works)
            for frame_info in inspect.stack():
                frame_locals = frame_info.frame.f_locals
                if 'self' in frame_locals and hasattr(frame_locals['self'], 'progression'):
                    game_state = frame_locals['self']
                    break
        except:
            pass
        
        if game_state and hasattr(game_state, 'progression'):
            progression = game_state.progression
            
            lines.append("[bold cyan]🎯 PROGRESSION DASHBOARD[/bold cyan]")
            lines.append("")
            
            # Analysis Points
            lines.append(f"[yellow]Analysis Points:[/yellow] {progression.analysis_points}")
            lines.append("")
            
            # Available Upgrades
            available_upgrades = progression.get_available_upgrades()
            if available_upgrades:
                lines.append("[green]🛠️ Available Upgrades:[/green]")
                for upgrade in available_upgrades:
                    lines.append(f"  {upgrade.icon} [bold]{upgrade.name}[/bold] (Cost: {upgrade.cost})")
                    lines.append(f"    {upgrade.description}")
                lines.append("    [dim]Use: UPGRADES BUY <upgrade_name>[/dim]")
                lines.append("")
            
            # Purchased Upgrades
            purchased_upgrades = progression.get_purchased_upgrades()
            if purchased_upgrades:
                lines.append("[blue]✅ Active Upgrades:[/blue]")
                for upgrade in purchased_upgrades:
                    lines.append(f"  {upgrade.icon} [bold]{upgrade.name}[/bold] - ACTIVE")
                lines.append("")
            
            # Recent Achievements
            unlocked_achievements = progression.get_unlocked_achievements()
            if unlocked_achievements:
                lines.append("[magenta]🏆 Recent Achievements:[/magenta]")
                # Show last 3 achievements
                for achievement in unlocked_achievements[-3:]:
                    lines.append(f"  {achievement.icon} [bold]{achievement.name}[/bold]")
                    lines.append(f"    {achievement.description}")
                if len(unlocked_achievements) > 3:
                    lines.append(f"    [dim]... and {len(unlocked_achievements) - 3} more[/dim]")
                lines.append("    [dim]Use: ACHIEVEMENTS for full list[/dim]")
                lines.append("")
            
            # Progress on next achievements
            lines.append("[yellow]📊 Progress Tracking:[/yellow]")
            progress_shown = 0
            for achievement in progression.achievements.values():
                if not achievement.unlocked and not achievement.hidden and progress_shown < 3:
                    progress_pct = (achievement.progress / achievement.target) * 100
                    progress_bar = self._create_progress_bar(progress_pct / 100.0, 20)
                    lines.append(f"  {achievement.icon} {achievement.name}")
                    lines.append(f"    {progress_bar} {achievement.progress}/{achievement.target}")
                    progress_shown += 1
            
            if progress_shown == 0:
                lines.append("  [dim]All visible achievements completed![/dim]")
            
            lines.append("")
            lines.append("[dim]Use F5 to cycle log views | Use PROGRESS for detailed stats[/dim]")
            
        else:
            lines.append("[red]Progression system not available[/red]")
        
        self.update_content(lines)
    
    def _create_progress_bar(self, progress: float, width: int = 20) -> str:
        """Create a simple progress bar"""
        filled = int(progress * width)
        empty = width - filled
        return f"[green]{'█' * filled}[/green][dim]{'░' * empty}[/dim]"
    
    def _display_recent_entries(self):
        """Display recent log entries with permanent content at top, new entries at bottom"""
        lines = []
        lines.append("[bold cyan]📚 CAPTAIN'S LOG & DATABASE[/bold cyan]")
        lines.append("═" * 60)
        
        # Header with statistics - PERMANENT CONTENT AT TOP
        total_entries = len(self.log_entries)
        total_bookmarks = len(self.bookmarks)
        timeline_events = len(self.discovery_timeline)
        
        lines.append(f"[yellow]Database Status:[/yellow] {total_entries} entries | {total_bookmarks} bookmarks | {timeline_events} timeline events")
        
        # Commands section - PERMANENT CONTENT AT TOP
        lines.append("[cyan]═══ DATABASE COMMANDS ═══[/cyan]")
        lines.append("[green]View Controls:[/green]")
        lines.append("• [yellow]LOG search <query>[/yellow] - Search entries")
        lines.append("• [yellow]LOG category <category>[/yellow] - Filter by category") 
        lines.append("• [yellow]LOG bookmarks[/yellow] - Show bookmarked entries")
        lines.append("• [yellow]LOG timeline[/yellow] - Discovery timeline")
        lines.append("• [yellow]LOG stats[/yellow] - Database statistics")
        lines.append("[green]Categories:[/green] " + " | ".join([f"[{cat['color']}]{cat['icon']} {name}[/{cat['color']}]" 
                                                                for name, cat in self.log_categories.items()]))
        lines.append("[cyan]═══ RECENT ENTRIES ═══[/cyan]")
        
        # Show recent entries at the BOTTOM - NEW CONTENT AREA
        recent_entries = self.log_entries[-20:] if len(self.log_entries) > 20 else self.log_entries
        
        for entry in recent_entries:  # Don't reverse - show in chronological order
            lines.extend(self._format_entry_summary(entry))
        
        # NO extra padding for better UX
        if not recent_entries:
            lines.append("[dim]No log entries yet[/dim]")
        
        self.update_content(lines)
    
    def _display_search_results(self):
        """Display search results with controls at top, results at bottom"""
        lines = []
        lines.append("[bold cyan]🔍 SEARCH RESULTS[/bold cyan]")
        lines.append("═" * 60)
        
        # Search controls at TOP
        if self.search_filter:
            lines.append(f"[yellow]Query:[/yellow] '{self.search_filter}'")
            if self.category_filter != "all":
                cat_info = self.log_categories[self.category_filter]
                lines.append(f"[yellow]Category Filter:[/yellow] {cat_info['icon']} {cat_info['name']}")
        else:
            lines.append("[dim]No search query specified[/dim]")
            lines.append("Use: [yellow]LOG search <query>[/yellow]")
        
        lines.append("[cyan]═══ SEARCH RESULTS ═══[/cyan]")
        
        # Search results at BOTTOM
        if self.search_filter:
            results = self.search_logs(self.search_filter, self.category_filter)
            lines.append(f"[green]Found {len(results)} matching entries:[/green]")
            
            for entry in results[-15:]:  # Show last 15 results
                lines.extend(self._format_entry_summary(entry))
        
        self.update_content(lines)
    
    def _display_category_view(self):
        """Display entries filtered by category with controls at top, entries at bottom"""
        lines = []
        lines.append("[bold cyan]📂 CATEGORY VIEW[/bold cyan]")
        lines.append("═" * 60)
        
        # Category controls at TOP
        if self.category_filter != "all":
            cat_info = self.log_categories[self.category_filter]
            lines.append(f"[yellow]Category:[/yellow] {cat_info['icon']} {cat_info['name']}")
        else:
            # Show category overview at TOP
            lines.append("[yellow]Category Overview:[/yellow]")
            
            for cat_id, cat_info in self.log_categories.items():
                count = len([e for e in self.log_entries if e['category'] == cat_id])
                icon = cat_info['icon']
                name = cat_info['name']
                color = cat_info['color']
                lines.append(f"[{color}]{icon} {name}:[/{color}] {count} entries")
            
            lines.append("Use: [yellow]LOG category <category_name>[/yellow]")
        
        lines.append("[cyan]═══ CATEGORY ENTRIES ═══[/cyan]")
        
        # Category entries at BOTTOM
        if self.category_filter != "all":
            category_entries = [e for e in self.log_entries if e['category'] == self.category_filter]
            lines.append(f"[green]{len(category_entries)} entries in this category:[/green]")
            
            for entry in category_entries[-15:]:  # Show last 15
                lines.extend(self._format_entry_summary(entry))
        
        self.update_content(lines)
    
    def _display_bookmarks(self):
        """Display bookmarked entries"""
        lines = []
        lines.append("[bold cyan]🔖 BOOKMARKED ENTRIES[/bold cyan]")
        lines.append("═" * 60)
        lines.append("")
        
        if self.bookmarks:
            lines.append(f"[green]{len(self.bookmarks)} bookmarked entries:[/green]")
            lines.append("")
            
            for bookmark in self.bookmarks:
                entry = self._find_entry_by_id(bookmark['entry_id'])
                if entry:
                    lines.append(f"[yellow]📌 {bookmark['title']}[/yellow]")
                    if bookmark['note']:
                        lines.append(f"   Note: {bookmark['note']}")
                    lines.append(f"   ID: {bookmark['entry_id']} | Category: {bookmark['category']}")
                    lines.append("")
        else:
            lines.append("[dim]No bookmarked entries[/dim]")
            lines.append("")
            lines.append("Add bookmarks with: [yellow]BOOKMARK <entry_id> [note][/yellow]")
        
        self.update_content(lines)
    
    def _display_timeline(self):
        """Display discovery timeline"""
        lines = []
        lines.append("[bold cyan]⏰ DISCOVERY TIMELINE[/bold cyan]")
        lines.append("═" * 60)
        lines.append("")
        
        if self.discovery_timeline:
            lines.append(f"[green]{len(self.discovery_timeline)} timeline events:[/green]")
            lines.append("")
            
            for i, event in enumerate(self.discovery_timeline[-10:]):  # Last 10 events
                timestamp = time.strftime("%H:%M:%S", time.localtime(event['timestamp']))
                significance = event['significance']
                significance_bar = "●" * min(5, int(significance)) + "○" * max(0, 5 - int(significance))
                
                lines.append(f"[yellow]{timestamp}[/yellow] - {event['title']}")
                lines.append(f"   Significance: {significance_bar} ({significance:.1f})")
                lines.append(f"   Entry: {event['entry_id']} | Category: {event['category']}")
                lines.append("")
        else:
            lines.append("[dim]No timeline events recorded[/dim]")
            lines.append("")
            lines.append("Timeline events are automatically created for discoveries")
        
        self.update_content(lines)
    
    def _display_statistics(self):
        """Display database statistics and analytics"""
        lines = []
        lines.append("[bold cyan]📊 DATABASE STATISTICS[/bold cyan]")
        lines.append("═" * 60)
        lines.append("")
        
        total_entries = len(self.log_entries)
        total_bookmarks = len(self.bookmarks)
        total_cross_refs = sum(len(refs) for refs in self.cross_references.values())
        
        lines.append(f"[yellow]Total Entries:[/yellow] {total_entries}")
        lines.append(f"[yellow]Bookmarks:[/yellow] {total_bookmarks}")
        lines.append(f"[yellow]Cross-references:[/yellow] {total_cross_refs}")
        lines.append(f"[yellow]Timeline Events:[/yellow] {len(self.discovery_timeline)}")
        lines.append("")
        
        # Category breakdown
        lines.append("[cyan]═══ CATEGORY BREAKDOWN ═══[/cyan]")
        for cat_id, cat_info in self.log_categories.items():
            count = len([e for e in self.log_entries if e['category'] == cat_id])
            percentage = (count / total_entries * 100) if total_entries > 0 else 0
            bar_length = int(percentage / 5)  # 20 char max bar
            bar = "█" * bar_length + "░" * (20 - bar_length)
            
            icon = cat_info['icon']
            name = cat_info['name']
            color = cat_info['color']
            lines.append(f"[{color}]{icon} {name:12}[/{color}] │{bar}│ {count:3d} ({percentage:5.1f}%)")
        
        lines.append("")
        
        # Cross-reference analysis
        lines.append("[cyan]═══ CROSS-REFERENCE ANALYSIS ═══[/cyan]")
        for ref_type, refs in self.cross_references.items():
            lines.append(f"[yellow]{ref_type.title()}:[/yellow] {len(refs)} linked entries")
        
        lines.append("")
        
        # Export options
        lines.append("[cyan]═══ EXPORT OPTIONS ═══[/cyan]")
        lines.append("[green]Available Exports:[/green]")
        lines.append("• [yellow]EXPORT text[/yellow] - Plain text format")
        lines.append("• [yellow]EXPORT json[/yellow] - JSON data format")
        lines.append("• [yellow]EXPORT timeline[/yellow] - Timeline only")
        lines.append("• [yellow]EXPORT bookmarks[/yellow] - Bookmarked entries only")
        
        self.update_content(lines)
    
    def _format_entry_summary(self, entry: Dict[str, Any]) -> List[str]:
        """Format an entry for summary display"""
        lines = []
        
        # Get category info
        cat_info = self.log_categories.get(entry['category'], {'icon': '📄', 'color': 'white'})
        
        # Format timestamp
        timestamp = time.strftime("%H:%M:%S", time.localtime(entry['timestamp']))
        
        # Simple manual escaping for problematic characters
        def safe_escape(text):
            return text.replace('[', '\\[').replace(']', '\\]')
        
        safe_title = safe_escape(entry['title'])
        
        # Title line with category icon and timestamp
        title_line = f"{cat_info['icon']} [{cat_info['color']}]{safe_title}[/{cat_info['color']}] [dim]({timestamp})[/dim]"
        lines.append(title_line)
        
        # Content preview (first 100 chars) - escape markup
        content_preview = safe_escape(entry['content'][:100])
        if len(entry['content']) > 100:
            content_preview += "..."
        lines.append(f"   {content_preview}")
        
        # Metadata line
        metadata_parts = []
        metadata_parts.append(f"ID: {entry['id']}")
        
        if entry.get('tags'):
            metadata_parts.append(f"Tags: {', '.join(entry['tags'])}")
        
        if entry['metadata'].get('signal_refs'):
            metadata_parts.append(f"Signals: {len(entry['metadata']['signal_refs'])}")
        
        if metadata_parts:
            lines.append(f"   [dim]{' | '.join(metadata_parts)}[/dim]")
        
        return lines
    
    def _find_entry_by_id(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Find an entry by its ID"""
        for entry in self.log_entries:
            if entry['id'] == entry_id:
                return entry
        return None
    
    def export_data(self, format_type: str = "text", filter_type: str = "all") -> str:
        """Export database in various formats"""
        if format_type == "json":
            import json
            export_data = {
                'entries': self.log_entries,
                'bookmarks': self.bookmarks,
                'cross_references': self.cross_references,
                'timeline': self.discovery_timeline,
                'export_timestamp': time.time()
            }
            return json.dumps(export_data, indent=2)
        
        elif format_type == "timeline":
            lines = ["DISCOVERY TIMELINE EXPORT\n", "=" * 40, ""]
            for event in self.discovery_timeline:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(event['timestamp']))
                lines.append(f"{timestamp} - {event['title']}")
                lines.append(f"  Significance: {event['significance']:.1f}")
                lines.append(f"  Entry ID: {event['entry_id']}")
                lines.append("")
            return "\n".join(lines)
        
        elif format_type == "bookmarks":
            lines = ["BOOKMARKED ENTRIES EXPORT\n", "=" * 40, ""]
            for bookmark in self.bookmarks:
                entry = self._find_entry_by_id(bookmark['entry_id'])
                if entry:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(entry['timestamp']))
                    lines.append(f"BOOKMARK: {bookmark['title']}")
                    lines.append(f"Timestamp: {timestamp}")
                    lines.append(f"Note: {bookmark['note']}")
                    lines.append(f"Content: {entry['content']}")
                    lines.append("")
            return "\n".join(lines)
        
        else:  # Default text format
            lines = ["CAPTAIN'S LOG DATABASE EXPORT\n", "=" * 50, ""]
            lines.append(f"Export Date: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
            lines.append(f"Total Entries: {len(self.log_entries)}")
            lines.append("")
            
            for entry in self.log_entries:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(entry['timestamp']))
                cat_info = self.log_categories.get(entry['category'], {'name': 'Unknown'})
                
                lines.append(f"ENTRY: {entry['id']}")
                lines.append(f"Title: {entry['title']}")
                lines.append(f"Timestamp: {timestamp}")
                lines.append(f"Category: {cat_info['name']}")
                lines.append(f"Content: {entry['content']}")
                
                if entry.get('tags'):
                    lines.append(f"Tags: {', '.join(entry['tags'])}")
                
                lines.append("")
            
            return "\n".join(lines)
    
    def clear_logs(self):
        """Clear all log entries (with confirmation)"""
        self.log_entries = []
        self.bookmarks = []
        self.cross_references = {}
        self.discovery_timeline = []
        self._add_initial_entries()
        
    def get_database_summary(self) -> Dict[str, Any]:
        """Get comprehensive database summary"""
        return {
            'total_entries': len(self.log_entries),
            'total_bookmarks': len(self.bookmarks),
            'category_counts': {cat: len([e for e in self.log_entries if e['category'] == cat]) 
                              for cat in self.log_categories.keys()},
            'cross_reference_counts': {ref_type: len(refs) for ref_type, refs in self.cross_references.items()},
            'timeline_events': len(self.discovery_timeline),
            'current_view': self.current_view,
            'search_filter': self.search_filter,
            'category_filter': self.category_filter
        }

class ScrollablePane(ScrollableContainer):
    """Scrollable pane base class for content that needs scrolling"""
    
    def __init__(self, title: str, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.content_lines = []
        self.can_focus = True
    
    def compose(self) -> ComposeResult:
        """Compose the scrollable pane with content"""
        yield Static(self._get_content(), id=f"{self.id}_content")
    
    def _get_content(self) -> str:
        """Get the current content as a string"""
        content = f"[bold cyan]{self.title}[/bold cyan]\n"
        if self.content_lines:
            content += "\n".join(self.content_lines)
        else:
            content += "[dim]No data[/dim]"
        return content
    
    def update_content(self, lines: List[str]):
        """Update the content of this scrollable pane"""
        self.content_lines = lines[:]
        content_widget = self.query_one(f"#{self.id}_content")
        if content_widget:
            content_widget.update(self._get_content())
