from visual import cut_eff
import pygame as pg

w = 480
h = 80

pg.init()

sf = pg.Surface((w, h), pg.SRCALPHA)
cut_eff(sf, h, 0, h // 2, w, h // 2, (50, 127, 0), 0)


pg.image.save(sf, "ceff.png")