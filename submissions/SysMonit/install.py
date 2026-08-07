
import subprocess
import sys
import os
import platform

def run_command(cmd, check=True):
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        return result.returncode == 0
    except subprocess.CalledProcessError:
        return False

def install_dependencies():
    print("🔧 Installing System Analyzer...")
    print("📦 Installing Python dependencies...")
    
    pip_commands = ['pip3 install -r requirements.txt', 'pip install -r requirements.txt']
    
    for cmd in pip_commands:
        if run_command(cmd, check=False):
            print("✅ Dependencies installed successfully!")
            return True
    
    print("❌ Failed to install dependencies")
    print("Please manually run: pip install psutil rich")
    return False

def create_launcher():
    system = platform.system()
    
    if system == "Windows":
        launcher_content = """@echo off
python main.py
pause
"""
        with open("system_analyzer.bat", "w") as f:
            f.write(launcher_content)
        print("✅ Created system_analyzer.bat launcher")
        
    else:
        launcher_content = """#!/bin/bash
python3 main.py
"""
        with open("system_analyzer.sh", "w") as f:
            f.write(launcher_content)
        
        os.chmod("system_analyzer.sh", 0o755)
        print("✅ Created system_analyzer.sh launcher")

def main():
    print("=" * 50)
    print("🖥️  SYSTEM ANALYZER INSTALLER")
    print("=" * 50)
    
    if not os.path.exists("main.py"):
        print("❌ main.py not found!")
        print("Please make sure all files are in the same directory")
        return
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        return
    
    if install_dependencies():
        create_launcher()
        
        print("\n🎉 Installation complete!")
        print("\n📋 To run the System Analyzer:")
        
        if platform.system() == "Windows":
            print("   • Double-click system_analyzer.bat")
            print("   • Or run: python main.py")
        else:
            print("   • Run: ./system_analyzer.sh")
            print("   • Or run: python3 main.py")
        
        print("\n🔧 Features included:")
        print("   • Storage Analyzer (disk usage, large files)")
        print("   • Network Analyzer (ports, ping, connections)")
        print("   • Task Manager (processes, resource usage)")
        print("   • System Monitor (CPU, memory, sensors)")
        
        print("\n✨ Enjoy analyzing your system!")
    else:
        print("\n❌ Installation failed")
        print("Please install dependencies manually:")
        print("   pip install psutil rich")

if __name__ == "__main__":
    main()