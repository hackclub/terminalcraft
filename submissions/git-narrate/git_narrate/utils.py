from datetime import datetime
from typing import List, Dict, Any
import re

def format_date(date: datetime) -> str:
    """Format a datetime object for display."""
    return date.strftime("%Y-%m-%d")

def format_duration(start: datetime, end: datetime) -> str:
    """Calculate and format a duration between two dates."""
    delta = end - start
    days = delta.days
    months, days = divmod(days, 30)
    years, months = divmod(months, 12)
    
    parts = []
    if years > 0:
        parts.append(f"{years} year{'s' if years != 1 else ''}")
    if months > 0:
        parts.append(f"{months} month{'s' if months != 1 else ''}")
    if days > 0 and not (years > 0 or months > 0):
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    
    return ", ".join(parts) if parts else "0 days"

def get_top_contributors(contributors: Dict[str, Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
    """Get the top contributors by commit count."""
    sorted_contributors = sorted(
        contributors.items(),
        key=lambda x: x[1]["commits"],
        reverse=True
    )
    return [{"name": name, **stats} for name, stats in sorted_contributors[:limit]]

def clean_commit_message(message: str) -> str:
    """Clean up a commit message for display."""
    # Remove common prefixes
    message = re.sub(r'^(feat|fix|docs|style|refactor|test|chore)(\([^)]+\))?:\s*', '', message, flags=re.IGNORECASE)
    # Remove trailing whitespace and newlines
    return message.strip()