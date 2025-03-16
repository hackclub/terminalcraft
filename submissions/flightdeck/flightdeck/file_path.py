import os

def get_full_path(file_path):
    try:
        full_path = os.path.abspath(file_path)
        return full_path
    except Exception as e:
        print(f"Error getting full path: {e}")
        return None