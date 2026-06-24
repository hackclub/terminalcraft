import os
import sys
import hashlib
import json
import time
import fnmatch
from pathlib import Path
from datetime import datetime
from collections import defaultdict

try:
    from termcolor import colored
except ImportError:
    def colored(text, color=None):
        return text

try:
    import notify2
    notify2_inited = False
except ImportError:
    notify2 = None
    notify2_inited = False

HASH_DB_DIR = Path.home() / ".heimdall"
HASH_DB_DIR.mkdir(exist_ok=True)
IGNORE_FILE_NAME = ".heimdallignore"

class FileInfo:
    def __init__(self, path, hash_val, mtime, size):
        self.path = path
        self.hash = hash_val
        self.mtime = mtime
        self.size = size
    
    def to_dict(self):
        return {"hash": self.hash, "mtime": self.mtime, "size": self.size}
    
    @classmethod
    def from_dict(cls, path, data):
        return cls(path, data["hash"], data["mtime"], data["size"])

def get_hasher(alg):
    try:
        hashlib.new(alg)
    except ValueError:
        print(f"Invalid hash algorithm '{alg}'. Falling back to sha256.")
        alg = "sha256"
    
    def hash_func(filepath):
        h = hashlib.new(alg)
        try:
            with open(filepath, "rb") as f:
                while chunk := f.read(65536):
                    h.update(chunk)
            return h.hexdigest()
        except (IOError, OSError) as e:
            print(f"Error hashing {filepath}: {e}")
            return None
    return hash_func

def load_hash_db(db_path):
    if not db_path.exists():
        return {}
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {path: FileInfo.from_dict(path, info) for path, info in data.items()}
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error loading hash database: {e}")
        return {}

def save_hash_db(db_path, file_infos):
    data = {path: info.to_dict() for path, info in file_infos.items()}
    try:
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"Error saving hash database: {e}")

def load_ignore_patterns(folder):
    ignore_path = Path(folder) / IGNORE_FILE_NAME
    if not ignore_path.exists():
        return []
    
    try:
        with open(ignore_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return [line.strip() for line in lines if line.strip() and not line.startswith("#")]
    except IOError as e:
        print(f"Error loading ignore file: {e}")
        return []

def should_ignore(path, ignore_patterns):
    path_str = str(path)
    basename = os.path.basename(path_str)
    
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(basename, pattern):
            return True
    return False

def scan_folder(folder, ignore_patterns, hash_func, verbose=False):
    file_infos = {}
    total_files = 0
    processed_files = 0
    
    for root, _, files in os.walk(folder):
        total_files += len(files)
    
    for root, _, files in os.walk(folder):
        for file in files:
            path = os.path.join(root, file)
            
            if should_ignore(path, ignore_patterns):
                if verbose:
                    print(f"Ignored: {path}")
                continue
            
            try:
                stat = os.stat(path)
                hash_val = hash_func(path)
                
                if hash_val:
                    file_info = FileInfo(path, hash_val, stat.st_mtime, stat.st_size)
                    file_infos[path] = file_info
                    processed_files += 1
                    
                    if verbose:
                        print(f"[{processed_files}/{total_files}] Hashed: {path}")
                        
            except (OSError, IOError) as e:
                if verbose:
                    print(f"Error processing {path}: {e}")
                continue
    
    return file_infos

def detect_moves(added_files, deleted_files, old_infos, new_infos):
    moves = []
    hash_to_deleted = defaultdict(list)
    hash_to_added = defaultdict(list)
    
    for deleted_path in deleted_files:
        if deleted_path in old_infos:
            file_hash = old_infos[deleted_path].hash
            hash_to_deleted[file_hash].append(deleted_path)
    
    for added_path in added_files:
        if added_path in new_infos:
            file_hash = new_infos[added_path].hash
            hash_to_added[file_hash].append(added_path)
    
    for file_hash in hash_to_deleted:
        if file_hash in hash_to_added:
            deleted_paths = hash_to_deleted[file_hash]
            added_paths = hash_to_added[file_hash]
            
            min_pairs = min(len(deleted_paths), len(added_paths))
            
            for i in range(min_pairs):
                old_path = deleted_paths[i]
                new_path = added_paths[i]
                old_info = old_infos[old_path]
                new_info = new_infos[new_path]
                
                if (old_info.size == new_info.size and 
                    abs(old_info.mtime - new_info.mtime) < 2):
                    moves.append((old_path, new_path))
    
    actual_added = []
    actual_deleted = []
    moved_old_paths = {move[0] for move in moves}
    moved_new_paths = {move[1] for move in moves}
    
    for path in added_files:
        if path not in moved_new_paths:
            actual_added.append(path)
    
    for path in deleted_files:
        if path not in moved_old_paths:
            actual_deleted.append(path)
    
    return moves, actual_added, actual_deleted

def compare_hashes(old_infos, new_infos):
    old_files = set(old_infos.keys())
    new_files = set(new_infos.keys())
    
    added_files = list(new_files - old_files)
    deleted_files = list(old_files - new_files)
    modified_files = []
    
    for path in new_files & old_files:
        if new_infos[path].hash != old_infos[path].hash:
            modified_files.append(path)
    
    moves, actual_added, actual_deleted = detect_moves(
        added_files, deleted_files, old_infos, new_infos
    )
    
    return actual_added, actual_deleted, modified_files, moves

def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

def format_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)}B"
    return f"{size:.1f}{units[unit_index]}"

def print_report(added, deleted, modified, moves, file_infos, show_size=False):
    lines = []
    total_changes = len(added) + len(deleted) + len(modified) + len(moves)
    
    if total_changes == 0:
        lines.append(colored("✔️ No changes detected.", "green"))
    else:
        if moves:
            lines.append(colored(f"\n🔄 Moved files ({len(moves)}):", "blue"))
            for old_path, new_path in sorted(moves):
                if show_size and new_path in file_infos:
                    size_str = f" [{format_size(file_infos[new_path].size)}]"
                else:
                    size_str = ""
                lines.append(f"  {old_path} → {new_path}{size_str}")
        
        if added:
            lines.append(colored(f"\n🟢 Added files ({len(added)}):", "green"))
            for path in sorted(added):
                if show_size and path in file_infos:
                    size_str = f" [{format_size(file_infos[path].size)}]"
                else:
                    size_str = ""
                mtime_str = format_time(file_infos[path].mtime)
                lines.append(f"  + {path}{size_str} (mtime: {mtime_str})")
        
        if deleted:
            lines.append(colored(f"\n🔴 Deleted files ({len(deleted)}):", "red"))
            for path in sorted(deleted):
                lines.append(f"  - {path}")
        
        if modified:
            lines.append(colored(f"\n🟠 Modified files ({len(modified)}):", "yellow"))
            for path in sorted(modified):
                if show_size and path in file_infos:
                    size_str = f" [{format_size(file_infos[path].size)}]"
                else:
                    size_str = ""
                mtime_str = format_time(file_infos[path].mtime)
                lines.append(f"  * {path}{size_str} (mtime: {mtime_str})")
    
    output = "\n".join(lines)
    print(output)
    return output

def send_notification(title, message):
    global notify2_inited
    if notify2 is None:
        return
    
    try:
        if not notify2_inited:
            notify2.init("Heimdall")
            notify2_inited = True
        
        notification = notify2.Notification(title, message)
        notification.show()
    except Exception as e:
        print(f"Notification error: {e}")

def get_folder_hash(folder_path):
    return hashlib.sha256(str(Path(folder_path).resolve()).encode()).hexdigest()[:12]

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Heimdall - File Integrity Monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("folder", nargs="?", help="Folder to monitor (optional for --reset)")
    parser.add_argument("-w", "--watch", action="store_true", help="Continuous monitoring mode")
    parser.add_argument("-i", "--interval", type=int, default=5, help="Watch interval in seconds (default: 5)")
    parser.add_argument("-r", "--reset", action="store_true", help="Reset hash database")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-o", "--output", help="Append reports to file")
    parser.add_argument("-a", "--algorithm", default="sha256", help="Hash algorithm (default: sha256)")
    parser.add_argument("-s", "--show-size", action="store_true", help="Show file sizes")
    parser.add_argument("--no-notifications", action="store_true", help="Disable desktop notifications")
    
    args = parser.parse_args()

    if args.reset:
        if args.folder:
            folder_path = Path(args.folder).resolve()
            if not folder_path.is_dir():
                print(f"Error: '{folder_path}' is not a directory.")
                return 1
            folder_hash = get_folder_hash(folder_path)
            db_path = HASH_DB_DIR / f"heimdall_{folder_hash}.json"
            if db_path.exists():
                db_path.unlink()
                print(colored(f"✅ Hash database reset for '{folder_path}'.", "cyan"))
            else:
                print(colored(f"ℹ️ No hash database found for '{folder_path}'.", "yellow"))
        else:
            db_files = list(HASH_DB_DIR.glob("heimdall_*.json"))
            if db_files:
                for db_file in db_files:
                    db_file.unlink()
                print(colored(f"✅ All hash databases cleared ({len(db_files)} files).", "cyan"))
            else:
                print(colored("ℹ️ No hash databases found to clear.", "yellow"))
        return 0

    if not args.folder:
        print("Error: Please specify a folder to monitor.")
        parser.print_help()
        return 1

    folder_path = Path(args.folder).resolve()
    if not folder_path.is_dir():
        print(f"Error: '{folder_path}' is not a directory.")
        return 1

    # FIXED: Load ignore patterns here, after folder_path is defined
    ignore_patterns = load_ignore_patterns(folder_path)
    hash_func = get_hasher(args.algorithm)
    
    folder_hash = get_folder_hash(folder_path)
    db_path = HASH_DB_DIR / f"heimdall_{folder_hash}.json"

    print(f"📁 Monitoring: {folder_path}")
    if ignore_patterns:
        print(f"🚫 Ignoring: {', '.join(ignore_patterns)}")
    print(f"💾 Database: {db_path}")
    print(f"🔐 Algorithm: {args.algorithm}")
    
    if args.watch:
        print(f"⏱️ Interval: {args.interval}s")
        print("Press Ctrl+C to stop.\n")

    old_file_infos = load_hash_db(db_path)

    if not old_file_infos:
        print("Creating baseline...")
        new_file_infos = scan_folder(folder_path, ignore_patterns, hash_func, verbose=args.verbose)
        save_hash_db(db_path, new_file_infos)
        print(colored(f"✅ Baseline created with {len(new_file_infos)} files.", "cyan"))
        return 0

    def check_changes():
        nonlocal old_file_infos
        
        if args.verbose:
            print(f"Scanning {folder_path}...")
        
        new_file_infos = scan_folder(folder_path, ignore_patterns, hash_func, verbose=args.verbose)
        added, deleted, modified, moves = compare_hashes(old_file_infos, new_file_infos)

        total_changes = len(added) + len(deleted) + len(modified) + len(moves)
        
        if total_changes > 0:
            report = print_report(added, deleted, modified, moves, new_file_infos, show_size=args.show_size)
            change_summary = f"Changes: +{len(added)} -{len(deleted)} *{len(modified)} ↔{len(moves)}"
            
            if not args.no_notifications:
                send_notification("heimdall alert", change_summary)
            
            old_file_infos = new_file_infos
            save_hash_db(db_path, new_file_infos)
            
            if args.output:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                try:
                    with open(args.output, "a", encoding="utf-8") as f:
                        f.write(f"\n{'='*50}\n")
                        f.write(f"Report: {timestamp}\n")
                        f.write(f"{'='*50}\n")
                        f.write(report + "\n")
                except IOError as e:
                    print(f"Error writing to output file: {e}")
            
            print(colored(f"\n💾 Database updated at {datetime.now().strftime('%H:%M:%S')}", "cyan"))
        else:
            if args.watch:
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"\r✅ No changes detected at {timestamp}", end="", flush=True)
            else:
                print(colored("✔️ No changes detected.", "green"))

    if args.watch:
        try:
            while True:
                check_changes()
                if args.verbose:
                    print(f"\n⏳ Waiting {args.interval}s...")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nstopping heimdall. farewell 👋")
            return 0
    else:
        check_changes()
        return 0

if __name__ == "__main__":
    sys.exit(main())
