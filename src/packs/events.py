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

class EyeAI(entity.EyeAI):
    pass

@entity.Entities.entity_type
class BloodyEye(Entity):
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('blood_ingot', .3, 5, 10),
        entity.IndividualLoot('bloodstone', .1, 1, 1),

    ])

    SOUND_HURT = 'sticky'
    SOUND_DEATH = 'sticky'

    NAME = 'Bloody Eye'
    DISPLAY_MODE = 1

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity_bloody_eye'], entity.EyeAI, 1000)
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 50
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 45
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 45
        self.obj.TOUCHING_DAMAGE = 120
        self.obj.SPEED *= 1.2
        self.obj.SIGHT_DISTANCE *= 2

    def t_draw(self):
        self.set_rotation(-self.obj.velocity.get_net_rotation())
        super().t_draw()

@entity.Entities.entity_type
class ScreamingWood(Entity):
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('blood_ingot', .3, 5, 10),
        entity.IndividualLoot('bloodstone', .1, 1, 1),

    ])

    SOUND_HURT = 'sticky'
    SOUND_DEATH = 'sticky'

    NAME = 'Screaming Wood'
    DISPLAY_MODE = 3

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity_screaming_wood'], entity.TreeMonsterAI, 1200)
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 70
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 75
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 75
        self.obj.TOUCHING_DAMAGE = 220
        self.obj.SPEED *= 3
        self.obj.SIGHT_DISTANCE *= 5


