from PIL import Image
import colorsys
import os

def get_terminal_width():
    """Gets the width of the terminal."""
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80  # Default width if terminal size cannot be determined

def get_ascii_char(luminance):
    """Maps luminance to an ASCII character."""
    ascii_chars = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    index = int(luminance * (len(ascii_chars) - 1))
    return ascii_chars[index]

def get_color_code(r, g, b):
    r = int(r)
    g = int(g)
    b = int(b)

    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

    if s < 0.2:
        gray = int(round((r + g + b) / 3.0 / 256.0 * 24))
        return f"\033[38;5;{232 + gray}m"
    else:
        r_index = int(round(r / 255.0 * 5))
        g_index = int(round(g / 255.0 * 5))
        b_index = int(round(b / 255.0 * 5))
        color_index = 16 + r_index * 36 + g_index * 6 + b_index
        return f"\033[38;5;{color_index}m"

def print_image(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
    except FileNotFoundError:
        print(f"Error: Image not found at {image_path}")
        return

    terminal_width = get_terminal_width()
    img_width, img_height = img.size
    aspect_ratio = img_height / img_width
    new_height = int(terminal_width * aspect_ratio * 0.5)
    img = img.resize((terminal_width, new_height))

    ascii_art = ""
    for y in range(new_height):
        for x in range(terminal_width):
            r, g, b = img.getpixel((x, y))
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
            ascii_char = get_ascii_char(luminance)
            color_code = get_color_code(r, g, b)
            ascii_art += color_code + ascii_char

        ascii_art += "\033[0m\n"

    print(ascii_art)

if __name__ == "__main__":
    print_image("B11491E1-F9F6-4FD1-969B-19B17202F125.jpg")