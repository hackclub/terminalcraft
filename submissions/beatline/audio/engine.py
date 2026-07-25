import sounddevice as sd
import numpy as np

class AudioEngine:
    @classmethod
    def create(cls, samplerate=44100, chunkSize=1024, use_loopback=False):
        self = cls()
        self.samplerate = samplerate
        self.chunkSize = chunkSize
        self.device = self._get_loopback_device() if use_loopback else None
        self.stream = sd.InputStream(
            channels=2 if use_loopback else 1,
            samplerate=self.samplerate,
            blocksize=self.chunkSize,
            dtype='float32',
            device=self.device
        )
        self.stream.start()
        return self

    def read_chunk(self):
        data, _ = self.stream.read(self.chunkSize)
        return np.mean(data, axis=1) if data.ndim > 1 else np.squeeze(data)

    def _get_loopback_device(self):
        for device in sd.query_devices():
            if 'loopback' in device['name'].lower() or 'stereo mix' in device['name'].lower():
                return device['name']
        raise RuntimeError("Loopback device not found. Make sure your system supports it.")