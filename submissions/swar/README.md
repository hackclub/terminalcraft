# SWAR - Text to Music CLI Tool


https://github.com/user-attachments/assets/bea1eeea-c6ed-4609-9b7e-44b13eb49b51


**Swar** is a command-line tool that converts any textual or code input into musical notes, generating MIDI files and optional music sheets. This project is ideal for creative data transmission, artistic audio encoding, or simply transforming messages into music.

---

## Features

- Converts plain text or code into musical notes
- Generates playable `.mid` files from input text
- Optionally outputs printable MusicXML sheet music
- Supports special character encoding via custom note mapping
- Built with a clean and modular CLI using `click`
- Includes a built-in MIDI player
- Cross-platform (works on Windows, macOS, Linux)
- Easily installable via `pip install .`

---

## Installation

To install and use Swar, ensure you have Python 3.7+ installed.

1. Clone the repository:

   ```bash
   git clone https://github.com/darshanC07/swar.git
   cd swar
2. Install the project using pip:

    ```bash
    pip install .

## CLI Usage
After installation, you can run Swar from any terminal:
Introduction

  ```bash
    swar
  ```
This prints the welcome message, logo, and basic help.

Convert Text to Music

  ```bash
    swar musicfy "your message here"
  ```
    
This creates a MIDI file named swar.mid in the current directory.

**Options:**
<br>
--output [filename] <br>
      Specify a custom output name (without .mid extension).

-ms <br>
Save a MusicXML file (sheet music) along with the MIDI.

Examples:

  ```bash
  swar musicfy "hello world" --output greeting
  swar musicfy "for sheet music" -ms
  ```
    
Play a MIDI File

```bash
swar play
```
This plays the most recently created swar.mid file.

You can also specify a custom file (without extension):

  ```bash
  swar play greeting
