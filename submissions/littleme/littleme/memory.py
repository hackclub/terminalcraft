import json
from datetime import datetime

FILE = 'memory.json'

def load():
    try:
        with open(FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save(input, response):
    memory = load()
    memory.append({
        'input': input,
        'response': response,
        'timestamp': datetime.now().isoformat()
    })

    with open(FILE, 'w') as f:
        json.dump(memory, f, indent=2)

def mwipe():
    with open(FILE, 'w') as f:
        json.dump([], f, indent=2)