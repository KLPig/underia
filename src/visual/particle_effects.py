import math

import pygame as pg

from src.visual import effects
from src.resources import position
from src import constants


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
        if follow_map:
            xx, yy = position.real_position((0, 0))
            self.ax = -xx
            self.ay = -yy
        self.follow_map = follow_map

    def update(self, window: pg.Surface):
        if self.follow_map:
            xx, yy = position.real_position((0, 0))
            nax = -xx
            nay = -yy
            self.x += nax - self.ax
            self.y += nay - self.ay
            self.ax = nax
            self.ay = nay
        self.x += self.forward_speed * math.cos(self.angle)
        self.y += self.forward_speed * math.sin(self.angle) + self.vy
        self.vy += self.g
        self.radius -= self.decay_speed
        if self.radius <= 0:
            return False
        pg.draw.circle(window, self.color, (int(self.x), int(self.y)), int(self.radius))
        return True


def p_particle_effects(x, y, n=15, r=10, col=(255, 0, 0), sp=6, t=10, g=0.6, follow_map=True):
    particles = []
    n = int(math.sqrt(n)) if constants.PARTICLES == 1 else 0 if constants.PARTICLES == 2 else n
    for i in range(n):
        angle = i * 2 * math.pi / n
        particles.append(Particle(x, y, r, col, sp, r / t, angle, g, follow_map))
    return particles
