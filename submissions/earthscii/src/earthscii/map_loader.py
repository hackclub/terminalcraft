"""Load a DEM file and convert it to a list of 3D points."""
import rasterio


def load_tile_at(lat, lon):
    """Load a tile at the given latitude and longitude."""
    fname = f"data/n{lat:02d}_w{abs(lon):03d}_1arc_v3.tif"
    return load_dem_as_points(fname)


def load_dem_as_points(path, stride=16, z_scale=0.5, transformable=True):
    """
    Load a DEM file (GeoTIFF) and convert it to a list of 3D points.

    stride: downsample factor for performance
    """
    with rasterio.open(path) as dataset:
        elevation = dataset.read(1)
        transform = dataset.transform
        width = elevation.shape[1]
        height = elevation.shape[0]

        # mask out nodata values
        valid = elevation != dataset.nodata

        points = []
        for y in range(0, height, stride):
            row = []
            for x in range(0, width, stride):
                z = elevation[y][x]
                if z == dataset.nodata:
                    continue
                row.append((x, y, z * z_scale))
            if row:
                points.append(row)

        return (points, transform) if transformable else points
