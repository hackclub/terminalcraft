import os
import shutil
import json
import config

UNDO_FILE = "undo.json"

def organize_files(folder):
    """Organizes files in the given folder based on categories from config.json."""
    categories = config.load_categories()
    moved_files = []

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)

        if os.path.isfile(file_path):
            _, ext = os.path.splitext(filename)
            ext = ext.lower()

            for category, extensions in categories.items():
                if ext in extensions:
                    category_folder = os.path.join(folder, category)
                    os.makedirs(category_folder, exist_ok=True)
                    new_path = os.path.join(category_folder, filename)
                    
                    shutil.move(file_path, new_path)
                    moved_files.append((filename, category))
                    print(f"✅ Moved {filename} -> {category}")

    if moved_files:
        with open(UNDO_FILE, "w") as undo_file:
            json.dump({"folder": folder, "files": moved_files}, undo_file)
        print("\n✅ Organization complete! Undo available.")
    else:
        print("\n⚠ No files matched the categories.")

def auto_arrange(folder):
    """Automatically organizes all files in the given folder."""
    if not os.path.exists(folder):
        print("❌ Error: Folder does not exist!")
        return
    
    print("\n🔄 Auto-arranging files...")
    organize_files(folder)
    print("\n✅ Auto-arrange completed!")
