from underia import dialog
from resources import path
import constants
import pygame as pg
import os

try:
    pt = path.get_path('assets/graphics/legend')
    image = {l: pg.image.load(os.path.join(pt, l)) for l in os.listdir(pt) if l.endswith('.png')}
except FileNotFoundError:
    print('Warning: File not found.\nIf story unused, ignore this warning.')

dialogger = None

def show_story(name, words):
    global dialogger
    window = pg.display.get_surface()
    if dialogger is None:
        dialogger = dialog.Dialogger(48, pg.Rect(0, window.get_height() - 180, window.get_width(), 180), target_surface=window,
                                     speed=13)
    texts = words

    for t in texts:
        dialogger.push_dialog(*t)
    dialogger.update([])
    while True:
        dialogger.dialog_rect = pg.Rect(0, window.get_height() - 180, window.get_width(), 180)
        window.fill((0, 0, 0))
        no = [i for i in range(len(texts)) if dialogger.curr_text in texts[i]][0]
        im = image[f'{name}_{no}.png']
        img = pg.transform.scale(im, ((window.get_height() - 180) / im.get_height() * im.get_width(), window.get_height() - 180))
        imr = img.get_rect(midtop=(window.get_width() / 2, 0))
        window.blit(img, imr)
        keys = []
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYDOWN:
                keys.append(event.key)
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    quit()
                elif event.key == pg.K_F4:
                    constants.FULLSCREEN = not constants.FULLSCREEN
                    pg.display.set_mode(pg.display.get_window_size(), (pg.FULLSCREEN if constants.FULLSCREEN else 0) | constants.FLAGS)
        if pg.K_c in keys or pg.K_DELETE in keys:
            cv = pg.Surface(window.get_size(), pg.SRCALPHA)
            cv.blit(window, (0, 0))
            if constants.USE_ALPHA:
                for i in range(255):
                    pg.event.get()
                    window.fill((0, 0, 0))
                    cv.set_alpha(255 - i)
                    window.blit(cv, (0, 0))
                    pg.display.update()
                break
        dialogger.update(keys)
        pg.display.update()
        if dialogger.curr_text == '':
            break
