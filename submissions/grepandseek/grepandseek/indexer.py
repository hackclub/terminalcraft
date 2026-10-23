import os
import json
import appdirs
import textract
import subprocess
import time
import re
import concurrent.futures
from pathlib import Path
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID, STORED

def normalize_path(path):
    """Normalize a path for consistent comparison"""
    return os.path.normcase(os.path.normpath(os.path.abspath(path)))

def extract_metadata(file_path):
    try:
        # Run ExifTool with the -j flag to output JSON
        result = subprocess.run(
            ["exiftool", "-j", file_path],
            capture_output=True,
            text=True,
            check=True
        )
        # ExifTool returns a JSON array, so we take the first item
        metadata = json.loads(result.stdout)
        if metadata:
            return metadata[0]
    except Exception as e:
        return {}
    return {}

class Indexer():
    def __init__(self, index_dir=None):
        if index_dir is None:
            # Get platform-appropriate data directory
            self.data_dir = appdirs.user_data_dir(appname="grepandseek", appauthor="alec-jensen")
            self.index_dir = os.path.join(self.data_dir, "index")
        else:
            self.index_dir = index_dir

        # Ensure directory exists
        Path(self.index_dir).mkdir(parents=True, exist_ok=True)

        self.schema = Schema(
            path=ID(stored=True, unique=True),
            filename=TEXT(stored=True),
            exif=TEXT(stored=True),
            content=TEXT(stored=True),
            last_updated=STORED
        )

        # Create or open index
        if not exists_in(self.index_dir):
            self.index = create_in(self.index_dir, self.schema)
        else:
            self.index = open_dir(self.index_dir)
            
        # Path to the config file
        self.config_path = os.path.join(self.data_dir, "config.json")
        
        # Initialize or load config
        self._init_config()

    def _init_config(self):
        """Initialize or load configuration file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
                # Ensure ignorepatterns exists in older config files
                if "ignorepatterns" not in self.config:
                    self.config["ignorepatterns"] = [r"^\.[^/\\]*"]  # Default: ignore dotfiles/folders
                    self._save_config()
        else:
            self.config = {
                "indexed_paths": [],
                "ignorepatterns": [r"^\.[^/\\]*"]  # Default: ignore dotfiles/folders
            }
            self._save_config()

    def _save_config(self):
        """Save configuration to disk"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def add_path(self, path):
        """Add a path to be indexed"""
        # Convert to absolute path
        abs_path = normalize_path(path)
        if abs_path not in self.config["indexed_paths"]:
            self.config["indexed_paths"].append(abs_path)
            self._save_config()
            return abs_path
        return None

    def remove_path(self, path):
        """Remove a path from indexing"""
        # Convert to absolute path
        abs_path = normalize_path(path)
        if abs_path in self.config["indexed_paths"]:
            self.config["indexed_paths"].remove(abs_path)
            self._save_config()
            return abs_path
        return None

    def get_indexed_paths(self):
        """Get list of paths being indexed"""
        return self.config["indexed_paths"]

    def add_ignore_pattern(self, pattern):
        """Add a regex pattern to ignore during indexing"""
        if pattern not in self.config["ignorepatterns"]:
            self.config["ignorepatterns"].append(pattern)
            self._save_config()
            return True
        return False

    def remove_ignore_pattern(self, pattern):
        """Remove a regex pattern from ignore list"""
        if pattern in self.config["ignorepatterns"]:
            self.config["ignorepatterns"].remove(pattern)
            self._save_config()
            return True
        return False

    def get_ignore_patterns(self):
        """Get list of ignore patterns"""
        return self.config["ignorepatterns"]

    def update_index(self, progress_callback=None, max_workers=None):
        """Update the index using multiple threads
        
        Args:
            progress_callback: Optional callable that takes (current_count, total_count, file_path)
            max_workers: Maximum number of worker threads (defaults to CPU count)
        """
        
        if not self.config["indexed_paths"]:
            return
        
        # Compile regex patterns for better performance
        ignore_patterns = [re.compile(pattern) for pattern in self.config["ignorepatterns"]]
        
        def should_ignore(path):
            """Check if path matches any ignore pattern"""
            basename = os.path.basename(path)
            for pattern in ignore_patterns:
                if pattern.search(basename):
                    return True
            return False
        
        # Collect all files to process
        files_to_process = []
        total_files = 0
        
        # Keep track of all valid file paths to check against index later
        valid_file_paths = set()
        
        for path in self.config["indexed_paths"]:
            if not os.path.exists(path):
                continue
            for root, dirs, files in os.walk(path):
                # Filter directories to skip based on ignore patterns
                dirs[:] = [d for d in dirs if not should_ignore(d)]
                
                # Collect files that don't match ignore patterns
                for file in files:
                    if not should_ignore(file):
                        file_path = os.path.join(root, file)
                        normalized_path = normalize_path(file_path)
                        files_to_process.append((root, file, normalized_path))
                        valid_file_paths.add(normalized_path)
                        total_files += 1
        
        if total_files == 0:
            return
        
        processed_files = 0
        indexed_files = 0
        
        # Function to process a single file in a worker thread
        def process_file(args):
            root, file, normalized_path = args
            file_path = os.path.join(root, file)
            filename = os.path.basename(file_path)
            
            try:
                # Get current file modification time
                current_mtime = os.path.getmtime(file_path)
                
                # Check if file exists in index and if it's been modified
                with self.index.searcher() as searcher:
                    doc = searcher.document(path=normalized_path)
                    if doc and 'last_updated' in doc and abs(doc['last_updated'] - current_mtime) < 0.001:
                        # File hasn't changed, no need to reindex (using small epsilon for float comparison)
                        return None
                
                # Convert EXIF data to string
                exif_data = extract_metadata(file_path)
                exif_str = json.dumps(exif_data)
                
                # Try to extract text content
                try:
                    content = textract.process(file_path).decode("utf-8")
                except Exception:
                    # check if file is encoded in any text format
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                    except Exception:
                        return None
                
                # Return the document data to be added to the index
                return {
                    "path": normalized_path,  # Store normalized path
                    "filename": filename,
                    "exif": exif_str,
                    "content": content,
                    "last_updated": current_mtime
                }
                
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                return None
        
        # Process files in parallel using a thread pool
        documents_to_add = []
        interrupted = False
        future_to_file = {}
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_file = {executor.submit(process_file, args): args for args in files_to_process}
                
                # Process results as they complete
                for future in concurrent.futures.as_completed(future_to_file):
                    root, file, normalized_path = future_to_file[future]
                    file_path = os.path.join(root, file)
                    
                    processed_files += 1
                    if progress_callback:
                        progress_callback(processed_files, total_files, file_path)
                        
                    try:
                        document = future.result(timeout=30)  # Add timeout to prevent hanging
                        if document:
                            documents_to_add.append(document)
                            indexed_files += 1
                    except concurrent.futures.TimeoutError:
                        print(f"Timeout processing {file_path}")
                    except Exception as e:
                        print(f"Exception processing {file_path}: {e}")
                        
        except KeyboardInterrupt:
            print("\nIndexing interrupted by user. Cancelling pending tasks...")
            interrupted = True
            for future in future_to_file:
                if not future.done():
                    future.cancel()
            print("Saving partial progress...")
        
        # Update the index with collected documents (even partial results)
        if documents_to_add:
            print(f"Saving {len(documents_to_add)} indexed documents to the index...")
            writer = self.index.writer()
            for doc in documents_to_add:
                writer.update_document(**doc)
            writer.commit()
            
        # Remove documents that should now be ignored based on updated patterns
        print("Checking for documents to remove...")
        to_delete = []
        
        reader = self.index.reader()

        if reader is None:
            return False
        
        for doc in reader.all_stored_fields():
            if 'path' in doc and doc['path'] not in valid_file_paths:
                to_delete.append(doc['path'])
        
        if to_delete:
            print(f"Removing {len(to_delete)} documents that now match ignore patterns...")
            writer = self.index.writer()
            for path in to_delete:
                writer.delete_by_term('path', path)
            writer.commit()
            
        # Only optimize if not interrupted, as it can be time-consuming
        if not interrupted:
            self.index.optimize()
                
        if interrupted:
            print("Indexing was interrupted. Partial progress has been saved.")
        else:
            print(f"Indexing complete. Processed {processed_files} files, indexed {indexed_files} files, removed {len(to_delete)} files.")

        return not interrupted  # Return success status

    def search(self, query_string, limit=10):
        """Search the index for the given query string"""
        from whoosh.qparser import QueryParser
        
        results = []
        with self.index.searcher() as searcher:
            query = QueryParser("content", self.index.schema).parse(query_string)
            
            search_results = searcher.search(query, limit=limit)
            
            for hit in search_results:
                results.append({
                    "path": hit["path"],
                    "content": hit.highlights("content"),
                    "score": hit.score
                })
        
        return results
