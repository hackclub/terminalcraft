import os
import pathlib
from utils.file_utils import load_node, slugify, open_in_editor, app_path
from datetime import datetime
import json

DATA_PATH = f"{app_path}/data/nodes"

def create_node(title):
    if not title or not title.strip():
        print("Title cannot be empty")
        return
    
    # ensure directory exists
    os.makedirs(DATA_PATH, exist_ok=True)
    
    slug = slugify(title)
    file_path = os.path.join(DATA_PATH, f"{slug}.md")

    # check if already exists
    if os.path.exists(file_path):
        print(f"Node already exists: {file_path}")
        return

    # create metadata
    data = {
        "title": title,
        "created": datetime.now().isoformat(),
        "links": []
    }

    try:
        with open(file_path, "w") as f:
            f.write(f"---\n{json.dumps(data, indent=2)}\n---\n\n# {title}\n")
        
        print(f"Created node: {file_path}")
        
        # Open in editor first so user can add content
        open_in_editor(file_path)
        
        # After editing, assign domain using AI
        try:
            from core.heatmap import add_domain_to_new_note
            domain = add_domain_to_new_note(file_path)
            if domain:
                print(f"Assigned domain: {domain}")
        except ImportError:
            # Heatmap module not available, skip domain assignment
            pass
        except Exception as e:
            print(f"Error assigning domain: {e}")
            
    except Exception as e:
        print(f"Error creating node: {e}")

def list_nodes():
    if not os.path.exists(DATA_PATH):
        return []
    
    nodes = []
    try:
        for entry in pathlib.Path(DATA_PATH).iterdir():
            if entry.is_file() and entry.suffix == '.md':  # only markdown files
                node_data = load_node(str(entry))
                if node_data:  # only include valid nodes
                    nodes.append({'path': str(entry), **node_data})
    except Exception as e:
        print(f"Error listing nodes: {e}")
    
    return nodes

def format_nodes_metadata(nodes):
    if not nodes:
        return "No nodes available"
    
    output = ""
    for i, node in enumerate(nodes):
        name = node.get('title', 'Untitled')
        created = node.get('created', 'Unknown date')
        links = node.get('links', [])
        file_path = node.get('path', '')
        domain = node.get('domain', 'Uncategorized')
        
        output += f"Index: {i}\nTitle: {name}\nCreated: {created}\nDomain: {domain}\nLinks: {links}\nPath: {file_path}\n\n"
    
    return output