import os
from os.path import isfile, isdir
from utils import get_file_size, get_file_age, hash_file
from tqdm import tqdm
from rich.console import Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.table import Table
from rich.layout import Layout
from rich.tree import Tree

GHOSTY_EXTENSIONS = [".tmp", ".bak", ".swp"]

DEFAULT_EXCLUDE_PATTERNS = [
    # Version control
    '.git',
    '.svn',
    '.hg',
    # Package managers
    'node_modules',
    'venv',
    'env',
    '.venv',
    '.env',
    'virtualenv',
    # Build directories
    'build',
    'dist',
    'target',
    'out',
    # IDE specific
    '.idea',
    '.vscode',
    '.vs',
    '.eclipse',
    # Cache directories
    '.cache',
    '__pycache__',
    '.pytest_cache',
    '.coverage',
    # Log files
    '*.log',
    'logs',
    # Temporary files
    'tmp',
    'temp',
    # Dependencies
    'vendor',
    'bower_components',
    'jspm_packages',
    # Database files
    '*.sqlite',
    '*.db',
    # Backup files
    '*.bak',
    '*.backup',
    '*.old',
    # System files
    '.DS_Store',
    'Thumbs.db'
]

def bld_tree(path, max_depth=2, depth=0, scanned_files=None):
    tree = Tree(f"📁 {os.path.basename(path) or path}")
    if depth >= max_depth:
        return tree

    try:
        for entry in sorted(os.listdir(path)):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                subtree = bld_tree(full_path, max_depth, depth + 1, scanned_files)
                tree.add(subtree)
            else:
                if scanned_files and full_path in scanned_files:
                    status = scanned_files[full_path]
                    if status.get('is_ghost'):
                        tree.add(f"[magenta]📄 {entry}[/magenta]")
                    elif status.get('is_large'):
                        tree.add(f"[yellow]📄 {entry}[/yellow]")
                    elif status.get('is_old'):
                        tree.add(f"[red]📄 {entry}[/red]")
                    elif status.get('is_duplicate'):
                        tree.add(f"[blue]📄 {entry}[/blue]")
                    else:
                        tree.add(f"[green]📄 {entry}[/green]")
                else:
                    tree.add(f"📄 {entry}")
    except Exception:
        tree.add("[red]Permission Denied[/red]")
    return tree

def drw_r_panel(progress, scanned, ghost, large, old, duplicates, current_file=None):
    stats = Table.grid(padding=(0, 2))
    stats.add_column(justify="right", style="cyan")
    stats.add_column()
    stats.add_row("Files scanned:", f"{scanned:,}")
    stats.add_row("Ghost files:", f"[magenta]{ghost}[/magenta]")
    stats.add_row("Large files:", f"[yellow]{large}[/yellow]")
    stats.add_row("Old files:", f"[red]{old}[/red]")
    stats.add_row("Duplicate sets:", f"[blue]{duplicates}[/blue]")
    stats.add_row("Time elapsed:", f"{progress.tasks[0].elapsed:0.2f}s")

    header = "[bold blue]🔍 Scanning Files"
    if current_file:
        header += f" - [cyan]{os.path.basename(current_file)}[/cyan]"

    return Group(
        Panel(header, border_style="blue"),
        progress,
        Panel(stats, title="📊 Stats", border_style="green")
    )

def scan_large_files(start_path, start_size=50 * 1024 * 1024, progress=False):
    sizes = []
    size = None

    if isdir(start_path):
        all_files = []
        for root, _, files in os.walk(start_path):
            for name in files:
                all_files.append(os.path.join(root, name))

        iterator = tqdm(all_files, desc="Scanning Large Files") if progress else all_files

        for path in iterator:
            try:
                size = get_file_size(path)
                if size > start_size:
                    sizes.append((path, size))
            except Exception:
                continue
    else:
        sizer = get_file_size(start_path)
        if sizer > 50 * 1024 * 1024:
            size = sizer

    return sizes if sizes else (True, size) if size else (False, sizer)

def scan_old_files(start_path, progress=False):
    results = []

    if isdir(start_path):
        all_files = []
        for root, _, files in os.walk(start_path):
            for name in files:
                all_files.append(os.path.join(root, name))

        iterator = tqdm(all_files, desc="Scanning Old Files") if progress else all_files

        for path in iterator:
            try:
                age = get_file_age(path)
                if age > 180 * 24 * 3600:
                    results.append((path, age))
            except Exception:
                continue
    else:
        age = get_file_age(start_path)
        if age > 180 * 24 * 3600:
            results.append((start_path, age))

    return results if len(results) > 1 else results[0] if len(results) > 0 else None

def scan_duplicates(start_path, progress=False):
    hashes = {}
    dups = {}

    all_files = []
    for root, _, files in os.walk(start_path):
        for name in files:
            all_files.append(os.path.join(root, name))

    iterator = tqdm(all_files, desc="Scanning Duplicates") if progress else all_files

    for full_path in iterator:
        try:
            h = hash_file(full_path)
            if h in hashes:
                dups.setdefault(h, [hashes[h]]).append(full_path)
            else:
                hashes[h] = full_path
        except Exception:
            continue

    return dups


def scan_all(start_path, progress=False, live_ui=False, 
             large_threshold=50 * 1024 * 1024,  # 50MB default
             old_threshold=180 * 24 * 3600,     # 180 days default
             scan_ghosts=True,
             scan_large=True,
             scan_old=True,
             scan_duplicates=True,
             hash_algo='md5',
             exclude_patterns=None):

    results = {
        "ghosts": [],
        "large": [],
        "old": [],
        "duplicates": {}
    }
    hashes = {}
    scanned_files = {}

    # Combine default exclusions with user's ones
    if exclude_patterns is None:
        exclude_patterns = DEFAULT_EXCLUDE_PATTERNS
    elif isinstance(exclude_patterns, str):
        try:
            with open(exclude_patterns, 'r') as f:
                user_patterns = [line.strip() for line in f if line.strip()]
            exclude_patterns = DEFAULT_EXCLUDE_PATTERNS + user_patterns
        except Exception:
            exclude_patterns = DEFAULT_EXCLUDE_PATTERNS + [exclude_patterns]
    else:
        exclude_patterns = DEFAULT_EXCLUDE_PATTERNS + exclude_patterns

    all_files = []
    for root, _, files in os.walk(start_path):
        # Skip excluded dirs
        if any(pattern in root for pattern in exclude_patterns):
            continue
            
        for name in files:
            full_path = os.path.join(root, name)
            # Skip excluded files
            if any(pattern in full_path or name.endswith(pattern.lstrip('*')) for pattern in exclude_patterns):
                continue
            all_files.append(full_path)

    if live_ui:
        progress_bar = Progress(
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            expand=True
        )
        task = progress_bar.add_task("Scan", total=len(all_files))
        
        layout = Layout()
        layout.split_row(
            Layout(Panel(bld_tree(start_path, scanned_files=scanned_files), title="📁 Directory Tree", border_style="magenta"), name="left", ratio=2),
            Layout(name="right", ratio=3)
        )

        scanned = ghost = large = old = duplicates = 0

        with Live(layout, refresh_per_second=10, screen=True):
            for path in all_files:
                try:
                    size = get_file_size(path)
                    age = get_file_age(path)
                    ext = os.path.splitext(path)[1].lower()
                    file_status = {}

                    if scan_ghosts and ext in GHOSTY_EXTENSIONS:
                        results["ghosts"].append((path, size, age))
                        ghost += 1
                        file_status['is_ghost'] = True
                    
                    if scan_large and size > large_threshold:
                        results["large"].append((path, size))
                        large += 1
                        file_status['is_large'] = True
                    
                    if scan_old and age > old_threshold:
                        results["old"].append((path, age))
                        old += 1
                        file_status['is_old'] = True
                    
                    if scan_duplicates:
                        file_hash = hash_file(path, algorithm=hash_algo)
                        if file_hash in hashes:
                            if file_hash not in results["duplicates"]:
                                results["duplicates"][file_hash] = [hashes[file_hash]]
                                duplicates += 1
                            results["duplicates"][file_hash].append(path)
                            file_status['is_duplicate'] = True
                        else:
                            hashes[file_hash] = path
                    
                    scanned_files[path] = file_status
                except Exception:
                    continue
                finally:
                    scanned += 1
                    progress_bar.update(task, advance=1)
                    layout["left"].update(Panel(bld_tree(start_path, scanned_files=scanned_files), title="📁 Directory Tree", border_style="magenta"))
                    right_panel = drw_r_panel(progress_bar, scanned, ghost, large, old, duplicates, current_file=path)
                    layout["right"].update(Panel(right_panel, border_style="cyan"))
        
    else:
        iterator = tqdm(all_files, desc="Full Scan") if progress else all_files
        for path in iterator:
            try:
                size = get_file_size(path)
                age = get_file_age(path)
                ext = os.path.splitext(path)[1].lower()

                if scan_ghosts and ext in GHOSTY_EXTENSIONS:
                    results["ghosts"].append((path, size, age))
                
                if scan_large and size > large_threshold:
                    results["large"].append((path, size))
                
                if scan_old and age > old_threshold:
                    results["old"].append((path, age))
                
                if scan_duplicates:
                    file_hash = hash_file(path, algorithm=hash_algo)
                    if file_hash in hashes:
                        results["duplicates"].setdefault(file_hash, []).append(path)
                    else:
                        hashes[file_hash] = path
            except Exception:
                continue

    return results
