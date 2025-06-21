#!/usr/bin/env python3
"""
Build debug version of Meet-Zone with comprehensive error handling
"""

import subprocess
import sys
import os
from pathlib import Path

def create_debug_spec():
    """Create a PyInstaller spec file with debug settings"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/meet_zone/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[('roster.csv', '.')],
    hiddenimports=[
        'zoneinfo.tzpath',
        'textual',
        'textual.app',
        'textual.widgets',
        'textual.widgets.button',
        'textual.widgets.data_table',
        'textual.widgets.footer',
        'textual.widgets.header',
        'textual.widgets.input',
        'textual.widgets.label',
        'textual.widgets.select',
        'textual.widgets.static',
        'textual.widgets.tabbed_content',
        'textual.widgets.tab_pane',
        'textual.containers',
        'textual.containers.container',
        'textual.containers.horizontal',
        'textual.containers.vertical',
        'textual.reactive',
        'textual.validation',
        'textual.coordinate',
        'pytz',
        'tkinter',
        'tkinter.messagebox',
        'logging',
        'meet_zone',
        'meet_zone.parser',
        'meet_zone.scheduler',
        'meet_zone.ui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Collect all textual modules
from PyInstaller.utils.hooks import collect_all
textual_datas, textual_binaries, textual_hiddenimports = collect_all('textual')
a.datas += textual_datas
a.binaries += textual_binaries
a.hiddenimports += textual_hiddenimports

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='meet-zone-debug',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console open for debug output
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('meet-zone-debug.spec', 'w') as f:
        f.write(spec_content)
    
    print("Created debug spec file: meet-zone-debug.spec")

def build_debug_executable():
    """Build the debug executable"""
    print("Building debug executable...")
    
    try:
        # Create the spec file
        create_debug_spec()
        
        # Build using the spec file
        cmd = [sys.executable, '-m', 'PyInstaller', 'meet-zone-debug.spec', '--clean']
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Debug executable built successfully!")
            print("Location: dist/meet-zone-debug.exe" if sys.platform == "win32" else "dist/meet-zone-debug")
        else:
            print("✗ Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
        
        return True
        
    except Exception as e:
        print(f"Build error: {e}")
        return False

def main():
    """Main build function"""
    print("Meet-Zone Debug Builder")
    print("=" * 30)
    
    # Check if PyInstaller is available
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # Build the debug executable
    if build_debug_executable():
        print("\n=== BUILD SUCCESSFUL ===")
        print("Debug executable created with:")
        print("- Console output enabled")
        print("- Debug symbols included")
        print("- All Textual modules included")
        print("- Comprehensive error handling")
        print("\nRun the executable from command line to see debug output.")
    else:
        print("\n=== BUILD FAILED ===")
        print("Check the output above for error details.")

if __name__ == "__main__":
    main()