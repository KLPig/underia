import pygame as pg

from visual import effects, particle_effects
from resources import position
from underia import game


class FadeCircle(effects.Effect):
    def __init__(self, x, y, decay_speed, time, col, follow_map):
        self.x = x
        self.y = y
        self.time = time
        self.decay_speed = decay_speed
        self.sz = 0
        self.col = col
        self.ax, self.ay = position.real_position((x, y))
        self.follow_map = follow_map

    def update(self, window: pg.Surface):
        if self.follow_map:
            self.x, self.y = position.displayed_position((self.ax, self.ay))
        scale = game.get_game().player.get_screen_scale()
        self.sz += self.decay_speed
        nsz = self.sz / scale
        sf = pg.Surface((nsz, nsz), pg.SRCALPHA)
        pg.draw.circle(sf, self.col, (nsz // 2, nsz // 2), nsz // 2)
        sf.set_alpha(int(255 * (1 - self.sz / (1 + self.time * self.decay_speed))))
        window.blit(sf, (self.x - nsz // 2, self.y - nsz // 2))
        return self.sz <= self.time * self.decay_speed


def p_fade_circle(x, y, col=(255, 0, 0), sp=6, t=10, follow_map=True):
    return [FadeCircle(x, y, sp, t, col, follow_map), particle_effects.CircularLighter(x, y, sp, col, 20, t)]
