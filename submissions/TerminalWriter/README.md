# TerminalWriter

TerminalWriter is a self-contained, terminal-only Python application for authoring, managing, and exporting digital books. It provides a dedicated writing environment within your terminal, entirely independent from external APIs or programs.

## Features

- Create, edit, and export digital books entirely from your terminal
- Support for Markdown formatting (bold, italic, headings, etc.)
- Image reference support for export formats
- Multiple export formats:
  - PDF
  - ePub
  - Plain Text
- Customize book appearance:
  - Font family
  - Font size
  - Book dimensions
- Cross-platform compatibility (Windows and Linux)

## Installation

### Prerequisites

- Python 3.6 or later

### Windows (PowerShell)

Run this command in PowerShell to install TerminalWriter:

```powershell
mkdir -Force "$env:USERPROFILE\terminalwriter" | Out-Null; Invoke-WebRequest -Uri "https://raw.githubusercontent.com/foglomon/terminalwriter/main/terminalwriter.py" -OutFile "$env:USERPROFILE\terminalwriter\terminalwriter.py"; pip install colorama markdown reportlab ebooklib beautifulsoup4 Pillow pyautogui; Set-Content -Path "$env:USERPROFILE\terminalwriter.bat" -Value "@echo off`r`npython `"$env:USERPROFILE\terminalwriter\terminalwriter.py`" %*"; Set-Content -Path "$env:USERPROFILE\tw.bat" -Value "@echo off`r`npython `"$env:USERPROFILE\terminalwriter\terminalwriter.py`" %*"; $env:PATH += ";$env:USERPROFILE"; [Environment]::SetEnvironmentVariable("PATH", "$($env:PATH)", "User"); Write-Output "TerminalWriter installed! Run 'terminalwriter' or 'tw' from any terminal."
```

### Linux (Bash)

Run this command in a terminal to install TerminalWriter:

```bash
mkdir -p ~/terminalwriter && curl -s https://raw.githubusercontent.com/foglomon/terminalwriter/main/terminalwriter.py -o ~/terminalwriter/terminalwriter.py && pip install colorama markdown reportlab ebooklib beautifulsoup4 Pillow pyautogui && echo -e '#!/bin/bash\npython ~/terminalwriter/terminalwriter.py "$@"' > ~/terminalwriter.sh && chmod +x ~/terminalwriter.sh && sudo ln -sf ~/terminalwriter.sh /usr/local/bin/terminalwriter && sudo ln -sf ~/terminalwriter.sh /usr/local/bin/tw && echo "TerminalWriter installed! Run 'terminalwriter' or 'tw' from any terminal."
```

## Usage

### Running TerminalWriter

After installation, you can start TerminalWriter by typing either of these commands in any terminal:

```
terminalwriter
```

or the shorter version:

```
tw
```

### Main Menu

When you start TerminalWriter, you will see a main menu with the following options:

1. Create New Book
2. Edit Existing Book
3. Export Book
4. Exit

### Creating a New Book

Select "Create New Book" from the main menu and provide:

- Book title
- Author name
- Book description

You will then enter the writing interface.

### Writing Interface

In the writing interface, you can:

- Type text directly, with support for Markdown formatting
- Use special commands, which are organized into the following categories:

#### Line Editing Commands
- `edit <number>` - Edit a specific line by its line number.
- `new line` - Insert a blank line at the end of your text.
- `add line <number>` - Insert a blank line before the specified line number.
- `delete line <number>` - Delete the specified line and shift remaining lines up.

#### Navigation Commands
- `new page` - Create a new page and navigate to it.
- `previous page` - Go to the previous page.
- `next page` - Go to the next page.
- `go to page = <num>` - Jump to a specific page number.

#### Formatting Commands
- `update font = <name>` - Change the font (e.g., `update font = Times-Roman`).
- `update font-size = <size>` - Change the font size (e.g., `update font-size = 12`).
- `update book-dimensions = <wxh>` - Change book dimensions (e.g., `update book-dimensions = 6x9`).

#### Content Editing Commands
- `clear page` - Clear all content from the current page.
- `search = <text>` - Search for text across all pages.

#### Book Management Commands
- `save` - Explicitly save the book.
- `rename book` - Change the title of the book.
- `update description` - Change the book description.
- `characters` - Manage characters in your book, including a built-in character name generator

#### System Commands
- `help` - Show the help screen.
- `status` - Show book statistics and information.
- `exit` - Return to the main menu.

### Markdown Support

You can use standard Markdown syntax:

- Bold: `*bold text*` or `**bold text**`
- Italic: `_italic text_`
- Headings: `# Heading 1`, `## Heading 2`, `### Heading 3`
- Images: `![alt text](file:///path/to/image.jpg)`
- Links: `[link text](https://example.com)`
- Inline font size: `!font-size(24)[text]`
- Character names: `<character>` (replaced with the character's name)

## Exporting Books

Select "Export Book" from the main menu, choose the book to export, and select your desired format:

1. PDF
2. ePub
3. Plain Text

The exported file will be placed in a directory named "exports" within your book's directory.

## Author

Created by Ishman Singh alias foglomon as an open-source tool for writers who prefer terminal-based workflows.
