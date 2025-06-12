"""
Audio Analysis Tools and Pattern Recognition
Provides audio pattern analysis and recognition algorithms
"""

from typing import Dict, List, Tuple, Optional, Any
import random
import math
from dataclasses import dataclass


@dataclass
class AudioAnalysisResult:
    """Data structure for audio analysis results"""
    success: bool
    pattern_type: str
    confidence: float  # 0.0 to 1.0
    decoded_message: str
    analysis_steps: List[str]
    timing_info: Dict[str, float]


class AudioAnalyzer:
    """Analyze and decode audio patterns"""
    
    def __init__(self):
        self.morse_code = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F',
            '--.': 'G', '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L',
            '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R',
            '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
            '-.--': 'Y', '--..': 'Z', '-----': '0', '.----': '1', '..---': '2',
            '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7',
            '---..': '8', '----.': '9', '_': ' '
        }
    
    def analyze_pattern(self, pattern: List[Any], pattern_type: str) -> AudioAnalysisResult:
        """Analyze an audio pattern and extract information"""
        if pattern_type == "morse":
            return self._analyze_morse_pattern(pattern)
        elif pattern_type == "rhythm":
            return self._analyze_rhythm_pattern(pattern)
        elif pattern_type == "harmonic":
            return self._analyze_harmonic_pattern(pattern)
        elif pattern_type == "pulse":
            return self._analyze_pulse_pattern(pattern)
        else:
            return AudioAnalysisResult(
                False, "unknown", 0.0, "", ["Unknown pattern type"], {}
            )
    
    def _analyze_morse_pattern(self, pattern: List[str]) -> AudioAnalysisResult:
        """Analyze morse code pattern"""
        try:
            decoded_chars = []
            analysis_steps = ["Analyzing morse code pattern"]
            confidence = 0.9
            
            for code in pattern:
                if code in self.morse_code:
                    decoded_chars.append(self.morse_code[code])
                    analysis_steps.append(f"'{code}' → '{self.morse_code[code]}'")
                else:
                    decoded_chars.append('?')
                    analysis_steps.append(f"'{code}' → unrecognized")
                    confidence *= 0.8  # Reduce confidence for unknown codes
            
            decoded_message = ''.join(decoded_chars)
            
            # Calculate timing info
            dot_count = sum(1 for code in pattern if code == '.')
            dash_count = sum(1 for code in pattern if code == '-')
            timing_info = {
                "total_symbols": len(pattern),
                "dots": dot_count,
                "dashes": dash_count,
                "estimated_duration": len(pattern) * 0.4  # Average symbol duration
            }
            
            success = confidence > 0.5
            
            return AudioAnalysisResult(
                success, "morse", confidence, decoded_message,
                analysis_steps, timing_info
            )
            
        except Exception as e:
            return AudioAnalysisResult(
                False, "morse", 0.0, "", [f"Error analyzing morse: {str(e)}"], {}
            )
    
    def _analyze_rhythm_pattern(self, pattern: List[str]) -> AudioAnalysisResult:
        """Analyze rhythm pattern"""
        try:
            analysis_steps = ["Analyzing rhythm pattern"]
            
            # Count different beat types
            short_beats = sum(1 for beat in pattern if beat == '.')
            long_beats = sum(1 for beat in pattern if beat == '-')
            rests = sum(1 for beat in pattern if beat == '_')
            
            total_beats = len(pattern)
            
            # Analyze rhythm characteristics
            if all(beat == '.' for beat in pattern):
                rhythm_type = "steady"
                confidence = 0.95
            elif short_beats > long_beats * 2:
                rhythm_type = "quick"
                confidence = 0.8
            elif long_beats > short_beats:
                rhythm_type = "slow"
                confidence = 0.8
            elif rests > 0:
                rhythm_type = "syncopated"
                confidence = 0.7
            else:
                rhythm_type = "complex"
                confidence = 0.6
            
            analysis_steps.extend([
                f"Short beats: {short_beats}",
                f"Long beats: {long_beats}",
                f"Rests: {rests}",
                f"Pattern type: {rhythm_type}"
            ])
            
            timing_info = {
                "total_beats": total_beats,
                "short_beats": short_beats,
                "long_beats": long_beats,
                "rests": rests,
                "estimated_tempo": 120  # BPM estimate
            }
            
            decoded_message = f"{rhythm_type} rhythm pattern"
            
            return AudioAnalysisResult(
                True, "rhythm", confidence, decoded_message,
                analysis_steps, timing_info
            )
            
        except Exception as e:
            return AudioAnalysisResult(
                False, "rhythm", 0.0, "", [f"Error analyzing rhythm: {str(e)}"], {}
            )
    
    def _analyze_harmonic_pattern(self, frequencies: List[float]) -> AudioAnalysisResult:
        """Analyze harmonic frequency pattern"""
        try:
            analysis_steps = ["Analyzing harmonic pattern"]
            
            if not frequencies:
                return AudioAnalysisResult(
                    False, "harmonic", 0.0, "", ["No frequencies to analyze"], {}
                )
            
            base_freq = frequencies[0]
            analysis_steps.append(f"Base frequency: {base_freq:.1f} Hz")
            
            # Analyze harmonic relationships
            harmonic_ratios = []
            for freq in frequencies[1:]:
                ratio = freq / base_freq
                harmonic_ratios.append(ratio)
                analysis_steps.append(f"{freq:.1f} Hz is {ratio:.2f}x base frequency")
            
            # Determine harmonic type
            if len(frequencies) == 1:
                harmonic_type = "fundamental"
                confidence = 0.95
            elif len(frequencies) == 2 and abs(harmonic_ratios[0] - 2.0) < 0.1:
                harmonic_type = "octave"
                confidence = 0.9
            elif len(frequencies) == 2 and abs(harmonic_ratios[0] - 1.5) < 0.1:
                harmonic_type = "perfect_fifth"
                confidence = 0.85
            elif len(frequencies) >= 3:
                # Check for major chord (1, 1.25, 1.5)
                if (len(harmonic_ratios) >= 2 and 
                    abs(harmonic_ratios[0] - 1.25) < 0.1 and
                    abs(harmonic_ratios[1] - 1.5) < 0.1):
                    harmonic_type = "major_chord"
                    confidence = 0.8
                else:
                    harmonic_type = "complex_harmonic"
                    confidence = 0.7
            else:
                harmonic_type = "unknown"
                confidence = 0.5
            
            timing_info = {
                "frequency_count": len(frequencies),
                "frequency_range": f"{min(frequencies):.1f}-{max(frequencies):.1f} Hz",
                "base_frequency": base_freq,
                "harmonic_ratios": harmonic_ratios
            }
            
            decoded_message = f"{harmonic_type} harmonic pattern"
            
            return AudioAnalysisResult(
                True, "harmonic", confidence, decoded_message,
                analysis_steps, timing_info
            )
            
        except Exception as e:
            return AudioAnalysisResult(
                False, "harmonic", 0.0, "", [f"Error analyzing harmonics: {str(e)}"], {}
            )
    
    def _analyze_pulse_pattern(self, pattern: List[str]) -> AudioAnalysisResult:
        """Analyze pulse sequence pattern"""
        try:
            analysis_steps = ["Analyzing pulse pattern"]
            
            # Count pulses and gaps
            pulse_count = sum(1 for p in pattern if p == 'P')
            gap_lengths = []
            current_gap = 0
            
            for element in pattern:
                if element.startswith('_'):
                    current_gap += len(element)
                else:
                    if current_gap > 0:
                        gap_lengths.append(current_gap)
                        current_gap = 0
            
            # Analyze timing pattern
            if len(set(gap_lengths)) <= 1:
                pulse_type = "regular"
                confidence = 0.9
            elif gap_lengths == sorted(gap_lengths):
                pulse_type = "accelerating"
                confidence = 0.8
            elif gap_lengths == sorted(gap_lengths, reverse=True):
                pulse_type = "decelerating"
                confidence = 0.8
            else:
                # Check for fibonacci-like pattern
                if len(gap_lengths) >= 3:
                    is_fibonacci = all(
                        abs(gap_lengths[i] - (gap_lengths[i-1] + gap_lengths[i-2])) <= 1
                        for i in range(2, len(gap_lengths))
                    )
                    if is_fibonacci:
                        pulse_type = "fibonacci"
                        confidence = 0.85
                    else:
                        pulse_type = "irregular"
                        confidence = 0.6
                else:
                    pulse_type = "irregular"
                    confidence = 0.6
            
            analysis_steps.extend([
                f"Total pulses: {pulse_count}",
                f"Gap pattern: {gap_lengths}",
                f"Pulse type: {pulse_type}"
            ])
            
            timing_info = {
                "pulse_count": pulse_count,
                "total_duration": len(pattern),
                "gap_lengths": gap_lengths,
                "pulse_density": pulse_count / len(pattern)
            }
            
            decoded_message = f"{pulse_type} pulse sequence"
            
            return AudioAnalysisResult(
                True, "pulse", confidence, decoded_message,
                analysis_steps, timing_info
            )
            
        except Exception as e:
            return AudioAnalysisResult(
                False, "pulse", 0.0, "", [f"Error analyzing pulses: {str(e)}"], {}
            )


class PatternRecognizer:
    """Advanced pattern recognition for audio signals"""
    
    def __init__(self):
        self.known_patterns = {}
        self.similarity_threshold = 0.8
        
    def add_known_pattern(self, name: str, pattern: List[Any], pattern_type: str):
        """Add a pattern to the known pattern database"""
        self.known_patterns[name] = {
            "pattern": pattern,
            "type": pattern_type,
            "signature": self._calculate_pattern_signature(pattern)
        }
    
    def recognize_pattern(self, pattern: List[Any], pattern_type: str) -> Tuple[Optional[str], float]:
        """Recognize a pattern against known patterns"""
        best_match = None
        best_similarity = 0.0
        
        pattern_signature = self._calculate_pattern_signature(pattern)
        
        for name, known_pattern in self.known_patterns.items():
            if known_pattern["type"] != pattern_type:
                continue
                
            similarity = self._calculate_similarity(
                pattern_signature, known_pattern["signature"]
            )
            
            if similarity > best_similarity and similarity > self.similarity_threshold:
                best_similarity = similarity
                best_match = name
        
        return best_match, best_similarity
    
    def _calculate_pattern_signature(self, pattern: List[Any]) -> str:
        """Calculate a signature for pattern comparison"""
        # Convert pattern to normalized string representation
        signature_parts = []
        
        for element in pattern:
            if isinstance(element, str):
                signature_parts.append(element)
            elif isinstance(element, (int, float)):
                # Normalize numbers to rough categories
                if element < 1:
                    signature_parts.append("low")
                elif element < 10:
                    signature_parts.append("med")
                else:
                    signature_parts.append("high")
            else:
                signature_parts.append("?")
        
        return "".join(signature_parts)
    
    def _calculate_similarity(self, sig1: str, sig2: str) -> float:
        """Calculate similarity between two pattern signatures"""
        if not sig1 or not sig2:
            return 0.0
        
        # Simple Levenshtein-like distance
        max_len = max(len(sig1), len(sig2))
        min_len = min(len(sig1), len(sig2))
        
        # Count matching characters at same positions
        matches = sum(1 for i in range(min_len) if sig1[i] == sig2[i])
        
        # Penalize length differences
        length_penalty = abs(len(sig1) - len(sig2)) / max_len
        
        similarity = (matches / max_len) - length_penalty
        return max(0.0, min(1.0, similarity))
    
    def suggest_pattern_completion(self, partial_pattern: List[Any], pattern_type: str) -> List[Any]:
        """Suggest completion for a partial pattern"""
        if pattern_type == "morse":
            return self._suggest_morse_completion(partial_pattern)
        elif pattern_type == "rhythm":
            return self._suggest_rhythm_completion(partial_pattern)
        elif pattern_type == "pulse":
            return self._suggest_pulse_completion(partial_pattern)
        else:
            return []
    
    def _suggest_morse_completion(self, partial: List[str]) -> List[str]:
        """Suggest morse code completion"""
        # Look for common morse patterns
        common_endings = {
            ('...', '---', '...'): ['...'],  # SOS completion
            ('.', '.'): ['-', '.', '-', '.'],  # Common letter patterns
            ('-', '-'): ['.', '.', '.']  # Balance long with short
        }
        
        # Check last few elements for patterns
        if len(partial) >= 2:
            key = tuple(partial[-2:])
            if key in common_endings:
                return common_endings[key]
        
        # Default suggestion
        return ['.', '-', '.']
    
    def _suggest_rhythm_completion(self, partial: List[str]) -> List[str]:
        """Suggest rhythm pattern completion"""
        # Analyze rhythm and suggest completion
        if not partial:
            return ['.', '.', '-', '.']
        
        # Count beat types
        short_count = sum(1 for beat in partial if beat == '.')
        long_count = sum(1 for beat in partial if beat == '-')
        
        # Try to balance the pattern
        if short_count > long_count * 2:
            return ['-', '.', '-']  # Add some long beats
        elif long_count > short_count:
            return ['.', '.', '.']  # Add short beats
        else:
            return ['.', '-', '.']  # Balanced pattern
    
    def _suggest_pulse_completion(self, partial: List[str]) -> List[str]:
        """Suggest pulse sequence completion"""
        if not partial:
            return ['P', '_', 'P', '_']
        
        # Look for pattern in gaps
        gap_pattern = []
        for element in partial:
            if element.startswith('_'):
                gap_pattern.append(len(element))
        
        if len(gap_pattern) >= 2:
            # Try to continue the gap pattern
            if gap_pattern[-1] > gap_pattern[-2]:
                # Increasing gaps
                next_gap = '_' * (gap_pattern[-1] + 1)
                return ['P', next_gap]
            else:
                # Regular or decreasing
                next_gap = '_' * gap_pattern[-1]
                return ['P', next_gap]
        
        return ['P', '_', 'P']
    
    def generate_pattern_hint(self, pattern: List[Any], pattern_type: str) -> str:
        """Generate a helpful hint for pattern recognition"""
        if pattern_type == "morse":
            dot_count = sum(1 for x in pattern if x == '.')
            dash_count = sum(1 for x in pattern if x == '-')
            return f"Pattern has {dot_count} dots and {dash_count} dashes"
        elif pattern_type == "rhythm":
            beat_count = len([x for x in pattern if x != '_'])
            return f"Rhythm has {beat_count} beats with varying durations"
        elif pattern_type == "harmonic":
            freq_count = len(pattern)
            return f"Harmonic pattern with {freq_count} frequency components"
        elif pattern_type == "pulse":
            pulse_count = sum(1 for x in pattern if x == 'P')
            return f"Pulse sequence with {pulse_count} pulses"
        else:
            return "Analyze the pattern structure for clues" 