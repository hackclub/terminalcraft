"""Utility helper functions for TerminalOS."""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Tuple, List, Optional, Dict, Any
import importlib.util

from .logger import get_logger

logger = get_logger(__name__)


def get_terminal_size() -> Tuple[int, int]:
    """Get current terminal size."""
    try:
        size = shutil.get_terminal_size(fallback=(80, 24))
        return size.columns, size.lines
    except Exception:
        return 80, 24


def check_dependencies() -> bool:
    """Check if all required dependencies are available."""
    required_packages = [
        'textual',
        'rich',
        'click',
        'psutil',
        'pyfiglet',
        'pygments',
        'watchdog',
        'yaml'
    ]
    
    missing = []
    for package in required_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        logger.error(f"Missing required packages: {', '.join(missing)}")
        return False
    
    return True


def run_command(command: str, capture_output: bool = True, timeout: int = 30) -> Dict[str, Any]:
    """Run a shell command and return result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=capture_output,
            text=True,
            timeout=timeout
        )
        
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout if capture_output else '',
            'stderr': result.stderr if capture_output else '',
        }
    
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': f'Command timed out after {timeout}s',
        }
    
    except Exception as e:
        return {
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': str(e),
        }


def format_bytes(bytes_value: int) -> str:
    """Format bytes in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} EB"


def format_duration(seconds: float) -> str:
    """Format duration in human readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}h"
    else:
        days = seconds / 86400
        return f"{days:.1f}d"


def safe_path_join(base: Path, *parts: str) -> Path:
    """Safely join path parts, preventing directory traversal."""
    result = base
    for part in parts:
        # Remove any directory traversal attempts
        clean_part = part.replace('..', '').replace('/', '').replace('\\', '')
        if clean_part:
            result = result / clean_part
    return result


def ensure_directory(path: Path) -> bool:
    """Ensure directory exists, create if necessary."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {path}: {e}")
        return False


def get_file_icon(file_path: Path) -> str:
    """Get appropriate icon for file type."""
    if file_path.is_dir():
        return "📁"
    
    suffix = file_path.suffix.lower()
    icon_map = {
        '.py': '🐍', '.js': '📜', '.html': '🌐', '.css': '🎨',
        '.json': '📋', '.yaml': '⚙️', '.yml': '⚙️', '.xml': '📄',
        '.txt': '📝', '.md': '📖', '.rst': '📖',
        '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️',
        '.mp3': '🎵', '.wav': '🎵', '.mp4': '🎬', '.avi': '🎬',
        '.pdf': '📕', '.doc': '📘', '.docx': '📘',
        '.zip': '📦', '.tar': '📦', '.gz': '📦',
    }
    
    return icon_map.get(suffix, '📄')


def get_syntax_language(file_path: Path) -> Optional[str]:
    """Get syntax highlighting language for file."""
    suffix = file_path.suffix.lower()
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.html': 'html',
        '.css': 'css',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.xml': 'xml',
        '.md': 'markdown',
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'zsh',
        '.fish': 'fish',
        '.c': 'c',
        '.cpp': 'cpp',
        '.h': 'c',
        '.hpp': 'cpp',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.rb': 'ruby',
        '.sql': 'sql',
    }
    
    return language_map.get(suffix)


def is_binary_file(file_path: Path) -> bool:
    """Check if file is binary."""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            return b'\0' in chunk
    except Exception:
        return True


def get_mime_type(file_path: Path) -> str:
    """Get MIME type of file."""
    try:
        import mimetypes
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type or 'application/octet-stream'
    except Exception:
        return 'application/octet-stream'


class PerformanceMonitor:
    """Monitor performance metrics."""
    
    def __init__(self):
        self.start_time = None
        self.metrics = {}
    
    def start(self, operation: str):
        """Start timing an operation."""
        import time
        self.start_time = time.time()
        self.current_operation = operation
    
    def end(self) -> float:
        """End timing and return duration."""
        if self.start_time is None:
            return 0.0
        
        import time
        duration = time.time() - self.start_time
        
        if hasattr(self, 'current_operation'):
            self.metrics[self.current_operation] = duration
        
        self.start_time = None
        return duration
    
    def get_metrics(self) -> Dict[str, float]:
        """Get all recorded metrics."""
        return self.metrics.copy()