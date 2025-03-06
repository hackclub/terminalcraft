import os
import shutil
import json

UNDO_LOG_FILE = "undo_log.json"

def undo_last_operation():
    if not os.path.exists(UNDO_LOG_FILE):
        print("\n❌ No undo log found! Nothing to undo.")
        return
    
    with open(UNDO_LOG_FILE, "r") as log:
        moved_files = json.load(log)

    for entry in moved_files:
        if os.path.exists(entry["new"]):
            shutil.move(entry["new"], entry["original"])
    
    os.remove(UNDO_LOG_FILE)
    print("\n✅ Undo successful! Files restored to original locations.")
