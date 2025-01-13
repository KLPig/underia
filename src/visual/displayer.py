import copy

import pygame as pg

from src import pygame_lights
from src.resources import position
from src.underia import game, weapons
from src.visual import effects
from src import constants


class Displayer:
    SCREEN_WIDTH = 2400
    SCREEN_HEIGHT = 1350

    def __init__(self):
        try:
            pg.display.set_mode((4800, 2700), pg.RESIZABLE | pg.HWSURFACE | pg.DOUBLEBUF | pg.FULLSCREEN | pg.SCALED)
        except pg.error:
            pass
        self.canvas = pg.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pg.SRCALPHA | pg.HWACCEL)
        self.canvas.fill((255, 255, 255, 255))
        self.alpha_masks: list[tuple[int, int, int, int]] = []
        self.shake_x, self.shake_y = 0, 0
        self.effects: list[effects.Effect] = []
        font = 'dtm-sans'#'Hiragino Sans GB'
        self.font = pg.font.SysFont(font, 32)
        self.font_s = pg.font.SysFont(font, 20)
        self.night_darkness_color = (127, 127, 0)
        self.lsw, self.lsh = 1600, 900

    def update(self):
        window = pg.display.get_surface()
        for effect in self.effects:
            if not effect.update(self.canvas):
                self.effects.remove(effect)
        scale = min(window.get_width() / self.SCREEN_WIDTH, window.get_height() / self.SCREEN_HEIGHT)
        for alpha_mask in self.alpha_masks:
            self.canvas.fill(alpha_mask)
        self.alpha_masks.clear()
        blit_surface = pg.transform.scale(copy.copy(self.canvas),
                                          (int(self.SCREEN_WIDTH * scale), int(self.SCREEN_HEIGHT * scale)))
        rect = blit_surface.get_rect(center=(window.get_width() // 2, window.get_height() // 2))
        rect.x += self.shake_x
        rect.y += self.shake_y
        self.shake_x, self.shake_y = 0, 0
        window.fill((0, 0, 0))
        window.blit(blit_surface, rect)
        self.canvas.fill((255, 255, 255, 255))
        self.canvas.set_alpha(255)
        # self.SCREEN_WIDTH = int(1600 * game.get_game().player.get_screen_scale())
        # self.SCREEN_HEIGHT = int(900 * game.get_game().player.get_screen_scale())
        if self.lsw != self.SCREEN_WIDTH or self.lsh != self.SCREEN_HEIGHT:
            self.lsw, self.lsh = self.SCREEN_WIDTH, self.SCREEN_HEIGHT
            self.canvas = pg.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pg.SRCALPHA)

    def reflect(self, window_x: float, window_y: float) -> tuple[int, int]:
        window = pg.display.get_surface()
        scale_x = self.SCREEN_WIDTH / window.get_width()
        scale_y = self.SCREEN_HEIGHT / window.get_height()

        canvas_x = int(window_x * scale_x)
        canvas_y = int(window_y * scale_y)

        return canvas_x, canvas_y

    def night_darkness(self):
        if not constants.LIGHTING:
            pg.display.update()
            return
        filter = pg.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pg.SRCALPHA)
        player = game.get_game().player
        if player.weapons[player.sel_weapon] is not weapons.WEAPONS['true_nights_edge']:
            filter.fill(self.night_darkness_color)
        else:
            filter.fill((50, 0, 50))
        if game.get_game().day_time > 0.75 or game.get_game().day_time < 0.4:
            lv = game.get_game().player.get_light_level()
            px, py = position.displayed_position(game.get_game().player.obj.pos)
            if lv:
                filter.blit(
                    pygame_lights.global_light(filter.get_size(), 50 + game.get_game().player.get_night_vision()),
                    (0, 0))

                light = pygame_lights.LIGHT(lv * 150, pygame_lights.pixel_shader(lv * 150,
                                                                                 (255, 127, 0) if player.weapons[
                                                                                                      player.sel_weapon] is not
                                                                                                  weapons.WEAPONS[
                                                                                                      'nights_edge'] and
                                                                                                  player.weapons[
                                                                                                      player.sel_weapon] is not
                                                                                                  weapons.WEAPONS[
                                                                                                      'true_nights_edge'] else (
                                                                                 127, 0, 127), 1, False))
                light.main([], filter, px, py)
        self.canvas.blit(filter, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
        pg.display.update()

    def effect(self, effect_list):
        self.effects.extend(effect_list)
