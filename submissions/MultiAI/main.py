import os
import json
import requests

CONFIG_FILE = os.path.expanduser("~/.ai_cli_config.json")

# ---------------- API Key Manager ---------------- #
def load_api_keys():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_api_keys(keys):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(keys, f, indent=2)

def get_api_key(platform_name, display_name):
    keys = load_api_keys()
    if platform_name in keys:
        return keys[platform_name]
    print("\nYou can always grab you API key from https://groq.com/, For more details go through README.md file\n")
    key = input(f"🔐 Enter your {display_name} API key: ").strip()
    keys[platform_name] = key
    save_api_keys(keys)
    return key

# ---------------- Groq AI ---------------- #
def list_groq_models(api_key):
    url = "https://api.groq.com/openai/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        return res.json().get("data", [])
    except Exception as e:
        print(f"❌ Error fetching models: {e}")
        return []

def choose_model(models):
    print("\n🧠 Available Groq Models:\n")
    for i, model in enumerate(models, 1):
        print(f"{i}. {model['id']}")

    while True:
        choice = input("\n👉 Choose a model by number (or type /exit to quit): ").strip()

        if choice.lower() == "/exit":
            print("👋 Exiting. Goodbye!")
            return None
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(models):
            print("⚠️ Invalid choice. Please try again.")
            continue
        return models[int(choice) - 1]["id"]



def call_groq(api_key, model_id, prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        res = requests.post(url, headers=headers, json=data)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ API error: {e}"


def generate_image(prompt, replicate_api_key):
    url = "https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": f"Token {replicate_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "version": "db21e45bfa982e1351bcd7fc5cdb9b15f2d6eabf05cc406a9db51613b6e0ae99",  # SDXL 1.0
        "input": {"prompt": prompt}
    }

# ---------------- CLI Main ---------------- #
def main():
    groq_api_key = get_api_key("groq", "Groq")

    print("\n💬 Groq AI CLI")
    print("Type /image to generate an image.")
    print("Type /change to switch models.")
    print("Type /exit to quit.\n")
    print("NOTE : SOME OF THE AI MODELS WON'T WORK DUE TO BACKEND ISSUES. YOU CAN ALWAYS CHOOSE ANOTHER MODEL AND TRY !!!\n")

    models = list_groq_models(groq_api_key)
    if not models:
        print("❌ No models found.")
        return

    model_id = choose_model(models)
    if not model_id:
        return
    print(f"\n✅ Using model: {model_id}\n")

    # Chat loop
    while True:
        prompt = input("> ").strip()

        if prompt == "":
            continue
        elif prompt == "/exit":
            print("👋 Exiting. Goodbye!")
            break
        elif prompt == "/change":
            model_id = choose_model(models)
            if model_id:
                print(f"\n✅ Switched to model: {model_id}\n")
            continue

        print("⏳ Thinking...\n")
        response = call_groq(groq_api_key, model_id, prompt)
        print(f"✅ Response:\n{response}\n---\n")



if __name__ == "__main__":
    main()