import pytest
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from codesec.scanner import SecurityScanner
from codesec.explorer import CodeExplorer
from codesec.reports import ReportGenerator

def test_security_scanner_patterns():
    scanner = SecurityScanner()
    
    # Test AWS key pattern
    assert scanner.patterns['aws_key'].search('AKIAIOSFODNN7EXAMPLE')
    assert not scanner.patterns['aws_key'].search('NOTANAWSKEY123456')
    
    # Test API token pattern
    assert scanner.patterns['api_token'].search('api_key_1234567890abcdef1234567890abcdef')
    assert not scanner.patterns['api_token'].search('not_an_api_key_123')
    
def test_code_explorer_file_types():
    explorer = CodeExplorer()
    
    # Create temporary test files
    test_dir = Path('test_files')
    test_dir.mkdir(exist_ok=True)
    
    (test_dir / 'test.py').touch()
    (test_dir / 'test.js').touch()
    
    file_types = explorer._count_file_types(list(test_dir.glob('*')))
    
    assert file_types['.py'] == 1
    assert file_types['.js'] == 1
    
    # Cleanup
    for f in test_dir.glob('*'):
        f.unlink()
    test_dir.rmdir()
    
def test_report_generator():
    generator = ReportGenerator()
    
    test_data = {
        'issues': [
            {
                'type': 'aws_key',
                'message': 'AWS key found',
                'severity': 'HIGH',
                'file': 'test.py',
                'line': 10
            }
        ]
    }
    
    # Test JSON report
    json_path = Path('test_report.json')
    generator.generate_json(test_data, json_path)
    
    assert json_path.exists()
    json_path.unlink()  # Cleanup
    
    # Test Markdown report
    md_path = Path('test_report.md')
    generator.generate_markdown(test_data, md_path)
    
    assert md_path.exists()
    md_path.unlink()  # Cleanup