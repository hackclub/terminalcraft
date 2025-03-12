import json
import textwrap
from typing import Dict, List, Any

import requests
from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.widgets import Header, Footer, Button, Input, Static
from textual import events

class SigmaDictionary(App):
    """A Textual app to look up word definitions using a dictionary API."""

    TITLE = "Sigma Dictionary"
    SUB_TITLE = "Look up word definitions with ease(made for true rizzlers BTW)"
    API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"
    
    ERROR_EMPTY_SEARCH = "Please enter a word to search."
    ERROR_WORD_NOT_FOUND = "'{word}' not found in the dictionary."
    ERROR_API_RESPONSE = "Error: Received status code {status_code}"
    ERROR_NETWORK = "Network error: {error}"
    ERROR_JSON_DECODE = "Error decoding the API response."
    ERROR_UNEXPECTED = "An unexpected error occurred: {error}"
    
    HISTORY_EMPTY = "No search history available."

    CSS = """
    Screen {
        background: #1f1d2e;
    }

    Header {
        dock: top;
        background: #191724;
        color: #e0def4;
    }

    Footer {
        dock: bottom;
        background: #191724;
        color: #e0def4;
    }

    #search-container {
        layout: horizontal;
        height: 3;
        margin: 1 2;
    }

    #search-input {
        width: 80%;
        margin-right: 2;
    }

    #search-button {
        width: 20%;
    }

    #results-container {
        height: auto;
        margin: 1 2;
        background: #2a273f;
        padding: 1;
        border: solid #6e6a86;
    }

    .word-title {
        color: #9ccfd8;
        text-style: bold;
        margin-bottom: 1;
    }

    .part-of-speech {
        color: #c4a7e7;
        text-style: bold;
        margin-top: 1;
    }

    .definition {
        margin-left: 2;
    }

    .example {
        margin-left: 4;
        color: #908caa;
        text-style: italic;
    }

    .history-title {
        color: #9ccfd8;
        text-style: bold;
        margin: 1;
    }

    .history-item {
        margin-left: 2;
        color: #e0def4;
    }

    .error {
        color: #eb6f92;
    }
    """
    
    def __init__(self) -> None:
        """Initialize the dictionary app."""
        super().__init__()
        self.history: List[str] = []
        
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        
        with Container(id="search-container"):
            yield Input(placeholder="Enter a word to search...", id="search-input")
            yield Button("Search", id="search-button")
        
        yield ScrollableContainer(id="results-container")
        
        yield Footer()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "search-button":
            self.search_word()
            
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        if event.input.id == "search-input":
            self.search_word()
            
    def show_message(self, message: str, error: bool = False) -> None:
        """Display a message in the results container.
        
        Args:
            message: The message to display
            error: Whether this is an error message
        """
        container = self.query_one("#results-container", ScrollableContainer)
        container.remove_children()
        classes = "error" if error else None
        container.mount(Static(message, classes=classes))
    
    def search_word(self) -> None:
        """Search for a word using the API."""
        search_input = self.query_one("#search-input", Input)
        word = search_input.value.strip().lower()
        
        if not word:
            self.show_message(self.ERROR_EMPTY_SEARCH, error=True)
            return
        
        if word not in self.history:
            self.history.append(word)
        
        self.show_message(f"Searching for '{word}'...")
            
        try:
            response = requests.get(self.API_URL.format(word))
            
            if response.status_code == 200:
                data = response.json()[0]
                self.display_definition(data)
            elif response.status_code == 404:
                self.show_message(self.ERROR_WORD_NOT_FOUND.format(word=word), error=True)
            else:
                self.show_message(self.ERROR_API_RESPONSE.format(status_code=response.status_code), error=True)
                
        except requests.exceptions.RequestException as e:
            self.show_message(self.ERROR_NETWORK.format(error=e), error=True)
        except json.JSONDecodeError:
            self.show_message(self.ERROR_JSON_DECODE, error=True)
        except Exception as e:
            self.show_message(self.ERROR_UNEXPECTED.format(error=e), error=True)
    
    def display_definition(self, data: Dict[str, Any]) -> None:
        """Display word definition and related information.
        
        Args:
            data: Dictionary data returned from the API
        """
        container = self.query_one("#results-container", ScrollableContainer)
        container.remove_children()
        
        word = data.get("word", "Unknown")
        phonetics = data.get("phonetic", "")
        
        container.mount(Static(f"{word.upper()}", classes="word-title"))
        if phonetics:
            container.mount(Static(f"Pronunciation: {phonetics}"))
        
        self._display_meanings(container, data.get("meanings", []))
    
    def _display_meanings(self, container: ScrollableContainer, meanings: List[Dict[str, Any]]) -> None:
        """Display word meanings, definitions, examples, synonyms and antonyms.
        
        Args:
            container: The container to mount the widgets
            meanings: List of meanings from the API response
        """
        for i, meaning in enumerate(meanings, 1):
            part_of_speech = meaning.get("partOfSpeech", "")
            container.mount(Static(f"{i}. {part_of_speech.upper()}", classes="part-of-speech"))
            
            definitions = meaning.get("definitions", [])
            for j, definition in enumerate(definitions, 1):
                wrapped_text = textwrap.fill(definition.get("definition", ""), width=80)
                container.mount(Static(f"{j}. {wrapped_text}", classes="definition"))
                
                example = definition.get("example")
                if example:
                    container.mount(Static(f"Example: {example}", classes="example"))
            
            self._display_related_words(container, 
                                      synonyms=meaning.get("synonyms", []), 
                                      antonyms=meaning.get("antonyms", []))
    
    def _display_related_words(self, container: ScrollableContainer, 
                             synonyms: List[str], antonyms: List[str]) -> None:
        """Display synonyms and antonyms.
        
        Args:
            container: The container to mount the widgets
            synonyms: List of synonyms
            antonyms: List of antonyms
        """
        if synonyms:
            container.mount(Static(f"Synonyms: {', '.join(synonyms[:5])}", classes="definition"))
        
        if antonyms:
            container.mount(Static(f"Antonyms: {', '.join(antonyms[:5])}", classes="definition"))
    
    def action_show_history(self) -> None:
        """Show search history."""
        container = self.query_one("#results-container", ScrollableContainer)
        container.remove_children()
        
        container.mount(Static("Search History", classes="history-title"))
        if self.history:
            for i, word in enumerate(self.history, 1):
                container.mount(Static(f"{i}. {word}", classes="history-item"))
        else:
            container.mount(Static(self.HISTORY_EMPTY, classes="history-item"))
    
    def on_key(self, event: events.Key) -> None:
        """Handle key presses."""
        if event.key == "h" and event.ctrl:
            self.action_show_history()

if __name__ == "__main__":
    app = SigmaDictionary()
    app.run()