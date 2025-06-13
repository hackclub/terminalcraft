#!/usr/bin/env python3
"""
Build script for TermiCast executable
Creates a single, portable executable that runs anywhere!

Run this after installing dependencies: python build_executable.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("🚀 Building TermiCast executable...")
    print("   This might take a few minutes - time for coffee! ☕")
    
    # Make sure we're in the right directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Clean up any previous builds
    build_dirs = ['build', 'dist', '__pycache__']
    for dir_name in build_dirs:
        if Path(dir_name).exists():
            print(f"   Cleaning up old {dir_name} directory...")
            shutil.rmtree(dir_name)
    
    # PyInstaller command - creating a single file executable
    cmd = [
        'pyinstaller',
        '--onefile',                    # Single executable file
        '--name=termicast',            # Name of the executable
        '--console',                   # Keep console window
        '--noconfirm',                 # Overwrite without asking
        '--clean',                     # Clean cache before build
        '--add-data', 'data/*:data',   # Include data files
        '--add-data', 'tle/*:tle',     # Include TLE files if they exist
        '--hidden-import', 'skyfield.documentation',
        '--hidden-import', 'numpy.core._dtype_ctypes',
        '--hidden-import', 'pkg_resources.py2_warn',
        'termicast_main.py'            # Use the standalone entry point
    ]
    
    # Add some extra options to make it more robust
    extra_options = [
        '--collect-data', 'skyfield',   # Collect skyfield data files
        '--collect-data', 'rich',       # Rich console data
        '--exclude-module', 'tkinter',  # We don't need GUI stuff
        '--exclude-module', 'matplotlib.backends._backend_tk',
    ]
    
    cmd.extend(extra_options)
    
    print("   Running PyInstaller...")
    print(f"   Command: {' '.join(cmd)}")
    
    try:
        # Run the build command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build successful!")
            
            # Check if the executable was created
            exe_path = Path("dist/termicast")
            if sys.platform == "win32":
                exe_path = Path("dist/termicast.exe")
            
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"   📦 Executable created: {exe_path}")
                print(f"   📏 Size: {size_mb:.1f} MB")
                print(f"   🎉 You can now run: ./{exe_path}")
                
                # Test the executable quickly
                print("\n🧪 Testing the executable...")
                test_result = subprocess.run([str(exe_path), '--version'], 
                                           capture_output=True, text=True)
                if test_result.returncode == 0:
                    print("✅ Executable test passed!")
                    print(f"   Version output: {test_result.stdout.strip()}")
                else:
                    print("⚠️  Executable test failed, but it might still work")
                    
            else:
                print("❌ Executable not found in expected location")
                
        else:
            print(f"❌ Build failed with return code {result.returncode}")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            
    except FileNotFoundError:
        print("❌ PyInstaller not found!")
        print("   Install it with: pip install pyinstaller")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    # Clean up build artifacts but keep the dist folder
    if Path('build').exists():
        print("   🧹 Cleaning up build artifacts...")
        shutil.rmtree('build')
    
    # Remove spec file
    spec_file = Path('termicast.spec')
    if spec_file.exists():
        spec_file.unlink()
        
    print("\n🎯 Build process complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 