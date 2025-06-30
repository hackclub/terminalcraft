import os
import json
import re
import subprocess

app_path = os.path.expanduser('~/Axon')

def slugify(title):
    return title.lower().replace(" ", "-")

def load_node(path):
    with open(path, "r") as f:
        content = f.read()
    match = re.search(r"---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    metadata = json.loads(match.group(1))
    return metadata

def open_in_editor(path):
    editor = os.getenv("EDITOR", "nano")
    subprocess.call([editor, path])