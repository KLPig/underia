from underia import entity, game, inventory, player_profile
from values import damages, effects
from resources import position
from physics import vector
import constants

import copy
import random
import pygame as pg
import math

class Entity(entity.Entities.Entity):
    pass

class LootTable(entity.LootTable):
    pass

class IndividualLoot(entity.IndividualLoot):
    pass

class SelectionLoot(entity.SelectionLoot):
    pass

class WormEntity(entity.Entities.WormEntity):
    pass

class MonsterAI(entity.MonsterAI):
    pass

class RangedAI(entity.RangedAI):
    pass

@entity.AIs.entity_ai
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


@entity.AIs.entity_ai
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

@entity.AIs.entity_ai
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

@entity.AIs.entity_ai
class LeafAI(StarAI):
    MASS = 320
    TOUCHING_DAMAGE = 288
    SPEED = 1.8

@entity.AIs.entity_ai
class WorldsFruitAI(MonsterAI):
    MASS = 5000
    FRICTION = 0.9
    SPEED = .5
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

@entity.AIs.entity_ai
class AppleProtectionAI(MonsterAI):
    MASS = 80
    FRICTION = 0.9
    TOUCHING_DAMAGE = 48
    VITAL = True
    SIGHT_DISTANCE = 99999

    def __init__(self, pos):
        super().__init__(pos)
        self.upper = None

    def on_update(self):
        if self.upper is not None:
            vv = self.upper.pos - self.pos
            self.apply_force(vv / abs(vv) * (abs(vv) - 150) / 5)

@entity.AIs.entity_ai
class AppleAttackAI(MonsterAI):
    MASS = 80
    FRICTION = 0.9
    TOUCHING_DAMAGE = 48
    VITAL = True
    SIGHT_DISTANCE = 99999

    def on_update(self):
        player = self.cur_target
        if player is not None:
            pp = player.pos - self.pos
            self.apply_force(pp / 10)
        else:
            self.idle()

@entity.AIs.entity_ai
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

@entity.AIs.entity_ai
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
            self.d = 240 + (math.sin(self.tick / 200 * math.pi) + 1) * 300
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


@entity.Entities.entity_type
class MagmaKingFireball(Entity):
    NAME = 'Magma King Fireball'
    DISPLAY_MODE = 3
    DMG = 68
    DIVERSITY = False

    def __init__(self, pos, rot):
        super().__init__(pos, game.get_game().graphics['entity_fireball'], MagmaKingFireballAI, 200)
        self.obj.rot = rot
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = -30
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 0
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = -80
        if constants.DIFFICULTY >= 3:
            self.hp_sys.IMMUNE = True

    def on_update(self):
        super().on_update()
        self.set_rotation(self.rot)
        self.hp_sys.hp -= 5
        self.damage()

    def damage(self):
        if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                           self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
            game.get_game().player.hp_sys.damage(self.DMG, damages.DamageTypes.MAGICAL)
            game.get_game().player.hp_sys.effect(effects.Burning(4, 4))
            game.get_game().player.hp_sys.enable_immune()
            self.hp_sys.hp = 0

@entity.Entities.entity_type
class SandStormAttack(MagmaKingFireball):

    def damage(self):
        if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                           self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 36:
            game.get_game().player.hp_sys.damage(77, damages.DamageTypes.MAGICAL)
            game.get_game().player.hp_sys.enable_immune()
            self.hp_sys.hp = 0

@entity.Entities.entity_type
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
            game.get_game().player.hp_sys.enable_immune()
            self.hp_sys.hp = 0

@entity.Entities.entity_type
class Star(Entity):
    NAME = 'Star'
    DISPLAY_MODE = 3
    LOOT_TABLE = LootTable([
        IndividualLoot('magic_stone', 0.9, 12, 15),
        IndividualLoot('mana_crystal', 0.5, 1, 2),
        IndividualLoot('star_amulet', 0.4, 1, 1),
    ])

    SOUND_HURT = 'crystal'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity_star'], StarAI, 900)
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = -11


@entity.Entities.entity_type
class FluffBall(Entity):
    NAME = 'Fluff Ball'
    DISPLAY_MODE = 1
    LOOT_TABLE = LootTable([
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
            super().__init__(pos, game.get_game().graphics['entity_fluffball'], FluffBallAI,
                             int(4800 * 1.5 ** (game.get_game().stage - 3 * game.get_game().chapter)))
        else:
            super().__init__(pos, game.get_game().graphics['entity_fluffball'], FluffBallAI, 880)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = -2
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = -8
        if game.get_game().stage > 0:
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = -4
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = -9
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = -8
            self.obj.SPEED *= 3
            self.NAME = f'Rolling Fluff-Ball LV.{game.get_game().stage - 3 * game.get_game().chapter}'
            self.obj.TOUCHING_DAMAGE *= (
                        6 + 1.5 * (game.get_game().stage - 3 * game.get_game().chapter + constants.DIFFICULTY))

    def t_draw(self):
        super().t_draw()
        if self.hp_sys.hp <= 0:
            b = 0
            if not 'M1B' in game.get_game().player.nts and random.random() < .1:
                game.get_game().player.nts.append('M1B')
                b = 1
            if b:
                game.get_game().dialog.push_dialog('[Notebook Updated!]')

    def on_update(self):
        super().on_update()
        px = game.get_game().player.obj.pos[0] - self.obj.pos[0]
        self.set_rotation(px / 80 + self.rot)

@entity.Entities.entity_type
class Fluffff(WormEntity):
    NAME = 'Fluffff'
    DISPLAY_MODE = 1
    BOSS_NAME = 'The Fluffy Worm'
    LOOT_TABLE = LootTable([
        IndividualLoot('flufffur', 1, 5, 8),
        SelectionLoot([('swwwword', 1, 1), ('kuangkuangkuang', 1, 1), ('furfur', 1, 1)], 1, 1),
    ])
    IS_MENACE = True

    SOUND_HURT = 'dragon'
    SOUND_DEATH = 'sticky'

    def __init__(self, pos):
        if 'D3' in game.get_game().player.nts and game.get_game().stage <= 0:
            super().__init__(pos, 20 + [-2, 0, 6, 12][constants.DIFFICULTY],
                             game.get_game().graphics['entity_fluffball'],
                             game.get_game().graphics['entity_fluffff'], FluffBallAI,
                             int(60000 * [.5, 1, 1.6, 2.2][constants.DIFFICULTY]), 260, 180)
            self.obj.SPEED *= 2
            for b in self.body:
                for d in b.hp_sys.defenses.defences.keys():
                    b.hp_sys.resistances[d] *= .2 if b not in [self.body[0], self.body[-1]] else 1.5
                    b.hp_sys.defenses[d] += 80
                b.img = game.get_game().graphics['entity_fluffff_otherworld']
            if not len([1 for l in self.LOOT_TABLE.loot_list if 'item' in dir(l) and l.item == 'otherworld_stone']):
                self.LOOT_TABLE.loot_list.append(
                    IndividualLoot('otherworld_stone', 1, 10, 20),
                )
                self.LOOT_TABLE.loot_list.append(
                    IndividualLoot('worm_scarf', 1, 1, 1),
                )
            self.NAME = 'Fluffff - Otherworld'
        else:
            super().__init__(pos, 12 + [-2, 0, 6, 12][constants.DIFFICULTY],
                             game.get_game().graphics['entity_fluffball'],
                             game.get_game().graphics['entity_fluffff'], FluffBallAI,
                             int(88000 * [.5, 1, 1.6, 2.2][constants.DIFFICULTY]), 130, 90)
        self.body[0].obj.SIGHT_DISTANCE = 9999
        self.body[0].obj.SPEED *= 3

    def t_draw(self):
        super().t_draw()

        if self.hp_sys.hp <= 0:
            b = 0
            if not 'D1B' in game.get_game().player.nts and random.random() < .1:
                game.get_game().player.nts.append('D1B')
                b = 1
            if b:
                game.get_game().dialog.push_dialog('[Notebook Updated!]')

@entity.Entities.entity_type
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
                game.get_game().entities.append(HeavenBall(self.obj.pos, self.rot))


@entity.Entities.entity_type
class ProtectApple(Entity):
    NAME = 'Apple'
    DISPLAY_MODE = 3
    LOOT_TABLE = LootTable([])
    SOUND_HURT = 'ore'
    SOUND_DEATH = 'ore'
    VITAL = True

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity_apple'], AppleProtectionAI, 600)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 8
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 18
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 13

    def on_hit(self, plyr):
        plyr.hp_sys.effect(effects.Faith(8, 5))

@entity.Entities.entity_type
class AttackApple(Entity):
    NAME = 'Apple'
    DISPLAY_MODE = 3
    LOOT_TABLE = LootTable([])
    SOUND_HURT = 'ore'
    SOUND_DEATH = 'ore'
    VITAL = True

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity_apple'], AppleAttackAI, 800)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 8
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 18
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 13

    def on_hit(self, plyr):
        plyr.hp_sys.effect(effects.Faith(8, 5))

@entity.Entities.entity_type
class TheWorldsFruit(Entity):
    NAME = 'The World\'s Fruit'
    DISPLAY_MODE = 3
    LOOT_TABLE = LootTable([
        SelectionLoot([('doctor_expeller', 1, 1), ('apple_knife', 1, 1), ('fruit_wand', 1, 1)], 1, 2),
        IndividualLoot('life_core', 1, 10, 20),
        ])
    SOUND_SPAWN = 'boss'
    SOUND_HURT = 'ore'
    SOUND_DEATH = 'huge_monster'
    BOSS_NAME = 'The God\'s Heritage'
    IS_MENACE = True
    PHASE_SEGMENTS = []

    def __init__(self, pos):
        super().__init__(pos, copy.copy(game.get_game().graphics['entity_worlds_fruit']), WorldsFruitAI, 18000)
        an = [10, 12, 20, 30][constants.DIFFICULTY]
        if 'D3' in game.get_game().player.nts and game.get_game().stage <= 0:
            self.hp_sys.max_hp *= 2
            self.hp_sys.hp *= 2
            self.obj.TOUCHING_DAMAGE += 50
            self.obj.SPEED *= 2
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] += 30
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] += 30
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] += 30
            if not len([1 for l in self.LOOT_TABLE.loot_list if 'item' in dir(l) and l.item == 'otherworld_stone']):
                self.LOOT_TABLE.loot_list.append(
                    IndividualLoot('otherworld_stone', 1, 1, 2),
                )
                self.LOOT_TABLE.loot_list.append(
                    IndividualLoot('worlds_seed', 1, 1, 1),
                )
            self.NAME = 'The Worlds Fruit - Otherworld'
            self.img = game.get_game().graphics['entity_worlds_fruit_otherworld']
            self.d = True
            an += 5
        else:
            self.d = False
        self.apples = [ProtectApple((self.obj.pos[0] + random.randint(-1000, 1000), self.obj.pos[1] + random.randint(-1000, 1000))) for _ in range(an)] + \
                      [AttackApple((self.obj.pos[0] + random.randint(-1000, 1000), self.obj.pos[1] + random.randint(-1000, 1000))) for _ in range(an)]
        self.phase = 0
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 20
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 28
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 26
        self.hp_sys(op='config', immune=True)
        for a in self.apples:
            a.obj.upper = self.obj
            game.get_game().entities.append(a)
        self.o_hp = self.hp_sys.max_hp
        self.hp_sys.max_hp += sum([a.hp_sys.max_hp for a in self.apples]) - 20000
        self.hp_sys.hp = self.hp_sys.max_hp
        self.PHASE_SEGMENTS = [self.o_hp / self.hp_sys.max_hp]
        self.tick = 0

    def on_update(self):
        if self.phase == 0:
            if constants.DIFFICULTY >= 1:
                for a in self.apples:
                    ap = a.obj.pos - self.obj.pos
                    if a.hp_sys.hp <= 0 or a not in game.get_game().entities:
                        self.apples.remove(a)
                        self.obj.SPEED *= 1.001
                        for aa in self.apples:
                            aa.obj.SPEED *= 1.002
            self.hp_sys.hp = self.o_hp + max(0, sum([a.hp_sys.hp for a in self.apples]) - 20000)
            if self.hp_sys.hp <= self.o_hp or not len(self.apples):
                self.phase = 1
                dm = [6, 7, 15, 25][constants.DIFFICULTY]
                for a in [ProtectApple((self.obj.pos[0] + random.randint(-100, 100), self.obj.pos[1] + random.randint(-100, 100))) for _ in range(dm)] + \
                      [AttackApple((self.obj.pos[0] + random.randint(-100, 100), self.obj.pos[1] + random.randint(-100, 100))) for _ in range(dm)]:
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
            if constants.DIFFICULTY >= 2:
                if not random.randint(0, 3000):
                    self.apples.append(ProtectApple((self.obj.pos[0] + random.randint(-1000, 1000), self.obj.pos[1] + random.randint(-1000, 1000))))
                if not random.randint(0, 3000):
                    self.apples.append(AttackApple((self.obj.pos[0] + random.randint(-1000, 1000), self.obj.pos[1] + random.randint(-1000, 1000))))
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

    def t_draw(self):
        super().t_draw()
        if self.hp_sys.hp <= 0:
            b = 0
            if not 'D1C' in game.get_game().player.nts:
                game.get_game().player.nts.append('D1C')
                b = 1
            if b:
                game.get_game().dialog.push_dialog('[Notebook Updated!]')

@entity.Entities.entity_type
class MagmaKing(Entity):
    NAME = 'Magma King'
    DISPLAY_MODE = 3
    VITAL = True
    LOOT_TABLE = LootTable([
    ])

    SOUND_SPAWN = 'boss'
    SOUND_HURT = 'sticky'
    SOUND_DEATH = 'huge_monster'

    DIVERSITY = False

    PHASE_SEGMENTS = [0.15, 0.3, 0.4, 0.8, 0.9]

    def __init__(self, pos, cps=0, hp=-1):
        super().__init__(pos, pg.transform.scale_by(game.get_game().graphics['entity_magma_king'], 1 / 1.1 ** cps),
                         MagmaKingAI, 28800)
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 12
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 8
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 8
        self.phase = cps
        if hp > 0:
            self.hp_sys.hp = hp

    def on_update(self):
        super().on_update()
        self.hp_sys.heal([0, 0, 1, 3][constants.DIFFICULTY])
        if self.phase < 3 and self.hp_sys.hp <= self.hp_sys.max_hp * self.PHASE_SEGMENTS[-1 - self.phase * 2]:
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] -= 20
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] -= 20
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] -= 20
            self.phase += 1
            self.hp_sys.hp //= 2
            for _ in range([1, 1, 2, 2][constants.DIFFICULTY]):
                game.get_game().entities.append(MagmaKing(self.obj.pos, cps=self.phase, hp=self.hp_sys.hp))
        if self.obj.state == 2 and self.obj.timer % (3 + self.phase) == 1:
            player = game.get_game().player
            game.get_game().entities.append(MagmaKingFireball(self.obj.pos, vector.coordinate_rotation(
                player.obj.pos[0] - self.obj.pos[0], player.obj.pos[1] - self.obj.pos[1])))
        if self.obj.state == 1 and self.obj.timer % 40 == 20:
            player = game.get_game().player
            for k in range(-60, 61, [10, 30, 30, 60, 60][self.phase] // (2 if constants.DIFFICULTY >= 3 else 1)):
                fb = MagmaKingFireball(self.obj.pos,
                                                k + vector.coordinate_rotation(player.obj.pos[0] - self.obj.pos[0],
                                                                               player.obj.pos[1] - self.obj.pos[1]))
                fb.obj.apply_force(
                    vector.Vector(self.obj.velocity.get_net_rotation(), self.obj.velocity.get_net_value() // 50))
                game.get_game().entities.append(fb)

@entity.Entities.entity_type
class MagmaKingCounter(Entity):
    NAME = 'Magma King'

    LOOT_TABLE = LootTable([
        IndividualLoot('blood_ingot', .7, 10, 20),
        IndividualLoot('firite_ingot', .9, 10, 30),
        IndividualLoot('firy_plant', 1, 20, 25),
        SelectionLoot([('mantle', 1, 1), ('phoenix_exploder', 1, 1), ('sunfire', 1, 1)], 1, 1),
    ])

    BOSS_NAME = 'The Fire Monster'
    PHASE_SEGMENTS = []
    IS_MENACE = True

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity_magma_king'], entity.BuildingAI, 1000000)
        self.obj.IS_OBJECT = False

    def draw(self):
        pass

    def on_update(self):
        s = 0
        sm = 1
        for i, e in enumerate([ee for ee in game.get_game().entities if type(ee) is MagmaKing]):
            if not i:
                self.obj.pos = e.obj.pos
            s += e.hp_sys.hp
            sm += e.hp_sys.max_hp
        self.hp_sys.hp = s
        self.hp_sys.max_hp = sm

@entity.Entities.entity_type
class SandStorm(Entity):
    NAME = 'Sandstorm'
    DISPLAY_MODE = 3
    IS_MENACE = True
    BOSS_NAME = 'The Ghost of Desert'
    LOOT_TABLE = LootTable([
        IndividualLoot('mysterious_ingot', 1, 15, 35),
        IndividualLoot('storm_core', 1, 2, 4),
        SelectionLoot([('tornado', 1, 1), ('storm_swift_sword', 1, 1), ('storm_stabber', 1, 1)], 1, 1),
    ])
    VITAL = True
    PHASE_SEGMENTS = [0.5]
    SOUND_SPAWN = 'boss'
    SOUND_HURT = 'skeleton'
    SOUND_DEATH = 'huge_monster'

    def __init__(self, pos, hp_sys=None, rot=0, ss=True):
        if ss:
            super().__init__(pos, game.get_game().graphics['entity_sandstorm'], SandStormAI,
                             hp=6000 * (2 + max(1, constants.DIFFICULTY)))
        else:
            super().__init__(pos, game.get_game().graphics['entity_sandstorm'], SandStormAI, hp_sys=hp_sys)
        if ss:
            for ar in range([180, 180, 120, 90][constants.DIFFICULTY], 360, [180, 180, 120, 90][constants.DIFFICULTY]):
                ss = SandStorm(pos, hp_sys=self.hp_sys, rot=rot + ar, ss=False)
                ss.IS_MENACE = False
                game.get_game().entities.append(ss)
                for r in ss.hp_sys.resistances:
                    self.hp_sys.resistances[r] *= .5
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 40
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 40
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 40
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
            game.get_game().entities.append(SandStormAttack(self.obj.pos, self.rot + random.randint(-10, 10)))
        if self.hp_sys.hp < self.hp_sys.max_hp * 0.5 and self.phase == 0:
            self.phase = 1
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] += 20
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] += 10
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] += 15
            self.obj = entity.CleverRangedAI(self.obj.pos)
            self.obj.TOUCHING_DAMAGE = 450
            self.obj.SIGHT_DISTANCE = 9999
            self.obj.MASS *= 3
            self.obj.SPEED *= 8
            self.obj.shoot_distance = random.randint(500, 2000)
            self.obj.state = 0
        if self.phase == 1 and self.tick % 50 == 0:
            self.obj.shoot_distance = random.randint(500, 2000)

    def t_draw(self):
        super().t_draw()
        if self.hp_sys.hp <= 0:
            b = 0
            if not 'D3' in game.get_game().player.nts:
                game.get_game().player.nts.append('D3')
                b = 1
            if b:
                game.get_game().dialog.push_dialog('[Notebook Updated!]', 'Looks like the world have changed...')


