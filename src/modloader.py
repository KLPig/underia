import copy
import os
import pygame as pg
import constants

from resources import path
from mods import UnderiaModData
import pickle

if constants.OS == "Windows":
    pass
else:
    import appscript

anchor = 0
cmds = []
cb = 0
bios = [pg.image.load(path.get_path(f'assets/graphics/background/{b}.png')) for b in ['forest', 'rainforest', 'snowland', 'heaven',
                                                                                      'inner', 'hell', 'desert']]
bios = [pg.transform.scale(b, (100, 100)) for b in bios]
datas = []
load_mods = []

mod_dir = path.get_save_path('mods')

if not os.path.exists(mod_dir):
    os.mkdir(mod_dir)

for d in os.listdir(mod_dir):
    if os.path.isdir(os.path.join(mod_dir, d)):
        pass
    else:
        os.system(f'rm {os.path.join(mod_dir, d)}')
mod_datas: list[UnderiaModData] = [pickle.load(open(os.path.join(mod_dir, d, 'data.umod'), 'rb')) for d in os.listdir(mod_dir)]
icos: list[pg.Surface] = [pg.image.load(os.path.join(mod_dir, d, 'assets/assets/icon.png')) for d in os.listdir(mod_dir)]
ds = os.listdir(mod_dir)
scr = 0

if not os.path.exists(mod_dir):
    os.mkdir(mod_dir)

def load_mod():
    global anchor, cmds, cb, mod_datas, icos, scr, ds
    clk = pg.time.Clock()
    screen = pg.display.get_surface()
    font = pg.font.Font(path.get_path('assets/dtm-mono.otf'), 32)
    btn_t = ['Open Mod Folder', 'Reload Mods', 'Done']
    btn_r = [pg.Rect(300, 50, 320, 80), pg.Rect(640, 50, 320, 80), pg.Rect(980, 50, 320, 80)]

    tick = 0
    last_tick = 0
    tt = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return cmds, None
            elif event.type == pg.MOUSEBUTTONDOWN:
                last_tick = tt
                if event.button == 1:
                    pos = pg.mouse.get_pos()
                    if btn_r[0].collidepoint(pos):
                        if constants.OS == "Windows":
                            os.system(f'explorer {mod_dir}')
                        else:
                            appscript.app('Finder').reveal(appscript.mactypes.Alias(mod_dir).alias)
                            appscript.app('Finder').activate()
                    elif btn_r[1].collidepoint(pos):
                        mod_datas = [pickle.load(open(os.path.join(mod_dir, d, 'data.umod'), 'rb')) for d in os.listdir(mod_dir)]
                        icos = [pg.image.load(os.path.join(mod_dir, d, 'assets/assets/icon.png')) for d in os.listdir(mod_dir)]
                        ds = os.listdir(mod_dir)
                    elif btn_r[2].collidepoint(pos):
                        cv = pg.Surface(screen.get_size(), pg.SRCALPHA)
                        cv.blit(screen, (0, 0))
                        if constants.USE_ALPHA:
                            for i in range(255):
                                pg.event.get()
                                screen.fill((0, 0, 0))
                                cv.set_alpha(255 - i)
                                screen.blit(cv, (0, 0))
                                pg.display.update()
                        return cmds, load_mods
            elif event.type == pg.KEYDOWN:
                last_tick = tt
                if event.key == pg.K_UP:
                    scr = max(0, min(scr + 240, 240 * len(mod_datas) - 760))
                elif event.key == pg.K_DOWN:
                    scr = max(0, min(scr - 240, 240 * len(mod_datas) - 760))
                elif event.key == pg.K_F4:
                    constants.FULLSCREEN = not constants.FULLSCREEN
                    pg.display.set_mode(pg.display.get_window_size(), (pg.FULLSCREEN if constants.FULLSCREEN else 0) | constants.FLAGS)
                elif event.key == pg.K_ESCAPE:
                    pg.quit()
                    return cmds, None
                elif event.key in [pg.K_f, pg.K_c]:
                    if constants.OS == "Windows":
                        os.system(f'explorer {mod_dir}')
                    else:
                        appscript.app('Finder').reveal(appscript.mactypes.Alias(mod_dir).alias)
                        appscript.app('Finder').activate()
                elif event.key in [pg.K_r, pg.K_x]:
                    mod_datas = [pickle.load(open(os.path.join(mod_dir, d, 'data.umod'), 'rb')) for d in os.listdir(mod_dir)]
                    icos = [pg.image.load(os.path.join(mod_dir, d, 'assets/assets/icon.png')) for d in os.listdir(mod_dir)]
                    ds = os.listdir(mod_dir)
                elif event.key in [pg.K_RETURN, pg.K_z]:
                    cv = pg.Surface(screen.get_size(), pg.SRCALPHA)
                    cv.blit(screen, (0, 0))
                    if constants.USE_ALPHA:
                        for i in range(255):
                            pg.event.get()
                            screen.fill((0, 0, 0))
                            cv.set_alpha(255 - i)
                            screen.blit(cv, (0, 0))
                            pg.display.update()
                    return cmds, load_mods
            elif event.type == pg.MOUSEWHEEL:
                scr += event.y * 5
                scr = max(0, min(scr, 240 * len(mod_datas) - screen.get_height() + 300))
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
        for i in range(len(mod_datas)):
            r = (300, 180 + 240 * i - scr, 1000, 200)
            pg.draw.rect(screen, (0, 0, 0), (300, 180 + 240 * i - scr,
                                             screen.get_width() - 600, 200), border_radius=20)
            pg.draw.rect(screen, (255, 255, 255) if not pg.Rect(r).collidepoint(pg.mouse.get_pos()) else (255, 255, 0),
                         (300, 180 + 240 * i - scr, screen.get_width() - 600, 200), 5, border_radius=20)
            ico = icos[i]
            ico = pg.transform.scale(ico, (150, 150))
            screen.blit(ico, (325, 180 + 240 * i - scr + 25))
            data = mod_datas[i]
            name = font.render(data.name + ('(Loaded)' if ds[i] in load_mods else ''), True, (255, 255, 255), (0, 0, 0))
            screen.blit(name, (525, 180 + 240 * i - scr + 25))
            info = font.render(f'by {data.author} v{data.version[0]}.{data.version[1]}.{data.version[2]}',
                               True, (100, 100, 100), (0, 0, 0))
            screen.blit(info, (525, 180 + 240 * i - scr + 25 + 50))
            desc = font.render(data.desc, True, (100, 100, 100), (0, 0, 0))
            screen.blit(desc, (525, 180 + 240 * i - scr + 25 + 100))
            if pg.Rect(r).collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0]:
                if ds[i] in load_mods:
                    load_mods.remove(ds[i])
                else:
                    load_mods.append(ds[i])
                while pg.mouse.get_pressed()[0]:
                    pg.event.get()
                    pass
        w, h = screen.get_size()
        for i in range(len(btn_t)):
            btn_r[i].centerx = (i + 1) * w // 4
            btn_r[i].centery = h - 100
        for i in range(len(btn_t)):
            if pg.Rect(btn_r[i]).collidepoint(pg.mouse.get_pos()):
                btn = font.render(btn_t[i], True, (255, 255, 0))
            else:
                btn = font.render(btn_t[i], True, (255, 255, 255))
            pg.draw.rect(screen, (0, 0, 0), btn_r[i], border_radius=10)
            pg.draw.rect(screen, (255, 255, 255), btn_r[i], 5, border_radius=10)
            br = btn.get_rect(center=btn_r[i].center)
            screen.blit(btn, br)
        if tick >= 500:
            tick = 0
            cb = (cb + 1) % 7
        tick += 1
        tt += 1
        if tt - last_tick > 180:
            cv = pg.Surface(screen.get_size(), pg.SRCALPHA)
            cv.blit(screen, (0, 0))
            if constants.USE_ALPHA:
                for i in range(255):
                    pg.event.get()
                    screen.fill((0, 0, 0))
                    cv.set_alpha(255 - i)
                    screen.blit(cv, (0, 0))
                    pg.display.update()
            return cmds, load_mods
        pg.display.flip()
        clk.tick(60)
