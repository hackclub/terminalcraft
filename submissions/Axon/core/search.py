import json
from core.node_manager import list_nodes
import dotenv
import os
from utils.file_utils import open_in_editor, app_path

dotenv.load_dotenv(os.path.join(app_path, '.env'))
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MAX_FOLLOW_UP = 20

def ai_follow_up(file_path, messages):
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except:
        return {"status": "not_found", "msg": "Could not read file"}

    messages.append({
        "role": "user",
        "content": f"Here is the note '{file_path}' content:\n\n{content}\n\nNow you can verify, follow up, or read another note if needed. The most important thing is to return strict JSON as defined in the system prompt."
    })

    try:
        response = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)['result']
    except:
        return {"status": "not_found", "msg": "AI response error"}

def handle_follow_ups(file_path, messages, depth=1):
    if depth > MAX_FOLLOW_UP:
        print("⚠️ Maximum follow-up depth reached.")
        return
    
    if not file_path:
        print("❌ No relevant note found even after reading.")
        return

    # retry logic for API failures
    result = None
    for attempt in range(3):  # limit retries
        try:
            result = ai_follow_up(file_path, messages)
            break
        except:
            if attempt < 2:
                print(f"⚠️ Retry {attempt + 1}/3...")
            else:
                print("⚠️ Max retries reached")

    if not result:
        print("Try again later...")
        return

    status = result.get('status', 'unknown')
    found = result.get('found_path', '')
    next_read = result.get('read_path', '')
    msg = result.get('msg', 'No message')

    print(msg)

    if status == 'found' and found:
        print("✅ Final note identified:", found.split('/')[-1])
        ask_to_open_note(found)
    elif status == 'read' and next_read:
        handle_follow_ups(next_read, messages, depth + 1)
    else:
        print("❌ No relevant note found even after reading.")

def ask_to_open_note(file_path):
    """Ask the user if they want to open the found note"""
    if not file_path or not os.path.exists(file_path):
        return
        
    response = input("📝 Do you want to open this note? (y/n): ").strip().lower()
    if response == 'y' or response == 'yes':
        print(f"Opening {file_path.split('/')[-1]}...")
        open_in_editor(file_path)
    else:
        print("Note not opened.")

def semantic_search(query):
    print(f"🔍 Searching for: '{query}'...")
    nodes = list_nodes()
    
    if not nodes:
        print("❌ No nodes found in knowledge base.")
        return

    messages = [
        {
            "role": "system",
            "content": (
                "You are a search agent operating inside a collection of notes. Your task is to locate the most relevant note based on the search query. "
                "If you are not sufficiently confident in a match (confidence_score < 0.7), do not return status: 'not_found'. "
                "Instead, respond with status: 'read' and include the path to the note you'd like to examine in 'read_path'. "
                "This allows you to read the note for improved accuracy. Always respond strictly in the following JSON format: "
                "{\"result\": {\"status\": \"found|not_found|read\", \"confidence_score\": float (0.0–1.0), "
                "\"found_path\": \"string or null\", \"read_path\": \"string or null\", \"msg\": \"Descriptive message\"}}. "
                "Do not return 'not_found' unless you're confident (confidence_score ≥ 0.7) that no relevant note exists."
            )
        },
        {
            "role": "user",
            "content": f"Notes: {nodes}, search query: {query}",
        }
    ]

    try:
        response = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        data = json.loads(response.choices[0].message.content)['result']
    except:
        print("❌ Search API error")
        return

    status = data.get('status', 'unknown')
    confidence = data.get('confidence_score', 0.0)
    found = data.get('found_path', '')
    next_read = data.get('read_path', '')
    msg = data.get('msg', 'No message')

    print(msg)

    if status == 'found' and found:
        print("✅ The note is:", found.split('/')[-1])
        ask_to_open_note(found)
    elif status == 'read':
        if not next_read:
            # retry with same query
            semantic_search(query)
            return
        handle_follow_ups(next_read, messages)
    else:
        print("❌ No relevant note found.")