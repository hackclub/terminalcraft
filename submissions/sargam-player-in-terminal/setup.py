import os
from pathlib import Path

def create_directories():
    directories = ["sounds", "recordings"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created {directory}/ directory")


def main():
    print("Setting up Indian Classical Music Terminal Instrument\n")
    
    create_directories()
    create_readme()
    create_sample_sounds_info()
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Add your .wav sound files to the sounds/ directory")
    print("3. Run the application: python main.py")
    print("\nSee README.md for detailed instructions.")
    print("Happy music making!")

if __name__ == "__main__":
    main()