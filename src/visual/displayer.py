import pygame as pg
import copy
from src.visual import effects

class Displayer:
    SCREEN_WIDTH = 1600
    SCREEN_HEIGHT = 900

    def __init__(self):
        pg.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pg.RESIZABLE | pg.DOUBLEBUF | pg.HWSURFACE | pg.SCALED)
        self.canvas = pg.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pg.SRCALPHA)
        self.canvas.fill((255, 255, 255, 255))
        self.alpha_masks: list[tuple[int, int, int, int]] = []
        self.shake_x, self.shake_y = 0, 0
        self.effects: list[effects.Effect] = []

    def update(self):
        window = pg.display.get_surface()
        for effect in self.effects:
            if not effect.update(self.canvas):
                self.effects.remove(effect)
        scale = min(window.get_width() / self.SCREEN_WIDTH, window.get_height() / self.SCREEN_HEIGHT)
        for alpha_mask in self.alpha_masks:
            self.canvas.fill(alpha_mask)
        self.alpha_masks.clear()
        blit_surface = pg.transform.scale(copy.copy(self.canvas), (int(self.SCREEN_WIDTH * scale), int(self.SCREEN_HEIGHT * scale)))
        rect = blit_surface.get_rect(center=window.get_rect().center)
        rect.x += self.shake_x
        rect.y += self.shake_y
        self.shake_x, self.shake_y = 0, 0
        window.blit(blit_surface, rect)
        self.canvas.fill((255, 255, 255, 255))
        pg.display.update()

    def effect(self, effect_list):
        self.effects.extend(effect_list)
