import json
import os

CONFIG_FILE = "config.json"

# Load categories from JSON file
def load_categories():
    if not os.path.exists(CONFIG_FILE):
        return {}

    with open(CONFIG_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

# Save categories to JSON file
def save_categories(categories):
    with open(CONFIG_FILE, "w") as file:
        json.dump(categories, file, indent=4)

# Modify or create categories
def modify_categories():
    categories = load_categories()

    category = input("\nEnter the category name to modify or create (e.g., Pictures): ").strip()
    extensions = input("Enter file extensions to add (comma-separated, e.g., .svg, .webp): ").strip()

    # Convert input to a proper list of extensions
    extensions_list = [ext.strip() for ext in extensions.split(",") if ext.strip()]

    # Update or create the category
    if category in categories:
        categories[category].extend(ext for ext in extensions_list if ext not in categories[category])
    else:
        categories[category] = extensions_list

    save_categories(categories)
    print(f"\n✅ Updated category '{category}' with extensions: {categories[category]}")
