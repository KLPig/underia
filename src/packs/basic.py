from underia import entity, game
from values import damages, effects
from resources import position
from physics import vector
import constants
from visual import draw

import random

class BuildingAI(entity.BuildingAI):
    pass

class SlowMoverAI(entity.SlowMoverAI):
    pass


@entity.AIs.entity_ai
class TreeMonsterAI(entity.MonsterAI):
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

@entity.AIs.entity_ai
class CactusAI(TreeMonsterAI):
    TOUCHING_DAMAGE = 30

@entity.AIs.entity_ai
class EyeAI(entity.MonsterAI):
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
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py) + 180, 10))
            elif self.timer < 190:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 30))
            elif self.timer < 195:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 300))
        else:
            self.idle()

@entity.AIs.entity_ai
class MagmaCubeAI(SlowMoverAI):
    TOUCHING_DAMAGE = 66


@entity.AIs.entity_ai
class CloseBloodflowerAI(SlowMoverAI):
    MASS = 240
    TOUCHING_DAMAGE = 24


@entity.AIs.entity_ai
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
                    self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 180))
                else:
                    self.apply_force(vector.Vector(vector.coordinate_rotation(px, py) + self.prot, 60))
                if self.touched_player:
                    self.timer = 0
                    self.prot = random.randint(150, 210)
            else:
                self.idle()
        else:
            self.idle()

@entity.AIs.entity_ai
class SoulFlowerAI(BloodflowerAI):
    TOUCHING_DAMAGE = 128

@entity.AIs.entity_ai
class SnowDrakeAI(BloodflowerAI):
    TOUCHING_DAMAGE = 220
    MASS = 220

@entity.AIs.entity_ai
class RedWatcherAI(SlowMoverAI):
    FRICTION = 0.92
    MASS = 400
    TOUCHING_DAMAGE = 54
    SPEED = 1.5

class RangedAI(entity.RangedAI):
    pass

@entity.AIs.entity_ai
class TrueEyeAI(entity.MonsterAI):
    MASS = 700
    FRICTION = 0.97
    TOUCHING_DAMAGE = 55
    SIGHT_DISTANCE = 99999

    def __init__(self, pos):
        super().__init__(pos)
        self.timer = 0
        self.phase = 0
        self.trt = 0

    def on_update(self):
        if self.timer < 0:
            self.timer += 1
            return
        self.timer = (self.timer + 1) % (350 + self.phase * 100)
        player = game.get_game().player
        px = player.obj.pos[0] - self.pos[0]
        py = player.obj.pos[1] - self.pos[1]
        if self.phase <= 2:
            if 0 < self.timer < 100:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py) + 180, 20 - self.phase * 5))
            elif self.timer < 200:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px, py), 120 + self.phase * 240))
            elif self.timer % (50 - self.phase * 10) == 0:
                self.trt = vector.coordinate_rotation(px, py)
                if constants.DIFFICULTY >= 2:
                    self.velocity /= 10000
            elif self.timer % (50 - self.phase * 10) < 12:
                self.apply_force(vector.Vector(self.trt, 2000 - self.phase * 200))
        elif self.phase <= 4:
            if self.timer < 450:
                if self.timer % 150 <= 100:
                    self.trt = vector.coordinate_rotation(px, py)
                    if constants.DIFFICULTY >= 2:
                        self.velocity /= 10000
                    self.apply_force(vector.Vector2D(self.trt, 10))
                else:
                    self.apply_force(vector.Vector(self.trt, 3500))
            else:
                self.pos << (self.pos[0] * 4 // 5 + game.get_game().player.obj.pos[0] // 5,
                            self.pos[1] * 4 // 5 + game.get_game().player.obj.pos[1] // 5 - 400 + constants.DIFFICULTY * 110)


@entity.Entities.entity_type
class Eye(entity.Entities.Entity):
    NAME = 'Eye'
    DISPLAY_MODE = 1
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('dangerous_necklace', 0.1, 1, 1),
        entity.IndividualLoot('cell_organization', 0.8, 1, 3),
        entity.IndividualLoot('watcher_wand', 0.06, 1, 1),
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
            self.obj.TOUCHING_DAMAGE = 50
            self.NAME = 'The Eye'
            self.obj.TOUCHING_DAMAGE *= 6

    def t_draw(self):
        super().t_draw()
        if self.hp_sys.hp <= 0:
            b = 0
            if not 'M1' in game.get_game().player.nts and random.random() < .1:
                game.get_game().player.nts.append('M1')
                b = 1
            if b:
                game.get_game().dialog.push_dialog('[Notebook Updated!]')

    def on_update(self):
        super().on_update()
        self.set_rotation((self.rot * 5 - self.obj.velocity.get_net_rotation()) // 6)


@entity.Entities.entity_type
class Tree(entity.Entities.Entity):
    NAME = 'Tree'
    DISPLAY_MODE = 3
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('wood', 0.9, 15, 25),
        entity.IndividualLoot('leaf', 0.9, 5, 7),
        entity.IndividualLoot('red_apple', 0.03, 1, 1),
    ])
    DIVERSITY = False

    @staticmethod
    def is_suitable(biome: str):
        return biome in ['forest', 'rainforest']

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity_tree'], BuildingAI, 10)
        self.hp_sys(op='config', maximum_damage=3)

    def t_draw(self):
        super().t_draw()
        if self.hp_sys.hp <= 0:
            b = 0
            if not 'L1' in game.get_game().player.nts:
                game.get_game().player.nts.append('L1')
                b = 1
            if not 'M1C' in game.get_game().player.nts and random.random() < .1:
                game.get_game().player.nts.append('M1C')
                b = 1
            if b:
                game.get_game().dialog.push_dialog('[Notebook Updated!]')

@entity.Entities.entity_type
class HugeTree(entity.Entities.Entity):
    NAME = 'Huge Tree'
    DISPLAY_MODE = 3
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('wood', 0.9, 30, 50),
        entity.IndividualLoot('red_apple', 0.07, 1, 1),
    ])

    @staticmethod
    def is_suitable(biome: str):
        return biome in ['rainforest']

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity_huge_tree'], BuildingAI, 200)
        self.hp_sys(op='config', maximum_damage=50)


    def t_draw(self):
        super().t_draw()
        if self.hp_sys.hp <= 0:
            b = 0
            if not 'M1C' in game.get_game().player.nts and random.random() < .1:
                game.get_game().player.nts.append('M1C')
                b = 1
            if b:
                game.get_game().dialog.push_dialog('[Notebook Updated!]')

@entity.Entities.entity_type
class TreeMonster(entity.Entities.Entity):
    NAME = 'Tree Monster'
    DISPLAY_MODE = 3
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('wood', 0.5, 5, 12),
        entity.IndividualLoot('leaf', 0.8, 1, 2),
        entity.IndividualLoot('copper', 0.6, 8, 18),
        entity.IndividualLoot('red_apple', 0.04, 1, 1),
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

@entity.Entities.entity_type
class ClosedBloodflower(entity.Entities.Entity):
    NAME = 'Closed Bloodflower'
    DISPLAY_MODE = 3
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('copper', 0.9, 8, 18),
        entity.IndividualLoot('cell_organization', 0.5, 2, 8),
        entity.IndividualLoot('leaf', 0.5, 7, 12),
        entity.IndividualLoot('spikeflower', 0.18, 1, 1),
        entity.IndividualLoot('red_apple', 0.02, 1, 1),
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

@entity.Entities.entity_type
class Bloodflower(entity.Entities.Entity):
    NAME = 'Bloodflower'
    DISPLAY_MODE = 3
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('cell_organization', 0.9, 12, 16),
        entity.IndividualLoot('spikeflower', 0.36, 1, 1),
        entity.SelectionLoot([('purple_ring', 1, 1), ('cyan_ring', 1, 1), ('yellow_ring', 1, 1)], 0, 1),
        entity.IndividualLoot('red_apple', 0.02, 1, 1),
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

@entity.Entities.entity_type
class RedWatcher(entity.Entities.Entity):
    NAME = 'Red Watcher'
    DISPLAY_MODE = 3
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('magic_stone', 0.2, 5, 10),
        entity.SelectionLoot([('purple_ring', 1, 1), ('cyan_ring', 1, 1), ('yellow_ring', 1, 1)], 1, 2),
    ])

    SOUND_HURT = 'corrupt'
    SOUND_DEATH = 'monster'

    def __init__(self, pos):
        if game.get_game().stage > 0:
            super().__init__(pos, game.get_game().graphics['entity_red_watcher'], RedWatcherAI, int(12000 * 1.5 ** (game.get_game().stage - 3 * game.get_game().chapter)))
        else:
            super().__init__(pos, game.get_game().graphics['entity_red_watcher'], RedWatcherAI, 1500)
        self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = 2.5
        self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 2.44
        self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 2.52
        if game.get_game().stage > 0:
            self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = 2.75
            self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 2.64
            self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 2.76
            self.NAME = f'The Red-Watcher LV.{(game.get_game().stage + constants.DIFFICULTY - 3 * game.get_game().chapter)}'
            self.obj.SPEED *= 10 + 3 * (game.get_game().stage + constants.DIFFICULTY - 3 * game.get_game().chapter)
            self.obj.MASS *= 9
            self.obj.TOUCHING_DAMAGE *= 7 + 2 * (game.get_game().stage + constants.DIFFICULTY - 3 * game.get_game().chapter)
        self.tick = 0

    def on_update(self):
        super().on_update()
        self.tick += 1
        if game.get_game().stage + constants.DIFFICULTY >= 2:
            if self.tick % (120 - max(20, constants.DIFFICULTY + game.get_game().stage) * 20) * 5 == 0:
                pp = game.get_game().player.obj.pos
                self.obj.pos = pp + vector.Vector2D(random.randint(0, 360), random.randint(100, 400))

@entity.Entities.entity_type
class Cactus(entity.Entities.Entity):
    NAME = 'Cactus'
    DISPLAY_MODE = 3
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('wood', 0.9, 15, 25),
        entity.IndividualLoot('copper', 0.6, 8, 18),
        entity.IndividualLoot('cactus_wand', 0.2, 1, 1),
        entity.IndividualLoot('red_apple', 0.04, 1, 1),
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

@entity.Entities.entity_type
class ConiferousTree(entity.Entities.Entity):
    NAME = 'Coniferous Tree'
    DISPLAY_MODE = 3
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('wood', 0.9, 15, 25),
        entity.IndividualLoot('copper', 0.6, 8, 18),
        entity.IndividualLoot('coniferous_leaf', 0.2, 50, 200),
        entity.IndividualLoot('red_apple', 0.06, 1, 1),
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


    def t_draw(self):
        super().t_draw()
        if self.hp_sys.hp <= 0:
            b = 0
            if not 'M1C' in game.get_game().player.nts and random.random() < .1:
                game.get_game().player.nts.append('M1C')
                b = 1
            if b:
                game.get_game().dialog.push_dialog('[Notebook Updated!]')

@entity.Entities.entity_type
class MagmaCube(entity.Entities.Entity):
    NAME = 'Magma Cube'
    DISPLAY_MODE = 3
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('cell_organization', 0.9, 10, 15),
        entity.IndividualLoot('blood_ingot', 0.2, 5, 10),
        entity.IndividualLoot('firite_ingot', 0.5, 8, 15),
    ])

    SOUND_HURT = 'sticky'
    SOUND_DEATH = 'sticky'

    @staticmethod
    def is_suitable(biome: str):
        return biome in ['hell', 'hot_spring']

    def __init__(self, pos):
        if game.get_game().stage > 0:
            super().__init__(pos, game.get_game().graphics['entity_magma_cube'], RangedAI, 12000)
        else:
            super().__init__(pos, game.get_game().graphics['entity_magma_cube'], MagmaCubeAI, 1100)
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 10
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 8
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 15
        if game.get_game().stage > 0:
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 62
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 60
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 60
            self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 30
            self.NAME = 'The Fireball Magma Cube'
            self.obj.SPEED *= 1.5
            self.obj.MASS *= 1.5
            self.obj.TOUCHING_DAMAGE *= 6
            self.LOOT_TABLE = entity.LootTable([
                entity.IndividualLoot('cell_organization', .3, 10, 15),
                entity.IndividualLoot('blood_ingot', .3, 15, 20),
                entity.IndividualLoot('firite_ingot', 1, 18, 25),
                entity.IndividualLoot('firy_plant', 1, 5, 8),
                entity.IndividualLoot('soul_of_fire', 1, 5, 7),
            ])

        self.tick = 0

    def on_update(self):
        super().on_update()
        self.tick += 1
        if game.get_game().stage and self.tick % 5 == 0:
            px, py = game.get_game().player.obj.pos
            px -= self.obj.pos[0]
            py -= self.obj.pos[1]
            if vector.distance(px, py) > 800:
                return
            fb = entity.Entities.MagmaKingFireball(self.obj.pos, vector.coordinate_rotation(px, py))
            fb.DMG = 150
            game.get_game().entities.append(fb)


@entity.Entities.entity_type
class TrueEye(entity.Entities.Entity):
    NAME = 'True Eye'
    DISPLAY_MODE = 1
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('blood_ingot', 1, 20, 30),
        entity.IndividualLoot('platinum', 1, 20, 30),
        entity.IndividualLoot('zirconium', 1, 20, 30),
        entity.SelectionLoot([('orange_ring', 1, 1), ('blue_ring', 1, 1), ('green_ring', 1, 1)], 1, 1),
        entity.SelectionLoot([('tearblade', 1, 1), ('gaze', 1, 1), ('blood_watcher_wand', 1, 1)], 1, 1),
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
        for d in self.hp_sys.defenses.defences.keys():
            self.hp_sys.defenses[d] += max(0, constants.DIFFICULTY * 11 - 11)
        self.phase = 0
        self.tick = 0
        self.ses = []
        if constants.DIFFICULTY <= 1:
            self.PHASE_SEGMENTS = [0.3, 0.7]
        elif constants.DIFFICULTY <= 2:
            self.PHASE_SEGMENTS = [0.002, 0.3, 0.7]
        else:
            self.PHASE_SEGMENTS = [3 / self.hp_sys.max_hp, 0.002, 0.3, 0.7]
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
                    entity.IndividualLoot('otherworld_stone', 1, 10, 20),
                )
                self.LOOT_TABLE.loot_list.append(
                    entity.IndividualLoot('eye_lens', 1, 1, 1),
                )
            self.NAME = 'The True Eye - Otherworld'
            self.img = game.get_game().graphics['entity_true_eye_otherworld']
            self.d = True
        else:
            self.d = False

    def on_hit(self, plyr):
        if constants.DIFFICULTY >= 2:
            plyr.hp_sys.effect(effects.Bleeding(2 if constants.DIFFICULTY == 2 else 5, 1))

    def on_update(self):
        super().on_update()
        if self.hp_sys.hp <= .03 and self.phase >= 4:
            self.obj.SPEED = 0
            self.obj.TOUCHING_DAMAGE = 0
            self.obj.IS_OBJECT = False
            self.set_rotation(self.rot + 72)
            self.hp_sys.hp -= 0.001
            self.obj.phase = 5
            return
        else:
            self.obj.IS_OBJECT = True
        if self.obj.timer > 0:
            self.set_rotation((self.rot * 8 - self.obj.velocity.get_net_rotation()) // 9)
        else:
            self.set_rotation(self.rot + 72)
            self.hp_sys(op='config', immune=self.obj.timer < -5)
        if self.obj.timer % (50 - self.obj.phase * 10) == 0 and self.obj.timer >= 200:
            self.play_sound('eoc_roar')
        if self.hp_sys.hp <= self.hp_sys.max_hp * 0.7 and self.phase == 0:
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] -= 20
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] -= 20
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] -= 20
            self.obj.TOUCHING_DAMAGE += 10 + self.d * 10
            self.obj.phase = 1
            self.phase = 1
            self.obj.timer = -200
            if not self.d:
                self.img = game.get_game().graphics['entity_true_eye_phase2']
            self.set_rotation(self.rot)
            self.play_sound('spawn_boss')
            game.get_game().displayer.shake_amp += 20
        if self.hp_sys.hp <= self.hp_sys.max_hp * 0.3 and self.phase == 1:
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] -= 5
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] -= 5
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] -= 5
            self.obj.TOUCHING_DAMAGE += 15 + self.d * 10
            self.obj.phase = 2
            self.phase = 2
            self.obj.timer = -200
            if not self.d:
                self.img = game.get_game().graphics['entity_true_eye_phase3']
            self.set_rotation(self.rot)
            self.play_sound('spawn_boss')
            game.get_game().displayer.shake_amp += 20
        if self.hp_sys.hp <= self.hp_sys.max_hp * 0.002 and self.phase == 2 and constants.DIFFICULTY > 1:
            self.hp_sys.hp = self.hp_sys.max_hp * .002 - .1
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] += 100
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] += 100
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] += 100
            self.obj.TOUCHING_DAMAGE += 10 + self.d * 10
            self.obj.phase = 3
            self.phase = 3
            self.obj.timer = -200
            self.img.set_alpha(100)
            self.set_rotation(self.rot)
            self.play_sound('spawn_boss')
            game.get_game().displayer.shake_amp += 20
        if self.hp_sys.hp <= 3 and self.phase == 3 and constants.DIFFICULTY > 2:
            self.hp_sys.IMMUNE = True
            self.obj.phase = 4
            self.phase = 4
            self.obj.timer = -50
            self.img.set_alpha(30)
            self.play_sound('spawn_boss')
            game.get_game().displayer.shake_amp += 20
        if self.phase == 4:
            self.hp_sys.hp -= .002
            self.hp_sys.IMMUNE = True
        self.tick += 1
        if self.tick % (80 - constants.DIFFICULTY * 15 - self.phase * 7) == 0:
            game.get_game().entities.append(Eye((self.obj.pos[0], self.obj.pos[1] + 1)))
        elif self.obj.timer == 540:
            for _ in range(5 + constants.DIFFICULTY * 8 + self.phase):
                rx, ry = random.randint(-200, 200), random.randint(-200, 200)
                i = Eye((self.obj.pos[0] + rx, self.obj.pos[1] + ry))
                if constants.DIFFICULTY == 0:
                    i.hp_sys.max_hp = 1
                    i.hp_sys.hp = 1
                elif constants.DIFFICULTY == 1:
                    i.hp_sys.max_hp /= 5
                    i.hp_sys.hp /= 5
                elif constants.DIFFICULTY == 3:
                    i.hp_sys.IMMUNE = True
                    i.VITAL = True
                i.LOOT_TABLE = entity.LootTable([])
                px, py = game.get_game().player.obj.pos
                px -= i.obj.pos[0]
                py -= i.obj.pos[1]
                i.obj.apply_force(vector.Vector(vector.coordinate_rotation(px, py), vector.distance(px, py)))
                game.get_game().entities.append(i)
        self.ses.clear()
        if constants.DIFFICULTY >= 1:
            for e in game.get_game().entities:
                if type(e) is Eye and abs(e.obj.pos - self.obj.pos) < constants.DIFFICULTY * 400 - 300:
                    self.ses.append(e.obj.pos)
            for r in [damages.DamageTypes.PHYSICAL, damages.DamageTypes.MAGICAL, damages.DamageTypes.PIERCING]:
                self.hp_sys.resistances[r] = max(0, 1 - len(self.ses) * [0, 0.01, 0.1, 0.25][constants.DIFFICULTY]) \
                    if self.phase <= 2 else [1, .3, .15, 0.05][constants.DIFFICULTY]
            if self.phase == 3:
                self.obj.TOUCHING_DAMAGE = 90 + len(self.ses) * [0, 2, 4, 7][constants.DIFFICULTY]
            elif self.phase == 4:
                self.obj.TOUCHING_DAMAGE = 95 + len(self.ses) * [0, 3, 5, 9][constants.DIFFICULTY]

    def t_draw(self):
        for ip in self.ses:
            draw.line(game.get_game().displayer.canvas, (255, 0, 0),
                         position.displayed_position(self.obj.pos),
                         position.displayed_position(ip), 2)
        super().t_draw()
        if self.hp_sys.hp <= 1 and constants.DIFFICULTY >= 3 and self.phase == 3:
            self.hp_sys.hp = 1
        if self.hp_sys.hp <= .002 * self.hp_sys.max_hp and constants.DIFFICULTY >= 2 and self.phase == 2:
            self.hp_sys.hp = .002 * self.hp_sys.max_hp

        if self.hp_sys.hp <= 0:
            b = 0
            if not 'D1' in game.get_game().player.nts:
                game.get_game().player.nts.append('D1')
                b = 1
            if not 'M2' in game.get_game().player.nts and random.random() < .1:
                game.get_game().player.nts.append('M2')
                b = 1
            if b:
                game.get_game().dialog.push_dialog('[Notebook Updated!]')

            if not len([1 for f in game.get_game().furniture if type(f) is entity.Entities.NPCGuide]):
                gd = entity.Entities.NPCGuide((0, 0))
                game.get_game().furniture.append(gd)
                game.get_game().dialog.push_dialog(f'{gd.name} arrived!')



