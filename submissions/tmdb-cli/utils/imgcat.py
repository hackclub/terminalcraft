import requests, tempfile, subprocess, os

def print(url):
    """Display images using imgcat"""
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return
        
        # Temporarily download the image to run through imgcat
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name
        
        subprocess.run(["imgcat", temp_file_path], check=False)
        
        # Remove the file we created
        os.remove(temp_file_path)
    except Exception as e:
        print(f"Error displaying image: {e}")
        exit(1)