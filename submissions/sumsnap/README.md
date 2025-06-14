# 📝 sumsnap

**sumsnap** is a command-line tool that uses AI to generate concise or detailed summaries of text-based files and code projects.

> **Summarize anything, beautifully.**

---

## ✨ Features

- 📄 **Text-based summarization:** Summarize individual source code files, text documents, or entire project directories.
- 🧠 **AI-powered summaries:** Uses your preferred LLM (e.g., OpenAI, Google Gemini) via a configurable API endpoint.
- 🎨 **Beautiful CLI output:** Leverages [Rich](https://github.com/Textualize/rich) for styled summaries directly in your terminal.
- 💾 **Save summaries:** Optionally write summaries to Markdown files.
- 🔄 **Update READMEs:** Directly format and update existing `README.md` files with new summaries.
- ⚙️ **Customizable:** Configure API keys, endpoints, and AI models.
- 🙈 **Respects `.gitignore`:** Automatically excludes files and folders listed in your project's `.gitignore` files when summarizing directories.
- ➕ **Flexible Exclusions:** Manually exclude specific files or folders using the `--exclude` option.

---

## 🚀 Quick Start

### 1. Install sumsnap

#### Linux

```bash
curl -fsSL https://raw.githubusercontent.com/frinshhd/sumsnap/main/install/install-linux.sh | bash
```

#### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/frinshhd/sumsnap/main/install/install-windows.ps1 | iex
```

#### macOS

```bash
curl -fsSL https://raw.githubusercontent.com/frinshhd/sumsnap/main/install/install-macos.sh | bash
```

#### Install Pre-release

To install the latest pre-release version:

**Linux:**

```bash
curl -fsSL https://raw.githubusercontent.com/frinshhd/sumsnap/main/install/install-linux.sh | bash -s -- --prerelease
```

**Windows (PowerShell):**

```powershell
$env:SUMSNAP_PRERELEASE="1"; irm https://raw.githubusercontent.com/frinshhd/sumsnap/main/install/install-windows.ps1 | iex
```

**macOS:**

```bash
curl -fsSL https://raw.githubusercontent.com/frinshhd/sumsnap/main/install/install-macos.sh | bash -s -- --prerelease
```

---

### 2. Configure your API Credentials

Run the interactive setup command and follow the prompts:

```bash
sumsnap setup
```

This will guide you through setting your API endpoint, API key, and preferred AI model. These settings are stored in a local configuration file.

You can also set or update individual configuration values at any time:

```bash
sumsnap set-api-endpoint https://your-api-endpoint.com/v1
sumsnap set-api-key YOUR_API_KEY
sumsnap set-ai-model your-model-name
```

---

### 3. Summarize Files or Projects

The primary command is `sumsnap summary`:

```bash
sumsnap summary [OPTIONS] PATH
```

Where `PATH` is the path to a file or a project directory.

**Examples:**

Summarize a single file:

```bash
sumsnap summary my_script.py
```

Summarize an entire project folder:

```bash
sumsnap summary ./my_project_directory
```

Get a detailed summary and save it to a file:

```bash
sumsnap summary --detailed --save-to-file ./my_project_directory
```

Update an existing `README.md` in a project with a new summary:

```bash
sumsnap summary --update-readme ./my_project_directory/README.md ./my_project_directory
```

---

## ⚙️ Configuration Details

Your `sumsnap` configuration, including API keys and model settings, is stored in a user-specific `config.ini` file.

**Typical locations:**

- **Windows:** `C:\Users\<YourUsername>\AppData\Roaming\sumsnap\config.ini`
- **Linux/macOS:** `~/.config/sumsnap/config.ini`

**CLI commands for configuration:**

- `sumsnap setup`: Interactive setup for all required values.
- `sumsnap set-api-key <KEY>`: Sets your API key.
- `sumsnap set-api-endpoint <URL>`: Sets the API endpoint (OpenAI compatible).
- `sumsnap set-ai-model <MODEL_NAME>`: Sets the AI model to use.

---

## COMMAND: `sumsnap summary`

Generates a summary for the specified file or project directory.

### Key Options:

- `PATH`: (Required) The path to the file or project directory you want to summarize.
- `--detailed`: Generate a longer, more comprehensive summary.
- `--save-to-file`: Save the generated summary to a Markdown file.
  - For directories, saves to `project_summary.md` in the target directory.
  - For files, saves to `[original_filename]_summary.md`.
- `--format-readme`: Format the summary output as a professional `README.md` file (useful with `--save-to-file` or for console output).
- `--update-readme README_PATH`: Update an existing `README.md` file at the specified `README_PATH` with the generated summary. This option implies `--format-readme`.
- `--exclude TEXT`: A comma-separated list of file or folder names to exclude from the summary (e.g., `tests,docs,config.py`). For subfolders, use relative paths like `src/tests`.
- `--model TEXT`: Specify the AI model to use for this summarization, overriding the globally configured model.

### Excluding Files and Folders:

`sumsnap` offers two ways to exclude content:

1.  **`.gitignore`:** When summarizing a directory, `sumsnap` automatically respects the rules found in any `.gitignore` files within that directory and its subdirectories.
2.  **`--exclude` option:** Manually specify a comma-separated list of file or folder names.
    - Example: `sumsnap summary ./my_project --exclude node_modules,.env,temp_files`
    - To exclude subfolders: `sumsnap summary ./my_project --exclude src/generated,build_output`

### Full Options List:

```bash
Usage: sumsnap summary [OPTIONS] PATH

Options:
  PATH                        Path to a file or project directory to summarize. [required]
  --save-to-file              Save the generated summary to a markdown file.
  --model TEXT                Specify the model to use for summarization. Overrides the AI_MODEL environment variable.
  --detailed                  Generate a longer, more detailed and in-depth summary.
  --format-readme             Format the summary as a professional README.md file.
  --update-readme README_PATH Update an existing README.md file at README_PATH with the summary.
  --exclude TEXT              Comma-separated list of files or folders to exclude.
  --debug                     Enable debug output. [hidden]
  --help                      Show this message and exit.
```

---

## ℹ️ Version

To check the installed `sumsnap` version:

```bash
sumsnap --version
```
