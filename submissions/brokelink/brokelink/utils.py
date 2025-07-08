"""
Utilities for link checking and reporting.
"""

import os
import urllib.parse
from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass, field
from colorama import Fore, Style

from .parser import Link


@dataclass
class BrokenLinks:
    """Container for different types of broken links."""

    missing_files: List[Link] = field(default_factory=list)
    missing_images: List[Link] = field(default_factory=list)
    invalid_anchors: List[Link] = field(default_factory=list)

    def has_issues(self) -> bool:
        """Check if there are any broken links."""
        return bool(self.missing_files or self.missing_images or self.invalid_anchors)

    def total_count(self) -> int:
        """Get total count of broken links."""
        return (
            len(self.missing_files)
            + len(self.missing_images)
            + len(self.invalid_anchors)
        )


class LinkChecker:
    """Check links for validity."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._file_cache: Set[str] = set()
        self._anchor_cache: Dict[str, List[str]] = {}

    def check_links(
        self,
        links: List[Link],
        base_file: str,
        check_images: bool = True,
        check_anchors: bool = False,
    ) -> BrokenLinks:
        """Check a list of links for broken references."""
        broken = BrokenLinks()
        base_dir = Path(base_file).parent

        for link in links:
            if self._is_external_url(link.url):
                # Skip external URLs (would require network requests)
                continue

            if link.url.startswith("#"):
                # Anchor link within same file
                if check_anchors:
                    if not self._check_anchor(base_file, link.url):
                        broken.invalid_anchors.append(link)
                continue

            # Parse URL and remove anchor
            parsed = urllib.parse.urlparse(link.url)
            file_path = parsed.path
            anchor = parsed.fragment

            if not file_path:
                continue

            # Resolve relative path
            target_path = (base_dir / file_path).resolve()

            # Check if file exists
            if not target_path.exists():
                if link.link_type in ["markdown_image", "html_image"]:
                    if check_images:
                        broken.missing_images.append(link)
                else:
                    broken.missing_files.append(link)
                continue

            # Check anchor if present
            if anchor and check_anchors:
                if not self._check_anchor(str(target_path), f"#{anchor}"):
                    broken.invalid_anchors.append(link)

        return broken

    def _is_external_url(self, url: str) -> bool:
        """Check if URL is external (http/https/ftp/etc)."""
        return url.startswith(("http://", "https://", "ftp://", "mailto:"))

    def _check_anchor(self, file_path: str, anchor: str) -> bool:
        """Check if an anchor exists in a file."""
        if file_path not in self._anchor_cache:
            from .parser import LinkParser

            parser = LinkParser()
            self._anchor_cache[file_path] = parser.extract_headings(file_path)

        return anchor in self._anchor_cache[file_path]


class BrokenLinkReport:
    """Generate reports for broken links."""

    def __init__(self, file_path: str, broken_links: BrokenLinks):
        self.file_path = file_path
        self.broken_links = broken_links

    def print_issues(self):
        """Print broken link issues to console."""
        if self.broken_links.missing_files:
            print(
                f"  {Fore.RED}🔗 Missing files ({len(self.broken_links.missing_files)}):{Style.RESET_ALL}"
            )
            for link in self.broken_links.missing_files:
                print(f"    Line {link.line_number}: {link.url} ('{link.text}')")

        if self.broken_links.missing_images:
            print(
                f"  {Fore.RED}🖼️  Missing images ({len(self.broken_links.missing_images)}):{Style.RESET_ALL}"
            )
            for link in self.broken_links.missing_images:
                print(f"    Line {link.line_number}: {link.url} ('{link.text}')")

        if self.broken_links.invalid_anchors:
            print(
                f"  {Fore.RED}⚓ Invalid anchors ({len(self.broken_links.invalid_anchors)}):{Style.RESET_ALL}"
            )
            for link in self.broken_links.invalid_anchors:
                print(f"    Line {link.line_number}: {link.url} ('{link.text}')")

    def to_dict(self) -> Dict:
        """Convert report to dictionary for JSON output."""
        return {
            "file": self.file_path,
            "issues": {
                "missing_files": [
                    {
                        "line": link.line_number,
                        "url": link.url,
                        "text": link.text,
                        "type": link.link_type,
                    }
                    for link in self.broken_links.missing_files
                ],
                "missing_images": [
                    {
                        "line": link.line_number,
                        "url": link.url,
                        "text": link.text,
                        "type": link.link_type,
                    }
                    for link in self.broken_links.missing_images
                ],
                "invalid_anchors": [
                    {
                        "line": link.line_number,
                        "url": link.url,
                        "text": link.text,
                        "type": link.link_type,
                    }
                    for link in self.broken_links.invalid_anchors
                ],
            },
        }
