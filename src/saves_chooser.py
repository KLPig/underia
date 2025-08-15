import copy
import math
import os
import random

import pygame as pg
import constants
from underia import settings
from resources import path
import underia
import pickle
from underia import good_name_walker

n = -1

selects = []

for i in range(1, 21):
    if os.path.exists(path.get_save_path(f".save{i}.pkl")):
        selects.append(f"Save {i}")
    else:
        selects.append(f"Save {i}(empty)")

anchor = 0
cmds = []
cb = 0
bios = [pg.image.load(path.get_path(f'assets/graphics/background/{b}.png')) for b in ['forest', 'rainforest', 'snowland', 'heaven',
                                                                                      'hell', 'desert', 'inner', 'life_forest',
                                                                                      'hallow', 'wither', 'ancient', 'ancient_city']]
bios = [pg.transform.scale(b, (100, 100)) for b in bios]
datas = []

for i in range(1, 21):
    try:
        with open(path.get_save_path(f".save{i}.data.pkl"), "rb") as f:
            datas.append(pickle.load(f))
    except FileNotFoundError:
        datas.append(underia.GameData(underia.PlayerProfile(), 0))
    except ModuleNotFoundError:
        datas.append(underia.GameData(underia.PlayerProfile(), 0))

pf = underia.PlayerProfile()
t = 0

def choose_save():
    global n, selects, anchor, cmds, cb, t

    ucx = 100
    udr = 150

    ps_x = 200

    hrx = 0

    ssn = 0

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
                    if n == -1:
                        pg.quit()
                        return cmds, None
                    else:
                        n = -1
                elif event.key == pg.K_s:
                    settings.set_settings()
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
                elif event.key == pg.K_r:
                    if n != -1:
                        datas[n].name = good_name_walker.get_name(seed=random.randint(0, 10000))
                        with open(path.get_save_path(f".save{n + 1}.data.pkl"), "wb") as ff:
                            ff.write(pickle.dumps(datas[n]))
                        hrx = -1500
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
                    else:
                        if n == -1:
                            n = 0
                            anchor = 0
                        else:
                            n = (n + 1) % len(selects)
                            anchor = n
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
        if cb < 6:
            ncb = (cb + 1) % 6
        elif cb in [8, 9]:
            ncb = {8: 9, 9: 8}[cb]
        else:
            ncb = cb
        ncx = bios[ncb]
        if tick > 300:
            if constants.USE_ALPHA:
                ncx = copy.copy(ncx)
                ncx.set_alpha((tick - 300) * 255 // 200)
        for x in range(-100, screen.get_width() + 100, 100):
            for y in range(-100, screen.get_height() + 100, 100):
                screen.blit(cs, (x + tick % 100, y))
                if tick > 300:
                    screen.blit(ncx, (x + tick % 100, y))
        if tick >= 500:
            tick = 0
            if cb < 6:
                cb = (cb + 1) % 6
            elif cb in [8, 9]:
                cb = {8: 9, 9: 8}[cb]
        tick += 1
        ot = pg.transform.rotate(font_large.render(f"Underia", True, (0, 0, 0)),
                                  math.cos(tick / 125 * math.pi) * udr)
        otr = ot.get_rect(center=(screen.get_width() // 2 + 5, ucx + 5))
        screen.blit(ot, otr)
        ot = pg.transform.rotate(font_large.render(f"Underia", True, (255, 255, 255)),
                                  math.cos(tick / 125 * math.pi) * udr)
        otr = ot.get_rect(center=(screen.get_width() // 2, ucx))
        screen.blit(ot, otr)
        pst = font.render('Press anywhere to start', True, (0, 0, 0))
        pst.set_alpha(127)
        pstr = pst.get_rect(center=(screen.get_width() // 2 + 5, ps_x + 5))
        screen.blit(pst, pstr)
        pst = font.render('Press anywhere to start', True, (255, 255, 255))
        pst.set_alpha(255)
        pstr = pst.get_rect(center=(screen.get_width() // 2, ps_x))
        screen.blit(pst, pstr)
        if ssn != n:
            hrx = 5
            ssn = n
        if hrx > 1:
            hrx += 500
            if hrx > 4200:
                hrx = -4500
        else:
            hrx = hrx * 2 // 3
        if n != -1:
            ucx = ucx * 3 // 4 + 25
            udr = udr * 4 // 5 + 30
            ps_x = ps_x * 2 // 3 + screen.get_height() // 3 + 50
            sel = pg.Rect(screen.get_width() // 2 - 100, screen.get_height() // 2 - 100,
                          200, 200).collidepoint(pg.mouse.get_pos())
            dt = datas[n]

            if dt.lv in [3, 4]:
                cb = 6
            elif dt.lv == 5:
                cb = 7
            elif dt.lv in [7, 8, 9]:
                cb = max(8, min(cb, 9))
            elif dt.lv == 10:
                cb = 10
            elif dt.lv == 11:
                cb = 11
            else:
                cb = min(cb, 5)
            sn = selects[n]
            sf = pg.transform.scale(pf.get_surface(0, 0, 0), (200, 200))
            screen.blit(sf, (screen.get_width() // 2 - 90, 300 + math.sin(tick / 125 * math.pi) * 20 + 10 + hrx))
            sf = pf.get_surface(*dt.col if len(sn.split('(')) <= 1 else (255, 255, 255))
            sf = pg.transform.scale(sf, (200, 200))
            screen.blit(sf, (screen.get_width() // 2 - 100, 300 + math.sin(tick / 125 * math.pi) * 20 + 10 + hrx))
            time = ''
            try:
                time = f'{int(dt.time) // 3600:2d}:{int(dt.time) // 60 % 60:2d}'
            except AttributeError:
                pass
            st = font.render(str(n + 1) + '. ' + (dt.name if 'name' in dir(dt) else 'Underia World'), True, (0, 0, 0))
            sstr = st.get_rect(center=(screen.get_width() // 2 + 3, 700 + 3 + hrx))
            screen.blit(st, sstr)
            st = font.render(str(n + 1) + '. ' + (dt.name if 'name' in dir(dt) else 'Underia World'), True, (255, 255, 127) if sel else (255, 255, 255))
            sstr = st.get_rect(center=(screen.get_width() // 2, 700 + hrx))
            screen.blit(st, sstr)
            st = font.render(f'LV {dt.lv} {time}', True, (0, 0, 0))
            st.set_alpha(150)
            sstr = st.get_rect(midleft=(screen.get_width() // 2  - 300 + 3, 750 + 3 + hrx))
            screen.blit(st, sstr)
            st = font.render(f'LV {dt.lv} {time}', True, (255, 255, 255))
            st.set_alpha(150)
            sstr = st.get_rect(midleft=(screen.get_width() // 2 - 300, 750 + hrx))
            screen.blit(st, sstr)
        else:
            ucx = ucx * 3 // 4 + screen.get_height() // 8
            udr = udr * 4 // 5 + 5
            ps_x = ps_x * 2 // 3 + screen.get_height() // 6 + 50
        w, h = screen.get_size()

        if t < 40 and constants.USE_ALPHA:
            mask.set_alpha(255 - t * 255 // 40)
            screen.blit(mask, (0, 0))
            t += 1
        pg.display.flip()
        clk.tick(60)
