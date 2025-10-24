import os
import pygame as pg

assert __file__.endswith('docs/assets/graphics/items/docitem_update.py')

for l in os.listdir('.'):
    if not l.endswith('.png'):
        continue
    img = pg.image.load(l)
    if img.get_width() + img.get_height() < 400:
        img = pg.transform.scale(img, (200, 200 * img.get_height() // img.get_width()))
    pg.image.save(img, l)
