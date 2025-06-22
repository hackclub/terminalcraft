#!/usr/bin/env python3
"""
Test Meet-Zone locally without building executable
This helps determine if the issue is with the code or PyInstaller
"""

import sys
import os
import traceback

def test_local_execution():
    """Test running the application locally"""
    print("Testing Meet-Zone locally...")
    print("=" * 40)
    
    try:
        # Add src to path
        sys.path.insert(0, 'src')
        
        # Import and run the main function
        from meet_zone.__main__ import main
        
        print("Starting application...")
        result = main()
        print(f"Application exited with code: {result}")
        
    except KeyboardInterrupt:
        print("Application interrupted by user")
    except Exception as e:
        print(f"Application failed: {e}")
        traceback.print_exc()

def test_ui_only():
    """Test just the UI component"""
    print("\nTesting UI component only...")
    print("=" * 40)
    
    try:
        sys.path.insert(0, 'src')
        
        from meet_zone.ui import MeetZoneApp
        
        print("Creating MeetZone app...")
        app = MeetZoneApp()
        
        print("Starting UI...")
        app.run()
        
    except KeyboardInterrupt:
        print("UI interrupted by user")
    except Exception as e:
        print(f"UI failed: {e}")
        traceback.print_exc()

def main():
    """Main test function"""
    print("Meet-Zone Local Test")
    print("=" * 20)
    
    choice = input("Test (1) Full app or (2) UI only? [1]: ").strip() or "1"
    
    if choice == "1":
        test_local_execution()
    elif choice == "2":
        test_ui_only()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()