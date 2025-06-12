"""
Signal detection and management system
Handles signal generation, detection, and basic properties
"""

import random
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Signal:
    """Represents a detected signal with its properties"""
    id: str
    frequency: float
    strength: float
    modulation: str
    sector: str = ""
    stability: float = 1.0
    signature: str = ""
    decoded: bool = False


class SignalDetector:
    """
    Handles signal detection and generation for different sectors
    """
    
    def __init__(self):
        # Predefined signal data for different sectors
        self.sector_signals = {
            'ALPHA-1': [
                {
                    'base_frequency': 120.5,
                    'strength': 0.7,
                    'modulation': 'Pulsed-Echo',
                    'signature': 'ancient_beacon'
                },
                {
                    'base_frequency': 156.3,
                    'strength': 0.4,
                    'modulation': 'Phase-Shifted',
                    'signature': 'quantum_whisper'
                },
                {
                    'base_frequency': 189.1,
                    'strength': 0.8,
                    'modulation': 'Bio-Resonant',
                    'signature': 'living_echo'
                }
            ],
            'BETA-2': [
                {
                    'base_frequency': 145.7,
                    'strength': 0.6,
                    'modulation': 'Fragmented-Stream',
                    'signature': 'broken_transmission'
                },
                {
                    'base_frequency': 178.9,
                    'strength': 0.9,
                    'modulation': 'Quantum-Entangled',
                    'signature': 'twin_pulse'
                }
            ],
            'GAMMA-3': [
                {
                    'base_frequency': 167.4,
                    'strength': 0.3,
                    'modulation': 'Whisper-Code',
                    'signature': 'void_murmur'
                }
            ],
            # 🔴 NEW: DELTA-4 SECTOR - Hard difficulty with new signal types
            'DELTA-4': [
                {
                    'base_frequency': 134.2,
                    'strength': 0.5,
                    'modulation': 'Bio-Neural',
                    'signature': 'synaptic_cascade'
                },
                {
                    'base_frequency': 198.7,
                    'strength': 0.7,
                    'modulation': 'Quantum-Echo',
                    'signature': 'dimensional_rift'
                }
            ],
            # 🟣 NEW: EPSILON-5 SECTOR - Expert difficulty endgame challenge
            'EPSILON-5': [
                {
                    'base_frequency': 175.0,
                    'strength': 1.0,
                    'modulation': 'Singularity-Resonance',
                    'signature': 'apex_signal'
                }
            ]
        }
        
        # Modulation types and their characteristics (expanded with new signal types)
        self.modulation_types = {
            # Original signal types
            'Pulsed-Echo': {'stability': 0.8, 'complexity': 2, 'difficulty': 'Easy'},
            'Phase-Shifted': {'stability': 0.6, 'complexity': 3, 'difficulty': 'Easy'},
            'Bio-Resonant': {'stability': 0.9, 'complexity': 4, 'difficulty': 'Medium'},
            'Fragmented-Stream': {'stability': 0.4, 'complexity': 3, 'difficulty': 'Medium'},
            'Quantum-Entangled': {'stability': 0.7, 'complexity': 5, 'difficulty': 'Medium'},
            'Whisper-Code': {'stability': 0.5, 'complexity': 4, 'difficulty': 'Hard'},
            
            # NEW: Advanced Bio-Neural signals (living organism signatures)
            'Bio-Neural': {'stability': 0.6, 'complexity': 6, 'difficulty': 'Hard'},
            
            # NEW: Quantum-Echo signals (dimensional interference)  
            'Quantum-Echo': {'stability': 0.4, 'complexity': 7, 'difficulty': 'Hard'},
            
            # NEW: Endgame singularity signals
            'Singularity-Resonance': {'stability': 0.9, 'complexity': 9, 'difficulty': 'Expert'}
        }
    
    def scan_sector(self, sector: str, frequency_range: tuple = (100.0, 200.0)) -> List[Signal]:
        """
        Scan a sector for signals within the given frequency range
        """
        signals = []
        
        # Get predefined signals for this sector
        sector_data = self.sector_signals.get(sector, [])
        
        for i, signal_data in enumerate(sector_data):
            # Check if signal is within frequency range
            freq = signal_data['base_frequency']
            if frequency_range[0] <= freq <= frequency_range[1]:
                # Add some random variation to make each scan unique
                freq_variation = random.uniform(-2.0, 2.0)
                strength_variation = random.uniform(-0.1, 0.1)
                
                signal = Signal(
                    id=f"SIG_{i+1}",
                    frequency=freq + freq_variation,
                    strength=max(0.1, min(1.0, signal_data['strength'] + strength_variation)),
                    modulation=signal_data['modulation'],
                    sector=sector,
                    stability=self.modulation_types[signal_data['modulation']]['stability'],
                    signature=signal_data['signature']
                )
                
                signals.append(signal)
        
        # Add some random background signals occasionally
        if random.random() < 0.3:  # 30% chance of background signal
            noise_signal = self._generate_noise_signal(sector, frequency_range)
            signals.append(noise_signal)
        
        return signals
    
    def _generate_noise_signal(self, sector: str, frequency_range: tuple) -> Signal:
        """Generate a random background/noise signal"""
        frequency = random.uniform(frequency_range[0], frequency_range[1])
        strength = random.uniform(0.1, 0.4)  # Weak signals
        
        noise_modulations = ['Static-Burst', 'Cosmic-Noise', 'Solar-Interference']
        modulation = random.choice(noise_modulations)
        
        return Signal(
            id=f"NOISE_{random.randint(100, 999)}",
            frequency=frequency,
            strength=strength,
            modulation=modulation,
            sector=sector,
            stability=random.uniform(0.2, 0.6),
            signature='noise_pattern'
        )
    
    def get_signal_complexity(self, signal: Signal) -> int:
        """Get the complexity level of a signal for puzzle generation"""
        return self.modulation_types.get(signal.modulation, {}).get('complexity', 1)
    
    def apply_filter(self, signals: List[Signal], filter_type: str) -> List[Signal]:
        """Apply a filter to enhance or reduce certain signals"""
        filtered_signals = []
        
        for signal in signals:
            enhanced_signal = Signal(**signal.__dict__)  # Copy signal
            
            if filter_type == 'NOISE_REDUCTION':
                # Reduce noise signals, enhance real signals
                if signal.modulation in ['Static-Burst', 'Cosmic-Noise', 'Solar-Interference']:
                    enhanced_signal.strength *= 0.5  # Reduce noise
                else:
                    enhanced_signal.strength = min(1.0, enhanced_signal.strength * 1.2)  # Enhance signal
            
            elif filter_type == 'STABILITY_ENHANCER':
                # Improve signal stability
                enhanced_signal.stability = min(1.0, enhanced_signal.stability * 1.3)
            
            elif filter_type == 'FREQUENCY_LOCK':
                # Reduce frequency drift (represented as improved stability)
                enhanced_signal.stability = min(1.0, enhanced_signal.stability * 1.1)
            
            # Only include signals that are still strong enough to detect
            if enhanced_signal.strength > 0.1:
                filtered_signals.append(enhanced_signal)
        
        return filtered_signals
    
    def get_available_sectors(self) -> List[str]:
        """Get list of sectors that can be scanned"""
        return list(self.sector_signals.keys())
    
    def get_sector_info(self, sector: str) -> Dict[str, Any]:
        """Get information about a sector"""
        if sector not in self.sector_signals:
            return {"name": sector, "status": "Unknown", "signals": 0}
        
        signal_count = len(self.sector_signals[sector])
        
        # Determine sector characteristics based on signals
        status = "Unexplored"
        if signal_count > 0:
            status = "Active"
        if signal_count > 2:
            status = "High Activity"
        
        return {
            "name": sector,
            "status": status,
            "signals": signal_count,
            "explored": True
        }
