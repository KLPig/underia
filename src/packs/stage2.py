from underia import entity, game
from values import damages
from resources import position
from physics import vector
import constants
from values import effects
from visual import draw

import random
import copy
import pygame as pg

class Entity(entity.Entities.Entity):
    pass

class WormEntity(entity.Entities.WormEntity):
    pass

class AbyssRuneShootAI(entity.AbyssRuneShootAI):
    pass

class SnowDrakeAI(entity.SnowdrakeAI):
    pass
# modified in basic.py

class MechanicEyeAI(entity.MechanicEyeAI):
    pass
# modified in basic.py

class MagmaKingFireballAI(entity.MagmaKingFireballAI):
    pass

class CleverRangedAI(entity.CleverRangedAI):
    pass

class LootTable(entity.LootTable):
    pass

class IndividualLoot(entity.IndividualLoot):
    pass

class SelectionLoot(entity.SelectionLoot):
    pass

@entity.AIs.entity_ai
class IceCapAI(entity.SlowMoverAI):
    MASS = 200
    TOUCHING_DAMAGE = 188
    SPEED = 1.5

@entity.AIs.entity_ai
class FaithlessEyeAI(entity.MonsterAI):
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
        self.tr = 0

    def on_update(self):
        if self.tick > 320:
            self.state = (self.state + 1) % (1 + constants.DIFFICULTY2)
            self.tick = 0
        self.tick += 1
        px, py = self.cur_target.pos if self.cur_target is not None else (0, 0)
        if self.state == 0:
            if self.tick % (100 - 20 * self.phase) < 30:
                self.apply_force(vector.Vector(self.tr,
                                               5000 + self.phase * (1000 + constants.DIFFICULTY * 400)))
            else:
                self.tr = (self.tr * 5 + vector.coordinate_rotation(px - self.pos[0], py - self.pos[1])) / 6
        elif self.state == 1:
            tar_x, tar_y = px + self.ax, py + self.ay
            self.apply_force(vector.Vector(vector.coordinate_rotation(tar_x - self.pos[0], tar_y - self.pos[1]),
                                           vector.distance(tar_x - self.pos[0], tar_y - self.pos[1]) * 5))
            self.rot = vector.coordinate_rotation(px - self.pos[0], py - self.pos[1])
        elif self.state == 2:
            self.rot += 15 + self.tick ** 2 // 1000
        else:
            if self.tick % 60 > 10:
                self.apply_force(vector.Vector(self.tr,
                                               8000 + self.phase * (1000 + constants.DIFFICULTY * 400)))
            else:
                self.tr = (self.tr * 5 + vector.coordinate_rotation(px - self.pos[0], py - self.pos[1])) / 6
                self.velocity *= 0


@entity.AIs.entity_ai
class DestroyerAI(entity.SlowMoverAI):
    MASS = 7200
    FRICTION = 0.9
    TOUCHING_DAMAGE = 440

    PREFER_DISTANCE = 1
    SIGHT_DISTANCE = 99999

    def __init__(self, pos):
        super().__init__(pos)
        self.tick = 0
        self.state = 0
        self.tr = 0

    def on_update(self):
        player = self.cur_target.pos if self.cur_target is not None else (0, 0)
        px = player[0] - self.pos[0]
        py = player[1] - self.pos[1]
        self.tick += 1
        if self.tick > 700:
            self.tick = 0
            self.state = (self.state + 1) % constants.DIFFICULTY2
        if self.state == 0:
            if self.tick % 300 < 240:
                self.apply_force(
                    vector.Vector(vector.coordinate_rotation(px, py), 8000 + min(vector.distance(px, py) * 9, 22000)))
                self.tr = self.velocity.get_net_rotation()
            else:
                self.apply_force(vector.Vector(self.tr, 40000))
        elif self.state == 1:
            self.apply_force(vector.Vector(self.tr, 2000))
        else:
            dr = vector.coordinate_rotation(px, py)
            self.apply_force(vector.Vector2D(dr + 55, 35000))

@entity.AIs.entity_ai
class SkyCubeFighterAI(entity.MonsterAI):
    MASS = 2000
    FRICTION = 0.9
    TOUCHING_DAMAGE = 288

    SIGHT_DISTANCE = 19999

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
                    self.apply_force(vector.Vector(self.rt, 70000))
                else:
                    self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 6000))
            if self.tick > 300:
                self.state = (self.state + 1) % 2
                self.tick = 0

@entity.AIs.entity_ai
class SkyCubeRangerAI(SkyCubeFighterAI):
    MASS = 2000
    TOUCHING_DAMAGE = 180
    SIGHT_DISTANCE = 19999

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), (vector.distance(px, py) - 1200) * 12))

@entity.AIs.entity_ai
class SkyCubeBlockerAI(SkyCubeFighterAI):
    MASS = 4000
    TOUCHING_DAMAGE = 140
    SIGHT_DISTANCE = 19999

    def on_update(self):
        player = self.cur_target
        if player is not None:
            px = player.pos[0] - self.pos[0]
            py = player.pos[1] - self.pos[1]
            self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 20000))

@entity.AIs.entity_ai
class TheCPUAI(entity.SlowMoverAI):
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
                self.pos = vector.Vector2D(px + player.pos[0], py + player.pos[1])
            self.tick += 1
            if self.state == 0:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 15000))
            else:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), vector.distance(px, py) * 40))

@entity.AIs.entity_ai
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
                self.pos = vector.Vector2D(px + player.pos[0], py + player.pos[1])
            self.tick += 1
            if self.state == 0:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 15000))
            elif self.state == 1:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), vector.distance(px, py) * 40))
            else:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py - 1000),
                                               vector.distance(px, py - 1000) * 80))

@entity.Entities.entity_type
class TruthlessCurse(Entity):
    NAME = 'Truthless Curse'
    DISPLAY_MODE = 3
    DMG = 360

    def __init__(self, pos, rot):
        super().__init__(pos, game.get_game().graphics['entity_truthless_curse'], AbyssRuneShootAI, 1500)
        self.obj.rot = rot
        self.obj.SPEED *= 3

    def on_update(self):
        super().on_update()
        self.set_rotation(self.rot)
        self.hp_sys.hp -= 15
        self.damage()

    def damage(self):
        if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                           self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
            game.get_game().player.hp_sys.damage(self.DMG, damages.DamageTypes.MAGICAL)
            game.get_game().player.hp_sys.effect(effects.TruthlessCurse(2, 30))
            game.get_game().player.hp_sys.enable_immune()
            self.hp_sys.hp = 0


@entity.Entities.entity_type
class FaithlessCurse(Entity):
    NAME = 'Faithless Curse'
    DISPLAY_MODE = 3
    DMG = 280

    def __init__(self, pos, rot):
        super().__init__(pos, game.get_game().graphics['entity_faithless_curse'], AbyssRuneShootAI, 1500)
        self.obj.rot = rot
        self.obj.SPEED *= 3

    def on_update(self):
        super().on_update()
        self.set_rotation(self.rot)
        self.hp_sys.hp -= 15
        self.damage()

    def damage(self):
        if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                           self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
            game.get_game().player.hp_sys.damage(self.DMG, damages.DamageTypes.MAGICAL)
            game.get_game().player.hp_sys.effect(effects.FaithlessCurse(20, 1))
            game.get_game().player.hp_sys.enable_immune()
            self.hp_sys.hp = 0

@entity.Entities.entity_type
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

@entity.Entities.entity_type
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

@entity.Entities.entity_type
class MechanicEye(Entity):
    NAME = 'Mechanic Eye'
    DISPLAY_MODE = 1
    LOOT_TABLE = LootTable([
        IndividualLoot('evil_ingot', 1, 5, 8),
        IndividualLoot('soul', 1, 5, 8),
        IndividualLoot('watcher_wand', .05, 5, 8),
    ])

    SOUND_HURT = 'metal'
    SOUND_DEATH = 'explosive'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity_mechanic_eye'], MechanicEyeAI, 2000)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 60
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 65
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 68
        self.tick = 0

    def on_update(self):
        super().on_update()
        self.set_rotation((self.rot * 4 - self.obj.velocity.get_net_rotation()) // 5)
        self.tick += 1
        if self.tick % 6 == 1:
            game.get_game().entities.append(entity.Entities.Lazer(self.obj.pos, -self.rot))

@entity.Entities.entity_type
class FaithlessEye(Entity):
    NAME = 'Faithless Eye'
    DISPLAY_MODE = 1
    IS_MENACE = True
    BOSS_NAME = 'The Non-Believer'
    LOOT_TABLE = LootTable([
        SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 1, 3),
        IndividualLoot('soul_of_integrity', 1, 10, 22),
        IndividualLoot('double_watcher_wand', 0.25, 1, 1),
    ])

    SOUND_SPAWN = 'boss'
    SOUND_HURT = 'metal'
    SOUND_DEATH = 'explosive'
    PHASE_SEGMENTS = [0.25, 0.65]

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity_faithless_eye'], FaithlessEyeAI, 48000)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 85
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 87
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 88
        self.obj.SPEED *= 1.1
        self.phase = 1

    def on_update(self):
        super().on_update()
        if self.phase == 1 and (self.hp_sys.hp < self.hp_sys.max_hp * 0.65 or not
        bool(len([1 for e in game.get_game().entities if type(e) is TruthlessEye]))):
            self.phase = 2
            self.obj.phase = 2
            self.img = game.get_game().graphics['entity_faithless_eye_phase2']
            if self.hp_sys.hp > self.hp_sys.max_hp * 0.65:
                self.PHASE_SEGMENTS = []
        if self.phase == 2 and self.hp_sys.hp < self.hp_sys.max_hp * 0.3:
            self.phase = 3
            self.obj.state = not self.obj.state
        if self.obj.state == 0:
            self.set_rotation((self.rot * 2 - self.obj.velocity.get_net_rotation()) // 3)
        elif self.obj.state == 2:
            self.set_rotation((self.rot * 2 - self.obj.rot) // 3)
            px, py = game.get_game().player.obj.pos
            if self.obj.tick % 2 == 0:
                game.get_game().entities.append(FaithlessCurse(self.obj.pos, self.rot))
        else:
            self.set_rotation((self.rot - self.obj.rot) // 2)
            if self.obj.tick % 50 == 1:
                px, py = game.get_game().player.obj.pos
                k = 1
                if self.obj.phase == 2:
                    k = 3
                if self.obj.phase == 3:
                    k = 5
                ps = k * 3
                dr = random.uniform(-ps, ps)
                for r in range(-k * 15, k * 15 + 1, 15 - (self.obj.phase == 3) * 5):
                    game.get_game().entities.append(FaithlessCurse(self.obj.pos,
                                                                            vector.coordinate_rotation(
                                                                                px - self.obj.pos[0],
                                                                                py - self.obj.pos[1]) + r + dr))

@entity.Entities.entity_type
class TruthlessEye(Entity):
    NAME = 'Truthless Eye'
    DISPLAY_MODE = 1
    IS_MENACE = True
    BOSS_NAME = 'The Dishonester'
    LOOT_TABLE = LootTable([
        SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 1, 3),
        IndividualLoot('soul_of_integrity', 1, 10, 22),
        IndividualLoot('double_watcher_wand', 0.25, 1, 1),
    ])

    SOUND_SPAWN = 'boss'
    SOUND_HURT = 'metal'
    SOUND_DEATH = 'explosive'
    PHASE_SEGMENTS = [0.25, 0.6]

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
        bool(len([1 for e in game.get_game().entities if type(e) is FaithlessEye]))):
            self.phase = 2
            self.obj.phase = 2
            self.img = game.get_game().graphics['entity_faithless_eye_phase2']
            if self.hp_sys.hp > self.hp_sys.max_hp * 0.6:
                self.PHASE_SEGMENTS = []
        if self.phase == 2 and self.hp_sys.hp < self.hp_sys.max_hp * 0.25:
            self.phase = 3
        if self.obj.state == 0:
            self.set_rotation((self.rot * 2 - self.obj.velocity.get_net_rotation()) // 3)
        elif self.obj.state == 2:
            self.set_rotation((self.rot * 2 - self.obj.rot) // 3)
            px, py = game.get_game().player.obj.pos
            if self.obj.tick % 2 == 0:
                game.get_game().entities.append(TruthlessCurse(self.obj.pos, self.rot))
        else:
            self.set_rotation((self.rot - self.obj.rot) // 2)
            if self.obj.tick % 60 == 0:
                px, py = game.get_game().player.obj.pos
                k = 0
                if self.obj.phase == 2:
                    k = 5
                if self.obj.phase == 3:
                    k = 7
                ps = k * 2
                dr = random.uniform(-ps, ps)
                for r in range(-k * 20, k * 20 + 1, 20 - (self.obj.phase == 3) * 10):
                    game.get_game().entities.append(TruthlessCurse(self.obj.pos,
                                                                            vector.coordinate_rotation(
                                                                                px - self.obj.pos[0],
                                                                                py - self.obj.pos[1]) + dr + r))

@entity.Entities.entity_type
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
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 140
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 148
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 136

    def on_update(self):
        super().on_update()
        self.set_rotation(self.rot + 15)

@entity.Entities.entity_type
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
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 88
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 88
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 88
        self.tick = 0

    def on_update(self):
        super().on_update()
        self.set_rotation(self.rot - 22)
        if self.tick % 80 < 30:
            if self.tick % 3 == 0:
                game.get_game().entities.append(entity.Entities.Lazer(self.obj.pos,
                                                               vector.coordinate_rotation(
                                                                   game.get_game().player.obj.pos[0] - self.obj.pos[0],
                                                                   game.get_game().player.obj.pos[1] - self.obj.pos[1])
                                                               ))
        elif self.tick % 12 == 0:
            for ar in range(0, 361, 20 - constants.DIFFICULTY // 2 * 5):
                game.get_game().entities.append(entity.Entities.Lazer(self.obj.pos,
                                                               vector.coordinate_rotation(
                                                                   game.get_game().player.obj.pos[0] - self.obj.pos[0],
                                                                   game.get_game().player.obj.pos[1] - self.obj.pos[1])
                                                               + ar))
        self.tick += 1

@entity.Entities.entity_type
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
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 266
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 272
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 270

    def on_update(self):
        super().on_update()
        self.set_rotation(self.rot + 5)

@entity.Entities.entity_type
class Destroyer(WormEntity):
    NAME = 'Destroyer'
    DISPLAY_MODE = 1
    IS_MENACE = True
    BOSS_NAME = 'The Metal Worm of Strength'
    LOOT_TABLE = LootTable([
        SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 1, 3),
        IndividualLoot('soul_of_bravery', 1, 10, 22),
        IndividualLoot('demolisher', .5, 1, 1),
    ])

    SOUND_SPAWN = 'boss'
    SOUND_HURT = 'metal'
    SOUND_DEATH = 'explosive'
    VITAL = True

    def __init__(self, pos):
        super().__init__(pos, 64, game.get_game().graphics['entity_destroyer_head'],
                         game.get_game().graphics['entity_destroyer_body'], DestroyerAI, 240000, body_length=120,
                         body_touching_damage=280)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 45
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 40
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 55
        self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 20
        self.obj.SPEED *= 2
        self.tick = 0
        self.ft = 0
        for b in self.body:
            setattr(b, 'ot', -1000)
            setattr(b, 'op', False)
            for r in b.hp_sys.resistances.resistances.keys():
                b.hp_sys.resistances.resistances[r] *= 1.5

    def on_update(self):
        self.tick += 1
        if self.obj.state == 1:
            if self.ft > 0:
                self.ft -= 1
            else:
                self.ft = 120 - constants.DIFFICULTY * 10 - constants.DIFFICULTY2 * 15
                for b in self.body:
                    setattr(b, 'orr', random.randint(0, 360))
        if self.obj.state == 2:
            self.ft = 0
            if self.tick % 70 == 0:
                bb = random.choices(self.body, k=len(self.body) - 3)
                for b in bb:
                    game.get_game().entities.append(entity.Entities.Lazer(b.obj.pos,
                                                                   vector.coordinate_rotation(
                                                                       *(game.get_game().player.obj.pos - b.obj.pos))
                                                                   ))
        for b in self.body:
            if random.randint(0,
                              300 - constants.DIFFICULTY * 15 - constants.DIFFICULTY2 * 20) == 0 and self.obj.state == 0:
                rot = vector.coordinate_rotation(game.get_game().player.obj.pos[0] - b.obj.pos[0],
                                                 game.get_game().player.obj.pos[1] - b.obj.pos[1])
                l = entity.Entities.Lazer(b.obj.pos, rot)
                l.obj.apply_force(vector.Vector(rot, 5000))
                game.get_game().entities.append(l)
                setattr(b, 'ot', self.tick)
            if self.obj.state == 1:
                if self.ft == 10:
                    l = entity.Entities.Lazer(b.obj.pos, b.orr)
                    l.DMG += 80
                    game.get_game().entities.append(l)
                    if constants.DIFFICULTY2 == 3:
                        l = entity.Entities.Lazer(b.obj.pos + vector.Vector2D(random.randint(0, 360), 50), b.orr)
                        l.DMG += 80
                        game.get_game().entities.append(l)

            op = self.tick - getattr(b, 'ot') <= 100
            if b != self.body[0]:
                if op:
                    b.img = game.get_game().graphics['entity_destroyer_body_open']
                else:
                    b.img = game.get_game().graphics['entity_destroyer_body']
            if op and not getattr(b, 'op'):
                for r in b.hp_sys.resistances.resistances.keys():
                    b.hp_sys.resistances.resistances[r] *= 1 / (.3 - constants.DIFFICULTY * .05)
            else:
                for r in b.hp_sys.resistances.resistances.keys():
                    b.hp_sys.resistances.resistances[r] *= .3 - constants.DIFFICULTY * .05
            setattr(b, 'op', op)
        super().on_update()

    def t_draw(self):
        for b in self.body:
            if self.obj.state == 1 and 'orr' in dir(b) and self.ft > 10:
                draw.line(game.get_game().displayer.canvas, (255, 0, 0), position.displayed_position(b.obj.pos),
                          position.displayed_position(b.obj.pos + vector.Vector2D(b.orr, 3000)), 2
                          )
        super().t_draw()

@entity.Entities.entity_type
class TheCPU(Entity):
    NAME = 'The CPU'
    DISPLAY_MODE = 1
    IS_MENACE = True
    BOSS_NAME = 'The Electric Lier'
    LOOT_TABLE = LootTable([
        SelectionLoot([('palladium', 20, 30), ('mithrill', 20, 30), ('titanium', 20, 30)], 1, 3),
        IndividualLoot('soul_of_kindness', 1, 10, 22),
        IndividualLoot('remote_sword', 0.5, 1, 1),
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
        self.rs = []
        for _ in range(constants.DIFFICULTY2 * 4 + 2):
            rx = random.uniform(-1, 1)
            ry = (1 - rx ** 2) ** .5 * random.choice([-1, 1])

            self.rs.append(vector.Vector2D(0, 0, rx, ry) * 2 ** random.uniform(-1, 1))

    def on_update(self):
        super().on_update()
        if self.hp_sys.hp < self.hp_sys.max_hp * 0.5 and self.obj.phase == 1:
            self.obj.phase = 2
            self.img = game.get_game().graphics['entity_the_cpu_phase2']
            self.set_rotation(self.rot)
            self.obj.tick = -200
        if self.hp_sys.hp < self.hp_sys.max_hp * 0.35 and self.obj.phase == 2 and constants.DIFFICULTY2 > 1:
            self.obj.phase = 3
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
        if self.obj.phase >= 2:
            r.center = position.displayed_position((px + aay, py + aax))
            displayer.canvas.blit(self.d_img, r)
            r.center = position.displayed_position((px - aay, py - aax))
            displayer.canvas.blit(self.d_img, r)
            r.center = position.displayed_position((px + aay, py - aax))
            displayer.canvas.blit(self.d_img, r)
            r.center = position.displayed_position((px - aay, py + aax))
            displayer.canvas.blit(self.d_img, r)
        dt = vector.distance(aax, aay)
        pax = aax
        pay = aay
        if self.obj.phase == 3:
            for rx, ry in self.rs:
                aax = (rx * dt + pax) / 2
                aay = (ry * dt + pay) / 2
                r.center = position.displayed_position((px - aax, py + aay))
                displayer.canvas.blit(self.d_img, r)
                r.center = position.displayed_position((px + aax, py - aay))
                displayer.canvas.blit(self.d_img, r)
                r.center = position.displayed_position((px - aax, py - aay))
                displayer.canvas.blit(self.d_img, r)
                r.center = position.displayed_position((px + aay, py + aax))
                displayer.canvas.blit(self.d_img, r)
                r.center = position.displayed_position((px - aay, py - aax))
                displayer.canvas.blit(self.d_img, r)
                r.center = position.displayed_position((px + aay, py - aax))
                displayer.canvas.blit(self.d_img, r)
                r.center = position.displayed_position((px - aay, py + aax))
                displayer.canvas.blit(self.d_img, r)
        self.d_img.set_alpha(255)

