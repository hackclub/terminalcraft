

# BrokeLink

A powerful CLI tool to scan Markdown and HTML files for broken links, missing images, and invalid references.

## Features

- ✅ **Broken local links** - Find `[text](broken-link.md)` that don't exist
- ✅ **Dead image references** - Detect `![alt](img/notfound.png)` pointing to missing files  
- ✅ **Outdated internal references** - Check heading anchors and fragments
- 🎨 **Colored output** - Easy-to-read results with syntax highlighting
- 📄 **Multiple formats** - Support for Markdown (`.md`) and HTML (`.html/.htm`)
- 🔧 **Flexible scanning** - Include/exclude patterns, recursive directory scanning
- 📊 **JSON output** - Machine-readable results for CI/CD integration

## Installation

### From PyPI (when published)
```bash
pip install brokelink
```

### From Source
```bash
git clone https://github.com/000xs/brokelink.git
cd brokelink
pip install -e .

```
### verify installation
```
brokelink
```

## Quick Start

```bash
# Scan current directory
brokelink

# Scan specific directory
brokelink ./docs

# Scan with verbose output
brokelink -v

# Check only Markdown files
brokelink --include="*.md"

# Output as JSON
brokelink --format=json

# Include anchor checking (experimental)
brokelink --check-anchors
```

## Usage

```
Usage: brokelink [OPTIONS] [PATH]

  🔗 BrokeLink - Scan for broken links in Markdown and HTML files.

Options:
  -i, --include TEXT      File patterns to include (default: *.md *.html)
  -e, --exclude TEXT      File patterns to exclude
  -img, --check-images    Check image references (default: enabled)
  -a, --check-anchors     Check heading anchors (experimental)
  -v, --verbose           Verbose output
  -q, --quiet             Only show errors
  -f, --format [text|json] Output format
  --help                  Show this message and exit.
```

## Examples

### Basic Usage
```bash
# Scan all .md and .html files in current directory
brokelink

# Scan specific file
brokelink README.md

# Scan docs folder recursively  
brokelink ./docs
```

### Advanced Filtering
```bash
# Only check Markdown files
brokelink --include="*.md"

# Exclude certain directories
brokelink --exclude="node_modules/*" --exclude="build/*"

# Skip image checking
brokelink --no-check-images
```

### CI/CD Integration
```bash
# JSON output for parsing
brokelink --format=json --quiet > broken-links.json

# Exit code 1 if broken links found (perfect for CI)
brokelink || echo "Broken links detected!"
```

## Output Example

```
🔗 BrokeLink v1.0.0 - Scanning for broken links...

💥 Found 3 broken link(s) in 2 file(s):

📄 docs/README.md:
  🔗 Missing files (2):
    Line 15: ./nonexistent.md ('Documentation Link')
    Line 23: ../missing-guide.md ('Setup Guide')
  🖼️  Missing images (1):
    Line 8: ./images/logo.png ('BrokeLink Logo')

📄 index.html:
  ⚓ Invalid anchors (1):
    Line 42: #missing-section ('Jump to Section')
```

## Development

### Setup Development Environment
```bash
git clone https://github.com/000xs/brokelink.git
cd brokelink
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### Running Tests
```bash
python -m pytest tests/
```

### Project Structure
```
brokelink/
├── brokelink/              # Main package
│   ├── __init__.py
│   ├── cli.py              # CLI interface
│   ├── parser.py           # Link extraction
│   └── utils.py            # Link checking & reporting
├── demo/                   # Sample files for testing
├── tests/                  # Test suite
├── README.md
├── LICENSE
└── pyproject.toml          # Modern Python packaging
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

- [ ] External URL checking (with timeout/retry)
- [ ] Whitelist/blacklist for URLs
- [ ] Integration with popular static site generators
- [ ] Performance optimizations for large repositories
- [ ] GitHub Actions integration
- [ ] VS Code extension

---

Made with ❤️ for documentation maintainers everywhere!"# brokelink" 
