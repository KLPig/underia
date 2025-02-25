import math
import random
import pygame as pg

from visual import effects
from resources import position
from underia import game
import constants


class Particle(effects.Effect):
    def __init__(self, x, y, init_radius, color, forward_speed, decay_speed, angle, g, follow_map):
        self.x = x
        self.y = y
        self.radius = init_radius
        self.color = color
        self.forward_speed = forward_speed
        self.decay_speed = decay_speed
        self.angle = angle
        self.vy = 0
        self.g = g
        self.ax = 0
        self.ay = 0
        self.t = init_radius / decay_speed
        if follow_map:
            xx, yy = position.real_position((0, 0))
            self.ax = -xx
            self.ay = -yy
        self.follow_map = follow_map
        self.tick = 0

    def update(self, window: pg.Surface):
        if self.follow_map:
            xx, yy = position.real_position((0, 0))
            nax = -xx
            nay = -yy
            self.x += (nax - self.ax) / game.get_game().player.get_screen_scale()
            self.y += (nay - self.ay) / game.get_game().player.get_screen_scale()
            self.ax = nax
            self.ay = nay
        self.x += self.forward_speed * math.cos(self.angle)
        self.y += self.forward_speed * math.sin(self.angle) + self.vy
        self.vy += self.g
        self.tick += 1
        self.radius -= int(self.decay_speed * (0.8 + 0.1 * self.tick))
        if self.radius <= 0:
            return False
        if constants.FADING_PARTICLE:
            sf = pg.Surface((self.radius * 2, self.radius * 2), pg.SRCALPHA)
            pg.draw.circle(sf, self.color, (self.radius, self.radius), self.radius)
            sf.set_alpha(max(0, int(255 * (1 - self.tick / self.t))))
            window.blit(sf, (int(self.x - self.radius), int(self.y - self.radius)))
        else:
            pg.draw.circle(window, self.color, (int(self.x), int(self.y)), int(self.radius))
        return True

def p_particle_effects(x, y, n=15, r=10, col=(255, 0, 0), sp=6, t=10, g=0.6, follow_map=True,
                       randomize=True, randomize_size=True):
    particles = []
    n = int(math.sqrt(n)) if constants.PARTICLES == 1 else 0 if constants.PARTICLES == 2 else n
    for i in range(n):
        angle = i * 2 * math.pi / n + randomize * random.uniform(-math.pi / 12, math.pi / 12)
        nr = r + randomize_size * random.uniform(-r / 10, r / 10)
        particles.append(Particle(x, y, nr, col, sp, nr / t, angle, g, follow_map))
    return particles
