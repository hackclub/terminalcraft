import os
import argparse
import re
from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn
from rich.syntax import Syntax

from grepandseek.indexer import Indexer

def update_index_with_progress(indexer, console, description="Updating index"):
    """Update the index with a progress bar"""
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"[red]{description}...", total=100)
        
        def update_progress(current, total, file_path):
            percent_complete = int((current / total) * 100)
            filename = os.path.basename(file_path)
            progress.update(task, completed=percent_complete, 
                           description=f"[red]{description}... ({filename})")
        
        indexer.update_index(progress_callback=update_progress)

def main():
    parser = argparse.ArgumentParser(
        description='A search engine for your files'
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Search subcommand
    parser_search = subparsers.add_parser(
        "search", help="Perform a search."
    )
    parser_search.add_argument(
        "query", type=str, nargs="+", help="The search term(s)"
    )
    parser_search.add_argument(
        "-n", "--limit", type=int, default=10,
        help="Maximum number of results to display (default: 10)"
    )
    parser_search.add_argument(
        "-s", "--snippets", action="store_true",
        help="Show content snippets in results", default=True
    )

    # Indexer subcommand
    parser_indexer = subparsers.add_parser(
        "indexer", help="Commands related to the indexer."
    )
    indexer_subparsers = parser_indexer.add_subparsers(
        title="indexer commands", dest="indexer_command", required=True
    )
    # indexer init
    parser_init = indexer_subparsers.add_parser(
        "init", help="Initialize the index."
    )
    # indexer add
    parser_add = indexer_subparsers.add_parser(
        "add", help="Add a path to be indexed."
    )
    parser_add.add_argument("path", help="Path to be added to the index")
    # indexer remove
    parser_remove = indexer_subparsers.add_parser(
        "remove", help="Remove a path from the index."
    )
    parser_remove.add_argument("path", help="Path to be removed from the index")
    # indexer list
    parser_list = indexer_subparsers.add_parser(
        "list", help="List all indexing paths."
    )
    # indexer update-index
    parser_update = indexer_subparsers.add_parser(
        "update-index", help="Update the index."
    )
    parser_update.add_argument(
        "-s", "--silent", action="store_true",
        help="Silent mode, no progress bar", default=False
    )

    args = parser.parse_args()

    console = Console()

    indexer = Indexer()

    if args.command == "search":
        query = " ".join(args.query)
        results = indexer.search(query, limit=args.limit)
        
        console.print(f"[blue]Search results for '[bold]{query}[/bold]':[/blue]")
        if results:
            for i, result in enumerate(results, 1):
                # Convert file path to a valid file:// URL
                file_path = result['path']
                file_url = f"file://{os.path.abspath(file_path).replace(os.sep, '/')}"
                
                # Display the result with a clickable link
                console.print(f"[green]{i}. [link={file_url}]{file_path}[/link][/green] [grey](score: {result['score']:.2f})[/grey]")
                if args.snippets:
                    # Use regex to replace <b> tags with attributes
                    content = re.sub(r'<b(?:\s+[^>]*)?>', '[/dim]', result["content"])
                    content = content.replace('</b>', '[dim]')
                    content = " ... ".join([line for line in content.split("\n") if line.strip()])
                    console.print(f"   [dim]{content}[/dim]")
        else:
            console.print("[yellow]No results found.[/yellow]")
    elif args.command == "indexer":
        if args.indexer_command == "init":
            default_index_path = os.path.expanduser("~")
            inp = console.input(f"[blue]What path should be indexed?[/blue] (you can add more paths later) [{default_index_path}]: ")
            if inp:
                indexer.add_path(inp)
            else:
                indexer.add_path(default_index_path)
            console.print(f"[blue]Initializing index... (this may take a while)[/blue]")
            update_index_with_progress(indexer, console, "Initializing index")
            console.print(f"[green]Index initialized![/green]")
        elif args.indexer_command == "add":
            path = indexer.add_path(args.path)
            console.print(f"[green]Path '{path}' added to index![/green]")
        elif args.indexer_command == "remove":
            path = indexer.remove_path(args.path)
            console.print(f"[green]Path '{path}' removed from index![/green]")
        elif args.indexer_command == "list":
            indexed_paths = indexer.get_indexed_paths()
            if indexed_paths:
                console.print("[blue]Indexed paths:[/blue]")
                for path in indexed_paths:
                    console.print(f"  {path}")
            else:
                console.print("[yellow]No paths are being indexed.[/yellow]")
        elif args.indexer_command == "update-index":
            if args.silent:
                indexer.update_index()
            else:
                console.print("[blue]Updating index... (this may take a while)[/blue]")
                update_index_with_progress(indexer, console)
                console.print(f"[green]Index updated successfully![/green]")

if __name__ == "__main__":
    main()
