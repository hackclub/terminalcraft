from mido import MidiFile
import json
def shufflePlaybackError():# only sequential playback!!!
    print("\nBuzzer hardware only supports sequencial playback, please make sure your MIDI file fits that requirement.")
    return 1

def compile(fileName):
    results=getNotes(fileName) # (note, velocity, absoluteStart, duration)
    if results==1:
        return 1
    notes,tpqn,usqn=results
    for i in range(len(notes)):
        notes[i][0]=note2frequ(notes[i][0])
        notes[i][1]=normalizeV(notes[i][1])
        notes[i][2]=tick2ms(notes[i][2],tpqn,usqn)
        notes[i][3]=tick2ms(notes[i][3],tpqn,usqn)
    jsonFile=fileName+".json"
    with open(jsonFile,"w") as file:
        json.dump(notes,file)
    print(f"Your midi file is now playable on a buzzer hardware with {jsonFile}, try it out with p(play) mode!")
    

def note2frequ(note):
    return 440*2**((note-69)/12)

def normalizeV(velocity):
    return velocity/127

def tick2ms(time,tpqn,usqn):
    return (time*usqn)/(tpqn*1000)


def getNotes(fileName):
    notes=[] # (note, velocity, relativeStart, duration)

    mid=MidiFile(fileName)
    tpqn = mid.ticks_per_beat # Ticks Per Quarter Note

    # only sequential playback!!!
    if len(mid.tracks)!=1:
        return shufflePlaybackError()
    # note-local vars
    noteOn=False
    astotn=0 # stands for "absolute start time of this note"
    note=0
    velocity=0
    # global vars
    absTime=0
    usqn=500000 # tempo, no idea why chatgpt named it usqn, 500000 is the defult
    for msg in mid.tracks[0]:
        absTime+=msg.time
        if msg.type=='set_tempo':
            usqn = msg.tempo
        elif msg.type=="note_on":
            if noteOn:# omg is two notes trying to play at the same time?
                if msg.velocity==0 and msg.note==note:# just another way to note_off acording to gpt
                    notes.append([note,velocity,astotn,absTime-astotn])
                    noteOn=False
                else:# only sequential playback!!!
                    return shufflePlaybackError()
            else:# a new note is playing, record its info and will be sotred when stoped
                noteOn=True
                astotn=absTime
                note=msg.note
                velocity=msg.velocity

        elif msg.type=="note_off":
            if not noteOn:
                print("Your MIDI file tried to stop a note that is never played, please fix it somehow.")
                return 1
            notes.append((note,velocity,astotn,absTime-astotn))
            noteOn=False

    return notes, tpqn, usqn
                

