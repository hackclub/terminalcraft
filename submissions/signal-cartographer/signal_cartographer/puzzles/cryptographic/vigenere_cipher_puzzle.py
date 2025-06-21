"""
Vigenère Cipher Puzzle for The Signal Cartographer
Players decode polyalphabetic ciphers and discover keywords
"""

from typing import Any, Dict, List, Tuple, Optional
import random
import time

from ..puzzle_base import BasePuzzle, PuzzleResult, PuzzleDifficulty, generate_puzzle_id
from .cipher_library import CipherLibrary, CipherData
from .cipher_tools import CipherTools, FrequencyAnalyzer


class VigenereCipherPuzzle(BasePuzzle):
    """
    Vigenère cipher puzzle where players identify keywords and decode
    polyalphabetic encrypted messages
    """
    
    def __init__(self, 
                 difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL,
                 signal_data: Any = None,
                 puzzle_variant: str = "decode"):
        """
        Initialize Vigenère cipher puzzle
        
        Args:
            difficulty: Puzzle difficulty level
            signal_data: Associated signal data
            puzzle_variant: Type of puzzle (decode, keyword_find, key_length)
        """
        
        self.cipher_library = CipherLibrary()
        self.cipher_tools = CipherTools()
        self.frequency_analyzer = FrequencyAnalyzer()
        self.puzzle_variant = puzzle_variant
        self.target_cipher: Optional[CipherData] = None
        self.correct_keyword = ""
        self.choices: List[str] = []
        self.key_length_analysis: List[Tuple[int, float]] = []
        
        # Calculate difficulty parameters
        max_attempts = max(3, 7 - difficulty.value)
        time_limit = None
        if difficulty.value >= 3:
            time_limit = 300 - (difficulty.value - 3) * 60  # 300, 240, 180, 120 seconds
        
        super().__init__(
            puzzle_id=generate_puzzle_id(),
            name=f"Vigenère Cipher {puzzle_variant.title()}",
            description=f"Decode Vigenère cipher using cryptographic analysis",
            difficulty=difficulty,
            max_attempts=max_attempts,
            time_limit=time_limit,
            signal_data=signal_data
        )
    
    def _initialize_puzzle(self) -> None:
        """Initialize the Vigenère cipher puzzle"""
        # Select or generate cipher based on difficulty
        difficulty_range = self._get_difficulty_range()
        
        # Try to get existing cipher first
        available_ciphers = self.cipher_library.get_ciphers_by_type("vigenere")
        suitable_ciphers = [c for c in available_ciphers if difficulty_range[0] <= c.difficulty <= difficulty_range[1]]
        
        if suitable_ciphers and random.choice([True, False]):
            # Use existing cipher
            self.target_cipher = random.choice(suitable_ciphers)
        else:
            # Generate new cipher
            self.target_cipher = self.cipher_library.generate_cipher_puzzle(
                "vigenere", 
                self.difficulty.value,
                self._select_text_category()
            )
        
        self.correct_keyword = self.target_cipher.key
        
        # Generate analysis data
        self._generate_analysis_data()
        
        # Set solution based on variant
        if self.puzzle_variant == "decode":
            self.solution = self.target_cipher.sample_text
        elif self.puzzle_variant == "keyword_find":
            self.solution = self.correct_keyword
        else:  # key_length
            self.solution = str(len(self.correct_keyword))
        
        # Generate choices
        self._generate_choices()
        
        # Add hints
        self._generate_hints()
        
        # Calculate max score
        self.max_score = 600 + (self.difficulty.value - 1) * 300
    
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
            return random.choice(["simple_messages", "technical_logs"])
        else:
            return random.choice(categories)
    
    def _generate_analysis_data(self):
        """Generate cryptographic analysis data for the puzzle"""
        ciphertext = self.target_cipher.encrypted_text
        
        # Index of Coincidence analysis
        ic = self.frequency_analyzer.calculate_index_of_coincidence(ciphertext)
        
        # Key length estimation
        self.key_length_analysis = self.frequency_analyzer.estimate_vigenere_key_length(ciphertext, 15)
        
        # Vigenère analysis with correct key length
        correct_key_length = len(self.correct_keyword)
        vigenere_analysis = self.cipher_tools.analyze_vigenere_cipher(ciphertext, correct_key_length)
        
        # Store analysis for hints
        self.current_progress['index_of_coincidence'] = ic
        self.current_progress['key_length_analysis'] = self.key_length_analysis
        self.current_progress['vigenere_analysis'] = vigenere_analysis
        self.current_progress['ciphertext_length'] = len(ciphertext.replace(' ', ''))
        self.current_progress['correct_key_length'] = correct_key_length
    
    def _generate_choices(self):
        """Generate choices based on puzzle variant"""
        if self.puzzle_variant == "decode":
            # Choices are different decoded messages
            self.choices = [self.target_cipher.sample_text]
            
            # Add incorrect decodings with wrong keywords
            wrong_keywords = self._generate_wrong_keywords()
            for wrong_keyword in wrong_keywords[:4]:
                wrong_decoded = self.cipher_library.decrypt_text(
                    self.target_cipher.encrypted_text, "vigenere", wrong_keyword
                )
                self.choices.append(wrong_decoded)
        
        elif self.puzzle_variant == "keyword_find":
            # Choices are keyword guesses
            self.choices = [self.correct_keyword]
            self.choices.extend(self._generate_wrong_keywords()[:4])
        
        else:  # key_length variant
            # Choices are key length estimates
            correct_length = len(self.correct_keyword)
            self.choices = [str(correct_length)]
            
            # Add nearby lengths and analysis suggestions
            for i in range(1, 5):
                wrong_length = correct_length + i if i % 2 == 1 else correct_length - i
                if wrong_length > 0 and wrong_length != correct_length:
                    self.choices.append(str(wrong_length))
        
        # Shuffle choices and create mapping
        random.shuffle(self.choices)
        self.choice_mapping = {str(i+1): choice for i, choice in enumerate(self.choices)}
    
    def _generate_wrong_keywords(self) -> List[str]:
        """Generate plausible wrong keywords"""
        correct_keyword = self.correct_keyword
        wrong_keywords = []
        
        # Keywords with similar length
        similar_length_words = ["DECODE", "SIGNAL", "BEACON", "CRYPTO", "CIPHER", "PUZZLE", "ENIGMA"]
        target_length = len(correct_keyword)
        
        for word in similar_length_words:
            if len(word) == target_length and word != correct_keyword:
                wrong_keywords.append(word)
        
        # Keywords with different lengths but common
        common_keywords = ["KEY", "SECRET", "CODE", "HIDDEN", "MESSAGE", "QUANTUM", "VOID", "STAR"]
        wrong_keywords.extend([kw for kw in common_keywords if kw != correct_keyword])
        
        # Slightly modified correct keyword
        if len(correct_keyword) > 3:
            # Change one letter
            for i in range(len(correct_keyword)):
                modified = list(correct_keyword)
                original_char = modified[i]
                for new_char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    if new_char != original_char:
                        modified[i] = new_char
                        wrong_keywords.append(''.join(modified))
                        break
        
        return wrong_keywords[:10]  # Limit to reasonable number
    
    def _generate_hints(self):
        """Generate hints for the puzzle"""
        if not self.target_cipher:
            return
        
        # Hint 1: Basic cipher info
        key_length = len(self.correct_keyword)
        ic = self.current_progress.get('index_of_coincidence', 0)
        self.add_hint(1, f"Vigenère cipher with {key_length}-character keyword (IC: {ic:.3f})", 50)
        
        # Hint 2: Key length analysis
        if self.puzzle_variant != "key_length":
            key_length_analysis = self.current_progress.get('key_length_analysis', [])
            if key_length_analysis:
                top_lengths = [str(length) for length, score in key_length_analysis[:3]]
                self.add_hint(2, f"Most likely key lengths: {', '.join(top_lengths)}", 100)
        
        # Hint 3: Partial keyword or analysis
        if self.difficulty.value >= 3:
            vigenere_analysis = self.current_progress.get('vigenere_analysis', {})
            suggested_key = vigenere_analysis.get('suggested_key', '')
            if suggested_key:
                self.add_hint(3, f"Frequency analysis suggests keyword: '{suggested_key}'", 150)
        
        # Hint 4: Text category hint
        if self.difficulty.value >= 4:
            category = self.target_cipher.metadata.get('category', 'unknown')
            self.add_hint(4, f"Message appears to be from '{category}' category", 200)
        
        # Hint 5: Direct answer
        if self.difficulty.value >= 4:
            if self.puzzle_variant == "keyword_find":
                self.add_hint(5, f"The correct keyword is '{self.correct_keyword}'", 250)
            elif self.puzzle_variant == "key_length":
                self.add_hint(5, f"The key length is {len(self.correct_keyword)}", 200)
            else:
                self.add_hint(5, f"Decoded message: {self.target_cipher.sample_text}", 300)
    
    def validate_input(self, player_input: str) -> Tuple[bool, str]:
        """Validate player's cipher solution"""
        player_input = player_input.strip()
        
        # Check multiple choice number
        if player_input.isdigit():
            choice_num = player_input
            if choice_num in self.choice_mapping:
                selected_answer = self.choice_mapping[choice_num]
                
                if self.puzzle_variant == "keyword_find":
                    # Compare keywords
                    if selected_answer.upper() == self.correct_keyword.upper():
                        return True, f"Excellent! The keyword '{self.correct_keyword}' is correct!"
                    else:
                        return False, f"Keyword '{selected_answer}' is incorrect."
                elif self.puzzle_variant == "key_length":
                    # Compare key lengths
                    if selected_answer == str(len(self.correct_keyword)):
                        return True, f"Correct! Key length is {len(self.correct_keyword)}!"
                    else:
                        return False, f"Key length {selected_answer} is incorrect."
                else:
                    # Compare decoded messages
                    if selected_answer.upper() == self.solution.upper():
                        return True, f"Outstanding! You've decoded the Vigenère cipher!"
                    else:
                        return False, f"Incorrect decoding. This doesn't match the original message."
            else:
                return False, f"Invalid choice. Please select 1-{len(self.choices)}."
        
        # Check direct input
        if self.puzzle_variant == "keyword_find":
            # Direct keyword input
            if player_input.upper() == self.correct_keyword.upper():
                return True, f"Perfect! Keyword '{self.correct_keyword}' is correct!"
            else:
                return False, f"Keyword '{player_input}' is not correct. Try frequency analysis."
        elif self.puzzle_variant == "key_length":
            # Direct length input
            try:
                input_length = int(player_input)
                if input_length == len(self.correct_keyword):
                    return True, f"Correct! Key length is {len(self.correct_keyword)}!"
                else:
                    return False, f"Key length {input_length} is incorrect. Use Index of Coincidence analysis."
            except ValueError:
                return False, "Please enter a valid number for key length."
        else:
            # Direct message input
            if player_input.upper() == self.solution.upper():
                return True, f"Brilliant! You've cracked the Vigenère cipher!"
            elif player_input.upper() in self.solution.upper():
                return False, f"Partially correct - you have part of the message."
            else:
                return False, f"Incorrect decoding. Check your keyword and try again."
    
    def get_current_display(self) -> List[str]:
        """Get the current puzzle display"""
        lines = []
        
        # Header
        lines.append(f"[bold cyan]🔐 VIGENÈRE CIPHER PUZZLE[/bold cyan]")
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
        ic = self.current_progress.get('index_of_coincidence', 0)
        lines.append(f"• Message length: {ciphertext_len} characters")
        lines.append(f"• Cipher type: Vigenère (polyalphabetic)")
        lines.append(f"• Index of Coincidence: {ic:.3f}")
        lines.append(f"• Analysis method: IC analysis + frequency breakdown")
        
        # Show key length analysis for easier difficulties
        if self.difficulty.value <= 3 and self.puzzle_variant != "key_length":
            key_analysis = self.current_progress.get('key_length_analysis', [])
            if key_analysis:
                top3 = key_analysis[:3]
                lengths_str = ", ".join([f"{length}({score:.3f})" for length, score in top3])
                lines.append(f"• Likely key lengths: {lengths_str}")
        
        lines.append("")
        
        # Display choices
        if self.puzzle_variant == "keyword_find":
            lines.append("[cyan]═══ KEYWORD OPTIONS ═══[/cyan]")
            lines.append("Select the correct Vigenère keyword:")
        elif self.puzzle_variant == "key_length":
            lines.append("[cyan]═══ KEY LENGTH OPTIONS ═══[/cyan]")
            lines.append("Select the correct keyword length:")
        else:
            lines.append("[cyan]═══ DECODED MESSAGE OPTIONS ═══[/cyan]")
            lines.append("Select the correctly decoded message:")
        
        for i, choice in enumerate(self.choices, 1):
            if self.puzzle_variant == "key_length":
                lines.append(f"[white]{i}.[/white] {choice} characters")
            else:
                lines.append(f"[white]{i}.[/white] '{choice}'")
        
        lines.append("")
        
        # Instructions
        lines.append("[green]Instructions:[/green]")
        if self.puzzle_variant == "keyword_find":
            lines.append("• Find the correct keyword used for encryption")
            lines.append(f"• Enter the number (1-{len(self.choices)}) or type keyword directly")
        elif self.puzzle_variant == "key_length":
            lines.append("• Determine the length of the encryption keyword")
            lines.append(f"• Enter the number (1-{len(self.choices)}) or type length directly")
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
            key_length = len(self.correct_keyword)
            lines.append(f"[yellow]Key Length:[/yellow] {key_length} characters")
        
        return lines
    
    def _on_puzzle_start(self) -> None:
        """Called when puzzle starts"""
        self.current_progress['puzzle_variant'] = self.puzzle_variant
        self.current_progress['correct_keyword'] = self.correct_keyword
        self.current_progress['start_time'] = time.time()
    
    def _on_puzzle_complete(self, result: PuzzleResult) -> None:
        """Called when puzzle completes"""
        self.current_progress['completion_time'] = time.time()
        self.current_progress['final_score'] = result.score
        self.current_progress['cipher_solved'] = result.success
        self.current_progress['analysis_methods_used'] = self.hints_used 