#!/usr/bin/env python3
"""
TerminalWriter - A terminal-based book writing application
"""
import os
import json
import sys
import time
import re
from colorama import init, Fore, Back, Style
import markdown
import tempfile

# Initialize colorama for cross-platform colored terminal output
init()

# Global variables
# Use the Documents folder in user profile for storing books and configurations
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
        "settings": DEFAULT_SETTINGS.copy()
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
    
    while True:
        clear_screen()
        
        # Display book info and current page
        print(f"{Fore.GREEN}=== {book_data['title']} ===")
        print(f"Page {current_page + 1} of {len(book_data['pages'])}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Font: {book_data['settings']['font']} | "
              f"Size: {book_data['settings']['font-size']} | "
              f"Dimensions: {book_data['settings']['book-dimensions']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Commands:")
        print(f"  Writing: type your text and press Enter to add it to the current page")
        print(f"  Navigation: new page, previous page, next page, go to page = <number>")
        print(f"  Formatting: update font = <name>, update font-size = <size>, update book-dimensions = <widthxheight>")
        print(f"  Content: clear page, search = <text>, replace = <old>:<new>")
        print(f"  Book: save, rename book, update description")
        print(f"  System: help, status, exit{Style.RESET_ALL}")

        print("-" * 50)
        
        # Display current page content
        if book_data["pages"][current_page]["content"]:
            print(book_data["pages"][current_page]["content"])
        else:
            print(f"{Fore.YELLOW}This page is empty. Type your content above.{Style.RESET_ALL}")
        
        print("-" * 50)
        
        # Get user input
        user_input = input(f"{Fore.CYAN}> {Style.RESET_ALL}")
        
        # Process commands
        if user_input.lower() == "exit":
            break
        elif user_input.lower() == "help":
            show_help()
            input("Press Enter to continue...")
        elif user_input.lower() == "status":
            show_status(book_data)
            input("Press Enter to continue...")
        elif user_input.lower() == "new page":
            book_data["pages"].append({"content": ""})
            current_page = len(book_data["pages"]) - 1
            book_data["current_page"] = current_page
            save_book(book_slug, book_data)
        elif user_input.lower() == "previous page":
            if current_page > 0:
                current_page -= 1
                book_data["current_page"] = current_page
                save_book(book_slug, book_data)
        elif user_input.lower() == "next page":
            if current_page < len(book_data["pages"]) - 1:
                current_page += 1
                book_data["current_page"] = current_page
                save_book(book_slug, book_data)
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
                else:
                    print(f"{Fore.RED}Invalid page number. Valid range: 1-{len(book_data['pages'])}{Style.RESET_ALL}")
                    time.sleep(1)
            except:
                print(f"{Fore.RED}Invalid format. Use: go to page = <number>{Style.RESET_ALL}")
                time.sleep(1)
        elif user_input.lower() == "clear page":
            confirm = input(f"{Fore.YELLOW}Are you sure you want to clear this page? (yes/no): {Style.RESET_ALL}").lower()
            if confirm == "yes":
                book_data["pages"][current_page]["content"] = ""
                save_book(book_slug, book_data)
                print(f"{Fore.GREEN}Page cleared.{Style.RESET_ALL}")
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
                else:
                    print(f"{Fore.YELLOW}No matches found for '{search_text}'.{Style.RESET_ALL}")
                    time.sleep(1)
            except:
                print(f"{Fore.RED}Invalid format. Use: search = <text>{Style.RESET_ALL}")
                time.sleep(1)
        elif user_input.lower().startswith("replace ="):
            try:
                params = user_input.split("=")[1].strip()
                old_text, new_text = params.split(":", 1)
                old_text = old_text.strip()
                new_text = new_text.strip()
                
                content = book_data["pages"][current_page]["content"]
                if old_text in content:
                    modified_content, replaced_count = selective_replace(content, old_text, new_text)
                    book_data["pages"][current_page]["content"] = modified_content
                    save_book(book_slug, book_data)
                    if replaced_count > 0:
                        print(f"{Fore.GREEN}Replaced {replaced_count} occurrence(s) of '{old_text}' with '{new_text}'.{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}No occurrences of '{old_text}' found to replace.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}Text '{old_text}' not found on this page.{Style.RESET_ALL}")
                time.sleep(1)
            except Exception as e:
                print(f"{Fore.RED}Invalid format. Use: replace = old text : new text{Style.RESET_ALL}")
                print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
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
            if book_data["pages"][current_page]["content"]:
                book_data["pages"][current_page]["content"] += "\n" + user_input
            else:
                book_data["pages"][current_page]["content"] = user_input
            save_book(book_slug, book_data)


def selective_replace(content, old_text, new_text):
    """Find and selectively replace text occurrences
    
    Returns:
        tuple: (modified_content, replaced_count)
    """
    # Find all occurrences
    occurrences = []
    start_pos = 0
    while True:
        pos = content.find(old_text, start_pos)
        if pos == -1:
            break
        
        # Get some context around the occurrence
        context_start = max(0, pos - 20)
        context_end = min(len(content), pos + len(old_text) + 20)
        context_before = content[context_start:pos]
        context_after = content[pos + len(old_text):context_end]
        
        occurrences.append({
            "position": pos,
            "context": f"...{context_before}{Fore.RED}{old_text}{Style.RESET_ALL}{context_after}..."
        })
        
        start_pos = pos + len(old_text)
    
    if len(occurrences) > 1:
        clear_screen()
        print(f"{Fore.GREEN}Found {len(occurrences)} occurrences of '{old_text}':{Style.RESET_ALL}\n")
        
        for i, occurrence in enumerate(occurrences, 1):
            print(f"{i}. {occurrence['context']}")
        
        print(f"A. {Fore.YELLOW}Replace ALL occurrences{Style.RESET_ALL}")
        print(f"0. {Fore.YELLOW}Cancel{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.CYAN}Which occurrence to replace? (0-{len(occurrences)}, A for all): {Style.RESET_ALL}")
        
        if choice.lower() == 'a':
            # Replace all occurrences
            return content.replace(old_text, new_text), len(occurrences)
        elif choice.isdigit() and 1 <= int(choice) <= len(occurrences):
            # Replace only the selected occurrence
            occurrence_idx = int(choice) - 1
            pos = occurrences[occurrence_idx]["position"]
            
            new_content = content[:pos] + new_text + content[pos + len(old_text):]
            return new_content, 1
        else:
            return content, 0
    elif len(occurrences) == 1:
        # Only one occurrence, just replace it
        return content.replace(old_text, new_text), 1
    else:
        return content, 0


def show_help():
    """Show help information for the writing interface"""
    clear_screen()
    print(f"{Fore.GREEN}=== TerminalWriter Help ==={Style.RESET_ALL}")
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
    print("  replace = <old>:<new> - Replace text on the current page")
    
    print("\nBook Management Commands:")
    print("  save                 - Explicitly save the book (auto-saves occur after most actions)")
    print("  rename book          - Change the title of the book")
    print("  update description   - Change the book description")
    
    print("\nSystem Commands:")
    print("  help                 - Show this help screen")
    print("  status               - Show book statistics and information")
    print("  exit                 - Return to the main menu")
    
    print("\nMarkdown Formatting:")
    print("  **bold text**        - Makes text bold")
    print("  *italic text*        - Makes text italic")
    print("  # Heading 1          - Creates a large heading")
    print("  ## Heading 2         - Creates a medium heading")
    print("  ### Heading 3        - Creates a small heading")
    print("  ![alt text](file:///path/to/image.jpg) - Inserts an image")
    print("  [link text](https://example.com) - Creates a hyperlink")


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
                
            # Convert markdown to HTML
            html = markdown.markdown(page["content"])
            
            # Process image references in markdown
            img_pattern = r'!\[([^\]]*)\]\(file:///([^)]+)\)'
            matches = re.findall(img_pattern, page["content"])
            
            # Extract plain content for text processing
            plain_content = re.sub(img_pattern, '', page["content"])
            
            # Create paragraph from HTML
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
                
            # Convert markdown to HTML
            html_content = markdown.markdown(page["content"])
            
            # Create chapter
            chapter = epub.EpubHtml(title=f'Chapter {i+1}', file_name=f'chapter_{i+1}.xhtml')
            
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
        
        # Add default CSS
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
        print(f"{Fore.GREEN}=== Terminal Writer ==={Style.RESET_ALL}")
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
