import json
from core.node_manager import list_nodes, format_nodes_metadata
from utils.file_utils import app_path
import dotenv
import os

dotenv.load_dotenv(os.path.join(app_path, '.env'))
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MAX_FOLLOW_UP = 20

def select_relevant_notes(query, metadata):
    messages = [
        {
            "role": "system",
            "content": (
                "You are helping select relevant notes for a user's query. "
                "Look at the note titles, creation dates, and links to determine which notes might be relevant. "
                "Respond with a JSON object containing a 'selected_indices' field with an array of note indices (numbers) that are most relevant to the query. "
                "Select only the most relevant notes - don't select everything. If no notes seem relevant, return an empty array."
            )
        },
        {
            "role": "user",
            "content": f"Query: {query}\n\nAvailable Notes (metadata only):\n{metadata}\n\nWhich note indices are most relevant to this query?",
        }
    ]

    response = client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"}
    )

    try:
        data = json.loads(response.choices[0].message.content)
        return data.get('selected_indices', [])
    except:
        # fallback if parsing fails
        return []

def load_node_content(file_path):
    try:
        with open(file_path, 'r') as f:
            text = f.read()
            # extract content after frontmatter
            parts = text.split('---', 2)
            return parts[2].strip() if len(parts) >= 3 else text
    except:
        return "Content unavailable"

def format_selected_nodes_content(nodes, indices):
    if not indices:
        return ""
    
    content = ""
    for idx in indices:
        if 0 <= idx < len(nodes):  # bounds check
            node = nodes[idx]
            name = node.get('title', 'Untitled')
            file_path = node.get('path', '')
            
            text = load_node_content(file_path)
            content += f"Node: {name}\nContent: {text}\n\n"
    
    return content

def generate_answer(query, content):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI assistant helping with a personal knowledge management system. "
                "Answer the user's question based only on the provided relevant notes. "
                "If the provided notes don't contain enough information to answer the question, say so clearly. "
                "Always respond with a JSON object containing a 'result' field with your answer."
            )
        },
        {
            "role": "user",
            "content": f"Query: {query}\n\nRelevant Notes:\n{content}" if content else f"Query: {query}\n\nNo relevant notes were found in your knowledge base.",
        }
    ]
    
    response = client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"}
    )

    try:
        data = json.loads(response.choices[0].message.content)
        return data.get('result', 'No response generated')
    except:
        return "Error parsing AI response"

def ask(query):
    try:
        nodes = list_nodes()
        if not nodes:
            return "No nodes found in knowledge base."
        
        metadata = format_nodes_metadata(nodes)
        indices = select_relevant_notes(query, metadata)
        content = format_selected_nodes_content(nodes, indices)
        return generate_answer(query, content)
    except Exception as e:
        # basic error handling
        return f"Error processing query: {str(e)}"