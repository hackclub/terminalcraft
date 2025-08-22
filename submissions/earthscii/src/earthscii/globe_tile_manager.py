import math
import shutil
import urllib.request
from pathlib import Path
from earthscii.etopo_loader import load_etopo_as_sphere_points
from earthscii.utils import log


TILE_DIR = Path("./tiles")
TILE_DIR.mkdir(parents=True, exist_ok=True)
PARTIAL_SUFFIX = ".partial"


def estimate_fov_from_screen(forward_vec, zoom, screen_width, screen_height,
                             aspect_ratio=0.5):
    """Estimate the angular field of view in degrees covered by the screen."""
    EARTH_RADIUS = 6371000  # meters
    screen_width_m = screen_width / zoom
    screen_height_m = screen_height / (zoom * aspect_ratio)

    # Convert visible width on screen (in meters) into angle at Earth's surface
    angular_width_deg = math.degrees(screen_width_m / EARTH_RADIUS)
    angular_height_deg = math.degrees(screen_height_m / EARTH_RADIUS)
    log(f"[\033[92mDEBUG\033[0m] FOV: {angular_width_deg:.2f}° x {angular_height_deg:.2f}°")
    return angular_width_deg, angular_height_deg


def etopo2022_filename(lat, lon):
    ns = 'N' if lat >= 0 else 'S'
    ew = 'E' if lon >= 0 else 'W'
    return f"ETOPO_2022_v1_15s_{ns}{abs(lat):02d}{ew}{abs(lon):03d}_surface.tif"


def download_etopo2022_tile(lat, lon):
    fname = etopo2022_filename(lat, lon)
    local_path = TILE_DIR / fname
    partial_path = local_path.with_suffix(local_path.suffix + PARTIAL_SUFFIX)

    if local_path.exists():
        return str(local_path)
    if partial_path.exists():
        print(f"Removing incomplete download: {partial_path}")
        partial_path.unlink()

    base_url = "https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/15s/15s_surface_elev_gtif/"
    url = base_url + fname
    print(f"Downloading {fname}...")
    try:
        with urllib.request.urlopen(url) as response:
            with open(partial_path, "wb") as out_file:
                shutil.copyfileobj(response, out_file)
            partial_path.rename(local_path)
            return str(local_path)
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        if partial_path.exists():
            partial_path.unlink()
    return None


def latlon_from_vector(v):
    x, y, z = v
    lat = math.degrees(math.asin(z / math.sqrt(x*x + y*y + z*z)))
    lon = math.degrees(math.atan2(y, x))
    return lat, lon


def vector_from_latlon(lat, lon):
    """Converts geographic coordinates to a 3D unit vector."""
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    x = math.cos(lat_rad) * math.cos(lon_rad)
    y = math.cos(lat_rad) * math.sin(lon_rad)
    z = math.sin(lat_rad)
    return x, y, z


def down_to_15(x): return (x // 15) * 15

def up_to_15(x): return ((x+14) // 15) * 15

def get_visible_tile_coords(forward_vec, fov_lat, fov_lon, padding):
    lat_center, lon_center = latlon_from_vector(forward_vec)

    lat_min = int(lat_center - fov_lat // 2) - padding
    lat_max = int(lat_center + fov_lat // 2) + padding
    lon_min = int(lon_center - fov_lon // 2) - padding
    lon_max = int(lon_center + fov_lon // 2) + padding

    lat_min = max(-85, lat_min)
    lat_max = min(85, lat_max)

    lat_min_aligned = down_to_15(lat_min)
    lat_max_aligned = up_to_15(lat_max)
    lon_min_aligned = down_to_15(lon_min)
    lon_max_aligned = up_to_15(lon_max)

    return [
        (lat, lon)
        for lat in range(lat_min_aligned, lat_max_aligned + 1, 15)
        for lon in range(lon_min_aligned, lon_max_aligned + 1, 15)
    ]


def load_visible_globe_points(forward_vec, zoom, screen_width, screen_height,
                              aspect_ratio=0.5):
    fov_horiz, fov_vert = estimate_fov_from_screen(forward_vec, zoom,
                                                   screen_width, screen_height,
                                                   aspect_ratio)
    tile_coords = get_visible_tile_coords(forward_vec, fov_vert, fov_horiz,
                                          padding=1)
    paths = []
    for lat, lon in tile_coords:
        path = download_etopo2022_tile(lat, lon)
        log(f"[\033[32mINFO\033[0m] Downloading tile: lat={lat}, lon={lon}")
        if path:
            paths.append(path)

    stride = compute_lod_stride(zoom)
    all_points = []
    for path in paths:
        try:
            points = load_etopo_as_sphere_points(path, stride=stride)
            if points is None:
                log(f"[\033[31mERROR\033[0m] No points returned from: {path}")
                continue
        except Exception as e:
            log(f"[\033[31mEXCEPTION\033[0m] Failed to load {path}: {e}")
            continue
        all_points.extend(points)

    log(f"[\033[92mDEBUG\033[0m] Looking for tiles near: {latlon_from_vector(forward_vec)}")
    log(f"[\033[92mDEBUG\033[0m] Tile coords to load: {tile_coords}")
    log(f"[\033[32mINFO\033[0m] Loaded {len(paths)} tile(s)")
    log(f"[\033[32mINFO\033[0m] Loaded {len(all_points)} points")

    if not all_points:
        log("[\033[91mFATAL\033[0m] No points to render!")
        raise RuntimeError("No terrain data loaded.")

    return all_points


def compute_lod_stride(zoom):
    log(f"[\033[92mDEBUG\033[0m] stride in use with zoom: {zoom}")
    if zoom > 3.0:
        return 2
    elif zoom > 2.0:
        return 4
    elif zoom > 1.0:
        return 8
    elif zoom > 0.5:
        return 16
    else:
        return 32
