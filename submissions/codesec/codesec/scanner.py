import re
from pathlib import Path
from typing import Dict, List, Optional
import json
import sqlite3
from dataclasses import dataclass

@dataclass
class SecurityIssue:
    type: str
    message: str
    line: Optional[int] = None
    severity: str = "HIGH"

class SecurityScanner:
    """Scanner for detecting security and privacy issues in code."""
    def __init__(self):
        patterns = {
            'aws_key': r'(?:AKIA|A3T|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}',
            'api_token': r'(?i)(api[_-]?key|token|secret)[_-]?[a-zA-Z0-9]{32,}',
            'suspicious_domains': r'(?:tracking\.|analytics\.|telemetry\.)[\w-]+\.[a-z]{2,}',
            'plaintext_storage': r'(?i)(password|secret|token|key)[\s]*=[\s]*["\'][^"\']+["\']'
        }
        # Compile all regex patterns
        self.patterns = {
            name: re.compile(pattern) for name, pattern in patterns.items()
        }
        
    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for security issues."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for hard-coded credentials
            for pattern_name, pattern in self.patterns.items():
                matches = re.finditer(pattern, content)
                for match in matches:
                    issues.append({
                        'type': pattern_name,
                        'message': f'Potential {pattern_name} found',
                        'line': content.count('\n', 0, match.start()) + 1
                    })
            
            # Special handling for browser credential files
            if file_path.suffix in ['.sqlite', '.json']:
                if self._check_browser_creds(file_path):
                    issues.append({
                        'type': 'browser_credentials',
                        'message': f'Potential browser credentials found in {file_path.name}'
                    })
                    
        except Exception as e:
            issues.append({
                'type': 'error',
                'message': f'Error scanning file: {str(e)}'
            })
            
        return issues
    
    def _check_browser_creds(self, file_path: Path) -> bool:
        """Check if a file contains browser credentials."""
        if file_path.suffix == '.sqlite':
            try:
                conn = sqlite3.connect(file_path)
                cursor = conn.cursor()
                
                # Check for common browser credential table names
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' 
                    AND name IN ('logins', 'cookies', 'web_data', 'Login Data')
                """)
                
                return bool(cursor.fetchone())
            except:
                return False
            finally:
                if 'conn' in locals():
                    conn.close()
                    
        elif file_path.suffix == '.json':
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                # Check for common browser credential JSON structures
                credential_indicators = ['credentials', 'cookies', 'passwords', 'logins']
                return any(indicator in str(data).lower() for indicator in credential_indicators)
            except:
                return False
                
        return False

    def generate_report(self, issues: List[Dict]) -> Dict:
        """Generate a structured report from the found issues."""
        return {
            'total_issues': len(issues),
            'issues_by_type': self._group_by_type(issues),
            'issues': issues
        }
    
    def _group_by_type(self, issues: List[Dict]) -> Dict:
        """Group issues by their type."""
        grouped = {}
        for issue in issues:
            issue_type = issue['type']
            if issue_type not in grouped:
                grouped[issue_type] = []
            grouped[issue_type].append(issue)
        return grouped
