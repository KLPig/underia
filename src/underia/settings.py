import constants
import pygame as pg
from resources import path
from underia import game

SETTINGS = [
    ('Graphics', [
        ['BLADE_EFFECT_QUALITY', 'Blade Cutting Effect', (1, 'High'), (2, 'Low'), (3, 'Fast')],
        ['PARTICLES', 'Particles', (0, 'Least'), (1, 'Less'), (2, 'Normal')],
        ['EASY_BACKGROUND', 'Background', (0, 'Graphic'), (1, 'Easy')],
        ['HEART_BAR', 'Heart Status Bars', (0, 'Off'), (1, 'On')],
        ['FADING_PARTICLE', 'Fading Particles', (0, 'Off'), (1, 'On')],
        ['USE_ALPHA', 'Enable Transparent', (0, 'Off'), (1, 'On')],
        ['LIGHTING', 'Lighting', (0, 'Off'), (1, 'On')]
    ]),
    ('Content', [
        ['APRIL_FOOL', 'April Fools', (0, 'Off'), (1, 'On')],
        ['ENTITY_NUMBER', 'Entity Number', (6, 'Fast'), (12, 'Low'), (18, 'Normal'), (28, 'High'), (36, 'Fancy')],
        ['FPS', 'FPS Limit', (120, '120')],
        ['ULTIMATE_AMMO_BONUS', 'Unlimited Ammo No.', (4000, '4000'), (10000, '10000'), (20000, '20000'), (114514, '114514')],
        ['LANG', 'Language', ('en', 'English'), ('zh', '简体中文')]
    ])
]

def set_settings():
    sel_c = 0
    sel_s = 0
    window = pg.display.get_surface()
    font = pg.font.Font(path.get_path('assets/fz-pixel.ttf'),
                        54)
    while True:
        window.fill((0, 0, 0))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    sel_c = (sel_c - 1 + len(SETTINGS[sel_s][1])) % len(SETTINGS[sel_s][1])
                elif event.key == pg.K_DOWN:
                    sel_c = (sel_c + 1) % len(SETTINGS[sel_s][1])
                elif event.key == pg.K_LEFT:
                    sel_s = (sel_s - 1 + len(SETTINGS)) % len(SETTINGS)
                    sel_c = 0
                elif event.key == pg.K_RIGHT:
                    sel_s = (sel_s + 1) % len(SETTINGS)
                    sel_c = 0
                elif event.key in [pg.K_RETURN, pg.K_z]:
                    st = SETTINGS[sel_s][1][sel_c]
                    at = getattr(constants, st[0])
                    opt = st[2:]
                    i = [i for i, (j, o) in enumerate(opt) if j == at][0]
                    setattr(constants, st[0], opt[(i + 1) % len(opt)][0])
                    if st[1] == 'Language':
                        game.get_game().displayer.__init__()
                elif event.key == pg.K_ESCAPE:
                    return
        tr = font.render(SETTINGS[sel_s][0], True, (255, 255, 255))
        window.blit(tr, (100, 100))
        for i, st in enumerate(SETTINGS[sel_s][1]):
            at = getattr(constants, st[0])
            ot = st[1]
            opt = st[2:]
            dt = at
            for j, o in enumerate(opt):
                if j == at:
                    dt = o[1]
            if i == sel_c:
                col = (255, 255, 0)
            else:
                col = (255, 255, 255)
            tr = font.render(ot, True, col)
            window.blit(tr, (100, 200 + 80 * i))
            tr = font.render(str(dt), True, col)
            window.blit(tr, (window.get_width() - 50 - tr.get_width(), 200 + 80 * i))
        pg.display.flip()
