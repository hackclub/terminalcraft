"""Display a 3D map in a terminal window."""
import curses
import time
import argparse
import numpy as np
import rasterio
import datetime
import traceback
import sys
from rasterio.transform import xy
from earthscii.projection import project_map
from earthscii.renderer import render_map
from earthscii.map_loader import load_dem_as_points
from earthscii.globe_projection import project_globe
from earthscii.globe_tile_manager import load_visible_globe_points
from earthscii.globe_tile_manager import vector_from_latlon
from earthscii.utils import log
from importlib.resources import files

def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("tile", nargs="?", help="Path to a local .tif DEM tile")
    parser.add_argument("--globe", action="store_true", help="Enable global view (janky for now)")
    parser.add_argument("--lat", type=float, help="Initial latitude—global view only")
    parser.add_argument("--lon", type=float, help="Initial longitude—global view only")
    parser.add_argument( "--aspect", type=float, default=None, help="Override aspect ratio (default: 0.5), to compensate for fonts being taller than they are wide")
    parser.add_argument("--demo", action="store_true", help="Run with a bundled demo tile")
    parser.add_argument("--tilewalk", action="store_true", help="Explore ETOPO tiles one at a time (requires internet)")
    parser.add_argument("--debug", action="store_true", help="Enable verbose debug output on crash")

    return parser, parser.parse_args()


def main_wrapper():
    """Entry point for pip-installed script"""
    # Parse command-line arguments

    parser, args = parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(1)

    curses.wrapper(lambda stdscr: main(stdscr, args))

def tilewalk_mode(stdscr, args):
    """Load and display tiles individually, allowing movemeent between them."""
    log("[\033[33mWARN\033[0m] tilewalk mode not yet implemented")
    time.sleep(2)
    raise KeyboardInterrupt()


def globe_mode(stdscr, args, angle_x, angle_y, zoom, width, height, aspect_ratio):
    """Run with a globe view"""
    if args.lat is not None and args.lon is not None:
        forward_vec = np.array(vector_from_latlon(args.lat, args.lon))

        # Derive angles from vector
        angle_x = int(np.degrees(np.arcsin(forward_vec[1])))  # pitch from y
        angle_y = int(np.degrees(np.arctan2( forward_vec[2], forward_vec[0])))  # yaw from z/x
    else:
        forward_vec = forward_from_angles(angle_x, angle_y)

        log(f"[\033[92mDEBUG\033[0m] forward_vec = {forward_vec}")
        log(f"[\033[92mDEBUG\033[0m] zoom = {zoom}, screen = {width}x{height}")

    globe_points = load_visible_globe_points(
        forward_vec, zoom, width, height, aspect_ratio
    )

    return forward_vec, angle_x, angle_y, globe_points


def single_tile_mode(stdscr, args):
    """Run with a single tile"""
    log("[\033[33mWARN\033[0m] single tile mode not yet implemented")
    time.sleep(2)
    raise KeyboardInterrupt()


def main(stdscr, args):
    log("[\033[32mINFO\033[0m] New session started\n------------")

    init_curses(stdscr)

    angle_x = 0
    angle_y = 90
    angle_z = 0
    height, width = stdscr.getmaxyx()
    aspect_ratio = args.aspect if args.aspect is not None else 0.5
    is_global = False

    zoom = 0.2

    offset_x, offset_y = width // 2, height // 2
    prev_state = None

    if args.tilewalk:
        tilewalk_mode(stdscr, args)
    elif args.globe:
        forward_vec, angle_x, angle_y, globe_points = globe_mode(
            stdscr, args, angle_x, angle_y, zoom, width, height, aspect_ratio
        )
        is_global = True
    else:
        try:
            if args.demo:
                # Load the bundled tile using importlib.resources
                demo_path = files("earthscii").joinpath("data/n37_w123_1arc_v3.tif")
                path = str(demo_path)
            elif args.tile:
                path = args.tile
            else:
                raise ValueError("You must provide a tile path or use --demo.")

            map_data, transform = load_dem_as_points(path)

            flat_points = [pt for row in map_data for pt in row]
            xs = [p[0] for p in flat_points]
            ys = [p[1] for p in flat_points]
            map_width = max(xs) - min(xs)
            map_height = max(ys) - min(ys)

            fudge_factor = 0.9
            zoom_x = width / map_width
            zoom_y = (height / map_height) * aspect_ratio
            zoom = min(zoom_x, zoom_y) * fudge_factor

        except FileNotFoundError:
            log(f"[\033[91mERROR\033[0m] File not found: {path}\n")
            fatal(stdscr, f"File not found: {path}")
            return

        except Exception as e:
            log(f"[\033[91mFATAL\033[0m] Error loading tile: {e}\n")
            fatal(stdscr, f"Failed to load tile '{path}': {e}", debug=args.debug, exception=e)
            return

        is_global = False

    buffer = curses.newwin(height, width, 0, 0)

    while True:
        try:
            key = stdscr.getch()

            angle_x, angle_y, angle_z, zoom, offset_x, offset_y, changed = handle_keys(
                key, angle_x, angle_y, angle_z, zoom, offset_x, offset_y
            )

            if changed:
                stdscr.refresh()
                if is_global:
                    forward_vec = forward_from_angles(angle_x, angle_y)
                    globe_points = load_visible_globe_points(
                        forward_vec, zoom, width, height, aspect_ratio
                    )


            state = (angle_x, angle_y, angle_z, zoom, offset_x, offset_y)

            if state != prev_state:
                buffer.erase()

                if is_global:
                    log(f"[\033[92mDEBUG\033[0m] angle_x = {angle_x}, angle_y = {angle_y}, angle_z = {angle_z}")
                    projected = project_globe(
                        globe_points,
                        angle_x, angle_y, angle_z,
                        zoom, offset_x, offset_y,
                        aspect_ratio=aspect_ratio
                    )

                else:
                    projected = project_map(
                        map_data,
                        angle_x, angle_y, angle_z,
                        zoom, offset_x, offset_y,
                        aspect_ratio=aspect_ratio
                    )

                render_map(buffer, projected)

                lon = lat = None

                if not is_global:
                    # display lat/lon of center
                    try:
                        # Approximate screen center in raster pixel coordinates
                        # (stride = 16)
                        lon, lat = xy(transform, (height // 2) * 16,
                                      (width // 2) * 16)
                    except:
                        pass

                elif is_global:
                    from earthscii.globe_tile_manager import latlon_from_vector
                    lat, lon = latlon_from_vector(forward_vec)

            render_overlay(buffer, angle_x, angle_y, angle_z, zoom, lat, lon)

            buffer.noutrefresh()
            curses.doupdate()
            prev_state = state

        except KeyboardInterrupt:
            break

        time.sleep(0.016)


if __name__ == '__main__':
    args = parse_args()

    try:
        curses.wrapper(lambda stdscr: main(stdscr, args))
    except Exception as e:
        log(f"[\033[91mFATAL\033[0m] Uncaught Exception: {e}")
        if args.debug:
            traceback.print_exc()
        with open("debug.log", "a") as f:
            traceback.print_exc(file=f)
        raise
def handle_keys(key, angle_x, angle_y, angle_z, zoom, offset_x, offset_y):
    changed = False

    if key == ord('q'):
        log("[\033[32mINFO\033[0m] Exiting\n------------")
        raise KeyboardInterrupt()
    elif key == ord('w'):  # tilt up
        angle_x -= 5
        changed = True
    elif key == ord('s'):  # tilt down
        angle_x += 5
        changed = True
    elif key == ord('a'):  # rotate left (yaw)
        angle_z -= 5
        changed = True
    elif key == ord('d'):  # rotate right (yaw)
        angle_z += 5
        changed = True
    elif key == ord(','):
        angle_y -= 5  # orbit left
        changed = True
    elif key == ord('.'):
        angle_y += 5  # orbit right
        changed = True
    elif key == ord('+') or key == ord('='):
        zoom *= 1.1
        changed = True
    elif key == ord('-'):
        zoom /= 1.1
        changed = True
    elif key == curses.KEY_UP:
        offset_y -= 1
        changed = True
    elif key == curses.KEY_DOWN:
        offset_y += 1
        changed = True
    elif key == curses.KEY_LEFT:
        offset_x -= 1
        changed = True
    elif key == curses.KEY_RIGHT:
        offset_x += 1
        changed = True
    elif key == ord('r'):
        angle_x, angle_y, angle_z = 0, 90, 0
        changed = True

    angle_x = max(min(angle_x, 95), -95)
    return angle_x, angle_y, angle_z, zoom, offset_x, offset_y, changed


def render_overlay(buffer, angle_x, angle_y, angle_z, zoom, lat=None, lon=None):
    buffer.addstr(0, 0, "@")  # This should always appear in top-left
    if lat is not None and lon is not None:
        buffer.addstr(0, 1, f"Lat: {lat:.4f}, Lon: {lon:.4f}")
    buffer.addstr(0, 50, f"angle_x = {angle_x}", curses.color_pair(3))
    buffer.addstr(1, 50, f"angle_y = {angle_y}", curses.color_pair(3))
    buffer.addstr(2, 50, f"angle_z = {angle_z}", curses.color_pair(3))
    buffer.addstr(3, 50, f"zoom = {zoom:.2f}", curses.color_pair(3))


def init_curses(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(50)
    stdscr.keypad(True)
    curses.start_color()

    # Define color pairs (foreground, background)
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)


def forward_from_angles(angle_x, angle_y):
    fx = np.cos(np.radians(angle_y)) * np.cos(np.radians(angle_x))
    fy = np.sin(np.radians(angle_x))
    fz = np.sin(np.radians(angle_y)) * np.cos(np.radians(angle_x))
    return np.array([fx, fy, fz])


def fatal(stdscr, message, debug=False, exception=None):
    stdscr.clear()
    try:
        stdscr.addstr(0, 0, f"ERROR: {message}", curses.color_pair(4))
    except curses.error:
        stdscr.addstr(0, 0, f"ERROR: {message}")
    stdscr.refresh()

    if debug and exception:
        with open("debug.log", "a") as f:
            f.write(f"Fatal error: {type(exception).__name__}: {exception}\n")
            traceback.print_exception(type(exception), exception, exception.__traceback__, file=f)

    time.sleep(3)
    raise KeyboardInterrupt()
