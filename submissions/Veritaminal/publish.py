#!/usr/bin/env python3
"""
PyPI Publishing Script for Veritaminal

This script builds and publishes the Veritaminal package to PyPI.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Ensure all required publishing tools are installed."""
    required = ["twine", "build"]
    for package in required:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing required publishing dependency: {package}")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)

def build_package():
    """Build the package using Python build."""
    print("Building package...")
    subprocess.run([sys.executable, "-m", "build"], check=True)

def upload_to_test_pypi():
    """Upload the built package to TestPyPI first."""
    print("Uploading to TestPyPI...")
    # Using local .pypirc file
    pypirc_path = os.path.join(os.path.dirname(__file__), ".pypirc")
    subprocess.run([
        sys.executable, "-m", "twine", "upload", 
        "--repository", "testpypi",
        "--config-file", pypirc_path,
        "dist/*"
    ], check=True)

def upload_to_pypi():
    """Upload the built package to PyPI."""
    print("Uploading to PyPI...")
    # Using local .pypirc file
    pypirc_path = os.path.join(os.path.dirname(__file__), ".pypirc")
    subprocess.run([
        sys.executable, "-m", "twine", "upload",
        "--config-file", pypirc_path,
        "dist/*"
    ], check=True)

def clean():
    """Clean build artifacts."""
    print("Cleaning build artifacts...")
    for path in ["build", "dist", "*.egg-info"]:
        try:
            subprocess.run(["rm", "-rf", path], check=True)
        except Exception:
            # On Windows, rmdir is different
            if os.name == "nt":
                if path == "*.egg-info":
                    for egg_info in Path("").glob("*.egg-info"):
                        subprocess.run(["rmdir", "/S", "/Q", str(egg_info)], shell=True)
                else:
                    subprocess.run(["rmdir", "/S", "/Q", path], shell=True)

def main():
    """Run the publishing workflow."""
    try:
        choice = input("Do you want to publish to [T]estPyPI, [P]yPI, or [B]oth? ").lower()
        
        check_dependencies()
        
        # Clean first
        clean()
        
        # Build the package
        build_package()
        
        # Upload based on choice
        if choice == 't' or choice == 'b':
            upload_to_test_pypi()
        
        if choice == 'p' or choice == 'b':
            upload_to_pypi()
        
        print("Package publishing complete!")
        
    except Exception as e:
        print(f"Error during publishing: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
