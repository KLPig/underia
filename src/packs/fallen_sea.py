from underia import entity, game
from values import damages
from resources import position
from physics import vector
import constants

import copy
import pygame as pg

class Entity(entity.Entities.Entity):
    pass

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

class BloodflowerAI(entity.BloodflowerAI):
    pass

class SlowMoverAI(entity.SlowMoverAI):
    pass

class MonsterAI(entity.MonsterAI):
    pass

class CellsAI(entity.CellsAI):
    pass

class BuildingAI(entity.BuildingAI):
    pass

@entity.AIs.entity_ai
class UrchinAI(SlowMoverAI):
    MASS = 50
    IDLE_SPEED = 100
    FRICTION = 0.6
    TOUCHING_DAMAGE = 120
    SIGHT_DISTANCE = 500

    def __init__(self, pos):
        super().__init__(pos)
        self.timer = 0
        self.prot = 0

    def on_update(self):
        player = self.cur_target
        if self.timer > 550:
            self.timer = 0
        if player is not None:
            self.timer += 1
            if self.timer > 500:
                self.apply_force(vector.Vector2D(self.prot, 3000))
            elif self.timer > 300:
                self.prot = vector.coordinate_rotation(*(game.get_game().player.obj.pos -self.pos))
                self.apply_force(vector.Vector2D(self.prot, 700))
        else:
            self.idle()

@entity.AIs.entity_ai
class GlimmerSkateAI(MonsterAI):
    MASS = 2000
    FRICTION = 0.8
    IDLE_SPEED = 12000
    IDLE_TIME = 15
    SPEED = .7
    IDLE_CHANGER = 40
    TOUCHING_DAMAGE = 450

    SIGHT_DISTANCE = 9999


    def __init__(self, pos):
        super().__init__(pos)
        self.tick = 0
        self.dr = 0
        self.state = 0

    def update(self):
        super().update()
        self.tick += 1
        if self.tick % 800 < 400:
            self.idle()
            self.state = 0
        elif self.tick % 800 == 400:
            self.dr = vector.coordinate_rotation(*(game.get_game().player.obj.pos - self.pos))
        elif self.tick % 800 < 500:
            self.apply_force(vector.Vector2D(-self.dr, 25000))
            self.state = 1
        else:
            self.apply_force(vector.Vector2D(self.dr + self.tick * 3, 35000))
            self.state = 2

@entity.AIs.entity_ai
class PressureEyeAI(CellsAI):
    MASS = 350
    TOUCHING_DAMAGE = 220
    SPEED = 5.5
    SIGHT_DISTANCE = 800

@entity.Entities.entity_type
class GlimmerBubble(Entity):
    NAME = 'Glimmer Bubble'
    DISPLAY_MODE = 3
    DMG = 90

    def __init__(self, pos, rot):
        super().__init__(pos, game.get_game().graphics['entity_null'], MagmaKingFireballAI, 200)
        self.obj.rot = rot
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 50
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 50
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 50
        if constants.DIFFICULTY >= 3:
            self.hp_sys.IMMUNE = True

    def t_draw(self):
        super().t_draw()
        pg.draw.circle(game.get_game().displayer.canvas,
                       (0, 255, 255),
                       position.displayed_position(self.obj.pos),
                       int(60 / game.get_game().player.get_screen_scale()),
                       int(10 / game.get_game().player.get_screen_scale()))

    def on_update(self):
        super().on_update()
        self.set_rotation(self.rot)
        self.hp_sys.hp -= 5
        self.damage()

    def damage(self):
        if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                           self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 50:
            game.get_game().player.hp_sys.damage(self.DMG, damages.DamageTypes.MAGICAL)
            game.get_game().player.hp_sys.enable_immune()
            self.hp_sys.hp = 0

@entity.Entities.entity_type
class ForgottenStone(Entity):
    NAME = 'Forgotten Stone'
    DISPLAY_MODE = 3
    DMG = 110

    def __init__(self, pos, rot):
        super().__init__(pos, game.get_game().graphics['entity_forgotten_stone'], MagmaKingFireballAI, 600)
        self.obj.rot = rot
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = -30
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 0
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = -80
        if constants.DIFFICULTY >= 3:
            self.hp_sys.IMMUNE = True

    def on_update(self):
        super().on_update()
        self.set_rotation(self.rot)
        self.hp_sys.hp -= 10
        self.damage()

    def damage(self):
        if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                           self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 15:
            game.get_game().player.hp_sys.damage(self.DMG, damages.DamageTypes.MAGICAL)
            game.get_game().player.hp_sys.enable_immune()
            self.hp_sys.hp = 0

@entity.Entities.entity_type
class ForgottenFlower(Entity):
    NAME = 'Forgotten Flower'
    DISPLAY_MODE = 3
    LOOT_TABLE = LootTable([
        IndividualLoot('spikeflower', 0.36, 1, 1),
        IndividualLoot('forgotten_shard', 1, 5, 8),
        IndividualLoot('cell_organization', .7, 10, 20),
        IndividualLoot('coral_reef', .5, 10, 20),
        IndividualLoot('silver_ingot', .5, 5, 10),
        IndividualLoot('azure_amulet', .03, 1, 1),
        IndividualLoot('tsunamic_bottle', .03, 1, 1),
        IndividualLoot('diving_boots', .03, 1, 1),
        IndividualLoot('isobar', .03, 1, 1),
    ])

    SOUND_HURT = 'corrupt'
    SOUND_DEATH = 'sticky'

    def __init__(self, pos):
        if game.get_game().stage > 0:
            super().__init__(pos, copy.copy(game.get_game().graphics['entity_forgotten_flower']), BloodflowerAI, 6000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 185
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 185
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 185
            self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 95
            self.obj.TOUCHING_DAMAGE *= 4
            self.obj.SPEED *= 2
            self.obj.SIGHT_DISTANCE *= 2
            self.dt = 5
        else:
            super().__init__(pos, game.get_game().graphics['entity_forgotten_flower'], BloodflowerAI, 1200)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 25
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 25
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 25
            self.dt = 16
        self.obj.MASS *= 2.5
        self.obj.SPEED *= 8
        self.obj.FRICTION = .7
        self.obj.TOUCHING_DAMAGE *= 2
        self.obj.SIGHT_DISTANCE /= 2
        self.tick = 0

    def on_update(self):
        super().on_update()
        self.tick += 1
        self.set_rotation(-self.obj.velocity.get_net_rotation())
        if self.tick % (self.dt * 5) == 0:
            for ar in range(0, 360, 60 - (constants.DIFFICULTY + 1) // 2 * 15):
                game.get_game().entities.append(ForgottenStone(self.obj.pos, ar + self.rot))
        elif self.tick % self.dt == 0:
            for ar in range(0, 360, 120 - (constants.DIFFICULTY + 1) // 2 * 30):
                game.get_game().entities.append(ForgottenStone(self.obj.pos, ar + self.rot))

@entity.Entities.entity_type
class Urchin(Entity):
    NAME = 'Urchin'
    DISPLAY_MODE = 3
    LOOT_TABLE = LootTable([
        IndividualLoot('forgotten_shard', 1, 5, 8),
        IndividualLoot('cell_organization', .7, 10, 20),
        IndividualLoot('coral_reef', .5, 10, 20),
        IndividualLoot('silver_ingot', .5, 5, 10),
        IndividualLoot('seaprick', .03, 1, 1),
        IndividualLoot('dim_heavysword', .03, 1, 1),
        IndividualLoot('heavybow', .03, 1, 1),
        IndividualLoot('sunken_shield', .03, 1, 1),
    ])

    SOUND_HURT = 'corrupt'
    SOUND_DEATH = 'sticky'

    def __init__(self, pos):
        if game.get_game().stage > 0:
            super().__init__(pos, copy.copy(game.get_game().graphics['entity_urchin']), UrchinAI, 3000)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 285
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 285
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 285
            self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 335
            self.tr = 2.5
            self.obj.TOUCHING_DAMAGE *= 4
        else:
            super().__init__(pos, copy.copy(game.get_game().graphics['entity_urchin']), UrchinAI, 900)
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 85
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 85
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 85
            self.tr = 1.0
        self.dr = 0

    def on_update(self):
        nr = max(min(abs(game.get_game().player.obj.pos - self.obj.pos) / 2 - 300, 300), 0) - self.dr
        self.dr += nr
        self.img.set_alpha(255 - self.dr * 127 // 300)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] += nr * self.tr
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] += nr * self.tr
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] += nr * self.tr
        super().on_update()
        self.rotate(abs(self.obj.velocity) / 20)

@entity.Entities.entity_type
class LazerFish(Entity):
    NAME = 'Lazer Fish'
    DISPLAY_MODE = 2
    LOOT_TABLE =  LootTable([
        IndividualLoot('soul', .3, 10, 15),
        IndividualLoot('evil_ingot', .3, 15, 20),
        IndividualLoot('firite_ingot', 1, 18, 25),
        IndividualLoot('firy_plant', 1, 5, 8),
        IndividualLoot('coral_reef', 1, 10, 15),
        IndividualLoot('soul_of_fire', 1, 5, 7),
    ])

    SOUND_HURT = 'sticky'
    SOUND_DEATH = 'sticky'

    @staticmethod
    def is_suitable(biome: str):
        return biome in ['hot_spring', 'fallen_sea', 'ocean']

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity_lazer_fish'], CleverRangedAI, 12000)
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 240
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 200
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 300
        self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 100
        self.obj.SPEED *= 2
        self.obj.SIGHT_DISTANCE = 800
        self.obj.FRICTION = .5
        self.obj.TOUCHING_DAMAGE = 450
        self.tick = 0

    def on_update(self):
        super().on_update()
        self.tick += 1
        if self.tick % 3 == 0:
            tar = self.obj.cur_target
            if tar is not None and abs(tar.pos - self.obj.pos) > 300:
                game.get_game().entities.append(entity.Entities.Lazer(self.obj.pos,
                                                               vector.coordinate_rotation(*(tar.pos - self.obj.pos))))

@entity.Entities.entity_type
class PressureEye(Entity):
    NAME = 'Pressure Eye'
    DISPLAY_MODE = 1
    LOOT_TABLE = LootTable([
        IndividualLoot('soul', .3, 10, 15),
        IndividualLoot('evil_ingot', .3, 15, 20),
        IndividualLoot('firite_ingot', 1, 18, 25),
        IndividualLoot('blood_ingot', 1, 8, 15),
        IndividualLoot('firy_plant', 1, 5, 8),
        IndividualLoot('soul_of_fire', 1, 6, 9),
        IndividualLoot('watcher_wand', .05, 1, 1),
    ])

    SOUND_HURT = 'sticky'
    SOUND_DEATH = 'sticky'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity_pressure_eye'], PressureEyeAI, 2500)
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 240
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 200
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 300
        self.hp_sys.defenses[damages.DamageTypes.ARCANE] = 100

    def t_draw(self):
        self.set_rotation(-self.obj.velocity.get_net_rotation())
        super().t_draw()

@entity.Entities.entity_type
class GlimmerSkate(Entity):
    NAME = 'Glimmer Skate'
    DISPLAY_MODE = 1
    IS_MENACE = True
    LOOT_TABLE = LootTable([
        IndividualLoot('coral_reef', 1, 30, 50),
        IndividualLoot('forgotten_shard', 1, 30, 50),
        IndividualLoot('sea_pearl', 1, 3, 6),
    ])

    def __init__(self, pos):
        super().__init__(pos, pg.transform.scale2x(
            game.get_game().graphics['entity_glimmer_skate_body'].subsurface((42, 12, 108, 66))),
                         GlimmerSkateAI, 9000)
        b_img = [
            game.get_game().graphics['entity_glimmer_skate_tail'].subsurface((54, 54, 84, 138)),
            game.get_game().graphics['entity_glimmer_skate_lwing'].subsurface((0, 24, 96, 60)),
            game.get_game().graphics['entity_glimmer_skate_rwing'].subsurface((96, 24, 96, 60)),
        ]
        self.obj.TOUCHING_DAMAGE = 220
        self.bodies = []
        for i, b in enumerate(b_img):
            e = entity.Entities.Entity(pos, pg.transform.scale2x(b), BuildingAI, 11000 - (i == 0) * 3000)
            adf = (not i) * 40
            e.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 40 + adf
            e.hp_sys.defenses[damages.DamageTypes.PIERCING] = 40 + adf
            e.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 40 + adf
            e.obj.IS_OBJECT = False
            e.DISPLAY_MODE = 1
            e.get_shown_txt = lambda *args: ('', '')
            self.bodies.append(e)
            game.get_game().entities.insert(0, e)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 400
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 400
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 400
        self.tick = 0
        self.dt = 3

    def t_draw(self):
        self.tick += 1
        self.set_rotation(-self.obj.velocity.get_net_rotation())
        super().t_draw()
        sn = len([1 for b in self.bodies if b.hp_sys.hp > 0])
        if sn < self.dt:
            an = self.dt - sn
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] -= 95 * an
            self.hp_sys.defenses[damages.DamageTypes.PIERCING] -= 95 * an
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] -= 95 * an
            self.dt -= an
            self.obj.SPEED *= 1.3 ** an
        ap = [vector.Vector2D(0, 78), vector.Vector2D(48, -24), vector.Vector2D(-48, -24), ]
        for i, b in enumerate(self.bodies):
            b.DISPLAY_MODE = 1
            b.set_rotation(self.rot)
            ax, ay = ap[i] * 2
            b.obj.pos = self.obj.pos + vector.Vector2D(-self.rot, ay) + vector.Vector2D(-self.rot + 90, ax)
        if sn == 0:
            if self.tick % 18 == 1 and self.obj.state != 1:
                for r in range(0, 360, 60 - (constants.DIFFICULTY + 1) // 2 * 15):
                    game.get_game().entities.append(GlimmerBubble(self.obj.pos, -self.rot + r))
        elif self.obj.state == 1:
            if self.tick % 15 == 1:
                if self.bodies[1].hp_sys.hp > 0:
                    game.get_game().entities.append(GlimmerBubble(self.obj.pos, -self.rot - 90))
                if self.bodies[2].hp_sys.hp > 0:
                    game.get_game().entities.append(GlimmerBubble(self.obj.pos, -self.rot + 90))
        elif self.obj.state == 2:
            if self.tick % 5 == 1:
                if self.bodies[1].hp_sys.hp > 0:
                    game.get_game().entities.append(GlimmerBubble(self.obj.pos, -self.rot - 90))


