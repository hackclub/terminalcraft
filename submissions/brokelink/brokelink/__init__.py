"""
BrokeLink - A CLI tool for finding broken links in Markdown and HTML files.
"""

__version__ = "1.0.0"
__author__ = "000x"
__email__ = "sithumss9122@gmail.com"

from .parser import LinkParser
from .utils import LinkChecker

__all__ = ["LinkParser", "LinkChecker"]