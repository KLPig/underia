import os

import pygame as pg


def convert_weapon(weapon_img):
    im = pg.image.load(weapon_img)
    im = pg.transform.rotate(im, -45)
    l = im.get_width() + 10
    s = pg.Surface((l + im.get_width(), im.get_height()), pg.SRCALPHA)
    imr = im.get_rect(midleft=(l, im.get_height() // 2))
    s.blit(im, imr)
    pg.image.save(s, 'weapons/' + weapon_img)


if not os.path.exists('weapons'):
    os.mkdir('weapons')

for f in os.listdir('.'):
    if f.endswith('.png'):
        convert_weapon(f)
