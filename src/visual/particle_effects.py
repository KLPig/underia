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
            sf = pg.Surface((int(self.radius * 1.5), int(self.radius * 1.5)), pg.SRCALPHA)
            #pg.draw.circle(sf, self.color, (self.radius, self.radius), self.radius)
            sf.fill(self.color)
            sf.set_alpha(max(0, int(255 * (1 - self.tick / self.t))))
            window.blit(sf, (int(self.x - self.radius), int(self.y - self.radius)))
        else:
            pg.draw.circle(window, self.color, (int(self.x), int(self.y)), int(self.radius))
        return True

class CircularLighter(effects.Effect):
    def __init__(self, x, y, speed, color, pr, t, g=0.6, follow_map=True):
        self.x = x
        self.y = y
        self.speed = speed
        self.color = color
        self.radius = 0
        self.g = g
        self.follow_map = follow_map
        self.tick = 0
        self.vy = 0
        if follow_map:
            xx, yy = position.real_position((0, 0))
            self.ax = -xx
            self.ay = -yy
        self.angle = 0
        self.t = t
        self.pr = pr

    def update(self, window: pg.Surface):
        if self.follow_map:
            xx, yy = position.real_position((0, 0))
            nax = -xx
            nay = -yy
            self.x += (nax - self.ax) / game.get_game().player.get_screen_scale()
            self.y += (nay - self.ay) / game.get_game().player.get_screen_scale()
            self.ax = nax
            self.ay = nay
        self.y += self.vy
        self.vy += self.g
        self.tick += 1
        self.radius += self.speed
        if self.tick >= self.t:
            return False
        game.get_game().displayer.point_light(self.color, (self.x, self.y),
                                              self.pr / 40 * (self.t - self.tick) / self.t,
                                              self.radius * 1.1)
        return True


def p_particle_effects(x, y, n=15, r=10, col=(255, 0, 0), sp=6, t=10, g=0.6, follow_map=True,
                       randomize=True, randomize_size=True):
    particles = []
    n = int(math.sqrt(n)) if constants.PARTICLES == 1 else 0 if constants.PARTICLES == 2 else n
    ar = random.uniform(0, 2 * math.pi) if randomize else 0
    for i in range(n):
        angle = i * 2 * math.pi / n + randomize * random.uniform(-math.pi / 12, math.pi / 12) + ar
        nr = r + randomize_size * random.uniform(-r / 10, r / 10)
        particles.append(Particle(x, y, nr, col, sp, nr / t, angle, g, follow_map))
    return particles + [CircularLighter(x, y, sp, col, r, t, g, follow_map)]
