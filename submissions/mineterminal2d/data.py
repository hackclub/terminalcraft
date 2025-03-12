from dataclasses import dataclass

@dataclass(order=True)
class Block:
    id: str
    char: str
    color: str
    name: str

    def __iter__(self):
        return iter((self.id, self.char, self.color, self.name))

def get_block(id: str):
    for b in BLOCKS:
        if b.id == id: return b

BLOCKS = [
    Block("dirt", "█", "#A0522D", "Dirt"),
    Block("grass", "█", "#008000", "Grass"),
    Block("stone", "█", "#808080", "Stone"),
    Block("sand", "█", "#FFE4B5", "Sand"),
    Block("log", "║", "#A0522D on #6d381f", "Log"),
    Block("leaves", "🮐", "#32CD32 on #5ccd96", "Leaves"),
    Block("glass", "🮙", "#ccc5c5 on #9dcbe9", "Glass"),
    Block("planks", "🮙", "#845029 on #5a361c", "Planks"),
    Block("stairs_r", "🬵", "#845029 on #87CEFA", "Stairs R"),
    Block("stairs_l", "🬱", "#845029 on #87CEFA", "Stairs L"),
]

DIRT = BLOCKS[0]
GRASS = BLOCKS[1]
STONE = BLOCKS[2]
SAND = BLOCKS[3]
LOG = BLOCKS[4]
LEAVES = BLOCKS[5]

