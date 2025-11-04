import math
import os
import random
import time
import datetime
from functools import lru_cache
import asyncio
from importlib.metadata import version

import pygame as pg

import resources, visual, constants, physics, web, underia3, values
from underia import player, entity, projectiles, weapons, inventory, dialog, styles, animation
import perlin_noise
import underia.settings as settings

MUSICS = {
    'lantern': ['snowland1', 'snowland0', 'heaven1', 'heaven0', 'forest0', 'rainforest0', 'desert0'],
    'wild_east': ['desert1', 'desert0', 'wither0', 'wither1'],
    'waterfall': ['forest0', 'rainforest0', 'desert0', 'snowland0', 'heaven0', 'heaven1', 'inner0', 'wither1',
                  'ocean0', 'ocean1'],
    'fields': ['forest1', 'rainforest1', 'snowland1', 'forest0', 'ocean'],
    'empty': ['hell0', 'hell1', 'forest1', 'rainforest1', 'battle', 'hallow0', 'hallow1', 'wither0', 'wither1',
              'life_forest0', 'life_forest1', 'ocean0', 'ocean1'],
    'snow': ['snowland0', 'snowland1', 'hallow0', 'hallow1'],
    'hesitation': ['fallen_sea0', 'fallen_sea1', 'heaven1', 'wither1', 'ocean1', 'ocean0'],
    'sanctuary': ['fallen_sea0', 'fallen_sea1', 'hell0', 'heaven0', 'heaven1', 'ocean1'],
    #'here_we_are': ['inner0', 'inner1'],
    'amalgam': ['inner0', 'inner1', 'none0', 'none1', 'wither0', 'wither1'],
    'left_alone': ['hot_spring0', 'hot_spring1', 'hell0', 'hell1'],
    'hadopelagic_pressure': ['hot_spring0', 'hot_spring1', 'ocean0', 'ocean1', 'hell0', 'fallen_sea1'],
    'hydrothermophobia': ['hot_spring0', 'hot_spring1', 'hell1', 'hell0', 'fallen_sea1'],
    'null': [],
    'rude_buster': ['battle'],
    'worlds_revolving': ['battle'],
    'boss_otherworld': ['battle'],
    'plantera': ['battle'],
    'wof_otherworld': ['battle'],
    'mercy_remix': ['battle'],
    'nothing_matter': ['battle'],
    'from_now_on': ['battle'],
    'knight_appears': ['battle'],
    'knight': ['battle'],
    'ruf_calamity': ['battle'],
    'platinum_star': ['battle'],
}

MUSIC_DATA = {
    'lantern': 'Toby Fox - Lantern (Deltarune)',
    'wild_east': 'MasterSwordRemix - Wild East (Undertale Yellow)',
    'waterfall': 'Toby Fox - Waterfall (Undertale)',
    'fields': 'Toby Fox - Fields of Hopes and Dreams (Deltarune)',
    'empty': '',
    'snow': 'Scott Lloyd Shelly - Snow (Terraria)',
    'amalgam': 'Toby Fox - Amalgam (Undertale)',
    'null': '',
    'rude_buster': 'Toby Fox - Rude Buster (Deltarune)',
    'worlds_revolving': 'Toby Fox - The World\'s Revolving (Deltarune)',
    'boss_otherworld': 'Jonathan van den Wijngaarden, Frank Klepacki - Boss 2 (Otherworldly, Terraria)',
    'mercy_remix': 'Jammin - Mercy (Remixed, Terraria Homeward Journey)',
    'nothing_matter': 'Jammin - Nothing Matters (Terraria Homeward Journey)',
    'from_now_on': 'Toby Fox - From Now On (Deltarune)',
    'dark_sanctuary': 'Toby Fox - Dark Sanctuary (Deltarune)',
    '3rd_sanctuary': 'Toby Fox - 3rd Sanctuary (Deltarune)',
    'knight': 'Toby Fox - Black Knife (Deltarune)',
    'hesitation': 'Hesitation (Terraria Calamity)',
    'sanctuary': 'Sanctuary (Terraria Calamity)',
    'hadopelagic_pressure': 'Hadopelagic Pressure (Terraria Calamity)',
    'hydrothermophobia': 'Hydrothermophobia (Terraria Calamity)',
    'left_alone': 'Left Alone (Terraria Calamity)',

    'platinum_star': 'Platinum Star (Terraria Fargo)',
    'ruf_calamity': 'Raw, Unfiltered Calamity (Terraria Calamity)'
}

class Game:
    ITEM_SPLIT_MIN = 1
    ITEM_SPLIT_MAX = 2
    TIME_SPEED = .00004
    CHUNK_SIZE = 100

    def __init__(self):
        self.dimension = 'overworld'
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
        self.mus_text = None
        self.must_st = -1
        self.fun = random.randint(1, 13)
        self.c_dmg = 0
        self.further_entities: dict[tuple[int, int], list[entity.Entities.Entity | object]] = {}
        self.t_cmd = ''
        self.save_time = datetime.datetime.now()

    def get_night_color(self, time_days: float):
        if len([1 for e in self.entities if type(e) is entity.Entities.AbyssEye]):
            return 255, 200, 200
        if len([1 for e in self.entities if type(e) is entity.Entities.CLOCK]):
            return 0, 50, 50
        dd = [e.nightstate for e in self.entities if type(e) is underia3.StanoZolol]
        if len(dd):
            return 150 - dd[0] * 150, 150 - dd[0] * 150, 0
        if 0.2 < time_days <= 0.3:
            r = 50 + int(205 * (time_days - 0.2) / 0.1)
            g = 50 + int(205 * (time_days - 0.2) / 0.1)
            b = 50 + int(100 * (time_days - 0.2) / 0.1)
        elif 0.3 < time_days <= 0.7:
            r = 255
            g = 255
            b = 255
            if 'solar eclipse' in self.world_events:
                r -= 100
                g -= 100
                b -= 150
        elif 0.45 < time_days <= 0.55:
            r = 255
            g = 255
            b = 200
            if 'solar eclipse' in self.world_events:
                r -= 100
                g -= 100
                b -= 150
        elif 0.7 < time_days <= 0.75:
            r = 255
            g = 255 - int(128 * (time_days - 0.7) / 0.05)
            b = 255 - int(175 * (time_days - 0.7) / 0.05)
        elif 0.75 < time_days <= 0.8:
            r = 255 - int((205 if 'blood moon' not in self.world_events else 55) * (time_days - 0.75) / 0.05)
            g = 127 - int(87 * (time_days - 0.75) / 0.05)
            b = 80
        else:
            r = 50 if 'blood moon' not in self.world_events else 200
            g = 50
            b = 80
        if self.get_biome() == 'fallen_sea':
            r = 40
            g = 40
            b = 120
        if self.get_biome() == 'hot_spring':
            r = 60
            g = 20
            b = 20
        if self.get_biome() == 'hell' and self.chapter == 2:
            r = 255
            g = 0
            b = 0
        if 'aimer' in self.player.accessories or 'photon_aimer' in self.player.accessories:
            r = 255 - (255 - r) * 4 // 5
            g = 255 - (255 - g) * 4 // 5
            b = 255 - (255 - b) * 4 // 5
        if 'chaos_evileye' in self.player.accessories or 'horizon_goggles' in self.player.accessories:
            r = 255 - (255 - r) * 3 // 5
            g = 255 - (255 - g) * 3 // 5
            b = 255 - (255 - b) * 3 // 5
        if 'fate_alignment_amulet' in self.player.accessories or self.chapter > 1:
            r = 255 - (255 - r) // 2
            g = 255 - (255 - g) // 2
            b = 255 - (255 - b) // 2
        if self.get_biome() == 'hot_spring':
            r = (120 + r) // 3
            g = (40 + r) // 3
            b = (40 + r) // 3
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
        stt = 3 - st
        window = pg.display.get_surface()
        window.fill((0,0,0))
        font = self.displayer.font
        words = [
            'ALRIGHT, EVERYTHING, NOW, HAS ALREADY BEEN PREPARED FOR \'ME\'......',
            'FOR THIS WHOLE "UNDERIA"... AND THE OTHER WORLDS......',
            'LET\'S JUST WAIT FOR ALL THAT TO BE DONE, SHALL WE?........'
        ]
        for i in range(stt - 1):
            txt = font.render(words[i], True, (255, 255, 255))
            window.blit(txt, (100, 100 + i * 100))
        ntxt = font.render(words[stt - 1][:min(len(words[stt - 1]), int(1.3 * prog * len(words[stt - 1])))], True, (255, 255, 255))
        window.blit(ntxt, (100, stt * 100))
        pg.display.update()
        pg.event.get()

    def setup(self):
        if 'fun' not in dir(self):
            self.fun = random.randint(1, 13)
        self.player.shield_break = 0
        self.dimension = 'overworld'
        rr = random.Random()
        for weapon in weapons.WEAPONS.values():
            for d in weapon.damages.keys():
                rr.seed(self.fun + hash(weapon))
                ar = rr.randint(90, 120) // 5 * 5 / 100
                weapon.damages[d] *= ar
                if 'mana_cost' in dir(weapon):
                    weapon.mana_cost *= ar * rr.uniform(.9, 1.2)

        self.player.hp_sys.is_player = True
        self.must_st = -1
        self.mus_text = None
        self.lp = (0, 0)
        self.server = None
        self.client = None
        self.role = ''
        self.p_obj = []
        self.sounds = {}
        self.player.splint_t = 0
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
        formats = ['.ogg', '.wav', '.mp3']
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
        self.save_time = datetime.datetime.now()

    def play_sound(self, sound: str, vol=1.0, stop_if_need=True, fadeout=0):
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

    @staticmethod
    @lru_cache(maxsize=constants.MEMORY_USE)
    def is_wall(pos):
        return int(random.random() * 10 + pos[0] * 114 + pos[1] * 77) % 10 < 8

    def get_biome(self, pos=None):
        if pos is None:
            pos = self.chunk_pos
        if self.dimension == 'ancient_city':
            hp = ((pos[0] - 120) * self.CHUNK_SIZE // 400, (pos[1] - 120) * self.CHUNK_SIZE // 400)
            if ((pos[0] - 120) * self.CHUNK_SIZE % 4000 < 400 or (pos[1] - 120) * self.CHUNK_SIZE % 4000 < 400) and self.is_wall(hp):
                return 'ancient_wall'
            else:
                return 'ancient_city'
        if len([1 for e in self.entities if type(e) in [entity.Entities.OmegaFlowery]]):
            return 'none'
        if len([1 for e in self.entities if type(e) is entity.Entities.AbyssEye]):
            return 'heaven'
        if len([1 for e in self.entities if type(e) is entity.Entities.ReincarnationTheWorldsTree]):
            return 'life_forest'
        if len([1 for e in self.entities if type(e) is entity.Entities.MATTER]):
            return 'hell'
        if len([1 for e in self.entities if type(e) in [entity.Entities.Jevil, entity.Entities.Jevil2, entity.Entities.OblivionAnnihilator]]) or \
                self.player.inventory.is_enough(inventory.ITEMS['chaos_heart']):
            return 'inner'

        if self.chapter == 2:
            if (pos[1] - 120) * self.CHUNK_SIZE < -100000:
                return 'ancient_city'
            elif (pos[1] - 120) * self.CHUNK_SIZE < -80000:
                return 'ancient'

        pos_fallen_sea = physics.Vector2D(self.fun ** 3 % 360, ((self.fun * 3 // 4 + 1000 // self.fun) ** 2 * 17 % 1000) + 300)
        if (pos[0] - pos_fallen_sea.x - 120) ** 2 + (pos[1] - pos_fallen_sea.y - 120) ** 2 < 10000:
            return 'fallen_sea'
        elif (pos[0] - pos_fallen_sea.x - 120) ** 2 + (pos[1] - pos_fallen_sea.y - 120) ** 2 < 15000:
            return 'desert'


        if pos[1] > 2500 and self.stage >= 1:
            return 'hot_spring'
        if (pos[0] - 120) ** 2 + (pos[1] - 120) ** 2 < 5000:
            return 'forest'


        lvs = ['hell', 'desert', 'rainforest', 'forest', 'snowland', 'heaven', 'hallow', 'wither', 'ancient']
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
        idx = int(self.map_ns[pos] * 6)
        if pos in self.w_ns.keys():
            w = self.w_ns[pos]
        else:
            w = self.weather_noise([pos[0] / 400.0, pos[1] / 400.0])
            self.wm_min = min(self.m_min, w)
            self.wm_max = max(self.m_max, w)
        w = (w - self.wm_min) / (self.wm_max - self.wm_min + 0.01)
        if (pos[0] - 120) ** 2 + (pos[1] - 120) ** 2 * 4 > 12000000:
            dt = w * .5 + idx / 12
            if dt > .9:
                idx = 2
            elif dt > .75:
                idx = 3
            elif dt > .65:
                idx = 1
            else:
                return 'ocean'
        elif abs(w * .291 + self.map_ns[pos] * .7098 - .5) < .01 + .05 * (((pos[0] - 120) ** 2 + (pos[1] - 120) ** 2 * 4) / 12000000) ** .5:
            return 'ocean'
        elif 12000000 > (pos[0] - 120) ** 2 + (pos[1] - 120) ** 2 * 4 > 11000000:
            return 'desert'
        elif 5 > idx > 0:
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
        if self.chapter == 1:
            for pp, r in self.hallow_points:
                if physics.distance(pp[0] - (pos[0] - 120) * self.CHUNK_SIZE, pp[1] - (pos[1] - 120) * self.CHUNK_SIZE) < r:
                    idx = 6
            for pp, r in self.wither_points:
                if physics.distance(pp[0] - (pos[0] - 120) * self.CHUNK_SIZE, pp[1] - (pos[1] - 120) * self.CHUNK_SIZE) < r:
                    idx = 7
        if idx != 1 and len([1 for e in self.entities if type(e) in [underia3.TralaleroTralala]]):
            return 'ocean'
        biome = lvs[idx]
        if b:
            no_of_decor = [4, 7, 10, 8, 4, 3, 6, 5, 0][idx]
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

    YCOLS = {'hell': (255, 0, 0), 'desert': (255, 191, 63), 'forest': (0, 255, 0), 'rainforest': (127, 255, 0),
                'snowland': (255, 255, 255), 'heaven': (127, 127, 255), 'inner': (0, 0, 0), 'none': (0, 0, 0),
                'hallow': (0, 255, 255), 'fallen_sea': (0, 100, 255), 'hot_spring': (50, 0, 0)}

    @lru_cache(maxsize=int(constants.MEMORY_USE * .05))
    def get_chunked_images(self, biomes, bg_size):
        cols = Game.YCOLS
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
        bg_size = 200 if self.dimension == 'overworld' else int(400 / self.player.get_screen_scale())

        pp = self.chunk_pos
        

        chunk_size = 3
        bg_ax = int(self.player.ax / self.player.get_screen_scale()) % (bg_size * chunk_size)
        bg_ay = int(self.player.ay / self.player.get_screen_scale()) % (bg_size * chunk_size)
        cols = {'hell': (255, 0, 0), 'desert': (255, 191, 63), 'forest': (0, 255, 0), 'rainforest': (127, 255, 0),
                'snowland': (255, 255, 255), 'heaven': (127, 127, 255), 'inner': (0, 0, 0), 'none': (0, 0, 0),
                'hallow': (0, 255, 255), 'wither': (50, 0, 0), 'life_forest': (50, 127, 0), 'ancient': (50, 0, 0),
                'ancient_city': (255, 200, 128), 'ancient_wall': (100, 50, 0), 'ocean': (0, 0, 255),
                'fallen_sea': (0, 100, 255), 'hot_spring': (50, 0, 0)}
        if not self.graphics.is_loaded('nbackground_hell') or self.graphics['nbackground_hell'].get_width() != bg_size:
            for k in cols.keys():
                self.graphics['nbackground_' + k] = pg.transform.scale(self.graphics['background_' + k],
                                                                       (bg_size, bg_size))
        if pg.K_TAB in self.get_keys():
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
        if self.chapter == 2:
            for e in self.entities:
                if e.obj.pos[1] < -99000:
                    e.obj.pos.y = -99000
            if self.player.obj.pos[1] < -99000:
                self.player.obj.pos.y = -98999
                if self.player.inventory.is_enough(underia3.ITEMS['ancient_key']) or self.dimension == 'ancient_city':
                    if self.player.max_mana >= 300:
                        self.dimension = 'overworld' if self.dimension == 'ancient_city' else 'ancient_city'
                        self.player.profile.add_point(10)
                        self.player.hp_sys.max_hp = 1200
                        self.player.max_mana = 500
                    else:
                        self.dialog.dialog('You are not strong enough to enter the Ancient City.')
                elif not len([1 for e in self.entities if type(e) is underia3.ChaosDisciple]):
                    self.entities.append(underia3.ChaosDisciple(self.player.obj.pos + (random.randint(-1000, 1000), random.randint(-1000, 1000))))
                self.player.obj.velocity *= 0
                self.player.obj.velocity += (0, 500)

            dp = resources.displayed_position((0, -100000))
            bs = int(1024 / self.player.get_screen_scale())
            if -1500 <= dp[1] <= self.displayer.canvas.get_height() + 1500:
                ap = int(self.player.ax / self.player.get_screen_scale()) % bs
                for i in range(-ap, self.displayer.SCREEN_WIDTH + ap, bs):
                    self.displayer.canvas.blit(pg.transform.scale_by(self.graphics.get_graphics('entity3_uwall' + str(i // bs % 2 + 1)),
                                                                     1 / self.player.get_screen_scale()), (i, dp[1]))

    def blend_map(self):
        # self.displayer.canvas.blit(self.bl_bg, (0, 0))
        self.update_map()

    def update(self):
        for a in animation.ANIMATIONS:
            a.update()
        if self.client is not None and not self.client.started:
            loop = asyncio.get_event_loop()
            loop.create_task(self.client.start())
        if '3rd_sanctuary' not in MUSICS:
            MUSICS['3rd_sanctuary'] = ['forest0', 'forest1', 'rainforest0', 'rainforest1', 'desert0', 'desert1',
                                       'snowland0', 'snowland1', 'hell0', 'hell1', 'heaven0', 'heaven1', 'ancient0',
                                       'ancient1']
            MUSICS['dark_sanctuary'] = ['ancient0', 'ancient1', 'ancient_city0', 'ancient_city1',
                                        'ancient_wall0', 'ancient_wall1']
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
                elif len([1 for e in self.entities if type(e) is entity.Entities.Ray]):
                    self.prepared_music = 'platinum_star'
                elif len([1 for e in self.entities if type(e) is entity.Entities.Irec]):
                    self.prepared_music = 'ruf_calamity'
                elif len([1 for e in self.entities if type(e) is entity.Entities.ReincarnationTheWorldsTree]):
                    self.prepared_music = 'mercy_remix'
                elif len([1 for e in self.entities if type(e) is entity.Entities.Faith]):
                    self.prepared_music = 'nothing_matter'
                elif len([1 for e in self.entities if type(e) is entity.Entities.OmegaFlowery]):
                    self.prepared_music = 'empty'
                elif len([1 for e in self.entities if type(e) is underia3.ChaosDisciple]):
                    self.prepared_music = 'knight' if [e for e in self.entities if type(e) is underia3.ChaosDisciple][0].phase == 0 else 'knight_appears'
                elif len([1 for e in self.entities if type(e) in [entity.Entities.GodsEye]]):
                    self.prepared_music = 'wof_otherworld'
                elif len([1 for e in self.entities if type(e) in [entity.Entities.CLOCK, entity.Entities.MATTER]]):
                    self.prepared_music = 'boss_otherworld'
                else:
                    self.prepared_music = 'rude_buster'
                    if self.chapter > 1:
                        self.prepared_music = 'from_now_on'
            elif len([1 for e in self.entities if type(e) is underia3.ChaosDisciple and not e.IS_MENACE]):
                self.cur_music = None
                self.channel.stop()
                self.prepared_music = 'knight_appears'
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
            if self.cur_music in MUSIC_DATA and len(MUSIC_DATA[self.cur_music]):
                self.must_st = 0
                self.mus_text = (self.displayer.ffont.render(MUSIC_DATA[self.cur_music], True, (255, 255, 255)),
                                 self.displayer.font.render(MUSIC_DATA[self.cur_music], True, (0, 0, 0)))

        self.chunk_pos = (
        int(self.player.obj.pos[0]) // self.CHUNK_SIZE + 120, int(self.player.obj.pos[1]) // self.CHUNK_SIZE + 120)
        self.day_time += self.TIME_SPEED
        self.day_time %= 1.0
        if self.day_time - self.TIME_SPEED < 0.25 <= self.day_time:
            self.on_day_start()
        if self.day_time - self.TIME_SPEED < 0.85 <= self.day_time:
            self.on_day_end()
        self.on_update()
        self.c_dmg = 0
        self.handle_events()
        self.blend_map()
        for img, x, y, scale_req in self.decors:
            if self.displayer.canvas.get_rect().collidepoint(*resources.displayed_position((x, y))) and scale_req >= self.player.get_screen_scale():
                self.displayer.canvas.blit(pg.transform.scale_by(self.graphics.get_graphics(img),
                                                                     1 / self.player.get_screen_scale()),
                                           resources.displayed_position((x, y)))
        chunk_entities = {}
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
                    if not amount:
                        continue
                    k = random.randint(self.ITEM_SPLIT_MIN, min(self.ITEM_SPLIT_MAX, amount))
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
        for i, e in enumerate(self.entities):
            e.t_draw()
        self.displayer.night_darkness_color = self.get_night_color(self.day_time % 1.0)
        self.displayer.night_darkness()
        self.damage_texts = [(dmg, tick + 1, pos) for dmg, tick, pos in self.damage_texts if tick < 80]
        for dmg, tick, pos in self.damage_texts:
            ll = int(math.log(max(.01, int(dmg)), max(1.1, 1 + (1 + self.player.strike) ** 2))) % 2 == 1 if str.isdecimal(dmg) and int(dmg) > 0 else 1
            f = self.displayer.font_dmg.render(str(dmg), True, (255, 127, 0) if ll else (255, 0, 0))
            f.set_alpha(min(255.0, tick * tick / 2))
            fr = f.get_rect(center=resources.displayed_position((pos[0] + 2, pos[1] + (80 - tick) ** 3 // 4000 + 2)))
            self.displayer.canvas.blit(f, fr)
            f = self.displayer.font_dmg.render(str(dmg), True, (255, 0, 0) if ll else (255, 127, 0))
            f.set_alpha(min(255.0, tick * tick / 3))
            fr = f.get_rect(center=resources.displayed_position((pos[0], pos[1] + (80 - tick) ** 3 // 4000)))
            self.displayer.canvas.blit(f, fr)
        self.player.ui()
        menaces = [ee for ee in self.entities if ee.IS_MENACE]
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
                fill_uncoloured = (227, 105, 86)
                fill_coloured = (207, 255, 112)
                tt = math.sin(self.day_time * 1000)
                ct = math.cos(self.day_time * 1000)
                if 'CHAOS' in dir(menace):
                    fill_uncoloured = (tt * 120 + 127, tt * 120 + 127, tt * 120 + 127)
                    fill_coloured = (tt * -120 + 127, tt * -120 + 127, tt * -120 + 127)
                    border = (tt * 50 + 55, 0, ct * 50 + 55)
                if i >= c_phase:
                    pg.draw.circle(self.displayer.canvas, fill_coloured, (x - 580 + 50 * i, y - 100), 20)
                else:
                    pg.draw.circle(self.displayer.canvas, fill_uncoloured, (x - 580 + 50 * i, y - 100), 20)
                border = (242, 166, 94)
                pg.draw.circle(self.displayer.canvas, border, (x - 580 + 50 * i, y - 100), 20, width=8)
                t_p = menace.hp_sys.hp / menace.hp_sys.max_hp
                pc_p = menace.hp_sys.pacify / menace.hp_sys.max_hp
                pp_p = menace.hp_sys.pacify / (menace.hp_sys.max_hp - menace.hp_sys.hp) if menace.hp_sys.hp < menace.hp_sys.max_hp else 0
                t_l = 1200 - 50 * len(menace.PHASE_SEGMENTS) - 80
                sp = [0] + menace.PHASE_SEGMENTS + [1]
                sp_e = sp[-c_phase - 1]
                sp_s = sp[-c_phase - 2]
                r_p = ((menace.hp_sys.hp - sp_s * menace.hp_sys.max_hp) /
                       (sp_e * menace.hp_sys.max_hp - sp_s * menace.hp_sys.max_hp))
                pg.draw.rect(self.displayer.canvas, fill_uncoloured,
                             (x + 600 - t_l, y - 120, t_l, 40))
                pg.draw.rect(self.displayer.canvas, fill_coloured,
                             (x + 600 - t_l, y - 120, int(t_l * t_p), 40))
                pg.draw.rect(self.displayer.canvas, (0, 255, 255),
                             (x + 600 - int(t_l * pc_p), y - 120, int(t_l * pc_p), 40))
                pg.draw.rect(self.displayer.canvas, border,
                             (x + 600 - t_l, y - 120, t_l, 40), width=8, border_radius=3)
                tf = self.displayer.ffont.render(str(int(t_p * 100)) + '%', True, (0, 0, 0))
                tfr = tf.get_rect(midright=(x + 600 - 10, y - 100))
                self.displayer.canvas.blit(tf, tfr)
                tf = self.displayer.ffont.render(str(int(t_p * 100)) + '%', True, (255, 255, 255))
                tfr = tf.get_rect(midright=(x + 600 - 15, y - 105))
                self.displayer.canvas.blit(tf, tfr)
                pg.draw.rect(self.displayer.canvas, fill_uncoloured,
                             (x - 600, y - 50, 1200, 60))
                pg.draw.rect(self.displayer.canvas, fill_coloured,
                             (x - 600, y - 50, int(1200 * r_p), 60))
                pg.draw.rect(self.displayer.canvas, border,
                             (x - 600, y - 50, 1200, 60), width=8, border_radius=3)
                ft = self.displayer.font.render(f'{styles.text(menace.NAME)}' + (f'({int(menace.hp_sys.hp)}/{int(menace.hp_sys.max_hp)})' if not menace.hp_sys.IMMUNE else ''),
                                                True, (0, 0, 0))
                ftr = ft.get_rect(midright=(x + 560, y - 20))
                self.displayer.canvas.blit(ft, ftr)
            y -= 140
        if self.map_open:
            sf = pg.Surface((800, 800), pg.SRCALPHA)
            bg_size = 200 if self.dimension == 'overworld' else int(400 / self.player.get_screen_scale())
            chunk_size = 3
            bg_ax = int(self.player.ax / self.player.get_screen_scale()) % (bg_size * chunk_size)
            bg_ay = int(self.player.ay / self.player.get_screen_scale()) % (bg_size * chunk_size)
            stt = {}
            rf = []
            for i in range(-20, 20):
                for j in range(-20, 20):
                    try:
                        cx, cy = resources.real_position((i * 3 - bg_ax + bg_size // 2, j * 3 - bg_ay + bg_size // 2))
                        ps = ((cx + i * 3 * bg_size * self.player.get_screen_scale()) // self.CHUNK_SIZE + 120,
                              (cy + j * 3 * bg_size * self.player.get_screen_scale()) // self.CHUNK_SIZE + 120)
                        if ps in self.map_ns:
                            ll = self.get_biome(ps)
                            col = Game.YCOLS[ll]
                        elif i and not j and (i - 1, j) not in rf:
                            col = stt[(i - 1, j)]
                            rf.append((i, j))
                        elif not i and j and (i, j - 1) not in rf:
                            col = stt[(i, j - 1)]
                            rf.append((i, j))
                        elif i and j:
                            s1 = stt[(i, j - 1)] if (i, j - 1) not in rf else (0, 0, 0)
                            s2 = stt[(i - 1, j)] if (i - 1, j) not in rf else (0, 0, 0)
                            if s1 == (0, 0, 0):
                                rs = s2
                            elif s2 == (0, 0, 0):
                                rs = s1
                            else:
                                rs = random.choice([s1, s2])
                            col = rs
                            rf.append((i, j))
                        else:
                            col = (0, 0, 0)
                    except KeyError:
                        col = (0, 0, 0)
                    pg.draw.rect(sf, col, (i * 40 + 400, j * 40 + 400, 40, 40))
                    stt[(i, j)] = col
            if constants.USE_ALPHA:
                sf.set_alpha(200)
            self.displayer.canvas.blit(sf, (self.displayer.SCREEN_WIDTH // 2 - 400, self.displayer.SCREEN_HEIGHT // 2 - 400))
        if not self.player.in_ui:
            w = self.player.weapons[self.player.sel_weapon]
            im = self.graphics['items_' + inventory.ITEMS[w.name.replace(' ', '_')].img]
            im = pg.transform.scale(im, (64, 64))
            imr = im.get_rect(topright=self.displayer.reflect(*pg.mouse.get_pos()))
            self.displayer.canvas.blit(im, imr)
        if self.must_st != -1:
            self.must_st += 1
            ps = 0
            if self.must_st < 25:
                ps = (self.must_st - 25) * 10 - 5
            if self.must_st > 125:
                ps = (self.must_st - 125) * 10 + 5
            m1, m2 = self.mus_text
            m1.set_alpha(255 - abs(ps))
            m2.set_alpha(255 - abs(ps))
            rr = pg.Surface((self.displayer.canvas.get_width(), 200))
            rr.set_alpha(128 - abs(ps))
            self.displayer.canvas.blit(rr, (0, 100))
            m1r = m1.get_rect(center=(self.displayer.canvas.get_width() // 2, 200))
            m1r.x += ps * 3
            self.displayer.canvas.blit(m1, m1r)
            if self.must_st >= 150:
                self.must_st = -1
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
                    text = font.render('[T] for command', True, (255, 255, 255))
                    text_rect = text.get_rect(center=(window.get_rect().centerx,
                                                      window.get_rect().centery + 240))
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
                                elif ev.key == pg.K_t:
                                    cmd = ''
                                    qt = False
                                    shift = False
                                    while not qt:
                                        for ee in pg.event.get():
                                            if ee.type == pg.QUIT:
                                                raise resources.Interrupt()
                                            elif ee.type == pg.KEYDOWN:
                                                if ee.key == pg.K_BACKSPACE:
                                                    cmd = cmd[:-1] if len(cmd) > 0 else ''
                                                elif ee.key == pg.K_LSHIFT or ee.key == pg.K_RSHIFT:
                                                     shift = True
                                                elif ee.key == pg.K_RETURN:
                                                    qt = True
                                                    try:
                                                        cmd = str(eval(cmd))
                                                    except Exception as e:
                                                        cmd = str(e)
                                                else:
                                                    cc = pg.key.name(ee.key)
                                                    if cc == 'space':
                                                        cc = ' '
                                                    changes = {'1': '!', '2': '@', '3': '#', '4': '$', '5': '%', '6': '^', '7': '&', '8': '*', '9': '(', '0': ')', '-': '_', '=': '+', '[': '{', ']': '}', ';': ':', ',': '<', '.': '>', '/': '?'}
                                                    if shift:
                                                        if cc in changes:
                                                            cc = changes[cc]
                                                        else:
                                                            cc = cc.upper()
                                                    else:
                                                        cc = cc.lower()
                                                    cmd += cc
                                            elif ee.type == pg.KEYUP:
                                                 if ee.key == pg.K_LSHIFT or ee.key == pg.K_RSHIFT:
                                                     shift = False
                                        text = font.render(cmd, True, (255, 255, 255))
                                        pg.draw.rect(window, (0, 0, 0), (0, window.get_rect().centery + 300, window.get_width(), 40))
                                        text_rect = text.get_rect(center=(window.get_rect().centerx,
                                                                          window.get_rect().centery + 320))
                                        window.blit(text, text_rect)
                                        pg.display.flip()
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
        while True:
            self.update()
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
