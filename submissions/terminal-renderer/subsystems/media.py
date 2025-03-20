from PIL import Image 
from subsystems.display import DisplaySettings
import numpy, math

class Media:
    def __init__(self, path):
        self.gif = Image.open(path)
        self.gifLength = self.gif.n_frames
        self.frames = []
        for i in range(self.gifLength):
            self.gif.seek(i)
            self.frames.append(numpy.array(self.rescale(self.gif.copy()).convert("RGB")))
    
    def rescale(self, image:Image.Image):
        # x, y = image.size
        # sx = DisplaySettings.WIDTH/x
        # sy = DisplaySettings.HEIGHT/y
        # sf = min(sx, sy)
        # return image.resize((int(x*sf), int(y*sf)))
        return image.resize((DisplaySettings.WIDTH, DisplaySettings.HEIGHT))

    def get(self, index = 0):
        return self.frames[index]