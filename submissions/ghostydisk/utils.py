import os
import hashlib
import time
import json
from typing import List, Tuple, Dict, Any
from datetime import datetime

from display import format_size

BUFFER_READ_LIMIT = 8 * 1024 * 1024

def get_file_size(path):
    return os.path.getsize(path)


def get_file_age(path):
    last_modified = os.path.getmtime(path)
    return time.time() - last_modified


def hash_file(path, algorithm='md5'):
    hash_algorithms = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256
    }
    
    if algorithm not in hash_algorithms:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}. Supported algorithms are: {', '.join(hash_algorithms.keys())}")
    
    hasher = hash_algorithms[algorithm]()
    
    try:
        with open(path, 'rb') as f:
            buf = f.read(BUFFER_READ_LIMIT)
            while buf:
                hasher.update(buf)
                buf = f.read(BUFFER_READ_LIMIT)
        return hasher.hexdigest()
    except Exception as e:
        raise Exception(f"Error calculating hash for {path}: {str(e)}")


def results_to_list(results, show_both_duplicates=False, kind=False):
    out = []

    if kind:
        out.extend([("ghost", g) for g in results['ghosts']])
        out.extend([("large", f[0]) for f in results['large']])
        out.extend([("old", f[0]) for f in results['old']])
        if show_both_duplicates == False:
            out.extend([("duplicate", item[1][0]) for item in results['duplicates'].items()])
        else:
            for key, dup in results['duplicates'].items():
                for item in dup:
                    out.append(("duplicate", item))
    else:
        out.extend(results['ghosts'])
        out.extend([f[0] for f in results['large']])
        out.extend([f[0] for f in results['old']])
        if show_both_duplicates == False:
            out.extend([item[1][0] for item in results['duplicates'].items()])
        else:
            for key, dup in results['duplicates'].items():
                for item in dup:
                    out.append(item)

    return list(set(out))

def export_results(results: Dict[str, Any], format_type: str, output_path: str = None):
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"ghostydisk_scan_{timestamp}"

    if format_type == "txt":
        return export_txt(results, output_path)
    elif format_type == "json":
        return export_json(results, output_path)
    elif format_type == "md":
        return export_markdown(results, output_path)
    else:
        raise ValueError(f"Unsupported format: {format_type}")

def export_txt(results: Dict[str, Any], output_path: str) -> str:
    output_file = f"{output_path}.txt"
    
    with open(output_file, 'w') as f:
        f.write("GhostyDisk Scan Results\n")
        f.write("=" * 50 + "\n\n")
        
        # Ghost Files
        f.write("👻 Ghost Files:\n")
        f.write("-" * 30 + "\n")
        for path, size, age in results["ghosts"]:
            f.write(f"Path: {path}\n")
            f.write(f"Size: {format_size(size)}\n")
            f.write(f"Age: {age // (24*3600)} days\n\n")
        
        # Large Files
        f.write("💾 Large Files:\n")
        f.write("-" * 30 + "\n")
        for path, size in results["large"]:
            f.write(f"Path: {path}\n")
            f.write(f"Size: {format_size(size)}\n\n")
        
        # Old Files
        f.write("⌛ Old Files:\n")
        f.write("-" * 30 + "\n")
        for path, age in results["old"]:
            f.write(f"Path: {path}\n")
            f.write(f"Age: {age // (24*3600)} days\n\n")
        
        # Duplicates
        f.write("🌀 Duplicate Files:\n")
        f.write("-" * 30 + "\n")
        for hash_val, paths in results["duplicates"].items():
            f.write(f"Hash: {hash_val}\n")
            for path in paths:
                f.write(f"  - {path}\n")
            f.write("\n")
    
    return output_file

def export_json(results: Dict[str, Any], output_path: str) -> str:
    output_file = f"{output_path}.json"
    
    json_data = {
        "ghost_files": [
            {
                "path": path,
                "size": size,
                "age_days": age // (24*3600)
            }
            for path, size, age in results["ghosts"]
        ],
        "large_files": [
            {
                "path": path,
                "size": size
            }
            for path, size in results["large"]
        ],
        "old_files": [
            {
                "path": path,
                "age_days": age // (24*3600)
            }
            for path, age in results["old"]
        ],
        "duplicates": {
            hash_val: paths
            for hash_val, paths in results["duplicates"].items()
        }
    }
    
    with open(output_file, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    return output_file

def export_markdown(results: Dict[str, Any], output_path: str) -> str:
    output_file = f"{output_path}.md"
    
    with open(output_file, 'w') as f:
        f.write("# GhostyDisk Scan Results\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Ghost Files
        f.write("## 👻 Ghost Files\n\n")
        if results["ghosts"]:
            f.write("| Path | Size | Age |\n")
            f.write("|------|------|-----|\n")
            for path, size, age in results["ghosts"]:
                f.write(f"| `{path}` | {format_size(size)} | {age // (24*3600)} days |\n")
        else:
            f.write("No ghost files found.\n")
        f.write("\n")
        
        # Large Files
        f.write("## 💾 Large Files\n\n")
        if results["large"]:
            f.write("| Path | Size |\n")
            f.write("|------|------|\n")
            for path, size in results["large"]:
                f.write(f"| `{path}` | {format_size(size)} |\n")
        else:
            f.write("No large files found.\n")
        f.write("\n")
        
        # Old Files
        f.write("## ⌛ Old Files\n\n")
        if results["old"]:
            f.write("| Path | Age |\n")
            f.write("|------|-----|\n")
            for path, age in results["old"]:
                f.write(f"| `{path}` | {age // (24*3600)} days |\n")
        else:
            f.write("No old files found.\n")
        f.write("\n")
        
        # Duplicates
        f.write("## 🌀 Duplicate Files\n\n")
        if results["duplicates"]:
            for hash_val, paths in results["duplicates"].items():
                f.write(f"### Hash: `{hash_val}`\n\n")
                for path in paths:
                    f.write(f"- `{path}`\n")
                f.write("\n")
        else:
            f.write("No duplicate files found.\n")
    
    return output_file