# Terminal Craft

A terminal based web browser made for a terminal craft Hack Club ysws! You can browse the internet using just text in your terminal! However if you get bored of using the terminal you can toggle on the regular browser. Also features a productivity mode with AI that forces you to stay productive :)

## Demo
You can watch a demo here [Demo Video](https://youtu.be/eSnp-2NApZI)

## Commands

- `help`: Print the list of commands.
- `exit`: Exits the program.
- `new`: Opens a new tab.
- `close`: Closes the current tab.
- `back`: Goes back one page.
- `forward`: Goes forward one page.
- `search <query>`: Searches for a query.
- `switch <tab_number>`: Switches to a specified tab.
- `tabs`: Print the number of tabs open.
- `up`: Moves up in the search results.
- `down`: Moves down in the search results.
- `next`: Moves to the next page of search results.
- `prev`: Moves to the previous page of search results.
- `open`: Opens the current search result.
- `head`: Toggles headless mode on and off.
- `prod`: Toggles productivity mode on and off.
- `refresh`: Refreshes the current page.
- `bookmark`: Saves the current URL to bookmarks.
- `bookmarks`: Print the list of bookmarks.
- `clearhistory`: Clears the browsing history.
- `goto <bookmark_number>`: Goes to a bookmarked URL.
- `rmbookmark <bookmark_number>`: Removes a bookmark.

## Dependencies

- `selenium`
- `webdriver_manager`
- `requests`
- `beautifulsoup4`
- `readability-lxml`
- `textwrap`
- `random`
- `re`

## Running it

Just rain the main.py file 💀 (but make sure you have all of the dependencies first). Or if you have a Mac just run the executable to run the program. If you are feeling extra cool (or just don't have a Mac) you can compile itself using the compile.py script, so long as you have the Pyinstaller library installed.