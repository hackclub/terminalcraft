#!/usr/bin/env python3
"""
Comprehensive PyInstaller build script for Meet-Zone
This script creates a working executable with all necessary modules included
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def check_requirements():
    """Check and install required build dependencies"""
    print("Checking build requirements...")
    
    required_packages = ['pyinstaller', 'pillow']
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)

def create_icon():
    """Create a simple icon file"""
    try:
        from PIL import Image
        
        # Create a simple 32x32 icon
        img = Image.new('RGBA', (32, 32), (0, 100, 200, 255))
        
        if sys.platform == "win32":
            img.save('icon.ico', format='ICO')
            return 'icon.ico'
        else:
            img.save('icon.png', format='PNG')
            return 'icon.png'
            
    except Exception as e:
        print(f"Warning: Could not create icon: {e}")
        return None

def build_executable():
    """Build the executable with comprehensive module inclusion"""
    print("Building Meet-Zone executable...")
    
    # Clean previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # Create icon
    icon_file = create_icon()
    
    # Determine platform-specific settings
    if sys.platform == "win32":
        exe_name = "meet-zone-windows"
        data_separator = ";"
    else:
        exe_name = f"meet-zone-{sys.platform}"
        data_separator = ":"
    
    # Build comprehensive PyInstaller command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        f'--name={exe_name}',
        '--onefile',
        '--windowed',
        f'--add-data=roster.csv{data_separator}.',
        
        # Core hidden imports
        '--hidden-import=zoneinfo.tzpath',
        '--hidden-import=logging',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.messagebox',
        
        # PyTZ imports
        '--hidden-import=pytz',
        
        # Textual core imports
        '--hidden-import=textual',
        '--hidden-import=textual.app',
        '--hidden-import=textual.reactive',
        '--hidden-import=textual.validation',
        '--hidden-import=textual.coordinate',
        
        # Textual widgets (comprehensive list)
        '--hidden-import=textual.widgets',
        '--hidden-import=textual.widgets.button',
        '--hidden-import=textual.widgets.data_table',
        '--hidden-import=textual.widgets.footer',
        '--hidden-import=textual.widgets.header',
        '--hidden-import=textual.widgets.input',
        '--hidden-import=textual.widgets.label',
        '--hidden-import=textual.widgets.select',
        '--hidden-import=textual.widgets.static',
        '--hidden-import=textual.widgets.tabbed_content',
        '--hidden-import=textual.widgets.tab_pane',
        
        # Textual containers
        '--hidden-import=textual.containers',
        '--hidden-import=textual.containers.container',
        '--hidden-import=textual.containers.horizontal',
        '--hidden-import=textual.containers.vertical',
        
        # Application modules
        '--hidden-import=meet_zone',
        '--hidden-import=meet_zone.parser',
        '--hidden-import=meet_zone.scheduler',
        '--hidden-import=meet_zone.ui',
        
        # Collect all textual modules
        '--collect-all=textual',
        
        # Clean build
        '--clean',
        
        # Entry point
        'src/meet_zone/__main__.py'
    ]
    
    # Add icon if available
    if icon_file:
        cmd.insert(-1, f'--icon={icon_file}')
    
    print("PyInstaller command:")
    print(' '.join(cmd))
    print()
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✓ Executable built successfully!")
            
            # Find the executable
            exe_path = None
            if sys.platform == "win32":
                exe_path = f"dist/{exe_name}.exe"
            else:
                exe_path = f"dist/{exe_name}"
            
            if os.path.exists(exe_path):
                print(f"Executable location: {exe_path}")
                
                # Make executable on Unix systems
                if sys.platform != "win32":
                    os.chmod(exe_path, 0o755)
                    print("Made executable")
                
                # Show file size
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"File size: {size_mb:.1f} MB")
                
                return True
            else:
                print("✗ Executable not found in expected location")
                return False
        else:
            print("✗ Build failed!")
            print("\nSTDOUT:")
            print(result.stdout)
            print("\nSTDERR:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Build timed out (took longer than 5 minutes)")
        return False
    except Exception as e:
        print(f"✗ Build error: {e}")
        return False

def test_executable():
    """Test the built executable"""
    print("\nTesting executable...")
    
    if sys.platform == "win32":
        exe_path = "dist/meet-zone-windows.exe"
    else:
        exe_path = f"dist/meet-zone-{sys.platform}"
    
    if not os.path.exists(exe_path):
        print("Executable not found for testing")
        return False
    
    try:
        # Test with --help flag (should exit quickly)
        result = subprocess.run([exe_path, '--help'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✓ Executable runs and shows help")
            return True
        else:
            print("✗ Executable failed to run")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Executable test timed out")
        return False
    except Exception as e:
        print(f"✗ Test error: {e}")
        return False

def main():
    """Main build function"""
    print("Meet-Zone Executable Builder")
    print("=" * 40)
    print(f"Platform: {sys.platform}")
    print(f"Python: {sys.version}")
    print()
    
    try:
        # Check requirements
        check_requirements()
        print()
        
        # Build executable
        if build_executable():
            print("\n" + "=" * 40)
            print("BUILD SUCCESSFUL!")
            print("=" * 40)
            
            # Test the executable
            if test_executable():
                print("\n✓ Executable is working!")
                print("\nYou can now run:")
                if sys.platform == "win32":
                    print("  dist\\meet-zone-windows.exe")
                else:
                    print(f"  ./dist/meet-zone-{sys.platform}")
            else:
                print("\n⚠ Executable built but may have runtime issues")
                print("Try running it manually to see error messages")
        else:
            print("\n" + "=" * 40)
            print("BUILD FAILED!")
            print("=" * 40)
            print("Check the error messages above for details")
            
    except KeyboardInterrupt:
        print("\nBuild interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()