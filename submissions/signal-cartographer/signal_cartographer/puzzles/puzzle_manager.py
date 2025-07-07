"""
Puzzle Manager for The Signal Cartographer
Coordinates multiple puzzles, tracks progress, and manages puzzle sessions
"""

from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import time
import json
from dataclasses import dataclass, asdict

from .puzzle_base import BasePuzzle, PuzzleState, PuzzleResult, PuzzleDifficulty


class SessionState(Enum):
    """Enumeration of puzzle session states"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class PuzzleSession:
    """Data structure for a puzzle solving session"""
    session_id: str
    puzzle_id: str
    signal_id: str
    tool_name: str
    start_time: float
    end_time: Optional[float]
    state: SessionState
    results: Optional[PuzzleResult]
    player_progress: Dict[str, Any]


@dataclass
class AnalysisSession:
    """Complete analysis session containing multiple puzzle attempts"""
    session_id: str
    tool_name: str
    signal_id: str
    start_time: float
    end_time: Optional[float]
    puzzle_sessions: List[PuzzleSession]
    overall_score: int
    completion_status: str


class PuzzleManager:
    """
    Manages puzzle lifecycle, progress tracking, and session coordination
    """
    
    def __init__(self):
        self.active_puzzles: Dict[str, BasePuzzle] = {}
        self.puzzle_history: List[PuzzleSession] = []
        self.analysis_sessions: List[AnalysisSession] = []
        self.current_analysis_session: Optional[AnalysisSession] = None
        self.player_stats = {
            'puzzles_completed': 0,
            'total_score': 0,
            'average_score': 0,
            'puzzles_by_difficulty': {diff.name: 0 for diff in PuzzleDifficulty},
            'completion_rate': 0.0,
            'favorite_puzzle_type': None,
            'total_time_spent': 0.0,
            'hints_used_total': 0,
            'best_scores': {}
        }
        self.achievements = []
        
    def start_analysis_session(self, tool_name: str, signal_id: str) -> str:
        """
        Start a new analysis session for a specific tool and signal
        
        Args:
            tool_name: Name of the analysis tool being used
            signal_id: ID of the signal being analyzed
            
        Returns:
            Session ID for the new analysis session
        """
        session_id = f"analysis_{int(time.time())}_{tool_name}"
        
        self.current_analysis_session = AnalysisSession(
            session_id=session_id,
            tool_name=tool_name,
            signal_id=signal_id,
            start_time=time.time(),
            end_time=None,
            puzzle_sessions=[],
            overall_score=0,
            completion_status="in_progress"
        )
        
        return session_id
    
    def end_analysis_session(self) -> Optional[AnalysisSession]:
        """
        End the current analysis session
        
        Returns:
            Completed analysis session data
        """
        if not self.current_analysis_session:
            return None
        
        session = self.current_analysis_session
        session.end_time = time.time()
        
        # Calculate overall score from puzzle sessions
        if session.puzzle_sessions:
            total_score = sum(ps.results.score for ps in session.puzzle_sessions if ps.results)
            session.overall_score = total_score
            
            # Determine completion status
            completed_puzzles = sum(1 for ps in session.puzzle_sessions 
                                  if ps.results and ps.results.success)
            if completed_puzzles > 0:
                session.completion_status = "completed"
            else:
                session.completion_status = "failed"
        else:
            session.completion_status = "abandoned"
        
        self.analysis_sessions.append(session)
        self.current_analysis_session = None
        
        return session
    
    def register_puzzle(self, puzzle: BasePuzzle) -> bool:
        """
        Register a puzzle with the manager
        
        Args:
            puzzle: Puzzle instance to register
            
        Returns:
            True if registration successful
        """
        if puzzle.puzzle_id in self.active_puzzles:
            return False
        
        self.active_puzzles[puzzle.puzzle_id] = puzzle
        return True
    
    def start_puzzle(self, puzzle_id: str) -> Tuple[bool, str]:
        """
        Start a puzzle by ID
        
        Args:
            puzzle_id: ID of puzzle to start
            
        Returns:
            Tuple of (success, message)
        """
        if puzzle_id not in self.active_puzzles:
            return False, f"Puzzle {puzzle_id} not found"
        
        puzzle = self.active_puzzles[puzzle_id]
        
        if not puzzle.start_puzzle():
            return False, f"Could not start puzzle {puzzle_id}"
        
        # Create puzzle session
        session = PuzzleSession(
            session_id=f"session_{int(time.time())}_{puzzle_id}",
            puzzle_id=puzzle_id,
            signal_id=getattr(puzzle.signal_data, 'id', 'unknown') if puzzle.signal_data else 'none',
            tool_name=self._get_tool_name_for_puzzle(puzzle),
            start_time=time.time(),
            end_time=None,
            state=SessionState.ACTIVE,
            results=None,
            player_progress={}
        )
        
        # Add to current analysis session if active
        if self.current_analysis_session:
            self.current_analysis_session.puzzle_sessions.append(session)
        
        return True, f"Puzzle {puzzle.name} started successfully"
    
    def submit_puzzle_answer(self, puzzle_id: str, answer: str) -> Tuple[bool, PuzzleResult]:
        """
        Submit an answer for a puzzle
        
        Args:
            puzzle_id: ID of the puzzle
            answer: Player's answer
            
        Returns:
            Tuple of (puzzle_exists, result)
        """
        if puzzle_id not in self.active_puzzles:
            return False, None
        
        puzzle = self.active_puzzles[puzzle_id]
        result = puzzle.submit_answer(answer)
        
        # Update session with result
        self._update_session_result(puzzle_id, result)
        
        # Update player stats if puzzle completed
        if result.success or puzzle.state in [PuzzleState.FAILED, PuzzleState.ABANDONED]:
            self._update_player_stats(puzzle, result)
            self._check_achievements(puzzle, result)
        
        return True, result
    
    def get_puzzle_hint(self, puzzle_id: str, level: int = 1) -> Optional[str]:
        """
        Get a hint for a puzzle
        
        Args:
            puzzle_id: ID of the puzzle
            level: Hint level requested
            
        Returns:
            Hint text if available, None otherwise
        """
        if puzzle_id not in self.active_puzzles:
            return None
        
        puzzle = self.active_puzzles[puzzle_id]
        hint = puzzle.get_hint(level)
        
        if hint:
            return hint.text
        
        return None
    
    def pause_puzzle(self, puzzle_id: str) -> bool:
        """Pause a puzzle"""
        if puzzle_id not in self.active_puzzles:
            return False
        
        puzzle = self.active_puzzles[puzzle_id]
        success = puzzle.pause_puzzle()
        
        if success:
            self._update_session_state(puzzle_id, SessionState.PAUSED)
        
        return success
    
    def resume_puzzle(self, puzzle_id: str) -> bool:
        """Resume a paused puzzle"""
        if puzzle_id not in self.active_puzzles:
            return False
        
        puzzle = self.active_puzzles[puzzle_id]
        success = puzzle.resume_puzzle()
        
        if success:
            self._update_session_state(puzzle_id, SessionState.ACTIVE)
        
        return success
    
    def abandon_puzzle(self, puzzle_id: str) -> Optional[PuzzleResult]:
        """Abandon a puzzle"""
        if puzzle_id not in self.active_puzzles:
            return None
        
        puzzle = self.active_puzzles[puzzle_id]
        result = puzzle.abandon_puzzle()
        
        self._update_session_result(puzzle_id, result)
        self._update_player_stats(puzzle, result)
        
        return result
    
    def reset_puzzle(self, puzzle_id: str) -> bool:
        """Reset a puzzle to initial state"""
        if puzzle_id not in self.active_puzzles:
            return False
        
        puzzle = self.active_puzzles[puzzle_id]
        return puzzle.reset_puzzle()
    
    def get_puzzle_status(self, puzzle_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a puzzle"""
        if puzzle_id not in self.active_puzzles:
            return None
        
        puzzle = self.active_puzzles[puzzle_id]
        return puzzle.get_status_summary()
    
    def get_active_puzzles(self) -> List[Dict[str, Any]]:
        """Get list of all active puzzles"""
        return [puzzle.get_status_summary() for puzzle in self.active_puzzles.values()]
    
    def get_player_statistics(self) -> Dict[str, Any]:
        """Get comprehensive player statistics"""
        stats = self.player_stats.copy()
        
        # Calculate additional runtime stats
        if self.puzzle_history:
            completed_puzzles = [ps for ps in self.puzzle_history if ps.results and ps.results.success]
            stats['completion_rate'] = len(completed_puzzles) / len(self.puzzle_history) * 100
            
            if completed_puzzles:
                avg_score = sum(ps.results.score for ps in completed_puzzles) / len(completed_puzzles)
                stats['average_score'] = int(avg_score)
        
        # Add session information
        stats['active_sessions'] = len([s for s in self.analysis_sessions if s.completion_status == "in_progress"])
        stats['total_sessions'] = len(self.analysis_sessions)
        
        return stats
    
    def get_puzzle_recommendations(self, signal_data: Any = None) -> List[str]:
        """
        Get puzzle recommendations based on player performance and signal type
        
        Args:
            signal_data: Signal data to base recommendations on
            
        Returns:
            List of recommended puzzle types
        """
        recommendations = []
        
        # Analyze player performance by difficulty
        stats = self.get_player_statistics()
        
        # Recommend based on completion rate and difficulty comfort zone
        completion_rate = stats.get('completion_rate', 0)
        
        if completion_rate > 80:
            recommendations.append("Try harder difficulty puzzles for better rewards")
        elif completion_rate < 40:
            recommendations.append("Consider easier puzzles to build confidence")
        
        # Signal-specific recommendations
        if signal_data:
            signal_type = getattr(signal_data, 'modulation', 'Unknown')
            if signal_type == 'AM':
                recommendations.append("Pattern recognition puzzles work well with AM signals")
            elif signal_type in ['FM', 'PSK']:
                recommendations.append("Cryptographic analysis recommended for complex modulation")
        
        if not recommendations:
            recommendations.append("Continue with current difficulty level")
        
        return recommendations
    
    def export_progress_data(self) -> Dict[str, Any]:
        """Export all progress data for saving"""
        return {
            'player_stats': self.player_stats,
            'achievements': self.achievements,
            'analysis_sessions': [asdict(session) for session in self.analysis_sessions],
            'puzzle_history': [asdict(ps) for ps in self.puzzle_history]
        }
    
    def import_progress_data(self, data: Dict[str, Any]) -> bool:
        """Import progress data from save"""
        try:
            self.player_stats = data.get('player_stats', self.player_stats)
            self.achievements = data.get('achievements', [])
            
            # Reconstruct analysis sessions
            session_data = data.get('analysis_sessions', [])
            self.analysis_sessions = []
            for s_data in session_data:
                # Convert puzzle sessions
                puzzle_sessions = []
                for ps_data in s_data.get('puzzle_sessions', []):
                    ps = PuzzleSession(**ps_data)
                    puzzle_sessions.append(ps)
                
                s_data['puzzle_sessions'] = puzzle_sessions
                session = AnalysisSession(**s_data)
                self.analysis_sessions.append(session)
            
            # Reconstruct puzzle history
            history_data = data.get('puzzle_history', [])
            self.puzzle_history = [PuzzleSession(**ps_data) for ps_data in history_data]
            
            return True
        except Exception as e:
            print(f"Error importing progress data: {e}")
            return False
    
    def _get_tool_name_for_puzzle(self, puzzle: BasePuzzle) -> str:
        """Get the tool name associated with a puzzle"""
        # This would be implemented based on how puzzles are categorized
        # For now, return a generic name
        return "unknown_tool"
    
    def _update_session_result(self, puzzle_id: str, result: PuzzleResult) -> None:
        """Update the session with puzzle result"""
        # Find the most recent session for this puzzle
        if self.current_analysis_session:
            for session in reversed(self.current_analysis_session.puzzle_sessions):
                if session.puzzle_id == puzzle_id and session.results is None:
                    session.results = result
                    session.end_time = time.time()
                    session.state = SessionState.COMPLETED
                    break
    
    def _update_session_state(self, puzzle_id: str, state: SessionState) -> None:
        """Update session state"""
        if self.current_analysis_session:
            for session in reversed(self.current_analysis_session.puzzle_sessions):
                if session.puzzle_id == puzzle_id:
                    session.state = state
                    break
    
    def _update_player_stats(self, puzzle: BasePuzzle, result: PuzzleResult) -> None:
        """Update player statistics with puzzle result"""
        if result.success:
            self.player_stats['puzzles_completed'] += 1
            self.player_stats['total_score'] += result.score
            
            # Update difficulty stats
            diff_name = puzzle.difficulty.name
            self.player_stats['puzzles_by_difficulty'][diff_name] += 1
            
            # Update best score for this puzzle type
            puzzle_type = type(puzzle).__name__
            current_best = self.player_stats['best_scores'].get(puzzle_type, 0)
            if result.score > current_best:
                self.player_stats['best_scores'][puzzle_type] = result.score
        
        # Update total time spent
        self.player_stats['total_time_spent'] += result.time_taken
        self.player_stats['hints_used_total'] += result.hints_used
    
    def _check_achievements(self, puzzle: BasePuzzle, result: PuzzleResult) -> None:
        """Check for new achievements based on puzzle completion"""
        new_achievements = []
        
        # First puzzle completion
        if result.success and self.player_stats['puzzles_completed'] == 1:
            new_achievements.append("First Steps - Completed your first puzzle")
        
        # Perfect score achievement
        if result.success and result.score >= puzzle.max_score:
            new_achievements.append("Perfect Analysis - Achieved maximum score")
        
        # Speed achievements
        if result.success and result.time_taken < 60:
            new_achievements.append("Lightning Fast - Completed puzzle in under 1 minute")
        
        # Difficulty achievements
        if result.success and puzzle.difficulty == PuzzleDifficulty.EXPERT:
            new_achievements.append("Expert Analyst - Completed an Expert level puzzle")
        
        # No hints achievement
        if result.success and result.hints_used == 0:
            new_achievements.append("Independent Thinker - Completed puzzle without hints")
        
        # Add new achievements
        for achievement in new_achievements:
            if achievement not in self.achievements:
                self.achievements.append(achievement)
    
    def clear_completed_puzzles(self) -> int:
        """Remove completed puzzles from active list"""
        completed_ids = []
        for puzzle_id, puzzle in self.active_puzzles.items():
            if puzzle.state in [PuzzleState.COMPLETED, PuzzleState.FAILED, PuzzleState.ABANDONED]:
                completed_ids.append(puzzle_id)
        
        for puzzle_id in completed_ids:
            del self.active_puzzles[puzzle_id]
        
        return len(completed_ids) 