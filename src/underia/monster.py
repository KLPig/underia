from src.physics import mover, vector
from src.underia import game
from src.values import hp_system
import pygame as pg

class MonsterAI(mover.Mover):
    MASS = 80
    FRICTION = 0.95

    def on_update(self):
        player = game.get_game().player
        px = player.obj.pos[0] - self.pos[0]
        py = player.obj.pos[1] - self.pos[1]
        self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 20))

class Monsters:
    class Monster:
        def __init__(self, pos):
            self.obj = MonsterAI(pos)
            self.hp_sys = hp_system.HPSystem(500)

        def update(self):
            displayer = game.get_game().displayer
            ax, ay = game.get_game().player.ax, game.get_game().player.ay
            self.obj.update()
            self.hp_sys.update()
            pg.draw.circle(displayer.canvas, (0, 0, 255), (self.obj.pos[0] - ax, self.obj.pos[1] - ay), 10)

    class Test(Monster):
        pass