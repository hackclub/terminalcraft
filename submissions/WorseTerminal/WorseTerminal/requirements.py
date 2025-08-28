import subprocess, sys, time, os

PACKAGES = {
    "termcolor": "termcolor",
    "colorama": "colorama",
    "textblob": "textblob"
}

def install_package(package_name):
    is_virtual_env = sys.prefix != sys.base_prefix
    
    command = [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", package_name]

    if not is_virtual_env:
        print(f"-> Installing {package_name} for the current user (no virtual environment detected)...")
        command.append("--user")
    else:
        print(f"-> Installing {package_name} in the active virtual environment...")

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(f"   [OK] Successfully installed {package_name}.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   [ERROR] Failed to install {package_name}.")
        print(f"   Details: {e.stderr.strip()}")
        return False
    except FileNotFoundError:
        print("   [ERROR] 'pip' command not found. Please ensure Python and pip are correctly installed and in your system's PATH.")
        return False

def check_and_install_dependencies():
    print("--- Starting Dependency Check ---")
    all_good = True
    
    for package, module in PACKAGES.items():
        try:
            __import__(module)
            print(f"[✓] {package.capitalize()} is already installed.")
        except ImportError:
            print(f"[!] {package.capitalize()} is not installed.")
            if not install_package(package):
                all_good = False
    
    print("\n--- Dependency Check Complete ---")
    if all_good:
        print("All required packages are installed. You can now run the main application.")
    else:
        print("One or more packages could not be installed. Please review the errors above.")

def install_corpora():
    try:
        from textblob import Word
        Word("test").definitions  # Attempt access to force loading
    except LookupError:
        print("Downloading required corpora for TextBlob...")
        try:
            from textblob import download_corpora
            download_corpora.download_all()
            print("   [OK] Corpora downloaded.")
        except Exception as e:
            print(f"   [ERROR] Failed to download corpora: {e}")
            print("Try running requirements.py again.")
        

if __name__ == "__main__":
    if os.name == 'nt':
        os.system('title Dependency Installer')

    check_and_install_dependencies()
    install_corpora()
    
    print("\nThis window will close in 5 seconds...")
    time.sleep(5)
