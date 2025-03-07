import os
import cv2
import sys
import yt_dlp
import re
from .clear_terminal import clear_terminal

def decode():
    clear_terminal()
    inp = str(input("Decode from an URL/Path (1/2/Exit): "))
    
    video_path = None
    downloaded_file = None

    if inp == "1":
        video_url = input("Enter the URL of the video: ")
        
        os.makedirs("Data/temp", exist_ok=True)
        
        ydl_opts = {
            "format": "best",
            "outtmpl": "Data/temp/%(title)s.%(ext)s",
            "quiet": False,
            "no_warnings": False
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            if 'entries' in info:
                info = info['entries'][0]
            
            title = info.get('title', 'video')
            ext = info.get('ext', 'mp4')
            downloaded_file = f"Data/temp/{title}.{ext}"
            video_path = downloaded_file
            
            print(f"Downloaded video to: {video_path}")
            
    elif inp == "2":
        video_path = input("Enter the path of the video: ")
    else:
        sys.exit(0)
    
    if not video_path or not os.path.exists(video_path):
        print(f"Error: Video file not found at path: {video_path}")
        return
    
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print(f"Error: OpenCV could not open video file: {video_path}")
        return
    
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    ppf = width * height

    print("Decoding...")
    print(f"Video dimensions: {width}x{height}")
    print(f"Total frames: {frame_count}")

    data = []

    for frame_idx in range(frame_count):
        success, frame = video.read()
        if not success:
            print(f"Error: Could not read frame {frame_idx}.")
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        _, binary_frame = cv2.threshold(gray_frame, 127, 1, cv2.THRESH_BINARY_INV)

        for row in range(height):
            for col in range(width):
                if row * width + col < width * height:
                    data.append(str(binary_frame[row, col]))

        print(f"Progress: {frame_idx + 1}/{frame_count} frames ({(frame_idx + 1) * 100 // frame_count}%)")
    video.release()

    data_string = ''.join(data)
    
    total_bits_needed = frame_count * ppf
    
    if len(data_string) > total_bits_needed:
        data_string = data_string[:total_bits_needed]
    
    last_one_index = data_string.rfind('1')
    if last_one_index == -1:
        print("Error: No valid data found in the video.")
        return
    
    data_string = data_string[:last_one_index + 1]
    
    print(f"Total data bits: {len(data_string)}")
    
    extension = ""
    if len(data_string) >= 32:
        extension_bits = data_string[-32:]
        data_string = data_string[:-32]
        
        print(f"Extension bits: {extension_bits}")
        
        for i in range(0, 32, 8):
            if i + 8 <= len(extension_bits):
                char_bits = extension_bits[i:i+8]
                try:
                    char_value = int(char_bits, 2)
                    if char_value > 0:
                        if 32 <= char_value <= 126:
                            extension += chr(char_value)
                        else:
                            print(f"Skipping non-printable character: {char_value}")
                except ValueError as e:
                    print(f"Error parsing binary: {e}")
        
        hash_padding_count = 0
        while extension.endswith('#') and hash_padding_count < 3:
            extension = extension[:-1]
            hash_padding_count += 1
            
    extension = re.sub(r'[^a-zA-Z0-9.]', '', extension)
    
    if not extension or len(extension) > 10:
        extension = "txt"
    
    extension = "." + extension
    
    print(f"Detected file extension: {extension}")
    
    byte_chunks = [data_string[i:i+8] for i in range(0, len(data_string), 8)]

    if len(byte_chunks) > 0 and len(byte_chunks[-1]) < 8:
        byte_chunks.pop()

    decoded_bytes = bytearray()
    for chunk in byte_chunks:
        try:
            decoded_bytes.append(int(chunk, 2))
        except ValueError:
            continue

    os.makedirs("Data/outputs", exist_ok=True)

    output_name = input("Enter the name for the output file (without extension): ")
    output_path = f"Data/outputs/{output_name}{extension}"
    
    try:
        with open(output_path, "wb") as file:
            file.write(decoded_bytes)
        print(f"Decoding complete. File saved as {output_path}")
    except OSError as e:
        safe_path = f"Data/outputs/{output_name}.bin"
        print(f"Error saving with detected extension: {str(e)}")
        print(f"Saving with .bin extension instead")
        with open(safe_path, "wb") as file:
            file.write(decoded_bytes)
        print(f"Decoding complete. File saved as {safe_path}")

    if downloaded_file and os.path.exists(downloaded_file):
        try:
            os.remove(downloaded_file)
            print(f"Removed temporary file: {downloaded_file}")
        except Exception as e:
            print(f"Warning: Could not remove temporary file: {e}")
        
    print()
    inp = input("Press Enter to continue: ")