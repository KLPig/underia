from packs import SelectionLoot
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

class BuildingAI(entity.BuildingAI):
    pass

@entity.Entities.entity_type
class PineNeedles(entity.Entities.Lazer):
    NAME = 'pine_needles'
    DMG = 300
    SOUND_SPAWN = None

    def t_draw(self):
        super().t_draw()
        if abs(self.obj.velocity):
            draw.line(game.get_game().displayer.canvas, (0, 100, 0),
                      position.displayed_position(self.obj.pos),
                      position.displayed_position(self.obj.pos + self.obj.velocity / abs(self.obj.velocity) * 200), 5)

@entity.Entities.entity_type
class EverScream(Entity):
    NAME = 'Everscream'
    BOSS_NAME = 'The Terror of Christmas'
    IS_MENACE = True
    DISPLAY_MODE = 1
    DIVERSITY = False

    PHASE_SEGMENTS = [.5, .8]

    LOOT_TABLE = entity.LootTable([
        SelectionLoot([('christmas_tree_sword', 1, 1), ('candy_cane', 1, 1)], 1, 2),
    ])

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity_everscream'], BuildingAI, 80000)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 60
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 60
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 60
        self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 60

        self.phase = 1
        self.state = 0
        self.tick = 0
        self.pjs = []
        self.dr = 0

    def t_draw(self):
        super().t_draw()
        self.tick += 1
        if random.randint(0, self.tick) > 400:
            self.state += 1
            self.tick = 0

        ap = game.get_game().player.obj.pos - self.obj.pos

        if self.phase:
            game.get_game().player.obj.apply_force(-ap / 15)
            if self.phase > 1:
                game.get_game().player.obj.apply_force(-ap / 15)


        if self.hp_sys.hp <= 1:
            if 'cm_tree' not in game.get_game().npc_data:
                game.get_game().furniture.append(entity.Entities.ChristmasTree((0, 0)))
                game.get_game().dialog.dialog('Christmas Tree arrived!')

        if self.phase <= 1:
            if self.state % 5 == 0:
                if self.tick % 60 == 0:
                    rt = random.randint(0, 360)
                    for ar in range(0, 360, 60 - self.phase * 4):
                        self.pjs.append(PineNeedles(self.obj.pos, rt + ar))
            elif self.state % 5 == 1:
                if self.tick % (10 - self.phase * 6) == 0:
                    self.pjs.append(PineNeedles(self.obj.pos, random.randint(0, 360)))
            elif self.state % 5 == 2:
                if self.tick % 12 == 0:
                    for ar in range(0, 360, 120 - self.phase * 48):
                        self.pjs.append(PineNeedles(self.obj.pos, self.tick + ar))
            elif self.state % 5 == 3:
                if self.tick % 80 == 0:
                    for ar in range(0, 360, 60 - self.phase * 30):
                        self.pjs.append(PineNeedles(self.obj.pos, ar + 30))
                elif self.tick % 20 == 0:
                    for ar in range(0, 360, 180 - self.phase * 90):
                        self.pjs.append(PineNeedles(self.obj.pos, self.tick * 2 // 3 + ar))
            elif self.state % 5 == 4:
                if self.tick % 80 == 0:
                    rt = random.randint(0, 360)
                    for ar in range(0, 360, 120 - self.phase * 90):
                        self.pjs.append(PineNeedles(self.obj.pos, ar + rt))
                elif self.tick % 20 == 0:
                    for ar in range(0, 360, 60 - self.phase * 15):
                        self.pjs.append(PineNeedles(self.obj.pos, ar + self.tick * 2 // 3))
        else:
            if self.state % 3 == 0:
                if self.tick % 8 == 0:
                    rt = random.randint(0, 360)
                    for ar in range(0, 360, 40):
                        self.pjs.append(PineNeedles(self.obj.pos, ar + rt))
                self.dr = vector.coordinate_rotation(*(game.get_game().player.obj.pos - self.obj.pos))
            elif self.state % 3 == 1:
                self.dr = (self.dr * 14 + vector.coordinate_rotation(*(game.get_game().player.obj.pos - self.obj.pos))) // 15
                self.obj.apply_force(vector.Vector2D(self.dr, 10000))
                if self.tick % 12 == 0:
                    for ar in [0, 180, 130, 230]:
                        self.pjs.append(PineNeedles(self.obj.pos, ar + self.dr))
            elif self.state % 3 == 2:
                self.dr = (self.dr * 2 + vector.coordinate_rotation(*(game.get_game().player.obj.pos - self.obj.pos))) // 3
                self.obj.apply_force(vector.Vector2D(self.dr, 4000))
                if self.tick % 25 == 0:
                    rt = random.randint(0, 360)
                    for ar in range(0, 360, 15):
                        self.pjs.append(PineNeedles(self.obj.pos, ar + rt))

        if self.phase == 0 and self.hp_sys.hp < .8 * self.hp_sys.max_hp:
            self.phase = 1
        if self.phase == 1 and self.hp_sys.hp < .5 * self.hp_sys.max_hp:
            self.phase = 2
            self.state = 0

            self.obj.FRICTION = .9
            self.obj.SPEED = 1
            self.obj.MASS = 500

        for p in self.pjs:
            p.t_draw()
            if p.hp_sys.hp <= 0:
                self.pjs.remove(p)

    def on_update(self):
        super().on_update()
        for p in self.pjs:
            p.on_update()
