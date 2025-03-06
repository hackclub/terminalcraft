import os
import shutil
import json
import config

UNDO_LOG_FILE = "undo_log.json"

def organize_files(folder_path):
    moved_files = []
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        if os.path.isfile(file_path):
            ext = filename.split(".")[-1].lower()
            category = config.FILE_TYPES.get(ext, "Other")
            dest_folder = os.path.join(folder_path, category)
            
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
            
            new_path = os.path.join(dest_folder, filename)
            shutil.move(file_path, new_path)
            moved_files.append({"original": file_path, "new": new_path})
    
    if moved_files:
        with open(UNDO_LOG_FILE, "w") as log:
            json.dump(moved_files, log, indent=4)
        print("\n✅ Files organized successfully! Undo log saved.")
    else:
        print("\nNo files found to organize.")
