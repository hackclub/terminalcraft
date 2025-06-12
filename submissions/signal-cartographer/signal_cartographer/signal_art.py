"""
ASCII Art and Signal Visualization System
Generates visual representations of signals and their signatures
"""

from typing import Dict, List
import random
import math


class SignalArt:
    """Generates ASCII art for signal signatures and visualizations"""
    
    def __init__(self):
        # ASCII art patterns for different signal signatures
        self.signal_patterns = {
            'ancient_beacon': [
                "  ∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿",
                "  ∿     ◊ ◊ ◊ ◊     ∿",
                "  ∿   ◊ ∿ ∿ ∿ ∿ ◊   ∿",
                "  ∿ ◊ ∿ ◊ ▫ ▫ ◊ ∿ ◊ ∿",
                "  ∿   ◊ ∿ ∿ ∿ ∿ ◊   ∿",
                "  ∿     ◊ ◊ ◊ ◊     ∿",
                "  ∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿"
            ],
            'quantum_whisper': [
                "  ░░░░░░░░░░░░░░░░░░░░",
                "  ░ ∴ · ∴ · ∴ · ∴ ░",
                "  ░ · ∴ · ∴ · ∴ · ░",
                "  ░ ∴ · ⊙ ⊙ · ∴ · ░",
                "  ░ · ∴ · ∴ · ∴ · ░",
                "  ░ ∴ · ∴ · ∴ · ∴ ░",
                "  ░░░░░░░░░░░░░░░░░░░░"
            ],
            'living_echo': [
                "  ≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋",
                "  ≋ ♦ ♦ ♦ ♦ ♦ ♦ ♦ ≋",
                "  ≋ ♦ ❋ ❋ ❋ ❋ ❋ ♦ ≋",
                "  ≋ ♦ ❋ ● ● ● ❋ ♦ ≋",
                "  ≋ ♦ ❋ ❋ ❋ ❋ ❋ ♦ ≋",
                "  ≋ ♦ ♦ ♦ ♦ ♦ ♦ ♦ ≋",
                "  ≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋≋"
            ],
            'broken_transmission': [
                "  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓",
                "  ▓ ╱ ╲ ╱ ╲ ╱ ╲ ╱ ▓",
                "  ▓ ╲ ╱ X X ╱ ╲ ╱ ▓",
                "  ▓ ╱ X ▒ ▒ X ╱ ╲ ▓",
                "  ▓ ╲ ╱ X X ╱ ╲ ╱ ▓",
                "  ▓ ╱ ╲ ╱ ╲ ╱ ╲ ╱ ▓",
                "  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓"
            ],
            'twin_pulse': [
                "  ████████████████████",
                "  █ ⟐⟐⟐    ⟐⟐⟐ █",
                "  █ ⟐◊⟐    ⟐◊⟐ █",
                "  █ ⟐⬣⟐ ⟸⟹ ⟐⬣⟐ █",
                "  █ ⟐◊⟐    ⟐◊⟐ █",
                "  █ ⟐⟐⟐    ⟐⟐⟐ █",
                "  ████████████████████"
            ],
            'void_murmur': [
                "  ······················",
                "  · ◦ ∘ ○ ● ○ ∘ ◦ ·",
                "  · ∘ ○ ● ■ ● ○ ∘ ·",
                "  · ○ ● ■ ░ ■ ● ○ ·",
                "  · ∘ ○ ● ■ ● ○ ∘ ·",
                "  · ◦ ∘ ○ ● ○ ∘ ◦ ·",
                "  ······················"
            ],
            'noise_pattern': [
                "  ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒",
                "  ▒ · ▪ ∘ ▫ ▪ ∘ · ▒",
                "  ▒ ∘ · ▪ ∘ · ▫ ▪ ▒",
                "  ▒ ▪ ▫ · ▪ ▫ · ∘ ▒",
                "  ▒ ∘ ▪ ▫ · ▪ ∘ · ▒",
                "  ▒ · ∘ ▪ ▫ ∘ ▪ ▫ ▒",
                "  ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒"
            ]
        }
        
        # Frequency visualization characters
        self.freq_chars = ['_', '⁻', '~', '∿', '⌢', '⌣', '∩', '∪']
        
    def get_signal_signature(self, signature_type: str) -> List[str]:
        """Get ASCII art for a signal signature"""
        return self.signal_patterns.get(signature_type, self.signal_patterns['noise_pattern'])
    
    def generate_spectrum_display(self, signals: List, frequency_range: tuple) -> List[str]:
        """Generate a simple ASCII spectrum display"""
        spectrum = []
        
        # Create frequency scale
        freq_min, freq_max = frequency_range
        spectrum.append(f"  Frequency Range: {freq_min:.1f} - {freq_max:.1f} MHz")
        spectrum.append("  " + "─" * 40)
        
        # Visual representation of spectrum
        if signals:
            spectrum.append("  Signal Activity:")
            for i, signal in enumerate(signals[:8]):  # Show up to 8 signals
                strength_bar = "█" * int(signal.strength * 10) + "░" * (10 - int(signal.strength * 10))
                freq_pos = int(((signal.frequency - freq_min) / (freq_max - freq_min)) * 30)
                line = "  " + "·" * freq_pos + "▲" + "·" * (30 - freq_pos - 1)
                spectrum.append(f"  {signal.id:>6}: [{strength_bar}] {signal.frequency:6.1f} MHz")
                spectrum.append(line)
        else:
            spectrum.append("  No signals detected")
            spectrum.append("  " + "·" * 40)
        
        spectrum.append("  " + "─" * 40)
        return spectrum
    
    def generate_waveform(self, signal, width: int = 30) -> List[str]:
        """Generate a simple ASCII waveform for a signal"""
        waveform = []
        
        # Generate waveform based on signal properties
        amplitude = int(signal.strength * 5)  # Max height of 5
        stability = signal.stability
          # Create waveform pattern
        pattern = []
        for i in range(width):
            # Base wave with some variation
            base_height = amplitude * abs(math.sin(i * 0.3))
            
            # Add instability noise
            if stability < 0.7:
                noise = random.randint(-1, 1) if random.random() < (1 - stability) else 0
                base_height = max(0, min(5, base_height + noise))
            
            pattern.append(int(base_height))
        
        # Convert to ASCII
        for row in range(5, -1, -1):  # Top to bottom
            line = "  "
            for height in pattern:
                if height >= row:
                    line += "█"
                else:
                    line += " "
            waveform.append(line)
        
        return waveform
    
    def get_analysis_display(self, signal) -> List[str]:
        """Generate analysis display for a focused signal"""
        display = []
        
        display.append(f"Signal Analysis: {signal.id}")
        display.append("─" * 30)
        display.append(f"Frequency: {signal.frequency:.2f} MHz")
        display.append(f"Strength:  {signal.strength:.2f}")
        display.append(f"Stability: {signal.stability:.2f}")
        display.append(f"Type:      {signal.modulation}")
        display.append("")
        
        # Add signal signature
        display.append("Signal Signature:")
        signature_art = self.get_signal_signature(signal.signature)
        display.extend(signature_art)
        
        display.append("")
        display.append("Waveform Analysis:")
        waveform = self.generate_waveform(signal)
        display.extend(waveform)
        
        return display


class ProgressiveReveal:
    """Handles progressive revelation of signal information through analysis"""
    
    def __init__(self):
        self.analysis_stages = {
            'basic': ['frequency', 'strength'],
            'intermediate': ['modulation', 'stability'],
            'advanced': ['signature', 'decoded_data'],
            'complete': ['origin', 'message']
        }
    
    def get_revealed_info(self, signal, analysis_level: str) -> Dict[str, any]:
        """Get information revealed at a specific analysis level"""
        revealed = {}
        
        stages_to_include = []
        if analysis_level in ['basic', 'intermediate', 'advanced', 'complete']:
            stages_to_include.append('basic')
        if analysis_level in ['intermediate', 'advanced', 'complete']:
            stages_to_include.append('intermediate')
        if analysis_level in ['advanced', 'complete']:
            stages_to_include.append('advanced')
        if analysis_level == 'complete':
            stages_to_include.append('complete')
        
        for stage in stages_to_include:
            for field in self.analysis_stages[stage]:
                if hasattr(signal, field):
                    revealed[field] = getattr(signal, field)
        
        return revealed
