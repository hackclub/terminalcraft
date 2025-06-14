# 📝 sumsnap

**sumsnap** is a powerful yet simple command-line tool that uses AI to generate concise or detailed summaries of files including code, text documents, images, and PDFs.

> **Summarize anything, beautifully.**

---

## ✨ Features

- 📄 **Multi-format input:** Summarize code, text, images, and PDFs.
- 🧠 **AI-powered summaries:** Uses your preferred LLM (e.g., OpenAI) via API.
- 🎨 **Beautiful CLI output:** Leverages [Rich](https://github.com/Textualize/rich) for styled summaries.
- 💾 **Save summaries:** Optionally write summaries to Markdown files.
- ⚡ **Progress indication:** See a spinner while your summaries are generated.
- 🔒 **Secure config:** Set API keys and options securely via CLI config commands.

---

## 🚀 Quick Start

### 1. Install sumsnap

#### macOS

```bash
curl -fsSL https://raw.githubusercontent.com/frinshhd/sumsnap/main/install/install-macos.sh | bash
```

#### Linux

```bash
curl -fsSL https://raw.githubusercontent.com/frinshhd/sumsnap/main/install/install-linux.sh | bash
```

#### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/frinshhd/sumsnap/main/install/install-windows.ps1 | iex
```

### Install prerelease

#### macOS (latest pre-release)

```bash
curl -fsSL https://raw.githubusercontent.com/frinshhd/sumsnap/main/install/install-macos.sh | bash -s -- --prerelease
```

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

### 3. Summarize files or projects

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
- `--format-readme` to format the summary as a professional README.md file.
- `--exclude` to skip specific files or folders (comma-separated).

**Example:**

```bash
sumsnap summary --detailed --save-to-file --exclude tests,docs,config.py my_code.py
```

**All options:**

```bash
sumsnap summary [OPTIONS] PATH

Options:
  --save-to-file      Save the generated summary to a markdown file.
  --model TEXT        Specify the model to use for summarization. Overrides the AI_MODEL environment variable.
  --detailed          Generate a longer, more detailed and in-depth summary.
  --format-readme     Format the summary as a professional README.md file.
  --exclude TEXT      Comma-separated list of files or folders to exclude from the summary.
```

---

## ⚙️ Configuration

Set these values using the CLI commands:

- `set-api-key` – Your API key for the chosen LLM provider.
- `set-api-endpoint` – The API endpoint using OpenAI's format.
- `set-ai-model` – The model to use.

Or use the interactive `setup` command to set all at once.

Your configuration is stored in a user-specific config file (e.g., on Windows: `C:\Users\<YourUsername>\AppData\Roaming\sumsnap\config.ini`).