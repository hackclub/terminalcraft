# FracSH - Terminal Fractal Explorer and Renderer

FracSH is a fast, rabbit hole of a fractal explorer. 
It has built in Mandelbrot, Julia, Multibrot, Burning Ship, custom formulas, colored ASCII (or unicode.), BMP export (implemented by me!), and more—all in Python!

## Features

- Real-time terminal fractal rendering (Mandelbrot, Julia, Multibrot, Burning Ship, ...)
- Custom formula support (enter your own mandelbrot formulas.)
- Colored ASCII mode (for nostalgia!)
- Julia mode for any formula (experimental, 50/50 chance of working.)
- Multithreaded rendering for fast previews and BMP export (fully working, very fast for python standards.)
- Progress bars for both preview and BMP rendering (mandelbrot-8 so slow, the preview has a progress bar 🥀)
- Parameter import/export (go back to your fav location)
- Resolution prompt for BMP export (customized resolutions such as user defined resolutions, common is 1024x600 for being fast to render and clarity.)
- Multiple color palettes and coloring modes (CGA Included!)
- Keyboard controls for zoom, pan, palette, fractal, and more (Down below!)

## Screenshots

![image](https://github.com/user-attachments/assets/647a3473-20b3-4110-b9c2-cac2b72fd6c9)

![image](https://github.com/user-attachments/assets/0150d243-1883-4459-b2e3-cd45808cc780)


![image](https://github.com/user-attachments/assets/a6ab4b71-b0d2-4578-af01-dc3c9bb218c2)

![image](https://github.com/user-attachments/assets/b8091763-42ae-4d92-9c2e-e50c7eae1d33)
![image](https://github.com/user-attachments/assets/34c4afeb-efde-4d91-8bab-43f299da290a)


## Usage

1. **Run the program:**
   ```
   python main.py
   ```

2. **Controls:**
   - Arrows / WASD: Pan (You can even scroll with a mouse to go up and down instead of W and S)
   - + / -: Zoom in/out
   - P: Next palette
   - F: Next fractal
   - O: Next coloring mode
   - H: Home/reset view
   - B: Export BMP (with resolution prompt)
   - C: Enter custom formula
   - J: Toggle Julia mode
   - U: Toggle ASCII mode
   - Z: Export parameters
   - Y: Import parameters
   - Q: Quit (or CTRL-C :3)

3. **Custom formulas:**  (im not a mathematician so i don't know much about creating my own custom formulas, but there you go! works.)
   When prompted, enter two comma-separated expressions for the real and imaginary parts, for example an mandelbrot set looks like this:
   ```
   zx*zx-zy*zy+cx,2*zx*zy+cy
   ```

4. **BMP Export:**  
   Press B, enter your wanted resolution (e.g. 1920x1080, 512x512), and wait for the progress bar to finish. (actually works!)

## Requirements

- Python 3.13.5 (only tested on latest version, older might work without issues.)
- [blessed](https://pypi.org/project/blessed/) (`pip install blessed`)
## Platform Compatibility

| Platform         | Supported | Notes                        |
|------------------|:---------:|------------------------------|
| Windows 11       |    ✅     | Fully tested                 |
| Python 3.13.5    |    ✅     | Recommended version          |
| Raspbian         |    ✅     | Fully tested, Python 3.11            |

## License

MIT License

---

Time spent: 5 hours programming, 7+5 hours researching.
## Achknowledgements

- [Wikipedia](https://en.wikipedia.org/wiki/Mandelbrot_set)
- Very inspired and motivated by [Golova.dev](https://golova.dev/experiments/fractalSounds)
- Made for TerminalCraft as LemonGravy
