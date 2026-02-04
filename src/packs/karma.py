import math
from underia import entity, game
from values import damages
from physics import vector
from resources import position
import constants

import pygame as pg

class Entity(entity.Entities.Entity):
    pass


@entity.Entities.entity_type
class Paradoxee(Entity):
    NAME = 'Paradoxee'
    DISPLAY_MODE = 3
    DMG = 1100

    def __init__(self, pos, rot):
        super().__init__(pos, game.get_game().graphics['entity_null'], entity.MagmaKingFireballAI, 6000)
        self.obj.rot = rot
        self.obj.SPEED *= 12
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 1600
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 1600
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 1600
        if constants.DIFFICULTY >= 3:
            self.hp_sys.IMMUNE = True
        self.show_bar = False
        self.tick = 0

    def t_draw(self):
        super().t_draw()
        self.tick += 1
        pg.draw.circle(game.get_game().displayer.canvas, (255, 0, 0),
                       position.displayed_position(self.obj.pos),
                       1 + int(30 * (math.sin(self.tick / 7) + 1) /
                               game.get_game().player.get_screen_scale()), 3)
        pg.draw.circle(game.get_game().displayer.canvas, (255, 255, 0),
                       position.displayed_position(self.obj.pos),
                       1 + int(30 * (math.sin(self.tick / 7 + math.pi) + 1) /
                               game.get_game().player.get_screen_scale()), 3)

    def on_update(self):
        super().on_update()
        self.set_rotation(self.rot)
        self.hp_sys.hp -= 30
        self.damage()

    def damage(self):
        if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                           self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 15:
            game.get_game().player.hp_sys.damage(self.DMG, damages.DamageTypes.MAGICAL)
            game.get_game().player.hp_sys.enable_immune()
            self.hp_sys.hp = 0

@entity.Entities.entity_type
class ParadoxTree(Entity):
    NAME = 'Paradox Tree'
    DISPLAY_MODE = 3
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('reason', .5, 6, 20),
        entity.IndividualLoot('result', .5, 6, 20),
    ])


    SOUND_HURT = 'monster'
    SOUND_DEATH = 'monster'

    @staticmethod
    def is_suitable(biome: str):
        return biome in ['forest', 'rainforest']

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity_paradox_tree'], entity.TreeMonsterAI, 250000)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 128
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 120
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 120
        self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 100
        self.hp_sys.defenses[damages.DamageTypes.THINKING] = 0
        self.obj.TOUCHING_DAMAGE = 1800
        self.obj.SPEED *= 75
        self.obj.MASS *= 25
        self.obj.SIGHT_DISTANCE *= 3

@entity.Entities.entity_type
class ParadoxerReason(Entity):
    NAME = 'Paradoxer: Reason'
    DISPLAY_MODE = 3
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('reason', 1, 6, 20),
    ])

    SOUND_HURT = 'crystal'
    SOUND_DEATH = 'explosive'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity_paradoxer_reason'], entity.BloodflowerAI, 140000)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 130
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 140
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 130
        self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 70
        self.hp_sys.defenses[damages.DamageTypes.THINKING] = 200
        self.obj.SPEED *= 75
        self.obj.MASS *= 12
        self.obj.TOUCHING_DAMAGE = 1200
        self.obj.SIGHT_DISTANCE *= 3
        self.tick = 0

    def t_draw(self):
        super().t_draw()
        self.tick += 1
        if self.obj.cur_target is None:
            return
        if self.tick % 12 == 1:
            for ar in range(0, 360, 120):
                game.get_game().entities.append(Paradoxee(self.obj.pos, self.tick * 7 + ar))

@entity.Entities.entity_type
class ParadoxerResult(Entity):
    NAME = 'Paradoxer: Result'
    DISPLAY_MODE = 3
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('result', 1, 6, 20),
    ])

    SOUND_HURT = 'crystal'
    SOUND_DEATH = 'explosive'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity_paradoxer_result'], entity.BloodflowerAI, 220000)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 180
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 180
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 180
        self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 120
        self.hp_sys.defenses[damages.DamageTypes.THINKING] = 300
        self.obj.SPEED *= 40
        self.obj.MASS *= 14
        self.obj.SIGHT_DISTANCE *= 3
        self.obj.TOUCHING_DAMAGE = 1500
        self.tick = 0

    def t_draw(self):
        super().t_draw()
        self.tick += 1
        if self.obj.cur_target is None:
            return
        if self.tick % 12 == 1:
            for ar in range(0, 360, 90):
                game.get_game().entities.append(Paradoxee(self.obj.pos, -self.tick * 3 + ar))