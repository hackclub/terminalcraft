import sys
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DirectoryTree, Static
from textual.containers import Container, Horizontal, Vertical
from rich.syntax import Syntax
from .scanner import SecurityScanner
from .reports import ReportGenerator

class CodeView(Static):
    """A widget to display code with syntax highlighting."""
    def __init__(self) -> None:
        super().__init__("")
        self.code = ""

    def update_code(self, path: Path) -> None:
        """Update the displayed code."""
        try:
            syntax = Syntax.from_path(
                path,
                line_numbers=True,
                word_wrap=True,
                indent_guides=True,
                theme="monokai"
            )
            self.update(syntax)
        except Exception as e:
            self.update(f"Error loading file: {e}")

class SecurityPanel(Static):
    """Display security scan results."""
    def __init__(self) -> None:
        super().__init__("")
        self.scanner = SecurityScanner()

    def scan_file(self, path: Path) -> None:
        """Scan a file and display results."""
        issues = self.scanner.scan_file(path)
        if issues:
            self.update("\n".join(f"⚠️ {issue['message']}" for issue in issues))
        else:
            self.update("✅ No security issues found")

class CodeSecApp(App):
    """Main CodeSec CLI application."""
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Horizontal():
            yield DirectoryTree(".", id="tree")
            with Vertical():
                yield CodeView()
                yield SecurityPanel()
        yield Footer()

    def on_directory_tree_file_selected(self, event):
        """Handle file selection in the directory tree."""
        code_view = self.query_one(CodeView)
        security_panel = self.query_one(SecurityPanel)
        
        path = Path(event.path)
        code_view.update_code(path)
        security_panel.scan_file(path)

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CodeSec CLI - Security and Privacy Analyzer")
    parser.add_argument("path", help="Path to analyze", type=Path)
    parser.add_argument("--report", help="Generate report file", type=Path)
    
    args = parser.parse_args()
    
    if args.report:
        # Run in report mode
        scanner = SecurityScanner()
        report_gen = ReportGenerator()
        issues = scanner.scan_file(args.path)
        report_gen.generate_markdown({"issues": issues}, args.report)
    else:
        # Run in TUI mode
        app = CodeSecApp()
        app.run()

if __name__ == "__main__":
    main()
