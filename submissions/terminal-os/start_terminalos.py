#!/usr/bin/env python3
"""
TerminalOS Direct Launcher v1.0.0
Runs TerminalOS without installation - Just works!
"""

import sys
import os
from pathlib import Path

# Colors for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    """Print TerminalOS header."""
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("╔══════════════════════════════════════════╗")
    print("║              🖥️  TerminalOS               ║")
    print("║        Direct Launcher v1.0.0           ║")
    print("╚══════════════════════════════════════════╝")
    print(f"{Colors.END}")

def check_python_version():
    """Check Python version compatibility."""
    if sys.version_info < (3, 8):
        print(f"{Colors.RED}❌ Python 3.8+ required. You have {sys.version}{Colors.END}")
        return False
    print(f"{Colors.GREEN}✅ Python {sys.version.split()[0]} - OK{Colors.END}")
    return True

def install_missing_packages():
    """Install missing packages automatically."""
    required_packages = {
        'textual': 'textual>=0.41.0',
        'rich': 'rich>=13.0.0', 
        'click': 'click>=8.1.0',
        'psutil': 'psutil>=5.9.0',
        'pyfiglet': 'pyfiglet>=0.8.0',
        'pygments': 'pygments>=2.14.0'
    }
    
    missing = []
    for pkg in required_packages:
        try:
            __import__(pkg)
            print(f"{Colors.GREEN}✅ {pkg}{Colors.END}")
        except ImportError:
            missing.append(required_packages[pkg])
            print(f"{Colors.YELLOW}⚠️  {pkg} - Not found{Colors.END}")
    
    if missing:
        print(f"\n{Colors.CYAN}📦 Installing missing packages...{Colors.END}")
        import subprocess
        try:
            cmd = [sys.executable, '-m', 'pip', 'install'] + missing
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ All packages installed successfully!{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}❌ Failed to install packages: {result.stderr}{Colors.END}")
                return False
        except Exception as e:
            print(f"{Colors.RED}❌ Installation error: {e}{Colors.END}")
            return False
    
    return True

def setup_paths():
    """Setup Python paths for imports."""
    current_dir = Path(__file__).parent
    terminalos_dir = current_dir / "terminalos"
    
    if not terminalos_dir.exists():
        print(f"{Colors.RED}❌ terminalos directory not found at: {terminalos_dir}{Colors.END}")
        return False
    
    # Add to Python path
    sys.path.insert(0, str(current_dir))
    print(f"{Colors.GREEN}✅ Python paths configured{Colors.END}")
    return True

def main():
    """Main launcher function."""
    print_header()
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return 1
    
    # Setup paths
    if not setup_paths():
        input("Press Enter to exit...")
        return 1
    
    # Check and install dependencies
    print(f"\n{Colors.CYAN}🔍 Checking dependencies...{Colors.END}")
    if not install_missing_packages():
        input("Press Enter to exit...")
        return 1
    
    # Parse command line arguments
    debug_mode = '--debug' in sys.argv
    no_boot = '--no-boot' in sys.argv
    
    try:
        print(f"\n{Colors.CYAN}🚀 Starting TerminalOS...{Colors.END}")
        
        # Import TerminalOS
        from terminalos.core.app import TerminalOSApp
        
        # Create and configure app
        app = TerminalOSApp()
        app.configure({
            'debug': debug_mode,
            'theme': 'dark',
            'no_boot': no_boot
        })
        
        # Run the application
        app.run()
        
        print(f"\n{Colors.GREEN}👋 TerminalOS closed successfully!{Colors.END}")
        return 0
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  TerminalOS interrupted by user{Colors.END}")
        return 0
    except ImportError as e:
        print(f"\n{Colors.RED}❌ Import error: {e}{Colors.END}")
        print(f"{Colors.YELLOW}💡 Make sure all files are in the correct structure{Colors.END}")
        return 1
    except Exception as e:
        print(f"\n{Colors.RED}❌ Runtime error: {e}{Colors.END}")
        if debug_mode:
            import traceback
            traceback.print_exc()
        else:
            print(f"{Colors.YELLOW}💡 Run with --debug for detailed error information{Colors.END}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        if exit_code != 0:
            input("\nPress Enter to exit...")
        sys.exit(exit_code)
    except Exception as e:
        print(f"{Colors.RED}❌ Fatal error: {e}{Colors.END}")
        input("Press Enter to exit...")
        sys.exit(1)