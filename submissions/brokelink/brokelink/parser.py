"""
Link Parser - Extract links from Markdown and HTML files.
"""

import re
import os
from pathlib import Path
from typing import List, Dict, NamedTuple
from bs4 import BeautifulSoup

class Link(NamedTuple):
    """Represents a link found in a document."""
    text: str
    url: str
    line_number: int
    link_type: str  # 'markdown_link', 'markdown_image', 'html_link', 'html_image'

class LinkParser:
    """Parse and extract links from Markdown and HTML files."""
    
    def __init__(self):
        # Markdown patterns
        self.md_link_pattern = re.compile(r'\[([^\]]*)\]\(([^)]+)\)', re.MULTILINE)
        self.md_image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)', re.MULTILINE)
        
    def extract_links(self, file_path: str) -> List[Link]:
        """Extract all links from a file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return []
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if file_path.suffix.lower() == '.md':
            return self._parse_markdown(content)
        elif file_path.suffix.lower() in ['.html', '.htm']:
            return self._parse_html(content)
        else:
            # Try to parse as markdown by default
            return self._parse_markdown(content)
    
    def _parse_markdown(self, content: str) -> List[Link]:
        """Parse links from Markdown content."""
        links = []
        lines = content.split('\n')
        
        # Find regular links
        for match in self.md_link_pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            links.append(Link(
                text=match.group(1),
                url=match.group(2),
                line_number=line_num,
                link_type='markdown_link'
            ))
        
        # Find image links
        for match in self.md_image_pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            links.append(Link(
                text=match.group(1),
                url=match.group(2),
                line_number=line_num,
                link_type='markdown_image'
            ))
        
        return links
    
    def _parse_html(self, content: str) -> List[Link]:
        """Parse links from HTML content."""
        links = []
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find <a> tags
            for tag in soup.find_all('a', href=True):
                line_num = self._get_line_number(content, str(tag))
                links.append(Link(
                    text=tag.get_text(),
                    url=tag['href'],
                    line_number=line_num,
                    link_type='html_link'
                ))
            
            # Find <img> tags
            for tag in soup.find_all('img', src=True):
                line_num = self._get_line_number(content, str(tag))
                links.append(Link(
                    text=tag.get('alt', ''),
                    url=tag['src'],
                    line_number=line_num,
                    link_type='html_image'
                ))
                
        except Exception as e:
            # If HTML parsing fails, return empty list
            pass
        
        return links
    
    def _get_line_number(self, content: str, tag_str: str) -> int:
        """Get approximate line number for an HTML tag."""
        try:
            index = content.find(tag_str)
            if index != -1:
                return content[:index].count('\n') + 1
        except:
            pass
        return 1
    
    def extract_headings(self, file_path: str) -> List[str]:
        """Extract heading anchors from a file (for anchor checking)."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return []
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        headings = []
        
        if file_path.suffix.lower() == '.md':
            # Markdown headings
            heading_pattern = re.compile(r'^#+\s+(.+)$', re.MULTILINE)
            for match in heading_pattern.finditer(content):
                heading = match.group(1).strip()
                # Convert to anchor format (simplified)
                anchor = heading.lower().replace(' ', '-').replace('.', '').replace(',', '')
                headings.append(f"#{anchor}")
        
        elif file_path.suffix.lower() in ['.html', '.htm']:
            try:
                soup = BeautifulSoup(content, 'html.parser')
                for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    if tag.get('id'):
                        headings.append(f"#{tag['id']}")
            except:
                pass
        
        return headings