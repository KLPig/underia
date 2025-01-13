import copy
import math
import random

import pygame as pg

from src.physics import mover, vector
from src.resources import position
from src.underia import game, styles, inventory
from src.values import hp_system, damages, effects
from src import constants


class Loots:
    def __call__(self):
        return []

    def get_all_items(self):
        return []


class IndividualLoot(Loots):
    def __init__(self, item, chance, amount_min, amount_max):
        self.item = item
        self.chance = chance
        self.amount_min = amount_min
        self.amount_max = amount_max

    def __call__(self):
        if random.randint(0, 10000) / 10000 < self.chance:
            return [(self.item, random.randint(self.amount_min, self.amount_max))]
        else:
            return []

    def get_all_items(self):
        return [self.item]


class SelectionLoot(Loots):
    def __init__(self, items: list[tuple[str, int, int]], selection_min, selection_max):
        self.items = items
        self.selection_min = selection_min
        self.selection_max = selection_max

    def __call__(self):
        selection_size = random.randint(self.selection_min, self.selection_max)
        return [(item, random.randint(rmin, rmax)) for item, rmin, rmax in random.choices(self.items, k=selection_size)]

    def get_all_items(self):
        return [item for item, _, _ in self.items]


class LootTable:
    def __init__(self, loot_list: list[Loots]):
        self.loot_list = loot_list

    def __call__(self):
        loot_items = []
        for loot in self.loot_list:
            loot_items.extend(loot())
        return loot_items

    def get_all_items(self):
        all_items = []
        for loot in self.loot_list:
            all_items.extend(loot.get_all_items())
        return all_items


class MonsterAI(mover.Mover):
    MASS = 120
    FRICTION = 0.95
    TOUCHING_DAMAGE = 10
    PREFER_DISTANCE = 1.5

    IDLE_TIME = 100
    IDLE_SPEED = 120
    IDLE_CHANGER = 50

    def __init__(self, pos):
        super().__init__(pos)
        self.touched_player = False
        self.cur_target = None
        self.idle_timer = 0
        self.idle_rotation = 0

    def update(self):
        super().update()
        self.get_target()

    def idle(self):
        if self.idle_timer > self.IDLE_TIME + random.randint(-50, 50):
            self.idle_timer = 0
            self.idle_rotation = (self.idle_rotation + random.randint(-self.IDLE_CHANGER, self.IDLE_CHANGER)) % 360
        self.apply_force(vector.Vector(self.idle_rotation, self.IDLE_SPEED))

    def get_target(self):
        es = game.get_game().get_player_objects()
        if self.cur_target not in es:
            self.cur_target = None
        d = constants.INFINITY if self.cur_target is None else vector.distance(self.pos[0] - self.cur_target.pos[0],
                                                                               self.pos[1] - self.cur_target.pos[1])
        for e in es:
            if e is not self.cur_target:
                new_d = vector.distance(self.pos[0] - e.pos[0], self.pos[1] - e.pos[1])
                if new_d * self.PREFER_DISTANCE < d:
                    self.cur_target = e
                    d = new_d


    def on_update(self):
        pass


class TreeMonsterAI(MonsterAI):
    MASS = 200
    FRICTION = 0.8

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            if vector.distance(px, py) < 500:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 120))


class CactusAI(TreeMonsterAI):
    TOUCHING_DAMAGE = 30


class EyeAI(MonsterAI):
    MASS = 60
    FRICTION = 0.96
    TOUCHING_DAMAGE = 16

    def __init__(self, pos):
        super().__init__(pos)
        self.timer = 0

    def on_update(self):
        self.timer = (self.timer + 1) % 240
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            if self.touched_player:
                self.timer = -100
            if self.timer < 110:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py) + 180, 12))
            elif self.timer < 190:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 24))
            elif self.timer < 195:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 100))
        else:
            self.idle()


class SlowMoverAI(MonsterAI):
    MASS = 200
    FRICTION = 0.8

    IDLE_TIME = 120
    IDLE_SPEED = 100

    def __init__(self, pos):
        super().__init__(pos)
        self.idle_timer = 0
        self.idle_rotation = 0

    def on_update(self):
        player = game.get_game().player
        px = player.obj.pos[0] - self.pos[0]
        py = player.obj.pos[1] - self.pos[1]
        if vector.distance(px, py) < 500:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 120))
        else:
            self.idle_timer += 1
            if self.idle_timer > random.randint(50, 200):
                self.idle_timer = 0
                self.idle_rotation = (self.idle_rotation + random.randint(-50, 50)) % 360
            self.apply_force(vector.Vector(self.idle_rotation, 100))


class MagmaCubeAI(SlowMoverAI):
    TOUCHING_DAMAGE = 32


class CloseBloodflowerAI(SlowMoverAI):
    MASS = 240
    TOUCHING_DAMAGE = 12


class BloodflowerAI(CloseBloodflowerAI):
    FRICTION = 0.97
    TOUCHING_DAMAGE = 22

    def __init__(self, pos):
        super().__init__(pos)
        self.timer = 0

    def on_update(self):
        player = self.cur_target
        self.timer += 1
        if self.timer > 100:
            self.timer = 0
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            if vector.distance(px, py) < 800:
                if self.timer > 20:
                    self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 120))
                if self.touched_player:
                    self.timer = 0
            else:
                self.idle()
        else:
            self.idle()


class SoulFlowerAI(BloodflowerAI):
    TOUCHING_DAMAGE = 68

class SnowDrakeAI(BloodflowerAI):
    TOUCHING_DAMAGE = 128
    MASS = 220

class CellsAI(EyeAI):
    TOUCHING_DAMAGE = 89
    MASS = 720

    IDLE_SPEED = 400

    def on_update(self):
        self.timer = (self.timer + 1) % 240
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            if self.touched_player:
                self.timer = -50
            if self.timer < 50:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py) + 180, 150))
            elif self.timer < 160:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 320))
            elif self.timer < 195:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 1500))
        else:
            self.idle()

class IceCapAI(SlowMoverAI):
    MASS = 200
    TOUCHING_DAMAGE = 148

class MechanicEyeAI(CellsAI):
    MASS = 200
    TOUCHING_DAMAGE = 65

    IDLE_SPEED = 600

    def on_update(self):
        self.timer += 1
        if self.timer > 30:
            self.timer = 0
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            if self.touched_player:
                self.timer = -20
            if self.timer < 0:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), -300))
            if vector.distance(px, py) > 1200:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 120))
            if 0 <= self.timer < 10:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 800))
        else:
            self.idle()


class RedWatcherAI(SlowMoverAI):
    FRICTION = 0.92
    MASS = 400
    TOUCHING_DAMAGE = 28


class RuneRockAI(SlowMoverAI):
    MASS = 240
    FRICTION = 0.9
    TOUCHING_DAMAGE = 56


class BuildingAI(MonsterAI):
    MASS = 2000
    FRICTION = 0.5
    TOUCHING_DAMAGE = 0


class AbyssEyeAI(BuildingAI):
    MASS = 6000
    FRICTION = 0.1
    TOUCHING_DAMAGE = 60


class TrueEyeAI(MonsterAI):
    MASS = 300
    FRICTION = 0.97
    TOUCHING_DAMAGE = 45

    def __init__(self, pos):
        super().__init__(pos)
        self.timer = 0

    def on_update(self):
        self.timer = (self.timer + 1) % 350
        player = game.get_game().player
        px = player.obj.pos[0] - self.pos[0]
        py = player.obj.pos[1] - self.pos[1]
        if self.timer < 100:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py) + 180, 20))
        elif self.timer < 200:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 120))
        elif self.timer % 50 < 12:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 3000))


class StarAI(MonsterAI):
    FRICTION = 1
    MASS = 200

    PREFER_DISTANCE = 1

    IDLE_SPEED = 60

    def __init__(self, pos):
        super().__init__(pos)
        self.idle_timer = 0
        self.idle_rotation = 0

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            if vector.distance(px, py) < 1200:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 40))
            else:
                self.idle()
        else:
            self.idle()


class LeafAI(StarAI):
    MASS = 320
    TOUCHING_DAMAGE = 120


class MagmaKingAI(MonsterAI):
    FRICTION = 0.9
    MASS = 360
    TOUCHING_DAMAGE = 65

    IDLE_SPEED = 500

    def __init__(self, pos):
        super().__init__(pos)
        self.timer = 0
        self.state = 0

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            if self.state == 0:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 450))
            elif self.state == 1:
                if self.timer % 40 < 5:
                    self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 5000))
            else:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), -200))
            if self.timer > random.randint(50, 200):
                self.state = (self.state + 1) % 3
                self.timer = 0
            self.timer += 1


class SandStormAI(MonsterAI):
    FRICTION = 1
    MASS = 50
    TOUCHING_DAMAGE = 180

    def __init__(self, pos):
        super().__init__(pos)
        self.rot = 0
        self.d = 240
        self.tick = 0
        self.state = 0

    def on_update(self):
        if self.tick == 300:
            self.state = (self.state + 1) % 3
            self.tick = 0
        self.tick += 1
        if self.state == 0:
            self.rot = (self.rot + .5) % 360
            self.d = 240 + abs(self.tick % 200 - 100) * 6
        elif self.state == 1:
            self.rot = (self.rot + 6) % 360
            if self.d > 180:
                self.d -= 20
        else:
            self.rot = (self.rot + 13) % 360
            if self.d < 600:
                self.d += 20
        pos = self.cur_target.pos if self.cur_target is not None else (0, 0)
        ax, ay = vector.rotation_coordinate(self.rot)
        px, py = pos[0] + ax * self.d, pos[1] + ay * self.d
        self.pos = ((self.pos[0] + px * 5) // 6, (self.pos[1] + py * 5) // 6)


class AbyssRuneAI(MonsterAI):
    FRICTION = 0.9
    MASS = 100
    TOUCHING_DAMAGE = 100

    def __init__(self, pos):
        super().__init__(pos)
        self.rot = 0
        self.d = 240
        self.tick = 0
        self.state = 0
        self.ar = 6

    def on_update(self):
        self.rot = (self.rot + self.ar) % 360
        e = [e for e in game.get_game().entities if type(e) is Entities.AbyssEye]
        if not len(e):
            return
        self.pos = e[0].obj.pos
        ax, ay = vector.rotation_coordinate(self.rot)
        self.pos = (self.pos[0] + ax * self.d, self.pos[1] + ay * self.d)


class MagmaKingFireballAI(MonsterAI):
    FRICTION = 1
    MASS = 50
    TOUCHING_DAMAGE = 0
    IS_OBJECT = False

    def __init__(self, pos):
        super().__init__(pos)
        self.rot = 0

    def on_update(self):
        self.apply_force(vector.Vector(self.rot, 20))


class AbyssRuneShootAI(MonsterAI):
    FRICTION = 1
    MASS = 5000
    TOUCHING_DAMAGE = 0
    IS_OBJECT = False

    def __init__(self, pos):
        super().__init__(pos)
        self.rot = 0

    def on_update(self):
        self.apply_force(vector.Vector(self.rot, 2000))

class FastBulletAI(MonsterAI):
    FRICTION = 1
    MASS = 100
    TOUCHING_DAMAGE = 0
    IS_OBJECT = False

    def __init__(self, pos):
        super().__init__(pos)
        self.rot = 0
        self.speed = 1000

    def on_update(self):
        self.apply_force(vector.Vector(self.rot, self.speed))


class FaithlessEyeAI(MonsterAI):
    FRICTION = 0.9
    MASS = 800
    TOUCHING_DAMAGE = 100

    PREFER_DISTANCE = 2

    def __init__(self, pos):
        super().__init__(pos)
        self.rot = 0
        self.tick = 0
        self.state = 0
        self.ax = -1000
        self.ay = 0
        self.phase = 1

    def on_update(self):
        if self.tick > 320:
            self.state = (self.state + 1) % 2
            self.tick = 0
        self.tick += 1
        px, py = self.cur_target.pos if self.cur_target is not None else (0, 0)
        if self.state == 0:
            if self.tick % (100 - 20 * self.phase) < 30:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px - self.pos[0], py - self.pos[1]),
                                               4000 + self.phase * 2000))
        else:
            tar_x, tar_y = px + self.ax, py + self.ay
            self.apply_force(vector.Vector(vector.coordinate_rotation(tar_x - self.pos[0], tar_y - self.pos[1]),
                                           vector.distance(tar_x - self.pos[0], tar_y - self.pos[1]) * 5))
            self.rot = vector.coordinate_rotation(px - self.pos[0], py - self.pos[1])


class DestroyerAI(SlowMoverAI):
    MASS = 7200
    FRICTION = 0.9
    TOUCHING_DAMAGE = 220

    PREFER_DISTANCE = 1

    def __init__(self, pos):
        super().__init__(pos)
        self.tick = 0
        self.state = 0

    def on_update(self):
        player = self.cur_target.pos if self.cur_target is not None else (0, 0)
        px = player[0] - self.pos[0]
        py = player[1] - self.pos[1]
        if self.tick > 200:
            self.state = (self.state + 1) % 2
            self.tick = 0
        self.tick += 1
        if self.state == 0:
            self.apply_force(
                vector.Vector(vector.coordinate_rotation(px, py), 8000 + min(vector.distance(px, py) * 9, 22000)))
        else:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), vector.distance(px, py) * 45))


class DevilPythonAI(DestroyerAI):
    MASS = 8000
    FRICTION = 0.9
    TOUCHING_DAMAGE = 320

    PREFER_DISTANCE = 3

    def __init__(self, pos):
        super().__init__(pos)
        self.tick = 0
        self.state = 0
        self.rot = 0
        self.tp = 0, 0

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            if self.tick > 200:
                self.state = (self.state + 1) % 2
                self.tick = 0
                self.rot = random.randint(0, 360)
            self.tick += 1
            if self.state == 0:
                self.rot += 3
                ax, ay = vector.rotation_coordinate(self.rot)
                px += ax * 1000
                py += ay * 1000
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), vector.distance(px, py) * 100))
            else:
                if self.tick % 80 == 1:
                    self.rot = vector.coordinate_rotation(px, py)
                elif self.tick % 80 < 50:
                    self.apply_force(vector.Vector(self.rot, 150000))

class JevilAI(SlowMoverAI):
    MASS = 1000
    FRICTION = 0.9
    TOUCHING_DAMAGE = 250

    IDLE_SPEED = 1500

    def __init__(self, pos):
        super().__init__(pos)
        self.tick = 0
        self.state = 0
        self.phase = 1
        self.ax, self.ay = 1, 0

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            if self.tick < 0:
                self.tick += 1
                return
            self.tick += 1
            if self.tick > 50:
                self.state = (self.state + 1) % 8
                self.tick = 0
                self.ax, self.ay = vector.rotation_coordinate(random.randint(0, 360))
                if self.state % 2 == 0:
                    self.pos = (px + self.pos[0] + self.ax * 600, py + self.pos[1] + self.ay * 600)
                if self.state == 1:
                    if random.randint(0, 1):
                        game.get_game().play_sound('chaos_chaos', 0.99 ** int(vector.distance(px, py) / 10))
                    else:
                        game.get_game().play_sound('i_can_do_anything', 0.99 ** int(vector.distance(px, py) / 10))
            if self.state % 2 == 0:
                px += self.ax * 600
                py += self.ay * 600
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), vector.distance(px, py) * 10))
            else:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 4000))
        else:
            self.tick += 1
            if self.tick > 50:
                self.tick = 0
            self.idle()

class PlanteraAI(SlowMoverAI):
    MASS = 1000
    FRICTION = 0.9
    TOUCHING_DAMAGE = 250

    def __init__(self, pos):
        super().__init__(pos)
        self.tick = 50
        self.state = 0
        self.rot = 0
        self.phase = 1

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px, py = player.pos[0] - self.pos[0], player.pos[1] - self.pos[1]
            self.tick += 1
            if self.tick > 40:
                self.state = (self.state + 1) % 6
                self.tick = 0
                if self.state < 5:
                    self.rot = vector.coordinate_rotation(px, py)
                    self.apply_force(vector.Vector(self.rot, 20000 + 20000 * self.phase))
            if self.state < 5:
                self.apply_force(vector.Vector(self.rot, 2000 * self.phase - 1800))

class GhostFaceAI(SlowMoverAI):
    MASS = 1000
    FRICTION = 0.9
    TOUCHING_DAMAGE = 440

    def __init__(self, pos):
        super().__init__(pos)
        self.tick = 0
        self.appear_time = 50
        self.appear_rate = 3

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            if vector.distance(px, py) < 2000:
                self.tick += 1
                if self.tick > self.appear_rate:
                    self.tick = 0
                    self.pos = (self.pos[0] + px // self.appear_rate, self.pos[1] + py // self.appear_rate)

class JevilKnifeAI(SlowMoverAI):
    MASS = 1000
    FRICTION = 0.95
    TOUCHING_DAMAGE = 320

    def __init__(self, pos):
        super().__init__(pos)
        self.r = 0
        self.d = 0
        self.upper = None

    def on_update(self):
        self.r = (self.r + 4) % 360
        self.d = (self.d + 1) % 240
        pos = self.upper.cur_target.pos if self.upper.cur_target is not None else (0, 0)
        px = pos[0] - self.pos[0] + ((math.cos(self.d / 120 * math.pi) + 1) * 500 + 500) * math.cos(math.radians(self.r))
        py = pos[1] - self.pos[1] + ((math.cos(self.d / 120 * math.pi) + 1) * 500 + 500) * math.sin(math.radians(self.r))
        self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), vector.distance(px, py) * 50))


class TheCPUAI(SlowMoverAI):
    MASS = 10000
    FRICTION = 0.95
    TOUCHING_DAMAGE = 130

    def __init__(self, pos):
        super().__init__(pos)
        self.tick = 0
        self.state = 0
        self.phase = 1

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            if self.tick < 0:
                self.tick += 1
                return
            if self.tick > 100:
                self.state = (self.state + 1) % 2
                self.tick = 0
                if random.randint(0, 1):
                    px *= -1
                if random.randint(0, 1):
                    py *= -1
                if self.phase == 2 and random.randint(0, 1):
                    t = px
                    px = py
                    py = t
                self.pos = (px + player.pos[0], py + player.pos[1])
            self.tick += 1
            if self.state == 0:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 15000))
            else:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), vector.distance(px, py) * 40))


class GreedAI(SlowMoverAI):
    MASS = 400
    FRICTION = 0.95
    TOUCHING_DAMAGE = 0
    TD = 220
    KB = 100

    def __init__(self, pos):
        super().__init__(pos)
        self.tick = 0
        self.state = 0
        self.phase = 1
        self.rot = 0
        self.dp = pos

    def on_update(self):
        self.pos = self.dp
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            self.tick += 1
            if self.tick > 80:
                self.state = (self.state + 1) % 4
                if self.state == 3:
                    self.rot = (self.rot + 180) % 360
                self.tick = 0
            if self.state == 0:
                self.TOUCHING_DAMAGE = self.TD
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 600))
            else:
                self.TOUCHING_DAMAGE = 0
                ax, ay = vector.rotation_coordinate(self.rot)
                px += ax * 320
                py += ay * 320
                self.pos = (self.pos[0] + px // 5, self.pos[1] + py // 5)
                self.velocity.clear()
                self.velocity.add(vector.Vector(0, self.KB))
                if self.state == 1:
                    self.rot = (self.rot + 3) % 360
                elif self.state == 3:
                    self.rot = (self.rot + 10) % 360
                else:
                    pg.draw.line(game.get_game().displayer.canvas, (255, 0, 0), position.displayed_position(self.pos),
                                 position.displayed_position((self.pos[0] + px - 800 * ax, self.pos[1] + py - 800 * ay)),
                                 width=50)
            self.dp = self.pos

class CardBombAI(SlowMoverAI):
    MASS = 600
    FRICTION = 0.95
    TOUCHING_DAMAGE = 120

    def __init__(self, pos):
        super().__init__(pos)

    def update(self):
        self.apply_force(vector.Vector(180, 1200))

class Entities:

    class Tag(inventory.Inventory.Item.Tag):
        pass

    class DisplayModes:
        NO_IMAGE = 0
        DIRECTIONAL = 1
        BIDIRECTIONAL = 2
        NO_DIRECTION = 3

    class Entity:
        NAME = 'Entity'
        DISPLAY_MODE = 0
        LOOT_TABLE = LootTable([])
        ENTITY_TAGS = []
        IS_MENACE = False

        SOUND_SPAWN = None
        SOUND_HURT = None
        SOUND_DEATH = None

        def __init__(self, pos, img=None, ai: type(MonsterAI) = MonsterAI, hp=120,
                     hp_sys: hp_system.HPSystem | None = None):
            self.obj: mover.Mover = ai(pos)
            self.show_bar = True
            if hp_sys is None:
                self.hp_sys = hp_system.HPSystem(hp)
            else:
                self.hp_sys = hp_system.SubHPSystem(hp_sys)
                self.show_bar = False
            self.img: pg.Surface | None = img
            self.d_img = self.img
            self.rot = 0
            self.touched_player = False
            try:
                if self.SOUND_SPAWN is not None:
                    self.play_sound('spawn_' + self.SOUND_SPAWN)
            except ValueError:
                pass
            self.hp_sys.SOUND_HURT = self.SOUND_HURT

        def set_rotation(self, rot):
            self.rot = rot
            if self.DISPLAY_MODE == Entities.DisplayModes.DIRECTIONAL:
                self.d_img = pg.transform.rotate(self.img, rot)
            elif self.DISPLAY_MODE == Entities.DisplayModes.BIDIRECTIONAL:
                if rot % 360 < 180:
                    self.d_img = pg.transform.flip(self.img, True, False)
                else:
                    self.d_img = self.img
            else:
                self.d_img = self.img
            self.d_img = pg.transform.scale_by(self.d_img, 1 / game.get_game().player.get_screen_scale())

        def play_sound(self, sound):
            d = vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                                self.obj.pos[1] - game.get_game().player.obj.pos[1])
            game.get_game().play_sound(sound, 0.99 ** int(d / 10))

        def is_suitable(self, biome: str):
            return True

        def on_damage_player(self):
            pass

        def rotate(self, angle):
            self.set_rotation((self.rot + angle) % 360)

        def update(self):
            self.set_rotation(self.rot)
            self.hp_sys.pos = self.obj.pos
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[
                                   1]) > game.get_game().player.SIMULATE_DISTANCE and not self.IS_MENACE:
                return
            self.obj.update()
            self.hp_sys.update()
            p = position.displayed_position((self.obj.pos[0], self.obj.pos[1]))
            if p[0] < -100 or p[0] > game.get_game().displayer.SCREEN_WIDTH + 100 or p[1] < -100 or p[
                1] > game.get_game().displayer.SCREEN_HEIGHT + 100:
                return
            self.draw()

        def draw(self):
            displayer = game.get_game().displayer
            if self.DISPLAY_MODE == Entities.DisplayModes.NO_IMAGE:
                pg.draw.circle(displayer.canvas, (0, 0, 255), position.displayed_position(self.obj.pos), 10)
                if self.show_bar:
                    styles.hp_bar(self.hp_sys, position.displayed_position((self.obj.pos[0], self.obj.pos[1] - 10)), 60)
            else:
                r = self.d_img.get_rect()
                r.center = position.displayed_position(self.obj.pos)
                displayer.canvas.blit(self.d_img, r)
                if self.show_bar:
                    styles.hp_bar(self.hp_sys, position.displayed_position(
                        (self.obj.pos[0], self.obj.pos[1] - self.d_img.get_height() // 2 - 10)),
                                  self.img.get_width() * 2)
                if r.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
                    f = displayer.font.render(f'{self.NAME}({int(self.hp_sys.hp)}/{self.hp_sys.max_hp})', True,
                                              (255, 255, 255), (0, 0, 0))
                    displayer.canvas.blit(f, game.get_game().displayer.reflect(*pg.mouse.get_pos()))

    class Dummy(Entity):
        NAME = 'Dummy'
        DISPLAY_MODE = 0
        LOOT_TABLE = LootTable([])
        ENTITY_TAGS = []
        IS_MENACE = False

        SOUND_SPAWN = None
        SOUND_HURT = None
        SOUND_DEATH = None

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_dummy'], BuildingAI, 100)
            self.hp_sys.IMMUNE = True

    class WormEntity:
        NAME = 'Entity'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])
        ENTITY_TAGS = []
        IS_MENACE = False

        SOUND_SPAWN = None
        SOUND_HURT = None
        SOUND_DEATH = None

        def __init__(self, pos, length, img_head=None, img_body=None, head_ai: type(MonsterAI) = MonsterAI, hp=120,
                     body_length=60, body_touching_damage=100):
            self.length = length
            self.body_length = body_length
            self.hp_sys = hp_system.HPSystem(hp)
            self.body = [Entities.Entity(pos, img_head, head_ai, hp_sys=self.hp_sys)] + [
                Entities.Entity((pos[0] + i + 1, pos[1]), img_body, MonsterAI, hp_sys=self.hp_sys) for i in
                range(length - 1)]
            self.obj = self.body[0].obj
            for i in range(1, self.length):
                game.get_game().entities.append(self.body[i])
                self.body[i].obj.IS_OBJECT = False
                self.body[i].obj.TOUCHING_DAMAGE = body_touching_damage
                # self.body[i].obj.IS_OBJECT = False
            self.d_img = self.body[0].d_img
            self.img = self.body[0].img
            self.rot = self.body[0].rot
            for b in self.body:
                b.DISPLAY_MODE = 1
                b.NAME = self.NAME
            try:
                if self.SOUND_SPAWN is not None:
                    self.body[0].play_sound('spawn_' + self.SOUND_SPAWN)
            except ValueError:
                pass
            self.hp_sys.SOUND_HURT = self.SOUND_HURT

        def play_sound(self, sound):
            self.body[0].play_sound(sound)

        def on_damage_player(self):
            pass

        def update(self):
            self.body[0].update()
            self.body[0].set_rotation(-self.obj.velocity.get_net_rotation())
            for i in range(1, self.length):
                ox, oy = self.body[i - 1].obj.pos
                nx, ny = self.body[i].obj.pos
                self.body[i].set_rotation(-vector.coordinate_rotation(ox - nx, oy - ny))
                ax, ay = vector.rotation_coordinate(vector.coordinate_rotation(ox - nx, oy - ny))
                tx, ty = ox - ax * self.body_length, oy - ay * self.body_length
                self.body[i].obj.pos = (tx, ty)
                if not i and self.body[i].obj.velocity.get_net_value() > 0:
                    self.body[0].obj.velocity.add(self.body[i].obj.velocity.get_net_vector())
                    self.body[i].obj.velocity.clear()
                self.body[i].obj.object_collision(self.body[i - 1].obj, self.body_length + 1)
                self.body[i - 1].obj.object_collision(self.body[i].obj, self.body_length + 1)
                self.body[i].obj.object_collision(game.get_game().player.obj, self.body_length // 2 + 1 + 50)
                # self.body[i].obj.apply_force(vector.Vector(vector.coordinate_rotation(tx - nx, ty - ny), vector.distance(tx - nx, ty - ny) * 8))


        def set_rotation(self, rot):
            self.body[0].set_rotation(rot)

        def rotate(self, rot):
            self.body[0].rotate(rot)

        def is_suitable(self, biome: str):
            return True

    class Test(Entity):
        NAME = 'Test'
        pass

    class Eye(Entity):
        NAME = 'Eye'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            SelectionLoot([('iron', 10, 12), ('steel', 6, 8)], 1, 2),
            IndividualLoot('dangerous_necklace', 0.1, 1, 1),
            IndividualLoot('cell_organization', 0.8, 1, 3),
            IndividualLoot('watcher_wand', 0.06, 1, 1),
        ])

        SOUND_HURT = 'sticky'

        def is_suitable(self, biome: str):
            return True

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_eye'], EyeAI, 190)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = -2
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 2

        def update(self):
            self.set_rotation((self.rot * 5 - self.obj.velocity.get_net_rotation()) // 6)
            super().update()

    class TrueEye(Entity):
        NAME = 'True Eye'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('blood_ingot', 1, 20, 30),
            IndividualLoot('platinum', 1, 80, 90),
            SelectionLoot([('orange_ring', 1, 1), ('blue_ring', 1, 1), ('green_ring', 1, 1)], 1, 1),
            IndividualLoot('aimer', 0.2, 1, 1),
            IndividualLoot('tip2', 1, 1, 1),
        ])
        IS_MENACE = True

        SOUND_SPAWN = 'boss'
        SOUND_HURT = 'sticky'
        SOUND_DEATH = 'huge_monster'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_true_eye'], TrueEyeAI, 4200)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = -5
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 8
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 2

        def update(self):
            self.set_rotation((self.rot * 8 - self.obj.velocity.get_net_rotation()) // 9)
            super().update()

    class Tree(Entity):
        NAME = 'Tree'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('wood', 0.9, 15, 25)
        ])

        def is_suitable(self, biome: str):
            return biome in ['forest', 'rainforest']

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_tree'], BuildingAI, 10)
            self.hp_sys(op='config', maximum_damage=3)

    class HugeTree(Entity):
        NAME = 'Huge Tree'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('wood', 0.9, 30, 50),
            IndividualLoot('platinum', 0.6, 15, 40),
        ])

        def is_suitable(self, biome: str):
            return biome in ['rainforest']

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_huge_tree'], BuildingAI, 200)
            self.hp_sys(op='config', maximum_damage=50)

    class TreeMonster(Entity):
        NAME = 'Tree Monster'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('wood', 0.5, 5, 12),
            IndividualLoot('leaf', 0.8, 1, 2),
            IndividualLoot('copper', 0.6, 15, 40),
        ])

        SOUND_DEATH = 'monster'

        def is_suitable(self, biome: str):
            return biome in ['forest', 'rainforest']

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_tree_monster'], TreeMonsterAI, 225)

    class ClosedBloodflower(Entity):
        NAME = 'Closed Bloodflower'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('copper', 0.9, 15, 25),
            IndividualLoot('cell_organization', 0.3, 2, 8),
            IndividualLoot('leaf', 0.5, 7, 12),
            IndividualLoot('spikeflower', 0.18, 1, 1),
        ])

        SOUND_HURT = 'corrupt'
        SOUND_DEATH = 'sticky'

        def is_suitable(self, biome: str):
            return biome in ['forest', 'rainforest']

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_closed_bloodflower'], CloseBloodflowerAI, 56)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 6
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 7
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 3

    class Bloodflower(Entity):
        NAME = 'Bloodflower'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('steel', 0.9, 15, 25),
            IndividualLoot('cell_organization', 0.9, 12, 16),
            IndividualLoot('platinum', 0.3, 10, 20),
            IndividualLoot('spikeflower', 0.36, 1, 1),
            SelectionLoot([('purple_ring', 1, 1), ('cyan_ring', 1, 1), ('yellow_ring', 1, 1)], 0, 1),
        ])

        SOUND_HURT = 'corrupt'
        SOUND_DEATH = 'sticky'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_bloodflower'], BloodflowerAI, 920)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = -25
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = -18
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = -32

    class RedWatcher(Entity):
        NAME = 'Red Watcher'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('platinum', 0.9, 20, 40),
            IndividualLoot('magic_stone', 0.2, 5, 10),
            IndividualLoot('iron', 0.9, 15, 25),
            SelectionLoot([('purple_ring', 1, 1), ('cyan_ring', 1, 1), ('yellow_ring', 1, 1)], 1, 2),
        ])

        SOUND_DEATH = 'monster'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_red_watcher'], RedWatcherAI, 1500)
            self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = 2.5
            self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 2.3
            self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 2.8

    class Cactus(Entity):
        NAME = 'Cactus'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('wood', 0.9, 15, 25),
            IndividualLoot('iron', 0.8, 20, 30),
            IndividualLoot('copper', 0.6, 15, 40),
            IndividualLoot('cactus_wand', 0.2, 1, 1),
        ])

        SOUND_DEATH = 'monster'

        def is_suitable(self, biome: str):
            return biome in ['desert']

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_cactus'], CactusAI, 365)

    class ConiferousTree(Entity):
        NAME = 'Coniferous Tree'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('wood', 0.9, 15, 25),
            IndividualLoot('steel', 0.8, 20, 30),
            IndividualLoot('copper', 0.6, 15, 40),
            IndividualLoot('coniferous_leaf', 0.2, 50, 200),
        ])

        SOUND_DEATH = 'monster'

        def is_suitable(self, biome: str):
            return biome in ['snowland']

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_coniferous_tree'], CactusAI, 385)

    class MagmaCube(Entity):
        NAME = 'Magma Cube'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('cell_organization', 0.9, 10, 15),
            IndividualLoot('platinum', 0.8, 20, 30),
            IndividualLoot('blood_ingot', 0.6, 5, 10),
            IndividualLoot('firite_ingot', 0.5, 8, 15),
        ])

        SOUND_HURT = 'sticky'
        SOUND_DEATH = 'sticky'

        def is_suitable(self, biome: str):
            return biome in ['hell']

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_magma_cube'], MagmaCubeAI, 1100)
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 10
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 8
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 15

    class DropItem(Entity):
        NAME = 'Drop Item'
        DISPLAY_MODE = 3

        def __init__(self, pos, item_id, item_amount):
            super().__init__(pos, game.get_game().graphics['items_' + item_id], BuildingAI, 1)
            self.amount = item_amount
            if self.img.get_width() < 64:
                self.img = pg.transform.scale(self.img, (64, 64))
                self.d_img = self.img
            self.NAME = item_id.replace('_', '').title()
            self.item_id = item_id
            self.hp_sys(op='config', immune=True)

        def update(self):
            super().update()
            px, py = game.get_game().player.obj.pos
            if vector.distance(self.obj.pos[0] - px, self.obj.pos[1] - py) < 40:
                game.get_game().player.inventory.add_item(inventory.ITEMS[self.item_id], self.amount)
                self.hp_sys.hp = 0
            elif vector.distance(self.obj.pos[0] - px, self.obj.pos[1] - py) < 120:
                self.obj.apply_force(
                    vector.Vector(vector.coordinate_rotation(px - self.obj.pos[0], py - self.obj.pos[1]), 24000))

    class Star(Entity):
        NAME = 'Star'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('platinum', 0.7, 15, 55),
            IndividualLoot('magic_stone', 0.9, 12, 15),
            IndividualLoot('mana_crystal', 0.5, 1, 2)
        ])

        SOUND_HURT = 'corrupt'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_star'], StarAI, 820)
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = -11

    class MagmaKingFireball(Entity):
        NAME = 'Magma King Fireball'
        DISPLAY_MODE = 3

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_fireball'], MagmaKingFireballAI, 5000)
            self.obj.rot = rot
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = -50
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 40
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 20

        def update(self):
            self.set_rotation(self.rot)
            self.hp_sys.hp -= 20
            super().update()
            self.damage()

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(40, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class SandStormAttack(MagmaKingFireball):

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(72, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class MagmaKing(Entity):
        NAME = 'Magma King'
        DISPLAY_MODE = 3
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            IndividualLoot('blood_ingot', 0.8, 5, 10),
            IndividualLoot('firite_ingot', 1, 30, 40),
            IndividualLoot('firy_plant', 1, 10, 20),
            IndividualLoot('tip3', 1, 1, 1),
        ])

        SOUND_SPAWN = 'boss'
        SOUND_HURT = 'sticky'
        SOUND_DEATH = 'huge_monster'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_magma_king'], MagmaKingAI, 6400)
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 72
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 68
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 88

        def update(self):
            super().update()
            if self.obj.state == 2 and self.obj.timer % 10 == 1:
                player = game.get_game().player
                game.get_game().entities.append(Entities.MagmaKingFireball(self.obj.pos, vector.coordinate_rotation(
                    player.obj.pos[0] - self.obj.pos[0], player.obj.pos[1] - self.obj.pos[1])))
            if self.obj.state == 1 and self.obj.timer % 40 == 20:
                player = game.get_game().player
                for k in range(-30, 31, 15):
                    fb = Entities.MagmaKingFireball(self.obj.pos,
                                                    k + vector.coordinate_rotation(player.obj.pos[0] - self.obj.pos[0],
                                                                                   player.obj.pos[1] - self.obj.pos[1]))
                    fb.obj.apply_force(
                        vector.Vector(self.obj.velocity.get_net_rotation(), self.obj.velocity.get_net_value() // 50))
                    game.get_game().entities.append(fb)

    class SandStorm(Entity):
        NAME = 'Sandstorm'
        DISPLAY_MODE = 3
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            IndividualLoot('mysterious_ingot', 1, 15, 35),
            IndividualLoot('storm_core', 1, 2, 4),
            IndividualLoot('tornado', 0.5, 1, 1),
            IndividualLoot('tip4', 1, 1, 1),
        ])

        SOUND_SPAWN = 'boss'
        SOUND_DEATH = 'huge_monster'

        def __init__(self, pos, hp_sys, rot):
            super().__init__(pos, game.get_game().graphics['entity_sandstorm'], SandStormAI, hp_sys=hp_sys)
            self.obj.rot = rot
            self.tick = 0
            self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 4
            self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 5

        def update(self):
            super().update()
            self.tick += 1
            if self.tick % (8 if self.obj.state == 0 else (5 if self.obj.state == 2 else 8000)) == 1:
                px, py = game.get_game().player.obj.pos
                rot = vector.coordinate_rotation(px - self.obj.pos[0], py - self.obj.pos[1])
                self.set_rotation(rot)
                game.get_game().entities.append(Entities.SandStormAttack(self.obj.pos, self.rot))

    class RuneRock(Entity):
        NAME = 'Rune Rock'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('magic_stone', 0.3, 20, 30),
            IndividualLoot('mysterious_substance', 0.8, 10, 12),
        ])

        SOUND_HURT = 'metal'
        SOUND_DEATH = 'explosive'

        def is_suitable(self, biome: str):
            return biome in ['desert']

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_rune_rock'], RuneRockAI, 1550)
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 32

    class AbyssRuneShoot(Entity):
        NAME = 'Abyss Rune'
        DISPLAY_MODE = 3

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_abyss_rune'], AbyssRuneShootAI, 50000)
            self.obj.rot = rot

        def update(self):
            self.set_rotation(self.rot)
            self.hp_sys.hp -= 200
            super().update()
            self.damage()

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(68, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class TruthlessCurse(Entity):
        NAME = 'Truthless Curse'
        DISPLAY_MODE = 3

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_truthless_curse'], AbyssRuneShootAI, 500000)
            self.obj.rot = rot

        def update(self):
            self.set_rotation(self.rot)
            self.hp_sys.hp -= 2000
            super().update()
            self.damage()

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(80, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.effect(effects.TruthlessCurse(2, 30))
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class FaithlessCurse(Entity):
        NAME = 'Faithless Curse'
        DISPLAY_MODE = 3

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_faithless_curse'], AbyssRuneShootAI, 500000)
            self.obj.rot = rot

        def update(self):
            self.set_rotation(self.rot)
            self.hp_sys.hp -= 2000
            super().update()
            self.damage()

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(80, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.effect(effects.FaithlessCurse(20, 1))
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class SpadeBullet(Entity):
        NAME = 'Spade Bullet'
        DISPLAY_MODE = 1

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_spade_bullet'], FastBulletAI, 50000000)
            self.obj.rot = rot
            self.obj.speed = 240

        def update(self):
            self.hp_sys.hp -= 200000
            super().update()
            self.damage()
            self.set_rotation(90 - self.obj.rot)

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 50:
                game.get_game().player.hp_sys.damage(210, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class AlmondBullet(Entity):
        NAME = 'Almond Bullet'
        DISPLAY_MODE = 1

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_almond_bullet'], FastBulletAI, 50000000)
            self.obj.rot = rot
            self.obj.speed = 500

        def update(self):
            self.hp_sys.hp -= 200000
            super().update()
            self.damage()
            self.set_rotation(90 - self.obj.rot)

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 50:
                game.get_game().player.hp_sys.damage(210, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class BombBullet(Entity):
        NAME = 'Bomb Bullet'
        DISPLAY_MODE = 1

        def __init__(self, pos, rot, mode, spd, r=1):
            super().__init__(pos, game.get_game().graphics[f'entity_{mode}_bomb_bullet'], FastBulletAI, 50000000)
            self.obj.rot = rot
            self.obj.speed = spd
            self.mode = mode
            self.r = r
            self.rt = 0
            self.buls = []
            if self.mode == 'heart' and self.r:
                self.buls = [Entities.BombBullet((0, 0), rot, 'heart', 0, 0) for _ in range(4)]
                for b in self.buls:
                    game.get_game().entities.append(b)
                self.img = game.get_game().graphics[f'entity_null']
                self.d_img = game.get_game().graphics[f'entity_null']

        def update(self):
            self.hp_sys.hp -= 200000
            super().update()
            self.damage()
            self.set_rotation(90 - self.obj.rot)
            if self.r and self.mode == 'heart':
                self.rt += 5
                for i in range(4):
                    rr = self.rt + i * 90
                    ax, ay = vector.rotation_coordinate(rr)
                    self.buls[i].obj.pos = (self.obj.pos[0] + ax * 100, self.obj.pos[1] + ay * 100)


        def damage(self):
            if self.mode == 'heart' and not self.r:
                return
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 50:
                game.get_game().player.hp_sys.damage(225, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class Seed(Entity):
        NAME = 'Seed'
        DISPLAY_MODE = 1

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_seed'], FastBulletAI, 50000000)
            self.obj.rot = rot
            self.obj.speed = 3200
            self.obj.MASS *= 5

        def update(self):
            self.hp_sys.hp -= 200000
            super().update()
            self.set_rotation(-self.obj.rot)
            self.damage()

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 320:
                game.get_game().player.hp_sys.damage(256, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.effect(effects.Poison(5, 24))
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class SpikeBall(Entity):
        NAME = 'Spike Ball'
        DISPLAY_MODE = 1

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_spikeball'], FastBulletAI, 50000000)
            self.obj.rot = rot
            self.obj.speed = 0
            self.set_rotation(self.obj.rot)
            self.obj.MASS *= 8

        def update(self):
            self.hp_sys.hp -= 200000
            super().update()
            self.damage()

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 220:
                game.get_game().player.hp_sys.damage(312, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.effect(effects.Poison(8, 45))
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class CardBomb(Entity):
        NAME = 'Card Bomb'
        DISPLAY_MODE = 1

        SOUND_DEATH = 'card_bomb'

        def __init__(self, pos, mode):
            super().__init__(pos, game.get_game().graphics[f'entity_{mode}_bomb'], CardBombAI, 300000000)
            self.obj.rot = 0
            self.mode = mode

        def update(self):
            self.obj.pos = (self.obj.pos[0], self.obj.pos[1] + 75)
            self.hp_sys.hp -= 75 * 10 ** 5
            super().update()
            if self.hp_sys.hp <= 0:
                self.hp_sys.hp = 0
                px, py = (game.get_game().player.obj.pos[0] - self.obj.pos[0],
                          game.get_game().player.obj.pos[1] - self.obj.pos[1])
                rot = vector.coordinate_rotation(px, py)
                if self.mode == 'heart':
                    game.get_game().entities.append(Entities.BombBullet(self.obj.pos, rot, 'heart', 120, 1))
                elif self.mode == 'spade':
                    sr = random.randint(0, 18)
                    for i in range(sr, sr + 360, 18):
                        game.get_game().entities.append(Entities.BombBullet(self.obj.pos, i, 'spade', 200, 1))
                elif self.mode == 'diamond':
                    for i in range(120, 360, 80):
                        game.get_game().entities.append(Entities.BombBullet(self.obj.pos, rot, 'diamond', i, 1))
                elif self.mode == 'club':
                    for i in range(-60, 61, 30):
                        game.get_game().entities.append(Entities.BombBullet(self.obj.pos, rot + i, 'club', 300, 1))

    class Time(Entity):
        NAME = 'Time'
        DISPLAY_MODE = 3

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_time'], AbyssRuneShootAI, 5000000)
            self.obj.rot = rot

        def update(self):
            self.set_rotation(self.rot)
            self.hp_sys.hp -= 20000
            super().update()
            self.damage()

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(110, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class DevilsMark(Entity):
        NAME = 'Devil\'s Mark'
        DISPLAY_MODE = 3

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_devils_mark'], BuildingAI, 500000)
            self.tick = 0

        def update(self):
            self.hp_sys.hp -= 20000
            super().update()
            self.img = pg.transform.scale_by(game.get_game().graphics['entity_devils_mark'], 1 + self.tick * 0.15)
            self.d_img = copy.copy(self.img)
            self.d_img.set_alpha(255 - self.tick)
            if self.tick > 250:
                self.hp_sys.hp = 0
            self.damage()
            self.tick += 1

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < self.d_img.get_width() / 2:
                game.get_game().player.hp_sys.damage(136, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()

    class Lazer(Entity):
        NAME = 'Lazer'
        DISPLAY_MODE = 1

        SOUND_SPAWN = 'lazer'

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_lazer'], AbyssRuneShootAI, 500000)
            self.obj.rot = rot
            self.set_rotation(90 + rot)

        def update(self):
            self.set_rotation(self.rot)
            self.hp_sys.hp -= 2000
            super().update()
            self.damage()

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(188, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class AbyssRune(Entity):
        NAME = 'Abyss Rune'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('soul', 0.9, 1, 2),
        ])

        def __init__(self, pos, rot, dis, hp=10000, ar=6):
            super().__init__(pos, game.get_game().graphics['entity_abyss_rune'], AbyssRuneAI, hp)
            self.obj.rot = rot
            self.obj.d = dis
            self.obj.ar = ar / 10

        def update(self):
            super().update()
            e = [e for e in game.get_game().entities if type(e) is Entities.AbyssEye]
            if not len(e):
                self.hp_sys.hp -= self.hp_sys.max_hp // 300

    class AbyssEye(Entity):
        NAME = 'Abyss Eye'
        DISPLAY_MODE = 3
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            IndividualLoot('soul', 1, 100, 200),
            SelectionLoot([('spiritual_stabber', 1, 1), ('spiritual_piercer', 1, 1), ('spiritual_destroyer', 1, 1)], 1,
                          2),
            IndividualLoot('tip5', 1, 1, 1),
        ])

        SOUND_SPAWN = 'boss'
        SOUND_HURT = 'corrupt'
        SOUND_DEATH = 'huge_monster'

        def is_suitable(self, biome: str):
            return biome in ['heaven']

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_abyss_eye'], AbyssEyeAI, 14400)
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 20
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 25
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 23
            self.tick = 0
            self.state = 0
            self.rounds = 0
            for i in range(5):
                for r in range(0, 361, [60, 40, 30, 20, 15, 10][i]):
                    game.get_game().entities.append(
                        Entities.AbyssRune((0, 0), r, i * 300 + 300, 15000 - i * i * 500, int((-1.15) ** i * 3)))
            for r in range(0, 361, 5):
                game.get_game().entities.append(Entities.AbyssRune((0, 0), r, 1800, 10000000, 12))

        def update(self):
            super().update()
            game.get_game().day_time = 0
            self.tick += 1
            if self.tick > random.randint(200, 400):
                self.tick = 0
                self.state = (self.state + 1) % 3
                if not self.state:
                    self.rounds += 1
            if self.state == 0:
                if self.tick % 10 == 1:
                    game.get_game().entities.append(Entities.AbyssRuneShoot(self.obj.pos, self.tick * 2))
            elif self.state == 1:
                if self.tick % 10 == 1:
                    game.get_game().entities.append(Entities.AbyssRuneShoot(self.obj.pos, random.randint(0, 360)))
            else:
                if self.tick % 10 == 1:
                    if self.rounds < 5:
                        k = [180, 120, 90, 72, 60][self.rounds]
                    else:
                        k = 45
                    for r in range(0, 360, k):
                        game.get_game().entities.append(Entities.AbyssRuneShoot(self.obj.pos, self.tick + r))

    class SwordInTheStone(Entity):
        NAME = 'Sword in the Stone'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            SelectionLoot([('magic_sword', 1, 1), ('magic_blade', 1, 1)], 1, 1)
        ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_sword_in_the_stone'], BuildingAI, 10000)

    class EvilMark(Entity):
        NAME = 'Evil Mark'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('soul', 0.9, 6, 7),
            IndividualLoot('evil_ingot', 1, 10, 12),
            SelectionLoot([('tip61', 1, 1), ('tip62', 1, 1), ('tip63', 1, 1)], 1, 1),
        ])

        SOUND_HURT = 'corrupt'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_evil_mark'], BuildingAI, 1800)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 40
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 50
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 80

    class SoulFlower(Entity):
        NAME = 'soul flower'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('mana_crystal', 0.9, 15, 25),
            IndividualLoot('seatea', 0.9, 12, 16),
            IndividualLoot('evil_ingot', 0.6, 1, 3),
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 0, 1)
        ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_soul_flower'], SoulFlowerAI, 2600)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 50
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 80
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 60

    class Cells(Entity):
        NAME = 'Cells'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('soul_of_flying', 0.9, 5, 12),
            IndividualLoot('evil_ingot', 0.9, 2, 5),
        ])

        SOUND_HURT = 'sticky'
        SOUND_DEATH = 'sticky'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_cells'], CellsAI, 3200)

    class SnowDrake(Entity):
        NAME = 'Snow Drake'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('soul_of_coldness', 0.9, 5, 12),
            IndividualLoot('evil_ingot', 0.9, 2, 5),
        ])

        SOUND_HURT = 'sticky'
        SOUND_DEATH = 'monster'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_snowdrake'], SnowDrakeAI, 2500)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 10
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 15
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 18

    class IceCap(Entity):
        NAME = 'Ice Cap'
        DISPLAY_MODE = 2
        LOOT_TABLE = LootTable([
            IndividualLoot('soul_of_coldness', 0.9, 5, 12),
            IndividualLoot('evil_ingot', 0.9, 2, 5),
        ])

        SOUND_HURT = 'metal'
        SOUND_DEATH = 'monster'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_ice_cap'], IceCapAI, 1200)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 2
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 2
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 8
            self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = .2
            self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = .2
            self.hp_sys.resistances[damages.DamageTypes.PIERCING] = .2

    class MechanicEye(Entity):
        NAME = 'Mechanic Eye'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('evil_ingot', 0.9, 5, 8),
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 0, 1)
        ])

        SOUND_HURT = 'metal'
        SOUND_DEATH = 'explosive'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_mechanic_eye'], MechanicEyeAI, 2800)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 10
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 15
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 18

        def update(self):
            super().update()
            self.set_rotation((self.rot * 4 - self.obj.velocity.get_net_rotation()) // 5)

    class FaithlessEye(Entity):
        NAME = 'Faithless Eye'
        DISPLAY_MODE = 1
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 1, 3),
            IndividualLoot('soul_of_integrity', 1, 10, 22),
            IndividualLoot('double_watcher_wand', 0.5, 1, 1),
            IndividualLoot('tip71', 1, 1, 1),
        ])

        SOUND_SPAWN = 'boss'
        SOUND_HURT = 'metal'
        SOUND_DEATH = 'explosive'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_faithless_eye'], FaithlessEyeAI, 14000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 35
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 37
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 38
            self.phase = 1

        def update(self):
            if self.phase == 1 and (self.hp_sys.hp < self.hp_sys.max_hp // 2 or not \
                    bool(len([1 for e in game.get_game().entities if type(e) is Entities.TruthlessEye]))):
                self.phase = 2
                self.obj.phase = 2
                self.img = game.get_game().graphics['entity_faithless_eye_phase2']
            super().update()
            if self.obj.state == 0:
                self.set_rotation((self.rot * 2 - self.obj.velocity.get_net_rotation()) // 3)
            else:
                self.set_rotation((self.rot - self.obj.rot) // 2)
                if self.obj.tick % 50 == 1:
                    px, py = game.get_game().player.obj.pos
                    k = 1
                    if self.obj.phase == 2:
                        k = 3
                    for r in range(-k * 15, k * 15 + 1, 15):
                        game.get_game().entities.append(Entities.FaithlessCurse(self.obj.pos,
                                                                                vector.coordinate_rotation(
                                                                                    px - self.obj.pos[0],
                                                                                    py - self.obj.pos[1]) + r))

    class TruthlessEye(Entity):
        NAME = 'Truthless Eye'
        DISPLAY_MODE = 1
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 1, 3),
            IndividualLoot('soul_of_integrity', 1, 10, 22),
            IndividualLoot('double_watcher_wand', 0.5, 1, 1),
            IndividualLoot('tip71', 1, 1, 1),
        ])

        SOUND_SPAWN = 'boss'
        SOUND_HURT = 'metal'
        SOUND_DEATH = 'explosive'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_truthless_eye'], FaithlessEyeAI, 18000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 35
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 37
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 38
            self.obj.ax = 900
            self.obj.ay = -400
            self.obj.state = 1
            self.phase = 1

        def update(self):
            if self.phase == 1 and (self.hp_sys.hp < self.hp_sys.max_hp // 2 or not \
                    bool(len([1 for e in game.get_game().entities if type(e) is Entities.FaithlessEye]))):
                self.phase = 2
                self.obj.phase = 2
                self.img = game.get_game().graphics['entity_faithless_eye_phase2']
            super().update()
            if self.obj.state == 0:
                self.set_rotation((self.rot * 2 - self.obj.velocity.get_net_rotation()) // 3)
            else:
                self.set_rotation((self.rot - self.obj.rot) // 2)
                if self.obj.tick % 60 == 0:
                    px, py = game.get_game().player.obj.pos
                    k = 0
                    if self.obj.phase == 2:
                        k = 5
                    for r in range(-k * 20, k * 20 + 1, 20):
                        game.get_game().entities.append(Entities.TruthlessCurse(self.obj.pos,
                                                                                vector.coordinate_rotation(
                                                                                    px - self.obj.pos[0],
                                                                                    py - self.obj.pos[1]) + r))

    class Destroyer(WormEntity):
        NAME = 'Destroyer'
        DISPLAY_MODE = 1
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 1, 3),
            IndividualLoot('soul_of_bravery', 1, 10, 22),
            IndividualLoot('tip73', 1, 1, 1),
        ])

        SOUND_SPAWN = 'boss'
        SOUND_HURT = 'metal'
        SOUND_DEATH = 'explosive'

        def __init__(self, pos):
            super().__init__(pos, 54, game.get_game().graphics['entity_destroyer_head'],
                             game.get_game().graphics['entity_destroyer_body'], DestroyerAI, 240000, body_length=90)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 80
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 60
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 90

        def update(self):
            super().update()
            for b in self.body:
                if random.randint(0, 1000) == 0:
                    rot = vector.coordinate_rotation(game.get_game().player.obj.pos[0] - b.obj.pos[0],
                                                     game.get_game().player.obj.pos[1] - b.obj.pos[1])
                    l = Entities.Lazer(b.obj.pos, rot)
                    l.obj.apply_force(vector.Vector(rot, 3000))
                    game.get_game().entities.append(l)

    class TheCPU(Entity):
        NAME = 'The CPU'
        DISPLAY_MODE = 1
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 1, 3),
            IndividualLoot('soul_of_kindness', 1, 10, 22),
            IndividualLoot('remote_sword', 0.8, 1, 1),
            IndividualLoot('tip72', 1, 1, 1),
        ])

        SOUND_SPAWN = 'boss'
        SOUND_HURT = 'metal'
        SOUND_DEATH = 'explosive'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_the_cpu'], TheCPUAI, 24000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 30
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 25
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 45
            self.show_bar = False

        def update(self):
            if self.hp_sys.hp < self.hp_sys.max_hp * 0.5 and self.obj.phase == 1:
                self.obj.phase = 2
                self.img = game.get_game().graphics['entity_the_cpu_phase2']
                self.set_rotation(self.rot)
                self.obj.tick = -200
            px, py = game.get_game().player.obj.pos
            aax, aay = self.obj.pos[0] - game.get_game().player.obj.pos[0], self.obj.pos[1] - \
                       game.get_game().player.obj.pos[1]
            displayer = game.get_game().displayer
            r = self.d_img.get_rect()
            self.d_img.set_alpha(255 - int(240 * self.hp_sys.hp // self.hp_sys.max_hp))
            r.center = position.displayed_position((px - aax, py + aay))
            displayer.canvas.blit(self.d_img, r)
            r.center = position.displayed_position((px + aax, py - aay))
            displayer.canvas.blit(self.d_img, r)
            r.center = position.displayed_position((px - aax, py - aay))
            displayer.canvas.blit(self.d_img, r)
            if self.obj.phase == 2:
                r.center = position.displayed_position((px + aay, py + aax))
                displayer.canvas.blit(self.d_img, r)
                r.center = position.displayed_position((px - aay, py - aax))
                displayer.canvas.blit(self.d_img, r)
                r.center = position.displayed_position((px + aay, py - aax))
                displayer.canvas.blit(self.d_img, r)
                r.center = position.displayed_position((px - aay, py + aax))
                displayer.canvas.blit(self.d_img, r)
            self.d_img.set_alpha(255)
            super().update()

    class Greed(Entity):
        NAME = 'Greed'
        DISPLAY_MODE = 1
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 1, 3),
            IndividualLoot('saint_steel_ingot', 1, 5, 8),
            IndividualLoot('soul_of_perseverance', 1, 10, 22),
            SelectionLoot([('tip8', 1, 1), ('tip9', 1, 1)], 0, 2),
        ])

        SOUND_HURT = 'corrupt'
        SOUND_DEATH = 'explosive'

        def __init__(self, pos, d=False):
            super().__init__(pos, game.get_game().graphics['entity_greed'], GreedAI, 32000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 20
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 30
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 20
            self.d = d
            self.phase = 1
            if self.d:
                self.LOOT_TABLE = LootTable([])

        def update(self):
            super().update()
            if self.hp_sys.hp <= self.hp_sys.max_hp * (1 - self.phase * 0.2) and not self.d:
                self.phase += 1
                for i in range(4 * self.phase - 1):
                    d = Entities.Greed(self.obj.pos, True)
                    d.IS_MENACE = False
                    d.hp_sys.hp = 50000 + 20000 * self.phase
                    d.hp_sys.max_hp = d.hp_sys.hp
                    d.img = pg.transform.scale_by(d.img, 0.2 + 0.1 * self.phase)
                    d.obj.state = i
                    d.obj.TD = 60
                    d.obj.KB = 40
                    d.rot = random.randint(0, 360)
                    game.get_game().entities.append(d)
            if self.obj.state == 0:
                self.set_rotation((self.rot * 2 - self.obj.velocity.get_net_rotation()) // 3)
            else:
                self.set_rotation(-vector.coordinate_rotation(game.get_game().player.obj.pos[0] - self.obj.pos[0],
                                                              game.get_game().player.obj.pos[1] - self.obj.pos[1]))

    class EyeOfTime(Entity):
        NAME = 'Eye of Time'
        DISPLAY_MODE = 1
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            SelectionLoot([('palladium', 2, 3), ('mithrill', 2, 3), ('titanium', 2, 3)], 1, 3),
            IndividualLoot('dark_ingot', 1, 5, 8),
            IndividualLoot('soul_of_patience', 1, 1, 2),
            IndividualLoot('tip8', 0.1, 1, 1),
            IndividualLoot('tip9', 0.1, 1, 1),
        ])

        SOUND_DEATH = 'huge_monster'

        def __init__(self, pos, d: int = False, _hp_sys=None, idx: float = 0):
            _p = pos
            _p = (game.get_game().player.obj.pos[0] + random.randint(-5000, 5000),
                  game.get_game().player.obj.pos[1] + random.randint(-5000, 5000))
            if not d:
                hp_sys = hp_system.HPSystem(104000)
                for i in range(9):
                    game.get_game().entities.append(Entities.EyeOfTime(pos, True, hp_sys, i + 1))
                super().__init__(_p, game.get_game().graphics['entity_eye_of_time'], BuildingAI, hp_sys=hp_sys)
            else:
                super().__init__(_p, game.get_game().graphics['entity_eye_of_time'], BuildingAI, hp_sys=_hp_sys)
                self.IS_MENACE = False
            self.img = copy.copy(self.img)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 15
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 25
            self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 30
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 50
            self.tick = 20 * idx
            self.state = 0
            self.obj.IS_OBJECT = True
            self.obj.TOUCHING_DAMAGE = 100
            self.me = 1
            self.phase = 1
            self.d = d

        def update(self):
            self.tick += 1
            if self.phase == 1 and self.hp_sys.hp < self.hp_sys.max_hp * 0.5:
                self.phase = 2
                self.me = 2
                if not self.d:
                    for f in range(20):
                        et = Entities.EyeOfTime(self.obj.pos, 114, self.hp_sys, 1)
                        et.tick = (self.tick + 20 * f + 10) % 100
                        game.get_game().entities.append(et)
            if self.tick > 200 // self.me:
                self.state = (self.state + 1) % 1
                self.tick = 0
                self.obj.pos = (game.get_game().player.obj.pos[0] + random.randint(-500, 500),
                                game.get_game().player.obj.pos[1] + random.randint(-500, 500))
                self.obj.velocity.clear()
                self.obj.velocity.add(vector.Vector(random.randint(0, 360), 5))
                self.set_rotation(random.randint(-50, 50))
            if self.tick < 20:
                self.img.set_alpha(self.tick * 12 + 15)
            elif self.tick > 200 // self.me - 20:
                self.img.set_alpha(255 - (self.tick - 200 // self.me + 20) * 12)
            if self.tick % 20 == 0 and 20 <= self.tick <= 20 + 20 * self.me:
                t = Entities.Time(self.obj.pos,
                                  vector.coordinate_rotation(game.get_game().player.obj.pos[0] - self.obj.pos[0],
                                                             game.get_game().player.obj.pos[1] - self.obj.pos[1]))
                t.obj.apply_force(
                    vector.Vector(vector.coordinate_rotation(game.get_game().player.obj.pos[0] - self.obj.pos[0],
                                                             game.get_game().player.obj.pos[1] - self.obj.pos[1]),
                                  1000))
                game.get_game().entities.append(t)
            self.set_rotation(self.rot)
            super().update()

    class DevilPython(WormEntity):
        NAME = 'Devil Python'
        DISPLAY_MODE = 1
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 1, 3),
            IndividualLoot('daedalus_ingot', 1, 5, 8),
            IndividualLoot('soul_of_justice', 1, 10, 22),
            SelectionLoot([('tip8', 1, 1), ('tip9', 1, 1)], 0, 2),
        ])

        SOUND_HURT = 'corrupt'
        SOUND_DEATH = 'explosive'

        def __init__(self, pos):
            super().__init__(pos, 60, game.get_game().graphics['entity_devil_python_head'],
                             game.get_game().graphics['entity_devil_python_body'], DevilPythonAI, 84000,
                             body_length=90, body_touching_damage=100)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 25
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 30
            self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 15
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 60

        def update(self):
            super().update()
            for b in self.body:
                if random.randint(0, 1000) < 3:
                    game.get_game().entities.append(Entities.DevilsMark(b.obj.pos))

    class Leaf(Entity):
        NAME = 'Leaf'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('soul_of_growth', 1, 5, 10),
            IndividualLoot('chlorophyll', 0.03, 1, 1)
        ])

        SOUND_DEATH = 'monster'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_leaf'], LeafAI, 2000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 25
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 15
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 50

    class JevilKnife(Entity):
        NAME = 'Joker Evil Knife'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            ])

        def __init__(self, pos, hp_sys):
            super().__init__(pos, game.get_game().graphics['entity_jevil_knife'], JevilKnifeAI, hp_sys=hp_sys)
            self.tick = 0

        def update(self):
            super().update()
            self.set_rotation(self.tick * 18)
            self.tick += 1

    class Jevil(Entity):
        NAME = 'Joker Evil'
        DISPLAY_MODE = 2
        LOOT_TABLE = LootTable([
            IndividualLoot('chaos_ingot', 1, 50, 60),
            SelectionLoot([('jevil_knife', 1, 1), ('jevils_tail', 1, 1)], 1, 1),
            ])
        IS_MENACE = True

        SOUND_HURT = 'haha'
        SOUND_DEATH = 'haha'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_jevil'], JevilAI, 555000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 100
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 400
            self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 300
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 300
            self.phase = 0

        def update(self):
            self.hp_sys.SOUND_HURT = self.SOUND_HURT if not random.randint(0, 10) else None
            if self.hp_sys.hp < self.hp_sys.max_hp * 0.9 and self.phase == 0:
                self.phase = 1
                self.play_sound('i_can_do_anything')
            if self.hp_sys.hp < self.hp_sys.max_hp * 0.7 and self.phase == 1:
                self.phase = 2
                self.play_sound('devil_knife')
                for i in range(0, 360, 90):
                    kf = Entities.JevilKnife(self.obj.pos, self.hp_sys)
                    kf.obj.upper = self.obj
                    kf.obj.r = i
                    game.get_game().entities.append(kf)
            super().update()
            if self.hp_sys.hp < self.hp_sys.max_hp * 0.5 and self.phase == 2:
                self.phase = 3
                self.img = game.get_game().graphics['entity_null']
                self.play_sound('neo_chaos')
            r = -vector.coordinate_rotation(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                                                          self.obj.pos[1] - game.get_game().player.obj.pos[1])
            self.set_rotation(r)
            if self.phase <= 1:
                if self.obj.state in [0, 4] and self.obj.tick % 60 <= 1:
                    for r in range(-30, 31, 15 - 5 * self.phase):
                        bul = Entities.SpadeBullet(self.obj.pos, r - self.rot + 180)
                        game.get_game().entities.append(bul)
                elif self.obj.state in [2, 6] and self.obj.tick % 20 <= 1:
                    for r in range(-20 + 20 * (self.obj.tick % 40 < 20), 21, 40):
                        bul = Entities.AlmondBullet(self.obj.pos, r - self.rot + 180)
                        if self.phase:
                            bul.obj.speed = 800
                        game.get_game().entities.append(bul)
            elif self.phase == 2:
                if self.obj.state % 2 == 0 and self.obj.tick % 18 <= 1:
                    md = ['heart', 'club', 'spade', 'diamond'][self.obj.state // 2]
                    px, py = game.get_game().player.obj.pos
                    bul = Entities.CardBomb((px + random.randint(-1500, 1500), py + random.randint(-2500, -1000)), md)
                    game.get_game().entities.append(bul)
            else:
                if self.obj.tick % 15 <= 1:
                    md = random.choice(['heart', 'club', 'spade', 'diamond'])
                    px, py = game.get_game().player.obj.pos
                    bul = Entities.CardBomb((px + random.randint(-1500, 1500), py + random.randint(-2500, -1000)), md)
                    game.get_game().entities.append(bul)

    class PlanteraBulb(Entity):
        NAME = 'Plantera Bulb'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('plantera_bulb', 1, 1, 1),
            ])

        def is_suitable(self, biome: str):
            return biome in ['inner']

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_plantera_bulb'], BuildingAI, 10 ** 5)

    class Plantera(Entity):
        NAME = 'Plantera'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('origin', 1, 1, 1),
            IndividualLoot('willpower_shard', 1, 10, 30)
        ])
        IS_MENACE = True

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_plantera'], PlanteraAI, 1250000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 50
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 50
            self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 50
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 25
            self.sps = pos
            self.phase = 1
            self.cur_fs = 3200
            self.ctfs = 3200
            self.t = 0

        def update(self):
            super().update()
            self.t += 1
            pcs = int(10 * self.hp_sys.hp / self.hp_sys.max_hp) + 12 - self.phase * 6
            if self.t % (7 - 3 * self.phase + int(5 * self.hp_sys.hp / self.hp_sys.max_hp)) == 0:
                for _ in range(random.randint(1, 1 + self.phase)):
                    py = random.randint(-pcs, pcs) * 2
                    if random.randint(0, 10) >= self.phase * 4 - 1:
                        bul = Entities.Seed(self.obj.pos, self.obj.velocity.get_net_rotation() + py)
                        game.get_game().entities.append(bul)
                    elif random.randint(0, 10) > 4 - self.phase * 2:
                        bul = Entities.SpikeBall(self.obj.pos, self.obj.velocity.get_net_rotation() + py)
                        game.get_game().entities.append(bul)
            if self.hp_sys.hp < self.hp_sys.max_hp * 0.6 and self.phase == 1:
                self.phase = 2
                self.ctfs = 2500
                for k in self.hp_sys.defenses.defences.keys():
                    self.hp_sys.defenses[k] -= 10000
                    self.hp_sys.defenses[k] //= 5
                self.obj.phase = 2
            self.cur_fs = (self.cur_fs + self.ctfs) // 2
            rot = -self.obj.velocity.get_net_rotation()
            self.set_rotation((self.rot + rot) // 2)
            pg.draw.circle(game.get_game().displayer.canvas, (255, 0, 0),
                           position.displayed_position(self.sps), self.cur_fs / game.get_game().player.get_screen_scale(), 5)
            apx, apy = game.get_game().player.obj.pos[0] - self.sps[0], game.get_game().player.obj.pos[1] - self.sps[1]
            if vector.distance(apx, apy) > self.cur_fs:
                apx *= self.cur_fs / vector.distance(apx, apy)
                apy *= self.cur_fs / vector.distance(apx, apy)
                game.get_game().player.obj.pos = (self.sps[0] + apx, self.sps[1] + apy)

    class GhostFace(Entity):
        NAME = 'Ghost Face'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('chaos_ingot', 1, 5, 12),
            IndividualLoot('wierd_essence', 0.5, 10, 22),
            ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_ghost_face'], GhostFaceAI, 30000)

    class SadFace(Entity):
        NAME = 'Sad Face'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('chaos_ingot', 1, 5, 12),
            IndividualLoot('wierd_essence', 0.5, 10, 22),
            ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_sad_face'], GhostFaceAI, 40000)
            self.obj.appear_time = 80
            self.obj.appear_rate = 7
            self.obj.TOUCHING_DAMAGE = 500

    class AngryFace(Entity):
        NAME = 'Angry Face'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('chaos_ingot', 1, 5, 12),
            IndividualLoot('wierd_essence', 0.5, 10, 22),
            ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_angry_face'], GhostFaceAI, 20000)
            self.obj.appear_time = 30
            self.obj.appear_rate = 2
            self.obj.TOUCHING_DAMAGE = 380

    class TimeTrap(Entity):
        NAME = 'Timetrap'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('chaos_ingot', 1, 5, 12),
            IndividualLoot('time_essence', 0.5, 10, 22),
            ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_timetrap'], BuildingAI, 100000)
            self.obj.TOUCHING_DAMAGE = 300

        def update(self):
            super().update()
            px, py = game.get_game().player.obj.pos
            px -= self.obj.pos[0]
            py -= self.obj.pos[1]
            if vector.distance(px, py) < 200:
                game.get_game().player.obj.pos = self.obj.pos
            elif vector.distance(px, py) < 2000:
                pg.draw.line(game.get_game().displayer.canvas, (0, 255, 0),
                             position.displayed_position(self.obj.pos),
                             position.displayed_position(game.get_game().player.obj.pos), 10)
                game.get_game().player.obj.pos = (game.get_game().player.obj.pos[0] - px // 20, game.get_game().player.obj.pos[1] - py // 20)
            pg.draw.circle(game.get_game().displayer.canvas, (255, 0, 0),
                           position.displayed_position(self.obj.pos), 200 / game.get_game().player.get_screen_scale(), 5)
            pg.draw.circle(game.get_game().displayer.canvas, (100, 100, 255),
                           position.displayed_position(self.obj.pos), 2000 / game.get_game().player.get_screen_scale(), 5)

    class TimeFlower(Entity):
        NAME = 'Timeflower'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('chaos_ingot', 1, 5, 12),
            IndividualLoot('time_essence', 0.5, 10, 22),
            ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_timeflower'], SoulFlowerAI, 100000)
            self.obj.TOUCHING_DAMAGE = 560

        def update(self):
            super().update()
            px, py = game.get_game().player.obj.pos
            px -= self.obj.pos[0]
            py -= self.obj.pos[1]
            if vector.distance(px, py) < 100:
                game.get_game().player.obj.pos = self.obj.pos
            elif vector.distance(px, py) < 1000:
                pg.draw.line(game.get_game().displayer.canvas, (0, 255, 0),
                             position.displayed_position(self.obj.pos),
                             position.displayed_position(game.get_game().player.obj.pos), 10)
                game.get_game().player.obj.pos = (game.get_game().player.obj.pos[0] - px // 40, game.get_game().player.obj.pos[1] - py // 40)
            pg.draw.circle(game.get_game().displayer.canvas, (255, 0, 0),
                           position.displayed_position(self.obj.pos), 100 / game.get_game().player.get_screen_scale(), 5)
            pg.draw.circle(game.get_game().displayer.canvas, (100, 100, 255),
                           position.displayed_position(self.obj.pos), 1000 / game.get_game().player.get_screen_scale(), 5)

    class Times(Entity):
        NAME = 'Times'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_times'], FastBulletAI, 10 ** 9)
            self.obj.MASS = 1000
            self.obj.rot = rot
            self.obj.speed = 5000
            self.tick = 0

        def update(self):
            self.tick += 1
            if self.tick < 10:
                ax, ay = vector.rotation_coordinate(self.obj.rot)
                pg.draw.line(game.get_game().displayer.canvas, (255, 0, 0),
                             position.displayed_position(self.obj.pos),
                             position.displayed_position((self.obj.pos[0] + ax * 3000, self.obj.pos[1] + ay * 3000)), 3)

            else:
                super().update()
                self.damage()
                self.hp_sys.hp -= 25 * 10 ** 6

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 220:
                game.get_game().player.hp_sys.damage(440, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class TimeNumeral(Entity):
        NAME = 'Time Numeral'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])

        def __init__(self, pos, hp_sys, no: int):
            super().__init__(pos, game.get_game().graphics[f'entity_clock{no}'], BuildingAI, hp_sys=hp_sys)
            self.obj.MASS = 5000
            self.obj.TOUCHING_DAMAGE = 800
            self.obj.IS_OBJECT = False

    class CLOCK(Entity):
        NAME = 'CLOCK'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('chaos_ingot', 1, 100, 120),
            IndividualLoot('time_essence', 1, 30, 45),
            IndividualLoot('time_fountain', 1, 1, 1),
            ])
        IS_MENACE = True

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_clock'], BuildingAI, 6000000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 50
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 50
            self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 50
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 25
            self.obj.TOUCHING_DAMAGE = 9999
            self.phase = 0
            self.tick = 0
            self.rt = 0
            self.dt = 0
            self.nums = [Entities.TimeNumeral(self.obj.pos, self.hp_sys, i) for i in range(1, 13)]
            for e in self.nums:
                game.get_game().entities.append(e)

        def update(self):
            super().update()
            self.tick += 1
            if self.phase == 0:
                self.rt += 3
                if self.tick < 100:
                    self.dt += 12
                if self.tick > 120:
                    self.tick = 0
                    self.phase = 1
                    for e in self.nums:
                        e.obj.IS_OBJECT = True
            else:
                px, py = game.get_game().player.obj.pos
                px -= self.obj.pos[0]
                py -= self.obj.pos[1]
                if vector.distance(px, py) > self.dt:
                    ap = self.dt / vector.distance(px, py)
                    game.get_game().player.obj.pos = (self.obj.pos[0] + ap * px, self.obj.pos[1] + ap * py)
                    px *= ap
                    py *= ap
                if self.phase == 1:
                    if self.tick % 32 == 1:
                        game.get_game().entities.append(Entities.Times(self.obj.pos, vector.coordinate_rotation(px, py)))
                elif self.phase == 2:
                    if self.tick % 8 == 1:
                        for ar in range(0, 360, 90):
                            game.get_game().entities.append(Entities.Times(self.obj.pos, ar + self.tick // 8 * 15))
                elif self.phase == 3:
                    if self.tick % 8 == 1:
                        for ar in range(0, 360, 180):
                            game.get_game().entities.append(Entities.Times(self.obj.pos, ar + self.tick // 8 * 5))
                        game.get_game().entities.append(Entities.Times(self.obj.pos, vector.coordinate_rotation(px, py)))
                elif self.phase == 4:
                    if self.tick % 8 == 1:
                        for ar in range(0, 360, 60):
                            game.get_game().entities.append(Entities.Times(self.obj.pos, ar + self.tick // 8 * 2))
                elif self.phase == 5:
                    rt = vector.coordinate_rotation(px, py)
                    if self.tick % 8 == 1:
                        if self.tick % 16 == 1:
                            st = -60
                        else:
                            st = -45
                        for ar in range(st, -st + 1, 30):
                            game.get_game().entities.append(Entities.Times(self.obj.pos, rt + ar))
                        game.get_game().entities.append(Entities.Times(self.obj.pos, rt + 180))
                elif self.phase == 6:
                    if self.tick % 32 == 1:
                        for e in self.nums:
                            epx, epy = game.get_game().player.obj.pos
                            epx -= e.obj.pos[0]
                            epy -= e.obj.pos[1]
                            game.get_game().entities.append(Entities.Times(e.obj.pos, vector.coordinate_rotation(epx, epy)))
                elif self.phase == 7:
                    if self.tick % 12 == 1:
                        for e in self.nums:
                            epx, epy = game.get_game().player.obj.pos
                            epx -= e.obj.pos[0]
                            epy -= e.obj.pos[1]
                            game.get_game().entities.append(Entities.Times(e.obj.pos, vector.coordinate_rotation(epx, epy)))
                elif self.phase == 8:
                    if self.tick % 8 == 1:
                        for e in self.nums:
                            epx, epy = self.obj.pos
                            epx -= e.obj.pos[0]
                            epy -= e.obj.pos[1]
                            game.get_game().entities.append(Entities.Times(e.obj.pos, vector.coordinate_rotation(epx, epy)))
                        game.get_game().entities.append(Entities.Times(self.obj.pos, vector.coordinate_rotation(px, py)))
                elif self.phase == 9:
                    if self.tick % 32 == 1:
                        for e in self.nums:
                            epx, epy = self.obj.pos
                            epx -= e.obj.pos[0]
                            epy -= e.obj.pos[1]
                            game.get_game().entities.append(Entities.Times(e.obj.pos, vector.coordinate_rotation(epx, epy)))
                    if self.tick % 16 == 1:
                        for ar in range(0, 360, 180):
                            game.get_game().entities.append(Entities.Times(self.obj.pos, ar + self.tick // 8 * 2))
                elif self.phase == 10:
                    if self.tick % 8 == 1:
                        for ar in range(0, 360, 30):
                            game.get_game().entities.append(Entities.Times(self.obj.pos, ar + self.tick // 8 * 18))
                elif self.phase == 11:
                    if self.tick % 16 == 1:
                        for e in self.nums:
                            epx, epy = game.get_game().player.obj.pos
                            epx -= e.obj.pos[0]
                            epy -= e.obj.pos[1]
                            game.get_game().entities.append(Entities.Times(e.obj.pos, vector.coordinate_rotation(epx, epy)))
                    if self.tick % 8 == 1:
                        game.get_game().entities.append(Entities.Times(self.obj.pos, vector.coordinate_rotation(px, py)))
                elif self.phase == 12:
                    if self.tick % 6 == 1:
                        for e in self.nums:
                            epx, epy = game.get_game().player.obj.pos
                            epx -= e.obj.pos[0]
                            epy -= e.obj.pos[1]
                            game.get_game().entities.append(Entities.Times(e.obj.pos, vector.coordinate_rotation(epx, epy)))
                    if self.tick % 2 == 1:
                        game.get_game().entities.append(Entities.Times(self.obj.pos, vector.coordinate_rotation(px, py)))
                if self.hp_sys.hp < self.hp_sys.max_hp * (1 - self.phase / 12):
                    self.phase += 1
                    self.set_rotation(self.rot)
                self.rt += 3 + self.phase * 30
                self.dt = int(1500 + 300 * math.sin(self.tick / 10))
            for i, e in enumerate(self.nums):
                ax, ay = vector.rotation_coordinate(self.rt % 360 + i * 30)
                e.obj.pos = (self.obj.pos[0] + ax * self.dt,
                             self.obj.pos[1] + ay * self.dt)


def entity_spawn(entity: type(Entities.Entity), to_player_min=1500, to_player_max=2500, number_factor=0.5,
                 target_number=5, rate=0.5):
    game_obj = game.get_game()
    if random.random() < max(0.0, (len([e for e in game_obj.entities if
                                        type(e) is entity]) - target_number) * number_factor / 10) - rate / 50 + 1:
        return
    player = game_obj.player
    dist = random.randint(to_player_min, to_player_max)
    r = random.random() * 2 * math.pi
    px, py = player.obj.pos[0] + dist * math.cos(r), player.obj.pos[1] + dist * math.sin(r)
    game_obj.entities.append(entity((px, py)))


def spawn_sandstorm():
    hp_sys = hp_system.HPSystem(15200)
    hp_sys.resistances[damages.DamageTypes.PIERCING] = 2.5
    for i in range(2):
        e = Entities.SandStorm((0, 0), hp_sys, i * 180)
        e.IS_MENACE = i == 1
        game.get_game().entities.append(e)
