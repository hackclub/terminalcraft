import json
import pathlib
import textwrap
from functools import lru_cache
from typing import Dict, List, Any, Optional, Tuple, Union
import requests
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, ScrollableContainer
from textual.widgets import Header, Footer, Button, Input, Static, Rule


class SigmaDictionary(App):
    TITLE = "Sigma Dictionary"
    SUB_TITLE = "Look up word definitions with ease"
    API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"
    MAX_CACHE_SIZE = 100
    MAX_HISTORY_SIZE = 50

    BINDINGS = [
        Binding("f1", "history", "History"),
        Binding("f2", "clear_cache", "Clear Cache"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    ERROR_EMPTY_SEARCH = "Please enter a word to search."
    ERROR_WORD_NOT_FOUND = "'{word}' not found in the dictionary."
    ERROR_API_RESPONSE = "Error: Received status code {status_code}"
    ERROR_NETWORK = "Network error: {error}"
    ERROR_JSON_DECODE = "Error decoding the API response."
    ERROR_UNEXPECTED = "An unexpected error occurred: {error}"
    ERROR_CACHE_CLEAR = "Error clearing cache: {error}"

    HISTORY_EMPTY = "No search history available."
    CACHE_CLEARED = "Cache cleared successfully."

    CSS = """
    Screen {
        background: #121212; 
        color: #e0e0e0;
    }
    
    Header {
        dock: top; 
        background: #1e1e1e; 
        color: #ffffff; 
        text-style: bold; 
        padding: 1; 
        height: 3;
    }
    
    Footer {
        dock: bottom; 
        background: #1e1e1e; 
        color: #ffffff; 
        padding: 0; 
        height: 1;
    }
    
    .section-header {
        padding: 1 2; 
        margin: 1 0 0 0; 
        text-style: bold; 
        color: #bb86fc; 
        background: #121212; 
        border-bottom: solid #333333;
    }
    
    #search-container {
        layout: horizontal; 
        height: 3; 
        margin: 0 0 1 0; 
        background: #1e1e1e; 
        padding: 0 2;
    }
    
    #search-input {
        width: 80%; 
        margin-right: 1; 
        border: solid #333333; 
        background: #2d2d2d; 
        color: #e0e0e0;
    }
    
    #search-button {
        width: 20%; 
        background: #bb86fc; 
        color: #121212; 
        height: 3; 
        text-style: bold; 
        content-align: center middle;
    }
    
    #search-button:hover {
        background: #03dac6; 
        color: #121212;
    }
    
    #results-container {
        height: auto; 
        margin: 0; 
        background: #1e1e1e; 
        padding: 0 2;
    }
    
    .word-title {
        color: #bb86fc; 
        text-style: bold; 
        margin: 1 0; 
        text-align: center; 
        width: 100%;
    }
    
    .part-of-speech {
        color: #03dac6; 
        text-style: bold; 
        margin-top: 1;
    }
    
    .definition {
        margin: 0 0 0 1; 
        color: #e0e0e0;
    }
    
    .example {
        margin: 0 0 1 2; 
        color: #a0a0a0; 
        text-style: italic;
    }
    
    .sub-section {
        margin: 0 0 1 1; 
        color: #a0a0a0;
    }
    
    .history-title {
        color: #bb86fc; 
        text-style: bold; 
        margin: 1 0; 
        text-align: center; 
        width: 100%;
    }
    
    .history-item {
        margin: 0 0 0 1; 
        padding: 1 0; 
        color: #e0e0e0;
    }
    
    .error {
        color: #cf6679; 
        margin: 1 0; 
        padding: 1;
    }
    
    .success {
        color: #03dac6; 
        margin: 1 0; 
        padding: 1;
    }
    
    Button {
        border: none;
    }
    
    Button:hover {
        background: #03dac6; 
        color: #121212;
    }
    
    .big-button {
        width: 100%; 
        height: 3; 
        margin: 1 0; 
        background: #bb86fc; 
        color: #121212; 
        text-style: bold; 
        content-align: center middle;
    }
    
    Rule {
        color: #333333; 
        height: 1;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.history: List[str] = []
        self.cache: Dict[str, Any] = {}
        self._setup_storage()

    def _setup_storage(self) -> None:
        app_dir = pathlib.Path(__file__).parent
        self.sigmad_dir = app_dir / ".sigmad"
        self.sigmad_dir.mkdir(exist_ok=True)
        self.history_file = self.sigmad_dir / "history.json"
        self.cache_file = self.sigmad_dir / "cache.json"
        self._load_data()

    def _load_data(self) -> None:
        self._load_history()
        self._load_cache()

    def _load_history(self) -> None:
        self.history = self._load_json_file(
            self.history_file, default=[], limit=self.MAX_HISTORY_SIZE
        )

    def _load_cache(self) -> None:
        self.cache = self._load_json_file(
            self.cache_file, default={}, limit=self.MAX_CACHE_SIZE
        )

    def _load_json_file(
        self, file_path: pathlib.Path, default: Union[List, Dict], limit: int = 0
    ) -> Union[List, Dict]:
        if not file_path.exists():
            return default

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

                if isinstance(data, list) and limit > 0 and len(data) > limit:
                    return data[-limit:]

                if isinstance(data, dict) and limit > 0 and len(data) > limit:
                    return dict(list(data.items())[-limit:])

                return data
        except (json.JSONDecodeError, IOError):
            return default

    def _save_json_file(self, file_path: pathlib.Path, data: Union[List, Dict]) -> bool:
        try:
            with open(file_path, "w") as f:
                json.dump(data, f)
            return True
        except IOError as e:
            self.show_message(f"Failed to save to {file_path.name}: {e}", error=True)
            return False

    def _save_history(self) -> None:
        self._save_json_file(self.history_file, self.history)

    def _save_cache(self) -> None:
        self._save_json_file(self.cache_file, self.cache)

    def _add_to_history(self, word: str) -> None:
        if word in self.history:
            self.history.remove(word)
        self.history.append(word)
        if len(self.history) > self.MAX_HISTORY_SIZE:
            self.history = self.history[-self.MAX_HISTORY_SIZE :]
        self._save_history()

    def _add_to_cache(self, word: str, data: Dict[str, Any]) -> None:
        self.cache[word] = data
        if len(self.cache) > self.MAX_CACHE_SIZE:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self._save_cache()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Search", classes="section-header")
        with Container(id="search-container"):
            yield Input(placeholder="Enter a word...", id="search-input")
            yield Button("  GO  ", id="search-button")
        yield Static("Results", classes="section-header")
        yield ScrollableContainer(id="results-container")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "search-button":
            self.search_word()
        elif button_id == "clear-history":
            self._clear_history()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search-input":
            self.search_word()

    def _clear_history(self) -> None:
        self.history = []
        self._save_history()
        self.action_history()

    def show_message(
        self, message: str, error: bool = False, success: bool = False
    ) -> None:
        container = self.query_one("#results-container", ScrollableContainer)
        container.remove_children()

        classes = "error" if error else "success" if success else None
        container.mount(Static(message, classes=classes))

    def _search_specific_word(self, word: str) -> None:
        search_input = self.query_one("#search-input", Input)
        search_input.value = word
        self.search_word()

    @lru_cache(maxsize=5)
    def _fetch_word_data(
        self, word: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        try:
            response = requests.get(self.API_URL.format(word), timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data:
                    return data[0], None
                return None, self.ERROR_WORD_NOT_FOUND.format(word=word)
            elif response.status_code == 404:
                return None, self.ERROR_WORD_NOT_FOUND.format(word=word)
            else:
                return None, self.ERROR_API_RESPONSE.format(
                    status_code=response.status_code
                )

        except requests.exceptions.RequestException as e:
            return None, self.ERROR_NETWORK.format(error=e)
        except json.JSONDecodeError:
            return None, self.ERROR_JSON_DECODE
        except Exception as e:
            return None, self.ERROR_UNEXPECTED.format(error=e)

    def search_word(self) -> None:
        search_input = self.query_one("#search-input", Input)
        word = search_input.value.strip().lower()

        if not word:
            self.show_message(self.ERROR_EMPTY_SEARCH, error=True)
            return

        self._add_to_history(word)

        if word in self.cache:
            self.show_message(f"Found '{word}' in cache")
            self.display_definition(self.cache[word])
            return

        self.show_message(f"Searching for '{word}'...")

        data, error = self._fetch_word_data(word)

        if error:
            self.show_message(error, error=True)
            return

        if data:
            self._add_to_cache(word, data)
            self.display_definition(data)

    def display_definition(self, data: Dict[str, Any]) -> None:
        container = self.query_one("#results-container", ScrollableContainer)
        container.remove_children()

        word = data.get("word", "Unknown")
        phonetics = data.get("phonetic", "")

        container.mount(Static(f"{word.upper()}", classes="word-title"))
        if phonetics:
            safe_phonetics = self._escape_markup(phonetics)
            container.mount(Static(f"{safe_phonetics}", classes="definition"))

        container.mount(Rule())
        self._display_meanings(container, data.get("meanings", []))

    @staticmethod
    def _escape_markup(text: str) -> str:
        if not isinstance(text, str):
            return str(text)

        replacements = {
            "[": "\\[",
            "]": "\\]",
            "{": "\\{",
            "}": "\\}",
            "<": "\\<",
            ">": "\\>",
            "*": "\\*",
            "_": "\\_",
            "`": "\\`",
            "#": "\\#",
            "|": "\\|",
            "@": "\\@",
        }

        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        return text

    def _display_meanings(
        self, container: ScrollableContainer, meanings: List[Dict[str, Any]]
    ) -> None:
        for i, meaning in enumerate(meanings, 1):
            part_of_speech = meaning.get("partOfSpeech", "")
            container.mount(
                Static(f"{part_of_speech.upper()}", classes="part-of-speech")
            )
            self._display_definitions(container, meaning.get("definitions", []))
            self._display_related_words(
                container,
                synonyms=meaning.get("synonyms", []),
                antonyms=meaning.get("antonyms", []),
            )
            if i < len(meanings):
                container.mount(Rule())

    def _display_definitions(
        self, container: ScrollableContainer, definitions: List[Dict[str, Any]]
    ) -> None:
        for j, definition in enumerate(definitions, 1):
            def_text = definition.get("definition", "")
            if not def_text:
                continue

            wrapped_text = textwrap.fill(def_text, width=80)
            container.mount(Static(f"{j}. {wrapped_text}", classes="definition"))

            if example := definition.get("example"):
                safe_example = self._escape_markup(example)
                container.mount(Static(f'Example: "{safe_example}"', classes="example"))

    def _display_related_words(
        self, container: ScrollableContainer, synonyms: List[str], antonyms: List[str]
    ) -> None:
        if synonyms:
            container.mount(
                Static(
                    f"Synonyms: {', '.join(synonyms[:5])}",
                    classes="definition sub-section",
                )
            )
        if antonyms:
            container.mount(
                Static(
                    f"Antonyms: {', '.join(antonyms[:5])}",
                    classes="definition sub-section",
                )
            )

    def action_history(self) -> None:
        results = self.query_one("#results-container")
        results.remove_children()
        results.mount(Static("Search History", classes="history-title"))
        results.mount(Rule())

        if not self.history:
            results.mount(Static(self.HISTORY_EMPTY, classes="history-item"))
        else:
            for i, word in enumerate(reversed(self.history), 1):
                results.mount(Static(f"{i}. {word}", classes="history-item"))

            results.mount(Rule())
            results.mount(
                Button(
                    "Clear History",
                    variant="default",
                    id="clear-history",
                    classes="big-button",
                )
            )

    def action_clear_cache(self) -> None:
        try:
            self.cache = {}
            self._save_cache()
            self._fetch_word_data.cache_clear()
            self.show_message(self.CACHE_CLEARED, success=True)
        except Exception as e:
            self.show_message(self.ERROR_CACHE_CLEAR.format(error=e), error=True)


if __name__ == "__main__":
    app = SigmaDictionary()
    app.run()
