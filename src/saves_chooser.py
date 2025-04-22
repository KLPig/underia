import copy
import math
import os
import pygame as pg
import constants

from resources import path
import underia
import pickle

n = -1

selects = []

for i in range(1, 10):
    if os.path.exists(path.get_save_path(f".save{i}.pkl")):
        selects.append(f"Save {i}")
    else:
        selects.append(f"Save {i}(empty)")

anchor = 0
cmds = []
cb = 0
bios = [pg.image.load(path.get_path(f'assets/graphics/background/{b}.png')) for b in ['forest', 'rainforest', 'snowland', 'heaven',
                                                                                      'inner', 'hell', 'desert']]
bios = [pg.transform.scale(b, (100, 100)) for b in bios]
datas = []

for i in range(1, 10):
    try:
        with open(path.get_save_path(f".save{i}.data.pkl"), "rb") as f:
            datas.append(pickle.load(f))
    except FileNotFoundError:
        datas.append(underia.GameData(underia.PlayerProfile()))
    except ModuleNotFoundError:
        datas.append(underia.GameData(underia.PlayerProfile()))

pf = underia.PlayerProfile()
t = 0

def choose_save():
    global n, selects, anchor, cmds, cb, t
    clk = pg.time.Clock()
    font = pg.font.Font(path.get_path('assets/dtm-mono.otf' if constants.LANG != 'zh' else 'assets/fz-pixel.ttf'), 48)
    font_large = pg.font.Font(path.get_path('assets/dtm-mono.otf' if constants.LANG != 'zh' else 'assets/fz-pixel.ttf'), 72)

    font_large.set_bold(True)
    font.set_bold(True)
    font.set_italic(True)
    screen = pg.display.get_surface()
    mask = pg.Surface(screen.get_size(), pg.SRCALPHA)
    mask.fill((0, 0, 0, 255))
    tick = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return cmds, None
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    return cmds, None
                elif event.key == pg.K_UP:
                    if n != -1:
                        n = (n - 1 + len(selects)) % len(selects)
                        anchor = n
                    else:
                        n = 0
                        anchor = 0
                elif event.key == pg.K_DOWN:
                    if n != -1:
                        n = (n + 1) % len(selects)
                        anchor = n
                    else:
                        n = 0
                        anchor = 0
                elif event.key == pg.K_F4:
                    constants.FULLSCREEN = not constants.FULLSCREEN
                    pg.display.set_mode(pg.display.get_window_size(), (pg.FULLSCREEN if constants.FULLSCREEN else 0) | constants.FLAGS)
                elif event.key in [pg.K_RETURN, pg.K_z]:
                    if n != -1:
                        cv = pg.Surface(screen.get_size(), pg.SRCALPHA)
                        cv.blit(screen, (0, 0))
                        if constants.USE_ALPHA:
                            for i in range(255):
                                pg.event.get()
                                screen.fill((0, 0, 0))
                                cv.set_alpha(255 - i)
                                screen.blit(cv, (0, 0))
                                pg.display.update()
                        return cmds, f".save{n + 1}.pkl"
                elif event.key in [pg.K_w]:
                    if n != -1:
                        cmds.append('client')
                        cv = pg.Surface(screen.get_size(), pg.SRCALPHA)
                        cv.blit(screen, (0, 0))
                        if constants.USE_ALPHA:
                            for i in range(255):
                                pg.event.get()
                                screen.fill((0, 0, 0))
                                cv.set_alpha(255 - i)
                                screen.blit(cv, (0, 0))
                                pg.display.update()
                        return cmds, f".save{n + 1}.pkl"
                elif event.key in [pg.K_BACKSPACE, pg.K_x]:
                    if os.path.exists(path.get_save_path(f".save{n + 1}.pkl")):
                        os.remove(path.get_save_path(f".save{n + 1}.pkl"))
                        selects[n] = f"Save {n + 1}(empty)"
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = pg.mouse.get_pos()
                    if pg.Rect(screen.get_width() // 2 - 100, screen.get_height() // 2 - 100,
                                 200, 200).collidepoint(pos):
                        if n != -1:
                            cv = pg.Surface(screen.get_size(), pg.SRCALPHA)
                            cv.blit(screen, (0, 0))
                            if constants.USE_ALPHA:
                                for i in range(255):
                                    pg.event.get()
                                    screen.fill((0, 0, 0))
                                    cv.set_alpha(255 - i)
                                    screen.blit(cv, (0, 0))
                                    pg.display.update()
                            return cmds, f".save{n + 1}.pkl"
                elif event.button == 4:
                    if n != -1:
                        n = (n - 1 + len(selects)) % len(selects)
                        anchor = n
                    else:
                        n = 0
                        anchor = 0
                elif event.button == 5:
                    if n != -1:
                        n = (n + 1) % len(selects)
                        anchor = n
                    else:
                        n = 0
                        anchor = 0
        screen.fill((0, 0, 0))
        cs = bios[cb]
        ncx = bios[(cb + 1) % 7]
        if tick > 300:
            if constants.USE_ALPHA:
                ncx = copy.copy(ncx)
                ncx.set_alpha((tick - 300) * 255 // 200)
        for x in range(-100, screen.get_width() + 100, 100):
            for y in range(-100, screen.get_height() + 100, 100):
                screen.blit(cs, (x + tick % 100, y))
                if tick > 300:
                    screen.blit(ncx, (x + tick % 100, y))
        if tick >= 480:
            tick = 0
            cb = (cb + 1) % 7
        tick += 1
        ot = pg.transform.rotate(font_large.render(f"Underia", True, (0, 0, 0)),
                                  math.cos(tick / 120 * math.pi) * 150)
        otr = ot.get_rect(center=(screen.get_width() // 2 + 5, 100 + 5))
        screen.blit(ot, otr)
        ot = pg.transform.rotate(font_large.render(f"Underia", True, (255, 255, 255)),
                                  math.cos(tick / 120 * math.pi) * 150)
        otr = ot.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(ot, otr)
        if n != -1:
            sel = pg.Rect(screen.get_width() // 2 - 100, screen.get_height() // 2 - 100,
                          200, 200).collidepoint(pg.mouse.get_pos())
            dt = datas[n]
            sn = selects[n]
            sf = pg.transform.scale(pf.get_surface(0, 0, 0), (200, 200))
            screen.blit(sf, (screen.get_width() // 2 - 90, 300 + (tick % 100 > 50) * 20 + 10))
            sf = pf.get_surface(*dt.col if len(sn.split('(')) <= 1 else (255, 255, 255))
            sf = pg.transform.scale(sf, (200, 200))
            screen.blit(sf, (screen.get_width() // 2 - 100, 300 + (tick % 100 > 50) * 20))
            st = font.render(sn.split('(')[0] + f' LV.{dt.lv}', True, (0, 0, 0))
            sstr = st.get_rect(center=(screen.get_width() // 2 + 3, 700 + 3))
            screen.blit(st, sstr)
            st = font.render(sn.split('(')[0] + f' LV.{dt.lv}', True, (255, 255, 127) if sel else (255, 255, 255))
            sstr = st.get_rect(center=(screen.get_width() // 2, 700))
            screen.blit(st, sstr)
        w, h = screen.get_size()

        if t < 40 and constants.USE_ALPHA:
            mask.set_alpha(255 - t * 255 // 40)
            screen.blit(mask, (0, 0))
            t += 1
        pg.display.flip()
        clk.tick(60)
