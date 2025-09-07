import threading
from blessed import Terminal
import math
import os
import struct
import time

# --- ASCII MODE ---
ascii_mode = False
ascii_chars = " .:-=+*%@#"

# --- BMP Saving Utilities ---
def prompt_resolution(term, default_w=1920, default_h=1080):
    print(term.move(3, 0) + term.clear_eol + term.bold_yellow(f"Enter resolution WxH (default {default_w}x{default_h}): "), end="", flush=True)
    res_str = ""
    while True:
        ch = term.inkey(timeout=None)
        if ch.name == "KEY_ENTER" or ch == "\n":
            break
        elif ch.name == "KEY_BACKSPACE":
            res_str = res_str[:-1]
            print(term.move(3, 0) + term.clear_eol + term.bold_yellow(f"Enter resolution WxH (default {default_w}x{default_h}): ") + res_str, end="", flush=True)
        elif ch.is_sequence or ch == "":
            continue
        else:
            res_str += ch
            print(term.move(3, 0) + term.clear_eol + term.bold_yellow(f"Enter resolution WxH (default {default_w}x{default_h}): ") + res_str, end="", flush=True)
    if "x" in res_str:
        try:
            w, h = map(int, res_str.lower().split("x"))
            return w, h
        except Exception:
            return default_w, default_h
    return default_w, default_h
def save_bmp(filename, width, height, pixels):
    row_padded = (width * 3 + 3) & ~3
    filesize = 54 + row_padded * height
    bmp_header = b'BM' + struct.pack('<IHHII', filesize, 0, 0, 54, 40)
    bmp_header += struct.pack('<iiHHIIIIII', width, height, 1, 24, 0, row_padded * height, 0, 0, 0, 0)
    with open(filename, 'wb') as f:
        f.write(bmp_header)
        for y in range(height-1, -1, -1):
            row = b''
            for x in range(width):
                r, g, b = pixels[y * width + x]
                row += struct.pack('BBB', b, g, r)
            row += b'\x00' * (row_padded - width * 3)
            f.write(row)

def palette_color_to_rgb(color_index):
    if 16 <= color_index <= 231:
        c = color_index - 16
        r = (c // 36) * 51
        g = ((c % 36) // 6) * 51
        b = (c % 6) * 51
        return (r, g, b)
    elif 232 <= color_index <= 255:
        v = (color_index - 232) * 10 + 8
        return (v, v, v)
    else:
        table = [
            (0,0,0),(128,0,0),(0,128,0),(128,128,0),(0,0,128),(128,0,128),(0,128,128),(192,192,192),
            (128,128,128),(255,0,0),(0,255,0),(255,255,0),(0,0,255),(255,0,255),(0,255,255),(255,255,255)
        ]
        return table[color_index % 16]

def render_fractal_image_mt(width, height, xmin, xmax, ymin, ymax, palette, max_iter, formula, coloring, progress_callback=None, julia_mode=False, julia_c=(0.0, 0.0), n_threads=8):
    pixels = [None] * (width * height)
    lock = threading.Lock()
    rows_done = [0]

    def worker(y_start, y_end):
        for y in range(y_start, y_end):
            cy = ymax - (y / (height - 1)) * (ymax - ymin)
            for x in range(width):
                cx = xmin + (x / (width - 1)) * (xmax - xmin)
                if julia_mode:
                    zx, zy = cx, cy
                    c_real, c_imag = julia_c
                else:
                    zx, zy = 0.0, 0.0
                    c_real, c_imag = cx, cy
                count = 0
                # --- Apply correct escape logic for Squarebrot and Rotating Squarebrot ---
                if formula is FRACTALS[FRACTAL_NAMES.index("Rotating Squarebrot")][1]:
                    angle = math.pi / 8
                    while True:
                        zx, zy = formula(zx, zy, c_real, c_imag)
                        zx_rot, zy_rot = rotate(zx, zy, angle * count)
                        if max(abs(zx_rot), abs(zy_rot)) >= 2.0 or count >= max_iter:
                            break
                        count += 1
                elif formula is FRACTALS[FRACTAL_NAMES.index("Squarebrot")][1]:
                    while max(abs(zx), abs(zy)) < 2.0 and count < max_iter:
                        zx, zy = formula(zx, zy, c_real, c_imag)
                        count += 1
                else:
                    while zx*zx + zy*zy < 4.0 and count < max_iter:
                        zx, zy = formula(zx, zy, c_real, c_imag)
                        count += 1
                color_idx = coloring(count, zx, zy, max_iter, palette)
                rgb = palette_color_to_rgb(color_idx)
                pixels[y * width + x] = rgb
            if progress_callback:
                with lock:
                    rows_done[0] += 1
                    progress_callback(rows_done[0], height)

    threads = []
    rows_per_thread = height // n_threads
    for i in range(n_threads):
        y_start = i * rows_per_thread
        y_end = (i + 1) * rows_per_thread if i < n_threads - 1 else height
        t = threading.Thread(target=worker, args=(y_start, y_end))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    return pixels

def save_current_fractal_bmp(filename, width, height, xmin, xmax, ymin, ymax, palette, max_iter, formula, coloring, progress_callback=None, julia_mode=False, julia_c=(0.0, 0.0)):
    n_threads = get_optimal_thread_count()
    pixels = render_fractal_image_mt(width, height, xmin, xmax, ymin, ymax, palette, max_iter, formula, coloring, progress_callback, julia_mode, julia_c, n_threads=n_threads)
    save_bmp(filename, width, height, pixels)

def bmp_progress_bar(term, y_done, y_total, term_width):
    bar_width = min(term_width - 18, 60)
    done = int(bar_width * y_done / y_total)
    bar = (
        term.green + "█" * done +
        term.bright_black + "░" * (bar_width - done) +
        term.normal
    )
    percent = int(100 * y_done / y_total)
    print(term.move(2, 0) + f"BMP Rendering: [{bar}] {percent:3d}%", end="", flush=True)

def preview_progress_bar(term, y_done, y_total, term_width):
    bar_width = min(term_width - 18, 60)
    done = int(bar_width * y_done / y_total)
    bar = (
        term.cyan + "█" * done +
        term.bright_black + "░" * (bar_width - done) +
        term.normal
    )
    percent = int(100 * y_done / y_total)
    print(term.move(2, 0) + f"Preview Rendering: [{bar}] {percent:3d}%", end="", flush=True)

def get_optimal_thread_count():
    try:
        count = os.cpu_count()
        if count is None:
            return 4
        return min(max(2, count), 32)
    except Exception:
        return 4

term = Terminal()

# --- Color Palettes ---
def generate_heatmap_palette():
    return [
        17, 18, 19, 20, 21, 27, 33, 39, 45, 51, 50, 49, 48, 47, 46, 82,
        118, 154, 190, 226, 220, 214, 208, 202, 196, 160, 124, 88, 52, 53, 54, 55,
        56, 57, 93, 129, 165, 201, 200, 199, 198, 197, 203, 209, 215, 221, 227, 228,
        229, 230, 231, 225, 219, 213, 207, 201, 200, 199, 198, 197, 196, 16, 232, 233
    ] * 4

def generate_pastel_palette():
    return [
        195, 189, 159, 151, 159, 195, 225, 231, 229, 230, 194, 159, 195, 225, 231, 230,
        194, 159, 195, 225, 231, 230, 194, 159, 195, 225, 231, 230, 194, 159, 195, 225,
        231, 230, 194, 159, 195, 225, 231, 230, 194, 159, 195, 225, 231, 230, 194, 159,
        195, 225, 231, 230, 194, 159, 195, 225, 231, 230, 194, 159, 195, 225, 231, 230
    ] * 4

def generate_extravagant_palette():
    return [
        21, 27, 33, 39, 45, 51, 50, 49, 48, 47, 46, 82, 118, 154, 190, 226,
        220, 214, 208, 202, 196, 160, 124, 88, 52, 53, 54, 55, 56, 57, 93, 129,
        165, 201, 200, 199, 198, 197, 203, 209, 215, 221, 227, 228, 229, 230, 231, 225,
        219, 213, 207, 201, 200, 199, 198, 197, 196, 160, 124, 88, 52, 21, 27, 33
    ] * 4

PALETTES = {
    "heatmap": generate_heatmap_palette()[:216],
    "pastel": generate_pastel_palette()[:216],
    "monochrome": [
        232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247,
        248, 249, 250, 251, 252, 253, 254, 255, 255, 254, 253, 252, 251, 250, 249, 248,
        247, 246, 245, 244, 243, 242, 241, 240, 239, 238, 237, 236, 235, 234, 233, 232,
        232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247
    ],
    "extravagant": generate_extravagant_palette()[:216],
    "cga": [
        16, 18, 19, 21, 27, 33, 39, 45, 51, 15, 15, 15, 15, 15, 15, 15,
        15, 15, 15, 15, 15, 15, 15, 15, 13, 13, 13, 13, 13, 13, 13, 13,
        13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13,
        13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13
    ]
}
PALETTE_NAMES = list(PALETTES.keys())

# --- Fractal Formulas --- Essential.
def mandelbrot_formula(zx, zy, cx, cy):
    return zx*zx - zy*zy + cx, 2*zx*zy + cy

def julia_formula(zx, zy, cx, cy):
    return zx*zx - zy*zy + cx, 2*zx*zy + cy

FRACTALS = [ #Don't bother reading this too much, just variables, no code here.
    ("Mandelbrot", mandelbrot_formula),
    ("Burning Ship", lambda zx, zy, cx, cy: (abs(zx*zx - zy*zy) + cx, abs(2*zx*zy) + cy)),
    ("Tricorn (Mandelbar)", lambda zx, zy, cx, cy: (zx*zx - zy*zy + cx, -2*zx*zy + cy)),
    ("Multibrot-3", lambda zx, zy, cx, cy: (
        zx**3 - 3*zx*zy*zy + cx,
        3*zx*zx*zy - zy**3 + cy
    )),
    ("Multibrot-4", lambda zx, zy, cx, cy: (
        zx**4 - 6*zx*zx*zy*zy + zy**4 + cx,
        4*zx**3*zy - 4*zx*zy**3 + cy
    )),
    ("Multibrot-5", lambda zx, zy, cx, cy: (
        zx**5 - 10*zx**3*zy**2 + 5*zx*zy**4 + cx,
        5*zx**4*zy - 10*zx**2*zy**3 + zy**5 + cy
    )),
    ("Multibrot-8", lambda zx, zy, cx, cy: (
        zx**8 - 28*zx**6*zy**2 + 70*zx**4*zy**4 - 28*zx**2*zy**6 + zy**8 + cx,
        8*zx**7*zy - 56*zx**5*zy**3 + 56*zx**3*zy**5 - 8*zx*zy**7 + cy
    )),
    ("Celtic", lambda zx, zy, cx, cy: (abs(zx*zx - zy*zy) + cx, 2*zx*zy + cy)),
    ("Perpendicular", lambda zx, zy, cx, cy: (zx*zx - zy*zy + cx, -2*abs(zx)*zy + cy)),
    ("Perpendicular Burning Ship", lambda zx, zy, cx, cy: (abs(zx*zx - zy*zy) + cx, -2*abs(zx)*zy + cy)),
    ("Heart", lambda zx, zy, cx, cy: (abs(zx*zx - zy*zy) + cx, 2*zx*zy + cy)),
    ("Cosine Mandelbrot", lambda zx, zy, cx, cy: (
        math.cos(zx*zx - zy*zy) + cx,
        math.cos(2*zx*zy) + cy
    )),
    ("Sine Mandelbrot", lambda zx, zy, cx, cy: (
        math.sin(zx*zx - zy*zy) + cx,
        math.sin(2*zx*zy) + cy
    )),
    ("Tangent Mandelbrot", lambda zx, zy, cx, cy: (
        math.tan(zx*zx - zy*zy) + cx,
        math.tan(2*zx*zy) + cy
    )),
    ("Phoenix", lambda zx, zy, cx, cy, p=[0.56667, 0.0]: (
        zx*zx - zy*zy + cx + p[0]*zx,
        2*zx*zy + cy + p[1]*zy
    )),
    ("Absolute Mandelbrot", lambda zx, zy, cx, cy: (abs(zx*zx - zy*zy) + cx, abs(2*zx*zy) + cy)),
    ("Squared Imaginary", lambda zx, zy, cx, cy: (zx*zx - zy*zy + cx, 2*zx*abs(zy) + cy)),
    ("Squarebrot", lambda zx, zy, cx, cy: (zx*zx - zy*zy + cx, 2*zx*zy + cy)),
    ("Rotating Squarebrot", lambda zx, zy, cx, cy: (
    zx*zx - zy*zy + cx,
    2*zx*zy + cy
))
]
FRACTAL_NAMES = [f[0] for f in FRACTALS]

# --- Coloring Techniques ---
def color_escape(count, zx, zy, max_iter, palette):
    idx = int(count / max_iter * (len(palette) - 1))
    return palette[idx]

def color_smooth(count, zx, zy, max_iter, palette):
    if count == max_iter:
        idx = 0
    else:
        norm = zx*zx + zy*zy
        if norm > 1.0:
            try:
                mu = count + 1 - math.log(math.log(norm))/math.log(2)
            except (ValueError, ZeroDivisionError):
                mu = count
        else:
            mu = count
        idx = int(mu / max_iter * (len(palette) - 1)) % len(palette)
    return palette[idx]

def color_angle(count, zx, zy, max_iter, palette):
    if count == max_iter:
        idx = 0
    else:
        angle = math.atan2(zy, zx)
        idx = int(((angle + math.pi) / (2 * math.pi)) * (len(palette) - 1))
    return palette[idx]

def color_orbit_trap(count, zx, zy, max_iter, palette):
    if count == max_iter:
        idx = 0
    else:
        trap = abs(zy)
        norm = min(trap * 10, 1.0)
        idx = int(norm * (len(palette) - 1))
    return palette[idx]

COLORINGS = [
    ("Escape Time", color_escape),
    ("Smooth", color_smooth),
    ("Angle", color_angle),
    ("Orbit Trap", color_orbit_trap),
]
COLORING_NAMES = [c[0] for c in COLORINGS]

# --- Julia Mode Globals ---
julia_mode = False
julia_c = (0.0, 0.0)

# --- Custom Formula Globals ---
custom_formula = None
custom_formula_name = "Custom"
formula_str = ""
def rotate(zx, zy, angle): # SQUAREBROT
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return zx * cos_a - zy * sin_a, zx * sin_a + zy * cos_a
# --- Fractal Renderer --- MARKDOWN
class FractalRenderer(threading.Thread): # DEFINE DEFINE DEFINE1!!!
    def __init__(self, width, height, xmin, xmax, ymin, ymax, palette, max_iter, formula, coloring, stop_event, n_threads=8, row_offset=3, julia_mode=False, julia_c=(0.0, 0.0), ascii_mode=False, progress_callback=None, fractal_idx=0):
        super().__init__()
        self.width = width
        self.height = height
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.palette = palette
        self.max_iter = max_iter
        self.formula = formula
        self.coloring = coloring
        self.stop_event = stop_event
        self.n_threads = n_threads
        self.row_offset = row_offset
        self.rows = [""] * (height // 2)
        self.julia_mode = julia_mode
        self.julia_c = julia_c
        self.ascii_mode = ascii_mode
        self.progress_callback = progress_callback
        self.total_rows = height // 2
        self.rows_done = 0
        self.lock = threading.Lock()
        self.fractal_idx = fractal_idx
    def render_rows(self, y_start, y_end): # RENDER LOGIC! RENDER LOGIC!
        chars = "▄"
        for y in range(y_start, y_end, 2):
            if self.stop_event.is_set():
                return
            row = ""
            for x in range(self.width):
                cx = self.xmin + (x / (self.width - 1)) * (self.xmax - self.xmin)
                cy1 = self.ymax - (y / (self.height - 1)) * (self.ymax - self.ymin)
                cy2 = self.ymax - ((y+1) / (self.height - 1)) * (self.ymax - self.ymin)
                if self.julia_mode:
                    zx1, zy1 = cx, cy1
                    zx2, zy2 = cx, cy2
                    c_julia = self.julia_c
                    count1 = 0
                    while zx1*zx1 + zy1*zy1 < 4.0 and count1 < self.max_iter:
                        zx1, zy1 = self.formula(zx1, zy1, c_julia[0], c_julia[1])
                        count1 += 1
                    count2 = 0
                    while zx2*zx2 + zy2*zy2 < 4.0 and count2 < self.max_iter:
                        zx2, zy2 = self.formula(zx2, zy2, c_julia[0], c_julia[1])
                        count2 += 1
                else:
                    # First row (cy1)
                    zx, zy = 0.0, 0.0
                    count1 = 0
                    if FRACTAL_NAMES[self.fractal_idx] == "Rotating Squarebrot":
                        angle = math.pi / 8
                        while True:
                            zx, zy = self.formula(zx, zy, cx, cy1)
                            zx_rot, zy_rot = rotate(zx, zy, angle * count1)
                            if max(abs(zx_rot), abs(zy_rot)) >= 2.0 or count1 >= self.max_iter:
                                break
                            count1 += 1
                    elif FRACTAL_NAMES[self.fractal_idx] == "Squarebrot":
                        while max(abs(zx), abs(zy)) < 2.0 and count1 < self.max_iter:
                            zx, zy = self.formula(zx, zy, cx, cy1)
                            count1 += 1
                    else:
                        while zx*zx + zy*zy < 4.0 and count1 < self.max_iter:
                            zx, zy = self.formula(zx, zy, cx, cy1)
                            count1 += 1
                    # Second row (cy2)
                    zx, zy = 0.0, 0.0
                    count2 = 0
                    if FRACTAL_NAMES[self.fractal_idx] == "Rotating Squarebrot":
                        angle = math.pi / 8
                        while True:
                            zx, zy = self.formula(zx, zy, cx, cy2)
                            zx_rot, zy_rot = rotate(zx, zy, angle * count2)
                            if max(abs(zx_rot), abs(zy_rot)) >= 2.0 or count2 >= self.max_iter:
                                break
                            count2 += 1
                    elif FRACTAL_NAMES[self.fractal_idx] == "Squarebrot":
                        while max(abs(zx), abs(zy)) < 2.0 and count2 < self.max_iter:
                            zx, zy = self.formula(zx, zy, cx, cy2)
                            count2 += 1
                    else:
                        while zx*zx + zy*zy < 4.0 and count2 < self.max_iter:
                            zx, zy = self.formula(zx, zy, cx, cy2)
                            count2 += 1
                if self.ascii_mode:
                    idx1 = int(count1 / self.max_iter * (len(ascii_chars) - 1))
                    idx2 = int(count2 / self.max_iter * (len(ascii_chars) - 1))
                    char = ascii_chars[max(idx1, idx2)]
                    color1 = self.coloring(count1, zx1 if self.julia_mode else zx, zy1 if self.julia_mode else zy, self.max_iter, self.palette)
                    row += f"\033[38;5;{color1}m{char}\033[0m"
                else:
                    color1 = self.coloring(count1, zx1 if self.julia_mode else zx, zy1 if self.julia_mode else zy, self.max_iter, self.palette)
                    color2 = self.coloring(count2, zx2 if self.julia_mode else zx, zy2 if self.julia_mode else zy, self.max_iter, self.palette)
                    row += f"\033[38;5;{color1}m\033[48;5;{color2}m{chars}\033[0m"
            self.rows[y // 2] = row # FIX SPASM IN PROGRESS BAR
            # --- Thread-safe progress update ---
            if self.progress_callback:
                with self.lock:
                    self.rows_done += 1
                    self.progress_callback(self.rows_done, self.total_rows)

    def run(self): # threading
        threads = []
        rows_per_thread = (self.height // 2) // self.n_threads
        for i in range(self.n_threads):
            y_start = i * rows_per_thread * 2
            y_end = (i + 1) * rows_per_thread * 2 if i < self.n_threads - 1 else self.height
            t = threading.Thread(target=self.render_rows, args=(y_start, y_end))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        for i, row in enumerate(self.rows):
            print(f"\033[{self.row_offset + i};1H{row}", end="", flush=True)
        total_rows = self.row_offset + len(self.rows)
        term_height = term.height
        for y in range(total_rows, term_height):
            print(f"\033[{y+1};1H" + " " * self.width)

def draw_status(term, fractal_idx, palette_idx, coloring_idx, zoom, cx, cy, max_iter, width, status_message=""):
    mode_str = "Julia" if julia_mode else (custom_formula_name if custom_formula else FRACTAL_NAMES[fractal_idx])
    julia_str = f" | c=({julia_c[0]:.4f},{julia_c[1]:.4f})" if julia_mode else ""
    ascii_str = " | ASCII" if ascii_mode else ""
    print(term.move(0, 0) + term.bold_white_on_black +
          f"Fractal: {mode_str}{julia_str}{ascii_str} | Palette: {PALETTE_NAMES[palette_idx]} | Coloring: {COLORING_NAMES[coloring_idx]} | Zoom: {zoom:.2f} | Center: ({cx:.4f}, {cy:.4f}) | Iter: {max_iter} | {status_message}".ljust(width))
    print(term.move(1, 0) + term.bold_white_on_black +
          "q:quit  +/-:zoom  arrows/WASD:pan  P:palette  F:fractal  O:coloring  H:home  B:save  J:julia  U:ascii  C:custom  Z:export  Y:import".ljust(width))
    print(term.normal, end="")

def main():
    global julia_mode, julia_c, custom_formula, custom_formula_name, ascii_mode, formula_str
    MIN_WIDTH = 40 # WILL CHECK IF ITS GOOD LATER
    MIN_HEIGHT = 12
    stop_event = threading.Event()
    renderer = None
    palette_idx = 0
    fractal_idx = 0
    coloring_idx = 0
    max_iter = 80

    DEFAULT_XMIN, DEFAULT_XMAX = -2.5, 1.0
    DEFAULT_YMIN, DEFAULT_YMAX = -1.25, 1.25
    DEFAULT_ZOOM = 1.0

    xmin, xmax = DEFAULT_XMIN, DEFAULT_XMAX
    ymin, ymax = DEFAULT_YMIN, DEFAULT_YMAX
    zoom = DEFAULT_ZOOM
    cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2

    status_message = ""

    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        prev_term_size = (term.width, term.height)
        while True:
            term_width, term_height = term.width, term.height

            if term_width < MIN_WIDTH or term_height < MIN_HEIGHT:
                print(term.home + term.clear + term.bold_red_on_black +
                      f"!!! SMALL TERMINAL SIZE: {term_width}x{term_height} !!!\n"
                      f"Resize to at least {MIN_WIDTH}x{MIN_HEIGHT} to continue.\n" +
                      term.normal)
                key = term.inkey(timeout=0.5)
                continue

            status_lines = 2
            margin_lines = 1
            height = max(2, (term_height - status_lines - margin_lines) * 2)
            width = min(term_width, 120) * 2

            w = (xmax - xmin) / zoom
            h = (ymax - ymin) / zoom
            x0 = cx - w / 2
            x1 = cx + w / 2
            y0 = cy - h / 2
            y1 = cy + h / 2

            print(term.home + term.clear, end="")
            draw_status(term, fractal_idx, palette_idx, coloring_idx, zoom, cx, cy, max_iter, term_width, status_message)

            if renderer and renderer.is_alive():
                stop_event.set()
                renderer.join()
                stop_event.clear()

            # Choose formula: Julia, custom, or fractal, sometimes squarebrot.... brot....
            if julia_mode:
                formula = julia_formula
            elif custom_formula:
                formula = custom_formula
            else:
                formula = FRACTALS[fractal_idx][1]

            def preview_callback(y_done, y_total):
                preview_progress_bar(term, y_done, y_total, term_width)

            renderer = FractalRenderer(
                width, height, x0, x1, y0, y1,
                PALETTES[PALETTE_NAMES[palette_idx]],
                max_iter,
                formula,
                COLORINGS[coloring_idx][1],
                stop_event,
                n_threads=get_optimal_thread_count(),
                row_offset=3,
                julia_mode=julia_mode,
                julia_c=julia_c,
                ascii_mode=ascii_mode,
                progress_callback=preview_callback,
                fractal_idx=fractal_idx  # <-- thank you squarebrot... it means alot to me you're my opp, even the bmp render had to updated

            )
            renderer.start()

            while True:
                key = term.inkey(timeout=0.1)
                if (term.width, term.height) != prev_term_size:
                    prev_term_size = (term.width, term.height)
                    stop_event.set()
                    renderer.join()
                    stop_event.clear()
                    break
                if key:
                    stop_event.set()
                    renderer.join()
                    stop_event.clear()
                    if key in ('q', 'Q'):
                        return
                    elif key in ('+', '='):
                        zoom *= 1.2
                    elif key == '-':
                        zoom /= 1.2
                    elif key.code in (term.KEY_LEFT,) or key in ('a', 'A'):
                        cx -= 0.2 * w
                    elif key.code in (term.KEY_RIGHT,) or key in ('d', 'D'):
                        cx += 0.2 * w
                    elif key.code in (term.KEY_UP,) or key in ('w', 'W'):
                        cy += 0.2 * h
                    elif key.code in (term.KEY_DOWN,) or key in ('s', 'S'):
                        cy -= 0.2 * h
                    elif key in ('b', 'B'):
                        #img_width = 1920 ENRIQUEEEEEE
                        #img_height = 1080
                        img_width, img_height = prompt_resolution(term, 1920, 1080)
                        aspect = img_width / img_height
                        w = x1 - x0
                        h = y1 - y0
                        center_x = (x0 + x1) / 2
                        center_y = (y0 + y1) / 2
                        if w / h > aspect:
                            new_h = w / aspect
                            y0_bmp = center_y - new_h / 2
                            y1_bmp = center_y + new_h / 2
                            x0_bmp, x1_bmp = x0, x1
                        else:
                            new_w = h * aspect
                            x0_bmp = center_x - new_w / 2
                            x1_bmp = center_x + new_w / 2
                            y0_bmp, y1_bmp = y0, y1
                        status_message = "RENDERING BMP..."
                        print(term.home + term.clear, end="")
                        draw_status(term, fractal_idx, palette_idx, coloring_idx, zoom, cx, cy, max_iter, term_width, status_message)
                        def progress_callback(y_done, y_total):
                            bmp_progress_bar(term, y_done, y_total, term_width)
                        epoch = int(time.time())
                        filename = f"fractal-{epoch}.bmp"
                        save_current_fractal_bmp(
                            filename,
                            img_width, img_height,
                            x0_bmp, x1_bmp, y0_bmp, y1_bmp,
                            PALETTES[PALETTE_NAMES[palette_idx]],
                            max_iter * 2,
                            formula,
                            COLORINGS[coloring_idx][1],
                            progress_callback,
                            julia_mode=julia_mode,
                            julia_c=julia_c
                        )
                        status_message = ""
                    elif key in ('p', 'P'):
                        palette_idx = (palette_idx + 1) % len(PALETTE_NAMES)
                    elif key in ('f', 'F'):
                        fractal_idx = (fractal_idx + 1) % len(FRACTALS)
                        zoom = DEFAULT_ZOOM
                        xmin, xmax = DEFAULT_XMIN, DEFAULT_XMAX
                        ymin, ymax = DEFAULT_YMIN, DEFAULT_YMAX
                        cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2
                        julia_mode = False
                        custom_formula = None
                    elif key in ('o', 'O'):
                        coloring_idx = (coloring_idx + 1) % len(COLORINGS)
                    elif key in ('h', 'H'):
                        zoom = DEFAULT_ZOOM
                        xmin, xmax = DEFAULT_XMIN, DEFAULT_XMAX
                        ymin, ymax = DEFAULT_YMIN, DEFAULT_YMAX
                        cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2
                        julia_mode = False
                        custom_formula = None
                    elif key in ('j', 'J'):
                        if not julia_mode:
                            julia_c = (cx, cy)
                            julia_mode = True
                            status_message = f"Julia mode: c=({julia_c[0]:.4f},{julia_c[1]:.4f})"
                        else:
                            julia_mode = False
                            status_message = "Mandelbrot mode"
                    elif key in ('u', 'U'):
                        ascii_mode = not ascii_mode
                        status_message = "ASCII mode ON" if ascii_mode else "ASCII mode OFF"
                    elif key in ('c', 'C'):
                        print(term.move(3, 0) + term.clear_eol + term.bold_yellow("Enter custom formula (real,imag): "), end="", flush=True)
                        formula_str = ""
                        while True:
                            ch = term.inkey(timeout=None)
                            if ch.name == "KEY_ENTER" or ch == "\n":
                                break
                            elif ch.name == "KEY_BACKSPACE":
                                formula_str = formula_str[:-1]
                                print(term.move(3, 0) + term.clear_eol + term.bold_yellow("Enter custom formula (real,imag): ") + formula_str, end="", flush=True)
                            elif ch.is_sequence or ch == "":
                                continue
                            else:
                                formula_str += ch
                                print(term.move(3, 0) + term.clear_eol + term.bold_yellow("Enter custom formula (real,imag): ") + formula_str, end="", flush=True)
                        try:
                            real_str, imag_str = formula_str.split(",", 1)
                            allowed_names = {"zx":0, "zy":0, "cx":0, "cy":0, "abs":abs, "math":math}
                            real_expr = compile(real_str.strip(), "<string>", "eval")
                            imag_expr = compile(imag_str.strip(), "<string>", "eval")
                            def custom(zx, zy, cx, cy):
                                return (
                                    eval(real_expr, {"__builtins__":None}, {"zx":zx,"zy":zy,"cx":cx,"cy":cy,"abs":abs,"math":math}),
                                    eval(imag_expr, {"__builtins__":None}, {"zx":zx,"zy":zy,"cx":cx,"cy":cy,"abs":abs,"math":math})
                                )
                            custom_formula = custom
                            custom_formula_name = "Custom"
                            fractal_idx = 0
                            julia_mode = False
                            status_message = "Custom formula set!"
                        except Exception as e:
                            custom_formula = None
                            status_message = f"Invalid formula!"
                    elif key in ('z', 'Z'):
                        # --- EXPORT PARAMETERS ---
                        params = {
                            "fractal_idx": fractal_idx,
                            "palette_idx": palette_idx,
                            "coloring_idx": coloring_idx,
                            "zoom": zoom,
                            "cx": cx,
                            "cy": cy,
                            "max_iter": max_iter,
                            "julia_mode": julia_mode,
                            "julia_c": julia_c,
                            "ascii_mode": ascii_mode,
                            "custom_formula_str": formula_str if custom_formula else None
                        }
                        param_str = repr(params)
                        print(term.move(3, 0) + term.clear_eol + term.bold_yellow("Exported parameters (copy this, then press any key):"))
                        print(term.move(4, 0) + term.clear_eol + param_str)
                        term.inkey(timeout=None)  # Wait for any key press
                        status_message = "Parameters exported!"
                    elif key in ('y', 'Y'):
                        # --- IMPORT PARAMETERS ---
                        print(term.move(3, 0) + term.clear_eol + term.bold_yellow("Paste parameters and press Enter: "), end="", flush=True)
                        import_str = ""
                        while True:
                            ch = term.inkey(timeout=None)
                            if ch.name == "KEY_ENTER" or ch == "\n":
                                break
                            elif ch.name == "KEY_BACKSPACE":
                                import_str = import_str[:-1]
                                print(term.move(3, 0) + term.clear_eol + term.bold_yellow("Paste parameters and press Enter: ") + import_str, end="", flush=True)
                            elif ch.is_sequence or ch == "":
                                continue
                            else:
                                import_str += ch
                                print(term.move(3, 0) + term.clear_eol + term.bold_yellow("Paste parameters and press Enter: ") + import_str, end="", flush=True)
                        try:
                            params = eval(import_str, {"__builtins__":None}, {})
                            fractal_idx = params.get("fractal_idx", fractal_idx)
                            palette_idx = params.get("palette_idx", palette_idx)
                            coloring_idx = params.get("coloring_idx", coloring_idx)
                            zoom = params.get("zoom", zoom)
                            cx = params.get("cx", cx)
                            cy = params.get("cy", cy)
                            max_iter = params.get("max_iter", max_iter)
                            julia_mode = params.get("julia_mode", julia_mode)
                            julia_c = tuple(params.get("julia_c", julia_c))
                            ascii_mode = params.get("ascii_mode", ascii_mode)
                            custom_formula_str = params.get("custom_formula_str", None)
                            if custom_formula_str:
                                try:
                                    real_str, imag_str = custom_formula_str.split(",", 1)
                                    real_expr = compile(real_str.strip(), "<string>", "eval")
                                    imag_expr = compile(imag_str.strip(), "<string>", "eval")
                                    def custom(zx, zy, cx, cy):
                                        return (
                                            eval(real_expr, {"__builtins__":None}, {"zx":zx,"zy":zy,"cx":cx,"cy":cy,"abs":abs,"math":math}),
                                            eval(imag_expr, {"__builtins__":None}, {"zx":zx,"zy":zy,"cx":cx,"cy":cy,"abs":abs,"math":math})
                                        )
                                    custom_formula = custom
                                    custom_formula_name = "Custom"
                                    formula_str = custom_formula_str
                                except Exception:
                                    custom_formula = None
                                    formula_str = ""
                            else:
                                custom_formula = None
                                formula_str = ""
                            status_message = "Parameters imported!"
                        except Exception as e:
                            status_message = "Import failed!"
                    break

if __name__ == "__main__":
    main()
