#!/usr/bin/env python3
"""
ASCII Animation Demos
This script provides 5 amazing ASCII art animations that can be played
without requiring any video input. It uses the same underlying ASCII art
rendering capabilities from video_to_ascii.py but generates frames
programmatically instead of reading from a video file.
"""
import os
import time
import math
import random
import numpy as np
import argparse
from threading import Thread
from queue import Queue
from video_to_ascii import (
    convert_frame_to_ascii,
    clear_console,
    detect_terminal_size,
    ASCII_CHARS_STANDARD,
    ASCII_CHARS_DETAILED,
    ASCII_CHARS_INVERTED
)
DEFAULT_FPS = 30
DEFAULT_DURATION = 10  
def generate_sine_wave_frame(width, height, time_step, amplitude=0.5, frequency=1.0):
    """
    Generate a sine wave animation frame with multiple waves and dynamic elements
    """
    frame = np.ones((height, width, 3), dtype=np.uint8) * 15  
    frame[:, :, 0] = 25  
    mid_y = height // 2
    num_stars = 50
    for _ in range(num_stars):
        star_x = random.randint(0, width - 1)
        star_y = random.randint(0, height - 1)
        brightness = 150 + int(100 * math.sin(time_step * 3 + star_x * star_y))
        brightness = max(150, min(255, brightness))
        frame[star_y, star_x] = [brightness, brightness, brightness]
    moon_radius = height // 10
    moon_x = int(width * 0.8)
    moon_y = int(height * 0.2)
    moon_x += int(math.sin(time_step * 0.5) * width * 0.05)
    moon_y += int(math.cos(time_step * 0.3) * height * 0.03)
    for y in range(max(0, moon_y - moon_radius), min(height, moon_y + moon_radius)):
        for x in range(max(0, moon_x - moon_radius), min(width, moon_x + moon_radius)):
            if (x - moon_x) ** 2 + (y - moon_y) ** 2 <= moon_radius ** 2:
                brightness = 200 + int(30 * math.sin((x - moon_x) * 0.2) * math.cos((y - moon_y) * 0.2))
                brightness = min(255, brightness)
                frame[y, x] = [brightness, brightness, brightness]
    wave_properties = [
        (0.3, 1.0, 0.0, [0, 200, 255], 2),  
        (0.2, 1.5, math.pi / 4, [255, 100, 100], 2),  
        (0.15, 2.0, math.pi / 2, [100, 255, 100], 1),  
        (0.25, 0.7, math.pi, [255, 255, 100], 2),  
    ]
    for amp, freq, phase, color, thickness in wave_properties:
        for x in range(width):
            y = int(mid_y + amp * height * math.sin(freq * (x / width * 2 * math.pi + time_step + phase)))
            y = max(0, min(height - 1, y))
            frame[y, x] = color
            for offset in range(-thickness, thickness + 1):
                y_offset = y + offset
                if 0 <= y_offset < height:
                    fade_factor = 1.0 - abs(offset) / (thickness + 1)
                    faded_color = [int(c * fade_factor) for c in color]
                    frame[y_offset, x] = faded_color
    num_particles = 20
    main_amp, main_freq = wave_properties[0][0], wave_properties[0][1]
    for i in range(num_particles):
        particle_x = int((i / num_particles + time_step * 0.2) % 1.0 * width)
        base_y = int(mid_y + main_amp * height * math.sin(main_freq * (particle_x / width * 2 * math.pi + time_step)))
        particle_y = base_y + int(math.sin(i + time_step * 2) * height * 0.05)
        if 0 <= particle_y < height and 0 <= particle_x < width:
            hue = (i / num_particles + time_step * 0.1) % 1.0
            r = int(255 * (0.5 + 0.5 * math.sin(hue * 2 * math.pi)))
            g = int(255 * (0.5 + 0.5 * math.sin(hue * 2 * math.pi + 2*math.pi/3)))
            b = int(255 * (0.5 + 0.5 * math.sin(hue * 2 * math.pi + 4*math.pi/3)))
            particle_size = 2
            for dy in range(-particle_size, particle_size + 1):
                for dx in range(-particle_size, particle_size + 1):
                    px, py = particle_x + dx, particle_y + dy
                    if 0 <= py < height and 0 <= px < width:
                        dist = math.sqrt(dx**2 + dy**2)
                        if dist <= particle_size:
                            intensity = 1.0 - dist / (particle_size + 1)
                            frame[py, px] = [int(r * intensity), int(g * intensity), int(b * intensity)]
    return frame
def generate_matrix_rain_frame(width, height, drops, time_step):
    """
    Generate an enhanced Matrix-style digital rain animation frame with dynamic elements
    """
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    grid_intensity = 5 + int(2 * math.sin(time_step))
    for y in range(0, height, 8):
        for x in range(0, width, 8):
            frame[min(y, height-1), min(x, width-1)] = [0, grid_intensity, 0]
    matrix_chars = "01"  
    scan_line_pos = int((time_step * 10) % (height * 2))
    if scan_line_pos < height:
        scan_intensity = 10 + int(5 * math.sin(time_step * 5))
        frame[scan_line_pos, :] = [0, scan_intensity, scan_intensity // 2]
    if random.random() < 0.05:  
        glitch_y = random.randint(0, height - 1)
        glitch_width = random.randint(10, width // 3)
        glitch_x = random.randint(0, width - glitch_width)
        glitch_intensity = random.randint(10, 30)
        frame[glitch_y, glitch_x:glitch_x+glitch_width] = [glitch_intensity, glitch_intensity, 0]
    for i, drop in enumerate(drops):
        x, y, speed, length, brightness, char_change_rate, color_variation = drop
        for j in range(length):
            y_pos = int(y - j)
            x_pos = int(x)
            if 0 <= y_pos < height and 0 <= x_pos < width:
                fade = brightness * (1 - j / length)
                is_head = (j == 0)
                r_value = int(fade * 30 * color_variation)  
                g_value = int(fade * 255)  
                b_value = int(fade * 50 * color_variation)  
                if is_head:
                    r_value = g_value = b_value = int(255 * brightness)
                frame[y_pos, x_pos] = [r_value, g_value, b_value]
                if is_head and y_pos > 0 and y_pos < height-1 and x_pos > 0 and x_pos < width-1:
                    glow = int(100 * brightness)
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue  
                            ny, nx = y_pos + dy, x_pos + dx
                            if 0 <= ny < height and 0 <= nx < width:
                                if frame[ny, nx, 1] < glow:
                                    frame[ny, nx] = [glow//5, glow, glow//5]
        if random.random() < char_change_rate:
            x = x + random.uniform(-0.5, 0.5)
            x = max(0, min(width - 1, x))
        current_speed = speed * (1 + 0.2 * math.sin(time_step + i))
        drops[i] = (x, y + current_speed, speed, length, brightness, char_change_rate, color_variation)
        if int(y) - length > height:
            is_focus_drop = random.random() < 0.1  
            drops[i] = (
                random.randint(0, width - 1),  
                random.randint(-20, 0),        
                random.uniform(1.0, 3.0) if is_focus_drop else random.uniform(0.5, 2.0),  
                random.randint(15, 30) if is_focus_drop else random.randint(5, 20),  
                random.uniform(0.8, 1.0) if is_focus_drop else random.uniform(0.5, 0.9),  
                random.uniform(0.05, 0.2),  
                random.uniform(0.5, 1.5)    
            )
    return frame
def generate_firework_frame(width, height, fireworks, time_step):
    """
    Generate an enhanced fireworks animation frame with realistic effects
    """
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        gradient = int(5 * y / height)  
        frame[y, :] = [gradient, gradient, gradient + 2]  
    num_stars = 50
    for i in range(num_stars):
        star_x = int((width * i / num_stars + time_step * 2) % width)
        star_y = int(height * (0.1 + 0.3 * random.random()))
        brightness = 100 + int(50 * math.sin(time_step * 3 + i))
        brightness = min(255, max(50, brightness))
        frame[star_y, star_x] = [brightness, brightness, brightness]
    moon_radius = width // 20
    moon_x = width - moon_radius - 10
    moon_y = moon_radius + 10
    for y in range(max(0, moon_y - moon_radius), min(height, moon_y + moon_radius)):
        for x in range(max(0, moon_x - moon_radius), min(width, moon_x + moon_radius)):
            dx = x - moon_x
            dy = y - moon_y
            distance = math.sqrt(dx*dx + dy*dy)
            if distance <= moon_radius:
                crater_effect = random.randint(-10, 0) if random.random() < 0.2 else 0
                brightness = 180 + crater_effect
                frame[y, x] = [brightness, brightness, brightness + 20]  
    new_fireworks = []
    for firework in fireworks:
        status, x, y, color, particles, firework_type, trail_particles = firework
        if status == 'rising':
            if 0 <= y < height and 0 <= x < width:
                frame[int(y), int(x)] = color
            if random.random() < 0.3:  
                trail_particles.append({
                    'x': x + random.uniform(-0.5, 0.5),
                    'y': y + random.uniform(0, 1),
                    'size': random.uniform(0.5, 1.5),
                    'life': 1.0
                })
            active_trail_particles = []
            for particle in trail_particles:
                particle['y'] += 0.2  
                particle['x'] += random.uniform(-0.1, 0.1)  
                particle['life'] -= 0.05  
                if (particle['life'] > 0 and 
                    0 <= particle['x'] < width and 
                    0 <= particle['y'] < height):
                    smoke_color = [
                        int(40 * particle['life'] + color[0] * 0.1),
                        int(40 * particle['life'] + color[1] * 0.1),
                        int(40 * particle['life'] + color[2] * 0.1)
                    ]
                    px, py = int(particle['x']), int(particle['y'])
                    if 0 <= px < width and 0 <= py < height:
                        frame[py, px] = smoke_color
                    active_trail_particles.append(particle)
            y -= 2 + random.uniform(-0.2, 0.2)
            x += random.uniform(-0.1, 0.1)  
            if y < random.randint(height // 4, height // 2):
                particles = []
                num_particles = 80 if firework_type == 'large' else 50
                if firework_type == 'circular':
                    for i in range(num_particles):
                        angle = 2 * math.pi * i / num_particles
                        speed = random.uniform(1.0, 2.5)
                        angle += random.uniform(-0.1, 0.1)
                        particles.append({
                            'x': x,
                            'y': y,
                            'vx': math.cos(angle) * speed,
                            'vy': math.sin(angle) * speed,
                            'life': 1.0,
                            'size': random.uniform(1.0, 2.0)
                        })
                elif firework_type == 'spiral':
                    for i in range(num_particles):
                        angle = 10 * 2 * math.pi * i / num_particles
                        radius = 3 * i / num_particles
                        speed = random.uniform(0.5, 2.0)
                        particles.append({
                            'x': x,
                            'y': y,
                            'vx': math.cos(angle) * radius * speed,
                            'vy': math.sin(angle) * radius * speed,
                            'life': 1.0,
                            'size': random.uniform(1.0, 1.5)
                        })
                else:  
                    for _ in range(num_particles):
                        angle = random.uniform(0, 2 * math.pi)
                        speed = random.uniform(0.5, 3.0)
                        particles.append({
                            'x': x,
                            'y': y,
                            'vx': math.cos(angle) * speed,
                            'vy': math.sin(angle) * speed,
                            'life': 1.0,
                            'size': random.uniform(1.0, 2.0)
                        })
                secondary_color = [
                    random.randint(150, 255),
                    random.randint(150, 255),
                    random.randint(150, 255)
                ]
                new_fireworks.append(('exploding', x, y, color, particles, firework_type, active_trail_particles, secondary_color))
            else:
                new_fireworks.append(('rising', x, y, color, particles, firework_type, active_trail_particles))
        elif status == 'exploding':
            active_particles = []
            active_trail_particles = trail_particles if len(firework) > 6 else []
            secondary_color = firework[7] if len(firework) > 7 else color
            new_active_trail = []
            for particle in active_trail_particles:
                particle['y'] += 0.2  
                particle['x'] += random.uniform(-0.1, 0.1)  
                particle['life'] -= 0.05  
                if (particle['life'] > 0 and 
                    0 <= particle['x'] < width and 
                    0 <= particle['y'] < height):
                    smoke_color = [
                        int(40 * particle['life'] + color[0] * 0.1),
                        int(40 * particle['life'] + color[1] * 0.1),
                        int(40 * particle['life'] + color[2] * 0.1)
                    ]
                    px, py = int(particle['x']), int(particle['y'])
                    if 0 <= px < width and 0 <= py < height:
                        frame[py, px] = smoke_color
                    new_active_trail.append(particle)
            for particle in particles:
                particle['vx'] += random.uniform(-0.05, 0.05)
                particle['x'] += particle['vx']
                particle['y'] += particle['vy'] + 0.1  
                particle['life'] -= 0.02  
                if (particle['life'] > 0 and 
                    0 <= particle['x'] < width and 
                    0 <= particle['y'] < height):
                    use_secondary = (firework_type == 'spiral' and int(particle['x'] + particle['y']) % 2 == 0) or \
                                   (firework_type == 'circular' and random.random() < 0.3)
                    current_color = secondary_color if use_secondary else color
                    faded_color = [int(c * particle['life']) for c in current_color]
                    px, py = int(particle['x']), int(particle['y'])
                    size = max(1, int(particle['size'] * particle['life']))
                    for dy in range(-size//2, size//2 + 1):
                        for dx in range(-size//2, size//2 + 1):
                            nx, ny = px + dx, py + dy
                            if 0 <= nx < width and 0 <= ny < height:
                                distance = math.sqrt(dx*dx + dy*dy)
                                if distance <= size/2:
                                    intensity = 1.0 - (distance / (size/2))
                                    pixel_color = [int(c * intensity) for c in faded_color]
                                    frame[ny, nx] = pixel_color
                    active_particles.append(particle)
            if active_particles or new_active_trail:
                new_fireworks.append(('exploding', x, y, color, active_particles, firework_type, new_active_trail, secondary_color))
    if random.random() < 0.05 and len(fireworks) < 6:  
        x = random.randint(width // 6, width * 5 // 6)  
        y = height - 1
        color = [
            random.randint(150, 255),  
            random.randint(150, 255),  
            random.randint(150, 255)   
        ]
        new_fireworks.append(('rising', x, y, color, []))
    return frame, new_fireworks
def generate_starfield_frame(width, height, stars, time_step):
    """
    Generate an enhanced starfield/space travel animation frame with dynamic elements
    """
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            noise_val = (math.sin(x * 0.01 + time_step * 0.1) * 
                         math.sin(y * 0.01 + time_step * 0.05) * 
                         math.sin((x + y) * 0.005 + time_step * 0.03))
            r_val = max(0, min(20, int(10 + 10 * noise_val)))
            g_val = max(0, min(15, int(5 + 10 * noise_val)))
            b_val = max(0, min(30, int(15 + 15 * noise_val)))
            if abs(noise_val) > 0.7 and random.random() < 0.8:
                frame[y, x] = [r_val, g_val, b_val]
    center_x, center_y = width // 2, height // 2
    galaxy_time = time_step * 0.2
    galaxy_x = int(center_x + width * 0.3 * math.cos(galaxy_time))
    galaxy_y = int(center_y + height * 0.2 * math.sin(galaxy_time))
    galaxy_size = width // 10
    for dy in range(-galaxy_size, galaxy_size + 1):
        for dx in range(-galaxy_size, galaxy_size + 1):
            nx, ny = galaxy_x + dx, galaxy_y + dy
            if 0 <= nx < width and 0 <= ny < height:
                distance = math.sqrt(dx*dx + dy*dy)
                if distance <= galaxy_size:
                    angle = math.atan2(dy, dx)
                    spiral = (distance / galaxy_size) * 5 + angle + galaxy_time
                    spiral_factor = (math.sin(spiral) + 1) / 2
                    intensity = (1.0 - (distance / galaxy_size)) * 0.5
                    if spiral_factor > 0.5 and random.random() < intensity * 0.8:
                        r_val = int(30 * intensity)
                        g_val = int(20 * intensity)
                        b_val = int(50 * intensity)
                        frame[ny, nx] = [r_val, g_val, b_val]
    if random.random() < 0.02:  
        shooting_star_x = random.randint(0, width - 1)
        shooting_star_y = random.randint(0, height // 3)  
        shooting_star_length = random.randint(5, 15)
        shooting_star_angle = random.uniform(math.pi / 4, 3 * math.pi / 4)  
        for i in range(shooting_star_length):
            trail_x = int(shooting_star_x - i * math.cos(shooting_star_angle))
            trail_y = int(shooting_star_y - i * math.sin(shooting_star_angle))
            if 0 <= trail_x < width and 0 <= trail_y < height:
                brightness = 255 * (1 - i / shooting_star_length)
                frame[trail_y, trail_x] = [int(brightness), int(brightness), int(brightness)]
    for i, star in enumerate(stars):
        x, y, z, color = star
        speed_factor = 0.01 * (1 + 0.5 * math.sin(x * 10 + y * 10 + time_step))
        z -= speed_factor
        twinkle_phase = 0  
        size_factor = 1.0  
        if z <= 0:
            stars[i] = (
                random.uniform(-1, 1),  
                random.uniform(-1, 1),  
                random.uniform(0, 1),    
                [
                    random.randint(150, 255),  
                    random.randint(150, 255),  
                    random.randint(200, 255)   
                ],
                random.uniform(0.8, 1.5),  
                random.uniform(0, 2 * math.pi)  
            )
            continue
        proj_x = int(center_x + (x / z) * width)
        proj_y = int(center_y + (y / z) * height)
        brightness = 1.0 - z
        twinkle_factor = 0.7 + 0.3 * math.sin(time_step * 3 + i)
        brightness *= twinkle_factor
        star_color = [int(c * brightness) for c in color]
        if 0 <= proj_x < width and 0 <= proj_y < height:
            size = max(1, int(3 * (1 - z) * (size_factor if len(star) > 4 else 1.0)))
            if random.random() < 0.2:  
                star_color[0] = min(255, int(star_color[0] * (1 + 0.2 * math.sin(time_step + i))))
                star_color[2] = min(255, int(star_color[2] * (1 + 0.2 * math.cos(time_step + i))))
            for dy in range(-size, size + 1):
                for dx in range(-size, size + 1):
                    nx, ny = proj_x + dx, proj_y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        distance = math.sqrt(dx*dx + dy*dy)
                        if distance <= size:
                            intensity = 1.0 - (distance / size)
                            pixel_color = [int(c * intensity) for c in star_color]
                            if sum(pixel_color) > sum(frame[ny, nx]):
                                frame[ny, nx] = pixel_color
        if len(star) > 4:
            stars[i] = (x, y, z, color, size_factor, twinkle_phase + 0.1)
        else:
            stars[i] = (x, y, z, color)
    return frame
def generate_plasma_frame(width, height, time_step, plasma_state=None):
    """
    Generate an enhanced colorful plasma animation frame with dynamic elements
    """
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    if plasma_state is None:
        plasma_state = {
            'color_shift': 0,
            'blobs': [
                {'x': width * 0.3, 'y': height * 0.3, 'vx': 0.5, 'vy': 0.7, 'size': width/8},
                {'x': width * 0.7, 'y': height * 0.7, 'vx': -0.6, 'vy': -0.4, 'size': width/10},
                {'x': width * 0.5, 'y': height * 0.5, 'vx': 0.3, 'vy': -0.5, 'size': width/12}
            ],
            'wave_params': {
                'scale1': 30.0 + 10.0 * math.sin(time_step / 5.0),
                'scale2': 20.0 + 5.0 * math.cos(time_step / 3.0),
                'scale3': 15.0 + 7.0 * math.sin(time_step / 4.0)
            }
        }
    else:
        for blob in plasma_state['blobs']:
            blob['x'] += blob['vx']
            blob['y'] += blob['vy']
            if blob['x'] < 0 or blob['x'] > width:
                blob['vx'] *= -1
            if blob['y'] < 0 or blob['y'] > height:
                blob['vy'] *= -1
            if random.random() < 0.05:  
                blob['vx'] += random.uniform(-0.1, 0.1)
                blob['vy'] += random.uniform(-0.1, 0.1)
                blob['vx'] = max(-1.0, min(1.0, blob['vx']))
                blob['vy'] = max(-1.0, min(1.0, blob['vy']))
        plasma_state['wave_params']['scale1'] = 30.0 + 10.0 * math.sin(time_step / 5.0)
        plasma_state['wave_params']['scale2'] = 20.0 + 5.0 * math.cos(time_step / 3.0)
        plasma_state['wave_params']['scale3'] = 15.0 + 7.0 * math.sin(time_step / 4.0)
        plasma_state['color_shift'] = (plasma_state['color_shift'] + 0.01) % (2 * math.pi)
    scale1 = plasma_state['wave_params']['scale1']
    scale2 = plasma_state['wave_params']['scale2']
    scale3 = plasma_state['wave_params']['scale3']
    color_shift = plasma_state['color_shift']
    time_factor1 = time_step / 10.0
    time_factor2 = time_step / 7.0
    time_factor3 = time_step / 5.0
    blob_influence = np.zeros((height, width))
    for blob in plasma_state['blobs']:
        for y in range(height):
            for x in range(width):
                dx = x - blob['x']
                dy = y - blob['y']
                distance = math.sqrt(dx*dx + dy*dy)
                if distance < blob['size'] * 2:
                    influence = 1.0 - (distance / (blob['size'] * 2))
                    blob_influence[y, x] += influence
    if np.max(blob_influence) > 0:
        blob_influence = blob_influence / np.max(blob_influence)
    for y in range(height):
        for x in range(width):
            v1 = math.sin(x / scale1 + time_factor1)
            v2 = math.sin(y / scale2 + time_factor2)
            v3 = math.sin((x + y) / scale3 + time_factor3)
            v4 = math.sin(math.sqrt(x*x + y*y) / scale1 + time_factor1)
            blob_wave = 0
            for blob in plasma_state['blobs']:
                dx = x - blob['x']
                dy = y - blob['y']
                distance = math.sqrt(dx*dx + dy*dy)
                blob_wave += 0.5 * math.sin(distance / 10.0 - time_step)
            plasma_value = (v1 + v2 + v3 + v4 + blob_wave + blob_influence[y, x] + 5) / 10.0
            r = int(255 * (0.5 + 0.5 * math.sin(math.pi * plasma_value + color_shift)))
            g = int(255 * (0.5 + 0.5 * math.sin(math.pi * plasma_value + color_shift + 2*math.pi/3)))
            b = int(255 * (0.5 + 0.5 * math.sin(math.pi * plasma_value + color_shift + 4*math.pi/3)))
            if random.random() < 0.001:  
                r, g, b = 255, 255, 255  
            frame[y, x] = [r, g, b]
    return frame, plasma_state
def play_animation(generate_frame_func, width, height, fps=DEFAULT_FPS, 
                   duration=DEFAULT_DURATION, char_set='standard', colored=True, loop=False):
    """
    Play an animation using the provided frame generation function
    """
    total_frames = int(duration * fps)
    frame_delay = 1 / fps
    animation_state = None
    if generate_frame_func == generate_matrix_rain_frame:
        drops = []
        for _ in range(width // 2):  
            is_focus_drop = random.random() < 0.1  
            drops.append((
                random.randint(0, width - 1),  
                random.randint(-20, height),    
                random.uniform(1.0, 3.0) if is_focus_drop else random.uniform(0.5, 2.0),  
                random.randint(15, 30) if is_focus_drop else random.randint(5, 20),  
                random.uniform(0.8, 1.0) if is_focus_drop else random.uniform(0.5, 0.9),  
                random.uniform(0.05, 0.2),  
                random.uniform(0.5, 1.5)    
            ))
        animation_state = drops
    elif generate_frame_func == generate_firework_frame:
        animation_state = []
        for _ in range(2):
            x = random.randint(width // 6, width * 5 // 6)
            y = height - 1
            color = [
                random.randint(150, 255),  
                random.randint(150, 255),  
                random.randint(150, 255)   
            ]
            firework_type = random.choice(['random', 'circular', 'spiral', 'large'])
            animation_state.append(('rising', x, y, color, [], firework_type, []))
    elif generate_frame_func == generate_starfield_frame:
        stars = []
        for _ in range(500):  
            stars.append((
                random.uniform(-1, 1),  
                random.uniform(-1, 1),  
                random.uniform(0, 1),    
                [
                    random.randint(150, 255),  
                    random.randint(150, 255),  
                    random.randint(200, 255)   
                ],
                random.uniform(0.8, 1.5),      
                random.uniform(0, 2 * math.pi)  
            ))
        animation_state = stars
    elif generate_frame_func == generate_plasma_frame:
        animation_state = {
            'color_shift': 0,
            'blobs': [
                {'x': width * 0.3, 'y': height * 0.3, 'vx': 0.5, 'vy': 0.7, 'size': width/8},
                {'x': width * 0.7, 'y': height * 0.7, 'vx': -0.6, 'vy': -0.4, 'size': width/10},
                {'x': width * 0.5, 'y': height * 0.5, 'vx': 0.3, 'vy': -0.5, 'size': width/12}
            ],
            'wave_params': {
                'scale1': 30.0,
                'scale2': 20.0,
                'scale3': 15.0
            }
        }
    try:
        frame_count = 0
        while frame_count < total_frames or loop:
            if loop and frame_count >= total_frames:
                frame_count = 0
            time_step = (frame_count / total_frames) * 2 * math.pi if total_frames > 0 else 0
            if generate_frame_func == generate_matrix_rain_frame:
                frame = generate_frame_func(width, height, animation_state, time_step)
            elif generate_frame_func == generate_firework_frame:
                frame, animation_state = generate_frame_func(width, height, animation_state, time_step)
            elif generate_frame_func == generate_starfield_frame:
                frame = generate_frame_func(width, height, animation_state, time_step)
            elif generate_frame_func == generate_plasma_frame:
                frame, animation_state = generate_frame_func(width, height, time_step, animation_state)
            else:
                frame = generate_frame_func(width, height, time_step)
            ascii_frame = convert_frame_to_ascii(frame, width, height, char_set, colored)
            clear_console()
            print(ascii_frame)
            if not loop:
                progress = f"Frame: {frame_count+1}/{total_frames} ({(frame_count+1)/total_frames*100:.1f}%)"
            else:
                progress = f"Frame: {frame_count+1} (Loop mode)"
            print(progress)
            time.sleep(frame_delay)
            frame_count += 1
    except KeyboardInterrupt:
        print("\nAnimation stopped by user")
    finally:
        print("\nAnimation finished")
def show_demo_menu():
    """
    Display a menu of available demos
    """
    print("\n===== ASCII Animation Demos =====\n")
    print("1. Sine Wave")
    print("2. Matrix Digital Rain")
    print("3. Fireworks")
    print("4. Starfield")
    print("5. Plasma Effect")
    print("6. Custom Settings")
    print("0. Exit")
    choice = input("\nSelect a demo option (0-6): ")
    return choice
def custom_settings():
    """
    Allow user to input custom settings for animations
    """
    term_width, term_height = detect_terminal_size()
    try:
        width = int(input(f"Width (default: {term_width}): ") or term_width)
        height = int(input(f"Height (default: {term_height}): ") or term_height)
        fps = int(input("FPS (default: 30): ") or 30)
        duration = int(input("Duration in seconds (default: 10): ") or 10)
        print("\nAnimation options:")
        print("1. Sine Wave")
        print("2. Matrix Digital Rain")
        print("3. Fireworks")
        print("4. Starfield")
        print("5. Plasma Effect")
        anim_choice = input("Select animation (default: 1): ") or "1"
        print("\nCharacter set options:")
        print("1. Standard")
        print("2. Detailed")
        print("3. Inverted")
        char_choice = input("Select character set (default: 1): ") or "1"
        char_set = {"1": "standard", "2": "detailed", "3": "inverted"}.get(char_choice, "standard")
        color = input("Enable color? (y/n, default: y): ").lower() != 'n'
        loop = input("Loop animation? (y/n, default: n): ").lower() == 'y'
        animation_funcs = {
            "1": generate_sine_wave_frame,
            "2": generate_matrix_rain_frame,
            "3": generate_firework_frame,
            "4": generate_starfield_frame,
            "5": generate_plasma_frame
        }
        animation_func = animation_funcs.get(anim_choice, generate_sine_wave_frame)
        print("\nStarting animation with custom settings...")
        time.sleep(1)
        play_animation(
            animation_func, width, height, fps, duration, char_set, color, loop
        )
    except ValueError:
        print("Invalid input. Using default values.")
        play_animation(generate_sine_wave_frame, term_width, term_height)
def main():
    parser = argparse.ArgumentParser(description='ASCII Animation Demos')
    parser.add_argument('--width', type=int, default=0, help='Width of ASCII art (default: auto-detect)')
    parser.add_argument('--height', type=int, default=0, help='Height of ASCII art (default: auto-detect)')
    parser.add_argument('--fps', type=int, default=DEFAULT_FPS, help=f'Frames per second (default: {DEFAULT_FPS})')
    parser.add_argument('--duration', type=int, default=DEFAULT_DURATION, 
                        help=f'Animation duration in seconds (default: {DEFAULT_DURATION})')
    parser.add_argument('--demo', type=int, choices=range(1, 6), 
                        help='Run specific demo (1-5) without showing menu')
    args = parser.parse_args()
    if args.width <= 0 or args.height <= 0:
        term_width, term_height = detect_terminal_size()
        if args.width <= 0:
            args.width = term_width
        if args.height <= 0:
            args.height = term_height
    if args.demo:
        animation_funcs = {
            1: generate_sine_wave_frame,
            2: generate_matrix_rain_frame,
            3: generate_firework_frame,
            4: generate_starfield_frame,
            5: generate_plasma_frame
        }
        play_animation(
            animation_funcs[args.demo], 
            args.width, 
            args.height, 
            args.fps, 
            args.duration, 
            'standard', 
            True, 
            False
        )
        return
    while True:
        choice = show_demo_menu()
        if choice == "0":
            print("Exiting demo.")
            break
        elif choice == "1":
            play_animation(generate_sine_wave_frame, args.width, args.height, args.fps, args.duration)
        elif choice == "2":
            play_animation(generate_matrix_rain_frame, args.width, args.height, args.fps, args.duration)
        elif choice == "3":
            play_animation(generate_firework_frame, args.width, args.height, args.fps, args.duration)
        elif choice == "4":
            play_animation(generate_starfield_frame, args.width, args.height, args.fps, args.duration)
        elif choice == "5":
            play_animation(generate_plasma_frame, args.width, args.height, args.fps, args.duration)
        elif choice == "6":
            custom_settings()
        else:
            print("Invalid choice. Please try again.")
        input("\nPress Enter to return to menu...")
        os.system('cls' if os.name == 'nt' else 'clear')
if __name__ == "__main__":
    main()