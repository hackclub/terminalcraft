"""Help text and examples for Terminal Bookmarks CLI."""

MAIN_HELP = """
Terminal Bookmarks - Manage your terminal commands with ease

Usage:
  tb <command> [options]

Commands:
  add     Add a new bookmark
  list    List all bookmarks
  search  Search bookmarks
  run     Execute a bookmark
  export  Export bookmarks
  import  Import bookmarks
  help    Show this help

Run 'tb help <command>' for command-specific help.
"""

COMMAND_HELP = {
    "add": {
        "desc": "Add a new bookmark",
        "usage": "tb add <command> --title <title> [options]",
        "example": 'tb add "git status" --title "Check Git Status" --tags git',
        "options": [
            ("--title", "Bookmark title (required)"),
            ("--tags", "Comma-separated tags"),
            ("--desc", "Command description"),
            ("--require", "Required dependencies"),
        ]
    },
    'search': {
        'title': 'Search Command Help',
        'content': """
Search for bookmarks using various criteria:

Examples:
  tbm search "git"                    Simple text search
  tbm search -t "git,python"          Search by tags
  tbm search -i                       Interactive mode
  tbm search -f json                  JSON output

Options:
  -t, --tags TEXT         Include tags (comma-separated)
  -x, --exclude TEXT      Exclude tags (comma-separated)
  -d, --date [all|today|week|month]
                         Filter by date added
  -i, --interactive      Use interactive mode
  -f, --format [table|json|csv]
                         Output format
        """
    },
} 