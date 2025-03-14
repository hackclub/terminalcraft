import os
import sys
import shutil
import subprocess

def create_executable():
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        
        print("Creating executable...")
        subprocess.run([
            "pyinstaller",
            "--onefile",
            "--name=system_monitor",
            "--clean",
            "--add-data=README.md;.",
            "--icon=NONE",
            "system_monitor.py"
        ], check=True)
        
        print("Executable created successfully!")
        print(f"You can find it in the 'dist' folder: {os.path.join(os.getcwd(), 'dist', 'system_monitor.exe')}")
        
        return True
    except Exception as e:
        print(f"Error creating executable: {e}")
        return False

def create_zip_package():
    try:
        package_dir = "system_monitor_package"
        if os.path.exists(package_dir):
            shutil.rmtree(package_dir)
        os.makedirs(package_dir)
        
        files_to_copy = [
            "system_monitor.py",
            "README.md",
            "requirements.txt",
            "setup.py"
        ]
        
        for file in files_to_copy:
            if os.path.exists(file):
                shutil.copy(file, package_dir)
        
        shutil.make_archive("system_monitor", "zip", ".", package_dir)
        
        shutil.rmtree(package_dir)
        
        print("Zip package created successfully!")
        print(f"You can find it here: {os.path.join(os.getcwd(), 'system_monitor.zip')}")
        
        return True
    except Exception as e:
        print(f"Error creating zip package: {e}")
        return False

def main():
    print("System Monitor Packaging Tool")
    print("-----------------------------")
    print("1. Create executable (requires PyInstaller)")
    print("2. Create zip package")
    print("3. Both")
    print("4. Exit")
    
    choice = input("Enter your choice (1-4): ")
    
    if choice == "1":
        create_executable()
    elif choice == "2":
        create_zip_package()
    elif choice == "3":
        create_executable()
        create_zip_package()
    elif choice == "4":
        print("Exiting...")
        return
    else:
        print("Invalid choice")
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
