import json

def save(data, filename):
    """Save API response data to a JSON file"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"\nSaved to {filename}")