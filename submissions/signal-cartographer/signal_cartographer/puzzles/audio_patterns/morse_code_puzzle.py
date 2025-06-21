"""
Morse Code Puzzle for The Signal Cartographer
Players decode morse code messages and patterns
"""

from typing import Any, Dict, List, Tuple, Optional
import random
import time

from ..puzzle_base import BasePuzzle, PuzzleResult, PuzzleDifficulty, generate_puzzle_id
from .audio_library import AudioLibrary, AudioPatternData
from .audio_tools import AudioAnalyzer, AudioAnalysisResult


class MorseCodePuzzle(BasePuzzle):
    """
    Morse code puzzle where players decode textual morse patterns
    into readable messages
    """
    
    def __init__(self, 
                 difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL,
                 signal_data: Any = None,
                 puzzle_variant: str = "decode"):
        """
        Initialize morse code puzzle
        
        Args:
            difficulty: Puzzle difficulty level
            signal_data: Associated signal data
            puzzle_variant: Type of puzzle (decode, encode, complete)
        """
        
        self.audio_library = AudioLibrary()
        self.audio_analyzer = AudioAnalyzer()
        self.puzzle_variant = puzzle_variant
        self.target_message = ""
        self.morse_pattern: List[str] = []
        self.ascii_visualization: List[str] = []
        self.choices: List[str] = []
        
        # Calculate difficulty parameters
        max_attempts = max(3, 6 - difficulty.value)
        time_limit = None
        if difficulty.value >= 3:
            time_limit = 240 - (difficulty.value - 3) * 40  # 240, 200, 160, 120 seconds
        
        super().__init__(
            puzzle_id=generate_puzzle_id(),
            name=f"Morse Code Analysis - {puzzle_variant.title()}",
            description=f"Decode morse code transmissions",
            difficulty=difficulty,
            max_attempts=max_attempts,
            time_limit=time_limit,
            signal_data=signal_data
        )
    
    def _initialize_puzzle(self) -> None:
        """Initialize the morse code puzzle"""
        # Select message based on difficulty and variant
        self.target_message = self._select_target_message()
        
        # Generate morse pattern
        if self.puzzle_variant == "encode":
            # Player encodes text to morse
            self.morse_pattern = []
            self.solution = " ".join(self.audio_library.text_to_morse(self.target_message))
        elif self.puzzle_variant == "complete":
            # Player completes partial morse
            full_morse = self.audio_library.text_to_morse(self.target_message)
            self.morse_pattern = self._create_partial_morse(full_morse)
            missing_part = full_morse[len(self.morse_pattern):]
            self.solution = " ".join(missing_part)
        else:  # decode
            # Player decodes morse to text
            self.morse_pattern = self.audio_library.text_to_morse(self.target_message)
            self.solution = self.target_message
        
        # Create ASCII visualization
        self.ascii_visualization = self.audio_library.morse_to_ascii(self.morse_pattern)
        
        # Generate multiple choice options
        self._generate_choices()
        
        # Generate hints
        self._generate_hints()
        
        # Calculate max score
        self.max_score = 400 + (self.difficulty.value - 1) * 200
    
    def _select_target_message(self) -> str:
        """Select appropriate message based on difficulty"""
        if self.difficulty == PuzzleDifficulty.TRIVIAL:
            messages = ["SOS", "HI", "OK", "NO", "YES"]
        elif self.difficulty == PuzzleDifficulty.EASY:
            messages = ["HELLO", "HELP", "CODE", "WAVE", "ECHO"]
        elif self.difficulty == PuzzleDifficulty.NORMAL:
            messages = ["SIGNAL", "DECODE", "PUZZLE", "AUDIO", "MORSE"]
        elif self.difficulty == PuzzleDifficulty.HARD:
            messages = ["CRYPTOGRAM", "FREQUENCY", "AMPLITUDE", "QUANTUM"]
        else:  # EXPERT, NIGHTMARE
            messages = ["ELECTROMAGNETIC", "CARTOGRAPHER", "TRANSMISSION", "INTERFERENCE"]
        
        return random.choice(messages)
    
    def _create_partial_morse(self, full_morse: List[str]) -> List[str]:
        """Create partial morse pattern for completion puzzles"""
        completion_ratio = 0.7 - (self.difficulty.value - 1) * 0.1  # 70% to 30%
        partial_length = max(1, int(len(full_morse) * completion_ratio))
        return full_morse[:partial_length]
    
    def _generate_choices(self):
        """Generate multiple choice options"""
        if self.puzzle_variant == "decode":
            # Text choices
            self.choices = [self.target_message]
            
            # Add similar words
            similar_words = self._generate_similar_words(self.target_message)
            self.choices.extend(similar_words[:3])
            
            # Add random words of similar length
            word_length = len(self.target_message)
            random_words = ["SIGNAL", "CIPHER", "DECODE", "FILTER", "PROBE", "SCAN"]
            for word in random_words:
                if (abs(len(word) - word_length) <= 2 and 
                    word not in self.choices):
                    self.choices.append(word)
                    if len(self.choices) >= 5:
                        break
        
        elif self.puzzle_variant == "encode":
            # Morse choices
            correct_morse = " ".join(self.audio_library.text_to_morse(self.target_message))
            self.choices = [correct_morse]
            
            # Add variations with common errors
            self.choices.extend(self._generate_morse_variations(correct_morse))
        
        else:  # complete
            # Completion choices
            full_morse = self.audio_library.text_to_morse(self.target_message)
            missing_part = full_morse[len(self.morse_pattern):]
            correct_completion = " ".join(missing_part)
            self.choices = [correct_completion]
            
            # Add incorrect completions
            self.choices.extend(self._generate_completion_variations(missing_part))
        
        # Shuffle and limit choices
        random.shuffle(self.choices)
        self.choices = self.choices[:4]
        
        # Create choice mapping
        self.choice_mapping = {str(i+1): choice for i, choice in enumerate(self.choices)}
    
    def _generate_similar_words(self, target: str) -> List[str]:
        """Generate words similar to target"""
        similar = []
        
        # Same length variations
        if target == "SIGNAL":
            similar = ["CIPHER", "DECODE", "FILTER"]
        elif target == "HELLO":
            similar = ["WORLD", "AUDIO", "PULSE"]
        elif target == "MORSE":
            similar = ["VOICE", "SOUND", "RADIO"]
        else:
            # Generic similar length words
            length = len(target)
            words = ["CODE", "WAVE", "BEAM", "DATA", "ECHO", "SCAN", "PROBE"]
            similar = [w for w in words if abs(len(w) - length) <= 1]
        
        return similar[:3]
    
    def _generate_morse_variations(self, correct_morse: str) -> List[str]:
        """Generate incorrect morse variations"""
        variations = []
        
        # Swap dots and dashes
        swapped = correct_morse.replace('.', 'X').replace('-', '.').replace('X', '-')
        variations.append(swapped)
        
        # Add extra symbols
        extra = correct_morse.replace(' ', ' . ')
        variations.append(extra)
        
        # Remove some symbols
        if len(correct_morse) > 3:
            shortened = correct_morse[:-2]
            variations.append(shortened)
        
        return variations[:3]
    
    def _generate_completion_variations(self, correct_completion: List[str]) -> List[str]:
        """Generate incorrect completion options"""
        variations = []
        
        # Wrong symbols
        if correct_completion:
            wrong1 = ['.', '-', '.']
            wrong2 = ['-', '-', '.']
            wrong3 = ['.', '.', '-']
            
            variations.extend([
                " ".join(wrong1),
                " ".join(wrong2),
                " ".join(wrong3)
            ])
        
        return variations[:3]
    
    def _generate_hints(self):
        """Generate hints for the puzzle"""
        # Hint 1: Basic morse code info
        if self.puzzle_variant == "decode":
            self.add_hint(1, "International morse code uses dots (.) and dashes (-)", 50)
        elif self.puzzle_variant == "encode":
            self.add_hint(1, f"Convert '{self.target_message}' to morse code", 50)
        else:
            self.add_hint(1, "Complete the morse code pattern", 50)
        
        # Hint 2: Pattern analysis
        if self.difficulty.value >= 2:
            if self.puzzle_variant == "decode":
                pattern_hint = f"Message has {len(self.target_message)} letters"
            else:
                pattern_hint = f"Pattern has {len(self.morse_pattern)} symbols"
            self.add_hint(2, pattern_hint, 100)
        
        # Hint 3: First letter/symbol
        if self.difficulty.value >= 3:
            if self.puzzle_variant == "decode":
                first_letter = self.target_message[0] if self.target_message else "?"
                first_morse = self.morse_pattern[0] if self.morse_pattern else "?"
                self.add_hint(3, f"First letter '{first_letter}' = '{first_morse}'", 150)
            else:
                hint_text = "Check morse code reference table"
                self.add_hint(3, hint_text, 150)
        
        # Hint 4: Partial solution
        if self.difficulty.value >= 4:
            if self.puzzle_variant == "decode" and len(self.target_message) > 3:
                partial = self.target_message[:len(self.target_message)//2]
                self.add_hint(4, f"First part: '{partial}'", 200)
            else:
                self.add_hint(4, "Use timing patterns: dot=short, dash=long", 200)
        
        # Hint 5: Direct answer
        if self.difficulty.value >= 4:
            self.add_hint(5, f"Answer: {self.solution}", 250)
    
    def validate_input(self, player_input: str) -> Tuple[bool, str]:
        """Validate player's answer"""
        player_input = player_input.strip().upper()
        
        # Check multiple choice number
        if player_input.isdigit() and player_input in self.choice_mapping:
            selected_choice = self.choice_mapping[player_input]
            if selected_choice.upper() == self.solution.upper():
                return True, f"📡 Correct! {self._get_success_message()}"
            else:
                return False, f"Incorrect. '{selected_choice}' is not the right answer."
        
        # Check direct input
        if player_input == self.solution.upper():
            return True, f"📡 Excellent! {self._get_success_message()}"
        
        # Check if it's a reasonable attempt for morse
        if self.puzzle_variant in ["encode", "complete"]:
            # For morse input, check pattern similarity
            similarity = self._calculate_morse_similarity(player_input, self.solution)
            if similarity > 0.8:
                return False, f"Very close! Check your dots and dashes carefully."
            elif similarity > 0.5:
                return False, f"Partially correct pattern. Review morse code rules."
        
        return False, f"Incorrect. Try again or use a hint for guidance."
    
    def _get_success_message(self) -> str:
        """Get appropriate success message"""
        if self.puzzle_variant == "decode":
            return f"Decoded '{self.solution}' successfully!"
        elif self.puzzle_variant == "encode":
            return f"Encoded '{self.target_message}' correctly!"
        else:
            return f"Completed the morse pattern!"
    
    def _calculate_morse_similarity(self, input_morse: str, correct_morse: str) -> float:
        """Calculate similarity between morse patterns"""
        # Simple character-wise comparison
        input_chars = set(input_morse.replace(' ', ''))
        correct_chars = set(correct_morse.replace(' ', ''))
        
        if not correct_chars:
            return 0.0
        
        intersection = len(input_chars & correct_chars)
        union = len(input_chars | correct_chars)
        
        return intersection / union if union > 0 else 0.0
    
    def get_current_display(self) -> List[str]:
        """Get the current puzzle display"""
        lines = []
        
        # Header
        lines.append(f"[bold cyan]📡 MORSE CODE ANALYSIS - {self.puzzle_variant.upper()}[/bold cyan]")
        lines.append("=" * 60)
        lines.append("")
        
        # Puzzle info
        lines.append(f"[yellow]Puzzle Type:[/yellow] {self.puzzle_variant.title()}")
        lines.append(f"[yellow]Difficulty:[/yellow] {self.difficulty.name}")
        if self.puzzle_variant == "decode":
            lines.append(f"[yellow]Message Length:[/yellow] {len(self.target_message)} characters")
        lines.append("")
        
        # Display morse pattern
        if self.puzzle_variant == "encode":
            lines.append("[cyan]═══ ENCODE THIS MESSAGE ═══[/cyan]")
            lines.append(f"Text: [white]{self.target_message}[/white]")
            lines.append("Convert to morse code using dots (.) and dashes (-)")
        elif self.puzzle_variant == "complete":
            lines.append("[cyan]═══ COMPLETE THE PATTERN ═══[/cyan]")
            lines.append("Partial morse code:")
            pattern_display = " ".join(self.morse_pattern)
            lines.append(f"[white]{pattern_display}[/white] [red]???[/red]")
            lines.append(f"Target message: [white]{self.target_message}[/white]")
        else:  # decode
            lines.append("[cyan]═══ DECODE THIS PATTERN ═══[/cyan]")
            pattern_display = " ".join(self.morse_pattern)
            lines.append(f"Morse: [white]{pattern_display}[/white]")
            
            # ASCII visualization for easier difficulties
            if self.difficulty.value <= 3:
                lines.append("")
                lines.append("Visual pattern:")
                ascii_display = " ".join(self.ascii_visualization)
                lines.append(f"[blue]{ascii_display}[/blue]")
        
        lines.append("")
        
        # Morse code reference (for easier difficulties)
        if self.difficulty.value <= 2:
            lines.append("[cyan]═══ MORSE CODE REFERENCE ═══[/cyan]")
            lines.append("A=.-  B=-...  C=-.-.  D=-..  E=.  F=..-.")
            lines.append("G=--.  H=....  I=..  J=.---  K=-.-  L=.-..")
            lines.append("M=--  N=-.  O=---  P=.--.  Q=--.-  R=.-.")
            lines.append("S=...  T=-  U=..-  V=...-  W=.--  X=-..-")
            lines.append("Y=-.--  Z=--..  0=-----  1=.----  2=..---")
            lines.append("")
        
        # Multiple choice options
        if self.choices:
            lines.append("[cyan]═══ ANSWER OPTIONS ═══[/cyan]")
            for i, choice in enumerate(self.choices, 1):
                lines.append(f"[white]{i}.[/white] {choice}")
            lines.append("")
        
        # Instructions
        lines.append("[green]Instructions:[/green]")
        if self.puzzle_variant == "decode":
            lines.append("• Decode the morse pattern into readable text")
        elif self.puzzle_variant == "encode":
            lines.append("• Convert the text message into morse code")
        else:
            lines.append("• Complete the partial morse code pattern")
        
        lines.append(f"• Enter the number (1-{len(self.choices)}) or type answer directly")
        lines.append("• Use [yellow]HINT[/yellow] command for morse code help")
        lines.append("• Dots (.) = short signals, Dashes (-) = long signals")
        
        return lines
    
    def get_progress_display(self) -> List[str]:
        """Get progress indicators"""
        lines = []
        
        lines.append("[cyan]═══ TRANSMISSION PROGRESS ═══[/cyan]")
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
        
        # Morse pattern analysis
        if self.morse_pattern:
            dot_count = sum(1 for symbol in self.morse_pattern if symbol == '.')
            dash_count = sum(1 for symbol in self.morse_pattern if symbol == '-')
            lines.append(f"[yellow]Pattern Analysis:[/yellow] {dot_count} dots, {dash_count} dashes")
        
        lines.append(f"[yellow]Puzzle Type:[/yellow] {self.puzzle_variant.title()}")
        
        return lines
    
    def _on_puzzle_start(self) -> None:
        """Called when puzzle starts"""
        self.current_progress['puzzle_variant'] = self.puzzle_variant
        self.current_progress['target_message'] = self.target_message
        self.current_progress['morse_pattern'] = self.morse_pattern
        self.current_progress['start_time'] = time.time()
    
    def _on_puzzle_complete(self, result: PuzzleResult) -> None:
        """Called when puzzle completes"""
        self.current_progress['completion_time'] = time.time()
        self.current_progress['final_score'] = result.score
        self.current_progress['transmission_decoded'] = result.success
        self.current_progress['analysis_methods_used'] = self.hints_used 

    def start(self) -> bool:
        """Start the puzzle (compatibility method)"""
        return self.start_puzzle() 