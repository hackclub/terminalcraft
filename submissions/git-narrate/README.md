# Git-Narrate User Guide 📖

Welcome to Git-Narrate! This guide will help you get started with turning your project's history into an exciting story.

## What is Git-Narrate?

Imagine your project is like a movie, and every change you make is a scene. Git-Narrate is like a movie director that watches all these scenes and creates a story about how your project was made. It looks at your project's `git` history (the log of all your changes) and writes a narrative about it.

## Key Features

*   **Comprehensive Repository Analysis**: Git-Narrate delves into your Git repository to extract detailed information about commits, branches, tags, and contributors.
*   **AI-Powered Storytelling**: Leverage the power of AI to transform raw Git data into a rich, engaging, and accurate narrative of your project's development journey.
*   **Flexible Output Formats**: Generate your project's story in Markdown, HTML, or plain text, suitable for various uses like documentation, web display, or simple readability.
*   **Visual Insights**: Create insightful visualizations, including a commit activity timeline and a contributor activity chart, to better understand your project's evolution and team contributions.
*   **Interactive Command-Line Interface**: A user-friendly CLI guides you through the process with clear prompts for repository path, output preferences, and visualization options.

## Getting Started

### 1. Installation

To use Git-Narrate, you first need to install it on your computer. Open your terminal or command prompt and type the following command:

```bash
pip install git-narrate
```

This will download and install Git-Narrate so you can use it from anywhere on your computer.

### 2. Running Git-Narrate

Once installed, you can run Git-Narrate on any of your projects that use `git`.

1.  **Navigate to your project folder:**
    Open your terminal and go to the folder of the project you want to analyze. For example:
    ```bash
    cd /path/to/your/project
    ```

2.  **Run the command:**
    Now, simply run the `git-narrate` command:
    ```bash
    git-narrate 
    ```
    The application will then guide you through the process by asking for the following inputs:
    *   **Path to your Git repository**: You can enter the path to your repository (e.g., `/path/to/your/project`) or simply press Enter to use the current directory (`.`).
    *   **Output format**: Choose between Markdown, HTML, or plain text for your story.
    *   **Output file path**: Specify where you want to save the generated story file.
    *   **Generate visualization charts**: Confirm if you want to create `timeline.png` and `contributors.png` charts.

    After you provide these inputs, Git-Narrate will generate the story and any requested visualizations.

## Fun Things You Can Do

Git-Narrate will prompt you for your preferences, allowing you to:

*   **Choose Output Format**: Select `html` to generate a story that looks like a webpage (e.g., `git_story.html`).
*   **Generate Visualizations**: Opt to create `timeline.png` (commit activity over time) and `contributors.png` (contributor activity) charts.

 
## For Developers: A Quick Look Under the Hood

If you're a developer and want to contribute to Git-Narrate, here's a quick overview of how it works:

*   **`analyzer.py`**: This is the heart of the tool. It uses `GitPython` to read the `.git` folder and extract all the data about commits, branches, tags, and contributors.
*   **`narrator.py`**: This module takes the data from the analyzer and turns it into a story. It has different functions to create Markdown, HTML, or plain text stories.
*   **`ai_narrator.py`**: This module sends the project data to the Z.ai API and gets back a more detailed story.
*   **`visualizer.py`**: This module uses `matplotlib` to create the timeline and contributor charts.
*   **`cli.py`**: This file defines the command-line interface using `click`, so you can run `git-narrate` with different options.

### Contributing

We welcome contributions! If you want to help make Git-Narrate even better, please check out our [Contributing Guide](https://github.com/000xs/Git-Narrate/blob/main/CONTRIBUTING.md).

### License

Git-Narrate is licensed under the MIT License. You can find more details in the [LICENSE](https://github.com/000xs/Git-Narrate/blob/main/LICENSE) file.
