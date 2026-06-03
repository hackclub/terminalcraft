# Flashcard CLI - Your Terminal-Based Learning Companion

Flashcard CLI is a powerful and versatile command-line tool designed to help you learn and memorize information effectively using flashcards. Whether you're a student, a professional, or simply someone who enjoys learning, Flashcard CLI provides a convenient and engaging way to study and review your knowledge.
![alt text](flascard-cli-image.jpg)


 
## Key Features

*   **Easy to Use:** Simple and intuitive command-line interface.
*   **Customizable:** Create and manage your own flashcard decks.
*   **Interactive Learning:** Engaging learning sessions with performance tracking.
*   **Terminal-Based:** Study without distractions, right in your terminal.

## Installation

```bash
pip install flashcard-cli
```

(Image: Screenshot of the installation process)

## Usage

### Adding Flashcards

```bash
flashcard add
```
![alt text](<Screenshot 2025-07-31 074056.png>)
This command will prompt you to enter a question and answer for your flashcard. The flashcard will be saved to `flashcards.json` by default.

 

### Starting a Learning Session

```bash
flashcard start
```
![alt text](<Screenshot 2025-07-31 100754.png>)

This command will start a learning session, presenting each flashcard in a visually appealing card-like panel. The system will wait for you to press Enter to reveal the answer, then ask if you got it right. After all flashcards, it will show a summary of your performance.

 

### Other Commands

*   `flashcard manage`: manag flascard with edit and delete.
  
![alt text](image-5.png)
 

## Configuration

 
## Troubleshooting
 Make sure that the Flashcard CLI is installed correctly and that the `flashcard` command is in your system's PATH.

## Development

To install in editable mode:

```bash
pip install -e .
```

 

## Publishing to PyPI

To publish the package to PyPI, you need to build the package and then upload it to PyPI.

### Build the Package

```bash
python -m build
```

This will create a `dist` directory with the built package.

### Upload to PyPI

```bash
twine upload dist/*
```

**Note:** You will need to have `twine` installed (`pip install twine`) and have a PyPI account.

## GitHub Workflow for PyPI Release

To automate the release process to PyPI, you can set up a GitHub workflow. See `.github/workflows/release.yml` for the workflow configuration.

**Note:**

*   You will need to configure a PyPI API token as a secret in your GitHub repository settings.

## Contributing

Contributions are welcome! Please submit a pull request with your changes.

## License

This project is licensed under the MIT License.

 