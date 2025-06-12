"""
Substitution Cipher Puzzle for The Signal Cartographer
Players decode substitution ciphers with custom alphabet mappings
"""

from typing import Any, Dict, List, Tuple, Optional
import random
import time

from ..puzzle_base import BasePuzzle, PuzzleResult, PuzzleDifficulty, generate_puzzle_id
from .cipher_library import CipherLibrary, CipherData
from .cipher_tools import CipherTools, FrequencyAnalyzer


class SubstitutionCipherPuzzle(BasePuzzle):
    """
    Substitution cipher puzzle where players identify alphabet mappings
    and decode encrypted messages
    """
    
    def __init__(self, 
                 difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL,
                 signal_data: Any = None,
                 puzzle_variant: str = "decode"):
        """
        Initialize substitution cipher puzzle
        
        Args:
            difficulty: Puzzle difficulty level
            signal_data: Associated signal data
            puzzle_variant: Type of puzzle (decode, mapping_find, frequency_analysis)
        """
        
        self.cipher_library = CipherLibrary()
        self.cipher_tools = CipherTools()
        self.frequency_analyzer = FrequencyAnalyzer()
        self.puzzle_variant = puzzle_variant
        self.target_cipher: Optional[CipherData] = None
        self.correct_mapping: Dict[str, str] = {}
        self.choices: List[str] = []
        self.substitution_hints: Dict[str, List[str]] = {}
        
        # Calculate difficulty parameters
        max_attempts = max(3, 6 - difficulty.value)
        time_limit = None
        if difficulty.value >= 3:
            time_limit = 400 - (difficulty.value - 3) * 80  # 400, 320, 240, 160 seconds
        
        super().__init__(
            puzzle_id=generate_puzzle_id(),
            name=f"Substitution Cipher {puzzle_variant.title()}",
            description=f"Decode substitution cipher using frequency analysis",
            difficulty=difficulty,
            max_attempts=max_attempts,
            time_limit=time_limit,
            signal_data=signal_data
        )
    
    def _initialize_puzzle(self) -> None:
        """Initialize the substitution cipher puzzle"""
        # Select or generate cipher based on difficulty
        difficulty_range = self._get_difficulty_range()
        
        # Try to get existing cipher first
        available_ciphers = self.cipher_library.get_ciphers_by_type("substitution")
        suitable_ciphers = [c for c in available_ciphers if difficulty_range[0] <= c.difficulty <= difficulty_range[1]]
        
        if suitable_ciphers and random.choice([True, False]):
            # Use existing cipher
            self.target_cipher = random.choice(suitable_ciphers)
        else:
            # Generate new cipher
            self.target_cipher = self.cipher_library.generate_cipher_puzzle(
                "substitution", 
                self.difficulty.value,
                self._select_text_category()
            )
        
        self.correct_mapping = eval(self.target_cipher.key)
        
        # Generate analysis data
        self._generate_analysis_data()
        
        # Set solution based on variant
        if self.puzzle_variant == "decode":
            self.solution = self.target_cipher.sample_text
        elif self.puzzle_variant == "mapping_find":
            # Show one specific letter mapping as solution
            self.solution = self._select_key_mapping()
        else:  # frequency_analysis
            self.solution = self.target_cipher.sample_text
        
        # Generate choices
        self._generate_choices()
        
        # Add hints
        self._generate_hints()
        
        # Calculate max score
        self.max_score = 800 + (self.difficulty.value - 1) * 400
    
    def _get_difficulty_range(self) -> Tuple[int, int]:
        """Get cipher difficulty range based on puzzle difficulty"""
        if self.difficulty == PuzzleDifficulty.TRIVIAL:
            return (1, 2)
        elif self.difficulty == PuzzleDifficulty.EASY:
            return (2, 3)
        elif self.difficulty == PuzzleDifficulty.NORMAL:
            return (3, 4)
        elif self.difficulty == PuzzleDifficulty.HARD:
            return (4, 5)
        else:  # EXPERT, NIGHTMARE
            return (4, 5)
    
    def _select_text_category(self) -> str:
        """Select appropriate text category based on difficulty"""
        categories = ["simple_messages", "technical_logs", "alien_transmissions", "lore_fragments"]
        
        if self.difficulty.value <= 2:
            return random.choice(["technical_logs", "alien_transmissions"])
        else:
            return random.choice(categories)
    
    def _generate_analysis_data(self):
        """Generate cryptographic analysis data for the puzzle"""
        ciphertext = self.target_cipher.encrypted_text
        
        # Frequency analysis
        freq_data = self.frequency_analyzer.analyze_text(ciphertext)
        
        # Substitution suggestions
        self.substitution_hints = self.frequency_analyzer.suggest_substitutions(ciphertext)
        
        # Store analysis for hints
        self.current_progress['frequency_data'] = freq_data
        self.current_progress['substitution_hints'] = self.substitution_hints
        self.current_progress['ciphertext_length'] = len(ciphertext.replace(' ', ''))
    
    def _select_key_mapping(self) -> str:
        """Select a key letter mapping to test"""
        # Find the most frequent cipher letter
        freq_data = self.current_progress.get('frequency_data')
        if freq_data:
            sorted_freqs = sorted(freq_data.letter_frequencies.items(), 
                                key=lambda x: x[1], reverse=True)
            if sorted_freqs:
                cipher_letter = sorted_freqs[0][0]
                plain_letter = self.correct_mapping.get(cipher_letter, cipher_letter)
                return f"{cipher_letter}→{plain_letter}"
        
        # Fallback
        return "E→T"
    
    def _generate_choices(self):
        """Generate choices based on puzzle variant"""
        if self.puzzle_variant == "decode":
            # Choices are different decoded messages
            self.choices = [self.target_cipher.sample_text]
            
            # Add incorrect decodings with wrong mappings
            wrong_mappings = self._generate_wrong_mappings()
            for wrong_mapping in wrong_mappings[:4]:
                try:
                    wrong_decoded = self.cipher_library.decrypt_text(
                        self.target_cipher.encrypted_text, "substitution", str(wrong_mapping)
                    )
                    self.choices.append(wrong_decoded)
                except:
                    # Fallback to partial decoding
                    self.choices.append("GARBLED MESSAGE WITH ERRORS")
        
        elif self.puzzle_variant == "mapping_find":
            # Choices are letter mappings
            self.choices = [self.solution]  # Correct mapping
            
            # Add wrong mappings for the same cipher letter
            target_cipher_letter = self.solution.split('→')[0]
            correct_plain_letter = self.solution.split('→')[1]
            
            other_letters = [chr(65 + i) for i in range(26) if chr(65 + i) != correct_plain_letter]
            for wrong_letter in random.sample(other_letters, min(4, len(other_letters))):
                self.choices.append(f"{target_cipher_letter}→{wrong_letter}")
        
        else:  # frequency_analysis variant
            # Choices are decoded messages using frequency suggestions
            self.choices = [self.target_cipher.sample_text]
            
            # Add decodings using frequency analysis suggestions
            for i in range(4):
                # Create partial mapping based on frequency suggestions
                partial_mapping = {}
                for cipher_char, suggestions in self.substitution_hints.items():
                    if suggestions:
                        # Use different suggestions for wrong choices
                        suggestion_index = min(i, len(suggestions) - 1)
                        partial_mapping[cipher_char] = suggestions[suggestion_index]
                
                # Apply partial mapping
                try:
                    partial_decoded = ""
                    for char in self.target_cipher.encrypted_text:
                        if char.upper() in partial_mapping:
                            mapped = partial_mapping[char.upper()]
                            partial_decoded += mapped if char.isupper() else mapped.lower()
                        else:
                            partial_decoded += char
                    self.choices.append(partial_decoded)
                except:
                    self.choices.append("PARTIAL FREQUENCY ANALYSIS RESULT")
        
        # Shuffle choices and create mapping
        random.shuffle(self.choices)
        self.choice_mapping = {str(i+1): choice for i, choice in enumerate(self.choices)}
    
    def _generate_wrong_mappings(self) -> List[Dict[str, str]]:
        """Generate plausible wrong substitution mappings"""
        wrong_mappings = []
        
        # Create variations of the correct mapping
        for i in range(5):
            wrong_mapping = self.correct_mapping.copy()
            
            # Swap a few letter mappings
            letters = list(wrong_mapping.keys())
            for j in range(min(3, len(letters) // 3)):
                if len(letters) >= 2:
                    letter1, letter2 = random.sample(letters, 2)
                    # Swap their mappings
                    wrong_mapping[letter1], wrong_mapping[letter2] = \
                        wrong_mapping[letter2], wrong_mapping[letter1]
            
            wrong_mappings.append(wrong_mapping)
        
        return wrong_mappings
    
    def _generate_hints(self):
        """Generate hints for the puzzle"""
        if not self.target_cipher:
            return
        
        # Hint 1: Basic cipher info
        ciphertext_len = self.current_progress.get('ciphertext_length', 0)
        self.add_hint(1, f"Substitution cipher with {ciphertext_len} characters - use frequency analysis", 50)
        
        # Hint 2: Most frequent cipher letters
        freq_data = self.current_progress.get('frequency_data')
        if freq_data and self.puzzle_variant != "frequency_analysis":
            sorted_freqs = sorted(freq_data.letter_frequencies.items(), 
                                key=lambda x: x[1], reverse=True)
            top3_letters = [letter for letter, freq in sorted_freqs[:3]]
            self.add_hint(2, f"Most frequent cipher letters: {', '.join(top3_letters)}", 100)
        
        # Hint 3: Specific letter mapping
        if self.difficulty.value >= 3:
            # Give away one letter mapping
            freq_data = self.current_progress.get('frequency_data')
            if freq_data:
                sorted_freqs = sorted(freq_data.letter_frequencies.items(), 
                                    key=lambda x: x[1], reverse=True)
                if sorted_freqs:
                    cipher_letter = sorted_freqs[0][0]
                    plain_letter = self.correct_mapping.get(cipher_letter, cipher_letter)
                    self.add_hint(3, f"Letter mapping hint: {cipher_letter} → {plain_letter}", 150)
        
        # Hint 4: Text category hint
        if self.difficulty.value >= 4:
            category = self.target_cipher.metadata.get('category', 'unknown')
            self.add_hint(4, f"Message appears to be from '{category}' category", 200)
        
        # Hint 5: Multiple letter mappings
        if self.difficulty.value >= 4:
            # Give away 3 letter mappings
            freq_data = self.current_progress.get('frequency_data')
            if freq_data:
                sorted_freqs = sorted(freq_data.letter_frequencies.items(), 
                                    key=lambda x: x[1], reverse=True)
                mappings = []
                for cipher_letter, freq in sorted_freqs[:3]:
                    plain_letter = self.correct_mapping.get(cipher_letter, cipher_letter)
                    mappings.append(f"{cipher_letter}→{plain_letter}")
                self.add_hint(5, f"Key mappings: {', '.join(mappings)}", 300)
    
    def validate_input(self, player_input: str) -> Tuple[bool, str]:
        """Validate player's cipher solution"""
        player_input = player_input.strip()
        
        # Check multiple choice number
        if player_input.isdigit():
            choice_num = player_input
            if choice_num in self.choice_mapping:
                selected_answer = self.choice_mapping[choice_num]
                
                if self.puzzle_variant == "mapping_find":
                    # Compare letter mappings
                    if selected_answer == self.solution:
                        return True, f"Correct! {self.solution} is the right mapping!"
                    else:
                        return False, f"Mapping {selected_answer} is incorrect."
                else:
                    # Compare decoded messages
                    if selected_answer.upper() == self.solution.upper():
                        return True, f"Excellent! You've decoded the substitution cipher!"
                    else:
                        return False, f"Incorrect decoding. This doesn't match the original message."
            else:
                return False, f"Invalid choice. Please select 1-{len(self.choices)}."
        
        # Check direct input
        if self.puzzle_variant == "mapping_find":
            # Direct mapping input (format: A→B)
            if '→' in player_input or '->' in player_input:
                # Normalize arrow format
                mapping_input = player_input.replace('->', '→').upper()
                if mapping_input == self.solution:
                    return True, f"Perfect! {self.solution} is correct!"
                else:
                    return False, f"Mapping {mapping_input} is not correct."
            else:
                return False, "Please use format: CIPHER_LETTER→PLAIN_LETTER (e.g., A→E)"
        else:
            # Direct message input
            if player_input.upper() == self.solution.upper():
                return True, f"Outstanding! You've cracked the substitution cipher!"
            elif player_input.upper() in self.solution.upper():
                return False, f"Partially correct - you have part of the message."
            else:
                return False, f"Incorrect decoding. Use frequency analysis to find letter mappings."
    
    def get_current_display(self) -> List[str]:
        """Get the current puzzle display"""
        lines = []
        
        # Header
        lines.append(f"[bold cyan]🔐 SUBSTITUTION CIPHER PUZZLE[/bold cyan]")
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
        lines.append("[cyan]═══ FREQUENCY ANALYSIS ═══[/cyan]")
        freq_data = self.current_progress.get('frequency_data')
        if freq_data:
            # Show letter frequencies
            sorted_freqs = sorted(freq_data.letter_frequencies.items(), 
                                key=lambda x: x[1], reverse=True)
            lines.append("• Cipher letter frequencies:")
            freq_display = []
            for letter, freq in sorted_freqs[:8]:  # Top 8 most frequent
                freq_display.append(f"{letter}:{freq:.1f}%")
            lines.append(f"  {', '.join(freq_display)}")
            
            # Show English frequency reference for easier difficulties
            if self.difficulty.value <= 3:
                lines.append("• English frequency order: E, T, A, O, I, N, S, H, R...")
        
        lines.append("")
        
        # Display choices
        if self.puzzle_variant == "mapping_find":
            lines.append("[cyan]═══ LETTER MAPPING OPTIONS ═══[/cyan]")
            lines.append("Select the correct letter mapping:")
        elif self.puzzle_variant == "frequency_analysis":
            lines.append("[cyan]═══ FREQUENCY ANALYSIS RESULTS ═══[/cyan]")
            lines.append("Select the best frequency-based decoding:")
        else:
            lines.append("[cyan]═══ DECODED MESSAGE OPTIONS ═══[/cyan]")
            lines.append("Select the correctly decoded message:")
        
        for i, choice in enumerate(self.choices, 1):
            lines.append(f"[white]{i}.[/white] '{choice}'")
        
        lines.append("")
        
        # Instructions
        lines.append("[green]Instructions:[/green]")
        if self.puzzle_variant == "mapping_find":
            lines.append("• Find the correct cipher→plain letter mapping")
            lines.append(f"• Enter the number (1-{len(self.choices)}) or format: A→E")
        else:
            lines.append("• Use frequency analysis to decode the message")
            lines.append(f"• Enter the number (1-{len(self.choices)}) or type the message directly")
        lines.append("• Use [yellow]HINT[/yellow] command for frequency analysis help")
        
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
            lines.append(f"[yellow]Mapping Type:[/yellow] Full alphabet substitution")
        
        return lines
    
    def _on_puzzle_start(self) -> None:
        """Called when puzzle starts"""
        self.current_progress['puzzle_variant'] = self.puzzle_variant
        self.current_progress['correct_mapping'] = self.correct_mapping
        self.current_progress['start_time'] = time.time()
    
    def _on_puzzle_complete(self, result: PuzzleResult) -> None:
        """Called when puzzle completes"""
        self.current_progress['completion_time'] = time.time()
        self.current_progress['final_score'] = result.score
        self.current_progress['cipher_solved'] = result.success
        self.current_progress['analysis_methods_used'] = self.hints_used 