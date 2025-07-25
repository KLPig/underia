import copy
import math
import random

import pygame as pg

from physics import mover, vector
from resources import position
from underia import game, styles, inventory
from values import hp_system, damages, effects, elements
import constants
from visual import particle_effects as pef, fade_circle as fc, draw, cut_effects as cef
import functools


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
    def __init__(self, loot_list: list[Loots | IndividualLoot | SelectionLoot]):
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
    SIGHT_DISTANCE = 800

    IDLE_TIME = 100
    IDLE_SPEED = 120
    IDLE_CHANGER = 50

    SPEED = 1.0

    def __init__(self, pos):
        super().__init__(pos)
        self.touched_player = False
        self.cur_target = None
        self.idle_timer = 0
        self.idle_rotation = random.randint(0, 360)
        self.time_touched_player = constants.INFINITY

    def update(self):
        super().update()
        self.get_target()
        if self.time_touched_player < constants.INFINITY:
            self.time_touched_player += 1
        self.time_touched_player *= not self.touched_player

    def apply_force(self, force):
        super().apply_force(force * self.SPEED)

    def idle(self):
        if not self.idle_rotation and random.randint(0, 360):
            self.idle_rotation = random.randint(0, 360)
        if self.idle_timer > self.IDLE_TIME // 5 + random.randint(-50, 50):
            self.idle_timer = 0
            self.idle_rotation += random.randint(-self.IDLE_CHANGER, self.IDLE_CHANGER) // 5
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
                if new_d * self.PREFER_DISTANCE < min(d, self.SIGHT_DISTANCE):
                    self.cur_target = e
                    d = new_d

        if self.cur_target is not None:
            d = vector.distance(self.pos[0] - self.cur_target.pos[0],
                                self.pos[1] - self.cur_target.pos[1])
            if d > self.SIGHT_DISTANCE * self.PREFER_DISTANCE:
                self.cur_target = None


    def on_update(self):
        pass


class TreeMonsterAI(MonsterAI):
    MASS = 200
    FRICTION = 0.8
    SIGHT_DISTANCE = 300
    PREFER_DISTANCE = 1.1

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            if self.time_touched_player > 30:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 280))
        else:
            pass


class CactusAI(TreeMonsterAI):
    TOUCHING_DAMAGE = 30


class EyeAI(MonsterAI):
    MASS = 60
    FRICTION = 0.96
    TOUCHING_DAMAGE = 16
    SIGHT_DISTANCE = 600

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
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py) + 180, 30))
            elif self.timer < 190:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 30))
            elif self.timer < 195:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 180))
        else:
            self.idle()


class SlowMoverAI(MonsterAI):
    MASS = 200
    FRICTION = 0.8

    SIGHT_DISTANCE = 1100

    IDLE_TIME = 120
    IDLE_SPEED = 100

    def __init__(self, pos):
        super().__init__(pos)
        self.idle_timer = 0
        self.idle_rotation = 0

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            if self.time_touched_player > 30:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 150))
            else:
                self.idle()
        else:
            self.idle()

class OrgeAI(SlowMoverAI):
    MASS = 6000
    FRICTION = 0.6
    TOUCHING_DAMAGE = 368
    IDLE_SPEED = 10000
    SIGHT_DISTANCE = 3600

    def __init__(self, pos):
        super().__init__(pos)
        self.timer = 0
        self.state = 0

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            if self.time_touched_player < 80:
                self.idle()
            elif self.state == 0:
                self.FRICTION = 0.6
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 12000))
            elif self.state == 2:
                self.FRICTION = 0.75
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 72000))
            self.timer += 1
            if random.randint(0, self.timer) > 100:
                self.state = (self.state + 1) % 3
        else:
            self.idle()

class FluffBallAI(MonsterAI):
    MASS = 100
    FRICTION = 0.9
    TOUCHING_DAMAGE = 64
    SIGHT_DISTANCE = 750

    IDLE_TIME = 60
    IDLE_SPEED = 180

    def __init__(self, pos):
        super().__init__(pos)
        self.timer = 0

    def on_update(self):
        self.timer = (self.timer + 1) % 120
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            if self.touched_player:
                self.timer = -100
            if self.timer > 0:
                self.apply_force(vector.Vector(vector.coordinate_rotation(1, 0), px / 2))
                self.apply_force(vector.Vector(vector.coordinate_rotation(0, 1), py / 6))
        else:
            self.idle()

class RangedAI(MonsterAI):
    MASS = 200
    FRICTION = 0.85

    IDLE_TIME = 80
    IDLE_SPEED = 120

    def __init__(self, pos):
        super().__init__(pos)
        self.idle_timer = 0
        self.idle_rotation = 0
        self.shoot_distance = 500
        self.spd = 180

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            if vector.distance(px, py) > self.shoot_distance:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), self.spd))
            else:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), -1.2 * self.spd))
        else:
            self.idle()

class CleverRangedAI(RangedAI):
    def on_update(self):
        super().on_update()
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py) + 90, self.spd / 2))

class SkyCubeFighterAI(MonsterAI):
    MASS = 5000
    FRICTION = 0.9
    TOUCHING_DAMAGE = 288

    def __init__(self, pos):
        super().__init__(pos)
        self.tick = 0
        self.state = 0
        self.rt = 0

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            if self.state == 0:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py),
                                               vector.distance(px, py) * 12))
            elif self.state == 1:
                if self.tick % 80 < 5:
                    self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 50))
                    self.rt = vector.coordinate_rotation(px, py)
                elif self.tick % 80 < 50:
                    self.apply_force(vector.Vector(self.rt, 12000))
                else:
                    self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 6000))
            if self.tick > 300:
                self.state = (self.state + 1) % 2
                self.tick = 0

class SkyCubeRangerAI(SkyCubeFighterAI):
    MASS = 4000
    TOUCHING_DAMAGE = 180

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), (vector.distance(px, py) - 1200) * 12))

class SkyCubeBlockerAI(SkyCubeFighterAI):
    MASS = 8000
    TOUCHING_DAMAGE = 140

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 10000))

class MagmaCubeAI(SlowMoverAI):
    TOUCHING_DAMAGE = 66


class CloseBloodflowerAI(SlowMoverAI):
    MASS = 240
    TOUCHING_DAMAGE = 24


class BloodflowerAI(CloseBloodflowerAI):
    FRICTION = 0.97
    TOUCHING_DAMAGE = 45

    def __init__(self, pos):
        super().__init__(pos)
        self.timer = 0
        self.prot = 180

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
                else:
                    self.apply_force(vector.Vector(vector.coordinate_rotation(px, py) + self.prot, 180))
                if self.touched_player:
                    self.timer = 0
                    self.prot = random.randint(150, 210)
            else:
                self.idle()
        else:
            self.idle()


class SoulFlowerAI(BloodflowerAI):
    TOUCHING_DAMAGE = 128

class SnowDrakeAI(BloodflowerAI):
    TOUCHING_DAMAGE = 220
    MASS = 220

class CellsAI(EyeAI):
    TOUCHING_DAMAGE = 128
    MASS = 720
    SPEED = 13.5

class IceCapAI(SlowMoverAI):
    MASS = 200
    TOUCHING_DAMAGE = 188
    SPEED = 1.5

class MechanicEyeAI(CellsAI):
    MASS = 200
    TOUCHING_DAMAGE = 188
    SPEED = 5.5
    SIGHT_DISTANCE = 500

class RedWatcherAI(SlowMoverAI):
    FRICTION = 0.92
    MASS = 400
    TOUCHING_DAMAGE = 54
    SPEED = 1.5

class RuneRockAI(SlowMoverAI):
    MASS = 240
    FRICTION = 0.9
    TOUCHING_DAMAGE = 88
    SPEED = 1.2

class BuildingAI(MonsterAI):
    MASS = 2000
    FRICTION = 0.5
    TOUCHING_DAMAGE = 0

class WorldsFruitAI(MonsterAI):
    MASS = 5000
    FRICTION = 0.9
    TOUCHING_DAMAGE = 64
    SIGHT_DISTANCE = 99999

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            if vector.distance(px, py) < 1000:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), vector.distance(px, py) * 18))
            else:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 6000))
        else:
            self.idle()

class AppleProtectionAI(MonsterAI):
    MASS = 40
    FRICTION = 0.9
    TOUCHING_DAMAGE = 48
    VITAL = True
    SIGHT_DISTANCE = 99999

    def __init__(self, pos):
        super().__init__(pos)
        self.upper: mover.Mover | None = None

    def on_update(self):
        if self.upper is not None:
            vx, vy = self.upper.pos
            vx -= self.pos[0]
            vy -= self.pos[1]
            self.apply_force(vector.Vector(vector.coordinate_rotation(vx, vy),
                                           vector.distance(vx, vy) / 2))

class AppleAttackAI(MonsterAI):
    MASS = 40
    FRICTION = 0.9
    TOUCHING_DAMAGE = 48
    VITAL = True
    SIGHT_DISTANCE = 99999

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), vector.distance(px, py) / 3))
        else:
            self.idle()


class AbyssEyeAI(BuildingAI):
    MASS = 6000
    FRICTION = 0.1
    TOUCHING_DAMAGE = 100

class TrueEyeAI(MonsterAI):
    MASS = 300
    FRICTION = 0.97
    TOUCHING_DAMAGE = 45
    SIGHT_DISTANCE = 99999

    def __init__(self, pos):
        super().__init__(pos)
        self.timer = 0
        self.phase = 0
        self.trt = 0

    def on_update(self):
        self.timer = (self.timer + 1) % (350 + self.phase * 100)
        player = game.get_game().player
        px = player.obj.pos[0] - self.pos[0]
        py = player.obj.pos[1] - self.pos[1]
        if 0 < self.timer < 100:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py) + 180, 20 + self.phase * 50))
        elif self.timer < 200:
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 120 + self.phase * 240))
        elif self.timer % (50 - self.phase * 10) == 0:
            self.trt = vector.coordinate_rotation(px, py)
        elif self.timer % (50 - self.phase * 10) < 12:
            self.apply_force(vector.Vector(self.trt, 2000 - self.phase * 200))

class DragonAI(MonsterAI):
    MASS = 8800
    FRICTION = 0.8
    SIGHT_DISTANCE = 99999
    TOUCHING_DAMAGE = 640
    IS_OBJECT = False

    def __init__(self, pos):
        super().__init__(pos)
        self.state = 0
        self.d_rot = 0

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px, py = player.pos[0] - self.pos[0], player.pos[1] - self.pos[1]
            self.d_rot = vector.coordinate_rotation(px, py) - self.velocity.get_net_rotation()
            if self.d_rot > 180:
                self.d_rot -= 360
            elif self.d_rot < -180:
                self.d_rot += 360
            if self.state == 0:
                self.apply_force(vector.Vector(self.velocity.get_net_rotation(), max(0, 128000 - self.d_rot * 400)))
                self.apply_force(vector.Vector(self.velocity.get_net_rotation() + 90, self.d_rot * 500))
                self.IS_OBJECT = False
            elif self.state == 1:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 80000))
                self.IS_OBJECT = True
            else:
                self.IS_OBJECT = True

class QuarkGhostAI(MonsterAI):
    MASS = 8800
    FRICTION = 0.8
    SIGHT_DISTANCE = 99999
    TOUCHING_DAMAGE = 640
    IS_OBJECT = False

    def __init__(self, pos):
        super().__init__(pos)
        self.state = 0
        self.d_rot = 0

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px, py = player.pos[0] - self.pos[0], player.pos[1] - self.pos[1]
            self.d_rot = vector.coordinate_rotation(px, py) - self.velocity.get_net_rotation()
            if self.d_rot > 180:
                self.d_rot -= 360
            elif self.d_rot < -180:
                self.d_rot += 360
            self.apply_force(vector.Vector(self.velocity.get_net_rotation(), max(0, 150000 - self.d_rot * 300)))
            self.apply_force(vector.Vector(self.velocity.get_net_rotation() + 90, self.d_rot * 300))
            self.IS_OBJECT = True

class NagaAI(MonsterAI):
    MASS = 15000
    FRICTION = 0.8
    SIGHT_DISTANCE = 9999
    TOUCHING_DAMAGE = 2200
    IS_OBJECT = False

    def __init__(self, pos):
        super().__init__(pos)
        self.state = 0
        self.d_rot = 0

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px, py = player.pos[0] - self.pos[0], player.pos[1] - self.pos[1]
            self.d_rot = vector.coordinate_rotation(px, py) - self.velocity.get_net_rotation()
            if self.d_rot > 180:
                self.d_rot -= 360
            elif self.d_rot < -180:
                self.d_rot += 360
            if self.state == 0:
                self.apply_force(vector.Vector(self.velocity.get_net_rotation(), max(0, 320000 - self.d_rot * 640)))
                self.apply_force(vector.Vector(self.velocity.get_net_rotation() + 90, self.d_rot * 880))
            elif self.state == 1:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 3600000))
            else:
                pass

class LifeWatcherAI(MonsterAI):
    MASS = 2400
    FRICTION = 0.97
    TOUCHING_DAMAGE = 188
    SIGHT_DISTANCE = 99999

    def __init__(self, pos):
        super().__init__(pos)
        self.timer = 0
        self.phase = 0
        self.trt = 0
        self.state = 0

    def on_update(self):
        self.timer = (self.timer + 1) % 500
        player = game.get_game().player
        px = player.obj.pos[0] - self.pos[0]
        py = player.obj.pos[1] - self.pos[1]
        if 0 < self.timer < 100:
            self.state = 0
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py) + 180, 1200))
        elif self.timer < 200:
            self.state = 1
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 1800))
        elif self.timer % 50 == 0:
            self.trt = vector.coordinate_rotation(px, py)
        elif self.timer % 50 < 18:
            self.state = 2
            self.apply_force(vector.Vector(self.trt, 18800))
        else:
            self.state = 3



class StarAI(MonsterAI):
    FRICTION = .9
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
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 400))
            if self.touched_player:
                self.pos << (self.pos[0] + px * 6,
                            self.pos[1] + py * 6)
        else:
            self.idle()


class LeafAI(StarAI):
    MASS = 320
    TOUCHING_DAMAGE = 288
    SPEED = 1.8

class MagmaKingAI(MonsterAI):
    FRICTION = 0.9
    MASS = 360
    TOUCHING_DAMAGE = 72
    SIGHT_DISTANCE = 99999
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
    SIGHT_DISTANCE = 99999

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
        self.pos << ((self.pos[0] + px * 6) / 7, (self.pos[1] + py * 6) / 7)


class AbyssRuneAI(MonsterAI):
    FRICTION = 0.9
    MASS = 100
    TOUCHING_DAMAGE = 150

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
        self.pos << e[0].obj.pos
        ax, ay = vector.rotation_coordinate(self.rot)
        self.pos << (self.pos[0] + ax * self.d, self.pos[1] + ay * self.d)


class MagmaKingFireballAI(MonsterAI):
    FRICTION = 1
    MASS = 200
    TOUCHING_DAMAGE = 0
    IS_OBJECT = False

    def __init__(self, pos):
        super().__init__(pos)
        self.rot = 0
        self.SPEED *= 4

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
    TOUCHING_DAMAGE = 360

    PREFER_DISTANCE = 2
    SIGHT_DISTANCE = 99999

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
    TOUCHING_DAMAGE = 440

    PREFER_DISTANCE = 1
    SIGHT_DISTANCE = 99999

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
    TOUCHING_DAMAGE = 580

    PREFER_DISTANCE = 3
    SIGHT_DISTANCE = 99999

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
    TOUCHING_DAMAGE = 690

    IDLE_SPEED = 1500
    SIGHT_DISTANCE = 99999

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
                    self.pos << (px + self.pos[0] + self.ax * 600, py + self.pos[1] + self.ay * 600)
                dialogs = [
                    ['I CAN DO ANYTHING!', 'CHAOS, CHAOS!', 'SHALL WE PLAY THE RING-AROUND?', ],
                    ['HEE, HEE, HAVING FUN?! JOIN THE CLUB!', 'THESE CURTAINS ARE REALLY ON FIRE!',
                     'MY HEARTS GO OUT TO ALL YOU SINNERS!', 'WHO KEEPS SPINNING THE WORLD AROUND?'],
                    ['ENOUGH!! YOU KIDS TIRED ME UP!', 'YOU KIDS ARE REALLY KEEPING UP!',
                     'NU-HA!! I NEVER HAD SUCH FUN, FUN!!', 'A BEAUTY IS JOYING IN MY HEART!'],
                    ['THIS BODY CANNOT BE KILLED!', 'PLEASE, IT\'S JUST A SIMPLE CHAOS.',
                     'THIS IS IT, BOISENGIRLS! SEE YA!']
                ]
                if self.state == 1:
                    if random.randint(0, 1):
                        game.get_game().play_sound('chaos_chaos', 0.99 ** int(vector.distance(px, py) / 10))
                    else:
                        game.get_game().play_sound('i_can_do_anything', 0.99 ** int(vector.distance(px, py) / 10))
                    if random.randint(0, 1):
                        game.get_game().dialog.dialog(random.choice(dialogs[self.phase]))
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
    TOUCHING_DAMAGE = 790
    SIGHT_DISTANCE = 99999

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
    TOUCHING_DAMAGE = 540
    SIGHT_DISTANCE = 1200

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
                if self.tick > self.appear_rate * 5:
                    self.tick = 0
                    self.pos << (self.pos[0] + px // self.appear_rate, self.pos[1] + py // self.appear_rate)

class JevilKnifeAI(SlowMoverAI):
    MASS = 3000
    FRICTION = 0.95
    TOUCHING_DAMAGE = 540

    def __init__(self, pos):
        super().__init__(pos)
        self.r = 0
        self.d = 0
        self.upper = None

    def on_update(self):
        self.r = (self.r + 1) % 360
        self.d = (self.d + 3) % 240
        pos = self.upper.cur_target.pos if self.upper.cur_target is not None else (0, 0)
        px = pos[0] - self.pos[0] + ((math.cos(self.d / 120 * math.pi) + 1) * 500 + 500) * math.cos(math.radians(self.r))
        py = pos[1] - self.pos[1] + ((math.cos(self.d / 120 * math.pi) + 1) * 500 + 500) * math.sin(math.radians(self.r))
        self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), vector.distance(px, py) * 50))


class TheCPUAI(SlowMoverAI):
    MASS = 10000
    FRICTION = 0.95
    TOUCHING_DAMAGE = 180
    SIGHT_DISTANCE = 99999

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
                self.pos << (px + player.pos[0], py + player.pos[1])
            self.tick += 1
            if self.state == 0:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 15000))
            else:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), vector.distance(px, py) * 40))

class MechanicMedusaAI(TheCPUAI):

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            if self.tick < 0:
                self.tick += 1
                return
            if self.tick > 100:
                self.state = (self.state + 1) % 3
                self.tick = 0
                if random.randint(0, 1):
                    px *= -1
                if random.randint(0, 1):
                    py *= -1
                if self.phase == 2 and random.randint(0, 1):
                    t = px
                    px = py
                    py = t
                self.pos << (px + player.pos[0], py + player.pos[1])
            self.tick += 1
            if self.state == 0:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 15000))
            elif self.state == 1:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), vector.distance(px, py) * 40))
            else:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py - 1000),
                                               vector.distance(px, py - 1000) * 80))


class GreedAI(SlowMoverAI):
    MASS = 400
    FRICTION = 0.95
    TOUCHING_DAMAGE = 0
    TD = 220
    KB = 100
    SIGHT_DISTANCE = 99999

    def __init__(self, pos):
        super().__init__(pos)
        self.tick = 0
        self.state = 0
        self.phase = 1
        self.rot = 0
        self.dp = pos

    def on_update(self):
        self.pos << self.dp
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
                self.pos << (self.pos[0] + px // 5, self.pos[1] + py // 5)
                self.velocity.clear()
                self.velocity.add(vector.Vector(0, self.KB))
                if self.state == 1:
                    self.rot = (self.rot + 3) % 360
                elif self.state == 3:
                    self.rot = (self.rot + 10) % 360
                else:
                    draw.line(game.get_game().displayer.canvas, (255, 0, 0), position.displayed_position(self.pos),
                                 position.displayed_position((self.pos[0] + px - 800 * ax, self.pos[1] + py - 800 * ay)),
                                 width=50)
            self.dp = self.pos

class CardBombAI(SlowMoverAI):
    MASS = 600
    FRICTION = 0.95
    TOUCHING_DAMAGE = 320

    def __init__(self, pos):
        super().__init__(pos)

    def update(self):
        self.apply_force(vector.Vector(180, 1200))

class GodsEyeAI(MonsterAI):
    MASS = 1200
    FRICTION = 0.95
    TOUCHING_DAMAGE = 1080
    SIGHT_DISTANCE = 99999
    SPEED = 0.5

    def __init__(self, pos):
        super().__init__(pos)
        self.tick = 0
        self.state = 0
        self.rot = 0
        self.phs = 0

    def update(self):
        px, py = self.cur_target.pos if self.cur_target is not None else (0, 0)
        super().update()
        self.tick += 1
        if self.state == 0:
            pass
        elif self.state <= 2:
            ax = px - self.pos[0]
            ay = py - self.pos[1]
            ax += 1000 if self.state == 1 else -1000
            self.apply_force(vector.Vector(vector.coordinate_rotation(ax, ay),
                                           vector.distance(ax, ay) * 24))
        elif self.state <= 4:
            rt = (self.tick * 5 + self.state * 180) % 360
            ax, ay = vector.rotation_coordinate(rt)
            ax = ax * 1500 + px - self.pos[0]
            ay = ay * 1500 + py - self.pos[1]
            self.apply_force(vector.Vector(vector.coordinate_rotation(ax, ay),
                                           vector.distance(ax, ay) * 18))
        elif self.state == 5:
            ax = px - self.pos[0]
            ay = py - self.pos[1]
            if self.tick % (30 - self.phs * 8) < 3:
                self.rot = vector.coordinate_rotation(ax, ay)
            elif self.tick % (30 - self.phs * 8) < 20:
                self.apply_force(vector.Vector(self.rot, 18000 + self.phs * 20000))
            else:
                self.apply_force(vector.Vector(vector.coordinate_rotation(ax, ay), 1200))
        elif self.state == 6:
            ax = px - self.pos[0]
            ay = py - self.pos[1]
            ay -= 2000
            self.apply_force(vector.Vector(vector.coordinate_rotation(ax, ay),
                                           vector.distance(ax, ay) * 24))

class WorldsTreeAI(MonsterAI):
    MASS = 3200
    FRICTION = 0.95
    TOUCHING_DAMAGE = 2000
    SIGHT_DISTANCE = 99999

    def __init__(self, pos):
        super().__init__(pos)
        self.tick = 0
        self.state = 0
        self.rot = 0

    def update(self):
        px, py = self.cur_target.pos if self.cur_target is not None else (0, 0)
        super().update()
        self.tick += 1
        if self.state == 0:
            pass
        elif self.state == 1:
            ax = px - self.pos[0]
            ay = py - self.pos[1]
            ay -= 1000
            self.apply_force(vector.Vector(vector.coordinate_rotation(ax, ay),
                                           vector.distance(ax, ay) * 20))
        elif self.state == 2:
            ax = px - self.pos[0]
            ay = py - self.pos[1]
            self.apply_force(vector.Vector(vector.coordinate_rotation(ax, ay),
                                           vector.distance(ax, ay) * 6 + 8000))

@functools.lru_cache(maxsize=int(constants.MEMORY_USE * .1))
def entity_get_surface(display_mode, rot, scale, img):
    if img.get_width() + img.get_height() > 30 * scale:
        if display_mode == Entities.DisplayModes.DIRECTIONAL:
            d_img = pg.transform.rotate(img, rot)
        elif display_mode == Entities.DisplayModes.BIDIRECTIONAL:
            if rot % 360 < 180:
                d_img = pg.transform.flip(img, True, False)
            else:
                d_img = img
        else:
            d_img = img
        return pg.transform.scale(d_img,(d_img.get_width() / scale, d_img.get_height() / scale))
    else:
        return pg.Surface((img.get_width() / scale, img.get_height() / scale))

class Entities:

    class DisplayModes:
        NO_IMAGE = 0
        DIRECTIONAL = 1
        BIDIRECTIONAL = 2
        NO_DIRECTION = 3

    class Entity:
        NAME = 'Entity'
        DIVERSITY = True
        DISPLAY_MODE = 0
        LOOT_TABLE = LootTable([])
        ENTITY_TAGS = []
        IS_MENACE = False
        VITAL = False
        PHASE_SEGMENTS = []
        ADJECTIVES = [
            ['Protected', 1.05, 5, 30, 5],
            ['Armed', 1.11, 8, 60, 15],
            ['Tank', 1.25, 20, 160, 20],

            ['Tenacious', 1.6, 0, -20, -10],
            ['Lifelong', 1.8, 0, 0, 0],
            ['Swift', 0.8, -2, -50, -2],

            ['Elite', 5, 28, 80, 30],
        ]

        SOUND_SPAWN = None
        SOUND_HURT = None
        SOUND_DEATH = None

        ENO = 0

        BOSS_NAME = ''

        def __init__(self, pos, img=None, ai: type(MonsterAI) = MonsterAI, hp=120,
                     hp_sys: hp_system.HPSystem | None = None):
            self.obj: MonsterAI | mover.Mover = ai(pos)
            self.show_bar = True
            if hp_sys is None:
                self.hp_sys = hp_system.HPSystem(hp)
            else:
                self.hp_sys = hp_system.SubHPSystem(hp_sys)
                self.show_bar = False
            self.img: pg.Surface | None = img
            self.img_idx = [k for k, v in game.get_game().graphics.graphics.items() if k.startswith('entity') and v == self.img]
            if len(self.img_idx):
                self.img_idx = self.img_idx[0]
            else:
                self.img_idx = 'entity_null'
            self.d_img = self.img
            self.rot = 0
            self.add_star = False
            self.touched_player = False
            try:
                if self.SOUND_SPAWN is not None:
                    self.play_sound('spawn_' + self.SOUND_SPAWN)
            except ValueError:
                pass
            self.hp_sys.SOUND_HURT = self.SOUND_HURT
            if self.IS_MENACE:
                self.hp_sys.displayed_hp = 0
            self.adj = ''
            if not random.randint(0, 3) and not self.IS_MENACE and self.DIVERSITY:
                self.adj, hp_t, def_a, mass_a, _atk_a = random.choice(self.ADJECTIVES)
                self.hp_sys.max_hp *= hp_t
                self.hp_sys.hp = self.hp_sys.max_hp
                self.obj.MASS += mass_a
                self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] += def_a
                self.hp_sys.defenses[damages.DamageTypes.MAGICAL] += def_a
                self.hp_sys.defenses[damages.DamageTypes.PIERCING] += def_a
                self.hp_sys.defenses[damages.DamageTypes.ARCANE] += def_a
                self.obj.TOUCHING_DAMAGE += _atk_a
            self.hp_sys.max_hp *= 0.9 + 0.2 * random.random()
            self.hp_sys.hp = self.hp_sys.max_hp
            self.o_atk = 0
            self.show_boss = False
            self.ueid = Entities.Entity.ENO
            Entities.Entity.ENO += 1

            self.hp_sys.max_hp *= [.6, 1.0, 1.9, 2.4][constants.DIFFICULTY]
            self.hp_sys.hp = self.hp_sys.max_hp

            self.obj.MASS *= [.5, 1.0, 1.8, 2.6][constants.DIFFICULTY]
            self.obj.SPEED *= [.45, 1.0, 2.0, 3.5][constants.DIFFICULTY]

            for d in self.hp_sys.defenses.defences.keys():
                self.hp_sys.defenses[d] += abs(self.hp_sys.max_hp) * [0, .0001, .001, .01][constants.DIFFICULTY]
            self.hp_sys.DODGE_RATE += [0, 0, 0.03, 0.12][constants.DIFFICULTY]

        def set_rotation(self, rot):
            if self.img.get_width() < 5:
                return
            p = position.displayed_position((self.obj.pos[0], self.obj.pos[1]))
            if p[0] < -100 or p[0] > game.get_game().displayer.SCREEN_WIDTH + 100 or p[1] < -100 or p[1] > game.get_game().displayer.SCREEN_HEIGHT + 100:
                return
            self.rot = rot
            self.d_img = entity_get_surface(self.DISPLAY_MODE, (round(self.rot / 3) * 3 % 360 + 360) % 360,
                                            game.get_game().player.get_screen_scale(), self.img)

        def play_sound(self, sound):
            d = vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                                self.obj.pos[1] - game.get_game().player.obj.pos[1])
            game.get_game().play_sound(sound, 0.99 ** int(d / 10))
            
        @staticmethod
        def is_playing(sound):
            return game.get_game().sounds[sound].get_num_channels() > 0

        def dump_display(self):
            return {'pos': self.obj.pos, 'rot': self.rot, 'img_idx': self.img_idx, 'display_mode': self.DISPLAY_MODE, 'hp_sys': self.hp_sys}

        @staticmethod
        def is_suitable(biome: str):
            return True

        def on_damage_player(self):
            pass

        def rotate(self, angle):
            self.set_rotation((self.rot + angle) % 360)

        def update(self):
            p = position.displayed_position((self.obj.pos[0], self.obj.pos[1]))
            if p[0] < -100 or p[0] > game.get_game().displayer.SCREEN_WIDTH + 100 or p[1] < -100 or p[
                1] > game.get_game().displayer.SCREEN_HEIGHT + 100:
                if not self.obj.IS_OBJECT or self.IS_MENACE or self.VITAL:
                    pass
                else:
                    return
            self.t_update()
            self.obj.update()
            self.t_draw()

        def t_update(self):
            if not self.add_star:
                self.add_star = True
                if 'star_supporter' in game.get_game().player.profile.select_skill and type(self) is not Entities.DropItem and self.obj.IS_OBJECT and \
                    not len([1 for l in self.LOOT_TABLE.loot_list if type(l) is IndividualLoot and l.item == 'star']):
                    self.LOOT_TABLE.loot_list.append(IndividualLoot('star', 0.2, 1, 1))
            if not self.show_boss and self.IS_MENACE and len(self.BOSS_NAME):
                self.show_boss = True
                window = pg.display.get_surface()
                sf = copy.copy(window)
                for i in range(240):
                    if i < 30:
                        w = i ** 2 / 900
                    elif i > 210:
                        w = (240 - i) ** 2 / 900
                    else:
                        w = 1.0
                    window.blit(sf, (0, 0))
                    pg.draw.rect(window, (255, 181, 112),
                                 (window.get_width() * (1 - w) / 2, 100, window.get_width() * w, 160))
                    pg.draw.rect(window, (242, 166, 94),
                                 (window.get_width() * (1 - w) / 2, 100, window.get_width() * w, 160), 15)
                    t = game.get_game().displayer.font.render(styles.text(self.BOSS_NAME), True, (182, 106, 34))
                    window.blit(t, (window.get_width() / 2 - t.get_width() / 2, 150))
                    t = game.get_game().displayer.font.render(styles.text(self.NAME), True, (182, 106, 34))
                    window.blit(t, (window.get_width() / 2 - t.get_width() / 2, 200))
                    pg.display.flip()
                    game.get_game().handle_events()
                    game.get_game().clock.update()
            p = position.displayed_position((self.obj.pos[0], self.obj.pos[1]))
            if p[0] < -100 or p[0] > game.get_game().displayer.SCREEN_WIDTH + 100 or p[1] < -100 or p[
                1] > game.get_game().displayer.SCREEN_HEIGHT + 100:
                if not self.obj.IS_OBJECT or self.IS_MENACE or self.VITAL:
                    pass
                else:
                    return
            if len([1 for e in self.hp_sys.effects if type(e) is effects.Frozen]):
                return
            self.on_update()

        def on_update(self):
            pass

        def t_draw(self):
            p = position.displayed_position((self.obj.pos[0], self.obj.pos[1]))
            if p[0] < -100 or p[0] > game.get_game().displayer.SCREEN_WIDTH + 100 or p[1] < -100 or p[
                1] > game.get_game().displayer.SCREEN_HEIGHT + 100:
                if not self.obj.IS_OBJECT or self.IS_MENACE or self.VITAL:
                    pass
                else:
                    return
            if not len([1 for e in self.hp_sys.effects if type(e) is effects.Frozen]):
                self.obj.update()
            self.set_rotation(self.rot)
            self.hp_sys.pos << self.obj.pos
            self.hp_sys.update()
            p = position.displayed_position((self.obj.pos[0], self.obj.pos[1]))
            if self.img.get_width() + self.img.get_height() > 30 * game.get_game().player.get_screen_scale():
                if p[0] < -100 or p[0] > game.get_game().displayer.SCREEN_WIDTH + 100 or p[1] < -100 \
                        or p[1] > game.get_game().displayer.SCREEN_HEIGHT + 100:
                    return
                self.set_rotation(self.rot)
                self.draw()
            for e in self.hp_sys.effects:
                if e.CORRESPONDED_ELEMENT != elements.ElementTypes.NONE and random.random() < 0.3:
                    cols = {
                        elements.ElementTypes.FIRE: (255, 0, 0),
                        elements.ElementTypes.WATER: (0, 127, 255),
                        elements.ElementTypes.EARTH: (127, 80, 40),
                        elements.ElementTypes.WIND: (0, 255, 127),
                        elements.ElementTypes.LIGHT: (255, 255, 0),
                        elements.ElementTypes.DARK: (0, 0, 0),
                        elements.ElementTypes.POISON: (0, 255, 0),
                        elements.ElementTypes.LIFE: (127, 255, 0),
                        elements.ElementTypes.DEATH: (63, 0, 0),
                        elements.ElementTypes.ACID: (127, 255, 0),
                        elements.ElementTypes.COLD: (127, 127, 255),
                    }
                    game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                            col=cols[e.CORRESPONDED_ELEMENT], n=1,
                                                                            sp=(self.d_img.get_width() * 1.2 + 5) / 50 * game.get_game().player.get_screen_scale(),
                                                                            t=50))

        def draw(self):
            if 'o_atk' not in dir(self) or (self.obj.TOUCHING_DAMAGE and not self.o_atk):
                self.o_atk = self.obj.TOUCHING_DAMAGE
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
                if r.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())) and self.show_bar:
                    mx, my = game.get_game().displayer.reflect(*pg.mouse.get_pos())
                    f = displayer.font.render(f'{styles.text(self.adj)}: {styles.text(self.NAME)}', True, (255, 255, 255))
                    f_bg = displayer.font.render(f'{styles.text(self.adj)}: {styles.text(self.NAME)}', True, (0, 0, 0))
                    displayer.canvas.blit(f_bg, (mx + 2, my + 2))
                    displayer.canvas.blit(f, (mx, my))
                    dm, df = 0, 0
                    for dt, d in game.get_game().player.weapons[game.get_game().player.sel_weapon].damages.items():
                        dm += d
                        df += self.hp_sys.defenses[dt]
                    txt = (f'{int(self.hp_sys.hp)}/{int(self.hp_sys.max_hp)} HP '
                           f'{self.obj.TOUCHING_DAMAGE / self.o_atk * 100 if self.o_atk else 0:.0f}% AT '
                           f'{df / dm * 100 if dm else 0:.0f}% DF')
                    f = displayer.font.render(txt, True, (255, 255, 255))
                    f_bg = displayer.font.render(txt, True, (0, 0, 0))
                    displayer.canvas.blit(f_bg, (mx + 2, my + 2 + f.get_height()))
                    displayer.canvas.blit(f, (mx, my + f.get_height()))

    class Ore(Entity):
        IMG = 'entity_ore'
        DISPLAY_MODE = 3
        NAME = 'Ore'
        TOUGHNESS = 0
        HP = 10
        SOUND_HURT = 'ore'
        SOUND_DEATH = 'ore'

        def __init__(self, pos, hp=0):
            super().__init__(pos, game.get_game().graphics[self.IMG], BuildingAI, self.HP if not hp else hp)
            self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 0
            self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 0
            self.hp_sys.resistances[damages.DamageTypes.ARCANE] = 0
            self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = 0
            self.hp_sys.resistances[damages.DamageTypes.THINKING] = 0
            self.hp_sys.resistances[damages.DamageTypes.MINE_POWER] = 12
            self.hp_sys.defenses[damages.DamageTypes.MINE_POWER] = self.TOUGHNESS * 12
            self.hp_sys(op='config', minimum_damage=0, maximum_damage=20)

    class RawOre(Entity):
        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_null'], BuildingAI, 1)
            self.hp_sys.hp = 0
            stage = game.get_game().stage
            biome = game.get_game().get_biome()
            self.obj.IS_OBJECT = False
            if biome == 'heaven':
                return
            ore_chances = {
                Entities.CopperOre: 11,
                Entities.IronOre: 9,
                Entities.SteelOre: 9,
                Entities.PlatinumOre: 3,
                Entities.MagicOre: 5,
                Entities.BloodOre: 1,
                Entities.FiriteOre: 1,
                Entities.FiryOre: 0,
                Entities.MysteriousOre: 0,
            }
            new_world_chances = {
                Entities.SpiritualOre: 15,
                Entities.EvilOre: 15,
                Entities.PalladiumOre: 10,
                Entities.MithrillOre: 10,
                Entities.TitaniumOre: 10,
                Entities.TalentOre: 7,
                Entities.ChlorophyteOre: 0,
            }
            if biome == 'desert':
                ore_chances[Entities.IronOre] += 4
                ore_chances[Entities.PlatinumOre] += 2
            elif biome == 'snowland':
                ore_chances[Entities.SteelOre] += 4
                ore_chances[Entities.PlatinumOre] += 2
            elif biome == 'rainforest':
                ore_chances[Entities.PlatinumOre] += 5
                ore_chances[Entities.MagicOre] += 2
            elif biome == 'hell':
                ore_chances[Entities.BloodOre] += 2
                ore_chances[Entities.FiriteOre] += 2
            if game.get_game().player.hp_sys.max_hp >= 500:
                ore_chances[Entities.MysteriousOre] += 2
                if biome == 'desert':
                    ore_chances[Entities.MysteriousOre] += 8
            if stage > 0:
                for k, v in new_world_chances.items():
                    ore_chances[k] = v
                if stage > 5:
                    ore_chances[Entities.SpiritualOre] = 0
                if biome == 'rainforest':
                    ore_chances[Entities.ChlorophyteOre] += 20
            ore_type = random.choices(list(ore_chances.keys()), weights=list(ore_chances.values()), k=1)[0]
            game.get_game().entities.append(ore_type(self.obj.pos))


    class Chest(Ore):
        IMG = 'entity_chest'
        DISPLAY_MODE = 3
        NAME = 'Chest'
        BIOMES = []
        HP = 30
        TOUGHNESS = 2

        def __init__(self, pos, hp=0):
            super().__init__(pos, self.HP if not hp else hp)

        @staticmethod
        def is_suitable(biome: str):
            return biome in []

        def on_update(self):
            super().on_update()
            rd = random.randint(1, 2)
            self.hp_sys(op='config', minimum_damage=rd, maximum_damage=rd + 3)

    class GreenChest(Chest):
        IMG = 'entity_green_chest'
        LOOT_TABLE = LootTable([
            SelectionLoot([('iron', 10, 12), ('steel', 10, 12)], 0, 2),
            IndividualLoot('leaf', 1, 10, 12),
            IndividualLoot('platinum', 0.2, 10, 20),
            SelectionLoot([('mana_flower', 1, 1), ('life_flower', 0, 1), ('star_amulet', 1, 1)], 0, 1),
            SelectionLoot([('hermes_boots', 0, 1), ('lucky_clover', 1, 1), ('seed_amulet', 1, 1)], 0, 2),
            IndividualLoot('fairy_wings', 0.1, 1, 1),
            SelectionLoot([('purple_ring', 0, 1), ('cyan_ring', 0, 1), ('yellow_ring', 0, 1),
                            ('green_ring', 0, 1), ('blue_ring', 0, 1), ('orange_ring', 0, 1)], 0, 3),
        ])
        BIOMES = ['forest', 'rainforest']

        @staticmethod
        def is_suitable(biome: str):
            return biome in ['forest', 'rainforest']

    class RedChest(Chest):
        IMG = 'entity_red_chest'
        LOOT_TABLE = LootTable([
            SelectionLoot([('platinum', 3, 5), ('magic_stone', 10, 12)], 1, 2),
            IndividualLoot('firite_ingot', 0.5, 10, 12),
            IndividualLoot('firy_plant', 0.4, 1, 4),
            IndividualLoot('fireball_magic', 0.1, 1, 1),
            SelectionLoot([('fire_gloves', 1, 1), ('quenched_cross', 1, 1), ('lava_walker', 1, 1)], 0, 2),
            # IndividualLoot('obsidian', 0.6, 12, 20),
        ])
        BIOMES = ['hell']
        TOUGHNESS = 7
        HP = 50

        @staticmethod
        def is_suitable(biome: str):
            return biome in ['hell']

    class WhiteChest(Chest):
        IMG = 'entity_white_chest'
        LOOT_TABLE = LootTable([
            SelectionLoot([('steel', 10, 12), ('magic_stone', 10, 12)], 0, 2),
            SelectionLoot([('coniferous_leaf', 100, 200), ('snowball', 100, 200)], 0, 1),
            IndividualLoot('platinum', 0.2, 10, 30),
            SelectionLoot([('white_guard', 1, 2), ('snowstorm_bottle', 1, 1), ('snow_wings', 0, 1)], 0, 1),
            SelectionLoot([('purple_ring', 0, 1), ('cyan_ring', 0, 1), ('yellow_ring', 0, 1),
                            ('green_ring', 0, 1), ('blue_ring', 0, 1), ('orange_ring', 0, 1)], 0, 3),
        ])
        BIOMES = ['snowland']
        TOUGHNESS = 4
        HP = 40

        @staticmethod
        def is_suitable(biome: str):
            return biome in ['snowland']

    class OrangeChest(Chest):
        IMG = 'entity_orange_chest'
        LOOT_TABLE = LootTable([
            SelectionLoot([('platinum', 10, 12), ('mana_crystal', 1, 3)], 1, 2),
            IndividualLoot('copper', 1, 10, 12),
            IndividualLoot('mysterious_substance', 0.1, 10, 30),
            SelectionLoot([('rune_cross', 1, 1), ('rune_eye', 1, 1), ('rune_gloves', 1, 1)], 0, 1),
            IndividualLoot('nice_cream', 0.3, 5, 12),
            ])
        BIOMES = ['desert']
        TOUGHNESS = 4
        HP = 40

        @staticmethod
        def is_suitable(biome: str):
            return biome in ['desert']

    class BlueChest(Chest):
        IMG = 'entity_blue_chest'
        LOOT_TABLE = LootTable([
            SelectionLoot([('platinum', 20, 32), ('magic_stone', 10, 12)], 1, 2),
            # SelectionLoot([('iron_donut', 1, 10), ('heart_pie', 1, 10)], 0, 1),
            # IndividualLoot('obsidian', 0.6, 12, 20),
        ])
        BIOMES = ['heaven']
        TOUGHNESS = 7
        HP = 50

        @staticmethod
        def is_suitable(biome: str):
            return biome in ['heaven']

    class StoneAltar(Ore):
        DISPLAY_MODE = 3
        NAME = 'Stone Altar'
        IMG = 'entity_stone_altar'
        TOUGHNESS = 60

        def __init__(self, pos):
            super().__init__(pos, 100)

        def on_update(self):
            super().on_update()
            px = game.get_game().player.obj.pos[0] - self.obj.pos[0]
            py = game.get_game().player.obj.pos[1] - self.obj.pos[1]
            if vector.distance(px, py) < 1000:
                if not len([1 for e in game.get_game().player.hp_sys.effects if type(e) is effects.StoneAltar]):
                    game.get_game().player.hp_sys.effect(effects.StoneAltar(5, 1))

    class MetalAltar(Ore):
        DISPLAY_MODE = 3
        NAME = 'Metal Altar'
        IMG = 'entity_metal_altar'
        TOUGHNESS = 88

        def __init__(self, pos):
            super().__init__(pos, 280)

        def on_update(self):
            super().on_update()
            px = game.get_game().player.obj.pos[0] - self.obj.pos[0]
            py = game.get_game().player.obj.pos[1] - self.obj.pos[1]
            if vector.distance(px, py) < 1500:
                if not len([1 for e in game.get_game().player.hp_sys.effects if type(e) is effects.MetalAltar]):
                    game.get_game().player.hp_sys.effect(effects.MetalAltar(8, 1))

    class ScarlettAltar(Ore):
        DISPLAY_MODE = 3
        NAME = 'Scarlett Altar'
        IMG = 'entity_scarlett_altar'
        TOUGHNESS = 89

        def __init__(self, pos):
            super().__init__(pos, 400)

        def on_update(self):
            super().on_update()
            px = game.get_game().player.obj.pos[0] - self.obj.pos[0]
            py = game.get_game().player.obj.pos[1] - self.obj.pos[1]
            if vector.distance(px, py) < 1800:
                if not len([1 for e in game.get_game().player.hp_sys.effects if type(e) is effects.ScarlettAltar]):
                    game.get_game().player.hp_sys.effect(effects.ScarlettAltar(10, 1))

    class CopperOre(Ore):
        IMG = 'entity_copper_ore'
        NAME = 'Copper Ore'
        TOUGHNESS = 0
        HP = 10
        LOOT_TABLE = LootTable([
            IndividualLoot('copper', 1, 20, 32),
            ])

    class IronOre(Ore):
        IMG = 'entity_iron_ore'
        NAME = 'Iron Ore'
        TOUGHNESS = 2
        HP = 12
        LOOT_TABLE = LootTable([
            IndividualLoot('iron', 1, 20, 25),
            ])

    class SteelOre(Ore):
        IMG = 'entity_steel_ore'
        NAME = 'Steel Ore'
        TOUGHNESS = 2
        HP = 12
        LOOT_TABLE = LootTable([
            IndividualLoot('steel', 1, 20, 25),
            ])

    class PlatinumOre(Ore):
        IMG = 'entity_platinum_ore'
        NAME = 'Platinum Ore'
        TOUGHNESS = 5
        HP = 16
        LOOT_TABLE = LootTable([
            IndividualLoot('platinum', 1, 28, 36),
            ])

    class MagicOre(Ore):
        IMG = 'entity_magic_ore'
        NAME = 'Magic Ore'
        TOUGHNESS = 7
        HP = 20
        LOOT_TABLE = LootTable([
            IndividualLoot('magic_stone', 1, 15, 18),
            ])

    class BloodOre(Ore):
        IMG = 'entity_blood_ore'
        NAME = 'Blood Ore'
        TOUGHNESS = 8
        HP = 35
        LOOT_TABLE = LootTable([
            IndividualLoot('cell_organization', 1, 12, 18),
            ])

    class FiriteOre(Ore):
        IMG = 'entity_firite_ore'
        NAME = 'Firite Ore'
        TOUGHNESS = 14
        HP = 50
        LOOT_TABLE = LootTable([
            IndividualLoot('firite_ingot', 1, 10, 12),
            ])

    class FiryOre(Ore):
        IMG = 'entity_firy_ore'
        NAME = 'Firy Ore'
        TOUGHNESS = 25
        HP = 72
        LOOT_TABLE = LootTable([
            IndividualLoot('firy_plant', 1, 1, 2),
            ])

    class MysteriousOre(Ore):
        IMG = 'entity_mysterious_ore'
        NAME = 'Mysterious Ore'
        TOUGHNESS = 30
        HP = 80
        LOOT_TABLE = LootTable([
            IndividualLoot('mysterious_substance', 1, 10, 12),
            ])

    class SpiritualOre(Ore):
        IMG = 'entity_spiritual_ore'
        NAME = 'Spiritual Ore'
        TOUGHNESS = 65
        HP = 200
        LOOT_TABLE = LootTable([
            IndividualLoot('soul', 1, 20, 24),
            ])

    class EvilOre(Ore):
        IMG = 'entity_evil_ore'
        NAME = 'Evil Ore'
        TOUGHNESS = 80
        HP = 240
        LOOT_TABLE = LootTable([
            IndividualLoot('evil_ingot', 1, 10, 12),
            ])

    class PalladiumOre(Ore):
        IMG = 'entity_palladium_ore'
        NAME = 'Palladium Ore'
        TOUGHNESS = 84
        HP = 300
        LOOT_TABLE = LootTable([
            IndividualLoot('palladium', 1, 20, 24),
            ])

    class MithrillOre(Ore):
        IMG = 'entity_mithrill_ore'
        NAME = 'Mithrill Ore'
        TOUGHNESS = 84
        HP = 300
        LOOT_TABLE = LootTable([
            IndividualLoot('mithrill', 1, 20, 24),
            ])

    class TitaniumOre(Ore):
        IMG = 'entity_titanium_ore'
        NAME = 'Titanium Ore'
        TOUGHNESS = 84
        HP = 300
        LOOT_TABLE = LootTable([
            IndividualLoot('titanium', 1, 20, 24),
            ])

    class TalentOre(Ore):
        IMG = 'entity_talent_ore'
        NAME = 'Talent Ore'
        TOUGHNESS = 128
        HP = 500
        LOOT_TABLE = LootTable([
            IndividualLoot('mystery_core', 1, 1, 3),
            ])

    class ChlorophyteOre(Ore):
        IMG = 'entity_chlorophyte_ore'
        NAME = 'Chlorophyte Ore'
        TOUGHNESS = 200
        HP = 1000
        LOOT_TABLE = LootTable([
            IndividualLoot('chlorophyte_ingot', 1, 2, 3),
            ])

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
        BOSS_NAME = ''
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])
        ENTITY_TAGS = []
        IS_MENACE = False
        PHASE_SEGMENTS = []

        SOUND_SPAWN = None
        SOUND_HURT = None
        SOUND_DEATH = None
        VITAL = False

        def __init__(self, pos, length, img_head=None, img_body=None, head_ai: type(MonsterAI) = MonsterAI, hp=120,
                     body_length=60, body_touching_damage=100):
            self.length = length
            self.body_length = body_length
            self.hp_sys = hp_system.HPSystem(hp)
            self.show_bar = True
            self.body = [Entities.Entity(pos, img_head, head_ai, hp_sys=self.hp_sys)] + [
                Entities.Entity((pos[0] + i + 1, pos[1]), img_body, MonsterAI, hp_sys=self.hp_sys) for i in
                range(length - 1)]
            self.obj = self.body[0].obj
            for i in range(1, self.length):
                game.get_game().entities.append(self.body[i])
                self.body[i].obj.IS_OBJECT = (i % 2 == 0)
                self.body[i].obj.TOUCHING_DAMAGE = body_touching_damage
                # self.body[i].obj.IS_OBJECT = False
            self.d_img = self.body[0].d_img
            self.img = self.body[0].img
            self.rot = self.body[0].rot
            for b in self.body:
                b.DISPLAY_MODE = 1
                b.NAME = self.NAME
                b.VITAL = True
            try:
                if self.SOUND_SPAWN is not None:
                    self.body[0].play_sound('spawn_' + self.SOUND_SPAWN)
            except ValueError:
                pass
            self.hp_sys.SOUND_HURT = self.SOUND_HURT
            self.show_boss = False
            self.ueid = Entities.Entity.ENO
            Entities.Entity.ENO += 1

        def play_sound(self, sound):
            self.body[0].play_sound(sound)

        def on_damage_player(self):
            pass

        def on_update(self):
            self.body[0].on_update()

        def t_draw(self):
            self.body[0].set_rotation(-self.obj.velocity.get_net_rotation())
            for i in range(1, self.length):
                ox, oy = self.body[i - 1].obj.pos
                nx, ny = self.body[i].obj.pos
                self.body[i].set_rotation(-vector.coordinate_rotation(ox - nx, oy - ny))
                ax, ay = vector.rotation_coordinate(vector.coordinate_rotation(ox - nx, oy - ny))
                tx, ty = ox - ax * self.body_length, oy - ay * self.body_length
                self.body[i].obj.pos << (tx, ty)
                if not i and self.body[i].obj.velocity.get_net_value() > 0:
                    self.body[0].obj.velocity.add(self.body[i].obj.velocity.get_net_vector())
                    self.body[i].obj.velocity.clear()
                # self.body[i].obj.apply_force(vector.Vector(vector.coordinate_rotation(tx - nx, ty - ny), vector.distance(tx - nx, ty - ny) * 8))
            self.body[0].t_draw()

        def draw(self):
            self.body[0].draw()

        def t_update(self):
            if not self.show_boss and self.IS_MENACE and len(self.BOSS_NAME):
                self.show_boss = True
                window = pg.display.get_surface()
                sf = copy.copy(window)
                for i in range(240):
                    if i < 30:
                        w = i ** 2 / 900
                    elif i > 210:
                        w = (240 - i) ** 2 / 900
                    else:
                        w = 1.0
                    window.blit(sf, (0, 0))
                    pg.draw.rect(window, (255, 181, 112),
                                 (window.get_width() * (1 - w) / 2, 100, window.get_width() * w, 160))
                    pg.draw.rect(window, (242, 166, 94),
                                 (window.get_width() * (1 - w) / 2, 100, window.get_width() * w, 160), 15)
                    t = game.get_game().displayer.font.render(styles.text(self.BOSS_NAME), True, (182, 106, 34))
                    window.blit(t, (window.get_width() / 2 - t.get_width() / 2, 150))
                    t = game.get_game().displayer.font.render(styles.text(self.NAME), True, (182, 106, 34))
                    window.blit(t, (window.get_width() / 2 - t.get_width() / 2, 200))
                    pg.display.flip()
                    game.get_game().handle_events()
                    game.get_game().clock.update()
            self.body[0].t_update()
            self.on_update()

        def set_rotation(self, rot):
            self.body[0].set_rotation(rot)

        def rotate(self, rot):
            self.body[0].rotate(rot)

        @staticmethod
        def is_suitable(biome: str):
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
        SOUND_DEATH = 'sticky'

        @staticmethod
        def is_suitable(biome: str):
            return True

        def __init__(self, pos):
            if game.get_game().stage > 0:
                super().__init__(pos, game.get_game().graphics['entity_eye'], EyeAI, 2880)
            else:
                super().__init__(pos, game.get_game().graphics['entity_eye'], EyeAI, 360)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = -2
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 2
            if game.get_game().stage > 0:
                self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 36
                self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 44
                self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 32
                self.obj.SPEED *= 3
                self.obj.MASS *= 2.5
                self.obj.TOUCHING_DAMAGE * 50
                self.NAME = 'The Eye'
                self.obj.TOUCHING_DAMAGE *= 6


        def on_update(self):
            super().on_update()
            self.set_rotation((self.rot * 5 - self.obj.velocity.get_net_rotation()) // 6)

    class FluffBall(Entity):
        NAME = 'Fluff Ball'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            SelectionLoot([('iron', 10, 12), ('steel', 6, 8)], 1, 2),
            IndividualLoot('flufffur', 1, 5, 8),
            IndividualLoot('cell_organization', 0.8, 1, 3),
        ])

        SOUND_HURT = 'dragon'
        SOUND_DEATH = 'sticky'

        @staticmethod
        def is_suitable(biome: str):
            return True

        def __init__(self, pos):
            if game.get_game().stage > 0:
                super().__init__(pos, game.get_game().graphics['entity_fluffball'], FluffBallAI, 4800)
            else:
                super().__init__(pos, game.get_game().graphics['entity_fluffball'], FluffBallAI, 880)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = -2
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = -8
            if game.get_game().stage > 0:
                self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = -4
                self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = -9
                self.hp_sys.defenses[damages.DamageTypes.PIERCING] = -8
                self.obj.SPEED *= 3
                self.NAME = 'Rolling Fluff-Ball'
                self.obj.TOUCHING_DAMAGE *= 6

        def on_update(self):
            super().on_update()
            px = game.get_game().player.obj.pos[0] - self.obj.pos[0]
            self.set_rotation(px / 80 + self.rot)

    class Fluffff(WormEntity):
        NAME = 'Fluffff'
        DISPLAY_MODE = 1
        BOSS_NAME = 'The Fluffy Worm'
        LOOT_TABLE = LootTable([
            IndividualLoot('platinum', 1, 20, 30),
            IndividualLoot('flufffur', 1, 5, 8),
            IndividualLoot('blood_ingot', 0.2, 10, 30),
            SelectionLoot([('swwwword', 1, 1), ('kuangkuangkuang', 1, 1)], 1, 1),
        ])
        IS_MENACE = True

        SOUND_HURT = 'dragon'
        SOUND_DEATH = 'sticky'

        def __init__(self, pos):
            super().__init__(pos, 12, game.get_game().graphics['entity_fluffball'],
                             game.get_game().graphics['entity_fluffff'], FluffBallAI,
                             88000, 130, 40)
            self.body[0].obj.SIGHT_DISTANCE = 9999

    class TrueEye(Entity):
        NAME = 'True Eye'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('blood_ingot', 1, 20, 30),
            IndividualLoot('platinum', 1, 20, 30),
            SelectionLoot([('orange_ring', 1, 1), ('blue_ring', 1, 1), ('green_ring', 1, 1)], 1, 1),
            IndividualLoot('aimer', 1, 1, 1),
            IndividualLoot('tip2', 1, 1, 1),
        ])
        BOSS_NAME = 'The Watcher of Terror'
        IS_MENACE = True

        SOUND_SPAWN = 'boss'
        SOUND_HURT = 'sticky'
        SOUND_DEATH = 'huge_monster'

        PHASE_SEGMENTS = [0.3, 0.7]

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_true_eye'], TrueEyeAI, 22000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = -5
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 8
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 2
            self.phase = 0
            self.tick = 0

        def on_update(self):
            super().on_update()
            if self.obj.timer > 0:
                self.set_rotation((self.rot * 8 - self.obj.velocity.get_net_rotation()) // 9)
            else:
                self.set_rotation(self.rot + 12)
            self.hp_sys(op='config', immune=self.obj.timer < 0)
            if self.obj.timer % (50 - self.obj.phase * 10) == 0 and self.obj.timer >= 200:
                self.play_sound('eoc_roar')
            if self.hp_sys.hp <= self.hp_sys.max_hp * 0.7 and self.phase == 0:
                self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] -= 20
                self.hp_sys.defenses[damages.DamageTypes.MAGICAL] -= 20
                self.hp_sys.defenses[damages.DamageTypes.PIERCING] -= 20
                self.obj.TOUCHING_DAMAGE = 56
                self.obj.phase = 1
                self.phase = 1
                self.obj.timer = -100
                self.img = game.get_game().graphics['entity_true_eye_phase2']
                self.set_rotation(self.rot)
                self.play_sound('spawn_boss')
            if self.hp_sys.hp <= self.hp_sys.max_hp * 0.3 and self.phase == 1:
                self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] -= 5
                self.hp_sys.defenses[damages.DamageTypes.MAGICAL] -= 5
                self.hp_sys.defenses[damages.DamageTypes.PIERCING] -= 5
                self.obj.TOUCHING_DAMAGE = 72
                self.obj.phase = 2
                self.phase = 2
                self.obj.timer = -100
                self.img = game.get_game().graphics['entity_true_eye_phase3']
                self.set_rotation(self.rot)
                self.play_sound('spawn_boss')
            self.tick += 1
            if self.tick % 60 == 0 and self.phase >= 1:
                game.get_game().entities.append(Entities.Eye((self.obj.pos[0], self.obj.pos[1] + 1)))
            elif self.obj.timer == 540:
                for _ in range(12):
                    rx, ry = random.randint(-200, 200), random.randint(-200, 200)
                    i = Entities.Eye((self.obj.pos[0] + rx, self.obj.pos[1] + ry))
                    px, py = game.get_game().player.obj.pos
                    px -= i.obj.pos[0]
                    py -= i.obj.pos[1]
                    i.obj.apply_force(vector.Vector(vector.coordinate_rotation(px, py), vector.distance(px, py) * 60))
                    game.get_game().entities.append(i)

    class Tree(Entity):
        NAME = 'Tree'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('wood', 0.9, 15, 25),
            IndividualLoot('leaf', 0.9, 5, 7),
            IndividualLoot('red_apple', 0.03, 1, 1),
        ])

        @staticmethod
        def is_suitable(biome: str):
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
            IndividualLoot('red_apple', 0.07, 1, 1),
        ])

        @staticmethod
        def is_suitable(biome: str):
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
            IndividualLoot('copper', 0.6, 8, 18),
            IndividualLoot('red_apple', 0.04, 1, 1),
        ])

        SOUND_HURT = 'monster'
        SOUND_DEATH = 'monster'

        @staticmethod
        def is_suitable(biome: str):
            return biome in ['forest', 'rainforest']

        def __init__(self, pos):
            if game.get_game().stage > 0:
                super().__init__(pos, game.get_game().graphics['entity_tree_monster'], TreeMonsterAI, 4500)
            else:
                super().__init__(pos, game.get_game().graphics['entity_tree_monster'], TreeMonsterAI, 250)
            if game.get_game().stage > 0:
                self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 88
                self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 100
                self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 92
                self.NAME = 'The Walking Tree'
                self.obj.TOUCHING_DAMAGE *= 8

    class ClosedBloodflower(Entity):
        NAME = 'Closed Bloodflower'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('copper', 0.9, 8, 18),
            IndividualLoot('cell_organization', 0.5, 2, 8),
            IndividualLoot('leaf', 0.5, 7, 12),
            IndividualLoot('spikeflower', 0.18, 1, 1),
            IndividualLoot('red_apple', 0.02, 1, 1),
        ])

        SOUND_HURT = 'corrupt'
        SOUND_DEATH = 'sticky'

        @staticmethod
        def is_suitable(biome: str):
            return biome in ['forest', 'rainforest']

        def __init__(self, pos):
            if game.get_game().stage > 0:
                super().__init__(pos, game.get_game().graphics['entity_closed_bloodflower'], CloseBloodflowerAI, 1080)
            else:
                super().__init__(pos, game.get_game().graphics['entity_closed_bloodflower'], CloseBloodflowerAI, 56)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 6
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 7
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 3
            if game.get_game().stage > 0:
                self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 108
                self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 98
                self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 112
                self.NAME = 'The Closed Bloody-Flower'
                self.obj.SPEED *= 5.2
                self.obj.MASS *= 5
                self.obj.TOUCHING_DAMAGE *= 5

    class Bloodflower(Entity):
        NAME = 'Bloodflower'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('steel', 0.9, 15, 25),
            IndividualLoot('cell_organization', 0.9, 12, 16),
            IndividualLoot('platinum', 0.3, 10, 20),
            IndividualLoot('spikeflower', 0.36, 1, 1),
            SelectionLoot([('purple_ring', 1, 1), ('cyan_ring', 1, 1), ('yellow_ring', 1, 1)], 0, 1),
            IndividualLoot('red_apple', 0.02, 1, 1),
        ])

        SOUND_HURT = 'corrupt'
        SOUND_DEATH = 'sticky'

        def __init__(self, pos):
            if game.get_game().stage > 0:
                super().__init__(pos, game.get_game().graphics['entity_bloodflower'], BloodflowerAI, 5400)
            else:
                super().__init__(pos, game.get_game().graphics['entity_bloodflower'], BloodflowerAI, 920)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = -25
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = -18
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = -32
            if game.get_game().stage > 0:
                self.obj.SPEED *= 8
                self.obj.MASS *= 5
                self.obj.TOUCHING_DAMAGE *= 10
                self.NAME = 'The Bloody-Flower'

    class RedWatcher(Entity):
        NAME = 'Red Watcher'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('platinum', 0.9, 20, 40),
            IndividualLoot('magic_stone', 0.2, 5, 10),
            IndividualLoot('iron', 0.9, 15, 25),
            SelectionLoot([('purple_ring', 1, 1), ('cyan_ring', 1, 1), ('yellow_ring', 1, 1)], 1, 2),
        ])

        SOUND_HURT = 'corrupt'
        SOUND_DEATH = 'monster'

        def __init__(self, pos):
            if game.get_game().stage > 0:
                super().__init__(pos, game.get_game().graphics['entity_red_watcher'], RedWatcherAI, 12000)
            else:
                super().__init__(pos, game.get_game().graphics['entity_red_watcher'], RedWatcherAI, 1500)
            self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = 2.5
            self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 2.44
            self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 2.52
            if game.get_game().stage > 0:
                self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = 2.75
                self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 2.64
                self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 2.76
                self.NAME = 'The Red-Watcher'
                self.obj.SPEED *= 10
                self.obj.MASS *= 9
                self.obj.TOUCHING_DAMAGE *= 7

    class Cactus(Entity):
        NAME = 'Cactus'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('wood', 0.9, 15, 25),
            IndividualLoot('iron', 0.8, 20, 30),
            IndividualLoot('copper', 0.6, 8, 18),
            IndividualLoot('cactus_wand', 0.2, 1, 1),
            IndividualLoot('red_apple', 0.04, 1, 1),
        ])

        SOUND_HURT = 'monster'
        SOUND_DEATH = 'monster'

        @staticmethod
        def is_suitable(biome: str):
            return biome in ['desert']

        def __init__(self, pos):
            if game.get_game().stage > 0:
                super().__init__(pos, game.get_game().graphics['entity_cactus'], CactusAI, 7200)
            else:
                super().__init__(pos, game.get_game().graphics['entity_cactus'], CactusAI, 365)
            if game.get_game().stage > 0:
                self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 88
                self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 100
                self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 92
                self.NAME = 'The Spiked Cactus'
                self.obj.TOUCHING_DAMAGE *= 8

    class ConiferousTree(Entity):
        NAME = 'Coniferous Tree'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('wood', 0.9, 15, 25),
            IndividualLoot('steel', 0.8, 20, 30),
            IndividualLoot('copper', 0.6, 8, 18),
            IndividualLoot('coniferous_leaf', 0.2, 50, 200),
            IndividualLoot('red_apple', 0.06, 1, 1),
        ])

        SOUND_HURT = 'monster'
        SOUND_DEATH = 'monster'

        @staticmethod
        def is_suitable(biome: str):
            return biome in ['snowland']

        def __init__(self, pos):
            if game.get_game().stage > 0:
                super().__init__(pos, game.get_game().graphics['entity_coniferous_tree'], CactusAI, 7500)
            else:
                super().__init__(pos, game.get_game().graphics['entity_coniferous_tree'], CactusAI, 385)
            if game.get_game().stage > 0:
                self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 88
                self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 100
                self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 92
                self.NAME = 'The Coniferous Tree'
                self.obj.TOUCHING_DAMAGE *= 8

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

        @staticmethod
        def is_suitable(biome: str):
            return biome in ['hell']

        def __init__(self, pos):
            if game.get_game().stage > 0:
                super().__init__(pos, game.get_game().graphics['entity_magma_cube'], RangedAI, 36000)
            else:
                super().__init__(pos, game.get_game().graphics['entity_magma_cube'], MagmaCubeAI, 1100)
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 10
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 8
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 15
            if game.get_game().stage > 0:
                self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 12
                self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 10
                self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 20
                self.NAME = 'The Fireball Magma Cube'
                self.obj.SPEED *= 1.5
                self.obj.MASS *= 1.5
                self.obj.TOUCHING_DAMAGE *= 6
            self.tick = 0

        def on_update(self):
            super().on_update()
            self.tick += 1
            if game.get_game().stage and self.tick % 40 == 0:
                px, py = game.get_game().player.obj.pos
                px -= self.obj.pos[0]
                py -= self.obj.pos[1]
                if vector.distance(px, py) > 800:
                    return
                game.get_game().entities.append(Entities.MagmaKingFireball(self.obj.pos, vector.coordinate_rotation(px, py)))

    class DropItem(Entity):
        NAME = 'Drop Item'
        DISPLAY_MODE = 3

        def __init__(self, pos, item_id, item_amount):
            super().__init__(pos, game.get_game().graphics['items_' + item_id], BuildingAI, 1)
            self.amount = item_amount
            if self.img.get_width() < 64:
                self.img = pg.transform.scale(self.img, (64, 64))
                self.d_img = self.img
            self.NAME = item_id.replace('_', ' ').title()
            self.item_id = item_id
            self.rarity = inventory.ITEMS[item_id].rarity
            self.hp_sys(op='config', immune=True)
            self.obj.FRICTION = 0.9
            self.obj.velocity.add(vector.Vector(random.randint(0, 360),
                                                random.randint(2, 40)))

        def on_update(self):
            super().on_update()
            px, py = game.get_game().player.obj.pos
            if vector.distance(self.obj.pos[0] - px, self.obj.pos[1] - py) < 60 + self.rarity * 25 and \
                    (len(game.get_game().player.inventory.items) < game.get_game().player.inv_capacity or
                            game.get_game().player.inventory.is_enough(inventory.ITEMS[self.item_id])):
                game.get_game().player.inventory.add_item(inventory.ITEMS[self.item_id], self.amount)
                self.hp_sys.hp = 0
                self.play_sound('grab')
            elif vector.distance(self.obj.pos[0] - px, self.obj.pos[1] - py) < 120 + self.rarity * 50:
                self.obj.apply_force(
                    vector.Vector(vector.coordinate_rotation(px - self.obj.pos[0], py - self.obj.pos[1]), 24000))
            elif vector.distance(self.obj.pos[0] - px, self.obj.pos[1] - py) < 240 + self.rarity * 100:
                self.obj.apply_force(
                    vector.Vector(vector.coordinate_rotation(px - self.obj.pos[0], py - self.obj.pos[1]), 12000))

    class Star(Entity):
        NAME = 'Star'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('platinum', 0.7, 15, 55),
            IndividualLoot('magic_stone', 0.9, 12, 15),
            IndividualLoot('mana_crystal', 0.5, 1, 2),
            IndividualLoot('star_amulet', 0.4, 1, 1),
        ])

        SOUND_HURT = 'crystal'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_star'], StarAI, 820)
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = -11

    class MagmaKingFireball(Entity):
        NAME = 'Magma King Fireball'
        DISPLAY_MODE = 3

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_fireball'], MagmaKingFireballAI, 200)
            self.obj.rot = rot
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = -30
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 20
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = -80

        def on_update(self):
            super().on_update()
            self.set_rotation(self.rot)
            self.hp_sys.hp -= 1
            self.damage()

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(68, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class ProtectApple(Entity):
        NAME = 'Apple'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([])
        SOUND_HURT = 'ore'
        SOUND_DEATH = 'ore'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_apple'], AppleProtectionAI, 330)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 8
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 18
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 13

    class AttackApple(Entity):
        NAME = 'Apple'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([])
        SOUND_HURT = 'ore'
        SOUND_DEATH = 'ore'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_apple'], AppleAttackAI, 330)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 8
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 18
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 13

    class TheWorldsFruit(Entity):
        NAME = 'The World\'s Fruit'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            SelectionLoot([('doctor_expeller', 1, 1), ('apple_knife', 1, 1), ('fruit_wand', 1, 1)], 1, 2),
            ])
        SOUND_SPAWN = 'boss'
        SOUND_HURT = 'ore'
        SOUND_DEATH = 'huge_monster'
        BOSS_NAME = 'The God\'s Heritage'
        IS_MENACE = True
        PHASE_SEGMENTS = []

        def __init__(self, pos):
            super().__init__(pos, copy.copy(game.get_game().graphics['entity_worlds_fruit']), WorldsFruitAI, 4400)
            self.apples = [Entities.ProtectApple((self.obj.pos[0] + random.randint(-100, 100), self.obj.pos[1] + random.randint(-100, 100))) for _ in range(10)] + \
                          [Entities.AttackApple((self.obj.pos[0] + random.randint(-100, 100), self.obj.pos[1] + random.randint(-100, 100))) for _ in range(10)]
            self.phase = 0
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 20
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 28
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 26
            self.hp_sys(op='config', immune=True)
            for a in self.apples:
                a.obj.upper = self.obj
                game.get_game().entities.append(a)
            self.o_hp = self.hp_sys.max_hp
            self.hp_sys.max_hp += sum([a.hp_sys.max_hp for a in self.apples])
            self.hp_sys.hp = self.hp_sys.max_hp
            self.PHASE_SEGMENTS = [self.o_hp / self.hp_sys.max_hp]
            self.tick = 0

        def on_update(self):
            if self.phase == 0:
                for a in self.apples:
                    ax, ay = a.obj.pos
                    ax -= self.obj.pos[0]
                    ay -= self.obj.pos[1]
                    if vector.distance(ax, ay) > 400:
                        ax *= 400 / vector.distance(ax, ay)
                        ay *= 400 / vector.distance(ax, ay)
                        a.obj.pos << (self.obj.pos[0] + ax, self.obj.pos[1] + ay)
                    if a.hp_sys.hp <= 0:
                        self.apples.remove(a)
                self.hp_sys.hp = self.o_hp + sum([a.hp_sys.hp for a in self.apples])
                if self.hp_sys.hp <= self.o_hp or not len(self.apples):
                    self.phase = 1
                    for a in [Entities.ProtectApple((self.obj.pos[0] + random.randint(-100, 100), self.obj.pos[1] + random.randint(-100, 100))) for _ in range(6)] + \
                          [Entities.AttackApple((self.obj.pos[0] + random.randint(-100, 100), self.obj.pos[1] + random.randint(-100, 100))) for _ in range(6)]:
                        self.apples.append(a)
                        a.obj.upper = self.obj
                        game.get_game().entities.append(a)
                    self.obj.MASS -= 500
                self.tick = (self.tick + 1) % 180
                if 120 < self.tick < 150:
                    self.img.set_alpha(255 - (self.tick - 120) * 255 // 30)
                elif self.tick == 150:
                    px, py = game.get_game().player.obj.pos
                    vx, vy = vector.rotation_coordinate(random.randint(0, 359))
                    self.obj.pos << (px + vx * 1000, py + vy * 1000)
                elif self.tick > 150:
                    self.img.set_alpha((self.tick - 150) * 255 // 30)
            else:
                self.hp_sys(op='config', immune=False)
                self.tick = (self.tick + 1) % 80
                if 60 < self.tick < 70:
                    self.img.set_alpha(255 - (self.tick - 60) * 255 // 10)
                elif self.tick == 70:
                    px, py = game.get_game().player.obj.pos
                    vx, vy = vector.rotation_coordinate(random.randint(0, 359))
                    self.obj.pos << (px + vx * 1000, py + vy * 1000)
                elif self.tick > 70:
                    self.img.set_alpha((self.tick - 70) * 255 // 10)
            self.set_rotation(self.rot)

    class HeavenBall(MagmaKingFireball):
        NAME = 'Heaven Ball'

        def __init__(self, pos, rot):
            super().__init__(pos, rot)
            self.img = game.get_game().graphics['entity_heaven_ball']

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 8:
                game.get_game().player.hp_sys.damage(88, damages.DamageTypes.MAGICAL)
                if not game.get_game().player.hp_sys.is_immune:
                    game.get_game().player.obj.apply_force(vector.Vector(self.rot, 120))
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class SandStormAttack(MagmaKingFireball):

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(77, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class HeavenGuard(Entity):
        NAME = 'Heaven Guard'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])

        SOUND_HURT = 'sticky'
        SOUND_DEATH = 'sticky'

        @staticmethod
        def is_suitable(biome: str):
            return True

        def __init__(self, pos):
            if game.get_game().stage:
                super().__init__(pos, game.get_game().graphics['entity_heaven_guard'], RangedAI, 8800)
            else:
                super().__init__(pos, game.get_game().graphics['entity_heaven_guard'], RangedAI, 550)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 55
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 62
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 57
            self.tick = 0
            if game.get_game().stage:
                self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 88
                self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 94
                self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 89
                self.obj.SPEED *= 5.0
                self.obj.SIGHT_DISTANCE *= 1.5
                self.obj.MASS *= 3
                self.NAME = 'The Heaven\'s Guard'

        def on_update(self):
            px, py = game.get_game().player.obj.pos
            self.set_rotation(-vector.coordinate_rotation(px - self.obj.pos[0], py - self.obj.pos[1]))
            self.tick += 1
            if vector.distance(self.obj.pos[0] - px, self.obj.pos[1] - py) < self.obj.SIGHT_DISTANCE:
                if self.tick % 18 == 1:
                    game.get_game().entities.append(Entities.HeavenBall(self.obj.pos, self.rot))

    class MagmaKing(Entity):
        NAME = 'Magma King'
        DISPLAY_MODE = 3
        VITAL = True
        LOOT_TABLE = LootTable([
        ])

        SOUND_SPAWN = 'boss'
        SOUND_HURT = 'sticky'
        SOUND_DEATH = 'huge_monster'

        PHASE_SEGMENTS = [0.15, 0.3, 0.4, 0.8, 0.9]

        def __init__(self, pos, cps=0, hp=28800):
            super().__init__(pos, pg.transform.scale_by(game.get_game().graphics['entity_magma_king'], 1 / 1.1 ** cps),
                             MagmaKingAI, 28800)
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 32
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 28
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 28
            self.phase = cps
            self.hp_sys.hp = hp
            self.hp_sys.max_hp = hp

        def on_update(self):
            super().on_update()
            if self.phase < 3 and self.hp_sys.hp <= self.hp_sys.max_hp * self.PHASE_SEGMENTS[-1 - self.phase * 2]:
                self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] -= 10
                self.hp_sys.defenses[damages.DamageTypes.MAGICAL] -= 10
                self.hp_sys.defenses[damages.DamageTypes.PIERCING] -= 10
                self.phase += 1
                self.hp_sys.hp //= 2
                game.get_game().entities.append(Entities.MagmaKing(self.obj.pos, cps=self.phase, hp=self.hp_sys.hp))
            if self.obj.state == 2 and self.obj.timer % (10 - self.phase) == 1:
                player = game.get_game().player
                game.get_game().entities.append(Entities.MagmaKingFireball(self.obj.pos, vector.coordinate_rotation(
                    player.obj.pos[0] - self.obj.pos[0], player.obj.pos[1] - self.obj.pos[1])))
            if self.obj.state == 1 and self.obj.timer % 40 == 20:
                player = game.get_game().player
                for k in range(-30 - self.phase * 5, 31 + self.phase * 5, max(5, 20 - self.phase * 5)):
                    fb = Entities.MagmaKingFireball(self.obj.pos,
                                                    k + vector.coordinate_rotation(player.obj.pos[0] - self.obj.pos[0],
                                                                                   player.obj.pos[1] - self.obj.pos[1]))
                    fb.obj.apply_force(
                        vector.Vector(self.obj.velocity.get_net_rotation(), self.obj.velocity.get_net_value() // 50))
                    game.get_game().entities.append(fb)

    class MagmaKingCounter(Entity):
        NAME = 'Magma King'

        LOOT_TABLE = LootTable([
            IndividualLoot('blood_ingot', .7, 10, 20),
            IndividualLoot('firite_ingot', .9, 10, 30),
            IndividualLoot('firy_plant', 1, 20, 25),
            IndividualLoot('tip3', 1, 1, 1),
        ])

        BOSS_NAME = 'The Fire Monster'
        PHASE_SEGMENTS = [0.15, 0.3, 0.4, 0.8, 0.9]
        IS_MENACE = True

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_magma_king'], BuildingAI, 1000000)
            self.obj.IS_OBJECT = False

        def draw(self):
            pass

        def on_update(self):
            s = 0
            sm = 1
            for i, e in enumerate([ee for ee in game.get_game().entities if type(ee) is Entities.MagmaKing]):
                if not i:
                    self.obj.pos = e.obj.pos
                s += e.hp_sys.hp
                sm += e.hp_sys.max_hp
            self.hp_sys.hp = s
            self.hp_sys.max_hp = sm

    class SandStorm(Entity):
        NAME = 'Sandstorm'
        DISPLAY_MODE = 3
        IS_MENACE = True
        BOSS_NAME = 'The Ghost of Desert'
        LOOT_TABLE = LootTable([
            IndividualLoot('mysterious_ingot', 1, 15, 35),
            IndividualLoot('storm_core', 1, 2, 4),
            IndividualLoot('tornado', 0.5, 1, 1),
            IndividualLoot('tip4', 1, 1, 1),
        ])
        VITAL = True
        PHASE_SEGMENTS = [0.5]
        SOUND_SPAWN = 'boss'
        SOUND_HURT = 'skeleton'
        SOUND_DEATH = 'huge_monster'

        def __init__(self, pos, hp_sys=None, rot=0, ss=True):
            super().__init__(pos, game.get_game().graphics['entity_sandstorm'], SandStormAI, hp_sys=hp_sys if not ss else hp_system.HPSystem(32000))
            if ss:
                game.get_game().entities.append(Entities.SandStorm(pos, hp_sys=self.hp_sys, rot=rot + 180, ss=False))
                self.IS_MENACE = False
            self.obj.rot = rot
            self.obj.update()
            self.tick = 0
            self.phase = 0
            self.obj.pos << (pos[0] + random.randint(-100, 100), pos[1] + random.randint(-100, 100))
            self.obj.IS_OBJECT = False
            self.show_bar = True

        def on_update(self):
            super().on_update()
            self.tick += 1
            dr = self.phase * 2
            if self.tick % (8 - dr if self.obj.state == 0 else (5 - dr if self.obj.state == 2 else 8000)) == 1:
                px, py = game.get_game().player.obj.pos
                rot = vector.coordinate_rotation(px - self.obj.pos[0], py - self.obj.pos[1])
                self.set_rotation(rot)
                game.get_game().entities.append(Entities.SandStormAttack(self.obj.pos, self.rot + random.randint(-10, 10)))
            if self.hp_sys.hp < self.hp_sys.max_hp * 0.5 and self.phase == 0:
                self.phase = 1
                self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] += 20
                self.hp_sys.defenses[damages.DamageTypes.PIERCING] += 10
                self.hp_sys.defenses[damages.DamageTypes.MAGICAL] += 15
                self.obj = CleverRangedAI(self.obj.pos)
                self.obj.TOUCHING_DAMAGE = 450
                self.obj.SIGHT_DISTANCE = 9999
                self.obj.MASS *= 3
                self.obj.SPEED *= 8
                self.obj.shoot_distance = random.randint(500, 2000)
                self.obj.state = 0
            if self.phase == 1 and self.tick % 50 == 0:
                self.obj.shoot_distance = random.randint(500, 2000)


    class RuneRock(Entity):
        NAME = 'Rune Rock'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('magic_stone', 0.3, 20, 30),
            IndividualLoot('mysterious_substance', 0.8, 10, 12),
        ])

        SOUND_HURT = 'skeleton'
        SOUND_DEATH = 'explosive'

        @staticmethod
        def is_suitable(biome: str):
            return biome in ['desert']

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_rune_rock'], RuneRockAI, 1550)
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 32

    class AbyssRuneShoot(Entity):
        NAME = 'Abyss Rune'
        DISPLAY_MODE = 3

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_abyss_rune'], AbyssRuneShootAI, 500)
            self.obj.rot = rot
            self.obj.MASS /= 2

        def on_update(self):
            self.set_rotation(self.rot)
            self.hp_sys.hp -= 3
            self.damage()

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(144, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class TruthlessCurse(Entity):
        NAME = 'Truthless Curse'
        DISPLAY_MODE = 3

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_truthless_curse'], AbyssRuneShootAI, 12000)
            self.obj.rot = rot

        def on_update(self):
            super().on_update()
            self.set_rotation(self.rot)
            self.hp_sys.hp -= 120
            self.damage()

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(360, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.effect(effects.TruthlessCurse(2, 30))
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class FaithlessCurse(Entity):
        NAME = 'Faithless Curse'
        DISPLAY_MODE = 3

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_faithless_curse'], AbyssRuneShootAI, 12000)
            self.obj.rot = rot

        def on_update(self):
            super().on_update()
            self.set_rotation(self.rot)
            self.hp_sys.hp -= 120
            self.damage()

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(280, damages.DamageTypes.MAGICAL)
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

        def on_update(self):
            super().on_update()
            self.hp_sys.hp -= 200000
            self.damage()
            self.set_rotation(90 - self.obj.rot)

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 50:
                game.get_game().player.hp_sys.damage(540, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class AlmondBullet(Entity):
        NAME = 'Almond Bullet'
        DISPLAY_MODE = 1

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_almond_bullet'], FastBulletAI, 50000000)
            self.obj.rot = rot
            self.obj.speed = 500

        def on_update(self):
            super().on_update()
            self.hp_sys.hp -= 200000
            self.damage()
            self.set_rotation(90 - self.obj.rot)

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 50:
                game.get_game().player.hp_sys.damage(540, damages.DamageTypes.MAGICAL)
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

        def on_update(self):
            super().on_update()
            self.hp_sys.hp -= 200000
            self.damage()
            self.set_rotation(90 - self.obj.rot)
            if self.r and self.mode == 'heart':
                self.rt += 5
                for i in range(4):
                    rr = self.rt + i * 90
                    ax, ay = vector.rotation_coordinate(rr)
                    self.buls[i].obj.pos << (self.obj.pos[0] + ax * 100, self.obj.pos[1] + ay * 100)


        def damage(self):
            if self.mode == 'heart' and not self.r:
                return
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 50:
                game.get_game().player.hp_sys.damage(480, damages.DamageTypes.MAGICAL)
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

        def on_update(self):
            super().on_update()
            self.hp_sys.hp -= 200000
            self.set_rotation(-self.obj.rot)
            self.damage()

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 320:
                game.get_game().player.hp_sys.damage(360, damages.DamageTypes.MAGICAL)
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

        def on_update(self):
            super().on_update()
            self.hp_sys.hp -= 200000
            self.damage()

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 220:
                game.get_game().player.hp_sys.damage(640, damages.DamageTypes.MAGICAL)
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

        def on_update(self):
            super().on_update()
            self.obj.pos << (self.obj.pos[0], self.obj.pos[1] + 75)
            self.hp_sys.hp -= 75 * 10 ** 5
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
            super().__init__(pos, game.get_game().graphics['entity_time'], AbyssRuneShootAI, 5000)
            self.obj.rot = rot

        def on_update(self):
            super().on_update()
            self.set_rotation(self.rot)
            self.hp_sys.hp -= 20
            self.damage()

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(360, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class DevilsMark(Entity):
        NAME = 'Devil\'s Mark'
        DISPLAY_MODE = 3

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_devils_mark'], BuildingAI, 500000)
            self.tick = 0

        def on_update(self):
            super().on_update()
            self.hp_sys.hp -= 20000
            self.img = pg.transform.scale_by(game.get_game().graphics['entity_devils_mark'], 1 + self.tick * 0.15)
            if constants.USE_ALPHA:
                self.d_img = copy.copy(self.img)
                self.d_img.set_alpha(255 - self.tick)
            if self.tick > 250:
                self.hp_sys.hp = 0
            self.damage()
            self.tick += 1

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < self.d_img.get_width() / 2:
                game.get_game().player.hp_sys.damage(360, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()

    class Lazer(Entity):
        NAME = 'Lazer'
        DISPLAY_MODE = 1

        SOUND_SPAWN = 'lazer'

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_lazer'], AbyssRuneShootAI, 500000)
            self.obj.rot = rot
            self.set_rotation(90 - rot)
            self.obj.apply_force(vector.Vector(rot, 32000))

        def on_update(self):
            super().on_update()
            self.set_rotation(self.rot)
            self.hp_sys.hp -= 2000
            self.damage()

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(188, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class FireBreath(Entity):
        NAME = 'Dragon Breath: Fire'

        def __init__(self, pos, rot, target):
            super().__init__(pos, game.get_game().graphics['entity_fire_breath'], MonsterAI, 500000)
            self.obj.rot = rot
            self.target = target
            self.tick = 0

        def t_draw(self):
            if self.tick > 10:
                game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                         col=(255, 0, 0), sp=20 / game.get_game().player.get_screen_scale(),
                                                                        t=30, n=5, g=-0.1))
            else:
                pg.draw.circle(game.get_game().displayer.canvas, (255, 0, 0), position.displayed_position(self.obj.pos),
                               20 / game.get_game().player.get_screen_scale())
                game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                        col=(255, 0, 0),
                                                                        sp=10 / game.get_game().player.get_screen_scale(),
                                                                        t=15, n=6))

        def on_update(self):
            super().on_update()
            self.tick += 1
            if self.tick < 10:
                self.obj.pos << ((self.obj.pos[0] * 3 + self.target[0]) / 4,
                                (self.obj.pos[1] * 3 + self.target[1]) / 4)
            if vector.distance(self.obj.pos[0] - self.target[0],
                               self.obj.pos[1] - self.target[1]) < 50:
                self.tick = 10
            self.hp_sys.hp -= 5000
            self.damage()

        def damage(self):
            if self.tick > 10:
                r = 600
            else:
                r = 20
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < r:
                game.get_game().player.hp_sys.damage(640, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.effect(effects.Burning(10, 3))
                game.get_game().player.hp_sys.enable_immume()

    class IceBreath(Entity):
        NAME = 'Dragon Breath: Ice'

        def __init__(self, pos, rot, target):
            super().__init__(pos, game.get_game().graphics['entity_ice_breath'], MonsterAI, 500000)
            self.obj.rot = rot
            self.target = target
            self.tick = 0

        def t_draw(self):
            if self.tick > 10:
                game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                        col=(200, 255, 255),
                                                                        sp=20 / game.get_game().player.get_screen_scale(),
                                                                        t=30, n=5, g=-0.1))
            else:
                pg.draw.circle(game.get_game().displayer.canvas, (200, 255, 255),
                               position.displayed_position(self.obj.pos),
                               20 / game.get_game().player.get_screen_scale())
                game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                        col=(200, 255, 255),
                                                                        sp=10 / game.get_game().player.get_screen_scale(),
                                                                        t=15, n=6))

        def on_update(self):
            super().on_update()
            self.tick += 1
            if self.tick < 10:
                self.obj.pos << ((self.obj.pos[0] * 3 + self.target[0]) / 4,
                                (self.obj.pos[1] * 3 + self.target[1]) / 4)
            if vector.distance(self.obj.pos[0] - self.target[0],
                               self.obj.pos[1] - self.target[1]) < 50:
                self.tick = 10
            self.hp_sys.hp -= 5000
            self.damage()

        def damage(self):
            if self.tick > 10:
                r = 600
            else:
                r = 20
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < r:
                game.get_game().player.hp_sys.damage(680, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.effect(effects.Freezing(7, 3))
                game.get_game().player.hp_sys.enable_immume()

    class DarkBreath(Entity):
        NAME = 'Dragon Breath: Dark'

        def __init__(self, pos, rot, target):
            super().__init__(pos, game.get_game().graphics['entity_dark_breath'], MonsterAI, 500000)
            self.obj.rot = rot
            self.target = target
            self.tick = 0

        def t_draw(self):
            if self.tick > 10:
                game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                        col=(50, 0, 50),
                                                                        sp=20 / game.get_game().player.get_screen_scale(),
                                                                        t=30, n=5, g=-0.1))
            else:
                pg.draw.circle(game.get_game().displayer.canvas, (0, 0, 0),
                               position.displayed_position(self.obj.pos),
                               20 / game.get_game().player.get_screen_scale())
                game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                         col=(50, 0, 50),
                                                                         sp=10 / game.get_game().player.get_screen_scale(),
                                                                         t=15, n=6))

        def on_update(self):
            super().on_update()
            self.tick += 1
            if self.tick < 10:
                self.obj.pos << ((self.obj.pos[0] * 2 + self.target[0]) / 3,
                                (self.obj.pos[1] * 2 + self.target[1]) / 3)
            if vector.distance(self.obj.pos[0] - self.target[0],
                               self.obj.pos[1] - self.target[1]) < 50:
                self.tick = max(10, self.tick)
            self.hp_sys.hp -= 5000
            self.damage()

        def damage(self):
            if self.tick > 10:
                r = 600
            else:
                r = 20
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < r:
                game.get_game().player.hp_sys.damage(750, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.effect(effects.Darkened(5, 3))
                game.get_game().player.hp_sys.enable_immume()

    class LightBreath(Entity):
        NAME = 'Dragon Breath: Light'

        def __init__(self, pos, rot, target):
            super().__init__(pos, game.get_game().graphics['entity_light_breath'],
                             MonsterAI, 500000)
            self.obj.rot = rot
            self.target = target
            self.tick = 0

        def t_draw(self):
            if self.tick > 10:
                game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                        col=(255, 255, 200),
                                                                        sp=20 / game.get_game().player.get_screen_scale(),
                                                                        t=30, n=5, g=-0.1))
            else:
                pg.draw.circle(game.get_game().displayer.canvas, (0, 0, 0),
                               position.displayed_position(self.obj.pos),
                               20 / game.get_game().player.get_screen_scale())
                game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                        col=(255, 200, 200),
                                                                        sp=10 / game.get_game().player.get_screen_scale(),
                                                                        t=15, n=6))

        def on_update(self):
            super().on_update()
            self.tick += 1
            if self.tick < 10:
                self.obj.pos << ((self.obj.pos[0] * 2 + self.target[0]) / 3,
                                (self.obj.pos[1] * 2 + self.target[1]) / 3)
            if vector.distance(self.obj.pos[0] - self.target[0],
                               self.obj.pos[1] - self.target[1]) < 50:
                self.tick = max(10, self.tick)
            self.hp_sys.hp -= 5000
            self.damage()

        def damage(self):
            if self.tick > 10:
                r = 600
            else:
                r = 20
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < r:
                game.get_game().player.hp_sys.damage(960, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.effect(effects.Enlightened(7, 3))
                game.get_game().player.hp_sys.enable_immume()

    class MechanicBreath(Entity):
        NAME = 'Dragon Breath: Mechanic'

        def __init__(self, pos, rot, target):
            super().__init__(pos, game.get_game().graphics['entity_light_breath'], MonsterAI, 500000)
            self.obj.rot = rot
            self.target = target
            self.tick = 0

        def t_draw(self):
            if self.tick > 10:
                if self.tick % 10 == 0:
                    rot = random.randint(0, 360)
                    ax, ay = vector.rotation_coordinate(rot)
                    game.get_game().entities.append(Entities.CyberBreath(self.obj.pos, rot,
                                                                         (self.obj.pos[0] + ax * 1200, self.obj.pos[1] + ay * 1200)))
                game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                        col=(100, 100, 100),
                                                                        sp=20 / game.get_game().player.get_screen_scale(),
                                                                        t=30, n=5, g=-0.1))
            else:
                pg.draw.circle(game.get_game().displayer.canvas, (100, 100, 100),
                               position.displayed_position(self.obj.pos),
                               20 / game.get_game().player.get_screen_scale())
                game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                        col=(100, 100, 100),
                                                                        sp=10 / game.get_game().player.get_screen_scale(),
                                                                        t=15, n=6))

        def on_update(self):
            super().on_update()
            self.tick += 1
            if self.tick < 10:
                self.obj.pos << ((self.obj.pos[0] * 2 + self.target[0]) / 3,
                                (self.obj.pos[1] * 2 + self.target[1]) / 3)
            if vector.distance(self.obj.pos[0] - self.target[0], self.obj.pos[1] - self.target[1]) < 50:
                self.tick = max(10, self.tick)
            self.hp_sys.hp -= 5000
            self.damage()

        def damage(self):
            if self.tick > 10:
                r = 600
            else:
                r = 20
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < r:
                game.get_game().player.hp_sys.damage(1280, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()

    class CyberBreath(Entity):
        NAME = 'Dragon Breath: Cyber'

        def __init__(self, pos, rot, target):
            super().__init__(pos, game.get_game().graphics['entity_light_breath'], MonsterAI, 500000)
            self.obj.rot = rot
            self.target = target
            self.tick = 0

        def t_draw(self):
            if self.tick > 10:
                game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                        col=(227, 255, 200),
                                                                        sp=20 / game.get_game().player.get_screen_scale(),
                                                                        t=10, n=2, g=-0.1))
            else:
                pg.draw.circle(game.get_game().displayer.canvas, (227, 255, 200),
                               position.displayed_position(self.obj.pos),
                               20 / game.get_game().player.get_screen_scale())
                game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                        col=(227, 255, 200),
                                                                        sp=10 / game.get_game().player.get_screen_scale(),
                                                                        t=15, n=2))

        def on_update(self):
            super().on_update()
            self.tick += 1
            if self.tick < 10:
                self.obj.pos << ((self.obj.pos[0] * 2 + self.target[0]) / 3,
                                (self.obj.pos[1] * 2 + self.target[1]) / 3)
            if vector.distance(self.obj.pos[0] - self.target[0],
                               self.obj.pos[1] - self.target[1]) < 50:
                self.tick = max(10, self.tick)
            self.hp_sys.hp -= 5000
            self.damage()

        def damage(self):
            if self.tick > 10:
                r = 200
            else:
                r = 20
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < r:
                game.get_game().player.hp_sys.damage(1140, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()

    class UniSpike(Lazer):
        NAME = 'Uni-Spike'
        SOUND_SPAWN = None

        def __init__(self, pos, rot):
            super(Entities.Lazer, self).__init__(pos, game.get_game().graphics['entity_uni_spike'], AbyssRuneShootAI, 500000)
            self.obj.rot = rot
            self.set_rotation(90 - rot)
            self.obj.apply_force(vector.Vector(rot, 36000))

        def on_update(self):
            super().on_update()
            self.set_rotation(self.rot + 18)

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(158, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class IceShard(Lazer):
        NAME = 'Ice Shard'
        SOUND_SPAWN = None

        def __init__(self, pos, rot):
            super(Entities.Lazer, self).__init__(pos, game.get_game().graphics['entity_ice_shard'], AbyssRuneShootAI, 500000)
            self.obj.rot = rot
            self.set_rotation(90 - rot)
            self.obj.apply_force(vector.Vector(rot, 128000))

        def on_update(self):
            super().on_update()
            self.set_rotation(self.rot + 18)

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 60:
                game.get_game().player.hp_sys.damage(228, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class WitherSkull(Lazer):
        NAME = 'Wither Skull'
        SOUND_SPAWN = None
        SOUND_DEATH = 'explosion'

        def __init__(self, pos, rot):
            super(Entities.Lazer, self).__init__(pos, game.get_game().graphics['entity_wither_skull'], AbyssRuneShootAI, 500000)
            self.obj.rot = rot
            self.set_rotation(90 - rot)
            self.obj.apply_force(vector.Vector(rot, random.randint(36000, 108000)))
            self.obj.MASS /= 3
            self.ex_t = 0

        def on_update(self):
            super().on_update()

        def damage(self):
            self.ex_t += 1
            if random.randint(0, self.ex_t) > 10:
                game.get_game().displayer.effect(fc.p_fade_circle(*position.displayed_position(self.obj.pos),
                                                                   col=(0, 0, 0), sp=30,
                                                                   t=10))
                if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                                   self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 300:
                    game.get_game().player.hp_sys.damage(120, damages.DamageTypes.MAGICAL)
                    game.get_game().player.hp_sys.effect(effects.Wither(10, 5))
                    game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class LifeShard(Lazer):
        NAME = 'Life Shard'
        SOUND_SPAWN = None

        def __init__(self, pos, rot):
            super(Entities.Lazer, self).__init__(pos, game.get_game().graphics['entity_life_shard'], AbyssRuneShootAI, 500000)
            self.obj.rot = rot
            self.set_rotation(90 - rot)
            self.obj.MASS /= 4
            self.obj.apply_force(vector.Vector(rot + random.randint(60, 130) * random.choice([-1, 1]),
                                               random.randint(80000, 120000)))
            self.obj.FRICTION = 1
            self.ex_t = 0

        def on_update(self):
            super().on_update()

        def damage(self):
            self.ex_t += 1
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 300:
                game.get_game().player.hp_sys.damage(255, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class PoisonSaliva(Lazer):
        NAME = 'Poison Saliva'
        SOUND_SPAWN = None

        def __init__(self, pos, rot):
            super(Entities.Lazer, self).__init__(pos, game.get_game().graphics['entity_poison_saliva'], AbyssRuneShootAI, 500000)
            self.obj.rot = rot
            self.set_rotation(90 - rot)
            self.obj.apply_force(vector.Vector(rot, 36000))

        def on_update(self):
            super().on_update()
            self.set_rotation(self.rot + 18)

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(220, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.effect(effects.Sticky(6, 10))
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class GoblinArrow(Lazer):
        NAME = 'Goblin Arrow'
        SOUND_SPAWN = None

        def __init__(self, pos, rot):
            super(Entities.Lazer, self).__init__(pos, game.get_game().graphics['entity_goblin_arrow'], AbyssRuneShootAI, 500000)
            self.obj.rot = rot
            self.set_rotation(90 - rot)
            self.obj.apply_force(vector.Vector(rot, 36000))

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
                game.get_game().player.hp_sys.damage(168, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class GoblinOctave(Lazer):
        NAME = 'Goblin Octave'
        SOUND_SPAWN = None

        def __init__(self, pos, rot):
            super(Entities.Lazer, self).__init__(pos, game.get_game().graphics['entity_null'], AbyssRuneShootAI, 500000)
            self.img = pg.Surface((50, 120), pg.SRCALPHA)
            pg.draw.ellipse(self.img, (200, 200, 200), (0, 0, 50, 120), 8)
            self.obj.rot = rot
            self.set_rotation(90 - rot)
            self.obj.apply_force(vector.Vector(rot, 72000))

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 66:
                if game.get_game().player.hp_sys.is_immune:
                    return
                game.get_game().player.hp_sys.damage(144, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()

    class AbyssRune(Entity):
        NAME = 'Abyss Rune'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('soul', 0.9, 1, 2),
        ])
        VITAL = True

        def __init__(self, pos, rot, dis, hp=10000, ar=6):
            super().__init__(pos, game.get_game().graphics['entity_abyss_rune'], AbyssRuneAI, hp)
            self.obj.rot = rot
            self.obj.d = dis
            self.obj.ar = ar / 10

        def on_update(self):
            super().on_update()
            e = [e for e in game.get_game().entities if type(e) is Entities.AbyssEye]
            if not len(e):
                self.hp_sys.hp -= self.hp_sys.max_hp // 300

    class AbyssEye(Entity):
        NAME = 'Abyss Eye'
        DISPLAY_MODE = 3
        IS_MENACE = True
        BOSS_NAME = 'The Dimensional Intruder'
        LOOT_TABLE = LootTable([
            IndividualLoot('soul', 1, 100, 200),
            SelectionLoot([('spiritual_stabber', 1, 1), ('spiritual_piercer', 1, 1), ('spiritual_destroyer', 1, 1)], 1,
                          2),
            IndividualLoot('tip5', 1, 1, 1),
            IndividualLoot('spiritual_pickaxe', 1, 1, 1)
        ])

        SOUND_SPAWN = 'boss'
        SOUND_HURT = 'monster'
        SOUND_DEATH = 'huge_monster'

        PHASE_SEGMENTS = [0.2, 0.55]

        @staticmethod
        def is_suitable(biome: str):
            return biome in ['heaven']

        def __init__(self, pos):
            if game.get_game().chapter == 1:
                self.LOOT_TABLE = LootTable([
                    IndividualLoot('muse_core', 1, 1, 1),
                    IndividualLoot('bible', 1, 1, 1),
                    IndividualLoot('z', 1, 1, 1),
                    ])
            super().__init__(pos, game.get_game().graphics['entity_abyss_eye'], AbyssEyeAI, 64000)
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 20
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 25
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 23
            self.tick = 0
            self.state = 0
            self.rounds = 0
            self.phase = 0
            for i in range(5):
                for r in range(0, 361, [60, 40, 30, 20, 15, 10][i]):
                    game.get_game().entities.append(
                        Entities.AbyssRune((0, 0), r, i * 300 + 300, 15000 - i * i * 500, int((-1.15) ** i * 3)))
            for r in range(0, 361, 5):
                game.get_game().entities.append(Entities.AbyssRune((0, 0), r, 1800, 10000000, 12))
            self.rr = [180, 120, 90, 72, 60]

        def on_update(self):
            super().on_update()
            game.get_game().day_time = 0
            self.tick += 1
            if self.hp_sys.hp < self.hp_sys.max_hp * .55 and self.phase == 0:
                self.phase = 1
                for e in game.get_game().entities:
                    e.hp_sys.damage(10000, damages.DamageTypes.TRUE)
                self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] += 20
                self.hp_sys.defenses[damages.DamageTypes.PIERCING] += 20
                self.hp_sys.defenses[damages.DamageTypes.MAGICAL] += 20
                self.rounds += 2
                self.rr.extend([45, 40, 36, 30])
            elif self.hp_sys.hp < self.hp_sys.max_hp * .2 and self.phase == 1:
                self.phase = 2
                for e in game.get_game().entities:
                    e.hp_sys.damage(4000, damages.DamageTypes.TRUE)
                self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] += 20
                self.hp_sys.defenses[damages.DamageTypes.PIERCING] += 20
                self.hp_sys.defenses[damages.DamageTypes.MAGICAL] += 20
                self.hp_sys.defenses[damages.DamageTypes.MAGICAL] += 20
                self.rounds += 2
                self.rr.extend([24, 20, 18])
            if self.tick > random.randint(200, 400):
                self.tick = 0
                self.state = (self.state + 1) % 3
                if not self.state:
                    self.rounds += 1
            if self.state == 0:
                if self.tick % 4 == 1:
                    game.get_game().entities.append(Entities.AbyssRuneShoot(self.obj.pos, self.tick * 2))
            elif self.state == 1:
                if self.tick % 12 == 1:
                    game.get_game().entities.append(Entities.AbyssRuneShoot(self.obj.pos, random.randint(0, 360)))
            else:
                if self.tick % 6 - self.phase == 1:
                    if self.rounds < len(self.rr):
                        k = self.rr[self.rounds]
                    else:
                        k = 45
                    for r in range(0, 360, k):
                        game.get_game().entities.append(Entities.AbyssRuneShoot(self.obj.pos, self.tick * (6 + self.phase) // 6 + r))

    class SwordInTheStone(Ore):
        NAME = 'Sword in the Stone'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            SelectionLoot([('magic_sword', 1, 1), ('magic_blade', 1, 1)], 1, 1)
        ])
        IMG = 'entity_sword_in_the_stone'
        TOUGHNESS = 2

        def __init__(self, pos):
            super().__init__(pos, 100)

    class EvilMark(Ore):
        NAME = 'Evil Mark'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('soul', 0.9, 6, 7),
            IndividualLoot('evil_ingot', 1, 10, 12),
            SelectionLoot([('tip61', 1, 1), ('tip62', 1, 1), ('tip63', 1, 1)], 1, 1),
        ])
        TOUGHNESS = 50
        IMG = 'entity_evil_mark'

        def __init__(self, pos):
            super().__init__(pos, 80)

    class SoulFlower(Entity):
        NAME = 'Soul Flower'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('mana_crystal', 0.9, 15, 25),
            IndividualLoot('seatea', 0.9, 12, 16),
            IndividualLoot('evil_ingot', 0.6, 1, 3),
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 0, 1)
        ])

        SOUND_HURT = 'monster'
        SOUND_DEATH = 'sticky'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_soul_flower'], SoulFlowerAI, 2600)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 50
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 80
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 60

    class UniSaur(Entity):
        NAME = 'Uni-saur'
        DISPLAY_MODE = 2
        LOOT_TABLE = LootTable([
            IndividualLoot('seatea', 0.9, 12, 16),
            IndividualLoot('evil_ingot', 0.6, 12, 20),
            IndividualLoot('colourful_substance', 0.2, 1, 2),
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 0, 1)
        ])

        SOUND_HURT = 'dragon'
        SOUND_DEATH = 'monster'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_uni_saur'], SoulFlowerAI, 4800)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 100
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 120
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 100
            self.obj.TOUCHING_DAMAGE = 180
            self.obj.SIGHT_DISTANCE *= 2
            self.tick = 0

        def on_update(self):
            super().on_update()
            self.tick += 1
            px, py = (game.get_game().player.obj.pos[0] - self.obj.pos[0],
                      game.get_game().player.obj.pos[1] - self.obj.pos[1])
            self.set_rotation((self.rot * 2 + vector.coordinate_rotation(px, py)) // 3)
            if 800 > vector.distance(px, py) > 400:
                if self.tick % 38 == 1:
                    game.get_game().entities.append(Entities.UniSpike(self.obj.pos, self.rot))

    class LightFly(Entity):
        NAME = 'Light Fly'
        DISPLAY_MODE = 2
        LOOT_TABLE = LootTable([
            IndividualLoot('soul_of_flying', 0.9, 5, 12),
            IndividualLoot('evil_ingot', 0.9, 2, 5),
            IndividualLoot('starlight_shard', 0.1, 1, 2),
            IndividualLoot('evil_ingot', 0.6, 12, 20),
            IndividualLoot('colourful_substance', 0.2, 1, 2),
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 0, 1)
        ])

        SOUND_HURT = 'crystal'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_night_fly'], SoulFlowerAI, 2200)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 100
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 120
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 100
            self.obj.TOUCHING_DAMAGE = 220
            self.obj.MASS /= 3
            self.obj.SPEED *= 2
            self.obj.SIGHT_DISTANCE *= 2

        def on_update(self):
            super().on_update()
            px, py = (game.get_game().player.obj.pos[0] - self.obj.pos[0],
                      game.get_game().player.obj.pos[1] - self.obj.pos[1])
            self.set_rotation((self.rot * 2 + vector.coordinate_rotation(px, py)) // 3)

    class RedCorruption(Entity):
        NAME = 'Red Corruption'
        DISPLAY_MODE = 2
        LOOT_TABLE = LootTable([
            IndividualLoot('evil_ingot', 0.6, 12, 35),
            IndividualLoot('dark_substance', 0.2, 1, 2),
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 0, 1)
        ])

        SOUND_HURT = 'corrupt'
        SOUND_DEATH = 'sticky'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_red_corruption'], SlowMoverAI, 8800)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 150
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 180
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 150
            self.obj.SPEED *= 2
            self.obj.MASS *= 3
            self.obj.TOUCHING_DAMAGE = 280
            self.obj.SIGHT_DISTANCE *= 3
            self.tick = 0

        def on_update(self):
            super().on_update()
            px, py = (game.get_game().player.obj.pos[0] - self.obj.pos[0],
                      game.get_game().player.obj.pos[1] - self.obj.pos[1])
            self.set_rotation((self.rot * 2 - vector.coordinate_rotation(px, py)) // 3)
            self.tick += 1
            if vector.distance(px, py) < 400 and self.tick % 5 == 1:
                game.get_game().player.hp_sys.effect(effects.Wither(12, 1))

    class PurpleCorruption(Entity):
        NAME = 'Red Corruption'
        DISPLAY_MODE = 2
        LOOT_TABLE = LootTable([
            IndividualLoot('evil_ingot', 0.6, 12, 35),
            IndividualLoot('dark_substance', 0.2, 1, 2),
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 0, 1)
        ])

        SOUND_HURT = 'corrupt'
        SOUND_DEATH = 'sticky'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_purple_corruption'], SlowMoverAI, 4800)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 150
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 180
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 150
            self.obj.SPEED *= 3
            self.obj.MASS *= 3
            self.obj.TOUCHING_DAMAGE = 280
            self.obj.SIGHT_DISTANCE *= 3
            self.tick = 0

        def on_update(self):
            super().on_update()
            px, py = (game.get_game().player.obj.pos[0] - self.obj.pos[0],
                      game.get_game().player.obj.pos[1] - self.obj.pos[1])
            self.set_rotation((self.rot * 2 - vector.coordinate_rotation(px, py)) // 3)
            self.tick += 1
            if vector.distance(px, py) < 400 and self.tick % 4 == 1:
                game.get_game().player.hp_sys.effect(effects.Wither(15, 1))

    class PolarSnowman(Entity):
        NAME = 'Polar Snowman'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('evil_ingot', 0.6, 12, 35),
            IndividualLoot('cold_substance', 0.2, 1, 2),
            ])

        SOUND_HURT = 'ore'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_polar_snowman'], RangedAI, 2500)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 180
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 200
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 180
            self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 100
            self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 120
            self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 80
            self.obj.SPEED *= 10
            self.obj.MASS *= 4
            self.obj.TOUCHING_DAMAGE = 360

    class TheWither(Entity):
        NAME = 'The Wither'
        DISPLAY_MODE = 3
        IS_MENACE = True
        BOSS_NAME = 'The Contanminated Destroyer'
        PHASE_SEGMENTS = [0.4, 0.7]
        LOOT_TABLE = LootTable([
            IndividualLoot('evil_ingot', 0.9, 2, 5),
            IndividualLoot('starlight_shard', 0.3, 1, 1),
        ])

        SOUND_HURT = 'skeleton'
        SOUND_DEATH = 'huge_monster'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_the_wither'], CleverRangedAI, 88000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 188
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 180
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 160
            self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 160
            self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 150
            self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 80

            self.obj.SPEED *= 8
            self.obj.MASS *= 5
            self.obj.TOUCHING_DAMAGE = 350
            self.obj.SIGHT_DISTANCE *= 5
            self.obj.shoot_distance = 1200
            self.tt = 0
            self.phase = 0

            game.get_game().player.hp_sys.effect(effects.Wither(180, 5))

        def on_update(self):
            super().on_update()
            self.tt += 1
            px, py = (game.get_game().player.obj.pos[0] - self.obj.pos[0],
                      game.get_game().player.obj.pos[1] - self.obj.pos[1])
            rt = vector.coordinate_rotation(px, py)
            if self.tt % 3 == 0 and vector.distance(px, py) < 800:
                game.get_game().player.hp_sys.effect(effects.Wither(100, 1))
            if self.phase == 0:
                if self.tt % 16 == 1:
                    game.get_game().entities.append(Entities.WitherSkull(self.obj.pos, rt))
                if self.hp_sys.hp < self.hp_sys.max_hp * .7:
                    self.phase = 1
                    self.obj.SPEED *= 2.5
                    self.obj.shoot_distance = 500
            elif self.phase == 1:
                if self.tt % 5 == 1:
                    game.get_game().entities.append(Entities.WitherSkull(self.obj.pos, rt + random.randint(-60, 60)))
                if self.hp_sys.hp < self.hp_sys.max_hp * .4:
                    self.phase = 2
                    self.obj.SPEED *= 2
                    self.obj.shoot_distance = 200
            elif self.phase == 2:
                if self.tt % 3 == 1:
                    game.get_game().entities.append(Entities.WitherSkull(self.obj.pos, rt + random.randint(-120, 120)))

    class LifeWatcher(Entity):
        NAME = 'Life Watcher'
        DISPLAY_MODE = 1
        IS_MENACE = True
        BOSS_NAME = 'The Cursed Fairy'
        PHASE_SEGMENTS = [0.4, 0.7]
        LOOT_TABLE = LootTable([
            IndividualLoot('evil_ingot', 0.9, 2, 5),
            IndividualLoot('starlight_shard', 0.3, 1, 1),
        ])

        SOUND_HURT = 'monster'
        SOUND_DEATH = 'huge_monster'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_life_watcher'], LifeWatcherAI, 48000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 40
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 50
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 40
            self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 20
            self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 50
            self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 10

            self.phase = 0
            self.tick = 0

        def on_update(self):
            super().on_update()
            self.tick += 1
            self.set_rotation((self.rot * 2 - self.obj.velocity.get_net_rotation()) // 3)
            if self.hp_sys.hp < self.hp_sys.max_hp * .7 and self.phase == 0:
                self.phase = 1
                self.obj.SPEED *= 4
                self.obj.MASS *= 3
                self.obj.TOUCHING_DAMAGE += 50
            if self.hp_sys.hp < self.hp_sys.max_hp * .4 and self.phase == 1:
                self.phase = 2
                self.obj.SPEED *= 2.5
                self.obj.MASS *= 2

            if self.tick % ([10, 18, 8, 24][self.obj.state] - [0, 2, 5][self.phase]) == 0:
                px, py = (game.get_game().player.obj.pos[0] - self.obj.pos[0],
                          game.get_game().player.obj.pos[1] - self.obj.pos[1])
                rot = vector.coordinate_rotation(px, py)
                game.get_game().entities.append(Entities.LifeShard(self.obj.pos, rot))

    class PolarCube(Entity):
        NAME = 'Polar Cube'
        DISPLAY_MODE = 1
        IS_MENACE = False
        BOSS_NAME = 'The Ghost of the Snowland'
        LOOT_TABLE = LootTable([
            IndividualLoot('evil_ingot', 0.6, 12, 35),
            IndividualLoot('cold_substance', 0.2, 1, 2),
            ])

        SOUND_HURT = 'crystal'
        SOUND_DEATH = 'huge_monster'

        def __init__(self, pos, hp_sys=None, t=5):
            if hp_sys is None:
                super().__init__((pos[0] + random.randint(-1000, 1000),
                                  pos[1] + random.randint(-1000, 1000)), game.get_game().graphics['entity_polar_cube'], RangedAI, 96000)
                self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 180
                self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 200
                self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 180
                self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 100
                self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 120
                self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 80
                self.IS_MENACE = True
            else:
                super().__init__(pos, game.get_game().graphics['entity_polar_cube'], RangedAI, hp_sys=hp_sys)
            if t:
                game.get_game().entities.append(Entities.PolarCube(pos, self.hp_sys, t - 1))
            self.tick = random.randint(0, 180)
            self.obj.SPEED *= 10
            self.obj.MASS *= 3
            self.obj.SPEED *= random.uniform(.5, 1.5)
            self.obj.TOUCHING_DAMAGE = 280
            self.obj.SIGHT_DISTANCE = 9999

        def on_update(self):
            super().on_update()
            self.tick += 1
            if self.tick > 180:
                self.tick %= 180
            if self.tick == 0:
                self.obj.shoot_distance = 0
            elif self.tick < 80:
                self.set_rotation(self.rot + 15)
                if self.tick % 12 == 1:
                    px, py = (game.get_game().player.obj.pos[0] - self.obj.pos[0],
                              game.get_game().player.obj.pos[1] - self.obj.pos[1])
                    for ar in [-20, 0, 20]:
                        game.get_game().entities.append(Entities.IceShard(self.obj.pos,
                                                                          vector.coordinate_rotation(px, py) + ar))
            elif self.tick == 80:
                self.obj.shoot_distance = random.randint(0, 900)
            else:
                self.set_rotation(self.rot + 36)
                if self.tick % 37 == 1:
                    sr = random.randint(0, 360)
                    for ar in range(0, 360, 30):
                        game.get_game().entities.append(Entities.IceShard(self.obj.pos, sr + ar))

    class Naga(WormEntity):
        BOSS_NAME = 'The Poison Python'
        NAME = 'Noxious Fangs: Naga'
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            IndividualLoot('naga_scale', 1, 50, 60),
            ])
        SOUND_HURT = 'dragon'
        SOUND_DEATH = 'dragon'

        def __init__(self, pos):
            super().__init__(pos, 32, game.get_game().graphics['entity_naga_head'], game.get_game().graphics['entity_naga_body'],
                             NagaAI, 3600000, body_length=250, body_touching_damage=1800)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 800
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 1000
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 800
            self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 500
            self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 600
            self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 550
            self.tick = 5

        def on_update(self):
            super().on_update()
            self.tick += 1
            if self.tick > 0 and random.randint(0, self.tick) > 120:
                self.tick = -random.randint(25, 35)
                self.obj.state = 1
            else:
                self.obj.state = 0
            if 0 >= self.tick > -15:
                self.obj.state = 2

    class Ignis(Entity):
        NAME = 'The Scorching Wing: Ignis'
        DISPLAY_MODE = 1
        IS_MENACE = True
        BOSS_NAME = 'The Fire Dragon'
        LOOT_TABLE = LootTable([
            IndividualLoot('dragon_bone', 1, 50, 60),
            IndividualLoot('dragon_skull', 1, 1, 1),
            SelectionLoot([('fire_dragon_blood', 5, 15), ('dragon_scale_red', 10, 20)], 1, 2),
            IndividualLoot('fire_dragon_heart', 1, 1, 1),
            ])
        PHASE_SEGMENTS = [0.4, 0.7]

        SOUND_HURT = 'dragon'
        SOUND_DEATH = 'dragon'

        def ssuper(self):
            return super()

        def __init__(self, pos):
            super().__init__(pos, pg.transform.scale2x(game.get_game().graphics['entity_ignis_body']),
                             DragonAI, 450000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 200
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 250
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 200
            self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 150
            self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 170
            self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 100
            self.head = Entities.Entity(pos, pg.transform.scale2x(game.get_game().graphics['entity_ignis_head']),
                                        MonsterAI, hp_sys=self.hp_sys)
            self.tail = Entities.Entity(pos, pg.transform.scale2x(game.get_game().graphics['entity_ignis_tail']),
                                        MonsterAI, hp_sys=self.hp_sys)
            self.head.obj.IS_OBJECT = False
            self.tail.obj.IS_OBJECT = False
            self.head.IS_MENACE = False
            self.head.IS_MENACE = False
            self.head.show_bar = False
            self.tail.show_bar = False
            self.head.DISPLAY_MODE = 1
            self.tail.DISPLAY_MODE = 1
            self.head.NAME = self.NAME
            self.tail.NAME = self.NAME
            self.tick = 0
            self.phase = 0
            self.limit_pt = pos

        def t_draw(self):
            if 'limit_pt' not in dir(self):
                self.limit_pt = self.obj.pos
            self.tail.obj.pos << self.obj.pos
            self.tail.t_draw()
            super().t_draw()
            self.head.obj.pos << self.obj.pos
            self.head.t_draw()
            pg.draw.circle(game.get_game().displayer.canvas, (255, 255, 255),
                            position.displayed_position(self.limit_pt),
                           8000 / game.get_game().player.get_screen_scale(), 5)
            px, py = game.get_game().player.obj.pos
            px -= self.limit_pt[0]
            py -= self.limit_pt[1]
            if vector.distance(px, py) > 8000:
                px *= 8000 / vector.distance(px, py)
                py *= 8000 / vector.distance(px, py)
                game.get_game().player.obj.pos << (px + self.limit_pt[0], py + self.limit_pt[1])
            sx, sy = self.obj.pos
            sx -= self.limit_pt[0]
            sy -= self.limit_pt[1]
            if vector.distance(sx, sy) > 8000:
                sx *= 8000 / vector.distance(sx, sy)
                sy *= 8000 / vector.distance(sx, sy)
                self.obj.pos << (sx + self.limit_pt[0], sy + self.limit_pt[1])

        def on_update(self):
            if self.phase == 0 and self.hp_sys.hp < self.hp_sys.max_hp * .7:
                self.phase = 1
                self.obj.SPEED *= 1.2
            if self.phase == 1 and self.hp_sys.hp < self.hp_sys.max_hp * .4:
                self.phase = 2
                self.obj.SPEED *= 1.5
            super().on_update()
            dr = self.obj.d_rot / 30
            self.set_rotation(-self.obj.velocity.get_net_rotation())
            self.head.set_rotation(self.rot + dr)
            self.tail.set_rotation(self.rot - dr)
            self.tick += 1
            if self.tick % 300 < 180:
                self.obj.state = 0
                fq = 20
            elif self.tick % 30 < 18:
                self.obj.state = 1
                fq = 10
            else:
                self.obj.state = 2
                fq = 4
            fq //= (self.phase + 1)
            if self.tick % fq == 1:
                for _ in range( 1):
                    game.get_game().entities.append(Entities.FireBreath(self.obj.pos, self.rot, (game.get_game().player.obj.pos[0] + random.randint(-500 - self.phase * 200, 500 + self.phase * 200),
                                                                                                  game.get_game().player.obj.pos[1] + random.randint(-500 - self.phase * 200, 500 + self.phase * 200))))

    class Northrend(Ignis):
        NAME = 'The Frost Breath: Northrend'
        DISPLAY_MODE = 1
        IS_MENACE = True
        BOSS_NAME = 'The Ice Dragon'
        LOOT_TABLE = LootTable([
            IndividualLoot('dragon_bone', 1, 50, 60),
            IndividualLoot('dragon_skull', 1, 1, 1),
            SelectionLoot([('ice_dragon_blood', 5, 15), ('dragon_scale_blue', 10, 20)], 1, 2),
            IndividualLoot('ice_dragon_heart', 1, 1, 1),
        ])
        PHASE_SEGMENTS = [0.4, 0.7]

        def __init__(self, pos):
            super().ssuper().__init__(pos, pg.transform.scale2x(game.get_game().graphics['entity_northrend_body']),
                                                  DragonAI, 360000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 220
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 270
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 220
            self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 170
            self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 190
            self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 120
            self.head = Entities.Entity(pos, pg.transform.scale2x(game.get_game().graphics['entity_northrend_head']),
                                        MonsterAI, hp_sys=self.hp_sys)
            self.tail = Entities.Entity(pos, pg.transform.scale2x(game.get_game().graphics['entity_northrend_tail']),
                                        MonsterAI, hp_sys=self.hp_sys)
            self.head.obj.IS_OBJECT = False
            self.tail.obj.IS_OBJECT = False
            self.head.IS_MENACE = False
            self.head.IS_MENACE = False
            self.head.show_bar = False
            self.tail.show_bar = False
            self.head.DISPLAY_MODE = 1
            self.tail.DISPLAY_MODE = 1
            self.head.NAME = self.NAME
            self.tail.NAME = self.NAME
            self.tick = 0
            self.phase = 0

        def on_update(self):
            if self.phase == 0 and self.hp_sys.hp < self.hp_sys.max_hp * .7:
                self.phase = 1
                self.obj.SPEED *= 1.2
            if self.phase == 1 and self.hp_sys.hp < self.hp_sys.max_hp * .4:
                self.phase = 2
                self.obj.SPEED *= 1.5
            dr = self.obj.d_rot / 30
            self.set_rotation(-self.obj.velocity.get_net_rotation())
            self.head.set_rotation(self.rot + dr)
            self.tail.set_rotation(self.rot - dr)
            self.tick += 1
            if self.tick % 300 < 180:
                self.obj.state = 0
                fq = 16
            elif self.tick % 30 < 18:
                self.obj.state = 1
                fq = 8
            else:
                self.obj.state = 2
                fq = 3
            fq //= (self.phase + 1)
            if self.tick % fq == 1:
                for _ in range(1):
                    game.get_game().entities.append(Entities.IceBreath(self.obj.pos, self.rot, (game.get_game().player.obj.pos[0] + random.randint(-600 - self.phase * 300, 600 + self.phase * 300),
                                                                                                  game.get_game().player.obj.pos[1] + random.randint(-600 - self.phase * 300, 600 + self.phase * 300))))

    class Nefarian(Ignis):
        NAME = 'the Shadow Embrace: Nefarian'
        DISPLAY_MODE = 1
        IS_MENACE = True
        BOSS_NAME = 'The Dark Dragon'
        LOOT_TABLE = LootTable([
            IndividualLoot('dragon_bone', 1, 50, 60),
            IndividualLoot('dragon_skull', .8, 1, 1),
            SelectionLoot([('dark_dragon_blood', 5, 15), ('dragon_scale_black', 10, 20)], 1, 2),
            IndividualLoot('dark_dragon_heart', .8, 1, 1),
        ])
        PHASE_SEGMENTS = [0.55]

        def __init__(self, pos):
            super().ssuper().__init__(pos, pg.transform.scale2x(game.get_game().graphics['entity_nefarian_body']),
                                      DragonAI, 540000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 60
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 70
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 60
            self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 40
            self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 50
            self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 30
            self.head = Entities.Entity(pos, pg.transform.scale2x(game.get_game().graphics['entity_nefarian_head']),
                                        MonsterAI, hp_sys=self.hp_sys)
            self.tail = Entities.Entity(pos, pg.transform.scale2x(game.get_game().graphics['entity_nefarian_tail']),
                                        MonsterAI, hp_sys=self.hp_sys)
            self.head.obj.IS_OBJECT = False
            self.tail.obj.IS_OBJECT = False
            self.head.IS_MENACE = False
            self.head.IS_MENACE = False
            self.head.show_bar = False
            self.tail.show_bar = False
            self.head.DISPLAY_MODE = 1
            self.tail.DISPLAY_MODE = 1
            self.head.NAME = self.NAME
            self.tail.NAME = self.NAME
            self.tick = 0
            self.phase = 0

        def on_update(self):
            if self.hp_sys.hp < .55 * self.hp_sys.max_hp and self.phase == 0:
                self.phase = 1
                self.obj.SPEED *= 1.2
            dr = self.obj.d_rot / 30
            self.set_rotation(-self.obj.velocity.get_net_rotation())
            self.head.set_rotation(self.rot + dr)
            self.tail.set_rotation(self.rot - dr)
            self.tick += 1
            if self.tick % 300 < 180:
                self.obj.state = 0
                fq = 15
                fq2 = 8
            elif self.tick % 30 < 18:
                self.obj.state = 1
                fq = 12
                fq2 = 18
            else:
                self.obj.state = 2
                fq = 8
                fq2 = 20
            fq *= 2
            fq2 *= 3
            fq //= (self.phase + 1)
            fq2 //= (self.phase + 1)
            if self.tick % fq == 1:
                for _ in range(2):
                    game.get_game().entities.append(Entities.DarkBreath(self.obj.pos, self.rot, (game.get_game().player.obj.pos[0] + random.randint(-800 - self.phase * 300, 800 + self.phase * 300),
                                                                                                  game.get_game().player.obj.pos[1] + random.randint(-800 - self.phase * 300, 800 + self.phase * 300))))
            if self.tick % fq2 == 1:
                for _ in range(self.phase + 1):
                    pp = (self.obj.pos[0] + random.randint(-1000 - self.phase * 500, 1000 + self.phase * 500),
                          self.obj.pos[1] + random.randint(-1000 - self.phase * 500, 1000 + self.phase * 500))
                    tp = (game.get_game().player.obj.pos[0] + random.randint(-1000 - self.phase * 500, 1000 + self.phase * 500),
                            game.get_game().player.obj.pos[1] + random.randint(-1000 - self.phase * 500, 1000 + self.phase * 500))
                    game.get_game().entities.append(Entities.DarkBreath(pp, random.randint(0, 360), tp))
                    game.get_game().displayer.effect(fc.p_fade_circle(*position.displayed_position(tp),
                                                                      col=(50, 0, 50), sp=15, t=10))

    class Olivia(Ignis):
        NAME = 'The Radiance of Light: Olivia'
        DISPLAY_MODE = 1
        IS_MENACE = True
        BOSS_NAME = 'The Light Dragon'
        LOOT_TABLE = LootTable([
            IndividualLoot('dragon_bone', 1, 50, 60),
            IndividualLoot('dragon_skull', 1, 1, 1),
            SelectionLoot([('light_dragon_blood', 5, 15), ('dragon_scale_yellow', 10, 20)], 1, 2),
            IndividualLoot('light_dragon_heart', 1, 1, 1),
        ])
        PHASE_SEGMENTS = [0.55]

        def __init__(self, pos):
            super().ssuper().__init__(pos, pg.transform.scale2x(game.get_game().graphics['entity_olivia_body']),
                                      DragonAI, 480000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 250
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 280
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 250
            self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 200
            self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 220
            self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 150
            self.head = Entities.Entity(pos, pg.transform.scale2x(game.get_game().graphics['entity_olivia_head']),
                                        MonsterAI, hp_sys=self.hp_sys)
            self.tail = Entities.Entity(pos, pg.transform.scale2x(game.get_game().graphics['entity_olivia_tail']),
                                        MonsterAI, hp_sys=self.hp_sys)
            self.head.obj.IS_OBJECT = False
            self.tail.obj.IS_OBJECT = False
            self.head.IS_MENACE = False
            self.head.IS_MENACE = False
            self.head.show_bar = False
            self.tail.show_bar = False
            self.head.DISPLAY_MODE = 1
            self.tail.DISPLAY_MODE = 1
            self.head.NAME = self.NAME
            self.tail.NAME = self.NAME
            self.tick = 0
            self.phase = 0

        def on_update(self):
            if self.hp_sys.hp < .55 * self.hp_sys.max_hp and self.phase == 0:
                self.phase = 1
                self.obj.SPEED *= 1.2
            dr = self.obj.d_rot / 30
            self.set_rotation(-self.obj.velocity.get_net_rotation())
            self.head.set_rotation(self.rot + dr)
            self.tail.set_rotation(self.rot - dr)
            self.tick += 1
            if self.tick % 300 < 180:
                self.obj.state = 0
                fq = 15
                fq2 = 7
            elif self.tick % 30 < 18:
                self.obj.state = 1
                fq = 12
                fq2 = 16
            else:
                self.obj.state = 2
                fq = 8
                fq2 = 19
            fq *= 2
            fq2 *= 3
            fq //= (self.phase + 1)
            fq2 //= (self.phase + 1)
            if self.tick % fq == 1:
                for _ in range(2):
                    game.get_game().entities.append(Entities.LightBreath(self.obj.pos, self.rot, (
                    game.get_game().player.obj.pos[0] + random.randint(-1200 - self.phase * 300, 1200 + self.phase * 300),
                    game.get_game().player.obj.pos[1] + random.randint(-1200 - self.phase * 300,
                                                                       1200 + self.phase * 300))))
            if self.tick % fq2 == 1:
                for _ in range(self.phase + 1):
                    pp = (self.obj.pos[0] + random.randint(-1500 - self.phase * 500, 1500 + self.phase * 500),
                          self.obj.pos[1] + random.randint(-1500 - self.phase * 500, 1500 + self.phase * 500))
                    tp = (game.get_game().player.obj.pos[0] + random.randint(-1500 - self.phase * 500,
                                                                             1500 + self.phase * 500),
                          game.get_game().player.obj.pos[1] + random.randint(-1500 - self.phase * 500,
                                                                             1500 + self.phase * 500))
                    game.get_game().entities.append(Entities.LightBreath(pp, random.randint(0, 360), tp))
                    game.get_game().displayer.effect(fc.p_fade_circle(*position.displayed_position(tp),
                                                                      col=(255, 255, 200), sp=20, t=10))

    class Cybress(Ignis):
        NAME = 'The Heart of Iron: Cybress'
        DISPLAY_MODE = 1
        IS_MENACE = True
        BOSS_NAME = 'The Mechanic Dragon'
        LOOT_TABLE = LootTable([
            IndividualLoot('dragon_bone', 1, 50, 60),
            IndividualLoot('dragon_skull', 1, 1, 1),
            SelectionLoot([('mechanic_dragon_blood', 5, 15), ('dragon_scale_gray', 10, 20)], 1, 2),
            IndividualLoot('mechanic_dragon_heart', 1, 1, 1),
        ])

        def __init__(self, pos):
            self.ssuper().__init__(pos, pg.transform.scale2x(game.get_game().graphics['entity_cybress_body']),
                                      DragonAI, 320000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 350
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 380
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 350
            self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 220
            self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 240
            self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 200
            self.head = Entities.Entity(pos, pg.transform.scale2x(game.get_game().graphics['entity_cybress_head']),
                                        MonsterAI, hp_sys=self.hp_sys)
            self.tail = Entities.Entity(pos, pg.transform.scale2x(game.get_game().graphics['entity_cybress_tail']),
                                        MonsterAI, hp_sys=self.hp_sys)
            self.head.obj.IS_OBJECT = False
            self.tail.obj.IS_OBJECT = False
            self.head.IS_MENACE = False
            self.head.IS_MENACE = False
            self.head.show_bar = False
            self.tail.show_bar = False
            self.head.DISPLAY_MODE = 1
            self.tail.DISPLAY_MODE = 1
            self.head.NAME = self.NAME
            self.tail.NAME = self.NAME
            self.tick = 0
            self.phase = 0
            self.obj.SPEED *= 2.5
            self.obj.MASS *= 1.5
            self.obj.TOUCHING_DAMAGE += 100

        def on_update(self):
            dr = self.obj.d_rot / 30
            self.set_rotation(-self.obj.velocity.get_net_rotation())
            self.head.set_rotation(self.rot + dr)
            self.tail.set_rotation(self.rot - dr)
            self.tick += 1
            if self.tick % 250 < 200:
                self.obj.state = 0
                fq = 15
            elif self.tick % 25 < 18:
                self.obj.state = 1
                fq = 12
            else:
                self.obj.state = 2
                fq = 8
            fq *= 2
            if self.tick % fq == 1:
                for _ in range(2):
                    game.get_game().entities.append(Entities.MechanicBreath(self.obj.pos, self.rot, (
                        game.get_game().player.obj.pos[0] + random.randint(-1500, 1500),
                        game.get_game().player.obj.pos[1] + random.randint(-1500, 1500))))

    class Eonar(Ignis):
        NAME = 'The Whisper of Mind: Eonar'
        DISPLAY_MODE = 1
        IS_MENACE = True
        BOSS_NAME = 'The Mind Dragon'
        LOOT_TABLE = LootTable([
            IndividualLoot('dragon_bone', 1, 50, 60),
            IndividualLoot('dragon_skull', 1, 1, 1),
            SelectionLoot([('mind_dragon_blood', 5, 15), ('dragon_scale_green', 10, 20)], 1, 2),
            IndividualLoot('mind_dragon_heart', 1, 1, 1),
        ])
        def __init__(self, pos):
            self.ssuper().__init__(pos, pg.transform.scale2x(game.get_game().graphics['entity_eonar_body']),
                                      DragonAI, 180000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 100
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 150
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 100
            self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 50
            self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 70
            self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 20
            for k in self.hp_sys.resistances.resistances.keys():
                self.hp_sys.resistances[k] *= .4
            self.head = Entities.Entity(pos, pg.transform.scale2x(game.get_game().graphics['entity_eonar_head']),
                                        MonsterAI, hp_sys=self.hp_sys)
            self.tail = Entities.Entity(pos, pg.transform.scale2x(game.get_game().graphics['entity_eonar_tail']),
                                        MonsterAI, hp_sys=self.hp_sys)
            self.head.obj.IS_OBJECT = False
            self.tail.obj.IS_OBJECT = False
            self.head.IS_MENACE = False
            self.head.IS_MENACE = False
            self.head.show_bar = False
            self.tail.show_bar = False
            self.head.DISPLAY_MODE = 1
            self.tail.DISPLAY_MODE = 1
            self.head.NAME = self.NAME
            self.tail.NAME = self.NAME
            self.tick = 0
            self.phase = 0
            self.obj.TOUCHING_DAMAGE += 200
            self.obj.MASS *= .5

        def on_update(self):
            dr = self.obj.d_rot / 30
            self.set_rotation(-self.obj.velocity.get_net_rotation())
            self.head.set_rotation(self.rot + dr)
            self.tail.set_rotation(self.rot - dr)
            self.tick += 1
            if self.tick % 250 < 200:
                self.obj.state = 0
                fq = 15
            elif self.tick % 25 < 18:
                self.obj.state = 1
                fq = 12
            else:
                self.obj.state = 2
                fq = 8
            if self.tick % fq == 1:
                if random.randint(0, 2) == 0:
                    v = self.obj.velocity.get_net_value()
                    self.obj.velocity.clear()
                    self.obj.velocity.add(vector.Vector(random.randint(0, 360), v * random.uniform(1, 3)))
                elif random.randint(0, 1):
                    game.get_game().displayer.effect(fc.p_fade_circle(*position.displayed_position(self.obj.pos),
                                                                      col=(227, 255, 200), sp=80, t=10))
                    if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                                        self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 800:
                        game.get_game().player.hp_sys.damage(self.obj.TOUCHING_DAMAGE, damages.DamageTypes.MAGICAL)
                else:
                    self.obj.pos << (game.get_game().player.obj.pos[0] + random.randint(-500, 500),
                                     game.get_game().player.obj.pos[1] + random.randint(-500, 500))

    class Cells(Entity):
        NAME = 'Cells'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('soul_of_flying', 0.9, 5, 12),
            IndividualLoot('evil_ingot', 0.9, 2, 5),
            IndividualLoot('starlight_shard', 0.3, 1, 1),
        ])

        SOUND_HURT = 'sticky'
        SOUND_DEATH = 'sticky'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_cells'], CellsAI, 3200)

    class HeavenGoblinFighter(Entity):
        NAME = 'Heaven Goblin Fighter'
        DISPLAY_MODE = 2
        LOOT_TABLE = LootTable([
            IndividualLoot('wooden_stick', 0.09, 1, 1),
            IndividualLoot('spikeball', 0.09, 1, 1),
            IndividualLoot('shotgun', 0.12, 1, 1)
            ])

        SOUND_HURT = 'goblin'
        SOUND_DEATH = 'monster'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_heaven_goblin_fighter'], SoulFlowerAI, 600)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 58
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 55
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 46
            self.obj.SPEED *= 3
            self.obj.MASS *= 2.5
            self.obj.TOUCHING_DAMAGE = 188
            self.obj.SIGHT_DISTANCE *= 280

        def on_update(self):
            super().on_update()
            self.set_rotation((self.rot * 2 - self.obj.velocity.get_net_rotation()) // 3)

    class HeavenGoblinThief(Entity):
        NAME = 'Heaven Goblin Thief'
        DISPLAY_MODE = 2
        LOOT_TABLE = LootTable([
            IndividualLoot('wooden_stick', 0.09, 1, 1),
            IndividualLoot('spikeball', 0.09, 1, 1),
            ])

        SOUND_HURT = 'goblin'
        SOUND_DEATH = 'monster'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_heaven_goblin_thief'], SoulFlowerAI, 1000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = -20
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = -25
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = -30
            self.obj.SPEED *= 5
            self.obj.MASS *= 4
            self.obj.TOUCHING_DAMAGE = 225
            self.obj.SIGHT_DISTANCE *= 250

        def on_update(self):
            super().on_update()
            self.set_rotation((self.rot * 2 - self.obj.velocity.get_net_rotation()) // 3)

    class HeavenGoblinRanger(Entity):
        NAME = 'Heaven Goblin Ranger'
        DISPLAY_MODE = 2
        LOOT_TABLE = LootTable([
            IndividualLoot('wooden_stick', 0.09, 1, 1),
            IndividualLoot('spikeball', 0.09, 1, 1),
            IndividualLoot('shotgun', 0.12, 1, 1)
            ])

        SOUND_HURT = 'goblin'
        SOUND_DEATH = 'monster'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_heaven_goblin_ranger'], RangedAI, 560)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 20
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 25
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 28
            self.obj.SPEED *= 2.5
            self.obj.MASS *= 2
            self.obj.TOUCHING_DAMAGE = 88
            self.obj.SIGHT_DISTANCE *= 300
            self.tick = 0

        def on_update(self):
            super().on_update()
            px, py = (game.get_game().player.obj.pos[0] - self.obj.pos[0],
                      game.get_game().player.obj.pos[1] - self.obj.pos[1])
            rot = vector.coordinate_rotation(px, py)
            if self.tick % 25 == 1:
                game.get_game().entities.append(Entities.GoblinArrow(self.obj.pos, rot))
            self.tick += 1
            self.set_rotation((self.rot * 2 + rot) // 3)

    class HeavenGoblinPoet(Entity):
        NAME = 'Heaven Goblin Poet'
        DISPLAY_MODE = 2
        LOOT_TABLE = LootTable([
            ])

        SOUND_HURT = 'goblin'
        SOUND_DEATH = 'monster'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_heaven_goblin_poet'], RangedAI, 12800)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 80
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 60
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 70
            self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 50
            self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 45
            self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 40
            self.obj.SPEED *= 4
            self.obj.MASS *= 3
            self.obj.TOUCHING_DAMAGE = 125
            self.obj.SIGHT_DISTANCE *= 320
            self.tick = 0

        def on_update(self):
            super().on_update()
            self.set_rotation((self.rot * 2 - self.obj.velocity.get_net_rotation()) // 3)
            if self.tick % 8 == 1:
                game.get_game().entities.append(Entities.GoblinOctave(self.obj.pos,
                                                                      vector.coordinate_rotation(game.get_game().player.obj.pos[0] - self.obj.pos[0],
                                                                                                 game.get_game().player.obj.pos[1] - self.obj.pos[1])))
            self.tick += 1

    class HeavenGoblinPriest(Entity):
        NAME = 'Heaven Goblin Priest'
        DISPLAY_MODE = 2
        LOOT_TABLE = LootTable([
            ])

        SOUND_HURT = 'goblin'
        SOUND_DEATH = 'monster'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_heaven_goblin_priest'], RangedAI, 12800)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 80
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 60
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 70
            self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 50
            self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 45
            self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 40
            self.obj.SPEED *= 4
            self.obj.MASS *= 3
            self.obj.TOUCHING_DAMAGE = 125
            self.obj.SIGHT_DISTANCE *= 360
            self.tick = 0

        def on_update(self):
            super().on_update()
            self.set_rotation((self.rot * 2 - self.obj.velocity.get_net_rotation()) // 3)
            if self.tick % 54 == 1:
                game.get_game().displayer.effect(fc.p_fade_circle(*position.displayed_position(self.obj.pos),
                                                                  col=(255, 255, 0), sp=20,
                                                                  t=10))
                if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                                   self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 200:
                    game.get_game().player.hp_sys.damage(215, damages.DamageTypes.MAGICAL)
                    game.get_game().player.hp_sys.enable_immume()
            self.tick += 1

    class Orge(Entity):
        NAME = 'Orge'
        DISPLAY_MODE = 2
        LOOT_TABLE = LootTable([
            IndividualLoot('starlight_shard', 0.8, 0, 2),
            ])

        SOUND_SPAWN = 'boss'
        SOUND_HURT = 'goblin'
        SOUND_DEATH = 'huge_monster'
        IS_MENACE = True

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_orge'], OrgeAI, 44000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 40
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 45
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 50
            self.tick = 0

        def on_update(self):
            super().on_update()
            self.set_rotation((self.rot * 2 - self.obj.velocity.get_net_rotation()) // 3)
            px, py = (game.get_game().player.obj.pos[0] - self.obj.pos[0],
                      game.get_game().player.obj.pos[1] - self.obj.pos[1])
            self.tick += 1
            if 200 < vector.distance(px, py) < 1000 and self.tick % 16 == 1:
                game.get_game().entities.append(Entities.PoisonSaliva(self.obj.pos,
                                                                      vector.coordinate_rotation(px, py) + random.randint(-2, 2)))


    class GoblinWave(Entity):
        NAME = 'The Heaven Goblins'
        DISPLAY_MODE = 2
        LOOT_TABLE = LootTable([
            ])
        IS_MENACE = True
        BOSS_NAME = 'The Heaven Intruder'

        NUMBERS = [20, 30, 30, 40, 60]

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_goblin_wave'], BuildingAI, 120)
            self.obj.IS_OBJECT = False
            self.goblins = []
            self.tick = 0
            self.this_no = []
            self.wave = 0
            self.hp_sys(op='config', immune=True)

        def on_update(self):
            self.NAME = 'The Heaven Goblins(Wave %d)' % (self.wave + 1)
            self.obj.pos << (game.get_game().player.obj.pos[0],
                            game.get_game().player.obj.pos[1] - 1000)
            self.tick += 1
            if self.tick % 10 == 1 and len(self.goblins) < self.NUMBERS[self.wave] * 2:
                px, py = game.get_game().player.obj.pos
                ax, ay = vector.rotation_coordinate(random.randint(0, 360))
                dt = random.randint(800, 1200)
                ps = px + ax * dt, py + ay * dt
                if (not random.randint(0, 10) or not len(self.goblins)) and self.wave == 4:
                    self.goblins.append(Entities.Orge(ps))
                elif not random.randint(0, 3) and self.wave > 1:
                    self.goblins.append(Entities.HeavenGoblinRanger(ps))
                elif not random.randint(0, 1) and self.wave not in [0, 2]:
                    self.goblins.append(Entities.HeavenGoblinThief(ps))
                else:
                    self.goblins.append(Entities.HeavenGoblinFighter(ps))
                game.get_game().entities.append(self.goblins[-1])
            self.hp_sys.max_hp = self.NUMBERS[self.wave]
            self.hp_sys.hp = self.NUMBERS[self.wave] - sum([e.hp_sys.hp <= 0 for e in self.goblins])
            if self.hp_sys.hp <= 0:
                if self.wave < 4:
                    self.wave += 1
                    self.goblins.clear()
                    self.hp_sys.hp = self.NUMBERS[self.wave]
            self.goblins = [g for g in self.goblins if vector.distance(g.obj.pos[0] - self.obj.pos[0],
                                                                        g.obj.pos[1] - self.obj.pos[1]) < (1300 + g.IS_MENACE * 2700) ** 2]

    class GoblinWaveEP2(Entity):
        NAME = 'The Heaven Goblins(EP2)'
        DISPLAY_MODE = 2
        LOOT_TABLE = LootTable([
            ])
        IS_MENACE = True
        BOSS_NAME = 'The Heaven Intruder'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_goblin_wave'], BuildingAI, 120)
            self.obj.IS_OBJECT = False
            self.goblins = []
            self.tick = 0
            self.hp_sys.max_hp = 140
            self.hp_sys.hp = 140

        def update(self):
            self.obj.pos << game.get_game().player.obj.pos
            self.tick += 1
            if self.tick % 10 == 1 and len(self.goblins) < 320:
                px, py = self.obj.pos
                ax, ay = vector.rotation_coordinate(random.randint(0, 360))
                dt = random.randint(800, 1000)
                ps = px + ax * dt, py + ay * dt
                if not random.randint(0, 4):
                    self.goblins.append(Entities.HeavenGoblinPoet(ps))
                elif not random.randint(0, 3):
                    self.goblins.append(Entities.HeavenGoblinPriest(ps))
                elif not random.randint(0, 3):
                    self.goblins.append(Entities.HeavenGoblinFighter(ps))
                elif random.randint(0, 1):
                    self.goblins.append(Entities.HeavenGoblinThief(ps))
                else:
                    self.goblins.append(Entities.HeavenGoblinRanger(ps))
                game.get_game().entities.append(self.goblins[-1])
            self.hp_sys.hp = 140 - sum([e.hp_sys.hp <= 0 for e in self.goblins])
            self.goblins = [g for g in self.goblins if vector.distance(g.obj.pos[0] - self.obj.pos[0],
                                                                        g.obj.pos[1] - self.obj.pos[1]) < 1100 ** 2]

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

        def on_update(self):
            super().on_update()
            self.set_rotation((self.rot * 4 - self.obj.velocity.get_net_rotation()) // 5)

    class FaithlessEye(Entity):
        NAME = 'Faithless Eye'
        DISPLAY_MODE = 1
        IS_MENACE = True
        BOSS_NAME = 'The Non-Believer'
        LOOT_TABLE = LootTable([
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 1, 3),
            IndividualLoot('soul_of_integrity', 1, 10, 22),
            IndividualLoot('double_watcher_wand', 0.5, 1, 1),
            IndividualLoot('tip71', 1, 1, 1),
        ])

        SOUND_SPAWN = 'boss'
        SOUND_HURT = 'metal'
        SOUND_DEATH = 'explosive'
        PHASE_SEGMENTS = [0.65]


        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_faithless_eye'], FaithlessEyeAI, 48000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 85
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 87
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 88
            self.phase = 1

        def on_update(self):
            super().on_update()
            if self.phase == 1 and (self.hp_sys.hp < self.hp_sys.max_hp * 0.65 or not
                    bool(len([1 for e in game.get_game().entities if type(e) is Entities.TruthlessEye]))):
                self.phase = 2
                self.obj.phase = 2
                self.img = game.get_game().graphics['entity_faithless_eye_phase2']
                if self.hp_sys.hp > self.hp_sys.max_hp * 0.65:
                    self.PHASE_SEGMENTS = []
            if self.phase == 2 and self.hp_sys.hp < self.hp_sys.max_hp * 0.3:
                self.phase = 3
            if self.obj.state == 0:
                self.set_rotation((self.rot * 2 - self.obj.velocity.get_net_rotation()) // 3)
            else:
                self.set_rotation((self.rot - self.obj.rot) // 2)
                if self.obj.tick % 50 == 1:
                    px, py = game.get_game().player.obj.pos
                    k = 1
                    if self.obj.phase == 2:
                        k = 3
                    if self.obj.phase == 3:
                        k = 5
                    for r in range(-k * 15, k * 15 + 1, 15 - (self.obj.phase == 3) * 5):
                        game.get_game().entities.append(Entities.FaithlessCurse(self.obj.pos,
                                                                                vector.coordinate_rotation(
                                                                                    px - self.obj.pos[0],
                                                                                    py - self.obj.pos[1]) + r))

    class TruthlessEye(Entity):
        NAME = 'Truthless Eye'
        DISPLAY_MODE = 1
        IS_MENACE = True
        BOSS_NAME = 'The Dishonester'
        LOOT_TABLE = LootTable([
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 1, 3),
            IndividualLoot('soul_of_integrity', 1, 10, 22),
            IndividualLoot('double_watcher_wand', 0.5, 1, 1),
            IndividualLoot('tip71', 1, 1, 1),
        ])

        SOUND_SPAWN = 'boss'
        SOUND_HURT = 'metal'
        SOUND_DEATH = 'explosive'
        PHASE_SEGMENTS = [0.6]

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_truthless_eye'], FaithlessEyeAI, 56000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 85
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 87
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 88
            self.obj.ax = 900
            self.obj.ay = -400
            self.obj.state = 1
            self.phase = 1

        def on_update(self):
            super().on_update()
            if self.phase == 1 and (self.hp_sys.hp < self.hp_sys.max_hp * 0.6 or not
                    bool(len([1 for e in game.get_game().entities if type(e) is Entities.FaithlessEye]))):
                self.phase = 2
                self.obj.phase = 2
                self.img = game.get_game().graphics['entity_faithless_eye_phase2']
                if self.hp_sys.hp > self.hp_sys.max_hp * 0.6:
                    self.PHASE_SEGMENTS = []
            if self.phase == 2 and self.hp_sys.hp < self.hp_sys.max_hp * 0.25:
                self.phase = 3
            if self.obj.state == 0:
                self.set_rotation((self.rot * 2 - self.obj.velocity.get_net_rotation()) // 3)
            else:
                self.set_rotation((self.rot - self.obj.rot) // 2)
                if self.obj.tick % 60 == 0:
                    px, py = game.get_game().player.obj.pos
                    k = 0
                    if self.obj.phase == 2:
                        k = 5
                    if self.obj.phase == 3:
                        k = 7
                    for r in range(-k * 20, k * 20 + 1, 20 - (self.obj.phase == 3) * 10):
                        game.get_game().entities.append(Entities.TruthlessCurse(self.obj.pos,
                                                                                vector.coordinate_rotation(
                                                                                    px - self.obj.pos[0],
                                                                                    py - self.obj.pos[1]) + r))

    class SkyCubeFighter(Entity):
        NAME = 'Sky Cube Fighter'
        DISPLAY_MODE = 1
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            IndividualLoot('rune_blade', 0.5, 1, 1),
            IndividualLoot('starlight_shard', 0.8, 1, 2),
        ])

        SOUND_SPAWN = 'boss'
        SOUND_HURT = 'metal'
        SOUND_DEATH = 'explosive'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_sky_cube_fighter'], SkyCubeFighterAI, 36000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 40
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 48
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 36

        def on_update(self):
            super().on_update()
            self.set_rotation(self.rot + 15)

    class SkyCubeRanger(Entity):
        NAME = 'Sky Cube Ranger'
        DISPLAY_MODE = 1
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            IndividualLoot('dark_exploder', 0.5, 1, 1),
            IndividualLoot('starlight_shard', 0.8, 1, 2),
        ])

        SOUND_SPAWN = 'boss'
        SOUND_HURT = 'metal'
        SOUND_DEATH = 'explosive'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_sky_cube_ranger'], SkyCubeRangerAI, 28000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 12
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 18
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 12
            self.tick = 0

        def on_update(self):
            super().on_update()
            self.set_rotation(self.rot - 22)
            if self.tick % 80 < 20:
                if self.tick % 5 == 0:
                    game.get_game().entities.append(Entities.Lazer(self.obj.pos,
                                                                   vector.coordinate_rotation(
                                                                       game.get_game().player.obj.pos[0] - self.obj.pos[0],
                                                                       game.get_game().player.obj.pos[1] - self.obj.pos[1])
                                                                   ))
            elif self.tick % 12 == 0:
                for ar in range(-30, 31, 10):
                    game.get_game().entities.append(Entities.Lazer(self.obj.pos,
                                                                   vector.coordinate_rotation(
                                                                       game.get_game().player.obj.pos[0] - self.obj.pos[0],
                                                                       game.get_game().player.obj.pos[1] - self.obj.pos[1])
                                                                   + ar))
            self.tick += 1

    class SkyCubeBlocker(Entity):
        NAME = 'Sky Cube Blocker'
        DISPLAY_MODE = 1
        IS_MENACE = True
        LOOT_TABLE = LootTable([
            IndividualLoot('water_of_disability', 0.5, 1, 1),
            IndividualLoot('starlight_shard', 0.8, 1, 2),
        ])

        SOUND_SPAWN = 'boss'
        SOUND_HURT = 'metal'
        SOUND_DEATH = 'explosive'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_sky_cube_blocker'], SkyCubeBlockerAI, 42000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 66
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 72
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 70

        def on_update(self):
            super().on_update()
            self.set_rotation(self.rot + 5)

    class Destroyer(WormEntity):
        NAME = 'Destroyer'
        DISPLAY_MODE = 1
        IS_MENACE = True
        BOSS_NAME = 'The Metal Worm of Strength'
        LOOT_TABLE = LootTable([
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 1, 3),
            IndividualLoot('soul_of_bravery', 1, 10, 22),
            IndividualLoot('tip73', 1, 1, 1),
        ])

        SOUND_SPAWN = 'boss'
        SOUND_HURT = 'metal'
        SOUND_DEATH = 'explosive'
        VITAL = True

        def __init__(self, pos):
            super().__init__(pos, 64, game.get_game().graphics['entity_destroyer_head'],
                             game.get_game().graphics['entity_destroyer_body'], DestroyerAI, 550000, body_length=120,
                             body_touching_damage=280)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 90
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 80
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 110
            self.obj.SPEED *= 2

        def on_update(self):
            super().on_update()
            for b in self.body:
                if random.randint(0, 1000) == 0:
                    rot = vector.coordinate_rotation(game.get_game().player.obj.pos[0] - b.obj.pos[0],
                                                     game.get_game().player.obj.pos[1] - b.obj.pos[1])
                    l = Entities.Lazer(b.obj.pos, rot)
                    l.obj.apply_force(vector.Vector(rot, 5000))
                    game.get_game().entities.append(l)

    class TheCPU(Entity):
        NAME = 'The CPU'
        DISPLAY_MODE = 1
        IS_MENACE = True
        BOSS_NAME = 'The Electric Lier'
        LOOT_TABLE = LootTable([
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 1, 3),
            IndividualLoot('soul_of_kindness', 1, 10, 22),
            IndividualLoot('remote_sword', 0.8, 1, 1),
            IndividualLoot('tip72', 1, 1, 1),
        ])

        SOUND_SPAWN = 'boss'
        SOUND_HURT = 'metal'
        SOUND_DEATH = 'explosive'
        PHASE_SEGMENTS = [0.5]

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_the_cpu'], TheCPUAI, 48000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 30
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 25
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 45
            self.show_bar = False

        def on_update(self):
            super().on_update()
            if self.hp_sys.hp < self.hp_sys.max_hp * 0.5 and self.obj.phase == 1:
                self.obj.phase = 2
                self.img = game.get_game().graphics['entity_the_cpu_phase2']
                self.set_rotation(self.rot)
                self.obj.tick = -200

        def t_draw(self):
            super().t_draw()
            px, py = game.get_game().player.obj.pos
            aax, aay = self.obj.pos[0] - game.get_game().player.obj.pos[0], self.obj.pos[1] - \
                       game.get_game().player.obj.pos[1]
            displayer = game.get_game().displayer
            r = self.d_img.get_rect()
            if constants.USE_ALPHA:
                self.d_img.set_alpha(255 - int(240 * self.hp_sys.hp // self.hp_sys.max_hp))
            else:
                self.d_img.set_alpha(0)
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

    class MechanicalMedusa(WormEntity):
        NAME = 'Mechanical Medusa'
        DISPLAY_MODE = 1
        IS_MENACE = True
        BOSS_NAME = 'The Final Mechanic'
        LOOT_TABLE = LootTable([
            SelectionLoot([('strength_ingot', 20, 30),
                           ('sight_ingot', 20, 30),
                           ('phantom_ingot', 20, 30)], 1, 2),
        ])

        SOUND_SPAWN = 'boss'
        SOUND_HURT = 'metal'
        SOUND_DEATH = 'explosive'
        VITAL = True
        PHASE_SEGMENTS = [0.3, 0.8]

        def __init__(self, pos):
            super().__init__(pos, 54, game.get_game().graphics['entity_the_cpu'],
                             game.get_game().graphics['entity_destroyer_body'], MechanicMedusaAI,
                             440000, body_length=90)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 60
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 80
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 60
            self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 44
            self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 64
            self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 24
            self.phase = 1
            self.eyes = [Entities.FaithlessEye((pos[0] - 1000, pos[1])),
                         Entities.TruthlessEye((pos[0] + 1000, pos[1]))]
            for e in self.eyes:
                e.hp_sys = hp_system.SubHPSystem(self.hp_sys)
                e.obj.state = 1
                e.phase = 2
                e.obj.phase = 1
                e.show_bar = False
                e.PHASE_SEGMENTS = []
                e.IS_MENACE = False
                e.VITAL = True
                e.LOOT_TABLE = LootTable([])
            self.tick = 0

        def on_update(self):
            super().on_update()
            self.tick += 1
            if self.phase == 1 and self.hp_sys.hp < self.hp_sys.max_hp * 0.8:
                self.phase = 2
                self.body[0].img = game.get_game().graphics['entity_the_cpu_phase2']
                self.body[0].obj.state = 2
                self.body[0].obj.tick = -200
                for e in self.eyes:
                    game.get_game().entities.append(e)
            if self.phase == 2 and self.hp_sys.hp < self.hp_sys.max_hp * 0.3:
                self.phase = 3
            for b in self.body:
                if random.randint(0, 1100 - self.phase * 220) == 0:
                    rot = vector.coordinate_rotation(game.get_game().player.obj.pos[0] - b.obj.pos[0],
                                                     game.get_game().player.obj.pos[1] - b.obj.pos[1])
                    l = Entities.Lazer(b.obj.pos, rot)
                    l.obj.apply_force(vector.Vector(rot, 8000))
                    game.get_game().entities.append(l)
            if self.obj.state == 2 and self.tick % 10 == 0:
                px, py = game.get_game().player.obj.pos
                px -= self.obj.pos[0]
                py -= self.obj.pos[1]
                rot = vector.coordinate_rotation(px, py)
                for ar in range(-30, 31, 10):
                    game.get_game().entities.append(Entities.Lazer(self.obj.pos, rot + ar))

        def t_draw(self):
            super().t_draw()

            if self.phase == 3:
                px, py = game.get_game().player.obj.pos
                for b in self.body:
                    aax, aay = (b.obj.pos[0] - game.get_game().player.obj.pos[0],
                                b.obj.pos[1] - game.get_game().player.obj.pos[1])
                    displayer = game.get_game().displayer
                    r = b.d_img.get_rect()
                    if constants.USE_ALPHA:
                        b.d_img.set_alpha(255 - int(720 * b.hp_sys.hp // b.hp_sys.max_hp))
                    else:
                        b.d_img.set_alpha(0)
                    r.center = position.displayed_position((px - aax, py + aay))
                    displayer.canvas.blit(b.d_img, r)
                    r.center = position.displayed_position((px + aax, py - aay))
                    displayer.canvas.blit(b.d_img, r)
                    r.center = position.displayed_position((px - aax, py - aay))
                    displayer.canvas.blit(b.d_img, r)
                    r.center = position.displayed_position((px + aay, py + aax))
                    displayer.canvas.blit(b.d_img, r)
                    r.center = position.displayed_position((px - aay, py - aax))
                    displayer.canvas.blit(b.d_img, r)
                    r.center = position.displayed_position((px + aay, py - aax))
                    displayer.canvas.blit(b.d_img, r)
                    r.center = position.displayed_position((px - aay, py + aax))
                    displayer.canvas.blit(b.d_img, r)

    class Greed(Entity):
        NAME = 'Greed'
        DISPLAY_MODE = 1
        IS_MENACE = True
        BOSS_NAME = 'The Greedy Biter'
        LOOT_TABLE = LootTable([
            SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 1, 3),
            IndividualLoot('saint_steel_ingot', 1, 5, 8),
            IndividualLoot('soul_of_perseverance', 1, 10, 22),
            SelectionLoot([('tip8', 1, 1), ('tip9', 1, 1)], 0, 2),
        ])

        SOUND_HURT = 'corrupt'
        SOUND_DEATH = 'explosive'
        PHASE_SEGMENTS = [0.2, 0.4, 0.6, 0.8]

        def __init__(self, pos, d=False):
            super().__init__(pos, game.get_game().graphics['entity_greed'], GreedAI, 128000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 110
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 110
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 110
            self.d = d
            self.phase = 1
            if self.d:
                self.LOOT_TABLE = LootTable([])

        def on_update(self):
            super().on_update()
            if self.hp_sys.hp <= self.hp_sys.max_hp * (1 - self.phase * 0.2) and not self.d:
                self.phase += 1
                for i in range(4 * self.phase - 1):
                    d = Entities.Greed(self.obj.pos, True)
                    d.IS_MENACE = False
                    d.hp_sys.hp = 8000 + 4000 * self.phase
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
        VITAL = True
        BOSS_NAME = 'Follower of the Truth'
        LOOT_TABLE = LootTable([
            SelectionLoot([('palladium', 2, 3), ('mithrill', 2, 3), ('titanium', 2, 3)], 1, 3),
            IndividualLoot('dark_ingot', 1, 5, 8),
            IndividualLoot('soul_of_patience', 1, 1, 2),
            IndividualLoot('tip8', 0.1, 1, 1),
            IndividualLoot('tip9', 0.1, 1, 1),
        ])

        SOUND_DEATH = 'huge_monster'
        PHASE_SEGMENTS = [0.5]

        def __init__(self, pos, d: int = False, _hp_sys=None, idx: float = 0):
            _p = pos
            _p = (game.get_game().player.obj.pos[0] + random.randint(-5000, 5000),
                  game.get_game().player.obj.pos[1] + random.randint(-5000, 5000))
            if not d:
                hp_sys = hp_system.HPSystem(750000)
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
            self.obj.TOUCHING_DAMAGE = 420
            self.me = 1
            self.phase = 1
            self.d = d
            self.show_bar = True

        def on_update(self):
            super().on_update()
            self.tick += 1
            if self.phase == 1 and self.hp_sys.hp < self.hp_sys.max_hp * 0.5:
                self.phase = 2
                self.me = 2
                if not self.d:
                    for f in range(20):
                        et = Entities.EyeOfTime(self.obj.pos, 114, self.hp_sys, 1)
                        et.tick = (self.tick + 20 * f + 10) % 100
                        game.get_game().entities.append(et)
            self.obj.IS_OBJECT = False
            if self.tick > 200 // self.me:
                self.state = (self.state + 1) % 1
                self.tick = 0
                self.obj.pos << (game.get_game().player.obj.pos[0] + random.randint(-500, 500),
                                game.get_game().player.obj.pos[1] + random.randint(-500, 500))
                self.obj.velocity.clear()
                self.obj.velocity.add(vector.Vector(random.randint(0, 360), 5))
                self.set_rotation(random.randint(-50, 50))
            if self.tick < 20 and constants.USE_ALPHA:
                self.img.set_alpha(self.tick * 12 + 15)
            elif self.tick > 200 // self.me - 20 and constants.USE_ALPHA:
                self.img.set_alpha(255 - (self.tick - 200 // self.me + 20) * 12)
            else:
                self.img.set_alpha(255)
                self.obj.IS_OBJECT = True
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

    class DevilPython(WormEntity):
        NAME = 'Devil Python'
        DISPLAY_MODE = 1
        IS_MENACE = True
        BOSS_NAME = 'The World\'s Devourer'
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
                             game.get_game().graphics['entity_devil_python_body'], DevilPythonAI, 800000,
                             body_length=90, body_touching_damage=320)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 25
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 30
            self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 15
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 60

        def on_update(self):
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

    class LifeTree(Entity):
        NAME = 'Life Tree'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('soul_of_growth', 1, 5, 10),
            IndividualLoot('leaf', 1, 5, 10),
            IndividualLoot('wood', 1, 25, 30),
            IndividualLoot('chlorophyll', 0.03, 1, 1),
            IndividualLoot('chlorophyte_ingot', 0.3, 1, 5),
            ])

        SOUND_HURT = 'corrupt'
        SOUND_DEATH = 'sticky'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_life_tree'], LeafAI, 8800)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 95
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 114
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 128
            self.obj.SPEED *= 2
            self.obj.MASS *= 4
            self.obj.TOUCHING_DAMAGE *= 2

    class IceThorn(Entity):
        NAME = 'Ice Thorn'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('soul_of_coldness', 1, 5, 10),
            IndividualLoot('leaf', 1, 5, 10),
            IndividualLoot('chlorophyll', 0.03, 1, 1),
            IndividualLoot('dchlorophyte_ingot', 0.5, 1, 5),
            ])

        SOUND_HURT = 'corrupt'
        SOUND_DEATH = 'sticky'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_life_tree'], LeafAI, 4800)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 195
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 188
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 188
            self.obj.SPEED *= 3
            self.obj.MASS *= 2
            self.obj.TOUCHING_DAMAGE *= 2.5

    class JevilKnife(Entity):
        NAME = 'Joker Evil Knife'
        DISPLAY_MODE = 1
        VITAL = True
        LOOT_TABLE = LootTable([
            ])

        def __init__(self, pos, hp_sys):
            super().__init__(pos, game.get_game().graphics['entity_jevil_knife'], JevilKnifeAI, hp_sys=hp_sys)
            self.tick = 0

        def on_update(self):
            super().on_update()
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
        BOSS_NAME = 'The Chaos Laughter'
        PHASE_SEGMENTS = [0.5, 0.7, 0.9]

        SOUND_HURT = 'haha'
        SOUND_DEATH = 'haha'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_jevil'], JevilAI, 456000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 100
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 400
            self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 300
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 300
            self.phase = 0
            game.get_game().dialog.dialog('CHAOS, CHAOS, \nCATCH ME IF YOU CAN!')

        def on_update(self):
            super().on_update()
            self.hp_sys.SOUND_HURT = self.SOUND_HURT if not random.randint(0, 10) else None
            if self.hp_sys.hp < self.hp_sys.max_hp * 0.9 and self.phase == 0:
                self.phase = 1
                self.play_sound('i_can_do_anything')
                game.get_game().dialog.dialog('HEARTS, DIAMONDS, \nI CAN DO ANYTHING!')
            if self.hp_sys.hp < self.hp_sys.max_hp * 0.7 and self.phase == 1:
                self.phase = 2
                self.play_sound('devil_knife')
                game.get_game().dialog.dialog('UEUEUE! LET\'S TRY THE DEVILS KNIFE!')
                for i in range(0, 360, 90):
                    kf = Entities.JevilKnife(self.obj.pos, self.hp_sys)
                    kf.obj.upper = self.obj
                    kf.obj.r = i
                    game.get_game().entities.append(kf)
            if self.hp_sys.hp < self.hp_sys.max_hp * 0.5 and self.phase == 2:
                self.phase = 3
                self.img = game.get_game().graphics['entity_null']
                self.play_sound('neo_chaos')
                game.get_game().dialog.dialog('JUST KIDDING!\nHERE\'S THE FINAL CHAOS!')
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

    class Jevil2(Entity):
        NAME = 'Jevil'
        DISPLAY_MODE = 2
        LOOT_TABLE = LootTable([
            IndividualLoot('chaos_ingot', 1, 50, 60),
            SelectionLoot([('jevil_knife', 1, 1), ('jevils_tail', 1, 1)], 1, 1),
            ])
        IS_MENACE = True
        BOSS_NAME = 'The Chaos Laughter'
        PHASE_SEGMENTS = [0.5, 0.7, 0.9]

        SOUND_HURT = 'haha'
        SOUND_DEATH = 'haha'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_jevil'], JevilAI, 128000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 100
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 100
            self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 100
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 100
            self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 120
            self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 60
            self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 80
            self.phase = 0
            game.get_game().dialog.dialog('CHAOS, CHAOS, \nCATCH ME IF YOU CAN!')

        def on_update(self):
            super().on_update()
            self.hp_sys.SOUND_HURT = self.SOUND_HURT if not random.randint(0, 10) else None
            if self.hp_sys.hp < self.hp_sys.max_hp * 0.9 and self.phase == 0:
                self.phase = 1
                self.play_sound('i_can_do_anything')
                game.get_game().dialog.dialog('HEARTS, DIAMONDS, \nI CAN DO ANYTHING!')
            if self.hp_sys.hp < self.hp_sys.max_hp * 0.7 and self.phase == 1:
                self.phase = 2
                self.play_sound('devil_knife')
                game.get_game().dialog.dialog('UEUEUE! LET\'S TRY THE DEVILS KNIFE!')
                for i in range(0, 360, 60):
                    kf = Entities.JevilKnife(self.obj.pos, self.hp_sys)
                    kf.obj.upper = self.obj
                    kf.obj.r = i
                    game.get_game().entities.append(kf)
            if self.hp_sys.hp < self.hp_sys.max_hp * 0.5 and self.phase == 2:
                self.phase = 3
                self.img = game.get_game().graphics['entity_null']
                self.play_sound('neo_chaos')
                game.get_game().dialog.dialog('JUST KIDDING!\nHERE\'S THE FINAL CHAOS!')
            r = -vector.coordinate_rotation(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                                                          self.obj.pos[1] - game.get_game().player.obj.pos[1])
            self.set_rotation(r)
            if self.phase <= 1:
                if self.obj.state in [0, 4] and self.obj.tick % 75 <= 1:
                    for r in range(-30, 31, 15 - 5 * self.phase):
                        bul = Entities.SpadeBullet(self.obj.pos, r - self.rot + 180)
                        game.get_game().entities.append(bul)
                elif self.obj.state in [2, 6] and self.obj.tick % 25 <= 1:
                    for r in range(-20 + 20 * (self.obj.tick % 40 < 20), 21, 40):
                        bul = Entities.AlmondBullet(self.obj.pos, r - self.rot + 180)
                        if self.phase:
                            bul.obj.speed = 800
                        game.get_game().entities.append(bul)
            elif self.phase == 2:
                if self.obj.state % 2 == 0 and self.obj.tick % 25 <= 1:
                    md = ['heart', 'club', 'spade', 'diamond'][self.obj.state // 2]
                    px, py = game.get_game().player.obj.pos
                    bul = Entities.CardBomb((px + random.randint(-1500, 1500), py + random.randint(-2500, -1000)), md)
                    game.get_game().entities.append(bul)
            else:
                if self.obj.tick % 18 <= 1:
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

        @staticmethod
        def is_suitable(biome: str):
            return biome in ['inner']

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_plantera_bulb'], BuildingAI, 10 ** 5 // 4)

    class Plantera(Entity):
        NAME = 'Plantera'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('origin', 1, 1, 1),
            IndividualLoot('willpower_shard', 1, 10, 30)
        ])
        IS_MENACE = True
        BOSS_NAME = 'The Semi-god'
        PHASE_SEGMENTS = [0.6]

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_plantera'], PlanteraAI, 320000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 50
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 50
            self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 50
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 25
            self.sps = pos
            self.phase = 1
            self.cur_fs = 3200
            self.ctfs = 3200
            self.t = 0

        def on_update(self):
            super().on_update()
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
                game.get_game().player.obj.pos << (self.sps[0] + apx, self.sps[1] + apy)

    class GhostFace(Entity):
        NAME = 'Ghost Face'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('chaos_ingot', 1, 50, 120),
            IndividualLoot('wierd_essence', 0.5, 10, 22),
            ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_ghost_face'], GhostFaceAI, 22000)

    class SadFace(Entity):
        NAME = 'Sad Face'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('chaos_ingot', 1, 15, 50),
            IndividualLoot('wierd_essence', 0.5, 10, 22),
            ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_sad_face'], GhostFaceAI, 22000)
            self.obj.appear_time = 80
            self.obj.appear_rate = 7
            self.obj.TOUCHING_DAMAGE = 560

    class AngryFace(Entity):
        NAME = 'Angry Face'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('chaos_ingot', 1, 15, 50),
            IndividualLoot('wierd_essence', 0.5, 10, 22),
            ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_angry_face'], GhostFaceAI, 12000)
            self.obj.appear_time = 30
            self.obj.appear_rate = 2
            self.obj.TOUCHING_DAMAGE = 450

    class CurseGhost(Entity):
        NAME = 'Curse Ghost'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('soul', 1, 12, 18),
            IndividualLoot('wierd_essence', 0.3, 8, 15),
        ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_curse_ghost'], SoulFlowerAI, 88000)
            self.obj.TOUCHING_DAMAGE = 660
            self.obj.SPEED *= 2
            self.obj.FRICTION = 0.8

        def on_update(self):
            super().on_update()
            px, py = game.get_game().player.obj.pos
            px -= self.obj.pos[0]
            py -= self.obj.pos[1]
            pg.draw.circle(game.get_game().displayer.canvas, (127, 255, 0), position.displayed_position(self.obj.pos),
                           radius=800 / game.get_game().player.get_screen_scale(), width=5)
            if vector.distance(px, py) < 800:
                entity_spawn(Entities.GhostFace, target_number=1, to_player_max=2500, to_player_min=2000, rate=0.2)
                entity_spawn(Entities.AngryFace, target_number=1, to_player_max=2500, to_player_min=2000, rate=0.2)
                entity_spawn(Entities.SadFace, target_number=1, to_player_max=2500, to_player_min=2000, rate=0.2)

    class TimeTrap(Entity):
        NAME = 'Timetrap'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('chaos_ingot', 1, 15, 50),
            IndividualLoot('time_essence', 0.5, 10, 22),
            ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_timetrap'], BuildingAI, 25000)
            self.obj.TOUCHING_DAMAGE = 420

        def on_update(self):
            super().on_update()
            px, py = game.get_game().player.obj.pos
            px -= self.obj.pos[0]
            py -= self.obj.pos[1]
            if vector.distance(px, py) < 200:
                game.get_game().player.obj.pos << self.obj.pos
            elif vector.distance(px, py) < 2000:
                draw.line(game.get_game().displayer.canvas, (0, 255, 0),
                             position.displayed_position(self.obj.pos),
                             position.displayed_position(game.get_game().player.obj.pos), 10)
                game.get_game().player.obj.pos << (game.get_game().player.obj.pos[0] - px // 20, game.get_game().player.obj.pos[1] - py // 20)
            pg.draw.circle(game.get_game().displayer.canvas, (255, 0, 0),
                           position.displayed_position(self.obj.pos), 200 / game.get_game().player.get_screen_scale(), 5)
            pg.draw.circle(game.get_game().displayer.canvas, (100, 100, 255),
                           position.displayed_position(self.obj.pos), 2000 / game.get_game().player.get_screen_scale(), 5)

    class TimeFlower(Entity):
        NAME = 'Timeflower'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('chaos_ingot', 1, 15, 50),
            IndividualLoot('time_essence', 0.5, 10, 22),
            ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_timeflower'], SoulFlowerAI, 25000)
            self.obj.TOUCHING_DAMAGE = 560

        def on_update(self):
            super().on_update()
            px, py = game.get_game().player.obj.pos
            px -= self.obj.pos[0]
            py -= self.obj.pos[1]
            if vector.distance(px, py) < 100:
                game.get_game().player.obj.pos << self.obj.pos
            elif vector.distance(px, py) < 1000:
                draw.line(game.get_game().displayer.canvas, (0, 255, 0),
                             position.displayed_position(self.obj.pos),
                             position.displayed_position(game.get_game().player.obj.pos), 10)
                game.get_game().player.obj.pos << (game.get_game().player.obj.pos[0] - px // 40, game.get_game().player.obj.pos[1] - py // 40)
            pg.draw.circle(game.get_game().displayer.canvas, (255, 0, 0),
                           position.displayed_position(self.obj.pos), 100 / game.get_game().player.get_screen_scale(), 5)
            pg.draw.circle(game.get_game().displayer.canvas, (100, 100, 255),
                           position.displayed_position(self.obj.pos), 1000 / game.get_game().player.get_screen_scale(), 5)

    class TimeTrapGuard(TimeTrap):
        LOOT_TABLE = LootTable([])

    class AncientDebris(Entity):
        NAME = 'Ancient Debris'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('mysterious_ingot', 1, 12, 18),
            IndividualLoot('time_essence', 0.3, 8, 15),
        ])


        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_ancient_debris'], BuildingAI, 32000)
            self.obj.TOUCHING_DAMAGE = 540
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 440
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 480
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 400

        def on_update(self):
            super().on_update()
            px, py = game.get_game().player.obj.pos
            px -= self.obj.pos[0]
            py -= self.obj.pos[1]
            pg.draw.circle(game.get_game().displayer.canvas,(0, 255, 255), position.displayed_position(self.obj.pos),
                           radius=800 / game.get_game().player.get_screen_scale(), width=5)
            if vector.distance(px, py) < 800:
                entity_spawn(Entities.TimeTrapGuard, target_number=3, to_player_max=2500, to_player_min=2000, rate=0.2)

    class Molecules(Entity):
        NAME = 'Molecules'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('chaos_ingot', 1, 15, 50),
            IndividualLoot('substance_essence', 0.5, 10, 22),
            ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_molecules'], CellsAI, 55)
            self.obj.TOUCHING_DAMAGE = 640
            self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] /= 1000
            self.hp_sys.resistances[damages.DamageTypes.PIERCING] /= 1000
            self.hp_sys.resistances[damages.DamageTypes.MAGICAL] /= 1000
            self.hp_sys.resistances[damages.DamageTypes.ARCANE] /= 1000
            self.hp_sys(op='config', minimum_damage=0.01)

        def on_update(self):
            super().on_update()
            self.set_rotation(self.rot + 2)

    class TitaniumIngot(Entity):
        NAME = 'Titanium Ingot'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('chaos_ingot', 1, 15, 50),
            IndividualLoot('substance_essence', 0.5, 10, 22),
            ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_titanium_ingot'], BuildingAI, 24)
            self.obj.TOUCHING_DAMAGE = 720
            self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] /= 2500
            self.hp_sys.resistances[damages.DamageTypes.PIERCING] /= 2500
            self.hp_sys.resistances[damages.DamageTypes.MAGICAL] /= 2500
            self.hp_sys.resistances[damages.DamageTypes.ARCANE] /= 2500
            self.hp_sys(op='config', minimum_damage=0.004)

    class Spark(Entity):
        NAME = 'Spark'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('chaos_ingot', 1, 15, 50),
            IndividualLoot('light_essence', 0.5, 10, 22),
            ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_spark'], StarAI, 80000)
            self.obj.TOUCHING_DAMAGE = 640
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 600
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 720
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 700
            self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 1200

    class Holyfire(Entity):
        NAME = 'Holyfire'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([
            IndividualLoot('chaos_ingot', 1, 15, 50),
            IndividualLoot('light_essence', 0.5, 10, 22),
            ])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_holyfire'], StarAI, 20000)
            self.obj.TOUCHING_DAMAGE = 640
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 600
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 720
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 700
            self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 1200

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

        def t_draw(self):
            if self.tick >= 10:
                super().t_draw()

        def on_update(self):
            super().on_update()
            self.tick += 1
            if self.tick < 10:
                ax, ay = vector.rotation_coordinate(self.obj.rot)
                draw.line(game.get_game().displayer.canvas, (255, 0, 0),
                             position.displayed_position(self.obj.pos),
                             position.displayed_position((self.obj.pos[0] + ax * 3000, self.obj.pos[1] + ay * 3000)), 3)

            else:
                self.damage()
                self.hp_sys.hp -= 25 * 10 ** 6

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 80:
                game.get_game().player.hp_sys.damage(640, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class Thing(Entity):
        NAME = 'Thing'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['items_null'], BuildingAI, 10 ** 5)
            self.obj.MASS = 1000
            self.tick = 0
            self.obj.IS_OBJECT = False

        def t_draw(self):
            super().t_draw()
            self.tick += 1
            if self.tick < 10:
                pg.draw.circle(game.get_game().displayer.canvas, (255, 0, 0),
                               position.displayed_position(self.obj.pos), 50 / game.get_game().player.get_screen_scale(),
                               5)
                if self.tick % 3 == 1:
                    game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                             col=(0, 0, 255), t=5, sp=16, n=35))
            else:
                self.damage()
                self.hp_sys.hp -= 10 ** 4
                pg.draw.circle(game.get_game().displayer.canvas, (0, 0, 255),
                               position.displayed_position(self.obj.pos), 50 / game.get_game().player.get_screen_scale())

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 50:
                game.get_game().player.hp_sys.damage(700, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.enable_immume()
                self.hp_sys.hp = 0

    class SunFire(Entity):
        NAME = 'SunFire'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])

        def __init__(self, pos, rot, follow_entity=None):
            super().__init__(pos, game.get_game().graphics['items_null'], FastBulletAI, 10 ** 9)
            self.obj.MASS = 1000
            self.obj.rot = rot
            self.obj.speed = 8800
            self.tick = 0
            if follow_entity is not None:
                self.ax = self.obj.pos[0] - follow_entity.obj.pos[0]
                self.ay = self.obj.pos[1] - follow_entity.obj.pos[1]
                self.arot = rot + follow_entity.rot
                self.follow_entity = follow_entity
            else:
                self.ax, self.ay, self.arot = 0, 0, 0
                self.follow_entity = None

        def t_draw(self):
            if self.tick >= 10:
                self.obj.update()
                game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                         col=(255, 63, 0), t=3, sp=16, n=5))
            else:
                if self.follow_entity is not None:
                    self.obj.pos << (self.follow_entity.obj.pos[0] + self.ax, self.follow_entity.obj.pos[1] + self.ay)
                    self.obj.rot = -self.follow_entity.rot + self.arot
                ax, ay = vector.rotation_coordinate(self.obj.rot)
                draw.line(game.get_game().displayer.canvas, (255, 0, 0),
                             position.displayed_position(self.obj.pos),
                             position.displayed_position((self.obj.pos[0] + ax * 3000, self.obj.pos[1] + ay * 3000)), 3)

        def on_update(self):
            super().on_update()
            self.tick += 1
            if self.tick < 10:
                pass

            else:
                self.damage()
                self.hp_sys.hp -= 25 * 10 ** 6


        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 80:
                game.get_game().player.hp_sys.damage(880, damages.DamageTypes.MAGICAL)
                self.hp_sys.hp = 0

    class MoonFire(Entity):
        NAME = 'MoonFire'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])

        def __init__(self, pos, rot, follow_entity=None):
            super().__init__(pos, game.get_game().graphics['items_null'], FastBulletAI, 10 ** 9)
            self.obj.MASS = 1000
            self.obj.rot = rot
            self.obj.speed = 8800
            self.tick = 0
            if follow_entity is not None:
                self.ax = self.obj.pos[0] - follow_entity.obj.pos[0]
                self.ay = self.obj.pos[1] - follow_entity.obj.pos[1]
                self.arot = rot + follow_entity.rot
                self.follow_entity = follow_entity
            else:
                self.ax, self.ay, self.arot = 0, 0, 0
                self.follow_entity = None

        def t_draw(self):
            if self.tick >= 10:
                self.obj.update()
                game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                        col=(63, 255, 0), t=3, sp=16, n=5))
            else:
                if self.follow_entity is not None:
                    self.obj.pos << (self.follow_entity.obj.pos[0] + self.ax, self.follow_entity.obj.pos[1] + self.ay)
                    self.obj.rot = -self.follow_entity.rot + self.arot
                ax, ay = vector.rotation_coordinate(self.obj.rot)
                draw.line(game.get_game().displayer.canvas, (0, 255, 0),
                             position.displayed_position(self.obj.pos),
                             position.displayed_position((self.obj.pos[0] + ax * 3000, self.obj.pos[1] + ay * 3000)), 3)

        def on_update(self):
            super().on_update()
            self.tick += 1
            if self.tick < 10:
                pass

            else:
                self.damage()
                self.hp_sys.hp -= 25 * 10 ** 6

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 80:
                game.get_game().player.hp_sys.damage(640, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.effect(effects.CurseFire(6, 15))
                self.hp_sys.hp = 10 ** 8

    class TimeNumeral(Entity):
        NAME = 'Time Numeral'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])

        def __init__(self, pos, hp_sys, no: int):
            super().__init__(pos, game.get_game().graphics[f'entity_clock{no}'], BuildingAI, hp_sys=hp_sys)
            self.obj.MASS = 5000
            self.obj.TOUCHING_DAMAGE = 900
            self.obj.IS_OBJECT = False

    class CLOCK(Entity):
        NAME = 'CLOCK'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('chaos_ingot', 1, 100, 120),
            IndividualLoot('time_essence', 1, 30, 45),
            IndividualLoot('time_fountain', 1, 1, 1),
            IndividualLoot('patience_amulet', .5, 1, 1),
            ])
        IS_MENACE = True
        BOSS_NAME = 'The Watcher of Ages'
        PHASE_SEGMENTS = [i / 12 for i in range(1, 12)]

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_clock'], BuildingAI, 800000)
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

        def on_update(self):
            super().on_update()
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
                    game.get_game().player.obj.pos << (self.obj.pos[0] + ap * px, self.obj.pos[1] + ap * py)
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
                e.obj.pos << (self.obj.pos[0] + ax * self.dt,
                             self.obj.pos[1] + ay * self.dt)

    class MATTER(Entity):
        NAME = 'MATTERS'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('chaos_ingot', 1, 100, 120),
            IndividualLoot('substance_essence', 1, 30, 45),
            IndividualLoot('substance_fountain', 1, 1, 1),
            IndividualLoot('integrity_amulet', .5, 1, 1),
            ])
        IS_MENACE = True
        BOSS_NAME = 'The Constructor'
        PHASE_SEGMENTS = [i / 9 for i in range(1, 9)]

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_matters'], BuildingAI, 7200)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 50
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 50
            self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 50
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 25
            self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] /= 100
            self.hp_sys.resistances[damages.DamageTypes.MAGICAL] /= 100
            self.hp_sys.resistances[damages.DamageTypes.ARCANE] /= 100
            self.hp_sys.resistances[damages.DamageTypes.PIERCING] /= 100
            self.hp_sys(op='config', minimum_damage=0.01)
            self.obj.TOUCHING_DAMAGE = 599
            self.phase = 0
            self.tick = 0
            self.dt = 0
            self.cdt = 0
            self.set_rotation(self.rot)

        def on_update(self):
            super().on_update()
            self.cdt = (self.cdt + self.dt * 8) // 2

            pg.draw.circle(game.get_game().displayer.canvas, (0, 0, 255),
                           position.displayed_position(self.obj.pos), self.cdt / game.get_game().player.get_screen_scale(),
                           5)
            if self.hp_sys.hp < self.hp_sys.max_hp * (1 - self.phase / 9):
                self.phase += 1
                self.cdt -= 400
            self.tick += 1
            if self.phase:
                px, py = game.get_game().player.obj.pos
                px -= self.obj.pos[0]
                py -= self.obj.pos[1]
                if vector.distance(px, py) > self.cdt:
                    ap = self.cdt / vector.distance(px, py)
                    game.get_game().player.obj.pos << (self.obj.pos[0] + ap * px, self.obj.pos[1] + ap * py)
                    px *= ap
                    py *= ap
            if self.phase == 0:
                if self.tick <= 120:
                    self.dt = self.tick * 5
                else:
                    self.phase = 1
            elif self.phase == 1:
                self.dt = 6000
                if self.tick % 32 == 1:
                    game.get_game().entities.append(Entities.Thing(game.get_game().player.obj.pos))
            elif self.phase == 2:
                if self.tick % 8 == 1:
                    game.get_game().entities.append(Entities.Thing(game.get_game().player.obj.pos))
            elif self.phase == 3:
                if self.tick % 16 == 1:
                    ply = game.get_game().player
                    game.get_game().entities.append(Entities.Thing(game.get_game().player.obj.pos))
                    rt = random.randint(0, 360)
                    for ar in range(0, 360, 180):
                        ax, ay = vector.rotation_coordinate(rt + ar)
                        for dt in [100, 300, 500]:
                            game.get_game().entities.append(Entities.Thing((ply.obj.pos[0] + ax * dt,
                                                                           ply.obj.pos[1] + ay * dt)))
            elif self.phase == 4:
                if self.tick % 16 == 1:
                    ply = game.get_game().player
                    game.get_game().entities.append(Entities.Thing(game.get_game().player.obj.pos))
                    rt = random.randint(0, 360)
                    for ar in range(0, 360, 90):
                        ax, ay = vector.rotation_coordinate(rt + ar)
                        for dt in [200, 400, 600, 800]:
                            game.get_game().entities.append(Entities.Thing((ply.obj.pos[0] + ax * dt,
                                                                           ply.obj.pos[1] + ay * dt)))
            elif self.phase == 5:
                if self.tick % 24 == 1:
                    ply = game.get_game().player
                    game.get_game().entities.append(Entities.Thing(game.get_game().player.obj.pos))
                    rt = random.randint(0, 360)
                    for ar in range(0, 330, 30):
                        ax, ay = vector.rotation_coordinate(rt + ar)
                        for dt in [200, 400, 600, 800]:
                            game.get_game().entities.append(Entities.Thing((ply.obj.pos[0] + ax * dt,
                                                                           ply.obj.pos[1] + ay * dt)))
            elif self.phase == 6:
                if self.tick % 32 == 1:
                    game.get_game().entities.append(Entities.Thing(game.get_game().player.obj.pos))
                elif self.tick % 16 == 1:
                    ply = game.get_game().player
                    rt = random.randint(0, 360)
                    for ar in range(0, 360, 30):
                        ax, ay = vector.rotation_coordinate(rt + ar)
                        for dt in [200, 400, 600, 800]:
                            game.get_game().entities.append(Entities.Thing((ply.obj.pos[0] + ax * dt,
                                                                           ply.obj.pos[1] + ay * dt)))
                elif self.tick % 4 == 1:
                    dt = random.randint(0, self.cdt)
                    vx, vy = vector.rotation_coordinate(random.randint(0, 360))
                    game.get_game().entities.append(Entities.Thing((self.obj.pos[0] + vx * dt,
                                                                   self.obj.pos[1] + vy * dt)))
            elif self.phase == 7:
                if self.tick % 4 == 1:
                    for _ in range(12):
                        dt = random.randint(0, self.cdt)
                        vx, vy = vector.rotation_coordinate(random.randint(0, 360))
                        game.get_game().entities.append(Entities.Thing((self.obj.pos[0] + vx * dt,
                                                                        self.obj.pos[1] + vy * dt)))
            elif self.phase == 8:
                if self.tick % 3 == 1:
                    for _ in range(14):
                        dt = random.randint(0, self.cdt)
                        vx, vy = vector.rotation_coordinate(random.randint(0, 360))
                        game.get_game().entities.append(Entities.Thing((self.obj.pos[0] + vx * dt,
                                                                        self.obj.pos[1] + vy * dt)))
            else:
                if self.tick % 3 == 1:
                    for _ in range(16):
                        dt = random.randint(0, self.cdt)
                        vx, vy = vector.rotation_coordinate(random.randint(0, 360))
                        game.get_game().entities.append(Entities.Thing((self.obj.pos[0] + vx * dt,
                                                                        self.obj.pos[1] + vy * dt)))

    class SunEye(Entity):
        NAME = 'Sun Eye'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('celestial_fountain', 1, 1, 1),
            IndividualLoot('scorch_core', 1, 1, 1),
            IndividualLoot('perseverance_amulet', .5, 1, 1),
            ])
        VITAL = True

        def __init__(self, pos, hp_sys):
            super().__init__(pos, game.get_game().graphics['entity_sun_eye'], GodsEyeAI, hp_sys=hp_sys)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 400
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 200
            self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 1000
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 500
            self.action_state = 0
            self.tick = 0
            self.phs = 0

        def t_draw(self):
            super().t_draw()
            if self.action_state <= 2:
                s = game.get_game().graphics['entity_sun_eye_back_soul']
                if s.get_alpha() != 120:
                    s.set_alpha(120)
                s = pg.transform.scale(s, (1200 / game.get_game().player.get_screen_scale(),
                                           1200 / game.get_game().player.get_screen_scale()))
                sr = s.get_rect(center=position.displayed_position(self.obj.pos))
                game.get_game().displayer.canvas.blit(s, sr)

        def on_update(self):
            self.obj.phs = self.phs
            self.tick += 1
            self.obj.state = self.action_state
            if self.action_state in [3, 4]:
                px, py = game.get_game().player.obj.pos
                px -= self.obj.pos[0]
                py -= self.obj.pos[1]
                self.set_rotation(-vector.coordinate_rotation(px, py))
                if self.tick % (60 - self.phs * 30) == 0:
                    for ar in range(-20, 21, 20 - self.phs * 10):
                        game.get_game().entities.append(Entities.SunFire(self.obj.pos,
                                                                         ar - self.rot, self))
            elif self.action_state == 5:
                self.set_rotation(-self.obj.velocity.get_net_rotation())
                if self.tick % (15 - self.phs * 7) == 0:
                    for ar in range(-20, 21, 10 - self.phs * 5):
                        game.get_game().entities.append(Entities.SunFire(self.obj.pos,
                                                                         ar - self.rot, self))
            elif self.action_state == 6:
                self.set_rotation(self.rot + 112)
                if self.tick % (2 - self.phs) == 0:
                    game.get_game().entities.append(Entities.SunFire((game.get_game().player.obj.pos[0] + random.randint(-3000, 3000),
                                                                        game.get_game().player.obj.pos[1] - random.randint(1000, 4000)),
                                                                      vector.coordinate_rotation(0, 1)))
                if self.tick % 10 == 5:
                    game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                            n=35, col=(255, 63, 0), sp=40, t=10))

    class MoonEye(Entity):
        NAME = 'Moon Eye'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('celestial_fountain', 1, 1, 1),
            IndividualLoot('curse_core', 1, 1, 1),
            IndividualLoot('bravery_amulet', .5, 1, 1),
            ])
        VITAL = True

        def __init__(self, pos, hp_sys):
            super().__init__(pos, game.get_game().graphics['entity_moon_eye'], GodsEyeAI, hp_sys=hp_sys)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 400
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 200
            self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 1000
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 500
            self.action_state = 0
            self.tick = 0
            self.phs = 0

        def t_draw(self):
            super().t_draw()
            if self.action_state <= 2:
                s = game.get_game().graphics['entity_moon_eye_back_soul']
                if s.get_alpha() != 120:
                    s.set_alpha(120)
                s = pg.transform.scale(s, (1200 / game.get_game().player.get_screen_scale(),
                                           1200 / game.get_game().player.get_screen_scale()))
                sr = s.get_rect(center=position.displayed_position(self.obj.pos))
                game.get_game().displayer.canvas.blit(s, sr)

        def on_update(self):
            self.obj.phs = self.phs
            self.tick += 1
            self.obj.state = self.action_state
            if self.action_state in [3, 4]:
                px, py = game.get_game().player.obj.pos
                px -= self.obj.pos[0]
                py -= self.obj.pos[1]
                self.set_rotation(-vector.coordinate_rotation(px, py))
                if self.tick % (60 - self.phs * 30) == 30 - self.phs * 15:
                    for ar in range(-20, 21, 20 - self.phs * 10):
                        game.get_game().entities.append(Entities.MoonFire(self.obj.pos,
                                                                          ar - self.rot, self))
            elif self.action_state == 5:
                self.set_rotation(-self.obj.velocity.get_net_rotation())
                if self.tick % (15 - self.phs * 7) == 0:
                    for ar in range(-20, 21, 10 - self.phs * 5):
                        game.get_game().entities.append(Entities.MoonFire(self.obj.pos,
                                                                          ar - self.rot, self))
            elif self.action_state == 6:
                self.set_rotation(self.rot + 112)
                if self.tick % (2 - self.phs) == 0:
                    game.get_game().entities.append(Entities.MoonFire((game.get_game().player.obj.pos[0] + random.randint(-3000, 3000),
                                                                        game.get_game().player.obj.pos[1] - random.randint(1000, 4000)),
                                                                      vector.coordinate_rotation(0, 1)))
                if self.tick % 10 == 0:
                    game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                            n=35, col=(63, 255, 0), sp=40, t=10))

    class GodsEye(Entity):
        NAME = 'GOD\'S EYE'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])
        IS_MENACE = True
        BOSS_NAME = 'Sun and Moon'

        PHASE_SEGMENTS = [0.08, 0.13, 0.18, 0.24, 0.30, 0.38, 0.46, 0.55, 0.64, 0.76, 0.88, 0.94, 0.98]

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['items_null'], BuildingAI, 540000)
            self.obj.IS_OBJECT = False
            self.sun_eye = Entities.SunEye((self.obj.pos[0] + random.randint(-1000, 1000),
                                            self.obj.pos[1] + random.randint(-1000, 1000)), self.hp_sys)
            self.moon_eye = Entities.MoonEye((self.obj.pos[0] + random.randint(-1000, 1000),
                                            self.obj.pos[1] + random.randint(-1000, 1000)), self.hp_sys)
            self.phase = 0
            game.get_game().entities.append(self.sun_eye)
            game.get_game().entities.append(self.moon_eye)
            self.sun_eye.action_state = 1
            self.moon_eye.action_state = 2
            self.tick = 0

        def on_update(self):
            self.tick += 1
            if self.phase < len(self.PHASE_SEGMENTS) and self.hp_sys.hp < self.hp_sys.max_hp * self.PHASE_SEGMENTS[-1 - self.phase]:
                self.phase += 1
            if (self.sun_eye not in game.get_game().entities or self.moon_eye not in game.get_game().entities) and \
                self.hp_sys.hp > 0:
                if self.sun_eye in game.get_game().entities:
                    game.get_game().entities.remove(self.sun_eye)
                    del self.sun_eye
                if self.moon_eye in game.get_game().entities:
                    game.get_game().entities.remove(self.moon_eye)
                    del self.moon_eye
                game.get_game().entities.remove(self)
            if self.phase == 0:
                self.sun_eye.action_state = 1
                self.moon_eye.action_state = 2
            elif self.phase == 1:
                if self.tick % 360 < 180:
                    self.sun_eye.action_state = 3
                    self.moon_eye.action_state = 4
                else:
                    self.sun_eye.action_state = 4
                    self.moon_eye.action_state = 3
            elif self.phase == 2:
                if self.tick % 360 < 180:
                    self.sun_eye.action_state = 3
                    self.moon_eye.action_state = 4
                else:
                    self.sun_eye.action_state = 5
                    self.moon_eye.action_state = 5
            elif self.phase == 3:
                if self.tick % 360 < 180:
                    self.sun_eye.action_state = 3
                    self.moon_eye.action_state = 5
                else:
                    self.sun_eye.action_state = 5
                    self.moon_eye.action_state = 4
            elif self.phase == 4:
                self.sun_eye.action_state = 6
                if self.tick % 360 < 180:
                    self.moon_eye.action_state = 5
                else:
                    self.moon_eye.action_state = 4
            elif self.phase == 5:
                self.moon_eye.action_state = 6
                if self.tick % 360 < 180:
                    self.sun_eye.action_state = 5
                else:
                    self.sun_eye.action_state = 3
            elif self.phase == 6:
                if self.tick % 360 < 180:
                    self.sun_eye.action_state = 6
                    self.moon_eye.action_state = 4
                else:
                    self.sun_eye.action_state = 3
                    self.moon_eye.action_state = 6
            elif self.phase == 7:
                if self.tick % 360 < 180:
                    self.sun_eye.action_state = 3
                    self.moon_eye.action_state = 5
                else:
                    self.sun_eye.action_state = 5
                    self.moon_eye.action_state = 4
            elif self.phase == 8:
                self.sun_eye.action_state = 6
                self.moon_eye.action_state = 6
            elif self.phase == 9:
                self.sun_eye.phs = 1
                self.moon_eye.phs = 1
                self.sun_eye.action_state = 2
                self.moon_eye.action_state = 1
            elif self.phase == 10:
                if self.tick % 360 < 180:
                    self.sun_eye.action_state = 3
                    self.moon_eye.action_state = 4
                else:
                    self.sun_eye.action_state = 5
                    self.moon_eye.action_state = 5
            elif self.phase == 11:
                self.sun_eye.action_state = 6
                if self.tick % 360 < 180:
                    self.moon_eye.action_state = 5
                else:
                    self.moon_eye.action_state = 3
            elif self.phase == 12:
                self.moon_eye.action_state = 6
                if self.tick % 360 < 180:
                    self.sun_eye.action_state = 5
                else:
                    self.sun_eye.action_state = 4
            else:
                self.sun_eye.action_state = 6
                self.moon_eye.action_state = 6
            self.obj.pos << self.sun_eye.obj.pos

    class HolyPillar(Ore):
        NAME = 'Holy Pillar'
        DISPLAY_MODE = 1
        TOUGHNESS = 400
        LOOT_TABLE = LootTable([
            IndividualLoot('result', 1, 10, 20),
        ])
        IMG = 'entity_holy_pillar'

        def __init__(self, pos):
            super().__init__(pos, 100)
            self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = 0
            self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 0
            self.hp_sys.resistances[damages.DamageTypes.ARCANE] = 0
            self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 0
            self.hp_sys(op='config', minimum_damage=0)

    class ScarlettPillar(Ore):
        NAME = 'Scarlett Pillar'
        DISPLAY_MODE = 1
        TOUGHNESS = 400
        LOOT_TABLE = LootTable([
            IndividualLoot('reason', 1, 10, 20),
        ])
        IMG = 'entity_scarlett_pillar'

        def __init__(self, pos):
            super().__init__(pos, 100)
            self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = 0
            self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 0
            self.hp_sys.resistances[damages.DamageTypes.ARCANE] = 0
            self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 0
            self.hp_sys(op='config', minimum_damage=0)

    class LifeFire(Entity):
        NAME = 'Life Fire'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])

        def __init__(self, pos, rot, follow_entity=None, tt=0):
            super().__init__(pos, game.get_game().graphics['entity_lifefire'], FastBulletAI, 10 ** 6)
            self.obj.MASS = 1000
            self.obj.rot = rot
            self.obj.speed = 8800
            self.tick = tt
            self.tt = 0
            if follow_entity is not None:
                self.ax = self.obj.pos[0] - follow_entity.obj.pos[0]
                self.ay = self.obj.pos[1] - follow_entity.obj.pos[1]
                self.arot = rot + follow_entity.rot
                self.follow_entity = follow_entity
            else:
                self.ax, self.ay, self.arot = 0, 0, 0
                self.follow_entity = None

        def t_draw(self):
            self.tt += 1
            if self.tick > 10:
                self.obj.update()
                game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                        col=(200, 255, 100), t=6, sp=20, n=3))
            else:
                if self.follow_entity is not None:
                    self.obj.pos << (self.follow_entity.obj.pos[0] + self.ax, self.follow_entity.obj.pos[1] + self.ay)
                    self.obj.rot = -self.follow_entity.rot + self.arot
                ax, ay = vector.rotation_coordinate(self.obj.rot)
                draw.line(game.get_game().displayer.canvas, (0, 255, 0),
                          position.displayed_position(self.obj.pos),
                          position.displayed_position((self.obj.pos[0] + ax * 3000, self.obj.pos[1] + ay * 3000)),
                          3)

        def on_update(self):
            self.tick += 1
            if self.tick < 10:
                pass
            else:
                self.damage()
                self.hp_sys.hp -= 25 * 10 ** 3

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 180:
                game.get_game().player.hp_sys.damage(2200, damages.DamageTypes.MAGICAL)
                self.hp_sys.hp = 10 ** 8

    class LifeDart(Entity):
        NAME = 'Life Dart'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])

        def __init__(self, pos, rot, follow_entity=None):
            super().__init__(pos, game.get_game().graphics['entity_lifefire'], FastBulletAI, 10 ** 6)
            self.obj.MASS = 4000
            self.obj.rot = rot
            self.obj.speed = 8800
            self.tick = 0
            self.tt = 0
            if follow_entity is not None:
                self.ax = self.obj.pos[0] - follow_entity.obj.pos[0]
                self.ay = self.obj.pos[1] - follow_entity.obj.pos[1]
                self.arot = rot + follow_entity.rot
                self.follow_entity = follow_entity
            else:
                self.ax, self.ay, self.arot = 0, 0, 0
                self.follow_entity = None

        def t_draw(self):
            self.tt += 1
            if self.tick > 10:
                self.obj.update()
                self.show_bar = False
                cef.cut_eff(game.get_game().displayer.canvas, 60 / game.get_game().player.get_screen_scale(),
                            *position.displayed_position(self.obj.pos),
                            *position.displayed_position(self.obj.pos + self.obj.velocity * 2),
                            color=(50, 120, 0))
                self.set_rotation(self.obj.velocity.get_net_rotation())
                if self.tt % 40 == 1:
                    game.get_game().displayer.effect(
                        pef.p_particle_effects(*position.displayed_position(self.obj.pos),
                                               col=(0, 127, 0), t=60, sp=2, n=12, g=0))
                    self.rot = self.obj.velocity.get_net_rotation()
                    game.get_game().entities.extend([
                        Entities.LifeFire(self.obj.pos, self.rot + 90, tt=8),
                        Entities.LifeFire(self.obj.pos, self.rot - 90, tt=8),
                    ])
            else:
                if self.follow_entity is not None:
                    self.obj.pos << (self.follow_entity.obj.pos[0] + self.ax, self.follow_entity.obj.pos[1] + self.ay)
                    self.obj.rot = -self.follow_entity.rot + self.arot
                ax, ay = vector.rotation_coordinate(self.obj.rot)
                draw.line(game.get_game().displayer.canvas, (0, 255, 0),
                          position.displayed_position(self.obj.pos),
                          position.displayed_position((self.obj.pos[0] + ax * 3000, self.obj.pos[1] + ay * 3000)),
                          int(7 + 6 * math.sin(self.tt / 30)))

        def on_update(self):
            self.tick += 1
            if self.tick < 10:
                pass
            else:
                self.damage()
                self.hp_sys.hp -= 25 * 10 ** 3

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 180:
                game.get_game().player.hp_sys.damage(2800, damages.DamageTypes.MAGICAL)
                self.hp_sys.hp = 10 ** 8
                
    class LargeTree(Entity):
        NAME = 'Large Tree'
        DISPLAY_MODE = 1
        
        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_tree'], FastBulletAI, 10 ** 7)
            self.obj.MASS *= 3
            self.obj.SPEED *= 2
            self.obj.MASS = 3000
            self.tick = 0
            self.tt = 0
            self.obj.rot = rot

        def t_draw(self):
            self.tt += 1
            self.rotate(8)
            if self.tick > 10:
                super().t_draw()
                self.obj.update()
                self.show_bar = False
                self.set_rotation(self.obj.velocity.get_net_rotation())
                if self.tt % 60 == 1:
                    for i in range(0, 360, 60):
                        vv = Entities.LifeDart(self.obj.pos, self.rot + i, follow_entity=self)
                        vv.obj.velocity -= vector.Vector2D(self.rot + i, 50)
                        vv.tick = 5
                        game.get_game().entities.append(vv)
            else:
                ax, ay = vector.rotation_coordinate(self.obj.rot)
                draw.line(game.get_game().displayer.canvas, (0, 255, 0),
                          position.displayed_position(self.obj.pos),
                          position.displayed_position((self.obj.pos[0] + ax * 3000, self.obj.pos[1] + ay * 3000)),
                          int(20 + 15 * math.sin(self.tt / 30)))

        def on_update(self):
            self.tick += 1
            if self.tick < 10:
                pass
            else:
                self.damage()
                self.hp_sys.hp -= 25 * 10 ** 4

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 180:
                game.get_game().player.hp_sys.damage(2800, damages.DamageTypes.MAGICAL)
                self.hp_sys.hp = 10 ** 8

    class FaithFire(Entity):
        NAME = 'Faith Fire'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])

        def __init__(self, pos, rot, follow_entity=None):
            super().__init__(pos, game.get_game().graphics['items_null'], FastBulletAI, 10 ** 6)
            self.obj.MASS = 1000
            self.obj.rot = rot
            self.obj.speed = 8800
            self.tick = 0
            if follow_entity is not None:
                self.ax = self.obj.pos[0] - follow_entity.obj.pos[0]
                self.ay = self.obj.pos[1] - follow_entity.obj.pos[1]
                self.arot = rot + follow_entity.rot
                self.follow_entity = follow_entity
            else:
                self.ax, self.ay, self.arot = 0, 0, 0
                self.follow_entity = None

        def t_draw(self):
            if self.tick > 10:
                self.obj.update()
                game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                        col=(0, 0, 0), t=6, sp=8, n=2))
            else:
                if self.follow_entity is not None:
                    self.obj.pos << (self.follow_entity.obj.pos[0] + self.ax, self.follow_entity.obj.pos[1] + self.ay)
                    self.obj.rot = -self.follow_entity.rot + self.arot
                ax, ay = vector.rotation_coordinate(self.obj.rot)
                draw.line(game.get_game().displayer.canvas, (0, 0, 0),
                             position.displayed_position(self.obj.pos),
                             position.displayed_position(
                                 (self.obj.pos[0] + ax * 3000, self.obj.pos[1] + ay * 3000)), 3)

        def on_update(self):
            self.tick += 1
            if self.tick < 10:
                pass
            else:
                self.damage()
                self.hp_sys.hp -= 25 * 10 ** 3

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 180:
                game.get_game().player.hp_sys.damage(2000, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.effect(effects.Faith(4, 100))
                self.hp_sys.hp = 10 ** 8

    class QuarkFire(Entity):
        NAME = 'Quark Fire'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])

        def __init__(self, pos, rot, follow_entity=None):
            super().__init__(pos, game.get_game().graphics['items_null'], FastBulletAI, 10 ** 9)
            self.obj.MASS = 1000
            self.obj.rot = rot
            self.obj.speed = 8800
            self.tick = 0
            if follow_entity is not None:
                self.ax = self.obj.pos[0] - follow_entity.obj.pos[0]
                self.ay = self.obj.pos[1] - follow_entity.obj.pos[1]
                self.arot = rot + follow_entity.rot
                self.follow_entity = follow_entity
            else:
                self.ax, self.ay, self.arot = 0, 0, 0
                self.follow_entity = None

        def t_draw(self):
            if self.tick > 5:
                self.obj.update()
                game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                        col=(0, 255, 255), t=6, sp=8, n=2))
            else:
                if self.follow_entity is not None:
                    self.obj.pos << (
                    self.follow_entity.obj.pos[0] + self.ax, self.follow_entity.obj.pos[1] + self.ay)
                    self.obj.rot = -self.follow_entity.rot + self.arot
                ax, ay = vector.rotation_coordinate(self.obj.rot)
                draw.line(game.get_game().displayer.canvas, (0, 255, 255),
                             position.displayed_position(self.obj.pos),
                             position.displayed_position(
                                 (self.obj.pos[0] + ax * 3000, self.obj.pos[1] + ay * 3000)), 3)

        def on_update(self):
            self.tick += 1
            if self.tick < 10:
                pass
            else:
                self.damage()
                self.hp_sys.hp -= 25 * 10 ** 6

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 180:
                game.get_game().player.hp_sys.damage(1500, damages.DamageTypes.MAGICAL)
                game.get_game().player.hp_sys.effect(effects.Faith(4, 24))
                self.hp_sys.hp = 10 ** 8

    class QuarkGhost(WormEntity):
        BOSS_NAME = 'The Eternal Energy'
        NAME = 'The Quark Ghost'
        DISPLAY_MODE = 1
        IS_MENACE = True
        PHASE_SEGMENTS = [0.3, 0.6]
        LOOT_TABLE = LootTable([
            IndividualLoot('quark_rusher', 1, 1, 1),
        ])

        def __init__(self, pos):
            super().__init__(pos, 64, game.get_game().graphics['entity_quark_ghost_head'],
                             game.get_game().graphics['entity_quark_ghost_body'],
                             QuarkGhostAI, 45000000, body_length=250, body_touching_damage=1500)

            self.phase = 0

        def on_update(self):
            super().on_update()
            if self.phase == 0 and self.hp_sys.hp < self.hp_sys.max_hp * .6:
                self.phase = 1
                self.obj.SPEED *= 1.5
            if self.phase == 1 and self.hp_sys.hp < self.hp_sys.max_hp * .3:
                self.phase = 2
                self.obj.SPEED *= 1.5
            for b in self.body:
                if random.randint(0, 650 - self.phase * 180) == 114:
                    px, py = game.get_game().player.obj.pos
                    px -= b.obj.pos[0]
                    py -= b.obj.pos[1]
                    game.get_game().entities.append(Entities.QuarkFire(b.obj.pos, vector.coordinate_rotation(px, py), b))


    class ReincarnationTheWorldsTree(Entity):
        NAME = 'Reincarnation: The World\'s Tree'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('death_fountain', 1, 1, 1),
            IndividualLoot('kindness_amulet', .5, 1, 1),
            SelectionLoot([('generation', 1, 1)], 1, 1),
        ])
        IS_MENACE = True
        BOSS_NAME = 'The Unwill of the Supreme'
        PHASE_SEGMENTS = [0.1, 0.22, 0.34, 0.46, 0.58, 0.7, 0.8, 0.9]
        PHASES = ['none', 'born', 'growth', 'huge', 'fruit', 'death', 'gone', 'recovery', 'rebirth']

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_reincarnation__the_worlds_tree_none'], WorldsTreeAI, 25000000)
            self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = 0.8
            self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 0.8
            self.hp_sys.resistances[damages.DamageTypes.ARCANE] = 0.8
            self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 0.8
            self.phase = -1
            self.tick = 0
            self.at_p = 0
            game.get_game().decors.clear()
            game.get_game().entities.clear()
            self.rw = constants.INFINITY
            self.rh = constants.INFINITY

        def t_draw(self):
            super().t_draw()
            if self.phase in [-1, 0, 8]:
                s = game.get_game().graphics['entity_worlds_tree_back_soul']
                if s.get_alpha() != 120:
                    s.set_alpha(120)
                s = pg.transform.scale(s, (1200 / game.get_game().player.get_screen_scale(),
                                           1200 / game.get_game().player.get_screen_scale()))
                sr = s.get_rect(center=position.displayed_position(self.obj.pos))
                game.get_game().displayer.canvas.blit(s, sr)
            if self.rw < constants.INFINITY and self.rh < constants.INFINITY:
                draw.l_rect(game.get_game().displayer.canvas, (255, 255, 255),
                            position.displayed_position(self.obj.pos - (self.rw // 2, self.rh // 2)),
                            position.displayed_position(self.obj.pos + (self.rw // 2, self.rh // 2)), 10)
                if game.get_game().player.obj.pos[0] < self.obj.pos[0] - self.rw // 2:
                    game.get_game().player.obj.velocity.add(vector.Vector2D(dx=50))
                if game.get_game().player.obj.pos[0] > self.obj.pos[0] + self.rw // 2:
                    game.get_game().player.obj.velocity.add(vector.Vector2D(dx=-50))
                if game.get_game().player.obj.pos[1] < self.obj.pos[1] - self.rh // 2:
                    game.get_game().player.obj.velocity.add(vector.Vector2D(dy=50))
                if game.get_game().player.obj.pos[1] > self.obj.pos[1] + self.rh // 2:
                    game.get_game().player.obj.velocity.add(vector.Vector2D(dy=-50))


        def on_update(self):
            self.tick += 1
            if self.phase >= 0:
                if random.randint(0, self.tick) > 80:
                    self.at_p += 1
                    self.tick = 0
            if self.phase == -1:
                if self.tick == 1:
                    self.hp_sys.IMMUNE = True
                    self.obj.IS_OBJECT = False
                    if constants.LANG == 'en':
                        game.get_game().dialog.dialog(
                            'The death is not the end....',
                            'It never ends....',
                            '"GODKILLER", \ncan you handle that?'
                        )
                    else:
                        game.get_game().dialog.dialog(
                            '【輪迴】不止，生生不息...',
                            '【弒神者】，\n汝可敢挑战【輪迴】？'
                        )
                elif not len(game.get_game().dialog.curr_text):
                    self.hp_sys.IMMUNE = False
                    self.obj.IS_OBJECT = True
                    self.phase = 0
                return
            if self.phase < len(self.PHASE_SEGMENTS) and self.hp_sys.hp < self.hp_sys.max_hp * self.PHASE_SEGMENTS[-1 - self.phase]:
                self.phase += 1
                self.img = game.get_game().graphics['entity_reincarnation__the_worlds_tree_' + self.PHASES[self.phase]]
                self.NAME = 'The World\'s Tree - ' + self.PHASES[self.phase].upper()
                self.hp_sys.effect(effects.Frozen(3, 1))
            if random.uniform(0, 10 - self.phase) < .4:
                for i, e in enumerate(game.get_game().entities):
                    if type(e) is Entities.LifeFire:
                        game.get_game().entities[i].obj = SoulFlowerAI(e.obj.pos)
                        e.obj.SPEED *= 5
                        e.obj.FRICTION = 1
                        e.obj.TOUCHING_DAMAGE = 0
                        e.obj.SIGHT_DISTANCE = 9999
                        setattr(e.obj, 'rot', 0)
                self.play_sound('create')
                self.hp_sys.effect(effects.Frozen(1, 1))
            if self.phase == 0:
                self.obj.state = 0
                if self.at_p % 3 == 0:
                    if self.tick % 5 == 0:
                        game.get_game().entities.append(
                            Entities.LifeDart((game.get_game().player.obj.pos[0] + random.randint(-3000, 3000),
                                               game.get_game().player.obj.pos[1] + random.randint(1000, 4000)),
                                              vector.coordinate_rotation(0, -1)))
                    self.rw = 6000
                    self.rh = 6000
                elif self.at_p % 3 == 1:
                    self.rw = 6000
                    self.rh = 4000
                    if self.tick % 24 == 0:
                        for ry in range(-2000, 2001, 1000):
                            game.get_game().entities.append(Entities.LifeDart(self.obj.pos + (-4000, ry),
                                                            vector.coordinate_rotation(1, 0)))
                        for ry in range(-1500, 2001, 1000):
                            game.get_game().entities.append(Entities.LifeDart(self.obj.pos + (4000, ry),
                                                                              vector.coordinate_rotation(-1, 0)))
                elif self.at_p % 3 == 2:
                    self.rw = 6000
                    self.rh = 2000
                    if self.tick % 10 == 0:
                        game.get_game().entities.append(Entities.LifeDart(self.obj.pos + (-4000 - self.tick * 100 % 4000, -1000),
                                                                          vector.coordinate_rotation(1, 0)))
                        game.get_game().entities.append(Entities.LifeDart(self.obj.pos + (4000 + self.tick * 100 % 4000, 1000),
                                                                          vector.coordinate_rotation(-1, 0)))
            elif self.phase == 1:
                if self.at_p % 2 == 0:
                    self.obj.state = 1
                    self.obj.FRICTION = .9
                    self.rw = 1000
                    self.rh = 1000
                    game.get_game().entities = [e for e in game.get_game().entities if type(e) is not Entities.LifeFire]
                else:
                    self.rw = 4000
                    self.rh = 4000
                    self.obj.FRICTION = 0
                    if self.tick % 10 == 0:
                        for ar in range(int((self.obj.pos[0] + self.obj.pos[1]) / 300) % 60, 360, 60):
                            game.get_game().entities.append(Entities.LifeDart(self.obj.pos, ar, self))
            elif self.phase == 2:
                self.obj.state = 1
                if self.at_p % 2 == 0:
                    self.rw = 500
                    self.rh = 500
                    self.obj.FRICTION = 1
                    self.obj.state = 1
                else:
                    self.obj.state = 0
                    self.rw = 2000
                    self.rh = 8000
                    if self.tick % 10 == 0:
                        game.get_game().entities.append(Entities.LargeTree(self.obj.pos, 0))
                        game.get_game().entities.append(Entities.LargeTree(self.obj.pos, 180))
            elif self.phase == 3:
                self.obj.state = 2
                rr = random.randint(0, 30)
                if self.tick % 16 == 0:
                    for ar in range(0, 360, 30):
                        game.get_game().entities.append(Entities.LifeFire(self.obj.pos, ar + rr, self))
                elif self.tick % 2 == 0:
                    px, py = game.get_game().player.obj.pos
                    rr = vector.coordinate_rotation(px - self.obj.pos[0], py - self.obj.pos[1])
                    pr = self.tick % 16 // 2
                    game.get_game().entities.append(Entities.LifeFire(self.obj.pos, rr - pr * 5, self))
                    game.get_game().entities.append(Entities.LifeFire(self.obj.pos, rr + pr * 5, self))
            elif self.phase == 4:
                if self.tick % 80 < 40:
                    self.obj.state = 1
                else:
                    self.obj.state = 2
                if self.tick % 2 == 0:
                    dr = self.tick // 2 * 20 % 360
                    for ar in range(0, 360, 24):
                        game.get_game().entities.append(Entities.LifeFire(self.obj.pos, ar + dr, self))
            elif self.phase == 5:
                self.obj.state = 0
                if self.tick % 16 == 0:
                    px, py = game.get_game().player.obj.pos
                    rr = vector.coordinate_rotation(px - self.obj.pos[0], py - self.obj.pos[1])
                    game.get_game().entities.append(Entities.LifeFire(self.obj.pos, rr - 15, self))
                    game.get_game().entities.append(Entities.LifeFire(self.obj.pos, rr + 15, self))
                    game.get_game().entities.append(Entities.LifeFire(self.obj.pos, rr - 45, self))
                    game.get_game().entities.append(Entities.LifeFire(self.obj.pos, rr + 45, self))
                elif self.tick % 8 == 0:
                    px, py = game.get_game().player.obj.pos
                    rr = vector.coordinate_rotation(px - self.obj.pos[0], py - self.obj.pos[1])
                    game.get_game().entities.append(Entities.LifeFire(self.obj.pos, rr, self))
                    game.get_game().entities.append(Entities.LifeFire(self.obj.pos, rr - 30, self))
                    game.get_game().entities.append(Entities.LifeFire(self.obj.pos, rr + 30, self))
                    game.get_game().entities.append(Entities.LifeFire(self.obj.pos, rr - 60, self))
                    game.get_game().entities.append(Entities.LifeFire(self.obj.pos, rr + 60, self))
            elif self.phase == 6:
                px, py = game.get_game().player.obj.pos
                ax, ay = random.randint(-1000, 1000), random.randint(-1000, 1000)
                game.get_game().entities.append(Entities.LifeFire((px + ax, py + ay),
                                                vector.coordinate_rotation(-ax, -ay), self))
                if self.tick % 2 == 0:
                    game.get_game().entities.append(
                        Entities.LifeFire((game.get_game().player.obj.pos[0] + random.randint(-3000, 3000),
                                           game.get_game().player.obj.pos[1] + random.randint(1000, 4000)),
                                          vector.coordinate_rotation(0, -1)))
            elif self.phase == 7:
                self.obj.state = 1
                if self.tick % 3 == 0:
                    game.get_game().entities.append(
                        Entities.LifeFire((game.get_game().player.obj.pos[0] + random.randint(-3000, 3000),
                                           game.get_game().player.obj.pos[1] + random.randint(1000, 4000)),
                                          vector.coordinate_rotation(0, -1)))
                if self.tick % 12 == 0:
                    for _ in range(9):
                        px, py = game.get_game().player.obj.pos
                        rr = vector.coordinate_rotation(px - self.obj.pos[0], py - self.obj.pos[1])
                        game.get_game().entities.append(Entities.LifeFire(self.obj.pos, rr + random.randint(-30, 30), self))
            elif self.phase == 8:
                self.obj.state = 1
                if self.tick % 2 == 0:
                    game.get_game().entities.append(
                        Entities.LifeFire((game.get_game().player.obj.pos[0] + random.randint(-3000, 3000),
                                           game.get_game().player.obj.pos[1] + random.randint(1000, 4000)),
                                          vector.coordinate_rotation(0, -1)))
                if self.tick % 6 == 0:
                    pr = self.tick % 360
                    for ar in range(0, 360, 20):
                        game.get_game().entities.append(Entities.LifeFire(self.obj.pos, ar + pr, self))

    class Faith(Entity):
        NAME = 'Supreme Lord: Faith'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('no_fountain', 1, 1, 1),
            IndividualLoot('justice_amulet', .5, 1, 1),
            SelectionLoot([('prophecy', 1, 1)], 1, 1),
        ])
        IS_MENACE = True
        BOSS_NAME = 'The End of Shapeless'
        PHASE_SEGMENTS = []
        PHASES = []

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_faith'], BuildingAI, 8000000)
            self.obj.MASS = 1800
            self.obj.TOUCHING_DAMAGE = 2400
            self.state = 0
            self.tick = 0
            self.interval = 30

        def on_update(self):
            if random.uniform(0, self.hp_sys.hp) < 80000:
                for i, e in enumerate(game.get_game().entities):
                    if type(e) is Entities.FaithFire:
                        game.get_game().entities[i].obj = CleverRangedAI(e.obj.pos)
                        e.obj.SPEED *= 5
                        e.obj.SIGHT_DISTANCE = 9999
                        e.hp_sys.hp //= 3
                        e.obj.TOUCHING_DAMAGE = 0
                        setattr(e.obj, 'rot', 0)
                self.play_sound('create')
                self.hp_sys.effect(effects.Frozen(7, 1))
            if self.tick < 20:
                s = game.get_game().graphics['entity_faith_back_soul']
                if s.get_alpha() != 120:
                    s.set_alpha(120)
                s = pg.transform.scale(s, (1200 / game.get_game().player.get_screen_scale(),
                                           1200 / game.get_game().player.get_screen_scale()))
                sr = s.get_rect(center=position.displayed_position(self.obj.pos))
                game.get_game().displayer.canvas.blit(s, sr)
            self.tick += 1
            if self.tick > 240:
                self.state = random.randint(0, 3)
                self.interval = 20
                self.tick = 0
            if self.tick % 12 == 0:
                self.hp_sys.heal(12000)
            px, py = game.get_game().player.obj.pos
            px -= self.obj.pos[0]
            py -= self.obj.pos[1] + 1000
            self.obj.apply_force(vector.Vector(vector.coordinate_rotation(px, py), vector.distance(px, py) * 16))
            if self.state == 0:
                if self.tick % self.interval == 0:
                    for _ in range(6):
                        game.get_game().entities.append(
                            Entities.FaithFire((game.get_game().player.obj.pos[0] + random.randint(-3000, 3000),
                                               game.get_game().player.obj.pos[1] - random.randint(1000, 4000)),
                                              vector.coordinate_rotation(0, 1)))
                    self.interval = max(3, self.interval - 4)
                    self.tick += self.interval - self.tick % self.interval + 1
            elif self.state == 1:
                if self.tick % self.interval == 0:
                    px, py = game.get_game().player.obj.pos
                    px -= self.obj.pos[0]
                    py -= self.obj.pos[1]
                    for _ in range(3):
                        game.get_game().entities.append(Entities.FaithFire(self.obj.pos,
                                                                           vector.coordinate_rotation(px, py) + random.randint(-10, 10), self))
                    self.interval = max(1, self.interval - 5)
                    self.tick += self.interval - self.tick % self.interval + 1
            elif self.state == 2:
                if self.tick % self.interval == 0:
                    r = random.randint(0, 1)
                    if r:
                        ar = [-80, -60, -40, -20, 0, 20, 40, 60, 80]
                    else:
                        ar = [-180, -160, -140, -120, -100, 100, 120, 140, 160]
                    px, py = game.get_game().player.obj.pos
                    px -= self.obj.pos[0]
                    py -= self.obj.pos[1]
                    for a in ar:
                        game.get_game().entities.append(Entities.FaithFire(self.obj.pos,
                                                                          vector.coordinate_rotation(px, py) + a,
                                                                          self))
                    self.interval = max(4, self.interval - 4)
                    self.tick += self.interval - self.tick % self.interval + 1
            elif self.state == 3:
                if self.tick % self.interval == 0:
                    px, py = game.get_game().player.obj.pos
                    r = random.randint(0, 359)
                    for ar in range(r, r + 300, 10):
                        vx, vy = vector.rotation_coordinate(ar)
                        game.get_game().entities.append(Entities.FaithFire((px + vx * 500, py + vy * 500), ar + 180,
                                                                          self))
                    self.interval = max(7, self.interval - 4)
                    self.tick += self.interval - self.tick % self.interval + 1

    class BurstBall(Entity):
        NAME = 'Burst Ball'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])

        SOUND_HURT = 'crystal'
        SOUND_DEATH = 'explosion'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_burst_ball'], DragonAI, 1000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 1000
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 1000
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 1000
            self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 1000
            self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 1000
            self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 1000
            self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 1000
            self.obj.TOUCHING_DAMAGE = 1000
            game.get_game().displayer.effect(fc.p_fade_circle(*position.displayed_position(self.obj.pos),
                                                              col=(255, 255, 255), sp=30, t=20))

        def on_update(self):
            super().on_update()
            self.set_rotation(self.rot + 6)

    class CrushBall(BurstBall):
        NAME = 'Crush Ball'

        def __init__(self, pos):
            super().__init__(pos)
            self.obj.TOUCHING_DAMAGE += 200
            self.obj.MASS -= 100

    class OblivionAnnihilator(Entity):
        NAME = 'Oblivion: Annihilator'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('destroy_shard', 1, 20, 30)
        ])
        IS_MENACE = True
        BOSS_NAME = 'The Void and Chaos'
        PHASE_SEGMENTS = [0.6, 0.85]

        SOUND_HURT = 'corrupt'
        SOUND_DEATH = 'haha'

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_oblivion_annihilator'], BuildingAI, 4000000)
            self.obj.MASS = 10 ** 8
            self.obj.TOUCHING_DAMAGE = 2500
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 2000
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 2000
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 2000
            self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 2000
            self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 2000
            self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 2000
            self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 2000
            game.get_game().dialog.push_dialog('The Annihilator is awoken!', '* The nightmare begins...')
            self.tick = 0
            self.phase = 0
            game.get_game().decors.clear()
            self.dd = None

        def t_draw(self):
            super().t_draw()
            if len([1 for e in self.hp_sys.effects if type(e) is effects.Frozen]) and random.randint(0, 100) < self.phase * 18 + 7:
                self.hp_sys.effects = [e for e in self.hp_sys.effects if type(e) is not effects.Frozen]

        def on_update(self):
            super().on_update()
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] += .1
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] += .1
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] += .1
            self.hp_sys.defenses[damages.DamageTypes.ARCANE] += .1
            self.hp_sys.defenses[damages.DamageTypes.OCTAVE] += .1
            self.hp_sys.defenses[damages.DamageTypes.PACIFY] += .1
            self.hp_sys.defenses[damages.DamageTypes.HALLOW] += .1
            self.obj.TOUCHING_DAMAGE += 2
            self.tick += 1
            if self.hp_sys.hp < self.hp_sys.max_hp * .85 and self.phase == 0:
                self.phase = 1
                dragon = Entities.Eonar((self.obj.pos[0] + random.randint(-1000, 1000),
                                         self.obj.pos[1] + random.randint(-1000, 1000)))
                dragon.NAME = 'Crush of Mind: ???'
                dragon.hp_sys(op='config', immune=True)
                dragon.obj.TOUCHING_DAMAGE = 1600
                self.dd = dragon
                game.get_game().entities.append(dragon)
                self.hp_sys.heal(self.hp_sys.max_hp)
            elif self.hp_sys.hp < self.hp_sys.max_hp * .6 and self.phase == 1:
                self.phase = 2
                self.dd.hp_sys.hp = 0
            if self.phase == 0:
                if self.tick % 28 == 0:
                    game.get_game().entities.append(Entities.BurstBall((self.obj.pos[0] + random.randint(-1000, 1000),
                                                                        self.obj.pos[1] + random.randint(-1000, 1000))))
            elif self.phase == 1:
                if self.tick % 44 == 0:
                    game.get_game().entities.append(Entities.BurstBall((self.obj.pos[0] + random.randint(-1000, 1000),
                                                                        self.obj.pos[1] + random.randint(-1000, 1000))))
                elif self.tick % 44 == 22:
                    game.get_game().entities.append(Entities.CrushBall((self.obj.pos[0] + random.randint(-1000, 1000),
                                                                        self.obj.pos[1] + random.randint(-1000, 1000))))
            else:
                if self.tick % 54 == 0:
                    for _ in range(6):
                        game.get_game().entities.append(Entities.BurstBall((self.obj.pos[0] + random.randint(-1000, 1000),
                                                                            self.obj.pos[1] + random.randint(-1000, 1000))))
                        game.get_game().entities.append(Entities.CrushBall((self.obj.pos[0] + random.randint(-1000, 1000),
                                                                            self.obj.pos[1] + random.randint(-1000, 1000))))



    class OmegaFlowery(Entity):
        NAME = 'Omega Flowey'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([
            IndividualLoot('the_final_soul', 1, 10, 20),
            IndividualLoot('the_final_ingot', 1, 25, 40),
            SelectionLoot([('murders_knife', 1, 1), ('savior', 1, 1)], 2, 2),
        ])
        IS_MENACE = True
        PHASE_SEGMENTS = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_omega_flowery'], BuildingAI, 10 ** 9 * 4)
            self.obj.MASS = 10 ** 8
            self.obj.TOUCHING_DAMAGE = 0
            self.obj.IS_OBJECT = False
            self.petals = []
            # self.petals = [Entities.Entity(self.obj.pos, game.get_game().graphics['entity_petal'], BuildingAI,
            #                                hp_sys=self.hp_sys) for _ in range(6)]
            for i, p in enumerate(self.petals):
                p.set_rotation(i * 60)
                p.DISPLAY_MODE = 1
                p.NAME = 'Petal'
                p.VITAL = True
                p.obj.IS_OBJECT = False
                game.get_game().entities.append(p)
            self.tick = 0
            self.rt = 0
            self.phase = 0
            self.play_sound('Your_Best_Nightmare_music_intro')
            self.c_cnt = 0
            self.state = 0
            self.a_tick = 0
            self.a_state = 0
            self.a_interval = 100
            game.get_game().player.hp_sys.effect(effects.Polluted(10 ** 9, 1))

        def t_draw(self):
            if not self.phase:
                super().t_draw()
            elif self.phase < 13 and not self.state:
                super().t_draw()
            game.get_game().entities = [e for e in game.get_game().entities if e.VITAL or e.IS_MENACE or not e.obj.IS_OBJECT]
            game.get_game().drop_items = []
            px, py = game.get_game().player.obj.pos
            px -= self.obj.pos[0]
            py -= self.obj.pos[1]
            if vector.distance(px, py) > 1200:
                px *= 1200 / vector.distance(px, py)
                py *= 1200 / vector.distance(px, py)
            game.get_game().player.obj.pos << (px + self.obj.pos[0], py + self.obj.pos[1])
            col = (200, 255, 127)
            if self.phase:
                if self.state == -1:
                    col = (255, 0, 0)
                elif self.state == 0:
                    pass
                else:
                    cols = {2: (0, 255, 255), 4: (255, 127, 0), 6: (0, 0, 255), 8: (255, 0, 255), 10: (0, 255, 0),
                            12: (255, 255, 0)}
                    if self.phase in cols.keys():
                        col = cols[self.phase]
            pg.draw.circle(game.get_game().displayer.canvas, col, position.displayed_position(self.obj.pos),
                           1200 / game.get_game().player.get_screen_scale())
            if self.phase:
                game.get_game().player.scale = 3
                if self.phase >= 13:
                    self.rt += 25
                    self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = 3
                    self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 3
                    self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 3
                    self.hp_sys.resistances[damages.DamageTypes.ARCANE] = 3
                    self.hp_sys.resistances[damages.DamageTypes.THINKING] = 10
                    self.NAME = 'Finale'
                    self.hp_sys(op='config', maximum_damage=self.hp_sys.hp - 1)
                elif self.state == -1:
                    txt = game.get_game().displayer.font.render(styles.text('WARNING!'), True, (255, 0, 0), (0, 0, 0))
                    tr = txt.get_rect(center=(game.get_game().displayer.SCREEN_WIDTH // 2, 100))
                    game.get_game().displayer.canvas.blit(txt, tr)
                    self.NAME = 'WARNING!'
                elif self.state == 0:
                    self.rt += 20
                    self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = 7
                    self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 7
                    self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 7
                    self.hp_sys.resistances[damages.DamageTypes.ARCANE] = 7
                    self.hp_sys.resistances[damages.DamageTypes.THINKING] = 32
                    self.NAME = 'Omega Flowey'
                else:
                    self.rt -= 5
                    self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = 0
                    self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 0
                    self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 0
                    self.hp_sys.resistances[damages.DamageTypes.ARCANE] = 0
                    self.hp_sys.resistances[damages.DamageTypes.THINKING] = 1
                    self.NAME = '???'
            else:
                pass
            if (self.phase % 2 == 0 or self.state < 0) and self.phase < 13:
                self.a_state = 0
            elif self.a_tick > self.a_interval:
                self.a_tick = 0
                if self.phase == 1:
                    self.a_state = random.randint(1, 2)
                elif self.phase == 3:
                    self.a_state = random.randint(1, 4)
                elif self.phase == 5:
                    self.a_state = random.randint(2, 6)
                elif self.phase == 7:
                    self.a_state = random.randint(5, 7)
                elif self.phase == 9:
                    self.a_state = random.randint(1, 7)
                elif self.phase == 11:
                    self.a_state = random.randint(1, 9)
                elif self.phase == 13:
                    self.a_state = 2
                elif self.phase == 14:
                    self.a_state = random.randint(1, 9)
                elif self.phase == 15:
                    self.a_state = random.randint(1, 9)
            self.a_tick += 1
            if self.a_state == 0:
                pass
            elif self.a_state == 1:
                if self.a_tick % 30 == 0:
                    for _ in range(random.randint(3, 5)):
                        px, py = game.get_game().player.obj.pos
                        rot = random.randint(0, 359)
                        vx, vy = vector.rotation_coordinate(rot)
                        game.get_game().entities.append(Entities.FriendlyBullet((px + vx * 2000, py + vy * 2000), 180 + rot))
            elif self.a_state == 2:
                if self.a_tick % 5 == 0:
                    for _ in range(random.randint(1, 3)):
                        game.get_game().entities.append(Entities.FriendlyBullet((self.obj.pos[0] - 3000, self.obj.pos[1] + random.randint(-2000, 2000)),
                                                                                vector.coordinate_rotation(1, 0)))
                    for _ in range(random.randint(1, 3)):
                        game.get_game().entities.append(Entities.FriendlyBullet((self.obj.pos[0] + 3000, self.obj.pos[1] + random.randint(-2000, 2000)),
                                                                                vector.coordinate_rotation(-1, 0)))
            elif self.a_state == 3:
                if self.a_tick % 20 == 0:
                    for _ in range(random.randint(5, 8)):
                        game.get_game().entities.append(Entities.Bomb((self.obj.pos[0] + random.randint(-2000, 2000), self.obj.pos[1] - 2000),
                                                                       vector.coordinate_rotation(0, 1)))
            elif self.a_state == 4:
                if self.a_tick % 15 == 0:
                    ar = random.choice([10, 9, 8, 6, 5, 4, 3])
                    ang = (ar - 2) * 180 / ar / 2
                    for i in range(ar):
                        ax, ay = vector.rotation_coordinate(i * 360 / ar)
                        game.get_game().entities.append(Entities.FriendlyBullet((self.obj.pos[0] + ax * 500, self.obj.pos[1] + ay * 500),
                                                                               i * 360 / ar + 180 + ang))
                if self.a_tick % 5 == 0:
                    game.get_game().entities.append(Entities.Bomb((game.get_game().player.obj.pos[0], game.get_game().player.obj.pos[1] - 3000),
                                                                  vector.coordinate_rotation(0, 1)))
            elif self.a_state == 5:
                if self.a_tick % 5 == 0:
                    game.get_game().entities.append(Entities.Flower(game.get_game().player.obj.pos))
                if self.a_tick % 30 == 0:
                    for _ in range(random.randint(2, 3)):
                        game.get_game().entities.append(Entities.Bomb((self.obj.pos[0] + random.randint(-2000, 2000), self.obj.pos[1] - 2000),
                                                                       vector.coordinate_rotation(0, 1)))
            elif self.a_state == 6:
                if self.a_tick % 20 == 0:
                    for _ in range(random.randint(2, 3)):
                        px, py = game.get_game().player.obj.pos
                        rot = random.randint(0, 359)
                        vx, vy = vector.rotation_coordinate(rot)
                        game.get_game().entities.append(Entities.FriendlyBullet((px + vx * 2000, py + vy * 2000), 180 + rot))
                if self.a_tick % 5 == 0:
                    game.get_game().entities.append(Entities.Flower((self.obj.pos[0] + random.randint(-2000, 2000),
                                                                     self.obj.pos[1] + random.randint(-2000, 2000))))
            elif self.a_state == 7:
                if self.a_tick % 40 == 0:
                    for _ in range(random.randint(2, 4)):
                        px, py = game.get_game().player.obj.pos
                        rot = random.randint(0, 359)
                        vx, vy = vector.rotation_coordinate(rot)
                        game.get_game().entities.append(Entities.FriendlyBullet((px + vx * 2000, py + vy * 2000), 180 + rot))
                elif self.a_tick % 40 == 20:
                    game.get_game().entities.append(Entities.Bomb((game.get_game().player.obj.pos[0], game.get_game().player.obj.pos[1] - 3000),
                                                                  vector.coordinate_rotation(0, 1)))
                elif self.a_tick % 5 == 0:
                    for _ in range(random.randint(0, 2)):
                        game.get_game().entities.append(Entities.FriendlyBullet((self.obj.pos[0] - 3000, self.obj.pos[1] + random.randint(-2000, 2000)),
                                                                                vector.coordinate_rotation(1, 0)))
                    for _ in range(random.randint(0, 2)):
                        game.get_game().entities.append(Entities.FriendlyBullet((self.obj.pos[0] + 3000, self.obj.pos[1] + random.randint(-2000, 2000)),
                                                                                vector.coordinate_rotation(-1, 0)))
            elif self.a_state == 8:
                if self.a_tick % 50 == 1:
                    ax, ay = vector.rotation_coordinate(random.randint(0, 359))
                    dt = random.randint(1200, 2000)
                    game.get_game().entities.append(Entities.FlyAttractor((self.obj.pos[0] + ax * dt, self.obj.pos[1] + ay * dt)))
            elif self.a_state == 9:
                if self.a_tick % 72 == 1:
                    ax, ay = vector.rotation_coordinate(random.randint(0, 359))
                    dt = random.randint(1200, 2000)
                    game.get_game().entities.append(Entities.FlyAttractor((self.obj.pos[0] + ax * dt, self.obj.pos[1] + ay * dt)))
                if self.a_tick % 5 == 0:
                    for _ in range(random.randint(0, 1)):
                        game.get_game().entities.append(Entities.FriendlyBullet((self.obj.pos[0] - 3000, self.obj.pos[1] + random.randint(-2000, 2000)),
                                                                                vector.coordinate_rotation(1, 0)))
                    for _ in range(random.randint(0, 1)):
                        game.get_game().entities.append(Entities.FriendlyBullet((self.obj.pos[0] + 3000, self.obj.pos[1] + random.randint(-2000, 2000)),
                                                                                    vector.coordinate_rotation(-1, 0)))
            if self.phase == 0:
                if self.is_playing('Your_Best_Nightmare_music_intro'):
                    game.get_game().player.scale = self.tick / 200 + 1
                elif self.tick >= 0:
                    self.play_sound('Your_Best_Nightmare_music_Flowey_laugh')
                    self.tick = -100000
                elif self.tick < 0 and not self.is_playing('Your_Best_Nightmare_music_Flowey_laugh'):
                    self.phase = 1
                    self.play_sound('Your_Best_Nightmare_music_part_1')
                    self.state = 0
                    self.c_cnt = 0
            elif self.hp_sys.hp < self.hp_sys.max_hp * 0.9 and self.phase == 1:
                self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = 0
                self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 0
                self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 0
                self.hp_sys.resistances[damages.DamageTypes.ARCANE] = 0
                self.hp_sys.resistances[damages.DamageTypes.THINKING] = 0
                if not self.c_cnt and not self.is_playing('Your_Best_Nightmare_music_part_1'):
                    self.c_cnt = 1
                    self.play_sound('Your_Best_Nightmare_music_alarm')
                    self.state = -1
                elif self.c_cnt:
                    if not self.is_playing('Your_Best_Nightmare_music_alarm'):
                        self.phase = 2
                        self.play_sound('Your_Best_Nightmare_music_SOUL_1')
                        self.tick = 0
                        self.c_cnt = 0
                        self.state = 1
                        for r in range(0, 360, 120):
                            game.get_game().entities.append(Entities.Knife(self.obj.pos, r, 0))
                            game.get_game().entities.append(Entities.Knife(self.obj.pos, r, 10 * math.pi))
                        for r in range(60, 360, 120):
                            game.get_game().entities.append(Entities.Knife(self.obj.pos, r, 5 * math.pi))
                            game.get_game().entities.append(Entities.Knife(self.obj.pos, r, 15 * math.pi))
            elif self.phase == 2 and not self.is_playing('Your_Best_Nightmare_music_SOUL_1'):
                self.play_sound('Your_Best_Nightmare_music_part_2')
                self.phase = 3
                self.state = 0
                for e in game.get_game().entities:
                    if type(e) is Entities.Knife:
                        e.hp_sys.hp = 0
            elif self.hp_sys.hp < self.hp_sys.max_hp * 0.8 and self.phase == 3:
                self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = 0
                self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 0
                self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 0
                self.hp_sys.resistances[damages.DamageTypes.ARCANE] = 0
                self.hp_sys.resistances[damages.DamageTypes.THINKING] = 0
                if not self.c_cnt and not self.is_playing('Your_Best_Nightmare_music_part_2'):
                    self.c_cnt = 1
                    self.play_sound('Your_Best_Nightmare_music_alarm')
                    self.state = -1
                elif self.c_cnt:
                    if not self.is_playing('Your_Best_Nightmare_music_alarm'):
                        self.phase = 4
                        self.play_sound('Your_Best_Nightmare_music_SOUL_2')
                        self.tick = 0
                        self.c_cnt = 0
                        self.state = 1
                        for i in range(30):
                            game.get_game().entities.append(Entities.Gloves(self.obj.pos, i * 12, math.pi * 40 * i / 15))
            elif self.phase == 4 and not self.is_playing('Your_Best_Nightmare_music_SOUL_2'):
                self.play_sound('Your_Best_Nightmare_music_part_3')
                self.phase = 5
                self.state = 0
                for e in game.get_game().entities:
                    if type(e) is Entities.Gloves:
                        e.hp_sys.hp = 0
            elif self.hp_sys.hp < self.hp_sys.max_hp * 0.7 and self.phase == 5:
                self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = 0
                self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 0
                self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 0
                self.hp_sys.resistances[damages.DamageTypes.ARCANE] = 0
                self.hp_sys.resistances[damages.DamageTypes.THINKING] = 0
                if not self.c_cnt and not self.is_playing('Your_Best_Nightmare_music_part_3'):
                    self.c_cnt = 1
                    self.play_sound('Your_Best_Nightmare_music_alarm')
                    self.state = -1
                elif self.c_cnt:
                    if not self.is_playing('Your_Best_Nightmare_music_alarm'):
                        self.phase = 6
                        self.play_sound('Your_Best_Nightmare_music_SOUL_3')
                        self.tick = 0
                        self.c_cnt = 0
                        self.state = 1
                        for i in range(15):
                            game.get_game().entities.append(Entities.Shoe(self.obj.pos, i * 24))
            elif self.phase == 6 and not self.is_playing('Your_Best_Nightmare_music_SOUL_3'):
                self.play_sound('Your_Best_Nightmare_music_part_2')
                self.phase = 7
                self.state = 0
                for e in game.get_game().entities:
                    if type(e) is Entities.Shoe:
                        e.hp_sys.hp = 0
            elif self.hp_sys.hp < self.hp_sys.max_hp * 0.6 and self.phase == 7:
                self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = 0
                self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 0
                self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 0
                self.hp_sys.resistances[damages.DamageTypes.ARCANE] = 0
                self.hp_sys.resistances[damages.DamageTypes.THINKING] = 0
                if not self.c_cnt and not self.is_playing('Your_Best_Nightmare_music_part_2'):
                    self.c_cnt = 1
                    self.play_sound('Your_Best_Nightmare_music_alarm')
                    self.state = -1
                elif self.c_cnt:
                    if not self.is_playing('Your_Best_Nightmare_music_alarm'):
                        self.phase = 8
                        self.play_sound('Your_Best_Nightmare_music_SOUL_4')
                        self.tick = 0
                        self.c_cnt = 0
                        self.state = 1
                        for i in range(36):
                            game.get_game().entities.append(Entities.AlphaBet(self.obj.pos, i * 10,
                                                                              (i % 6) / 6 * 2 * math.pi, i))
            elif self.phase == 8 and not self.is_playing('Your_Best_Nightmare_music_SOUL_4'):
                self.play_sound('Your_Best_Nightmare_music_part_1')
                self.phase = 9
                self.state = 0
                for e in game.get_game().entities:
                    if type(e) is Entities.AlphaBet:
                        e.hp_sys.hp = 0
            elif self.hp_sys.hp < self.hp_sys.max_hp * 0.5 and self.phase == 9:
                self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = 0
                self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 0
                self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 0
                self.hp_sys.resistances[damages.DamageTypes.ARCANE] = 0
                self.hp_sys.resistances[damages.DamageTypes.THINKING] = 0
                if not self.c_cnt and not self.is_playing('Your_Best_Nightmare_music_part_1'):
                    self.c_cnt = 1
                    self.play_sound('Your_Best_Nightmare_music_alarm')
                    self.state = -1
                elif self.c_cnt:
                    if not self.is_playing('Your_Best_Nightmare_music_alarm'):
                        self.phase = 10
                        self.play_sound('Your_Best_Nightmare_music_SOUL_5')
                        self.tick = 0
                        self.c_cnt = 0
                        self.state = 1
                        for i in range(40):
                            game.get_game().entities.append(Entities.Pan(self.obj.pos, i * 9))
            elif self.phase == 10 and not self.is_playing('Your_Best_Nightmare_music_SOUL_5'):
                self.play_sound('Your_Best_Nightmare_music_part_3')
                self.phase = 11
                self.state = 0
                for e in game.get_game().entities:
                    if type(e) is Entities.Pan:
                        e.hp_sys.hp = 0
            elif self.hp_sys.hp < self.hp_sys.max_hp * 0.4 and self.phase == 11:
                self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = 0
                self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 0
                self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 0
                self.hp_sys.resistances[damages.DamageTypes.ARCANE] = 0
                self.hp_sys.resistances[damages.DamageTypes.THINKING] = 0
                if not self.c_cnt and not self.is_playing('Your_Best_Nightmare_music_part_3'):
                    self.c_cnt = 1
                    self.play_sound('Your_Best_Nightmare_music_alarm')
                    self.state = -1
                elif self.c_cnt:
                    if not self.is_playing('Your_Best_Nightmare_music_alarm'):
                        self.phase = 12
                        self.play_sound('Your_Best_Nightmare_music_SOUL_6')
                        self.tick = 0
                        self.c_cnt = 0
                        self.state = 1
                        for i in range(36):
                            game.get_game().entities.append(Entities.Bullet(self.obj.pos, i * 10,
                                                                              (i % 4) / 4 * 2 * math.pi))
            elif self.phase == 12 and not self.is_playing('Your_Best_Nightmare_music_SOUL_6'):
                self.state = 2
                self.phase = 13
                for e in game.get_game().entities:
                    if type(e) is Entities.Bullet:
                        e.hp_sys.hp = 0
                self.play_sound('Finale_music_1')
            elif self.phase == 13 and not self.is_playing('Finale_music_1'):
                self.state = 3
                self.phase = 14
                self.play_sound('Finale_music_2')
                self.a_interval = 50
            elif self.phase == 14 and not self.is_playing('Finale_music_2'):
                self.state = 4
                self.phase = 15
                self.play_sound('Finale_music_3')
                self.a_interval = 40
            elif self.phase == 15 and not self.is_playing('Finale_music_3') and self.hp_sys.hp < 10:
                self.phase = 16
                self.tick = 0
            elif self.phase == 16 and self.tick > 100:
                self.hp_sys.hp = 0
                game.get_game().projectiles = []
                game.get_game().player.hp_sys.effects = []
            self.tick += 1
            if self.phase < 16:
                self.hp_sys.hp = max(self.hp_sys.hp, 1)
            """
            for i in range(6):
                self.petals[i].set_rotation(self.rt + i * 60)
                ax, ay = vector.rotation_coordinate(45 - self.rt - i * 60)
                self.petals[i].obj.pos << (self.obj.pos[0] + ax * 1536, self.obj.pos[1] + ay * 1536)"""

    class FriendlyBullet(Entity):
        NAME = 'Friendly Bullet'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])
        VITAL = True

        def __init__(self, pos, rot, follow_entity=None):
            super().__init__(pos, game.get_game().graphics['entity_friendly_bullet'], FastBulletAI, 10 ** 9)
            self.obj.MASS = 1000
            self.obj.rot = rot
            self.obj.speed = 7200
            self.tick = 0
            if follow_entity is not None:
                self.ax = self.obj.pos[0] - follow_entity.obj.pos[0]
                self.ay = self.obj.pos[1] - follow_entity.obj.pos[1]
                self.arot = rot + follow_entity.rot
                self.follow_entity = follow_entity
            else:
                self.ax, self.ay, self.arot = 0, 0, 0
                self.follow_entity = None

        def on_update(self):
            super().on_update()
            self.tick += 1
            if self.tick % 3 == 0:
                self.set_rotation(self.rot + 77)
            if self.tick < 10:
                if self.follow_entity is not None:
                    self.obj.pos << (self.follow_entity.obj.pos[0] + self.ax, self.follow_entity.obj.pos[1] + self.ay)
                    self.obj.rot = -self.follow_entity.rot + self.arot
                ax, ay = vector.rotation_coordinate(self.obj.rot)
                draw.line(game.get_game().displayer.canvas, (255, 0, 0),
                             position.displayed_position(self.obj.pos),
                             position.displayed_position((self.obj.pos[0] + ax * 3000, self.obj.pos[1] + ay * 3000)), 3)
            else:
                self.damage()
                self.hp_sys.hp -= 25 * 10 ** 6

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 80:
                game.get_game().player.hp_sys.damage(1600, damages.DamageTypes.MAGICAL)
                self.hp_sys.hp = 10 ** 8

    class Knife(Entity):
        NAME = '?????'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])
        VITAL = True

        def __init__(self, pos, rot, st=0.0):
            super().__init__(pos, game.get_game().graphics['entity_knife'], BuildingAI, 5 * 10 ** 8)
            self.obj.MASS = 1000
            self.obj.rot = rot
            self.tick = st
            self.s_pos = pos
            self.rt = rot
            self.set_rotation(rot + 180)
            self.obj.TOUCHING_DAMAGE = 1000

        def on_update(self):
            self.rt += 2
            self.tick += 1
            self.set_rotation(self.rt + 180)
            ax, ay = vector.rotation_coordinate(self.rt)
            self.obj.pos << (self.s_pos[0] + ax * (2000 + 2500 * math.sin(self.tick / 20)),
                            self.s_pos[1] + ay * (2000 + 2500 * math.sin(self.tick / 20)))

    class Bomb(Entity):
        NAME = 'Friendly Bomb'
        DISPLAY_MODE = 3
        LOOT_TABLE = LootTable([])
        VITAL = True

        def __init__(self, pos, rot, follow_entity=None):
            super().__init__(pos, game.get_game().graphics['entity_bomb'], FastBulletAI, 10 ** 9)
            self.obj.MASS = 1000
            self.obj.rot = rot
            self.obj.speed = 7200
            self.tick = 0
            self.sp = pos
            if follow_entity is not None:
                self.ax = self.obj.pos[0] - follow_entity.obj.pos[0]
                self.ay = self.obj.pos[1] - follow_entity.obj.pos[1]
                self.arot = rot + follow_entity.rot
                self.follow_entity = follow_entity
            else:
                self.ax, self.ay, self.arot = 0, 0, 0
                self.follow_entity = None

        def on_update(self):
            super().on_update()
            self.tick += 1
            if self.tick < 10:
                if self.follow_entity is not None:
                    self.obj.pos << (self.follow_entity.obj.pos[0] + self.ax, self.follow_entity.obj.pos[1] + self.ay)
                    self.obj.rot = -self.follow_entity.rot + self.arot
                ax, ay = vector.rotation_coordinate(self.obj.rot)
                draw.line(game.get_game().displayer.canvas, (255, 0, 0),
                             position.displayed_position(self.obj.pos),
                             position.displayed_position((self.obj.pos[0] + ax * 3000, self.obj.pos[1] + ay * 3000)), 3)

            else:
                super().update()
                self.damage()
                self.hp_sys.hp -= 25 * 10 ** 6

        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 80:
                game.get_game().player.hp_sys.damage(1200, damages.DamageTypes.MAGICAL)
                self.hp_sys.hp = 0
            if vector.distance(self.sp[0] - self.obj.pos[0], self.sp[1] - self.obj.pos[1]) > 3000:
                game.get_game().displayer.effect(fc.p_fade_circle(*position.displayed_position(self.obj.pos), col=(255, 0, 0),
                                                                  sp=80, t=20))
                if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                                   self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 1600:
                    game.get_game().player.hp_sys.damage(2200, damages.DamageTypes.MAGICAL)
                self.hp_sys.hp = 0

    class Gloves(Entity):
        NAME = '??????'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])
        VITAL = True

        def __init__(self, pos, rot, st=0.0):
            super().__init__(pos, game.get_game().graphics['entity_gloves'], BuildingAI, 5 * 10 ** 8)
            self.obj.MASS = 1000
            self.obj.rot = rot
            self.tick = st
            self.s_pos = pos
            self.rt = rot
            self.set_rotation(rot + 180)
            self.obj.TOUCHING_DAMAGE = 1000

        def on_update(self):
            self.tick += 1
            self.set_rotation(self.rt + 180)
            ax, ay = vector.rotation_coordinate(self.rt)
            self.obj.pos << (self.s_pos[0] + ax * (2000 * math.sin(self.tick / 40) - 500),
                            self.s_pos[1] + ay * (2000 * math.sin(self.tick / 40) - 500))

    class Flower(Entity):
        NAME = 'Smiling Flower'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])
        VITAL = True

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['entity_flower'], BuildingAI, 4 * 10 ** 8)
            self.obj.MASS = 1000
            self.tick = 0
            self.set_rotation(random.randint(0, 360))
            self.obj.IS_OBJECT = False

        def on_update(self):
            self.tick += 1
            super().update()
            if self.tick < 10:
                self.set_rotation(self.rot + 40)
            elif self.tick == 10:
                self.set_rotation(0)
            elif self.tick < 50:
                self.hp_sys.hp -= 10 ** 7
                self.damage()
            else:
                self.hp_sys.hp = 0
        def damage(self):
            if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                               self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 400:
                game.get_game().player.hp_sys.damage(900, damages.DamageTypes.MAGICAL)

    class Shoe(Entity):
        NAME = '????'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])
        VITAL = True

        def __init__(self, pos, rot, st=0.0):
            super().__init__(pos, game.get_game().graphics['entity_shoe'], BuildingAI, 5 * 10 ** 8)
            self.obj.MASS = 1000
            self.obj.rot = rot
            self.tick = st
            self.s_pos = pos
            self.rt = rot
            self.dt = 2000
            self.set_rotation(rot + 180)
            self.obj.TOUCHING_DAMAGE = 1000

        def on_update(self):
            self.rt += 6
            self.set_rotation(self.rt + 180)
            ax, ay = vector.rotation_coordinate(self.rt)
            self.obj.pos << (self.s_pos[0] + ax * self.dt,
                            self.s_pos[1] + ay * self.dt)
            if not self.tick and random.randint(0, 10) == 3:
                self.tick = 1
            if self.tick:
                self.tick += 1
                self.dt = -500 + 2500 * (self.tick - 50) ** 2 / 2500
                if self.tick > 100:
                    self.tick = 0

    class AlphaBet(Entity):
        NAME = '????????'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])
        VITAL = True

        def __init__(self, pos, rot, st=0.0, no=0):
            super().__init__(pos, pg.transform.scale_by(game.get_game().displayer.font.render(chr(65 + no) if no < 26 else chr(48 + no - 26), 10), True, (255, 255, 255), (0, 0, 0)),
                             BuildingAI, 5 * 10 ** 8)
            self.obj.MASS = 1000
            self.obj.rot = rot
            self.tick = st
            self.s_pos = pos
            self.rt = rot
            self.set_rotation(rot + 180)
            self.obj.TOUCHING_DAMAGE = 1000

        def on_update(self):
            self.rt += 2
            self.tick += 1
            self.set_rotation(self.rt + 180)
            ax, ay = vector.rotation_coordinate(self.rt)
            self.obj.pos << (self.s_pos[0] + ax * (1000 + 3000 * math.sin(self.tick / 20)),
                            self.s_pos[1] + ay * (1000 + 3000 * math.sin(self.tick / 20)))

    class Fly(Entity):
        NAME = 'Fly'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])
        VITAL = True

        def __init__(self, pos, rot):
            super().__init__(pos, game.get_game().graphics['entity_fly'], FastBulletAI, 4 * 10 ** 8)
            self.obj.MASS = 1000
            self.obj.rot = rot
            self.obj.speed = 8800
            self.tick = 0
            self.obj.TOUCHING_DAMAGE = 960

        def on_update(self):
            self.tick += 1
            super().on_update()
            self.hp_sys.hp -= 25 * 10 ** 6
            if self.tick < 5:
                ax, ay = vector.rotation_coordinate(self.obj.rot)
                draw.line(game.get_game().displayer.canvas, (255, 0, 0),
                             position.displayed_position(self.obj.pos),
                             position.displayed_position((self.obj.pos[0] + ax * 3000, self.obj.pos[1] + ay * 3000)), 3)
            else:
                self.hp_sys.hp -= 25 * 10 ** 6

    class FlyAttractor(Entity):
        NAME = 'Fly Attractor'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])
        VITAL = True

        def __init__(self, pos):
            super().__init__(pos, game.get_game().graphics['item_null'], BuildingAI, 1)
            px, py = game.get_game().player.obj.pos
            px -= self.obj.pos[0]
            py -= self.obj.pos[1]
            rt = vector.coordinate_rotation(px, py)
            for i in range(80):
                dt = 2000 + i * 20
                art = rt + random.randint(-10, 10)
                ax, ay = vector.rotation_coordinate(art)
                game.get_game().entities.append(Entities.Fly((self.obj.pos[0] + ax * dt, self.obj.pos[1] + ay * dt), art + 180))

        def on_update(self):
            self.hp_sys.hp = 0

    class Pan(Entity):
        NAME = '???'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])
        VITAL = True

        def __init__(self, pos, rot, st=0.0):
            super().__init__(pos, game.get_game().graphics['entity_pan'], BuildingAI, 5 * 10 ** 8)
            self.obj.MASS = 1000
            self.obj.rot = rot
            self.tick = st
            self.s_pos = pos
            self.rt = rot
            self.dt = 5000
            self.set_rotation(rot + 180)
            self.obj.TOUCHING_DAMAGE = 1000

        def on_update(self):
            self.rt += 10
            self.set_rotation(self.rt + 180)
            ax, ay = vector.rotation_coordinate(self.rt)
            self.obj.pos << (self.s_pos[0] + ax * self.dt,
                            self.s_pos[1] + ay * self.dt)
            if not self.tick and random.randint(0, 10) == 3:
                self.tick = 1
            if self.tick:
                self.tick += 1
                self.dt = -2000 + 5000 * (self.tick - 40) ** 2 / 1600
                if self.tick > 80:
                    self.tick = 0

    class Bullet(Entity):
        NAME = '??????'
        DISPLAY_MODE = 1
        LOOT_TABLE = LootTable([])
        VITAL = True

        def __init__(self, pos, rot, st=0.0):
            super().__init__(pos, game.get_game().graphics['entity_bullet'], BuildingAI, 5 * 10 ** 8)
            self.obj.MASS = 1000
            self.obj.rot = rot
            self.tick = st
            self.s_pos = pos
            self.rt = rot
            self.set_rotation(rot + 180)
            self.obj.TOUCHING_DAMAGE = 1000

        def on_update(self):
            self.tick += 1
            self.set_rotation(-self.obj.velocity.get_net_rotation())
            ax, ay = vector.rotation_coordinate(self.rt)
            self.obj.pos << (self.s_pos[0] + ax * (3000 * math.sin(self.tick / 40) - 1000),
                            self.s_pos[1] + ay * (3000 * math.sin(self.tick / 40) - 1000))


def entity_spawn(entity: type(Entities.Entity), to_player_min=1500, to_player_max=2500, number_factor=0.5,
                 target_number=5, rate=0.5):
    game_obj = game.get_game()
    if (random.random() < (len([1 for e in game_obj.entities if type(e) is entity]) - int(target_number ** .45))
            * number_factor * rate / 200 - rate / 80 + 1
            + (len(game_obj.entities) - constants.ENTITY_NUMBER) / 16 * (not entity.IS_MENACE)):
        return
    player = game_obj.player
    dist = random.randint(to_player_min, to_player_max)
    r = random.random() * 2 * math.pi
    px, py = player.obj.pos[0] + dist * math.cos(r), player.obj.pos[1] + dist * math.sin(r)
    e = entity((px, py))
    if not e.is_suitable(game.get_game().get_biome((px // game.get_game().CHUNK_SIZE + 120,
                                                    py // game.get_game().CHUNK_SIZE + 120))):
        return
    game_obj.entities.append(e)
