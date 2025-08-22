"""
Cipher Tools and Frequency Analysis Utilities
Provides cryptographic analysis tools and helper functions
"""

from typing import Dict, List, Tuple, Optional, Any
import string
import re
import random
from collections import Counter
from dataclasses import dataclass


@dataclass
class FrequencyData:
    """Data structure for frequency analysis results"""
    letter_frequencies: Dict[str, float]
    bigram_frequencies: Dict[str, float]
    trigram_frequencies: Dict[str, float]
    word_frequencies: Dict[str, int]
    total_letters: int
    total_words: int


class FrequencyAnalyzer:
    """Analyze text frequency patterns for cryptographic analysis"""
    
    def __init__(self):
        # Standard English letter frequencies (approximate)
        self.english_frequencies = {
            'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97, 'N': 6.75,
            'S': 6.33, 'H': 6.09, 'R': 5.99, 'D': 4.25, 'L': 4.03, 'C': 2.78,
            'U': 2.76, 'M': 2.41, 'W': 2.36, 'F': 2.23, 'G': 2.02, 'Y': 1.97,
            'P': 1.93, 'B': 1.29, 'V': 0.98, 'K': 0.77, 'J': 0.15, 'X': 0.15,
            'Q': 0.10, 'Z': 0.07
        }
        
        # Common English bigrams
        self.common_bigrams = [
            'TH', 'HE', 'IN', 'ER', 'AN', 'RE', 'ED', 'ND', 'ON', 'EN',
            'AT', 'OU', 'EA', 'HA', 'NG', 'AS', 'OR', 'TI', 'IS', 'ET'
        ]
        
        # Common English trigrams
        self.common_trigrams = [
            'THE', 'AND', 'ING', 'HER', 'HAT', 'HIS', 'THA', 'ERE', 'FOR', 'ENT',
            'ION', 'TER', 'HAS', 'YOU', 'ITH', 'VER', 'ALL', 'WIT', 'THI', 'TIO'
        ]
    
    def analyze_text(self, text: str) -> FrequencyData:
        """Perform comprehensive frequency analysis on text"""
        # Clean text (keep only alphabetic characters for frequency analysis)
        clean_text = re.sub(r'[^A-Za-z\s]', '', text.upper())
        letters_only = re.sub(r'[^A-Za-z]', '', clean_text)
        
        # Letter frequencies
        letter_counts = Counter(letters_only)
        total_letters = sum(letter_counts.values())
        letter_frequencies = {
            letter: (count / total_letters * 100) if total_letters > 0 else 0
            for letter, count in letter_counts.items()
        }
        
        # Bigram frequencies  
        bigrams = [letters_only[i:i+2] for i in range(len(letters_only) - 1)]
        bigram_counts = Counter(bigrams)
        total_bigrams = sum(bigram_counts.values())
        bigram_frequencies = {
            bigram: (count / total_bigrams * 100) if total_bigrams > 0 else 0
            for bigram, count in bigram_counts.items()
        }
        
        # Trigram frequencies
        trigrams = [letters_only[i:i+3] for i in range(len(letters_only) - 2)]
        trigram_counts = Counter(trigrams)
        total_trigrams = sum(trigram_counts.values())
        trigram_frequencies = {
            trigram: (count / total_trigrams * 100) if total_trigrams > 0 else 0
            for trigram, count in trigram_counts.items()
        }
        
        # Word frequencies
        words = clean_text.split()
        word_counts = Counter(words)
        
        return FrequencyData(
            letter_frequencies=letter_frequencies,
            bigram_frequencies=bigram_frequencies,
            trigram_frequencies=trigram_frequencies,
            word_frequencies=dict(word_counts),
            total_letters=total_letters,
            total_words=len(words)
        )
    
    def calculate_index_of_coincidence(self, text: str) -> float:
        """Calculate Index of Coincidence for text (useful for Vigenère analysis)"""
        clean_text = re.sub(r'[^A-Za-z]', '', text.upper())
        n = len(clean_text)
        
        if n <= 1:
            return 0.0
        
        letter_counts = Counter(clean_text)
        ic = sum(count * (count - 1) for count in letter_counts.values()) / (n * (n - 1))
        
        return ic
    
    def find_likely_caesar_shifts(self, ciphertext: str, top_n: int = 5) -> List[Tuple[int, float]]:
        """Find most likely Caesar cipher shifts using frequency analysis"""
        results = []
        clean_cipher = re.sub(r'[^A-Za-z]', '', ciphertext.upper())
        
        for shift in range(26):
            # Decrypt with this shift
            decrypted = ""
            for char in clean_cipher:
                shifted = (ord(char) - 65 - shift) % 26
                decrypted += chr(shifted + 65)
            
            # Calculate chi-squared statistic against English frequencies
            freq_data = self.analyze_text(decrypted)
            chi_squared = self._calculate_chi_squared(freq_data.letter_frequencies)
            
            results.append((shift, chi_squared))
        
        # Sort by chi-squared (lower is better match to English)
        results.sort(key=lambda x: x[1])
        return results[:top_n]
    
    def estimate_vigenere_key_length(self, ciphertext: str, max_length: int = 20) -> List[Tuple[int, float]]:
        """Estimate Vigenère key length using Index of Coincidence"""
        clean_cipher = re.sub(r'[^A-Za-z]', '', ciphertext.upper())
        results = []
        
        for key_length in range(1, max_length + 1):
            # Split text into subsequences based on key length
            subsequences = [''] * key_length
            for i, char in enumerate(clean_cipher):
                subsequences[i % key_length] += char
            
            # Calculate average IC for subsequences
            total_ic = 0
            valid_subsequences = 0
            
            for subseq in subsequences:
                if len(subseq) > 1:
                    ic = self.calculate_index_of_coincidence(subseq)
                    total_ic += ic
                    valid_subsequences += 1
            
            avg_ic = total_ic / valid_subsequences if valid_subsequences > 0 else 0
            results.append((key_length, avg_ic))
        
        # Sort by IC (higher IC suggests correct key length for English)
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def _calculate_chi_squared(self, observed_frequencies: Dict[str, float]) -> float:
        """Calculate chi-squared statistic comparing observed vs expected English frequencies"""
        chi_squared = 0.0
        
        for letter in string.ascii_uppercase:
            observed = observed_frequencies.get(letter, 0)
            expected = self.english_frequencies.get(letter, 0)
            
            if expected > 0:
                chi_squared += ((observed - expected) ** 2) / expected
        
        return chi_squared
    
    def suggest_substitutions(self, ciphertext: str) -> Dict[str, List[str]]:
        """Suggest possible character substitutions based on frequency analysis"""
        freq_data = self.analyze_text(ciphertext)
        suggestions = {}
        
        # Sort cipher letters by frequency
        cipher_freq_sorted = sorted(
            freq_data.letter_frequencies.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Sort English letters by frequency
        english_freq_sorted = sorted(
            self.english_frequencies.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Suggest mappings based on frequency matching
        for i, (cipher_char, cipher_freq) in enumerate(cipher_freq_sorted):
            if i < len(english_freq_sorted):
                # Primary suggestion based on frequency rank
                primary_suggestion = english_freq_sorted[i][0]
                
                # Additional suggestions from nearby frequencies
                additional = []
                for j in range(max(0, i-2), min(len(english_freq_sorted), i+3)):
                    if j != i:
                        additional.append(english_freq_sorted[j][0])
                
                suggestions[cipher_char] = [primary_suggestion] + additional[:3]
        
        return suggestions


class CipherTools:
    """Collection of cryptographic analysis and solving tools"""
    
    def __init__(self):
        self.frequency_analyzer = FrequencyAnalyzer()
    
    def brute_force_caesar(self, ciphertext: str) -> List[Tuple[int, str, float]]:
        """Brute force all Caesar cipher possibilities with quality scores"""
        results = []
        clean_cipher = re.sub(r'[^A-Za-z\s]', '', ciphertext.upper())
        
        for shift in range(26):
            decrypted = ""
            for char in clean_cipher:
                if char.isalpha():
                    shifted = (ord(char) - 65 - shift) % 26
                    decrypted += chr(shifted + 65)
                else:
                    decrypted += char
            
            # Score based on English-like characteristics
            score = self._score_english_text(decrypted)
            results.append((shift, decrypted, score))
        
        # Sort by score (higher is better)
        results.sort(key=lambda x: x[2], reverse=True)
        return results
    
    def analyze_vigenere_cipher(self, ciphertext: str, key_length: int) -> Dict[str, Any]:
        """Analyze Vigenère cipher with known key length"""
        clean_cipher = re.sub(r'[^A-Za-z]', '', ciphertext.upper())
        
        # Split into subsequences
        subsequences = [''] * key_length
        for i, char in enumerate(clean_cipher):
            subsequences[i % key_length] += char
        
        # Analyze each subsequence as Caesar cipher
        key_chars = []
        analysis_results = []
        
        for i, subseq in enumerate(subsequences):
            if subseq:
                caesar_results = self.frequency_analyzer.find_likely_caesar_shifts(subseq, 3)
                best_shift = caesar_results[0][0] if caesar_results else 0
                key_char = chr((best_shift) % 26 + 65)
                key_chars.append(key_char)
                
                analysis_results.append({
                    'position': i,
                    'subsequence': subseq,
                    'likely_shifts': caesar_results,
                    'suggested_key_char': key_char
                })
            else:
                key_chars.append('A')  # Default
                analysis_results.append({
                    'position': i,
                    'subsequence': '',
                    'likely_shifts': [],
                    'suggested_key_char': 'A'
                })
        
        suggested_key = ''.join(key_chars)
        
        return {
            'suggested_key': suggested_key,
            'key_length': key_length,
            'subsequence_analysis': analysis_results,
            'decrypted_preview': self._decrypt_vigenere(ciphertext, suggested_key)
        }
    
    def _decrypt_vigenere(self, ciphertext: str, key: str) -> str:
        """Decrypt Vigenère cipher with given key"""
        result = ""
        key = key.upper()
        key_index = 0
        
        for char in ciphertext:
            if char.isalpha():
                key_char = key[key_index % len(key)]
                shift = ord(key_char) - 65
                shifted = (ord(char.upper()) - 65 - shift) % 26
                result += chr(shifted + 65) if char.isupper() else chr(shifted + 97)
                key_index += 1
            else:
                result += char
        
        return result
    
    def _score_english_text(self, text: str) -> float:
        """Score text based on English-like characteristics"""
        if not text:
            return 0.0
        
        score = 0.0
        clean_text = re.sub(r'[^A-Za-z\s]', '', text.upper())
        
        # Frequency analysis score
        freq_data = self.frequency_analyzer.analyze_text(clean_text)
        chi_squared = self.frequency_analyzer._calculate_chi_squared(freq_data.letter_frequencies)
        freq_score = max(0, 100 - chi_squared)  # Lower chi-squared is better
        
        # Common bigram score
        bigram_score = 0
        for bigram in self.frequency_analyzer.common_bigrams:
            if bigram in clean_text:
                bigram_score += freq_data.bigram_frequencies.get(bigram, 0)
        
        # Common trigram score
        trigram_score = 0
        for trigram in self.frequency_analyzer.common_trigrams:
            if trigram in clean_text:
                trigram_score += freq_data.trigram_frequencies.get(trigram, 0)
        
        # Combine scores (weighted)
        score = freq_score * 0.4 + bigram_score * 0.3 + trigram_score * 0.3
        
        return score
    
    def detect_cipher_type(self, ciphertext: str) -> Dict[str, Any]:
        """Attempt to detect the type of cipher used"""
        clean_cipher = re.sub(r'[^A-Za-z]', '', ciphertext.upper())
        
        if not clean_cipher:
            return {"type": "unknown", "confidence": 0, "analysis": {}}
        
        analysis = {}
        
        # Calculate Index of Coincidence
        ic = self.frequency_analyzer.calculate_index_of_coincidence(clean_cipher)
        analysis['index_of_coincidence'] = ic
        
        # Analyze letter frequencies
        freq_data = self.frequency_analyzer.analyze_text(clean_cipher)
        analysis['frequency_data'] = freq_data
        
        # Decision logic
        if ic > 0.065:  # Close to English IC (~0.067)
            # Likely monoalphabetic cipher (Caesar, Substitution)
            # Try Caesar first (simpler)
            caesar_results = self.frequency_analyzer.find_likely_caesar_shifts(clean_cipher, 3)
            best_score = self._score_english_text(
                self.brute_force_caesar(ciphertext)[0][1]
            )
            
            if best_score > 60:  # Good English-like score
                return {
                    "type": "caesar",
                    "confidence": min(95, best_score + 20),
                    "analysis": {
                        "ic": ic,
                        "suggested_shifts": caesar_results,
                        "best_score": best_score
                    }
                }
            else:
                return {
                    "type": "substitution", 
                    "confidence": 70,
                    "analysis": {
                        "ic": ic,
                        "substitution_suggestions": self.frequency_analyzer.suggest_substitutions(clean_cipher)
                    }
                }
        
        elif 0.04 < ic < 0.055:  # Lower IC suggests polyalphabetic
            # Likely Vigenère cipher
            key_length_analysis = self.frequency_analyzer.estimate_vigenere_key_length(clean_cipher)
            likely_key_length = key_length_analysis[0][0] if key_length_analysis else 3
            
            vigenere_analysis = self.analyze_vigenere_cipher(clean_cipher, likely_key_length)
            
            return {
                "type": "vigenere",
                "confidence": 75,
                "analysis": {
                    "ic": ic,
                    "key_length_estimates": key_length_analysis[:5],
                    "vigenere_analysis": vigenere_analysis
                }
            }
        
        else:
            return {
                "type": "unknown",
                "confidence": 30,
                "analysis": {
                    "ic": ic,
                    "note": "Unusual frequency distribution - may be complex cipher or non-English text"
                }
            }
    
    def generate_cipher_key(self, cipher_type: str, difficulty: int) -> str:
        """Generate appropriate cipher key for given type and difficulty"""
        if cipher_type == "caesar":
            # Higher difficulty = more unusual shifts
            if difficulty <= 2:
                return str(random.choice([1, 2, 3, 4, 5]))
            elif difficulty <= 4:
                return str(random.choice([6, 7, 8, 9, 10, 11, 12]))
            else:
                return str(random.choice([13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]))
        
        elif cipher_type == "vigenere":
            # Higher difficulty = longer keywords
            key_length = min(12, 3 + difficulty)
            return ''.join(random.choices(string.ascii_uppercase, k=key_length))
        
        elif cipher_type == "substitution":
            # Create random substitution mapping
            alphabet = list(string.ascii_uppercase)
            shuffled = alphabet.copy()
            random.shuffle(shuffled)
            return str({alphabet[i]: shuffled[i] for i in range(26)})
        
        return "UNKNOWN" 