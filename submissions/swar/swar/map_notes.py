import json
import sys, os

def resource_path(path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, path)
    return path

with open(resource_path('swar/notes.json'), 'r') as file:
    data = json.load(file)

special_symbols = {
    " " : "!0",
    "!" : "!1",
    '"' : "!2",
    "#" : "!3",
    "$" : "!4",
    "%" : "!5",
    "&" : "!6",
    "'" : "!7",
    "(" : "!8",
    ")" : "!9",
    "*" : "@0",
    "+" : "@1",
    "," : "@2",
    "-" : "@3",
    "." : "@4",
    "/" : "@5",
    ":" : "@6",
    ";" : "@7",
    "<" : "@8",
    "=" : "@9",
    ">" : "$0",
    "?" : "$1",
    "@" : "$2",
    "[" : "$3",
    "\\" : "$4",
    "]" : "$5",
    "^" : "$6",
    "_" : "$7",
    "`" : "$8",
    "{" : "$9",
    "|" : "%0",
    "}" : "%1",
    "~" : "%2"
}


pitch_map= {
        "C": 0,
        "D": 2,
        "E": 4,
        "F": 5,
        "G": 7,
        "A": 9,
        "B": 11,
    }
acc_map = {
        "#": 1
    }

def mapper(text:str):
    text = text.lower()
    for key in special_symbols:
        if key in text:
            text = text.replace(key, special_symbols[key])
    
    note_data = [data[f"{char}"] for char in text]
    return note_data

def note_to_midi(note:str,issmooth:bool=True):
    accidental_offset = 0
    for i in note:
        if i in pitch_map.keys():
            pitch_index = pitch_map[i]
        elif i in acc_map.keys():
            accidental_offset = acc_map[i]
        else:
            octave = int(i)
    
    MIDI = 12 * (octave + 1) + pitch_index + accidental_offset
    
    if issmooth:
        return int(round(MIDI))
    else :
        return MIDI
    