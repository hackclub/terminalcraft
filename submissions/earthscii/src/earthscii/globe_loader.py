import rasterio
import math

EARTH_RADIUS = 6371000  # meters

def latlon_to_xyz(lat, lon, elevation):
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    radius = EARTH_RADIUS + elevation
    x = radius * math.cos(lat_rad) * math.cos(lon_rad)
    y = radius * math.cos(lat_rad) * math.sin(lon_rad)
    z = radius * math.sin(lat_rad)
    return (x, y, z)


def load_tiles_as_sphere_points(paths, stride=16, z_scale=0.5):
    points = []

    for path in paths:
        with rasterio.open(path) as dataset:
            elevation = dataset.read(1)
            transform = dataset.transform
            width = elevation.shape[1]
            height = elevation.shape[0]
            nodata = dataset.nodata

            for y in range(0, height, stride):
                for x in range(0, width, stride):
                    z = elevation[y][x]
                    if z == nodata:
                        continue

                    lat, lon = rasterio.transform.xy(transform, y, x)
                    z_scaled = z * z_scale
                    p = latlon_to_xyz(lat, lon, z_scaled)
                    points.append(p)

    return points
