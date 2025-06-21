#!/usr/bin/env python3
"""
Minimal debug script to test Meet-Zone components individually
This helps identify exactly where the application is failing
"""

import sys
import os
import traceback
import logging

def setup_logging():
    """Setup basic logging"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('debug-minimal.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def test_python_environment():
    """Test basic Python environment"""
    print("=== PYTHON ENVIRONMENT TEST ===")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Executable: {sys.executable}")
    print(f"Frozen (PyInstaller): {getattr(sys, 'frozen', False)}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}...")  # First 3 entries
    print()

def test_basic_imports():
    """Test basic Python imports"""
    print("=== BASIC IMPORTS TEST ===")
    
    # Test standard library
    try:
        import datetime, pathlib, csv, argparse
        print("✓ Standard library imports: OK")
    except Exception as e:
        print(f"✗ Standard library imports: FAILED - {e}")
        return False
    
    # Test tkinter (for error dialogs)
    try:
        import tkinter
        print("✓ Tkinter import: OK")
    except Exception as e:
        print(f"✗ Tkinter import: FAILED - {e}")
    
    return True

def test_third_party_imports():
    """Test third-party library imports"""
    print("=== THIRD-PARTY IMPORTS TEST ===")
    
    # Test pytz
    try:
        import pytz
        print(f"✓ PyTZ import: OK (version: {getattr(pytz, '__version__', 'unknown')})")
    except Exception as e:
        print(f"✗ PyTZ import: FAILED - {e}")
        return False
    
    # Test textual
    try:
        import textual
        print(f"✓ Textual import: OK (version: {textual.__version__})")
    except Exception as e:
        print(f"✗ Textual import: FAILED - {e}")
        return False
    
    return True

def test_textual_components():
    """Test specific Textual components"""
    print("=== TEXTUAL COMPONENTS TEST ===")
    
    try:
        from textual.app import App
        print("✓ textual.app.App: OK")
    except Exception as e:
        print(f"✗ textual.app.App: FAILED - {e}")
        return False
    
    try:
        from textual.widgets import TabbedContent, TabPane
        print("✓ textual.widgets.TabbedContent, TabPane: OK")
    except Exception as e:
        print(f"✗ textual.widgets.TabbedContent, TabPane: FAILED - {e}")
        return False
    
    try:
        from textual.widgets import Button, DataTable, Input, Label, Select
        print("✓ textual.widgets (Button, DataTable, Input, Label, Select): OK")
    except Exception as e:
        print(f"✗ textual.widgets (Button, DataTable, Input, Label, Select): FAILED - {e}")
        return False
    
    try:
        from textual.containers import Container, Horizontal, Vertical
        print("✓ textual.containers: OK")
    except Exception as e:
        print(f"✗ textual.containers: FAILED - {e}")
        return False
    
    return True

def test_application_imports():
    """Test application-specific imports"""
    print("=== APPLICATION IMPORTS TEST ===")
    
    try:
        from meet_zone.parser import parse_roster, Participant
        print("✓ meet_zone.parser: OK")
    except Exception as e:
        print(f"✗ meet_zone.parser: FAILED - {e}")
        return False
    
    try:
        from meet_zone.scheduler import find_best_slots, TimeSlot
        print("✓ meet_zone.scheduler: OK")
    except Exception as e:
        print(f"✗ meet_zone.scheduler: FAILED - {e}")
        return False
    
    try:
        from meet_zone.ui import display_results, MeetZoneApp
        print("✓ meet_zone.ui: OK")
    except Exception as e:
        print(f"✗ meet_zone.ui: FAILED - {e}")
        return False
    
    return True

def test_simple_app_creation():
    """Test creating a simple Textual app"""
    print("=== SIMPLE APP CREATION TEST ===")
    
    try:
        from textual.app import App
        from textual.widgets import Static
        
        class TestApp(App):
            def compose(self):
                yield Static("Test app works!")
        
        app = TestApp()
        print("✓ Simple Textual app creation: OK")
        return True
    except Exception as e:
        print(f"✗ Simple Textual app creation: FAILED - {e}")
        traceback.print_exc()
        return False

def test_meetzone_app_creation():
    """Test creating the actual MeetZone app"""
    print("=== MEETZONE APP CREATION TEST ===")
    
    try:
        from meet_zone.ui import MeetZoneApp
        app = MeetZoneApp()
        print("✓ MeetZone app creation: OK")
        return True
    except Exception as e:
        print(f"✗ MeetZone app creation: FAILED - {e}")
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic tests"""
    setup_logging()
    
    print("Meet-Zone Diagnostic Tool")
    print("=" * 50)
    
    tests = [
        test_python_environment,
        test_basic_imports,
        test_third_party_imports,
        test_textual_components,
        test_application_imports,
        test_simple_app_creation,
        test_meetzone_app_creation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()
        except Exception as e:
            print(f"Test failed with exception: {e}")
            traceback.print_exc()
            results.append(False)
            print()
    
    print("=== SUMMARY ===")
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if all(results):
        print("✓ All tests passed! The issue might be with app execution, not imports.")
    else:
        print("✗ Some tests failed. Check the output above for details.")
    
    print("\nCheck 'debug-minimal.log' for detailed logging.")
    
    # Keep console open on Windows
    if sys.platform == "win32":
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()