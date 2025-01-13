import perlin_noise
import pygame as pg

noise = perlin_noise.PerlinNoise(octaves=0.4, seed=4002)
map_dt = [[noise([x / 30.0, y / 30.0]) for x in range(240)] for y in range(240)]
m_min = min(min(d) for d in map_dt)
m_max = max(max(d) for d in map_dt)
surf = pg.Surface((240, 240))

lvs = [(255, 41, 0), (255, 127, 0), (0, 255, 0), (0, 127, 0), (255, 255, 255), (127, 127, 127)]

print(m_min, m_max)

for x in range(240):
    for y in range(240):
        dt = map_dt[x][y]
        dt_norm = (dt - m_min) / (m_max - m_min)
        dt_norm = max(0.0, min(1.0, dt_norm))
        color_idx = int(dt_norm * (len(lvs) - 1))
        color = lvs[color_idx]
        surf.set_at((x, y), color)
pg.draw.circle(surf, (0, 255, 0), (120, 120), 20)

pg.image.save(surf, "map_summon.png")