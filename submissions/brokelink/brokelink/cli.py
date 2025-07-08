"""
BrokeLink CLI - Main entry point for the command-line interface.
"""

import os
import sys
import glob
from pathlib import Path
import click
from colorama import init, Fore, Style

from .parser import LinkParser
from .utils import LinkChecker, BrokenLinkReport

 
init(autoreset=True)

@click.command()
@click.argument('path', type=click.Path(exists=True), default='.')
@click.option('--include', '-i', multiple=True, default=['*.md', '*.html'], 
              help='File patterns to include (default: *.md *.html)')
@click.option('--exclude', '-e', multiple=True, 
              help='File patterns to exclude')
@click.option('--check-images', '-img', is_flag=True, default=True,
              help='Check image references (default: enabled)')
@click.option('--check-anchors', '-a', is_flag=True, default=False,
              help='Check heading anchors (experimental)')
@click.option('--verbose', '-v', is_flag=True, 
              help='Verbose output')
@click.option('--quiet', '-q', is_flag=True,
              help='Only show errors')
@click.option('--format', '-f', type=click.Choice(['text', 'json']), default='text',
              help='Output format')
def main(path, include, exclude, check_images, check_anchors, verbose, quiet, format):
    """
    🔗 BrokeLink - Scan for broken links in Markdown and HTML files.
    
    PATH: Directory or file to scan (default: current directory)
    """
    
    if not quiet:
        click.echo(f"{Fore.CYAN}🔗 BrokeLink v1.0.0 - Scanning for broken links...{Style.RESET_ALL}")
    
    # Initialize components
    parser = LinkParser()
    checker = LinkChecker(verbose=verbose)
    
    # Find files to scan
    files_to_scan = _find_files(path, include, exclude)
    
    if not files_to_scan:
        click.echo(f"{Fore.YELLOW}⚠️  No files found matching patterns: {', '.join(include)}{Style.RESET_ALL}")
        return
    
    if verbose:
        click.echo(f"{Fore.BLUE}📁 Found {len(files_to_scan)} files to scan{Style.RESET_ALL}")
    
    # Scan files
    total_broken = 0
    reports = []
    
    for file_path in files_to_scan:
        if verbose:
            click.echo(f"{Fore.BLUE}🔍 Scanning: {file_path}{Style.RESET_ALL}")
        
        try:
            links = parser.extract_links(file_path)
            broken_links = checker.check_links(links, file_path, check_images, check_anchors)
            
            if broken_links.has_issues():
                report = BrokenLinkReport(file_path, broken_links)
                reports.append(report)
                total_broken += broken_links.total_count()
                
        except Exception as e:
            if not quiet:
                click.echo(f"{Fore.RED}❌ Error scanning {file_path}: {e}{Style.RESET_ALL}")
    
    # Output results
    if format == 'json':
        _output_json(reports)
    else:
        _output_text(reports, total_broken, quiet)
    
    # Exit with appropriate code
    sys.exit(1 if total_broken > 0 else 0)

def _find_files(path, include_patterns, exclude_patterns):
    """Find files matching include patterns and not matching exclude patterns."""
    files = []
    path_obj = Path(path)
    
    if path_obj.is_file():
        return [str(path_obj)]
    
    for pattern in include_patterns:
        if path_obj.is_dir():
            files.extend(glob.glob(str(path_obj / "**" / pattern), recursive=True))
        else:
            files.extend(glob.glob(pattern, recursive=True))
    
    # Remove excluded files
    if exclude_patterns:
        excluded = set()
        for pattern in exclude_patterns:
            excluded.update(glob.glob(pattern, recursive=True))
        files = [f for f in files if f not in excluded]
    
    return sorted(set(files))

def _output_text(reports, total_broken, quiet):
    """Output results in text format."""
    if not reports:
        if not quiet:
            click.echo(f"{Fore.GREEN}✅ No broken links found!{Style.RESET_ALL}")
        return
    
    click.echo(f"\n{Fore.RED}💥 Found {total_broken} broken link(s) in {len(reports)} file(s):{Style.RESET_ALL}")
    
    for report in reports:
        click.echo(f"\n{Fore.YELLOW}📄 {report.file_path}:{Style.RESET_ALL}")
        report.print_issues()

def _output_json(reports):
    """Output results in JSON format."""
    import json
    
    result = {
        "total_files": len(reports),
        "total_broken": sum(r.broken_links.total_count() for r in reports),
        "files": [report.to_dict() for report in reports]
    }
    
    click.echo(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()