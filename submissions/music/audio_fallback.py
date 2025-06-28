"""
Fallback audio system for CLI instruments
Uses basic winsound beeps if advanced audio libraries are not available
"""
import threading
import time
try:
    from audio_samples import audio_engine
    ADVANCED_AUDIO = True
    print("✓ Using advanced realistic audio samples")
except ImportError:
    try:
        import winsound
        ADVANCED_AUDIO = False
        print("⚠ Using basic winsound audio (install numpy and simpleaudio for better sound)")
        class BasicAudioEngine:
            """Basic audio engine using winsound beeps"""
            def __init__(self):
                self.currently_playing = False
            def play_piano_note(self, frequency: float) -> None:
                """Play a basic piano note using winsound"""
                if self.currently_playing:
                    return
                self.currently_playing = True
                try:
                    winsound.Beep(int(frequency), 300)
                    if frequency * 2 <= 32767:
                        threading.Timer(0.05, lambda: winsound.Beep(int(frequency * 2), 100)).start()
                except:
                    pass
                def reset():
                    time.sleep(0.4)
                    self.currently_playing = False
                threading.Thread(target=reset, daemon=True).start()
            def play_guitar_note(self, frequency: float) -> None:
                """Play a basic guitar note using winsound"""
                if self.currently_playing:
                    return
                self.currently_playing = True
                try:
                    winsound.Beep(int(frequency), 400)
                    if frequency * 2 <= 32767:
                        threading.Timer(0.1, lambda: winsound.Beep(int(frequency * 2), 100)).start()
                except:
                    pass
                def reset():
                    time.sleep(0.5)
                    self.currently_playing = False
                threading.Thread(target=reset, daemon=True).start()
            def play_drum_hit(self, drum_type: str) -> None:
                """Play a basic drum hit using winsound"""
                if self.currently_playing:
                    return
                self.currently_playing = True
                drum_freqs = {
                    'kick': 60, 'snare': 200, 'hihat_closed': 8000, 'hihat_open': 6000,
                    'tom1': 300, 'tom2': 200, 'tom3': 150, 'crash': 4000, 'ride': 3000
                }
                try:
                    freq = drum_freqs.get(drum_type, 200)
                    duration = 800 if drum_type in ['crash', 'ride'] else 200
                    winsound.Beep(freq, duration)
                except:
                    pass
                def reset():
                    time.sleep(0.3)
                    self.currently_playing = False
                threading.Thread(target=reset, daemon=True).start()
            def stop_all(self) -> None:
                """Stop all sounds (not supported in basic mode)"""
                pass
        audio_engine = BasicAudioEngine()
    except ImportError:
        print("✗ No audio system available. Please install numpy and simpleaudio for audio support.")
        class NoAudioEngine:
            """Dummy audio engine when no audio is available"""
            def play_piano_note(self, frequency: float) -> None:
                print(f"🎹 Piano note: {frequency:.1f} Hz")
            def play_guitar_note(self, frequency: float) -> None:
                print(f"🎸 Guitar note: {frequency:.1f} Hz")
            def play_drum_hit(self, drum_type: str) -> None:
                print(f"🥁 Drum hit: {drum_type}")
            def stop_all(self) -> None:
                pass
        audio_engine = NoAudioEngine()
        ADVANCED_AUDIO = False