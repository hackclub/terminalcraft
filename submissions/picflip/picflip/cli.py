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

def convert_image(input_path, output_path, output_format):
    """
    convert an image to the formats below.
    Supports:
      - PNG
      - JPG/JPEG
      - WEBP
      - SVG (input only, converts to PNG)
    """
    supported_formats = {'png', 'jpg', 'jpeg', 'webp'}
    output_format = output_format.lower()
    
    if output_format not in supported_formats:
        print(f"unsupported output format. supported formats are: {', '.join(supported_formats)}")
        return

    ext = os.path.splitext(input_path)[1].lower()
    try:
        if ext == '.svg':
            try:
                import cairosvg
            except ImportError:
                print("cairosvg is not installed. install it with: pip install cairosvg")
                return
            cairosvg.svg2png(url=input_path, write_to=output_path)
            print(f"converted SVG to PNG: {output_path}")
        else:
            with Image.open(input_path) as img:
                if output_format in ['jpg', 'jpeg'] and img.mode == 'RGBA':
                    img = img.convert('RGB')
                img.save(output_path, output_format.upper())
            print(f"✓ Converted {ext[1:].upper()} to {output_format.upper()}: {output_path}")
    except FileNotFoundError:
        print(f"input file not found: {input_path}")
    except Exception as e:
        print(f"error converting image: {e}")

def usage():
    print("Usage:")
    print("  python main.py remove <input_image> <output_image>")
    print("  python main.py convert <input_image> <output_image> <output_format>")
    print("Example:")
    print("  python main.py convert shrek.webp shrek.jpg jpg")

def main():
    parser = argparse.ArgumentParser(
        description="picflip - A simple tool to remove backgrounds and convert images!",
        epilog="""
Examples:
  Remove background:    python cli.py remove input.jpg output.png
  Convert image:        python cli.py convert input.jpg output.png png
  Convert formats:      python cli.py convert photo.webp photo.jpg jpg
  Convert SVG:         python cli.py convert icon.svg icon.png png
        """
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Remove command
    parser_remove = subparsers.add_parser("remove", 
        help="Remove the background from an image",
        description="Remove the background from any image and save it as PNG (recommended) or other formats"
    )
    parser_remove.add_argument("input", help="Path to the input image (supports jpg, png, webp)")
    parser_remove.add_argument("output", help="Path for the output image (PNG recommended for transparency)")
    
    # Convert command
    parser_convert = subparsers.add_parser("convert",
        help="Convert images between formats",
        description="Convert images between different formats (PNG, JPG, JPEG, WEBP, SVG)"
    )
    parser_convert.add_argument("input", help="Path to the input image")
    parser_convert.add_argument("output", help="Path for the output image")
    parser_convert.add_argument("format", help="Output format (png, jpg, jpeg, webp)")
    
    args = parser.parse_args()
    if args.command == "remove":
        remove_background(args.input, args.output)
    elif args.command == "convert":
        convert_image(args.input, args.output, args.format)
    elif args.command == "usage":
        usage()

if __name__ == "__main__":
    main()
