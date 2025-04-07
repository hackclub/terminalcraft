from typing import List, Optional, Dict, Set, Tuple, Union
from uuid import UUID, uuid4
from datetime import datetime, timedelta, UTC
import json
import os
import re
from difflib import SequenceMatcher
from pathlib import Path

from .models import (
    Bookmark, 
    SearchOptions, 
    SearchResult, 
    DateFilter, 
    SortOrder
)
from ..utils.exceptions import BookmarkError, BookmarkNotFoundError, ValidationError
from ..utils.id_generator import generate_short_id

class BookmarkManager:
    """Manages operations on bookmarks including CRUD and search."""

    def __init__(self, storage_path: str):
        """Initialize the BookmarkManager.
        
        Args:
            storage_path: Path to the JSON file storing bookmarks
        """
        self.bookmarks: Dict[str, Bookmark] = {}  
        self.storage_path = Path(storage_path)
        self._load()

    def _load(self) -> None:
        """Load bookmarks from storage."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.bookmarks = {
                        id_str: Bookmark.from_dict(bookmark_data)
                        for id_str, bookmark_data in data.items()
                    }
        except FileNotFoundError:
            self.bookmarks = {}
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid bookmark data format: {e}")
        except Exception as e:
            raise BookmarkError(f"Error loading bookmarks: {str(e)}")

    def save(self) -> None:
        """Save bookmarks to storage."""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                id: bookmark.to_dict()
                for id, bookmark in self.bookmarks.items()
            }
            temp_path = self.storage_path.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            temp_path.replace(self.storage_path)
            
        except Exception as e:
            raise BookmarkError(f"Failed to save bookmarks: {str(e)}")

    def add_bookmark(self, title: str, command: str, 
                    description: Optional[str] = None,
                    tags: Optional[List[str]] = None) -> Bookmark:
        """Add a new bookmark with a unique short ID."""
        if not title or not command:
            raise ValidationError("Title and command are required")
        bookmark = Bookmark(
            title=title,
            command=command,
            description=description,
            tags=tags
        )
        while bookmark.id in self.bookmarks:
            bookmark.id = generate_short_id()
            
        self.bookmarks[bookmark.id] = bookmark
        self.save()
        return bookmark

    def get_bookmark(self, bookmark_id: str) -> Bookmark:
        """Retrieve a bookmark by ID.
        
        Args:
            bookmark_id: ID of the bookmark
            
        Returns:
            The requested Bookmark instance
            
        Raises:
            BookmarkNotFoundError: If bookmark doesn't exist
        """
        if bookmark_id not in self.bookmarks:
            raise BookmarkNotFoundError(f"Bookmark {bookmark_id} not found")
        return self.bookmarks[bookmark_id]

    def update_bookmark(self, 
                       bookmark_id: str, 
                       **kwargs) -> Bookmark:
        """Update a bookmark's attributes.
        
        Args:
            bookmark_id: ID of the bookmark to update
            **kwargs: Attributes to update
            
        Returns:
            The updated Bookmark instance
            
        Raises:
            BookmarkNotFoundError: If bookmark doesn't exist
        """
        if bookmark_id not in self.bookmarks:
            raise BookmarkNotFoundError(f"Bookmark {bookmark_id} not found")

        bookmark = self.bookmarks[bookmark_id]
        for key, value in kwargs.items():
            if hasattr(bookmark, key):
                setattr(bookmark, key, value)

        self.save()
        return bookmark

    def delete_bookmark(self, bookmark_id: Union[str, UUID]) -> None:
        """Delete a bookmark.
        
        Args:
            bookmark_id: The ID of the bookmark to delete (can be string or UUID)
            
        Raises:
            BookmarkNotFoundError: If the bookmark doesn't exist
            BookmarkError: If the deletion fails
        """
        # Convert UUID to string if necessary
        str_id = str(bookmark_id)
        
        if str_id not in self.bookmarks:
            raise BookmarkNotFoundError(f"Bookmark {str_id} not found")
            
        # Store a copy in case we need to rollback
        bookmark_copy = self.bookmarks[str_id]
        
        try:
            del self.bookmarks[str_id]
            self.save()
        except Exception as e:
            # Rollback the deletion if save fails
            self.bookmarks[str_id] = bookmark_copy
            raise BookmarkError(f"Failed to delete bookmark: {str(e)}")

    def get_all_tags(self) -> Set[str]:
        """Get all unique tags across all bookmarks."""
        tags = set()
        for bookmark in self.bookmarks.values():
            tags.update(bookmark.tags)
        return tags

    def suggest_tags(self, partial_tag: str, limit: int = 5) -> List[str]:
        """Suggest tags based on partial input."""
        all_tags = self.get_all_tags()
        partial_tag = partial_tag.lower()
        prefix_matches = [tag for tag in all_tags if tag.lower().startswith(partial_tag)]
        fuzzy_matches = []
        for tag in all_tags:
            if tag not in prefix_matches:
                ratio = SequenceMatcher(None, partial_tag, tag.lower()).ratio()
                if ratio > 0.5:
                    fuzzy_matches.append((tag, ratio))
        fuzzy_matches.sort(key=lambda x: x[1], reverse=True)
        suggestions = prefix_matches + [tag for tag, _ in fuzzy_matches]
        return suggestions[:limit]

    def search_bookmarks(self, options: SearchOptions) -> List[SearchResult]:
        """Enhanced search with multiple criteria and scoring."""
        try:
            results: List[SearchResult] = []
            
            for bookmark in self.bookmarks.values():
                if not self._matches_date_filter(bookmark, options.date_filter):
                    continue
                if options.min_usage and bookmark.use_count < options.min_usage:
                    continue
                if not self._matches_tag_filters(bookmark, options.include_tags, options.exclude_tags):
                    continue
                score, matches = self._calculate_relevance(bookmark, options)
                if score > 0 or not options.query:
                    results.append(SearchResult(bookmark, score, matches))
            self._sort_results(results, options.sort_by)
            
            return results
        except Exception as e:
            raise BookmarkError(f"Search failed: {str(e)}")

    def _matches_date_filter(self, bookmark: Bookmark, date_filter: DateFilter) -> bool:
        """Check if bookmark matches the date filter."""
        if date_filter == DateFilter.ALL:
            return True

        now = datetime.now(UTC)  
        created = bookmark.created_at

        if date_filter == DateFilter.TODAY:
            return created.date() == now.date()
        elif date_filter == DateFilter.THIS_WEEK:
            week_ago = now - timedelta(days=7)
            return created >= week_ago
        elif date_filter == DateFilter.THIS_MONTH:
            month_ago = now - timedelta(days=30)
            return created >= month_ago

        return True

    def _matches_tag_filters(self, 
                           bookmark: Bookmark, 
                           include_tags: List[str], 
                           exclude_tags: List[str]) -> bool:
        """Check if bookmark matches tag filters."""
        bookmark_tags = {tag.lower() for tag in bookmark.tags}
        if include_tags and not all(tag.lower() in bookmark_tags for tag in include_tags):
            return False
        if exclude_tags and any(tag.lower() in bookmark_tags for tag in exclude_tags):
            return False
            
        return True

    def _calculate_relevance(self, bookmark: Bookmark, options: SearchOptions) -> Tuple[float, Dict[str, List[str]]]:
        """Calculate relevance score and collect matches."""
        if not options.query:
            return 1.0, {}
        
        query = options.query.lower()  
        score = 0.0
        matches = {}
        weights = {
            'title': 1.0,
            'command': 0.8,
            'description': 0.6,
            'tags': 0.4
        }
        def check_field(text: str, field_name: str, weight: float) -> float:
            if not text:
                return 0.0

            if options.exact_match:
                if query == text.lower():
                    matches[field_name] = [text]
                    return weight
                return 0.0
            text_lower = text.lower()
            if query in text_lower:
                matches[field_name] = [text]
                return weight * 0.8  
            ratio = SequenceMatcher(None, query, text_lower).ratio()
            if ratio > 0.6:  
                matches[field_name] = [text]
                return weight * ratio

            return 0.0
        score += check_field(bookmark.title, 'title', weights['title'])
        score += check_field(bookmark.command, 'command', weights['command'])
        score += check_field(bookmark.description or "", 'description', weights['description'])
        tag_matches = []
        for tag in bookmark.tags:
            if check_field(tag, 'tag', weights['tags']) > 0:
                tag_matches.append(tag)
        if tag_matches:
            matches['tags'] = tag_matches
            score += weights['tags']

        return score, matches

    def _sort_results(self, results: List[SearchResult], sort_by: SortOrder) -> None:
        """Sort search results based on specified criteria."""
        if sort_by == SortOrder.RELEVANCE:
            results.sort(key=lambda x: x.score, reverse=True)
        elif sort_by == SortOrder.DATE_ADDED:
            results.sort(key=lambda x: x.bookmark.created_at, reverse=True)
        elif sort_by == SortOrder.USAGE:
            results.sort(key=lambda x: x.bookmark.use_count, reverse=True)
        elif sort_by == SortOrder.TITLE:
            results.sort(key=lambda x: x.bookmark.title.lower())

    def record_usage(self, bookmark_id: str) -> None:
        """Record usage of a bookmark."""
        bookmark = self.get_bookmark(bookmark_id)
        bookmark.last_used = datetime.now(UTC)  
        bookmark.use_count += 1
        self.save()

    def get_all_bookmarks(self) -> List[Bookmark]:
        """Get all bookmarks."""
        try:
            if not hasattr(self, 'bookmarks') or self.bookmarks is None:
                self.bookmarks = {}
            return list(self.bookmarks.values())
        except Exception as e:
            raise BookmarkError(f"Failed to retrieve bookmarks: {str(e)}")

    def find_bookmark_by_partial_id(self, partial_id: str) -> Optional[Bookmark]:
        """Find a bookmark by ID (exact or partial match)."""
        try:
            if partial_id in self.bookmarks:
                return self.bookmarks[partial_id]
            matches = [b for b in self.bookmarks.values() 
                      if b.id.startswith(partial_id.upper())]
            
            if len(matches) > 1:
                raise BookmarkError(
                    f"Multiple bookmarks found matching '{partial_id}'. Please be more specific."
                )
            return matches[0] if matches else None
        except Exception as e:
            raise BookmarkError(f"Failed to search bookmarks: {str(e)}") 