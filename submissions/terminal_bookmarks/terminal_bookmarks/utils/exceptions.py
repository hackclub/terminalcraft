"""Custom exceptions with helpful context."""

class BookmarkError(Exception):
    """Base class for bookmark-related errors."""
    def __init__(self, message: str, help_text: str = None):
        super().__init__(message)
        self.help_text = help_text

class BookmarkNotFoundError(BookmarkError):
    """Raised when a bookmark cannot be found."""
    def __init__(self, message: str):
        super().__init__(
            message,
            help_text="Use 'tb list' to see all available bookmarks"
        )

class ValidationError(BookmarkError):
    """Raised when input validation fails."""
    def __init__(self, message: str):
        super().__init__(
            message,
            help_text="Check the command documentation for correct usage"
        )

class ExecutionError(BookmarkError):
    """Raised when command execution fails."""
    def __init__(self, message: str):
        super().__init__(
            message,
            help_text="Verify the command and any required dependencies"
        )

class SecurityError(BookmarkError):
    """Raised for security-related issues."""
    pass

class DependencyError(BookmarkError):
    """Raised when required dependencies are missing."""
    pass

class ContextError(BookmarkError):
    """Raised when execution context is invalid."""
    pass

class PlatformError(BookmarkError):
    """Raised when there are platform compatibility issues."""
    pass

class StorageError(BookmarkError):
    """Raised when there are storage-related issues."""
    pass

class ShellIntegrationError(BookmarkError):
    """Raised when shell integration fails."""
    pass 