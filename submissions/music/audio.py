"""
Ultra-Realistic Audio Sample Generator using Pygame for CLI Instruments
Uses cutting-edge physical modeling and synthesis techniques with Pygame audio
"""
import numpy as np
import pygame
import threading
import time
from typing import Optional, List, Tuple
import random
import math
try:
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)  
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except:
    PYGAME_AVAILABLE = False
class AudioSample:
    """Class to represent and play an audio sample using pygame"""
    def __init__(self, sample_data: np.ndarray, sample_rate: int = 44100):
        self.sample_data = sample_data
        self.sample_rate = sample_rate
        self._sound = None
        self._create_pygame_sound()
    def _create_pygame_sound(self):
        """Convert numpy array to pygame sound"""
        if not PYGAME_AVAILABLE:
            return
        try:
            audio_data = (self.sample_data * 32767).astype(np.int16)
            stereo_data = np.column_stack((audio_data, audio_data))
            self._sound = pygame.sndarray.make_sound(stereo_data)
        except Exception as e:
            print(f"Error creating pygame sound: {e}")
            self._sound = None
    def play(self) -> None:
        """Play the audio sample"""
        if self._sound and PYGAME_AVAILABLE:
            try:
                pygame.mixer.stop()
                self._sound.play()
            except Exception as e:
                print(f"Error playing sound: {e}")
    def stop(self) -> None:
        """Stop the currently playing sound"""
        if PYGAME_AVAILABLE:
            pygame.mixer.stop()
class UltraRealisticInstruments:
    """Ultra-realistic instrument synthesis using advanced physical modeling"""
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
    def generate_piano_note(self, frequency: float, duration: float = 1.0, velocity: float = 0.8) -> AudioSample:
        """Generate ultra-realistic piano using physical string modeling with sympathetic resonance"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        string_tension = 1000 + frequency * 10  
        string_density = 0.0001 / (frequency / 440)  
        string_length = 1.0 / frequency  
        inharmonicity_coeff = 0.00013 * (frequency / 440) ** 1.5
        wave = np.zeros_like(t)
        for n in range(1, 41):
            partial_freq = frequency * n * np.sqrt(1 + inharmonicity_coeff * n**2)
            if partial_freq < self.sample_rate / 2:  
                if n == 1:
                    amplitude = 1.0 * velocity
                elif n <= 3:
                    amplitude = (0.7 / n) * velocity
                elif n <= 8:
                    amplitude = (0.4 / n**1.2) * velocity
                elif n <= 16:
                    amplitude = (0.2 / n**1.5) * velocity
                else:
                    amplitude = (0.05 / n**2) * velocity
                phase_offset = random.uniform(0, 2*np.pi)
                fm_depth = 0.001 * amplitude
                fm_freq = 2.3 + random.uniform(-0.2, 0.2)
                freq_mod = 1 + fm_depth * np.sin(2 * np.pi * fm_freq * t)
                partial_wave = amplitude * np.sin(2 * np.pi * partial_freq * freq_mod * t + phase_offset)
                wave += partial_wave
        hammer_time = 0.001 + (1 - velocity) * 0.001
        hammer_samples = int(hammer_time * self.sample_rate)
        string_attack_time = 0.005
        string_samples = int(string_attack_time * self.sample_rate)
        board_delay_time = 0.008
        board_delay_samples = int(board_delay_time * self.sample_rate)
        envelope = np.ones_like(t)
        if hammer_samples > 0:
            hammer_env = np.exp(np.linspace(-3, 0, hammer_samples))
            envelope[:hammer_samples] *= hammer_env
        decay_fast = np.exp(-t * (8 + frequency/200))  
        decay_medium = np.exp(-t * (2 + frequency/1000))
        decay_slow = np.exp(-t * (0.5 + frequency/4000))
        total_decay = (0.4 * decay_fast + 0.4 * decay_medium + 0.2 * decay_slow)
        envelope *= total_decay
        soundboard_resonance = np.zeros_like(t)
        if board_delay_samples < len(t):
            board_freqs = [100, 200, 315, 500, 800]  
            for board_freq in board_freqs:
                board_amp = 0.02 * np.exp(-(board_freq - 315)**2 / 50000)  
                board_wave = board_amp * np.sin(2 * np.pi * board_freq * t[board_delay_samples:])
                soundboard_resonance[board_delay_samples:] += board_wave
        wave *= envelope
        wave += soundboard_resonance * velocity * 0.3
        sympathetic_freqs = [frequency * 2, frequency * 3, frequency / 2]
        for sym_freq in sympathetic_freqs:
            if 20 <= sym_freq <= 4000:
                sym_amp = 0.02 * velocity / (1 + abs(np.log(sym_freq / frequency)))
                sym_wave = sym_amp * np.sin(2 * np.pi * sym_freq * t) * np.exp(-t * 3)
                wave += sym_wave
        hammer_noise = np.random.normal(0, 0.008 * velocity, len(t))
        hammer_noise *= np.exp(-t * 150)  
        string_noise = np.random.normal(0, 0.002 * velocity, len(t))
        string_noise = np.convolve(string_noise, [0.2, 0.6, 0.2], mode='same')  
        string_noise *= np.exp(-t * 10)
        wave += hammer_noise + string_noise
        if np.max(np.abs(wave)) > 0:
            wave = wave / np.max(np.abs(wave)) * 0.85
        room_reverb = np.random.normal(0, 0.001, len(t)) * envelope
        wave += room_reverb
        return AudioSample(wave, self.sample_rate)
    def generate_guitar_note(self, frequency: float, duration: float = 1.0, fret: int = 0, string_num: int = 1) -> AudioSample:
        """Generate ultra-realistic guitar using enhanced Karplus-Strong with body modeling"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        string_tensions = [82.4, 110.9, 147.8, 196.9, 246.9, 329.6]  
        string_diameters = [0.012, 0.016, 0.024, 0.032, 0.042, 0.053]  
        tension = string_tensions[min(string_num - 1, 5)]
        diameter = string_diameters[min(string_num - 1, 5)]
        delay_samples = self.sample_rate / frequency
        delay_int = int(delay_samples)
        delay_frac = delay_samples - delay_int
        delay_line = np.zeros(delay_int + 1)
        pluck_position = 0.13  
        pluck_samples = int(delay_int * pluck_position)
        for i in range(delay_int):
            if i < pluck_samples:
                delay_line[i] = (i / pluck_samples) * random.uniform(0.8, 1.2)
            else:
                delay_line[i] = ((delay_int - i) / (delay_int - pluck_samples)) * random.uniform(0.8, 1.2)
        pick_noise = np.random.normal(0, 0.05, delay_int + 1)
        delay_line += pick_noise * np.exp(-np.arange(delay_int + 1) * 0.1)
        output = np.zeros(len(t))
        dc_blocker_x1, dc_blocker_y1 = 0, 0
        lowpass_state = 0
        allpass_state = np.zeros(3)
        damping_factor = 0.995 + 0.004 * (frequency / 1000)
        for i in range(len(t)):
            output[i] = delay_line[0]
            feedback = delay_line[0]
            dc_out = feedback - dc_blocker_x1 + 0.995 * dc_blocker_y1
            dc_blocker_x1 = feedback
            dc_blocker_y1 = dc_out
            feedback = dc_out
            feedback = lowpass_state + 0.5 * (feedback - lowpass_state)
            lowpass_state = feedback
            if delay_frac > 0:
                feedback = delay_frac * feedback + (1 - delay_frac) * allpass_state[0]
                allpass_state = np.roll(allpass_state, 1)
                allpass_state[0] = feedback
            feedback *= damping_factor
            if abs(feedback) > 0.1:
                feedback *= 0.998
            delay_line = np.roll(delay_line, -1)
            delay_line[-1] = feedback
        body_modes = [
            (95, 0.8, 15),    
            (180, 0.4, 25),   
            (220, 0.3, 20),   
            (315, 0.2, 30),   
            (400, 0.15, 35),  
            (500, 0.1, 40),
        ]
        body_response = np.zeros_like(output)
        for freq_mode, amp, q in body_modes:
            if freq_mode < self.sample_rate / 2:
                w = 2 * np.pi * freq_mode / self.sample_rate
                r = 1 - (w / q)
                y1, y2 = 0, 0
                for j in range(len(output)):
                    resonance = output[j] + 2 * r * np.cos(w) * y1 - r**2 * y2
                    body_response[j] += amp * resonance
                    y2, y1 = y1, resonance
        wave = output + body_response * 0.4
        attack_time = 0.003  
        attack_samples = int(attack_time * self.sample_rate)
        envelope = np.ones_like(t)
        if attack_samples > 0:
            attack_curve = np.power(np.linspace(0, 1, attack_samples), 0.3)
            envelope[:attack_samples] = attack_curve
        decay_rate = 1.2 + diameter * 10  
        decay_envelope = np.exp(-t * decay_rate)
        envelope *= decay_envelope
        vibrato_freq = 4.5 + random.uniform(-0.5, 0.5)
        vibrato_depth = 0.008 * np.power(envelope, 0.5)  
        vibrato_delay = 0.2  
        vibrato_env = np.ones_like(t)
        vibrato_start = int(vibrato_delay * self.sample_rate)
        if vibrato_start < len(t):
            vibrato_env[vibrato_start:] = 1 + vibrato_depth[vibrato_start:] * np.sin(
                2 * np.pi * vibrato_freq * t[vibrato_start:]
            )
        wave *= envelope * vibrato_env
        if fret > 0:
            fret_buzz = np.random.normal(0, 0.001, len(t))
            fret_buzz *= envelope * np.exp(-t * 20)
            wave += fret_buzz
        room_size = 0.3  
        room_reverb = np.convolve(wave, np.exp(-np.arange(1000) * 0.01), mode='same') * room_size * 0.1
        wave += room_reverb[:len(wave)]
        if np.max(np.abs(wave)) > 0:
            wave = wave / np.max(np.abs(wave)) * 0.8
        return AudioSample(wave, self.sample_rate)
    def generate_drum_hit(self, drum_type: str, duration: float = 0.8, velocity: float = 0.8) -> AudioSample:
        """Generate ultra-realistic drums using advanced physical modeling"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        if drum_type == "kick":
            drum_diameter = 0.55  
            membrane_tension = 500  
            air_volume = 0.08  
            f0 = 55 * (membrane_tension / 500)  
            pitch_sweep = f0 * (1 + 3 * np.exp(-t * 80))  
            membrane_wave = np.zeros_like(t)
            membrane_wave += np.sin(2 * np.pi * np.cumsum(pitch_sweep) / self.sample_rate)
            mode_11_freq = f0 * 1.594
            membrane_wave += 0.3 * np.sin(2 * np.pi * mode_11_freq * t) * np.exp(-t * 15)
            mode_21_freq = f0 * 2.136
            membrane_wave += 0.15 * np.sin(2 * np.pi * mode_21_freq * t) * np.exp(-t * 25)
            impact_duration = 0.005
            impact_samples = int(impact_duration * self.sample_rate)
            impact_noise = np.random.normal(0, 1, len(t))
            impact_envelope = np.exp(-t * 400)  
            impact_filtered = np.zeros_like(impact_noise)
            for i in range(1, len(impact_noise)):
                impact_filtered[i] = 0.6 * impact_filtered[i-1] + 0.4 * impact_noise[i]
            impact_component = 0.8 * impact_filtered * impact_envelope
            port_freq = 45  
            air_component = 0.4 * np.sin(2 * np.pi * port_freq * t) * np.exp(-t * 8)
            shell_freq = 80
            shell_component = 0.2 * np.sin(2 * np.pi * shell_freq * t) * np.exp(-t * 12)
            wave = (membrane_wave * 0.6 + impact_component * 0.3 + 
                   air_component * 0.8 + shell_component * 0.3) * velocity
        elif drum_type == "snare":
            membrane_diameter = 0.35  
            snare_count = 24  
            f0 = 180  
            pitch_sweep = f0 * (1 + 0.8 * np.exp(-t * 25))
            membrane = np.sin(2 * np.pi * np.cumsum(pitch_sweep) / self.sample_rate)
            membrane *= np.exp(-t * 8)  
            wire_fundamental = 3000  
            wire_modes = []
            for i in range(snare_count):
                wire_freq = wire_fundamental * (1 + random.uniform(-0.1, 0.1))
                wire_decay = 15 + random.uniform(-5, 5)
                wire_wave = np.sin(2 * np.pi * wire_freq * t) * np.exp(-t * wire_decay)
                wire_modes.append(wire_wave)
            snare_rattle = np.sum(wire_modes, axis=0) / snare_count
            contact_noise = np.random.normal(0, 0.6, len(t))
            filtered_noise = np.zeros_like(contact_noise)
            hp_state = 0
            for i in range(len(contact_noise)):
                filtered_noise[i] = contact_noise[i] - 0.9 * hp_state
                hp_state = contact_noise[i]
            snare_env = np.exp(-t * 12)
            snare_component = (snare_rattle * 0.6 + filtered_noise * 0.4) * snare_env
            wave = (0.4 * membrane + 0.6 * snare_component) * velocity
        elif drum_type in ["hihat_closed", "hihat_open"]:
            alloy_density = 8400  
            thickness = 0.001  
            diameter = 0.35 if "hihat" in drum_type else 0.5  
            cymbal_modes = []
            base_freq = 8000
            for mode in range(12):
                mode_freq = base_freq * (1 + mode * 0.3) * random.uniform(0.95, 1.05)
                mode_amp = 1.0 / (1 + mode * 0.5)  
                mode_decay = 20 + mode * 5
                if mode_freq < self.sample_rate / 2:
                    mode_wave = mode_amp * np.sin(2 * np.pi * mode_freq * t)
                    mode_wave *= np.exp(-t * mode_decay)
                    cymbal_modes.append(mode_wave)
            cymbal_wave = np.sum(cymbal_modes, axis=0) / len(cymbal_modes)
            shimmer_freq = 15 + random.uniform(-3, 3)
            shimmer = 1 + 0.1 * np.sin(2 * np.pi * shimmer_freq * t)
            cymbal_wave *= shimmer
            attack_noise = np.random.normal(0, 0.8, len(t))
            attack_env = np.exp(-t * 100)
            attack_component = attack_noise * attack_env
            if drum_type == "hihat_closed":
                damping_factor = np.exp(-t * 40)  
            else:
                damping_factor = np.exp(-t * 8)   
            wave = (cymbal_wave * 0.7 + attack_component * 0.3) * damping_factor * velocity
        else:  
            f0 = {"high_tom": 220, "mid_tom": 150, "low_tom": 100}.get(drum_type, 180)
            pitch_sweep = f0 * (1 + 1.5 * np.exp(-t * 20))
            fundamental = np.sin(2 * np.pi * np.cumsum(pitch_sweep) / self.sample_rate)
            overtone1 = 0.4 * np.sin(2 * np.pi * f0 * 1.6 * t) * np.exp(-t * 15)
            overtone2 = 0.2 * np.sin(2 * np.pi * f0 * 2.1 * t) * np.exp(-t * 20)
            shell_freq = f0 * 0.8
            shell_component = 0.3 * np.sin(2 * np.pi * shell_freq * t) * np.exp(-t * 10)
            impact = np.random.normal(0, 0.3, len(t)) * np.exp(-t * 80)
            tom_env = np.exp(-t * (6 + f0/50))  
            wave = (fundamental + overtone1 + overtone2 + shell_component + impact) * tom_env * velocity
        wave = wave * (velocity**0.7)  
        if drum_type == "kick":
            room_delay = int(0.02 * self.sample_rate)  
            if room_delay < len(wave):
                room_response = np.zeros_like(wave)
                room_response[room_delay:] = wave[:-room_delay] * 0.15
                wave += room_response
        if np.max(np.abs(wave)) > 0:
            wave = wave / np.max(np.abs(wave)) * 0.9
        return AudioSample(wave, self.sample_rate)
ultra_realistic_instruments = UltraRealisticInstruments()
def get_ultra_realistic_piano_sample(frequency: float, duration: float = 1.0, velocity: float = 0.8) -> AudioSample:
    """Get ultra-realistic piano sample"""
    return ultra_realistic_instruments.generate_piano_note(frequency, duration, velocity)
def get_ultra_realistic_guitar_sample(frequency: float, duration: float = 1.0, fret: int = 0, string_num: int = 1) -> AudioSample:
    """Get ultra-realistic guitar sample"""
    return ultra_realistic_instruments.generate_guitar_note(frequency, duration, fret, string_num)
def get_ultra_realistic_drum_sample(drum_type: str, duration: float = 0.8, velocity: float = 0.8) -> AudioSample:
    """Get ultra-realistic drum sample"""
    return ultra_realistic_instruments.generate_drum_hit(drum_type, duration, velocity)