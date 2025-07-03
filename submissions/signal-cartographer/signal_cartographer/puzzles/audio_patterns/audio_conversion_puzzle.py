"""
Audio Conversion Puzzle for The Signal Cartographer
Players convert between different audio representations and formats
"""

from typing import Any, Dict, List, Tuple, Optional
import random
import time

from ..puzzle_base import BasePuzzle, PuzzleResult, PuzzleDifficulty, generate_puzzle_id
from .audio_library import AudioLibrary
from .audio_tools import AudioAnalyzer


class AudioConversionPuzzle(BasePuzzle):
    """
    Audio conversion puzzle where players convert between different audio formats
    """
    
    def __init__(self, 
                 difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL,
                 signal_data: Any = None,
                 conversion_type: str = "morse_to_text"):
        """
        Initialize audio conversion puzzle
        
        Args:
            difficulty: Puzzle difficulty level
            signal_data: Associated signal data
            conversion_type: Type of conversion (morse_to_text, frequency_to_note, binary_to_audio, text_to_morse)
        """
        
        self.audio_library = AudioLibrary()
        self.audio_analyzer = AudioAnalyzer()
        self.conversion_type = conversion_type
        self.source_format = ""
        self.target_format = ""
        self.source_data = ""
        self.conversion_rules: List[str] = []
        self.reference_table: Dict[str, str] = {}
        
        # Calculate difficulty parameters
        max_attempts = max(3, 6 - difficulty.value)
        time_limit = None
        if difficulty.value >= 3:
            time_limit = 360 - (difficulty.value - 3) * 60  # 360, 300, 240, 180 seconds
        
        super().__init__(
            puzzle_id=generate_puzzle_id(),
            name=f"Audio Convert - {conversion_type.replace('_', ' ').title()}",
            description=f"Convert between audio formats",
            difficulty=difficulty,
            max_attempts=max_attempts,
            time_limit=time_limit,
            signal_data=signal_data
        )
    
    def _initialize_puzzle(self) -> None:
        """Initialize the audio conversion puzzle"""
        # Generate conversion based on type and difficulty
        if self.conversion_type == "morse_to_text":
            self._generate_morse_to_text()
        elif self.conversion_type == "frequency_to_note":
            self._generate_frequency_to_note()
        elif self.conversion_type == "binary_to_audio":
            self._generate_binary_to_audio()
        elif self.conversion_type == "text_to_morse":
            self._generate_text_to_morse()
        else:
            self._generate_morse_to_text()  # Default
        
        # Generate hints
        self._generate_hints()
        
        # Calculate max score
        self.max_score = 650 + (self.difficulty.value - 1) * 325
    
    def _generate_morse_to_text(self):
        """Generate morse code to text conversion"""
        morse_map = self.audio_library.get_morse_patterns()
        
        # Create word list based on difficulty
        word_lists = {
            1: ["CAT", "DOG", "SOS", "HI", "OK"],
            2: ["HELLO", "WORLD", "SIGNAL", "AUDIO", "RADIO"],
            3: ["BEACON", "MESSAGE", "TRANSMISSION", "DECODE"]
        }
        
        level = min(self.difficulty.value // 2 + 1, 3)
        word = random.choice(word_lists[level])
        
        # Convert word to morse
        morse_parts = []
        for char in word:
            if char in morse_map:
                morse_parts.append(morse_map[char])
        
        self.source_data = " / ".join(morse_parts)  # Use / to separate letters
        self.solution = word
        
        self.source_format = "Morse Code"
        self.target_format = "Text"
        self.conversion_rules = [
            "Morse patterns separated by ' / ' represent individual letters",
            "● = dot (short signal), ■ = dash (long signal)",
            "International Morse Code standard"
        ]
        
        # Create reference table (partial for hints)
        self.reference_table = {pattern: letter for letter, pattern in morse_map.items()}
    
    def _generate_frequency_to_note(self):
        """Generate frequency to musical note conversion"""
        # Musical note frequencies (Hz)
        note_frequencies = {
            "C4": 261.63, "C#4": 277.18, "D4": 293.66, "D#4": 311.13,
            "E4": 329.63, "F4": 349.23, "F#4": 369.99, "G4": 392.00,
            "G#4": 415.30, "A4": 440.00, "A#4": 466.16, "B4": 493.88,
            "C5": 523.25, "D5": 587.33, "E5": 659.25, "F5": 698.46,
            "G5": 783.99, "A5": 880.00
        }
        
        # Select notes based on difficulty
        if self.difficulty.value <= 2:
            # Simple notes without sharps
            simple_notes = {k: v for k, v in note_frequencies.items() if "#" not in k}
            selected_notes = random.sample(list(simple_notes.keys()), min(3, len(simple_notes)))
        else:
            # Include sharps for difficulty
            selected_notes = random.sample(list(note_frequencies.keys()), min(4, len(note_frequencies)))
        
        # Create frequency sequence
        frequencies = [note_frequencies[note] for note in selected_notes]
        self.source_data = ", ".join([f"{freq:.2f} Hz" for freq in frequencies])
        self.solution = " ".join(selected_notes)
        
        self.source_format = "Frequencies"
        self.target_format = "Musical Notes"
        self.conversion_rules = [
            "Convert frequencies to standard musical note names",
            "Format: Note + Octave (e.g., A4, C#5)",
            "A4 = 440.00 Hz reference"
        ]
        
        self.reference_table = {f"{freq:.2f} Hz": note for note, freq in note_frequencies.items()}
    
    def _generate_binary_to_audio(self):
        """Generate binary to audio pattern conversion"""
        # Binary patterns representing audio characteristics
        audio_patterns = {
            "00": "Silent", "01": "Soft", "10": "Medium", "11": "Loud",
            "000": "Quiet", "001": "Low", "010": "Mid", "011": "High",
            "100": "Bass", "101": "Treble", "110": "Full", "111": "Peak"
        }
        
        # Generate binary sequence based on difficulty
        if self.difficulty.value <= 2:
            # 2-bit patterns
            patterns = ["00", "01", "10", "11"]
            sequence_length = 3 + self.difficulty.value
        else:
            # 3-bit patterns
            patterns = ["000", "001", "010", "011", "100", "101", "110", "111"]
            sequence_length = 2 + (self.difficulty.value - 2)
        
        selected_patterns = random.choices(patterns, k=sequence_length)
        self.source_data = " ".join(selected_patterns)
        
        # Convert to audio descriptions
        audio_descriptions = [audio_patterns[pattern] for pattern in selected_patterns]
        self.solution = " ".join(audio_descriptions)
        
        self.source_format = "Binary"
        self.target_format = "Audio Levels"
        self.conversion_rules = [
            "Convert binary patterns to audio level descriptions",
            "Each binary group represents audio characteristics",
            "Higher binary values = louder/stronger signals"
        ]
        
        self.reference_table = audio_patterns
    
    def _generate_text_to_morse(self):
        """Generate text to morse code conversion"""
        morse_map = self.audio_library.get_morse_patterns()
        
        # Create words based on difficulty
        word_lists = {
            1: ["HI", "SOS", "OK"],
            2: ["HELLO", "RADIO", "SIGNAL"],
            3: ["BEACON", "DECODE", "TRANSMISSION"]
        }
        
        level = min(self.difficulty.value // 2 + 1, 3)
        word = random.choice(word_lists[level])
        
        self.source_data = word
        
        # Convert to morse
        morse_parts = []
        for char in word:
            if char in morse_map:
                morse_parts.append(morse_map[char])
        
        self.solution = " / ".join(morse_parts)
        
        self.source_format = "Text"
        self.target_format = "Morse Code"
        self.conversion_rules = [
            "Convert text to International Morse Code",
            "● = dot (short), ■ = dash (long)",
            "Separate letters with ' / '"
        ]
        
        self.reference_table = morse_map
    
    def _generate_hints(self):
        """Generate hints for the puzzle"""
        # Hint 1: Conversion type
        conversion_names = {
            "morse_to_text": "Morse Code → Text",
            "frequency_to_note": "Frequency → Musical Notes",
            "binary_to_audio": "Binary → Audio Levels",
            "text_to_morse": "Text → Morse Code"
        }
        conversion_name = conversion_names.get(self.conversion_type, self.conversion_type)
        self.add_hint(1, f"Conversion: {conversion_name}", 120)
        
        # Hint 2: Conversion rules
        if self.difficulty.value >= 2:
            self.add_hint(2, f"Rule: {self.conversion_rules[0]}", 180)
        
        # Hint 3: Reference info
        if self.difficulty.value >= 3:
            reference_hints = {
                "morse_to_text": "● = dot, ■ = dash. Example: ●■ = A",
                "frequency_to_note": "A4 = 440 Hz. Octave doubles frequency.",
                "binary_to_audio": "00=Silent, 01=Soft, 10=Medium, 11=Loud",
                "text_to_morse": "A = ●■, B = ■●●●, C = ■●■●"
            }
            hint = reference_hints.get(self.conversion_type, "Check the reference table")
            self.add_hint(3, hint, 240)
        
        # Hint 4: Partial conversion
        if self.difficulty.value >= 4:
            if self.conversion_type == "morse_to_text":
                # Show first letter conversion
                first_pattern = self.source_data.split(" / ")[0]
                if first_pattern in self.reference_table:
                    first_letter = self.reference_table[first_pattern]
                    self.add_hint(4, f"First pattern '{first_pattern}' = '{first_letter}'", 300)
            elif self.conversion_type == "frequency_to_note":
                # Show first frequency conversion
                first_freq = self.source_data.split(", ")[0]
                if first_freq in self.reference_table:
                    first_note = self.reference_table[first_freq]
                    self.add_hint(4, f"First frequency {first_freq} = {first_note}", 300)
            else:
                self.add_hint(4, "Use the reference table for step-by-step conversion", 300)
        
        # Hint 5: Solution preview
        if self.difficulty.value >= 4:
            solution_parts = self.solution.split()
            if len(solution_parts) > 1:
                partial_solution = solution_parts[0] + "..."
                self.add_hint(5, f"Starts with: {partial_solution}", 400)
    
    def validate_input(self, player_input: str) -> Tuple[bool, str]:
        """Validate player's conversion"""
        player_input = player_input.strip().upper()
        expected = self.solution.upper()
        
        # Direct match
        if player_input == expected:
            return True, f"🎯 Perfect conversion! Correct answer: {self.solution}"
        
        # Remove common formatting differences
        player_cleaned = player_input.replace("  ", " ").replace(" / ", "/").replace("/", " / ")
        expected_cleaned = expected.replace("  ", " ").replace(" / ", "/").replace("/", " / ")
        
        if player_cleaned == expected_cleaned:
            return True, f"🎯 Correct! Formatting adjusted: {self.solution}"
        
        # Check partial matches for multi-part answers
        player_parts = player_input.split()
        expected_parts = expected.split()
        
        if len(player_parts) == len(expected_parts):
            correct_parts = sum(1 for p, e in zip(player_parts, expected_parts) if p == e)
            accuracy = correct_parts / len(expected_parts)
            
            if accuracy >= 0.8:
                return False, f"Very close! {correct_parts}/{len(expected_parts)} parts correct."
            elif accuracy >= 0.5:
                return False, f"Good progress! {correct_parts}/{len(expected_parts)} parts correct."
        
        # Special handling for morse code
        if self.conversion_type in ["morse_to_text", "text_to_morse"]:
            # Check character by character for morse
            if self.conversion_type == "morse_to_text":
                # Compare letters
                if len(player_input) == len(self.solution):
                    correct_chars = sum(1 for p, e in zip(player_input, self.solution) if p == e)
                    if correct_chars >= len(self.solution) * 0.7:
                        return False, f"Close! {correct_chars}/{len(self.solution)} letters correct."
        
        return False, f"Incorrect conversion. Expected: {self.solution}"
    
    def get_current_display(self) -> List[str]:
        """Get the current puzzle display"""
        lines = []
        
        # Header
        lines.append(f"[bold cyan]🔄 AUDIO CONVERSION - {self.conversion_type.replace('_', ' ').upper()}[/bold cyan]")
        lines.append("=" * 60)
        lines.append("")
        
        # Puzzle info
        lines.append(f"[yellow]Conversion:[/yellow] {self.source_format} → {self.target_format}")
        lines.append(f"[yellow]Difficulty:[/yellow] {self.difficulty.name}")
        lines.append("")
        
        # Source data
        lines.append("[cyan]═══ SOURCE DATA ═══[/cyan]")
        lines.append(f"[green]{self.source_data}[/green]")
        lines.append("")
        
        # Conversion rules
        lines.append("[cyan]═══ CONVERSION RULES ═══[/cyan]")
        for i, rule in enumerate(self.conversion_rules, 1):
            lines.append(f"[white]{i}.[/white] {rule}")
        lines.append("")
        
        # Reference table (partial based on difficulty)
        if self.difficulty.value <= 3:
            lines.append("[cyan]═══ REFERENCE TABLE ═══[/cyan]")
            
            if self.conversion_type == "morse_to_text":
                # Show sample morse patterns
                sample_patterns = ["●■", "■●●●", "■●■●", "■●●", "●"]
                sample_letters = ["A", "B", "C", "D", "E"]
                lines.append("Sample Morse Patterns:")
                for pattern, letter in zip(sample_patterns, sample_letters):
                    lines.append(f"  {pattern} = {letter}")
                    
            elif self.conversion_type == "frequency_to_note":
                # Show sample frequencies
                lines.append("Common Note Frequencies:")
                lines.append("  A4 = 440.00 Hz")
                lines.append("  C4 = 261.63 Hz")
                lines.append("  E4 = 329.63 Hz")
                lines.append("  G4 = 392.00 Hz")
                
            elif self.conversion_type == "binary_to_audio":
                # Show binary mapping
                lines.append("Binary to Audio Mapping:")
                if "00" in self.reference_table:
                    # 2-bit patterns
                    for binary, audio in [("00", "Silent"), ("01", "Soft"), ("10", "Medium"), ("11", "Loud")]:
                        lines.append(f"  {binary} = {audio}")
                else:
                    # 3-bit patterns
                    for binary, audio in list(self.reference_table.items())[:4]:
                        lines.append(f"  {binary} = {audio}")
                        
            elif self.conversion_type == "text_to_morse":
                # Show sample text to morse
                lines.append("Sample Text to Morse:")
                for letter, pattern in [("A", "●■"), ("B", "■●●●"), ("C", "■●■●"), ("D", "■●●")]:
                    lines.append(f"  {letter} = {pattern}")
            
            lines.append("")
        
        # Target format
        lines.append("[cyan]═══ CONVERT TO ═══[/cyan]")
        lines.append(f"[yellow]{self.target_format}:[/yellow] [red]???[/red]")
        lines.append("")
        
        # Instructions
        lines.append("[green]Instructions:[/green]")
        lines.append(f"• Convert the {self.source_format} data to {self.target_format}")
        lines.append("• Follow the conversion rules exactly")
        lines.append("• Use the reference table for guidance")
        if self.conversion_type == "morse_to_text":
            lines.append("• Enter letters without spaces (e.g., HELLO)")
        elif self.conversion_type == "text_to_morse":
            lines.append("• Separate morse patterns with ' / ' (e.g., ●■ / ■●●●)")
        elif self.conversion_type == "frequency_to_note":
            lines.append("• Enter notes separated by spaces (e.g., A4 C5 E4)")
        lines.append("• Use [yellow]HINT[/yellow] for conversion help")
        
        return lines
    
    def get_progress_display(self) -> List[str]:
        """Get progress indicators"""
        lines = []
        
        lines.append("[cyan]═══ CONVERSION PROGRESS ═══[/cyan]")
        lines.append(f"[yellow]Attempts:[/yellow] {self.attempts_made}/{self.max_attempts}")
        lines.append(f"[yellow]Current Score:[/yellow] {self.current_score}/{self.max_score}")
        
        if self.time_limit:
            elapsed = self._get_elapsed_time()
            remaining = max(0, self.time_limit - elapsed)
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            lines.append(f"[yellow]Time Remaining:[/yellow] {minutes:02d}:{seconds:02d}")
        
        if self.hints_used > 0:
            lines.append(f"[yellow]Conversion Tools Used:[/yellow] {self.hints_used}")
        
        lines.append(f"[yellow]Source Format:[/yellow] {self.source_format}")
        lines.append(f"[yellow]Target Format:[/yellow] {self.target_format}")
        
        # Data complexity
        source_parts = len(self.source_data.split())
        lines.append(f"[yellow]Data Elements:[/yellow] {source_parts}")
        
        # Conversion complexity
        complexity_levels = {
            "morse_to_text": "Signal Decoding",
            "frequency_to_note": "Frequency Analysis",
            "binary_to_audio": "Digital Conversion",
            "text_to_morse": "Signal Encoding"
        }
        complexity = complexity_levels.get(self.conversion_type, "Format Conversion")
        lines.append(f"[yellow]Complexity:[/yellow] {complexity}")
        
        return lines
    
    def start(self) -> bool:
        """Start the puzzle (compatibility method)"""
        return self.start_puzzle()
    
    def _on_puzzle_start(self) -> None:
        """Called when puzzle starts"""
        self.current_progress['conversion_type'] = self.conversion_type
        self.current_progress['source_data'] = self.source_data
        self.current_progress['source_format'] = self.source_format
        self.current_progress['target_format'] = self.target_format
        self.current_progress['start_time'] = time.time()
    
    def _on_puzzle_complete(self, result: PuzzleResult) -> None:
        """Called when puzzle completes"""
        self.current_progress['completion_time'] = time.time()
        self.current_progress['final_score'] = result.score
        self.current_progress['conversion_successful'] = result.success
        self.current_progress['conversion_rules'] = self.conversion_rules 