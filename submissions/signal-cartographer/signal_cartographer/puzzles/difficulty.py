"""
Difficulty Scaling System for The Signal Cartographer
Manages puzzle difficulty progression and adaptive complexity
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import time
import random
import math

from .puzzle_base import PuzzleDifficulty


class DifficultyFactor(Enum):
    """Different factors that contribute to puzzle difficulty"""
    COMPLEXITY = "complexity"          # Basic puzzle complexity
    TIME_PRESSURE = "time_pressure"    # Time constraints
    PATTERN_OBSCURITY = "pattern_obscurity"  # How hidden patterns are
    NOISE_LEVEL = "noise_level"        # Amount of distraction/noise
    MULTI_STEP = "multi_step"          # Number of steps required
    PRECISION = "precision"            # Required accuracy level


class DifficultyProfile:
    """Profile defining difficulty characteristics for a puzzle type"""
    
    def __init__(self, name: str):
        self.name = name
        self.base_factors: Dict[DifficultyFactor, float] = {}
        self.scaling_rates: Dict[DifficultyFactor, float] = {}
        self.max_values: Dict[DifficultyFactor, float] = {}
        self.min_values: Dict[DifficultyFactor, float] = {}
        
    def set_factor(self, factor: DifficultyFactor, 
                  base_value: float, 
                  scaling_rate: float = 1.0,
                  max_value: float = 10.0,
                  min_value: float = 0.1):
        """Set difficulty factor parameters"""
        self.base_factors[factor] = base_value
        self.scaling_rates[factor] = scaling_rate
        self.max_values[factor] = max_value
        self.min_values[factor] = min_value
    
    def calculate_factor_value(self, factor: DifficultyFactor, difficulty: PuzzleDifficulty) -> float:
        """Calculate the actual value for a difficulty factor at given difficulty level"""
        if factor not in self.base_factors:
            return 1.0
        
        base = self.base_factors[factor]
        rate = self.scaling_rates[factor]
        max_val = self.max_values[factor]
        min_val = self.min_values[factor]
        
        # Scale based on difficulty level (1-6)
        multiplier = 1.0 + (difficulty.value - 1) * rate / 5.0
        scaled_value = base * multiplier
        
        # Clamp to min/max values
        return max(min_val, min(max_val, scaled_value))


class AdaptiveDifficulty:
    """Adaptive difficulty system that adjusts based on player performance"""
    
    def __init__(self):
        self.player_performance_history: List[Dict[str, Any]] = []
        self.current_difficulty_level = PuzzleDifficulty.NORMAL
        self.adaptation_threshold = 5  # Number of puzzles before adaptation
        self.success_rate_target = 0.7  # Target success rate
        self.adaptation_sensitivity = 0.3  # How quickly to adapt (0-1)
        
    def record_performance(self, success: bool, time_taken: float, 
                          difficulty: PuzzleDifficulty, hints_used: int) -> None:
        """Record a puzzle performance result"""
        performance = {
            'success': success,
            'time_taken': time_taken,
            'difficulty': difficulty,
            'hints_used': hints_used,
            'timestamp': time.time()
        }
        self.player_performance_history.append(performance)
        
        # Keep only recent history
        if len(self.player_performance_history) > 20:
            self.player_performance_history = self.player_performance_history[-20:]
    
    def get_recommended_difficulty(self) -> PuzzleDifficulty:
        """Get recommended difficulty based on recent performance"""
        if len(self.player_performance_history) < self.adaptation_threshold:
            return self.current_difficulty_level
        
        recent_performance = self.player_performance_history[-self.adaptation_threshold:]
        success_rate = sum(1 for p in recent_performance if p['success']) / len(recent_performance)
        
        # Calculate adjustment
        if success_rate > self.success_rate_target + 0.2:
            # Player doing very well, increase difficulty
            adjustment = 1
        elif success_rate > self.success_rate_target + 0.1:
            # Player doing well, slight increase
            adjustment = 0.5
        elif success_rate < self.success_rate_target - 0.2:
            # Player struggling, decrease difficulty
            adjustment = -1
        elif success_rate < self.success_rate_target - 0.1:
            # Player having some trouble, slight decrease
            adjustment = -0.5
        else:
            # Player performance is good, no change
            adjustment = 0
        
        # Apply adaptation sensitivity
        adjustment *= self.adaptation_sensitivity
        
        # Calculate new difficulty level
        current_value = self.current_difficulty_level.value
        new_value = max(1, min(6, current_value + adjustment))
        
        # Update current difficulty
        for difficulty in PuzzleDifficulty:
            if difficulty.value == int(round(new_value)):
                self.current_difficulty_level = difficulty
                break
        
        return self.current_difficulty_level
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of player performance"""
        if not self.player_performance_history:
            return {"message": "No performance data available"}
        
        recent_count = min(10, len(self.player_performance_history))
        recent = self.player_performance_history[-recent_count:]
        
        success_rate = sum(1 for p in recent if p['success']) / len(recent)
        avg_time = sum(p['time_taken'] for p in recent) / len(recent)
        avg_hints = sum(p['hints_used'] for p in recent) / len(recent)
        
        return {
            'recent_success_rate': success_rate,
            'average_completion_time': avg_time,
            'average_hints_used': avg_hints,
            'recommended_difficulty': self.current_difficulty_level.name,
            'total_puzzles_attempted': len(self.player_performance_history)
        }


class DifficultyScaler:
    """
    Main difficulty scaling system that manages puzzle complexity across all types
    """
    
    def __init__(self):
        self.difficulty_profiles: Dict[str, DifficultyProfile] = {}
        self.adaptive_system = AdaptiveDifficulty()
        self.signal_type_modifiers: Dict[str, float] = {}
        
        # Initialize default profiles
        self._initialize_default_profiles()
        self._initialize_signal_modifiers()
    
    def _initialize_default_profiles(self):
        """Initialize default difficulty profiles for different puzzle types"""
        
        # Pattern Recognition Profile
        pattern_profile = DifficultyProfile("pattern_recognition")
        pattern_profile.set_factor(DifficultyFactor.COMPLEXITY, 2.0, 1.5, 8.0, 1.0)
        pattern_profile.set_factor(DifficultyFactor.PATTERN_OBSCURITY, 1.5, 2.0, 10.0, 0.5)
        pattern_profile.set_factor(DifficultyFactor.NOISE_LEVEL, 1.0, 1.2, 5.0, 0.1)
        pattern_profile.set_factor(DifficultyFactor.TIME_PRESSURE, 1.0, 0.8, 3.0, 0.5)
        self.difficulty_profiles["pattern_recognition"] = pattern_profile
        
        # Cryptographic Profile
        crypto_profile = DifficultyProfile("cryptographic")
        crypto_profile.set_factor(DifficultyFactor.COMPLEXITY, 3.0, 2.0, 10.0, 1.5)
        crypto_profile.set_factor(DifficultyFactor.MULTI_STEP, 2.0, 1.8, 8.0, 1.0)
        crypto_profile.set_factor(DifficultyFactor.PRECISION, 2.5, 1.5, 9.0, 1.0)
        crypto_profile.set_factor(DifficultyFactor.TIME_PRESSURE, 1.5, 1.0, 4.0, 0.8)
        self.difficulty_profiles["cryptographic"] = crypto_profile
        
        # Spectral Analysis Profile
        spectral_profile = DifficultyProfile("spectral")
        spectral_profile.set_factor(DifficultyFactor.COMPLEXITY, 2.5, 1.8, 9.0, 1.2)
        spectral_profile.set_factor(DifficultyFactor.NOISE_LEVEL, 2.0, 2.2, 8.0, 0.5)
        spectral_profile.set_factor(DifficultyFactor.PRECISION, 3.0, 1.6, 10.0, 1.5)
        spectral_profile.set_factor(DifficultyFactor.TIME_PRESSURE, 1.2, 0.9, 3.5, 0.6)
        self.difficulty_profiles["spectral"] = spectral_profile
        
        # ASCII Manipulation Profile
        ascii_profile = DifficultyProfile("ascii_manipulation")
        ascii_profile.set_factor(DifficultyFactor.COMPLEXITY, 1.5, 1.2, 6.0, 0.8)
        ascii_profile.set_factor(DifficultyFactor.MULTI_STEP, 1.8, 1.5, 7.0, 1.0)
        ascii_profile.set_factor(DifficultyFactor.PATTERN_OBSCURITY, 1.2, 1.3, 5.0, 0.3)
        ascii_profile.set_factor(DifficultyFactor.TIME_PRESSURE, 0.8, 0.7, 2.5, 0.4)
        self.difficulty_profiles["ascii_manipulation"] = ascii_profile
        
        # Constellation Mapping Profile
        constellation_profile = DifficultyProfile("constellation_mapping")
        constellation_profile.set_factor(DifficultyFactor.COMPLEXITY, 2.2, 1.6, 8.5, 1.0)
        constellation_profile.set_factor(DifficultyFactor.PRECISION, 2.8, 1.7, 9.5, 1.3)
        constellation_profile.set_factor(DifficultyFactor.PATTERN_OBSCURITY, 2.0, 1.9, 8.0, 0.8)
        constellation_profile.set_factor(DifficultyFactor.TIME_PRESSURE, 1.3, 1.1, 4.0, 0.7)
        self.difficulty_profiles["constellation_mapping"] = constellation_profile
        
        # Temporal Sequencing Profile
        temporal_profile = DifficultyProfile("temporal_sequencing")
        temporal_profile.set_factor(DifficultyFactor.COMPLEXITY, 2.0, 1.4, 7.5, 1.0)
        temporal_profile.set_factor(DifficultyFactor.MULTI_STEP, 2.5, 2.0, 9.0, 1.2)
        temporal_profile.set_factor(DifficultyFactor.TIME_PRESSURE, 2.0, 1.8, 6.0, 1.0)
        temporal_profile.set_factor(DifficultyFactor.PRECISION, 1.8, 1.3, 7.0, 0.9)
        self.difficulty_profiles["temporal_sequencing"] = temporal_profile
    
    def _initialize_signal_modifiers(self):
        """Initialize signal type modifiers that affect difficulty"""
        self.signal_type_modifiers = {
            'AM': 1.0,           # Standard difficulty
            'FM': 1.2,           # Slightly harder
            'PSK': 1.5,          # More complex
            'Pulsed': 1.1,       # Slightly harder
            'Pulsed-Echo': 1.3,  # Complex timing
            'Unknown': 1.4,      # Uncertainty adds difficulty
            'Quantum': 2.0,      # Very complex
            'Ancient': 1.8,      # Historical complexity
            'Bio': 1.6,          # Organic patterns
        }
    
    def calculate_puzzle_parameters(self, 
                                  puzzle_type: str, 
                                  base_difficulty: PuzzleDifficulty,
                                  signal_data: Any = None,
                                  adaptive: bool = True) -> Dict[str, Any]:
        """
        Calculate specific puzzle parameters based on difficulty scaling
        
        Args:
            puzzle_type: Type of puzzle (e.g., "pattern_recognition")
            base_difficulty: Base difficulty level
            signal_data: Associated signal data for context
            adaptive: Whether to use adaptive difficulty
            
        Returns:
            Dictionary of puzzle parameters
        """
        # Get recommended difficulty if using adaptive system
        if adaptive:
            recommended_difficulty = self.adaptive_system.get_recommended_difficulty()
            # Blend base and recommended difficulty
            final_difficulty_value = (base_difficulty.value + recommended_difficulty.value) / 2
            final_difficulty = self._value_to_difficulty(final_difficulty_value)
        else:
            final_difficulty = base_difficulty
        
        # Get difficulty profile for puzzle type
        profile = self.difficulty_profiles.get(puzzle_type)
        if not profile:
            # Return basic parameters if no profile found
            return {
                'difficulty': final_difficulty,
                'max_attempts': 5,
                'time_limit': None,
                'complexity_factor': final_difficulty.value,
                'hint_cost_multiplier': 1.0
            }
        
        # Calculate factor values
        factors = {}
        for factor in DifficultyFactor:
            factors[factor.value] = profile.calculate_factor_value(factor, final_difficulty)
        
        # Apply signal type modifier if signal data available
        signal_modifier = 1.0
        if signal_data:
            signal_type = getattr(signal_data, 'modulation', 'Unknown')
            signal_modifier = self.signal_type_modifiers.get(signal_type, 1.0)
        
        # Calculate specific parameters
        complexity = factors[DifficultyFactor.COMPLEXITY.value] * signal_modifier
        max_attempts = max(3, int(8 - complexity / 2))
        
        # Time limit calculation (if time pressure factor exists)
        time_limit = None
        if DifficultyFactor.TIME_PRESSURE.value in factors:
            time_pressure = factors[DifficultyFactor.TIME_PRESSURE.value]
            if time_pressure > 1.5:  # Only add time limit for higher pressure
                base_time = 300  # 5 minutes
                time_limit = base_time / time_pressure
        
        # Hint cost multiplier
        hint_cost_multiplier = 1.0 + (final_difficulty.value - 1) * 0.2
        
        # Score multiplier based on difficulty
        score_multiplier = 1.0 + (final_difficulty.value - 1) * 0.3
        
        return {
            'difficulty': final_difficulty,
            'max_attempts': max_attempts,
            'time_limit': time_limit,
            'complexity_factor': complexity,
            'noise_level': factors.get(DifficultyFactor.NOISE_LEVEL.value, 1.0),
            'pattern_obscurity': factors.get(DifficultyFactor.PATTERN_OBSCURITY.value, 1.0),
            'multi_step_factor': factors.get(DifficultyFactor.MULTI_STEP.value, 1.0),
            'precision_requirement': factors.get(DifficultyFactor.PRECISION.value, 1.0),
            'hint_cost_multiplier': hint_cost_multiplier,
            'score_multiplier': score_multiplier,
            'signal_modifier': signal_modifier,
            'adaptive_difficulty_used': adaptive
        }
    
    def record_puzzle_performance(self, success: bool, time_taken: float, 
                                difficulty: PuzzleDifficulty, hints_used: int) -> None:
        """Record puzzle performance for adaptive system"""
        self.adaptive_system.record_performance(success, time_taken, difficulty, hints_used)
    
    def get_difficulty_recommendation(self, puzzle_type: str, signal_data: Any = None) -> PuzzleDifficulty:
        """Get difficulty recommendation for a specific puzzle type and signal"""
        base_recommendation = self.adaptive_system.get_recommended_difficulty()
        
        # Adjust based on signal complexity if available
        if signal_data:
            signal_type = getattr(signal_data, 'modulation', 'Unknown')
            signal_modifier = self.signal_type_modifiers.get(signal_type, 1.0)
            
            # If signal is complex, suggest slightly easier puzzle to compensate
            if signal_modifier > 1.5:
                adjusted_value = max(1, base_recommendation.value - 1)
                return self._value_to_difficulty(adjusted_value)
            elif signal_modifier > 1.2:
                adjusted_value = max(1, base_recommendation.value - 0.5)
                return self._value_to_difficulty(adjusted_value)
        
        return base_recommendation
    
    def get_performance_analysis(self) -> Dict[str, Any]:
        """Get detailed performance analysis"""
        return self.adaptive_system.get_performance_summary()
    
    def create_custom_profile(self, name: str, base_profile: str = None) -> DifficultyProfile:
        """Create a custom difficulty profile"""
        profile = DifficultyProfile(name)
        
        if base_profile and base_profile in self.difficulty_profiles:
            # Copy from base profile
            base = self.difficulty_profiles[base_profile]
            profile.base_factors = base.base_factors.copy()
            profile.scaling_rates = base.scaling_rates.copy()
            profile.max_values = base.max_values.copy()
            profile.min_values = base.min_values.copy()
        
        self.difficulty_profiles[name] = profile
        return profile
    
    def _value_to_difficulty(self, value: float) -> PuzzleDifficulty:
        """Convert numeric value to PuzzleDifficulty enum"""
        clamped_value = max(1, min(6, int(round(value))))
        for difficulty in PuzzleDifficulty:
            if difficulty.value == clamped_value:
                return difficulty
        return PuzzleDifficulty.NORMAL  # fallback
    
    def get_scaling_preview(self, puzzle_type: str, signal_type: str = None) -> Dict[str, List[Any]]:
        """Get a preview of how difficulty scales across all levels"""
        preview = {}
        
        for difficulty in PuzzleDifficulty:
            # Create mock signal data if signal type provided
            mock_signal = None
            if signal_type:
                class MockSignal:
                    def __init__(self, modulation):
                        self.modulation = modulation
                mock_signal = MockSignal(signal_type)
            
            params = self.calculate_puzzle_parameters(
                puzzle_type, 
                difficulty, 
                mock_signal, 
                adaptive=False
            )
            
            preview[difficulty.name] = {
                'max_attempts': params['max_attempts'],
                'time_limit': params['time_limit'],
                'complexity': round(params['complexity_factor'], 2),
                'score_multiplier': round(params['score_multiplier'], 2)
            }
        
        return preview 