"""Help and tips for Terminal Bookmarks."""
from random import choice
from .styling import format_tip

TIPS = [
    "Use tags to organize related commands (e.g., 'git', 'docker')",
    "Search is case-insensitive and matches partial words",
    "Use 'tb run <id>' with the first few characters of the ID",
    "Add descriptions to remember what complex commands do",
    "Use --preview to see commands before running them",
    "Group related commands with consistent tag names",
    "Use 'tb list --detailed' to see full command details",
    "Bookmark commands with environment variables for flexibility"
]

COMMAND_HELP = {
    'add': "Add new bookmarks with: tb add -t 'title' -c 'command'",
    'list': "List all bookmarks with: tb list",
    'search': "Search bookmarks with: tb search <query>",
    'run': "Execute bookmarks with: tb run <id>",
    'delete': "Remove bookmarks with: tb delete <id>"
}

def show_random_tip():
    """Show a random usage tip."""
    format_tip(choice(TIPS))

def get_command_help(command: str) -> str:
    """Get help text for a specific command."""
    return COMMAND_HELP.get(command, "Use --help for command details") 