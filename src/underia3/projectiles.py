import math
import pygame as pg
from underia import projectiles, game, weapons
from values import damages, effects
from physics import vector
from resources import position
import random

class FeatherSwordMotion(projectiles.ProjectileMotion):
    FRICTION = .95
    MASS = 5

    def __init__(self, *args):
        super().__init__(*args)
        self.d = random.choice([1, -1])

    def on_update(self):
        self.apply_force(vector.Vector2D(self.rotation, 20))
        self.apply_force(vector.Vector2D(self.rotation + 90, self.d * 80))
        self.rotation = self.velocity.get_net_rotation()

class FeatherSword(projectiles.Projectiles.Projectile):
    def __init__(self, pos, rot):
        super().__init__(pos, img=game.get_game().graphics['projectiles_feather_sword'], motion=FeatherSwordMotion)
        self.obj.rotation = rot
        self.obj.apply_force(vector.Vector2D(rot, 800))
        self.tick = 0

    def damage(self):
        for e in game.get_game().entities:
            if vector.distance(*(e.obj.pos - self.obj.pos)) < 120:
                e.hp_sys.damage(weapons.WEAPONS['feather_sword'].damages[damages.DamageTypes.PHYSICAL] * .12 *  \
                                game.get_game().player.attack * game.get_game().player.attacks[0],
                                damages.DamageTypes.PHYSICAL, penetrate=50)
                self.dead = True

    def update(self):
        super().update()
        self.tick += 1
        if self.tick > 200:
            self.dead = True
        self.damage()

class FeatherThaumaturgy(projectiles.Projectiles.Projectile):
    def __init__(self, pos, rot):
        super().__init__(pos, img=game.get_game().graphics['projectiles_feather_sword'], motion=FeatherSwordMotion)
        self.obj.rotation = rot
        self.obj.apply_force(vector.Vector2D(rot, 800))
        self.tick = 0

    def damage(self):
        for e in game.get_game().entities:
            if vector.distance(*(e.obj.pos - self.obj.pos)) < 120:
                e.hp_sys.damage(20 * \
                                game.get_game().player.attack * game.get_game().player.attacks[0],
                                damages.DamageTypes.PHYSICAL, penetrate=50)
                self.dead = True

    def update(self):
        super().update()
        self.tick += 1
        if self.tick > 200:
            self.dead = True
        self.damage()

class EWoodenWand(projectiles.Projectiles.PlatinumWand):
    COL = (200, 255, 100)
    DAMAGE_AS = 'e_wooden_wand'
    IMG = 'projectiles_u3_wooden_wand'

class LycheeSpike(projectiles.Projectiles.PlatinumWand):
    COL = (50, 0, 50)
    DAMAGE_AS = 'lychee_spike'
    IMG = 'projectiles_lychee_spike'

    def __init__(self, *args):
        super().__init__(*args)
        self.obj.MASS /= 4

class Brainstorm(projectiles.Projectiles.PlatinumWand):
    COL = (0, 255, 255)
    DAMAGE_AS = 'brainstorm'
    IMG = 'projectiles_brainstorm'
    DEL = False
    LIMIT_VEL = 0
    DURATION = 40000

    def __init__(self, *args):
        super().__init__(*args)
        self.obj.MASS *= 10
        self.obj.FRICTION = 1

    def update(self):
        super().update()
        for ee in game.get_game().entities:
            ee.obj.apply_force((self.obj.pos - ee.obj.pos) * min(1, 100000000 / self.obj.MASS / abs(self.obj.pos - ee.obj.pos) ** 3))

class LycheeWand(projectiles.Projectiles.MagicCircle):
    DAMAGE_AS = 'lychee_wand'
    IMG = 'projectiles_lychee_wand'
    DURATION = 30
    ALPHA = 50
    ROT_SPEED = 1

class MysterySwiftsword(projectiles.Projectiles.Beam):
    WIDTH = 10
    DAMAGE_AS = 'mystery_swiftsword'
    COLOR = (0, 255, 255)
    DMG_TYPE = damages.DamageTypes.PHYSICAL
    DURATION = 8

class IntestinalSword(projectiles.Projectiles.Beam):
    WIDTH = 20
    DAMAGE_AS = 'intestinal_sword'
    COLOR = (120, 50, 50)
    DMG_TYPE = damages.DamageTypes.PHYSICAL
    DURATION = 12
    CUT_EFFECT = True
    LENGTH = 200
    ENABLE_IMMUNE = False

class Observe(projectiles.Projectiles.Beam):
    WIDTH = 36
    LENGTH = 2000
    DAMAGE_AS = 'observe'
    COLOR = (150, 50, 100)
    DMG_TYPE = damages.DamageTypes.PHYSICAL
    DURATION = 10
    FOLLOW_PLAYER = False
    CUT_EFFECT = True

class EWoodenArrow(projectiles.Projectiles.Arrow):
    DAMAGES = 10
    SPEED = 300
    IMG = 'u3_wooden_arrow'

class LycheeArrow(projectiles.Projectiles.Arrow):
    DAMAGES = 0
    IMG = 'u3_lychee_arrow'

    def damage(self, pos, cd):
        imr = self.d_img.get_rect(center=pos)
        x, y = pos
        for entity in game.get_game().entities:
            if imr.collidepoint(entity.obj.pos[0], entity.obj.pos[1]) or entity.d_img.get_rect(
                    center=entity.obj.pos()).collidepoint(x, y) and entity not in cd:
                entity.hp_sys.damage(
                    self.dmg * game.get_game().player.attack * game.get_game().player.attacks[1],
                    damages.DamageTypes.PIERCING)
                entity.hp_sys.effect(effects.Frozen(0.2, 1))
                if self.DELETE:
                    self.dead = True
                else:
                    cd.append(entity)
        return cd

class EBullet(projectiles.Projectiles.Bullet):
    DAMAGE_AS = 'e_bullet'
    IMG = 'projectiles_u3_bullet'
    SPEED = 1000
    TAIL_COLOR = (100, 0, 100)
    TAIL_SIZE = 4
    TAIL_WIDTH = 5

AMMO = {
    'e_wooden_arrow': EWoodenArrow,
    'e_bullet': EBullet,
}

for k, v in AMMO.items():
    projectiles.AMMOS[k] = v

class LycheeTwinblade(projectiles.Projectiles.ThiefWeapon):
    IMG = 'items_weapons_lychee_blade'
    DAMAGE_AS = 'lychee_twinblade'

THIEF_WEAPONS = {
    'lychee_twinblade': LycheeTwinblade,
}

for k, v in THIEF_WEAPONS.items():
    projectiles.THIEF_WEAPONS[k] = v

class WoodenFlute(projectiles.Projectiles.PlatinumWand):
    DAMAGE_AS = 'wooden_flute'
    IMG = 'projectiles_wooden_flute'
    SPEED = 800
    ENABLE_IMMUNE = True
    DELETE_SELF = True
    DURATION = 500
    LIMIT_VEL = 0

    def __init__(self, pos, rotation):
        super().__init__(pos, rotation)
        self.obj.apply_force(vector.Vector(rotation, self.SPEED))
        self.img = game.get_game().graphics[self.IMG]
        self.set_rotation(rotation)
        self.hit = False
        self.ar_t = random.randint(0, 754)
        self.ar_y = random.randint(0, 754)

    def update(self):
        #self.set_rotation(math.sin((self.tick + self.ar_t) / 50) * (self.ar_t / 3 + 50))
        self.obj.pos += vector.Vector2D(dy=math.sin((self.tick + self.ar_y) / 120) * (self.ar_y / 1000 + 1))
        super().update()

    def damage(self):
        for entity in game.get_game().entities:
            if (vector.distance(entity.obj.pos[0] - self.obj.pos[0], entity.obj.pos[1] - self.obj.pos[1]) <
                    120 + (entity.d_img.get_width() + self.d_img.get_height()) / 4):
                if entity.hp_sys.is_immune and self.ENABLE_IMMUNE:
                    continue
                entity.hp_sys.damage(weapons.WEAPONS[self.DAMAGE_AS].damages[
                                         damages.DamageTypes.OCTAVE] * game.get_game().player.attack *
                                     game.get_game().player.attacks[3], damages.DamageTypes.OCTAVE,
                                     )
                if self.ENABLE_IMMUNE:
                    entity.hp_sys.enable_immume()
                if not self.hit:
                    self.hit = True
                else:
                    continue
                if len(weapons.WEAPONS[self.DAMAGE_AS].gains):
                    gain = random.choice(weapons.WEAPONS[self.DAMAGE_AS].gains)
                    game.get_game().player.hp_sys.effect(
                        gain(3 + game.get_game().player.calculate_data('gain_duration', rate_data=False), 3))
                game.get_game().player.inspiration += int(weapons.WEAPONS[self.DAMAGE_AS].back_rate *
                                                          weapons.WEAPONS[self.DAMAGE_AS].inspiration_cost)
                self.dead = self.dead or self.DELETE_SELF

class TheRovingChord(WoodenFlute):
    DAMAGE_AS = 'the_roving_chord'
    IMG = 'projectiles_the_roving_chord'
    SPEED = 300
    ENABLE_IMMUNE = False
    LIMIT_VEL = 0
    DURATION = 1000

    def __init__(self, pos, rotation, d=True):
        if d:
            for i in range(2):
                game.get_game().projectiles.append(TheRovingChord(pos, rotation, False))
        super().__init__(pos, rotation)

    def update(self):
        # self.set_rotation(math.sin((self.tick + self.ar_t) / 50) * (self.ar_t / 3 + 50))
        self.obj.pos += vector.Vector2D(dy=math.sin((self.tick + self.ar_y) / 120) * 2)
        super().update()

class HolyCondense(projectiles.Projectiles.HolyLight):
    def update(self):
        self.obj.apply_force(vector.Vector2D(dx=self.ax, dy=self.ay) * 60)
        self.set_rotation(90)
        pg.draw.circle(game.get_game().displayer.canvas, (255, 255, 0),
                       position.displayed_position(self.obj.pos),
                       int(800 / game.get_game().player.get_screen_scale()),
                       int(5 / game.get_game().player.get_screen_scale()))
        self.damage()
        self.tick += 1
        if self.tick > 200:
            self.dead = True