"""
Caesar Cipher Puzzle for The Signal Cartographer
Players decode Caesar-shifted messages using cryptographic analysis
"""

from typing import Any, Dict, List, Tuple, Optional
import random
import time

from ..puzzle_base import BasePuzzle, PuzzleResult, PuzzleDifficulty, generate_puzzle_id
from .cipher_library import CipherLibrary, CipherData
from .cipher_tools import CipherTools, FrequencyAnalyzer


class CaesarCipherPuzzle(BasePuzzle):
    """
    Caesar cipher puzzle where players identify the correct shift value
    and decode encrypted messages
    """
    
    def __init__(self, 
                 difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL,
                 signal_data: Any = None,
                 puzzle_variant: str = "decode"):
        """
        Initialize Caesar cipher puzzle
        
        Args:
            difficulty: Puzzle difficulty level
            signal_data: Associated signal data
            puzzle_variant: Type of puzzle (decode, shift_find, frequency_analysis)
        """
        
        self.cipher_library = CipherLibrary()
        self.cipher_tools = CipherTools()
        self.frequency_analyzer = FrequencyAnalyzer()
        self.puzzle_variant = puzzle_variant
        self.target_cipher: Optional[CipherData] = None
        self.correct_shift = 0
        self.choices: List[str] = []
        self.decoded_previews: Dict[int, str] = {}
        
        # Calculate difficulty parameters
        max_attempts = max(4, 8 - difficulty.value)
        time_limit = None
        if difficulty.value >= 3:
            time_limit = 240 - (difficulty.value - 3) * 40  # 240, 200, 160, 120 seconds
        
        super().__init__(
            puzzle_id=generate_puzzle_id(),
            name=f"Caesar Cipher {puzzle_variant.title()}",
            description=f"Decode Caesar cipher using cryptographic analysis",
            difficulty=difficulty,
            max_attempts=max_attempts,
            time_limit=time_limit,
            signal_data=signal_data
        )
    
    def _initialize_puzzle(self) -> None:
        """Initialize the Caesar cipher puzzle"""
        # Select or generate cipher based on difficulty
        difficulty_range = self._get_difficulty_range()
        
        # Try to get existing cipher first
        available_ciphers = self.cipher_library.get_ciphers_by_type("caesar")
        suitable_ciphers = [c for c in available_ciphers if difficulty_range[0] <= c.difficulty <= difficulty_range[1]]
        
        if suitable_ciphers and random.choice([True, False]):
            # Use existing cipher
            self.target_cipher = random.choice(suitable_ciphers)
        else:
            # Generate new cipher
            self.target_cipher = self.cipher_library.generate_cipher_puzzle(
                "caesar", 
                self.difficulty.value,
                self._select_text_category()
            )
        
        self.correct_shift = int(self.target_cipher.key)
        
        # Generate analysis data
        self._generate_analysis_data()
        
        # Set solution based on variant
        if self.puzzle_variant == "decode":
            self.solution = self.target_cipher.sample_text
        elif self.puzzle_variant == "shift_find":
            self.solution = str(self.correct_shift)
        else:  # frequency_analysis
            self.solution = self.target_cipher.sample_text
        
        # Generate choices
        self._generate_choices()
        
        # Add hints
        self._generate_hints()
        
        # Calculate max score
        self.max_score = 400 + (self.difficulty.value - 1) * 200
    
    def _get_difficulty_range(self) -> Tuple[int, int]:
        """Get cipher difficulty range based on puzzle difficulty"""
        if self.difficulty == PuzzleDifficulty.TRIVIAL:
            return (1, 2)
        elif self.difficulty == PuzzleDifficulty.EASY:
            return (1, 3)
        elif self.difficulty == PuzzleDifficulty.NORMAL:
            return (2, 4)
        elif self.difficulty == PuzzleDifficulty.HARD:
            return (3, 5)
        else:  # EXPERT, NIGHTMARE
            return (4, 5)
    
    def _select_text_category(self) -> str:
        """Select appropriate text category based on difficulty"""
        categories = ["simple_messages", "technical_logs", "alien_transmissions", "lore_fragments"]
        
        if self.difficulty.value <= 2:
            return "simple_messages"
        elif self.difficulty.value <= 3:
            return random.choice(["simple_messages", "technical_logs"])
        else:
            return random.choice(categories)
    
    def _generate_analysis_data(self):
        """Generate cryptographic analysis data for the puzzle"""
        ciphertext = self.target_cipher.encrypted_text
        
        # Brute force analysis
        brute_force_results = self.cipher_tools.brute_force_caesar(ciphertext)
        self.decoded_previews = {shift: decoded for shift, decoded, score in brute_force_results}
        
        # Frequency analysis
        suggested_shifts = self.frequency_analyzer.find_likely_caesar_shifts(ciphertext, 5)
        
        # Store analysis for hints
        self.current_progress['brute_force_top3'] = brute_force_results[:3]
        self.current_progress['frequency_analysis'] = suggested_shifts
        self.current_progress['ciphertext_length'] = len(ciphertext.replace(' ', ''))
    
    def _generate_choices(self):
        """Generate choices based on puzzle variant"""
        if self.puzzle_variant == "decode":
            # Choices are different decoded messages
            self.choices = [self.target_cipher.sample_text]
            
            # Add incorrect decodings (wrong shifts)
            wrong_shifts = []
            for i in range(1, 26):
                if i != self.correct_shift:
                    wrong_shifts.append(i)
            
            selected_wrong = random.sample(wrong_shifts, min(4, len(wrong_shifts)))
            for wrong_shift in selected_wrong:
                wrong_decoded = self.cipher_library.decrypt_text(
                    self.target_cipher.encrypted_text, "caesar", str(wrong_shift)
                )
                self.choices.append(wrong_decoded)
        
        elif self.puzzle_variant == "shift_find":
            # Choices are shift values
            self.choices = [str(self.correct_shift)]
            
            # Add nearby shift values as incorrect choices
            nearby_shifts = []
            for offset in [-3, -2, -1, 1, 2, 3]:
                wrong_shift = (self.correct_shift + offset) % 26
                if wrong_shift != self.correct_shift:
                    nearby_shifts.append(str(wrong_shift))
            
            self.choices.extend(random.sample(nearby_shifts, min(4, len(nearby_shifts))))
        
        else:  # frequency_analysis variant
            # Mix of decoded messages from frequency analysis suggestions
            suggested_shifts = self.current_progress.get('frequency_analysis', [])
            self.choices = []
            
            for shift, score in suggested_shifts[:5]:
                decoded = self.decoded_previews.get(shift, "")
                if decoded:
                    self.choices.append(decoded)
        
        # Shuffle choices and create mapping
        random.shuffle(self.choices)
        self.choice_mapping = {str(i+1): choice for i, choice in enumerate(self.choices)}
    
    def _generate_hints(self):
        """Generate hints for the puzzle"""
        if not self.target_cipher:
            return
        
        # Hint 1: Basic cipher info
        self.add_hint(1, f"This is a Caesar cipher with {len(self.target_cipher.encrypted_text)} characters", 30)
        
        # Hint 2: Frequency analysis hint
        if self.puzzle_variant != "frequency_analysis":
            suggested = self.current_progress.get('frequency_analysis', [])
            if suggested:
                top_suggestion = suggested[0][0]
                self.add_hint(2, f"Frequency analysis suggests shift {top_suggestion} as most likely", 60)
        
        # Hint 3: Show partial decoding
        if self.difficulty.value >= 3:
            preview_shift = random.choice([s for s, _ in self.current_progress.get('frequency_analysis', [(self.correct_shift, 0)])[:3]])
            preview_text = self.decoded_previews.get(preview_shift, "")[:20] + "..."
            self.add_hint(3, f"Shift {preview_shift} gives: '{preview_text}'", 90)
        
        # Hint 4: Text category hint
        if self.difficulty.value >= 4:
            category = self.target_cipher.metadata.get('category', 'unknown')
            self.add_hint(4, f"Message appears to be from '{category}' category", 120)
        
        # Hint 5: Direct answer
        if self.difficulty.value >= 4:
            if self.puzzle_variant == "shift_find":
                self.add_hint(5, f"The correct shift value is {self.correct_shift}", 150)
            else:
                self.add_hint(5, f"Decoded message: {self.target_cipher.sample_text}", 200)
    
    def validate_input(self, player_input: str) -> Tuple[bool, str]:
        """Validate player's cipher solution"""
        player_input = player_input.strip()
        
        # Check multiple choice number
        if player_input.isdigit():
            choice_num = player_input
            if choice_num in self.choice_mapping:
                selected_answer = self.choice_mapping[choice_num]
                
                if self.puzzle_variant == "shift_find":
                    # Compare shift values
                    if selected_answer == str(self.correct_shift):
                        return True, f"Correct! The Caesar shift is {self.correct_shift}!"
                    else:
                        return False, f"Incorrect. Shift {selected_answer} doesn't produce valid English."
                else:
                    # Compare decoded messages
                    if selected_answer.upper() == self.solution.upper():
                        return True, f"Excellent! You've decoded the message correctly!"
                    else:
                        return False, f"Incorrect decoding. This doesn't match the original message."
            else:
                return False, f"Invalid choice. Please select 1-{len(self.choices)}."
        
        # Check direct input
        if self.puzzle_variant == "shift_find":
            # Direct shift value input
            try:
                input_shift = int(player_input)
                if 0 <= input_shift <= 25:
                    if input_shift == self.correct_shift:
                        return True, f"Perfect! Caesar shift {input_shift} is correct!"
                    else:
                        return False, f"Shift {input_shift} is not correct. Try analyzing the frequency patterns."
                else:
                    return False, "Shift value must be between 0-25."
            except ValueError:
                return False, "Please enter a valid number for the shift value."
        else:
            # Direct message input
            if player_input.upper() == self.solution.upper():
                return True, f"Outstanding! You've decoded the Caesar cipher!"
            elif player_input.upper() in self.solution.upper():
                return False, f"Partially correct - you have part of the message."
            else:
                return False, f"Incorrect decoding. Check your shift value and try again."
    
    def get_current_display(self) -> List[str]:
        """Get the current puzzle display"""
        lines = []
        
        # Header
        lines.append(f"[bold cyan]🔐 CAESAR CIPHER PUZZLE[/bold cyan]")
        lines.append("=" * 60)
        lines.append("")
        
        # Puzzle info
        variant_desc = self.puzzle_variant.replace('_', ' ').title()
        lines.append(f"[yellow]Variant:[/yellow] {variant_desc}")
        lines.append(f"[yellow]Difficulty:[/yellow] {self.difficulty.name}")
        
        if self.target_cipher:
            lines.append(f"[yellow]Message Category:[/yellow] {self.target_cipher.metadata.get('category', 'Unknown')}")
        
        lines.append("")
        
        # Display encrypted message
        lines.append("[cyan]═══ ENCRYPTED TRANSMISSION ═══[/cyan]")
        if self.target_cipher:
            lines.append(f"'{self.target_cipher.encrypted_text}'")
        lines.append("")
        
        # Cryptographic analysis
        lines.append("[cyan]═══ CRYPTOGRAPHIC ANALYSIS ═══[/cyan]")
        ciphertext_len = self.current_progress.get('ciphertext_length', 0)
        lines.append(f"• Message length: {ciphertext_len} characters")
        lines.append(f"• Cipher type: Caesar (shift cipher)")
        lines.append(f"• Analysis method: Frequency analysis + brute force")
        
        # Show frequency analysis hints for easier difficulties
        if self.difficulty.value <= 3:
            freq_analysis = self.current_progress.get('frequency_analysis', [])
            if freq_analysis:
                top3 = freq_analysis[:3]
                shifts_str = ", ".join([str(shift) for shift, score in top3])
                lines.append(f"• Most likely shifts: {shifts_str}")
        
        lines.append("")
        
        # Display choices
        if self.puzzle_variant == "shift_find":
            lines.append("[cyan]═══ SHIFT VALUE OPTIONS ═══[/cyan]")
            lines.append("Select the correct Caesar cipher shift:")
        elif self.puzzle_variant == "decode":
            lines.append("[cyan]═══ DECODED MESSAGE OPTIONS ═══[/cyan]")
            lines.append("Select the correctly decoded message:")
        else:
            lines.append("[cyan]═══ FREQUENCY ANALYSIS RESULTS ═══[/cyan]")
            lines.append("Select the most English-like decoding:")
        
        for i, choice in enumerate(self.choices, 1):
            if self.puzzle_variant == "shift_find":
                # Show shift value with preview
                shift_val = choice
                preview = self.decoded_previews.get(int(shift_val), "")[:30] + "..."
                lines.append(f"[white]{i}.[/white] Shift {shift_val}: '{preview}'")
            else:
                # Show decoded message
                lines.append(f"[white]{i}.[/white] '{choice}'")
        
        lines.append("")
        
        # Instructions
        lines.append("[green]Instructions:[/green]")
        if self.puzzle_variant == "shift_find":
            lines.append("• Find the correct shift value (0-25)")
            lines.append(f"• Enter the number (1-{len(self.choices)}) or type shift value directly")
        else:
            lines.append("• Identify the correctly decoded English message")
            lines.append(f"• Enter the number (1-{len(self.choices)}) or type the message directly")
        lines.append("• Use [yellow]HINT[/yellow] command for cryptographic analysis help")
        
        return lines
    
    def get_progress_display(self) -> List[str]:
        """Get progress indicators"""
        lines = []
        
        lines.append("[cyan]═══ CIPHER PROGRESS ═══[/cyan]")
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
        
        # Show cryptographic analysis summary
        if hasattr(self, 'target_cipher') and self.target_cipher:
            lines.append(f"[yellow]Cipher Strength:[/yellow] {self.target_cipher.difficulty}/5")
            lines.append(f"[yellow]Key Length:[/yellow] 1 character (shift value)")
        
        return lines
    
    def _on_puzzle_start(self) -> None:
        """Called when puzzle starts"""
        self.current_progress['puzzle_variant'] = self.puzzle_variant
        self.current_progress['correct_shift'] = self.correct_shift
        self.current_progress['start_time'] = time.time()
    
    def _on_puzzle_complete(self, result: PuzzleResult) -> None:
        """Called when puzzle completes"""
        self.current_progress['completion_time'] = time.time()
        self.current_progress['final_score'] = result.score
        self.current_progress['cipher_solved'] = result.success
        self.current_progress['analysis_methods_used'] = self.hints_used 