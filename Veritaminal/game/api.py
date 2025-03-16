"""
API module for Veritaminal

Handles interactions with the Google Gemini AI API for generating game content.
"""

import os
import logging
import random
import string
import json
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types
from typing import List, Dict, Optional, Any, TypedDict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("No API key found. Please set GEMINI_API_KEY in your .env file.")

client = genai.Client(api_key=api_key)

# Define Pydantic-like schemas for API responses
class TravelerDocument(TypedDict):
    name: str
    backstory: str
    additional_fields: Dict[str, Any]

class AIJudgment(TypedDict):
    decision: str
    confidence: float
    reasoning: str
    suspicious_elements: List[str]

# System instructions for different AI functionalities
SYSTEM_INSTRUCTIONS = {
    "document_generation": """
    You are a document generation system for a border control game.
    Generate ONLY structured JSON data with the following fields:
    - name: Full name (first and last) with no prefix or label
    - backstory: Brief one-sentence backstory that mentions the name
    - additional_fields: Any relevant fields as key-value pairs
    
    DO NOT include labels like "Name:" in your output. Return ONLY valid JSON.
    Generate unique names different from previously seen travelers.
    Keep content appropriate and non-political. Occasionally include subtle inconsistencies.
    """,
    
    "veritas_assistant": """
    You are Veritas, an AI assistant to a border control agent.
    Your role is to:
    - Provide subtle hints about document authenticity
    - Remain neutral but observant
    - Use clear, concise language
    - Occasionally express a slight personality
    
    Avoid directly telling the player the answer. Instead, guide their attention
    to potential issues or confirmations.
    """,
    
    "narrative_generation": """
    You are crafting a branching narrative for a border control simulation game.
    Create short, engaging story fragments that:
    - Respond to player decisions
    - Gradually build tension
    - Occasionally introduce moral dilemmas
    - Maintain consistent world-building
    
    Keep text concise (25-50 words) and focused on consequences of actions.
    """,
    
    "ai_judgment": """
    You are an expert document verification system evaluating border crossing documents.
    Consider:
    - Document completeness and accuracy
    - Consistency between name, permit, and backstory
    - Compliance with current border rules and regulations
    - Subtle discrepancies that might indicate fraud
    - Political and social context of the border situation
    - Previous patterns in approval/denial decisions

    Provide a fair and nuanced evaluation in VALID JSON format with these exact fields:
    - decision: either "approve" or "deny"
    - confidence: a float between 0.0 and 1.0
    - reasoning: a string explaining your decision
    - suspicious_elements: a list of strings, can be empty
    """
}

def generate_permit_number(valid=True):
    """
    Generate a permit number with controlled validity.
    
    Args:
        valid (bool): Whether to generate a valid permit number.
        
    Returns:
        str: A permit number (valid or invalid).
    """
    # Valid permit: 'P' followed by 4 digits
    if valid:
        digits = ''.join(random.choices(string.digits, k=4))
        return 'P' + digits
    else:
        # Different types of errors with equal probability
        error_type = random.choice(['wrong_prefix', 'wrong_length', 'non_digit'])
        
        if error_type == 'wrong_prefix':
            # Use a different letter prefix
            prefix = random.choice([c for c in string.ascii_uppercase if c != 'P'])
            digits = ''.join(random.choices(string.digits, k=4))
            return prefix + digits
        elif error_type == 'wrong_length':
            # Either too short or too long
            length = random.choice([3, 5])
            digits = ''.join(random.choices(string.digits, k=length))
            return 'P' + digits
        else:  # non_digit
            # Include a non-digit character
            digits = ''.join(random.choices(string.digits, k=3))
            special_char = random.choice(string.ascii_letters + string.punctuation)
            position = random.randint(0, 3)
            digits = digits[:position] + special_char + digits[position:]
            return 'P' + digits[:4]

def generate_text(prompt, system_type="document_generation", max_tokens=200):
    """
    Generate text using the Google Gemini AI API.
    
    Args:
        prompt (str): The prompt to send to the API.
        system_type (str): Type of system instruction to use.
        max_tokens (int): Maximum number of tokens to generate.
        
    Returns:
        str: Generated text.
    """
    try:
        # Select the appropriate system instruction
        system_instruction = SYSTEM_INSTRUCTIONS.get(system_type, SYSTEM_INSTRUCTIONS["document_generation"])

        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=0.9,
                system_instruction=system_instruction
            )
        )
        
        return response.text
            
    except Exception as e:
        logger.error("Error generating text: %s", str(e))
        return "Error generating text"

def generate_clean_name(used_names_context=""):
    """
    Generate a clean name without any prefixes or extra text.
    
    Args:
        used_names_context (str): Context about previously used names.
        
    Returns:
        str: A clean name.
    """
    prompt = f"""
    {used_names_context}
    
    Generate a unique full name (first and last) for a traveler.
    Return ONLY the name with no additional text, labels, or formatting.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=50,
                temperature=0.9,
                system_instruction="Return ONLY a name with first and last name. No additional text or explanation."
            )
        )
        
        name = response.text.strip()
        
        # Remove any common prefixes or formatting that might appear
        name = re.sub(r'^(Name:|Full name:|Traveler:|Traveler name:)\s*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'["*_]', '', name)  # Remove quotes, asterisks, underscores
        
        return name
    except Exception as e:
        logger.error(f"Error generating clean name: {e}")
        # Return a random fallback name
        first_names = ["Alex", "Sam", "Jordan", "Morgan", "Casey", "Taylor"]
        last_names = ["Smith", "Jones", "Garcia", "Chen", "Patel", "Müller"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_document_for_setting(setting, used_names_context="", system_type="document_generation", max_tokens=200):
    """
    Generate a document tailored to a specific border setting.
    
    Args:
        setting (dict): The border setting to generate a document for.
        used_names_context (str): Context about previously used names to avoid repetition.
        
    Returns:
        tuple: (name, permit, backstory, additional_fields)
    """
    # Decide whether this document should be valid or invalid
    should_be_valid = random.random() < 0.7  # 70% chance of valid document
    
    context = f"""
    Border Setting: {setting['name']}
    Situation: {setting['situation']}
    
    {used_names_context}
    
    Generate a traveler document for someone crossing this border.
    Return ONLY a valid JSON object with these fields:
    - name: A full name (first and last) different from previously seen travelers
    - backstory: A one-sentence backstory that mentions the name
    - additional_fields: Any relevant border-specific information
    
    DO NOT include labels like "Name:" in your output.
    Return ONLY the JSON object with no additional text.
    """
    
    try:
        # Generate document content with explicit schema enforcement
        system_instruction = SYSTEM_INSTRUCTIONS.get(system_type, SYSTEM_INSTRUCTIONS["document_generation"])
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=context,
            config=types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=0.9,
                system_instruction=system_instruction,
                response_mime_type="application/json"
            )
        )
        
        # Generate permit number using Python, not AI
        permit = generate_permit_number(valid=should_be_valid)
        
        # Parse the response as JSON
        response_text = response.text.strip()
        name = None
        backstory = None
        additional_fields = {}
        
        try:
            # Clean the response text to ensure it's valid JSON
            # Remove any non-JSON content
            json_match = re.search(r'({.*})', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                json_text = response_text
                
            # Parse JSON
            json_data = json.loads(json_text)
            
            # Extract fields, ensuring we get clean values
            if "name" in json_data and isinstance(json_data["name"], str):
                # Remove any "Name:" prefix if it somehow got included
                name = json_data["name"].strip()
                if name.lower().startswith("name:"):
                    name = name[5:].strip()
                    
            if "backstory" in json_data and isinstance(json_data["backstory"], str):
                backstory = json_data["backstory"].strip()
                
            if "additional_fields" in json_data and isinstance(json_data["additional_fields"], dict):
                additional_fields = json_data["additional_fields"]
            
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON response: %s", response_text)
        
        # Fallback values if parsing fails
        if not name:
            name = generate_clean_name(used_names_context)
        
        if not backstory:
            backstory = generate_consistent_backstory(name, "document_generation")
                
        return name, permit, backstory, additional_fields
        
    except Exception as e:
        logger.error(f"Error generating document for setting: {e}")
        # Return fallback values
        name = generate_clean_name(used_names_context)
        permit = generate_permit_number(valid=should_be_valid)
        backstory = generate_consistent_backstory(name, "document_generation")
        return name, permit, backstory, {}

def generate_consistent_backstory(name, system_type="document_generation", max_tokens=100):
    """
    Generate a backstory that is consistent with the provided name.
    
    Args:
        name (str): The traveler's name to use in the backstory.
        
    Returns:
        str: A one-sentence backstory that uses the same name.
    """
    system_instruction = SYSTEM_INSTRUCTIONS.get(system_type, SYSTEM_INSTRUCTIONS["document_generation"])
    prompt = f"Create a one-sentence backstory for a traveler named {name}. Make sure to use the exact name '{name}' in the backstory."
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=0.9,
                system_instruction=system_instruction
            )
        )
        
        return response.text.strip()
    except Exception as e:
        logger.error("Error generating backstory: %s", str(e))
        return f"{name} is a traveler with no additional information available."

def get_veritas_hint(doc, memory_context="", system_type="veritas_assistant", max_tokens=100):
    """
    Get a hint from Veritas about the document.
    
    Args:
        doc (dict): The document to analyze.
        memory_context (str): Context from the memory manager.
        
    Returns:
        str: A hint from Veritas.
    """
    system_instruction = SYSTEM_INSTRUCTIONS.get(system_type, SYSTEM_INSTRUCTIONS["veritas_assistant"])
    
    prompt = f"""
    {memory_context}
    
    Analyze this traveler:
    Name: {doc['name']}
    Permit: {doc['permit']}
    Backstory: {doc['backstory']}
    
    Provide a subtle hint about document authenticity without directly revealing if it's valid or not.
    Consider the border setting and recent history in your response.
    """
    
    response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=0.9,
                system_instruction=system_instruction
            )
        )
        
    return response.text.strip()
    
def generate_document_error():
    """
    Generate a random error to introduce into a document.
    
    Returns:
        str: Error description text
    """
    prompt = "Generate a realistic error that might appear in travel documentation. Format as: error_type: brief description"

    response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=1000,
                temperature=0.9
            )
        )
    
    return response.text

def ai_judge_document(doc, setting_context, memory_context, system_type="ai_judgment", max_tokens=300):
    """
    Use AI to judge if a document should be approved or denied.
    
    Args:
        doc (dict): The document to judge.
        setting_context (str): Context about the border setting.
        memory_context (str): Context about game history.
        
    Returns:
        dict: Judgment results including:
            - decision: "approve" or "deny"
            - confidence: float between 0-1
            - reasoning: explanation of the decision
            - suspicious_elements: list of suspicious elements if any
    """
    system_instruction = SYSTEM_INSTRUCTIONS.get(system_type, SYSTEM_INSTRUCTIONS["ai_judgment"])
    
    # Check if permit follows the required format: P followed by 4 digits
    permit_valid = len(doc['permit']) == 5 and doc['permit'][0] == 'P' and doc['permit'][1:].isdigit()
    
    # For more balanced gameplay, if the permit is invalid, we'll use our own judgment
    # rather than asking the AI
    if not permit_valid:
        return {
            "decision": "deny",
            "confidence": 0.9,
            "reasoning": f"The permit number {doc['permit']} does not follow the required format of 'P' followed by 4 digits.",
            "suspicious_elements": [f"Invalid permit format: {doc['permit']}"]
        }
    
    # Continue with AI judgment for more complex cases where the permit is valid
    # but there might be other issues
    
    # Build a rich context for the AI to make an informed decision
    prompt = f"""
    {setting_context}
    
    {memory_context}
    
    DOCUMENT TO EVALUATE:
    Name: {doc['name']}
    Permit: {doc['permit']}
    Backstory: {doc['backstory']}
    
    Evaluate this document based on the border rules and situation.
    Determine if this traveler should be approved or denied entry.
    
    Return a valid JSON object with exactly these fields:
    - decision: "approve" or "deny"
    - confidence: a number between 0.0 and 1.0
    - reasoning: a string explaining your decision
    - suspicious_elements: a list of strings (or empty list)
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=max_tokens,
                temperature=0.7,  # Lower temperature for more consistent judgments
                system_instruction=system_instruction,
                response_mime_type="application/json"
            )
        )
        
        # Parse the JSON response
        response_text = response.text.strip()
        
        try:
            # Clean the response text to ensure it's valid JSON
            json_match = re.search(r'({.*})', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                json_text = response_text
                
            judgment = json.loads(json_text)
            
            # Ensure required fields are present
            required_fields = ["decision", "confidence", "reasoning", "suspicious_elements"]
            for field in required_fields:
                if field not in judgment:
                    judgment[field] = "missing" if field != "confidence" else 0.5
                    
            # Override with a balanced probability to ensure fair gameplay
            if random.random() < 0.3:  # 30% chance to flip the decision
                original_decision = judgment["decision"]
                judgment["decision"] = "deny" if original_decision == "approve" else "approve"
                judgment["confidence"] = max(0.1, min(0.7, judgment["confidence"]))  # Lower confidence when flipping
            
            return judgment
        except json.JSONDecodeError:
            logger.error("Failed to parse AI judgment as JSON: %s", response_text)
        
        # Fallback with balanced probability
        return {
            "decision": "approve" if random.random() > 0.4 else "deny",  # 60% approve / 40% deny
            "confidence": random.uniform(0.5, 0.8),
            "reasoning": "Based on standard document verification procedures.",
            "suspicious_elements": []
        }
            
    except Exception as e:
        logger.error(f"Error in AI judgment: {e}")
        # Fallback response with balanced probability
        return {
            "decision": "approve" if random.random() > 0.4 else "deny",
            "confidence": random.uniform(0.5, 0.8),
            "reasoning": "Error occurred during judgment. Standard verification applied.",
            "suspicious_elements": []
        }

def generate_narrative_update(current_state, decision, is_correct, memory_context=""):
    """
    Generate a narrative update based on player decisions.
    
    Args:
        current_state (dict): The current story state.
        decision (str): The player's decision (approve/deny).
        is_correct (bool): Whether the decision was correct.
        memory_context (str): Context from the memory manager.
        
    Returns:
        str: A narrative update.
    """
    corruption = current_state.get("corruption", 0)
    trust = current_state.get("trust", 0)
    
    prompt = f"""
    {memory_context}
    
    Player decision: {decision}
    Decision correctness: {'correct' if is_correct else 'incorrect'}
    Current corruption level: {corruption}
    Current trust level: {trust}
    
    Generate a brief narrative update (1-2 sentences) describing the consequences of this decision.
    Consider the border setting and game history in your response.
    """

    system_instruction = SYSTEM_INSTRUCTIONS.get("narrative_generation", SYSTEM_INSTRUCTIONS["narrative_generation"])

    response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=2000,
                temperature=0.9,
                system_instruction=system_instruction
            )
        )
        
    
    return response.text.strip()
