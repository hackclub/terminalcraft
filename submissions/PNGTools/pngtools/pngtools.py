import argparse
import base64
import colorsys
import io
import math
import os
import random
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

class PNGTools:
    def __init__(self):
        self.original_image = None
        self.processed_image = None

    def load_image(self, file_path):

        if file_path.lower().endswith('.txt'):
            try:
                with open(file_path, 'r') as file:
                    base64_string = file.read().strip()
                image_data = base64.b64decode(base64_string)
                self.original_image = Image.open(io.BytesIO(image_data))
            except Exception as e:
                print(f"Error loading base64 data: {e}")
                sys.exit(1)

        else:
            try:
                self.original_image = Image.open(file_path)
            except Exception as e:
                print(f"Error loading image: {e}")
                sys.exit(1)

    def save_image(self, output_path):
        """Save the processed image to a file"""
        if not hasattr(self, 'processed_image') or self.processed_image is None:
            print("Error: No processed image to save.")
            sys.exit(1)

        file_extension = os.path.splitext(output_path)[1].lower()
        try:
            if isinstance(self.processed_image, str):
                # It's a string (likely base64 or analysis result)
                with open(output_path, 'w') as f:
                    f.write(self.processed_image)
            else:
                if file_extension == '.jpg' or file_extension == '.jpeg':
                    self.processed_image.convert("RGB").save(output_path, format="JPEG")
                elif file_extension == '.webp':
                    self.processed_image.save(output_path, format="WebP")
                else:  # Default to PNG
                    self.processed_image.save(output_path, format="PNG")
            print(f"Image saved to {output_path}")
        except Exception as e:
            print(f"Error saving image: {e}")
            sys.exit(1)
    
    
    def color_distance(self, color1, color2):
        return sum((a - b) ** 2 for a, b in zip(color1, color2)) ** 0.5 / 441.6729559300637

    def make_transparent(self, target_color, tolerance):
        if not self.original_image:
            return
        
        img = self.original_image.convert("RGBA")
        data = img.getdata()
        new_data = []
        target_rgb = tuple(int(target_color[i:i+2], 16) for i in (0, 2, 4))
        threshold = tolerance / 100.0

        for item in data:
            if self.color_distance(item[:3], target_rgb) <= threshold:
                new_data.append((item[0], item[1], item[2], 0))
            else:
                new_data.append(item)

        img.putdata(new_data)
        self.processed_image = img


    def swap_colors(self, target_color, new_color, tolerance):
        if not self.original_image:
            return
        
        img = self.original_image.convert("RGBA")
        data = img.getdata()
        new_data = []
        target_rgb = tuple(int(target_color[i:i+2], 16) for i in (0, 2, 4))
        new_rgb = tuple(int(new_color[i:i+2], 16) for i in (0, 2, 4))
        threshold = tolerance / 100.0

        for item in data:
            if self.color_distance(item[:3], target_rgb) <= threshold:
                new_data.append(new_rgb + (item[3],))
            else:
                new_data.append(item)

        img.putdata(new_data)
        self.processed_image = img

    def change_color_tone(self, new_tone):
        if not self.original_image:
            return
        
        img = self.original_image.convert("RGBA")
        data = img.getdata()
        new_data = []
        new_rgb = tuple(int(new_tone[i:i+2], 16) for i in (0, 2, 4))
        new_hsv = colorsys.rgb_to_hsv(*[x/255.0 for x in new_rgb])

        for item in data:
            if item[3] != 0:
                r, g, b = item[:3]
                h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
                new_r, new_g, new_b = colorsys.hsv_to_rgb(new_hsv[0], new_hsv[1], v)
                new_data.append((int(new_r*255), int(new_g*255), int(new_b*255), item[3]))
            else:
                new_data.append(item)

        img.putdata(new_data)
        self.processed_image = img

    def change_opacity(self, opacity):
        if not self.original_image:
            return

        img = self.original_image.convert("RGBA")
        data = img.getdata()
        new_data = []
        opacity_level = opacity / 100.0

        for item in data:
            new_alpha = int(item[3] * opacity_level)
            new_data.append(item[:3] + (new_alpha,))

        img.putdata(new_data)
        self.processed_image = img

    def add_noise(self, noise_level, color_similarity=None):
        if not self.original_image:
            return
        
        img = self.original_image.convert("RGBA")
        width, height = img.size
        pixels = img.load()
        noise_amount = noise_level / 100.0

        noise_type = "similar" if color_similarity is not None else "random"
        similarity = color_similarity / 100.0 if color_similarity is not None else None

        for _ in range(int(width * height * noise_amount)):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)

            if noise_type == "random":
                new_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 255)
            else:
                r, g, b, a = pixels[x, y]
                new_r = max(0, min(255, int(r + (random.random() * 2 - 1) * 255 * similarity)))
                new_g = max(0, min(255, int(g + (random.random() * 2 - 1) * 255 * similarity)))
                new_b = max(0, min(255, int(b + (random.random() * 2 - 1) * 255 * similarity)))
                new_color = (new_r, new_g, new_b, a)

            pixels[x, y] = new_color

        self.processed_image = img

    def compress_png(self, compression_level):
        if not self.original_image:
            return
        
        img = self.original_image.copy()
        original_size = self.find_file_size(self.original_image)
        target_ratio = (compression_level / 100) ** 0.7 * 98
        target_size = original_size * (1 - target_ratio / 100)
        min_resolution_factor = 0.1
        max_resolution_factor = 0.95

        if compression_level <= 20:
            resolution_factor = 0.85
            color_mode = 'P'
            palette_size = 256
        elif compression_level <= 40:
            resolution_factor = 0.7
            color_mode = 'P'
            palette_size = 192
        elif compression_level <= 60:
            resolution_factor = 0.55
            color_mode = 'P'
            palette_size = 128
        elif compression_level <= 80:
            resolution_factor = 0.4
            color_mode = 'P'
            palette_size = 64
        else:
            resolution_factor = 0.3
            color_mode = 'L' if compression_level > 85 else 'P'
            palette_size = 32

        img_resized = img.copy()
        new_width = max(1, int(img.width * resolution_factor))
        new_height = max(1, int(img.height * resolution_factor))
        img_resized = img_resized.resize((new_width, new_height), Image.Resampling.LANCZOS)

        if color_mode == 'P':
            if img_resized.mode == 'RGBA':
                background = Image.new('RGB', img_resized.size, (255, 255, 255))
                background.paste(img_resized, mask=img_resized.split()[3])
                img_resized = background
            elif img_resized.mode != 'RGB':
                img_resized = img_resized.convert('RGB')

            img_resized = img_resized.quantize(colors=palette_size, method=2)
        
        elif color_mode == 'L':
            img_resized = img_resized.convert('L')

        output = io.BytesIO()
        img_resized.save(output, format="PNG", optimize=True, compress_level=9)
        output.seek(0)
        self.processed_image = Image.open(output)
        compressed_size = self.find_file_size(self.processed_image)

        tolerance = 0.05 * target_size
        iterations = 0
        max_iterations = 3

        while abs(compressed_size - target_size) > tolerance and iterations < max_iterations:
            iterations += 1

            if compressed_size > target_size:
                resolution_factor *= 0.85
                if resolution_factor < min_resolution_factor:
                    resolution_factor = min_resolution_factor
                    break
            
            else:
                resolution_factor /= 0.85
                if resolution_factor > max_resolution_factor:
                    resolution_factor = max_resolution_factor
                    break

            img_resized = img.copy()
            new_width = max(1, int(img.width * resolution_factor))
            new_height = max(1, int(img.height * resolution_factor))
            img_resized = img_resized.resize((new_width, new_height), Image.Resampling.LANCZOS)

            if color_mode == 'P':
                if img_resized.mode == 'RGBA':
                    background = Image.new('RGB', img_resized.size, (255, 255, 255))
                    background.paste(img_resized, mask=img_resized.split()[3])
                    img_resized = background
                elif img_resized.mode != 'RGB':
                    img_resized = img_resized.convert('RGB')
                
                img_resized = img_resized.quantize(colors=palette_size, method=2)
            elif color_mode == 'L':
                img_resized = img_resized.convert('L')

            output = io.BytesIO()
            img_resized.save(output, format="PNG", optimize=True, compress_level=9)
            output.seek(0)
            self.processed_image = Image.open(output)
            compressed_size = self.find_file_size(self.processed_image)

        ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

        print(f"Original dimensions: {self.original_image.width}x{self.original_image.height}")
        print(f"Compressed dimensions: {self.processed_image.width}x{self.processed_image.height}")
        print(f"Original size: {original_size:.2f} KB")
        print(f"Compressed size: {compressed_size:.2f} KB")
        print(f"Compression ratio: {ratio:.2f}%")

        return ratio

    def find_file_size(self, image):
        temp_buffer = io.BytesIO()
        image.save(temp_buffer, format="PNG")
        size_bytes = temp_buffer.getbuffer().nbytes
        return size_bytes / 1024
    
    def convert_format(self, output_format):
        if not self.original_image:
            return
        
        if output_format == 'jpg' or output_format == 'jpeg':
            self.processed_image = self.original_image.convert("RGB")
        elif output_format == 'png':
            self.processed_image = self.original_image.convert("RGBA")
        elif output_format == 'webp':
            output = io.BytesIO()
            self.original_image.save(output, format="WEBP")
            output.seek(0)
            self.processed_image = Image.open(output)
        elif output_format == 'base64':
            buffered = io.BytesIO()
            self.original_image.save(buffered, format="PNG")
            self.processed_image = base64.b64encode(buffered.getvalue()).decode()
        else:
            print(f"Unsupported output format: {output_format}")
            sys.exit(1)

    def extract_alpha_channel(self, color):
        if not self.original_image:
            return
        
        if self.original_image.mode != 'RGBA':
            image = self.original_image.convert('RGBA')
        else:
            image = self.original_image

        data = np.array(image)
        r, g, b = [int(color[i:i+2], 16) for i in (0, 2, 4)]

        alpha = data[:, :, 3]
        rgb = np.zeros_like(data[:, :, :3])
        rgb[alpha == 0] = [r, g, b]
        rgb[alpha > 0] = [0, 0, 0]

        extracted = np.concatenate((rgb, np.expand_dims(255 - alpha, axis=2)), axis=2)
        self.processed_image = Image.fromarray(extracted.astype('uint8'), 'RGBA')

    def analyze_png(self):
        if not self.original_image:
            return
        
        analysis = f"Image Mode: {self.original_image.mode}\n"
        analysis += f"Image Size: {self.original_image.size}\n"
        analysis += f"Image Format: {self.original_image.format}\n"

        if 'dpi' in self.original_image.info:
            analysis += f"DPI: {self.original_image.info['dpi']}\n"

        if 'icc_profile' in self.original_image.info:
            analysis += "ICC Profile: Present\n"

        if 'exif' in self.original_image.info:
            analysis += "EXIF Data: Present\n"

        self.processed_image = analysis
        print(analysis)

    def find_png_file_size(self):
        if not self.original_image:
            return

        temp_buffer = io.BytesIO()
        self.original_image.save(temp_buffer, format="PNG")
        size_bytes = temp_buffer.getbuffer().nbytes

        if size_bytes < 1024:
            result = f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            result = f"{size_bytes / 1024:.2f} KB"
        else:
            result = f"{size_bytes / (1024 * 1024):.2f} MB"

        self.processed_image = result
        print(result)

    def find_png_color_count(self):
        if not self.original_image:
            return
        
        img_data = np.array(self.original_image)

        if len(img_data.shape) == 2:
            unique_colors = np.unique(img_data.reshape(-1))
            total_colors = len(unique_colors)
            grayscale_count = total_colors
            transparent_count = translucent_count = 0
            opaque_count = total_colors
        else:
            channels = img_data.shape[-1]
            unique_colors = np.unique(img_data.reshape(-1, channels), axis=0)
            total_colors = len(unique_colors)

            if channels >= 3:
                grayscale = np.all(unique_colors[:, 0] == unique_colors[:, 1]) & np.all(unique_colors[:, 1] == unique_colors[:, 2])
                grayscale_count = np.sum(grayscale)
            else:
                grayscale_count = total_colors if channels == 1 else 0

            if channels == 4:
                transparent = unique_colors[:, 3] == 0
                translucent = (unique_colors[:, 3] > 0) & (unique_colors[:, 3] < 255)
                opaque = unique_colors[:, 3] == 255
                transparent_count = np.sum(transparent)
                translucent_count = np.sum(translucent)
                opaque_count = np.sum(opaque)
            else:
                transparent_count = translucent_count = 0
                opaque_count = total_colors

        result = f"Unique Color Count:\n-------------------\n"
        result += f"Unique colors: {total_colors} (100%)\n"
        result += f"Unique grayscale colors: {grayscale_count} ({grayscale_count/total_colors:.2%})\n"

        if hasattr(img_data, 'shape') and len(img_data.shape) > 2 and img_data.shape[-1] == 4:
            result += f"Unique transparent colors: {transparent_count} ({transparent_count/total_colors:.2%})\n"
            result += f"Unique translucent colors: {translucent_count} ({translucent_count/total_colors:.2%})\n"
            result += f"Unique opaque colors: {opaque_count} ({opaque_count/total_colors:.2%})"
        else:
            result += f"Unique opaque colors: {opaque_count} ({opaque_count/total_colors:.2%})"

        self.processed_image = result
        print(result)

    def rotate_png(self, angle):
        if not self.original_image:
            return
        
        self.processed_image = self.original_image.rotate(
            angle, resample=Image.BICUBIC, expand=True
        )

    def skew_png(self, h_angle, v_angle):
        if not self.original_image:
            return
        
        width, height = self.original_image.size

        h_angle = (h_angle / 100.0) * 45
        v_angle = (v_angle / 100.0) * 45

        new_width = int(width + height * math.tan(math.radians(abs(h_angle))))  # Absolute value used to remove negative angle during calculation
        new_height = int(height + width * math.tan(math.radians(abs(v_angle))))
        skew_matrix = [1, math.tan(math.radians(h_angle)), 0, math.tan(math.radians(v_angle)), 1, 0]
        self.processed_image = self.original_image.transform((new_width, new_height), Image.AFFINE, skew_matrix, Image.BICUBIC)

    def mirror_png(self, flip_horizontal, flip_vertical):
        if not self.original_image:
            return
        
        image = self.original_image.copy()
        if flip_horizontal:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
        if flip_vertical:
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
        self.processed_image = image

    def add_text_to_png(self, text, color, font_size, bold, italic, x, y):
        if not self.original_image:
            return
        
        img = self.original_image.copy()
        draw = ImageDraw.Draw(img)

        color_rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

        try:
            font_style = ""
            if bold:
                font_style += "Bold"
            if italic:
                font_style += "Italic"

            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                    print("Warning: Could not load font, using default")

            draw.text((x, y), text, font=font, fill=color_rgb)
        except Exception as e:
            print(f"Error adding text: {e}")
            draw.text((x, y), text, fill=color_rgb)
        
        self.processed_image = img

    def pixelate_png(self, pixel_size):
        if not self.original_image:
            return
        
        small = self.original_image.resize((self.original_image.width // pixel_size, self.original_image.height // pixel_size), Image.NEAREST)
        self.processed_image = small.resize(self.original_image.size, Image.NEAREST)

    def blur_png(self, blur_radius):
        if not self.original_image:
            return
        
        self.processed_image = self.original_image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
                                                          
    def pick_png_color(self, x, y):
        if not self.original_image:
            return
        
        if x < 0 or y < 0 or x >= self.original_image.width or y >= self.original_image.height:
            print(f"Error: Coordinates ({x}, {y}) are outside image dimensions ({self.original_image.width}, {self.original_image.height})")
            sys.exit(1)

        img = self.original_image.convert("RGBA")
        pixel = img.getpixel((x, y))

        if len(pixel) == 4:
            r, g, b, a = pixel
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            result = f"Color at ({x}, {y}):\nRGBA: ({r}, {g}, {b}, {a})\nHex: {hex_color}\nOpacity: {a/255:.2%}"

        else:
            r, g, b = pixel
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            result = f"Color at ({x}, {y}):\nRGB: ({r}, {g}, {b})\nHex: {hex_color}"
        

        self.processed_image = result
        print(result)

    def split_png_rgba(self, output_path):
        if not self.original_image:
            return
        
        img = self.original_image.convert("RGBA")
        r, g, b, a = img.split()

        output_base, output_ext = os.path.splitext(output_path)

        r_bg = Image.new('RGB', img.size, (0, 0, 0))
        g_bg = Image.new('RGB', img.size, (0, 0, 0))
        b_bg = Image.new('RGB', img.size, (0, 0, 0))
        a_bg = Image.new('L', img.size, 0)

        r_img = Image.merge('RGB', (r, Image.new('L', img.size, 0), Image.new('L', img.size, 0)))
        g_img = Image.merge('RGB', (Image.new('L', img.size, 0), g, Image.new('L', img.size, 0)))
        b_img = Image.merge('RGB', (Image.new('L', img.size, 0), Image.new('L', img.size, 0), b))

        r_img.save(f"{output_base}_R{output_ext}")
        g_img.save(f"{output_base}_G{output_ext}")
        b_img.save(f"{output_base}_B{output_ext}")
        a.save(f"{output_base}_A{output_ext}")

        print(f"RGBA components saved as {output_base}_R/G/B/A{output_ext}")
        self.processed_image = self.original_image.copy()

    def center_png(self):
        if not self.original_image:
            return
        
        img = self.original_image.convert("RGBA")
        alpha = img.getchannel('A')

        bbox = alpha.getbbox()
        if not bbox:
            self.processed_image = img
            return
        
        object_img = img.crop(bbox)

        obj_width, obj_height = object_img.size
        img_width, img_height = img.size
        left = (img_width - obj_width) // 2
        top = (img_height - obj_height) // 2
        new_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        new_img.paste(object_img, (left, top))
        self.processed_image = new_img

    def add_border(self, thickness, color="000000"):
        if not self.original_image:
            return
        
        img = self.original_image.convert("RGBA")
        width, height = img.size
        border_color = tuple(int(color[i:i+2], 16) for i in (0, 2, 4)) + (255,)
        new_width = width + 2 * thickness
        new_height = height + 2 * thickness
        new_img = Image.new('RGBA', (new_width, new_height), border_color)
        new_img.paste(img, (thickness, thickness), img)
        self.processed_image = new_img

    def round_corners(self, cornerradius=None, tl=None, tr=None, bl=None, br=None):
        if not self.original_image:
            return
        
        img = self.original_image.convert("RGBA")
        width, height = img.size
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)

        if cornerradius is not None:
            tl = tr = bl = br = cornerradius
        else:
            tl = tl or 0
            tr = tr or 0
            bl = bl or 0
            br = br or 0

        draw.rectangle([(tl, 0), (width - tr, height)], fill=255)
        draw.rectangle([(0, tl), (width, height - bl)], fill=255)

        if tl > 0:
            draw.pieslice([(0, 0), (tl * 2, tl * 2)], 180, 270, fill=255)
        if tr > 0:
            draw.pieslice([(width - tr * 2, 0), (width, tr * 2)], 270, 0, fill=255)
        if bl > 0:
            draw.pieslice([(0, height - bl * 2), (bl * 2, height)], 90, 180, fill=255)
        if br > 0:
            draw.pieslice([(width - br * 2, height - br * 2), (width, height)], 0, 90, fill=255)

        result = Image.new('RGBA', img.size, (0, 0, 0, 0))
        result.paste(img, (0, 0), mask)
        self.processed_image = result

    def multiply_png(self, x_times, y_times):
        if not self.original_image:
            return
        
        try:
            x_times = int(x_times) if x_times is not None else 1
            y_times = int(y_times) if y_times is not None else 1
        except (ValueError, TypeError):
            print("Error: x_times and y_times must be valid integers")
            sys.exit(1)

        if x_times < 1 and y_times < 1:
            print("Error: At least one of x_times or y_times must be 1 or greater")
            sys.exit(1)

        img = self.original_image.convert("RGBA")
        width, height = img.size

        x_times = max(1, x_times)
        y_times = max(1, y_times)

        new_width = width * x_times
        new_height = height * y_times
        new_img = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))

        for y in range(y_times):
            for x in range(x_times):
                new_img.paste(img, (x * width, y * height), img)

        self.processed_image = new_img

    def trim_png(self):
        if not self.original_image:
            return
        
        img = self.original_image.convert("RGBA")
        alpha = img.getchannel('A')
        bbox = alpha.getbbox()

        if not bbox:
            self.processed_image = img
            return
        
        self.processed_image = img.crop(bbox)

    def hide_text(self, message):
        if not self.original_image:
            return
            
        img = self.original_image.convert("RGBA")
        message_bytes = message.encode('utf-8')
        message_bytes += b'\x00'
        width, height = img.size
        max_bytes = width * height * 3 // 8
        if len(message_bytes) > max_bytes:
            print(f"Error: Message too long for this image. Maximum size: {max_bytes} bytes")
            sys.exit(1)
        pixels = list(img.getdata())
        pixel_array = list(pixels)
        message_bits = ''.join([format(byte, '08b') for byte in message_bytes])
        bit_index = 0
        
        for i in range(len(pixel_array)):
            if bit_index >= len(message_bits):
                break
                
            r, g, b, a = pixel_array[i]
            if bit_index < len(message_bits):
                r = (r & ~1) | int(message_bits[bit_index])
                bit_index += 1
            
            if bit_index < len(message_bits):
                g = (g & ~1) | int(message_bits[bit_index])
                bit_index += 1
            
            if bit_index < len(message_bits):
                b = (b & ~1) | int(message_bits[bit_index])
                bit_index += 1
            
            pixel_array[i] = (r, g, b, a)
        
        new_img = Image.new('RGBA', img.size)
        new_img.putdata(pixel_array)
        self.processed_image = new_img

    def extract_hidden_text(self):
        if not self.original_image:
            return
            
        img = self.original_image.convert("RGBA")
        pixels = list(img.getdata())
        extracted_bits = ''
        for r, g, b, a in pixels:
            extracted_bits += str(r & 1)
            extracted_bits += str(g & 1)
            extracted_bits += str(b & 1)
        
        extracted_bytes = bytearray()
        for i in range(0, len(extracted_bits), 8):
            if i + 8 <= len(extracted_bits):
                byte = int(extracted_bits[i:i+8], 2)
                if byte == 0:
                    break
                extracted_bytes.append(byte)
        
        try:
            message = extracted_bytes.decode('utf-8')
            result = f"Extracted message: {message}"
        except UnicodeDecodeError:
            result = "No valid UTF-8 message found or message is corrupted."
        
        self.processed_image = result
        print(result)

def print_usage():
    usage = """
Usage: pngtools -i <input.png> -o <output.png> -p <operation> [options]

Required Arguments:
    -i, --input <file>          Input PNG file
    -o, --output <file>         Output PNG file (not required for info commands)
    -p, --process <operation>   Processing operation to perform on input image

    
Processing Operations:
    transparent         Remove a specific color, making it transparent
        --color <hex>           Color to make transparent (without #)
        --tolerance <percent>   Similar color tolerance (0-100)

    swap-color          Replace one color with another
        --from <hex>            Color to replace (without #)
        --to <hex>              Replacement color (without #)
        --tolerance <percent>   Similar color tolerance (0-100)

    color-tone          Convert all colors to a single tone
        --color <hex>           Target color (without #)

    opacity             Adjust the opacity of the PNG
        --level <percent>       Opacity level (0-100)

    noise               Add noise to the PNG
        --amount <percent>      Noise intensity (0-100)
        --tolerance <percent>   (Optional) Color similarity for noise

    compress            Compress the PNG file
        --level <percent>       Target compression level (0-100)

    convert             Convert image format (png, jpg, webp, base64)
                        Automatically detects format from input and output filename
    
    alpha-extract       Extract alpha channel as a silhouette
        -color <hex>            Silhouette color (without #)

    rotate              Rotate the PNG
        --angle <degrees>       Rotation angle (0-360)

    skew                Skew the PNG along X and/or Y axis
        --x <percent>           Skew amount along X-axis
        --y <percent>           Skew amount along Y-axis

    mirror              Mirror (flip) the PNG
        --horizontal            Flip horizontally
        --vertical              Flip vertically

    text                Add text to the PNG
        --text "<string>"       Text content (in quotes)
        --color <hex>           Text color (without #)
        --size <px>             Font size (in px)
        --bold                  (Optional) Bold text
        --italic                (Optional) Italic text
        --x <px>                X position
        --y <px>                Y position

    pixelate            Pixelate the PNG
        --size <px>             Pixel block size

    blur
        --radius <px>           Blur radius
    
    split-rgba          Split PNG into RGBA components
                        Outputs: <name>_R.png, <name>_G.png, etc.

    center              Center object within a transparent PNG

    border              Add a border around the PNG
        --thickness <px>        Border thickness in pixels
        --color <hex>           Border color (without #)

    round-corners       Round PNG corners (choose one mode)
        (Option 1)              Uniform radius for all corners
        --cornerradius <px>     Corner radius in px

        (Option 2)              Different radius for each corner
        --tl <px>               Corrner radius of top left corner
        --tr <px>               Corrner radius of top right corner
        --bl <px>               Corrner radius of bottom left corner
        --br <px>               Corrner radius of bottom right corner

    multiply            Duplicate the PNG
        --x <n>                 Times to repeat horizontally
        --y <n>                 Times to repeat vertically

    trim                Remove transparent space around object in PNG

    hide-text           Hide a secret message inside the PNG
        --message "<string>"    Message to conceal (in quotes)

        
Information Commands (No output file required):
    analyze             Analyze the PNG file (basic metadata)
    size                Get PNG file size
    color-count         Count the number of unique colors in the PNG
    extract-hidden-text Extract hidden text from PNG
    pick-color          Get color at specific coordinates
        --x <px>                X cooridnate
        --y <px>                Y coordinate
"""

    print(usage)

def main_cli():
    if len(sys.argv) == 1:
        print_usage()
        sys.exit(1)

    parser = argparse.ArgumentParser(description='PNG manipulation tool', add_help=False)

    parser.add_argument('-h', '--help', action='store_true', help='Show this help message')
    parser.add_argument('-i', '--input', help='Input image file')
    parser.add_argument('-o', '--output', help='Output image file (not required for info commands)')
    parser.add_argument('-p', '--process', help='Processing operation to perform')

    args, _ = parser.parse_known_args()
    if args.help:
        print_usage()
        sys.exit(0)

    parser = argparse.ArgumentParser(description='PNG manipulation tool')
    parser.add_argument('-i', '--input', required=True, help='Input image file')
    parser.add_argument('-o', '--output', help='Output image file (not required for info commands)')
    parser.add_argument('-p', '--process', required=True, help='Processing operation to perform')

    parser.add_argument('--color', help='Color (hex without #)')
    parser.add_argument('--from', dest='from_color', help='Source color (hex without #)')
    parser.add_argument('--to', help='Target color (hex without #)')
    parser.add_argument('--tolerance', type=float, default=10, help='Color tolerance (0-100)')
    parser.add_argument('--level', type=float, help='Level for various operations (0-100)')
    parser.add_argument('--amount', type=float, help='Amount for noise (0-100)')
    parser.add_argument('--angle', type=float, help='Rotation angle (0-360)')
    parser.add_argument('--x', type=float, help='X position or skew amount')
    parser.add_argument('--y', type=float, help='Y position or skew amount')
    parser.add_argument('--horizontal', action='store_true', help='Apply horizontal flip')
    parser.add_argument('--vertical', action='store_true', help='Apply vertical flip')
    parser.add_argument('--text', help='Text to add to image')
    parser.add_argument('--size', type=int, help='Size for font or pixels')
    parser.add_argument('--bold', action='store_true', help='Bold text')
    parser.add_argument('--italic', action='store_true', help='Italic text')
    parser.add_argument('--radius', type=float, help='Blur radius')
    parser.add_argument('--message', help='Message to hide in PNG')
    parser.add_argument('--thickness', type=int, help='Border thickness')
    parser.add_argument('--cornerradius', type=int, help='Corner radius')
    parser.add_argument('--tl', type=int, help='Top left corner radius')
    parser.add_argument('--tr', type=int, help='Top right corner radius')
    parser.add_argument('--bl', type=int, help='Bottom left corner radius')
    parser.add_argument('--br', type=int, help='Bottom right corner radius')

    try:
        args = parser.parse_args()
    except SystemExit:
        print_usage()
        sys.exit(1)

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' does not exist")
        print_usage()
        sys.exit(1)

    info_commands = ['analyze', 'size', 'color-count', 'pick-color', 'extract-hidden-text']
    if args.process not in info_commands and not args.output:
        print("Error: Output file is required for this operation")
        print_usage()
        sys.exit(1)

    tools = PNGTools()
    tools.load_image(args.input)

    if args.process == 'transparent':
        if not args.color:
            print("Error: --color is required for transparent operation")
            print_usage()
            sys.exit(1)
        tools.make_transparent(args.color, args.tolerance)

    elif args.process == 'swap-color':
        if not args.from_color or not args.to:
            print("Error: --from and --to colors are required for swap-color operation")
            print_usage()
            sys.exit(1)
        tools.swap_colors(args.from_color, args.to, args.tolerance)

    elif args.process == 'color-tone':
        if not args.color:
            print("Error: --color is required for color-tone operation")
            print_usage()
            sys.exit(1)
        tools.change_color_tone(args.color)

    elif args.process == 'opacity':
        if args.level is None:
            print("Error: --level is required for opacity operation")
            print_usage()
            sys.exit(1)
        tools.change_opacity(args.level)

    elif args.process == 'noise':
        if args.amount is None:
            print("Error: --amount is required for noise operation")
            print_usage()
            sys.exit(1)
        tools.add_noise(args.amount, args.tolerance if args.tolerance != 10 else None)

    elif args.process == 'compress':
        if args.level is None:
            print("Error: --level is required for compress operation")
            print_usage()
            sys.exit(1)
        tools.compress_png(args.level)

    elif args.process == 'convert':
        if not args.output:
            print("Error: output file is required for convert operation")
            print_usage()
            sys.exit(1)
        output_format = os.path.splitext(args.output)[1].lower()[1:]

        if output_format == 'txt' and args.input.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            output_format = 'base64'

        tools.convert_format(output_format)

    elif args.process == 'alpha-extract':
        if not args.color:
            print("Error: --color is required for alpha-extract operation")
            print_usage()
            sys.exit(1)
        tools.extract_alpha_channel(args.color)

    elif args.process == 'analyze':
        tools.analyze_png()

    elif args.process == 'size':
        tools.find_png_file_size()

    elif args.process == 'color-count':
        tools.find_png_color_count()

    elif args.process == 'rotate':
        if args.angle is None:
            print("Error: --angle is required for rotate operation")
            print_usage()
            sys.exit(1)
        tools.rotate_png(args.angle)

    elif args.process == 'skew':
        if args.x is None and args.y is None:
            print("Error: at least one of --x or --y is required for skew operation")
            print_usage()
            sys.exit(1)
        tools.skew_png(args.x or 0, args.y or 0)
    
    elif args.process == 'mirror':
        tools.mirror_png(args.horizontal, args.vertical)

    elif args.process == 'text':
        if not args.text or not args.color or args.size is None:
            print("Error: --text, --color, and --size are required for text operation")
            print_usage()
            sys.exit(1)
        tools.add_text_to_png(args.text, args.color, args.size, args.bold, args.italic, args.x or 0, args.y or 0)

    elif args.process == 'pixelate':
        if args.size is None:
            print("Error: --size is required for pixelate operation")
            print_usage()
            sys.exit(1)
        tools.pixelate_png(args.size)

    elif args.process == 'blur':
        if args.radius is None:
            print("Error: --radius is required for blur operation")
            print_usage()
            sys.exit(1)
        tools.blur_png(args.radius)

    elif args.process == 'pick-color':
        if args.x is None or args.y is None:
            print("Error: --x and --y coordinates are required for pick-color operation")
            print_usage()
            sys.exit(1)
        tools.pick_png_color(int(args.x), int(args.y))

    elif args.process == 'split-rgba':
        if not args.output:
            print("Error: output file is required for split-rgba operation")
            print_usage()
            sys.exit(1)
        tools.split_png_rgba(args.output)

    elif args.process == 'center':
        tools.center_png()

    elif args.process == 'border':
        if args.thickness is None:
            print("Error: --thickness is required for border operation")
            print_usage()
            sys.exit(1)
        tools.add_border(args.thickness, args.color or "000000")

    elif args.process == 'round-corners':
        if args.cornerradius is not None:
            tools.round_corners(cornerradius=args.cornerradius)
        elif args.tl is not None or args.tr is not None or args.bl is not None or args.br is not None:
            tools.round_corners(tl=args.tl, tr=args.tr, bl=args.bl, br=args.br)
        else:
            print("Error: either --cornerradius or corner-specific radii are required for round-corners operation")
            print_usage()
            sys.exit(1)

    elif args.process == 'multiply':
        if args.x is None and args.y is None:
            print("Error: at least one of --x or --y is required for multiply operation")
            print_usage()
            sys.exit(1)
        tools.multiply_png(args.x or 1, args.y or 1)

    elif args.process == 'trim':
        tools.trim_png()

    elif args.process == 'hide-text':
        if not args.message:
            print("Error: --message is required for hide-text operation")
            print_usage()
            sys.exit(1)
        tools.hide_text(args.message)

    elif args.process == 'extract-hidden-text':
        tools.extract_hidden_text()

    else:
        print(f"Error: Unknown operation '{args.process}'")
        print_usage()
        sys.exit(1)

    if args.process not in info_commands and args.output:
        tools.save_image(args.output)

if __name__ == "__main__":
    main_cli()