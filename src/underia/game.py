import os
import random
import time
from functools import lru_cache
import asyncio
import pygame as pg

import resources, visual, constants, physics, web
from underia import player, entity, projectiles, weapons, inventory, dialog, styles
import perlin_noise
import underia.settings as settings

MUSICS = {
    'lantern': ['snowland1', 'snowland0', 'heaven1', 'heaven0', 'forest0', 'rainforest0', 'desert0'],
    'wild_east': ['desert1', 'desert0', 'wither0', 'wither1'],
    'waterfall': ['forest0', 'rainforest0', 'desert0', 'snowland0', 'heaven0', 'heaven1', 'inner0', 'wither1'],
    'fields': ['forest1', 'rainforest1', 'snowland1', 'forest0'],
    'empty': ['hell0', 'hell1', 'forest1', 'rainforest1', 'battle', 'hallow0', 'hallow1', 'wither0', 'wither1',
              'life_forest0', 'life_forest1'],
    'snow': ['snowland0', 'snowland1', 'hallow0', 'hallow1'],
    #'here_we_are': ['inner0', 'inner1'],
    'amalgam': ['inner0', 'inner1', 'none0', 'none1', 'wither0', 'wither1'],
    'null': [],
    'rude_buster': ['battle'],
    'worlds_revolving': ['battle'],
    'boss_otherworld': ['battle'],
    'plantera': ['battle'],
    'wof_otherworld': ['battle'],
    'mercy_remix': ['battle'],
    'nothing_matter': ['battle'],
    'from_now_on': ['battle'],
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
        self.entities: list[entity.Entities.Entity | object] = []
        self.projectiles: list[projectiles.Projectiles.Projectile | object] = []
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
        self.wither_points: list[tuple[tuple[int, int], int]] = []
        self.role = ''
        self.server = None
        self.client: web.Client | None = None
        self.bl_bg = None
        self.lp = (100, 100)
        self.major_rate = 0
        self.game_time = 0

    def get_night_color(self, time_days: float):
        if len([1 for e in self.entities if type(e) is entity.Entities.AbyssEye]):
            return 255, 200, 200
        if 0.2 < time_days <= 0.3:
            r = int(255 * (time_days - 0.2) / 0.1)
            g = int(255 * (time_days - 0.2) / 0.1)
            b = int(255 * (time_days - 0.2) / 0.1)
        elif 0.3 < time_days <= 0.7:
            r = 255
            g = 255
            b = 255
            if 'solar eclipse' in self.world_events:
                r -= 100
                g -= 100
                b -= 150
        elif 0.7 < time_days <= 0.75:
            r = 255
            g = 255 - int(128 * (time_days - 0.7) / 0.05)
            b = 255 - int(255 * (time_days - 0.7) / 0.05)
        elif 0.75 < time_days <= 0.8:
            r = 255 - int(255 * (time_days - 0.75) / 0.05)
            g = 127 - int(127 * (time_days - 0.75) / 0.05)
            b = 0
        else:
            r = 0 if 'blood moon' not in self.world_events else 100
            g = 0
            b = 0
        if 'aimer' in self.player.accessories or 'photon_aimer' in self.player.accessories:
            r = 255 - (255 - r) * 4 // 5
            g = 255 - (255 - g) * 4 // 5
            b = 255 - (255 - b) * 4 // 5
        if 'chaos_evileye' in self.player.accessories or 'horizon_goggles' in self.player.accessories:
            r = 255 - (255 - r) * 2 // 3
            g = 255 - (255 - g) * 2 // 3
            b = 255 - (255 - b) * 2 // 3
        if 'fate_alignment_amulet' in self.player.accessories:
            r = 255 - (255 - r) // 3
            g = 255 - (255 - g) // 3
            b = 255 - (255 - b) // 3
        return r, g, b

    def on_day_start(self):
        if 'blood moon' in self.world_events:
            self.world_events.remove('blood moon')
        if random.random() < 0.03:
            self.world_events.append('solar eclipse')

    def on_day_end(self):
        if 'solar eclipse' in self.world_events:
            self.world_events.remove('solar eclipse')
        if random.random() < 0.03:
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
        self.lp = (0, 0)
        self.server = None
        self.client = None
        self.role = ''
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
        self.get_chunked_images.cache_clear()
        self.dialog = dialog.Dialogger(32, pg.Rect(0, pg.display.get_surface().get_height() * 3 // 4, pg.display.get_surface().get_width(), pg.display.get_surface().get_height() // 4), with_border=True, speed=1.6,
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
        formats = ['.ogg', '.wav']
        for m in os.listdir(resources.get_path('assets/musics')):
            if m[-4:] in formats:
                cnt += 1
        for s in os.listdir(resources.get_path('assets/sounds')):
            if s[-4:] in formats:
                cnt += 1
        self.gcnt = 0
        for m in os.listdir(resources.get_path('assets/musics')):
            if m[-4:] in formats:
                self.gcnt += 1
                self._display_progress(self.gcnt / cnt)
                self.musics[m.split('.')[0]] = pg.mixer.Sound(resources.get_path('assets/musics/' + m))
        for s in os.listdir(resources.get_path('assets/sounds')):
            if s[-4:] in formats:
                self.gcnt += 1
                self._display_progress(self.gcnt / cnt)
                self.sounds[s.split('.')[0]] = pg.mixer.Sound(resources.get_path('assets/sounds/' + s))
        for x in range(-200, 200):
            for y in range(-200, 200):
                self.get_biome((x, y))
            if x % 40 == 0:
                self._display_progress((x + 200) / 400, 0)

    def play_sound(self, sound: str, vol=1.0, stop_if_need=False, fadeout=0):
        self.sounds[sound].set_volume(vol * constants.SOUND_VOL)
        if self.sounds[sound].get_num_channels():
            if stop_if_need:
                self.sounds[sound].stop()
            else:
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
        if len([1 for e in self.entities if type(e) is entity.Entities.ReincarnationTheWorldsTree]):
            return 'life_forest'
        if len([1 for e in self.entities if type(e) in [entity.Entities.Jevil, entity.Entities.Jevil2, entity.Entities.OblivionAnnihilator]]) or \
                self.player.inventory.is_enough(inventory.ITEMS['chaos_heart']):
            return 'inner'
        if pos is None:
            pos = self.chunk_pos
        if pos[0] ** 2 + pos[1] ** 2 < 1000:
            return 'forest'
        lvs = ['hell', 'desert', 'rainforest', 'forest', 'snowland', 'heaven', 'hallow', 'wither']
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
        for pp, r in self.wither_points:
            if physics.distance(pp[0] - (pos[0] - 120) * self.CHUNK_SIZE, pp[1] - (pos[1] - 120) * self.CHUNK_SIZE) < r:
                idx = 7
        biome = lvs[idx]
        if b:
            no_of_decor = [4, 7, 10, 8, 4, 3, 6, 5][idx]
            if no_of_decor:
                for i in range(no_of_decor):
                    if random.random() < (0.007 - [0.003, 0.004, -0.002, -0.001, 0.003, 0.003, -0.001, -0.002][idx]) / 3:
                        self.decors.append((f'background_decor_{biome}{i + 1}',
                                            (pos[0] - 120) * self.CHUNK_SIZE + random.randint(-self.CHUNK_SIZE // 2, self.CHUNK_SIZE // 2),
                                             (pos[1] - 120) * self.CHUNK_SIZE + random.randint(-self.CHUNK_SIZE // 2, self.CHUNK_SIZE // 2),
                                            random.choices(list(range(1, 1000)), weights=list(range(1, 1000)), k=1)[0] / 100.0))
        return biome

    def get_player_objects(self) -> list[physics.Mover]:
        return [self.player.obj] + self.p_obj

    @lru_cache(maxsize=None)
    def get_chunked_images(self, biomes, bg_size):
        cols = {'hell': (255, 0, 0), 'desert': (255, 191, 63), 'forest': (0, 255, 0), 'rainforest': (127, 255, 0),
                'snowland': (255, 255, 255), 'heaven': (127, 127, 255), 'inner': (0, 0, 0), 'none': (0, 0, 0),
                'hallow': (0, 255, 255)}
        size = len(biomes)
        surf = pg.Surface((size * bg_size, size * bg_size), pg.SRCALPHA)
        surf.set_alpha(255)
        for i in range(size):
            for j in range(size):
                bo = biomes[i][j]
                if constants.EASY_BACKGROUND:
                    bg = pg.Surface((bg_size, bg_size))
                    bg.fill(cols[bo])
                else:
                    bg = self.graphics.get_graphics('nbackground_' + bo)
                surf.blit(bg, (i * bg_size, j * bg_size))
        return surf

    def update_map(self):
        bg_size = 200  # int(120 / self.player.get_screen_scale())
        chunk_size = 3
        bg_ax = int(self.player.ax / self.player.get_screen_scale()) % (bg_size * chunk_size)
        bg_ay = int(self.player.ay / self.player.get_screen_scale()) % (bg_size * chunk_size)
        cols = {'hell': (255, 0, 0), 'desert': (255, 191, 63), 'forest': (0, 255, 0), 'rainforest': (127, 255, 0),
                'snowland': (255, 255, 255), 'heaven': (127, 127, 255), 'inner': (0, 0, 0), 'none': (0, 0, 0),
                'hallow': (0, 255, 255), 'wither': (50, 0, 0), 'life_forest': (50, 127, 0)}
        if not self.graphics.is_loaded('nbackground_hell') or self.graphics['nbackground_hell'].get_width() != bg_size:
            for k in cols.keys():
                self.graphics['nbackground_' + k] = pg.transform.scale(self.graphics['background_' + k],
                                                                       (bg_size, bg_size))
        if pg.K_TAB in self.pressed_keys:
            self.map_open = not self.map_open
        if self.get_biome() != self.last_biome[0]:
            self.last_biome = (self.last_biome[0], self.last_biome[1] + 1)
            if self.last_biome[1] >= 20:
                self.last_biome = (self.get_biome(), 0)
        slg, _ = self.last_biome
        for i in range(-bg_size, self.displayer.SCREEN_WIDTH + bg_size * chunk_size, bg_size * chunk_size):
            for j in range(-bg_size, self.displayer.SCREEN_HEIGHT + bg_size * chunk_size, bg_size * chunk_size):
                cx, cy = resources.real_position((i - bg_ax + bg_size // 2, j - bg_ay + bg_size // 2))
                bgg = [[self.get_biome(((cx + i * bg_size * self.player.get_screen_scale()) // self.CHUNK_SIZE + 120,
                                        (cy + j * bg_size * self.player.get_screen_scale()) // self.CHUNK_SIZE + 120))
                        for j in range(chunk_size)] for i in range(chunk_size)]
                surf = self.get_chunked_images(tuple([tuple(b) for b in bgg]), bg_size)
                #self.bl_bg.blit(surf, (i - bg_ax, j - bg_ay))
                self.displayer.canvas.blit(surf, (i - bg_ax, j - bg_ay))

    def blend_map(self):
        # self.displayer.canvas.blit(self.bl_bg, (0, 0))
        self.update_map()

    def update(self):
        if self.client is not None and not self.client.started:
            loop = asyncio.get_event_loop()
            loop.create_task(self.client.start())
        if '3rd_sanctuary' not in MUSICS:
            MUSICS['3rd_sanctuary'] = ['forest0', 'forest1', 'rainforest0', 'rainforest1', 'desert0', 'desert1',
                                       'snowland0', 'snowland1', 'hell0', 'hell1', 'heaven0', 'heaven1']
            MUSICS['dark_sanctuary'] = ['forest0', 'forest1', 'rainforest0', 'rainforest1', 'desert0', 'desert1',
                                        'snowland0', 'snowland1', 'hell0', 'hell1', 'heaven0', 'heaven1']
        if (self.prepared_music is None and self.channel.get_busy() == 0) or \
                (self.cur_music is not None and (self.get_biome() + str(int(0.3 < self.day_time < 0.7))) not in
                 self.MUSICS[self.cur_music] and not len([1 for e in self.entities if e.IS_MENACE])) \
                or (self.cur_music is not None and len([1 for e in self.entities if e.IS_MENACE]) and
                    'battle' not in self.MUSICS[self.cur_music]):
            if len([1 for e in self.entities if e.IS_MENACE]):
                self.cur_music = None
                self.channel.stop()
                if len([1 for e in self.entities if type(e) in [entity.Entities.Jevil, entity.Entities.Jevil2]]):
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
                if self.chapter > 1:
                    self.prepared_music = 'from_now_on'
            else:
                self.cur_music = None
                self.channel.fadeout(8000)
                self.prepared_music = random.choice([k for k, v in self.MUSICS.items() \
                                                     if (self.get_biome() + str(int(0.3 < self.day_time < 0.7))) in v])
        if self.cur_music is None and self.prepared_music is not None and self.channel.get_busy() == 0:
            self.cur_music = self.prepared_music
            self.channel.set_volume(constants.MUSIC_VOL)
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
        self.handle_events()
        self.blend_map()
        for img, x, y, scale_req in self.decors:
            if self.displayer.canvas.get_rect().collidepoint(*resources.displayed_position((x, y))) and scale_req >= self.player.get_screen_scale():
                self.displayer.canvas.blit(pg.transform.scale_by(self.graphics.get_graphics(img),
                                                                     1 / self.player.get_screen_scale()),
                                           resources.displayed_position((x, y)))
        chunk_entities = {}
        for i, e in enumerate(self.entities):
            e.t_draw()
        '''
            px, py = resources.relative_position(e.obj.pos)
            cp = (round(px / 200), round(py / 200))
            if cp not in chunk_entities:
                chunk_entities[cp] = [i]
            else:
                chunk_entities[cp].append(i)
        for cp, entities in chunk_entities.items():
            for i, e1 in enumerate(entities):
                for e2 in entities[i + 1:]:
                    self.entities[e1].obj.object_collision(self.entities[e2].obj,
                                                           (self.entities[e1].d_img.get_width() + self.entities[e2].d_img.get_width() +
                                                            self.entities[e1].d_img.get_height() + self.entities[e2].d_img.get_height()) / 4)
        '''
        for e in self.entities:
            if e.hp_sys.hp <= 0:
                self.entities.remove(e)
                if e.obj.IS_OBJECT:
                    if e.SOUND_DEATH is not None:
                        e.play_sound('killed_' + e.SOUND_DEATH)
                    else:
                        e.play_sound('enemydust')
                loots = e.LOOT_TABLE()
                for item, amount in loots:
                    k = random.randint(self.ITEM_SPLIT_MIN, min(self.ITEM_SPLIT_MAX, amount) + 1)
                    for i in range(k):
                        self.drop_items.append(entity.Entities.DropItem((e.obj.pos[0] + random.randint(-10, 10),
                                                                         e.obj.pos[1] + random.randint(-10, 10)),
                                                                        item, amount // k + (i < amount % k)))
        if self.client is not None or self.server is not None:
            players = self.client.player_datas.values() if self.client is not None else self.server.players.values()
            for p in players:
                p_data: web.SinglePlayerData = p
                sf = self.player.profile.get_surface(*p_data.col)
                sf = pg.transform.scale(sf, (int(40 / self.player.get_screen_scale()),
                                             int(40 / self.player.get_screen_scale())))
                sfr = sf.get_rect(center=resources.displayed_position(p_data.pos))
                self.displayer.canvas.blit(sf, sfr)
                styles.hp_bar(p_data.hp_sys, resources.displayed_position((p_data.pos[0], p_data.pos[1] - 30)), 40)
        if self.server is not None:
            self.server.update()
        if self.client is not None:
            for d in self.client.displays:
                pos = d['pos']
                dx, dy = resources.displayed_position(pos)
                if not self.displayer.canvas.get_rect().collidepoint(dx, dy):
                    continue
                rot = d['rot']
                img_idx = d['img_idx']
                display_mode = d['display_mode']
                if display_mode == entity.Entities.DisplayModes.NO_DIRECTION:
                    rot = 0
                else:
                    rot = round(rot / 3) * 3
                img = entity.entity_get_surface(display_mode, rot, 1 / self.player.get_screen_scale(),
                                                self.graphics[img_idx])
                imr = img.get_rect(center=resources.displayed_position(pos))
                self.displayer.canvas.blit(img, imr)
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
            f = self.displayer.font_mono.render(str(dmg), True, (255, 0, 0))
            fr = f.get_rect(center=resources.displayed_position((pos[0], pos[1] + (80 - tick) ** 3 // 4000)))
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
            if not menace.show_bar:
                continue
            for i in range(len(menace.PHASE_SEGMENTS) + 1):
                if i >= c_phase:
                    pg.draw.circle(self.displayer.canvas, (207, 255, 112), (x - 380 + 50 * i, y - 100), 20)
                else:
                    pg.draw.circle(self.displayer.canvas, (227, 105, 86), (x - 380 + 50 * i, y - 100), 20)
                pg.draw.circle(self.displayer.canvas, (242, 166, 94), (x - 380 + 50 * i, y - 100), 20, width=8)
                t_p = menace.hp_sys.hp / menace.hp_sys.max_hp
                pc_p = menace.hp_sys.pacify / menace.hp_sys.max_hp
                pp_p = menace.hp_sys.pacify / (menace.hp_sys.max_hp - menace.hp_sys.hp) if menace.hp_sys.hp < menace.hp_sys.max_hp else 0
                t_l = 800 - 50 * len(menace.PHASE_SEGMENTS) - 80
                sp = [0] + menace.PHASE_SEGMENTS + [1]
                sp_e = sp[-c_phase - 1]
                sp_s = sp[-c_phase - 2]
                r_p = ((menace.hp_sys.hp - sp_s * menace.hp_sys.max_hp) /
                       (sp_e * menace.hp_sys.max_hp - sp_s * menace.hp_sys.max_hp))
                pg.draw.rect(self.displayer.canvas, (227, 105, 86),
                                 (x + 400 - t_l, y - 120, t_l, 40))
                pg.draw.rect(self.displayer.canvas, (207, 255, 112),
                                 (x + 400 - t_l, y - 120, int(t_l * t_p), 40))
                pg.draw.rect(self.displayer.canvas, (0, 255, 255),
                             (x + 400 - int(t_l * pc_p), y - 120, int(t_l * pc_p), 40))
                pg.draw.rect(self.displayer.canvas, (242, 166, 94),
                                 (x + 400 - t_l, y - 120, t_l, 40), width=8, border_radius=3)
                if not menace.hp_sys.IMMUNE:
                    tf = self.displayer.ffont.render(str(int(t_p * 100)) + '%', True, (0, 0, 0))
                    tfr = tf.get_rect(midright=(x + 400 - 10, y - 100))
                    self.displayer.canvas.blit(tf, tfr)
                    tf = self.displayer.ffont.render(str(int(t_p * 100)) + '%', True, (255, 255, 255))
                    tfr = tf.get_rect(midright=(x + 400 - 15, y - 105))
                    self.displayer.canvas.blit(tf, tfr)
                pg.draw.rect(self.displayer.canvas, (227, 105, 86),
                                 (x - 400, y - 50, 800, 60))
                pg.draw.rect(self.displayer.canvas, (207, 255, 112),
                                 (x - 400, y - 50, int(800 * r_p), 60))
                pg.draw.rect(self.displayer.canvas, (242, 166, 94),
                                 (x - 400, y - 50, 800, 60), width=8, border_radius=3)
                ft = self.displayer.font.render(f'{styles.text(menace.NAME)}' + f'({int(menace.hp_sys.hp)}/{int(menace.hp_sys.max_hp)})' if not menace.hp_sys.IMMUNE else '',
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
        if not self.player.in_ui:
            w = self.player.weapons[self.player.sel_weapon]
            im = self.graphics['items_' + inventory.ITEMS[w.name.replace(' ', '_')].img]
            im = pg.transform.scale(im, (64, 64))
            imr = im.get_rect(topright=self.displayer.reflect(*pg.mouse.get_pos()))
            self.displayer.canvas.blit(im, imr)
        self.displayer.update()
        if len(self.dialog.word_queue) or self.dialog.curr_text != '':
            self.dialog.update(self.pressed_keys)
        self.clock.update()
        pg.display.update()
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
                    window = pg.display.get_surface()
                    mask = pg.Surface(window.get_size(), pg.SRCALPHA)
                    mask.fill((0, 0, 0))
                    mask.set_alpha(200)
                    window.blit(mask, (0, 0))
                    font = pg.font.Font(resources.get_path('assets/dtm-sans.otf' if constants.LANG != 'zh' else 'assets/fz-pixel.ttf'), 30)
                    text = font.render('Underia', True, (255, 255, 255))
                    text_rect = text.get_rect(center=(window.get_rect().centerx,
                                                      window.get_rect().centery - 300))
                    window.blit(text, text_rect)
                    text = font.render('by KLpig', True, (255, 255, 255))
                    text_rect = text.get_rect(center=(window.get_rect().centerx,
                                                      window.get_rect().centery - 270))
                    window.blit(text, text_rect)
                    text = font.render('[BACKSPACE] to continue', True, (255, 255, 255))
                    text_rect = text.get_rect(center=(window.get_rect().centerx,
                                                      window.get_rect().centery - 80))
                    window.blit(text, text_rect)
                    text = font.render('[ESCAPE] to quit', True, (255, 255, 255))
                    text_rect = text.get_rect(center=(window.get_rect().centerx,
                                                      window.get_rect().centery))
                    window.blit(text, text_rect)
                    text = font.render('[W] to start server', True, (255, 255, 255))
                    text_rect = text.get_rect(center=(window.get_rect().centerx,
                                                      window.get_rect().centery + 80))
                    window.blit(text, text_rect)
                    text = font.render('[S] for settings', True, (255, 255, 255))
                    text_rect = text.get_rect(center=(window.get_rect().centerx,
                                                      window.get_rect().centery + 160))
                    window.blit(text, text_rect)
                    pg.display.flip()
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
                                elif ev.key == pg.K_w:
                                    if self.server is None:
                                        self.server = web.SocketServer()
                                        loop = asyncio.get_event_loop()
                                        loop.create_task(self.server.start_server())
                                elif ev.key == pg.K_s:
                                    settings.set_settings()
                        pg.display.update()
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

    async def entity_update(self):
        st = time.time()
        while True:
            for ee in self.entities:
                ee.t_update()
            nt = time.time()
            await asyncio.sleep(max(0.0, 1 / 40 - (nt - st)))
            st = time.time()

    async def map_update(self):
        st = time.time()
        while True:
            self.update_map()
            nt = time.time()
            await asyncio.sleep(max(0.0, 1 / 100 - (nt - st)))
            st = time.time()

    async def run(self):
        asyncio.create_task(self.entity_update())
        while self.update():
            await asyncio.sleep(0)


GAME: Game | None = None


def write_game(game: Game):
    global GAME
    GAME = game


def get_game() -> Game:
    global GAME
    if GAME is None:
        raise ValueError("Game not initialized")
    return GAME
