import math
import pygame as pg
from underia import projectiles, game, weapons
from values import damages, effects
from physics import vector
from visual import draw
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

class FeatherFeatherSwordMotion(projectiles.ProjectileMotion):
    FRICTION = .95
    MASS = 5

    def __init__(self, *args):
        super().__init__(*args)
        self.d = random.choice([1, -1])
        self.tgt = vector.Vector2D()
        self.sgt = vector.Vector2D(0, 0, *self.pos)
        self.dead = False
        self.tpos = vector.Vector2D(0, 0, *self.pos)

    def on_update(self):
        self.tgt = (self.tgt * 100 +
                    position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        self.tgt /= 101
        rg = float(abs(self.tpos - self.sgt)) / abs(self.tgt - self.sgt)
        rg += min(0.03, 80 / abs(self.tgt - self.sgt))
        self.pos = (self.tgt - self.sgt) * rg
        self.pos += self.sgt
        self.tpos = vector.Vector2D(0, 0, *self.pos)
        rot = (self.tgt - self.sgt).get_net_rotation()
        self.pos += vector.Vector2D(rot + 90 * self.d, (math.sin(math.pi * rg) if rg < 1 else -rg ** 2) * abs(self.tgt - self.sgt) * .4)
        if rg > 20:
            self.dead = True

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

class FeatherFeatherSword(projectiles.Projectiles.Projectile):
    def __init__(self, pos, rot):
        super().__init__(pos, img=game.get_game().graphics['entity_null'], motion=FeatherFeatherSwordMotion)
        self.obj.rotation = rot
        self.tick = 0
        self.obj.tgt << position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
        self.pp = []

    def damage(self):
        for e in game.get_game().entities:
            if vector.distance(*(e.obj.pos - self.obj.pos)) < 120:
                e.hp_sys.damage(weapons.WEAPONS['feather_feather_sword'].damages[damages.DamageTypes.PHYSICAL] * .1 *  \
                                game.get_game().player.attack * game.get_game().player.attacks[0],
                                damages.DamageTypes.PHYSICAL, penetrate=300)
                self.dead = True

    def update(self):
        self.pp.append(self.obj.pos.to_value())
        if len(self.pp) > 10:
            self.pp.pop(0)
        self.dead = self.obj.dead or self.dead
        for i in range(len(self.pp) - 1):
            draw.line(game.get_game().displayer.canvas, (255, 255, 255), position.displayed_position(self.pp[i]),
                      position.displayed_position(self.pp[i + 1]), int((5 + i * 2) / game.get_game().player.get_screen_scale()))
        super().update()
        self.tick += 1
        if self.tick > 500:
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

class EarthsTwinbladeForest(projectiles.Projectiles.NightsEdge):
    DAMAGE_AS = 'earths_twinblade'
    IMG = 'projectiles_earths_twinblade_forest'
    DMG_RATE = 1
    COL = (200, 255, 100)
    DMG_TYPE = damages.DamageTypes.PIERCING
    ENABLE_IMMUNE = 2.5
    DECAY_RATE = 0.9

    def __init__(self, *args):
        super().__init__(*args)
        self.obj.MASS /= 20
        self.obj.apply_force(self.obj.velocity * self.obj.MASS)
        self.obj.velocity += game.get_game().player.obj.velocity

    def update(self):
        super().update()
        self.obj.FRICTION = .4

    def damage(self):
        game.get_game().displayer.point_light(self.COL, position.displayed_position(self.obj.pos), 2.5,
                                              (self.d_img.get_width() + self.d_img.get_height()) * .55)
        kb = weapons.WEAPONS[self.DAMAGE_AS].knock_back
        for ee in game.get_game().entities:
            if (vector.distance(ee.obj.pos[0] - self.obj.pos[0], ee.obj.pos[1] - self.obj.pos[1]) <
                50 + (ee.d_img.get_width() + self.d_img.get_height())) / 4 and not ee.hp_sys.is_immune:
                at_mt = {damages.DamageTypes.PHYSICAL: 0, damages.DamageTypes.PIERCING: 1,
                         damages.DamageTypes.ARCANE: 2, damages.DamageTypes.MAGICAL: 2}[self.WT]
                ee.hp_sys.damage(
                    weapons.WEAPONS[self.DAMAGE_AS].damages[self.DMG_TYPE] * game.get_game().player.attack *
                    game.get_game().player.attacks[at_mt] * self.DMG_RATE, self.DMG_TYPE)
                self.dead = self.dead or self.DEL
                if not ee.hp_sys.is_immune:
                    r = vector.coordinate_rotation(ee.obj.pos[0] - self.obj.pos[0],
                                                   ee.obj.pos[1] - self.obj.pos[1])
                    ee.obj.velocity += vector.Vector2D(r, kb)
                    self.DMG_RATE *= self.DECAY_RATE
                ee.hp_sys.enable_immume(self.ENABLE_IMMUNE)
                self.damage_particle()
                break


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

class AbyssFury(projectiles.Projectiles.PlatinumWand):
    COL = (100, 0, 0)
    DAMAGE_AS = 'abyss_fury'
    IMG = 'entity_null'
    DEL = False
    LIMIT_VEL = -10
    DURATION = 1000
    DECAY_RATE = 1

    def __init__(self, pos, rot):
        super().__init__(pos, rot)
        self.obj.velocity.clear()
        self.obj.velocity += vector.Vector2D(rot, 80)
        self.obj.FRICTION = .9999

        self.poss = []

    def update(self):
        super().update()
        self.poss.append(self.obj.pos.to_value())
        if len(self.poss) > 15:
            self.poss.pop(0)
        for i in range(len(self.poss) - 1):
            draw.line(game.get_game().displayer.canvas, (255 * i // len(self.poss), 0, 0),
                      position.displayed_position(self.poss[i]),
                      position.displayed_position(self.poss[i + 1]), i * 10 // len(self.poss) + 1)

        tar, _ = self.get_closest_entity()
        if tar is None:
            return

        ap = tar.obj.pos - self.obj.pos
        ap = ap / abs(ap)
        self.obj.velocity += ap * 35

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

class U3Arrow(projectiles.Projectiles.Arrow):
    SPEED_RATE = .15
    DURATION = 400

class EWoodenArrow(U3Arrow):
    DAMAGES = 10
    SPEED = 300
    IMG = 'u3_wooden_arrow'

class FeatherArrow(U3Arrow):
    DAMAGES = 35
    SPEED = 500
    IMG = 'feather_arrow'\

    def damage(self, pos, cd):
        x, y = pos
        for ee in game.get_game().entities:
            if ee.ueid in cd:
                continue
            if (vector.distance(ee.obj.pos[0] - x, ee.obj.pos[1] - y) <
                    (
                            ee.d_img.get_width() + ee.d_img.get_height() + self.d_img.get_width() + self.d_img.get_height()) / 4 + 80):
                ee.hp_sys.damage(
                    self.dmg * game.get_game().player.attack * game.get_game().player.attacks[1] * .5,
                    damages.DamageTypes.PIERCING, penetrate=self.dmg * game.get_game().player.attack * game.get_game().player.attacks[1] * 3)
                if self.DELETE:
                    self.dead = True
                else:
                    self.dmg *= .8
                    self.TAIL_WIDTH = self.TAIL_WIDTH * 4 // 5
                    if self.dmg < 1:
                        self.dead = True
                    cd.append(ee.ueid)
        return cd

class ToxicArrow(U3Arrow):
    DAMAGES = 24
    SPEED = 400
    IMG = 'toxic_arrow'
    TAIL_COLOR = (200, 255, 100)

    def __init__(self, pos, rotation, speed, damage, t=0):
        super().__init__(pos, rotation, speed, damage)
        self.args = (pos, rotation, speed, damage, 1)
        self.t = t

    def update(self):
        super().update()
        if not random.randint(0, 30) and not self.t:
            self.dead = True
            self.t = 1
            for _ in range(random.randint(3, 5)):
                pj = ToxicArrow(self.obj.pos, self.rot + random.randint(-20, 20),
                                self.SPEED * 12 // 10, self.args[3], 1)
                game.get_game().projectiles.append(pj)

class RottenArrow(U3Arrow):
    DAMAGES = 45
    SPEED = 800
    IMG = 'rotten_arrow'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tc = 2

    def damage(self, pos, cd):
        x, y = pos
        for ee in game.get_game().entities:
            if ee.ueid in cd:
                continue
            if (vector.distance(ee.obj.pos[0] - x, ee.obj.pos[1] - y) <
                    (ee.d_img.get_width() + ee.d_img.get_height() + self.d_img.get_width() + self.d_img.get_height()) / 4 + 80) and \
                not ee.hp_sys.is_immune:
                ee.hp_sys.damage(
                    self.dmg * game.get_game().player.attack * game.get_game().player.attacks[1],
                    damages.DamageTypes.PIERCING)
                ee.hp_sys.enable_immume(.5)
                if not self.tc:
                    self.dead = True
                else:
                    self.tc -= 1
        return cd


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
    'feather_arrow': FeatherArrow,
    'toxic_arrow': ToxicArrow,
    'rotten_arrow': RottenArrow,
}

for k, v in AMMO.items():
    projectiles.AMMOS[k] = v

class LycheeTwinblade(projectiles.Projectiles.ThiefWeapon):
    IMG = 'items_weapons_lychee_blade'
    DAMAGE_AS = 'lychee_twinblade'

class EarthsTwinbladeSnow(projectiles.Projectiles.ThiefWeapon):
    IMG = 'items_weapons_magic_blade'
    DAMAGE_AS = 'earths_twinblade'

    def damage(self):
        for ee in game.get_game().entities:
            if vector.distance(ee.obj.pos[0] - self.obj.pos[0],
                               ee.obj.pos[1] - self.obj.pos[1]) < self.DMG_RANGE:
                if not ee.hp_sys.is_immune:
                    ee.hp_sys.damage(weapons.WEAPONS[self.DAMAGE_AS].damages[
                                             damages.DamageTypes.PIERCING] * game.get_game().player.attack *
                                     game.get_game().player.attacks[1], damages.DamageTypes.PIERCING)
                    ee.hp_sys.effect(effects.Frozen(1.5, 1))
                    ee.hp_sys.enable_immume(2.5)
                self.dead = self.dead or self.DEAD_DELETE

class EarthsTwinblade(projectiles.Projectiles.ThiefWeapon):
    def __init__(self, pos, rot, power):
        super().__init__(pos, rot, power)
        self.dead = True
        bt = weapons.WEAPONS['earths_twinblade'].attr
        if bt == 'forest':
            game.get_game().projectiles.append(EarthsTwinbladeForest(pos, rot))
        elif bt == 'snowland':
            game.get_game().projectiles.append(EarthsTwinbladeSnow(pos, rot, power))

THIEF_WEAPONS = {
    'lychee_twinblade': LycheeTwinblade,
    'earths_twinblade': EarthsTwinblade,
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

class GrowthEater(projectiles.Projectiles.LifeDevourer):
    DAMAGE_AS = 'lost__growth_eater'
    DMG_TYPE = damages.DamageTypes.PHYSICAL

class AncientSwiftsword(projectiles.Projectiles.NightsEdge):
    DAMAGE_AS = 'ancient_swiftsword'
    IMG = 'projectiles_ancient_swiftsword'
    DMG_RATE = 1.5
    COL = (0, 255, 255)
    DMG_TYPE = damages.DamageTypes.PHYSICAL
    ENABLE_IMMUNE = 2.5
    DECAY_RATE = 0.9

    def __init__(self, *args):
        super().__init__(*args)
        self.obj.MASS /= 5
        self.obj.apply_force(self.obj.velocity * self.obj.MASS)
        self.obj.velocity += game.get_game().player.obj.velocity

    def update(self):
        super().update()
        self.obj.FRICTION = 1

class AbyssRanseur(projectiles.Projectiles.PlatinumWand):
    DAMAGE_AS = 'abyss_ranseur'
    IMG = 'items_weapons_abyss_ranseur'
    DMG_RATE = 1
    COL = (100, 0, 0)
    DMG_TYPE = damages.DamageTypes.PHYSICAL
    ENABLE_IMMUNE = .5
    DURATION = 200
    LIMIT_VEL = -100
    DEL = False

    def __init__(self, *args):
        super().__init__(*args)
        self.obj.MASS /= 5
        self.obj.apply_force(self.obj.velocity * self.obj.MASS)
        self.obj.velocity += game.get_game().player.obj.velocity

        self.tar = None
        self.ap = vector.Vector2D()
        self.tk = 0

    def damage(self):
        self.tk += 1
        game.get_game().displayer.point_light(self.COL, position.displayed_position(self.obj.pos), 2.5,
                                              (self.d_img.get_width() + self.d_img.get_height()) * .55)
        if self.tar is not None:
            self.obj.pos << self.ap + self.tar.obj.pos
            if self.tk % 15 == 0:
                self.tar.hp_sys.damage(weapons.WEAPONS[self.DAMAGE_AS].damages[self.DMG_TYPE] * game.get_game().player.attack *
                                       game.get_game().player.attacks[0] * self.DMG_RATE * .2, self.DMG_TYPE, penetrate=100)
                self.tar.hp_sys.enable_immume(self.ENABLE_IMMUNE)
            return
        kb = weapons.WEAPONS[self.DAMAGE_AS].knock_back
        for ee in game.get_game().entities:
            if (vector.distance(ee.obj.pos[0] - self.obj.pos[0], ee.obj.pos[1] - self.obj.pos[1]) <
                50 + (ee.d_img.get_width() + self.d_img.get_height())) / 4 and not ee.hp_sys.is_immune:
                at_mt = {damages.DamageTypes.PHYSICAL: 0, damages.DamageTypes.PIERCING: 1,
                         damages.DamageTypes.ARCANE: 2, damages.DamageTypes.MAGICAL: 2}[self.WT]
                ee.hp_sys.damage(
                    weapons.WEAPONS[self.DAMAGE_AS].damages[self.DMG_TYPE] * game.get_game().player.attack *
                    game.get_game().player.attacks[at_mt] * self.DMG_RATE, self.DMG_TYPE)
                if not ee.hp_sys.is_immune:
                    r = vector.coordinate_rotation(ee.obj.pos[0] - self.obj.pos[0],
                                                   ee.obj.pos[1] - self.obj.pos[1])
                    ee.obj.apply_force(vector.Vector(r, kb * 120000 / ee.obj.MASS))
                    self.DMG_RATE *= self.DECAY_RATE
                ee.hp_sys.enable_immume(self.ENABLE_IMMUNE)
                self.damage_particle()
                self.tar = ee
                self.ap = self.obj.pos - ee.obj.pos
                self.DURATION = 500
                break

class Insights(projectiles.Projectiles.PlatinumWand):
    DAMAGE_AS = 'insights'
    IMG = 'items_null'
    DMG_RATE = .2
    COL = (0, 255, 255)
    DMG_TYPE = damages.DamageTypes.PHYSICAL
    ENABLE_IMMUNE = 0
    DURATION = 1000
    LIMIT_VEL = -100
    DEL = True


    def __init__(self, *args):
        super().__init__(*args)
        self.obj = projectiles.WeakProjectileMotion(self.obj.pos, 0)
        self.obj.MASS = 10
        self.obj.FRICTION = 1.01
        self.obj.velocity.clear()
        self.obj.force.clear()

    def update(self):
        super().update()
        tar, _ = self.get_closest_entity()
        if tar is not None:
            self.obj.apply_force(vector.Vector2D(vector.coordinate_rotation(*(tar.obj.pos - self.obj.pos)), 5))
        pg.draw.circle(game.get_game().displayer.canvas, (255, 255, 255), position.displayed_position(self.obj.pos),
                       int(45 / game.get_game().player.get_screen_scale()))
        pg.draw.circle(game.get_game().displayer.canvas, (0, 255, 255), position.displayed_position(self.obj.pos),
                       int(23 / game.get_game().player.get_screen_scale()),
                       int(15 / game.get_game().player.get_screen_scale()))

class Pierce(projectiles.Projectiles.PlatinumWand):
    DAMAGE_AS = 'pierce'
    IMG = 'items_null'
    DMG_RATE = 4
    COL = (0, 255, 255)
    DMG_TYPE = damages.DamageTypes.PIERCING
    ENABLE_IMMUNE = 0
    DURATION = 1000
    LIMIT_VEL = -100
    DEL = True


    def __init__(self, *args):
        super().__init__(*args)
        self.obj = projectiles.WeakProjectileMotion(self.obj.pos, 0)
        self.obj.MASS = 10
        self.obj.FRICTION = 1
        self.obj.velocity.clear()
        self.obj.force.clear()
        self.obj.velocity += vector.Vector2D(self.rot, 100)

    def update(self):
        super().update()
        tar, _ = self.get_closest_entity()
        if tar is not None:
            self.obj.apply_force(vector.Vector2D(vector.coordinate_rotation(*(tar.obj.pos - self.obj.pos)), 5))
        pg.draw.circle(game.get_game().displayer.canvas, (255, 255, 255), position.displayed_position(self.obj.pos),
                       int(45 / game.get_game().player.get_screen_scale()))
        pg.draw.circle(game.get_game().displayer.canvas, (0, 255, 255), position.displayed_position(self.obj.pos),
                       int(23 / game.get_game().player.get_screen_scale()),
                       int(15 / game.get_game().player.get_screen_scale()))
