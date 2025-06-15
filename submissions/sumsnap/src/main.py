import typer

from config import init_config
from config_commands import set_ai_model, set_api_endpoint, set_api_key, setup
from summary_command import summary

init_config()

app = typer.Typer()

app.command("summary")(summary)
app.command("setup")(setup)
app.command("set-api-endpoint")(set_api_endpoint)
app.command("set-api-key")(set_api_key)
app.command("set-ai-model")(set_ai_model)

@app.command()
def version():
    """Display the current version of the sumsnap CLI tool."""
    print("sumsnap v0.0.1")
    
#--------------------------------------

if __name__ == "__main__":
    app()