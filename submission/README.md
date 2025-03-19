# Buzzer Tone: a MIDI file to raw frequencies compiler
### Setup
- Install Python (minimum version 3.8) and PIP
- Install all packages in [requirements.txt](./requirements.txt) by running command `pip install mido sounddevice numpy`
### Usage
Run command `python buzzerTone.py <mode> <filename>`
What does "mode" represents:
1. `p`-play: test play compiled frequencies. Example: `python buzzerTone.py p "./testFiles/sus.mid.json"`
2. `c`-compile: compile a MIDI file into frequencies in JSON format. Example: `python buzzerTone.py c "./testFiles/sus.mid"`

Note: if your MIDI file has ANY form of Shuffle Playback, it will not be accepted, because you can only do Sequential Playback on a Buzzer hardware.

In compiled JSON files, there will be an array storing multiple arrays with 4 floats, where each element in those arrays represents:
1. Frequency (Hz)
2. Volume (/1)
3. Absolute Start time (ms)
4. Duration (ms)

Now go ahead and play some awesome music on your buzzer!
