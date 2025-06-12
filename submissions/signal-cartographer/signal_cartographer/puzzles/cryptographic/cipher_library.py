"""
Cipher Library System for Cryptographic Puzzles
Stores cipher definitions, sample texts, and cryptographic algorithms
"""

from typing import Dict, List, Tuple, Optional, Any
import random
import string
from dataclasses import dataclass


@dataclass
class CipherData:
    """Data structure for cipher information"""
    name: str
    cipher_type: str  # caesar, vigenere, substitution, etc.
    description: str
    difficulty: int  # 1-5
    sample_text: str
    encrypted_text: str
    key: str
    metadata: Dict[str, Any]


class CipherLibrary:
    """Library of cipher texts and cryptographic challenges"""
    
    def __init__(self):
        self.ciphers: Dict[str, CipherData] = {}
        self.sample_texts: Dict[str, List[str]] = {}
        self.common_words: List[str] = []
        self._initialize_library()
    
    def _initialize_library(self):
        """Initialize with sample ciphers and texts"""
        
        # Sample plaintext messages
        self.sample_texts = {
            "alien_transmissions": [
                "THE ANCIENT BEACON STILL TRANSMITS FROM SECTOR GAMMA",
                "QUANTUM ECHOES DETECTED IN THE VOID BETWEEN STARS",
                "THE WANDERING SHIP HAS BEEN SILENT FOR TOO LONG",
                "CRYSTALLINE STRUCTURES EMIT HARMONIC FREQUENCIES",
                "THE SIGNAL ORIGINATES FROM BEYOND KNOWN SPACE",
                "MEMETIC PATTERNS DETECTED IN TRANSMISSION DATA",
                "THE LAST EXPLORER LOGGED COORDINATES BEFORE VANISHING"
            ],
            "technical_logs": [
                "SCANNER EFFICIENCY AT NINETY SEVEN PERCENT",
                "FUEL RESERVES DROPPING TO CRITICAL LEVELS",
                "DECODER MODULE REQUIRES IMMEDIATE CALIBRATION", 
                "NAVIGATION SYSTEM LOCKED ONTO NEW COORDINATES",
                "ANALYSIS TOOLS FUNCTIONING WITHIN PARAMETERS",
                "SPECTRUM ANALYZER DETECTING UNUSUAL PATTERNS",
                "CARTOGRAPHY DATABASE UPDATED WITH NEW SECTORS"
            ],
            "lore_fragments": [
                "THE FIRST CARTOGRAPHERS MAPPED THE STELLAR VOID",
                "ANCIENT CIVILIZATIONS LEFT SIGNALS IN THE DARK",
                "THE GREAT SILENCE BEGAN THREE CENTURIES AGO",
                "WANDERERS SEEK THE SOURCE OF THE ETERNAL BEACON",
                "REALITY BENDS WHERE THE SIGNAL TOUCHES SPACE",
                "THE VOID WHISPERS SECRETS TO THOSE WHO LISTEN",
                "TIME FLOWS DIFFERENTLY NEAR THE QUANTUM ECHOES"
            ],
            "simple_messages": [
                "HELLO WORLD",
                "SIGNAL DETECTED",
                "MISSION COMPLETE",
                "COORDINATES FOUND",
                "BEACON ACTIVE",
                "ANALYSIS READY",
                "SYSTEM ONLINE"
            ]
        }
        
        # Common English words for frequency analysis
        self.common_words = [
            "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HER",
            "HAS", "HAD", "ONE", "OUR", "OUT", "DAY", "GET", "USE", "MAN", "NEW",
            "NOW", "OLD", "SEE", "HIM", "TWO", "HOW", "ITS", "WHO", "OIL", "SIT",
            "SIGNAL", "BEACON", "SPACE", "VOID", "STAR", "SHIP", "DATA", "SCAN"
        ]
        
        # Initialize sample Caesar ciphers
        self._create_caesar_samples()
        
        # Initialize sample Vigenère ciphers
        self._create_vigenere_samples()
        
        # Initialize substitution ciphers
        self._create_substitution_samples()
    
    def _create_caesar_samples(self):
        """Create sample Caesar cipher puzzles"""
        caesar_samples = [
            ("BEACON_ALPHA", "alien_transmissions", 0, 3),
            ("TECH_LOG_1", "technical_logs", 1, 7), 
            ("LORE_BETA", "lore_fragments", 2, 13),
            ("SIMPLE_MSG", "simple_messages", 0, 5),
            ("BEACON_GAMMA", "alien_transmissions", 3, 19),
        ]
        
        for name, category, text_index, shift in caesar_samples:
            if category in self.sample_texts and text_index < len(self.sample_texts[category]):
                plaintext = self.sample_texts[category][text_index]
                encrypted = self._caesar_encrypt(plaintext, shift)
                
                self.ciphers[name] = CipherData(
                    name=name,
                    cipher_type="caesar",
                    description=f"Caesar cipher with shift {shift}",
                    difficulty=min(5, abs(shift) // 4 + 1),
                    sample_text=plaintext,
                    encrypted_text=encrypted,
                    key=str(shift),
                    metadata={"shift": shift, "category": category}
                )
    
    def _create_vigenere_samples(self):
        """Create sample Vigenère cipher puzzles"""
        vigenere_samples = [
            ("VIGENERE_ALPHA", "alien_transmissions", 0, "SIGNAL"),
            ("VIGENERE_TECH", "technical_logs", 2, "DECODE"),
            ("VIGENERE_LORE", "lore_fragments", 1, "BEACON"),
            ("VIGENERE_BETA", "alien_transmissions", 4, "QUANTUM"),
            ("VIGENERE_GAMMA", "lore_fragments", 5, "VOID"),
        ]
        
        for name, category, text_index, keyword in vigenere_samples:
            if category in self.sample_texts and text_index < len(self.sample_texts[category]):
                plaintext = self.sample_texts[category][text_index]
                encrypted = self._vigenere_encrypt(plaintext, keyword)
                
                self.ciphers[name] = CipherData(
                    name=name,
                    cipher_type="vigenere",
                    description=f"Vigenère cipher with keyword '{keyword}'",
                    difficulty=min(5, len(keyword) // 2 + 2),
                    sample_text=plaintext,
                    encrypted_text=encrypted,
                    key=keyword,
                    metadata={"keyword": keyword, "category": category}
                )
    
    def _create_substitution_samples(self):
        """Create sample substitution cipher puzzles"""
        # Simple substitution mappings
        substitution_maps = [
            # ROT13-style but custom
            {"name": "SUBSTITUTION_ALPHA", "mapping": self._create_substitution_map("ZYXWVUTSRQPONMLKJIHGFEDCBA")},
            # Random substitution
            {"name": "SUBSTITUTION_BETA", "mapping": self._create_random_substitution()},
            # Keyword substitution
            {"name": "SUBSTITUTION_GAMMA", "mapping": self._create_keyword_substitution("BEACON")},
        ]
        
        for i, sub_data in enumerate(substitution_maps):
            category = "alien_transmissions" if i < 2 else "lore_fragments"
            text_index = i % len(self.sample_texts[category])
            plaintext = self.sample_texts[category][text_index]
            encrypted = self._substitution_encrypt(plaintext, sub_data["mapping"])
            
            self.ciphers[sub_data["name"]] = CipherData(
                name=sub_data["name"],
                cipher_type="substitution",
                description="Substitution cipher with custom alphabet mapping",
                difficulty=4,  # Generally harder than shift ciphers
                sample_text=plaintext,
                encrypted_text=encrypted,
                key=str(sub_data["mapping"]),
                metadata={"mapping": sub_data["mapping"], "category": category}
            )
    
    def _caesar_encrypt(self, text: str, shift: int) -> str:
        """Encrypt text using Caesar cipher"""
        result = ""
        for char in text:
            if char.isalpha():
                ascii_offset = 65 if char.isupper() else 97
                shifted = (ord(char) - ascii_offset + shift) % 26
                result += chr(shifted + ascii_offset)
            else:
                result += char
        return result
    
    def _caesar_decrypt(self, text: str, shift: int) -> str:
        """Decrypt text using Caesar cipher"""
        return self._caesar_encrypt(text, -shift)
    
    def _vigenere_encrypt(self, text: str, keyword: str) -> str:
        """Encrypt text using Vigenère cipher"""
        result = ""
        keyword = keyword.upper()
        key_index = 0
        
        for char in text:
            if char.isalpha():
                ascii_offset = 65 if char.isupper() else 97
                key_char = keyword[key_index % len(keyword)]
                shift = ord(key_char) - 65
                shifted = (ord(char.upper()) - 65 + shift) % 26
                result += chr(shifted + 65) if char.isupper() else chr(shifted + 97)
                key_index += 1
            else:
                result += char
        return result
    
    def _vigenere_decrypt(self, text: str, keyword: str) -> str:
        """Decrypt text using Vigenère cipher"""
        result = ""
        keyword = keyword.upper()
        key_index = 0
        
        for char in text:
            if char.isalpha():
                ascii_offset = 65 if char.isupper() else 97
                key_char = keyword[key_index % len(keyword)]
                shift = ord(key_char) - 65
                shifted = (ord(char.upper()) - 65 - shift) % 26
                result += chr(shifted + 65) if char.isupper() else chr(shifted + 97)
                key_index += 1
            else:
                result += char
        return result
    
    def _create_substitution_map(self, substitution_alphabet: str) -> Dict[str, str]:
        """Create substitution mapping from custom alphabet"""
        normal_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return {normal_alphabet[i]: substitution_alphabet[i] for i in range(26)}
    
    def _create_random_substitution(self) -> Dict[str, str]:
        """Create random substitution mapping"""
        normal_alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        shuffled_alphabet = normal_alphabet.copy()
        random.shuffle(shuffled_alphabet)
        return {normal_alphabet[i]: shuffled_alphabet[i] for i in range(26)}
    
    def _create_keyword_substitution(self, keyword: str) -> Dict[str, str]:
        """Create substitution mapping based on keyword"""
        keyword = keyword.upper()
        # Remove duplicates while preserving order
        unique_keyword = ""
        for char in keyword:
            if char not in unique_keyword and char.isalpha():
                unique_keyword += char
        
        # Create substitution alphabet
        substitution_alphabet = unique_keyword
        for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if char not in substitution_alphabet:
                substitution_alphabet += char
        
        normal_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return {normal_alphabet[i]: substitution_alphabet[i] for i in range(26)}
    
    def _substitution_encrypt(self, text: str, mapping: Dict[str, str]) -> str:
        """Encrypt text using substitution cipher"""
        result = ""
        for char in text:
            if char.upper() in mapping:
                substituted = mapping[char.upper()]
                result += substituted if char.isupper() else substituted.lower()
            else:
                result += char
        return result
    
    def _substitution_decrypt(self, text: str, mapping: Dict[str, str]) -> str:
        """Decrypt text using substitution cipher"""
        # Reverse the mapping
        reverse_mapping = {v: k for k, v in mapping.items()}
        return self._substitution_encrypt(text, reverse_mapping)
    
    def get_cipher(self, name: str) -> Optional[CipherData]:
        """Get cipher data by name"""
        return self.ciphers.get(name)
    
    def get_ciphers_by_type(self, cipher_type: str) -> List[CipherData]:
        """Get all ciphers of a specific type"""
        return [cipher for cipher in self.ciphers.values() if cipher.cipher_type == cipher_type]
    
    def get_ciphers_by_difficulty(self, difficulty: int) -> List[CipherData]:
        """Get all ciphers of a specific difficulty"""
        return [cipher for cipher in self.ciphers.values() if cipher.difficulty == difficulty]
    
    def get_random_cipher(self, cipher_type: str = None, difficulty_range: Tuple[int, int] = (1, 5)) -> Optional[CipherData]:
        """Get random cipher optionally filtered by type and difficulty"""
        valid_ciphers = []
        
        for cipher in self.ciphers.values():
            if cipher_type and cipher.cipher_type != cipher_type:
                continue
            if not (difficulty_range[0] <= cipher.difficulty <= difficulty_range[1]):
                continue
            valid_ciphers.append(cipher)
        
        return random.choice(valid_ciphers) if valid_ciphers else None
    
    def get_sample_text(self, category: str, length_preference: str = "medium") -> str:
        """Get sample text from category with length preference"""
        if category not in self.sample_texts:
            category = "simple_messages"  # Fallback
        
        texts = self.sample_texts[category]
        
        if length_preference == "short":
            # Prefer shorter texts
            texts = sorted(texts, key=len)[:len(texts)//2]
        elif length_preference == "long":
            # Prefer longer texts
            texts = sorted(texts, key=len)[len(texts)//2:]
        
        return random.choice(texts)
    
    def encrypt_text(self, text: str, cipher_type: str, key: str) -> str:
        """Encrypt text using specified cipher type and key"""
        if cipher_type == "caesar":
            shift = int(key)
            return self._caesar_encrypt(text, shift)
        elif cipher_type == "vigenere":
            return self._vigenere_encrypt(text, key)
        elif cipher_type == "substitution":
            # Key should be the mapping dict as string
            mapping = eval(key) if isinstance(key, str) else key
            return self._substitution_encrypt(text, mapping)
        else:
            return text
    
    def decrypt_text(self, text: str, cipher_type: str, key: str) -> str:
        """Decrypt text using specified cipher type and key"""
        if cipher_type == "caesar":
            shift = int(key)
            return self._caesar_decrypt(text, shift)
        elif cipher_type == "vigenere":
            return self._vigenere_decrypt(text, key)
        elif cipher_type == "substitution":
            # Key should be the mapping dict as string
            mapping = eval(key) if isinstance(key, str) else key
            return self._substitution_decrypt(text, mapping)
        else:
            return text
    
    def generate_cipher_puzzle(self, cipher_type: str, difficulty: int, 
                             text_category: str = None) -> CipherData:
        """Generate a new cipher puzzle on demand"""
        if not text_category:
            text_category = random.choice(list(self.sample_texts.keys()))
        
        # Select appropriate text length based on difficulty
        length_pref = "short" if difficulty <= 2 else "medium" if difficulty <= 4 else "long"
        plaintext = self.get_sample_text(text_category, length_pref)
        
        # Generate key based on cipher type and difficulty
        if cipher_type == "caesar":
            # Harder difficulties use larger shifts
            max_shift = min(25, 5 * difficulty)
            shift = random.randint(1, max_shift)
            encrypted = self._caesar_encrypt(plaintext, shift)
            key = str(shift)
            description = f"Caesar cipher with shift {shift}"
            
        elif cipher_type == "vigenere":
            # Longer keywords for higher difficulty
            keyword_length = min(10, 3 + difficulty)
            keyword = ''.join(random.choices(string.ascii_uppercase, k=keyword_length))
            encrypted = self._vigenere_encrypt(plaintext, keyword)
            key = keyword
            description = f"Vigenère cipher with {keyword_length}-letter keyword"
            
        elif cipher_type == "substitution":
            mapping = self._create_random_substitution()
            encrypted = self._substitution_encrypt(plaintext, mapping)
            key = str(mapping)
            description = "Random substitution cipher"
            
        else:
            # Fallback to Caesar
            shift = random.randint(1, 13)
            encrypted = self._caesar_encrypt(plaintext, shift)
            key = str(shift)
            description = f"Caesar cipher with shift {shift}"
        
        puzzle_name = f"GENERATED_{cipher_type.upper()}_{random.randint(1000, 9999)}"
        
        return CipherData(
            name=puzzle_name,
            cipher_type=cipher_type,
            description=description,
            difficulty=difficulty,
            sample_text=plaintext,
            encrypted_text=encrypted,
            key=key,
            metadata={"category": text_category, "generated": True}
        ) 