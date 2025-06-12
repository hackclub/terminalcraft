"""
Harmonic Pattern Puzzle for The Signal Cartographer
Players analyze frequency relationships and harmonic series
"""

from typing import Any, Dict, List, Tuple, Optional
import random
import time
import math

from ..puzzle_base import BasePuzzle, PuzzleResult, PuzzleDifficulty, generate_puzzle_id
from .audio_library import AudioLibrary
from .audio_tools import AudioAnalyzer


class HarmonicPatternPuzzle(BasePuzzle):
    """
    Harmonic pattern puzzle where players analyze frequency relationships and harmonic series
    """
    
    def __init__(self, 
                 difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL,
                 signal_data: Any = None,
                 harmonic_type: str = "overtone_series"):
        """
        Initialize harmonic pattern puzzle
        
        Args:
            difficulty: Puzzle difficulty level
            signal_data: Associated signal data
            harmonic_type: Type of harmonic analysis (overtone_series, chord_identification, ratio_analysis, fundamental_frequency)
        """
        
        self.audio_library = AudioLibrary()
        self.audio_analyzer = AudioAnalyzer()
        self.harmonic_type = harmonic_type
        self.fundamental_frequency = 0
        self.harmonic_frequencies: List[float] = []
        self.harmonic_pattern: List[str] = []
        self.frequency_ratios: List[float] = []
        self.pattern_description = ""
        self.missing_harmonics: List[int] = []  # Which harmonics are missing
        
        # Calculate difficulty parameters
        max_attempts = max(3, 6 - difficulty.value)
        time_limit = None
        if difficulty.value >= 3:
            time_limit = 360 - (difficulty.value - 3) * 60  # 360, 300, 240, 180 seconds
        
        super().__init__(
            puzzle_id=generate_puzzle_id(),
            name=f"Harmonic Pattern - {harmonic_type.replace('_', ' ').title()}",
            description=f"Analyze frequency relationships and harmonic series",
            difficulty=difficulty,
            max_attempts=max_attempts,
            time_limit=time_limit,
            signal_data=signal_data
        )
    
    def _initialize_puzzle(self) -> None:
        """Initialize the harmonic pattern puzzle"""
        # Generate harmonic challenge based on type and difficulty
        if self.harmonic_type == "overtone_series":
            self._generate_overtone_series()
        elif self.harmonic_type == "chord_identification":
            self._generate_chord_identification()
        elif self.harmonic_type == "ratio_analysis":
            self._generate_ratio_analysis()
        elif self.harmonic_type == "fundamental_frequency":
            self._generate_fundamental_frequency()
        else:
            self._generate_overtone_series()  # Default
        
        # Generate visual pattern
        self._create_harmonic_visualization()
        
        # Generate hints
        self._generate_hints()
        
        # Calculate max score
        self.max_score = 650 + (self.difficulty.value - 1) * 350
    
    def _generate_overtone_series(self):
        """Generate overtone series completion challenges"""
        # Choose fundamental frequency
        fundamental_options = [110, 220, 440, 330, 165]  # Musical frequencies
        self.fundamental_frequency = random.choice(fundamental_options)
        
        # Generate harmonic series (fundamental + overtones)
        harmonic_count = 6 + self.difficulty.value  # 7-12 harmonics total
        full_series = []
        for n in range(1, harmonic_count + 1):
            harmonic_freq = self.fundamental_frequency * n
            full_series.append(harmonic_freq)
        
        # Remove some harmonics based on difficulty
        missing_count = 1 + self.difficulty.value // 2
        self.missing_harmonics = random.sample(range(1, len(full_series)), missing_count)
        
        # Create the series with missing harmonics
        self.harmonic_frequencies = []
        for i, freq in enumerate(full_series):
            if i in self.missing_harmonics:
                self.harmonic_frequencies.append(0)  # Missing harmonic
            else:
                self.harmonic_frequencies.append(freq)
        
        # Calculate what's missing for the solution
        missing_freq = full_series[self.missing_harmonics[0]]  # First missing harmonic
        self.solution = str(int(missing_freq))
        
        self.pattern_description = f"Overtone series based on {self.fundamental_frequency}Hz fundamental"
    
    def _generate_chord_identification(self):
        """Generate chord identification challenges"""
        # Define chord types with frequency ratios
        chord_types = {
            1: {  # Simple triads
                "major": [1, 5/4, 3/2],  # Major triad ratios
                "minor": [1, 6/5, 3/2],  # Minor triad ratios
                "fifth": [1, 3/2]        # Perfect fifth
            },
            2: {  # Seventh chords
                "major7": [1, 5/4, 3/2, 15/8],
                "minor7": [1, 6/5, 3/2, 9/5],
                "dom7": [1, 5/4, 3/2, 9/5]
            },
            3: {  # Extended chords
                "major9": [1, 5/4, 3/2, 15/8, 9/4],
                "sus4": [1, 4/3, 3/2],
                "aug": [1, 5/4, 8/5]
            }
        }
        
        level = min(self.difficulty.value // 2 + 1, 3)
        chords = chord_types[level]
        
        # Choose a chord and fundamental
        chord_name, ratios = random.choice(list(chords.items()))
        self.fundamental_frequency = random.choice([220, 440, 330, 550])
        
        # Calculate frequencies
        self.harmonic_frequencies = []
        for ratio in ratios:
            freq = self.fundamental_frequency * ratio
            self.harmonic_frequencies.append(freq)
        
        # Remove one frequency (the challenge)
        missing_index = random.randint(0, len(self.harmonic_frequencies) - 1)
        missing_freq = self.harmonic_frequencies[missing_index]
        self.harmonic_frequencies[missing_index] = 0
        
        self.solution = chord_name
        self.pattern_description = f"Chord identification from {len(ratios)} frequency components"
    
    def _generate_ratio_analysis(self):
        """Generate frequency ratio analysis challenges"""
        # Use simple musical intervals
        interval_ratios = {
            1: {  # Simple ratios
                "octave": 2/1, "fifth": 3/2, "fourth": 4/3, "third": 5/4
            },
            2: {  # More complex
                "seventh": 16/9, "sixth": 5/3, "second": 9/8, "tritone": 45/32
            },
            3: {  # Very complex
                "ninth": 9/4, "eleventh": 11/4, "minor_seventh": 9/5, "augmented_fourth": 25/18
            }
        }
        
        level = min(self.difficulty.value // 2 + 1, 3)
        intervals = interval_ratios[level]
        
        # Choose fundamental and interval
        self.fundamental_frequency = random.choice([200, 300, 400, 500])
        interval_name, ratio = random.choice(list(intervals.items()))
        
        # Create frequency pair
        second_frequency = self.fundamental_frequency * ratio
        self.harmonic_frequencies = [self.fundamental_frequency, second_frequency]
        
        # Calculate the ratio for solution
        calculated_ratio = second_frequency / self.fundamental_frequency
        self.frequency_ratios = [calculated_ratio]
        
        self.solution = interval_name
        self.pattern_description = f"Musical interval ratio analysis: {ratio:.3f}"
    
    def _generate_fundamental_frequency(self):
        """Generate fundamental frequency detection challenges"""
        # Create harmonic series with noise and missing fundamental
        fundamental_options = [110, 165, 220, 330, 440]
        self.fundamental_frequency = random.choice(fundamental_options)
        
        # Generate only upper harmonics (missing fundamental)
        harmonic_numbers = [2, 3, 4, 5, 6, 7, 8]
        selected_harmonics = random.sample(harmonic_numbers, 4 + self.difficulty.value // 2)
        selected_harmonics.sort()
        
        self.harmonic_frequencies = []
        for n in selected_harmonics:
            harmonic_freq = self.fundamental_frequency * n
            # Add some noise
            noisy_freq = harmonic_freq + random.uniform(-5, 5)
            self.harmonic_frequencies.append(noisy_freq)
        
        self.solution = str(int(self.fundamental_frequency))
        self.pattern_description = f"Missing fundamental detection from {len(selected_harmonics)} harmonics"
    
    def _create_harmonic_visualization(self):
        """Create ASCII visualization of harmonic pattern"""
        self.harmonic_pattern = []
        
        if not self.harmonic_frequencies:
            return
        
        # Normalize frequencies for visualization
        max_freq = max(f for f in self.harmonic_frequencies if f > 0)
        min_freq = min(f for f in self.harmonic_frequencies if f > 0)
        freq_range = max_freq - min_freq if max_freq != min_freq else 1
        
        for i, freq in enumerate(self.harmonic_frequencies):
            if freq == 0:
                # Missing harmonic
                self.harmonic_pattern.append("???")
            else:
                # Visual representation of frequency
                if freq_range > 0:
                    height = int(((freq - min_freq) / freq_range) * 9) + 1
                else:
                    height = 5
                
                # Create bar chart representation
                bar = "█" * min(height, 10)
                self.harmonic_pattern.append(f"{bar} {freq:.0f}Hz")
    
    def _generate_hints(self):
        """Generate hints for the puzzle"""
        # Hint 1: Harmonic type
        self.add_hint(1, f"Analysis type: {self.harmonic_type.replace('_', ' ').title()}", 120)
        
        # Hint 2: Pattern description
        if self.difficulty.value >= 2:
            self.add_hint(2, self.pattern_description, 180)
        
        # Hint 3: Mathematical relationship
        if self.difficulty.value >= 3:
            if self.harmonic_type == "overtone_series":
                self.add_hint(3, f"Overtone series: f, 2f, 3f, 4f... where f = {self.fundamental_frequency}Hz", 250)
            elif self.harmonic_type == "chord_identification":
                self.add_hint(3, "Chords are built from specific frequency ratios", 250)
            elif self.harmonic_type == "ratio_analysis":
                f1, f2 = self.harmonic_frequencies[:2]
                self.add_hint(3, f"Ratio = {f2:.1f} / {f1:.1f} = {f2/f1:.3f}", 250)
            else:  # fundamental_frequency
                self.add_hint(3, "All harmonics are integer multiples of the fundamental", 250)
        
        # Hint 4: Specific guidance
        if self.difficulty.value >= 4:
            if self.harmonic_type == "overtone_series":
                missing_harmonic_num = self.missing_harmonics[0] + 1
                self.add_hint(4, f"Missing harmonic #{missing_harmonic_num} = {missing_harmonic_num} × {self.fundamental_frequency}Hz", 320)
            elif self.harmonic_type == "fundamental_frequency":
                gcd_hint = f"Find the greatest common divisor of the harmonics"
                self.add_hint(4, gcd_hint, 320)
            else:
                self.add_hint(4, "Analyze the mathematical relationships between frequencies", 320)
        
        # Hint 5: Direct answer
        if self.difficulty.value >= 4:
            self.add_hint(5, f"Answer: {self.solution}", 450)
    
    def validate_input(self, player_input: str) -> Tuple[bool, str]:
        """Validate player's harmonic analysis answer"""
        player_input = player_input.strip()
        
        # For frequency answers, handle numeric input
        if self.harmonic_type in ["overtone_series", "fundamental_frequency"]:
            try:
                player_freq = float(player_input)
                expected_freq = float(self.solution)
                
                # Allow for frequency tolerance (±5Hz or ±2%)
                tolerance = max(5, expected_freq * 0.02)
                if abs(player_freq - expected_freq) <= tolerance:
                    return True, f"🎯 Correct! The frequency is {expected_freq:.0f}Hz."
                else:
                    return False, f"Incorrect frequency. Expected: {expected_freq:.0f}Hz, got: {player_freq:.0f}Hz"
                    
            except ValueError:
                return False, "Please enter a valid frequency in Hz (e.g., 440)"
        
        # For chord and interval names
        elif self.harmonic_type in ["chord_identification", "ratio_analysis"]:
            player_answer = player_input.lower().replace(" ", "_")
            expected_answer = self.solution.lower()
            
            if player_answer == expected_answer:
                return True, f"🎯 Correct! The harmonic pattern is: {self.solution}"
            
            # Check for partial matches or common variations
            variations = {
                "major": ["maj", "M"],
                "minor": ["min", "m"],
                "seventh": ["7th", "7"],
                "fifth": ["5th", "5"],
                "fourth": ["4th", "4"],
                "third": ["3rd", "3"]
            }
            
            for correct, alts in variations.items():
                if correct in expected_answer and player_answer in alts:
                    return True, f"🎯 Correct! The harmonic pattern is: {self.solution}"
            
            return False, f"Incorrect. The harmonic pattern is: {self.solution}"
        
        return False, f"Incorrect. Expected: {self.solution}"
    
    def get_current_display(self) -> List[str]:
        """Get the current puzzle display"""
        lines = []
        
        # Header
        harmonic_name = self.harmonic_type.replace('_', ' ').upper()
        lines.append(f"[bold cyan]🎼 HARMONIC PATTERN - {harmonic_name}[/bold cyan]")
        lines.append("=" * 60)
        lines.append("")
        
        # Puzzle info
        lines.append(f"[yellow]Analysis Type:[/yellow] {self.harmonic_type.replace('_', ' ').title()}")
        lines.append(f"[yellow]Difficulty:[/yellow] {self.difficulty.name}")
        lines.append("")
        
        # Display harmonic data
        lines.append("[cyan]═══ HARMONIC FREQUENCIES ═══[/cyan]")
        lines.append("")
        
        for i, freq in enumerate(self.harmonic_frequencies, 1):
            if freq == 0:
                lines.append(f"Harmonic {i}: [red]??? Hz[/red] (MISSING)")
            else:
                lines.append(f"Harmonic {i}: [green]{freq:.1f} Hz[/green]")
        
        lines.append("")
        
        # Visual pattern
        if self.harmonic_pattern:
            lines.append("[cyan]═══ FREQUENCY VISUALIZATION ═══[/cyan]")
            for i, pattern in enumerate(self.harmonic_pattern, 1):
                if "???" in pattern:
                    lines.append(f"[red]{pattern}[/red]")
                else:
                    lines.append(f"[green]{pattern}[/green]")
            lines.append("")
        
        # Analysis information
        lines.append("[cyan]═══ HARMONIC ANALYSIS ═══[/cyan]")
        lines.append(f"• {self.pattern_description}")
        
        if self.harmonic_type == "overtone_series":
            lines.append(f"• Fundamental frequency: {self.fundamental_frequency}Hz")
            lines.append("• Each harmonic = n × fundamental frequency")
            
        elif self.harmonic_type == "chord_identification":
            lines.append("• Identify the chord type from frequency components")
            lines.append("• Consider the intervals between frequencies")
            
        elif self.harmonic_type == "ratio_analysis":
            if len(self.harmonic_frequencies) >= 2:
                f1, f2 = self.harmonic_frequencies[:2]
                ratio = f2 / f1
                lines.append(f"• Frequency ratio: {f2:.1f} / {f1:.1f} = {ratio:.3f}")
                lines.append("• Identify the musical interval")
                
        else:  # fundamental_frequency
            lines.append("• Find the missing fundamental frequency")
            lines.append("• All harmonics are multiples of the fundamental")
        
        lines.append("")
        
        # Instructions
        lines.append("[green]Instructions:[/green]")
        if self.harmonic_type == "overtone_series":
            lines.append("• Calculate the missing harmonic frequency")
            lines.append("• Use: harmonic = harmonic_number × fundamental")
        elif self.harmonic_type == "chord_identification":
            lines.append("• Analyze the frequency relationships")
            lines.append("• Enter the chord name (e.g., major, minor, dom7)")
        elif self.harmonic_type == "ratio_analysis":
            lines.append("• Calculate the frequency ratio")
            lines.append("• Enter the musical interval name")
        else:
            lines.append("• Find the fundamental frequency")
            lines.append("• All given frequencies are multiples of this value")
        
        lines.append("• Use [yellow]HINT[/yellow] for harmonic analysis help")
        
        return lines
    
    def get_progress_display(self) -> List[str]:
        """Get progress indicators"""
        lines = []
        
        lines.append("[cyan]═══ HARMONIC ANALYSIS PROGRESS ═══[/cyan]")
        lines.append(f"[yellow]Attempts:[/yellow] {self.attempts_made}/{self.max_attempts}")
        lines.append(f"[yellow]Current Score:[/yellow] {self.current_score}/{self.max_score}")
        
        if self.time_limit:
            elapsed = self._get_elapsed_time()
            remaining = max(0, self.time_limit - elapsed)
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            lines.append(f"[yellow]Time Remaining:[/yellow] {minutes:02d}:{seconds:02d}")
        
        if self.hints_used > 0:
            lines.append(f"[yellow]Analysis Tools Used:[/yellow] {self.hints_used}")
        
        lines.append(f"[yellow]Analysis Type:[/yellow] {self.harmonic_type.replace('_', ' ').title()}")
        lines.append(f"[yellow]Harmonics Count:[/yellow] {len(self.harmonic_frequencies)}")
        
        if self.fundamental_frequency > 0:
            lines.append(f"[yellow]Fundamental:[/yellow] {self.fundamental_frequency}Hz")
        
        # Analysis complexity
        complexity_levels = {
            "overtone_series": "Harmonic Series Analysis",
            "chord_identification": "Chord Recognition",
            "ratio_analysis": "Frequency Ratio Analysis",
            "fundamental_frequency": "Missing Fundamental Detection"
        }
        complexity = complexity_levels.get(self.harmonic_type, "Harmonic Analysis")
        lines.append(f"[yellow]Analysis Method:[/yellow] {complexity}")
        
        return lines
    
    def start(self) -> bool:
        """Start the puzzle (compatibility method)"""
        return self.start_puzzle()
    
    def _on_puzzle_start(self) -> None:
        """Called when puzzle starts"""
        self.current_progress['harmonic_type'] = self.harmonic_type
        self.current_progress['harmonic_frequencies'] = self.harmonic_frequencies
        self.current_progress['fundamental_frequency'] = self.fundamental_frequency
        self.current_progress['start_time'] = time.time()
    
    def _on_puzzle_complete(self, result: PuzzleResult) -> None:
        """Called when puzzle completes"""
        self.current_progress['completion_time'] = time.time()
        self.current_progress['final_score'] = result.score
        self.current_progress['harmonic_analyzed'] = result.success
        self.current_progress['pattern_description'] = self.pattern_description 