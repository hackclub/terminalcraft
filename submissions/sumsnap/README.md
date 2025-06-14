# 📝 sumsnap

**sumsnap** is a simple command-line tool that uses AI to generate concise or detailed summaries of files including code, text documents, images, and PDFs.

> **Summarize anything, beautifully.**

---

## ✨ Features

- 📄 **Multi-format input:** Summarize code, text, images, and PDFs.
- 🧠 **AI-powered summaries:** Uses your preferred LLM (e.g., OpenAI) via API.
- 🎨 **Beautiful CLI output:** Leverages [Rich](https://github.com/Textualize/rich) for styled summaries.
- 💾 **Save summaries:** Optionally write summaries to Markdown files.
- 🔄 **Update READMEs:** Directly format and update existing `README.md` files with new summaries.

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

### Install prerelease

#### Linux (latest pre-release)

```bash
curl -fsSL https://raw.githubusercontent.com/frinshhd/sumsnap/main/install/install-linux.sh | bash -s -- --prerelease
```

#### Windows (PowerShell, latest pre-release)

```powershell
$env:SUMSNAP_PRERELEASE="1"; irm https://raw.githubusercontent.com/frinshhd/sumsnap/main/install/install-windows.ps1 | iex
```

---

### 2. Configure your API credentials

Run the interactive setup command and follow the prompts:

```bash
sumsnap setup
```

You can also set or update individual values at any time:

```bash
sumsnap set-api-endpoint https://your-endpoint
sumsnap set-api-key your_api_key
sumsnap set-ai-model your_model_name
```

---

### 3. View the current version

To quickly check the installed `sumsnap` version:

```bash
sumsnap --version
```

(e.g., displays `v0.0.1`)

---

### 4. Summarize files or projects

Run sumsnap from the CLI:

```bash
sumsnap summary [OPTIONS] PATH
```

**Examples:**

Summarize a file:

```bash
sumsnap summary my_code.py
```

Summarize a whole project folder:

```bash
sumsnap summary ./my_project
```

#### Exclude files or folders

You can exclude files or folders from the summary using the `--exclude` option (comma-separated):

```bash
sumsnap summary ./my_project --exclude tests,docs,config.py
```

To exclude subfolders, use their relative paths:

```bash
sumsnap summary ./my_project --exclude src/tests,src/data
```

#### Common options

- `--detailed` for longer, more comprehensive summaries.
- `--save-to-file` to write the summary as a Markdown file.
- `--format-readme` to format the summary as a professional `README.md` file (output to console or file).
- `--update-readme` to directly update an existing `README.md` with the new summary.
- `--exclude` to skip specific files or folders (comma-separated).

**Example:**

```bash
sumsnap summary --detailed --save-to-file --exclude tests,docs,config.py my_code.py
```

#### Output Naming Conventions

When using `--save-to-file`:

- For directories, the summary will be saved to `project_summary.md` in the current working directory.
- For single files, the summary will be saved to `[original_filename]_summary.md` (e.g., `my_code_summary.md`).

When using `--update-readme`:

- `sumsnap` will attempt to locate and update an existing `README.md` file in the target directory (or parent directories for single files). This option also formats the summary as a `README.md`.

**All options for `sumsnap summary`:**

```bash
sumsnap summary [OPTIONS] PATH

Options:
  --save-to-file      Save the generated summary to a markdown file.
  --model TEXT        Specify the model to use for summarization. Overrides the AI_MODEL environment variable.
  --detailed          Generate a longer, more detailed and in-depth summary.
  --format-readme     Format the summary as a professional README.md file.
  --update-readme     Format the summary as a README.md and update an existing README.md file directly.
  --exclude TEXT      Comma-separated list of files or folders to exclude from the summary.
```

---

## ⚙️ Configuration

Your `sumsnap` configuration, including API keys and model settings, is stored in a user-specific `config.ini` file. This file is typically located at:

- **Windows:** `C:\Users\<YourUsername>\AppData\Roaming\sumsnap\config.ini`
- **Linux:** `~/.config/sumsnap/config.ini`

You can set these values using the CLI commands:

- `sumsnap set-api-key` – Your API key for the chosen LLM provider.
- `sumsnap set-api-endpoint` – The API endpoint using OpenAI's format.
- `sumsnap set-ai-model` – The model to use.

Alternatively, use the interactive `sumsnap setup` command to set all required configuration values at once.
