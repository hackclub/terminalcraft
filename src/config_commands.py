import typer
from config import set_config

def setup():
    """Interactively set up API endpoint, API key, and AI model."""
    endpoint = typer.prompt("Enter your AI API endpoint")
    api_key = typer.prompt("Enter your AI API key", hide_input=True)
    model = typer.prompt("Enter your AI model")
    set_config("AI_API_ENDPOINT", endpoint)
    set_config("AI_API_KEY", api_key)
    set_config("AI_MODEL", model)
    print("Setup complete. You can change these values anytime with the config-set command.")

def set_api_endpoint(endpoint: str = typer.Argument(..., help="Your AI API endpoint")):
    """Set the AI API endpoint."""
    set_config("AI_API_ENDPOINT", endpoint)
    print("AI API endpoint updated.")

def set_api_key(api_key: str = typer.Argument(..., help="Your AI API key")):
    """Set the AI API key."""
    set_config("AI_API_KEY", api_key)
    print("AI API key updated.")

def set_ai_model(model: str = typer.Argument(..., help="Your AI model")):
    """Set the AI model."""
    set_config("AI_MODEL", model)
    print("AI model updated.")