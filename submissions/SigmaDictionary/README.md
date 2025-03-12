# Sigma Dictionary

A minimalist terminal-based dictionary application built with Python and Textual that allows you to look up word definitions with ease.

## Features

- 📚 **Word Definitions**: Look up comprehensive definitions, examples, and phonetics
- 📜 **Search History**: Access your previous searches with a simple keystroke
- 💾 **Caching**: Faster lookups with built-in caching mechanism
- 🌈 **Beautiful UI**: Modern, clean interface with a dark theme

## Installation

### Prerequisites
- Python 3.7+
- UV (Python package installer)

## Usage

1. Clone this repository:
    ```bash
    git clone https://github.com/shubhisroking/SigmaDictionary.git
    cd SigmaDictionary
    ```

2. Run the application:
    ```bash
    uv run main.py
    ```

### Search for a word

1. Enter a word in the search input field
2. Press Enter or click the "GO" button
3. View the word's definition, phonetics, examples, and related words

## Key Bindings

The application provides the following keyboard shortcuts:

| Key | Description |
|-----|-------------|
| F1 | Show search history |
| F2 | Clear cache |
| Ctrl+Q | Quit the application |

## Technical Details

- Uses the [Free Dictionary API](https://dictionaryapi.dev/) to fetch word definitions
- Implements local caching to improve performance and reduce API calls
- Maintains search history for quick access to previous lookups
- Built with [Textual](https://textual.textualize.io/), a modern TUI (Text User Interface) framework for Python

## Data Storage

By default the application stores the following data locally:

- Search history (up to 50 words)
- Definition cache (up to 100 words)

These are stored in JSON format in the `.sigmad` directory within the application folder.