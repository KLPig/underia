import copy
import math
import numpy
import pygame as pg

import constants
from underia import entity, game, inventory
from physics import vector
from values import damages, effects, hp_system
from visual import draw
from resources import position
import random

class ChickenAI(entity.MonsterAI):
    IDLE_SPEED = 200
    IDLE_TIME = 30
    IDLE_CHANGER = 50

    TOUCHING_DAMAGE = 90
    SIGHT_DISTANCE = 2500

    MASS = 100
    FRICTION = 0.98

    def on_update(self):
        super().on_update()
        if self.cur_target is not None:
            px, py = self.cur_target.pos
            if self.time_touched_player < 120:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px - self.pos[0], py - self.pos[1]),
                                               -250))
            self.apply_force(vector.Vector(vector.coordinate_rotation(px - self.pos[0], py - self.pos[1]),
                                           150))
        else:
            if self.time_touched_player > 120:
                self.idle()

class CentipedeAI(entity.MonsterAI):
    IDLE_SPEED = 1000
    IDLE_TIME = 80
    IDLE_CHANGER = 10

    TOUCHING_DAMAGE = 110
    SIGHT_DISTANCE = 1200

    MASS = 200
    FRICTION = 0.9

    def on_update(self):
        super().on_update()
        if self.cur_target is not None:
            px, py = self.cur_target.pos
            if self.time_touched_player < 200:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px - self.pos[0], py - self.pos[1]) + 90,
                                               300))
            self.apply_force(vector.Vector(vector.coordinate_rotation(px - self.pos[0], py - self.pos[1]),
                                           400))
        else:
            if self.time_touched_player > 120:
                self.idle()

class LycheeAI(CentipedeAI):
    IDLE_SPEED = 0
    MASS = 80
    SIGHT_DISTANCE = 800
    TOUCHING_DAMAGE = 130

class PotAI(entity.MonsterAI):
    IDLE_SPEED = 800
    IDLE_TIME = 80
    IDLE_CHANGER = 10

    TOUCHING_DAMAGE = 160
    SIGHT_DISTANCE = 1600

    MASS = 100
    FRICTION = 0.95

    def on_update(self):
        super().on_update()
        if self.cur_target is not None:
            px, py = self.cur_target.pos
            if self.time_touched_player < 100:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px - self.pos[0], py - self.pos[1]) + 180,
                                               360000 / vector.distance(px - self.pos[0], py - self.pos[1])))
            self.apply_force(vector.Vector(vector.coordinate_rotation(px - self.pos[0], py - self.pos[1]),
                                           600))
        else:
            if self.time_touched_player > 300:
                self.idle()

class PoiseWalkerAI(entity.MonsterAI):
    IDLE_SPEED = 800
    IDLE_TIME = 20
    IDLE_CHANGER = 10
    MASS = 400
    SIGHT_DISTANCE = 3000
    TOUCHING_DAMAGE = 240
    FRICTION = 0.6

    def __init__(self, *args):
        super().__init__(*args)
        self.tick = 0
        self.tx, self.ty = 0, 0

    def on_update(self):
        super().on_update()
        if self.time_touched_player < 200:
            return
        if self.cur_target is not None:
            px, py = self.cur_target.pos
            self.tick += 1
            if random.randint(0, self.tick) > 140:
                self.tick = 0
            ax, ay = vector.rotation_coordinate(random.randint(0, 360))
            if self.tick < 70:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px - self.pos[0], py - self.pos[1]),
                                               1200))
            elif self.tick == 70:
                self.tx = ax * 1000 + px
                self.ty = ay * 1000 + py
            elif self.tick < 80:
                self.pos << ((self.pos[0] * 5 + self.tx) // 6, (self.pos[1] * 5 + self.ty) // 6)
                self.IS_OBJECT = False
            elif self.tick == 80:
                self.IS_OBJECT = True
            else:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px - self.pos[0], py - self.pos[1]),
                                               1800))
        else:
            self.idle()

class BonecaAmbalabuAI(entity.MonsterAI):
    MASS = 250
    FRICTION = 0.9
    IDLE_SPEED = 4000
    IDLE_TIME = 100
    IDLE_CHANGER = 180
    TOUCHING_DAMAGE = 100
    SIGHT_DISTANCE = 4000

    def on_update(self):
        super().on_update()
        if self.cur_target is None:
            self.idle()
            return
        pv = self.cur_target.pos - self.pos
        if self.time_touched_player < 100:
            self.apply_force(vector.Vector2D(0, 0, pv[0] * -1, pv[1] * -.3))
        else:
            self.apply_force(vector.Vector2D(0, 0, pv[0] * 2, pv[1] * .6))

class LaVacaSaturnoSaturnitaAI(entity.MonsterAI):
    MASS = 2000
    FRICTION = 0.9
    IDLE_CHANGER = 10
    IDLE_TIME = 10
    IDLE_SPEED = 8000
    SIGHT_DISTANCE = 2000
    TOUCHING_DAMAGE = 180

    def __init__(self, *args):
        super().__init__(*args)
        self.dy = -600

    def on_update(self):
        super().on_update()
        if self.cur_target is None:
            self.idle()
            return
        pv = self.cur_target.pos - self.pos + vector.Vector2D(dy=-self.dy)
        self.apply_force(pv * 8)

class ChimpanziniBananiniAI(entity.MonsterAI):
    MASS = 1000
    FRICTION = 0.9
    IDLE_SPEED = 4000
    IDLE_TIME = 100
    IDLE_CHANGER = 180
    SIGHT_DISTANCE = 2000
    TOUCHING_DAMAGE = 450

    def __init__(self, *args):
        super().__init__(*args)
        self.tick = 0

    def on_update(self):
        super().on_update()
        if self.cur_target is None:
            self.idle()
            return
        if random.randint(0, self.tick) > 150:
            self.tick = 0
        self.tick += 1

        if self.tick < 80:
            self.apply_force((self.cur_target.pos - (0, 500) - self.pos) * 25)
        elif self.tick < 100:
            self.apply_force(vector.Vector2D(dy=30000))


class BombardinoCrocodiloAI(entity.MonsterAI):
    MASS = 5000
    FRICTION = 0.95
    SIGHT_DISTANCE = 9999
    IS_OBJECT = False
    TOUCHING_DAMAGE = 150

    def __init__(self, *args):
        super().__init__(*args)
        self.tick = 0
        self.state = 0
        self.r = 0

    def on_update(self):
        super().on_update()
        if self.cur_target is None:
            self.idle()
            return
        pv = self.cur_target.pos - self.pos
        if random.randint(0, self.tick) > 300:
            self.state = not self.state
            self.tick = 0
        self.tick += 1
        if self.state == 0:
            self.IS_OBJECT = False
            self.apply_force(vector.Vector2D(dx=(1 if self.tick % 80 > 40 else -1) * 8000, dy=5 * (pv[1] - 2000)))
            self.r = vector.coordinate_rotation(*pv)
        else:
            self.IS_OBJECT = True
            if self.tick % int(100 / self.SPEED) < int(80 / self.SPEED):
                self.FRICTION = .95
                self.apply_force(vector.Vector2D(dr=self.r, dt=80000 * self.SPEED ** .3))
            else:
                self.FRICTION = .95 - (self.tick % int(100 / self.SPEED) - int(80 / self.SPEED)) * .01
                self.r = vector.coordinate_rotation(*pv)

class PredictAI(entity.MonsterAI):
    MASS = 2000
    FRICTION = .9
    IDLE_SPEED = 3000
    IDLE_TIME = 10
    IDLE_CHANGER = 180
    SIGHT_DISTANCE = 2000
    TOUCHING_DAMAGE = 200
    PREFER_DISTANCE = 8

    def __init__(self, *args):
        super().__init__(*args)
        self.tick = 0
        self.p_posx = []
        self.p_posy = []

    def on_update(self):
        super().on_update()
        self.tick += 1
        if self.tick % 10 == 0:
            self.p_posx.append(self.pos[0])
            self.p_posy.append(self.pos[1])
            if len(self.p_posx) > 10:
                self.p_posx.pop(0)
                self.p_posy.pop(0)
            px = numpy.polyfit(numpy.array([self.tick + a for a in range(-len(self.p_posx) * 10 + 10, 1, 10)]),
                               numpy.array(self.p_posx), 5)
            py = numpy.polyfit(numpy.array([self.tick + a for a in range(-len(self.p_posx) * 10 + 10, 1, 10)]),
                               numpy.array(self.p_posy), 5)
            self.apply_force((vector.Vector(px[self.tick + 50], py[self.tick + 50]) - self.pos) / 40)



class Entity(entity.Entities.Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Tree(Entity):
    NAME = 'Tree'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_wood', 1, 5, 25),
        entity.IndividualLoot('talent_fruit', .04, 1, 1),
        entity.IndividualLoot('moonflower', .01, 1, 1)
    ])
    SOUND_DEATH = 'ore'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics[f'entity3_tree{random.randint(1, 3)}'],
                         entity.BuildingAI, hp=12)
        for d in self.hp_sys.defenses.defences:
            self.hp_sys.defenses[d] += 1999

class DeadTree(Entity):
    NAME = 'Dead Tree'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_wood', 1, 15, 30),
        entity.IndividualLoot('talent_fruit', .02, 1, 1),
    ])
    SOUND_DEATH = 'ore'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics[f'entity3_dead_tree{random.randint(1, 2)}'],
                         entity.BuildingAI, hp=16)
        for d in self.hp_sys.defenses.defences:
            self.hp_sys.defenses[d] += 1999

class Chicken(Entity):
    NAME = 'Chicken'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_feather', 1, 5, 25),
        entity.IndividualLoot('feather_sword', .02, 1, 1),

    ])
    SOUND_HURT = 'dragon'
    SOUND_DEATH = 'dragon'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics[f'entity3_chicken'],
                         ChickenAI, hp=540)
        if not random.randint(0, 3):
            self.hp_sys.hp = 0
            self.obj.IS_OBJECT = False
            game.get_game().entities.append(FormalChicken(self.obj.pos))

    def on_update(self):
        super().on_update()
        self.set_rotation(-self.obj.velocity.get_net_rotation())

class FormalChicken(Chicken):
    NAME = 'Formal Chicken'
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_feather', 1, 5, 25),
        entity.IndividualLoot('feather_sword', .02, 1, 1),
        entity.IndividualLoot('sniper', .1, 1, 1),
        entity.IndividualLoot('e_wings', .02, 1, 1),
        entity.IndividualLoot('hand_of_social', .05, 1, 1),
        entity.IndividualLoot('black_leather_gloves', .05, 1, 1),
        entity.IndividualLoot('black_bow_tie', .05, 1, 1),
        entity.IndividualLoot('black_socks', .05, 1, 1),
        entity.IndividualLoot('hidden_sword', .05, 1, 1),
    ])

    SOUND_HURT = 'dragon'
    SOUND_DEATH = 'dragon'

    def __init__(self, pos):
        super(Chicken, self).__init__(pos, game.get_game().graphics[f'entity3_formal_chicken'],
                         ChickenAI, hp=1500)

class HeavenLazer(Entity):
    NAME = 'Heaven Lazer'
    DISPLAY_MODE = 1
    SOUND_SPAWN = 'lazer'

    def __init__(self, pos, rot, q=False):
        super().__init__(pos, game.get_game().graphics[f'entity_null'], entity.BuildingAI, hp=1000)
        self.set_rotation(rot)
        self.obj.FRICTION = .99
        self.obj.IS_OBJECT = False
        self.obj.MASS = 10000
        self.obj.SPEED *= 100
        self.q = q
        self.tick = 0
        self.show_bar = False

    def on_update(self):
        self.tick += 1
        super().on_update()
        if self.tick >= 20:
            if self.tick == 20:
                self.obj.apply_force(vector.Vector2D(self.rot, 6000 if self.q else 2000))
            else:
                self.obj.apply_force(vector.Vector2D(self.rot, 1000))
        self.hp_sys.hp -= 15

    def damage(self):
        if abs(self.obj.pos - game.get_game().player.obj.pos) < 300:
            self.hp_sys.hp = 0
            game.get_game().player.hp_sys.damage(65 + self.q * 20, damages.DamageTypes.MAGICAL)

    def t_draw(self):
        super().t_draw()
        if self.tick >= 20:
            self.damage()
        draw.line(game.get_game().displayer.canvas, (255, 0, 0), position.displayed_position(self.obj.pos),
                  position.displayed_position(self.obj.pos + vector.Vector2D(dr=self.rot, dt=1) *
                  (150 if self.tick > 20 else 1500)),
                  width=int(10 / game.get_game().player.get_screen_scale()) if self.tick > 20 else 2)

class HeavenRanger(Entity):
    NAME = 'Heaven "Ranger"'
    DISPLAY_MODE = 1
    SOUND_HURT = 'metal'
    SOUND_DEATH = 'explosive'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics[f'entity3_heaven_ranger'], entity.CleverRangedAI, hp=600)
        self.obj.TOUCHING_DAMAGE = 140
        self.obj.MASS = 80
        self.obj.SPEED *= .4
        self.obj.SIGHT_DISTANCE = 1350
        self.obj.shoot_distance = 440 - constants.DIFFICULTY * 40
        self.tick = 0
        for d in self.hp_sys.defenses.defences.keys():
            self.hp_sys.defenses[d] += 55

    def on_update(self):
        super().on_update()
        self.set_rotation(-vector.coordinate_rotation(*(game.get_game().player.obj.pos - self.obj.pos)))
        self.tick += 1
        dr = abs(self.obj.pos - game.get_game().player.obj.pos)
        if dr < 450:
            if self.tick % (15 - constants.DIFFICULTY * 3) == 0:
                game.get_game().entities.append(HeavenLazer(self.obj.pos, -self.rot, q=True))
        elif dr < self.obj.SIGHT_DISTANCE * (5 + constants.DIFFICULTY) // 5:
            if self.tick % (40 - constants.DIFFICULTY * 5) == 0:
                game.get_game().entities.append(HeavenLazer(self.obj.pos, -self.rot))

class HeavenDefender(Entity):
    NAME = 'Heaven "Defender"'
    DISPLAY_MODE = 3
    SOUND_HURT = 'metal'
    SOUND_DEATH = 'explosive'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics[f'entity3_heaven_defender'], entity.BuildingAI, hp=1400)
        self.obj.TOUCHING_DAMAGE = 160
        for d in self.hp_sys.defenses.defences.keys():
            self.hp_sys.defenses[d] += 75
        self.rangers = [HeavenRanger(self.obj.pos + vector.Vector2D(91, i * 50)) for i in range(constants.DIFFICULTY + 1)]
        for r in self.rangers:
            r.obj.SPEED = 0
            game.get_game().entities.append(r)
        self.tick = 0

    def on_update(self):
        self.tick += 1
        for i in range(len(self.rangers)):
            self.rangers[i].obj.pos = self.obj.pos + vector.Vector2D(91 + self.tick * (2 + constants.DIFFICULTY) +
                                                                     i * 360 // len(self.rangers), 250)

        super().on_update()

class BloodChicken(Chicken):
    NAME = 'Blood Chicken(LV.1)'
    LOOT_TABLE = entity.LootTable([
    ])

    SOUND_HURT = 'corrupt'
    SOUND_DEATH = 'sticky'

    def __init__(self, pos, lv: float=1.0):
        super(Chicken, self).__init__(pos, game.get_game().graphics[f'entity3_blood_chicken'],
                         ChickenAI, hp=int(5 ** lv) * 600)
        self.obj.TOUCHING_DAMAGE = int(120 * 2 ** lv)
        for d in self.hp_sys.defenses.defences.keys():
            self.hp_sys.defenses[d] += int(80 * 2 ** lv)
        self.obj.SPEED *= 1.2 ** lv
        self.NAME = f'Blood Chicken(LV.{lv:.1f})'
        self.obj.SIGHT_DISTANCE = 10000
        self.obj.MASS *= 2 ** lv * 30
        self.obj.SPEED *= 2 ** lv * 30

class NightmareFlower(Chicken):
    NAME = 'Nightwmare Flower(LV.1)'
    LOOT_TABLE = entity.LootTable([
    ])

    SOUND_HURT = 'corrupt'
    SOUND_DEATH = 'sticky'

    def __init__(self, pos, lv: float=1.0):
        super(Chicken, self).__init__(pos, game.get_game().graphics[f'entity3_nightmare_flower'],
                         entity.SoulFlowerAI, hp=int(4 ** lv) * 800)
        self.obj.TOUCHING_DAMAGE = int(150 * 1.5 ** lv)
        for d in self.hp_sys.defenses.defences.keys():
            self.hp_sys.defenses[d] += int(65 * 2 ** lv)
        self.obj.SPEED *= 1.6 ** lv * 3
        self.NAME = f'Nightmare Flower(LV.{lv:.1f})'
        self.obj.SIGHT_DISTANCE = 10000
        self.obj.MASS *= 2 ** lv * 30
        self.obj.SPEED *= 2 ** lv * 30
        self.obj.FRICTION = .91

class FearCollection(Chicken):
    NAME = 'Fear Collection(LV.1)'
    LOOT_TABLE = entity.LootTable([
    ])

    SOUND_HURT = 'corrupt'
    SOUND_DEATH = 'sticky'

    def __init__(self, pos, lv: float = 1.0):
        super(Chicken, self).__init__(pos, game.get_game().graphics[f'entity3_fear_collection'],
                                      entity.SoulFlowerAI, hp=int(4 ** lv) * 2200)
        self.obj.TOUCHING_DAMAGE = int(60 * 2.5 ** lv)
        for d in self.hp_sys.defenses.defences.keys():
            self.hp_sys.defenses[d] += int(120 * 2 ** lv)
        self.obj.SPEED *= 1.6 ** lv * 20
        self.NAME = f'Fear Collection(LV.{lv:.1f})'
        self.obj.SIGHT_DISTANCE = 10000
        self.obj.MASS *= 10 * 2 ** lv * 30
        self.obj.SPEED *= 2 ** lv * 30
        self.obj.FRICTION = .88

class FleshWalker(Chicken):
    NAME = 'Flesh Walker(LV.1)'
    LOOT_TABLE = entity.LootTable([
    ])

    SOUND_HURT = 'corrupt'
    SOUND_DEATH = 'sticky'

    def __init__(self, pos, lv: float = 1.0):
        super(Chicken, self).__init__(pos, game.get_game().graphics[f'entity3_flesh_walker'],
                                      PoiseWalkerAI, hp=int(4 ** lv) * 1200)
        self.obj.TOUCHING_DAMAGE = int(220 * 1.2 ** lv)
        for d in self.hp_sys.defenses.defences.keys():
            self.hp_sys.defenses[d] += int(10 * 2 ** lv)
        self.obj.SPEED *= 1.2 ** lv * 20
        self.NAME = f'Flesh Walker(LV.{lv:.1f})'
        self.obj.SIGHT_DISTANCE = 10000
        self.obj.MASS *= 2 ** lv * 30
        self.obj.SPEED *= 2 ** lv * 30

class BloodMoon(Entity):
    NAME = 'The Blood Moon'
    BOSS_NAME = 'Cursed Night'

    LOOT_TABLE = entity.LootTable([
    ])

    IS_MENACE = True

    def __init__(self, pos):
        super().__init__(pos, pg.Surface((1, 1)), entity.BuildingAI, hp=1000000)
        self.hp_sys.IMMUNE = True
        self.entities = []
        self.wave = 0
        self.tick = 0
        self.obj.IS_OBJECT = False

    def t_draw(self):
        self.obj.pos = game.get_game().player.obj.pos - (0, 10000)
        if 'blood moon' not in game.get_game().world_events:
            self.hp_sys.hp = 0
            game.get_game().dialog.dialog('The Blood Moon loses interest on you...')
            return
        tar = (self.wave * 5 + 10) * (2 + constants.DIFFICULTY) if self.wave % 5 != 4 else max(1, len(self.entities))
        self.hp_sys.max_hp = tar
        self.hp_sys.hp = self.hp_sys.max_hp - sum([1 - e.hp_sys.hp / e.hp_sys.max_hp for e in self.entities])
        if self.hp_sys.hp <= 0:
            if self.wave < 15 + (game.get_game().stage - 9) * 15:
                tm = [('nightmare_gaze', 5), ('e_whip', 6), ('reborn_amulet', 4), ('blood_pearl', 20)]
                if self.wave > 5:
                    tm.extend([('e_muramasa', 4), ('bloody_hand', 5), ('bloody_rain', 6)])
                rs = random.choices([x for x, _ in tm], [y for _, y in tm])[0]
                if self.wave <= 5:
                    rs.replace('blood_pearl', 'null')
                if rs != 'null':
                    game.get_game().drop_items.append(entity.Entities.DropItem(game.get_game().player.obj.pos, rs, 1))
                self.wave += 1
                self.entities.clear()
                game.get_game().dialog.dialog(f'Round {self.wave} cleared!')
                self.hp_sys.hp = 1
            else:
                game.get_game().dialog.dialog(f'Blood moon event cleared!')
                if 'blood moon' in game.get_game().world_events:
                    game.get_game().world_events.remove('blood moon')
        self.tick += 1
        if self.wave % 5 != 4:
            if len([1 for e in self.entities if e.hp_sys.hp > 0]) < 5 * (10 + constants.DIFFICULTY) and self.tick % 8 == 0:
                for _ in range(int(self.wave // 5 / 3 + constants.DIFFICULTY / 3) + 1):
                    rt = game.get_game().player.obj.pos + vector.Vector2D(random.randint(0, 360), random.randint(400, 1200))
                    lv = 1 + self.wave // 5 * .2 + constants.DIFFICULTY * .1 + self.wave // 5 ** 2 * .03 + (random.random() - .5) * .2
                    if random.random() < .3 and self.wave > 11:
                        tt = FleshWalker(rt, lv)
                    elif random.random() < .4 and self.wave > 6:
                        tt = FearCollection(rt, lv)
                    elif random.random() < .6 and self.wave > 1:
                        tt = NightmareFlower(rt, lv)
                    else:
                        tt = BloodChicken(rt, lv)
                    self.entities.append(tt)
                    game.get_game().entities.append(tt)
        else:
            if not len(self.entities):
                for i in range(2 + min(3, self.wave // 10) + constants.DIFFICULTY // 2):
                    rt = game.get_game().player.obj.pos + vector.Vector2D(random.randint(0, 360), random.randint(400, 1200))
                    lv = 1 + self.wave // 5 * .2 + constants.DIFFICULTY * .2 + self.wave // 5 ** 2 * .03 + (
                                random.random() - .5) * .2 + 2.5
                    if random.random() < .3 and self.wave > 11:
                        tt = FleshWalker(rt, lv)
                    elif random.random() < .4 and self.wave > 6:
                        tt = FearCollection(rt, lv)
                    elif random.random() < .6 and self.wave > 1:
                        tt = NightmareFlower(rt, lv)
                    else:
                        tt = BloodChicken(rt, lv)
                    tt.IS_MENACE = True
                    self.entities.append(tt)
                    game.get_game().entities.append(tt)

        for e in self.entities:
            ap = e.obj.pos - game.get_game().player.obj.pos
            if abs(ap) > 2000:
                ap = ap / abs(ap) * 2000
            e.obj.pos = game.get_game().player.obj.pos + ap
        pg.draw.circle(game.get_game().displayer.canvas, (255, 0, 0), position.displayed_position(game.get_game().player.obj.pos),
                       2000 / game.get_game().player.get_screen_scale(), 3)


class ManaChicken(Entity):
    NAME = 'Mana Chicken'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_feather', .5, 5, 25),
        entity.IndividualLoot('magic_feather', 1, 5, 25),
        entity.IndividualLoot('book', .3, 1, 2),
        entity.IndividualLoot('feather_sword', .02, 1, 1),
        entity.IndividualLoot('moonflower', .02, 1, 1)
    ])
    SOUND_HURT = 'dragon'
    SOUND_DEATH = 'sticky'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics[f'entity3_mana_chicken'],
                         ChickenAI, hp=1200)
        self.obj.MASS /= 3
        self.obj.TOUCHING_DAMAGE += 50

    def on_update(self):
        super().on_update()
        self.set_rotation(-self.obj.velocity.get_net_rotation())


class PoisonChicken(Chicken):
    NAME = 'Poison Chicken'
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_poison_powder', 1, 10, 20),
        entity.SelectionLoot([('e_feather', 3, 8), ('carrion', 3, 9)], 1, 2),
        entity.IndividualLoot('feather_sword', .02, 1, 1),
        entity.IndividualLoot('white_ribbon', 0.02, 1, 1),
    ])
    SOUND_HURT = 'dragon'
    SOUND_DEATH = 'dragon'

    def __init__(self, pos):
        super(Chicken, self).__init__(pos, game.get_game().graphics[f'entity3_poison_chicken'],
                                       ChickenAI, hp=1000)
        self.obj.MASS *= 2
        self.tick = 0

    def on_update(self):
        self.tick += 1
        super().on_update()
        if self.obj.cur_target is None:
            self.obj.idle()
            return
        px, py = self.obj.cur_target.pos
        if vector.distance(px - self.obj.pos[0], py - self.obj.pos[1]) < 500:
            game.get_game().player.hp_sys.effect(effects.CurseSnow(2, 1))
            if self.tick % 5 == 0:
                game.get_game().player.hp_sys.effect(effects.Poison(5, 1))

class BonecaAmbalabu(entity.Entities.Entity):
    NAME = 'Boneca Ambalabu'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('brainrot', 1, 10, 12),
        entity.IndividualLoot('mystery_shard', 1, 30, 32),
        entity.IndividualLoot('mystery_glove', .03, 1, 1),
        entity.IndividualLoot('amber_card', .05, 1, 1),
        entity.IndividualLoot('wheel_frogile_sword', .05, 1, 1),
    ])
    SOUND_HURT = 'dragon'
    SOUND_DEATH = 'dragon'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity3_boneca_ambalabu'],
                         BonecaAmbalabuAI, hp=1200)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 40
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 30
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 35
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 35
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 25
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 10

    def on_update(self):
        super().on_update()
        if self.obj.cur_target is None:
            self.obj.idle()
            return
        px, py = self.obj.cur_target.pos - self.obj.pos
        self.set_rotation(-vector.cartesian_to_polar(px, py)[0])

class LaVacaSaturnoSaturnita(entity.Entities.Entity):
    NAME = 'La Vaca Saturno Saturnita'
    IS_MENACE = True
    BOSS_NAME = ''
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('brainrot', 1, 30, 32),
        entity.IndividualLoot('mystery_shard', 1, 30, 32),
        entity.IndividualLoot('mystery_soul', .4, 6, 12),
        entity.IndividualLoot('moonflower', .08, 1, 1),
        entity.IndividualLoot('tuner', 1, 1, 1),
        entity.IndividualLoot('amber_card', .15, 1, 3),
        entity.SelectionLoot([('starnight_broadsword', 0, 1), ('moonshadow_bullet', 0, 1000), ('starry_night', 0, 1)], 0, 1),
    ])
    SOUND_HURT = 'sticky'
    SOUND_DEATH = 'sticky'

    def __init__(self, pos):
        if game.get_game().stage == 9:
            super().__init__(pos, game.get_game().graphics['entity3_la_vaca_saturno_saturnita'],
                             LaVacaSaturnoSaturnitaAI, hp=18000)
        else:
            super().__init__(pos, game.get_game().graphics['entity3_la_vaca_saturno_saturnita'],
                             LaVacaSaturnoSaturnitaAI, hp=12000)
            self.hp_sys.DODGE_RATE += 0.1
            self.obj.dy = random.choice([-1, 1]) * random.randint(400, 1600)
            self.IS_MENACE = False
            LaVacaSaturnoSaturnita.LOOT_TABLE = entity.LootTable([
                entity.IndividualLoot('brainrot', 1, 30, 32),
                entity.IndividualLoot('mystery_shard', 1, 30, 32),
                entity.IndividualLoot('mystery_soul', .4, 6, 12),
                entity.IndividualLoot('moonflower', .08, 1, 1),
                entity.IndividualLoot('tuner', 1, 1, 1),
                entity.IndividualLoot('amber_card', .15, 1, 3),
                entity.SelectionLoot([('starnight_broadsword', 0, 1), ('moonshadow_bullet', 0, 1000), ('starry_night', 0, 1)], 0, 1),
                entity.IndividualLoot('brain_rotter', 1, 10, 20),
            ])
        self.hp_sys.DODGE_RATE += 0.1

class ChimpanziniBananini(entity.Entities.Entity):
    NAME = 'Chimpanzini Bananini'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('brain_rotter', 1, 10, 20),
    ])
    SOUND_HURT = 'sticky'
    SOUND_DEATH = 'sticky'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity3_chimpanzini_bananini'],
                         ChimpanziniBananiniAI, hp=6400)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 300
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 300
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 300
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 200
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 200
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 200
        self.hp_sys.DODGE_RATE += 0.2

    def on_update(self):
        super().on_update()
        self.set_rotation(-self.obj.velocity.get_net_rotation())

class TrippiTroppi(entity.Entities.Entity):
    NAME = 'Trippi Troppi'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('brain_rotter', 1,   10, 20),
    ])
    SOUND_HURT = 'sticky'
    SOUND_DEATH = 'sticky'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity3_trippi_troppi'],
                         entity.DestroyerAI, hp=160000)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = -100
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = -100
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = -100
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = -150
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = -150
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = -150
        self.hp_sys.DODGE_RATE += 0.1
        self.obj.TOUCHING_DAMAGE = 600
        self.obj.SIGHT_DISTANCE = 300

    def on_update(self):
        super().on_update()
        self.set_rotation(-self.obj.velocity.get_net_rotation())

class PoisonCentipede(entity.Entities.WormEntity):
    NAME = 'Poison Centipede'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_poison_powder', 1, 10, 20),
        entity.IndividualLoot('corrupt_sword', .06, 1, 1),
    ])
    SOUND_HURT = 'crystal'
    SOUND_DEATH = 'monster'

    def __init__(self, pos):
        super().__init__(pos, random.randint(9, 16), game.get_game().graphics[f'entity3_poison_centipede_head'],
                         game.get_game().graphics[f'entity3_poison_centipede_body'], CentipedeAI, hp=2000,
                         body_length=100, body_touching_damage=100)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 20
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 10
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 25
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 25
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 15
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 20

class Lychee(entity.Entities.Entity):
    NAME = 'Lychee'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('lychee_shard', 0.3, 1, 4),
        entity.IndividualLoot('pink_ribbon', 0.02, 1, 1),
        entity.IndividualLoot('cute_watch', .05, 1, 1),
        ])
    SOUND_HURT = 'crystal'
    SOUND_DEATH = 'dragon'
    
    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity3_lychee'], LycheeAI, hp=400)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 30
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 20
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 35
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 35
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 25
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 30

class PurpleClayPot(entity.Entities.Entity):
    NAME = 'Purple Clay Pot'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('purple_clay', .7, 2, 3),
        entity.IndividualLoot('pink_ribbon', 0.03, 1, 1),
        ])
    SOUND_HURT = 'crystal'
    SOUND_DEATH = 'ore'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity3_purple_clay_pot'], PotAI, hp=300)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 40
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 45
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 45
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 45
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 40
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 45


class PoiseWalker(entity.Entities.Entity):
    NAME = 'Poise Walker'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_poison_powder', 1, 5, 25),
        entity.SelectionLoot([('poise_blade', 0, 1), ('pollutant', 0, 1), ('poison_needle', 0, 1)], 0, 1),
        entity.SelectionLoot([('e_feather', 3, 8), ('carrion', 2, 8)], 1, 2),
        entity.IndividualLoot('white_ribbon', 0.05, 1, 1),
    ])
    IS_MENACE = True
    BOSS_NAME = ''

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity3_poise_walker'], PoiseWalkerAI, hp=6000)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 250
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 250
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 250
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 250
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 250
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 250
        self.tick = 0

    def on_update(self):
        super().on_update()
        self.set_rotation(-self.obj.velocity.get_net_rotation())
        if self.obj.cur_target is None:
            self.obj.idle()
            return
        px, py = self.obj.cur_target.pos
        if vector.distance(px - self.obj.pos[0], py - self.obj.pos[1]) < 500:
            game.get_game().player.hp_sys.effect(effects.CurseSnow(2, 1))
            if self.tick % 5 == 0:
                game.get_game().player.hp_sys.effect(effects.Poison(5, 2))
                game.get_game().player.hp_sys.effect(effects.Freezing(20, 1))
        self.tick += 1

class LycheeGuard(Lychee):
    DIVERSITY = False

    def __init__(self, pos):
        super().__init__(pos)
        self.tick = int(int(pos[0] + pos[1]) // 25 % 96)
        self.obj.TOUCHING_DAMAGE = 300
        self.hp_sys.max_hp *= 3
        self.hp_sys.hp *= 3
        self.lychees = []
        self.img = copy.copy(self.img)
        self.set_rotation(0)
        self.focused = False

    def t_draw(self):
        self.hp_sys.heal([0, 0, .05, 1][constants.DIFFICULTY])

        if self.hp_sys.hp < 1:
            self.hp_sys.hp = 1
        elif self.hp_sys.hp < self.hp_sys.max_hp / 2:
            self.img.set_alpha(50)
            self.obj.IS_OBJECT = False
        else:
            self.img.set_alpha(255)
            self.hp_sys.IMMUNE = False
        self.set_rotation(0)
        for l in self.lychees:
            l.t_draw()
            if l.hp_sys.hp <= 0:
                self.lychees.remove(l)
            elif l.hp_sys.hp <= 1:
                l.hp_sys.hp -= .02
        super().t_draw()

    def update(self):
        for l in self.lychees:
            l.update()
        super().update()

    def on_update(self):
        super().on_update()
        self.tick = int(self.tick + 1)
        if self.hp_sys.hp < self.hp_sys.max_hp / 2:
            if self.tick % (192 // (1 + self.focused)) == 1:
                lychee = Lychee(self.obj.pos)
                lychee.obj.SIGHT_DISTANCE *= 5
                lychee.VITAL = True
                lychee.hp_sys.max_hp = 1
                lychee.hp_sys.hp = 1
                lychee.hp_sys.shields = [('s1', 1), ('s2', 1), ('s3', 1)]
                lychee.show_bar = False
                lychee.LOOT_TABLE = entity.LootTable([])
                lychee.obj.FRICTION = 1
                lychee.VITAL = True
                self.lychees.append(lychee)
            elif self.tick % (12 // (1 + 3 * self.focused)) == 1:
                self.lychees.append(LycheeKok(self.obj.pos, vector.cartesian_to_polar( *game.get_game().player.obj.pos - self.obj.pos)[0]))
        else:
            if self.tick % 48 == 1:
                self.lychees.append(LycheeKok(self.obj.pos, vector.cartesian_to_polar(*game.get_game().player.obj.pos - self.obj.pos)[0]))

class LycheeKing(entity.Entities.Entity):
    NAME = 'Lychee King'
    BOSS_NAME = 'Irrational at All'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('lychee_core_shard', 1, 20, 30),
        entity.IndividualLoot('lychee_shard', .8, 40, 60),
        entity.IndividualLoot('hammer_of_rational', 1, 1, 1),
    ])
    PHASE_SEGMENTS = []
    IS_MENACE = True
    SOUND_SPAWN = 'boss'
    SOUND_HURT = 'crystal'
    SOUND_DEATH = 'dragon'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity3_lychee_king'], entity.BuildingAI, hp=18000)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 150
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 150
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 150
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 150
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 150
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 150
        self.tick = 0
        self.phase = 0
        self.o_hp = self.hp_sys.hp
        self.obj.TOUCHING_DAMAGE = 200
        self.lychees = [LycheeGuard((i * 200 + self.obj.pos[0], i * 200 + self.obj.pos[1])) for i in range(12)]
        for lychee in self.lychees:
            game.get_game().entities.append(lychee)
        self.hp_sys.max_hp += sum([l.hp_sys.max_hp for l in self.lychees])
        self.PHASE_SEGMENTS.append(self.o_hp / self.hp_sys.max_hp)

    def t_draw(self):
        super().t_draw()
        self.tick += 1
        if self.phase == 0 and not len([1 for l in self.lychees if l.hp_sys.hp >= l.hp_sys.max_hp * .5]):
            self.phase = 1
            for l in self.lychees:
                l.hp_sys.max_hp = 1
                l.hp_sys.hp = 1
                l.obj.IS_OBJECT = False
            self.tick = -80
        for i in range(12):
            lychee = self.lychees[i]
            av = vector.Vector2D(i * 30 + self.tick * 2,
                                 600 + self.tick ** 2 / 6400 * 1400 if self.tick < 0 else
                                 2000 + 500 * math.sin(self.tick / 60 * math.pi + math.pi * i)
                                 if self.hp_sys.hp < self.o_hp else 600)
            av.x *= (1 + .5 * math.sin(self.tick / 40))
            av.y *= (1 + .5 * math.cos(self.tick / 40))
            lychee.obj.pos = self.obj.pos + av
            if int(self.tick % 600 // 50) * 7 % 12 == i:
                lychee.focused = True
            else:
                lychee.focused = False
        l_hp = sum([l.hp_sys.hp for l in self.lychees])
        if l_hp > 20:
            self.hp_sys.hp = self.o_hp + l_hp
        else:
            self.hp_sys.hp = min(self.hp_sys.hp, self.o_hp - 1)
        if self.hp_sys.hp <= 1:
            for l in self.lychees:
                if l in game.get_game().entities:
                    game.get_game().entities.remove(l)
            self.lychees.clear()

class LycheeKok(entity.Entities.Lazer):
    NAME = 'Lai Chi Kok'
    SOUND_SPAWN = None

    def __init__(self, pos, rot):
        super(entity.Entities.Lazer, self).__init__(pos, game.get_game().graphics['entity3_lychee_kok'],
                                                    entity.AbyssRuneShootAI, 500000)
        self.obj.rot = rot
        self.set_rotation(90 - rot)
        self.obj.MASS /= 4
        self.obj.apply_force(vector.Vector(rot + random.randint(90 - constants.DIFFICULTY * 20, 130) * random.choice([-1, 1]),
                                           random.randint(80000, 120000)))
        self.obj.FRICTION = 1
        self.ex_t = 0
        self.ppos = []
        self.show_bar = False
        self.obj.SPEED *= [1, 1, 2, 3][constants.DIFFICULTY]

    def t_draw(self):
        self.ppos.append(self.obj.pos.to_value())
        if len(self.ppos) > 3:
            self.ppos.pop(0)
        for i in range(len(self.ppos) - 1):
            draw.line(game.get_game().displayer.canvas,
                      (250, 250 - 150 * i // len(self.ppos), 200 - 50 * i // len(self.ppos)),
                      position.displayed_position(self.ppos[i]), position.displayed_position(self.ppos[i + 1]),
                      width=int(4 + 20 * i // len(self.ppos) // game.get_game().player.get_screen_scale()))
        super().t_draw()

    def damage(self):
        self.ex_t += 1
        if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                           self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 300:
            game.get_game().player.hp_sys.damage(150, damages.DamageTypes.MAGICAL)
            if constants.DIFFICULTY >= 2:
                game.get_game().player.hp_sys.effect(effects.Freezing(constants.DIFFICULTY * 3 - 5, 1))
            game.get_game().player.hp_sys.enable_immune()
            self.hp_sys.hp = 0

class ToxicIntestine(entity.Entities.WormEntity):
    NAME = 'Toxic Intestine'
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('clear_icy_prism', .04, 1, 1),
        entity.IndividualLoot('turbid_icy_prism', .04, 1, 1),
    ])

    def __init__(self, pos, length=15):
        super().__init__(pos, length, game.get_game().graphics['entity3_intestine'],
                         game.get_game().graphics['entity3_intestine'], entity.DestroyerAI, length * 400,
                         60, 140)
        self.obj.SPEED *= 1.5
        self.obj.MASS /= 1.5

class ToxicLargeIntestine(entity.Entities.WormEntity):
    NAME = 'Toxic Large Intestine'
    IS_MENACE = True
    BOSS_NAME = 'Pure Natural'
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('carrion', 1, 10, 20),
        entity.SelectionLoot([('intestinal_sword', 0, 1), ('organ_bullet', 0, 1000), ('organ_wand', 0, 1)], 0, 1),
    ])
    SOUND_SPAWN = 'boss'
    SOUND_HURT = 'metal'
    SOUND_DEATH = 'sticky'

    def __init__(self, pos, length=60):
        length = int(length * [0.5, 1, 2, 3.5][constants.DIFFICULTY])
        super().__init__(pos, length, game.get_game().graphics['entity3_large_intestine'],
                         game.get_game().graphics['entity3_large_intestine'], entity.DestroyerAI, length * 1000,
                         120, 220)
        s = 0
        self.obj.SPEED *= 1.5
        for e in self.body:
            e.hp_sys = hp_system.HPSystem(self.hp_sys.max_hp // length)
            e.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 60
            e.hp_sys.defenses[damages.DamageTypes.PIERCING] = 60
            e.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 60
            e.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 100
            e.hp_sys.defenses[damages.DamageTypes.HALLOW] = 100
            e.hp_sys.defenses[damages.DamageTypes.PACIFY] = 100
            e.show_bar = True
        self.body[0].hp_sys.max_hp = 1
        self.body[0].hp_sys.hp = 1
        for e in self.body:
            s += e.hp_sys.max_hp
        self.hp_sys.max_hp = s
        self.hp_sys.hp = s

    def t_draw(self):
        s = 0
        for i, b in enumerate(self.body):
            s += b.hp_sys.hp
            if 2 < b.hp_sys.hp < b.hp_sys.max_hp * .2:
                b.hp_sys.damage(9999, damages.DamageTypes.TRUE)
                ax, ay = vector.polar_to_cartesian(random.randint(0, 360), 300)
                game.get_game().entities.append(ToxicIntestine((b.obj.pos[0] + ax, b.obj.pos[1] + ay)))
                b.show_bar = False
                b.hp_sys.hp = 0
                b.img = game.get_game().graphics['entity3_large_intestine_used']
                b.set_rotation(self.rot)
            b.hp_sys.hp = max(1, b.hp_sys.hp)
        self.hp_sys.hp = s if s > 70 else 0
        super().t_draw()

class HGoblinFighter(entity.Entities.HeavenGoblinFighter):
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('heaven_wood', .3, 10, 20),
        entity.IndividualLoot('heaven_metal_helmet', .06, 1, 1),
        entity.IndividualLoot('heaven_metal_plate_mail', .06, 1, 1),
        entity.IndividualLoot('heaven_metal_leggings', .06, 1, 1),
        entity.IndividualLoot('shotgun', 0.04, 1, 1),
        entity.IndividualLoot('holy_condense_wand', 0.03, 1, 1),
        entity.IndividualLoot('holy_shine', 0.03, 1, 1),
        entity.IndividualLoot('heaven_amulet', .05, 1, 1),
        entity.IndividualLoot('angry_hat', .01, 1, 1),
        entity.IndividualLoot('happy_bottle', .01, 1, 1),
        entity.IndividualLoot('brass_knuckles', .01, 1, 1),
        entity.IndividualLoot('skyflower', .04, 1, 1),
        entity.IndividualLoot('heaven_trident', .08, 1, 1),
    ])
    SOUND_HURT = 'goblin'
    SOUND_DEATH = 'monster'

    def __init__(self, pos):
        super().__init__(pos)
        self.hp_sys.max_hp *= 5
        self.hp_sys.hp *= 5
        for k in self.hp_sys.resistances.resistances.keys():
            self.hp_sys.resistances[k] *= .8
            self.hp_sys.defenses[k] += 30
        self.obj.TOUCHING_DAMAGE += 80

class HGoblinRanger(entity.Entities.HeavenGoblinRanger):
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('heaven_wood', .3, 10, 20),
        entity.IndividualLoot('heaven_metal_helmet', .03, 1, 1),
        entity.IndividualLoot('heaven_metal_plate_mail', .03, 1, 1),
        entity.IndividualLoot('heaven_metal_leggings', .03, 1, 1),
        entity.IndividualLoot('shotgun', 0.08, 1, 1),
        entity.IndividualLoot('holy_condense_wand', 0.03, 1, 1),
        entity.IndividualLoot('holy_shine', 0.03, 1, 1),
        entity.IndividualLoot('heaven_amulet', .05, 1, 1),
        entity.IndividualLoot('angry_hat', .01, 1, 1),
        entity.IndividualLoot('happy_bottle', .01, 1, 1),
        entity.IndividualLoot('brass_knuckles', .01, 1, 1),
        entity.IndividualLoot('skyflower', .04, 1, 1),
        entity.IndividualLoot('heaven_trident', .08, 1, 1),
    ])

    def __init__(self, pos):
        super().__init__(pos)
        self.hp_sys.max_hp *= 5
        self.hp_sys.hp *= 5
        for k in self.hp_sys.resistances.resistances.keys():
            self.hp_sys.resistances[k] *= .8
        self.obj.SIGHT_DISTANCE *= 4

class HGoblinThief(entity.Entities.HeavenGoblinThief):
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('heaven_wood', .3, 10, 20),
        entity.IndividualLoot('heaven_metal_helmet', .03, 1, 1),
        entity.IndividualLoot('heaven_metal_plate_mail', .03, 1, 1),
        entity.IndividualLoot('heaven_metal_leggings', .03, 1, 1),
        entity.IndividualLoot('shotgun', 0.04, 1, 1),
        entity.IndividualLoot('holy_condense_wand', 0.03, 1, 1),
        entity.IndividualLoot('holy_shine', 0.03, 1, 1),
        entity.IndividualLoot('heaven_amulet', .05, 1, 1),
        entity.IndividualLoot('angry_hat', .01, 1, 1),
        entity.IndividualLoot('happy_bottle', .01, 1, 1),
        entity.IndividualLoot('brass_knuckles', .01, 1, 1),
        entity.IndividualLoot('skyflower', .04, 1, 1),
        entity.IndividualLoot('heaven_trident', .08, 1, 1),
    ])
    SOUND_HURT = 'goblin'
    SOUND_DEATH = 'monster'

    def __init__(self, pos):
        super().__init__(pos)
        self.hp_sys.max_hp *= 5
        self.hp_sys.hp *= 5
        for k in self.hp_sys.resistances.resistances.keys():
            self.hp_sys.resistances[k] *= .8
        self.obj.SIGHT_DISTANCE *= 2
        self.obj.SPEED *= 1.5
        self.obj.TOUCHING_DAMAGE += 30

class HOrge(entity.Entities.Orge):
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('heaven_wood', 1, 20, 40),
        entity.IndividualLoot('heaven_metal_helmet', .1, 1, 1),
        entity.IndividualLoot('heaven_metal_plate_mail', .1, 1, 1),
        entity.IndividualLoot('heaven_metal_leggings', .1, 1, 1),
        entity.IndividualLoot('shotgun', 0.15, 1, 1),
        entity.IndividualLoot('holy_condense_wand', 0.1, 1, 1),
        entity.IndividualLoot('holy_shine', 0.1, 1, 1),
        entity.IndividualLoot('skyflower', .12, 1, 1),
        entity.SelectionLoot([('happy_bottle', 0, 1), ('angry_hat', 0, 1), ('brass_knuckles', 0, 1)], 1, 1),
        entity.SelectionLoot([('wingblade', 0, 1), ('skyfire', 0, 1), ('wingknock', 0, 1)], 1, 1),
        ])
    SOUND_HURT = 'goblin'
    SOUND_DEATH = 'monster'
    IS_MENACE = True
    BOSS_NAME = ''

    def __init__(self, pos):
        super().__init__(pos)
        for k in self.hp_sys.resistances.resistances.keys():
            self.hp_sys.resistances[k] *= .5
        self.obj.SIGHT_DISTANCE *= 4
        self.obj.SPEED *= 1.5
        self.obj.TOUCHING_DAMAGE += 50

class BombardinoCrocodilo(entity.Entities.Entity):
    NAME = 'Bombardino Crocodilo'
    SOUND_HURT = 'metal'
    SOUND_DEATH = 'explosive'
    DISPLAY_MODE = 2
    IS_MENACE = True
    BOSS_NAME = 'Boom Boom Boom'
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('amber_card', .4, 1, 6),
        entity.IndividualLoot('hightech_steel_sword', .4, 1, 1),
        ])
    PHASE_SEGMENTS = [.2, .5]

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity3_bombardino_crocodilo'], BombardinoCrocodiloAI, hp=9000)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 220
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 250
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 200
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 150
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 300
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 150
        for r in self.hp_sys.resistances.resistances.keys():
            self.hp_sys.resistances[r] *= .8
        self.phase = 1

    def t_draw(self):
        super().t_draw()
        if self.hp_sys.hp <= 1:
            if self.hp_sys.max_hp > 1:
                self.hp_sys.hp = 1
                self.obj.IS_OBJECT = False
                self.obj.SPEED = 0.000001
                self.hp_sys.max_hp = 1
                self.PHASE_SEGMENTS = [.2, .4, .6, .8]
                self.hp_sys.MAXIMUM_DAMAGE = 0
                self.hp_sys.MINIMUM_DAMAGE = 0
                self.NAME = 'Bombardino Crocodilo (Dead)'
                self.phase = 4
            else:
                self.hp_sys.hp -= .0005

    def on_update(self):
        super().on_update()
        self.set_rotation(-self.obj.velocity.get_net_rotation())
        if self.phase == 1 and self.hp_sys.hp < self.hp_sys.max_hp * .5:
            self.phase = 2
            self.obj.SPEED *= 2
            for r in self.hp_sys.resistances.resistances.keys():
                self.hp_sys.resistances[r] *= .8
                self.hp_sys.defenses[r] += 50
            self.obj.TOUCHING_DAMAGE += 50
        if self.phase == 2 and self.hp_sys.hp < self.hp_sys.max_hp * .2:
            self.phase = 3
            self.obj.SPEED *= 2
            for r in self.hp_sys.resistances.resistances.keys():
                self.hp_sys.resistances[r] *= .3
                self.hp_sys.defenses[r] -= 300
            self.obj.TOUCHING_DAMAGE += 100
        self.hp_sys.hp -= [0, 0, .25, 1, 0][self.phase]

class ChaosBomb(entity.Entities.Entity):
    NAME = 'Chaos Bomb'
    DIVERSITY = False

    def __init__(self, pos, rot, action=0, dmg=50, drr=False):
        super().__init__(pos, game.get_game().graphics['entity_null'], entity.BuildingAI, hp=1)
        self.mp = []
        self.action = action
        self.rot = rot
        self.obj.MASS = 30
        self.obj.FRICTION = .92
        self.dmg = dmg
        self.drr = drr
        self.obj.IS_OBJECT = False
        self.tick = 0

        if constants.DIFFICULTY == 3:
            self.hp_sys.max_hp *= 2

        if action in [1, 3]:
            self.obj.apply_force(vector.Vector2D(rot, 1500))


    def t_draw(self):
        self.tick += 1
        self.mp.append(self.obj.pos.to_value())
        self.obj.update()
        if len(self.mp) > [15, 15, 20, 30][constants.DIFFICULTY]:
            self.mp.pop(0)
        for i in range(len(self.mp) - 1):
            draw.line(game.get_game().displayer.canvas, (255 * i // len(self.mp) * (not self.drr), 0, 255 * i // len(self.mp) * self.drr), position.displayed_position(self.mp[i]),
                      position.displayed_position(self.mp[i + 1]), i * (10 + self.drr * 20) // len(self.mp) + 1)
        if self.drr:
            pg.draw.circle(game.get_game().displayer.canvas, (0, 0, 255), position.displayed_position(self.obj.pos), 15)
        if self.action in [0, 2]:
            self.obj.apply_force(vector.Vector2D(self.rot, 300 if not self.action else 100))
        elif self.action in [1, 3]:
            self.obj.FRICTION = 1.01
            ap = game.get_game().player.obj.pos - self.obj.pos
            ap = ap / abs(ap)
            self.obj.apply_force(ap * (100 if constants.DIFFICULTY < 3 else 150))
        self.hp_sys.hp -= .005
        for i in range(0, len(self.mp), 4):
            game.get_game().displayer.point_light((255, 100, 100) if not self.drr else (100, 100, 255), position.displayed_position(self.mp[i]), 3, 10 + i * 3)
            if vector.distance(*(game.get_game().player.obj.pos - self.mp[i])) < 100:
                game.get_game().player.hp_sys.max_hp = max(20, game.get_game().player.hp_sys.max_hp - self.dmg * (1 + self.drr * 4) // [50, 20, 10, 8][constants.DIFFICULTY])
                if self.action != 3:
                    game.get_game().player.hp_sys.damage(self.dmg * (0.5 if not self.drr else 4), damages.DamageTypes.MAGICAL, penetrate=self.dmg * 5)
                self.hp_sys.hp = 0


class ChaosDisciple(entity.Entities.Entity):
    NAME = '??????'
    CHAOS = True
    BOSS_NAME = '??????'
    LOOT_TABLE = entity.LootTable([
        ])
    DISPLAY_MODE = 1
    PHASE_SEGMENTS = [.9999, .99995]
    DIVERSITY = False

    DEFEATED = False

    def __init__(self, pos):
        self.rr = game.get_game().player.inventory.is_enough(inventory.ITEMS['dark_matter'])

        self.PHASE_SEGMENTS = [.9999, .99995]
        game.get_game().player.hp_sys.effect(effects.ExtremeTerror(10 ** 8, 1))
        super().__init__(pos, game.get_game().graphics['entity3_chaos_disciple'], entity.BuildingAI,
                         hp=12 * 10 ** 9)
        for r in self.hp_sys.resistances.resistances.keys():
            self.hp_sys.resistances[r] *= 91 if not self.rr else 23
            self.hp_sys.defenses[r] = 0
        self.hp_sys.DODGE_RATE = .8 if not self.rr else .1
        self.hp_sys.IMMUNE = True
        self.tick = 0
        self.phase = -1

        self.state = 0

        self.obj.MASS = 100
        self.obj.FRICTION = .95
        self.obj.SIGHT_DISTANCE = 9999
        self.obj.TOUCHING_DAMAGE = 250
        self.dp1 = []
        self.dp2 = []
        self.dp3 = []
        self.dp4 = []

        self.pjs = []
        self.ddp = (0, 0)
        self.dr = 100
        game.get_game().player.hp_sys.max_hp = 250 + self.rr * 1250

    def t_draw(self):
        if self.phase != 4:
            self.obj.velocity.restrict(-20, 20)
        for p in self.pjs:
            if p.hp_sys.hp <= 0:
                self.pjs.remove(p)
            else:
                p.t_draw()
        self.obj.TOUCHING_DAMAGE = game.get_game().player.hp_sys.max_hp * .6
        self.dp1.append(self.obj.pos + vector.Vector2D(self.rot, self.dr))
        self.dp2.append(self.obj.pos + vector.Vector2D(self.rot, -self.dr))
        self.dp3.append(self.obj.pos + vector.Vector2D(self.rot + 90, self.dr))
        self.dp4.append(self.obj.pos + vector.Vector2D(self.rot - 90, self.dr))
        if len(self.dp1) > 20:
            self.dp1.pop(0)
            self.dp2.pop(0)
            self.dp3.pop(0)
            self.dp4.pop(0)
        for i in range(len(self.dp1) - 1):
            draw.line(game.get_game().displayer.canvas,
                      (255 * i / len(self.dp1), 255 * i / len(self.dp1), 255 * i / len(self.dp1)),
                      position.displayed_position(self.dp1[i]), position.displayed_position(self.dp1[i + 1]), i + 1)
            draw.line(game.get_game().displayer.canvas,
                      (255 - 255 * i / len(self.dp1), 255 - 255 * i / len(self.dp1), 255 - 255 * i / len(self.dp1)),
                      position.displayed_position(self.dp2[i]), position.displayed_position(self.dp2[i + 1]), i + 1)
            if self.rr:
                draw.line(game.get_game().displayer.canvas,
                          (100 * i / len(self.dp1), 0, 0),
                          position.displayed_position(self.dp3[i]), position.displayed_position(self.dp3[i + 1]), i + 1)
                draw.line(game.get_game().displayer.canvas,
                          (0, 0, 100 * i / len(self.dp1)),
                          position.displayed_position(self.dp4[i]), position.displayed_position(self.dp4[i + 1]), i + 1)
        pg.draw.circle(game.get_game().displayer.canvas, (255, 255, 255), position.displayed_position(self.dp1[-1]), 10)
        pg.draw.circle(game.get_game().displayer.canvas, (0, 0, 0), position.displayed_position(self.dp2[-1]), 10)
        if self.rr:
            pg.draw.circle(game.get_game().displayer.canvas, (100, 0, 0), position.displayed_position(self.dp3[-1]), 10)
            pg.draw.circle(game.get_game().displayer.canvas, (0, 0, 100), position.displayed_position(self.dp4[-1]), 10)
        if self.phase == -1:
            self.phase = 0
            if not self.DEFEATED:
                if self.rr:

                    game.get_game().dialog.dialog('...ARRAYER...', '...I FEEL THE POWER OF IT...',
                                                  '...THE \'DARK\' MATTER...', '...INTERESTING...',
                                                  '...YOU HAVE THE CHANCE TO MAKE ME TREAT YOU..',
                                                  '...A BIT MORE FOCUSED!')
                else:
                    game.get_game().dialog.dialog('...', '...A...AN...ARRAYER?...', '...INTERESTING...',
                                                  '...AND..SELECTED...BY...UNDERIA...?', '...HEH...HEH...HEH...',
                                                  '...GREAT...', '...THEN...GO...ON...', '...AND BE KILLED!..')

        elif self.phase == 0 and game.get_game().dialog.is_done():
            self.IS_MENACE = True
            self.hp_sys.IMMUNE = False
        if self.phase == 0:
            if game.get_game().dialog.is_done():
                if self.tick % 250 == 0:
                    self.state = (self.state + 1) % 4
                self.obj.velocity.restrict(-15, 15)
                self.obj.get_target()
                if self.obj.cur_target is not None:
                    ap = self.obj.cur_target.pos - self.obj.pos
                    ap = ap / abs(ap)
                    if self.state == 0:
                        self.obj.pos += ap * (20 + 20 * math.sin(math.radians(self.rot)))
                        if self.tick % 30 == 0:
                            self.pjs.append(ChaosBomb(self.obj.pos, self.rot, 1, 50, drr=self.rr))
                    elif self.state == 1:
                        if self.tick % int(50 - 30 * math.sin(math.radians(self.rot))) == 0:
                            self.play_sound('create')
                            ar = vector.Vector2D(random.randint(0, 360), 800)
                            self.obj.pos = game.get_game().player.obj.pos + ar
                            self.obj.velocity = -ar / 20
                            aar = random.randint(0, 60)
                            for r in range(0, 360, 360 // int(4 + 2 * math.sin(self.rot))):
                                self.pjs.append(ChaosBomb(self.obj.pos, r + aar, 2, 50, drr=self.rr))
                    elif self.state == 2:
                        self.obj.pos = game.get_game().player.obj.pos + (math.sin(math.radians(self.rot)) * 200, -1200)
                        if self.tick % 20 == 0:
                            ap = game.get_game().player.obj.pos - self.obj.pos
                            self.pjs.append(ChaosBomb(self.obj.pos, vector.coordinate_rotation(*ap), 0, 50, drr=self.rr))
                    elif self.state == 3:
                        if self.tick % 10 == 0:
                            for r in range(int(self.rot), int(self.rot) + 360, 90):
                                self.pjs.append(ChaosBomb(self.obj.pos, r, 0, 50, drr=self.rr))
                    else:
                        pass
            else:
                self.obj.pos = game.get_game().player.obj.pos + (0, -500)
        elif self.phase == 2:
            if self.tick % 160 == 0:
                self.state = (self.state + random.randint(0, 2)) % 5
            self.obj.velocity.restrict(-5, 5)
            self.obj.get_target()
            if self.obj.cur_target is not None:
                ap = self.obj.cur_target.pos - self.obj.pos
                ap = ap / abs(ap)
                if self.state == 0:
                    self.obj.pos += ap * (40 + 20 * math.sin(math.radians(self.rot)))
                    if self.tick % 30 == 0:
                        for _ in range(4):
                            self.pjs.append(ChaosBomb(self.obj.pos, random.randint(0, 360), 1, 60, drr=self.rr))
                elif self.state == 1:
                    if self.tick % int(30 - 10 * math.sin(math.radians(self.rot))) == 0:
                        self.play_sound('create')
                        ar = vector.Vector2D(random.randint(0, 360), 500)
                        self.obj.pos = game.get_game().player.obj.pos + ar
                        self.obj.velocity = -ar / 20
                        aar = random.randint(0, 60)
                        for r in range(0, 360, 360 // [2, 3, 4, 5, 6, 9][int(4 + 2 * math.sin(self.rot))]):
                            self.pjs.append(ChaosBomb(self.obj.pos, r + aar, 2, 60, drr=self.rr))
                elif self.state == 2:
                    self.obj.pos = game.get_game().player.obj.pos + (math.sin(math.radians(self.rot)) * 800, -1500)
                    if self.tick % 30 == 0:
                        ap = game.get_game().player.obj.pos - self.obj.pos
                        for ar in range(-60, 61, 30):
                            self.pjs.append(ChaosBomb(self.obj.pos, ar + vector.coordinate_rotation(*ap), 0, 60, drr=self.rr))
                elif self.state == 3:
                    if self.tick % 15 == 0:
                        for r in range(int(self.rot), int(self.rot) + 360, 72):
                            self.pjs.append(ChaosBomb(self.obj.pos, r, 0, 60, drr=self.rr))
                else:
                    aap = vector.Vector2D(180 + self.rot, 1500)
                    self.obj.pos = vector.Vector2D(0, 0, *self.ddp) + aap
                    if self.tick % 5 == 0:
                        self.pjs.append(ChaosBomb(self.obj.pos, self.rot, 2, 40))
                        for ar in range(90, 271, 30):
                            self.pjs.append(ChaosBomb(self.obj.pos, self.rot + ar, 0, 80, drr=self.rr))
                if self.state != 4:
                    self.ddp = game.get_game().player.obj.pos.to_value()
        self.tick += 1
        if self.phase == 0 and self.hp_sys.hp < self.hp_sys.max_hp * self.PHASE_SEGMENTS[-1] - 1:
            self.hp_sys.hp = self.hp_sys.max_hp * self.PHASE_SEGMENTS[-1] - 1
            self.phase = 1
            self.hp_sys.IMMUNE = True
            if not self.DEFEATED:
                game.get_game().dialog.dialog('INTEREST..ING...', 'VERY INTERESTING...')
                ChaosDisciple.DEFEATED = True
        if self.phase == 1:
            if game.get_game().player.hp_sys.max_hp <= 500 + self.rr * 2000:
                game.get_game().player.hp_sys.max_hp = min(game.get_game().player.hp_sys.max_hp + 1 + self.rr * 19, 500 + self.rr * 2000)
            else:
                game.get_game().player.hp_sys.heal(2 + self.rr * 8)
            self.hp_sys.heal(1000)
            if self.tick % 20 == 0:
                rr = random.randint(0, 360)
                self.pjs.append(ChaosBomb(self.obj.pos + vector.Vector2D(rr, 2000), rr + 180,
                                          2, 70, drr=self.rr))
            if self.hp_sys.hp >= self.hp_sys.max_hp and game.get_game().dialog.is_done():
                self.hp_sys.IMMUNE = False
                self.phase = 2
                self.hp_sys.DODGE_RATE = 0
                for d in self.hp_sys.defenses.defences.keys():
                    self.hp_sys.defenses[d] += 1000
                    self.hp_sys.resistances[d] /= 3
                for i in range(0, 360, 20):
                    self.pjs.append(ChaosBomb(self.obj.pos, i, 1, 60, drr=self.rr))
                self.PHASE_SEGMENTS.pop(-1)
        if self.phase == 2 and self.hp_sys.hp < self.hp_sys.max_hp * self.PHASE_SEGMENTS[-1]:
            self.phase = 3 if constants.DIFFICULTY > 1 else 4
            self.obj.IS_OBJECT = False
            self.tick = 0
            self.PHASE_SEGMENTS.pop(-1)
            self.hp_sys.max_hp = self.hp_sys.hp
            self.PHASE_SEGMENTS.append((self.hp_sys.max_hp - 1) / self.hp_sys.max_hp)
        if self.phase == 3:
            self.hp_sys.hp = self.PHASE_SEGMENTS[-1] * self.hp_sys.max_hp + (1500 - self.tick) / 1500
            self.dr = (self.dr + 3500 - self.tick) // 2
            self.obj.MASS = (self.obj.MASS + 10 ** 7) // 2
            if self.tick > 30:
                pp = game.get_game().player.obj.pos - self.obj.pos
                if abs(pp) > self.dr:
                    pp = pp / abs(pp) * self.dr
                game.get_game().player.obj.pos = self.obj.pos + pp
            game.get_game().player.hp_sys.max_hp = 500
            if self.tick % 2 == 0:
                self.pjs.append(ChaosBomb(self.obj.pos, random.randint(0, 360), 1, 100, drr=self.rr))
            if self.tick > 1500:
                self.phase = 4
                game.get_game().player.hp_sys.max_hp = 200
                game.get_game().player.hp_sys.effects.clear()
                for __ in range(1 + 3 * self.rr):
                    cc = random.choice(['shard_of_create', 'shard_of_destroy'])
                    for _ in range(4 - 3 * self.rr):
                        game.get_game().drop_items.append(entity.Entities.DropItem(self.obj.pos, cc, random.randint(8, 12) * (1 + self.rr)))
                if constants.DIFFICULTY >= 2:
                    for k in random.choices(['abyss_ranseur', 'abyss_gaze', 'abyss_fury'], k=constants.DIFFICULTY - 1):
                        game.get_game().drop_items.append(entity.Entities.DropItem(self.obj.pos, k, 1))
        if self.phase == 4:
            # leave
            self.dr = (self.dr + 100) // 2
            self.obj.MASS = 100
            self.obj.apply_force(vector.Vector2D(dy=-1000))
            if self.tick > 1600:
                game.get_game().entities.remove(self)
        if self.tick % 5 == 0:
            self.NAME = random.choice(['Chaos Disciple', '?????', 'Chaos Chaos Chaos Chaos', 'Unknown',
                                       'Unnameable', 'Chaotic', 'Unseen', 'Foreign Dimension', '...'])
        if constants.DIFFICULTY >= 1:
            self.rotate(math.sin(self.tick / 50) * 20)
        else:
            self.rotate(10)
        super().t_draw()

class RuneAltar(entity.Entities.Entity):
    DIVERSITY = False
    DISPLAY_MODE = 2
    NAME = 'Rune Altar'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity3_rune_altar'], entity.BuildingAI, hp=1000000)
        self.hp_sys.IMMUNE = True

    def on_update(self):
        super().on_update()
        if vector.distance(*(game.get_game().player.obj.pos - self.obj.pos)) < 400:
            game.get_game().player.hp_sys.effect(effects.RuneAltar(1, 1))

class AncientStone(entity.Entities.Entity):
    DIVERSITY = False
    DISPLAY_MODE =  2
    NAME = 'Ancient Stone'
    SOUND_HURT = 'ore'
    SOUND_DEATH = 'ore'

    LOOT_TABLE = entity.LootTable([
        entity.SelectionLoot([('null', 0, 0)], 1, 1),
    ])

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity3_ancient_stone'], entity.BuildingAI, hp=1500)
        for d in self.hp_sys.defenses.defences.keys():
            self.hp_sys.defenses[d] += 499
        if 'life_devourer' in game.get_game().player.owned_items:
            self.LOOT_TABLE.loot_list[0].selection_max += random.randint(0, 1)
            self.LOOT_TABLE.loot_list[0].items.append(('lost__growth_eater', 1, 1))
        if 'galaxy_broadsword' in game.get_game().player.owned_items:
            self.LOOT_TABLE.loot_list[0].selection_max += random.randint(0, 1)
            self.LOOT_TABLE.loot_list[0].items.append(('lost__star_broadsword', 1, 1))

class RuneGuard(entity.Entities.Entity):
    DISPLAY_MODE = 1
    NAME = 'Rune Guard'
    SOUND_DEATH = 'explosive'
    SOUND_HURT = 'metal'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity3_rune_guard'], entity.EyeAI, hp=1100)
        self.obj.SPEED *= 180
        self.obj.MASS *= 25
        self.obj.SIGHT_DISTANCE = 6000
        self.obj.TOUCHING_DAMAGE = 220
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 199
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 199
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 149
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 99
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 299
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 99
        if game.get_game().dimension == 'ancient_city':
            self.obj.SPEED *= 1.2
            self.obj.SIGHT_DISTANCE *= 2
            self.obj.TOUCHING_DAMAGE += 250
            self.hp_sys.max_hp *= 2
            self.hp_sys.hp = self.hp_sys.max_hp
            self.LOOT_TABLE = entity.LootTable([
                entity.IndividualLoot('ancient_rune_shard', 1, 5, 10),
            ])

    def on_update(self):
        super().on_update()
        self.set_rotation(-self.obj.velocity.get_net_rotation())

class RuneFlower(entity.Entities.Entity):
    DISPLAY_MODE = 2
    NAME = 'Rune Flower'
    SOUND_DEATH = 'explosive'
    SOUND_HURT = 'metal'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity3_rune_flower'], entity.SoulFlowerAI, hp=1200)
        self.obj.FRICTION -= 0.01
        self.obj.MASS *= 25
        self.obj.SPEED *= 45
        self.obj.SIGHT_DISTANCE = 4000
        self.obj.TOUCHING_DAMAGE = 230
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 169
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 169
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 119
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 69
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 269
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 69
        if game.get_game().dimension == 'ancient_city':
            self.obj.SPEED *= 1.2
            self.obj.SIGHT_DISTANCE *= 2
            self.obj.TOUCHING_DAMAGE += 250
            self.hp_sys.max_hp *= 2
            self.hp_sys.hp = self.hp_sys.max_hp
            self.LOOT_TABLE = entity.LootTable([
                entity.IndividualLoot('ancient_rune_shard', 1, 5, 10),
            ])

class EliteChicken(Chicken):
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_feather', .3, 5, 25),
        entity.SelectionLoot([('feather_of_sing', 1, 2), ('feather_of_dance', 1, 2), ('feather_of_rap', 1, 2), ('feather_of_basketball', 1, 2)], 1, 2),
        entity.IndividualLoot('feather_sword', .02, 1, 1),
        entity.IndividualLoot('dark_distortion', .01, 1, 1),
        ])

    def __init__(self, pos):
        super(Chicken, self).__init__(pos, game.get_game().graphics[f'entity3_elite_chicken'], ChickenAI, hp=1400)
        self.obj.MASS *= 15
        self.obj.SPEED *= 25
        self.obj.SIGHT_DISTANCE = 8000
        self.obj.TOUCHING_DAMAGE = 500
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 39
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 39
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 49
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 49
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 69
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 49
        self.hp_sys.DODGE_RATE += .01

class ChickenSinger(Chicken):
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_feather', .3, 5, 25),
        entity.IndividualLoot('feather_of_sing', 1, 4, 8),
        entity.IndividualLoot('feather_sword', .02, 1, 1),
        entity.IndividualLoot('dark_distortion', .01, 1, 1),
        entity.IndividualLoot('feather_of_basketball', .05, 10, 40),
        ])

    NAME = 'Chicken Singer'

    def __init__(self, pos):
        super(Chicken, self).__init__(pos, game.get_game().graphics[f'entity3_chicken_singer'], ChickenAI, hp=1000)
        self.obj.MASS *= 15
        self.obj.SPEED *= 25
        self.obj.SIGHT_DISTANCE = 10000
        self.obj.TOUCHING_DAMAGE = 450
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 39
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 39
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 49
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 49
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 69
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 49
        self.hp_sys.DODGE_RATE += .01

        self.ds = 0
        self.tick = 0
        self.ps = []

    def on_update(self):
        self.tick += 1
        self.ds = max(int(math.sin(self.tick / 25) * 500 + 300), 0)
        super().on_update()
        if self.ds:
            for e in game.get_game().entities:
                if e not in self.ps and abs(e.obj.pos - self.obj.pos) < self.ds:
                    self.ps.append(e)
                    e.obj.TOUCHING_DAMAGE *= 1.2
                    e.hp_sys.DODGE_RATE += .03
                    e.obj.SPEED *= 1.2
                    e.obj.SIGHT_DISTANCE *= 2
                if e in self.ps and abs(e.obj.pos - self.obj.pos) > self.ds:
                    self.ps.remove(e)
                    e.obj.TOUCHING_DAMAGE /= 1.2
                    e.hp_sys.DODGE_RATE -= .03
                    e.obj.SPEED /= 1.2
                    e.obj.SIGHT_DISTANCE /= 2

    def t_draw(self):
        if self.ds:
            pg.draw.circle(game.get_game().displayer.canvas, (0, 255, 255), position.displayed_position(self.obj.pos),
                           self.ds / game.get_game().player.get_screen_scale(), 2)
        super().t_draw()

class ChickenDancer(Chicken):
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_feather', .3, 5, 25),
        entity.IndividualLoot('feather_of_dance', 1, 4, 8),
        entity.IndividualLoot('feather_sword', .02, 1, 1),
        entity.IndividualLoot('dark_distortion', .01, 1, 1),
        entity.IndividualLoot('feather_of_basketball', .05, 10, 40),
        ])

    NAME = 'Chicken Dancer'

    def __init__(self, pos):
        super(Chicken, self).__init__(pos, game.get_game().graphics[f'entity3_chicken_dancer'], ChickenAI, hp=1500)
        self.obj.MASS *= 15
        self.obj.SPEED *= 45
        self.obj.SIGHT_DISTANCE = 10000
        self.obj.TOUCHING_DAMAGE = 500
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 39
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 39
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 49
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 49
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 69
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 49
        self.hp_sys.DODGE_RATE += .01

    def on_update(self):
        self.obj.TOUCHING_DAMAGE = 600 - int(self.hp_sys.hp / self.hp_sys.max_hp * 100)
        super().on_update()

class ChickenRapper(Chicken):
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_feather', .3, 5, 25),
        entity.IndividualLoot('feather_of_rap', 1, 4, 8),
        entity.IndividualLoot('feather_sword', .02, 1, 1),
        entity.IndividualLoot('dark_distortion', .01, 1, 1),
        entity.IndividualLoot('feather_of_basketball', .05, 10, 40),
        ])

    NAME = 'Chicken Rapper'

    def __init__(self, pos):
        super(Chicken, self).__init__(pos, game.get_game().graphics[f'entity3_chicken_rapper'], ChickenAI, hp=1300)
        self.obj.MASS *= 15
        self.obj.SPEED *= 25
        self.obj.SIGHT_DISTANCE = 8000
        self.obj.TOUCHING_DAMAGE = 530
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 39
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 39
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 49
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 49
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 69
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 49
        self.hp_sys.DODGE_RATE += .02

        self.ds = 0
        self.tick = 0

    def on_update(self):
        self.tick += 1
        self.ds = max(int(math.sin(self.tick / 25) * 1000 + 1200), 0)
        super().on_update()
        if abs(self.obj.pos - game.get_game().player.obj.pos) > self.ds:
            self.hp_sys.IMMUNE = True
        else:
            self.hp_sys.IMMUNE = False

    def t_draw(self):
        if self.ds:
            pg.draw.circle(game.get_game().displayer.canvas, (0, 255, 0) if not self.hp_sys.IMMUNE else (255, 0, 255), position.displayed_position(self.obj.pos),
                           self.ds / game.get_game().player.get_screen_scale(), 2 * (not self.hp_sys.IMMUNE))
        super().t_draw()

class DeathWhisperChickenAI(entity.MonsterAI):
    IS_OBJECT = True
    MASS = 1200
    FRICTION = .93
    TOUCHING_DAMAGE = 700
    SIGHT_DISTANCE = 99999

    def __init__(self, *args):
        super().__init__(*args)
        self.state = 0
        self.cc = 300
        self.tick = 0
        self.tp = vector.Vector2D()
        self.lp = vector.Vector2D()
        self.pp = vector.Vector2D()
        self.op = vector.Vector2D()
        self.nr = False
        self.dd = 2000 + constants.DIFFICULTY * 500
        self.wh = []

    def on_update(self):
        tar = self.cur_target
        if self.tick < self.cc:
            self.op = self.pos.to_value()
            if tar is not None:
                self.pp = (tar.pos + self.pp * 12) / 13
                rr = vector.coordinate_rotation(*(self.pp - self.pos))
                self.tp = self.pos + vector.Vector2D(rr, self.dd)
                self.nr = abs(self.pp - self.pos) > self.dd
        elif self.tick < self.cc + 20:
            self.pos = (self.tp + self.pos * 6) / 7
        else:
            if tar is not None:
                ap = tar.pos - self.op
                if self.nr:
                    if abs(ap) < self.dd:
                        tar.pos = vector.Vector2D() + self.op + ap / abs(ap) * self.dd
                    if abs(ap) > self.dd * 2:
                        tar.pos = vector.Vector2D() + self.op + ap / abs(ap) * self.dd * 2
                else:
                    if abs(ap) > self.dd:
                        tar.pos = vector.Vector2D() + self.op + ap / abs(ap) * self.dd
                self.pp = (tar.pos + self.pp * 21) / 22
            self.apply_force(vector.Vector2D(vector.coordinate_rotation(*(self.pp - self.pos)), 9000))
            if random.randint(0, self.tick - self.cc) > self.cc * 7 // 2:
                self.IS_OBJECT = True
                self.tick = 0
            else:
                if self.tick % 5 == 0:
                    self.IS_OBJECT = random.randint(0, 1)
        self.tick += 1


class DeathWhisper(Entity):
    DISPLAY_MODE = 0
    DIVERSITY = False

    def __init__(self, pos, rot=0, action=0):
        super().__init__(pos, game.get_game().graphics['entity3_death_whisper'], entity.BuildingAI, hp=800000)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 600
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 600
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 600
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 600
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 600
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 600
        self.action = action
        self.poss = []
        self.set_rotation(rot)
        self.st_pos = (pos[0], pos[1])
        self.bk = 0
        self.dmg = True

        self.obj.MASS = 30
        self.tick = 0
        self.obj.FRICTION = .9
        if self.action == 1:
            self.obj.FRICTION = 1.01
        elif self.action == 2:
            self.obj.FRICTION = 1
            self.obj.apply_force(vector.Vector2D(rot, 1000))

    def t_draw(self):
        self.tick += 1
        if self.action:
            self.hp_sys.hp -= self.hp_sys.max_hp * (8 - constants.DIFFICULTY) / 1500
        if self.bk:
            self.dmg = False
            self.obj.pos = (self.obj.pos * 5 + self.st_pos) / 6
            if vector.distance(*(self.obj.pos - self.st_pos)) < 200:
                self.hp_sys.hp = 0
        elif self.action == 1:
            pp = game.get_game().player.obj.pos
            self.obj.apply_force(vector.Vector2D(vector.coordinate_rotation(*(pp - self.obj.pos)), 15))
        elif self.action == 2:
            self.obj.apply_force(vector.Vector2D(-self.rot, 10))
        elif self.action == 3:
            self.obj.pos += vector.Vector2D(self.rot, 20)
            self.obj.pos += vector.Vector2D(self.rot + 90, math.sin(self.tick / 10) / 10)
        self.obj.update()
        self.poss.append(self.obj.pos.to_value())
        if len(self.poss) > 10:
            self.poss.pop(0)
        sc = len(self.poss) / 10 * (.6 + constants.DIFFICULTY * .4)
        for i in range(len(self.poss) - 1):
            draw.line(game.get_game().displayer.canvas, (i * 100 // len(self.poss), 0, 0), position.displayed_position(self.poss[i]),
                      position.displayed_position(self.poss[i+1]),
                      int(i * 40 * sc // len(self.poss) / game.get_game().player.get_screen_scale()))
        pg.draw.circle(game.get_game().displayer.canvas, (100, 0, 0),
                       position.displayed_position(self.obj.pos), int(20 * sc / game.get_game().player.get_screen_scale()))
        self.damage()

    def damage(self):
        if self.dmg:
            pp = game.get_game().player.obj.pos
            if abs(pp - self.obj.pos) < 50 * (.6 + constants.DIFFICULTY * .4):
                if self.action:
                    self.hp_sys.hp = 0
                if not game.get_game().player.hp_sys.is_immune:
                    game.get_game().player.hp_sys.damage(600, damages.DamageTypes.MAGICAL)
                    game.get_game().player.hp_sys.enable_immune()


class DeathWhisperChicken(Chicken):
    DIVERSITY = False
    CHAOS = True

    IS_MENACE = True
    NAME = 'The Death Whisper Chicken'

    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_feather', .3, 5, 10),
        entity.IndividualLoot('spot', 1, 8, 15),
    ])

    PHASE_SEGMENTS = [.2, .7]

    def __init__(self, pos):
        super(Chicken, self).__init__(pos, game.get_game().graphics[f'entity3_death_whisper_chicken'], DeathWhisperChickenAI, hp=32000)
        for r in self.hp_sys.resistances.resistances.keys():
            self.hp_sys.resistances.resistances[r] *= .3
            self.hp_sys.defenses[r] += 20
        self.phase = 0
        self.obj.tick = 0
        self.obj.cc = 300
        self.wh = []

    def draw(self):
        if self.hp_sys.hp < self.hp_sys.max_hp * 0.7 and self.phase == 0:
            self.phase = 1
            self.obj.SPEED *= 1.5
            self.obj.cc -= 80
        if self.hp_sys.hp < self.hp_sys.max_hp * 0.2 and self.phase == 1 and constants.DIFFICULTY > 1:
            self.phase = 2
            self.obj.SPEED *= 1.5
            self.obj.cc -= 80
            for r in self.hp_sys.resistances.resistances.keys():
                self.hp_sys.resistances.resistances[r] *= .3
            self.obj.dd -= 1000
        for t in self.wh:
            t.t_draw()
            if t.hp_sys.hp <= 1:
                self.wh.remove(t)
        if self.phase == 2:
            if self.obj.dd >= 3500 - constants.DIFFICULTY * 1000:
                self.obj.dd -= 15
        pg.draw.circle(game.get_game().displayer.canvas, (100, 0, 0), position.displayed_position(self.obj.tp), int(200 / game.get_game().player.get_screen_scale()), 2)
        pg.draw.circle(game.get_game().displayer.canvas, (0, 0, 0), position.displayed_position(self.obj.pp),
                       int(200 / game.get_game().player.get_screen_scale()), 2)
        if self.obj.tick == self.obj.cc + 10:
            for r in range(0, 360, 30 if self.phase < 2 else 15):
                self.wh.append(DeathWhisper(self.obj.pos, r, 3))
        if self.obj.tick > self.obj.cc + 20:
            pg.draw.circle(game.get_game().displayer.canvas, (0, 0, 0), position.displayed_position(self.obj.op),
                           int(self.obj.dd / game.get_game().player.get_screen_scale()),
                           int(min(25, self.obj.tick // 4 - self.obj.cc // 4 - 5) / game.get_game().player.get_screen_scale()) + 1)
            pg.draw.circle(game.get_game().displayer.canvas, (0, 0, 0), position.displayed_position(self.obj.op),
                           int(2 * self.obj.dd / game.get_game().player.get_screen_scale()),
                           int(min(25, self.obj.tick // 4 - self.obj.cc // 4 - 5) / game.get_game().player.get_screen_scale()) + 1)
            if self.obj.tick % 120 == 0 and self.phase >= 1 and constants.DIFFICULTY > 0:
                for r in range(0, 360, 25 - constants.DIFFICULTY * 5):
                    self.wh.append(DeathWhisper(vector.Vector2D(r, self.obj.dd) + self.obj.op, r, 1))
            elif self.obj.tick % 15 == 0:
                self.wh.append(DeathWhisper(self.obj.pos, 0, 1))


        super().draw()


class PetrifiedWitnessAI(entity.MonsterAI):
    MASS = 5000
    FRICTION = .95
    IDLE_SPEED = 12000
    IDLE_TIME = 50
    IDLE_CHANGER = 360
    SIGHT_DISTANCE = 99999
    TOUCHING_DAMAGE = 580

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = 0
        self.tick = 0
        self.phase = 0
        self.rot = 0
        self.ts = []
        self.ntd = 5
        self.tb = 0

    def on_update(self):
        super().on_update()
        self.get_target()
        self.tick += 1
        if self.cur_target is None:
            self.idle()
            return
        if self.tick < 0:
            self.rot += 14
            return
        pp: vector.Vector2D = self.cur_target.pos
        if self.tick > 300 - self.phase * 50:
            self.tick = [0, 0, -100, -200][self.state] * (10 + constants.DIFFICULTY * 2) // 10
            self.state = (self.state + 1) % min(4, 2 + self.phase)
            self.ntd = random.choice([4, 5, 6, 7, 9])
            self.tb = random.randint(0, 100)
        if self.state == 0:
            self.rot = vector.coordinate_rotation(*(pp - self.pos))
            if pp[0] < self.pos[0]:
                self.apply_force(vector.Vector2D(0, 0, *((pp + (800, 0) - self.pos) * 15)))
            else:
                self.apply_force(vector.Vector2D(0, 0, *((pp - (800, 0) - self.pos) * 15)))
        elif self.state == 1:
            if self.tick % (60 - self.phase * 6) <= (30 - self.phase * 5):
                self.rot = vector.coordinate_rotation(*(pp - self.pos))
                self.velocity /= self.phase * .02 + 1
            elif self.tick % (60 - self.phase * 6) <= (40 - self.phase * 6):
                pass
            else:
                self.apply_force(vector.Vector2D(self.rot, 45000 + self.phase * 25000))
        elif self.state == 2:
            if self.tick % (300 - self.phase * 10) <= (30 - self.phase * 5):
                self.ts.clear()
                self.rot = vector.coordinate_rotation(*(pp - self.pos))
                self.velocity /= 100
                bs = abs(pp - self.pos)
                tp = copy.copy(self.pos)
                rt = self.rot
                cs = {3: [120], 4: [90], 5: [144, 72], 6: [60], 7: [360 / 7, 102.857, 154.286], 9: [40, 80, 160]}
                for _ in range(self.ntd):
                    self.ts.append(vector.Vector2D(0, 0, *tp.to_value()))
                    tp += vector.Vector2D(rt, bs * 2)
                    rt += cs[self.ntd][self.tb % len(cs[self.ntd])]
            elif self.tick % (300 - self.phase * 10) <= (40 - self.phase * 6):
                pass
            else:
                rp = self.tick % (300 - self.phase * 10) - (40 - self.phase * 6)
                it = 30 - self.phase * 12
                idx = int(rp // it) % len(self.ts)
                sp = self.ts[idx]
                ep = self.ts[(idx + 1) % len(self.ts)]
                self.rot = vector.coordinate_rotation(*(ep - sp))
                self.pos << (ep - sp) * (rp % it) / it + sp
        elif self.state == 3:
            if self.tick < 20 == 0:
                self.rot = vector.coordinate_rotation(*(pp - self.pos))
                self.velocity /= 100
            else:
                self.rot += 37

class PhantomEye(Entity):
    DISPLAY_MODE = 0
    DIVERSITY = False

    def __init__(self, pos, rot=0, action=0):
        super().__init__(pos, game.get_game().graphics['entity3_phantom_eye'], entity.BuildingAI, hp=800000)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 600
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 600
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 600
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 600
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 600
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 600
        self.action = action
        self.poss = []
        self.set_rotation(rot)
        self.st_pos = (pos[0], pos[1])
        self.bk = 0
        self.dmg = True

        self.obj.MASS = 10
        self.tick = 0
        self.obj.FRICTION = .9
        if self.action == 1:
            self.obj.FRICTION = 1.01
        elif self.action == 2:
            self.obj.FRICTION = 1
            self.obj.apply_force(vector.Vector2D(rot, 1000))

    def t_draw(self):
        self.tick += 1
        if self.action:
            self.hp_sys.hp -= self.hp_sys.max_hp * (8 - constants.DIFFICULTY) / 1500
        if self.bk:
            self.dmg = False
            self.obj.pos = (self.obj.pos * 5 + self.st_pos) / 6
            if vector.distance(*(self.obj.pos - self.st_pos)) < 200:
                self.hp_sys.hp = 0
        elif self.action == 1:
            pp = game.get_game().player.obj.pos
            self.obj.apply_force(vector.Vector2D(vector.coordinate_rotation(*(pp - self.obj.pos)), 5))
        elif self.action == 2:
            self.obj.apply_force(vector.Vector2D(-self.rot, 10))
        elif self.action == 3:
            self.obj.pos += vector.Vector2D(self.rot, 20)
            self.obj.pos += vector.Vector2D(self.rot + 90, math.sin(self.tick / 10) / 10)
        self.obj.update()
        self.poss.append(self.obj.pos.to_value())
        if len(self.poss) > 10:
            self.poss.pop(0)
        for i in range(len(self.poss) - 1):
            draw.line(game.get_game().displayer.canvas, (i * 255 // len(self.poss), 255, 255), position.displayed_position(self.poss[i]),
                      position.displayed_position(self.poss[i+1]), i * 90 // len(self.poss) / game.get_game().player.get_screen_scale())
        sc = len(self.poss) / 10 * (.6 + constants.DIFFICULTY * .4)
        pg.draw.circle(game.get_game().displayer.canvas, (200 + self.dmg * 55, 200 + self.dmg * 55, 200 + self.dmg * 55), position.displayed_position(self.obj.pos), int(45 * sc / game.get_game().player.get_screen_scale()))
        pg.draw.circle(game.get_game().displayer.canvas, (0, 255, 255), position.displayed_position(self.obj.pos), int(23 * sc / game.get_game().player.get_screen_scale()),
                       int(15 * sc / game.get_game().player.get_screen_scale()))
        self.damage()

    def damage(self):
        if self.dmg:
            pp = game.get_game().player.obj.pos
            if abs(pp - self.obj.pos) < 50 * (.6 + constants.DIFFICULTY * .4):
                if self.action:
                    self.hp_sys.hp = 0
                if not game.get_game().player.hp_sys.is_immune:
                    game.get_game().player.hp_sys.damage(400, damages.DamageTypes.MAGICAL)
                    game.get_game().player.hp_sys.enable_immune()


class PetrifiedWitness(Entity):
    DISPLAY_MODE = 1
    IS_MENACE = True
    NAME = 'Petrified Witness'
    SOUND_DEATH = 'explosive'
    SOUND_HURT = 'metal'
    BOSS_NAME = 'The Lost Eye'
    PHASE_SEGMENTS = [.5, .8]

    TTD = 0

    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('hope_dust', 1, 4, 8),
    ])

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity3_petrified_witness'], PetrifiedWitnessAI, hp=140000)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 100
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 150
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 150
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 100
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 200
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 100
        self.obj: PetrifiedWitnessAI = self.obj
        self.eyes = [PhantomEye(self.obj.pos) for _ in range(2)]
        self.p_eyes = []
        self.p_eyes.extend(self.eyes)
        self.ft = 0
        self.dt = 0
        self.PHASE_SEGMENTS = [(1 + constants.DIFFICULTY / 2) / self.hp_sys.max_hp, .5, .8]
        if PetrifiedWitness.TTD > 0:
            game.get_game().dialog.dialog('Petrified Witness is disgusted to camouflage anymore!')

    def on_update(self):
        super().on_update()
        self.set_rotation(-self.obj.rot)
        if -20 < self.obj.tick < 0 and self.obj.phase < 3:
            for p in self.p_eyes:
                if p not in self.eyes:
                    p.bk = 1
        if PetrifiedWitness.TTD >= 1 and self.hp_sys.hp >= self.hp_sys.max_hp * .8:
            self.hp_sys.hp -= self.hp_sys.max_hp * .02
            self.obj.tick = -10000
        if PetrifiedWitness.TTD >= 2 and self.hp_sys.hp >= self.hp_sys.max_hp * .5:
            self.hp_sys.hp -= self.hp_sys.max_hp * .03
            self.obj.tick = -10000
        if self.obj.tick < 0:
            self.hp_sys.IMMUNE = True
        else:
            self.hp_sys.IMMUNE = False
        if self.hp_sys.hp < self.hp_sys.max_hp * .8 and self.obj.phase == 0:
            self.obj.phase = 1
            self.obj.tick = -100
            self.obj.state = 1
            self.play_sound('eoc_roar')
            for d in self.hp_sys.defenses.defences.keys():
                self.hp_sys.defenses[d] -= 20
            self.obj.TOUCHING_DAMAGE += 50
            self.p_eyes = []
            self.eyes = [PhantomEye(self.obj.pos) for _ in range(4)]
            self.p_eyes.extend(self.eyes)
            PetrifiedWitness.TTD = 1
        if self.hp_sys.hp < self.hp_sys.max_hp * .5 and self.obj.phase == 1:
            self.obj.phase = 2
            self.obj.tick = -150
            self.obj.state = 1
            self.play_sound('eoc_roar')
            for d in self.hp_sys.defenses.defences.keys():
                self.hp_sys.defenses[d] -= 10
            self.obj.TOUCHING_DAMAGE += 80
            self.p_eyes = []
            self.eyes = [PhantomEye(self.obj.pos) for _ in range(6)]
            self.p_eyes.extend(self.eyes)
            PetrifiedWitness.TTD = 2
        if self.hp_sys.hp <= self.hp_sys.max_hp * self.PHASE_SEGMENTS[0] and self.obj.phase == 2:
            self.obj.phase = 3
            self.obj.tick = -200
            self.hp_sys.hp = self.hp_sys.max_hp * self.PHASE_SEGMENTS[0]
            self.obj.state = 4
            self.play_sound('eoc_roar')
            self.p_eyes = []
            self.eyes = [PhantomEye(self.obj.pos) for _ in range(2 * (2 + constants.DIFFICULTY))]
            self.p_eyes.extend(self.eyes)

    def t_draw(self):
        if self.hp_sys.hp < self.hp_sys.max_hp * self.PHASE_SEGMENTS[0] and self.obj.phase == 2:
            self.hp_sys.hp = self.hp_sys.max_hp * self.PHASE_SEGMENTS[0] - .001
            self.hp_sys.IMMUNE = True
            self.obj.tick = -200
        try:
            self.ft
        except AttributeError:
            self.ft = 0
            self.dt = 0
            self.eyes = [PhantomEye(self.obj.pos) for _ in range(2)]
            self.p_eyes = []
        if self.obj.phase != 3:
            self.ft += 7
        else:
            self.hp_sys.IMMUNE = True
            self.ft += 1
            self.dt = self.dt // 2 + 700 - 100 * constants.DIFFICULTY + int(800 * self.hp_sys.hp / (1 + constants.DIFFICULTY / 2))
            self.obj.tick = -200
            self.hp_sys.hp -= .001
            ap = game.get_game().player.obj.pos - self.obj.pos
            if abs(ap) > self.dt:
                ap = ap / abs(ap) * self.dt
                game.get_game().player.obj.pos = self.obj.pos + ap
            if self.hp_sys.hp < .4:
                self.hp_sys.hp += .0007
                self.ft += 13
                if self.ft // 13 % (10 - constants.DIFFICULTY) == 0:
                    self.p_eyes.append(PhantomEye(self.obj.pos, action=1))
            elif self.ft % (20 - constants.DIFFICULTY * 2) == 0:
                for i, ee in enumerate(self.eyes):
                    if i % 2 == 0:
                        continue
                    self.p_eyes.append(PhantomEye(ee.obj.pos, action=2, rot=vector.coordinate_rotation(*(self.obj.pos - ee.obj.pos))))

        ar = 360 // len(self.eyes)
        for i, e in enumerate(self.eyes):
            e.obj.pos = self.obj.pos + vector.Vector2D(self.ft + ar * i, 200 + len(self.eyes) * 20 + self.dt)
        if self.obj.state == 3:
            self.dt = self.dt // 2 + 1500
        else:
            self.dt //= 2
        if self.obj.state == 0 and self.obj.tick % (35 - self.obj.phase * 2 - constants.DIFFICULTY) == 0:
            pp = game.get_game().player.obj.pos
            rr = vector.coordinate_rotation(*(pp - self.obj.pos))
            self.p_eyes.append(PhantomEye(self.obj.pos, rr, 2))
            if constants.DIFFICULTY or self.obj.phase:
                dr = 80 - constants.DIFFICULTY * 5 - self.obj.phase * 15
                for i in range(dr, 80, dr):
                    self.p_eyes.append(PhantomEye(self.obj.pos, rr + i, 2))
                    self.p_eyes.append(PhantomEye(self.obj.pos, rr - i, 2))
        if self.obj.state == 1 and self.obj.tick % (60 - self.obj.phase * 6) > (40 - self.obj.phase * 6):
            if self.obj.tick % (8 - self.obj.phase - constants.DIFFICULTY // 2) == 2:
                self.p_eyes.append(PhantomEye(self.obj.pos, 0, 1))
        if self.obj.state == 2 and self.obj.tick % (300 - self.obj.phase * 10) > (40 - self.obj.phase * 6):
            if self.obj.tick % (7 - self.obj.phase // 2 - constants.DIFFICULTY // 2) == 2:
                self.p_eyes.append(PhantomEye(self.obj.pos, 0, 1))
        if self.obj.state == 3 and self.obj.tick >= 20:
            if self.obj.tick % (25 - constants.DIFFICULTY // 2) == 0:
                for e in self.eyes:
                    self.p_eyes.append(PhantomEye(e.obj.pos, action=1))
                for ar in range(-8, 9, 4):
                    self.p_eyes.append(PhantomEye(self.obj.pos, action=3, rot=ar + self.rot))
            if self.obj.tick % (50 - constants.DIFFICULTY * 3) == 0:
                for ar in range(0, 360, 60):
                    self.p_eyes.append(PhantomEye(self.obj.pos, ar + self.obj.tick * 10 % 360, 2))
        for e in self.p_eyes:
            e.t_draw()
            if e.hp_sys.hp <= 0:
                self.p_eyes.remove(e)
        if self.obj.tick % (60 - self.obj.phase * 6) <= (40 - self.obj.phase * 6) and self.obj.state == 1:
            lx = self.obj.pos - vector.Vector2D(self.obj.rot + 90, 100)
            rx = self.obj.pos - vector.Vector2D(self.obj.rot - 90, 100)
            aax = vector.Vector2D(self.obj.rot, 3000 / game.get_game().player.get_screen_scale())
            pg.draw.line(game.get_game().displayer.canvas, (255, 0, 0), position.displayed_position(lx - aax),
                         position.displayed_position(lx + aax), 2)
            pg.draw.line(game.get_game().displayer.canvas, (255, 0, 0), position.displayed_position(rx - aax),
                         position.displayed_position(rx + aax), 2)
        if self.obj.state == 2:
            for i in range(len(self.obj.ts)):
                ni = (i + 1) % len(self.obj.ts)
                nni = (i + 2) % len(self.obj.ts)
                pg.draw.line(game.get_game().displayer.canvas, (255, 0, 0), position.displayed_position(self.obj.ts[i]),
                             position.displayed_position(self.obj.ts[ni]), 2)
                pg.draw.line(game.get_game().displayer.canvas, (255, 255, 0), position.displayed_position(self.obj.ts[i]),
                             position.displayed_position(self.obj.ts[nni]), 2)
        super().t_draw()

class TralaleroAI(entity.MonsterAI):
    SIGHT_DISTANCE = 60000
    FRICTION = 0.92
    TOUCHING_DAMAGE = 650
    MASS = 1000

    def __init__(self, obj):
        super().__init__(obj)
        self.tick = 0
        self.drt = 0

    def on_update(self):
        self.tick += 1
        self.get_target()
        if self.cur_target is None:
            self.idle()
            return
        if self.tick % 200 == 0:
            self.drt = vector.coordinate_rotation(*(self.pos - self.cur_target.pos))
        elif self.tick % 200 < 100:
            self.apply_force((self.cur_target.pos + vector.Vector2D(self.drt, 800) - self.pos) * 8)
            self.drt += math.sin(self.tick / 50 + 114) * 3 * (100 - self.tick % 200) / 100
        elif self.tick % 200 < 120:
            self.apply_force(vector.Vector2D(self.drt, -32000))
        else:
            self.apply_force((self.cur_target.pos - self.pos))


class Tralalero(Entity):
    DISPLAY_MODE = 1
    NAME = 'Tralalero'
    SOUND_HURT = 'sticky'
    SOUND_DEATH = 'sticky'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity3_tralalero'], TralaleroAI, hp=[600, 1200, 2400, 4000][constants.DIFFICULTY])
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 20
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 30
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 30
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 20
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 40
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 20

    def t_draw(self):
        if self.obj.tick % 200 < 100:
            self.set_rotation((self.rot * 9 + vector.coordinate_rotation(*(game.get_game().player.obj.pos - self.obj.pos)) - 90) / 10)
            draw.line(game.get_game().displayer.canvas, (255, 0, 0), position.displayed_position(self.obj.pos),
                      position.displayed_position(self.obj.pos + vector.Vector2D(self.rot + 90, 2000)), 3)
        else:
            self.set_rotation((self.rot * 9 - self.obj.velocity.get_net_rotation() - 90) / 10)
        super().t_draw()

class WaterTyphoon(Entity):
    def __init__(self, pos, mode=0, sz=.1):
        super().__init__(pos, game.get_game().graphics['entity_null'], entity.MonsterAI, hp=100)
        self.mod = mode
        self.tick = 0
        self.size = sz

    def t_draw(self):
        self.tick += 1
        for ll in range(10 + int(10 * self.size) * min(1, self.tick // 100)):
            for ar in range(0, 360, 60):
                draw.line(game.get_game().displayer.canvas, (100, 100, 255),
                          position.displayed_position(self.obj.pos + vector.Vector2D(ar + self.tick * 2 - 4 * ll ** 1.5, ll * 20 * self.size)),
                          position.displayed_position(self.obj.pos + vector.Vector2D(ar + self.tick * 2 - 4 * (ll + 1) ** 1.5, ll * 20 * self.size + 20 * self.size)),
                          width=int(20 * self.size - 20 * self.size * ll // (10 + int(10 * self.size) * min(1, self.tick // 100))))
        self.hp_sys.hp -= .4
        self.damage()

    def damage(self):
        if vector.distance(*(game.get_game().player.obj.pos - self.obj.pos)) < 200 * self.size ** 2:
            if not game.get_game().player.hp_sys.is_immune:
                game.get_game().player.hp_sys.damage(100, damages.DamageTypes.MAGICAL, penetrate=600)
                game.get_game().player.hp_sys.enable_immune(.5)

class OceanTornado(Entity):
    def __init__(self, pos, mode=0, leng=4000):
        super().__init__(pos, game.get_game().graphics['entity_null'], entity.MonsterAI, hp=100)
        self.mod = mode
        self.rt = 0
        self.leng = leng

    def t_draw(self):
        self.rt += 2
        dt = []
        tw = 0
        for ay in range(-self.leng, self.leng, 10):
            ar = ay + self.rt / 1.5
            aw = self.leng / 5 - (ay + self.leng) / 10
            ax, az = vector.Vector2D(ar, aw)
            dt.append((ax, ay, az))
            tw = max(tw, aw)
        vdt = []

        for i in range(len(dt) - 1):
            vdt.append((dt[i], dt[i + 1]))
        vdt = sorted(vdt, key=lambda x: -x[1][2])
        for sp, ep in vdt:
            sx, sy, sz = sp
            ex, ey, ez = ep
            draw.line(game.get_game().displayer.canvas, (int(50 * (sz + ez) / tw) + 150, int(50 * (sz + ez) / tw) + 150, 255), position.displayed_position(self.obj.pos + (sx, sy)),
                      position.displayed_position(self.obj.pos + (ex, ey)), (100 + (sz + ez) / 100) / game.get_game().player.get_screen_scale())

class TralaleroTralalaAI(entity.MonsterAI):
    MASS = 3000
    FRICTION = .93
    TOUCHING_DAMAGE = 900
    SIGHT_DISTANCE = 100000

    def __init__(self, *args):
        super().__init__(*args)
        self.state = 0

    def on_update(self):
        self.get_target()
        if self.cur_target is None:
            self.idle()
        if self.state == 0:
            self.apply_force((self.cur_target.pos - self.pos + (0, -1000)) * 18)
        elif self.state == 1:
            self.apply_force((self.cur_target.pos - self.pos + (0, 1000)) * 12)
        else:
            pass

class TralaleroTralala(Entity):
    DISPLAY_MODE = 2
    IS_MENACE = True
    NAME = 'Tralalero Tralala'
    BOSS_NAME = 'Hope from the Ocean'
    SOUND_HURT = 'sticky'
    SOUND_DEATH = 'huge_monster'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity3_tralalero_tralala'], TralaleroTralalaAI, hp=360000)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 60
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 60
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 60
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 40
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 80
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 20
        self.afterimages = []
        self.poss = []
        self.tt = 0
        self.typs = [WaterTyphoon(self.obj.pos, sz=1.5), OceanTornado(self.obj.pos)]
        self.trals = []
        self.sst = 3000
        self.st = 0
        self.r_typs = [WaterTyphoon(self.obj.pos + vector.Vector2D(rt, self.sst)) for rt in range(0, 360, 10)]

    def t_draw(self):
        for i, tps in enumerate(self.r_typs):
            tps.obj.pos = self.obj.pos + vector.Vector2D(i * 10 + self.tt, self.sst)
            tps.size = max(0, 1.0 - abs(tps.obj.pos - game.get_game().player.obj.pos) / 2500)
            tps.hp_sys.hp = 100
            tps.t_draw()
        ap = game.get_game().player.obj.pos - self.obj.pos
        if abs(ap) > self.sst:
            ap = ap / abs(ap) * self.sst
            game.get_game().player.obj.pos = self.obj.pos + ap
        if random.randint(0, self.tt) > 150:
            self.tt = 0
            self.st = (self.st + 1) % 7
            if self.st < 6:
                self.obj.state = self.st % 2
            else:
                self.obj.state = 2
        for t in self.typs:
            t.t_draw()
            if t.hp_sys.hp <= 0:
                self.typs.remove(t)
        for t in self.trals:
            if t.hp_sys.hp <= 0:
                self.trals.remove(t)
        self.tt += 1
        if self.obj.state <= 1:
            self.set_rotation(vector.coordinate_rotation(*(game.get_game().player.obj.pos - self.obj.pos)))
        elif self.obj.state == 2:
            self.rotate(9)
        if self.obj.state <= 1:
            if self.tt % 5 == 0:
                self.poss.append(self.obj.pos.to_value())
                self.afterimages.append(copy.copy(self.d_img))
            if self.tt % 200 == 1 and constants.DIFFICULTY > 1:
                for t in self.trals:
                    self.typs.append(WaterTyphoon(t.obj.pos, sz=.2))
            elif self.tt % 100 == 1:
                for _ in range(max(1, constants.DIFFICULTY)):
                    ee = Tralalero(self.obj.pos + vector.Vector2D(random.randint(-1000, 1000), random.randint(-1000, 1000)))
                    self.trals.append(ee)
                    game.get_game().entities.append(ee)
            elif self.tt % 20 == 1:
                self.typs.append(WaterTyphoon(self.obj.pos, sz=.5))
        elif self.obj.state == 2:
            if self.tt % 80 == 1:
                for _ in range(max(1, constants.DIFFICULTY)):
                    ee = Tralalero(self.obj.pos + vector.Vector2D(random.randint(-1000, 1000), random.randint(-1000, 1000)))
                    self.trals.append(ee)
                    game.get_game().entities.append(ee)
                self.typs.append(WaterTyphoon(self.obj.pos, sz=1.5 + constants.DIFFICULTY / 2))
        if len(self.poss) > 5:
            self.poss.pop(0)
        for i in range(len(self.poss)):
            self.afterimages[i].set_alpha(255 * i // len(self.poss))
            sr = self.afterimages[i].get_rect(center=position.displayed_position(self.poss[i]))
            game.get_game().displayer.canvas.blit(self.afterimages[i], sr)
        super().t_draw()

class StanoZololAI(entity.MonsterAI):
    MASS = 8000
    FRICTION = .8
    TOUCHING_DAMAGE = 1500
    SIGHT_DISTANCE = 100000

    def __init__(self, *args):
        super().__init__(*args)
        self.state = 0
        self.tt = 0
        self.tick = 0

    def on_update(self):
        self.tick += 1
        self.get_target()
        if self.cur_target is None:
            self.idle()
        pos = self.cur_target.pos - self.pos
        if self.state == 0:
            self.apply_force(vector.Vector2D(vector.coordinate_rotation(*pos) + 80 - constants.DIFFICULTY * 5, max(60000, 130000 - abs(pos) * 10)))
        elif self.state == 1:
            if self.tick % 300 < 20:
                self.tt = vector.coordinate_rotation(*pos)
            elif self.tick % 300 < 200:
                self.apply_force(vector.Vector2D(self.tt, min(50000, abs(pos) * 55) + 90000))
            else:
                self.apply_force(pos * 40)


class StanoZolol(entity.Entities.WormEntity):
    IS_MENACE = True

    NAME = 'Stanozolol'
    SOUND_HURT = 'metal'

    PHASE_SEGMENTS = [.5, .8]

    def __init__(self, pos):
        super().__init__(pos, 16, game.get_game().graphics['entity3_stanozolol_head'], game.get_game().graphics['entity3_stanozolol_body'],
                         StanoZololAI, 3450000, body_length=370, body_touching_damage=700)
        self.obj.SIGHT_DISTANCE = 100000
        self.body[-1].img = game.get_game().graphics['entity3_stanozolol_tail']
        self.body[0].obj.TOUCHING_DAMAGE += 250
        self.body[-1].obj.TOUCHING_DAMAGE += 450
        self.nightstate = 0
        self.tick = 0
        self.phase = 0
        self.fires = []
        self.nt = 2000
        for i, b in enumerate(self.body):
            b.SOUND_HURT = 'metal'
            if not i:
                dd = 300
            elif i != len(self.body) - 1:
                dd = 1200
            else:
                dd = 0
            b.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = dd
            b.hp_sys.defenses[damages.DamageTypes.PIERCING] = dd
            b.hp_sys.defenses[damages.DamageTypes.MAGICAL] = dd + 20
            b.hp_sys.defenses[damages.DamageTypes.OCTAVE] = dd - 50
            b.hp_sys.defenses[damages.DamageTypes.HALLOW] = dd + 150
            b.hp_sys.defenses[damages.DamageTypes.PACIFY] = dd - 100
            for r in self.hp_sys.resistances.resistances.keys():
                self.hp_sys.resistances[r] *= .6

    def on_update(self):
        for f in self.fires:
            f.on_update()
        super().on_update()
        if self.hp_sys.hp < self.hp_sys.max_hp * .8 and self.phase == 0:
            self.phase = 1
            self.nt = 2000
            for i, b in enumerate(self.body):
                if not i:
                    md = 0
                elif i != len(self.body) - 1:
                    md = 800
                else:
                    md = 200
                for d in b.hp_sys.defenses.defences.keys():
                    b.hp_sys.defenses[d] -= md
        if self.hp_sys.hp < self.hp_sys.max_hp * .5 and self.phase == 1:
            self.phase = 2
            self.nt = 2000
            for i, b in enumerate(self.body):
                for d in b.hp_sys.defenses.defences.keys():
                    b.hp_sys.defenses[d] -= 400
            self.obj.SPEED *= 1.2

    def t_draw(self):
        for f in self.fires:
            f.t_draw()
            if f.hp_sys.hp <= 0:
                self.fires.remove(f)
        self.body[0].img = game.get_game().graphics['entity3_stanozolol_head' + ('_close' if not self.nightstate else '')]
        if self.nightstate:
            game.get_game().displayer.point_light((0, 255, 255), position.displayed_position(self.obj.pos), 3,
                                                  int(300 / game.get_game().player.get_screen_scale()))
            game.get_game().displayer.point_light((0, 255, 255), position.displayed_position(self.body[-1].obj.pos), 3,
                                                  int(300 / game.get_game().player.get_screen_scale()))
        super().t_draw()
        self.tick += 1
        if random.randint(0, self.tick) > 900:
            self.tick = 0
            self.nightstate = not self.nightstate
            if self.nt and not self.nightstate:
                self.nt = 0
        self.obj.state = self.nightstate
        if self.nt:
            self.nt -= 1
            return
        if self.phase == 0:
            pp = game.get_game().player.obj.pos.to_value()
            if not self.nightstate:
                if self.tick % 100 == 1:
                    pp = vector.Vector2D(random.randint(0, 360), random.randint(500, 2000)) + pp
                    for b in self.body:
                        self.fires.append(CandleFire(b.obj.pos, vector.coordinate_rotation(*(-b.obj.pos + pp))))
                elif self.tick % 20 == 1:
                    bb = random.choice(self.body[1:-1])
                    self.fires.append(CandleFire(bb.obj.pos, vector.coordinate_rotation(*(-bb.obj.pos + pp)),
                                                 bb))
            else:
                if 20 < self.obj.tick % 300 < 200 and self.tick % 20 == 1:
                    self.fires.append(VoidFire(self.obj.pos, self.body[0].rot))
                if self.obj.tick % 300 == 250:
                    for r in range(0, 360, 60 - constants.DIFFICULTY * 15):
                        self.fires.append(VoidFire(self.obj.pos, self.body[0].rot + r, self.body[0]))
        elif self.phase == 1:
            pp = game.get_game().player.obj.pos.to_value()
            if not self.nightstate:
                if self.tick % 60 == 1:
                    pp = vector.Vector2D(random.randint(0, 360), random.randint(0, 500)) + pp
                    for b in self.body:
                        self.fires.append(CandleFire(b.obj.pos, vector.coordinate_rotation(*(-b.obj.pos + pp)), b))
                elif self.tick % 5 == 1:
                    bb = random.choice(self.body[1:-1])
                    self.fires.append(CandleFire(bb.obj.pos, vector.coordinate_rotation(*(-bb.obj.pos + pp)),
                                                 bb))
            else:
                if 20 < self.obj.tick % 300 < 200 and self.tick % 20 == 1:
                    for r in range(0, 360, 120):
                        self.fires.append(VoidFire(self.obj.pos, self.body[0].rot + r, self.body[0]))
                if self.obj.tick % 300 == 250:
                    for r in range(0, 360, 40 - constants.DIFFICULTY * 10):
                        self.fires.append(VoidFire(self.body[-1].obj.pos, self.body[-1].rot + r, self.body[-1]))
                        self.fires.append(VoidFire(self.obj.pos, self.body[0].rot + r, self.body[0]))
        elif self.phase == 2:
            pp = game.get_game().player.obj.pos.to_value()
            if not self.nightstate:
                if self.tick % 180 == 1:
                    ax = random.randint(-300, 300)
                    for d in range(-3000, 3000, 600):
                        self.fires.append(CandleFire(game.get_game().player.obj.pos + vector.Vector2D(dx=ax + d, dy=2000), vector.coordinate_rotation(0, -1)))
                elif self.tick % 30 == 1:
                    for b in self.body:
                        self.fires.append(CandleFire(b.obj.pos, vector.coordinate_rotation(*(-b.obj.pos + pp)), b))
            else:
                if 20 < self.obj.tick % 300 < 200 and self.tick % 40 == 1:
                    ar = random.randint(0, 90)
                    for r in range(0, 360, 90):
                        self.fires.append(VoidFire(self.obj.pos, self.body[0].rot + r + ar, self.body[0]))
                if self.obj.tick % 300  > 200 and self.tick % 5 == 0:
                    self.fires.append(VoidFire(self.body[-1].obj.pos, self.body[-1].rot + self.tick * 2, self.body[-1]))
                    self.fires.append(VoidFire(self.body[-1].obj.pos, self.body[-1].rot + self.tick * 2 + 180, self.body[-1]))


class CandleFire(Entity):
    NAME = 'Fire'
    DISPLAY_MODE = 1

    def __init__(self, pos, rot, follow_entity=None, tt=0):
        super().__init__(pos, game.get_game().graphics['entity_null'], entity.FastBulletAI, 10 ** 6)
        self.obj.MASS = 1000
        self.obj.rot = rot
        self.obj.speed = 4800
        self.tick = tt
        self.tt = 0
        self.poss = []
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
            for i in range(len(self.poss) - 1):
                sx, sy = self.poss[i]
                ex, ey = self.poss[i + 1]
                draw.line(game.get_game().displayer.canvas, (100, 100, 0), position.displayed_position((sx, sy)),
                          position.displayed_position((ex, ey)), int(i * 5 / game.get_game().player.get_screen_scale()))
            self.poss.append(self.obj.pos.to_value())
            if len(self.poss) > 10:
                self.poss.pop(0)
        else:
            if self.follow_entity is not None:
                self.obj.pos << (self.follow_entity.obj.pos[0] + self.ax, self.follow_entity.obj.pos[1] + self.ay)
                self.obj.rot = -self.follow_entity.rot + self.arot
            ax, ay = vector.rotation_coordinate(self.obj.rot)
            draw.line(game.get_game().displayer.canvas, (255, 255, 0),
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
                           self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 300 and \
            not game.get_game().player.hp_sys.is_immune:

            game.get_game().player.hp_sys.damage(800, damages.DamageTypes.MAGICAL)
            game.get_game().player.hp_sys.enable_immune(2)
            self.hp_sys.hp = 0

class VoidFire(Entity):
    NAME = 'Fire'
    DISPLAY_MODE = 1

    def __init__(self, pos, rot, follow_entity=None, tt=0):
        super().__init__(pos, game.get_game().graphics['entity_null'], entity.FastBulletAI, 10 ** 6)
        self.obj.MASS = 1000
        self.obj.rot = rot
        self.obj.speed = 4800
        self.tick = tt
        self.nt = 1000
        self.tt = 0
        self.poss = []
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
            for i in range(len(self.poss) - 1):
                sx, sy = self.poss[i]
                ex, ey = self.poss[i + 1]
                draw.line(game.get_game().displayer.canvas, (0, 255, 255), position.displayed_position((sx, sy)),
                          position.displayed_position((ex, ey)), int(i * 5 / game.get_game().player.get_screen_scale()))
            self.poss.append(self.obj.pos.to_value())
            if len(self.poss) > 10:
                self.poss.pop(0)
            game.get_game().displayer.point_light((0, 255, 255), position.displayed_position(self.obj.pos), 3.8,
                                                  int(300 / game.get_game().player.get_screen_scale()))
        else:
            if self.follow_entity is not None:
                self.obj.pos << (self.follow_entity.obj.pos[0] + self.ax, self.follow_entity.obj.pos[1] + self.ay)
                self.obj.rot = -self.follow_entity.rot + self.arot
            ax, ay = vector.rotation_coordinate(self.obj.rot)
            draw.line(game.get_game().displayer.canvas, (0, 255, 255),
                      position.displayed_position(self.obj.pos),
                      position.displayed_position((self.obj.pos[0] + ax * 3000, self.obj.pos[1] + ay * 3000)),
                      3)
            for dd in range(0, 3000, 300):
                game.get_game().displayer.point_light((0, 255, 255),
                                                      position.displayed_position(self.obj.pos + vector.Vector2D(self.obj.rot, dd)), 3,
                                                      int(150 / game.get_game().player.get_screen_scale()))

    def on_update(self):
        self.tick += 1
        if self.tick < 10:
            pass
        else:
            self.damage()
            self.hp_sys.hp -= 25 * 10 ** 3

    def damage(self):
        if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                           self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 300 and \
            not game.get_game().player.hp_sys.is_immune:
            game.get_game().player.hp_sys.damage(800, damages.DamageTypes.MAGICAL)
            game.get_game().player.hp_sys.enable_immune(2)
            self.hp_sys.hp = 0




