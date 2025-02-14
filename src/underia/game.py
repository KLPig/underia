import copy
import os
import random
import time
import pygame as pg

from src import resources, visual, constants, physics
from src.underia import player, entity, projectiles, weapons, inventory, dialog
import perlin_noise

MUSICS = {
    'lantern': ['snowland1', 'snowland0', 'heaven1', 'heaven0', 'forest0', 'rainforest0', 'desert0'],
    'wild_east': ['desert1', 'desert0'],
    'waterfall': ['forest0', 'rainforest0', 'desert0', 'snowland0', 'heaven0', 'heaven1', 'inner0'],
    'fields': ['forest1', 'rainforest1', 'snowland1', 'forest0'],
    'empty': ['hell0', 'hell1', 'forest1', 'rainforest1', 'battle', 'hallow0', 'hallow1'],
    'snow': ['snowland0', 'snowland1', 'hallow0', 'hallow1'],
    #'here_we_are': ['inner0', 'inner1'],
    'amalgam': ['inner0', 'inner1', 'none0', 'none1'],
    'null': [],
    'rude_buster': ['battle'],
    'worlds_revolving': ['battle'],
    'boss_otherworld': ['battle'],
    'plantera': ['battle'],
    'wof_otherworld': ['battle'],
    'mercy_remix': ['battle'],
    'nothing_matter': ['battle'],
}

class Game:
    ITEM_SPLIT_MIN = 1
    ITEM_SPLIT_MAX = 2
    TIME_SPEED = .00004
    CHUNK_SIZE = 100

    def __init__(self):
        self.displayer = visual.Displayer()
        self.graphics = resources.Graphics()
        self.events = []
        self.p_obj = []
        self.player = player.Player()
        self.pressed_keys = []
        self.pressed_mouse = []
        self.entities: list[entity.Entities.Entity] = []
        self.projectiles: list[projectiles.Projectiles.Projectile] = []
        self.clock = resources.Clock()
        self.damage_texts: list[tuple[str, int, tuple[int, int]]] = []
        self.save = ''
        self.day_time = 0.3
        self.drop_items = []
        self.map: pg.PixelArray | None = None
        self.chunk_pos = (0, 0)
        self.last_biome = ('forest', 0)
        self.stage = 0
        self.musics = {}
        self.channel = pg.mixer.Channel(0)
        self.prepared_music = None
        self.cur_music = 'null'
        self.MUSICS = MUSICS
        self.map_ns = {}
        self.m_min = 0
        self.m_max = 0
        self.sounds: dict[str, pg.mixer.Sound] = {}
        self.world_events = []
        self.dummy = None
        self.gcnt = 0
        self.map_open = False
        self.dialog: dialog.Dialogger | None = None
        self.decors: list[tuple[str, int, int, float]] = []
        self.chapter = 0
        self.seed = random.randint(0, 1000000)
        self.noise = perlin_noise.PerlinNoise(1.2, self.seed)
        self.weather_noise = perlin_noise.PerlinNoise(1.2, self.seed + 1)
        self.wm_min = 0
        self.wm_max = 0
        self.w_ns = {}
        self.hallow_points: list[tuple[tuple[int, int], int]] = []

    def get_night_color(self, time_days: float):
        if len([1 for e in self.entities if type(e) is entity.Entities.AbyssEye]):
            return 255, 0, 0
        if 0.2 < time_days <= 0.3:
            r = int(255 * (time_days - 0.2) / 0.1)
            g = int(255 * (time_days - 0.2) / 0.1)
            b = int(255 * (time_days - 0.2) / 0.1)
        elif 0.3 < time_days <= 0.7:
            r = 255
            g = 255
            b = 255
        elif 0.7 < time_days <= 0.75:
            r = 255
            g = 255 - int(128 * (time_days - 0.7) / 0.05)
            b = 255 - int(255 * (time_days - 0.7) / 0.05)
        elif 0.75 < time_days <= 0.8:
            r = 255 - int(255 * (time_days - 0.75) / 0.05)
            g = 127 - int(127 * (time_days - 0.75) / 0.05)
            b = 0
        else:
            r = 0
            g = 0
            b = 0
        return r, g, b

    def on_day_start(self):
        if 'blood moon' in self.world_events:
            self.world_events.remove('blood moon')
        if random.random() < 0.05:
            self.world_events.append('solar eclipse')

    def on_day_end(self):
        if 'solar eclipse' in self.world_events:
            self.world_events.remove('solar eclipse')
        if random.random() < 0.05:
            self.world_events.append('blood moon')

    def cnt_graphics(self, directory, index=''):
        cnt = 0
        for file in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, file)):
                if file.endswith(".png"):
                    cnt += 1
            else:
                cnt += self.cnt_graphics(os.path.join(directory, file), index + file + '_')
        return cnt

    def load_graphics(self, directory, index='', cnt=1):
        for file in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, file)):
                if file.endswith(".png"):
                    self.gcnt += 1
                    self.graphics.load_graphics(index + file.removesuffix(".png"), os.path.join(directory, file))
                    if self.gcnt % int(self.gcnt // 80 + 1) == 0:
                        self._display_progress(self.gcnt / cnt, st=2)
            else:
                self.load_graphics(os.path.join(directory, file), index + file + '_', cnt=cnt)

    def _display_progress(self, prog, st=1):
        window = pg.display.get_surface()
        window.fill((0, 0, 0))
        wc = window.get_width() // 2
        hc = window.get_height() // 2
        pg.draw.rect(window, (0, 255, 0) if st == 1 else (255, 0, 0 ) if st == 2 else(255, 255, 0), (wc - 400, hc - 100, 800, 200), border_radius=20)
        pg.draw.rect(window, (255, 255, 0) if st == 1 else (0, 255, 0) if st == 2 else (255, 255, 255), (wc - 400, hc - 100, int(800 * prog), 200), border_radius=20)
        pg.display.flip()
        pg.event.get()
        time.sleep(0.001)

    def setup(self):
        self.p_obj = []
        self.sounds = {}
        self.map_open = False
        self.map_ns = {}
        self.w_ns = {}
        self.m_min = 0
        self.m_max = 0
        self.wm_min = 0
        self.wm_max = 0
        self.gcnt = 0
        self.decors = []
        self.dialog = dialog.Dialogger(144, pg.Rect(0, 1980, 4800, 720), with_border=True, speed=.5,
                                       target_surface=pg.display.get_surface())
        self.noise = perlin_noise.PerlinNoise(1.2, self.seed)
        self.weather_noise = perlin_noise.PerlinNoise(1.2, self.seed + 1)
        window = pg.display.get_surface()
        pg.draw.rect(window, (0, 0, 0), (window.get_width() // 2 - 500, window.get_height() // 2 - 150, 1000, 300))
        self.musics = {}
        self.cur_music = 'null'
        self.prepared_music = None
        self.MUSICS = MUSICS
        self.channel = pg.mixer.Channel(0)
        self.load_graphics(resources.get_path('assets/graphics'),
                           cnt=self.cnt_graphics(resources.get_path('assets/graphics')))
        weapons.set_weapons()
        self.map = pg.PixelArray(self.graphics['background_map'])
        cnt = 0
        for m in os.listdir(resources.get_path('assets/musics')):
            if m[-4:] in ['.wav', '.ogg', '.m4a', '.mp3']:
                cnt += 1
        for s in os.listdir(resources.get_path('assets/sounds')):
            if s[-4:] in ['.wav', '.ogg', '.m4a', '.mp3']:
                cnt += 1
        self.gcnt = 0
        for m in os.listdir(resources.get_path('assets/musics')):
            if m[-4:] in ['.wav', '.ogg', '.m4a', '.mp3']:
                self.gcnt += 1
                self._display_progress(self.gcnt / cnt)
                self.musics[m.split('.')[0]] = pg.mixer.Sound(resources.get_path('assets/musics/' + m))
        for s in os.listdir(resources.get_path('assets/sounds')):
            if s[-4:] in ['.wav', '.ogg', '.m4a', '.mp3']:
                self.gcnt += 1
                self._display_progress(self.gcnt / cnt)
                self.sounds[s.split('.')[0]] = pg.mixer.Sound(resources.get_path('assets/sounds/' + s))
        for x in range(-200, 200):
            for y in range(-200, 200):
                self.get_biome((x, y))
            if x % 40 == 0:
                self._display_progress((x + 200) / 400, 0)

    def play_sound(self, sound: str, vol=1.0):
        self.sounds[sound].set_volume(vol)
        if self.sounds[sound].get_num_channels():
            return
        self.sounds[sound].play()

    def on_update(self):
        pass

    def update_function(self, func):
        setattr(self, 'on_update', func)

    def get_biome(self, pos=None):
        if len([1 for e in self.entities if type(e) in [entity.Entities.OmegaFlowery]]):
            return 'none'
        if len([1 for e in self.entities if type(e) is entity.Entities.AbyssEye]):
            return 'heaven'
        if len([1 for e in self.entities if type(e) in [entity.Entities.Jevil]]) or \
                self.player.inventory.is_enough(inventory.ITEMS['chaos_heart']):
            return 'inner'
        if pos is None:
            pos = self.chunk_pos
        if pos[0] ** 2 + pos[1] ** 2 < 1000:
            return 'forest'
        lvs = ['hell', 'desert', 'rainforest', 'forest', 'snowland', 'heaven', 'hallow']
        b = 0
        if pos not in self.map_ns.keys():
            val = self.noise([pos[0] / 400.0, pos[1] / 400.0])
            if val < self.m_min or val > self.m_max:
                self.map_ns = {}
            self.m_min = min(self.m_min, val)
            self.m_max = max(self.m_max, val)
            val = (val - self.m_min) / (self.m_max - self.m_min + 0.01)
            self.map_ns[pos] = val
            b = 1
        idx = int(self.map_ns[pos] * len(lvs))
        if pos in self.w_ns.keys():
            w = self.w_ns[pos]
        else:
            w = self.weather_noise([pos[0] / 400.0, pos[1] / 400.0])
            self.wm_min = min(self.m_min, w)
            self.wm_max = max(self.m_max, w)
        w = (w - self.wm_min) / (self.wm_max - self.wm_min + 0.01)
        if 5 > idx > 0:
            if w < 0.2:
                if idx == 4:
                    idx = 3
                else:
                    idx = 1
            elif w < 0.4:
                idx = max(1, idx - 1)
            elif w < 0.6:
                pass
            elif w < 0.8:
                idx = min(4, idx + 1)
            else:
                if idx == 1:
                    idx = 2
                else:
                    idx = 5
            if w < 0.5 and idx == 2:
                idx = 3
        for pp, r in self.hallow_points:
            if physics.distance(pp[0] - (pos[0] - 120) * self.CHUNK_SIZE, pp[1] - (pos[1] - 120) * self.CHUNK_SIZE) < r:
                idx = 6
        biome = lvs[idx]
        if b:
            no_of_decor = [4, 7, 10, 8, 4, 3, 0][idx]
            if no_of_decor:
                for i in range(no_of_decor):
                    if random.random() < 0.007 - [0.003, 0.004, -0.002, -0.001, 0.003, 0.003][idx]:
                        self.decors.append((f'background_decor_{biome}{i + 1}',
                                            (pos[0] - 120) * self.CHUNK_SIZE + random.randint(-self.CHUNK_SIZE // 2, self.CHUNK_SIZE // 2),
                                             (pos[1] - 120) * self.CHUNK_SIZE + random.randint(-self.CHUNK_SIZE // 2, self.CHUNK_SIZE // 2),
                                            random.choices(list(range(1, 1000)), weights=list(range(1, 1000)), k=1)[0] / 100.0))
        return biome

    def get_player_objects(self) -> list[physics.Mover]:
        return [self.player.obj] + self.p_obj

    def update(self):
        if (self.prepared_music is None and self.channel.get_busy() == 0) or \
                (self.cur_music is not None and (self.get_biome() + str(int(0.3 < self.day_time < 0.7))) not in
                 self.MUSICS[self.cur_music] and not len([1 for e in self.entities if e.IS_MENACE])) \
                or (self.cur_music is not None and len([1 for e in self.entities if e.IS_MENACE]) and
                    'battle' not in self.MUSICS[self.cur_music]):
            if len([1 for e in self.entities if e.IS_MENACE]):
                self.cur_music = None
                self.channel.stop()
                if len([1 for e in self.entities if type(e) is entity.Entities.Jevil]):
                    self.prepared_music = 'worlds_revolving'
                elif len([1 for e in self.entities if type(e) is entity.Entities.Plantera]):
                    self.prepared_music = 'plantera'
                elif len([1 for e in self.entities if type(e) is entity.Entities.ReincarnationTheWorldsTree]):
                    self.prepared_music = 'mercy_remix'
                elif len([1 for e in self.entities if type(e) is entity.Entities.Faith]):
                    self.prepared_music = 'nothing_matter'
                elif len([1 for e in self.entities if type(e) is entity.Entities.OmegaFlowery]):
                    self.prepared_music = 'empty'
                elif len([1 for e in self.entities if type(e) in [entity.Entities.GodsEye]]):
                    self.prepared_music = 'wof_otherworld'
                elif len([1 for e in self.entities if type(e) in [entity.Entities.CLOCK, entity.Entities.MATTER]]):
                    self.prepared_music = 'boss_otherworld'
                else:
                    self.prepared_music = 'rude_buster'
            else:
                self.cur_music = None
                self.channel.fadeout(8000)
                self.prepared_music = random.choice([k for k, v in self.MUSICS.items() \
                                                     if (self.get_biome() + str(int(0.3 < self.day_time < 0.7))) in v])
        if self.cur_music is None and self.prepared_music is not None and self.channel.get_busy() == 0:
            self.cur_music = self.prepared_music
            self.channel.play(self.musics[self.cur_music])
            self.prepared_music = None
        self.chunk_pos = (
        int(self.player.obj.pos[0]) // self.CHUNK_SIZE + 120, int(self.player.obj.pos[1]) // self.CHUNK_SIZE + 120)
        self.day_time += self.TIME_SPEED
        self.day_time %= 1.0
        if self.day_time - self.TIME_SPEED < 0.25 <= self.day_time:
            self.on_day_start()
        if self.day_time - self.TIME_SPEED < 0.8 <= self.day_time:
            self.on_day_end()
        self.on_update()
        self.events = pg.event.get()
        for event in self.events:
            if event.type == pg.QUIT:
                raise resources.Interrupt()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    paused = True
                    while paused:
                        for ev in pg.event.get():
                            if ev.type == pg.QUIT:
                                raise resources.Interrupt()
                            elif ev.type == pg.KEYDOWN:
                                if ev.key == pg.K_BACKSPACE:
                                    paused = False
                                elif ev.key == pg.K_ESCAPE:
                                    raise resources.Interrupt()
                            elif ev.key == pg.K_F4:
                                constants.FULLSCREEN = not constants.FULLSCREEN
                                pg.display.set_mode(pg.display.get_window_size(), (pg.FULLSCREEN if constants.FULLSCREEN else 0) | constants.FLAGS)
                        pg.display.flip()
                    self.pressed_mouse = []
                    self.pressed_keys = []
                elif event.key == pg.K_F4:
                    constants.FULLSCREEN = not constants.FULLSCREEN
                    pg.display.set_mode(pg.display.get_window_size(), (pg.FULLSCREEN if constants.FULLSCREEN else 0) | constants.FLAGS)
                else:
                    self.pressed_keys.append(event.key)
            elif event.type == pg.KEYUP:
                if event.key in self.pressed_keys:
                    self.pressed_keys.remove(event.key)
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.pressed_mouse.append(event.button)
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button in self.pressed_mouse:
                    self.pressed_mouse.remove(event.button)
        bg_size = int(120 / self.player.get_screen_scale())
        bg_ax = int(self.player.ax / self.player.get_screen_scale()) % bg_size
        bg_ay = int(self.player.ay / self.player.get_screen_scale()) % bg_size
        cols = {'hell': (255, 0, 0), 'desert': (255, 191, 63), 'forest': (0, 255, 0), 'rainforest': (127, 255, 0),
                'snowland': (255, 255, 255), 'heaven': (127, 127, 255), 'inner': (0, 0, 0), 'none': (0, 0, 0),
                'hallow': (0, 255, 255)}
        if not self.graphics.is_loaded('nbackground_hell') or self.graphics['nbackground_hell'].get_width() != bg_size:
            for k in cols.keys():
                self.graphics['nbackground_' + k] = pg.transform.scale(self.graphics['background_' + k], (bg_size, bg_size))
        if pg.K_TAB in self.pressed_keys:
            self.map_open = not self.map_open
        if self.get_biome() != self.last_biome[0]:
            self.last_biome = (self.last_biome[0], self.last_biome[1] + 1)
            if self.last_biome[1] >= 20:
                self.last_biome = (self.get_biome(), 0)
        if constants.EASY_BACKGROUND:
            g = pg.Surface((bg_size, bg_size))
            g.fill(cols[self.get_biome()])
        else:
            g = self.graphics.get_graphics('nbackground_' + self.get_biome())
        if constants.DISPLAY_STYLE:
            if constants.EASY_BACKGROUND:
                lg = pg.Surface((bg_size, bg_size))
                lg.fill(cols[self.last_biome[0]])
            else:
                lg = self.graphics.get_graphics('nbackground_' + self.last_biome[0])
        else:
            lg = pg.Surface((bg_size, bg_size))
        slg, _ = self.last_biome
        for i in range(-bg_size, self.displayer.SCREEN_WIDTH + bg_size, bg_size):
            for j in range(-bg_size, self.displayer.SCREEN_HEIGHT + bg_size, bg_size):
                if constants.DISPLAY_STYLE:
                    self.displayer.canvas.blit(g, (i - bg_ax, j - bg_ay))
                    if self.get_biome() != self.last_biome[0]:
                        self.displayer.canvas.blit(lg, (i - bg_ax, j - bg_ay))
                else:
                    cx, cy = resources.real_position((i - bg_ax + bg_size // 2, j - bg_ay + bg_size // 2))
                    cx = int(cx // self.CHUNK_SIZE) + 120
                    cy = int(cy // self.CHUNK_SIZE) + 120
                    if not self.last_biome[1]:
                        ap = 100
                        bi = self.get_biome()
                    elif self.last_biome[1] > 10:
                        ap = self.last_biome[1] * 2 - 100
                        bi = self.get_biome()
                    else:
                        ap = (10 - self.last_biome[1]) ** 2
                        bi = self.last_biome[0]
                    bo = self.get_biome(pos=(cx, cy))
                    if constants.EASY_BACKGROUND:
                        bg = pg.Surface((bg_size, bg_size))
                        bg.fill(cols[bo])
                    else:
                        bg = copy.copy(self.graphics.get_graphics('nbackground_' + bo))
                    self.displayer.canvas.blit(bg, (i - bg_ax, j - bg_ay))
                    if bi != bo and False:
                        if constants.EASY_BACKGROUND:
                            s = pg.Surface((bg_size, bg_size))
                            s.fill(cols[bi])
                        else:
                            s = copy.copy(self.graphics.get_graphics('nbackground_' + bi))
                        if g.get_alpha() != ap:
                            g.set_alpha(ap)
                        self.displayer.canvas.blit(s, (i - bg_ax, j - bg_ay))
        for img, x, y, scale_req in self.decors:
            if self.displayer.canvas.get_rect().collidepoint(*resources.displayed_position((x, y))) and scale_req >= self.player.get_screen_scale():
                self.displayer.canvas.blit(pg.transform.scale_by(self.graphics.get_graphics(img),
                                                                     1 / self.player.get_screen_scale()),
                                           resources.displayed_position((x, y)))
        for monster in self.entities:
            monster.update()
            if monster.hp_sys.hp <= 0:
                self.entities.remove(monster)
                if monster.obj.IS_OBJECT:
                    if monster.SOUND_DEATH is not None:
                        monster.play_sound('killed_' + monster.SOUND_DEATH)
                    else:
                        monster.play_sound('enemydust')
                loots = monster.LOOT_TABLE()
                for item, amount in loots:
                    k = random.randint(self.ITEM_SPLIT_MIN, min(self.ITEM_SPLIT_MAX, amount))
                    for i in range(k):
                        self.drop_items.append(entity.Entities.DropItem((monster.obj.pos[0] + random.randint(-10, 10),
                                                                         monster.obj.pos[1] + random.randint(-10, 10)),
                                                                        item, amount // k + (i < amount % k)))
            for monster2 in self.entities:
                monster.obj.object_gravitational(monster2.obj)
                monster.obj.object_collision(monster2.obj,
                                             (monster2.img.get_width() + monster2.img.get_height()) // 4 + (
                                                         monster.img.get_width() + monster.img.get_height()) // 4)
        self.player.update()
        for drop_item in self.drop_items:
            drop_item.update()
            if drop_item.hp_sys.hp <= 0:
                self.drop_items.remove(drop_item)
                del drop_item
        for proj in self.projectiles:
            proj.update()
            if proj.dead:
                self.projectiles.remove(proj)
                del proj
        self.damage_texts = [(dmg, tick + 1, pos) for dmg, tick, pos in self.damage_texts if tick < 80]
        for dmg, tick, pos in self.damage_texts:
            f = self.displayer.font.render(str(dmg), True, (255, 0, 0))
            fr = f.get_rect(center=resources.displayed_position((pos[0], pos[1] + (80 - tick) ** 2 // 100)))
            self.displayer.canvas.blit(f, fr)
        self.displayer.night_darkness_color = self.get_night_color(self.day_time % 1.0)
        self.displayer.night_darkness()
        self.player.ui()
        menaces = [entity for entity in self.entities if entity.IS_MENACE]
        y = self.displayer.SCREEN_HEIGHT - 80
        x = self.displayer.SCREEN_WIDTH // 2
        for menace in menaces:
            c_phase = len(menace.PHASE_SEGMENTS)
            for j, i in enumerate(menace.PHASE_SEGMENTS):
                if menace.hp_sys.hp >= menace.hp_sys.max_hp * i:
                    c_phase = len(menace.PHASE_SEGMENTS) - j - 1
            for i in range(len(menace.PHASE_SEGMENTS) + 1):
                if i >= c_phase:
                    pg.draw.circle(self.displayer.canvas, (0, 255, 0), (x - 380 + 50 * i, y - 100), 20)
                else:
                    pg.draw.circle(self.displayer.canvas, (255, 0, 0), (x - 380 + 50 * i, y - 100), 20)
                t_p = menace.hp_sys.hp / menace.hp_sys.max_hp
                t_l = 800 - 50 * len(menace.PHASE_SEGMENTS) - 80
                sp = [0] + menace.PHASE_SEGMENTS + [1]
                sp_e = sp[-c_phase - 1]
                sp_s = sp[-c_phase - 2]
                r_p = ((menace.hp_sys.hp - sp_s * menace.hp_sys.max_hp) /
                       (sp_e * menace.hp_sys.max_hp - sp_s * menace.hp_sys.max_hp))
                pg.draw.rect(self.displayer.canvas, (255, 0, 0),
                                 (x + 400 - t_l, y - 120, t_l, 40))
                pg.draw.rect(self.displayer.canvas, (0, 255, 0),
                                 (x + 400 - t_l, y - 120, int(t_l * t_p), 40))
                tf = self.displayer.font.render(str(int(t_p * 100)) + '%', True, (0, 0, 0))
                tf = pg.transform.scale_by(tf, 2.4)
                tfr = tf.get_rect(midright=(x + 400 - 10, y - 100))
                self.displayer.canvas.blit(tf, tfr)
                pg.draw.rect(self.displayer.canvas, (255, 0, 0),
                                 (x - 400, y - 50, 800, 60))
                pg.draw.rect(self.displayer.canvas, (0, 255, 0),
                                 (x - 400, y - 50, int(800 * r_p), 60))
                ft = self.displayer.font.render(f'{menace.NAME}({int(menace.hp_sys.hp)}/{int(menace.hp_sys.max_hp)})',
                                                True, (0, 0, 0))
                ftr = ft.get_rect(midright=(x + 360, y - 20))
                self.displayer.canvas.blit(ft, ftr)
            y -= 140
        if self.map_open:
            sf = pg.Surface((500, 500), pg.SRCALPHA)
            for i in range(-50, 50):
                for j in range(-50, 50):
                    try:
                        ps = (self.chunk_pos[0] + int(i / self.player.get_screen_scale()),
                              self.chunk_pos[1] + int(j / self.player.get_screen_scale()))
                        self.get_biome(ps)
                        vl = self.map_ns[ps]
                        col = (int(255 * vl), int(255 * vl), int(255 * vl))
                    except KeyError:
                        col = (0, 0, 0)
                    pg.draw.rect(sf, col, (i * 10, j * 10, 10, 10))
            if constants.USE_ALPHA:
                sf.set_alpha(200)
            self.displayer.canvas.blit(sf, (self.displayer.SCREEN_WIDTH // 2 - 250, self.displayer.SCREEN_HEIGHT // 2 - 250))
        self.displayer.update()
        if len(self.dialog.word_queue) or self.dialog.curr_text != '':
            self.dialog.update(self.pressed_keys)
        self.clock.update()
        return True

    def after_stop(self):
        self.pressed_keys.clear()
        self.pressed_mouse.clear()

    def handle_events(self):
        self.events = pg.event.get()
        for event in self.events:
            if event.type == pg.QUIT:
                raise resources.Interrupt()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    paused = True
                    while paused:
                        for ev in pg.event.get():
                            if ev.type == pg.QUIT:
                                raise resources.Interrupt()
                            elif ev.type == pg.KEYDOWN:
                                if ev.key == pg.K_BACKSPACE:
                                    paused = False
                                elif ev.key == pg.K_ESCAPE:
                                    raise resources.Interrupt()
                                elif ev.key == pg.K_F4:
                                    constants.FULLSCREEN = not constants.FULLSCREEN
                                    pg.display.set_mode(pg.display.get_window_size(), (pg.FULLSCREEN if constants.FULLSCREEN else 0) | constants.FLAGS)
                        pg.display.flip()
                    self.pressed_mouse = []
                    self.pressed_keys = []
                elif event.key == pg.K_F4:
                    constants.FULLSCREEN = not constants.FULLSCREEN
                    pg.display.set_mode(pg.display.get_window_size(), (pg.FULLSCREEN if constants.FULLSCREEN else 0) | constants.FLAGS)
                else:
                    self.pressed_keys.append(event.key)
            elif event.type == pg.KEYUP:
                if event.key in self.pressed_keys:
                    self.pressed_keys.remove(event.key)
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.pressed_mouse.append(event.button)
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button in self.pressed_mouse:
                    self.pressed_mouse.remove(event.button)

    def get_anchor(self):
        return self.player.obj.pos[0], self.player.obj.pos[1]
        # if not self.displayer.canvas.get_rect().collidepoint((self.player.obj.pos[0] - (self.entities[0].obj.pos[0] + self.player.obj.pos[0]) // 2 + self.displayer.SCREEN_WIDTH // 2, self.player.obj.pos[1] - (self.entities[0].obj.pos[1] + self.player.obj.pos[1]) // 2 + self.displayer.SCREEN_HEIGHT // 2)):
        # return self.player.obj.pos
        # return (self.entities[0].obj.pos[0] + self.player.obj.pos[0]) // 2, (self.entities[0].obj.pos[1] + self.player.obj.pos[1]) // 2

    def get_keys(self):
        return [event.key for event in self.events if event.type == pg.KEYDOWN]

    def get_pressed_keys(self):
        return self.pressed_keys

    def get_mouse_press(self):
        return [event.button for event in self.events if event.type == pg.MOUSEBUTTONDOWN]

    def get_pressed_mouse(self):
        return self.pressed_mouse

    def run(self):
        while self.update():
            pass


GAME: Game | None = None


def write_game(game: Game):
    global GAME
    GAME = game


def get_game() -> Game:
    global GAME
    if GAME is None:
        raise ValueError("Game not initialized")
    return GAME
