import os
import json
from datetime import datetime

DIR = "journal"
os.makedirs(DIR, exist_ok=True)


def get(name):
    return os.path.join(DIR, f"{name}.json")

def create(name):
    path = get(name)
    if os.path.exists(path):
        return False
    with open(path, 'w') as f:
        json.dump([], f)
    return True

def add(name, entry):
    path = get(name)
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        data = json.load(f)
    data.append({
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Contnent" : entry
    }) 
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    return True

def show(name):
    path = get(name)
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        return json.load(f)