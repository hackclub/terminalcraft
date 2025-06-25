import math
import numpy as np
from earthscii.utils import log


def project_globe(points, angle_x=0, angle_y=0, angle_z=0, zoom=1.0,
                  offset_x=0, offset_y=0, screen_width=80, screen_height=24,
                  aspect_ratio=0.5):
    log(f"[\033[32mINFO\033[0m] Projecting {len(points)} points")
    projected = []
    EARTH_RADIUS = 6371000  # in meters

    # Compute camera rotation
    ax = math.radians(angle_x)
    ay = math.radians(angle_y)
    az = math.radians(angle_z)

    # Camera forward vector
    fx = math.cos(ay) * math.cos(ax)
    fy = math.sin(ax)
    fz = math.sin(ay) * math.cos(ax)
    forward = np.array([fx, fy, fz])
    forward /= np.linalg.norm(forward)

    world_up = np.array([0, 1, 0])
    right = np.cross(world_up, forward)
    right /= np.linalg.norm(right)
    up = np.cross(forward, right)

    for p in points:
        rel = np.array(p)

        # Discard back-facing hemisphere
        if np.dot(forward, rel / np.linalg.norm(rel)) < 0:
            continue

        # Dynamic scale: map full screen width to ~2 Earth radii
        SCALE = (screen_width / (2 * EARTH_RADIUS)) / zoom

        sx = int(np.dot(rel, right)* SCALE) + offset_x
        sy = int(np.dot(rel, up) * SCALE * aspect_ratio) + offset_y
        sz = np.dot(rel, forward)
        projected.append((sx, sy, sz))
        if len(projected) < 5:
            log(f"[\033[96mPOINT\033[0m] sx={sx}, sy={sy}, sz={sz:.2f}")


    log(f"[\033[32mINFO\033[0m] Projected {len(projected)} front-facing points")
    return projected
