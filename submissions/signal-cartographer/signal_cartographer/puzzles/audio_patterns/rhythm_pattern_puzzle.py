"""
Rhythm Pattern Puzzle for The Signal Cartographer
Players analyze and identify rhythm patterns in signals
"""

from typing import Any, Dict, List, Tuple, Optional
import random
import time

from ..puzzle_base import BasePuzzle, PuzzleResult, PuzzleDifficulty, generate_puzzle_id
from .audio_library import AudioLibrary
from .audio_tools import AudioAnalyzer


class RhythmPatternPuzzle(BasePuzzle):
    """
    Rhythm pattern puzzle where players analyze temporal rhythm patterns
    """
    
    def __init__(self, 
                 difficulty: PuzzleDifficulty = PuzzleDifficulty.NORMAL,
                 signal_data: Any = None,
                 rhythm_type: str = "basic"):
        """
        Initialize rhythm pattern puzzle
        
        Args:
            difficulty: Puzzle difficulty level
            signal_data: Associated signal data
            rhythm_type: Type of rhythm (basic, syncopated, complex, polyrhythm)
        """
        
        self.audio_library = AudioLibrary()
        self.audio_analyzer = AudioAnalyzer()
        self.rhythm_type = rhythm_type
        self.rhythm_pattern: List[str] = []
        self.pattern_description = ""
        self.tempo_marking = ""
        self.rhythm_notation = ""
        self.completion_pattern: List[str] = []
        
        # Calculate difficulty parameters
        max_attempts = max(3, 6 - difficulty.value)
        time_limit = None
        if difficulty.value >= 3:
            time_limit = 300 - (difficulty.value - 3) * 50  # 300, 250, 200, 150 seconds
        
        super().__init__(
            puzzle_id=generate_puzzle_id(),
            name=f"Rhythm Pattern - {rhythm_type.title()}",
            description=f"Analyze temporal rhythm patterns",
            difficulty=difficulty,
            max_attempts=max_attempts,
            time_limit=time_limit,
            signal_data=signal_data
        )
    
    def _initialize_puzzle(self) -> None:
        """Initialize the rhythm pattern puzzle"""
        # Generate rhythm based on type and difficulty
        if self.rhythm_type == "basic":
            self._generate_basic_rhythm()
        elif self.rhythm_type == "syncopated":
            self._generate_syncopated_rhythm()
        elif self.rhythm_type == "complex":
            self._generate_complex_rhythm()
        elif self.rhythm_type == "polyrhythm":
            self._generate_polyrhythm()
        else:
            self._generate_basic_rhythm()  # Default
        
        # Generate hints
        self._generate_hints()
        
        # Calculate max score
        self.max_score = 600 + (self.difficulty.value - 1) * 300
    
    def _generate_basic_rhythm(self):
        """Generate basic rhythm patterns"""
        basic_patterns = {
            1: {  # Simple 4/4 time
                "pattern": ["●", "·", "●", "·", "●", "·", "●", "·"],
                "description": "Simple quarter note pattern in 4/4 time",
                "tempo": "Moderate (120 BPM)",
                "notation": "● = strong beat, · = rest"
            },
            2: {  # Eighth note pattern
                "pattern": ["●", "○", "●", "○", "●", "○", "●", "○"],
                "description": "Eighth note pattern with accents",
                "tempo": "Allegro (140 BPM)",
                "notation": "● = accent, ○ = weak beat"
            },
            3: {  # Mixed pattern
                "pattern": ["●", "·", "○", "●", "·", "○", "●", "·"],
                "description": "Mixed quarter and eighth notes",
                "tempo": "Andante (100 BPM)",
                "notation": "● = strong, ○ = medium, · = rest"
            }
        }
        
        level = min(self.difficulty.value // 2 + 1, 3)
        pattern_data = basic_patterns[level]
        
        # Create incomplete pattern for puzzle
        full_pattern = pattern_data["pattern"] * 2  # Repeat for 2 measures
        self.rhythm_pattern = full_pattern[:-2]  # Remove last 2 beats
        self.completion_pattern = full_pattern[-2:]  # These are the answer
        
        self.pattern_description = pattern_data["description"]
        self.tempo_marking = pattern_data["tempo"]
        self.rhythm_notation = pattern_data["notation"]
        self.solution = "".join(self.completion_pattern)
    
    def _generate_syncopated_rhythm(self):
        """Generate syncopated rhythm patterns"""
        syncopated_patterns = {
            1: {  # Simple syncopation
                "pattern": ["●", "·", "○", "●", "·", "○", "●", "·"],
                "description": "Basic syncopation with off-beat accents",
                "tempo": "Swing (110 BPM)",
                "notation": "● = downbeat, ○ = syncopated accent"
            },
            2: {  # Jazz syncopation
                "pattern": ["●", "○", "·", "○", "●", "○", "·", "○"],
                "description": "Jazz-style syncopated pattern",
                "tempo": "Medium Swing (130 BPM)",
                "notation": "● = strong, ○ = syncopated, · = rest"
            },
            3: {  # Complex syncopation
                "pattern": ["●", "·", "○", "·", "○", "●", "○", "·"],
                "description": "Complex syncopated rhythm with displaced accents",
                "tempo": "Fast Swing (150 BPM)",
                "notation": "Irregular accent placement"
            }
        }
        
        level = min(self.difficulty.value // 2 + 1, 3)
        pattern_data = syncopated_patterns[level]
        
        # Create incomplete pattern
        full_pattern = pattern_data["pattern"] * 2
        self.rhythm_pattern = full_pattern[:-3]  # Remove last 3 beats for difficulty
        self.completion_pattern = full_pattern[-3:]
        
        self.pattern_description = pattern_data["description"]
        self.tempo_marking = pattern_data["tempo"]
        self.rhythm_notation = pattern_data["notation"]
        self.solution = "".join(self.completion_pattern)
    
    def _generate_complex_rhythm(self):
        """Generate complex rhythm patterns"""
        complex_patterns = {
            1: {  # 3/4 waltz
                "pattern": ["●", "○", "○", "●", "○", "○"],
                "description": "3/4 waltz pattern",
                "tempo": "Moderate Waltz (90 BPM)",
                "notation": "● = strong downbeat, ○ = light beats"
            },
            2: {  # 7/8 irregular
                "pattern": ["●", "○", "●", "○", "●", "○", "·"],
                "description": "Irregular 7/8 meter",
                "tempo": "Presto (160 BPM)",
                "notation": "Asymmetrical grouping"
            },
            3: {  # Polymetric feel
                "pattern": ["●", "○", "·", "○", "●", "·", "○", "●", "○"],
                "description": "Polymetric pattern with shifting accents",
                "tempo": "Variable (120-140 BPM)",
                "notation": "Accents shift across beats"
            }
        }
        
        level = min(self.difficulty.value // 2 + 1, 3)
        pattern_data = complex_patterns[level]
        
        # Create incomplete pattern
        full_pattern = pattern_data["pattern"] * 2
        remove_count = 2 + self.difficulty.value // 2
        self.rhythm_pattern = full_pattern[:-remove_count]
        self.completion_pattern = full_pattern[-remove_count:]
        
        self.pattern_description = pattern_data["description"]
        self.tempo_marking = pattern_data["tempo"]
        self.rhythm_notation = pattern_data["notation"]
        self.solution = "".join(self.completion_pattern)
    
    def _generate_polyrhythm(self):
        """Generate polyrhythmic patterns"""
        poly_patterns = {
            1: {  # 2 against 3
                "pattern": ["●", "○", "●", "○", "●", "○"],
                "description": "2 against 3 polyrhythm",
                "tempo": "Steady (100 BPM)",
                "notation": "Two rhythmic layers"
            },
            2: {  # 3 against 4
                "pattern": ["●", "○", "·", "○", "●", "○", "·", "○", "●", "○", "·", "○"],
                "description": "3 against 4 polyrhythm",
                "tempo": "Moderate (110 BPM)",
                "notation": "Complex rhythmic interaction"
            },
            3: {  # African polyrhythm
                "pattern": ["●", "○", "·", "●", "○", "●", "·", "○", "●", "○", "●", "·"],
                "description": "African-inspired polyrhythmic pattern",
                "tempo": "Driving (125 BPM)",
                "notation": "Interlocking rhythmic parts"
            }
        }
        
        level = min(self.difficulty.value // 2 + 1, 3)
        pattern_data = poly_patterns[level]
        
        # Create incomplete pattern
        full_pattern = pattern_data["pattern"]
        remove_count = 3 + self.difficulty.value // 3
        self.rhythm_pattern = full_pattern[:-remove_count]
        self.completion_pattern = full_pattern[-remove_count:]
        
        self.pattern_description = pattern_data["description"]
        self.tempo_marking = pattern_data["tempo"]
        self.rhythm_notation = pattern_data["notation"]
        self.solution = "".join(self.completion_pattern)
    
    def _generate_hints(self):
        """Generate hints for the puzzle"""
        # Hint 1: Rhythm type
        self.add_hint(1, f"Rhythm type: {self.rhythm_type.title()}", 100)
        
        # Hint 2: Pattern description
        if self.difficulty.value >= 2:
            self.add_hint(2, f"Pattern: {self.pattern_description}", 150)
        
        # Hint 3: Notation guide
        if self.difficulty.value >= 3:
            self.add_hint(3, f"Notation: {self.rhythm_notation}", 200)
        
        # Hint 4: Tempo information
        if self.difficulty.value >= 4:
            self.add_hint(4, f"Tempo: {self.tempo_marking}", 250)
        
        # Hint 5: First beat of solution
        if self.difficulty.value >= 4 and len(self.completion_pattern) > 0:
            first_beat = self.completion_pattern[0]
            self.add_hint(5, f"Next beat starts with: {first_beat}", 300)
    
    def validate_input(self, player_input: str) -> Tuple[bool, str]:
        """Validate player's rhythm completion"""
        player_input = player_input.strip()
        
        # Direct pattern match
        if player_input == self.solution:
            return True, f"🎵 Perfect! You completed the rhythm pattern correctly."
        
        # Check individual beats
        if len(player_input) == len(self.solution):
            correct_beats = sum(1 for a, b in zip(player_input, self.solution) if a == b)
            accuracy = correct_beats / len(self.solution)
            
            if accuracy >= 0.8:
                return False, f"Very close! {correct_beats}/{len(self.solution)} beats correct."
            elif accuracy >= 0.5:
                return False, f"Good attempt! {correct_beats}/{len(self.solution)} beats correct."
            else:
                return False, f"Incorrect rhythm. Expected: {self.solution}"
        
        # Try to match common rhythm descriptions
        rhythm_descriptions = {
            "strong": "●",
            "accent": "●", 
            "beat": "●",
            "weak": "○",
            "light": "○",
            "off": "○",
            "rest": "·",
            "pause": "·",
            "silence": "·"
        }
        
        # Convert description to pattern
        words = player_input.lower().split()
        converted_pattern = ""
        for word in words:
            if word in rhythm_descriptions:
                converted_pattern += rhythm_descriptions[word]
        
        if converted_pattern == self.solution:
            return True, f"🎵 Correct! You identified the rhythm pattern."
        
        return False, f"Incorrect. The pattern should be: {self.solution}\n(● = strong, ○ = weak, · = rest)"
    
    def get_current_display(self) -> List[str]:
        """Get the current puzzle display"""
        lines = []
        
        # Header
        lines.append(f"[bold cyan]🎵 RHYTHM PATTERN - {self.rhythm_type.upper()}[/bold cyan]")
        lines.append("=" * 60)
        lines.append("")
        
        # Puzzle info
        lines.append(f"[yellow]Rhythm Type:[/yellow] {self.rhythm_type.title()}")
        lines.append(f"[yellow]Difficulty:[/yellow] {self.difficulty.name}")
        lines.append("")
        
        # Pattern description
        lines.append("[cyan]═══ RHYTHM ANALYSIS ═══[/cyan]")
        lines.append(f"[white]Description:[/white] {self.pattern_description}")
        lines.append(f"[white]Tempo:[/white] {self.tempo_marking}")
        lines.append("")
        
        # Show rhythm pattern
        lines.append("[cyan]═══ RHYTHM PATTERN ═══[/cyan]")
        lines.append("")
        
        # Display current pattern with missing beats
        pattern_display = " ".join(self.rhythm_pattern)
        missing_count = len(self.completion_pattern)
        missing_display = " ".join(["?"] * missing_count)
        
        lines.append(f"Pattern: [green]{pattern_display}[/green] [red]{missing_display}[/red]")
        lines.append("")
        
        # Beat counting
        total_beats = len(self.rhythm_pattern) + len(self.completion_pattern)
        beat_numbers = " ".join([str(i % 8 + 1) for i in range(total_beats)])
        lines.append(f"Beat #:  [yellow]{beat_numbers}[/yellow]")
        lines.append("")
        
        # Notation guide
        lines.append("[cyan]═══ NOTATION GUIDE ═══[/cyan]")
        lines.append("● = Strong beat / Accent")
        lines.append("○ = Weak beat / Light accent") 
        lines.append("· = Rest / Silence")
        lines.append("")
        lines.append(f"[white]Pattern Info:[/white] {self.rhythm_notation}")
        lines.append("")
        
        # Instructions
        lines.append("[green]Instructions:[/green]")
        lines.append("• Analyze the existing rhythm pattern")
        lines.append("• Identify the rhythmic structure and tempo")
        lines.append(f"• Complete the missing {missing_count} beats")
        lines.append("• Use ●○· symbols or describe in words")
        lines.append("• Use [yellow]HINT[/yellow] for rhythm analysis help")
        
        return lines
    
    def get_progress_display(self) -> List[str]:
        """Get progress indicators"""
        lines = []
        
        lines.append("[cyan]═══ RHYTHM ANALYSIS PROGRESS ═══[/cyan]")
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
        
        lines.append(f"[yellow]Rhythm Type:[/yellow] {self.rhythm_type.title()}")
        lines.append(f"[yellow]Pattern Length:[/yellow] {len(self.rhythm_pattern)} + {len(self.completion_pattern)} beats")
        lines.append(f"[yellow]Tempo:[/yellow] {self.tempo_marking}")
        
        # Pattern complexity indicator
        complexity_levels = {
            "basic": "Fundamental Rhythms",
            "syncopated": "Off-beat Accents",
            "complex": "Irregular Meters",
            "polyrhythm": "Multiple Rhythmic Layers"
        }
        complexity = complexity_levels.get(self.rhythm_type, "Unknown Pattern")
        lines.append(f"[yellow]Complexity:[/yellow] {complexity}")
        
        return lines
    
    def start(self) -> bool:
        """Start the puzzle (compatibility method)"""
        return self.start_puzzle()
    
    def _on_puzzle_start(self) -> None:
        """Called when puzzle starts"""
        self.current_progress['rhythm_type'] = self.rhythm_type
        self.current_progress['rhythm_pattern'] = self.rhythm_pattern
        self.current_progress['pattern_description'] = self.pattern_description
        self.current_progress['start_time'] = time.time()
    
    def _on_puzzle_complete(self, result: PuzzleResult) -> None:
        """Called when puzzle completes"""
        self.current_progress['completion_time'] = time.time()
        self.current_progress['final_score'] = result.score
        self.current_progress['rhythm_completed'] = result.success
        self.current_progress['completion_pattern'] = self.completion_pattern 