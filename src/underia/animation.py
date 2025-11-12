import random

from underia import game
import math
import pygame as pg

class Animation:
    def __init__(self, target: str, frames: list[int], nt: int = 10):
        self.target = target
        self.frames = frames
        self.cur = 0
        self.nt = nt
        self.tick = 0
        self.setup = False
        assert len(self.frames) > 0, "No frames provided for animation"

    def update(self):
        if not self.setup:
            self.setup = True
            game.get_game().graphics[self.target] = game.get_game().graphics[self.target + str(self.frames[0])]
        if self.tick >= self.nt:
            self.tick = 0
            self.cur = (self.cur + 1) % len(self.frames)
            game.get_game().graphics[self.target] = game.get_game().graphics[self.target + str(self.frames[self.cur])]
        else:
            self.tick += 1

class SoulAnimation:
    def __init__(self):
        self.started = False

    def update(self):
        if self.started:
            return
        self.started = True
        gfx = game.get_game().graphics
        st = gfx.graphics.keys()
        ps = [x for x in st if x.startswith("items_soul_of_")] + ["items_my_soul"]
        for dx in ps:
            print("Soul animation:", dx)
            dr = random.randint(0, 10)
            for i in range(10):
                dy = math.sin((i + dr) * 2 * math.pi / 10) * 3
                sf = pg.Surface(gfx[dx].get_size(), pg.SRCALPHA)
                sf.blit(gfx[dx], (0, int(dy)))
                gfx[dx + str(i)] = sf
            ANIMATIONS.append(Animation(dx, list(range(10)), 8))




ANIMATIONS = [
    Animation("items_spot", [1, 2, 3, 4], 15),
    Animation("items_dark_matter", [1, 2], 30),
    Animation("items_stone_of_faith", [1, 2, 3], 20),
    Animation("items_chaos_diamond", [1, 2, 3, 4, 5, 6, 7, 8], 15),
    Animation("items_chaos_reap", [1, 2, 3, 4], 10),
    SoulAnimation()
]



