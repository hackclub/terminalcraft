# Note: Everything in this directory is a minified version of https://github.com/unclecode/crawl4ai/tree/main due to it's massive installation size


from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Tuple
from .html2text import CustomHTML2Text


# from .types import RelevantContentFilter
import re
from urllib.parse import urljoin

# Pre-compile the regex pattern
LINK_PATTERN = re.compile(r'!?\[([^\]]+)\]\(([^)]+?)(?:\s+"([^"]*)")?\)')


def fast_urljoin(base: str, url: str) -> str:
    """Fast URL joining for common cases."""
    if url.startswith(("http://", "https://", "mailto:", "//")):
        return url
    if url.startswith("/"):
        # Handle absolute paths
        if base.endswith("/"):
            return base[:-1] + url
        return base + url
    return urljoin(base, url)


class MarkdownGenerationStrategy(ABC):
    """Abstract base class for markdown generation strategies."""

    def __init__(
        self,
        options: Optional[Dict[str, Any]] = None,
        verbose: bool = False,
    ):
        self.options = options or {}
        self.verbose = verbose

    @abstractmethod
    def generate_markdown(
        self,
        html: str,
        url: str = "",
        html2text_options: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> str:
        """Generate markdown from cleaned HTML."""
        pass


class DefaultMarkdownGenerator(MarkdownGenerationStrategy):
    """
    Default implementation of markdown generation strategy.

    How it works:
    1. Generate raw markdown from cleaned HTML.
    2. Convert links to citations.
    3. Generate fit markdown if content filter is provided.
    4. Return MarkdownGenerationResult.

    Args:
        content_filter (Optional[RelevantContentFilter]): Content filter for generating fit markdown.
        options (Optional[Dict[str, Any]]): Additional options for markdown generation. Defaults to None.

    Returns:
        MarkdownGenerationResult: Result containing raw markdown, fit markdown, fit HTML, and references markdown.
    """

    def __init__(
        self,
        options: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(options)

    def generate_markdown(
        self,
        html: str,
        url: str = "",
        html2text_options: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate markdown with citations from cleaned HTML.

        Returns:
            MarkdownGenerationResult: Result containing raw markdown, fit markdown, fit HTML, and references markdown.
        """
        try:
            # Initialize HTML2Text with default options for better conversion
            h = CustomHTML2Text(baseurl=url)
            default_options = {
                "body_width": 0,  # Disable text wrapping
                "ignore_emphasis": False,
                "ignore_links": False,
                "ignore_images": True,
                "protect_links": False,
                "single_line_break": True,
                "mark_code": True,
                "escape_snob": False,
                "only_text": True,
                "remove_forms": True,
                "exclude_external_images": True,
                "exclude_external_links": True,
                "exclude_social_media_links": True,
            }

            # Update with custom options if provided
            if html2text_options:
                default_options.update(html2text_options)
            elif options:
                default_options.update(options)
            elif self.options:
                default_options.update(self.options)

            h.update_params(**default_options)

            # Generate raw markdown
            try:
                raw_markdown = h.handle(html)
            except Exception as e:
                raw_markdown = f"Error converting HTML to markdown: {str(e)}"

            raw_markdown = raw_markdown.replace("    ```", "```")

            return raw_markdown
        except Exception as e:
            raise Exception(f"Error generating markdown for url '{url}': {str(e)}")
