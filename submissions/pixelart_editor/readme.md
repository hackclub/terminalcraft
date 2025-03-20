# asciiart_editor - ASCII Art Editor in Terminal


A feature-rich terminal-based ASCII art editor with advanced drawing capabilities, supporting mouse input, multiple colors, undo/redo history, and various drawing tools. Perfect for creating retro-style artwork directly in your terminal!

## Features ✨

- **Multi-tool Canvas Editing**
  - Freehand drawing
  - Line drawing tool
  - Flood fill (paint bucket)
  - Grid overlay for precision
- **Advanced Color Support**
  - 7-color palette (1-7 keys)
  - Separate foreground/background colors
- **File Management**
  - Save/Load JSON projects
  - Auto-save functionality
- **History Management**
  - Unlimited undo/redo
  - Cross-tool history support
- **Modern Interface**
  - Mouse support
  - Dynamic window resizing
  - Interactive help menu
- **Special Functions**
  - Canvas clearing
  - Character picker
  - Real-time preview


## Quickstart ⚡  
*Create basic shapes in under 1 minute:*

### **Single Point**
1. Press `←→↑↓` to move cursor  
2. Select color with `1`-`7`  
3. Press `Space` to place character  

### **Straight Line**
1. Move to start position → Press `l`  
2. Move to end position → Press `l` again  
*Example:*  
```
A----B (Press 'l' at A, then at B)
```

### **Filled Triangle**
1. **Draw Outline** with 3 lines:  
   ```
    ▲
   / \ 
  /___\```
  
   - Use `l` tool for each edge  

2. **Fill Interior**:  
   a. Move cursor inside triangle  
   b. Press `f` to flood-fill  

3. **Add Details**:  
   - Use different colors (`2`-`7`) for borders vs fill  
   - Toggle grid (`z`) for perfect angles  

---

**Pro Tip:** Combine these techniques to create:  
- Rectangles (4 lines + fill)  
- Diamonds (rotated squares)  
- Pixel-art characters (single-point details)  

---

## Installation 💻

**Requirements:**
- Python 3.6+
- curses-compatible terminal

```bash
pip install curses-menu  # Only required if not pre-installed
git clone https://github.com/piter231/pixelart_editor.git
cd pixelart_editor
```

## Usage 🎨

Start the editor:
```bash
python main.py
```

### Basic Workflow:
1. Move cursor with arrow keys or mouse clicks
2. Select color with number keys (1-7)
3. Draw with Space/click
4. Use tools (line, flood fill)
5. Save with `s` or quit with `q`

## Key Bindings ⌨️

| Key | Function                  | Description                          |
|-----|---------------------------|--------------------------------------|
| ←→↑↓| Move cursor              | Navigate drawing area               |
| Space | Draw                   | Place current character/color       |
| 1-7  | Select color           | Change drawing color                |
| c    | Clear canvas            | Reset entire canvas                 |
| z    | Toggle grid            | Show/hide alignment grid            |
| f    | Flood fill             | Fill enclosed area                  |
| l    | Line tool              | Draw straight lines                 |
| u/r  | Undo/Redo              | History navigation                  |
| x    | Change character       | Set custom ASCII character          |
| a    | Toggle auto-save       | Enable/disable 5-second auto-save   |
| s/o  | Save/Load              | File operations                     |
| h    | Help                   | Show interactive help               |
| q    | Quit                   | Exit program                        |

## Advanced Techniques 🖌️

### Line Drawing
1. Position cursor at start point
2. Press `l`
3. Move to end point
4. Press `l` again to complete

### Flood Fill Tips
- Works with both characters and colors
- Fills contiguous areas
- Combine with grid for pixel-art effects

### Mouse Controls
- Click to move cursor
- Click+drag for continuous drawing

### Color System
| Key | Color      | Pair # |
|-----|------------|--------|
| 1   | White      | 1      |
| 2   | Red        | 2      |
| 3   | Green      | 3      |
| 4   | Blue       | 4      |
| 5   | Yellow     | 5      |
| 6   | Cyan       | 6      |
| 7   | Magenta    | 7      |

## Customization ⚙️

### Modify Colors
Edit the `init_colors` method to change RGB values:
```python
curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
```

### Change Grid Style
Modify grid character in `draw_canvas`:
```python
self.stdscr.addstr(y, x, '+', curses.color_pair(8) | curses.A_DIM)
```

## Known Issues ⚠️

- Terminal compatibility varies
- Large canvases may impact performance
- Mouse support depends on terminal emulator

## Contributing 🤝

1. Fork the repository
2. Create feature branch (`git checkout -b feature/fooBar`)
3. Commit changes (`git commit -am 'Add some fooBar'`)
4. Push to branch (`git push origin feature/fooBar`)
5. Create new Pull Request

## License 📄

MIT License 

---

**Happy ASCII Art Creating!** 🎨👾
