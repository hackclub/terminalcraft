import os

def api_key():
    API_KEY = os.getenv("API_KEY")
    if not API_KEY:
        print("Your API key is missing. Please set it in your .env file using:")
        print("    python main.py config api_key YOUR_API_KEY")
        exit(1)
    return API_KEY

def base_url():
    BASE_URL = os.getenv("BASE_URL")
    if not BASE_URL:
        print("There is no base API URL set. Please set it in your .env file")
        exit(1)
    return BASE_URL

def img_url():
    IMG_URL = os.getenv("IMG_URL")
    if not IMG_URL:
        print("There is no API URL (for images) set. Please add it in your .env file")
        exit(1)
    return IMG_URL

def region():
    REGION = os.getenv("REGION")
    if not REGION:
        print("There is no region set. Please add it in your .env file")
        exit(1)
    return REGION