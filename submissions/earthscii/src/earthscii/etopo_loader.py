import rasterio
import math

EARTH_RADIUS = 6371000  # meters


def latlon_to_xyz(lat, lon, elevation):
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    r = EARTH_RADIUS + elevation
    x = r * math.cos(lat_rad) * math.cos(lon_rad)
    y = r * math.cos(lat_rad) * math.sin(lon_rad)
    z = r * math.sin(lat_rad)
    return (x, y, z)


def load_etopo_as_sphere_points(path, stride=32, z_scale=1.0):
    """
    Convert a GeoTIFF file to a list of 3D sphere points.

    Args
    ----
    path: path to GeoTIFF file
    stride: sampling stride in pixels
    z_scale: scale factor for exaggerating elevation

    Returns
    -------
    points: list of 3D sphere points

    """
    points = []

    with rasterio.open(path) as dataset:
        elevation = dataset.read(1)
        transform = dataset.transform
        nodata = dataset.nodata
        height, width = elevation.shape

        for y in range(0, height, stride):
            for x in range(0, width, stride):
                z = elevation[y][x]
                if z == nodata:
                    continue
                lon, lat = rasterio.transform.xy(transform, y, x)
                p = latlon_to_xyz(lat, lon, z * z_scale)
                points.append(p)

    return points
