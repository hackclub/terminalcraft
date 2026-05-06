# Flashcard CLI App

A fun and interactive flashcard CLI application built with [Textual](https://textual.textualize.io/). This tool scans your current directory for Python code, extracts function definitions with parameters, and quizzes you on them by randomly selecting a flashcard.

## Features

- **Code Scanning:** Recursively searches for Python files (excluding common folders like `venv`, `.git`, etc.) and extracts functions with parameters.
- **Interactive Quiz:** Randomly selects a function and prompts you to input its parameters.
- **Instant Feedback:** Compares your answer to the actual parameters and shows if you are correct.
- **Clean, Modern UI:** Powered by Textual, offering a responsive and elegant terminal interface.

## Demo 

### Terminal
Run the flashcard app in your terminal:

```bash
python LSFLASH.py
```

## Contributing
Contributions, issues, and feature requests are welcome!

**Adding Support for Other Languages:** <br>
Currently, the tool extracts Python function definitions. If you have experience with language-specific parsing libraries or regular expressions for other programming languages (e.g., JavaScript, Java, etc.), feel free to extend the code extraction functionality.
<br>
**General Improvements:**<br>
Any improvements, bug fixes, or additional features are welcome.
