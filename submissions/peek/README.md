*Adapted version of https://github.com/hs7t/peek/*

# peek!

![A terminal screenshot of peek](https://imgur.com/22Dtq9h.png)

Peek is a tiny CLI tool that quickly gives you a preview of all human-readable
text files in a directory. Features:
- smart file detection and support for most non-binary files, even those in obscure formats or 
without a file extension 
- little to no setup and a small, self-contained package
- syntax-highlighted previews for code, markup and more 
- fuzzy, case-insensitive search and glob pattern-based filtering
- multiple sorting options
- support for multiple platforms


# Getting peek

## Downloading a binary

Grab yourself a binary from the [Releases](https://github.com/hs7t/peek/releases/) 
tab on my repo, or the binaries.zip file in this folder.. They're available for three 
platforms:

- for Windows: `peek-windows-[x86_64 or arm64].exe`
- for macOS: `peek-macos-[arm64 or x86_64]`
- for Linux (x86-64 / arm64): `peek-linux-[x86_64 or arm64]`

### Linux and Mac

Before you can use peek on Linux or your Mac, you have to mark the
binary as an executable. From your terminal, run this command:
```bash
chmod +x peek-linux     # or peek-macos
```

## Optional setup: Adding peek to your PATH

Registering peek on your PATH makes it easy to preview from anywhere. To
do so, follow these steps:

1. Move the peek binary into a stable folder.
2. Run a command appropriate for your OS:
    - macOS (zsh):
        ```bash
        export PATH="$PATH:/path/to/folder"
        source ~/.zshrc
        ```
    - Linux (bash):
        ```bash
        export PATH="$PATH:/path/to/folder"
        source ~/.bashrc    # or ~/.profile, depending on your shell
        ```
    - Windows (PowerShell)
        ```powershell
        [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\path\to\folder", "User")
        ```
> [!TIP]
> You should rename the binary to `peek` (or `peek.exe` on Windows)
  if you want to use it by just typing `peek`.
# Usage

## Basic usage

Run peek in any directory to see a preview of all text files:

```bash
peek
```

This will show you a neat table with the filenames and first 5 lines
of each file, sorted by most recently modified.

### Looking for files

Search for and preview files with names similar to your query:

```bash
peek myfile
peek main.js
peek index
peek reamde.md      # you can make typos!
```

Peek uses fuzzy matching, so you don't need to type the exact filename.
It will find files that closely match your search term.

### Getting help  

Get a list of all commands and options:

```bash
# print help message
peek --help
```

## Options

### Selecting a directory
For simplicity's sake, peek only reads the text files in a given folder, 
excluding everything in subdirectories. To select a directory different to 
your current one:

```bash
peek -d /path/to/directory
peek --directory cats/
```

### Filtering files

You can choose to filter files using glob-style patterns, like so:

```bash
# only show .py files
peek -p "*.py"

# only show files containing .svelte.
peek --pattern "*.svelte.*"

```

### Sorting options

You can sort files by their size, names or recency:

```bash
# sort by file size (largest first)
peek -s size
peek --sorting size

# sort alphabetically
peek -s alphabetic
peek --sorting alphabetic

# sort by recency (most recently modified first) (default)
peek -s recency
peek --sorting recency
```

### Display options

There's various display options you can try to improve your
experience:

```bash
# show more lines per file (50 instead of 5)
peek -v
peek --verbose

# show line numbers in previews when syntax highlighting is on
peek -ln
peek --linenumbers

# disable syntax highlighting (faster)
peek -nhi
peek --no-highlighting

# low accuracy mode (faster, less precise file detection)
peek -la
peek --low-accuracy
```

### Debugging
If you want to troubleshoot peek, you can enable debug mode, which
shows you more information when errors occur:

```bash
peek -db
peek --debug-mode
```

# Contributing
Found a bug? Want a new feature? Open an issue through the [Issues](https://github.com/hs7t/peek/issues) tab.

# Credits

## Libraries
- [rich](https://github.com/Textualize/rich/), a fantastic library for terminal
formatting

- [TheFuzz](https://github.com/seatgeek/thefuzz), insanely easy Levenshtein Distance-based
fuzzy string matching

- [charset-normalizer](https://github.com/jawah/charset_normalizer), a universal character
encoding library

## Misc
- [@sindresorhus](https://github.com/sindresorhus/)'s 
[text-extensions](https://github.com/sindresorhus/text-extensions) and
 [binary-extensions](https://github.com/sindresorhus/binary-extensions)

## LLMs
LLMs (Claude Sonnet 4, GPT-4o, and GPT 4.1) were used for research, tooling setup
and debugging during development. This included library and architecture suggestions
as well as feedback on mistakes and potential improvements (and also setting up GitHub Actions
because it is my nemesis). All peek code was written by me.
