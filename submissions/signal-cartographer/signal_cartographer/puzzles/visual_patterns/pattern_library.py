"""
Pattern Library System for Visual Pattern Matching
Stores and manages ASCII patterns, constellations, and symbols for puzzles
"""

from typing import Dict, List, Tuple, Optional, Any
import random
from dataclasses import dataclass


@dataclass
class PatternData:
    """Data structure for a pattern"""
    name: str
    ascii_art: List[str]
    description: str
    difficulty: int  # 1-5
    tags: List[str]
    metadata: Dict[str, Any]


@dataclass
class ConstellationData:
    """Data structure for constellation patterns"""
    name: str
    stars: List[Tuple[int, int]]  # Coordinate positions
    connecting_lines: List[Tuple[int, int]]  # Star index pairs to connect
    ascii_representation: List[str]
    mythology: str
    difficulty: int
    brightness_levels: Dict[int, int]  # Star index to brightness (1-5)


class PatternLibrary:
    """Library of ASCII patterns for visual matching puzzles"""
    
    def __init__(self):
        self.patterns: Dict[str, PatternData] = {}
        self.categories: Dict[str, List[str]] = {}
        self._initialize_basic_patterns()
    
    def _initialize_basic_patterns(self):
        """Initialize the library with basic patterns"""
        
        # Simple geometric patterns
        self.add_pattern(PatternData(
            name="triangle",
            ascii_art=[
                "    *    ",
                "   * *   ",
                "  *   *  ",
                " ******* "
            ],
            description="Basic triangle pattern",
            difficulty=1,
            tags=["geometric", "simple"],
            metadata={"shape": "triangle", "complexity": "low"}
        ))
        
        self.add_pattern(PatternData(
            name="diamond",
            ascii_art=[
                "    *    ",
                "   * *   ",
                "  *   *  ",
                " *     * ",
                "  *   *  ",
                "   * *   ",
                "    *    "
            ],
            description="Diamond shape pattern",
            difficulty=2,
            tags=["geometric", "symmetric"],
            metadata={"shape": "diamond", "complexity": "medium"}
        ))
        
        self.add_pattern(PatternData(
            name="cross",
            ascii_art=[
                "    *    ",
                "    *    ",
                "    *    ",
                " ******* ",
                "    *    ",
                "    *    ",
                "    *    "
            ],
            description="Cross or plus pattern",
            difficulty=1,
            tags=["geometric", "religious"],
            metadata={"shape": "cross", "complexity": "low"}
        ))
        
        # Signal-related patterns
        self.add_pattern(PatternData(
            name="wave_simple",
            ascii_art=[
                " *   *   ",
                "* * * * *",
                "   *   * "
            ],
            description="Simple wave pattern",
            difficulty=2,
            tags=["wave", "signal"],
            metadata={"type": "sine_wave", "frequency": "low"}
        ))
        
        self.add_pattern(PatternData(
            name="wave_complex",
            ascii_art=[
                "*     *     *",
                " *   * *   * ",
                "  * *   * *  ",
                "   *     *   "
            ],
            description="Complex wave interference pattern",
            difficulty=4,
            tags=["wave", "signal", "complex"],
            metadata={"type": "interference", "frequency": "mixed"}
        ))
        
        # Circuit patterns
        self.add_pattern(PatternData(
            name="circuit_basic",
            ascii_art=[
                " *---*---* ",
                " |   |   | ",
                " *---*---* ",
                "     |     ",
                "     *     "
            ],
            description="Basic circuit diagram",
            difficulty=3,
            tags=["circuit", "technical"],
            metadata={"type": "logic_gate", "complexity": "basic"}
        ))
        
        # Alien/Unknown patterns
        self.add_pattern(PatternData(
            name="alien_glyph_1",
            ascii_art=[
                "  * * *  ",
                " *  *  * ",
                "*   *   *",
                " * *** * ",
                "  *   *  "
            ],
            description="Unknown alien glyph pattern",
            difficulty=5,
            tags=["alien", "mysterious", "complex"],
            metadata={"origin": "unknown", "meaning": "undeciphered"}
        ))
        
        self.add_pattern(PatternData(
            name="spiral",
            ascii_art=[
                "    ***    ",
                "  **   **  ",
                " *       * ",
                "*    **   *",
                "*   *  *  *",
                "*    **   *",
                " *       * ",
                "  **   **  ",
                "    ***    "
            ],
            description="Spiral pattern",
            difficulty=4,
            tags=["spiral", "complex", "hypnotic"],
            metadata={"type": "fibonacci", "direction": "clockwise"}
        ))
        
        # Initialize categories
        self._build_categories()
    
    def add_pattern(self, pattern: PatternData):
        """Add a pattern to the library"""
        self.patterns[pattern.name] = pattern
        self._update_categories(pattern)
    
    def get_pattern(self, name: str) -> Optional[PatternData]:
        """Get a pattern by name"""
        return self.patterns.get(name)
    
    def get_patterns_by_difficulty(self, difficulty: int) -> List[PatternData]:
        """Get all patterns of a specific difficulty level"""
        return [p for p in self.patterns.values() if p.difficulty == difficulty]
    
    def get_patterns_by_tag(self, tag: str) -> List[PatternData]:
        """Get all patterns with a specific tag"""
        return [p for p in self.patterns.values() if tag in p.tags]
    
    def get_random_pattern(self, difficulty_range: Tuple[int, int] = (1, 5)) -> PatternData:
        """Get a random pattern within difficulty range"""
        valid_patterns = [
            p for p in self.patterns.values() 
            if difficulty_range[0] <= p.difficulty <= difficulty_range[1]
        ]
        return random.choice(valid_patterns) if valid_patterns else None
    
    def create_pattern_variant(self, pattern_name: str, variant_type: str = "rotate") -> Optional[PatternData]:
        """Create a variant of an existing pattern"""
        original = self.get_pattern(pattern_name)
        if not original:
            return None
        
        if variant_type == "rotate":
            return self._rotate_pattern(original)
        elif variant_type == "mirror":
            return self._mirror_pattern(original)
        elif variant_type == "noise":
            return self._add_noise_to_pattern(original)
        
        return None
    
    def _rotate_pattern(self, pattern: PatternData) -> PatternData:
        """Create a 90-degree rotated version of the pattern"""
        ascii_art = pattern.ascii_art
        if not ascii_art:
            return pattern
        
        # Transpose the matrix (rotate 90 degrees)
        max_width = max(len(line) for line in ascii_art)
        padded_lines = [line.ljust(max_width) for line in ascii_art]
        
        rotated = []
        for col in range(max_width):
            new_line = ""
            for row in range(len(padded_lines) - 1, -1, -1):
                new_line += padded_lines[row][col]
            rotated.append(new_line.rstrip())
        
        return PatternData(
            name=f"{pattern.name}_rotated",
            ascii_art=rotated,
            description=f"Rotated version of {pattern.description}",
            difficulty=pattern.difficulty + 1,  # Slightly harder
            tags=pattern.tags + ["rotated"],
            metadata={**pattern.metadata, "variant": "rotated"}
        )
    
    def _mirror_pattern(self, pattern: PatternData) -> PatternData:
        """Create a mirrored version of the pattern"""
        ascii_art = pattern.ascii_art
        mirrored = [line[::-1] for line in ascii_art]
        
        return PatternData(
            name=f"{pattern.name}_mirrored",
            ascii_art=mirrored,
            description=f"Mirrored version of {pattern.description}",
            difficulty=pattern.difficulty + 1,
            tags=pattern.tags + ["mirrored"],
            metadata={**pattern.metadata, "variant": "mirrored"}
        )
    
    def _add_noise_to_pattern(self, pattern: PatternData, noise_level: float = 0.1) -> PatternData:
        """Add random noise to a pattern"""
        ascii_art = pattern.ascii_art
        noisy = []
        
        for line in ascii_art:
            noisy_line = ""
            for char in line:
                if char == ' ' and random.random() < noise_level:
                    noisy_line += random.choice(['.', ':', '~'])
                elif char != ' ' and random.random() < noise_level * 0.5:
                    noisy_line += ' '  # Remove character
                else:
                    noisy_line += char
            noisy.append(noisy_line)
        
        return PatternData(
            name=f"{pattern.name}_noisy",
            ascii_art=noisy,
            description=f"Noisy version of {pattern.description}",
            difficulty=pattern.difficulty + 2,  # Much harder with noise
            tags=pattern.tags + ["noisy", "challenging"],
            metadata={**pattern.metadata, "variant": "noisy", "noise_level": noise_level}
        )
    
    def _build_categories(self):
        """Build category index"""
        self.categories = {}
        for pattern in self.patterns.values():
            for tag in pattern.tags:
                if tag not in self.categories:
                    self.categories[tag] = []
                self.categories[tag].append(pattern.name)
    
    def _update_categories(self, pattern: PatternData):
        """Update categories for a new pattern"""
        for tag in pattern.tags:
            if tag not in self.categories:
                self.categories[tag] = []
            if pattern.name not in self.categories[tag]:
                self.categories[tag].append(pattern.name)


class ConstellationLibrary:
    """Library of constellation patterns for constellation mapping puzzles"""
    
    def __init__(self):
        self.constellations: Dict[str, ConstellationData] = {}
        self._initialize_constellations()
    
    def _initialize_constellations(self):
        """Initialize with famous constellations"""
        
        # Big Dipper (Ursa Major part)
        self.add_constellation(ConstellationData(
            name="Ursa Major",
            stars=[(2, 8), (5, 7), (8, 6), (11, 5), (14, 4), (17, 6), (20, 8)],
            connecting_lines=[(0, 1), (1, 2), (2, 3), (3, 4), (2, 5), (5, 6)],
            ascii_representation=[
                "                    * ",
                "                     ",
                "               *     ",
                "                     ",
                "          *          ",
                "                     ",
                "     *               ",
                "                     ",
                "*       *            "
            ],
            mythology="The Great Bear constellation",
            difficulty=2,
            brightness_levels={0: 3, 1: 4, 2: 5, 3: 4, 4: 3, 5: 2, 6: 3}
        ))
        
        # Orion's Belt
        self.add_constellation(ConstellationData(
            name="Orion",
            stars=[(8, 2), (10, 5), (12, 8), (6, 10), (8, 12), (10, 14), (14, 10)],
            connecting_lines=[(0, 1), (1, 2), (3, 4), (4, 5), (2, 6)],
            ascii_representation=[
                "        *            ",
                "                     ",
                "      *   *          ",
                "                     ",
                "    *       *        ",
                "                     ",
                "      * * *          ",
                "                     ",
                "        *            "
            ],
            mythology="The Hunter constellation",
            difficulty=3,
            brightness_levels={0: 5, 1: 4, 2: 5, 3: 3, 4: 4, 5: 3, 6: 2}
        ))
        
        # Cassiopeia (W shape)
        self.add_constellation(ConstellationData(
            name="Cassiopeia",
            stars=[(2, 6), (6, 4), (10, 2), (14, 4), (18, 6)],
            connecting_lines=[(0, 1), (1, 2), (2, 3), (3, 4)],
            ascii_representation=[
                "          *          ",
                "                     ",
                "      *     *        ",
                "                     ",
                "  *             *    ",
                "                     ",
                "                     "
            ],
            mythology="The Queen constellation",
            difficulty=2,
            brightness_levels={0: 3, 1: 4, 2: 5, 3: 4, 4: 3}
        ))
        
        # Southern Cross
        self.add_constellation(ConstellationData(
            name="Southern Cross",
            stars=[(10, 3), (8, 7), (10, 11), (12, 7), (6, 9)],
            connecting_lines=[(0, 2), (1, 3), (4, 1)],  # Cross pattern
            ascii_representation=[
                "          *          ",
                "                     ",
                "                     ",
                "        *   *        ",
                "                     ",
                "      *              ",
                "                     ",
                "        *            ",
                "                     ",
                "                     ",
                "          *          "
            ],
            mythology="Navigation cross of the south",
            difficulty=3,
            brightness_levels={0: 5, 1: 4, 2: 5, 3: 4, 4: 2}
        ))
        
        # Custom alien constellation
        self.add_constellation(ConstellationData(
            name="Xenomorph",
            stars=[(5, 3), (10, 2), (15, 4), (8, 8), (12, 8), (10, 12), (7, 15), (13, 15)],
            connecting_lines=[(1, 0), (1, 2), (1, 3), (1, 4), (3, 5), (4, 5), (5, 6), (5, 7)],
            ascii_representation=[
                "     *    *    *     ",
                "                     ",
                "                     ",
                "        * *          ",
                "                     ",
                "                     ",
                "          *          ",
                "                     ",
                "       *   *         "
            ],
            mythology="Unknown alien star formation",
            difficulty=5,
            brightness_levels={0: 2, 1: 5, 2: 3, 3: 4, 4: 4, 5: 5, 6: 3, 7: 3}
        ))
    
    def add_constellation(self, constellation: ConstellationData):
        """Add a constellation to the library"""
        self.constellations[constellation.name] = constellation
    
    def get_constellation(self, name: str) -> Optional[ConstellationData]:
        """Get a constellation by name"""
        return self.constellations.get(name)
    
    def get_random_constellation(self, difficulty_range: Tuple[int, int] = (1, 5)) -> ConstellationData:
        """Get a random constellation within difficulty range"""
        valid_constellations = [
            c for c in self.constellations.values()
            if difficulty_range[0] <= c.difficulty <= difficulty_range[1]
        ]
        return random.choice(valid_constellations) if valid_constellations else None
    
    def create_constellation_fragment(self, constellation_name: str, fragment_size: float = 0.6) -> Optional[ConstellationData]:
        """Create a partial view of a constellation for fragment puzzles"""
        original = self.get_constellation(constellation_name)
        if not original:
            return None
        
        # Select a subset of stars
        num_stars_to_keep = max(3, int(len(original.stars) * fragment_size))
        kept_star_indices = random.sample(range(len(original.stars)), num_stars_to_keep)
        
        fragment_stars = [original.stars[i] for i in kept_star_indices]
        
        # Update connecting lines to only include connections between kept stars
        index_mapping = {old_idx: new_idx for new_idx, old_idx in enumerate(kept_star_indices)}
        fragment_lines = []
        
        for start, end in original.connecting_lines:
            if start in kept_star_indices and end in kept_star_indices:
                new_start = index_mapping[start]
                new_end = index_mapping[end]
                fragment_lines.append((new_start, new_end))
        
        # Create new ASCII representation (simplified for fragments)
        fragment_ascii = self._render_constellation_ascii(fragment_stars, fragment_lines)
        
        return ConstellationData(
            name=f"{constellation_name}_fragment",
            stars=fragment_stars,
            connecting_lines=fragment_lines,
            ascii_representation=fragment_ascii,
            mythology=f"Partial view of {original.mythology}",
            difficulty=original.difficulty + 1,
            brightness_levels={i: original.brightness_levels.get(kept_star_indices[i], 3) 
                             for i in range(len(fragment_stars))}
        )
    
    def _render_constellation_ascii(self, stars: List[Tuple[int, int]], 
                                  connecting_lines: List[Tuple[int, int]]) -> List[str]:
        """Render constellation as ASCII art"""
        if not stars:
            return []
        
        # Find bounds
        max_x = max(star[0] for star in stars)
        max_y = max(star[1] for star in stars)
        
        # Create grid
        grid = [[' ' for _ in range(max_x + 3)] for _ in range(max_y + 3)]
        
        # Place stars
        for star in stars:
            if 0 <= star[1] < len(grid) and 0 <= star[0] < len(grid[0]):
                grid[star[1]][star[0]] = '*'
        
        # Convert to strings
        return [''.join(row) for row in grid] 