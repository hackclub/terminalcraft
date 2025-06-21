import numpy as np
import soundfile as sf
import sounddevice as sd

class FileAudioEngine:
    def __init__(self, filepath, chunkSize=1024):
        self.filepath = filepath
        self.chunkSize = chunkSize
        self.data, self.sampleRate = sf.read(filepath, dtype='float32')

        if self.data.ndim > 1:
            self.data = np.mean(self.data, axis=1)

        self.position = 0
        self.stream = sd.OutputStream(samplerate=self.sampleRate, channels=1, dtype='float32')
        self.stream.start()

    def read_chunk(self):
        if self.position + self.chunkSize >= len(self.data):
            self.position = 0 

        chunk = self.data[self.position:self.position + self.chunkSize]
        self.stream.write(chunk)
        self.position += self.chunkSize
        return chunk