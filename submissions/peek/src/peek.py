import typer
from pathlib import Path
from rich.console import Console

import config
from errorHandling import closeWithError
from fileActions import fetchMatchingFiles, listTextFiles
from display import printFilePreviewTable


console = Console()
app = typer.Typer()
debugMode = False

@app.command()
def peek(
        query: str = typer.Argument("", help="A file name to look for."), 
        directory: str = typer.Option(".", "-d", "--directory", help="A directory to look for files in."), 
        sorting: str = typer.Option("recency", "-s", "--sorting", help="A property by which to sort files: 'recency'/'size'/'alphabetic'."),
        pattern: str = typer.Option("*", "-p", "--pattern", help="A glob-style pattern to filter files by."),
        verbose: bool = typer.Option(False, "-v", "--verbose", help="Print more lines per file."),
        high_accuracy: bool = typer.Option(True, "-ha/-la", "--high-accuracy/--low-accuracy", help="Prioritize accuracy in search and file detection."),
        highlighting: bool = typer.Option(True, "-hi/-nhi", "--highlighting/--no-highlighting", help="Use syntax highlighting."),
        line_numbers: bool = typer.Option(False, "-ln/-nln", "--linenumbers/--no-linenumbers", help="Display line numbers in preview."),
        debug_flag: bool = typer.Option(False, "-db", "--debug", help="Enable debugging mode.")
    ):
    config.debugMode = debug_flag

    workingDir = Path(directory).resolve()
    if not workingDir.exists():
        closeWithError(f"It seems the directory '{directory}' does not exist.", 1)
        return
    if not workingDir.is_dir():
        closeWithError(f"The path '{directory}' is not a directory.")
        return
    
    if high_accuracy == True:
        accuracy = 'high'
    else:
        accuracy = 'low'

    try:
        filesInDir = listTextFiles(workingDir, pattern=pattern, sorting=sorting)
        matchingFiles = fetchMatchingFiles(filesInDir, query=query, binary_filter_accuracy=accuracy)
    except Exception as e:
        closeWithError()
        return
    

    if verbose == True:
        file_max_lines = 50
    else:
        file_max_lines = 5

    printFilePreviewTable(matchingFiles, console, file_max_lines=file_max_lines, syntax_highlighting=highlighting, show_line_numbers=line_numbers)

if __name__ == "__main__":
    app()
