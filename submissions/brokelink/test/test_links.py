"""
Tests for BrokeLink functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path

from brokelink.parser import LinkParser, Link
from brokelink.utils import LinkChecker, BrokenLinks


class TestLinkParser:
    """Test the LinkParser class."""

    def test_markdown_links(self):
        """Test parsing Markdown links."""
        content = """
# Test Document

[Valid link](./test.md)
![Image](./image.png)
[Another link](../parent.md)
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            f.flush()

            parser = LinkParser()
            links = parser.extract_links(f.name)

            assert len(links) == 3
            assert links[0].url == "./test.md"
            assert links[0].link_type == "markdown_link"
            assert links[1].url == "./image.png"
            assert links[1].link_type == "markdown_image"

            os.unlink(f.name)

    def test_html_links(self):
        """Test parsing HTML links."""
        content = """
        <html>
            <body>
                <a href="./test.html">Test Link</a>
                <img src="./image.jpg" alt="Test Image">
            </body>
        </html>
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write(content)
            f.flush()

            parser = LinkParser()
            links = parser.extract_links(f.name)

            assert len(links) == 2
            assert any(link.url == "./test.html" for link in links)
            assert any(link.url == "./image.jpg" for link in links)

            os.unlink(f.name)


class TestLinkChecker:
    """Test the LinkChecker class."""

    def test_broken_file_detection(self):
        """Test detection of broken file links."""
        # Create a temporary directory structure
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create test file
            test_file = tmpdir / "test.md"
            test_file.write_text("[Broken link](./missing.md)")

            # Parse links
            parser = LinkParser()
            links = parser.extract_links(str(test_file))

            # Check for broken links
            checker = LinkChecker()
            broken = checker.check_links(links, str(test_file))

            assert len(broken.missing_files) == 1
            assert broken.missing_files[0].url == "./missing.md"

    def test_valid_file_detection(self):
        """Test that valid files are not flagged as broken."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create files
            test_file = tmpdir / "test.md"
            target_file = tmpdir / "target.md"

            target_file.write_text("# Target Document")
            test_file.write_text("[Valid link](./target.md)")

            # Parse and check
            parser = LinkParser()
            links = parser.extract_links(str(test_file))

            checker = LinkChecker()
            broken = checker.check_links(links, str(test_file))

            assert len(broken.missing_files) == 0
            assert not broken.has_issues()


if __name__ == "__main__":
    pytest.main([__file__])
