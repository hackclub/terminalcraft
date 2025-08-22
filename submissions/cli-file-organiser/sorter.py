import os
import shutil
import argparse
import json
import datetime
import threading
import time
from tqdm import tqdm

CONFIG_FILE = "config.json"
UNDO_FILE = "undo_log.json"

# Default categories
DEFAULT_CATEGORIES = {
    "Programs": ["py", "c", "cpp", "java", "exe", "sh", "bat"],
    "Documents": ["pdf", "docx", "txt", "xls", "ppt"],
    "Images": ["png", "jpg", "jpeg", "gif", "bmp"],
    "Videos": ["mp4", "mkv", "avi", "mov"],
    "Music": ["mp3", "wav", "flac"],
    "Archives": ["zip", "rar", "tar", "gz"],
    "Large Files": [],
    "Uncategorized": []
}

def generate_default_config():
    """Creates a default config file if none exists."""
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as file:
            json.dump({"categories": DEFAULT_CATEGORIES, "large_file_size": 100}, file, indent=4)
        print("Created default config.json")

def load_config():
    """Loads user-defined config file if available."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {"categories": DEFAULT_CATEGORIES, "large_file_size": 100}

def log_action(log_file, message):
    """Logs actions to a file if logging is enabled."""
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    log_entry = f"{timestamp} {message}"
    
    if log_file:
        with open(log_file, "a") as log:
            log.write(log_entry + "\n")
    
    print(log_entry)

def get_file_extension(file):
    """Returns file extension in lowercase."""
    return file.split(".")[-1].lower() if "." in file else ""

def move_file(file_path, dest_folder, interactive, dry_run, log_file, undo_log):
    """Moves a file to the destination folder, with dry-run support."""
    os.makedirs(dest_folder, exist_ok=True)
    file_name = os.path.basename(file_path)
    dest_file = os.path.join(dest_folder, file_name)

    if interactive:
        confirm = input(f"Move {file_name} to {dest_folder}? (y/n): ").strip().lower()
        if confirm != "y":
            return

    if dry_run:
        log_action(log_file, f"[Dry Run] Would move: {file_name} -> {dest_folder}")
        return

    # Prevent overwriting
    counter = 1
    while os.path.exists(dest_file):
        name, ext = os.path.splitext(file_name)
        dest_file = os.path.join(dest_folder, f"{name}_{counter}{ext}")
        counter += 1

    shutil.move(file_path, dest_file)
    undo_log[file_name] = file_path
    log_action(log_file, f"Moved: {file_name} -> {dest_folder}")

def sort_files(folder_path, config, log_file, interactive, review_folder, large_file_size, ignored_files, ignored_folders, dry_run, sort_by):
    """Sorts files based on user settings."""
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    categories = config.get("categories", DEFAULT_CATEGORIES)
    large_file_limit = config.get("large_file_size", large_file_size)
    undo_log = {}

    # Sorting option
    if sort_by == "name":
        files.sort()

    start_time = time.time()

    # Progress bar
    for file in tqdm(files, desc="Sorting Files", unit="file"):
        file_path = os.path.join(folder_path, file)

        if file in ignored_files or any(folder in file_path for folder in ignored_folders):
            continue

        file_ext = get_file_extension(file)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB
        dest_folder = None

        if file_size > large_file_limit:
            dest_folder = os.path.join(folder_path, "Large Files")

        for category, extensions in categories.items():
            if file_ext in extensions:
                dest_folder = os.path.join(folder_path, category)
                break

        if not dest_folder:
            dest_folder = os.path.join(folder_path, "Uncategorized")

        if review_folder:
            dest_folder = os.path.join(folder_path, "Review", os.path.basename(dest_folder))

        move_file(file_path, dest_folder, interactive, dry_run, log_file, undo_log)

    if not dry_run:
        with open(UNDO_FILE, "w") as undo_file:
            json.dump(undo_log, undo_file)

    elapsed_time = time.time() - start_time
    print(f"Sorting completed in {elapsed_time:.2f} seconds")

def undo_last_sort(log_file):
    """Restores files to their original locations using undo_log.json."""
    if not os.path.exists(UNDO_FILE):
        print("No undo log found. Nothing to restore.")
        return
    
    with open(UNDO_FILE, "r") as undo_file:
        undo_log = json.load(undo_file)
    
    for file_name, original_path in tqdm(undo_log.items(), desc="Restoring Files", unit="file"):
        for root, _, files in os.walk(os.path.dirname(original_path)):
            if file_name in files:
                current_path = os.path.join(root, file_name)
                shutil.move(current_path, original_path)
                log_action(log_file, f"Restored: {file_name} -> {original_path}")
                break
    
    os.remove(UNDO_FILE)
    log_action(log_file, "Undo completed. Files restored.")

def main():
    generate_default_config()
    parser = argparse.ArgumentParser(description="CLI Directory Management System")
    parser.add_argument("folders", nargs="*", help="Folder(s) to organize")
    parser.add_argument("--log", help="Log file path", default=None)
    parser.add_argument("--config", help="Config file path", default=CONFIG_FILE)
    parser.add_argument("--interactive", action="store_true", help="Ask before moving files")
    parser.add_argument("--review-folder", action="store_true", help="Move files to a review folder first")
    parser.add_argument("--sort-by", choices=["date", "name"], help="Sort files by date or name")
    parser.add_argument("--large-files", type=int, help="Threshold for large files in MB", default=100)
    parser.add_argument("--ignore", nargs="*", help="Files or folders to ignore", default=[])
    parser.add_argument("--threads", type=int, help="Number of threads for batch sorting", default=4)
    parser.add_argument("--dry-run", action="store_true", help="Simulate sorting without moving files")
    parser.add_argument("--undo", action="store_true", help="Undo the last sorting operation")

    args = parser.parse_args()
    config = load_config()

    if args.undo:
        undo_last_sort(args.log)
        return

    if not args.folders:
        print("Error: No folders specified for sorting.")
        return

    for folder in args.folders:
        if not os.path.exists(folder):
            print(f"Error: Folder '{folder}' does not exist.")
            return

    for folder in args.folders:
        sort_files(
            folder, config, args.log, args.interactive, args.review_folder,
            args.large_files, args.ignore, args.ignore, args.dry_run, args.sort_by
        )

if __name__ == "__main__":
    main()
