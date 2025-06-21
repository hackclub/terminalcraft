#!/usr/bin/env python3
"""
Simple PyInstaller build script - minimal approach
Use this if the comprehensive build fails
"""

import subprocess
import sys
import os

def simple_build():
    """Build with minimal PyInstaller options"""
    print("Building with minimal PyInstaller options...")
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name=meet-zone-simple',
        '--onefile',
        '--console',  # Keep console for debugging
        '--add-data=roster.csv;.' if sys.platform == "win32" else '--add-data=roster.csv:.',
        '--hidden-import=textual',
        '--hidden-import=textual.widgets.tab_pane',
        '--hidden-import=pytz',
        '--collect-all=textual',
        'src/meet_zone/__main__.py'
    ]
    
    print("Command:", ' '.join(cmd))
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✓ Simple build completed!")
        
        exe_name = "meet-zone-simple.exe" if sys.platform == "win32" else "meet-zone-simple"
        exe_path = f"dist/{exe_name}"
        
        if os.path.exists(exe_path):
            print(f"Executable: {exe_path}")
            return True
        else:
            print("Executable not found")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False

if __name__ == "__main__":
    simple_build()