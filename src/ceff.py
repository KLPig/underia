import random
import perlin_noise
import pygame as pg
import math
from visual import effects as eff
import time

random.seed(time.time())

sf = pg.Surface((200, 200), pg.SRCALPHA)

def rotation_coordinate(rotation):
    return math.sin(math.radians(rotation)), -math.cos(math.radians(rotation))

noises = perlin_noise.PerlinNoise(octaves=2, seed=random.randint(0, 1000000))
snoises = [noises(i / 100) for i in range(1000)]
mx = max(snoises)
mn = min(snoises)
size = 3
sz = int(size * 10)
dst = size * 33
gdt = 23
for j in range(sz):
    i = j / 10
    d = (dst - i * gdt)
    dt = (sz - j) * 120 / sz * ((snoises[j * 999 // sz] - mn) / (mx - mn) * 8 / 5 + .2)
    rots = [rotation_coordinate(90 - dt * i / 9 + dt / 2) for i in range(9, -1, -1)]
    eff.pointed_curve((100 + int(155 * j / sz), int(100 * j / sz), 100 + int(155 * j / sz)),
                      [(int(vx * d + 100), int(vy * d + 100)) for vx, vy in rots], 3, salpha=int(255 - i * 20), target=sf)

pg.image.save(sf, "ceff.png")