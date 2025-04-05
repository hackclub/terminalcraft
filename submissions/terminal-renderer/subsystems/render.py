from subsystems.camera import *
from subsystems.world import *
from subsystems.display import *
from subsystems.debug import *

CUBE_INSTRUCTIONS = [
    # x
    [0,0,0,1,0,0],
    [0,0,1,1,0,1],
    [0,1,0,1,1,0],
    [0,1,1,1,1,1],
    # y
    [0,0,0,0,1,0],
    [0,0,1,0,1,1],
    [1,0,0,1,1,0],
    [1,0,1,1,1,1],
    # z
    [0,0,0,0,0,1],
    [0,1,0,0,1,1],
    [1,0,0,1,0,1],
    [1,1,0,1,1,1],
]
CUBE_SIZE = 5

class Renderer:
    def __init__(self, debug: Debug, camera:Camera, world:WorldState):
        self.debug = debug
        self.camera = camera
        self.world = world
        self.displayData = DisplayData(debug)
        self.lastBlocksProccessed = 0
        self.lastLinesProcessed = 0
    def render(self):
        # clear
        self.camera.update()
        self.displayData.reset()
        # calculations
        rotationMatrix = self.camera.latestRotation
        projectionMatrix = self.camera.latestProjection
        blocksProcessed = 0
        linesProcessed = 0
        for x in range(self.world.offset*2):
            for y in range(self.world.offset*2):
                for z in range(self.world.offset*2):
                    if self.world.getBlock(x,y,z) == Block.AIR:
                        continue
                    translationBase = [x-self.camera.x, y-self.camera.y, z-self.camera.z]

                    for instruction in CUBE_INSTRUCTIONS:
                        pointA = [translationBase[0] + instruction[0] * CUBE_SIZE,
                                  translationBase[1] + instruction[1] * CUBE_SIZE,
                                  translationBase[2] + instruction[2] * CUBE_SIZE]
                        pointB = [translationBase[0] + instruction[3] * CUBE_SIZE,
                                  translationBase[1] + instruction[4] * CUBE_SIZE,
                                  translationBase[2] + instruction[5] * CUBE_SIZE]
                        projectionA = self.camera.project(pointA)
                        projectionB = self.camera.project(pointB)

                        distance = numpy.linalg.norm(pointA)

                        self.displayData.drawLine(
                            projectionA[0]+DisplaySettings.WIDTH/2,
                            projectionA[1]+DisplaySettings.HEIGHT/2,
                            projectionB[0]+DisplaySettings.WIDTH/2,
                            projectionB[1]+DisplaySettings.HEIGHT/2,
                            Block.COLOR_MAP[self.world.getBlock(x,y,z)],
                            distance
                        )
                        linesProcessed += 1
                    blocksProcessed += 1
        self.lastBlocksProccessed = blocksProcessed
        self.lastLinesProcessed = linesProcessed
        self.debug.post(" | Renderer: {} blocks, {} lines, processed".format(blocksProcessed, linesProcessed))
        return self.displayData