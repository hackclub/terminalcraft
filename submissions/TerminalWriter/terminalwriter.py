#!/usr/bin/env python3
"""
TerminalWriter - A terminal-based book writing application
"""
import os
import json
import sys
import time
import re
import threading
from colorama import init, Fore, Back, Style
import markdown
import pyautogui
from bs4 import BeautifulSoup
import names

# Initialize colorama for colored terminal output
init()

# Global variables
# Using the Documents folder in user profile for storing books and configurations
USER_HOME = os.path.expanduser("~")
DOCUMENTS_DIR = os.path.join(USER_HOME, "Documents")
APP_DIR = os.path.join(DOCUMENTS_DIR, "TerminalWriter")
BOOKS_DIR = os.path.join(APP_DIR, "books")
CONFIG_FILE = os.path.join(APP_DIR, "config.json")

# Default book settings
DEFAULT_SETTINGS = {
    "font": "Times-Roman",
    "font-size": 12,
    "book-dimensions": "6x9"  # width x height in inches
}


def clear_screen():
    """Clear the terminal screen based on OS"""
    os.system('cls' if os.name == 'nt' else 'clear')


def load_config():
    """Load application configuration"""
    if not os.path.exists(CONFIG_FILE):
        config = {"books": [], "default_export_format": "pdf"}
        save_config(config)
        return config
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"{Fore.RED}Error loading configuration: {e}{Style.RESET_ALL}")
        return {"books": [], "default_export_format": "pdf"}


def save_config(config):
    """Save application configuration"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"{Fore.RED}Error saving configuration: {e}{Style.RESET_ALL}")


def ensure_books_directory():
    """Ensure the application directories exist"""
    # Create the app directory and books directory if they don't exist
    if not os.path.exists(APP_DIR):
        os.makedirs(APP_DIR, exist_ok=True)
    
    if not os.path.exists(BOOKS_DIR):
        os.makedirs(BOOKS_DIR, exist_ok=True)


def create_book():
    """Create a new book"""
    clear_screen()
    print(f"{Fore.GREEN}=== Create New Book ==={Style.RESET_ALL}")
    
    title = input(f"{Fore.CYAN}Enter book title: {Style.RESET_ALL}")
    author = input(f"{Fore.CYAN}Enter author name: {Style.RESET_ALL}")
    description = input(f"{Fore.CYAN}Enter book description: {Style.RESET_ALL}")
    
    book_slug = re.sub(r'[^a-zA-Z0-9_]', '_', title.lower())
    book_dir = os.path.join(BOOKS_DIR, book_slug)
    
    # Check if book already exists
    if os.path.exists(book_dir):
        print(f"{Fore.YELLOW}Warning: A book with a similar title already exists.{Style.RESET_ALL}")
        overwrite = input("Do you want to overwrite it? (yes/no): ").lower()
        if overwrite != "yes":
            print("Book creation canceled.")
            input("Press Enter to return to the main menu...")
            return
    
    # Create book directory
    os.makedirs(book_dir, exist_ok=True)
    
    # Create book metadata
    book_data = {
        "title": title,
        "author": author,
        "description": description,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "last_modified": time.strftime("%Y-%m-%d %H:%M:%S"),
        "pages": [{"content": ""}],  # Start with one empty page
        "current_page": 0,
        "settings": DEFAULT_SETTINGS.copy(),
        "characters": {}  # Dictionary to store character names and descriptions
    }
    
    # Save book metadata
    with open(os.path.join(book_dir, "book.json"), 'w') as f:
        json.dump(book_data, f, indent=2)
    
    # Update global configuration
    config = load_config()
    if book_slug not in [book["slug"] for book in config["books"]]:
        config["books"].append({
            "title": title,
            "slug": book_slug,
            "path": book_dir
        })
        save_config(config)
    
    print(f"{Fore.GREEN}Book '{title}' created successfully!{Style.RESET_ALL}")
    time.sleep(1)
    
    # Enter writing interface for the new book
    writing_interface(book_slug)


def select_book():
    """Show list of books and let user select one"""
    config = load_config()
    
    if not config["books"]:
        print(f"{Fore.YELLOW}No books found. Please create a new book first.{Style.RESET_ALL}")
        input("Press Enter to return to the main menu...")
        return None
    
    clear_screen()
    print(f"{Fore.GREEN}=== Select a Book ==={Style.RESET_ALL}")
    
    for i, book in enumerate(config["books"], 1):
        print(f"{i}. {book['title']}")
    
    print(f"0. {Fore.YELLOW}Cancel{Style.RESET_ALL}")
    
    while True:
        try:
            choice = int(input(f"{Fore.CYAN}Enter your choice (0-{len(config['books'])}): {Style.RESET_ALL}"))
            if choice == 0:
                return None
            if 1 <= choice <= len(config["books"]):
                return config["books"][choice - 1]["slug"]
            print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Please enter a number.{Style.RESET_ALL}")


def load_book(book_slug):
    """Load book data from disk"""
    book_path = os.path.join(BOOKS_DIR, book_slug, "book.json")
    try:
        with open(book_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"{Fore.RED}Error loading book: {e}{Style.RESET_ALL}")
        return None


def save_book(book_slug, book_data):
    """Save book data to disk"""
    book_path = os.path.join(BOOKS_DIR, book_slug, "book.json")
    
    # Update last modified time
    book_data["last_modified"] = time.strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with open(book_path, 'w') as f:
            json.dump(book_data, f, indent=2)
        return True
    except Exception as e:
        print(f"{Fore.RED}Error saving book: {e}{Style.RESET_ALL}")
        return False


def writing_interface(book_slug):
    """Interface for writing and editing a book"""
    book_data = load_book(book_slug)
    if not book_data:
        return
    
    current_page = book_data["current_page"]
    # New variables for line editing functionality
    current_content_lines = []
    current_line_index = -1
    editing_mode = False
    was_edit_operation = False
    
    while True:
        clear_screen()
        
        # Display book info and current page
        print(f"{Fore.GREEN}=== {book_data['title']} ===")
        print(f"Page {current_page + 1} of {len(book_data['pages'])}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Font: {book_data['settings']['font']} | "
              f"Size: {book_data['settings']['font-size']} | "
              f"Dimensions: {book_data['settings']['book-dimensions']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Type 'help' for more information{Style.RESET_ALL}")

        print("-" * 50)
        
        # Split content into lines for better display and editing
        if not current_content_lines:
            if book_data["pages"][current_page]["content"]:
                current_content_lines = book_data["pages"][current_page]["content"].split('\n')
            else:
                current_content_lines = [""]
        
        # Display current page content
        if current_content_lines and any(line.strip() for line in current_content_lines):
            for i, line in enumerate(current_content_lines):
                # Start with line number display
                line_display = f"{i+1}: "
                
                # If in editing mode and this is the current line, add cyan color
                if editing_mode and i == current_line_index:
                    line_display = f"{Fore.CYAN}{line_display}"
                
                # Process different markdown elements with colors:
                # Process character tags first (replace <tag> with character name)
                processed_line = line
                if "characters" in book_data and book_data["characters"]:
                    processed_line = process_character_tags(processed_line, book_data["characters"])
                    
                # 1. Check for headings first (# Heading)
                if re.match(r'^#+\s+', processed_line):
                    heading_level = len(re.match(r'^#+', processed_line).group())
                    heading_text = re.sub(r'^#+\s+', '', processed_line)
                    
                    # All headings in blue with BRIGHT style
                    line_display += f"{Fore.BLUE + Style.BRIGHT}{heading_text}{Style.RESET_ALL}"
                    if editing_mode and i == current_line_index:
                        line_display += f"{Fore.CYAN}"
                else:
                    # Process bold (**text**), italic (*text*), and font-size tags
                    current_pos = 0
                    result_line = ""
                    
                    # Handle bold text with asterisks (*bold*)
                    bold_pattern = re.compile(r'\*([^*]+?)\*')
                    # Handle italic text with underscores (_italic_)
                    italic_pattern = re.compile(r'\_([^_]+?)\_')
                    # Handle font size tags
                    font_size_pattern = re.compile(r'!font-size\((\d+)\)\[(.*?)\]')
                        
                    # Process the line character by character to handle overlapping tags
                    while current_pos < len(processed_line):
                        # Check for bold
                        bold_match = bold_pattern.search(processed_line, current_pos)
                        # Check for italic
                        italic_match = italic_pattern.search(processed_line, current_pos)
                        # Check for font size
                        font_match = font_size_pattern.search(processed_line, current_pos)
                        
                        # Find the earliest match
                        matches = [m for m in [bold_match, italic_match, font_match] if m]
                        if not matches:
                            # No more matches, add the rest of the text
                            result_line += processed_line[current_pos:]
                            break
                            
                        earliest_match = min(matches, key=lambda m: m.start())
                        
                        # Add text before the match
                        result_line += processed_line[current_pos:earliest_match.start()]
                        
                        if earliest_match == bold_match:
                            # Display bold text with bold terminal style instead of color
                            bold_text = earliest_match.group(1)
                            result_line += f"{Style.BRIGHT}{bold_text}{Style.NORMAL}"
                            if editing_mode and i == current_line_index:
                                result_line += f"{Fore.CYAN}"
                            current_pos = earliest_match.end()
                        elif earliest_match == italic_match:
                            # Display italic text with dim style (closest to italic in terminal)
                            italic_text = earliest_match.group(1)
                            result_line += f"{Style.DIM}{italic_text}{Style.NORMAL}"
                            if editing_mode and i == current_line_index:
                                result_line += f"{Fore.CYAN}"
                            current_pos = earliest_match.end()
                        elif earliest_match == font_match:
                            # Handle font size
                            size = earliest_match.group(1)
                            text = earliest_match.group(2)
                            result_line += f"{Fore.MAGENTA}[size={size}]{text}{Fore.RESET}"
                            if editing_mode and i == current_line_index:
                                result_line += f"{Fore.CYAN}"
                            current_pos = earliest_match.end()
                    
                    line_display += result_line
                
                # Reset styling at end of line
                if editing_mode and i == current_line_index:
                    line_display += f"{Style.RESET_ALL}"
                
                print(line_display)
        else:
            print(f"{Fore.YELLOW}This page is empty. Type your content above.{Style.RESET_ALL}")
        
        print("-" * 50)
        
        # Reset the edit operation flag at the start of each loop
        was_edit_operation = False
        
        # Show appropriate prompt based on editing mode
        if editing_mode:
            prompt_text = f"{Fore.CYAN}Editing line {current_line_index + 1} > {Style.RESET_ALL}"
            # Pre-populate with current line content
            line_content = current_content_lines[current_line_index]
            
            # Define function to auto-type the text after a short delay
            def auto_type_text(text):
                time.sleep(0.5)  # Wait for input prompt to appear
                pyautogui.write(text)
            
            # Start typing in a separate thread
            typing_thread = threading.Thread(target=auto_type_text, args=(line_content,))
            typing_thread.daemon = True
            typing_thread.start()
            
            # Get user input
            user_input = input(prompt_text)
            
            # If user just presses enter (and nothing was auto-typed), keep the current line unchanged
            if user_input == "":
                user_input = line_content
                
            # Update the line being edited
            current_content_lines[current_line_index] = user_input
            editing_mode = False
            # Update the book content with modified lines
            book_data["pages"][current_page]["content"] = '\n'.join(current_content_lines)
            save_book(book_slug, book_data)
            
            # Mark that we just performed an edit operation
            was_edit_operation = True
        else:
            # Regular input mode
            user_input = input(f"{Fore.CYAN}> {Style.RESET_ALL}")
        
        # Process commands - but skip command processing if we just edited a line
        if was_edit_operation:
            continue
            
        if user_input.lower() == "exit":
            break
        elif user_input.lower() == "help":
            show_help()
            input("Press Enter to continue...")
        elif user_input.lower() == "status":
            show_status(book_data)
            input("Press Enter to continue...")
        elif user_input.lower() == "characters":
            book_data = manage_characters(book_slug, book_data)
            # Reset line editing state to reflect any changes
            current_content_lines = []
        elif user_input.lower() == "new page":
            book_data["pages"].append({"content": ""})
            current_page = len(book_data["pages"]) - 1
            book_data["current_page"] = current_page
            save_book(book_slug, book_data)
            current_content_lines = [""]
            current_line_index = -1
            editing_mode = False
        elif user_input.lower() == "previous page":
            if current_page > 0:
                current_page -= 1
                book_data["current_page"] = current_page
                save_book(book_slug, book_data)
                # Reset line editing state for the new page
                current_content_lines = book_data["pages"][current_page]["content"].split('\n') if book_data["pages"][current_page]["content"] else [""]
                current_line_index = -1
                editing_mode = False
        elif user_input.lower() == "next page":
            if current_page < len(book_data["pages"]) - 1:
                current_page += 1
                book_data["current_page"] = current_page
                save_book(book_slug, book_data)
                # Reset line editing state for the new page
                current_content_lines = book_data["pages"][current_page]["content"].split('\n') if book_data["pages"][current_page]["content"] else [""]
                current_line_index = -1
                editing_mode = False
            else:
                print(f"{Fore.YELLOW}You are on the last page. Use 'new page' to add a new page.{Style.RESET_ALL}")
                time.sleep(1)
        elif user_input.lower().startswith("go to page ="):
            try:
                page_num = int(user_input.split("=")[1].strip())
                if 1 <= page_num <= len(book_data["pages"]):
                    current_page = page_num - 1
                    book_data["current_page"] = current_page
                    save_book(book_slug, book_data)
                    # Reset line editing state for the new page
                    current_content_lines = book_data["pages"][current_page]["content"].split('\n') if book_data["pages"][current_page]["content"] else [""]
                    current_line_index = -1
                    editing_mode = False
                else:
                    print(f"{Fore.RED}Invalid page number. Valid range: 1-{len(book_data['pages'])}{Style.RESET_ALL}")
                    time.sleep(1)
            except:
                print(f"{Fore.RED}Invalid format. Use: go to page = <number>{Style.RESET_ALL}")
                time.sleep(1)
        elif user_input.lower().startswith("edit "):
            # Enter line editing mode for a specific line
            try:
                line_num = int(user_input.lower().replace("edit ", "").strip())
                if current_content_lines and 1 <= line_num <= len(current_content_lines):
                    current_line_index = line_num - 1
                    editing_mode = True
                else:
                    print(f"{Fore.RED}Invalid line number. Valid range: 1-{len(current_content_lines)}{Style.RESET_ALL}")
                    time.sleep(1)
            except ValueError:
                print(f"{Fore.RED}Invalid format. Use: edit <number>{Style.RESET_ALL}")
                time.sleep(1)
        elif user_input.lower() == "new line":
            # Add a blank line to the content
            current_content_lines.append("")
            book_data["pages"][current_page]["content"] = '\n'.join(current_content_lines)
            save_book(book_slug, book_data)
            print(f"{Fore.GREEN}Blank line added at the end.{Style.RESET_ALL}")
            time.sleep(0.5)
        elif user_input.lower().startswith("add line "):
            # Add a blank line before the specified line number
            try:
                line_num = int(user_input.lower().replace("add line ", "").strip())
                if current_content_lines and 1 <= line_num <= len(current_content_lines) + 1:
                    # Insert blank line at the specified position
                    current_content_lines.insert(line_num - 1, "")
                    book_data["pages"][current_page]["content"] = '\n'.join(current_content_lines)
                    save_book(book_slug, book_data)
                    print(f"{Fore.GREEN}Blank line added before line {line_num}.{Style.RESET_ALL}")
                    time.sleep(0.5)
                else:
                    print(f"{Fore.RED}Invalid line number. Valid range: 1-{len(current_content_lines) + 1}{Style.RESET_ALL}")
                    time.sleep(1)
            except ValueError:
                print(f"{Fore.RED}Invalid format. Use: add line <number>{Style.RESET_ALL}")
                time.sleep(1)
        elif user_input.lower() == "clear page":
            confirm = input(f"{Fore.YELLOW}Are you sure you want to clear this page? (yes/no): {Style.RESET_ALL}").lower()
            if confirm == "yes":
                book_data["pages"][current_page]["content"] = ""
                save_book(book_slug, book_data)
                current_content_lines = [""]
                current_line_index = -1
                editing_mode = False
                print(f"{Fore.GREEN}Page cleared.{Style.RESET_ALL}")
                time.sleep(1)
        elif user_input.lower().startswith("delete line "):
            # Delete the specified line and shift remaining lines up
            try:
                line_num = int(user_input.lower().replace("delete line ", "").strip())
                if current_content_lines and 1 <= line_num <= len(current_content_lines):
                    # Ask for confirmation before deleting
                    line_content = current_content_lines[line_num - 1]
                    display_content = line_content[:50] + "..." if len(line_content) > 50 else line_content
                    confirm = input(f"{Fore.YELLOW}Delete line {line_num}: '{display_content}'? (yes/no): {Style.RESET_ALL}").lower()
                    
                    if confirm == "yes":
                        # Remove the line
                        current_content_lines.pop(line_num - 1)
                        
                        # If we removed the last line and the document is now empty, add an empty line
                        if not current_content_lines:
                            current_content_lines = [""]
                        
                        # Update the book content
                        book_data["pages"][current_page]["content"] = '\n'.join(current_content_lines)
                        save_book(book_slug, book_data)
                        print(f"{Fore.GREEN}Line {line_num} deleted.{Style.RESET_ALL}")
                        time.sleep(0.5)
                else:
                    print(f"{Fore.RED}Invalid line number. Valid range: 1-{len(current_content_lines)}{Style.RESET_ALL}")
                    time.sleep(1)
            except ValueError:
                print(f"{Fore.RED}Invalid format. Use: delete line <number>{Style.RESET_ALL}")
                time.sleep(1)        
        elif user_input.lower().startswith("search ="):
            try:
                search_text = user_input.split("=")[1].strip()
                search_results = []
                for i, page in enumerate(book_data["pages"]):
                    if search_text.lower() in page["content"].lower():
                        search_results.append((i, page["content"]))
                
                if search_results:
                    clear_screen()
                    print(f"{Fore.GREEN}Search results for '{search_text}':{Style.RESET_ALL}")
                    for i, content in search_results:
                        print(f"\nPage {i+1}:")
                        context = content[:100] + "..." if len(content) > 100 else content
                        print(context)
                    
                    go_to = input(f"\n{Fore.CYAN}Go to page number (or Enter to cancel): {Style.RESET_ALL}")
                    if go_to.isdigit() and 1 <= int(go_to) <= len(book_data["pages"]):
                        current_page = int(go_to) - 1
                        book_data["current_page"] = current_page
                        save_book(book_slug, book_data)
                        # Reset line editing state for the new page
                        current_content_lines = book_data["pages"][current_page]["content"].split('\n') if book_data["pages"][current_page]["content"] else [""]
                        current_line_index = -1
                        editing_mode = False
                else:
                    print(f"{Fore.YELLOW}No matches found for '{search_text}'.{Style.RESET_ALL}")
                    time.sleep(1)
            except:
                print(f"{Fore.RED}Invalid format. Use: search = <text>{Style.RESET_ALL}")
                time.sleep(1)

        elif user_input.lower() == "save":
            save_book(book_slug, book_data)
            print(f"{Fore.GREEN}Book saved.{Style.RESET_ALL}")
            time.sleep(1)
        elif user_input.lower() == "rename book":
            new_title = input(f"{Fore.CYAN}Enter new title: {Style.RESET_ALL}")
            if new_title:
                book_data["title"] = new_title
                save_book(book_slug, book_data)
                print(f"{Fore.GREEN}Book renamed to '{new_title}'.{Style.RESET_ALL}")
                time.sleep(1)
        elif user_input.lower() == "update description":
            print(f"Current description: {book_data['description']}")
            new_description = input(f"{Fore.CYAN}Enter new description: {Style.RESET_ALL}")
            if new_description:
                book_data["description"] = new_description
                save_book(book_slug, book_data)
                print(f"{Fore.GREEN}Description updated.{Style.RESET_ALL}")
                time.sleep(1)
        elif user_input.lower().startswith("update font ="):
            try:
                font = user_input.split("=")[1].strip()
                book_data["settings"]["font"] = font
                save_book(book_slug, book_data)
                print(f"{Fore.GREEN}Font updated to {font}{Style.RESET_ALL}")
                time.sleep(1)
            except:
                print(f"{Fore.RED}Invalid font format. Use: update font = <name>{Style.RESET_ALL}")
                time.sleep(1)
        elif user_input.lower().startswith("update font-size ="):
            try:
                size = int(user_input.split("=")[1].strip())
                book_data["settings"]["font-size"] = size
                save_book(book_slug, book_data)
                print(f"{Fore.GREEN}Font size updated to {size}{Style.RESET_ALL}")
                time.sleep(1)
            except:
                print(f"{Fore.RED}Invalid size format. Use: update font-size = <size>{Style.RESET_ALL}")
                time.sleep(1)
        elif user_input.lower().startswith("update book-dimensions ="):
            try:
                dimensions = user_input.split("=")[1].strip()
                if "x" in dimensions:
                    book_data["settings"]["book-dimensions"] = dimensions
                    save_book(book_slug, book_data)
                    print(f"{Fore.GREEN}Book dimensions updated to {dimensions}{Style.RESET_ALL}")
                    time.sleep(1)
                else:
                    raise ValueError("Invalid format")
            except:
                print(f"{Fore.RED}Invalid dimensions format. Use: update book-dimensions = <widthxheight>{Style.RESET_ALL}")
                time.sleep(1)
        else:
            # Add the input as content to the current page
            if user_input == "":
                # Handle empty input as a signal to continue writing rather than adding a blank line
                print(f"{Fore.YELLOW}To add a blank line, use the 'new line' command.{Style.RESET_ALL}")
                time.sleep(1)
            else:
                # If the page is blank (only one empty line), replace that line instead of appending
                if len(current_content_lines) == 1 and current_content_lines[0] == "":
                    current_content_lines[0] = user_input
                else:
                    # Otherwise append as normal
                    current_content_lines.append(user_input)
                
                # Update the book content
                book_data["pages"][current_page]["content"] = '\n'.join(current_content_lines)
                save_book(book_slug, book_data)




def show_help():
    """Show help information for the writing interface"""
    clear_screen()
    print(f"{Fore.GREEN}=== TerminalWriter Help ==={Style.RESET_ALL}")
    
    print("\nLine Editing Commands:")
    print("  edit <number>        - Edit a specific line by its line number")
    print("  new line             - Insert a blank line at the end of your text")
    print("  add line <number>    - Insert a blank line before the specified line number")
    print("  delete line <number> - Delete the specified line and shift remaining lines up")
    
    print("\nNavigation Commands:")
    print("  new page             - Create a new page and navigate to it")
    print("  previous page        - Go to the previous page")
    print("  next page            - Go to the next page")
    print("  go to page = <num>   - Jump to a specific page number")
    
    print("\nFormatting Commands:")
    print("  update font = <name> - Change the font (e.g., Times-Roman, Helvetica)")
    print("  update font-size = <size> - Change the font size (e.g., 12)")
    print("  update book-dimensions = <wxh> - Change dimensions (e.g., 6x9 inches)")
    
    print("\nContent Editing Commands:")
    print("  clear page           - Clear all content from the current page")
    print("  search = <text>      - Search for text across all pages")
    
    print("\nBook Management Commands:")
    print("  save                 - Explicitly save the book (auto-saves occur after most actions)")
    print("  rename book          - Change the title of the book")
    print("  update description   - Change the book description")
    print("  characters           - Manage characters in your book")
    
    print("\nSystem Commands:")
    print("  help                 - Show this help screen")
    print("  status               - Show book statistics and information")
    print("  exit                 - Return to the main menu")
    
    print("\nInline Formatting:")
    print("  !font-size(24)[text] - Makes specific text appear in size 24 (any size can be used)")
    print("  *bold text*          - Makes text bold")
    print("  _italic text_        - Makes text italic")
    print("  # Heading 1          - Creates a large heading")
    print("  ## Heading 2         - Creates a medium heading")
    print("  ### Heading 3        - Creates a small heading")
    print("  <character>          - Automatically replaced with the character's name")
    print("  ![alt text](file:///path/to/image.jpg) - Inserts an image")
    print("  [link text](https://example.com) - Creates a hyperlink")
    
    print("\nEditing Tips:")
    print("  - Use 'new line' to add a blank line to your text")
    print("  - Use 'edit <number>' to edit a specific line by its number")
    print("  - Line numbers are displayed for easier navigation")
    print("  - Pressing Enter during text entry creates a line break that will be preserved in exports")


def show_status(book_data):
    """Show status information about the book"""
    clear_screen()
    print(f"{Fore.GREEN}=== Book Status: {book_data['title']} ==={Style.RESET_ALL}")
    print(f"\nAuthor: {book_data['author']}")
    print(f"Created: {book_data['created_at']}")
    print(f"Last modified: {book_data['last_modified']}")
    print(f"Total pages: {len(book_data['pages'])}")
    
    # Count words and characters
    word_count = 0
    char_count = 0
    for page in book_data["pages"]:
        content = page["content"]
        words = content.split()
        word_count += len(words)
        char_count += len(content)
    
    print(f"\nTotal word count: {word_count}")
    print(f"Total character count: {char_count}")
    
    print(f"\nFormatting settings:")
    print(f"  Font: {book_data['settings']['font']}")
    print(f"  Font size: {book_data['settings']['font-size']}")
    print(f"  Book dimensions: {book_data['settings']['book-dimensions']} inches")


def export_to_pdf(book_data, output_path):
    """Export book to PDF format"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
        from reportlab.lib.units import inch
        
        # Parse book dimensions
        dimensions = book_data["settings"]["book-dimensions"].split("x")
        width = float(dimensions[0]) * inch
        height = float(dimensions[1]) * inch
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=(width, height),
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'BookTitle',
            parent=styles['Title'],
            fontName=book_data["settings"]["font"],
            fontSize=book_data["settings"]["font-size"] + 8,
            alignment=1,  # Center alignment
            spaceAfter=30
        )
        
        normal_style = ParagraphStyle(
            'BookText',
            parent=styles['Normal'],
            fontName=book_data["settings"]["font"],
            fontSize=book_data["settings"]["font-size"],
            leading=book_data["settings"]["font-size"] * 1.2
        )
        
        # Build content
        story = []
        
        # Add title page
        story.append(Paragraph(book_data["title"], title_style))
        story.append(Paragraph(f"By {book_data['author']}", normal_style))
        story.append(PageBreak())
        
        # Process each page
        for page in book_data["pages"]:
            if not page["content"].strip():
                continue
                
            # Process font-size tags before markdown conversion
            content = page["content"]
            
            # Process character tags first
            if "characters" in book_data and book_data["characters"]:
                content = process_character_tags(content, book_data["characters"])
            
            # Process custom font-size tags: !font-size(size)[text]
            # Replace with HTML spans for size changes
            pattern = r'!font-size\((\d+)\)\[(.*?)\]'
            
            def font_size_replace(match):
                size = match.group(1)
                text = match.group(2)
                return f'<span style="font-size:{size}pt;">{text}</span>'
            
            content_with_spans = re.sub(pattern, font_size_replace, content)
            
            # Ensure newlines are preserved by adding two spaces before each newline for markdown
            content_with_breaks = re.sub(r'(?m)$', '  ', content_with_spans)
            
            # Convert markdown to HTML
            html = markdown.markdown(content_with_breaks)
            
            # Process image references in markdown
            img_pattern = r'!\[([^\]]*)\]\(file:///([^)]+)\)'
            matches = re.findall(img_pattern, page["content"])
            
            # Extract plain content for text processing
            plain_content = re.sub(img_pattern, '', page["content"])
            
            # Handle font-size spans directly - extract them to create separate paragraphs
            html_parts = []
            soup = BeautifulSoup(html, 'html.parser')
            
            # Convert HTML to a series of plain paragraphs and styled text
            for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                # Process each paragraph element
                if element.name.startswith('h'):
                    # For headings, create a heading paragraph
                    heading_style = ParagraphStyle(
                        f'Heading{element.name[1]}',
                        parent=styles['Heading1'],
                        fontName=book_data["settings"]["font"],
                        fontSize=book_data["settings"]["font-size"] + (6 - int(element.name[1])) * 2,
                        alignment=1  # Center alignment
                    )
                    story.append(Paragraph(element.get_text(), heading_style))
                else:
                    # Create a simpler version of the paragraph without using complex spans
                    # We'll just extract the text and reconstruct the paragraph
                    # This avoids the 'findSpanStyle not implemented' error
                    simplified_text = ""
                    
                    # Process each part of the element to handle font sizes
                    for content in element.contents:
                        if isinstance(content, str):
                            simplified_text += content
                        elif content.name == 'span' and 'style' in content.attrs:
                            # For span elements with styles, we'll add the text separately
                            # with the appropriate font size
                            style_text = content.attrs['style']
                            size_match = re.search(r'font-size:(\d+)pt;', style_text)
                            
                            if size_match:
                                # If we have text already, add it first
                                if simplified_text:
                                    story.append(Paragraph(simplified_text, normal_style))
                                    simplified_text = ""
                                
                                # Now add the sized text
                                font_size = int(size_match.group(1))
                                sized_style = ParagraphStyle(
                                    f'SizedText_{font_size}',
                                    parent=normal_style,
                                    fontSize=font_size
                                )
                                story.append(Paragraph(content.get_text(), sized_style))
                            else:
                                # Just add the text if we can't extract a size
                                simplified_text += content.get_text()
                        elif content.name == 'br':
                            # Handle line breaks by adding the current text
                            # and starting a new paragraph
                            if simplified_text:
                                story.append(Paragraph(simplified_text, normal_style))
                                simplified_text = ""
                        elif content.name == 'em':
                            # Italic text
                            simplified_text += content.get_text()  # We'll just keep the text without styling
                        elif content.name == 'strong':
                            # Bold text
                            simplified_text += content.get_text()  # We'll just keep the text without styling
                        else:
                            # Other elements
                            simplified_text += content.get_text()
                    
                    # Add any remaining text
                    if simplified_text:
                        story.append(Paragraph(simplified_text, normal_style))
            
            # If no HTML elements were found, add the original HTML as a fallback
            if not soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                story.append(Paragraph(html, normal_style))
            
            # Add images if there are any
            for alt_text, img_path in matches:
                try:
                    img = Image(img_path, width=4*inch, height=3*inch)
                    story.append(img)
                except Exception as e:
                    # If image can't be loaded, add a note
                    story.append(Paragraph(f"[Image: {alt_text} (could not be loaded: {e})]", normal_style))
            
            story.append(PageBreak())
        
        # Add description at the end
        story.append(Paragraph("About This Book", title_style))
        story.append(Paragraph(book_data["description"], normal_style))
        
        # Build the PDF
        doc.build(story)
        return True
        
    except Exception as e:
        print(f"{Fore.RED}Error exporting to PDF: {e}{Style.RESET_ALL}")
        return False


def export_to_epub(book_data, output_path):
    """Export book to ePub format"""
    try:
        import ebooklib
        from ebooklib import epub
        from bs4 import BeautifulSoup
        
        # Create new EPUB book
        book = epub.EpubBook()
        
        # Set metadata
        book.set_identifier(f"terminalwriter-{int(time.time())}")
        book.set_title(book_data["title"])
        book.set_language('en')
        book.add_author(book_data["author"])
        
        # Create chapters
        chapters = []
        toc = []
        
        # Create title page
        title_page = epub.EpubHtml(title='Title Page', file_name='title.xhtml')
        title_page.content = f'''
        <html>
        <head>
            <title>{book_data["title"]}</title>
        </head>
        <body>
            <h1>{book_data["title"]}</h1>
            <p>By {book_data["author"]}</p>
        </body>
        </html>
        '''
        book.add_item(title_page)
        chapters.append(title_page)
        
        # Process each page into a chapter
        for i, page in enumerate(book_data["pages"]):
            if not page["content"].strip():
                continue
                
            # Process custom font-size tags: !font-size(size)[text]
            # Replace with HTML spans for size changes
            content = page["content"]
            
            # Process character tags first
            if "characters" in book_data and book_data["characters"]:
                content = process_character_tags(content, book_data["characters"])
                
            pattern = r'!font-size\((\d+)\)\[(.*?)\]'
            
            def font_size_replace(match):
                size = match.group(1)
                text = match.group(2)
                return f'<span style="font-size:{size}pt;">{text}</span>'
            
            content_with_spans = re.sub(pattern, font_size_replace, content)
            
            # Ensure newlines are preserved by adding two spaces before each newline for markdown
            content_with_breaks = re.sub(r'(?m)$', '  ', content_with_spans)
            
            # Convert markdown to HTML
            html_content = markdown.markdown(content_with_breaks)
            
            # Create chapter
            chapter = epub.EpubHtml(title=f'Chapter {i+1}', file_name=f'chapter_{i+1}.xhtml')
            
            # Clean up the HTML using BeautifulSoup to ensure proper formatting
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Process image references
            img_pattern = r'!\[([^\]]*)\]\(file:///([^)]+)\)'
            matches = re.findall(img_pattern, page["content"])
            
            # Replace image references with actual image tags
            for alt_text, img_path in matches:
                try:
                    # Create an image item
                    img_filename = os.path.basename(img_path)
                    epub_img = epub.EpubItem(
                        uid=f'image_{i}_{img_filename}',
                        file_name=f'images/{img_filename}',
                        media_type='image/jpeg',
                        content=open(img_path, 'rb').read()
                    )
                    book.add_item(epub_img)
                    
                    # Reference in HTML
                    img_tag = f'<img src="images/{img_filename}" alt="{alt_text}" />'
                    html_content = html_content.replace(f'<img src="file:///{img_path}" alt="{alt_text}" />', img_tag)
                except Exception as e:
                    placeholder = f'[Image: {alt_text} (could not be loaded: {e})]'
                    html_content += f'<p>{placeholder}</p>'
                    
            # Ensure font-size spans are properly styled with CSS classes
            html_content = html_content.replace('<span style="font-size:', '<span class="size-')
            
            chapter.content = f'''
            <html>
            <head>
                <title>Chapter {i+1}</title>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            '''
            
            book.add_item(chapter)
            chapters.append(chapter)
            toc.append(chapter)
        
        # Add description as the last chapter
        about_page = epub.EpubHtml(title='About This Book', file_name='about.xhtml')
        about_page.content = f'''
        <html>
        <head>
            <title>About This Book</title>
        </head>
        <body>
            <h1>About This Book</h1>
            <p>{book_data["description"]}</p>
        </body>
        </html>
        '''
        book.add_item(about_page)
        chapters.append(about_page)
        toc.append(about_page)
        
        # Define Table of Contents
        book.toc = toc
        
        # Add default CSS with specific font size classes
        style = '''
        body {
            font-family: serif;
            font-size: medium;
            margin: 0 5%;
            text-align: justify;
        }
        h1, h2, h3, h4 {
            text-align: center;
            font-weight: bold;
        }
        em {
            font-style: italic;
        }
        strong {
            font-weight: bold;
        }
        .size-8pt { font-size: 8pt; }
        .size-10pt { font-size: 10pt; }
        .size-12pt { font-size: 12pt; }
        .size-14pt { font-size: 14pt; }
        .size-16pt { font-size: 16pt; }
        .size-18pt { font-size: 18pt; }
        .size-20pt { font-size: 20pt; }
        .size-21pt { font-size: 21pt; }
        .size-24pt { font-size: 24pt; }
        .size-28pt { font-size: 28pt; }
        .size-32pt { font-size: 32pt; }
        .size-36pt { font-size: 36pt; }
        .size-42pt { font-size: 42pt; }
        .size-48pt { font-size: 48pt; }
        .size-54pt { font-size: 54pt; }
        .size-60pt { font-size: 60pt; }
        .size-72pt { font-size: 72pt; }
        '''
        css = epub.EpubItem(
            uid="style_default",
            file_name="style/default.css",
            media_type="text/css",
            content=style
        )
        book.add_item(css)
        
        # Add chapters to book
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        
        # Define spine
        book.spine = ['nav'] + chapters
        
        # Create EPUB
        epub.write_epub(output_path, book)
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}Error exporting to ePub: {e}{Style.RESET_ALL}")
        return False


def export_to_text(book_data, output_path):
    """Export book to plain text format"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write title and author
            f.write(f"{book_data['title']}\n")
            f.write(f"By {book_data['author']}\n\n")
            f.write("=" * 50 + "\n\n")
            
            # Write content
            for i, page in enumerate(book_data["pages"]):
                if page["content"].strip():
                    # Handle image references
                    content = page["content"]
                    
                    # Process character tags first
                    if "characters" in book_data and book_data["characters"]:
                        content = process_character_tags(content, book_data["characters"])
                    
                    # Process font size tags - in plain text we'll just include a note
                    pattern = r'!font-size\((\d+)\)\[(.*?)\]'
                    
                    def font_size_replace(match):
                        size = match.group(1)
                        text = match.group(2)
                        return text  # Just keep the text for plain text format
                    
                    content = re.sub(pattern, font_size_replace, content)
                    
                    # Handle image references
                    img_pattern = r'!\[([^\]]*)\]\(file:///[^)]+\)'
                    content = re.sub(img_pattern, r'[IMAGE: \1]', content)
                    
                    f.write(content + "\n\n")
                    f.write("-" * 50 + "\n\n")
            
            # Write description at the end
            f.write("About This Book\n")
            f.write("=" * 50 + "\n\n")
            f.write(book_data["description"] + "\n")
        
        return True
    except Exception as e:
        print(f"{Fore.RED}Error exporting to text: {e}{Style.RESET_ALL}")
        return False


def delete_book():
    """Delete an existing book from the system"""
    book_slug = select_book()
    if not book_slug:
        return
    
    # Get book data to display title
    book_path = os.path.join(BOOKS_DIR, book_slug, "book.json")
    try:
        with open(book_path, 'r') as f:
            book_data = json.load(f)
            title = book_data['title']
    except Exception:
        title = book_slug
    
    clear_screen()
    print(f"{Fore.RED}=== Delete Book: {title} ==={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Warning: This will permanently delete this book and all its contents.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}This action cannot be undone!{Style.RESET_ALL}")
    
    # Ask for confirmation with the book title
    confirmation = input(f"\n{Fore.RED}Type the book title to confirm deletion: {Style.RESET_ALL}")
    
    if confirmation == title:
        try:
            # Remove from configuration first
            config = load_config()
            config["books"] = [book for book in config["books"] if book["slug"] != book_slug]
            save_config(config)
            
            # Delete the book directory
            import shutil
            book_dir = os.path.join(BOOKS_DIR, book_slug)
            shutil.rmtree(book_dir)
            
            print(f"{Fore.GREEN}Book '{title}' has been deleted successfully.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error deleting book: {e}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Book deletion cancelled. Titles did not match.{Style.RESET_ALL}")
    
    input("Press Enter to return to the main menu...")


def export_book():
    """Export a book to various formats"""
    book_slug = select_book()
    if not book_slug:
        return
    
    book_data = load_book(book_slug)
    if not book_data:
        return
    
    clear_screen()
    print(f"{Fore.GREEN}=== Export Book: {book_data['title']} ==={Style.RESET_ALL}")
    print("1. PDF")
    print("2. ePub")
    print("3. Plain Text")
    print(f"0. {Fore.YELLOW}Cancel{Style.RESET_ALL}")
    
    try:
        choice = int(input(f"{Fore.CYAN}Select export format (0-3): {Style.RESET_ALL}"))
        
        if choice == 0:
            return
          # Sanitize the filename but keep it in the book's folder
        filename_base = re.sub(r'[^a-zA-Z0-9_]', '_', book_data['title'])
        
        if choice == 1:
            # Export to PDF
            output_path = os.path.join(BOOKS_DIR, book_slug, f"{filename_base}.pdf")
            print(f"{Fore.CYAN}Exporting to PDF...{Style.RESET_ALL}")
            if export_to_pdf(book_data, output_path):
                print(f"{Fore.GREEN}Book exported successfully to {output_path}{Style.RESET_ALL}")
            
        elif choice == 2:
            # Export to ePub
            output_path = os.path.join(BOOKS_DIR, book_slug, f"{filename_base}.epub")
            print(f"{Fore.CYAN}Exporting to ePub...{Style.RESET_ALL}")
            if export_to_epub(book_data, output_path):
                print(f"{Fore.GREEN}Book exported successfully to {output_path}{Style.RESET_ALL}")
            
        elif choice == 3:
            # Export to Text
            output_path = os.path.join(BOOKS_DIR, book_slug, f"{filename_base}.txt")
            print(f"{Fore.CYAN}Exporting to Plain Text...{Style.RESET_ALL}")
            if export_to_text(book_data, output_path):
                print(f"{Fore.GREEN}Book exported successfully to {output_path}{Style.RESET_ALL}")
        
        input("Press Enter to return to the main menu...")
        
    except ValueError:
        print(f"{Fore.RED}Invalid choice. Please enter a number.{Style.RESET_ALL}")
        time.sleep(1)


def edit_book():
    """Edit an existing book"""
    book_slug = select_book()
    if book_slug:
        writing_interface(book_slug)


def manage_characters(book_slug, book_data):
    """Interface for managing book characters"""
    while True:
        clear_screen()
        print(f"{Fore.GREEN}=== Character Management: {book_data['title']} ==={Style.RESET_ALL}")
        print("1. View Characters")
        print("2. Add Character")
        print("3. Remove Character")
        print("4. Generate Character Name")
        print(f"0. {Fore.YELLOW}Back to Writing Interface{Style.RESET_ALL}")
        
        try:
            choice = int(input(f"{Fore.CYAN}Enter your choice (0-4): {Style.RESET_ALL}"))
            
            if choice == 0:
                break
            elif choice == 1:
                view_characters(book_data)
            elif choice == 2:
                add_character(book_slug, book_data)
            elif choice == 3:
                remove_character(book_slug, book_data)
            elif choice == 4:
                generate_character_name(book_slug, book_data)
            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
                time.sleep(1)
        except ValueError:
            print(f"{Fore.RED}Please enter a number.{Style.RESET_ALL}")
            time.sleep(1)
    
    return book_data


def view_characters(book_data):
    """Display all characters in the book"""
    clear_screen()
    print(f"{Fore.GREEN}=== Characters in {book_data['title']} ==={Style.RESET_ALL}")
    
    if not book_data.get("characters", {}):
        print(f"{Fore.YELLOW}No characters defined yet. Use 'Add Character' to create some.{Style.RESET_ALL}")
    else:
        print("\nTag: Character Name")
        print("-" * 30)
        for tag, char_info in book_data["characters"].items():
            print(f"{Fore.CYAN}{tag}{Style.RESET_ALL}: {char_info['name']}")
    
    input("\nPress Enter to continue...")


def add_character(book_slug, book_data):
    """Add a new character to the book"""
    clear_screen()
    print(f"{Fore.GREEN}=== Add New Character ==={Style.RESET_ALL}")
    
    # Initialize characters dict if it doesn't exist
    if "characters" not in book_data:
        book_data["characters"] = {}
    
    tag = input(f"{Fore.CYAN}Enter character tag: {Style.RESET_ALL}")
    if not tag:
        print(f"{Fore.YELLOW}Character tag cannot be empty. Cancelling...{Style.RESET_ALL}")
        time.sleep(1)
        return
    
    if tag in book_data["characters"]:
        confirm = input(f"{Fore.YELLOW}Character <{tag}> already exists. Overwrite? (yes/no): {Style.RESET_ALL}").lower()
        if confirm != "yes":
            print("Character creation cancelled.")
            time.sleep(1)
            return
    
    name = input(f"{Fore.CYAN}Enter character name: {Style.RESET_ALL}")
    
    book_data["characters"][tag] = {
        "name": name
    }
    
    save_book(book_slug, book_data)
    print(f"{Fore.GREEN}Character <{tag}> added successfully!{Style.RESET_ALL}")
    time.sleep(1)


def remove_character(book_slug, book_data):
    """Remove a character from the book"""
    clear_screen()
    print(f"{Fore.GREEN}=== Remove Character ==={Style.RESET_ALL}")
    
    if not book_data.get("characters", {}):
        print(f"{Fore.YELLOW}No characters defined yet.{Style.RESET_ALL}")
        time.sleep(1)
        return
    
    print("Available characters:")
    for i, tag in enumerate(book_data["characters"].keys(), 1):
        char_name = book_data["characters"][tag]["name"]
        print(f"{i}. {tag}: {char_name}")
    
    print(f"0. {Fore.YELLOW}Cancel{Style.RESET_ALL}")
    
    try:
        choice = int(input(f"{Fore.CYAN}Enter your choice (0-{len(book_data['characters'])}): {Style.RESET_ALL}"))
        
        if choice == 0:
            return
        
        if 1 <= choice <= len(book_data["characters"]):
            tag_to_remove = list(book_data["characters"].keys())[choice - 1]
            char_name = book_data["characters"][tag_to_remove]["name"]
            confirm = input(f"{Fore.RED}Are you sure you want to remove {tag_to_remove}: {char_name}? (Yes/No): {Style.RESET_ALL}").lower()
            
            if confirm == "yes":
                del book_data["characters"][tag_to_remove]
                save_book(book_slug, book_data)
                print(f"{Fore.GREEN}Character {tag_to_remove}: {char_name} removed successfully!{Style.RESET_ALL}")
                time.sleep(1)
            elif confirm == "no":
                print(f"{Fore.YELLOW}Character removal cancelled.{Style.RESET_ALL}")
                time.sleep(1)
            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
                time.sleep(1)
        else:
            print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
            time.sleep(1)
    except ValueError:
        print(f"{Fore.RED}Please enter a number.{Style.RESET_ALL}")
        time.sleep(1)


def generate_character_name(book_slug, book_data):
    """Generate a character name using the names package"""
    clear_screen()
    print(f"{Fore.GREEN}=== Generate Character Name ==={Style.RESET_ALL}")
    
    print("Name generation options:")
    print("1. Full Name")
    print("2. First Name Only")
    print("3. Last Name Only")
    print(f"0. {Fore.YELLOW}Cancel{Style.RESET_ALL}")
    
    try:
        choice = int(input(f"{Fore.CYAN}Enter your choice (0-3): {Style.RESET_ALL}"))
        
        if choice == 0:
            return
        
        if choice in [1, 2]:
            print("-----------------------------------------------------")
            print("\nSelect gender:")
            print("1. Male")
            print("2. Female")
            print("3. Random")
            
            gender_choice = int(input(f"{Fore.CYAN}Enter your choice (1-3): {Style.RESET_ALL}"))
            
            if gender_choice == 1:
                gender = 'male'
            elif gender_choice == 2:
                gender = 'female'
            else:
                gender = None
        
        # Generate name based on selection
        generated_name = ""
        if choice == 1:  # Full name
            generated_name = names.get_full_name(gender=gender)
        elif choice == 2:  # First name only
            generated_name = names.get_first_name(gender=gender)
        elif choice == 3:  # Last name only
            generated_name = names.get_last_name()
        
        print(f"\n{Fore.GREEN}Generated Name: {Style.BRIGHT}{generated_name}{Style.RESET_ALL}")
        print("\nWould you like to add this character to your book?")
        print("1. Yes, add this character")
        print("2. Generate another name")
        print(f"0. {Fore.YELLOW}Cancel{Style.RESET_ALL}")
        
        add_choice = int(input(f"{Fore.CYAN}Enter your choice (0-2): {Style.RESET_ALL}"))
        
        if add_choice == 1:
            # Initialize characters dict if it doesn't exist
            if "characters" not in book_data:
                book_data["characters"] = {}
            
            # Ask for a tag for this character
            tag = input(f"{Fore.CYAN}Enter character tag (used like <tag> in text): {Style.RESET_ALL}")
            
            if not tag:
                print(f"{Fore.YELLOW}Character tag cannot be empty. Cancelling...{Style.RESET_ALL}")
                time.sleep(1)
                return
            
            if tag in book_data["characters"]:
                confirm = input(f"{Fore.YELLOW}Character <{tag}> already exists. Overwrite? (yes/no): {Style.RESET_ALL}").lower()
                if confirm != "yes":
                    print("Character addition cancelled.")
                    time.sleep(1)
                    return
            
            # Add the character
            book_data["characters"][tag] = {
                "name": generated_name
            }
            
            save_book(book_slug, book_data)
            print(f"{Fore.GREEN}Character <{tag}> added with name '{generated_name}'!{Style.RESET_ALL}")
            time.sleep(1)
        elif add_choice == 2:
            # Generate another name
            return generate_character_name(book_slug, book_data)
        
    except ValueError:
        print(f"{Fore.RED}Please enter a number.{Style.RESET_ALL}")
        time.sleep(1)
    
    input("Press Enter to continue...")


def process_character_tags(content, characters):
    """Replace character tags with their names in the content"""
    if not characters:
        return content
    
    # Create a pattern that matches character tags in the format <tag>
    for tag, char_info in characters.items():
        tag_pattern = f"<{tag}>"
        content = content.replace(tag_pattern, char_info["name"])
    
    return content


def main():
    """Main application function"""
    ensure_books_directory()
    
    # Show startup message the first time
    welcome_file = os.path.join(APP_DIR, ".welcome_shown")
    if not os.path.exists(welcome_file):
        print(f"{Fore.GREEN}Welcome to TerminalWriter!{Style.RESET_ALL}")
        print(f"Your books and configuration will be stored in: {APP_DIR}")
        print("Press Enter to continue...")
        input()
        # Create welcome file so we don't show this again
        with open(welcome_file, 'w') as f:
            f.write("1")
    
    while True:
        clear_screen()
        print(f"""{Fore.GREEN}=== Terminal Writer ==={Style.RESET_ALL}""")
        print("1. Create New Book")
        print("2. Edit Existing Book")
        print("3. Export Book")
        print(f"4. {Fore.RED}Delete Book{Style.RESET_ALL}")
        print(f"0. {Fore.YELLOW}Exit{Style.RESET_ALL}")
        
        try:
            choice = int(input(f"{Fore.CYAN}Enter your choice (0-4): {Style.RESET_ALL}"))
            
            if choice == 0:
                break
            elif choice == 1:
                create_book()
            elif choice == 2:
                edit_book()
            elif choice == 3:
                export_book()
            elif choice == 4:
                delete_book()
            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
                time.sleep(1)
        except ValueError:
            print(f"{Fore.RED}Please enter a number.{Style.RESET_ALL}")
            time.sleep(1)


if __name__ == "__main__":
    main()
