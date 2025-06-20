import os
import json
from utils.file_utils import load_node

DATA_PATH = "data/nodes"

def show_trail(name):
    slug = name.lower().replace(" ", "-")
    file_path = os.path.join(DATA_PATH, f"{slug}.md")

    if not os.path.exists(file_path):
        print("Node not found.")
        return

    data = load_node(file_path)
    print(f"🧭 Reasoning Trail for: {data['title']}")
    print(f"Created: {data['created']}")
    if data["links"]:
        print("Links:")
        for link in data["links"]:
            print(f"  → {link}")
    else:
        print("No links from this node.")
