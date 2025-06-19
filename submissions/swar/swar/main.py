from mido import Message, MidiFile, MidiTrack, MetaMessage
from swar.map_notes import mapper, note_to_midi
import os
import click
import swar.player as player
from music21 import stream, note
import sys

def resource_path(path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, path)
    return os.path.abspath(path)

@click.group(invoke_without_command=True)
@click.pass_context
def swar(ctx):
    if ctx.invoked_subcommand is None:
        click.echo("\n")
        print_pixel_art()
        click.echo("\n" + "-"*60)
        click.echo("                      SWAR CLI TOOL")
        click.echo("-"*60)
        click.echo(" Convert any text or code into musical notes and play them")
        click.echo(" like a piano – encoding information through sound.\n")
        click.echo(" Swar compiles characters into MIDI notes, plays them, and")
        click.echo(" stores them in a MIDI file. Ideal for creative sound-based")
        click.echo(" data transmission and artistic expression.")
        click.echo("-"*60)

def generate_musicxml(note_list, output='swar_sheet.musicxml'):
    s = stream.Stream()
    for n in note_list:
        s.append(note.Note(n))
    s.write('musicxml', fp=output)

@click.command()
@click.argument("text")
@click.option("--output", default="swar", help="specifies name of music file")
@click.option("-ms", is_flag=True, help="use this option to save a music sheet")
def musicfy(text: str, output: str = "swar", ms: bool = False):
    mid = MidiFile()
    track = MidiTrack()
    tempo = MetaMessage('set_tempo', tempo=180000)

    mid.tracks.append(track)
    track.append(tempo)
    track.append(Message('program_change', program=0, time=0))

    notes = mapper(text)
    MIDI_NOTES = [note_to_midi(n) for n in notes]

    for i, midi_val in enumerate(MIDI_NOTES):
        if i == len(MIDI_NOTES) - 1:
            track.append(Message('note_on', note=midi_val, velocity=64, time=0))
            track.append(Message('note_off', note=midi_val, velocity=60, time=2500))
        elif midi_val == 37:
            track.append(Message('note_on', note=midi_val, velocity=64, time=0))
            track.append(Message('note_off', note=midi_val, velocity=55, time=700))
        else:
            track.append(Message('note_on', note=midi_val, velocity=64, time=0))
            track.append(Message('note_off', note=midi_val, velocity=64, time=360))

    midi_path = f"{output}.mid"
    if os.path.exists(midi_path):
        os.remove(midi_path)

    mid.save(midi_path)
    click.echo("Successfully compiled your text to musical notes...")

    if ms:
        generate_musicxml(notes)

def print_pixel_art():
    '''Prints SWAR ASCII logo'''
    S = [
        " █████ ",
        "█      ",
        " █████ ",
        "      █",
        " █████ "
    ]
    
    W = [
        "█   █ ",
        "█   █ ",
        "█ █ █ ",
        "██ ██ ",
        "█   █ "
    ]
    
    A = [
        "█████ ",
        "█   █  ",
        "█████  ",
        "█   █  ",
        "█   █  "
    ]
    
    R = [
        " █████  ",
        "█   █  ",
        "█████  ",
        "█  █   ",
        "█   █  "
    ]
    
    word = [S, W, A, R]
    terminal_width = 60

    for row in range(5):
        line = ""
        for letter in word:
            line += letter[row] + "  "
        spaces = (terminal_width - len(line)) // 2
        print(" " * spaces + line)

swar.add_command(musicfy)
swar.add_command(player.play)

if __name__ == "__main__":
    swar()
