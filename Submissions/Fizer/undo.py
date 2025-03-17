import os
import shutil
import json

UNDO_FILE = "undo.json"

def undo_last_operation():
    if not os.path.exists(UNDO_FILE):
        print("\n⚠ No previous operation to undo.")
        return

    with open(UNDO_FILE, "r") as file:
        data = json.load(file)

    folder = data["folder"]
    moved_files = data["files"]

    for filename, category in moved_files:
        old_path = os.path.join(folder, category, filename)
        new_path = os.path.join(folder, filename)

        if os.path.exists(old_path):
            shutil.move(old_path, new_path)
            print(f"🔄 Restored {filename} -> {folder}")

    os.remove(UNDO_FILE)
    print("\n✅ Undo complete!")
