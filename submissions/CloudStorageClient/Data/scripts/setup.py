import os
import webbrowser
import sys

setup_steps = [
    "Step 1: Open Google Cloud Console Dashboard.",
    "Step 2: Sign in with your Google account.",
    "Step 3: Create a new project using the button on the top right.",
    "Step 4: Open the navigation menu, go to 'API & Services' > 'Library'.",
    "Step 5: Search for 'YouTube Data API v3', click on it, and enable it.",
    "Step 6: Go back to 'API & Services' > 'Credentials'.",
    "Step 7: Create an OAuth 2.0 Client ID.",
    "Step 8: Fill in the required information and download the JSON credentials file."
]

def open_urls():
    print("Opening required URLs in your browser...")
    webbrowser.open("https://console.cloud.google.com/apis/dashboard")

def guide_user():
    print("Setup Guide")
    for step in setup_steps:
        input(f"{step}\nPress Enter to continue...")
    path = str(input("Enter the path of the downloaded JSON file: "))

    if not os.path.exists(path):
        print("Error: File not found.")
        sys.exit(0)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    client_secret_path = os.path.join(parent_dir, "client_secret.json")
    
    os.makedirs(os.path.dirname(client_secret_path), exist_ok=True)
    
    try:
        with open(path, "r") as source_file:
            content = source_file.read()
            
        with open(client_secret_path, "w") as target_file:
            target_file.write(content)
            
    except Exception as e:
        print(f"Error during setup: {str(e)}")
        sys.exit(1)
        
    print("Setup complete! You can now start using the application.")