import selenium
import selenium.webdriver
import selenium.webdriver.chrome.options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import os
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from googlesearch import search
from searcher import google_search
from bs4 import BeautifulSoup
import random
from readability import Document
import textwrap
import re
import requests
import sys  # Add this import

current_search_index = 0
begin = 0
end = 3

# Vector to store messages
messages = []

headless_mode = True
productivity_mode = False

def help_command(_):
    for command in commands:
        messages.append(command + ": " + commands[command][1])
    messages.append("\n")
    
def productivity(_):
    global productivity_mode
    productivity_mode = not productivity_mode
    messages.append(f"Productivity mode {'enabled' if productivity_mode else 'disabled'}.")
    
def check_if_productive(search):
    response = requests.post(
        'https://ai.hackclub.com/chat/completions',
        headers={'Content-Type': 'application/json'},
        json={
            'messages': [
                {
                    'role': 'user',
                    'content': f'Is the following search productive, or is it a sign of the user slacking off? Do not be too strict, mainly just look for brainrot and respond with yes or no. If no respond with a more productive url and why it is a no {search}'
                }
            ]
        }
    )

    if response.status_code == 200:
        ai_response = response.json()
        if 'yes' in ai_response['choices'][0]['message']['content'].lower():
            return True
        else:
            messages.append(f"Suggested productive URL: {ai_response['choices'][0]['message']['content']}")
            return False
    else:
        messages.append("Failed to check productivity. Please try again later.")
        return False
    
def next_page(_):
    global begin, end, current_search_index
    if end >= 24:
        messages.append("Already at the end.")
        return
    begin += 3
    end += 3
    current_search_index = begin
    
def previous_page(_):
    global begin, end, current_search_index
    if begin == 0:
        messages.append("Already at the beginning.")
        return
    begin -= 3
    end -= 3
    current_search_index = begin
    
def up(_):
    global current_search_index, begin, end
    if current_search_index == begin:
        previous_page(None)
        messages.append("Already at the top, will go to previous page")        
        return
    current_search_index -= 1

def down(_):
    global current_search_index, begin, end
    if current_search_index >= end-1:
        next_page(None)
        messages.append("Already at the bottom, will go to next page")
        return
    current_search_index += 1

def switch_tab(tab):
    global current_search_index, begin, end
    if tab == None or tab == "" or not tab.isdigit():
        messages.append("Please enter a tab number.")
        return
    tab = int(tab)
    if tab > len(driver.window_handles):
        messages.append("Invalid tab number.")
        return
    current_search_index = 0
    begin = 0
    end = 3
    driver.switch_to.window(driver.window_handles[tab-1])
    
def enter_command(_):
    global current_search_index
    if "google.com/search" in driver.current_url:
        current_handle = driver.current_window_handle
        title = driver.title
        title = title.strip()
        title = title.replace(" - Google Search", "")
        listtoprint = google_search(title)
        urltogoto = listtoprint[current_search_index][0]
        try:
            driver.get(urltogoto)
        except requests.exceptions.Timeout:
            messages.append("Request timed out. Please try again later.")
            messages.append("If this issue continues just use a different wifi ot switch to data/hotspot")
            return
    else:
        messages.append("You are already in a website!")
        return
    
    
def new_tab(_):
    driver.execute_script("window.open('https://www.google.com/');")

def goback(_):
    global current_search_index, begin, end
    current_search_index = 0
    begin = 0
    end = 3
    driver.back()
    
def goforward(_):
    global current_search_index, begin, end
    current_search_index = 0
    begin = 0
    end = 3
    driver.forward()

def search(input):
    global current_search_index, begin, end, productivity_mode
    current_search_index = 0
    begin = 0
    end = 3
    status = False
    if input is None:
        messages.append("Please enter a search query.")
        return
    if productivity_mode == True:
        status = check_if_productive(input)
        messages.append(status)
    if status == False and productivity_mode == True:
        return
    if input.startswith("http://") or input.startswith("https://"):
        try:
            driver.get(input)
        except:
            input = input.replace(" ", "+")
            input = "https://www.google.com/search?q=" + input
            driver.get(input)   
            messages.append("Invalid URL, searched with Google Instead")
            return
    else:
        input = input.replace(" ", "+")
        input = "https://www.google.com/search?q=" + input
        driver.get(input)

def close_tab(_):
    global current_search_index, begin, end
    current_search_index = 0
    begin = 0
    end = 3
    if len(driver.window_handles) > 1:
        current_handle = driver.current_window_handle
        driver.close()
        remaining_handles = driver.window_handles
        driver.switch_to.window(remaining_handles[-1])
    else:
        driver.quit()
        sys.exit()
        
def numtabs(_):
    messages.append(str(len(driver.window_handles)))

def exit_command(_):
    messages.append("Exiting the program.")
    driver.quit()
    sys.exit()

def toggle_headless(_):
    global headless_mode, driver
    headless_mode = not headless_mode
    messages.append(f"Headless mode {'enabled' if headless_mode else 'disabled'}.")
    
    open_tabs = []
    
    for tab in driver.window_handles:
        driver.switch_to.window(tab)
        open_tabs.append(driver.current_url)
    
    driver.quit()
    chrome_options = selenium.webdriver.chrome.options.Options()
    if headless_mode:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)\
        
    for url in open_tabs:
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(url)
        
    driver.switch_to.window(driver.window_handles[0])
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    
def show_tabs():
    global current_search_index, begin, end
    x = os.get_terminal_size().columns
    spacing = x
    
    for i in range(0, x):
        print("-", end="")
    print("\n")
    
    listotabs = []
    current_tab = driver.current_window_handle
    for tab in driver.window_handles:
        driver.switch_to.window(tab)
        text = driver.current_url
        text = text.replace("https://", "")
        title = driver.title
        title = title.strip()
        title = title[:10]
        if title == "Google":
            text = "CLI Search"
        text = text[:15]
        spacing = spacing - len(text) - 7
        if text != "":
            listotabs.append((tab, title))
    
    spacing = spacing // (len(listotabs)+1)

    for tab, text in listotabs:
        for i in range(0, int(spacing)):
            print(" ", end="")
        print("| ", end="")
        if tab == current_tab:
            print("\033[94m" + text + "\033[0m", end="...") # Blueeeeeee
        else:
            print(text, end="...")
        print(" |", end="")
    
    print("\n")

    for i in range(0, x):
        print("-", end="")
    print("\n")
    
    driver.switch_to.window(current_tab) 
    
    show_search_results(begin, end)
    
def insert_paragraph_breaks(text, min_chars=250, max_chars=350):
    paragraphs = []
    start = 0
    n = len(text)
    while start < n:
        target = random.randint(min_chars, max_chars)
        if start + target >= n:
            paragraphs.append(text[start:].strip())
            break
        
        break_index = text.find(".", start + target)
        
        if break_index == -1:
            paragraphs.append(text[start:].strip())
            break
        else:
            paragraphs.append(text[start:break_index+1].strip())
            start = break_index + 1
            
    return "\n\n".join(paragraphs)
    

    
def show_search_results(start=1, end=3):
    global current_search_index
    
    if "search" in driver.current_url:
        current_handle = driver.current_window_handle
        title = driver.title
        title = title.strip()
        title = title.replace(" - Google Search", "")
        try:
            listtoprint = google_search(title)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                messages.append("Too many requests. Please try again later.")
                messages.append("If this issue continues try to switch to a different wifi network, or use personal data/hotspot")
                return
            else:
                raise
        
        for i in range(start, min(end, len(listtoprint))):
            result = listtoprint[i]
            if i == current_search_index:
                print(f"\033[94m{i+1}. {result[1]}\033[0m")
                print(f"\033[94mURL: {result[0]}\033[0m")
                print(f"\033[94mDescription: {result[2]}\033[0m")
            else:
                print(f"{i+1}. {result[1]}")
                print(f"URL: {result[0]}")
                print(f"Description: {result[2]}")
            print("\n")
            
    elif "google.com" in driver.current_url:
        try:
            with open("visuals/googlesearch.txt", "r") as file:
                content = file.read()
                lines = content.split('\n')
                for line in lines:
                    print(line.center(os.get_terminal_size().columns))
        except FileNotFoundError:
            print("googlesearch.txt not found.".center(os.get_terminal_size().columns))
        try:
            with open("visuals/searchchart.txt", "r") as file:
                content = file.read()
                lines = content.split('\n')
                for line in lines:
                    print(line.center(os.get_terminal_size().columns))
        except FileNotFoundError:
            print("searchchart.txt not found.".center(os.get_terminal_size().columns))
            
    else:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        main_content = soup.find('main')
        if not main_content:
            main_content = soup.body

        paragraphs = main_content.find_all('p')
        if paragraphs:
            raw_text = "\n\n".join(p.get_text(separator=' ', strip=True) for p in paragraphs)
        else:
            raw_text = main_content.get_text(separator='\n', strip=True)
        
        raw_text = re.sub(r'\s+', ' ', raw_text)
        
        if raw_text == "" or raw_text == " " or raw_text == "\n":
            spans = main_content.find_all('span')
            if spans:
                raw_text = "\n\n".join(span.get_text(separator=' ', strip=True) for span in spans)
            else:
                raw_text = main_content.get_text(separator='\n', strip=True)
        
        raw_text = re.sub(r'\s+', ' ', raw_text)
        
        formatted_text = insert_paragraph_breaks(raw_text)
        try:
            terminal_width = os.get_terminal_size().columns
        except OSError:
            terminal_width = 80

        paragraphs = formatted_text.split("\n\n")
        wrapped_paragraphs = [textwrap.fill(p, width=terminal_width) for p in paragraphs]
        final_text = "\n\n".join(wrapped_paragraphs)
        
        print(final_text)

bookmarks = []

def rm_bookmark(bookmark):
    if bookmark == None or bookmark == "" or not bookmark.isdigit():
        messages.append("Please enter a bookmark number.")
        return
    bookmark = int(bookmark)
    if bookmark > len(bookmarks):
        messages.append("Invalid bookmark number.")
        return
    bookmarks.pop(bookmark-1)
    messages.append("Bookmark removed.")

def refresh(_):
    driver.refresh()
    messages.append("Page refreshed.")

def bookmark(_):
    current_url = driver.current_url
    bookmarks.append(current_url)
    messages.append(f"Bookmarked: {current_url}")

def show_bookmarks(_):
    if bookmarks:
        messages.append("Bookmarks:")
        for i, bookmark in enumerate(bookmarks, start=1):
            messages.append(f"{i}. {bookmark}")
    else:
        messages.append("No bookmarks saved.")
        
def go_to_bookmark(bookmark):
    if bookmark == None or bookmark == "" or not bookmark.isdigit():
        messages.append("Please enter a bookmark number.")
        return
    bookmark = int(bookmark)
    if bookmark > len(bookmarks):
        messages.append("Invalid bookmark number.")
        return
    driver.get(bookmarks[bookmark-1])

def clear_history(_):
    driver.delete_all_cookies()
    messages.append("Browsing history cleared.")

commands = {
    "help": (help_command, "Displays the list of commands."),
    "exit": (exit_command, "Exits the program."),
    "new": (new_tab, "Opens a new tab."),
    "close": (close_tab, "Closes the current tab."),
    "back": (goback, "Goes back one page."),
    "forward": (goforward, "Goes forward one page."),
    "search": (search, "Searches for a query, needs a second input."),
    "switch": (switch_tab, "Switches to a tab, needs a second input."),
    "tabs": (numtabs, "Displays the number of tabs open."),
    "up": (up, "Moves up the search results."),
    "down": (down, "Moves down the search results."),
    "next": (next_page, "Moves to the next page of search results."),
    "prev": (previous_page, "Moves to the previous page of search results."),
    "open": (enter_command, "Enters the current search result."),
    "head": (toggle_headless, "Toggles headless mode on and off."),
    "prod": (productivity, "Toggles productivity mode on and off."),
    "refresh": (refresh, "Refreshes the current page."),
    "bookmark": (bookmark, "Saves the current URL to bookmarks."),
    "bookmarks": (show_bookmarks, "Displays the list of bookmarks."),
    "clearhistory": (clear_history, "Clears the browsing history."),
    "goto": (go_to_bookmark, "Goes to a bookmarked URL, needs a second input."),
    "rmbookmark": (rm_bookmark, "Removes a bookmark, needs a second input.")
}

# Configure Chrome options
chrome_options = selenium.webdriver.chrome.options.Options()
chrome_options.add_argument("--headless") # Headless mode on by default, so no seeing :(
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get("https://www.google.com/")
os.system('cls' if os.name == 'nt' else 'clear')
show_tabs()
current_tab = driver.current_window_handle

while True:
    inputy = input("Enter command: ").lower()
    inputy = inputy.strip()
    inputy = inputy.split(" ")
    firstinput = inputy[0]
    if len(inputy) > 1:
        secondinput = None
        for i in range(1, len(inputy)):
            if secondinput == None:
                secondinput = inputy[i]
            else:
                secondinput = secondinput + " " + inputy[i]
    else:
        secondinput = None
        
    os.system('cls' if os.name == 'nt' else 'clear')
    
    if firstinput in commands:
        commands[firstinput][0](secondinput)
        show_tabs()
        for message in messages:
            print(message)
        print("\n")
        messages.clear()
        print("Command: " + firstinput)
    else:
        show_tabs()
        print("Command: " + firstinput)
        print("Unknown command. Type 'help' for a list of commands.\n")
        
    current_tab = driver.current_window_handle
