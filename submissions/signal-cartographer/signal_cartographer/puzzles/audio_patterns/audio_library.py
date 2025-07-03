"""
Audio Library System for Audio Pattern Puzzles
Stores audio patterns, morse code, rhythms, and pulse sequences
"""

from typing import Dict, List, Tuple, Optional, Any
import random
import string
from dataclasses import dataclass


@dataclass
class AudioPatternData:
    """Data structure for audio pattern information"""
    name: str
    pattern_type: str  # morse, rhythm, harmonic, pulse, temporal
    description: str
    difficulty: int  # 1-5
    pattern: List[Any]  # The audio pattern data
    clues: List[str]  # Available clues
    timing: Dict[str, float]  # Timing information
    metadata: Dict[str, Any]


class AudioLibrary:
    """Library of audio patterns and signal analysis data"""
    
    def __init__(self):
        self.patterns: Dict[str, AudioPatternData] = {}
        self.morse_code: Dict[str, str] = {}
        self.rhythm_patterns: Dict[str, List[str]] = {}
        self.harmonic_patterns: Dict[str, List[float]] = {}
        self.pulse_sequences: Dict[str, List[str]] = {}
        self._initialize_library()
    
    def _initialize_library(self):
        """Initialize with audio pattern data"""
        
        # International Morse Code
        self.morse_code = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
            'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
            'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
            'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
            'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
            '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
            '8': '---..', '9': '----.', ' ': '_'
        }
        
        # Rhythm patterns using dots (short), dashes (long), underscores (rest)
        self.rhythm_patterns = {
            "simple_beat": [".", ".", ".", "."],
            "complex_beat": [".", "-", ".", "_", ".", "-"],
            "syncopated": [".", "_", "-", ".", "_", ".", "-"],
            "triplet": [".", ".", ".", "-", ".", ".", "."],
            "waltz": ["-", ".", ".", "-", ".", ".", "-", ".", "."],
            "signal_pulse": [".", ".", "-", "-", ".", "_", ".", ".", "-"],
            "alien_rhythm": ["-", ".", "_", ".", "-", "_", "-", ".", "."],
            "emergency": [".", ".", ".", "_", "-", "-", "-", "_", ".", ".", "."]
        }
        
        # Harmonic patterns (frequency relationships)
        self.harmonic_patterns = {
            "fundamental": [100.0],
            "octave": [100.0, 200.0],
            "fifth": [100.0, 150.0],
            "major_chord": [100.0, 125.0, 150.0],
            "minor_chord": [100.0, 120.0, 150.0],
            "overtones": [100.0, 200.0, 300.0, 400.0, 500.0],
            "alien_harmony": [100.0, 137.5, 183.3, 244.4],
            "quantum_resonance": [100.0, 161.8, 261.8, 423.6]
        }
        
        # Pulse sequences with timing patterns
        self.pulse_sequences = {
            "regular": ["P", "_", "P", "_", "P", "_", "P", "_"],
            "accelerating": ["P", "__", "P", "_", "P", "P", "_", "P"],
            "fibonacci": ["P", "_", "P", "__", "P", "___", "P", "_____"],
            "binary": ["P", "P", "_", "P", "_", "_", "_", "P"],
            "prime": ["P", "P", "_", "P", "_", "P", "_", "_"],
            "chaotic": ["P", "___", "P", "P", "_", "P", "__", "P"],
            "decay": ["P", "_", "P", "__", "P", "___", "P", "____"],
            "signal_burst": ["P", "P", "P", "___", "P", "_", "P", "P"]
        }
        
        # Initialize sample patterns
        self._create_morse_samples()
        self._create_rhythm_samples()
        self._create_harmonic_samples()
        self._create_pulse_samples()
    
    def _create_morse_samples(self):
        """Create sample morse code patterns"""
        morse_samples = [
            ("MORSE_SOS", "SOS", "Emergency distress signal"),
            ("MORSE_HELLO", "HELLO", "Simple greeting message"),
            ("MORSE_SIGNAL", "SIGNAL", "Signal identification"),
            ("MORSE_ALIEN", "ALIEN", "Unknown origin identifier"),
            ("MORSE_QUANTUM", "QUANTUM", "Quantum physics reference")
        ]
        
        for name, text, description in morse_samples:
            morse_pattern = [self.morse_code.get(char, '_') for char in text.upper()]
            difficulty = 2 if len(text) <= 4 else 3 if len(text) <= 6 else 4
            
            self.patterns[name] = AudioPatternData(
                name=name,
                pattern_type="morse",
                description=description,
                difficulty=difficulty,
                pattern=morse_pattern,
                clues=[f"Morse code for '{text}'", "International morse standard"],
                timing={"dot_duration": 0.2, "dash_duration": 0.6, "gap_duration": 0.2},
                metadata={"text": text, "length": len(text)}
            )
    
    def _create_rhythm_samples(self):
        """Create sample rhythm patterns"""
        rhythm_samples = [
            ("RHYTHM_SIMPLE", "simple_beat", "Basic steady beat"),
            ("RHYTHM_COMPLEX", "complex_beat", "Complex rhythmic pattern"),
            ("RHYTHM_SYNC", "syncopated", "Syncopated rhythm"),
            ("RHYTHM_ALIEN", "alien_rhythm", "Unknown rhythmic signature"),
            ("RHYTHM_EMERGENCY", "emergency", "Emergency signal pattern")
        ]
        
        for name, rhythm_type, description in rhythm_samples:
            pattern = self.rhythm_patterns[rhythm_type]
            difficulty = 2 if rhythm_type in ["simple_beat", "triplet"] else 4
            
            self.patterns[name] = AudioPatternData(
                name=name,
                pattern_type="rhythm",
                description=description,
                difficulty=difficulty,
                pattern=pattern,
                clues=[f"Rhythmic pattern: {rhythm_type}", "Listen for timing"],
                timing={"beat_duration": 0.5, "measure_length": len(pattern)},
                metadata={"rhythm_type": rhythm_type, "complexity": difficulty}
            )
    
    def _create_harmonic_samples(self):
        """Create sample harmonic patterns"""
        harmonic_samples = [
            ("HARMONIC_FUNDAMENTAL", "fundamental", "Single frequency tone"),
            ("HARMONIC_OCTAVE", "octave", "Fundamental + octave"),
            ("HARMONIC_CHORD", "major_chord", "Major chord harmony"),
            ("HARMONIC_ALIEN", "alien_harmony", "Non-human harmonic series"),
            ("HARMONIC_QUANTUM", "quantum_resonance", "Quantum resonance pattern")
        ]
        
        for name, harmonic_type, description in harmonic_samples:
            frequencies = self.harmonic_patterns[harmonic_type]
            difficulty = 2 if len(frequencies) <= 2 else 4 if len(frequencies) <= 3 else 5
            
            self.patterns[name] = AudioPatternData(
                name=name,
                pattern_type="harmonic",
                description=description,
                difficulty=difficulty,
                pattern=frequencies,
                clues=[f"Harmonic series: {harmonic_type}", "Frequency relationships"],
                timing={"duration": 2.0, "fade_time": 0.5},
                metadata={"harmonic_type": harmonic_type, "frequency_count": len(frequencies)}
            )
    
    def _create_pulse_samples(self):
        """Create sample pulse sequence patterns"""
        pulse_samples = [
            ("PULSE_REGULAR", "regular", "Regular pulse sequence"),
            ("PULSE_ACCEL", "accelerating", "Accelerating pulse pattern"),
            ("PULSE_FIB", "fibonacci", "Fibonacci-timed pulses"),
            ("PULSE_BINARY", "binary", "Binary-encoded pulse"),
            ("PULSE_CHAOTIC", "chaotic", "Chaotic pulse sequence")
        ]
        
        for name, pulse_type, description in pulse_samples:
            sequence = self.pulse_sequences[pulse_type]
            difficulty = 2 if pulse_type == "regular" else 4
            
            self.patterns[name] = AudioPatternData(
                name=name,
                pattern_type="pulse",
                description=description,
                difficulty=difficulty,
                pattern=sequence,
                clues=[f"Pulse sequence: {pulse_type}", "Timing pattern analysis"],
                timing={"pulse_duration": 0.1, "sequence_length": len(sequence)},
                metadata={"pulse_type": pulse_type, "encoding": pulse_type}
            )
    
    def get_pattern(self, name: str) -> Optional[AudioPatternData]:
        """Get audio pattern by name"""
        return self.patterns.get(name)
    
    def get_patterns_by_type(self, pattern_type: str) -> List[AudioPatternData]:
        """Get all patterns of a specific type"""
        return [pattern for pattern in self.patterns.values() if pattern.pattern_type == pattern_type]
    
    def get_patterns_by_difficulty(self, difficulty: int) -> List[AudioPatternData]:
        """Get all patterns of a specific difficulty"""
        return [pattern for pattern in self.patterns.values() if pattern.difficulty == difficulty]
    
    def get_random_pattern(self, pattern_type: str = None, difficulty_range: Tuple[int, int] = (1, 5)) -> Optional[AudioPatternData]:
        """Get random pattern optionally filtered by type and difficulty"""
        valid_patterns = []
        
        for pattern in self.patterns.values():
            if pattern_type and pattern.pattern_type != pattern_type:
                continue
            if not (difficulty_range[0] <= pattern.difficulty <= difficulty_range[1]):
                continue
            valid_patterns.append(pattern)
        
        return random.choice(valid_patterns) if valid_patterns else None
    
    def text_to_morse(self, text: str) -> List[str]:
        """Convert text to morse code pattern"""
        return [self.morse_code.get(char.upper(), '_') for char in text if char.upper() in self.morse_code or char == ' ']
    
    def morse_to_text(self, morse_pattern: List[str]) -> str:
        """Convert morse code pattern to text"""
        reverse_morse = {v: k for k, v in self.morse_code.items()}
        return ''.join([reverse_morse.get(code, '?') for code in morse_pattern])
    
    def morse_to_ascii(self, morse_pattern: List[str]) -> List[str]:
        """Convert morse pattern to ASCII visualization"""
        ascii_lines = []
        for code in morse_pattern:
            if code == '.':
                ascii_lines.append("●")
            elif code == '-':
                ascii_lines.append("───")
            elif code == '_':
                ascii_lines.append("   ")
            else:
                ascii_lines.append("?")
        return ascii_lines
    
    def rhythm_to_ascii(self, rhythm_pattern: List[str]) -> List[str]:
        """Convert rhythm pattern to ASCII visualization"""
        ascii_lines = []
        for beat in rhythm_pattern:
            if beat == '.':
                ascii_lines.append("♩")  # Quarter note
            elif beat == '-':
                ascii_lines.append("♪♪")  # Eighth notes
            elif beat == '_':
                ascii_lines.append("♬")  # Rest
            else:
                ascii_lines.append("?")
        return ascii_lines
    
    def harmonic_to_ascii(self, frequencies: List[float]) -> List[str]:
        """Convert harmonic pattern to ASCII visualization"""
        ascii_lines = []
        base_freq = frequencies[0] if frequencies else 100.0
        
        for freq in frequencies:
            ratio = freq / base_freq
            height = int(ratio * 3)  # Scale for ASCII display
            ascii_lines.append("│" * height + f" {freq:.1f}Hz")
        
        return ascii_lines
    
    def pulse_to_ascii(self, pulse_pattern: List[str]) -> List[str]:
        """Convert pulse pattern to ASCII visualization"""
        ascii_lines = []
        for pulse in pulse_pattern:
            if pulse == 'P':
                ascii_lines.append("█")
            elif pulse.startswith('_'):
                ascii_lines.append("·" * len(pulse))
            else:
                ascii_lines.append("?")
        return ascii_lines
    
    def generate_audio_puzzle(self, pattern_type: str, difficulty: int) -> AudioPatternData:
        """Generate a new audio puzzle on demand"""
        puzzle_name = f"GENERATED_{pattern_type.upper()}_{random.randint(1000, 9999)}"
        
        if pattern_type == "morse":
            words = ["SIGNAL", "AUDIO", "PULSE", "WAVE", "CODE", "DATA", "ECHO", "BEAM"]
            word = random.choice(words)
            pattern = self.text_to_morse(word)
            clues = [f"Morse code message", f"Word: {len(word)} letters"]
            timing = {"dot_duration": 0.2, "dash_duration": 0.6}
            
        elif pattern_type == "rhythm":
            beats = random.choice(list(self.rhythm_patterns.keys()))
            pattern = self.rhythm_patterns[beats]
            clues = [f"Rhythmic pattern", f"Pattern type: {beats}"]
            timing = {"beat_duration": 0.5}
            
        elif pattern_type == "harmonic":
            harmonics = random.choice(list(self.harmonic_patterns.keys()))
            pattern = self.harmonic_patterns[harmonics]
            clues = [f"Harmonic series", f"Frequencies: {len(pattern)}"]
            timing = {"duration": 2.0}
            
        elif pattern_type == "pulse":
            pulses = random.choice(list(self.pulse_sequences.keys()))
            pattern = self.pulse_sequences[pulses]
            clues = [f"Pulse sequence", f"Pattern: {pulses}"]
            timing = {"pulse_duration": 0.1}
            
        else:
            pattern = ["?"]
            clues = ["Unknown pattern"]
            timing = {}
        
        return AudioPatternData(
            name=puzzle_name,
            pattern_type=pattern_type,
            description=f"Generated {pattern_type} puzzle",
            difficulty=difficulty,
            pattern=pattern,
            clues=clues,
            timing=timing,
            metadata={"category": "generated", "generated": True}
        ) 