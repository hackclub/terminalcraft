"""
Pattern Matching Algorithms for Visual Pattern Puzzles
Provides utilities for comparing, scoring, and matching ASCII patterns
"""

from typing import List, Tuple, Dict, Optional, Any
import math
import re
from dataclasses import dataclass

from .pattern_library import PatternData, ConstellationData


@dataclass
class MatchResult:
    """Result of pattern matching operation"""
    similarity_score: float  # 0.0 to 1.0
    match_confidence: float  # 0.0 to 1.0
    transformation_applied: str  # Type of transformation if any
    match_details: Dict[str, Any]


class PatternMatcher:
    """
    Utility class for pattern matching and similarity analysis
    """
    
    def __init__(self):
        self.similarity_threshold = 0.8  # Minimum similarity for a match
        self.noise_tolerance = 0.15  # How much noise to tolerate
        
    def compare_patterns(self, pattern1: List[str], pattern2: List[str]) -> MatchResult:
        """
        Compare two ASCII patterns and return similarity metrics
        
        Args:
            pattern1: First pattern as list of strings
            pattern2: Second pattern as list of strings
            
        Returns:
            MatchResult with similarity and confidence scores
        """
        # Normalize patterns (same size, clean format)
        norm1, norm2 = self._normalize_patterns(pattern1, pattern2)
        
        # Calculate basic similarity
        basic_similarity = self._calculate_basic_similarity(norm1, norm2)
        
        # Try rotations and transformations
        best_similarity = basic_similarity
        best_transformation = "none"
        
        # Check 90-degree rotations
        for rotation in [90, 180, 270]:
            rotated = self._rotate_pattern(norm2, rotation)
            similarity = self._calculate_basic_similarity(norm1, rotated)
            if similarity > best_similarity:
                best_similarity = similarity
                best_transformation = f"rotation_{rotation}"
        
        # Check mirror transformations
        mirrored_h = self._mirror_pattern(norm2, "horizontal")
        similarity = self._calculate_basic_similarity(norm1, mirrored_h)
        if similarity > best_similarity:
            best_similarity = similarity
            best_transformation = "mirror_horizontal"
        
        mirrored_v = self._mirror_pattern(norm2, "vertical")
        similarity = self._calculate_basic_similarity(norm1, mirrored_v)
        if similarity > best_similarity:
            best_similarity = similarity
            best_transformation = "mirror_vertical"
        
        # Calculate confidence based on pattern complexity and similarity
        confidence = self._calculate_confidence(norm1, norm2, best_similarity)
        
        # Detailed analysis
        details = {
            "pattern1_complexity": self._calculate_pattern_complexity(norm1),
            "pattern2_complexity": self._calculate_pattern_complexity(norm2),
            "character_match_ratio": self._calculate_character_match_ratio(norm1, norm2),
            "shape_similarity": self._calculate_shape_similarity(norm1, norm2),
            "noise_level": self._estimate_noise_level(norm1, norm2)
        }
        
        return MatchResult(
            similarity_score=best_similarity,
            match_confidence=confidence,
            transformation_applied=best_transformation,
            match_details=details
        )
    
    def find_pattern_in_library(self, target_pattern: List[str], 
                               pattern_library: Dict[str, PatternData],
                               min_similarity: float = None) -> List[Tuple[str, MatchResult]]:
        """
        Find matching patterns in a pattern library
        
        Args:
            target_pattern: Pattern to match
            pattern_library: Library of patterns to search
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of (pattern_name, match_result) tuples, sorted by similarity
        """
        if min_similarity is None:
            min_similarity = self.similarity_threshold
        
        matches = []
        
        for pattern_name, pattern_data in pattern_library.items():
            match_result = self.compare_patterns(target_pattern, pattern_data.ascii_art)
            
            if match_result.similarity_score >= min_similarity:
                matches.append((pattern_name, match_result))
        
        # Sort by similarity score (descending)
        matches.sort(key=lambda x: x[1].similarity_score, reverse=True)
        
        return matches
    
    def validate_constellation_answer(self, player_input: str, 
                                    target_constellation: ConstellationData,
                                    all_constellations: Dict[str, ConstellationData]) -> Tuple[bool, str, float]:
        """
        Validate player's constellation identification answer
        
        Args:
            player_input: Player's answer
            target_constellation: Correct constellation
            all_constellations: All available constellations
            
        Returns:
            Tuple of (is_correct, feedback_message, confidence_score)
        """
        player_input = player_input.strip().lower()
        target_name = target_constellation.name.lower()
        
        # Exact match
        if player_input == target_name:
            return True, f"Perfect! You correctly identified {target_constellation.name}!", 1.0
        
        # Partial match
        if player_input in target_name or target_name in player_input:
            similarity = len(player_input) / len(target_name)
            if similarity > 0.7:
                return True, f"Close enough! The constellation is {target_constellation.name}.", similarity
            else:
                return False, f"Partially correct - '{player_input}' is part of the answer.", similarity
        
        # Check against all constellation names for better feedback
        best_match = None
        best_similarity = 0.0
        
        for constellation_name, constellation_data in all_constellations.items():
            similarity = self._string_similarity(player_input, constellation_name.lower())
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = constellation_name
        
        if best_similarity > 0.6:
            return False, f"Not quite. You might be thinking of {best_match}, but that's not correct.", best_similarity
        else:
            return False, f"'{player_input}' doesn't match any known constellation.", 0.0
    
    def _normalize_patterns(self, pattern1: List[str], pattern2: List[str]) -> Tuple[List[str], List[str]]:
        """Normalize two patterns to same dimensions for comparison"""
        # Find maximum dimensions
        max_height = max(len(pattern1), len(pattern2))
        max_width = max(
            max(len(line) for line in pattern1) if pattern1 else 0,
            max(len(line) for line in pattern2) if pattern2 else 0
        )
        
        # Pad patterns to same size
        norm1 = []
        for i in range(max_height):
            if i < len(pattern1):
                line = pattern1[i].ljust(max_width)
            else:
                line = ' ' * max_width
            norm1.append(line)
        
        norm2 = []
        for i in range(max_height):
            if i < len(pattern2):
                line = pattern2[i].ljust(max_width)
            else:
                line = ' ' * max_width
            norm2.append(line)
        
        return norm1, norm2
    
    def _calculate_basic_similarity(self, pattern1: List[str], pattern2: List[str]) -> float:
        """Calculate basic character-by-character similarity"""
        if not pattern1 or not pattern2:
            return 0.0
        
        total_chars = 0
        matching_chars = 0
        
        for line1, line2 in zip(pattern1, pattern2):
            for char1, char2 in zip(line1, line2):
                total_chars += 1
                if char1 == char2:
                    matching_chars += 1
                elif self._chars_similar(char1, char2):
                    matching_chars += 0.5  # Partial credit for similar chars
        
        return matching_chars / total_chars if total_chars > 0 else 0.0
    
    def _chars_similar(self, char1: str, char2: str) -> bool:
        """Check if two characters are visually similar"""
        # Group similar characters
        similar_groups = [
            ['*', '•', '○', '●', '+'],  # Star-like characters
            ['.', ':', '·'],            # Small dots
            ['~', '-', '−'],            # Horizontal lines
            ['|', '│', '┃'],            # Vertical lines
            [' ', '\t']                 # Whitespace
        ]
        
        for group in similar_groups:
            if char1 in group and char2 in group:
                return True
        
        return False
    
    def _rotate_pattern(self, pattern: List[str], degrees: int) -> List[str]:
        """Rotate a pattern by specified degrees (90, 180, 270)"""
        if degrees == 90:
            # Rotate 90 degrees clockwise
            if not pattern:
                return []
            
            height = len(pattern)
            width = max(len(line) for line in pattern) if pattern else 0
            
            # Pad all lines to same width
            padded = [line.ljust(width) for line in pattern]
            
            rotated = []
            for col in range(width):
                new_line = ""
                for row in range(height - 1, -1, -1):
                    new_line += padded[row][col]
                rotated.append(new_line)
            
            return rotated
        
        elif degrees == 180:
            # Rotate 180 degrees
            return [line[::-1] for line in reversed(pattern)]
        
        elif degrees == 270:
            # Rotate 270 degrees (same as 90 counterclockwise)
            rotated_90 = self._rotate_pattern(pattern, 90)
            return self._rotate_pattern(rotated_90, 180)
        
        return pattern
    
    def _mirror_pattern(self, pattern: List[str], direction: str) -> List[str]:
        """Mirror a pattern horizontally or vertically"""
        if direction == "horizontal":
            return [line[::-1] for line in pattern]
        elif direction == "vertical":
            return list(reversed(pattern))
        return pattern
    
    def _calculate_pattern_complexity(self, pattern: List[str]) -> float:
        """Calculate complexity score of a pattern"""
        if not pattern:
            return 0.0
        
        total_chars = sum(len(line) for line in pattern)
        non_space_chars = sum(sum(1 for char in line if char.strip()) for line in pattern)
        
        if total_chars == 0:
            return 0.0
        
        # Basic complexity: ratio of non-space to total characters
        density = non_space_chars / total_chars
        
        # Pattern variation: number of different characters used
        unique_chars = set()
        for line in pattern:
            unique_chars.update(char for char in line if char.strip())
        
        char_variety = len(unique_chars) / 10.0  # Normalize to 0-1 range
        
        # Geometric complexity: changes in pattern structure
        geometric_complexity = self._calculate_geometric_complexity(pattern)
        
        # Combine factors
        complexity = (density * 0.4 + char_variety * 0.3 + geometric_complexity * 0.3)
        
        return min(1.0, complexity)
    
    def _calculate_geometric_complexity(self, pattern: List[str]) -> float:
        """Calculate geometric complexity based on pattern structure changes"""
        if not pattern:
            return 0.0
        
        changes = 0
        total_positions = 0
        
        # Count horizontal changes
        for line in pattern:
            for i in range(len(line) - 1):
                total_positions += 1
                if line[i] != line[i + 1]:
                    changes += 1
        
        # Count vertical changes
        for col in range(max(len(line) for line in pattern)):
            for row in range(len(pattern) - 1):
                total_positions += 1
                char1 = pattern[row][col] if col < len(pattern[row]) else ' '
                char2 = pattern[row + 1][col] if col < len(pattern[row + 1]) else ' '
                if char1 != char2:
                    changes += 1
        
        return changes / total_positions if total_positions > 0 else 0.0
    
    def _calculate_character_match_ratio(self, pattern1: List[str], pattern2: List[str]) -> float:
        """Calculate ratio of exactly matching characters"""
        if not pattern1 or not pattern2:
            return 0.0
        
        matches = 0
        total = 0
        
        for line1, line2 in zip(pattern1, pattern2):
            for char1, char2 in zip(line1, line2):
                total += 1
                if char1 == char2:
                    matches += 1
        
        return matches / total if total > 0 else 0.0
    
    def _calculate_shape_similarity(self, pattern1: List[str], pattern2: List[str]) -> float:
        """Calculate similarity based on overall shape rather than exact characters"""
        # Convert patterns to binary (space vs non-space)
        shape1 = self._pattern_to_shape(pattern1)
        shape2 = self._pattern_to_shape(pattern2)
        
        return self._calculate_basic_similarity(shape1, shape2)
    
    def _pattern_to_shape(self, pattern: List[str]) -> List[str]:
        """Convert pattern to binary shape representation"""
        shape = []
        for line in pattern:
            shape_line = ""
            for char in line:
                shape_line += '#' if char.strip() else ' '
            shape.append(shape_line)
        return shape
    
    def _estimate_noise_level(self, pattern1: List[str], pattern2: List[str]) -> float:
        """Estimate amount of noise/interference between patterns"""
        shape_similarity = self._calculate_shape_similarity(pattern1, pattern2)
        char_similarity = self._calculate_character_match_ratio(pattern1, pattern2)
        
        # If shape is similar but characters differ, there's likely noise
        noise_estimate = max(0.0, shape_similarity - char_similarity)
        
        return min(1.0, noise_estimate)
    
    def _calculate_confidence(self, pattern1: List[str], pattern2: List[str], similarity: float) -> float:
        """Calculate confidence score for the match"""
        # Base confidence on similarity
        base_confidence = similarity
        
        # Adjust based on pattern complexity (more complex = higher confidence when matched)
        complexity1 = self._calculate_pattern_complexity(pattern1)
        complexity2 = self._calculate_pattern_complexity(pattern2)
        avg_complexity = (complexity1 + complexity2) / 2
        
        # Boost confidence for complex patterns that match well
        complexity_boost = avg_complexity * 0.2 if similarity > 0.8 else 0
        
        # Reduce confidence for very simple patterns (could be coincidental)
        simplicity_penalty = 0.1 if avg_complexity < 0.3 else 0
        
        confidence = base_confidence + complexity_boost - simplicity_penalty
        
        return max(0.0, min(1.0, confidence))
    
    def _string_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using edit distance"""
        if not str1 or not str2:
            return 0.0
        
        # Simple edit distance calculation
        len1, len2 = len(str1), len(str2)
        if len1 == 0:
            return 0.0
        if len2 == 0:
            return 0.0
        
        # Create distance matrix
        distance = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        # Initialize first row and column
        for i in range(len1 + 1):
            distance[i][0] = i
        for j in range(len2 + 1):
            distance[0][j] = j
        
        # Calculate edit distance
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if str1[i-1] == str2[j-1] else 1
                distance[i][j] = min(
                    distance[i-1][j] + 1,      # deletion
                    distance[i][j-1] + 1,      # insertion
                    distance[i-1][j-1] + cost  # substitution
                )
        
        # Convert distance to similarity
        max_len = max(len1, len2)
        similarity = 1.0 - (distance[len1][len2] / max_len)
        
        return max(0.0, similarity) 