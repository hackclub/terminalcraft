import json
import os

FILENAME = "marketplace.json"

# Load listings from file
def load_data():
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as f:
            return json.load(f)
    return []

# Save listings to file
def save_data(data):
    with open(FILENAME, "w") as f:
        json.dump(data, f, indent=2)

# Display all listings
def show_listings(data):
    print("\n📦 Current Listings:")
    if not data:
        print("No listings yet.\n")
        return
    for idx, item in enumerate(data, 1):
        print(f"{idx}. [{item['category']}] {item['title']} - {item['price']}\n   {item['desc']} (Posted by: {item['name']})")
    print()

# Post a new listing
def post_listing(data):
    print("\n📝 Post New Listing")
    name = input("Your name: ")
    title = input("Title of item/service: ")
    category = input("Category (Item, Service, Request): ")
    price = input("Price ($ or 'Free'): ")
    desc = input("Short description: ")

    new_item = {
        "name": name,
        "title": title,
        "category": category,
        "price": price,
        "desc": desc
    }

    data.append(new_item)
    save_data(data)
    print("✅ Listing added!\n")

# Delete a listing
def delete_listing(data):
    show_listings(data)
    try:
        idx = int(input("Enter the listing number to delete: ")) - 1
        if 0 <= idx < len(data):
            del data[idx]
            save_data(data)
            print("🗑️ Listing deleted.\n")
        else:
            print("❌ Invalid number.\n")
    except ValueError:
        print("❌ Please enter a number.\n")

# Main menu
def main():
    data = load_data()
    while True:
        print("====== Campus CLI Marketplace ======")
        print("1. View Listings")
        print("2. Post a Listing")
        print("3. Delete a Listing")
        print("4. Exit")
        choice = input("Choose an option (1-4): ")

        if choice == "1":
            show_listings(data)
        elif choice == "2":
            post_listing(data)
        elif choice == "3":
            delete_listing(data)
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Try again.\n")

if __name__ == "__main__":
    main()
