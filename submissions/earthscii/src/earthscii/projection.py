#projection.py
"""Basic isometric projection with Y-axis rotation."""
import math
import numpy as np


def rotate_xyz(x, y, z, angle_x, angle_y, angle_z):
    """Apply 3D rotation around X, Y, then Z."""
    # Convert to radians
    ax = math.radians(angle_x)
    ay = math.radians(angle_y)
    az = math.radians(angle_z)

    # Rotate around X
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + \
        z * math.cos(ax)

    # Rotate around Y
    x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + \
        z * math.cos(ay)

    # Rotate around Z
    x, y = x * math.cos(az) - y * math.sin(az), x * math.sin(az) + \
        y * math.cos(az)

    return x, y, z


def project_map(map_data, angle_x=0, angle_y=0, angle_z=0, zoom=1.0,
                offset_x=0, offset_y=0, aspect_ratio=0.5):
    projected = []

    # Convert angles to radians
    ax = math.radians(angle_x)
    ay = math.radians(angle_y)
    az = math.radians(angle_z)

    # Compute forward vector (orbit camera in spherical coords)
    fx = math.cos(ay) * math.cos(ax)
    fy = math.sin(ax)
    fz = math.sin(ay) * math.cos(ax)
    forward = np.array([fx, fy, fz])
    forward /= np.linalg.norm(forward)

    # Up vector (world up)
    world_up = np.array([0, 1, 0])

    # Right = up × forward
    right = np.cross(world_up, forward)
    right /= np.linalg.norm(right)

    # Recomputed up = forward × right
    up = np.cross(forward, right)

    # Get center of map
    all_points = [p for row in map_data for p in row]
    cx = sum(p[0] for p in all_points) / len(all_points)
    cy = sum(p[1] for p in all_points) / len(all_points)
    cz = sum(p[2] for p in all_points) / len(all_points)
    center = np.array([cx, cy, cz])

    for row in map_data:
        for x, y, z in row:
            point = np.array([x, y, z]) - center

            # Project point onto screen axes
            sx = int(np.dot(point, right) * zoom) + offset_x
            sy = int(np.dot(point, up) * zoom * aspect_ratio) + offset_y
            sz = np.dot(point, forward)

            # Apply post-projection Z rotation to screen coords
            if angle_z != 0:
                theta = math.radians(angle_z)
                cos_z = math.cos(theta)
                sin_z = math.sin(theta)
                dx = sx - offset_x
                dy = sy - offset_y
                sx = int(dx * cos_z - dy * sin_z + offset_x)
                sy = int(dx * sin_z + dy * cos_z + offset_y)

            projected.append((sx, sy, z))

    return projected
