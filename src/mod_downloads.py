import requests
import xml.etree.ElementTree as etree
import constants
import copy
import pygame as pg
from resources import path
import os
from mods import UnderiaModData
if constants.OS == 'OSX':
    import appscript

def compare(x: tuple[str, str, str], y: tuple[str, str, str]):
    if x[0] != y[0]:
        return 1 if y[0] > x[0] else -1
    elif x[1] != y[1]:
        return 1 if y[1] > x[1] else -1
    elif x[2] != y[2]:
        return 1 if y[2] > x[2] else -1
    else:
        return 0

url = 'https://raw.githubusercontent.com/KLPig/underia/master/docs/data.xml'

response = requests.get(url)

class Mod:
    def __init__(self, et_data):
        self.data = et_data
        self.name = et_data.find('name').text
        self.author = et_data.find('author').text
        self.desc = et_data.find('desc').text
        self.mid = et_data.find('mid').attrib['value']
        self.version = (et_data.find('version/first').text, et_data.find('version/second').text, et_data.find('version/third').text)
        self.support_min = et_data.find('support/version[@id="supported"]')
        self.support_max = et_data.find('support/version[@id="newest"]')
        self.support = [dd for dd in ["OSX", "Windows"] if et_data.find(f"support/platform[@id=\"{dd}\"]") is not None]

    def __str__(self):
        return f'(#{self.mid}){self.name} - by {self.author}\n> {self.desc}\n V.{"%s.%s.%s" % self.version}\nSupport: {"; ".join(self.support)}'

tree = etree.fromstring(response.content)
mods = tree.find('mods')
mdatas = []

if response.status_code == 200:
    for mod in mods:
        mdatas.append(Mod(mod))
    for d in mdatas:
        print(d)
else:
    print('Request failed with status code: {}'.format(response.status_code))


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

mod_datas: list[UnderiaModData] = [UnderiaModData(d.name, '%s.%s.%s' % d.version, d.author, d.desc) for d in mdatas]

ds = os.listdir(mod_dir)
scr = 0

if not os.path.exists(mod_dir):
    os.mkdir(mod_dir)

def load_mod():
    global anchor, cmds, cb, mod_datas, icos, scr, ds
    clk = pg.time.Clock()
    screen = pg.display.get_surface()
    font = pg.font.Font(path.get_path('assets/dtm-mono.otf' if constants.LANG != 'zh' else 'assets/fz-pixel.ttf'), 32)
    btn_t = ['Open Mod Folder']
    btn_r = [pg.Rect(300, 50, 1000, 80)]

    tick = 0
    last_tick = 0
    tt = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
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
                    return cmds, None
                elif event.key in [pg.K_f, pg.K_c]:
                    if constants.OS == "Windows":
                        os.system(f'explorer {mod_dir}')
                    else:
                        appscript.app('Finder').reveal(appscript.mactypes.Alias(mod_dir).alias)
                        appscript.app('Finder').activate()
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
            pg.draw.rect(screen, (255, 255, 255) if not pg.Rect(r).collidepoint(pg.mouse.get_pos()) and not os.path.exists(path.get_save_path(f'mods/{mdatas[i].name}/')) else (255, 255, 0),
                         (300, 180 + 240 * i - scr, screen.get_width() - 600, 200), 5, border_radius=20)
            data = mod_datas[i]
            name = font.render(data.name, True, (255, 255, 255), (0, 0, 0))
            screen.blit(name, (345, 180 + 240 * i - scr + 25))
            info = font.render(f'by {data.author} v{data.version[0]}.{data.version[1]}.{data.version[2]}',
                               True, (100, 100, 100), (0, 0, 0))
            screen.blit(info, (345, 180 + 240 * i - scr + 25 + 50))
            desc = font.render(data.desc, True, (100, 100, 100), (0, 0, 0))
            screen.blit(desc, (345, 180 + 240 * i - scr + 25 + 100))
            if pg.Rect(r).collidepoint(pg.mouse.get_pos()) and pg.mouse.get_pressed()[0]:
                data = mod_datas[i]
                if not os.path.exists(path.get_save_path('mods')):
                    os.mkdir(path.get_save_path('mods'))
                r = requests.get(f'https://raw.githubusercontent.com/KLPig/underia/master/mods/{mdatas[i].mid}/dist/dist.zip', stream=True)
                if r.ok:
                    with open(path.get_save_path(f'mods/{mdatas[i].mid}.zip'), 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            f.write(chunk)
                            f.flush()
                            os.fsync(f.fileno())

                        if constants.OS == "OSX":
                            os.system(f'unzip -o {path.get_save_path(f"mods/{mdatas[i].mid}.zip")} -d "{path.get_save_path(f"mods/{mdatas[i].name}")}"')
                else:
                    print('Error 91919')

        w, h = screen.get_size()
        for i in range(len(btn_t)):
            btn_r[i].centerx = w // 2
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
        if tt - last_tick > constants.INFINITY:
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

if __name__ == '__main__':
    print(load_mod())
