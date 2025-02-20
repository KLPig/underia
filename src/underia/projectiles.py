import copy
import math
import random
import pygame as pg
import perlin_noise
import functools
from src.physics import mover, vector
from src.resources import position
from src.underia import game, weapons, entity
from src.values import damages, effects, DamageTypes
from src.visual import effects as eff, particle_effects, fade_circle, draw
from src import constants


class ProjectileMotion(mover.Mover):
    MASS = 20
    FRICTION = 0.98
    TOUCHING_DAMAGE = 10

    def __init__(self, pos, rotation=0, spd=0):
        super().__init__(pos)
        self.rotation = rotation
        self.apply_force(vector.Vector(self.rotation, spd * 12))

    def on_update(self):
        self.apply_force(vector.Vector(self.rotation, 20))


class WeakProjectileMotion(ProjectileMotion):
    MASS = 10
    FRICTION = 0.9
    TOUCHING_DAMAGE = 5

    def __init__(self, pos, rotation):
        super().__init__(pos, rotation)
        self.apply_force(vector.Vector(self.rotation, 500))

    def on_update(self):
        pass

@functools.lru_cache(maxsize=None)
def projectile_get_surface(rot, scale, img):
    img = pg.transform.rotate(img, 90 - rot)
    return pg.transform.scale_by(img, 1 / scale)

class Projectiles:
    class Projectile:
        NAME = 'Projectile'

        def get_closest_entity(self) -> tuple[entity.Entities.Entity | None, float]:
            closest_entity = None
            closest_distance = 1000000
            for entity in game.get_game().entities:
                if not entity.obj.IS_OBJECT and not entity.VITAL and not entity.IS_MENACE:
                    continue
                if vector.distance(self.obj.pos[0] - entity.obj.pos[0],
                                   self.obj.pos[1] - entity.obj.pos[1]) - 1000 * entity.IS_MENACE < closest_distance:
                    closest_entity = entity
                    closest_distance = vector.distance(self.obj.pos[0] - entity.obj.pos[0],
                                                       self.obj.pos[1] - entity.obj.pos[1]) - 1000 * entity.IS_MENACE
            if closest_entity is None:
                return None, 0.0
            return closest_entity, vector.coordinate_rotation(closest_entity.obj.pos[0] - self.obj.pos[0],
                                                              closest_entity.obj.pos[1] - self.obj.pos[1])

        def __init__(self, pos, img=None, motion: type(ProjectileMotion) = ProjectileMotion):
            self.obj = motion(pos)
            self.img: pg.Surface | None = img
            self.d_img = self.img
            self.rot = 0
            self.dead = False

        def set_rotation(self, rot):
            if self.img.get_width() < 5:
                return
            p = position.displayed_position(self.obj.pos)
            if p[0] < -50 or p[0] > game.get_game().displayer.SCREEN_WIDTH + 50 or p[1] < -50 or p[
                1] > game.get_game().displayer.SCREEN_HEIGHT + 50:
                return
            self.rot = rot
            self.d_img = projectile_get_surface(rot, game.get_game().player.get_screen_scale(), self.img)

        def rotate(self, angle):
            self.set_rotation((self.rot + angle) % 360)

        def update(self):
            p = position.displayed_position((self.obj.pos[0], self.obj.pos[1]))
            if p[0] < -500 or p[0] > game.get_game().displayer.SCREEN_WIDTH + 500 or p[1] < -500 or p[
                1] > game.get_game().displayer.SCREEN_HEIGHT + 500:
                return
            self.obj.update()
            if p[0] < -50 or p[0] > game.get_game().displayer.SCREEN_WIDTH + 50 or p[1] < -50 or p[
                1] > game.get_game().displayer.SCREEN_HEIGHT + 50:
                return
            self.draw()
            self.set_rotation(self.obj.velocity.get_net_rotation())
            if p[1] > game.get_game().displayer.SCREEN_HEIGHT + 500:
                self.dead = True

        def draw(self):
            displayer = game.get_game().displayer
            imr = self.d_img.get_rect(center=position.displayed_position((self.obj.pos[0], self.obj.pos[1])))
            displayer.canvas.blit(self.d_img, imr)

    class ThiefWeapon(Projectile):
        NAME = 'Thief\'s Projectile'
        IMG = 'items_weapons_copper_knife'
        DAMAGE_AS = 'copper_knife'
        DMG_RANGE = 120
        DEAD_DELETE = True

        def __init__(self, pos, rotation, power):
            super().__init__(pos, game.get_game().graphics[self.IMG], ProjectileMotion)
            self.obj = WeakProjectileMotion(pos, rotation)
            self.obj.apply_force(vector.Vector(rotation, power - 500))
            self.p_calc = power
            self.set_rotation(rotation)

        def update(self):
            super().update()
            self.p_calc *= self.obj.FRICTION
            if self.p_calc < 1:
                self.dead = True
            self.obj.apply_force(vector.Vector(0, -50))
            self.damage()

        def damage(self):
            for entity in game.get_game().entities:
                if vector.distance(entity.obj.pos[0] - self.obj.pos[0], entity.obj.pos[1] - self.obj.pos[1]) < self.DMG_RANGE:
                    entity.hp_sys.damage(weapons.WEAPONS[self.DAMAGE_AS].damages[
                                             damages.DamageTypes.PIERCING] * game.get_game().player.attack *
                                         game.get_game().player.attacks[1], damages.DamageTypes.PIERCING)
                    self.dead = self.dead or self.DEAD_DELETE

    class Dagger(ThiefWeapon):
        IMG = 'items_weapons_dagger'
        DAMAGE_AS = 'dagger'

    class PlatinumDoubleknife(ThiefWeapon):
        IMG = 'items_weapons_platinum_doubleknife'
        DAMAGE_AS = 'platinum_doubleknife'

    class MagicSword(Projectile):
        NAME = 'Magic Sword'

        def __init__(self, pos, rotation):
            self.img = game.get_game().graphics['projectiles_magic_sword']
            self.obj = ProjectileMotion(pos, rotation)
            self.d_img = self.img
            self.rot = rotation
            self.set_rotation(rotation)
            self.tick = 0
            self.dead = False

        def update(self):
            super().update()
            self.tick += 1
            if self.tick > 200:
                self.dead = True
            self.damage()

        def damage(self):
            imr = self.d_img.get_rect(center=self.obj.pos)
            for entity in game.get_game().entities:
                if imr.collidepoint(entity.obj.pos[0], entity.obj.pos[1]) or entity.d_img.get_rect(
                        center=entity.obj.pos).collidepoint(self.obj.pos[0], self.obj.pos[1]):
                    entity.hp_sys.damage(weapons.WEAPONS['magic_sword'].damages[
                                             damages.DamageTypes.PHYSICAL] * 0.8 * game.get_game().player.attack *
                                         game.get_game().player.attacks[0],
                                         damages.DamageTypes.PHYSICAL)
                    self.dead = True
                    break

    class RuneBladeProjectile(MagicSword):
        NAME = 'Rune Blade'
        IMG = 'items_weapons_rune_blade'

        def __init__(self, pos, rotation):
            super().__init__(pos, rotation)
            self.img = game.get_game().graphics[self.IMG]
            self.d_img = self.img
            self.set_rotation(rotation)

        def update(self):
            super().update()
            self.obj.apply_force(vector.Vector(self.rot, 50))

        def damage(self):
            for entity in game.get_game().entities:
                if vector.distance(entity.obj.pos[0] - self.obj.pos[0],
                                   entity.obj.pos[1] - self.obj.pos[1]) < 100 + (entity.img.get_width() + entity.img.get_height()) / 4:
                    entity.hp_sys.damage(weapons.WEAPONS['rune_blade'].damages[damages.DamageTypes.PHYSICAL] * game.get_game().player.attack *
                                         game.get_game().player.attacks[0], damages.DamageTypes.PHYSICAL)
                    self.dead = self.dead

    class Fur(Projectile):
        NAME = 'Fur'

        def __init__(self, pos, rotation):
            self.img = game.get_game().graphics['projectiles_fur']
            self.obj = ProjectileMotion(pos, rotation)
            self.d_img = self.img
            self.rot = rotation
            self.set_rotation(rotation)
            self.tick = 0
            self.dead = False

        def update(self):
            super().update()
            self.tick += 1
            if self.tick > 200:
                self.dead = True
            imr = self.d_img.get_rect(center=self.obj.pos)
            for entity in game.get_game().entities:
                if imr.collidepoint(entity.obj.pos[0], entity.obj.pos[1]) or entity.d_img.get_rect(
                        center=entity.obj.pos).collidepoint(self.obj.pos[0], self.obj.pos[1]):
                    entity.hp_sys.damage(weapons.WEAPONS['fur_spear'].damages[
                                             damages.DamageTypes.PHYSICAL] * 0.08 * game.get_game().player.attack *
                                         game.get_game().player.attacks[0],
                                         damages.DamageTypes.PHYSICAL)
                    self.dead = True
                    break

    class Glow(Projectile):
        NAME = 'Glow'
        COL = (255, 127, 63)
        EFF = True

        def __init__(self, pos, rotation):
            self.obj = WeakProjectileMotion(pos, rotation)
            self.img = game.get_game().graphics['projectiles_glow']
            self.d_img = self.img
            self.rot = rotation
            self.set_rotation(rotation)
            self.dead = False

        def update(self):
            super().update()
            if self.obj.velocity.get_net_value() < 3 and type(self) not in [Projectiles.TalentBook, Projectiles.BurningBook]:
                self.dead = True
            if self.EFF:
                game.get_game().displayer.effect(particle_effects.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                                     3, t=8, r=20 / game.get_game().player.get_screen_scale(), col=self.COL,
                                                                                     sp=10 / game.get_game().player.get_screen_scale(),
                                                 ))
            imr = self.d_img.get_rect(center=self.obj.pos)
            if not game.get_game().displayer.canvas.get_rect().collidepoint(position.displayed_position(self.obj.pos)):
                self.dead = True
            if type(self) is Projectiles.Glow:
                for entity in game.get_game().entities:
                    if imr.collidepoint(entity.obj.pos[0], entity.obj.pos[1]) or entity.d_img.get_rect(
                            center=entity.obj.pos).collidepoint(self.obj.pos[0], self.obj.pos[1]):
                        entity.hp_sys.damage(weapons.WEAPONS['glowing_splint'].damages[
                                                 damages.DamageTypes.MAGICAL] * game.get_game().player.attack *
                                             game.get_game().player.attacks[2],
                                             damages.DamageTypes.MAGICAL)
                        entity.hp_sys.effect(effects.Burning(5, weapons.WEAPONS['glowing_splint'].damages[
                            damages.DamageTypes.MAGICAL] * game.get_game().player.attack * game.get_game().player.attacks[
                                                                 2] // 10 + 1))
                        self.dead = True
                        break

    class BurningBook(Glow):
        NAME = 'Burning Book'
        COL = (255, 63, 0)

        def __init__(self, pos, rotation):
            self.obj = ProjectileMotion(pos, rotation)
            self.img = game.get_game().graphics['projectiles_glow']
            self.d_img = self.img
            self.rot = rotation
            self.set_rotation(rotation)
            self.dead = False
            self.tick = 0

        def update(self):
            _, target_rot = self.get_closest_entity()
            if target_rot - self.rot > 180:
                target_rot -= 360
            if target_rot - self.rot < -180:
                target_rot += 360
            self.obj.velocity.reset()
            self.obj.velocity.vectors[0].value *= math.cos(math.radians(.15 * (target_rot - self.obj.rotation)))
            self.obj.rotation = (self.obj.rotation + .15 * (target_rot - self.obj.rotation))
            self.tick += 1
            super().update()
            if self.tick > 100:
                self.dead = True
            self.damage()

        def damage(self):
            imr = self.d_img.get_rect(center=self.obj.pos)
            for entity in game.get_game().entities:
                if imr.collidepoint(entity.obj.pos[0], entity.obj.pos[1]) or entity.d_img.get_rect(
                        center=entity.obj.pos).collidepoint(self.obj.pos[0], self.obj.pos[1]):
                    entity.hp_sys.damage(weapons.WEAPONS['burning_book'].damages[
                                             damages.DamageTypes.MAGICAL] * game.get_game().player.attack *
                                         game.get_game().player.attacks[2] * 0.5, damages.DamageTypes.MAGICAL,
                                         )
                    entity.hp_sys.effect(effects.Burning(9, weapons.WEAPONS['burning_book'].damages[
                        damages.DamageTypes.MAGICAL] * game.get_game().player.attack * game.get_game().player.attacks[
                                                             2] // 10 + 1))
                    self.dead = True

    class TalentBook(Glow):
        NAME = 'Talent Book'
        IMG = 'projectiles_talent_book'
        DAMAGE_AS = 'talent_book'
        COL = (100, 100, 255)

        def __init__(self, pos, rotation):
            self.obj = ProjectileMotion(pos, rotation)
            self.img = game.get_game().graphics[self.IMG]
            self.d_img = self.img
            self.rot = rotation
            self.set_rotation(rotation)
            self.dead = False
            self.tick = 0

        def update(self):
            _, target_rot = self.get_closest_entity()
            if target_rot - self.rot > 180:
                target_rot -= 360
            if target_rot - self.rot < -180:
                target_rot += 360
            self.obj.velocity.reset()
            self.obj.velocity.vectors[0].value *= math.cos(math.radians(.92 * (target_rot - self.obj.rotation)))
            self.obj.rotation = (self.obj.rotation + .92 * (target_rot - self.obj.rotation))
            self.tick += 1
            super().update()
            if self.tick > 100:
                self.dead = True
            imr = self.d_img.get_rect(center=self.obj.pos)
            for entity in game.get_game().entities:
                if (vector.distance(entity.obj.pos[0] - self.obj.pos[0], entity.obj.pos[1] - self.obj.pos[1]) <
                        50 + (entity.d_img.get_width() + self.d_img.get_height())) / 4:
                    entity.hp_sys.damage(weapons.WEAPONS[self.DAMAGE_AS].damages[
                                             damages.DamageTypes.MAGICAL] * game.get_game().player.attack *
                                         game.get_game().player.attacks[2], damages.DamageTypes.MAGICAL)
                    self.dead = True

    class CopperWand(Glow):
        DAMAGE_AS = 'copper_wand'
        IMG = 'projectiles_copper_wand'
        DMG_TYPE = damages.DamageTypes.MAGICAL
        WT = damages.DamageTypes.MAGICAL
        COL = (220, 210, 200)

        def __init__(self, pos, rotation):
            super().__init__(pos, rotation)
            self.img = game.get_game().graphics[self.IMG]

        def update(self):
            super().update()
            if self.obj.velocity.get_net_value() < 3:
                self.dead = True
            self.damage()

        def damage(self):
            kb = weapons.WEAPONS[self.DAMAGE_AS].knock_back
            imr = self.d_img.get_rect(center=self.obj.pos)
            for entity in game.get_game().entities:
                if (vector.distance(entity.obj.pos[0] - self.obj.pos[0], entity.obj.pos[1] - self.obj.pos[1]) <
                        50 + (entity.d_img.get_width() + self.d_img.get_height())) / 4:
                    at_mt = {damages.DamageTypes.PHYSICAL: 0, damages.DamageTypes.PIERCING: 1,
                             damages.DamageTypes.ARCANE: 2, damages.DamageTypes.MAGICAL: 2}[self.WT]
                    entity.hp_sys.damage(
                        weapons.WEAPONS[self.DAMAGE_AS].damages[self.DMG_TYPE] * game.get_game().player.attack *
                        game.get_game().player.attacks[at_mt], self.DMG_TYPE)
                    self.dead = True
                    if not entity.hp_sys.is_immune:
                        r = vector.coordinate_rotation(entity.obj.pos[0] - self.obj.pos[0],
                                                       entity.obj.pos[1] - self.obj.pos[1])
                        entity.obj.apply_force(vector.Vector(r, kb * 120000 / entity.obj.MASS))
                    break

    class IronWand(CopperWand):
        DAMAGE_AS = 'iron_wand'
        COL = (127, 127, 127)

    class IceShard(CopperWand):
        DAMAGE_AS = 'ice_shard'
        IMG = 'projectiles_ice_shard'
        COL = (200, 200, 255)
        def __init__(self, pos, rotation, no=8):
            super().__init__(pos, rotation)
            self.obj.apply_force(vector.Vector(rotation, random.randint(-100, 100)))
            for i in range(no):
                game.get_game().projectiles.append(Projectiles.IceShard(pos, rotation + random.randint(-12, 12), no=0))

    class PlatinumWand(CopperWand):
        DAMAGE_AS = 'platinum_wand'
        IMG = 'projectiles_platinum_wand'
        SPD = 100
        COL = (200, 200, 255)

        def __init__(self, pos, rotation):
            super().__init__(pos, rotation)
            self.obj = ProjectileMotion(pos, rotation, spd=self.SPD)
            self.obj.apply_force(vector.Vector(rotation, 100))
            self.tick = 0

        def update(self):
            self.tick += 1
            if self.tick > 100:
                self.dead = True
            super().update()

    class ObsidianWand(PlatinumWand):
        DAMAGE_AS = 'obsidian_wand'
        COL = (50, 50, 50)
        SPD = 120

    class FireBall(PlatinumWand):
        SPD = 200
        COL = (255, 100, 0)

    class RockWand(PlatinumWand):
        DAMAGE_AS = 'rock_wand'
        IMG = 'projectiles_rock_wand'
        COL = (255, 200, 150)

    class WindBlade(PlatinumWand):
        DAMAGE_AS = 'blade_wand'
        IMG = 'projectiles_wind_blade'
        WT = damages.DamageTypes.MAGICAL
        SPD = 320
        COL = (200, 200, 255)

    class WaterOfDisability(PlatinumWand):
        DAMAGE_AS = 'water_of_disability'
        IMG = 'items_null'
        WT = damages.DamageTypes.MAGICAL
        SPD = 240
        COL = (200, 200, 255)
        EFF = False

        def update(self):
            super().update()
            ax, ay = vector.rotation_coordinate(self.rot)
            draw.line(game.get_game().displayer.canvas, (200, 200, 255),
                         position.displayed_position(self.obj.pos),
                         position.displayed_position((self.obj.pos[0] + ax * 400, self.obj.pos[1] + ay * 400)),
                         width=int(5 / game.get_game().player.get_screen_scale()))
            self.damage()

        def damage(self):
            imr = self.d_img.get_rect(center=self.obj.pos)
            for entity in game.get_game().entities:
                if imr.collidepoint(entity.obj.pos[0], entity.obj.pos[1]) or entity.d_img.get_rect(
                        center=entity.obj.pos).collidepoint(self.obj.pos[0], self.obj.pos[1]):
                    if 'disa' in dir(entity.hp_sys.defenses):
                        if getattr(entity.hp_sys.defenses, 'disa') < 10:
                            entity.hp_sys.defenses.disa += 1
                            entity.hp_sys.defenses[damages.DamageTypes.MAGICAL] -= 8
                    else:
                        entity.hp_sys.defenses.disa = 1
                        entity.hp_sys.defenses[damages.DamageTypes.MAGICAL] -= 8
                    entity.hp_sys.damage(weapons.WEAPONS['water_of_disability'].damages[
                                             damages.DamageTypes.MAGICAL] * game.get_game().player.attack *
                                         game.get_game().player.attacks[2], damages.DamageTypes.MAGICAL,
                                         )
                    self.dead = True

    class NightsEdge(PlatinumWand):
        DAMAGE_AS = 'nights_edge'
        IMG = 'projectiles_nights_edge'
        WT = damages.DamageTypes.PHYSICAL
        COL = (50, 0, 50)

        def update(self):
            self.WT = damages.DamageTypes.PHYSICAL
            super().update()
            self.tick += 1
            if self.tick > 100:
                self.dead = True
            else:
                self.dead = False

    class ForbiddenCurseEvil(RockWand):
        DAMAGE_AS = 'forbidden_curse__evil'
        IMG = 'projectiles_forbidden_curse__evil'
        DMG_TYPE = damages.DamageTypes.ARCANE
        COL = (50, 0, 50)

        def update(self):
            super().update()
            self.obj.apply_force(vector.Vector(self.obj.velocity.get_net_rotation(), 200))

    class BalletShoes(TalentBook):
        DAMAGE_AS = 'ballet_shoes'
        IMG = 'projectiles_ballet_shoes'
        COL = (0, 0, 255)

    class GoldFine(PlatinumWand):
        DAMAGE_AS = 'gold_fine'
        EFF = False
        SPEED = 800
        ELLIPSE_SIZE = (80, 200)
        ELLIPSE_COLOUR = (255, 255, 200)
        ENABLE_IMMUNE = True

        def __init__(self, pos, rotation):
            super().__init__(pos, rotation)
            self.obj.apply_force(vector.Vector(rotation, self.SPEED))
            img = pg.Surface(self.ELLIPSE_SIZE, pg.SRCALPHA)
            pg.draw.ellipse(img, self.ELLIPSE_COLOUR, pg.Rect((0, 0), self.ELLIPSE_SIZE), width=18)
            self.img = img
            self.set_rotation(rotation)
            self.tick = 0
            self.hit = False

        def update(self):
            self.tick += 1
            if self.tick > 100:
                self.dead = True
            else:
                self.dead = False
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
                        game.get_game().player.hp_sys.effect(gain(3 + game.get_game().player.calculate_data('gain_duration', rate_data=False), 3))
                    game.get_game().player.inspiration += int(weapons.WEAPONS[self.DAMAGE_AS].back_rate *
                                                           weapons.WEAPONS[self.DAMAGE_AS].inspiration_cost)

    class StormHarp(GoldFine):
        DAMAGE_AS = 'storm_harp'
        IMG = 'projectiles_storm_harp'
        ELLIPSE_SIZE = (90, 250)
        ELLIPSE_COLOUR = (100, 130, 255)
        SPEED = 1300

    class AncientFlute(GoldFine):
        DAMAGE_AS = 'ancient_flute'
        IMG = 'projectiles_ancient_flute'
        ELLIPSE_SIZE = (40, 100)
        ELLIPSE_COLOUR = (255, 220, 200)
        SPEED = 1200

    class AppleSmellsGood(GoldFine):
        DAMAGE_AS = 'apple_smells_good'
        IMG = 'projectiles_apple_smells_good'
        ELLIPSE_SIZE = (40, 160)
        ELLIPSE_COLOUR = (255, 150, 150)
        SPEED = 1500

    class HolyStormer(GoldFine):
        DAMAGE_AS = 'holy_stormer'
        IMG = 'projectiles_holy_stormer'
        ELLIPSE_SIZE = (80, 600)
        ELLIPSE_COLOUR = (0, 255, 255)
        SPEED = 1000
        ENABLE_IMMUNE = False

        def __init__(self, pos, _):
            px, py = pos
            super().__init__((px, py + 1000), vector.coordinate_rotation(0, -1))

    class Snare(GoldFine):
        DAMAGE_AS = 'snare'
        IMG = 'projectiles_snare'
        RANGE = 1200

        def __init__(self, pos, rotation):
            super().__init__(pos, rotation)
            self.obj.apply_force(vector.Vector(rotation, self.SPEED))
            self.set_rotation(rotation)
            self.tick = 0
            self.hit = False
            game.get_game().displayer.effect(fade_circle.p_fade_circle(*position.displayed_position(pos), col=(200, 200, 200),
                                                                       sp=self.RANGE / 10, t=10, follow_map=True))

        def update(self):
            self.tick += 1
            if self.tick > 5:
                self.dead = True
            self.damage()

        def damage(self):
            for entity in game.get_game().entities:
                if (vector.distance(entity.obj.pos[0] - self.obj.pos[0], entity.obj.pos[1] - self.obj.pos[1]) <
                        self.RANGE + (entity.d_img.get_width() + self.d_img.get_height()) / 4):
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
                        game.get_game().player.hp_sys.effect(gain(3 + game.get_game().player.calculate_data('gain_duration', rate_data=False), 3))
                    game.get_game().player.inspiration += int(weapons.WEAPONS[self.DAMAGE_AS].back_rate *
                                                           weapons.WEAPONS[self.DAMAGE_AS].inspiration_cost)

    class WatcherBell(Projectile):
        DAMAGE_AS = 'watcher_bell'
        ENABLE_IMMUNE = True

        def __init__(self, pos, rotation):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.rot = rotation
            self.dead = False
            self.tick = 0
            self.obj.FRICTION = 0.95
            self.obj.MASS = 500
            self.ax, self.ay = vector.rotation_coordinate(random.randint(0, 359))
            self.hit = False

        def update(self):
            if self.tick < 6:
                self.obj.pos = (self.obj.pos[0] + 80 * self.ax / (self.tick + 1),
                                self.obj.pos[1] + 80 * self.ay / (self.tick + 1))
            else:
                tar, _ = self.get_closest_entity()
                if tar:
                    self.obj.apply_force(vector.Vector(vector.coordinate_rotation(tar.obj.pos[0] - self.obj.pos[0],
                                                                                   tar.obj.pos[1] - self.obj.pos[1]),
                                                       1200))
            self.obj.update()
            pg.draw.circle(game.get_game().displayer.canvas, (255, 255, 255),
                           position.displayed_position(self.obj.pos), int(20 / game.get_game().player.get_screen_scale()))
            pg.draw.circle(game.get_game().displayer.canvas, (200, 255, 0),
                           position.displayed_position(self.obj.pos), int(20 / game.get_game().player.get_screen_scale()),
                           int(5 / game.get_game().player.get_screen_scale()))
            self.tick += 1
            self.damage()
            if self.tick > 35:
                self.dead = True

        def damage(self):
            for entity in game.get_game().entities:
                if (vector.distance(entity.obj.pos[0] - self.obj.pos[0], entity.obj.pos[1] - self.obj.pos[1]) <
                        120 + (entity.d_img.get_width() + entity.d_img.get_height()) / 4):
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
                    self.dead = True
                    if len(weapons.WEAPONS[self.DAMAGE_AS].gains):
                        gain = random.choice(weapons.WEAPONS[self.DAMAGE_AS].gains)
                        game.get_game().player.hp_sys.effect(gain(3 + game.get_game().player.calculate_data('gain_duration', rate_data=False), 3))
                    game.get_game().player.inspiration += int(weapons.WEAPONS[self.DAMAGE_AS].back_rate *
                                                              weapons.WEAPONS[self.DAMAGE_AS].inspiration_cost)

    class MagicCircle(Projectile):
        DAMAGE_AS = 'magic_circle'
        IMG = 'projectiles_magic_circle'
        ROT_SPEED = 2
        ALPHA = 127
        DURATION = 100
        AUTO_FOLLOW = True
        DMG_TYPE = damages.DamageTypes.MAGICAL

        def __init__(self, pos, rotation):
            self.obj = mover.Mover(pos)
            self.img = game.get_game().graphics[self.IMG]
            if constants.USE_ALPHA:
                self.img = copy.copy(self.img)
                self.img.set_alpha(self.ALPHA)
            self.d_img = self.img
            self.rot = rotation
            self.set_rotation(rotation)
            self.dead = False
            self.tick = 0
            self.ttx = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))

        def update(self):
            mx, my = self.ttx
            if self.AUTO_FOLLOW:
                self.obj.pos = ((mx + self.obj.pos[0]) // 2, (my + self.obj.pos[1]) // 2)
            else:
                self.obj.pos = game.get_game().player.obj.pos
            self.tick += 1
            if self.tick < 5:
                self.img = copy.copy(game.get_game().graphics[self.IMG])
                self.img = pg.transform.scale_by(self.img, self.tick ** 2 / 25)
                if constants.USE_ALPHA:
                    self.img.set_alpha(self.ALPHA * self.tick ** 2 // 25)
                self.d_img = self.img
            elif self.tick > self.DURATION - 5:
                self.img = copy.copy(game.get_game().graphics[self.IMG])
                self.img = pg.transform.scale_by(self.img, (self.DURATION - self.tick) ** 2 / 25)
                if constants.USE_ALPHA:
                    self.img.set_alpha(self.ALPHA * (self.DURATION - self.tick) ** 2 // 25)
                self.d_img = self.img
            else:
                self.img = copy.copy(game.get_game().graphics[self.IMG])
                if constants.USE_ALPHA:
                    self.img.set_alpha(self.ALPHA)
                self.d_img = self.img
            if self.tick > self.DURATION:
                self.dead = True
            displayer = game.get_game().displayer
            self.set_rotation(self.ROT_SPEED * self.tick)
            imr = self.d_img.get_rect(center=position.displayed_position((self.obj.pos[0], self.obj.pos[1])))
            displayer.canvas.blit(self.d_img, imr)
            self.damage()

        def damage(self):
            for entity in game.get_game().entities:
                ex, ey = entity.obj.pos
                if vector.distance(self.obj.pos[0] - ex,
                                   self.obj.pos[1] - ey) < self.d_img.get_width() // 2 + entity.d_img.get_width() // 2:
                    entity.hp_sys.damage(
                        weapons.WEAPONS[self.DAMAGE_AS].damages[self.DMG_TYPE] * game.get_game().player.attack *
                        game.get_game().player.attacks[2], self.DMG_TYPE)

    class CactusWand(MagicCircle):
        DAMAGE_AS = 'cactus_wand'
        IMG = 'projectiles_cactus_wand'
        ROT_SPEED = 0.2
        ALPHA = 255
        DURATION = 200

    class CurseBook(MagicCircle):
        DAMAGE_AS = 'curse_book'
        IMG = 'projectiles_curse_book'

    class LightPurify(MagicCircle):
        DAMAGE_AS = 'light_purify'
        IMG = 'projectiles_light_purify'
        ROT_SPEED = 10
        ALPHA = 80

    class Storm(MagicCircle):
        DAMAGE_AS ='storm'
        IMG = 'projectiles_storm'
        ROT_SPEED = 28
        ALPHA = 127
        DURATION = 120
        AUTO_FOLLOW = True

        def update(self):
            super().update()
            self.obj.FRICTION = 0.5
            self.obj.MASS = 50000000
            for entity in game.get_game().entities:
                entity.obj.object_gravitational(self.obj)
                self.obj.object_gravitational(entity.obj)
            for p in game.get_game().projectiles:
                p.obj.object_gravitational(self.obj)
                self.obj.object_gravitational(p.obj)
            game.get_game().player.obj.object_gravitational(self.obj)
            self.obj.object_gravitational(game.get_game().player.obj)

    class LifeBringer(MagicCircle):
        DAMAGE_AS = 'lifebringer'
        IMG = 'projectiles_lifebringer'
        ROT_SPEED = 20
        ALPHA = 127
        DURATION = 120
        AUTO_FOLLOW = True

        def update(self):
            super().update()
            px, py = game.get_game().player.obj.pos
            if vector.distance(self.obj.pos[0] - px, self.obj.pos[1] - py) < self.img.get_width() // 2:
                game.get_game().player.hp_sys.heal(3)
                game.get_game().player.talent = min(game.get_game().player.talent + 0.25,
                                                    game.get_game().player.max_talent)
                game.get_game().player.mana = min(game.get_game().player.mana + 6, game.get_game().player.max_mana)


        def damage(self):
            pass

    class ForbiddenCurseDarkWield(MagicCircle):
        DAMAGE_AS = 'great_forbidden_curse__dark'
        IMG = 'projectiles_forbidden_curse__darks_wield'
        DURATION = 240
        ALPHA = 150
        ROT_SPEED = 3
        AUTO_FOLLOW = True
        DMG_TYPE = damages.DamageTypes.ARCANE

    class ShieldWand(MagicCircle):
        DAMAGE_AS = 'shield_wand'
        IMG = 'projectiles_shield_wand'
        DURATION = 200
        ROT_SPEED = 5
        AUTO_FOLLOW = False

        def __init__(self, pos, rotation):
            super().__init__(pos, rotation)
            game.get_game().player.hp_sys.effect(effects.Shield(10, 255))

    class ForbiddenCurseSpirit(MagicCircle):
        DAMAGE_AS = 'forbidden_curse__spirit'
        IMG = 'projectiles_forbidden_curse__spirit'
        DURATION = 240
        ALPHA = 80
        ROT_SPEED = 3
        AUTO_FOLLOW = True
        DMG_TYPE = damages.DamageTypes.ARCANE

    class GravityWand(MagicCircle):
        DAMAGE_AS = 'gravity_wand'
        IMG = 'projectiles_gravity_wand'
        DURATION = 40
        ROT_SPEED = 10
        ALPHA = 200
        AUTO_FOLLOW = False

        def __init__(self, pos, rotation):
            super().__init__(pos, rotation)
            game.get_game().player.hp_sys.effect(effects.Gravity(1, 255))

    class JudgementLight(Projectile):
        def __init__(self, pos, rotation):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.img = game.get_game().graphics['projectiles_judgement_light']
            self.d_img = self.img
            self.tx, self.ty = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            self.tick = 0
            self.te = []
            for e in game.get_game().entities:
                ex, ey = e.obj.pos
                if vector.distance(self.tx - ex, self.ty - ey) < 300:
                    self.te.append(e)
            self.tep = [e.obj.pos for e in self.te]

        def update(self):
            self.tick += 1
            for i in range(len(self.te)):
                self.te[i].obj.pos = self.tep[i]
            pg.draw.circle(game.get_game().displayer.canvas, (255, 255, 200),
                           position.displayed_position((self.tx, self.ty)), 300 / game.get_game().player.get_screen_scale(),
                           2)
            if self.tick < 80:
                w = 1
            elif self.tick < 90:
                w = 1 + (self.tick - 80) ** 2 * 6
            elif self.tick < 210:
                w = 600
            elif self.tick < 220:
                w = 601 - (self.tick - 210) ** 2 * 6
            else:
                self.dead = True
                return
            w += int(math.sin(self.tick / 10) * 10)
            sf = pg.Surface((600, 2600), pg.SRCALPHA)
            sf.fill((0, 0, 0, 0))
            draw.line(sf, (255, 255, 200),
                         (300, 300), (300, 2300), width=w)
            pg.draw.circle(sf, (255, 255, 200),
                           (300, 2300), w // 2)
            if constants.USE_ALPHA:
                sf.set_alpha(100)
            sf = pg.transform.scale_by(sf, 1 / game.get_game().player.get_screen_scale())
            sfr = sf.get_rect(midbottom=position.displayed_position((self.tx,
                                                                     self.ty + 500 / game.get_game().player.get_screen_scale())))
            game.get_game().displayer.canvas.blit(sf, sfr)
            for e in game.get_game().entities:
                ex, ey = e.obj.pos
                if vector.distance(self.tx - ex, self.ty - ey) < w // 2:
                    e.hp_sys.damage(weapons.WEAPONS['judgement_light'].damages[damages.DamageTypes.MAGICAL] *
                                     game.get_game().player.attack * game.get_game().player.attacks[2],
                                     damages.DamageTypes.MAGICAL)

    class DarkRestrict(Projectile):
        def __init__(self, pos, rotation):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.tick = 0
            self.img = game.get_game().graphics['entity_null']
            self.d_img = self.img
            self.tx, self.ty = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            self.obj.pos = self.tx, self.ty
            self.te = []
            for e in game.get_game().entities:
                ex, ey = e.obj.pos
                if vector.distance(self.tx - ex, self.ty - ey) < 800:
                    self.te.append(e)
            self.tep = [e.obj.pos for e in self.te]

        def update(self):
            self.tick += 1
            if self.tick < 10:
                w = self.tick ** 2 * 4
            elif self.tick < 70:
                w = 400
            elif self.tick < 80:
                w = 400 - (self.tick - 70) ** 2 * 4
            else:
                self.dead = True
                return
            pg.draw.circle(game.get_game().displayer.canvas, (0, 0, 0),
                           position.displayed_position((self.tx, self.ty)), w, 2)
            for i in range(len(self.te)):
                draw.line(game.get_game().displayer.canvas, (0, 0, 0),
                             position.displayed_position(self.tep[i]),
                             position.displayed_position(self.te[i].obj.pos), 10)
                self.te[i].obj.pos = self.tep[i]


    class Beam(Projectile):
        WIDTH = 120
        LENGTH = 2000
        DAMAGE_AS = 'prism'
        DMG = None
        COLOR = (255, 255, 255)
        DMG_TYPE = damages.DamageTypes.MAGICAL
        DURATION = 30
        FOLLOW_PLAYER = True
        FACE_TO_MOUSE = False

        def __init__(self, pos, rotation):
            ax, ay = vector.rotation_coordinate(rotation)
            self.tar_reg = abs(ax - ay * (-1 if ((ax > 0) != (ay > 0)) else 1))
            self.lf = ax > 0
            self.lr = ay > 0
            self.slope = ax / ay
            self.tick = 0
            self.obj = ProjectileMotion(pos, rotation, 0)
            self.dead = False
            self.start_pos = None
            self.end_pos = None
            self.rot = rotation
            if self.FACE_TO_MOUSE:
                mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
                self.arot = vector.coordinate_rotation(mx - pos[0], my - pos[1]) - rotation
            else:
                self.arot = 0
            self.start_pos = pos[0] + ax * 100, pos[1] + ay * 100
            self.end_pos = self.start_pos[0] + ax * self.LENGTH, self.start_pos[1] + ay * self.LENGTH
            self.pos = pos
            self.pap = None
            self.img = pg.Surface((1, 1))
            self.d_img = self.img

        def update(self):
            mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            if self.FACE_TO_MOUSE:
                self.rot = vector.coordinate_rotation(mx - self.pos[0], my - self.pos[1]) + self.arot
                ax, ay = mx - self.pos[0], my - self.pos[1]
                self.tar_reg = abs(ax - ay * (-1 if ((ax > 0) != (ay > 0)) else 1))
                self.lf = ax > 0
                self.lr = ay > 0
                self.slope = ax / ay
            if self.pap is None:
                self.pap = self.pos[0] - game.get_game().player.obj.pos[0], self.pos[1] - game.get_game().player.obj.pos[1]
            ax, ay = vector.rotation_coordinate(self.rot)
            self.tar_reg = abs(ax - ay * (-1 if ((ax > 0) != (ay > 0)) else 1))
            self.lf = ax > 0
            self.lr = ay > 0
            self.slope = ax / ay
            if self.FOLLOW_PLAYER:
                self.pos = game.get_game().player.obj.pos[0] + self.pap[0], game.get_game().player.obj.pos[1] + self.pap[1]
            self.obj.pos = self.pos
            self.start_pos = self.pos[0] + ax * 50 + self.WIDTH / 2 * ax, self.pos[1] + ay * 50 + self.WIDTH / 2 * ay
            self.end_pos = self.start_pos[0] + ax * self.LENGTH, self.start_pos[1] + ay * self.LENGTH
            for entity in game.get_game().entities:
                ex = entity.obj.pos[0] - game.get_game().player.obj.pos[0]
                ey = entity.obj.pos[1] - game.get_game().player.obj.pos[1]
                if (abs(self.slope * ey - ex) * math.sin(math.atan(abs(1 / (self.slope + 10 ** -10)))) <
                        self.WIDTH + (entity.d_img.get_width() + entity.d_img.get_height()) // 2 and
                        ((ex > 0) == self.lf) and ((ey > 0) == self.lr) and vector.distance(ey, ex) < self.LENGTH):
                    entity.hp_sys.damage((weapons.WEAPONS[self.DAMAGE_AS].damages[self.DMG_TYPE] if self.DMG is None
                                          else self.DMG) * \
                                         game.get_game().player.attack * game.get_game().player.attacks[{DamageTypes.PHYSICAL: 0,
                                                                                                         DamageTypes.PIERCING: 1,
                                                                                                         DamageTypes.MAGICAL: 2,
                                                                                                         DamageTypes.ARCANE: 2}[self.DMG_TYPE]],
                                         self.DMG_TYPE)
            if self.tick > self.DURATION:
                self.dead = True
            self.tick += 1
            size = min(self.WIDTH, int(self.tick ** 3) if self.tick < self.DURATION // 2 else \
                min(self.WIDTH, int((self.DURATION - self.tick) ** 3)))
            size = int(size / game.get_game().player.get_screen_scale())
            pg.draw.circle(game.get_game().displayer.canvas, self.COLOR, position.displayed_position(self.start_pos),
                           size // 2)
            draw.line(game.get_game().displayer.canvas, self.COLOR, position.displayed_position(self.start_pos),
                         position.displayed_position(self.end_pos), size)

    class ForwardBow(Beam):
        WIDTH = 10
        LENGTH = 3200
        DAMAGE_AS = 'forward_bow'
        COLOR = (180, 150, 255)
        DURATION = 8
        DMG_TYPE = damages.DamageTypes.PIERCING
        FACE_TO_MOUSE = True

    class ForwardBowHuge(ForwardBow):
        WIDTH = 60
        DURATION = 12

    class LazerRain(Beam):
        WIDTH = 5
        LENGTH = 2200
        DAMAGE_AS = 'lazer_rain'
        COLOR = (200, 200, 255)
        DURATION = 15
        DMG_TYPE = damages.DamageTypes.PIERCING

    class BladeBeam(Beam):
        WIDTH = 100
        LENGTH = 3200
        DAMAGE_AS = 'the_blade'
        COLOR = (0, 150, 50)
        DURATION = 12
        DMG_TYPE = damages.DamageTypes.PHYSICAL

    class BladeBeamSmall(BladeBeam):
        WIDTH = 30
        LENGTH = 3200
        DAMAGE_AS = 'the_blade'
        COLOR = (127, 255, 127)
        DURATION = 10
        DMG_TYPE = damages.DamageTypes.PHYSICAL

    class WatcherWand(Beam):
        WIDTH = 10
        LENGTH = 200
        DAMAGE_AS = 'watcher_wand'
        COLOR = (255, 0, 0)
        DURATION = 10

    class LifeWoodenSword(Beam):
        WIDTH = 30
        LENGTH = 150
        DAMAGE_AS = 'life_wooden_sword'
        COLOR = (0, 80, 0)
        DURATION = 5
        DMG_TYPE = damages.DamageTypes.PHYSICAL

    class LifeWoodenWand(Beam):
        WIDTH = 20
        LENGTH = 1000
        DAMAGE_AS = 'life_wooden_wand'
        COLOR = (0, 80, 0)
        DURATION = 15

    class BloodSacrifice(Beam):
        WIDTH = 40
        LENGTH = 1000
        DAMAGE_AS = 'blood_sacrifice'
        COLOR = (255, 0, 0)
        DURATION = 28

    class RedBeam(Beam):
        WIDTH = 40
        LENGTH = 1800
        DAMAGE_AS = 'double_watcher_wand'
        COLOR = (255, 100, 100)
        DURATION = 20

    class GreenBeam(Beam):
        WIDTH = 30
        LENGTH = 2400
        DAMAGE_AS = 'double_watcher_wand'
        COLOR = (100, 255, 100)
        DURATION = 20

    class TurningPoint(Beam):
        WIDTH = 150
        LENGTH = 5000
        DAMAGE_AS = 'turning_point'
        DMG_TYPE = damages.DamageTypes.PHYSICAL
        COLOR = (255, 0, 0)
        DURATION = 18
        FOLLOW_PLAYER = False

    class BeamPair(Projectile):
        def __init__(self, pos, rotation):
            super().__init__(pos, rotation, motion=mover.Mover)
            mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            r = Projectiles.RedBeam((pos[0] + random.randint(-300, 300), pos[1] + random.randint(-300, 300)),
                                    rotation)
            r.rot = vector.coordinate_rotation(mx - r.pos[0], my - r.pos[1])
            g = Projectiles.GreenBeam((pos[0] + random.randint(-300, 300), pos[1] + random.randint(-300, 300)),
                                      rotation)
            g.rot = vector.coordinate_rotation(mx - g.pos[0], my - g.pos[1])
            if random.randint(0, 1):
                game.get_game().projectiles.append(r)
                game.get_game().projectiles.append(g)
            else:
                game.get_game().projectiles.append(g)
                game.get_game().projectiles.append(r)
            self.dead = True

        def update(self):
            pass

    class Meteor(Projectile):
        DAMAGE_AS = 'skyfire__meteor'
        IMG = 'projectiles_meteor'
        DMG_TYPE = damages.DamageTypes.MAGICAL

        def __init__(self, pos, rotation):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.img = game.get_game().graphics[self.IMG]
            self.d_img = self.img
            self.rot = rotation
            self.dead = False
            self.tick = 0
            self.set_rotation(rotation)
            self.ps = [pos]
            self.tpx, self.tpy = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            self.tpx += random.randint(-100, 100)
            self.tpy += random.randint(-100, 100)

        def update(self):
            self.tick += 1
            self.obj.pos = self.tpx, self.tpy - 4500 + 5 * self.tick ** 2
            self.ps.append(self.obj.pos)
            if len(self.ps) > 5:
                self.ps.pop(0)
            super().update()
            # eff.pointed_curve((255, 100, 150), self.ps, 50, 127)
            pg.draw.circle(game.get_game().displayer.canvas, (255, 0, 0), position.displayed_position((self.tpx, self.tpy)),
                           radius=600 // game.get_game().player.get_screen_scale(), width=2)
            if self.tick >= 30:
                for e in game.get_game().entities:
                    if vector.distance(self.obj.pos[0] - e.obj.pos[0], self.obj.pos[1] - e.obj.pos[1]) < 600:
                        e.hp_sys.damage(
                            weapons.WEAPONS[self.DAMAGE_AS].damages[self.DMG_TYPE] * game.get_game().player.attack *
                            game.get_game().player.attacks[{DamageTypes.PHYSICAL: 0,
                                                             DamageTypes.PIERCING: 1,
                                                             DamageTypes.MAGICAL: 2,
                                                             DamageTypes.ARCANE: 2}[self.DMG_TYPE]], self.DMG_TYPE)
                self.dead = True
                game.get_game().displayer.effect(particle_effects.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                                     r=40, t=15, sp=30, n=30))


    class Starfury(Projectile):
        DMG_AS = 'starfury'
        O_DST = 20
        N_DST = 80

        def __init__(self, pos, rotation):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.img = game.get_game().graphics['projectiles_starfury']
            self.tx, self.ty = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            self.tx += pos[0]
            self.ty += pos[1]
            dx = random.randint(-100, 100)
            dy = -1000
            self.obj.pos = (self.tx + dx, self.ty + dy)
            self.ax = -dx / 8
            self.ay = -dy / 8
            self.rot = rotation
            self.dead = False
            self.tick = 0
            self.set_rotation(rotation)

        def update(self):
            super().update()
            self.set_rotation(self.rot + 45)
            self.obj.pos = (self.obj.pos[0] + self.ax, self.obj.pos[1] + self.ay)
            pg.draw.circle(game.get_game().displayer.canvas, (255, 255, 0), position.displayed_position((self.tx, self.ty)),
                           (self.O_DST + self.N_DST) // game.get_game().player.get_screen_scale(), 2)
            if self.tick > 8:
                self.dead = True
            self.tick += 1
            for e in game.get_game().entities:
                if vector.distance(self.obj.pos[0] - e.obj.pos[0], self.obj.pos[1] - e.obj.pos[1]) < self.O_DST + (self.tick >= 6) * self.N_DST:
                    e.hp_sys.damage(weapons.WEAPONS[self.DMG_AS].damages[damages.DamageTypes.PHYSICAL] *\
                                     game.get_game().player.attack * game.get_game().player.attacks[0], damages.DamageTypes.PHYSICAL)

    class StarWrath(Starfury):
        DMG_AS = 'star_wrath'
        O_DST = 50
        N_DST = 250

    class BeamLight(Beam):
        WIDTH = 100
        LENGTH = 1500
        DAMAGE_AS = 'prism_wand'
        COLOR = (200, 255, 200)
        DURATION = 20

    class LightsBeam(Beam):
        WIDTH = 30
        LENGTH = 1500
        DAMAGE_AS = 'lights_bible'
        COLOR = (255, 220, 180)
        DURATION = 15

    class LifeDevourer(Beam):
        WIDTH = 16
        LENGTH = 2000
        DAMAGE_AS = 'life_devourer'
        COLOR = (0, 80, 0)
        DURATION = 10
        FOLLOW_PLAYER = False

    class Excalibur(NightsEdge):
        DAMAGE_AS = 'excalibur'
        IMG = 'projectiles_excalibur'
        WT = damages.DamageTypes.PHYSICAL
        COL = (255, 255, 200)

    class Apple(NightsEdge):
        DAMAGE_AS = 'doctor_expeller'
        IMG = 'projectiles_apple'
        WT = damages.DamageTypes.PHYSICAL
        COL = (255, 200, 200)

    class TrueExcalibur(Excalibur):
        DAMAGE_AS = 'true_excalibur'

    class TrueNightsEdge(NightsEdge):
        DAMAGE_AS = 'true_nights_edge'
        IMG = 'projectiles_nights_edge'

        def update(self):
            super().update()
            self.tick += 1
            if self.tick > 100:
                self.dead = True
            else:
                self.dead = False
            self.img = pg.transform.scale_by(game.get_game().graphics['projectiles_nights_edge'],
                                             min(4.0, 0.3 * 1.15 ** self.tick))

    class BloodWand(PlatinumWand):
        DAMAGE_AS = 'blood_wand'
        IMG = 'projectiles_blood_wand'

    class MidnightsWand(BloodWand):
        DAMAGE_AS = 'midnights_wand'
        IMG = 'projectiles_midnights_wand'

    class SpiritualDestroyer(BloodWand):
        DAMAGE_AS = 'spiritual_destroyer'
        IMG = 'projectiles_spiritual_destroyer'

    class EvilBook(BloodWand):
        DAMAGE_AS = 'evil_book'
        IMG = 'projectiles_evil_book'

    class FallingApple(Projectile):
        def __init__(self, pos, rotation, no=3):
            if no:
                game.get_game().projectiles.append(Projectiles.FallingApple(pos, rotation, no - 1))
            super().__init__((pos[0] + random.randint(-500, 500), pos[1] + random.randint(-500, 500) - 1000), rotation, motion=mover.Mover)
            self.img = game.get_game().graphics['projectiles_apple']
            self.d_img = self.img
            self.obj.MASS = 1000
            self.rot = rotation
            self.dead = False
            self.tick = 0
            self.set_rotation(rotation)

        def update(self):
            super().update()
            self.set_rotation(self.rot + 23)
            self.obj.apply_force(vector.Vector(vector.coordinate_rotation(0, 1), 9810))
            if self.tick > 20:
                self.dead = True
            self.tick += 1
            self.damage()

        def damage(self):
            for e in game.get_game().entities:
                if vector.distance(self.obj.pos[0] - e.obj.pos[0], self.obj.pos[1] - e.obj.pos[1]) < 100:
                    e.hp_sys.damage(weapons.WEAPONS['fruit_wand'].damages[damages.DamageTypes.MAGICAL] *\
                                     game.get_game().player.attack * game.get_game().player.attacks[0], damages.DamageTypes.MAGICAL)

    class Seraph(Projectile):
        def __init__(self, pos, rotation):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.img = copy.copy(game.get_game().graphics['projectiles_seraph'])
            self.d_img = self.img
            self.rot = rotation
            self.dead = False
            self.tick = 0
            self.set_rotation(0)

        def update(self):
            px, py = game.get_game().player.obj.pos
            self.obj.pos = (px, py - 1000)
            self.tick += 1
            pg.draw.circle(game.get_game().displayer.canvas, (255, 0, 0), position.displayed_position(self.obj.pos),
                           radius=2000 // game.get_game().player.get_screen_scale(), width=12)
            if self.tick < 10 and constants.USE_ALPHA:
                self.img.set_alpha(self.tick * 10)
            elif self.tick < 90:
                if self.tick % 8 == 0:
                    game.get_game().displayer.effect(particle_effects.p_particle_effects(*position.displayed_position(self.obj.pos),
                                                                                         n=120, r=10, t=50, sp=40))
                    for e in game.get_game().entities:
                        if vector.distance(self.obj.pos[0] - e.obj.pos[0], self.obj.pos[1] - e.obj.pos[1]) < 2000:
                            e.hp_sys.damage(
                                weapons.WEAPONS['great_forbidden_curse__fire'].damages[damages.DamageTypes.ARCANE] * game.get_game().player.attack *
                                game.get_game().player.attacks[2], damages.DamageTypes.ARCANE)
            elif self.tick < 100:
                if constants.USE_ALPHA:
                    self.img.set_alpha(100 - (self.tick - 90) * 10)
            else:
                self.dead = True
            super().update()

    class ForbiddenCurseBloodMoon(Projectile):
        def __init__(self, pos, rotation):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.img = game.get_game().graphics['projectiles_forbidden_curse__blood_moon']
            self.d_img = self.img
            self.rot = rotation
            self.dead = False
            self.tick = 0
            self.set_rotation(0)

        def update(self):
            x = game.get_game().player.obj.pos[0]
            x /= 400
            x += game.get_game().displayer.canvas.get_width() // 2
            x = max(0, min(game.get_game().displayer.canvas.get_width(), x))
            y = game.get_game().player.obj.pos[1]
            y /= 1200
            y = max(-100, min(100, y))
            pg.draw.circle(game.get_game().displayer.canvas, (255, 0, 0), (x, y + 100),
                           200 / math.sqrt(game.get_game().player.get_screen_scale()))
            if self.tick > 500:
                self.dead = True
            self.tick += 1
            if self.tick % 10 == 0:
                for e in game.get_game().entities:
                    e.hp_sys.damage(weapons.WEAPONS['great_forbidden_curse__evil'].damages[damages.DamageTypes.ARCANE] *\
                                     game.get_game().player.attack * game.get_game().player.attacks[2], damages.DamageTypes.ARCANE)
                    if random.randint(0, 1000) == 37 and not e.IS_MENACE:
                        e.hp_sys.hp = 0

    class DeathNote(Projectile):
        def __init__(self, pos, rotation):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.img = game.get_game().graphics['projectiles_death_note']
            self.d_img = self.img
            self.rot = rotation
            self.dead = True
            self.get_closest_entity()[0].hp_sys.damage(weapons.WEAPONS['death_note'].damages[damages.DamageTypes.ARCANE] *\
                                                         game.get_game().player.attack * game.get_game().player.attacks[2],
                                                         damages.DamageTypes.ARCANE)

    class FallingAction(Projectile):
        def __init__(self, pos, rotation):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.img = game.get_game().graphics['projectiles_death_note']
            self.d_img = self.img
            self.rot = rotation
            self.dead = True
            self.get_closest_entity()[0].hp_sys.damage(weapons.WEAPONS['falling_action'].damages[damages.DamageTypes.MAGICAL] *\
                                                         game.get_game().player.attack * game.get_game().player.attacks[2],
                                                         damages.DamageTypes.MAGICAL)
            self.get_closest_entity()[0].hp_sys.damage(
                weapons.WEAPONS['falling_action'].damages[damages.DamageTypes.THINKING] * \
                game.get_game().player.attack * game.get_game().player.attacks[2],
                damages.DamageTypes.THINKING)

    class SunPearl(Projectile):
        def __init__(self, pos, rotation, no=2):
            if no:
                game.get_game().projectiles.append(Projectiles.SunPearl(pos, rotation, no - 1))
            super().__init__(pos, rotation, motion=mover.Mover)
            self.img = game.get_game().graphics['projectiles_sun_pearl']
            self.d_img = self.img
            self.rot = rotation
            self.dead = False
            self.obj.MASS = 1000
            self.obj.FRICTION = 0.9
            self.dt = 0
            self.rt = 240 - no * 120
            self.poss = [pos]
            self.tick = 0
            self.op = game.get_game().player.obj.pos

        def update(self):
            self.op = game.get_game().player.obj.pos
            if self.tick < 10:
                mx, my = position.relative_position(
                    position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
                tdt = vector.distance(mx, my) * game.get_game().player.get_screen_scale()
                self.rt += 24
                self.dt = (100 - (10 - self.tick) ** 2) * tdt / 100
            elif self.tick < 140:
                mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
                tdt = vector.distance(mx, my) * game.get_game().player.get_screen_scale() * (1 + 0.2 * math.sin(self.tick / 2))
                self.dt = tdt
                self.rt += 8
            else:
                self.dt += (self.tick - 140) * 20
                self.rt += 8
            ax, ay = vector.rotation_coordinate(self.rt)
            self.obj.pos = (self.op[0] + ax * self.dt, self.op[1] + ay * self.dt)
            self.poss.append(self.obj.pos)
            if len(self.poss) > 8:
                self.poss.pop(0)
            for i in range(len(self.poss) - 1):
                draw.line(game.get_game().displayer.canvas, (255, 0, 0), position.displayed_position(self.poss[i]),
                             position.displayed_position(self.poss[i + 1]),
                             int((i * 9 + 6) / game.get_game().player.get_screen_scale()))
            pg.draw.circle(game.get_game().displayer.canvas, (255, 0, 0), position.displayed_position(self.obj.pos),
                           int(30 / game.get_game().player.get_screen_scale()))
            pg.draw.circle(game.get_game().displayer.canvas, (255, 200, 0), position.displayed_position(self.obj.pos),
                           int(30 / game.get_game().player.get_screen_scale()),
                           int(8 / game.get_game().player.get_screen_scale()))
            if self.tick > 150:
                self.dead = True
            self.tick += 1
            self.damage()

        def damage(self):
            for e in game.get_game().entities:
                if vector.distance(self.obj.pos[0] - e.obj.pos[0], self.obj.pos[1] - e.obj.pos[1]) < 100 + (e.d_img.get_height() + e.d_img.get_width()) // 4:
                    e.hp_sys.damage(weapons.WEAPONS['sun_pearl'].damages[damages.DamageTypes.MAGICAL] *\
                                     game.get_game().player.attack * game.get_game().player.attacks[2], damages.DamageTypes.MAGICAL)

    class AcidRainDroplet(Projectile):
        def __init__(self, pos, rotation):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.img = game.get_game().graphics['projectiles_acid_rain']
            self.d_img = self.img
            self.rot = rotation
            self.dead = False
            sw = game.get_game().displayer.SCREEN_WIDTH
            sh = game.get_game().displayer.SCREEN_HEIGHT
            self.obj.pos = (pos[0] + random.randint(-sw, sw), pos[1] + random.randint(-sh, sh) - 1800)
            self.tick = 0

        def update(self):
            draw.line(game.get_game().displayer.canvas, (127, 255, 0),
                         position.displayed_position(self.obj.pos),
                         position.displayed_position((self.obj.pos[0], self.obj.pos[1] + 240)),
                         int(5 / game.get_game().player.get_screen_scale()))
            self.obj.pos = (self.obj.pos[0], self.obj.pos[1] + 150)
            self.tick += 1
            if self.tick > 12:
                self.dead = True
            self.damage()

        def damage(self):
            for e in game.get_game().entities:
                if vector.distance(self.obj.pos[0] - e.obj.pos[0], self.obj.pos[1] - e.obj.pos[1]) < 100:
                    e.hp_sys.damage(weapons.WEAPONS['great_forbidden_curse__water'].damages[damages.DamageTypes.ARCANE] *\
                                     game.get_game().player.attack * game.get_game().player.attacks[2], damages.DamageTypes.ARCANE)

    class AcidRain(Projectile):
        def __init__(self, pos, rotation):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.img = game.get_game().graphics['projectiles_acid_rain']
            self.d_img = self.img
            self.rot = rotation
            self.dead = False
            self.poss = [pos]
            self.tick = 0

        def update(self):
            self.poss.append(self.obj.pos)
            if len(self.poss) > 8:
                self.poss.pop(0)
            for i in range(len(self.poss) - 1):
                draw.line(game.get_game().displayer.canvas, (127, 255, 0), position.displayed_position(self.poss[i]),
                             position.displayed_position(self.poss[i + 1]),
                             int((i * 9 + 6) / game.get_game().player.get_screen_scale()))
            pg.draw.circle(game.get_game().displayer.canvas, (127, 255, 0), position.displayed_position(self.obj.pos),
                           int(30 / game.get_game().player.get_screen_scale()))
            pg.draw.circle(game.get_game().displayer.canvas, (255, 255, 255), position.displayed_position(self.obj.pos),
                           int(30 / game.get_game().player.get_screen_scale()),
                           int(8 / game.get_game().player.get_screen_scale()))
            if self.tick > 40:
                for _ in range(180):
                    game.get_game().projectiles.append(Projectiles.AcidRainDroplet(game.get_game().player.obj.pos,
                                                                                   self.rot))
                self.dead = True
            self.tick += 1
            self.obj.pos = (self.obj.pos[0], self.obj.pos[1] - self.tick * 5)

    class RisingAction(Projectile):
        def __init__(self, pos, rotation, no_left=5):
            if no_left:
                game.get_game().projectiles.append(Projectiles.RisingAction(pos, rotation, no_left - 1))
            super().__init__(pos, rotation, motion=mover.Mover)
            self.img = game.get_game().graphics['projectiles_rising_action']
            self.d_img = self.img
            self.rot = rotation
            self.dead = False
            self.obj.MASS = 20
            self.obj.FRICTION = 1
            self.obj.apply_force(vector.Vector(random.randint(50, 130) * random.choice([-1, 1]), 2000))
            self.poss = [pos]
            cols = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255), (255, 0, 0)]
            self.cols = []
            for i in range(1, 8):
                s_c = cols[i - 1]
                e_c = cols[i]
                for j in range(1, 11):
                    self.cols.append((s_c[0] + (e_c[0] - s_c[0]) * j / 10, s_c[1] + (e_c[1] - s_c[1]) * j / 10, s_c[2] + (e_c[2] - s_c[2]) * j / 10))
            self.cnt = 0
            self.tick = 0
            self.ax, self.ay = vector.rotation_coordinate(random.randint(0, 359))

        def update(self):
            tar = self.get_closest_entity()[0]
            mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            if self.tick > 10:
                self.obj.apply_force(vector.Vector(vector.coordinate_rotation(mx - self.obj.pos[0], my - self.obj.pos[1]),
                                                   1000))
                super().update()
            else:
                self.obj.pos = (self.obj.pos[0] + self.ax * 120 / (self.tick + 1),
                                self.obj.pos[1] + self.ay * 120 / (self.tick + 1))
            self.poss.append(self.obj.pos)
            if len(self.poss) > 8:
                self.poss.pop(0)
            self.cols.append(self.cols.pop(0))
            for i in range(len(self.poss) - 1):
                draw.line(game.get_game().displayer.canvas, self.cols[i], position.displayed_position(self.poss[i]),
                             position.displayed_position(self.poss[i + 1]),
                             int((i * 6 + 4) / game.get_game().player.get_screen_scale()))
            pg.draw.circle(game.get_game().displayer.canvas, (255, 255, 255), position.displayed_position(self.obj.pos),
                           int(20 / game.get_game().player.get_screen_scale()))
            pg.draw.circle(game.get_game().displayer.canvas, self.cols[0], position.displayed_position(self.obj.pos),
                           int(20 / game.get_game().player.get_screen_scale()),
                           int(5 / game.get_game().player.get_screen_scale()))
            if vector.distance(self.obj.pos[0] - tar.obj.pos[0], self.obj.pos[1] - tar.obj.pos[1]) < 540 + (tar.d_img.get_height() + tar.d_img.get_width()) / 4:
                tar.hp_sys.damage(weapons.WEAPONS['rising_action'].damages[damages.DamageTypes.MAGICAL] *\
                                  game.get_game().player.attack * game.get_game().player.attacks[2], damages.DamageTypes.MAGICAL)
                tar.hp_sys.damage(weapons.WEAPONS['rising_action'].damages[damages.DamageTypes.THINKING] *\
                                  game.get_game().player.attack * game.get_game().player.attacks[2], damages.DamageTypes.THINKING)
                self.tick += 30
            self.tick += 1
            if self.tick > 120:
                self.dead = True

    class Stop(Projectile):
        def __init__(self, pos, rotation):
            game.get_game().player.hp_sys.effect(effects.TimeStop(duration=1000000, level=1))
            for i in range(120):
                game.get_game().handle_events()
                game.get_game().player.update()
                for e in game.get_game().entities:
                    e.draw()
                    e.hp_sys.is_immune = 0
                for p in game.get_game().projectiles:
                    p.draw()
                game.get_game().player.ui()
                if constants.USE_ALPHA:
                    game.get_game().displayer.canvas.set_alpha(i * 2 + 15)
                game.get_game().displayer.update()
                pg.display.update()
                game.get_game().clock.update()
            game.get_game().player.hp_sys.effects = \
                [e for e in game.get_game().player.hp_sys.effects if type(e) is not effects.TimeStop]
            super().__init__(pos, rotation, motion=mover.Mover)
            self.img = game.get_game().graphics['projectiles_stop']
            self.d_img = self.img
            self.rot = rotation
            self.dead = True

    class HolyShine(Projectile):
        def __init__(self, pos, rotation):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.rot = rotation
            self.dead = False
            self.tick = 0
            self.obj.FRICTION = 0.95
            self.obj.MASS = 500
            self.ax, self.ay = vector.rotation_coordinate(random.randint(0, 359))

        def update(self):
            if self.tick < 6:
                self.obj.pos = (self.obj.pos[0] + 80 * self.ax / (self.tick + 1),
                                self.obj.pos[1] + 80 * self.ay / (self.tick + 1))
            else:
                tar, _ = self.get_closest_entity()
                if tar:
                    self.obj.apply_force(vector.Vector(vector.coordinate_rotation(tar.obj.pos[0] - self.obj.pos[0],
                                                                                   tar.obj.pos[1] - self.obj.pos[1]),
                                                       1200))
            self.obj.update()
            pg.draw.circle(game.get_game().displayer.canvas, (255, 255, 255),
                           position.displayed_position(self.obj.pos), int(20 / game.get_game().player.get_screen_scale()))
            pg.draw.circle(game.get_game().displayer.canvas, (255, 255, 0),
                           position.displayed_position(self.obj.pos), int(20 / game.get_game().player.get_screen_scale()),
                           int(5 / game.get_game().player.get_screen_scale()))
            self.tick += 1
            self.damage()
            if self.tick > 35:
                self.dead = True

        def damage(self):
            for e in game.get_game().entities:
                if (vector.distance(self.obj.pos[0] - e.obj.pos[0], self.obj.pos[1] - e.obj.pos[1]) <
                        100 + (e.d_img.get_height() + e.d_img.get_width()) // 4):
                    karma = game.get_game().player.good_karma
                    mult = weapons.WEAPONS['the_gods_penalty'].max_mult
                    step = 100
                    if not karma:
                        rate = 1
                    else:
                        rate = (1 + step / karma) ** (karma / step * math.log(mult, math.e))
                    e.hp_sys.damage(weapons.WEAPONS['the_gods_penalty'].damages[damages.DamageTypes.HALLOW] *\
                                     game.get_game().player.attack * game.get_game().player.attacks[4] * rate,
                                    damages.DamageTypes.HALLOW)
                    self.dead = True

    class TheGodsPenalty(Projectile):
        def draw_effect(self, window, x_low, x_high, pos, width=20, col=(255, 255, 200)):
            if min(x_high, pos[0] + 100) <= max(x_low, pos[0] - 100) or width <= 0:
                return
            if abs(pos[1] - window.get_height() / 2) < 150 and width == 20:
                draw.line(window, col, pos, window.get_rect().center, width)
            elif pos[1] > window.get_height() / 2:
                return
            else:
                nx = random.randint(max(x_low, pos[0] - 100), min(x_high, pos[0] + 100))
                ny = pos[1] + random.randint(50, 100)
                draw.line(window, col, pos, (nx, ny), width)
                self.draw_effect(window, x_low, x_high, (nx, ny), width, col)
                for _ in range(2 if random.random() < 0.01 else 1 if random.random() < 0.1 else 0):
                    nx = random.randint(max(x_low, pos[0] - 100), min(x_high, pos[0] + 100))
                    ny = pos[1] + random.randint(50, 100)
                    nw = width - random.randint(6, 12)
                    draw.line(window, col, pos, (nx, ny), nw)
                    self.draw_effect(window, x_low, x_high, (nx, ny), nw, col)


        def __init__(self, pos, rotation):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.rot = rotation
            self.dead = False
            self.tick = 0
            self.obj.pos = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            self.img = pg.Surface((400, 4000), pg.SRCALPHA)
            self.draw_effect(self.img, 0, self.img.get_width(), (self.img.get_width(), 0),
                             20, (255, 255, 200))
            self.img = pg.transform.scale_by(self.img, 2.5 / game.get_game().player.get_screen_scale())

        def update(self):
            self.set_rotation(90)
            super().update()
            self.tick += 1
            self.damage()

        def damage(self):
            if self.tick > 10:
                self.dead = True
            for e in game.get_game().entities:
                if vector.distance(self.obj.pos[0] - e.obj.pos[0], self.obj.pos[1] - e.obj.pos[1]) < 200:
                    karma = game.get_game().player.good_karma
                    mult = weapons.WEAPONS['the_gods_penalty'].max_mult
                    step = 100
                    if not karma:
                        rate = 1
                    else:
                        rate = (1 + step / karma) ** (karma / step * math.log(mult, math.e))
                    e.hp_sys.damage(weapons.WEAPONS['the_gods_penalty'].damages[damages.DamageTypes.HALLOW] *\
                                     game.get_game().player.attack * game.get_game().player.attacks[4] * rate,
                                    damages.DamageTypes.HALLOW)

    class TheTrueGodsPenalty(TheGodsPenalty):
        def update(self):
            self.set_rotation(90)
            pg.draw.circle(game.get_game().displayer.canvas, (255, 255, 0),
                           position.displayed_position(self.obj.pos),
                           int(200 / game.get_game().player.get_screen_scale()),
                           int(5 / game.get_game().player.get_screen_scale()))
            if self.tick < 10:
                pass
            elif self.tick < 50 and self.tick % 8 < 3:
                super(Projectiles.TheGodsPenalty, self).update()
                self.damage()
                if self.tick % 8 == 1:
                    self.obj.pos = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            elif self.tick >= 50:
                self.dead = True
            self.tick += 1

        def damage(self):
            for e in game.get_game().entities:
                if vector.distance(self.obj.pos[0] - e.obj.pos[0], self.obj.pos[1] - e.obj.pos[1]) < 200 \
                        and not e.hp_sys.is_immune:
                    karma = game.get_game().player.good_karma
                    mult = weapons.WEAPONS['the_true_gods_penalty'].max_mult
                    step = 80
                    if not karma:
                        rate = 1
                    else:
                        rate = (1 + step / karma) ** (karma / step * math.log(mult, math.e))
                    e.hp_sys.damage(weapons.WEAPONS['the_true_gods_penalty'].damages[damages.DamageTypes.HALLOW] *\
                                     game.get_game().player.attack * game.get_game().player.attacks[4] * rate,
                                    damages.DamageTypes.HALLOW)
                    e.hp_sys.enable_immume()

    class Bones(Projectile):
        pass

    class Arrow(Projectile):
        NAME = 'Arrow'
        SPEED = 6
        DAMAGES = 7
        IMG = 'arrow'
        AIMING = 0
        DELETE = True
        TAIL_SIZE = 0
        TAIL_WIDTH = 3
        TAIL_COLOR = (255, 255, 255)
        SPEED_RATE = 1.0

        def __init__(self, pos, rotation, speed, damage):
            self.obj = ProjectileMotion(pos, rotation, (speed + self.SPEED) * self.SPEED_RATE)
            self.dmg = damage + self.DAMAGES
            self.img = game.get_game().graphics['projectiles_' + self.IMG]
            self.d_img = self.img
            self.rot = rotation
            self.dead = False
            self.tick = 0
            self.set_rotation(rotation)
            self.ps = [pos]

        def update(self):
            if self.TAIL_SIZE:
                self.img = game.get_game().graphics['items_null']
            if self.dead:
                return
            t, target_rot = self.get_closest_entity()
            self.rot %= 360
            target_rot %= 360
            if target_rot - self.rot > 180:
                target_rot -= 360
            if target_rot - self.rot < -180:
                target_rot += 360
            self.obj.velocity.reset()
            if self.AIMING:
                self.obj.velocity.vectors[0].value *= math.cos(
                    math.radians(self.AIMING * (target_rot - self.obj.rotation)))
                self.obj.rotation = (self.obj.rotation + self.AIMING * (target_rot - self.obj.rotation)) % 360
            ox, oy = self.obj.pos
            super().update()
            ax, ay = self.obj.pos
            if ox == ax and oy == ay:
                self.dead = True
                return
            if len(self.ps) > self.TAIL_SIZE:
                self.ps.pop(0)
            self.ps.append((ax, ay))
            if self.TAIL_SIZE:
                eff.pointed_curve(self.TAIL_COLOR, self.ps, self.TAIL_WIDTH, 255)
            self.tick += 1
            if self.tick > 30:
                self.dead = True
            if ox != ax:
                aax = -(ox - ax) / abs(ox - ax) * 120
            else:
                aax = 1
            if oy != ay:
                aay = -(oy - ay) / abs(oy - ay) * 120
            else:
                aay = 1
            cd = []
            for x in range(int(ox), int(ax) + 1, int(aax)):
                for y in range(int(oy), int(ay) + 1, int(aay)):
                    pos = (x, y)
                    cd.extend(self.damage(pos, cd))
                    if self.dead:
                        break
                if self.dead:
                    break

        def damage(self, pos, cd):
            imr = self.d_img.get_rect(center=pos)
            x, y = pos
            for entity in game.get_game().entities:
                if imr.collidepoint(entity.obj.pos[0], entity.obj.pos[1]) or entity.d_img.get_rect(
                        center=entity.obj.pos).collidepoint(x, y) and entity not in cd:
                    entity.hp_sys.damage(
                        self.dmg * game.get_game().player.attack * game.get_game().player.attacks[1],
                        damages.DamageTypes.PIERCING)
                    if self.DELETE:
                        self.dead = True
                    else:
                        cd.append(entity)
            return cd

    class ConiferousLeaf(Arrow):
        DAMAGES = 15
        SPEED = 100
        IMG = 'coniferous_leaf'

    class MagicArrow(Arrow):
        DAMAGES = 18
        SPEED = 5
        IMG = 'magic_arrow'

    class BloodArrow(Arrow):
        DAMAGES = 30
        SPEED = 12
        IMG = 'blood_arrow'
        TAIL_SIZE = 2
        TAIL_WIDTH = 3
        TAIL_COLOR = (255, 0, 0)

    class Bullet(Arrow):
        NAME = 'Bullet'
        DAMAGES = 12
        SPEED = 210
        IMG = 'bullet'
        TAIL_SIZE = 1
        TAIL_WIDTH = 2
        TAIL_COLOR = (127, 127, 127)
        SPEED_RATE = 0.6

    class PlatinumBullet(Bullet):
        DAMAGES = 16
        IMG = 'platinum_bullet'
        TAIL_COLOR = (150, 150, 200)

    class Plasma(Bullet):
        DAMAGES = 35
        SPEED = 120
        IMG = 'plasma'
        TAIL_COLOR = (255, 0, 0)
        TAIL_SIZE = 2

    class Exploder(Bullet):
        DAMAGES = 0
        SPEED = 100
        IMG = 'exploder'

    class SnowBall(Bullet):
        DAMAGES = -20
        SPEED = 500
        IMG ='snow_ball'
        TAIL_SIZE = 5
        TAIL_WIDTH = 2
        TAIL_COLOR = (255, 255, 255)

    class RockBullet(Bullet):
        DAMAGES = 60
        SPEED = 20
        IMG = 'rock_bullet'
        TAIL_COLOR = (255, 200, 127)

    class ShadowBullet(Bullet):
        DAMAGES = 24
        SPEED = 100
        IMG = 'shadow_bullet'
        AIMING = 0.3
        TAIL_COLOR = (50, 0, 50)
        TAIL_SIZE = 3

        def __init__(self, pos, rotation, speed, damage):
            super().__init__(pos, rotation, speed, damage)
            self.poss = [game.get_game().player.obj.pos]

        def update(self):
            self.poss.append(self.obj.pos)
            if len(self.poss) > 5:
                self.poss.pop(0)
            super().update()
            eff.pointed_curve((60, 0, 60), self.poss, 5, 255)

    class Accelerationism(Bullet):
        DAMAGES = 320
        SPEED = 90
        IMG = 'accelerationism'
        TAIL_SIZE = 2
        TAIL_WIDTH = 2
        TAIL_COLOR = (200, 200, 255)

    class ChloroArrow(Bullet):
        DAMAGES = 120
        SPEED = 500
        IMG = 'null'
        TAIL_SIZE = 2
        TAIL_WIDTH = 2
        TAIL_COLOR = (0, 255, 0)

        def __init__(self, pos, rotation, speed, damage):
            super().__init__(pos, rotation, speed, damage)
            self.obj.velocity.clear()
            self.spd = speed + self.SPEED

        def update(self):
            tr = min(self.spd / 1200, .8)
            tar, _ = self.get_closest_entity()
            if tar is None:
                super().update()
                return
            tx, ty = tar.obj.pos
            self.obj.pos = (self.obj.pos[0] + (tx - self.obj.pos[0]) * tr,
                            self.obj.pos[1] + (ty - self.obj.pos[1]) * tr)
            vp = self.obj.pos
            super().update()
            self.obj.pos = vp

    class EnergyArrow(Arrow):
        DAMAGES = 20
        SPEED = 50
        IMG = 'null'
        TAIL_SIZE = 3
        TAIL_WIDTH = 10
        TAIL_COLOR = (0, 255, 255)

        def __init__(self, pos, rotation, speed, damage):
            self.DAMAGES = damage * 5 + self.DAMAGES
            super().__init__(pos, rotation, speed, damage)

        def damage(self, pos, cd):
            imr = self.d_img.get_rect(center=pos)
            x, y = pos
            for ee in game.get_game().entities:
                if imr.collidepoint(ee.obj.pos[0], ee.obj.pos[1]) or ee.d_img.get_rect(
                        center=ee.obj.pos).collidepoint(x, y) and ee not in cd:
                    for e2 in game.get_game().entities:
                        if vector.distance(e2.obj.pos[0] - self.obj.pos[0], e2.obj.pos[1] - self.obj.pos[1]) < 300:
                            e2.hp_sys.damage(self.dmg, damages.DamageTypes.PIERCING)
                    game.get_game().displayer.effect(fade_circle.p_fade_circle(*position.displayed_position(self.obj.pos),
                                                                                (0, 255, 255), t=12, sp=25 / game.get_game().player.get_screen_scale()))
                    if self.DELETE:
                        self.dead = True
                    else:
                        cd.append(ee)
            return cd

    class QuickArrow(Arrow):
        DAMAGES = 40
        SPEED = 200
        DELETE = False
        IMG = 'quick_arrow'
        TAIL_SIZE = 3
        TAIL_WIDTH = 3
        TAIL_COLOR = (0, 0, 255)

    class QuickBullet(Bullet):
        DAMAGES = 80
        SPEED = 500
        DELETE = False
        IMG = 'null'
        TAIL_SIZE = 5
        TAIL_WIDTH = 5
        TAIL_COLOR = (255, 127, 0)

    class SpaceJumper(Bullet):
        DAMAGES = 300
        SPEED = 2000
        IMG = 'null'
        TAIL_SIZE = 2
        TAIL_WIDTH = 8
        TAIL_COLOR = (0, 0, 0)

    class Lysis(Projectile):
        DAMAGE_AS = 'lysis'
        IMG = 'items_weapons_lysis'

        def __init__(self, pos, rotation):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.img = game.get_game().graphics['items_weapons_lysis']
            self.d_img = self.img
            self.rot = rotation
            self.set_rotation(self.rot)
            self.tick = 0
            self.tp = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))

        def update(self):
            self.set_rotation(vector.coordinate_rotation(self.tp[0] - self.obj.pos[0], self.tp[1] - self.obj.pos[1]))
            self.tick += 1
            if self.tick < 10:
                super().update()
                self.obj.pos = (self.obj.pos[0] + (self.tp[0] - self.obj.pos[0]) / 2,
                                self.obj.pos[1] + (self.tp[1] - self.obj.pos[1]) / 2)
                if vector.distance(self.tp[0] - self.obj.pos[0], self.tp[1] - self.obj.pos[1]) < 120:
                    self.tick = 10
                for e in game.get_game().entities:
                    if vector.distance(self.obj.pos[0] - e.obj.pos[0], self.obj.pos[1] - e.obj.pos[1]) < 120:
                        self.tick = 30
            elif self.tick < 40:
                rt = (40 - self.tick) ** 2
                dt = (40 - self.tick) ** 2
                rd = (40 - self.tick) ** 2 / 5 / game.get_game().player.get_screen_scale()
                for ar in range(0, 360, 72):
                    ax, ay = vector.rotation_coordinate(rt + ar)
                    pg.draw.circle(game.get_game().displayer.canvas, (100, 100, 255),
                                   position.displayed_position((self.obj.pos[0] + ax * dt, self.obj.pos[1] + ay * dt)),
                                   rd)
            elif self.tick < 60:
                if self.tick % 8 == 0:
                    game.get_game().displayer.effect(fade_circle.p_fade_circle(*position.displayed_position(self.obj.pos),
                                                                               (0, 0, 255), t=8, sp=100))
                for e in game.get_game().entities:
                    if vector.distance(self.obj.pos[0] - e.obj.pos[0], self.obj.pos[1] - e.obj.pos[1]) < 400:
                        e.hp_sys.damage(
                            weapons.WEAPONS[self.DAMAGE_AS].damages[damages.DamageTypes.PHYSICAL] * game.get_game().player.attack *
                            game.get_game().player.attacks[0], damages.DamageTypes.PHYSICAL)
            else:
                self.dead = True

    class BloodyShortknife(ThiefWeapon):
        DAMAGE_AS = 'bloody_shortknife'
        IMG = 'items_weapons_bloody_shortknife'

    class ObsidianKnife(ThiefWeapon):
        DAMAGE_AS = 'obsidian_knife'
        IMG = 'items_weapons_obsidian_knife'

    class ApplePiece(ThiefWeapon):
        DAMAGE_AS = 'apple_knife'
        IMG = 'projectiles_apple_piece'

    class AppleKnife(ThiefWeapon):
        DAMAGE_AS = 'apple_knife'
        IMG = 'items_weapons_apple_knife'

        def update(self):
            super().update()
            mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            if vector.distance(mx - self.obj.pos[0], my - self.obj.pos[1]) < 200:
                game.get_game().displayer.effect(fade_circle.p_fade_circle(*position.displayed_position(self.obj.pos),
                                                                           (255, 0, 0), t=8, sp=100))
                for _ in range(random.randint(5, 8)):
                    rot = random.randint(0, 360)
                    game.get_game().projectiles.append(Projectiles.ApplePiece(self.obj.pos, rot, self.p_calc * 5))
                self.dead = True

    class StormStabber(ThiefWeapon):
        DAMAGE_AS ='storm_stabber'
        IMG = 'items_weapons_storm_stabber'

    class TwilightShortsword(ThiefWeapon):
        DAMAGE_AS = 'twilight_shortsword'
        IMG = 'items_weapons_twilight_shortsword'

    class DawnShortsword(ThiefWeapon):
        DAMAGE_AS = 'dawn_shortsword'
        IMG = 'items_weapons_dawn_shortsword'

    class NightTwinsword(Projectile):
        def __init__(self, pos, rotation, power):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.img = game.get_game().graphics['items_weapons_twilight_shortsword']
            self.d_img = self.img
            self.rot = rotation
            self.dead = True
            self.tick = 0
            for i in range(-2, 3):
                s = (i % 2 + 2) % 2
                if s:
                    pj = Projectiles.TwilightShortsword(pos, rotation + i * 15, power)
                else:
                    pj = Projectiles.DawnShortsword(pos, rotation + i * 15, power)
                pj.DAMAGE_AS = 'night_twinsword'
                game.get_game().projectiles.append(pj)

    class SpiritualKnife(ThiefWeapon):
        DAMAGE_AS ='spiritual_knife'
        IMG = 'items_weapons_spiritual_knife'

    class DaedalusKnife(ThiefWeapon):
        DAMAGE_AS = 'daedalus_knife'
        IMG = 'items_weapons_daedalus_knife'

    class BloodyShortknife(ThiefWeapon):
        DAMAGE_AS = 'bloody_shortknife'
        IMG = 'items_weapons_bloody_shortknife'

    class Shuriken(ThiefWeapon):
        DAMAGE_AS = 'shuriken'
        IMG = 'items_weapons_shuriken'

    class SpikeBall(ThiefWeapon):
        DAMAGE_AS = 'spike_ball'
        IMG = 'items_weapons_spike_ball'

        def update(self):
            super().update()
            self.obj.apply_force(vector.Vector(0, 50))

    class DaedalusTwinknife(Projectile):
        def __init__(self, pos, rotation, power):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.img = game.get_game().graphics['items_weapons_daedalus_knife']
            self.d_img = self.img
            self.rot = rotation
            self.dead = True
            self.tick = 0
            for i in range(1, 4):
                s = (i % 2 + 2) % 2
                if s:
                    pj = Projectiles.SpiritualKnife(pos, rotation, power * i)
                else:
                    pj = Projectiles.DaedalusKnife(pos, rotation, power * i)
                pj.DAMAGE_AS = 'daedalus_twinknife'
                game.get_game().projectiles.append(pj)

    class Grenade(ThiefWeapon):
        DAMAGE_AS = 'grenade'
        IMG = 'items_weapons_grenade'
        DMG_RANGE = 500
        DEAD_DELETE = False
        COL = (255, 0, 0)
        K = 5

        def __init__(self, pos, rotation, power, k=-1):
            if k == -1 and game.get_game().player.calculate_data('grenade_scat', rate_data=False):
                for _ in range(self.K + random.randint(-2, 2)):
                    game.get_game().projectiles.append(type(self)(pos, rotation + random.randint(-16, 16),
                                                                  power * (.5 + random.random()) / 2, k=0))
            super().__init__(pos, rotation, power)
            self.img = game.get_game().graphics['items_weapons_grenade']
            self.d_img = self.img
            self.t = power // 80
            if game.get_game().player.calculate_data('grenade_scat', rate_data=False):
                self.DMG_RANGE //= 2

        def damage(self):
            if self.t:
                self.t -= 1
            for e in game.get_game().entities:
                if vector.distance(self.obj.pos[0] - e.obj.pos[0], self.obj.pos[1] - e.obj.pos[1]) < 120 or not self.t:
                    game.get_game().displayer.effect(fade_circle.p_fade_circle(*position.displayed_position(self.obj.pos),
                                                                               self.COL, t=10,
                                                                               sp=self.DMG_RANGE / game.get_game().player.get_screen_scale()))
                    for ee in game.get_game().entities:
                        if vector.distance(ee.obj.pos[0] - self.obj.pos[0], ee.obj.pos[1] - self.obj.pos[1]) < \
                            self.DMG_RANGE + (ee.d_img.get_width() + self.d_img.get_width()) / 4:
                            ee.hp_sys.damage(
                                weapons.WEAPONS[self.DAMAGE_AS].damages[damages.DamageTypes.PIERCING] * game.get_game().player.attack *
                                game.get_game().player.attacks[1], damages.DamageTypes.PHYSICAL)
                    self.dead = True
                    return

    class JadeGrenade(Grenade):
        DAMAGE_AS = 'grenade'
        IMG = 'items_weapons_grenade'
        DMG_RANGE = 800
        DEAD_DELETE = False
        COL = (255, 200, 100)
        K = 10

    class TrueTwinblade(ThiefWeapon):
        DAMAGE_AS = 'true_twinblade'
        IMG = 'items_weapons_true_twinblade1'
        DMG_RANGE = 260
        DEAD_DELETE = False

        def __init__(self, pos, rotation, power):
            super().__init__(pos, rotation, power)
            self.t = random.randint(1, 2)
            self.img = game.get_game().graphics[f'items_weapons_true_twinblade_{self.t}']
            self.lrot = rotation
            self.tk = 0
            self.mx, self.my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            self.noises = []

        def update(self):
            super().update()
            self.obj.pos = ((self.obj.pos[0] * 5 + self.mx) / 6, (self.obj.pos[1] * 5 + self.my) / 6)
            if self.tk > 36:
                self.dead = True
            self.p_calc = 1000
            self.set_rotation(int(self.tk ** 1.2 * 32))
            self.tk += 1
            if not len(self.noises):
                noises = perlin_noise.PerlinNoise(octaves=2, seed=random.randint(0, 1000000))
                self.noises = [noises(i / 100) for i in range(1000)]
            mx = max(self.noises)
            mn = min(self.noises)
            self.rot %= 360
            self.lrot %= 360
            if self.rot - self.lrot > 180:
                self.lrot += 360
            if self.lrot - self.rot > 180:
                self.rot += 360
            size = 6
            arot = self.rot - self.lrot
            sz = {3: 32, 4: 40, 6: 64, 8: 80, 10: 100}[size]
            dst = {3: 100, 4: 130, 6: 200, 8: 260, 10: 350}[size]
            gdt = 23
            for j in range(sz):
                i = j / 10
                d = (dst - i * gdt)
                dt = (sz - j) * arot / sz * ((self.noises[j * 999 // sz] - mn) / (mx - mn) * 8 / 5 + .2)
                adt = (sz - j) * arot / sz * ((self.noises[j * 999 // sz] - mn) / (mx - mn) * 2) / 8
                rots = [vector.rotation_coordinate(self.rot - dt * i / 9 + adt) for i in range(9, -1, -1)]
                eff.pointed_curve((127 + int(i * 15), 255 - int(i * 15), 127) if self.t == 1 else \
                                      (int(i * 15), 127, int(i * 30)),
                                  [(vx * d + self.obj.pos[0], vy * d + self.obj.pos[1])
                                   for vx, vy in rots], 3, salpha=int(255 - i * 30))
            self.lrot = self.rot

    class Deconstruction(Projectile):
        def __init__(self, pos, rotation):
            super().__init__(pos, rotation)
            self.obj = WeakProjectileMotion(pos, rotation)
            self.obj.apply_force(vector.Vector(rotation, 2000))
            self.obj.velocity.add(game.get_game().player.obj.velocity.get_net_vector())
            self.obj.IS_OBJECT = False
            self.img = game.get_game().graphics['items_weapons_null']
            self.tick = 0
            self.noises = []
            self.set_rotation(rotation)

        def update(self):
            super().update()
            if not len(self.noises):
                noises = perlin_noise.PerlinNoise(octaves=2, seed=random.randint(0, 1000000))
                self.noises = [noises(i / 100) for i in range(1000)]
            mx = max(self.noises)
            mn = min(self.noises)
            self.tick += 1
            size = 10 - 8 / self.tick
            if self.tick > 20:
                self.dead = True
            sz = int(size * 10)
            dst = size * 33
            gdt = 23
            for j in range(sz):
                i = j / 10
                d = (dst - i * gdt)
                dt = (sz - j) * 120 / sz * ((self.noises[j * 999 // sz] - mn) / (mx - mn) * 8 / 5 + .2)
                rots = [vector.rotation_coordinate(self.rot - dt * i / 9 + dt / 2) for i in range(9, -1, -1)]
                eff.pointed_curve((20 + int(180 * j / sz), int(200 * j / sz), 50 + int(200 * j / sz)),
                                  [(vx * d + self.obj.pos[0], vy * d + self.obj.pos[1])
                                   for vx, vy in rots], 3, salpha=int(255 - i * 30))
            for e in game.get_game().entities:
                if vector.distance(e.obj.pos[0] - self.obj.pos[0],
                                   e.obj.pos[1] - self.obj.pos[1]) < dst:
                    rt = vector.coordinate_rotation(e.obj.pos[0] - self.obj.pos[0],
                                                    e.obj.pos[1] - self.obj.pos[1])
                    rt = (rt % 360 + 360) % 360
                    self.rot = (self.rot % 360 + 360) % 360
                    if abs(rt - self.rot) < 80:
                        e.hp_sys.damage(weapons.WEAPONS['deconstruction'].damages[damages.DamageTypes.PHYSICAL] * \
                                        game.get_game().player.attack * game.get_game().player.attacks[0],
                                        damages.DamageTypes.PHYSICAL)
            self.lrot = self.rot

    class CardBullet(Projectile):
        def __init__(self, pos, rotation, mode, spd, r, f=0):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.obj.MASS = 100
            self.img = game.get_game().graphics[f'entity_{mode}_bomb_bullet']
            self.d_img = self.img
            self.rot = rotation
            self.dead = False
            self.tick = 0
            self.spd = spd
            self.mode = mode
            self.r = r
            self.buls = []
            self.set_rotation(self.rot)
            self.rt = 0
            if self.mode == 'heart' and self.r:
                self.buls = [Projectiles.CardBullet((0, 0), rotation, 'heart', 0, 0) for _ in range(6)]
                for b in self.buls:
                    game.get_game().projectiles.append(b)
                self.img = game.get_game().graphics[f'entity_null']
                self.d_img = game.get_game().graphics[f'entity_null']
            self.obj.apply_force(vector.Vector(self.rot, f))

        def update(self):
            self.set_rotation(self.rot)
            super().draw()
            self.tick += 1
            if self.tick > 300:
                self.dead = True
            self.damage()
            self.obj.apply_force(vector.Vector(self.rot, self.spd * 10))
            self.obj.update()
            if self.r and self.mode == 'heart':
                self.rt += 30
                for i in range(6):
                    rr = self.rt + i * 60
                    ax, ay = vector.rotation_coordinate(rr)
                    self.buls[i].obj.pos = (self.obj.pos[0] + ax * 120, self.obj.pos[1] + ay * 120)

        def damage(self):
            if self.mode == 'heart' and self.r:
                return
            for e in game.get_game().entities:
                if vector.distance(e.obj.pos[0] - self.obj.pos[0],
                                   e.obj.pos[1] - self.obj.pos[1]) < 220:
                    e.hp_sys.damage(weapons.WEAPONS['chaos_chaos'].damages[damages.DamageTypes.PIERCING] * game.get_game().player.attack * game.get_game().player.attacks[1],
                                    damages.DamageTypes.PIERCING)
                    self.dead = True

    class ChaosChaos(Projectile):
        def __init__(self, pos, rotation, power):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.img = game.get_game().graphics['items_weapons_chaos_chaos']
            self.d_img = self.img
            self.rot = rotation
            self.dead = True
            self.tick = 0
            rot = rotation
            r = random.randint(0, 3)
            if not r:
                game.get_game().projectiles.append(Projectiles.CardBullet(self.obj.pos, rot, 'heart', 120, 1, power))
            elif r == 1:
                sr = random.randint(0, 11)
                for i in range(sr, sr + 360, 12):
                    game.get_game().projectiles.append(Projectiles.CardBullet(self.obj.pos, i, 'spade', 200, 1, power))
            elif r == 2:
                for i in range(120, 360, 60):
                    game.get_game().projectiles.append(Projectiles.CardBullet(self.obj.pos, rot, 'diamond', i, 1, power))
            else:
                for i in range(-60, 61, 20):
                    game.get_game().projectiles.append(Projectiles.CardBullet(self.obj.pos, rot + i, 'club', 300, 1, power))

    class TimeFlies(Projectile):
        TIMER = 0
        STEP = 0
        STEP_COLS = ((0, 0, 50), (0, 0, 255), (100, 100, 255), (100, 255, 100), (255, 255, 100),
                     (255, 255, 0), (255, 255, 255))

        def __init__(self, pos, rotation, power):
            super().__init__(pos, rotation, motion=mover.Mover)
            self.img = game.get_game().graphics['items_weapons_null']
            self.d_img = self.img
            self.rot = rotation
            Projectiles.TimeFlies.TIMER = 0
            self.dead = bool(self.STEP)
            if not len([1 for p in game.get_game().projectiles if type(p) is Projectiles.TimeFlies]):
                self.dead = False
            Projectiles.TimeFlies.STEP = min(Projectiles.TimeFlies.STEP + 3, 72)
            self.ar = 0

        def update(self):
            if self.dead:
                return
            Projectiles.TimeFlies.TIMER += 1
            if Projectiles.TimeFlies.TIMER > 10:
                Projectiles.TimeFlies.TIMER = 0
                Projectiles.TimeFlies.STEP -= 1
                if Projectiles.TimeFlies.STEP <= 0:
                    self.dead = True
            self.obj.pos = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            self.ar += 8
            self.ar %= 360
            bs = Projectiles.TimeFlies.STEP // 12
            sz = 160 + Projectiles.TimeFlies.STEP * 20 + bs * 100
            sf = pg.Surface((int(sz / game.get_game().player.get_screen_scale()),
                             int(sz / game.get_game().player.get_screen_scale())),
                            pg.SRCALPHA)
            pg.draw.circle(sf, Projectiles.TimeFlies.STEP_COLS[bs], (sf.get_width() // 2, sf.get_height() // 2),
                           sf.get_width() // 2)
            if constants.USE_ALPHA:
                sf.set_alpha(80 - Projectiles.TimeFlies.TIMER // 5)
            sfr = sf.get_rect(center=position.displayed_position(self.obj.pos))
            game.get_game().displayer.canvas.blit(sf, sfr)
            bz = Projectiles.TimeFlies.STEP % 12
            for i in range(0, 360, 30):
                if bz <= i // 30 and not bs:
                    continue
                im = pg.transform.scale_by(game.get_game().graphics[f'entity_clock{i // 30 + 1}'],
                                           .2 / game.get_game().player.get_screen_scale() * (1 + 2 * (bs + (bz > i // 30))))
                im = pg.transform.scale_by(im, 1 / game.get_game().player.get_screen_scale())
                ax, ay = vector.rotation_coordinate(i + self.ar)
                imr = im.get_rect(center=position.displayed_position((self.obj.pos[0] + ax * sz // 2,
                                                                     self.obj.pos[1] + ay * sz // 2)))
                game.get_game().displayer.canvas.blit(im, imr)
            dmg = weapons.WEAPONS['time_flies'].damages[damages.DamageTypes.PIERCING] * game.get_game().player.attack * \
                  game.get_game().player.attacks[1]
            dmg *= (bs * 12 + bz) ** 1.5 / 300
            for e in game.get_game().entities:
                if vector.distance(e.obj.pos[0] - self.obj.pos[0],
                                   e.obj.pos[1] - self.obj.pos[1]) < sz // 2:
                    e.hp_sys.damage(dmg, damages.DamageTypes.PIERCING)

AMMOS = {
    'arrow': Projectiles.Arrow,
    'coniferous_leaf': Projectiles.ConiferousLeaf,
    'magic_arrow': Projectiles.MagicArrow,
    'blood_arrow': Projectiles.BloodArrow,
    'bullet': Projectiles.Bullet,
    'snowball': Projectiles.SnowBall,
    'platinum_bullet': Projectiles.PlatinumBullet,
    'plasma': Projectiles.Plasma,
    'rock_bullet': Projectiles.RockBullet,
    'shadow_bullet': Projectiles.ShadowBullet,
    'quick_arrow': Projectiles.QuickArrow,
    'quick_bullet': Projectiles.QuickBullet,
    'chloro_arrow': Projectiles.ChloroArrow,
    'space_jumper': Projectiles.SpaceJumper,
    'energy_arrow': Projectiles.EnergyArrow,
}

THIEF_WEAPONS = {
    'copper_knife': Projectiles.ThiefWeapon,
    'dagger': Projectiles.Dagger,
    'platinum_doubleknife': Projectiles.PlatinumDoubleknife,
    'obsidian_knife': Projectiles.ObsidianKnife,
    'bloody_shortknife': Projectiles.BloodyShortknife,
    'apple_knife': Projectiles.AppleKnife,
    'twilight_shortsword': Projectiles.TwilightShortsword,
    'dawn_shortsword': Projectiles.DawnShortsword,
    'night_twinsword': Projectiles.NightTwinsword,
    'spiritual_knife': Projectiles.SpiritualKnife,
    'daedalus_knife': Projectiles.DaedalusKnife,
    'daedalus_twinknife': Projectiles.DaedalusTwinknife,
    'true_twinblade': Projectiles.TrueTwinblade,
    'chaos_chaos': Projectiles.ChaosChaos,
    'storm_stabber': Projectiles.StormStabber,
    'time_flies': Projectiles.TimeFlies,
    'grenade': Projectiles.Grenade,
    'jade_grenade': Projectiles.JadeGrenade,
    'shuriken': Projectiles.Shuriken,
    'spikeball': Projectiles.SpikeBall,
}
