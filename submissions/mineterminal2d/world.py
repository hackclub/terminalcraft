from perlin_noise import PerlinNoise
import random

from data import DIRT, GRASS, LOG, SAND, STONE, Block, LEAVES

class World:
    on_update: "function"

    def __init__(self, seed: int):
        self.seed = seed
        self._perlin = PerlinNoise(seed=seed, octaves=5)
        self._random = random.Random(seed)
        self.changed = dict() # type: dict[tuple[int, int], Block]
        self._cache = dict()

    def default_height_at(self, x: int):
        return int(self._perlin.noise(x / 300) * 30 + 15)

    def random(self, init: str):
        self._random.seed(init)
        return self._random

    def get_block_at(self, x: int, y: int):
        if (x, y) in self.changed: return self.changed[(x, y)]
        if (x, y) in self._cache: return self._cache[(x, y)]

        def get():
            height = self.default_height_at(x)
            
            tree = self.random(f"{self.seed}.{x // 5}").randint(0, 3) == 0

            if y > height:
                tx = x % 5
                ty = y - self.default_height_at((x // 5) * 5 + 2) - 1
                if tree and ty < 7:
                    if ty in range(3) and tx == 2: return LOG
                    if ty == 3 and tx in range(1, 4): return LEAVES
                    if ty > 0 and ty < 3 and (tx in range(0, 2) or tx in range(3, 5)): return LEAVES
                
                return None
            else:
                if not tree and (height - y) < 4:
                    if self.random(f"{self.seed}.{x // 7}").randint(0, 3) == 0:
                        return SAND if (y == height or self.random(f"{self.seed}.{x}-{y}").randint(0, 4) > (height - y)) else DIRT
                
                if y == height: return GRASS
                stoneh = self.random(f"{self.seed}-{x}-{int(y / 2)}").randint(0, 2)
                if y < height - stoneh - 5: return STONE

                return DIRT
        
        blk = get()
        self._cache[(x, y)] = blk
        return blk
    
    def set_block_at(self, x: int, y: int, block: Block | None):
        if self.on_update:
            self.on_update()
        self.changed[(x, y)] = block
        self._cache[(x, y)] = block
