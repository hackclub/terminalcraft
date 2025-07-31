from pathlib import Path
import json
from typing import Dict, List
from datetime import datetime

class ReportGenerator:
    """Generate security audit reports in various formats."""
    
    def __init__(self):
        self.timestamp = datetime.now().isoformat()
        
    def generate_json(self, data: Dict, output_path: Path) -> None:
        """Generate a JSON format report."""
        report = {
            'timestamp': self.timestamp,
            'summary': {
                'total_issues': len(data.get('issues', [])),
                'severity_counts': self._count_severities(data.get('issues', []))
            },
            'details': data
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            
    def generate_markdown(self, data: Dict, output_path: Path) -> None:
        """Generate a Markdown format report."""
        issues = data.get('issues', [])
        severity_counts = self._count_severities(issues)
        
        md_content = [
            "# Security Audit Report",
            f"\nGenerated: {self.timestamp}",
            "\n## Summary",
            f"\nTotal Issues Found: {len(issues)}",
            "\n### Issues by Severity",
        ]
        
        for severity, count in severity_counts.items():
            md_content.append(f"- {severity}: {count}")
            
        md_content.extend([
            "\n## Detailed Findings",
            self._format_issues_markdown(issues)
        ])
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_content))
            
    def _count_severities(self, issues: List[Dict]) -> Dict[str, int]:
        """Count issues by severity level."""
        counts = {}
        for issue in issues:
            severity = issue.get('severity', 'UNKNOWN')
            counts[severity] = counts.get(severity, 0) + 1
        return counts
        
    def _format_issues_markdown(self, issues: List[Dict]) -> str:
        """Format issues as Markdown."""
        if not issues:
            return "\nNo issues found."
            
        sections = []
        for issue in issues:
            sections.append(f"""
### {issue['type']}
- **Severity**: {issue.get('severity', 'UNKNOWN')}
- **Location**: {issue.get('file', 'Unknown')}:{issue.get('line', 'Unknown')}
- **Message**: {issue['message']}
""")
            
        return '\n'.join(sections)
