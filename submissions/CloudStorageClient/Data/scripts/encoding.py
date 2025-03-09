import os
import cv2
import numpy as np
from .clear_terminal import clear_terminal

from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_youtube_service():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    client_secret_path = os.path.join(script_dir, "..", "client_secret.json")

    flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
    credentials = flow.run_local_server(port=0)
    return build("youtube", "v3", credentials=credentials)

class YouTubeAPI:
    def __init__(self, youtube):
        self.youtube = youtube
        
    def upload_video(self, file_path, title, description, category_id, privacy_status='unlisted'):
        print(f"Attempting to upload file at: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status
            }
        }

        media = MediaFileUpload(file_path, resumable=True)

        request = self.youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )

        response = request.execute()
        return response

def encode():
    youtube = get_youtube_service()
    clear_terminal()
    file_path = input("Enter the path of the file: ")

    if not os.path.exists(file_path):
        print("Error: File not found.")
        return

    base_name = os.path.basename(file_path)
    name_without_ext, file_extension = os.path.splitext(base_name)
    file_extension = file_extension.lower()[1:]

    frames_per_data_frame = 5

    clear_terminal()

    width, height = 2560, 1440
    ppf = width * height
    fps = 60
    output_filename = f"{name_without_ext}.mp4"
    
    os.makedirs("Data/outputs", exist_ok=True)
    
    output_path = os.path.join("Data/outputs", output_filename)
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    file_size = os.path.getsize(file_path)
    bytes_per_frame = ppf // 8

    total_data_frames = (file_size * 8 + ppf - 1) // ppf
    total_video_frames = total_data_frames * frames_per_data_frame
    
    print(f"Encoding {file_size} bytes into {total_data_frames} unique data frames.")
    print(f"Each frame will be repeated {frames_per_data_frame} times.")
    print(f"Total video frames: {total_video_frames}")

    with open(file_path, "rb") as file:
        for frame_idx in range(total_data_frames):
            frame = np.ones((height, width), dtype=np.uint8) * 255 

            chunk = file.read(bytes_per_frame)
            if not chunk:
                break

            binary_data = ''.join(format(byte, '08b') for byte in chunk)
            binary_data = binary_data.ljust(ppf, '0')

            for i, bit in enumerate(binary_data):
                row, col = divmod(i, width)
                if bit == "1":
                    frame[row, col] = 0

            bgr_frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            
            for _ in range(frames_per_data_frame):
                video_writer.write(bgr_frame)
            
            print(f"Progress: {frame_idx + 1}/{total_data_frames} data frames "
                  f"({(frame_idx + 1) * frames_per_data_frame}/{total_video_frames} video frames) "
                  f"({(frame_idx + 1) * 100 // total_data_frames}%)")

    video_writer.release()
    print("Encoding complete.")

    absolute_output_path = os.path.abspath(output_path)
    print(f"Video saved to: {absolute_output_path}")
    print(f"Total frames in video: {total_data_frames * frames_per_data_frame}")
    print(f"Video duration: {total_video_frames / fps:.2f} seconds")

    try:
        yt_api = YouTubeAPI(youtube)
        upload = yt_api.upload_video(
            absolute_output_path, 
            name_without_ext, 
            file_extension,
            28  
        )
        print("Video upload complete.")
    except Exception as e:
        print(f"Error during upload: {str(e)}")

    print()
    inp = input("Press Enter to continue: ")
