import copy
import os
import appscript
import pygame as pg
from src.resources import path
from src.mods import UnderiaModData
import pickle

anchor = 0
cmds = []
cb = 0
bios = [pg.image.load(path.get_path(f'assets/graphics/background/{b}.png')) for b in ['forest', 'rainforest', 'snowland', 'heaven',
                                                                                      'inner', 'hell', 'desert']]
bios = [pg.transform.scale(b, (100, 100)) for b in bios]
datas = []
load_mods = []

mod_dir = path.get_save_path('mods')

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
    pg.init()
    clk = pg.time.Clock()
    pg.display.set_caption("Underia")
    screen = pg.display.set_mode((1600, 900), pg.RESIZABLE | pg.HWSURFACE | pg.DOUBLEBUF | pg.FULLSCREEN | pg.SCALED)
    font = pg.font.SysFont('dtm-mono', 24)
    mod_text = font.render("Open Mod Folder", True, (255, 255, 255), (0, 0, 0))
    mod_text_focus = font.render("Open Mod Folder", True, (255, 255, 0), (0, 0, 0))
    reload_text = font.render("Reload Mods", True, (255, 255, 255), (0, 0, 0))
    reload_text_focus = font.render("Reload Mods", True, (255, 255, 0), (0, 0, 0))
    done_text = font.render("Done", True, (255, 255, 255), (0, 0, 0))
    done_text_focus = font.render("Done", True, (255, 255, 0), (0, 0, 0))

    tick = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return cmds, None
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = pg.mouse.get_pos()
                    if mod_text.get_rect(topleft=(10, 10)).collidepoint(pos):
                        appscript.app('Finder').reveal(appscript.mactypes.Alias(mod_dir).alias)
                        appscript.app('Finder').activate()
                    elif reload_text.get_rect(topleft=(10, 40)).collidepoint(pos):
                        mod_datas = [pickle.load(open(os.path.join(mod_dir, d, 'data.umod'), 'rb')) for d in os.listdir(mod_dir)]
                        icos = [pg.image.load(os.path.join(mod_dir, d, 'assets/assets/icon.png')) for d in os.listdir(mod_dir)]
                        ds = os.listdir(mod_dir)
                    elif done_text.get_rect(topleft=(10, 70)).collidepoint(pos):
                        pg.quit()
                        return cmds, load_mods
            elif event.type == pg.MOUSEWHEEL:
                scr += event.y * 5
                scr = max(0, min(scr, 240 * len(mod_datas) - 840))
        screen.fill((0, 0, 0))
        cs = bios[cb]
        ncx = bios[(cb + 1) % 7]
        if tick > 300:
            ncx = copy.copy(ncx)
            ncx.set_alpha((tick - 300) * 255 // 200)
        for x in range(-100, screen.get_width() + 100, 100):
            for y in range(-100, screen.get_height() + 100, 100):
                screen.blit(cs, (x + tick % 100, y))
                if tick > 300:
                    screen.blit(ncx, (x + tick % 100, y))
        if not mod_text.get_rect(topleft=(10, 10)).collidepoint(pg.mouse.get_pos()):
            screen.blit(mod_text, (10, 10))
        else:
            screen.blit(mod_text_focus, (10, 10))
        if not reload_text.get_rect(topleft=(10, 40)).collidepoint(pg.mouse.get_pos()):
            screen.blit(reload_text, (10, 40))
        else:
            screen.blit(reload_text_focus, (10, 40))
        if not done_text.get_rect(topleft=(10, 70)).collidepoint(pg.mouse.get_pos()):
            screen.blit(done_text, (10, 70))
        else:
            screen.blit(done_text_focus, (10, 70))
        for i in range(len(mod_datas)):
            r = (300, 100 + 240 * i - scr, 1000, 200)
            pg.draw.rect(screen, (0, 0, 0), (300, 100 + 240 * i - scr, 1000, 200))
            pg.draw.rect(screen, (255, 255, 255) if not pg.Rect(r).collidepoint(pg.mouse.get_pos()) else (255, 255, 0),
                         (300, 100 + 240 * i - scr, 1000, 200), 5)
            ico = icos[i]
            ico = pg.transform.scale(ico, (150, 150))
            screen.blit(ico, (325, 100 + 240 * i - scr + 25))
            data = mod_datas[i]
            name = font.render(data.name + ('(Loaded)' if ds[i] in load_mods else ''), True, (255, 255, 255), (0, 0, 0))
            screen.blit(name, (525, 100 + 240 * i - scr + 25))
            info = font.render(f'by {data.author} v{data.version[0]}.{data.version[1]}.{data.version[2]}',
                               True, (100, 100, 100), (0, 0, 0))
            screen.blit(info, (525, 100 + 240 * i - scr + 25 + 50))
            desc = font.render(data.desc, True, (100, 100, 100), (0, 0, 0))
            screen.blit(desc, (525, 100 + 240 * i - scr + 25 + 100))
            if pg.Rect(r).collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0]:
                if ds[i] in load_mods:
                    load_mods.remove(ds[i])
                else:
                    load_mods.append(ds[i])
                while pg.mouse.get_pressed()[0]:
                    pg.event.get()
                    pass
        if tick >= 500:
            tick = 0
            cb = (cb + 1) % 7
        tick += 1
        pg.display.flip()
        clk.tick(60)
