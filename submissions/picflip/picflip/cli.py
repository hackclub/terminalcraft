import argparse
import os
import io
import logging
import warnings
from rembg import remove
from PIL import Image

warnings.filterwarnings("ignore", message=".*context leak detected.*")
logging.getLogger("onnxruntime").setLevel(logging.ERROR)

def remove_background(input_path, output_path):
    """
    remove the background from an image!
    """
    try:
        with open(input_path, 'rb') as f:
            input_data = f.read()
        output_data = remove(input_data)
        image = Image.open(io.BytesIO(output_data))
        image.save(output_path)
        print(f"background removed! its at {output_path}")
    except Exception as e:
        print(f"couldnt remove bg :{e}")

def convert_to_png(input_path, output_path):
    """
    Convert an image to a png.
    Supports:
      - SVG (requires cairo on your computer)
      - JPG
      - WEBP
    """
    ext = os.path.splitext(input_path)[1].lower()
    try:
        if ext == '.svg':
            try:
                import cairosvg
            except ImportError:
                print("cairosvg is not installed. Run: pip install cairosvg")
                return
            cairosvg.svg2png(url=input_path, write_to=output_path)
            print(f"converted SVG to PNG! its at - {output_path}")
        else:
            with Image.open(input_path) as img:
                img.save(output_path, "PNG")
            print(f"converted {ext.upper()} to PNG! its at - {output_path}")
    except Exception as e:
        print(f"[✘] Error converting image: {e}")

def usage():
    print("Usage:")
    print("  python main.py remove <input_image> <output_image>")
    print("  python main.py convert <input_image> <output_image>")
    print("Example:")
    print("  python main.py convert shrek.webp shrek.png")

def main():
    parser = argparse.ArgumentParser(description="picflip - remove backgrounds from images and convert them to PNG!")
    subparsers = parser.add_subparsers(dest="command", required=True)
    parser_remove = subparsers.add_parser("remove", help="Remove the background from an image")
    parser_remove.add_argument("input", help="Path to the input image")
    parser_remove.add_argument("output", help="Path for the output image (PNG recommended)")
    parser_convert = subparsers.add_parser("convert", help="Convert an image to PNG")
    parser_convert.add_argument("input", help="Path to the input image (jpg, svg, webp, etc.)")
    parser_convert.add_argument("output", help="Path for the output PNG image")
    parser_usage = subparsers.add_parser("usage", help="Display usage instructions")
    args = parser.parse_args()
    if args.command == "remove":
        remove_background(args.input, args.output)
    elif args.command == "convert":
        convert_to_png(args.input, args.output)
    elif args.command == "usage":
        usage()

if __name__ == "__main__":
    main()
