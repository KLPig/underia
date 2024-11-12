import pygame as pg
import math
from src.visual import effects

class Particle(effects.Effect):
    def __init__(self, x, y, init_radius, color, forward_speed, decay_speed, angle, g):
        self.x = x
        self.y = y
        self.radius = init_radius
        self.color = color
        self.forward_speed = forward_speed
        self.decay_speed = decay_speed
        self.angle = angle
        self.vy = 0
        self.g = g

    def update(self, window: pg.Surface):
        self.x += self.forward_speed * math.cos(self.angle)
        self.y += self.forward_speed * math.sin(self.angle) + self.vy
        self.vy += self.g
        self.radius -= self.decay_speed
        if self.radius <= 0:
            return False
        pg.draw.circle(window, self.color, (int(self.x), int(self.y)), int(self.radius))
        return True

def particle_effects(x, y, n=15, r=10, col=(255, 0, 0), sp=6, t=10, g=0.6):
    particles = []
    for i in range(n):
        angle = i * 2 * math.pi / n
        particles.append(Particle(x, y, r, col, sp, r / t, angle, g))
    return particles

