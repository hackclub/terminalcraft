"""
Progression System for The Signal Cartographer
Handles upgrades, achievements, and player progression
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class Upgrade:
    """Represents a player upgrade"""
    id: str
    name: str
    description: str
    cost: int  # Number of analyses required
    unlocked: bool = False
    purchased: bool = False
    effect_value: float = 0.0
    icon: str = "⚙️"

@dataclass 
class Achievement:
    """Represents a player achievement"""
    id: str
    name: str
    description: str
    unlocked: bool = False
    unlock_date: Optional[str] = None
    progress: int = 0
    target: int = 1
    category: str = "general"
    icon: str = "🏆"
    hidden: bool = False

class ProgressionSystem:
    """Manages player upgrades and achievements"""
    
    def __init__(self):
        self.analysis_points = 0  # Currency earned from analyses
        self.upgrades = self._initialize_upgrades()
        self.achievements = self._initialize_achievements()
        self.stats = {
            'total_scans': 0,
            'total_analyses': 0,
            'sectors_discovered': 0,
            'signals_found': 0,
            'unique_signals': set(),
            'play_time_minutes': 0,
            'session_start': datetime.now().isoformat()
        }
        
    def _initialize_upgrades(self) -> Dict[str, Upgrade]:
        """Initialize the 4 core upgrades"""
        upgrades = {}
        
        # Scanner Sensitivity - detect more signals
        upgrades['scanner_sensitivity'] = Upgrade(
            id='scanner_sensitivity',
            name='Scanner Sensitivity',
            description='Increases signal detection range, finding weaker signals',
            cost=5,
            effect_value=1.0,  # +1 signal detection range
            icon='📡'
        )
        
        # Signal Amplifier - boost signal strength readings
        upgrades['signal_amplifier'] = Upgrade(
            id='signal_amplifier', 
            name='Signal Amplifier',
            description='Amplifies signal strength readings by 20%',
            cost=8,
            effect_value=0.2,  # +20% signal strength
            icon='🔊'
        )
        
        # Frequency Filter - reduce noise
        upgrades['frequency_filter'] = Upgrade(
            id='frequency_filter',
            name='Frequency Filter',
            description='Reduces background noise for clearer signal detection',
            cost=12,
            effect_value=0.3,  # -30% noise
            icon='🔧'
        )
        
        # Deep Space Antenna - detect distant sectors
        upgrades['deep_space_antenna'] = Upgrade(
            id='deep_space_antenna',
            name='Deep Space Antenna',
            description='Enables detection of extremely distant sectors',
            cost=20,
            effect_value=2.0,  # +2 sector detection range
            icon='📻'
        )
        
        return upgrades
        
    def _initialize_achievements(self) -> Dict[str, Achievement]:
        """Initialize the 10 core achievements"""
        achievements = {}
        
        # Basic progression achievements
        achievements['first_contact'] = Achievement(
            id='first_contact',
            name='First Contact',
            description='Analyze your first signal',
            target=1,
            category='analysis',
            icon='👽'
        )
        
        achievements['explorer'] = Achievement(
            id='explorer', 
            name='Explorer',
            description='Discover all 5 sectors',
            target=5,
            category='exploration',
            icon='🗺️'
        )
        
        achievements['signal_hunter'] = Achievement(
            id='signal_hunter',
            name='Signal Hunter', 
            description='Find 10 different signals',
            target=10,
            category='collection',
            icon='🎯'
        )
        
        achievements['master_analyst'] = Achievement(
            id='master_analyst',
            name='Master Analyst',
            description='Complete 50 analyses',
            target=50,
            category='analysis',
            icon='🔬'
        )
        
        achievements['deep_space_pioneer'] = Achievement(
            id='deep_space_pioneer',
            name='Deep Space Pioneer',
            description='Reach EPSILON-5 sector',
            target=1,
            category='exploration',
            icon='🚀'
        )
        
        # Advanced achievements
        achievements['speed_scanner'] = Achievement(
            id='speed_scanner',
            name='Speed Scanner',
            description='Complete 10 scans in 5 minutes',
            target=10,
            category='efficiency',
            icon='⚡',
            hidden=True
        )
        
        achievements['perfectionist'] = Achievement(
            id='perfectionist',
            name='Perfectionist',
            description='Analyze 5 signals with 100% success rate',
            target=5,
            category='skill',
            icon='💎',
            hidden=True
        )
        
        achievements['code_breaker'] = Achievement(
            id='code_breaker',
            name='Code Breaker',
            description='Successfully decrypt 3 cryptographic signals',
            target=3,
            category='analysis',
            icon='🔐'
        )
        
        achievements['constellation_mapper'] = Achievement(
            id='constellation_mapper',
            name='Constellation Mapper',
            description='Use constellation mapping on 5 different signals',
            target=5,
            category='tools',
            icon='⭐'
        )
        
        achievements['void_whisperer'] = Achievement(
            id='void_whisperer',
            name='Void Whisperer',
            description='Play for 2 hours total',
            target=120,  # 120 minutes
            category='dedication',
            icon='🌌'
        )
        
        return achievements
    
    def earn_analysis_points(self, points: int):
        """Award analysis points for completing analyses"""
        self.analysis_points += points
        self._check_upgrade_unlocks()
        
    def can_purchase_upgrade(self, upgrade_id: str) -> bool:
        """Check if player can purchase an upgrade"""
        upgrade = self.upgrades.get(upgrade_id)
        if not upgrade:
            return False
        return (upgrade.unlocked and 
                not upgrade.purchased and 
                self.analysis_points >= upgrade.cost)
    
    def purchase_upgrade(self, upgrade_id: str) -> bool:
        """Purchase an upgrade"""
        if not self.can_purchase_upgrade(upgrade_id):
            return False
            
        upgrade = self.upgrades[upgrade_id]
        self.analysis_points -= upgrade.cost
        upgrade.purchased = True
        return True
    
    def _check_upgrade_unlocks(self):
        """Check if any upgrades should be unlocked"""
        # Unlock upgrades based on analysis points
        if self.analysis_points >= 3:
            self.upgrades['scanner_sensitivity'].unlocked = True
        if self.analysis_points >= 6:
            self.upgrades['signal_amplifier'].unlocked = True
        if self.analysis_points >= 10:
            self.upgrades['frequency_filter'].unlocked = True
        if self.analysis_points >= 15:
            self.upgrades['deep_space_antenna'].unlocked = True
    
    def update_stat(self, stat_name: str, value: Any):
        """Update a tracking statistic"""
        if stat_name in self.stats:
            if stat_name == 'unique_signals' and isinstance(value, str):
                self.stats[stat_name].add(value)
            else:
                self.stats[stat_name] = value
        self._check_achievements()
    
    def increment_stat(self, stat_name: str, amount: int = 1):
        """Increment a tracking statistic"""
        if stat_name in self.stats:
            if stat_name == 'unique_signals':
                return  # Use update_stat for sets
            self.stats[stat_name] += amount
        self._check_achievements()
    
    def _check_achievements(self):
        """Check if any achievements should be unlocked"""
        # First Contact
        if (self.stats['total_analyses'] >= 1 and 
            not self.achievements['first_contact'].unlocked):
            self._unlock_achievement('first_contact')
        
        # Explorer - all 5 sectors
        if (self.stats['sectors_discovered'] >= 5 and
            not self.achievements['explorer'].unlocked):
            self._unlock_achievement('explorer')
        
        # Signal Hunter - 10 different signals
        if (len(self.stats['unique_signals']) >= 10 and
            not self.achievements['signal_hunter'].unlocked):
            self._unlock_achievement('signal_hunter')
        
        # Master Analyst - 50 analyses
        if (self.stats['total_analyses'] >= 50 and
            not self.achievements['master_analyst'].unlocked):
            self._unlock_achievement('master_analyst')
        
        # Void Whisperer - 2 hours play time
        if (self.stats['play_time_minutes'] >= 120 and
            not self.achievements['void_whisperer'].unlocked):
            self._unlock_achievement('void_whisperer')
        
        # Update achievement progress
        for achievement in self.achievements.values():
            if not achievement.unlocked:
                if achievement.id == 'explorer':
                    achievement.progress = self.stats['sectors_discovered']
                elif achievement.id == 'signal_hunter':
                    achievement.progress = len(self.stats['unique_signals'])
                elif achievement.id == 'master_analyst':
                    achievement.progress = self.stats['total_analyses']
                elif achievement.id == 'void_whisperer':
                    achievement.progress = self.stats['play_time_minutes']
    
    def _unlock_achievement(self, achievement_id: str):
        """Unlock an achievement"""
        achievement = self.achievements.get(achievement_id)
        if achievement and not achievement.unlocked:
            achievement.unlocked = True
            achievement.unlock_date = datetime.now().isoformat()
            achievement.progress = achievement.target
            return True
        return False
    
    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get all unlocked achievements"""
        return [ach for ach in self.achievements.values() if ach.unlocked]
    
    def get_available_upgrades(self) -> List[Upgrade]:
        """Get all available (unlocked but not purchased) upgrades"""
        return [up for up in self.upgrades.values() 
                if up.unlocked and not up.purchased]
    
    def get_purchased_upgrades(self) -> List[Upgrade]:
        """Get all purchased upgrades"""
        return [up for up in self.upgrades.values() if up.purchased]
    
    def get_progression_summary(self) -> Dict[str, Any]:
        """Get a summary of player progression"""
        return {
            'analysis_points': self.analysis_points,
            'achievements_unlocked': len(self.get_unlocked_achievements()),
            'total_achievements': len(self.achievements),
            'upgrades_purchased': len(self.get_purchased_upgrades()),
            'total_upgrades': len(self.upgrades),
            'stats': dict(self.stats),
            'next_unlock': self._get_next_unlock()
        }
    
    def _get_next_unlock(self) -> Optional[str]:
        """Get the next achievement or upgrade that's close to unlocking"""
        # Find closest achievement
        closest_ach = None
        closest_distance = float('inf')
        
        for ach in self.achievements.values():
            if not ach.unlocked and not ach.hidden:
                distance = ach.target - ach.progress
                if 0 < distance < closest_distance:
                    closest_distance = distance
                    closest_ach = ach.name
        
        return closest_ach
    
    def to_save_data(self) -> Dict[str, Any]:
        """Convert progression to save data"""
        return {
            'analysis_points': self.analysis_points,
            'upgrades': {uid: {
                'unlocked': up.unlocked,
                'purchased': up.purchased
            } for uid, up in self.upgrades.items()},
            'achievements': {aid: {
                'unlocked': ach.unlocked,
                'unlock_date': ach.unlock_date,
                'progress': ach.progress
            } for aid, ach in self.achievements.items()},
            'stats': dict(self.stats)
        }
    
    def load_save_data(self, save_data: Dict[str, Any]):
        """Load progression from save data"""
        self.analysis_points = save_data.get('analysis_points', 0)
        
        # Load upgrades
        upgrade_data = save_data.get('upgrades', {})
        for uid, data in upgrade_data.items():
            if uid in self.upgrades:
                self.upgrades[uid].unlocked = data.get('unlocked', False)
                self.upgrades[uid].purchased = data.get('purchased', False)
        
        # Load achievements
        achievement_data = save_data.get('achievements', {})
        for aid, data in achievement_data.items():
            if aid in self.achievements:
                self.achievements[aid].unlocked = data.get('unlocked', False)
                self.achievements[aid].unlock_date = data.get('unlock_date')
                self.achievements[aid].progress = data.get('progress', 0)
        
        # Load stats
        stats_data = save_data.get('stats', {})
        for stat_name, value in stats_data.items():
            if stat_name == 'unique_signals':
                self.stats[stat_name] = set(value) if isinstance(value, list) else set()
            else:
                self.stats[stat_name] = value 