import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pygame
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
import keyboard
import sys

class SoundManager:


    def __init__(self, sounds_dir: str = "sounds"):
        self.sounds_dir = Path(sounds_dir)
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self._initialize_pygame()
        self._load_sounds()
    
    def _initialize_pygame(self):
        try:
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
        except pygame.error as e:
            print(f"Failed to initialize pygame mixer: {e}")
            sys.exit(1)
    
    def _load_sounds(self):
        note_files = {
            'sa': 'sa.wav',
            're': 're.wav', 
            'ga': 'ga.wav',
            'ma': 'ma.wav',
            'pa': 'pa.wav',
            'dha': 'dha.wav',
            'ni': 'ni.wav',
            'sa_high': 'sa_high.wav'
        }
        
        if not self.sounds_dir.exists():
            self.sounds_dir.mkdir(parents=True, exist_ok=True)
            print(f"Created {self.sounds_dir} directory. Please add your .wav files there.")
        
        for note, filename in note_files.items():
            file_path = self.sounds_dir / filename
            if file_path.exists():
                try:
                    self.sounds[note] = pygame.mixer.Sound(str(file_path))
                except pygame.error as e:
                    print(f"Failed to load {filename}: {e}")
            else:
                print(f"Warning: {filename} not found in {self.sounds_dir}")
    
    def play_note(self, note: str):
        if note in self.sounds:
            threading.Thread(target=self._play_sound, args=(note,), daemon=True).start()
    
    def _play_sound(self, note: str):
        try:
            self.sounds[note].play()
        except Exception as e:
            print(f"Error playing {note}: {e}")


class RecordingManager:
    
    def __init__(self):
        self.recordings_dir = Path("recordings")
        self.recordings_dir.mkdir(exist_ok=True)
        self.current_recording: List[Tuple[str, float]] = []
        self.recording_start_time: Optional[float] = None
        self.is_recording = False
    
    def start_recording(self):
        self.current_recording = []
        self.recording_start_time = time.time()
        self.is_recording = True
    
    def stop_recording(self):
        self.is_recording = False
        return len(self.current_recording)
    
    def add_note(self, note: str):
        if self.is_recording and self.recording_start_time:
            timestamp = time.time() - self.recording_start_time
            self.current_recording.append((note, timestamp))
    
    def save_recording(self, filename: str) -> bool:
        if not self.current_recording:
            return False
        
        try:
            file_path = self.recordings_dir / f"{filename}.json"
            recording_data = {
                'timestamp': datetime.now().isoformat(),
                'notes': self.current_recording
            }
            
            with open(file_path, 'w') as f:
                json.dump(recording_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving recording: {e}")
            return False
    
    def load_recording(self, filename: str) -> bool:
        try:
            file_path = self.recordings_dir / f"{filename}.json"
            if not file_path.exists():
                return False
            
            with open(file_path, 'r') as f:
                recording_data = json.load(f)
            
            self.current_recording = recording_data.get('notes', [])
            return True
        except Exception as e:
            print(f"Error loading recording: {e}")
            return False
    
    def get_available_recordings(self) -> List[str]:
        return [f.stem for f in self.recordings_dir.glob("*.json")]
    
    def playback_recording(self, sound_manager: SoundManager, callback=None):
        if not self.current_recording:
            return
        
        def playback_thread():
            start_time = time.time()
            for note, timestamp in self.current_recording:
                target_time = start_time + timestamp
                current_time = time.time()
                if target_time > current_time:
                    time.sleep(target_time - current_time)
                
                sound_manager.play_note(note)
                if callback:
                    callback(note)
        
        threading.Thread(target=playback_thread, daemon=True).start()


class MusicUI:    
    def __init__(self):
        self.console = Console()
        self.current_mode = "menu"
        self.last_played_note = ""
        self.status_message = "Welcome to the Indian Classical Music Instrument!"
        
        # notes h, isko bdlna rhega if sond bdlna ho toh
        self.key_to_note = {
            'a': ('sa', 'Sa'),
            's': ('re', 'Re'), 
            'd': ('ga', 'Ga'),
            'f': ('ma', 'Ma'),
            'g': ('pa', 'Pa'),
            'h': ('dha', 'Dha'),
            'j': ('ni', 'Ni'),
            'k': ('sa_high', "Sa'")
        }
    
    def create_layout(self) -> Layout:
        layout = Layout()
        
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=5)
        )
        
        # top part
        header_text = Text("🎵 Indian Classical Music Instrument 🎵", 
                          style="bold magenta", justify="center")
        layout["header"].update(Panel(header_text, style="bright_blue"))
        
        # meow
        if self.current_mode == "menu":
            layout["main"].update(self._create_menu())
        elif self.current_mode == "live":
            layout["main"].update(self._create_live_play())
        elif self.current_mode == "record":
            layout["main"].update(self._create_record_mode())
        elif self.current_mode == "playback":
            layout["main"].update(self._create_playback_mode())
        elif self.current_mode == "select_recording":
            layout["main"].update(self._create_recording_selector())
        
        #  bottom footer footer
        layout["footer"].update(self._create_footer())
        
        return layout
    
    def _create_menu(self) -> Panel:
        """ main menu"""
        menu_text = Text()
        menu_text.append("Main Menu\n\n", style="bold cyan")
        menu_text.append("1. Live Play Mode\n", style="green")
        menu_text.append("2. Record a Session\n", style="yellow") 
        menu_text.append("3. Play Last Recording\n", style="blue")
        menu_text.append("4. Save Recording\n", style="magenta")
        menu_text.append("5. Load & Play Recording\n", style="cyan")
        menu_text.append("6. Exit\n\n", style="red")
        menu_text.append("Press the corresponding number key to select an option.", 
                        style="dim")
        
        return Panel(menu_text, title="Menu", border_style="green")
    
    def _create_live_play(self) -> Panel:
        """live play mode interface"""
        content = Text()
        content.append("🎹 Live Play Mode 🎹\n\n", style="bold green")
        content.append("Press keys to play notes:\n\n", style="cyan")
        
        # key mapping table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Key", style="cyan")
        table.add_column("Note", style="yellow")
        table.add_column("Sargam", style="green")
        
        for key, (note_id, display_note) in self.key_to_note.items():
            table.add_row(key.upper(), note_id.title(), display_note)
        
        content.append(f"\nLast played: {self.last_played_note}\n", style="bright_yellow")
        content.append("\nPress ESC to return to menu", style="dim")
        
        return Panel(content, title="Live Play", border_style="green")
    
    def _create_record_mode(self) -> Panel:
        content = Text()
        content.append("🔴 Recording Mode 🔴\n\n", style="bold red")
        content.append("Recording in progress...\n", style="yellow")
        content.append("Play notes using the keyboard\n\n", style="cyan")
        
        if self.last_played_note:
            content.append(f"Last recorded: {self.last_played_note}\n", style="bright_yellow")
        
        content.append("\nPress SPACE to stop recording", style="dim")
        content.append("\nPress ESC to cancel and return to menu", style="dim")
        
        return Panel(content, title="Record Session", border_style="red")
    
    def _create_playback_mode(self) -> Panel:
        content = Text()
        content.append("▶️  Playback Mode ▶️\n\n", style="bold blue")
        content.append("Playing back recorded session...\n", style="cyan")
        
        if self.last_played_note:
            content.append(f"Currently playing: {self.last_played_note}\n", style="bright_yellow")
        
        content.append("\nPress ESC to return to menu", style="dim")
        
        return Panel(content, title="Playback", border_style="blue")
    
    def _create_recording_selector(self) -> Panel:
        content = Text()
        content.append("🎵 Select Recording to Play 🎵\n\n", style="bold cyan")
        
        if hasattr(self, 'available_recordings') and self.available_recordings:
            content.append("Available recordings:\n\n", style="green")
            for i, recording in enumerate(self.available_recordings, 1):
                content.append(f"{i}. {recording}\n", style="yellow")
            
            content.append(f"\nPress 1-{len(self.available_recordings)} to select a recording\n", style="cyan")
        else:
            content.append("No recordings found.\n", style="red")
        
        content.append("Press ESC to return to menu", style="dim")
        
        return Panel(content, title="Select Recording", border_style="cyan")
    
    def set_available_recordings(self, recordings: List[str]):
        self.available_recordings = recordings
    
    def _create_footer(self) -> Panel:
        footer_text = Text()
        footer_text.append(f"Status: {self.status_message}", style="dim")
        
        return Panel(footer_text, title="Status", border_style="dim")
    
    def update_last_note(self, note: str):
        if note in [note_id for note_id, _ in self.key_to_note.values()]:
            display_note = next(display for note_id, display in self.key_to_note.values() 
                               if note_id == note)
            self.last_played_note = f"{display_note} ({note})"
    
    def set_status(self, message: str):
        """Update status message"""
        self.status_message = message
    
    def set_mode(self, mode: str):
        """Change the current UI mode"""
        self.current_mode = mode


class MusicInstrument:    
    def __init__(self):
        self.sound_manager = SoundManager()
        self.recording_manager = RecordingManager()
        self.ui = MusicUI()
        self.running = True
        self.selection_mode_recordings = []  # recording storage hai iska bhi kuch krna pdega
    
    def run(self):
        try:
            with Live(self.ui.create_layout(), refresh_per_second=10, screen=True) as live:
                self._setup_keyboard_hooks()
                
                while self.running:
                    live.update(self.ui.create_layout())
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            pass
        finally:
            self._cleanup()
    
    def _setup_keyboard_hooks(self):
        for key in self.ui.key_to_note.keys():
            keyboard.on_press_key(key, self._on_note_key)
        
        keyboard.on_press_key('esc', self._on_escape)
        keyboard.on_press_key('space', self._on_space)
        
        # Menu navigation 
        for i in range(1, 10):
            keyboard.on_press_key(str(i), self._on_number_key)
    
    def _on_note_key(self, event):
        key = event.name.lower()
        if key in self.ui.key_to_note:
            note_id, display_note = self.ui.key_to_note[key]
            
            self.sound_manager.play_note(note_id)
            
            self.ui.update_last_note(note_id)
            
            if self.recording_manager.is_recording:
                self.recording_manager.add_note(note_id)
    
    def _on_escape(self, event):
        """escape key - return to menu """
        if self.ui.current_mode != "menu":
            if self.recording_manager.is_recording:
                self.recording_manager.stop_recording()
                self.ui.set_status("Recording cancelled")
            
            self.ui.set_mode("menu")
            self.ui.set_status("Returned to main menu")
            self.selection_mode_recordings = []
    
    def _on_space(self, event):
        if self.ui.current_mode == "record":
            notes_count = self.recording_manager.stop_recording()
            self.ui.set_mode("menu")
            self.ui.set_status(f"Recording stopped. Captured {notes_count} notes.")
    
    def _on_number_key(self, event):
        key = event.name
        
        if self.ui.current_mode == "menu":
            self._handle_menu_selection(key)
        elif self.ui.current_mode == "select_recording":
            self._handle_recording_selection(key)
    
    def _handle_menu_selection(self, key: str):
        if key == '1':  # Play
            self.ui.set_mode("live")
            self.ui.set_status("Live play mode activated")
        
        elif key == '2':  # Record
            self.recording_manager.start_recording()
            self.ui.set_mode("record")
            self.ui.set_status("Recording started")
        
        elif key == '3':  # Playback Latest
            if self.recording_manager.current_recording:
                self.ui.set_mode("playback")
                self.ui.set_status("Playing back last recording...")
                self.recording_manager.playback_recording(
                    self.sound_manager, 
                    callback=self.ui.update_last_note
                )
            else:
                self.ui.set_status("No recording available to play")
        
        elif key == '4':  # Save
            if self.recording_manager.current_recording:
                filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                if self.recording_manager.save_recording(filename):
                    self.ui.set_status(f"Recording saved as {filename}.json")
                else:
                    self.ui.set_status("Failed to save recording")
            else:
                self.ui.set_status("No recording to save")
        
        elif key == '5':  # Load & Play
            recordings = self.recording_manager.get_available_recordings()
            if recordings:
                self.selection_mode_recordings = recordings
                self.ui.set_available_recordings(recordings)
                self.ui.set_mode("select_recording")
                self.ui.set_status("Select a recording to load and play")
            else:
                self.ui.set_status("No recordings found")
        
        elif key == '6':  # Exit
            self.running = False
    
    def _handle_recording_selection(self, key: str):
        try:
            selection = int(key) - 1
            if 0 <= selection < len(self.selection_mode_recordings):
                selected_recording = self.selection_mode_recordings[selection]
                
                if self.recording_manager.load_recording(selected_recording):
                    self.ui.set_mode("playback")
                    self.ui.set_status(f"Loaded and playing: {selected_recording}")
                    self.recording_manager.playback_recording(
                        self.sound_manager,
                        callback=self.ui.update_last_note
                    )
                else:
                    self.ui.set_status("Failed to load recording")
            else:
                self.ui.set_status("Invalid selection")
        except ValueError:
            pass
    
    def _cleanup(self):
        """Cleanup REsources"""
        keyboard.unhook_all()
        pygame.mixer.quit()


if __name__ == "__main__":
    try:
        app = MusicInstrument()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
    finally:
        print("\nThank you for using the Indian Classical Music Instrument!")
        print("🎵 Goodbye! 🎵")