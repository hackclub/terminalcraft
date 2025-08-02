# 🔥 BBQR (Barbequer) - QR Code Generator 🔥

**BBQR** (pronounced "barbequer"), the hottest terminal-based QR code generator that grills your data to perfection!

## 🍖 Features

BBQR can handle all your QR code grilling needs:

### Core QR Generation

- 🌐 **URLs** - Grill web links into scannable codes
- 📝 **Text** - Smoke any text into QR perfection
- 🖼️ **Images** - Convert images to base64 QR codes
- 📋 **Clipboard** - Automatically grab clipboard content
- 🔄 **Piped Input** - Accept data from pipes and redirects
- 🎨 **Logo Embedding** - Add custom logos to QR codes with high-quality rendering

### WiFi QR Codes (Cross-Platform)

- 📶 **Saved WiFi Profiles**:
  - Windows: Uses `netsh` commands
  - macOS: Reads from keychain
  - Linux: Uses NetworkManager
- 🥩 **Manual WiFi Entry**: Enter SSID, password, security type
- Supports WPA/WPA2, WEP, and Open networks

### File Operations

- ⬆️ **File Upload**: Upload files to 0x0.st with QR download codes
- 📦 **Large File Support**: Automatic chunking for files >512MB
- 🔗 **Parallel Processing**: Multi-threaded uploads/downloads
- ⏰ **Auto-Expiration**: Files removed after 30 days

### Advanced Features

- 👀 **File Watching**: Auto-generate QR codes when files change
- 📂 **Multi QR Generation**: Process multiple lines from files
- 🔍 **QR Code Reader**: Decode and handle various QR content types
- 🎨 **BBQ Theme**: Colorful, fun interface with ASCII art
- 🖼️ **High-Quality Logo Support**: aspect ratio preservation

## 🔧 Installation

### Installation

```bash
pip install bbqr
```

Then start grilling:

```bash
bbqr --help
```

### Development Setup

If you want to contribute or run from source:

1. **Clone the repository**:

   ```bash
   git clone https://github.com/foglomon/bbqr
   cd bbqr
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Start grilling**:
   ```bash
   python bbqr.py
   ```

## 🚀 Usage

### Command Line Options

```bash
# Basic QR generation
bbqr --url "https://github.com"
bbqr --text "Hello, World!"
bbqr --image photo.jpg
bbqr --clipboard
bbqr --wifi

# File operations
bbqr --file document.pdf
bbqr --read qrcode.png

# Advanced features
bbqr --watch notes.txt
bbqr --multi urls.txt
bbqr --watch journal.md --output qr_codes/

# Options
bbqr --text "Hello" --size 15 --save --copy
bbqr --url "https://github.com" --save

# Logo embedding
bbqr --url "https://mycompany.com" --logo company_logo.png
bbqr --wifi --logo logo.png --logo-size 25
bbqr --text "Hello World!" --logo brand.jpg --save

# Piped input
echo "Secret message" | bbqr
date | bbqr --save
curl -s https://api.github.com/users/octocat | bbqr
```

### Interactive Mode

Run without arguments for the BBQ-themed menu:

```bash
bbqr
```

You'll see a beautiful interface:

```
🔥 Welcome to BBQR - The Barbequer! 🔥
Time to grill your data into delicious QR codes!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🍖 Interactive Mode - What would you like to grill?
1. 🌐 URL
2. 📝 Text
3. 🖼️  Image
4. 📋 Clipboard
5. 🛜  WiFi
6. ⬆️  Upload File
7. 👀 Watch File
8. 📂 Multi QR from File
9. 🔍 Read QR Code
```

## 💾 Output Options

### 🖥️ Terminal Display (Always)

- **Dark/Light Mode Compatible**: Uses ASCII blocks optimized for both themes
- **Instant Preview**: See your QR code immediately without files
- **Beautiful ASCII Art**: Clean, scannable terminal QR codes

### 💾 File Saving (Optional)

- **Auto-generated filenames**: `bbqr_[type]_[YYYYMMDD_HHMMSS].png`
- **Safe naming**: No overwriting, proper extensions
- **Multiple formats supported**: PNG output for all QR types

## 🎨 Logo Embedding

BBQR now supports adding custom logos to your QR codes with professional-quality rendering:

### Features

- **High-Quality Processing**: LANCZOS resampling for crisp logo rendering
- **Aspect Ratio Preservation**: Logos maintain their original proportions
- **Multiple Format Support**: PNG, JPG, JPEG, GIF, BMP, TIFF
- **Transparency Support**: Full RGBA and palette transparency handling
- **Error Correction**: Automatically uses higher error correction for logo QR codes
- **Auto-Save**: QR codes with logos are automatically saved to files

### Usage

```bash
# Add logo via command line
bbqr --text "Hello World!" --logo company_logo.png
bbqr --wifi --logo brand.jpg --logo-size 25
bbqr --url "https://mysite.com" --logo logo.png --logo-size 15

# Interactive mode prompts for logo options
bbqr
```

### Logo Size Options

- Size range: 10-30% of QR code size
- Default: 20% (optimal for most designs)
- Larger logos may affect scannability

### Technical Details

- Uses higher error correction (ERROR_CORRECT_H) when logos are embedded
- Logos are centered and scaled proportionally
- Output files include timestamp: `bbqr_[type]_with_logo_[timestamp].png`

## 📶 WiFi QR Codes

### Cross-Platform Profile Support

**Windows**:

- Uses `netsh wlan show profiles` to list saved networks
- Retrieves passwords with `netsh wlan show profile key=clear`

**macOS**:

- Reads from system keychain using `security` command
- Falls back to `networksetup` for profile listing

**Linux**:

- Uses NetworkManager (`nmcli`) for profile management
- Falls back to `/etc/wpa_supplicant/wpa_supplicant.conf`

### Manual WiFi Setup

For new networks or when automatic retrieval fails:

1. Enter SSID (network name)
2. Select security type (WPA/WPA2, WEP, Open)
3. Enter password if required

Generated QR codes work with all modern smartphones!

## 📁 File Upload & Sharing

BBQR integrates with 0x0.st for easy file sharing:

### Features

- **Large File Support**: Automatic chunking for files >512MB
- **Parallel Processing**: Multi-threaded uploads/downloads
- **Progress Tracking**: Real-time progress bars
- **Integrity Checking**: SHA256 hash verification
- **Auto-Cleanup**: Temporary files automatically removed

### How It Works

1. Upload file to 0x0.st (30-day expiration)
2. Generate QR code containing download information
3. Scan QR code to download and reassemble file
4. Automatic integrity verification

## 🔍 QR Code Reading

BBQR can decode various QR code types:

### WiFi QR Codes

- Displays network name, security type, password
- Can automatically connect on Windows
- Supports standard WiFi QR format

### File Upload QR Codes

- Shows file info (name, size, chunks)
- Downloads and reassembles automatically
- Verifies file integrity

### Image QR Codes

- Extracts base64-encoded images
- Saves to Pictures directory
- Supports multiple image formats

### Text/URL QR Codes

- Displays content with formatting
- Opens URLs in browser
- Copies content to clipboard

## 👀 File Watching

Monitor files for changes and auto-generate QR codes:

```bash
# Watch file with default output
python bbqr.py --watch notes.txt

# Custom output location
python bbqr.py --watch journal.md --output qr_codes/journal_qr.png

# Custom QR size
python bbqr.py --watch data.txt --size 15
```

Uses cross-platform file watching (falls back to polling if needed).

## 📂 Multi QR Generation

Generate QR codes from multiple lines in a file:

```bash
python bbqr.py --multi urls.txt
python bbqr.py --multi contact_list.txt --size 12
```

Creates numbered QR code files in a `qrcodes/` directory.

## � Technical Details

### Dependencies

- `qrcode[pil]`: QR code generation
- `Pillow`: Image processing
- `pyperclip`: Clipboard operations
- `colorama`: Cross-platform colored output
- `watchdog`: File monitoring
- `pyzbar`: QR code decoding
- `requests`: HTTP operations for file upload

### File Structure

```
bbqr.py              # Main script
requirements.txt     # Dependencies
README.md           # This file
QUICKSTART.md       # Quick start guide
LICENSE             # MIT License
```

### Performance

- Multi-threaded file operations
- Efficient chunking algorithm
- Memory-conscious processing
- Progress tracking for long operations

## 🎨 BBQ Theme

BBQR uses a fun BBQ theme throughout:

- 🔥 Fire emojis for active operations
- 🥩 Meat emojis for success messages
- 💨 Smoke emojis for info messages
- 💥 Explosion emojis for errors
- BBQ-themed terminology ("grilling", "smoking", "cooking")

## 🔥 Examples

### Basic Usage

```bash
# Quick URL QR
python bbqr.py -u "https://example.com"

# Text with custom size
python bbqr.py -t "Meeting at 3PM" -s 12

# Clipboard content
python bbqr.py -c
```

### Advanced Usage

```bash
# File upload with save
python bbqr.py --file presentation.pdf --save

# Watch file with custom output
python bbqr.py --watch todo.txt --output ~/Desktop/todo_qr.png

# Multi QR generation
python bbqr.py --multi contact_list.txt

# Read and handle QR code
python bbqr.py --read wifi_qr.png
```

### Piped Usage

```bash
# From file
cat secret.txt | python bbqr.py

# From command output
date | python bbqr.py --save

# Chain commands
curl -s https://api.github.com/users/octocat | python bbqr.py --copy
```

## 💡 Tips

- QR codes display directly in terminal using ASCII art
- Use `--save` to create PNG files with auto-generated names
- Larger `--size` values create more detailed QR codes
- WiFi QR codes work with most modern smartphones
- File watching supports both real-time monitoring and polling fallback
- Multi QR generation creates organized numbered files
- QR reading handles multiple content types intelligently

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your BBQ-themed improvements
4. Test thoroughly across platforms
5. Submit a pull request

## 📄 License

MIT License - Feel free to grill this code however you like!

---

**Happy Grilling!** 🔥🍖🔥

_"Where data meets the grill, and QR codes are always perfectly cooked!"_

## 🔧 Installation

### Prerequisites

- Python 3.7 or higher
- Windows OS (for WiFi profile management)

### Quick Setup

1. **Clone or download** this repository:

   ```bash
   git clone <repository-url>
   cd bbqr
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Make it executable** (optional):

   ```bash
   pip install -e .
   ```

## 🚀 Usage

### Command Line Options

```bash
# Generate QR from URL
python bbqr.py --url https://github.com

# Generate QR from text
python bbqr.py --text "Hello, World!"

# Generate QR from image
python bbqr.py --image photo.jpg

# Generate QR from clipboard
python bbqr.py --clipboard

# Generate WiFi QR code
python bbqr.py --wifi

# Piped input
echo "Secret message" | python bbqr.py

# Custom size and auto-save with timestamp
python bbqr.py --text "Hello" --size 15 --save

# Save any QR code with auto-generated filename (works with all input types)
python bbqr.py --url "https://github.com" --save
python bbqr.py --wifi --save
```

## 💾 Output Functionality

BBQR has a **safe dual output system**:

### 🖥️ **Terminal Display (Always)**

- **Dark Mode Compatible**: Uses white blocks that show clearly on dark backgrounds
- **Light Mode Compatible**: Uses proper spacing for light backgrounds
- **ASCII Art**: Beautiful terminal-based QR code display
- **Instant View**: See your QR code immediately without opening files

### Interactive Mode

Run without arguments for interactive mode:

```bash
python bbqr.py
```

You'll see a beautiful BBQ-themed menu:

```
🔥 Welcome to BBQR - The Barbequer! 🔥
Time to grill your data into delicious QR codes!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🍖 Interactive Mode - What would you like to grill?
1. 🌐 URL
2. 📝 Text
3. 🖼️  Image
4. 📋 Clipboard
5. 📶 WiFi
```

### WiFi QR Codes

The WiFi feature offers two grilling methods:

#### 🔥 **Saved WiFi Profiles**

- Automatically discovers all saved Windows WiFi profiles
- Retrieves stored passwords using Windows netsh
- One-click QR generation for known networks

#### 🥩 **Manual WiFi Entry**

- Enter SSID, security type, and password manually
- Supports WPA/WPA2, WEP, and Open networks
- Perfect for sharing guest networks

## 📱 WiFi QR Code Format

Generated WiFi QR codes use the standard format:

```
WIFI:T:WPA;S:NetworkName;P:password;;
```

When scanned, devices will automatically prompt to join the network!

## 🎨 BBQ Theme

BBQR brings the heat with:

- 🔥 Fire emojis for emphasis
- 🥩 Meat-themed progress indicators
- 🍖 Grill terminology throughout
- 💨 Smoke effects for processing

## 🔧 Technical Details

### Dependencies

- **qrcode[pil]** - QR code generation with PIL imaging
- **Pillow** - Image processing
- **pyperclip** - Clipboard access
- **click** - Command-line interface enhancements
- **colorama** - Cross-platform colored terminal text

### Windows WiFi Integration

Uses Windows `netsh` command for:

- Listing saved WiFi profiles
- Retrieving stored passwords
- No additional dependencies required

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your BBQ-themed improvements
4. Test thoroughly
5. Submit a pull request

## 📄 License

GNU GPLv3

## 🔥 Examples

### Basic Usage

```bash
# Quick URL QR
python bbqr.py -u "https://example.com"

# Text with custom size
python bbqr.py -t "Meeting at 3PM" -s 12

# Clipboard content
python bbqr.py -c
```

### Piped Usage

```bash
# From file
cat secret.txt | python bbqr.py

# From command output
date | python bbqr.py

# Chain commands
curl -s https://api.github.com/users/octocat | python bbqr.py
```

### WiFi Sharing

```bash
# Interactive WiFi setup
python bbqr.py --wifi

# This will show:
# 1. 🔥 Use saved WiFi profile
# 2. 🥩 Add new WiFi credentials
```

## 💡 Tips

- QR codes are displayed directly in the terminal using ASCII art
- Use `--output` to save QR codes as image files
- Larger `--size` values create more detailed QR codes
- WiFi QR codes work with most modern smartphones
- Pipe any command output to instantly create QR codes

---

**Happy Grilling!** 🔥🍖🔥

_"Where data meets the grill, and QR codes are always perfectly cooked!"_
