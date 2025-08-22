import os
import requests
from pathlib import Path

TILE_DIR = Path("./tiles")
TILE_DIR.mkdir(exist_ok=True)

def tile_filename(lat, lon):
    ns = 'n' if lat >= 0 else 's'
    ew = 'e' if lon >= 0 else 'w'
    return f"{ns}{abs(lat):02d}_{ew}{abs(lon):03d}_1arc_v3.tif"

def local_tile_path(lat, lon):
    return TILE_DIR / tile_filename(lat, lon)

def download_tile(lat, lon):
    """Attempts to download a DEM tile from NASA Earthdata or other source."""
    path = local_tile_path(lat, lon)
    if path.exists():
        return str(path)

    # Example source: this is a placeholder; replace with real download URL
    filename = tile_filename(lat, lon)
    url = f"https://your-tile-server.org/tiles/{filename}"

    print(f"Downloading {filename} from {url}...")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(path, "wb") as f:
                f.write(response.content)
            print(f"Saved to {path}")
            return str(path)
        else:
            print(f"Failed to download tile: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading tile: {e}")
        return None
