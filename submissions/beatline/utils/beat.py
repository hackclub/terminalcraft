import numpy as np

class BeatDetector:
    sensitivity = 0.5
    previousEnergy = 0

    def detect(self, samples):
        energy = np.linalg.norm(samples)
        beat = energy > self.previousEnergy * (1 + self.sensitivity)
        self.previousEnergy = energy * 0.9 + self.previousEnergy * 0.1
        return beat