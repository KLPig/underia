from src.physics import mover, vector
from src.underia import game
from src.values import hp_system
import pygame as pg

class PlayerObject(mover.Mover):
    MASS = 60
    FRICTION = 0.9

    def on_update(self):
        keys = game.get_game().get_pressed_keys()
        if pg.K_UP in keys:
            self.apply_force(vector.Vector(0, 20))
        elif pg.K_DOWN in keys:
            self.apply_force(vector.Vector(180, 20))
        if pg.K_LEFT in keys:
            self.apply_force(vector.Vector(270, 20))
        elif pg.K_RIGHT in keys:
            self.apply_force(vector.Vector(90, 20))

class Player:
    def __init__(self):
        self.obj = PlayerObject((400, 300))
        self.hp_sys = hp_system.HPSystem(5000)
        self.ax, self.ay = 0, 0

    def update(self):
        displayer = game.get_game().displayer
        self.obj.update()
        self.ax, self.ay = self.obj.pos
        self.ax -= displayer.SCREEN_WIDTH // 2
        self.ay -= displayer.SCREEN_HEIGHT // 2
        pg.draw.circle(displayer.canvas, (255, 0, 0), (self.obj.pos[0] - self.ax, self.obj.pos[1] - self.ay), 10)
        self.hp_sys.update()
