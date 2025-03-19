import numpy as np
import sounddevice as sd
import json
import time

def play_tone(frequency, duration, volume,sample_rate=44100): # thx gpt
    t = np.linspace(0, duration/1000, int(sample_rate * duration/1000), endpoint=False)
    wave = volume * np.sin(2 * np.pi * frequency * t)  # Generate sine wave
    sd.play(wave, samplerate=sample_rate)
    sd.wait()


def play(fileName):
    with open(fileName) as file:
        notes=json.load(file)
    start=time.time()
    print("\nPlaying...")
    for i in notes:
        note,volume,absoluteStart,duration=i
        delay=absoluteStart/1000-(time.time()-start)
        if delay>0:
            time.sleep(delay)
        play_tone(note,duration,volume)

