import pygame as pg

from resources import position, path
from underia import game
from visual import effects, lighting
import constants


class Displayer:
    SCREEN_WIDTH = 2400
    SCREEN_HEIGHT = 1350

    def __init__(self):
        try:
            if constants.WEB_DEPLOY:
                pg.display.set_mode((4800, 2700))
            else:
                pg.display.set_mode((4800, 2700), pg.RESIZABLE | pg.HWSURFACE | pg.DOUBLEBUF | pg.SCALED)
        except pg.error:
            pass
        self.canvas = pg.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pg.SRCALPHA | pg.HWACCEL)
        self.canvas.fill((255, 255, 255, 255))
        self.alpha_masks: list[tuple[int, int, int, int]] = []
        self.shake_x, self.shake_y = 0, 0
        self.effects: list[effects.Effect] = []
        font = path.get_path('assets/dtm-sans.otf' if constants.LANG != 'zh' else 'assets/fz-pixel.ttf')
        self.font = pg.font.Font(font, 32)
        self.ffont = pg.font.Font(font, 72)
        self.ffont.set_italic(True)
        self.font_mono = pg.font.Font(path.get_path('assets/dtm-mono.otf' if constants.LANG != 'zh' else 'assets/fz-pixel.ttf'), 36)
        self.font_mono.set_italic(True)
        self.font_dmg = pg.font.Font(path.get_path('assets/papyrus.ttf'), 36)
        self.font_dmg.set_italic(True)
        self.font_dmg.set_bold(True)
        self.font_s = pg.font.Font(font, 20)
        self.night_darkness_color = (127, 127, 0)
        self.lsw, self.lsh = 1600, 900
        self.blit_pos = (0, 0)
        self.light_engine = lighting.LightingEngine(*self.canvas.get_size(), resolution_factor=.1)

    def update(self):
        window = pg.display.get_surface()
        for effect in self.effects:
            if not effect.update(self.canvas):
                self.effects.remove(effect)
        scale = min(window.get_width() / self.SCREEN_WIDTH, window.get_height() / self.SCREEN_HEIGHT)
        for alpha_mask in self.alpha_masks:
            self.canvas.fill(alpha_mask)
        self.alpha_masks.clear()
        blit_surface = pg.transform.scale(self.canvas,
                                          (int(self.SCREEN_WIDTH * scale), int(self.SCREEN_HEIGHT * scale)))
        rect = blit_surface.get_rect(center=(window.get_width() // 2, window.get_height() // 2))
        self.blit_pos = rect.topleft
        rect.x += self.shake_x
        rect.y += self.shake_y
        self.shake_x, self.shake_y = 0, 0
        window.fill((0, 0, 0))
        window.blit(blit_surface, rect)
        self.canvas.fill((255, 255, 255))
        if self.lsw != self.SCREEN_WIDTH or self.lsh != self.SCREEN_HEIGHT:
            self.lsw, self.lsh = self.SCREEN_WIDTH, self.SCREEN_HEIGHT
            self.canvas = pg.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pg.SRCALPHA)

    def reflect(self, window_x: float, window_y: float) -> tuple[int, int]:
        window = pg.display.get_surface()
        scale = min(window.get_width() / self.SCREEN_WIDTH,
                    window.get_height() / self.SCREEN_HEIGHT)
        canvas_x = int((window_x - self.blit_pos[0]) / scale)
        canvas_y = int((window_y - self.blit_pos[1]) / scale)
        return canvas_x, canvas_y

    def night_darkness(self):
        if not constants.LIGHTING:
            pg.display.update()
            return
        if not game.get_game().player.afterimage_shadow:
            self.light_engine.point_light(game.get_game().player.profile.get_color(),
                                          position.displayed_position(game.get_game().player.obj.pos),
                                          300 / game.get_game().player.get_screen_scale(),
                                          0.5)
        self.light_engine.update(self.canvas)
        self.light_engine.clear()
        r, g, b = self.night_darkness_color
        sr, sg, sb, sa = self.light_engine.ambient_light
        self.light_engine.ambient_light = ((r + sr * 4) // 5, (g + sg * 4) // 5, (b + sb * 4) // 5, sa)

    def add_blocking(self, rect: pg.Rect):
        if not constants.LIGHTING:
            return
        self.light_engine.hull(rect)

    def point_light(self, color, pos, power, size=5):
        if not constants.LIGHTING:
            return
        self.light_engine.point_light(color, pos, size * 2, power / 5)

    def effect(self, effect_list):
        self.effects.extend(effect_list)
