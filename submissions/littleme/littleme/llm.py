import google.generativeai as genai
from littleme.config import load

def ask(prompt):
    config = load()
    api_key = config.get("api_key")

    if not api_key:
        raise Exception("❌ API key not found in config.json")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    response = model.generate_content(prompt)
    return response.text.strip()
