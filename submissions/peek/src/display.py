from rich import box
from rich.table import Table
from rich.syntax import Syntax
from rich.text import Text
from utilities import getLines, stripEmptyTrailingLines, stringChunk, getLanguageForFilename
from pathlib import Path


def syntaxHighlight(string, filename, show_line_numbers=False):
    language = getLanguageForFilename(filename)
    highlightedStr = Syntax(string, language, background_color="default", theme="solarized-dark", line_numbers=show_line_numbers)
    return highlightedStr

def makeFileLink(text, file_path: Path):
    absolutePath = str(file_path)
    link = Text(file_path.name)
    link.stylize(f"link file://{absolutePath}")
    return link

def printFilePreviewTable(files, console, file_max_lines=4, show_line_numbers=False, syntax_highlighting=True):
    table = Table(show_header=True, header_style="yellow", box=box.ROUNDED)
    separator = "[dim]" + "·" * 3 + "[/dim]\n"

    table.add_column("File")
    table.add_column("Preview")

    for file in files:
        filename = file["path"].name
        chunk_content = stringChunk(file["chunk"])

        file_preview = stripEmptyTrailingLines(getLines(chunk_content, file_max_lines))
        if (syntax_highlighting == True):
            file_preview = syntaxHighlight(file_preview, filename, show_line_numbers=show_line_numbers)

        table.add_row(makeFileLink(filename, file["path"]), file_preview)
        table.add_row("", separator)
    console.print(table)
