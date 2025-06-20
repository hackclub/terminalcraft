import os
import json
from utils.file_utils import slugify, load_node

DATA_PATH = "data/nodes"

def link_nodes(source, target):
    # basic validation
    if not source or not target:
        print("Source and target are required.")
        return
    
    if source.lower() == target.lower():
        print("Cannot link a node to itself.")
        return
    
    src_slug = slugify(source)
    tgt_slug = slugify(target)

    src_path = os.path.join(DATA_PATH, f"{src_slug}.md")
    tgt_path = os.path.join(DATA_PATH, f"{tgt_slug}.md")

    # check both files exist
    if not os.path.exists(src_path):
        print(f"Source node '{source}' does not exist.")
        return
    
    if not os.path.exists(tgt_path):
        print(f"Target node '{target}' does not exist.")
        return

    try:
        data = load_node(src_path)
        if not data:
            print("Could not load source node data.")
            return
        
        # avoid duplicate links
        if tgt_slug in data.get('links', []):
            print(f"Link already exists: {source} -> {target}")
            return
        
        # add the link
        if 'links' not in data:
            data['links'] = []
        data['links'].append(tgt_slug)

        # write back to file
        with open(src_path, "w") as f:
            f.write(f"---\n{json.dumps(data, indent=2)}\n---\n\n# {data['title']}\n")

        print(f"Linked: {source} -> {target}")
        
    except Exception as e:
        print(f"Error linking nodes: {e}")
