import sys
import cv2
import numpy as np
import pygame
from moviepy import VideoFileClip
from time import sleep, time

try:
    file_path = sys.argv[1]
except:
    raise ValueError('ERROR: File path not provided')
cap = cv2.VideoCapture(file_path)

def clear():
    print('\033c', end='')

brightness = ' .:-~=+*#%@'
display = ''
fps = cap.get(cv2.CAP_PROP_FPS)
try:
    frame_delay = 1/fps
except:
    frame_delay = 0

if not cap.isOpened():
    raise ValueError('ERROR: Could not open file')

clip = VideoFileClip(file_path)
clip.audio.write_audiofile('temp_audio.wav', codec='pcm_s16le')
pygame.mixer.init()
pygame.mixer.music.load('temp_audio.wav')
pygame.mixer.music.play()
start_time = time()

frame_index = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    value = np.round(frame/255*(len(brightness)-1)).astype(int)
    display = '\n'.join(''.join(brightness[x] for x in y) for y in value)
    sys.stdout.write(display)

    sleep(max(0, (frame_index * frame_delay) - (time() - start_time)))
    clear()
    frame_index += 1
cap.release()
