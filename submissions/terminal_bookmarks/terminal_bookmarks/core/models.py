from dataclasses import dataclass, asdict
from datetime import datetime, UTC
from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4
from enum import Enum
from ..utils.platform import Platform
from ..utils.id_generator import generate_short_id

class DateFilter(Enum):
    """Enumeration for date-based filtering options."""
    TODAY = "today"
    THIS_WEEK = "week"
    THIS_MONTH = "month"
    ALL = "all"

class SortOrder(Enum):
    """Enumeration for result sorting options."""
    RELEVANCE = "relevance"
    DATE_ADDED = "date"
    USAGE = "usage"
    TITLE = "title"

class SearchOptions:
    """Class to hold search options and criteria."""
    def __init__(self,
                query: Optional[str] = None,
                include_tags: Optional[List[str]] = None,
                exclude_tags: Optional[List[str]] = None,
                date_filter: DateFilter = DateFilter.ALL,
                min_usage: Optional[int] = None,
                exact_match: bool = False,
                sort_by: SortOrder = SortOrder.RELEVANCE):
        self.query = str(query).strip() if query is not None else ""
        self.include_tags = include_tags or []
        self.exclude_tags = exclude_tags or []
        self.date_filter = date_filter
        self.min_usage = min_usage
        self.exact_match = exact_match
        self.sort_by = sort_by

class SearchResult:
    """Class to hold search result with relevance score."""
    def __init__(self, bookmark: 'Bookmark', score: float = 0.0, 
                matches: Optional[Dict[str, List[str]]] = None):
        self.bookmark = bookmark
        self.score = score
        self.matches = matches if matches is not None else {}

@dataclass
class Bookmark:
    """Represents a command bookmark."""
    title: str
    command: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    id: Optional[str] = None  # Make id optional, will be generated if None
    dependencies: Optional[List[str]] = None
    working_dir: Optional[str] = None
    platform: Optional[Union[Platform, str]] = None
    created_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    use_count: int = 0

    def __post_init__(self):
        """Initialize default values and validate fields."""
        if self.id is None:
            self.id = generate_short_id()
        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if isinstance(self.platform, str):
            if self.platform.lower() == "all":
                self.platform = None
            else:
                try:
                    self.platform = Platform(self.platform.lower())
                except ValueError:
                    self.platform = None

    def get_platform(self) -> Optional[Platform]:
        """Get platform as enum value."""
        return self.platform

    def to_dict(self) -> Dict[str, Any]:
        """Convert bookmark to dictionary format."""
        data = asdict(self)
        data['id'] = self.id
        data['created_at'] = self.created_at.isoformat()
        if self.last_used:
            data['last_used'] = self.last_used.isoformat()
        if self.platform:
            data['platform'] = self.platform.value
        else:
            data['platform'] = "all"
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Bookmark':
        """Create a Bookmark instance from a dictionary."""
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'last_used' in data and isinstance(data['last_used'], str):
            data['last_used'] = datetime.fromisoformat(data['last_used'])
        return cls(**data)

@dataclass
class Collection:
    """Represents a group of related bookmarks."""
    name: str
    description: Optional[str]
    bookmark_ids: List[UUID]

    def __post_init__(self):
        """Initialize default values."""
        if self.bookmark_ids is None:
            self.bookmark_ids = []

@dataclass
class ExecutionContext:
    """Represents the context for command execution."""
    force: bool = False
    check_dependencies: bool = True
    capture_output: bool = False
    timeout: Optional[int] = None
    env_vars: Dict[str, str] = None
    command_args: Optional[List[str]] = None

@dataclass
class ExecutionResult:
    """Represents the result of a command execution."""
    success: bool
    command: str
    output: str
    error: str
    return_code: int
    duration: float
    timestamp: datetime

@dataclass
class ExecutionHistory:
    """Represents a historical command execution."""
    id: UUID
    bookmark_id: UUID
    result: ExecutionResult
    context: ExecutionContext 