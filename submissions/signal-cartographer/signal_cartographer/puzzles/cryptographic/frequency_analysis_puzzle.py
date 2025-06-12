"""
Frequency Analysis Puzzle for The Signal Cartographer
Players learn and apply frequency analysis techniques to analyze cipher patterns
"""

from typing import Any, Dict, List, Tuple, Optional
import random
import time

from ..puzzle_base import BasePuzzle, PuzzleResult, PuzzleDifficulty, generate_puzzle_id
from .cipher_library import CipherLibrary, CipherData
from .cipher_tools import CipherTools, FrequencyAnalyzer, FrequencyData


class FrequencyAnalysisPuzzle(BasePuzzle):
    """
    Frequency analysis puzzle where players apply cryptographic analysis
    techniques to identify patterns and cipher characteristics
    """
    
    def __init__(self, 
                 difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL,
                 signal_data: Any = None,
                 puzzle_variant: str = "cipher_type"):
        """
        Initialize frequency analysis puzzle
        
        Args:
            difficulty: Puzzle difficulty level
            signal_data: Associated signal data
            puzzle_variant: Type of puzzle (cipher_type, ic_analysis, pattern_recognition)
        """
        
        self.cipher_library = CipherLibrary()
        self.cipher_tools = CipherTools()
        self.frequency_analyzer = FrequencyAnalyzer()
        self.puzzle_variant = puzzle_variant
        self.target_cipher: Optional[CipherData] = None
        self.analysis_data: Dict[str, Any] = {}
        self.choices: List[str] = []
        
        # Calculate difficulty parameters
        max_attempts = max(4, 7 - difficulty.value)
        time_limit = None
        if difficulty.value >= 3:
            time_limit = 180 - (difficulty.value - 3) * 30  # 180, 150, 120, 90 seconds
        
        super().__init__(
            puzzle_id=generate_puzzle_id(),
            name=f"Frequency Analysis {puzzle_variant.title()}",
            description=f"Apply cryptographic analysis techniques",
            difficulty=difficulty,
            max_attempts=max_attempts,
            time_limit=time_limit,
            signal_data=signal_data
        )
    
    def _initialize_puzzle(self) -> None:
        """Initialize the frequency analysis puzzle"""
        # Generate or select cipher for analysis
        cipher_types = ["caesar", "vigenere", "substitution"]
        weights = [0.4, 0.3, 0.3] if self.difficulty.value <= 3 else [0.3, 0.4, 0.3]
        
        selected_cipher_type = random.choices(cipher_types, weights=weights)[0]
        
        # Generate cipher
        self.target_cipher = self.cipher_library.generate_cipher_puzzle(
            selected_cipher_type,
            self.difficulty.value,
            self._select_text_category()
        )
        
        # Perform comprehensive analysis
        self._generate_analysis_data()
        
        # Set solution based on variant
        if self.puzzle_variant == "cipher_type":
            self.solution = self.target_cipher.cipher_type
        elif self.puzzle_variant == "ic_analysis":
            ic = self.analysis_data.get('index_of_coincidence', 0)
            if ic > 0.065:
                self.solution = "monoalphabetic"
            elif 0.04 < ic < 0.055:
                self.solution = "polyalphabetic"
            else:
                self.solution = "unknown"
        else:  # pattern_recognition
            self.solution = self._analyze_pattern_characteristics()
        
        # Generate choices
        self._generate_choices()
        
        # Add hints
        self._generate_hints()
        
        # Calculate max score
        self.max_score = 300 + (self.difficulty.value - 1) * 150
    
    def _select_text_category(self) -> str:
        """Select appropriate text category based on difficulty"""
        categories = ["simple_messages", "technical_logs", "alien_transmissions", "lore_fragments"]
        
        if self.difficulty.value <= 2:
            return random.choice(["simple_messages", "technical_logs"])
        else:
            return random.choice(categories)
    
    def _generate_analysis_data(self):
        """Perform comprehensive cryptographic analysis"""
        ciphertext = self.target_cipher.encrypted_text
        
        # Basic frequency analysis
        freq_data = self.frequency_analyzer.analyze_text(ciphertext)
        
        # Index of Coincidence
        ic = self.frequency_analyzer.calculate_index_of_coincidence(ciphertext)
        
        # Cipher type detection
        cipher_detection = self.cipher_tools.detect_cipher_type(ciphertext)
        
        # Store all analysis
        self.analysis_data = {
            'frequency_data': freq_data,
            'index_of_coincidence': ic,
            'cipher_detection': cipher_detection,
            'ciphertext_length': len(ciphertext.replace(' ', '')),
            'actual_cipher_type': self.target_cipher.cipher_type
        }
        
        # Add specific analysis based on cipher type
        if self.target_cipher.cipher_type == "vigenere":
            key_length_analysis = self.frequency_analyzer.estimate_vigenere_key_length(ciphertext)
            self.analysis_data['key_length_analysis'] = key_length_analysis
        elif self.target_cipher.cipher_type == "caesar":
            caesar_analysis = self.frequency_analyzer.find_likely_caesar_shifts(ciphertext, 5)
            self.analysis_data['caesar_analysis'] = caesar_analysis
        
        self.current_progress.update(self.analysis_data)
    
    def _analyze_pattern_characteristics(self) -> str:
        """Analyze key pattern characteristics for pattern recognition variant"""
        freq_data = self.analysis_data.get('frequency_data')
        ic = self.analysis_data.get('index_of_coincidence', 0)
        
        if not freq_data:
            return "insufficient_data"
        
        # Analyze letter distribution
        sorted_freqs = sorted(freq_data.letter_frequencies.items(), 
                            key=lambda x: x[1], reverse=True)
        
        if len(sorted_freqs) < 5:
            return "insufficient_data"
        
        # Check if there's a dominant letter (like 'E' in English)
        top_freq = sorted_freqs[0][1]
        if top_freq > 15:  # Very high frequency for one letter
            return "dominant_letter"
        elif ic > 0.065:
            return "even_distribution"
        elif 0.04 < ic < 0.055:
            return "polyalphabetic_pattern"
        else:
            return "unusual_pattern"
    
    def _generate_choices(self):
        """Generate choices based on puzzle variant"""
        if self.puzzle_variant == "cipher_type":
            # Cipher type identification
            self.choices = [self.target_cipher.cipher_type]
            other_types = ["caesar", "vigenere", "substitution"]
            for cipher_type in other_types:
                if cipher_type != self.target_cipher.cipher_type:
                    self.choices.append(cipher_type)
            
            # Add some advanced types for higher difficulty
            if self.difficulty.value >= 4:
                self.choices.extend(["transposition", "playfair"])
        
        elif self.puzzle_variant == "ic_analysis":
            # Index of Coincidence analysis
            correct_category = self.solution
            self.choices = [correct_category]
            
            other_categories = ["monoalphabetic", "polyalphabetic", "unknown"]
            for category in other_categories:
                if category != correct_category:
                    self.choices.append(category)
        
        else:  # pattern_recognition
            # Pattern characteristics
            correct_pattern = self.solution
            self.choices = [correct_pattern]
            
            other_patterns = ["dominant_letter", "even_distribution", 
                            "polyalphabetic_pattern", "unusual_pattern", "insufficient_data"]
            for pattern in other_patterns:
                if pattern != correct_pattern:
                    self.choices.append(pattern[:4])  # Limit to first 4
        
        # Shuffle choices and create mapping
        random.shuffle(self.choices)
        self.choice_mapping = {str(i+1): choice for i, choice in enumerate(self.choices)}
    
    def _generate_hints(self):
        """Generate hints for the puzzle"""
        if not self.target_cipher:
            return
        
        # Hint 1: Basic analysis info
        ic = self.analysis_data.get('index_of_coincidence', 0)
        ciphertext_len = self.analysis_data.get('ciphertext_length', 0)
        self.add_hint(1, f"Text length: {ciphertext_len}, Index of Coincidence: {ic:.3f}", 30)
        
        # Hint 2: Frequency analysis insight
        freq_data = self.analysis_data.get('frequency_data')
        if freq_data:
            sorted_freqs = sorted(freq_data.letter_frequencies.items(), 
                                key=lambda x: x[1], reverse=True)
            top_letter = sorted_freqs[0] if sorted_freqs else ('?', 0)
            self.add_hint(2, f"Most frequent letter: {top_letter[0]} ({top_letter[1]:.1f}%)", 60)
        
        # Hint 3: IC interpretation
        if self.difficulty.value >= 3:
            ic = self.analysis_data.get('index_of_coincidence', 0)
            if ic > 0.065:
                ic_hint = "IC suggests monoalphabetic cipher (Caesar/Substitution)"
            elif 0.04 < ic < 0.055:
                ic_hint = "IC suggests polyalphabetic cipher (Vigenère)"
            else:
                ic_hint = "IC suggests unusual distribution or short text"
            self.add_hint(3, ic_hint, 90)
        
        # Hint 4: Cipher detection result
        if self.difficulty.value >= 4:
            detection = self.analysis_data.get('cipher_detection', {})
            detected_type = detection.get('type', 'unknown')
            confidence = detection.get('confidence', 0)
            self.add_hint(4, f"Automated analysis suggests: {detected_type} ({confidence}% confidence)", 120)
        
        # Hint 5: Direct answer
        if self.difficulty.value >= 4:
            if self.puzzle_variant == "cipher_type":
                self.add_hint(5, f"Cipher type: {self.target_cipher.cipher_type}", 150)
            else:
                self.add_hint(5, f"Correct answer: {self.solution}", 150)
    
    def validate_input(self, player_input: str) -> Tuple[bool, str]:
        """Validate player's analysis result"""
        player_input = player_input.strip()
        
        # Check multiple choice number
        if player_input.isdigit():
            choice_num = player_input
            if choice_num in self.choice_mapping:
                selected_answer = self.choice_mapping[choice_num]
                
                if selected_answer == self.solution:
                    if self.puzzle_variant == "cipher_type":
                        return True, f"Correct! This is a {self.solution} cipher!"
                    elif self.puzzle_variant == "ic_analysis":
                        return True, f"Excellent! IC analysis indicates {self.solution} cipher!"
                    else:
                        return True, f"Perfect! Pattern analysis shows {self.solution.replace('_', ' ')}!"
                else:
                    return False, f"Incorrect. {selected_answer} doesn't match the frequency analysis."
            else:
                return False, f"Invalid choice. Please select 1-{len(self.choices)}."
        
        # Check direct input
        if player_input.lower() == self.solution.lower():
            return True, f"Outstanding! Your frequency analysis is correct!"
        else:
            # Check for partial matches
            if self.puzzle_variant == "cipher_type":
                if player_input.lower() in ["caesar", "vigenere", "substitution", "shift"]:
                    if player_input.lower() == self.solution or \
                       (player_input.lower() == "shift" and self.solution == "caesar"):
                        return True, f"Correct! This is a {self.solution} cipher!"
                    else:
                        return False, f"Not quite. '{player_input}' doesn't match the frequency patterns."
            
            return False, f"Incorrect analysis. Review the frequency patterns and Index of Coincidence."
    
    def get_current_display(self) -> List[str]:
        """Get the current puzzle display"""
        lines = []
        
        # Header
        lines.append(f"[bold cyan]📊 FREQUENCY ANALYSIS PUZZLE[/bold cyan]")
        lines.append("=" * 60)
        lines.append("")
        
        # Puzzle info
        variant_desc = self.puzzle_variant.replace('_', ' ').title()
        lines.append(f"[yellow]Analysis Type:[/yellow] {variant_desc}")
        lines.append(f"[yellow]Difficulty:[/yellow] {self.difficulty.name}")
        
        if self.target_cipher:
            lines.append(f"[yellow]Text Category:[/yellow] {self.target_cipher.metadata.get('category', 'Unknown')}")
        
        lines.append("")
        
        # Display ciphertext
        lines.append("[cyan]═══ CIPHERTEXT TO ANALYZE ═══[/cyan]")
        if self.target_cipher:
            lines.append(f"'{self.target_cipher.encrypted_text}'")
        lines.append("")
        
        # Frequency analysis display
        lines.append("[cyan]═══ FREQUENCY ANALYSIS RESULTS ═══[/cyan]")
        freq_data = self.analysis_data.get('frequency_data')
        ic = self.analysis_data.get('index_of_coincidence', 0)
        
        lines.append(f"• Text length: {self.analysis_data.get('ciphertext_length', 0)} characters")
        lines.append(f"• Index of Coincidence: {ic:.4f}")
        
        if freq_data:
            # Letter frequency table
            sorted_freqs = sorted(freq_data.letter_frequencies.items(), 
                                key=lambda x: x[1], reverse=True)
            lines.append("• Letter frequencies (top 10):")
            freq_line = "  "
            for i, (letter, freq) in enumerate(sorted_freqs[:10]):
                freq_line += f"{letter}:{freq:.1f}% "
                if i == 4:  # Split into two lines
                    lines.append(freq_line)
                    freq_line = "  "
            if freq_line.strip():
                lines.append(freq_line)
        
        # IC interpretation
        lines.append("")
        lines.append("• IC Reference:")
        lines.append("  English text: ~0.067 | Random text: ~0.038")
        lines.append("  Monoalphabetic: >0.060 | Polyalphabetic: 0.040-0.055")
        
        lines.append("")
        
        # Display choices based on variant
        if self.puzzle_variant == "cipher_type":
            lines.append("[cyan]═══ CIPHER TYPE OPTIONS ═══[/cyan]")
            lines.append("Identify the cipher type based on frequency analysis:")
        elif self.puzzle_variant == "ic_analysis":
            lines.append("[cyan]═══ IC ANALYSIS OPTIONS ═══[/cyan]")
            lines.append("Classify the cipher based on Index of Coincidence:")
        else:
            lines.append("[cyan]═══ PATTERN ANALYSIS OPTIONS ═══[/cyan]")
            lines.append("Identify the key pattern characteristic:")
        
        for i, choice in enumerate(self.choices, 1):
            display_choice = choice.replace('_', ' ').title()
            lines.append(f"[white]{i}.[/white] {display_choice}")
        
        lines.append("")
        
        # Instructions
        lines.append("[green]Instructions:[/green]")
        lines.append("• Analyze the frequency patterns and Index of Coincidence")
        lines.append(f"• Enter the number (1-{len(self.choices)}) or type your analysis directly")
        lines.append("• Use [yellow]HINT[/yellow] command for analysis guidance")
        
        return lines
    
    def get_progress_display(self) -> List[str]:
        """Get progress indicators"""
        lines = []
        
        lines.append("[cyan]═══ ANALYSIS PROGRESS ═══[/cyan]")
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
        
        # Show analysis summary
        ic = self.analysis_data.get('index_of_coincidence', 0)
        lines.append(f"[yellow]IC Value:[/yellow] {ic:.4f}")
        
        detection = self.analysis_data.get('cipher_detection', {})
        if detection:
            detected_type = detection.get('type', 'unknown')
            confidence = detection.get('confidence', 0)
            lines.append(f"[yellow]Auto-Detection:[/yellow] {detected_type} ({confidence}%)")
        
        return lines
    
    def _on_puzzle_start(self) -> None:
        """Called when puzzle starts"""
        self.current_progress['puzzle_variant'] = self.puzzle_variant
        self.current_progress['target_cipher_type'] = self.target_cipher.cipher_type
        self.current_progress['start_time'] = time.time()
    
    def _on_puzzle_complete(self, result: PuzzleResult) -> None:
        """Called when puzzle completes"""
        self.current_progress['completion_time'] = time.time()
        self.current_progress['final_score'] = result.score
        self.current_progress['analysis_correct'] = result.success
        self.current_progress['analysis_methods_used'] = self.hints_used 