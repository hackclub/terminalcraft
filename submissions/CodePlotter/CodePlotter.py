print("""
 _____           _     ______ _       _   _            
/  __ \\         | |    | ___ \\ |     | | | |           
| /  \\/ ___   __| | ___| |_/ / | ___ | |_| |_ ___ _ __ 
| |    / _ \\ / _` |/ _ \\  __/| |/ _ \\| __| __/ _ \\ '__|
| \\__/\\ (_) | (_| |  __/ |   | | (_) | |_| ||  __/ |   
 \\____/\\___/ \\__,_|\\___\\_|   |_|\\___/ \\__|\\__\\___|_|                                         

""")

import re
import math
import os
import itertools

# --- Constants ---
GCODE_TOLERANCE = 1e-6 # For comparing float coordinates

def parse_gcode_for_xy(gcode_lines):
    """
    Extracts X, Y coordinates and command type (G0/G1) for bounds calculation.
    Returns segments and the final X,Y position relative to the file's start.
    """
    path_segments = []
    current_segment = []
    last_x, last_y = 0.0, 0.0
    in_segment = False

    for line_num, line in enumerate(gcode_lines):
        line = line.strip().upper().split(';')[0]
        if not line: continue

        parts = line.split()
        command = None
        x_coord, y_coord = None, None
        z_present = False
        xy_present = False
        is_g0_g1 = False
        is_g92 = False

        temp_x, temp_y = last_x, last_y

        for part in parts:
            if not part: continue
            char = part[0]
            try:
                val_str = part[1:]
                if char == 'G':
                    g_val = int(float(val_str))
                    if g_val == 0 or g_val == 1:
                        command = f"G{g_val}"
                        is_g0_g1 = True
                    elif g_val == 92:
                        is_g92 = True
                elif char == 'X':
                    x_coord = float(val_str)
                    temp_x = x_coord
                    xy_present = True
                elif char == 'Y':
                    y_coord = float(val_str)
                    temp_y = y_coord
                    xy_present = True
                elif char == 'Z':
                    z_present = True
            except (ValueError, IndexError):
                continue

        if is_g0_g1:
            is_z_only_move = z_present and not xy_present
            current_point_x = x_coord if x_coord is not None else last_x
            current_point_y = y_coord if y_coord is not None else last_y

            current_point = {'x': current_point_x, 'y': current_point_y, 'cmd': command, 'z_only': is_z_only_move, 'line': line_num}
            moved_xy = abs(last_x - current_point_x) > GCODE_TOLERANCE or abs(last_y - current_point_y) > GCODE_TOLERANCE

            if command == "G0":
                if current_segment:
                    path_segments.append(list(current_segment))
                if moved_xy:
                    start_point_g0 = {'x': last_x, 'y': last_y, 'cmd': "G0_START", 'z_only': False, 'line': line_num}
                    g0_segment = [start_point_g0, current_point]
                    path_segments.append(g0_segment)
                current_segment = []
                in_segment = False

            elif command == "G1":
                if not in_segment and moved_xy:
                    start_point_g1 = {'x': last_x, 'y': last_y, 'cmd': "G1", 'z_only': False, 'line': line_num}
                    current_segment.append(start_point_g1)

                if moved_xy:
                    current_segment.append(current_point)
                    in_segment = True
                elif is_z_only_move and in_segment:
                    path_segments.append(list(current_segment))
                    current_segment = []
                    in_segment = False

            last_x, last_y = current_point_x, current_point_y

        elif is_g92:
            if in_segment:
                path_segments.append(list(current_segment))
                current_segment = []
                in_segment = False
            if x_coord is not None: last_x = x_coord
            if y_coord is not None: last_y = y_coord

        else:
            if in_segment:
                path_segments.append(list(current_segment))
                current_segment = []
                in_segment = False
            if xy_present:
                last_x, last_y = temp_x, temp_y

    if current_segment:
        path_segments.append(current_segment)

    return [seg for seg in path_segments if len(seg) >= 2], last_x, last_y

def calculate_bounds(segments):
    """Calculate the bounding box of G-code segments."""
    if not segments:
        return None
    
    min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')
    has_points = False
    
    for segment in segments:
        for point in segment:
            has_points = True
            min_x, max_x = min(min_x, point['x']), max(max_x, point['x'])
            min_y, max_y = min(min_y, point['y']), max(max_y, point['y'])
    
    return {"min_x": min_x, "max_x": max_x, "min_y": min_y, "max_y": max_y} if has_points else None

def generate_transformed_gcode(original_gcode_lines, x_scale=1.0, y_scale=1.0, z_scale=1.0, 
                              x_offset=0.0, y_offset=0.0, z_offset=0.0, 
                              pen_x_offset=0.0, pen_y_offset=0.0, rotation_angle=0.0):
    """
    Generates modified G-code lines applying all transformations including rotation.
    
    Args:
        original_gcode_lines: List of original G-code lines
        x_scale, y_scale, z_scale: Scaling factors
        x_offset, y_offset, z_offset: Translation offsets
        pen_x_offset, pen_y_offset: Pen offset for plotters
        rotation_angle: Rotation angle in degrees
    
    Returns:
        List of transformed G-code lines
    """
    modified_gcode = []
    coord_pattern = re.compile(r"([XYZ])([-+]?\d*\.?\d*)")
    
    # Convert rotation to radians
    rotation_rad = math.radians(rotation_angle)
    cos_theta = math.cos(rotation_rad)
    sin_theta = math.sin(rotation_rad)

    for line in original_gcode_lines:
        parts = line.split(';', 1)
        code_part = parts[0]
        comment_part = f";{parts[1]}" if len(parts) > 1 else ""

        cleaned_code_upper = code_part.strip().upper()
        is_motion_cmd = cleaned_code_upper.startswith('G0') or cleaned_code_upper.startswith('G1')
        is_set_coord_cmd = cleaned_code_upper.startswith('G92')

        if is_motion_cmd or is_set_coord_cmd:
            matches = list(coord_pattern.finditer(code_part))
            if matches:
                axes_values = {}
                for match in matches:
                    axis = match.group(1).upper()
                    try:
                        val = float(match.group(2))
                        axes_values[axis] = val
                    except ValueError:
                        pass
                
                # Apply transformations to X and Y coordinates
                if 'X' in axes_values and 'Y' in axes_values:
                    # Apply scaling
                    scaled_x = axes_values['X'] * x_scale
                    scaled_y = axes_values['Y'] * y_scale
                    
                    # Apply rotation
                    if rotation_angle != 0:
                        rotated_x = scaled_x * cos_theta - scaled_y * sin_theta
                        rotated_y = scaled_x * sin_theta + scaled_y * cos_theta
                        scaled_x = rotated_x
                        scaled_y = rotated_y
                    
                    # Apply offsets
                    final_x = scaled_x + x_offset - pen_x_offset
                    final_y = scaled_y + y_offset - pen_y_offset
                    
                    axes_values['X'] = final_x
                    axes_values['Y'] = final_y
                
                # Handle Z separately (no rotation)
                if 'Z' in axes_values:
                    axes_values['Z'] = (axes_values['Z'] * z_scale) + z_offset
                
                # Rebuild the line
                modified_code_part = cleaned_code_upper.split()[0]
                for axis, value in sorted(axes_values.items()):
                    modified_code_part += f" {axis}{value:.6f}"
                
                modified_line = modified_code_part + comment_part
            else:
                modified_line = code_part + comment_part
        else:
            modified_line = code_part + comment_part
        
        modified_gcode.append(modified_line)

    return modified_gcode

def crop_gcode_to_bed(original_gcode_lines, bed_width, bed_height, x_scale=1.0, y_scale=1.0, z_scale=1.0,
                     x_offset=0.0, y_offset=0.0, z_offset=0.0, pen_x_offset=0.0, pen_y_offset=0.0, rotation_angle=0.0):
    """
    Generates G-code with coordinates cropped to stay within bed boundaries.
    """
    modified_gcode = []
    coord_pattern = re.compile(r"([XYZ])([-+]?\d*\.?\d*)")
    
    rotation_rad = math.radians(rotation_angle)
    cos_theta = math.cos(rotation_rad)
    sin_theta = math.sin(rotation_rad)
    
    last_x, last_y = 0.0, 0.0
    
    modified_gcode.append("; Note: G-code has been cropped to stay within bed boundaries")

    for line in original_gcode_lines:
        parts = line.split(';', 1)
        code_part = parts[0]
        comment_part = f";{parts[1]}" if len(parts) > 1 else ""

        cleaned_code_upper = code_part.strip().upper()
        is_motion_cmd = cleaned_code_upper.startswith('G0') or cleaned_code_upper.startswith('G1')

        if is_motion_cmd:
            matches = list(coord_pattern.finditer(code_part))
            if matches:
                axes_values = {}
                for match in matches:
                    axis = match.group(1).upper()
                    try:
                        val = float(match.group(2))
                        axes_values[axis] = val
                    except ValueError:
                        pass
                
                if 'X' in axes_values and 'Y' in axes_values:
                    # Apply transformations
                    scaled_x = axes_values['X'] * x_scale
                    scaled_y = axes_values['Y'] * y_scale
                    
                    if rotation_angle != 0:
                        rotated_x = scaled_x * cos_theta - scaled_y * sin_theta
                        rotated_y = scaled_x * sin_theta + scaled_y * cos_theta
                        scaled_x = rotated_x
                        scaled_y = rotated_y
                    
                    final_x = scaled_x + x_offset - pen_x_offset
                    final_y = scaled_y + y_offset - pen_y_offset
                    
                    # Crop to bed boundaries
                    final_x = max(0, min(final_x, bed_width))
                    final_y = max(0, min(final_y, bed_height))
                    
                    if final_x != scaled_x + x_offset - pen_x_offset or final_y != scaled_y + y_offset - pen_y_offset:
                        comment_part += " ;CLIPPED to bed boundary"
                    
                    axes_values['X'] = final_x
                    axes_values['Y'] = final_y
                    last_x, last_y = final_x, final_y
                
                if 'Z' in axes_values:
                    axes_values['Z'] = (axes_values['Z'] * z_scale) + z_offset
                
                modified_code_part = cleaned_code_upper.split()[0]
                for axis, value in sorted(axes_values.items()):
                    modified_code_part += f" {axis}{value:.6f}"
                
                modified_line = modified_code_part + comment_part
                modified_gcode.append(modified_line)
            else:
                modified_gcode.append(code_part + comment_part)
        else:
            modified_gcode.append(code_part + comment_part)

    return modified_gcode

def apply_transformations_to_coords(original_coords_segments, transform_params):
    """Applies scale, offset, and rotation from a transform dict to coordinate segments."""
    transformed_segments = []
    x_scale = transform_params['x_scale']
    y_scale = transform_params['y_scale']
    x_offset = transform_params['x_offset']
    y_offset = transform_params['y_offset']
    
    # Get rotation angle in radians if it exists, otherwise default to 0
    rotation_angle = math.radians(transform_params.get('rotation_angle', 0))

    for segment in original_coords_segments:
        new_segment = []
        for point in segment:
            # Apply scale to original relative coords
            scaled_x = point['x'] * x_scale
            scaled_y = point['y'] * y_scale
            
            # Apply rotation if needed (rotate around origin before translation)
            if rotation_angle != 0:
                # Rotation formula: x' = x*cos(θ) - y*sin(θ), y' = x*sin(θ) + y*cos(θ)
                cos_theta = math.cos(rotation_angle)
                sin_theta = math.sin(rotation_angle)
                rotated_x = scaled_x * cos_theta - scaled_y * sin_theta
                rotated_y = scaled_x * sin_theta + scaled_y * cos_theta
                transformed_x = rotated_x + x_offset
                transformed_y = rotated_y + y_offset
            else:
                # No rotation, just apply offset
                transformed_x = scaled_x + x_offset
                transformed_y = scaled_y + y_offset
            
            # Copy other info
            new_segment.append({**point, 'x': transformed_x, 'y': transformed_y})
        transformed_segments.append(new_segment)
    return transformed_segments

def clip_line_to_bed(x1, y1, x2, y2, bed_width, bed_height):
    """
    Clips a line segment to stay within the bed boundaries using Cohen-Sutherland algorithm.
    """
    # Define region codes
    INSIDE = 0  # 0000
    LEFT = 1    # 0001
    RIGHT = 2   # 0010
    BOTTOM = 4  # 0100
    TOP = 8     # 1000
    
    # Calculate region code for a point
    def compute_code(x, y):
        code = INSIDE
        if x < 0:
            code |= LEFT
        elif x > bed_width:
            code |= RIGHT
        if y < 0:
            code |= BOTTOM
        elif y > bed_height:
            code |= TOP
        return code
    
    # Calculate codes for both points
    code1 = compute_code(x1, y1)
    code2 = compute_code(x2, y2)
    
    # Both points inside bed, no clipping needed
    if code1 == 0 and code2 == 0:
        return x2, y2
    
    # Line completely outside bed, return the start point
    if (code1 & code2) != 0:
        return x1, y1
    
    # Line needs clipping, determine which point is outside
    if code1 == 0:  # First point inside, second point outside
        outside_code = code2
        outside_x, outside_y = x2, y2
        inside_x, inside_y = x1, y1
    else:  # Second point inside or both points outside
        outside_code = code1
        outside_x, outside_y = x1, y1
        inside_x, inside_y = x2, y2
    
    # Calculate intersection with edge
    if outside_code & LEFT:  # Intersect with left edge
        y = inside_y + (outside_y - inside_y) * (-inside_x) / (outside_x - inside_x)
        x = 0
        if 0 <= y <= bed_height:
            return x, y
    
    if outside_code & RIGHT:  # Intersect with right edge
        y = inside_y + (outside_y - inside_y) * (bed_width - inside_x) / (outside_x - inside_x)
        x = bed_width
        if 0 <= y <= bed_height:
            return x, y
    
    if outside_code & BOTTOM:  # Intersect with bottom edge
        x = inside_x + (outside_x - inside_x) * (-inside_y) / (outside_y - inside_y)
        y = 0
        if 0 <= x <= bed_width:
            return x, y
    
    if outside_code & TOP:  # Intersect with top edge
        x = inside_x + (outside_x - inside_x) * (bed_height - inside_y) / (outside_y - inside_y)
        y = bed_height
        if 0 <= x <= bed_width:
            return x, y
    
    # If we reach here, something went wrong, just return last known good point
    return x1, y1

def center_file_on_bed(segments, transform_params, bed_width, bed_height):
    """Centers a file's segments on the bed by calculating appropriate offsets."""
    if not segments:
        return transform_params
    
    # Apply current scale and rotation to get bounds
    temp_segments = apply_transformations_to_coords(segments, {
        'x_scale': transform_params['x_scale'],
        'y_scale': transform_params['y_scale'],
        'x_offset': 0,  # Use 0 offset for centering calculation
        'y_offset': 0,
        'rotation_angle': transform_params.get('rotation_angle', 0)
    })
    
    bounds = calculate_bounds(temp_segments)
    if not bounds:
        return transform_params
    
    # Calculate required offset for centering
    path_width = bounds['max_x'] - bounds['min_x']
    path_height = bounds['max_y'] - bounds['min_y']
    path_center_x = bounds['min_x'] + path_width / 2.0
    path_center_y = bounds['min_y'] + path_height / 2.0
    bed_center_x = bed_width / 2.0
    bed_center_y = bed_height / 2.0
    
    # Update transform parameters
    new_transform = transform_params.copy()
    new_transform['x_offset'] = bed_center_x - path_center_x
    new_transform['y_offset'] = bed_center_y - path_center_y
    
    return new_transform

def process_multiple_files(file_paths, transformations, bed_width=220, bed_height=220, crop_to_bed=False):
    """
    Process multiple G-code files with individual transformations.
    
    Args:
        file_paths: List of file paths
        transformations: List of transformation dictionaries for each file
        bed_width, bed_height: Bed dimensions for bounds checking
        crop_to_bed: Whether to crop coordinates to bed boundaries
    
    Returns:
        List of processed G-code lines
    """
    merged_gcode = []
    merged_gcode.append("; G-code merged and modified by Legacy Command-Line Tool")
    merged_gcode.append(f"; Merging {len(file_paths)} file(s)")
    merged_gcode.append(";")
    merged_gcode.append(f"; Bed Dimensions Used: {bed_width:.3f} x {bed_height:.3f} mm")
    if crop_to_bed:
        merged_gcode.append("; Crop-to-bed: Enabled - G-code paths outside bed boundaries will be cropped")
    merged_gcode.append(";")
    
    for i, (file_path, transform) in enumerate(zip(file_paths, transformations)):
        try:
            with open(file_path, 'r', errors='ignore') as f:
                lines = [line.strip() for line in f if line.strip()]
            
            if not lines:
                print(f"Warning: Skipped empty file: {os.path.basename(file_path)}")
                continue
            
            filename = os.path.basename(file_path)
            merged_gcode.append(f"; --- Start: {filename} ---")
            merged_gcode.append(f"; Transform: Scale(X:{transform.get('x_scale', 1.0):.4f} Y:{transform.get('y_scale', 1.0):.4f} Z:{transform.get('z_scale', 1.0):.4f}) Offset(X:{transform.get('x_offset', 0.0):.4f} Y:{transform.get('y_offset', 0.0):.4f} Z:{transform.get('z_offset', 0.0):.4f}) Pen(X:{transform.get('pen_x_offset', 0.0):.4f} Y:{transform.get('pen_y_offset', 0.0):.4f}) Rotation({transform.get('rotation_angle', 0.0):.2f}°)")
            
            # Generate transformed G-code
            if crop_to_bed:
                transformed_lines = crop_gcode_to_bed(
                    lines, bed_width, bed_height,
                    x_scale=transform.get('x_scale', 1.0),
                    y_scale=transform.get('y_scale', 1.0),
                    z_scale=transform.get('z_scale', 1.0),
                    x_offset=transform.get('x_offset', 0.0),
                    y_offset=transform.get('y_offset', 0.0),
                    z_offset=transform.get('z_offset', 0.0),
                    pen_x_offset=transform.get('pen_x_offset', 0.0),
                    pen_y_offset=transform.get('pen_y_offset', 0.0),
                    rotation_angle=transform.get('rotation_angle', 0.0)
                )
            else:
                transformed_lines = generate_transformed_gcode(
                    lines,
                    x_scale=transform.get('x_scale', 1.0),
                    y_scale=transform.get('y_scale', 1.0),
                    z_scale=transform.get('z_scale', 1.0),
                    x_offset=transform.get('x_offset', 0.0),
                    y_offset=transform.get('y_offset', 0.0),
                    z_offset=transform.get('z_offset', 0.0),
                    pen_x_offset=transform.get('pen_x_offset', 0.0),
                    pen_y_offset=transform.get('pen_y_offset', 0.0),
                    rotation_angle=transform.get('rotation_angle', 0.0)
                )
            
            merged_gcode.extend(transformed_lines)
            merged_gcode.append(f"; --- End: {filename} ---")
            merged_gcode.append(";")
            
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            continue
    
    return merged_gcode

def interactive_transform_mode():
    """Interactive mode for transforming a single file."""
    print("\n=== Single File Transform Mode ===")
    
    file_path = input("Enter the path to your G-code file: ").strip()
    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'")
        return
    
    try:
        with open(file_path, 'r', errors='ignore') as f:
            gcode_lines = [line.strip() for line in f if line.strip()]
        
        if not gcode_lines:
            print("Error: File is empty or contains no valid G-code.")
            return
        
        print(f"\nLoaded file: {os.path.basename(file_path)}")
        print(f"Total lines: {len(gcode_lines)}")
        
        # Parse for bounds information
        segments, _, _ = parse_gcode_for_xy(gcode_lines)
        bounds = calculate_bounds(segments)
        
        if bounds:
            width = bounds['max_x'] - bounds['min_x']
            height = bounds['max_y'] - bounds['min_y']
            print(f"Original bounds: X[{bounds['min_x']:.2f} .. {bounds['max_x']:.2f}] Y[{bounds['min_y']:.2f} .. {bounds['max_y']:.2f}]")
            print(f"Original dimensions: {width:.2f} x {height:.2f} mm")
        
        # Get transformation parameters
        print("\n--- Transformation Parameters ---")
        x_scale = float(input("Enter X-axis scale factor (1.0 = no change): ") or "1.0")
        y_scale = float(input("Enter Y-axis scale factor (1.0 = no change): ") or "1.0")
        z_scale = float(input("Enter Z-axis scale factor (1.0 = no change): ") or "1.0")
        
        rotation_angle = float(input("Enter rotation angle in degrees (0 = no rotation): ") or "0.0")
        
        x_offset = float(input("Enter X-axis offset in mm (0 = no offset): ") or "0.0")
        y_offset = float(input("Enter Y-axis offset in mm (0 = no offset): ") or "0.0")
        z_offset = float(input("Enter Z-axis offset in mm (0 = no offset): ") or "0.0")
        
        pen_x_offset = float(input("Enter pen X offset in mm (0 = no offset): ") or "0.0")
        pen_y_offset = float(input("Enter pen Y offset in mm (0 = no offset): ") or "0.0")
        
        # Bed dimensions for validation
        bed_width = float(input("Enter bed width in mm (220): ") or "220.0")
        bed_height = float(input("Enter bed height in mm (220): ") or "220.0")
        
        # Options
        crop_to_bed = input("Crop to bed boundaries? (y/N): ").lower().startswith('y')
        
        # Apply transformations
        if crop_to_bed:
            modified_code = crop_gcode_to_bed(
                gcode_lines, bed_width, bed_height,
                x_scale, y_scale, z_scale,
                x_offset, y_offset, z_offset,
                pen_x_offset, pen_y_offset, rotation_angle
            )
        else:
            modified_code = generate_transformed_gcode(
                gcode_lines,
                x_scale, y_scale, z_scale,
                x_offset, y_offset, z_offset,
                pen_x_offset, pen_y_offset, rotation_angle
            )
        
        # Save output
        base_name = os.path.splitext(file_path)[0]
        default_output = f"{base_name}_modified.gcode"
        output_path = input(f"Enter output file path ({default_output}): ").strip() or default_output
        
        with open(output_path, 'w') as f:
            for line in modified_code:
                f.write(line + '\n')
        
        print(f"\nTransformed G-code saved to: {output_path}")
        
        # Calculate and display new bounds
        new_segments, _, _ = parse_gcode_for_xy(modified_code)
        new_bounds = calculate_bounds(new_segments)
        
        if new_bounds:
            new_width = new_bounds['max_x'] - new_bounds['min_x']
            new_height = new_bounds['max_y'] - new_bounds['min_y']
            print(f"New bounds: X[{new_bounds['min_x']:.2f} .. {new_bounds['max_x']:.2f}] Y[{new_bounds['min_y']:.2f} .. {new_bounds['max_y']:.2f}]")
            print(f"New dimensions: {new_width:.2f} x {new_height:.2f} mm")
            
            # Check if within bed bounds
            if new_bounds['min_x'] < 0 or new_bounds['min_y'] < 0 or new_bounds['max_x'] > bed_width or new_bounds['max_y'] > bed_height:
                print("WARNING: Transformed G-code extends outside bed boundaries!")
    
    except ValueError as e:
        print(f"Error: Invalid input - {e}")
    except Exception as e:
        print(f"Error processing file: {e}")

def interactive_merge_mode():
    """Interactive mode for merging multiple files."""
    print("\n=== Multi-File Merge Mode ===")
    
    files = []
    transformations = []
    
    # Get bed dimensions
    bed_width = float(input("Enter bed width in mm (220): ") or "220.0")
    bed_height = float(input("Enter bed height in mm (220): ") or "220.0")
    
    print("\nAdd files to merge (enter empty path to finish):")
    
    file_count = 1
    while True:
        file_path = input(f"File {file_count} path: ").strip()
        if not file_path:
            break
        
        if not os.path.exists(file_path):
            print(f"Error: File not found at '{file_path}'")
            continue
        
        # Load and analyze file
        try:
            with open(file_path, 'r', errors='ignore') as f:
                lines = [line.strip() for line in f if line.strip()]
            
            if not lines:
                print("Warning: File is empty, skipping.")
                continue
            
            segments, _, _ = parse_gcode_for_xy(lines)
            bounds = calculate_bounds(segments)
            
            print(f"Loaded: {os.path.basename(file_path)}")
            if bounds:
                width = bounds['max_x'] - bounds['min_x']
                height = bounds['max_y'] - bounds['min_y']
                print(f"  Bounds: X[{bounds['min_x']:.2f}..{bounds['max_x']:.2f}] Y[{bounds['min_y']:.2f}..{bounds['max_y']:.2f}] ({width:.2f}x{height:.2f}mm)")
            
            files.append(file_path)
            
            # Get transformation for this file
            print(f"\n--- Transformation for {os.path.basename(file_path)} ---")
            
            transform = {}
            transform['x_scale'] = float(input("X scale (1.0): ") or "1.0")
            transform['y_scale'] = float(input("Y scale (1.0): ") or "1.0")
            transform['z_scale'] = float(input("Z scale (1.0): ") or "1.0")
            transform['rotation_angle'] = float(input("Rotation degrees (0): ") or "0.0")
            transform['x_offset'] = float(input("X offset mm (0): ") or "0.0")
            transform['y_offset'] = float(input("Y offset mm (0): ") or "0.0")
            transform['z_offset'] = float(input("Z offset mm (0): ") or "0.0")
            transform['pen_x_offset'] = float(input("Pen X offset mm (0): ") or "0.0")
            transform['pen_y_offset'] = float(input("Pen Y offset mm (0): ") or "0.0")
            
            # Option to auto-center
            if input("Auto-center on bed? (y/N): ").lower().startswith('y'):
                transform = center_file_on_bed(segments, transform, bed_width, bed_height)
                print(f"Auto-centered: X offset = {transform['x_offset']:.2f}, Y offset = {transform['y_offset']:.2f}")
            
            transformations.append(transform)
            file_count += 1
            
        except Exception as e:
            print(f"Error loading file: {e}")
            continue
    
    if not files:
        print("No files loaded.")
        return
    
    # Processing options
    crop_to_bed = input("\nCrop all files to bed boundaries? (y/N): ").lower().startswith('y')
    
    # Generate merged output
    output_path = input("Enter output file path (merged.gcode): ").strip() or "merged.gcode"
    
    try:
        merged_gcode = process_multiple_files(files, transformations, bed_width, bed_height, crop_to_bed)
        
        with open(output_path, 'w') as f:
            for line in merged_gcode:
                f.write(line + '\n')
        
        print(f"\nMerged G-code saved to: {output_path}")
        print(f"Total files merged: {len(files)}")
        
    except Exception as e:
        print(f"Error creating merged file: {e}")

def scale_gcode(gcode_lines, x_scale=1.0, y_scale=1.0, z_scale=1.0):
    """
    Scales the X, Y, and Z coordinates in a list of G-code lines.

    Args:
        gcode_lines (list): A list of strings, where each string is a line of G-code.
        x_scale (float): The scaling factor for the X coordinates.
        y_scale (float): The scaling factor for the Y coordinates.
        z_scale (float): The scaling factor for the Z coordinates.

    Returns:
        list: A new list of G-code lines with the scaling applied.
    """
    modified_gcode = []
    for line in gcode_lines:
        parts = line.split()
        modified_parts = []
        for part in parts:
            if part.startswith('X') and len(part) > 1:
                try:
                    x_val = float(part[1:]) * x_scale
                    modified_parts.append(f'X{x_val:.6f}')
                except ValueError:
                    modified_parts.append(part)
            elif part.startswith('Y') and len(part) > 1:
                try:
                    y_val = float(part[1:]) * y_scale
                    modified_parts.append(f'Y{y_val:.6f}')
                except ValueError:
                    modified_parts.append(part)
            elif part.startswith('Z') and len(part) > 1:
                try:
                    z_val = float(part[1:]) * z_scale
                    modified_parts.append(f'Z{z_val:.6f}')
                except ValueError:
                    modified_parts.append(part)
            else:
                modified_parts.append(part)
        modified_gcode.append(' '.join(modified_parts))
    return modified_gcode

def offset_gcode(gcode_lines, x_offset=0.0, y_offset=0.0, z_offset=0.0):
    """
    Offsets the X, Y, and Z coordinates in a list of G-code lines.

    Args:
        gcode_lines (list): A list of strings, where each string is a line of G-code.
        x_offset (float): The amount to offset the X coordinates.
        y_offset (float): The amount to offset the Y coordinates.
        z_offset (float): The amount to offset the Z coordinates.

    Returns:
        list: A new list of G-code lines with the offsets applied.
    """
    modified_gcode = []
    for line in gcode_lines:
        parts = line.split()
        modified_parts = []
        for part in parts:
            if part.startswith('X') and len(part) > 1:
                try:
                    x_val = float(part[1:]) + x_offset
                    modified_parts.append(f'X{x_val:.6f}')
                except ValueError:
                    modified_parts.append(part)
            elif part.startswith('Y') and len(part) > 1:
                try:
                    y_val = float(part[1:]) + y_offset
                    modified_parts.append(f'Y{y_val:.6f}')
                except ValueError:
                    modified_parts.append(part)
            elif part.startswith('Z') and len(part) > 1:
                try:
                    z_val = float(part[1:]) + z_offset
                    modified_parts.append(f'Z{z_val:.6f}')
                except ValueError:
                    modified_parts.append(part)
            else:
                modified_parts.append(part)
        modified_gcode.append(' '.join(modified_parts))
    return modified_gcode

if __name__ == "__main__":
    print("=== G-Code Manipulator Command-Line Tool ===")
    print("Enhanced version with rotation, pen offsets, and multi-file support")
    print()
    print("Choose mode:")
    print("1. Single file transform")
    print("2. Multi-file merge")
    print("3. Legacy mode (simple scale/offset)")
    print()
    
    try:
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            interactive_transform_mode()
        elif choice == "2":
            interactive_merge_mode()
        elif choice == "3":
            # Legacy mode for backward compatibility
            file_path = input("Enter the path to your G-code file: ")
            with open(file_path, 'r') as f:
                gcode_lines = [line.strip() for line in f]

            print("\nOriginal G-code (first few lines):")
            for i, line in enumerate(gcode_lines[:5]):
                print(f"{i+1}: {line}")
            if len(gcode_lines) > 5:
                print("...")
                print(f"Total lines: {len(gcode_lines)}")

            x_scale = float(input("Enter the X-axis scale factor (e.g., 2.0 for 200%): "))
            y_scale = float(input("Enter the Y-axis scale factor: "))
            z_scale = float(input("Enter the Z-axis scale factor: "))

            scaled_code = scale_gcode(gcode_lines, x_scale, y_scale, z_scale)

            x_offset = float(input("Enter the X-axis offset: "))
            y_offset = float(input("Enter the Y-axis offset: "))
            z_offset = float(input("Enter the Z-axis offset: "))

            modified_code = offset_gcode(scaled_code, x_offset, y_offset, z_offset)

            output_file_path = input("Enter the path to save the modified G-code file: ")
            with open(output_file_path, 'w') as outfile:
                for line in modified_code:
                    outfile.write(line + '\n')

            print(f"\nModified G-code (scaled and offset) saved to: {output_file_path}")
        else:
            print("Invalid choice. Please run the program again.")
            
    except FileNotFoundError:
        print(f"Error: File not found")
    except ValueError:
        print("Invalid input. Please enter numeric values for the scaling factors and offsets.")
    except Exception as e:
        print(f"An error occurred: {e}")
