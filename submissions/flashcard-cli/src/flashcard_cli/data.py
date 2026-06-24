import sqlite3
from typing import List, Dict, Any
from .db import get_all_flashcard, add_flashcard

# Initialize local database connection with flashcard.db sql file
con = sqlite3.connect("flashcard.db")

def load_flashcards() -> List[Dict[str, Any]]:
    """Loads all flashcards from the database."""
    if not con:
        return []
    return get_all_flashcard(con)

def save_flashcard(question: str, answer: str) -> Dict[str, Any]:
    """Saves a single flashcard to the database."""
    
    return add_flashcard(con, question, answer)
