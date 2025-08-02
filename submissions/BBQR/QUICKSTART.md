# 🔥 BBQR Quick Start Guide 🔥

## Installation

1. **Use pip to install bbqr**
   ```bash
   pip install bbqr
   ```

## Development Installation

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Ready to grill!** Run BBQR directly:
   ```bash
   python bbqr.py
   ```

## Basic Usage

### Command Line Options

```bash
# Generate QR from URL
python bbqr.py --url "https://github.com"

# Generate QR from text
python bbqr.py --text "Hello World!"

# Generate QR from image (converts to base64)
python bbqr.py --image photo.jpg

# Generate QR from clipboard content
python bbqr.py --clipboard

# Generate WiFi QR code (interactive menu)
python bbqr.py --wifi

# Upload file and generate download QR
python bbqr.py --file document.pdf

# Read/decode QR code from image
python bbqr.py --read qrcode.png

# Custom size and auto-save
python bbqr.py --text "Hello" --size 15 --save

# Logo embedding!
python bbqr.py --url "https://mycompany.com" --logo company_logo.png
python bbqr.py --wifi --logo brand.jpg --logo-size 25
python bbqr.py --text "Hello World!" --logo logo.png --save
```

### Interactive Mode

Simply run without arguments for the BBQ-themed menu:

```bash
python bbqr.py
```

Menu options:

1. 🌐 URL
2. 📝 Text
3. 🖼️ Image
4. 📋 Clipboard
5. 🛜 WiFi
6. ⬆️ Upload File
7. 👀 Watch File
8. 📂 Multi QR from File
9. 🔍 Read QR Code

### Piped Input

```bash
# From command output
echo "Secret data" | python bbqr.py
date | python bbqr.py
curl -s https://api.github.com/users/octocat | python bbqr.py

# Save piped content
echo "Meeting at 3PM" | python bbqr.py --save
```

### Logo Embedding

Add custom logos to your QR codes:

```bash
# Add logo via command line (auto-detects logo size)
python bbqr.py --text "Hello!" --logo my_logo.png

# Specify logo size (10-30% of QR code)
python bbqr.py --wifi --logo company_logo.jpg --logo-size 20

# Interactive mode will prompt for logo options
python bbqr.py
```

### Supported Logo Formats
- PNG, JPG, JPEG, GIF, BMP, TIFF
- Transparent backgrounds supported
- Automatic scaling and aspect ratio preservation

### Notes
- QR codes with logos are automatically saved to files
- Uses high error correction for better scannability
- Default logo size: 20% (recommended)

## Advanced Features

### File Watching

Auto-generate QR codes when a file changes:

```bash
python bbqr.py --watch notes.txt
python bbqr.py --watch journal.md --output qr_codes/journal_qr.png
```

### Multi QR Generation

Generate QR codes from each line in a file:

```bash
python bbqr.py --multi urls.txt
python bbqr.py --multi data.txt --size 12
```

### File Upload & Sharing

Upload files to 0x0.st and get download QR codes:

```bash
python bbqr.py --file document.pdf
python bbqr.py --file large_video.mp4
```

- Supports chunking for large files (>512MB)
- 30-day expiration
- Parallel uploads/downloads

## WiFi QR Codes

Two methods for WiFi sharing:

**Saved Profiles** (cross-platform):

- Windows: Uses `netsh` commands
- macOS: Reads from keychain
- Linux: Uses NetworkManager

**Manual Entry**:

- Enter SSID, password, security type
- Supports WPA/WPA2, WEP, Open networks

## QR Code Reading

BBQR can decode QR codes and handle different content types:

- **WiFi QR codes**: Shows network info, can connect (Windows)
- **URLs**: Open in browser or copy to clipboard
- **Images**: Extract and save to Pictures folder
- **File uploads**: Download and reassemble chunked files
- **Text**: Display content and copy to clipboard

## Auto-Save Options

- **No --save**: Terminal ASCII display only
- **With --save**: Terminal display + PNG file
- **Filename format**: `bbqr_[type]_[YYYYMMDD_HHMMSS].png`
- **File types**: text, url, wifi, clipboard, piped, image, file_upload

## 🚀 User Experience Improvements

### Streamlined Interactive Mode
- **Single Logo Prompt**: Logo preferences asked once per session
- **Smart Menu Flow**: No redundant questions or double prompts  
- **Consistent Experience**: Same workflow for all QR types

### Better Error Handling
- **Helpful Suggestions**: Shows similar files when paths not found
- **Graceful Fallbacks**: Continues without logo if image fails to load
- **Clear Messages**: BBQ-themed, informative error messages

## Tips & Best Practices

- Use 10-20% logo size for best scannability
- Test QR codes with different devices after adding logos
- Keep logos simple with high contrast for better results
- Interactive mode is great for exploring features

## Quick Examples

```bash
# Basic QR generation
python bbqr.py --text "Meeting Room 3, 2:00 PM"

# WiFi sharing with save
python bbqr.py --wifi --save

# Watch file for changes
python bbqr.py --watch todo.txt

# Upload and share file
python bbqr.py --file presentation.pdf --save

# Decode existing QR code
python bbqr.py --read wifi_qr.png

# Generate multiple QR codes
python bbqr.py --multi contact_list.txt
```

🔥 **Happy Grilling!** 🔥
