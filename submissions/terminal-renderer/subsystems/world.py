import numpy

class Block:
    BLOCK_INDEX = list(range(4))
    AIR = 0
    STONE = 1
    DIRT = 2
    GRASS = 3

    COLOR_MAP = {
        AIR:    (  0,  0,  0),
        STONE:  (150,150,150),
        DIRT:   (150,100,100),
        GRASS:  (  0,200,  0),
    }

class WorldState:
    def __init__(self, r):
        self.offset = r
        self.world = numpy.zeros((r*2, r*2, r*2))

        # TEST, TO-DO: REMOVE!
        self.setBlock(5,5,5,Block.GRASS)
    def setBlock(self, x, y, z, block):
        self.world[x-self.offset][y-self.offset][z-self.offset] = block
    def getBlock(self, x, y, z):
        return self.world[x-self.offset][y-self.offset][z-self.offset]