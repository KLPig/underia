import math
import time

from underia import weapons, game, inventory
from underia import projectiles as proj
from values import damages, effects
from resources import position
from physics import vector
from visual import draw, cut_effects
from underia3 import projectiles
import constants
import random
import pygame as pg
import copy

class PurpleClayBroadBlade(weapons.Blade):
    def on_attack(self):
        super().on_attack()
        self.cutting_effect(8)

class WingBlade(weapons.Blade):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vel = vector.Vector2D()
        self.st = 0

    def on_start_attack(self):
        self.st += 1
        super().on_start_attack()
        mx, my = (-game.get_game().player.obj.pos + position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        self.vel += (self.st % 3 == 0) * vector.Vector2D(0, 0, mx, my) / 3

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(8, col1=(255, 255, 0), col2=(200, 200, 200))

    def update(self):
        super().update()
        self.x += self.vel.x
        self.y += self.vel.y
        self.vel *= 0.85
        self.vel -= vector.Vector2D(0, 0, self.x, self.y) / 50

class CelestialPiercer(weapons.Spear):
    def on_start_attack(self):
        super().on_start_attack()
        game.get_game().projectiles.append(projectiles.CelestialPiercer(game.get_game().player.obj.pos,
                                                                        self.rot))

class Muramasa(weapons.Muramasa):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lds = []
        self.ldss = []

    def on_start_attack(self):
        self.lds.clear()
        self.ldss.clear()
        super().on_start_attack()
        for _ in range(random.randint(2 + self.strike // 20, 5 + self.strike // 20)):
            dt = random.randint(50, 300)
            rt = random.randint(0, 360)
            self.lds.append((rt, dt, random.uniform(.5, 3), random.randint(0, 360), random.uniform(-.4, .4)))
            self.ldss.append([vector.Vector2D(rt, dt)])

    def on_end_attack(self):
        super().on_end_attack()
        self.lds.clear()
        self.ldss.clear()

    def update(self, f=0):
        for i, (rt, dt, om, thet, amp) in enumerate(self.lds):
            self.ldss[i].append(vector.Vector2D(rt + self.rot, (dt + 300 * amp * math.sin(om * self.timer / 2 + thet)) * self.scale) + (self.x, self.y))
            if len(self.ldss[i]) > 10:
                self.ldss[i].pop(0)
            for j in range(len(self.ldss[i]) - 1):
                draw.line(game.get_game().displayer.canvas, (255, 255, 255),
                          position.displayed_position(game.get_game().player.obj.pos + self.ldss[i][j]),
                position.displayed_position(game.get_game().player.obj.pos + self.ldss[i][j + 1]), int((2 + i % 2 * 2 + 5 * i // len(self.lds)) * (1 + math.sin(self.timer / 3) * .8) * self.scale / game.get_game().player.get_screen_scale()))

        self.sk_mcd = 150
        self.display = True
        self.cutting_effect(8, (255, 20, 20), (50, 20, 20))
        self.scale += .05 * math.sin(self.timer / self.at_time * math.pi * 2)
        super(weapons.Muramasa, self).update()
        if pg.K_q in game.get_game().get_pressed_keys() and not f and not self.sk_cd:
            wd = copy.copy(game.get_game().displayer.canvas)
            wwd = copy.copy(wd)
            for __ in range(3):
                self.attack()
                for _ in range(self.at_time):
                    self.update(1)
                    window = pg.display.get_surface()
                    if constants.USE_ALPHA:
                        sf = pg.Surface((window.get_width(), window.get_height()))
                        sf.fill((255, 0, 0))
                        sf.set_alpha(128)
                        window.blit(sf, (0, 0))
                    wd = copy.copy(game.get_game().displayer.canvas)
                    pg.display.update()
                    game.get_game().displayer.update()
                    game.get_game().displayer.canvas.blit(wd, (0, 0))
                wd = copy.copy(wwd)
                time.sleep(.2)
            self.sk_cd = self.sk_mcd


class MiracleCrystalBlade(weapons.Blade):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sst = 0

    def on_start_attack(self):
        self.sst += 1
        super().on_start_attack()
        rr = vector.coordinate_rotation(*(-game.get_game().player.obj.pos + position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if self.sst % 3 == 0:
            for ar in range(-10, 11, 10):
                game.get_game().projectiles.append(projectiles.MiracleCrystalBlade(game.get_game().player.obj.pos, rr + ar + random.randint(-5, 5)))

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(6, col1=(200, 255, 100), col2=(100, 150, 0))
        self.cutting_effect(4, col1=(0, 255, 255), col2=(0, 127, 127))

class Destroy(weapons.Blade):
    def damage(self):
        if self.rot_speed > 0:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed + 1))
        else:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed - 1), -1)
        for e in game.get_game().entities:
            dps = e.obj.pos
            px = dps[0] - self.x - game.get_game().player.obj.pos[0]
            py = dps[1] - self.y - game.get_game().player.obj.pos[1]
            r = int(vector.coordinate_rotation(px, py)) % 360
            if r in rot_range or r + 360 in rot_range or (
                    self.double_sided and ((r + 180) % 360 in rot_range or r + 180 in rot_range)):
                if vector.distance(px, py) < self.img.get_width() * self.scale + (
                        (e.img.get_width() + e.img.get_height()) // 2 if e.img is not None else 10):
                    rr = bool(e.hp_sys.hp > e.hp_sys.max_hp * .9) + 1
                    e.hp_sys.DODGE_RATE -= .5
                    for t, d in self.damages.items():
                        e.hp_sys.damage(
                            rr * d * game.get_game().player.attack * game.get_game().player.attacks[self.DMG_AS_IDX], t)
                    e.hp_sys.DODGE_RATE -= .5
                    if not e.hp_sys.is_immune:
                        rf = vector.coordinate_rotation(px + self.x, py + self.y)
                        e.obj.apply_force(vector.Vector(rf, min(self.knock_back * 120000 / e.obj.MASS, e.obj.MASS * 24)
                        if self.knock_back * 60000 < e.obj.MASS or constants.DIFFICULTY <= 1 else
                        min(self.knock_back * 600000 / e.obj.MASS, e.obj.MASS * 24)))
                    if 'matters_touch' in game.get_game().player.accessories:
                        e.obj.MASS *= 1.01
                    if 'grasp_of_the_infinite_corridor' in game.get_game().player.accessories:
                        if not e.IS_MENACE and not e.VITAL:
                            e.hp_sys.damage(e.hp_sys.max_hp / 10, damages.DamageTypes.THINKING)
                            if random.randint(0, 10) == 0:
                                e.hp_sys.hp = 0
                        else:
                            e.hp_sys.damage(max(e.hp_sys.max_hp / 1000, 10000), damages.DamageTypes.THINKING)
                    if self.ENABLE_IMMUNE:
                        if constants.DIFFICULTY > 1:
                            e.hp_sys.enable_immune()

class Generate(weapons.Blade):
    def damage(self):
        if self.rot_speed > 0:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed + 1))
        else:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed - 1), -1)
        for e in game.get_game().entities:
            dps = e.obj.pos
            px = dps[0] - self.x - game.get_game().player.obj.pos[0]
            py = dps[1] - self.y - game.get_game().player.obj.pos[1]
            r = int(vector.coordinate_rotation(px, py)) % 360
            if r in rot_range or r + 360 in rot_range or (
                    self.double_sided and ((r + 180) % 360 in rot_range or r + 180 in rot_range)):
                if vector.distance(px, py) < self.img.get_width() * self.scale + (
                        (e.img.get_width() + e.img.get_height()) // 2 if e.img is not None else 10):
                    rr = 4 * (1 - e.hp_sys.hp / e.hp_sys.max_hp) + 1
                    ahp = e.hp_sys.hp
                    for t, d in self.damages.items():
                        e.hp_sys.damage(
                            rr * d * game.get_game().player.attack * game.get_game().player.attacks[self.DMG_AS_IDX], t)
                    if not e.IS_MENACE:
                        e.hp_sys.max_hp += max(0, ahp - e.hp_sys.hp - 1)
                    if not e.hp_sys.is_immune:
                        rf = vector.coordinate_rotation(px + self.x, py + self.y)
                        e.obj.apply_force(vector.Vector(rf, min(self.knock_back * 120000 / e.obj.MASS, e.obj.MASS * 24)
                        if self.knock_back * 60000 < e.obj.MASS or constants.DIFFICULTY <= 1 else
                        min(self.knock_back * 600000 / e.obj.MASS, e.obj.MASS * 24)))
                    if 'matters_touch' in game.get_game().player.accessories:
                        e.obj.MASS *= 1.01
                    if 'grasp_of_the_infinite_corridor' in game.get_game().player.accessories:
                        if not e.IS_MENACE and not e.VITAL:
                            e.hp_sys.damage(e.hp_sys.max_hp / 10, damages.DamageTypes.THINKING)
                            if random.randint(0, 10) == 0:
                                e.hp_sys.hp = 0
                        else:
                            e.hp_sys.damage(max(e.hp_sys.max_hp / 1000, 10000), damages.DamageTypes.THINKING)
                    if self.ENABLE_IMMUNE:
                        if constants.DIFFICULTY > 1:
                            e.hp_sys.enable_immune()

class WheelFrogileSword(weapons.Blade):
    def damage(self):
        if self.rot_speed > 0:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed + 1))
        else:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed - 1), -1)
        for e in game.get_game().entities:
            dps = e.obj.pos
            px = dps[0] - self.x - game.get_game().player.obj.pos[0]
            py = dps[1] - self.y - game.get_game().player.obj.pos[1]
            r = int(vector.coordinate_rotation(px, py)) % 360
            if r in rot_range or r + 360 in rot_range or (
                    self.double_sided and ((r + 180) % 360 in rot_range or r + 180 in rot_range)):
                if vector.distance(px, py) < self.img.get_width() * self.scale + (
                        (e.img.get_width() + e.img.get_height()) // 2 if e.img is not None else 10):
                    ahp = e.hp_sys.hp
                    for t, d in self.damages.items():
                        e.hp_sys.damage(
                             d * game.get_game().player.attack * game.get_game().player.attacks[self.DMG_AS_IDX], t)
                    tv = vector.coordinate_rotation(*(game.get_game().player.obj.pos - e.obj.pos))
                    av = max(0, abs(e.obj.velocity) * math.cos(math.radians(tv - e.obj.velocity.get_net_rotation())))
                    e.obj.velocity -= vector.Vector2D(tv, av * 2)
                    if not e.hp_sys.is_immune:
                        rf = vector.coordinate_rotation(px + self.x, py + self.y)
                        e.obj.apply_force(vector.Vector(rf, min(self.knock_back * 120000 / e.obj.MASS, e.obj.MASS * 24)
                        if self.knock_back * 60000 < e.obj.MASS or constants.DIFFICULTY <= 1 else
                        min(self.knock_back * 600000 / e.obj.MASS, e.obj.MASS * 24)))
                    if 'matters_touch' in game.get_game().player.accessories:
                        e.obj.MASS *= 1.01
                    if 'grasp_of_the_infinite_corridor' in game.get_game().player.accessories:
                        if not e.IS_MENACE and not e.VITAL:
                            e.hp_sys.damage(e.hp_sys.max_hp / 10, damages.DamageTypes.THINKING)
                            if random.randint(0, 10) == 0:
                                e.hp_sys.hp = 0
                        else:
                            e.hp_sys.damage(max(e.hp_sys.max_hp / 1000, 10000), damages.DamageTypes.THINKING)
                    if self.ENABLE_IMMUNE:
                        if constants.DIFFICULTY > 1:
                            e.hp_sys.enable_immune()

class CorruptSword(weapons.Blade):
    def damage(self):
        if self.rot_speed > 0:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed + 1))
        else:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed - 1), -1)
        for e in game.get_game().entities:
            dps = e.obj.pos
            px = dps[0] - self.x - game.get_game().player.obj.pos[0]
            py = dps[1] - self.y - game.get_game().player.obj.pos[1]
            r = int(vector.coordinate_rotation(px, py)) % 360
            if r in rot_range or r + 360 in rot_range or (
                    self.double_sided and ((r + 180) % 360 in rot_range or r + 180 in rot_range)):
                if vector.distance(px, py) < self.img.get_width() * self.scale + (
                        (e.img.get_width() + e.img.get_height()) // 2 if e.img is not None else 10):
                    ahp = e.hp_sys.hp
                    for t, d in self.damages.items():
                        e.hp_sys.damage(
                             d * game.get_game().player.attack * game.get_game().player.attacks[self.DMG_AS_IDX], t)
                    e.hp_sys.effect(effects.Poison(8, 8))
                    if not e.hp_sys.is_immune:
                        rf = vector.coordinate_rotation(px + self.x, py + self.y)
                        e.obj.apply_force(vector.Vector(rf, min(self.knock_back * 120000 / e.obj.MASS, e.obj.MASS * 24)
                        if self.knock_back * 60000 < e.obj.MASS or constants.DIFFICULTY <= 1 else
                        min(self.knock_back * 600000 / e.obj.MASS, e.obj.MASS * 24)))
                    if 'matters_touch' in game.get_game().player.accessories:
                        e.obj.MASS *= 1.01
                    if 'grasp_of_the_infinite_corridor' in game.get_game().player.accessories:
                        if not e.IS_MENACE and not e.VITAL:
                            e.hp_sys.damage(e.hp_sys.max_hp / 10, damages.DamageTypes.THINKING)
                            if random.randint(0, 10) == 0:
                                e.hp_sys.hp = 0
                        else:
                            e.hp_sys.damage(max(e.hp_sys.max_hp / 1000, 10000), damages.DamageTypes.THINKING)
                    if self.ENABLE_IMMUNE:
                        if constants.DIFFICULTY > 1:
                            e.hp_sys.enable_immune()

class GaussDagger(weapons.Blade):
    def damage(self):
        if self.rot_speed > 0:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed + 1))
        else:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed - 1), -1)
        for e in game.get_game().entities:
            dps = e.obj.pos
            px = dps[0] - self.x - game.get_game().player.obj.pos[0]
            py = dps[1] - self.y - game.get_game().player.obj.pos[1]
            r = int(vector.coordinate_rotation(px, py)) % 360
            if r in rot_range or r + 360 in rot_range or (
                    self.double_sided and ((r + 180) % 360 in rot_range or r + 180 in rot_range)):
                if vector.distance(px, py) < self.img.get_width() * self.scale + (
                        (e.img.get_width() + e.img.get_height()) // 2 if e.img is not None else 10):
                    for t, d in self.damages.items():
                        e.hp_sys.damage(
                             d * game.get_game().player.attack * game.get_game().player.attacks[self.DMG_AS_IDX], t)
                        e.hp_sys.damage(d * game.get_game().player.attack * game.get_game().player.attacks[self.DMG_AS_IDX] * .3,
                                        damages.DamageTypes.TRUE)
                    if not e.hp_sys.is_immune:
                        rf = vector.coordinate_rotation(px + self.x, py + self.y)
                        e.obj.apply_force(vector.Vector(rf, min(self.knock_back * 120000 / e.obj.MASS, e.obj.MASS * 24)
                        if self.knock_back * 60000 < e.obj.MASS or constants.DIFFICULTY <= 1 else
                        min(self.knock_back * 600000 / e.obj.MASS, e.obj.MASS * 24)))
                    if 'matters_touch' in game.get_game().player.accessories:
                        e.obj.MASS *= 1.01
                    if 'grasp_of_the_infinite_corridor' in game.get_game().player.accessories:
                        if not e.IS_MENACE and not e.VITAL:
                            e.hp_sys.damage(e.hp_sys.max_hp / 10, damages.DamageTypes.THINKING)
                            if random.randint(0, 10) == 0:
                                e.hp_sys.hp = 0
                        else:
                            e.hp_sys.damage(max(e.hp_sys.max_hp / 1000, 10000), damages.DamageTypes.THINKING)
                    if self.ENABLE_IMMUNE:
                        if constants.DIFFICULTY > 1:
                            e.hp_sys.enable_immune()

class HighTechMetalSword(weapons.Blade):
    def damage(self):
        if self.rot_speed > 0:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed + 1))
        else:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed - 1), -1)
        for e in game.get_game().entities:
            dps = e.obj.pos
            px = dps[0] - self.x - game.get_game().player.obj.pos[0]
            py = dps[1] - self.y - game.get_game().player.obj.pos[1]
            r = int(vector.coordinate_rotation(px, py)) % 360
            if r in rot_range or r + 360 in rot_range or (
                    self.double_sided and ((r + 180) % 360 in rot_range or r + 180 in rot_range)):
                if vector.distance(px, py) < self.img.get_width() * self.scale + (
                        (e.img.get_width() + e.img.get_height()) // 2 if e.img is not None else 10):
                    ahp = e.hp_sys.hp
                    for t, d in self.damages.items():
                        e.hp_sys.damage(
                             d * game.get_game().player.attack * game.get_game().player.attacks[self.DMG_AS_IDX], t)
                    e.hp_sys.effect(effects.Burning(1, 10))
                    e.hp_sys.effect(effects.BleedingR(1, 10))
                    if not e.hp_sys.is_immune:
                        rf = vector.coordinate_rotation(px + self.x, py + self.y)
                        e.obj.apply_force(vector.Vector(rf, min(self.knock_back * 120000 / e.obj.MASS, e.obj.MASS * 24)
                        if self.knock_back * 60000 < e.obj.MASS or constants.DIFFICULTY <= 1 else
                        min(self.knock_back * 600000 / e.obj.MASS, e.obj.MASS * 24)))
                    if 'matters_touch' in game.get_game().player.accessories:
                        e.obj.MASS *= 1.01
                    if 'grasp_of_the_infinite_corridor' in game.get_game().player.accessories:
                        if not e.IS_MENACE and not e.VITAL:
                            e.hp_sys.damage(e.hp_sys.max_hp / 10, damages.DamageTypes.THINKING)
                            if random.randint(0, 10) == 0:
                                e.hp_sys.hp = 0
                        else:
                            e.hp_sys.damage(max(e.hp_sys.max_hp / 1000, 10000), damages.DamageTypes.THINKING)
                    if self.ENABLE_IMMUNE:
                        if constants.DIFFICULTY > 1:
                            e.hp_sys.enable_immune()

class ScarDagger(weapons.Blade):
    def on_start_attack(self):
        super().on_start_attack()
        game.get_game().player.hp_sys.damage(8, damages.DamageTypes.TRUE)

    def damage(self):
        if self.rot_speed > 0:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed + 1))
        else:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed - 1), -1)
        for e in game.get_game().entities:
            dps = e.obj.pos
            px = dps[0] - self.x - game.get_game().player.obj.pos[0]
            py = dps[1] - self.y - game.get_game().player.obj.pos[1]
            r = int(vector.coordinate_rotation(px, py)) % 360
            if r in rot_range or r + 360 in rot_range or (
                    self.double_sided and ((r + 180) % 360 in rot_range or r + 180 in rot_range)):
                if vector.distance(px, py) < self.img.get_width() * self.scale + (
                        (e.img.get_width() + e.img.get_height()) // 2 if e.img is not None else 10):
                    ahp = e.hp_sys.hp
                    for _ in range(2):
                        for t, d in self.damages.items():
                            e.hp_sys.damage(
                                 d * game.get_game().player.attack * game.get_game().player.attacks[self.DMG_AS_IDX], t,
                            penetrate=66)
                    dhp = ahp - e.hp_sys.hp
                    game.get_game().player.hp_sys.heal(min(8.5, dhp * .024))
                    e.hp_sys.effect(effects.BleedingR(1, 12))
                    if not e.hp_sys.is_immune:
                        rf = vector.coordinate_rotation(px + self.x, py + self.y)
                        e.obj.apply_force(vector.Vector(rf, min(self.knock_back * 120000 / e.obj.MASS, e.obj.MASS * 24)
                        if self.knock_back * 60000 < e.obj.MASS or constants.DIFFICULTY <= 1 else
                        min(self.knock_back * 600000 / e.obj.MASS, e.obj.MASS * 24)))
                    if 'matters_touch' in game.get_game().player.accessories:
                        e.obj.MASS *= 1.01
                    if 'grasp_of_the_infinite_corridor' in game.get_game().player.accessories:
                        if not e.IS_MENACE and not e.VITAL:
                            e.hp_sys.damage(e.hp_sys.max_hp / 10, damages.DamageTypes.THINKING)
                            if random.randint(0, 10) == 0:
                                e.hp_sys.hp = 0
                        else:
                            e.hp_sys.damage(max(e.hp_sys.max_hp / 1000, 10000), damages.DamageTypes.THINKING)
                    if self.ENABLE_IMMUNE:
                        if constants.DIFFICULTY > 1:
                            e.hp_sys.enable_immune()

class ChaosDagger(weapons.Blade):
    def on_start_attack(self):
        super().on_start_attack()

    def damage(self):
        if self.rot_speed > 0:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed + 1))
        else:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed - 1), -1)
        for e in game.get_game().entities:
            dps = e.obj.pos
            px = dps[0] - self.x - game.get_game().player.obj.pos[0]
            py = dps[1] - self.y - game.get_game().player.obj.pos[1]
            r = int(vector.coordinate_rotation(px, py)) % 360
            if r in rot_range or r + 360 in rot_range or (
                    self.double_sided and ((r + 180) % 360 in rot_range or r + 180 in rot_range)):
                if vector.distance(px, py) < self.img.get_width() * self.scale + (
                        (e.img.get_width() + e.img.get_height()) // 2 if e.img is not None else 10):
                    if 'd_cd_t' not in dir(e):
                        setattr(e, 'd_cd_t', 0)
                        tt = 0
                    else:
                        tt = getattr(e, 'd_cd_t') + 1
                        setattr(e, 'd_cd_t', tt)
                    for t, d in self.damages.items():
                        e.hp_sys.damage(
                            math.e ** (-.07 * tt) * d * game.get_game().player.attack * game.get_game().player.attacks[self.DMG_AS_IDX], t
                        )

                    if not e.hp_sys.is_immune:
                        rf = vector.coordinate_rotation(px + self.x, py + self.y)
                        e.obj.apply_force(vector.Vector(rf, min(self.knock_back * 120000 / e.obj.MASS, e.obj.MASS * 24)
                        if self.knock_back * 60000 < e.obj.MASS or constants.DIFFICULTY <= 1 else
                        min(self.knock_back * 600000 / e.obj.MASS, e.obj.MASS * 24)))
                    if 'matters_touch' in game.get_game().player.accessories:
                        e.obj.MASS *= 1.01
                    if 'grasp_of_the_infinite_corridor' in game.get_game().player.accessories:
                        if not e.IS_MENACE and not e.VITAL:
                            e.hp_sys.damage(e.hp_sys.max_hp / 10, damages.DamageTypes.THINKING)
                            if random.randint(0, 10) == 0:
                                e.hp_sys.hp = 0
                        else:
                            e.hp_sys.damage(max(e.hp_sys.max_hp / 1000, 10000), damages.DamageTypes.THINKING)
                    if self.ENABLE_IMMUNE:
                        if constants.DIFFICULTY > 1:
                            e.hp_sys.enable_immune()

class MuraKumo(weapons.Blade):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ap = vector.Vector2D()
        self.avel = vector.Vector2D()
        self.ds = pg.Surface((2000, 2000), pg.SRCALPHA)
        self.st = 0
        for i in range(500):
            x = random.randint(0, 2000)
            y = random.randint(0, 2000)
            sz = random.randint(1, 8)
            pg.draw.rect(self.ds, (150, 255, 100), (x - sz // 2, y - sz // 2, sz, sz))

    def attack(self):
        super().attack()
        if self.st <= 0:
            self.avel += vector.Vector2D(self.rot, -10)

    def update(self):
        super().update()
        self.ap += self.avel
        self.avel *= .99
        if abs(self.avel) < 3:
            self.ds.set_alpha(int(abs(self.avel) * 255 / 3))
        else:
            self.ds.set_alpha(255)
        dds = self.ds
        dds_r = dds.get_rect(center=position.displayed_position(self.ap))
        game.get_game().displayer.canvas.blit(dds, dds_r)

    def on_start_attack(self):
        super().on_start_attack()
        if abs(self.avel) < .1 or self.st == 1:
            self.st = 0
            self.ap = game.get_game().player.obj.pos + vector.Vector2D(self.rot, 500)
        else:
            self.st = (self.st + 1) % 2

    def damage(self):
        if self.rot_speed > 0:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed + 1))
            arot_range =  range(int(self.rot - self.rot_speed * 10), int(self.rot + self.rot_speed * 10 + 1))
        else:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed - 1), -1)
            arot_range =  range(int(self.rot - self.rot_speed * 10), int(self.rot + self.rot_speed * 10 + 1), -1)
        for e in game.get_game().entities:
            dps = e.obj.pos
            px = dps[0] - self.x - game.get_game().player.obj.pos[0]
            py = dps[1] - self.y - game.get_game().player.obj.pos[1]
            r = int(vector.coordinate_rotation(px, py)) % 360
            if r in rot_range or r + 360 in rot_range or (
                    self.double_sided and ((r + 180) % 360 in rot_range or r + 180 in rot_range)):
                if vector.distance(px, py) < self.img.get_width() * self.scale + (
                        (e.img.get_width() + e.img.get_height()) // 2 if e.img is not None else 10):
                    for t, d in self.damages.items():
                        e.hp_sys.damage(
                            d * game.get_game().player.attack * game.get_game().player.attacks[self.DMG_AS_IDX], t)
                    if not e.hp_sys.is_immune:
                        rf = vector.coordinate_rotation(px + self.x, py + self.y)
                        e.obj.apply_force(vector.Vector(rf, min(self.knock_back * 120000 / e.obj.MASS, e.obj.MASS * 24)
                        if self.knock_back * 60000 < e.obj.MASS or constants.DIFFICULTY <= 1 else
                        min(self.knock_back * 600000 / e.obj.MASS, e.obj.MASS * 24)))
                    if 'matters_touch' in game.get_game().player.accessories:
                        e.obj.MASS *= 1.01
                    if 'grasp_of_the_infinite_corridor' in game.get_game().player.accessories:
                        if not e.IS_MENACE and not e.VITAL:
                            e.hp_sys.damage(e.hp_sys.max_hp / 10, damages.DamageTypes.THINKING)
                            if random.randint(0, 10) == 0:
                                e.hp_sys.hp = 0
                        else:
                            e.hp_sys.damage(max(e.hp_sys.max_hp / 1000, 10000), damages.DamageTypes.THINKING)
                    if self.ENABLE_IMMUNE:
                        if constants.DIFFICULTY > 1:
                            e.hp_sys.enable_immune()
            if r in arot_range or r + 360 in arot_range or (
                    self.double_sided and ((r + 180) % 360 in arot_range or r + 180 in arot_range)):
                if vector.distance(px, py) < 3000 * self.scale + (
                        (e.img.get_width() + e.img.get_height()) // 2 if e.img is not None else 10) and not e.hp_sys.is_immune:
                    ar = 3000 * self.scale + ((e.img.get_width() + e.img.get_height()) // 2 if e.img is not None else 10)
                    ar = vector.distance(px, py) / ar
                    ar = (1 - ar) ** 2
                    for t, d in self.damages.items():
                        e.hp_sys.damage(
                            d * game.get_game().player.attack * game.get_game().player.attacks[self.DMG_AS_IDX] * ar * .3, t,
                            penetrate=d * game.get_game().player.attack * game.get_game().player.attacks[self.DMG_AS_IDX] * ar)
                    rf = vector.coordinate_rotation(px + self.x, py + self.y)
                    e.obj.velocity += vector.Vector(rf, ar * 25)
                    e.hp_sys.is_immune = 1

class Longinus(weapons.Blade):
    def on_attack(self):
        super().on_attack()
        self.cutting_effect(10, (255, 255, 100), (127, 255, 0))
        if self.timer % 3 == 0:
            game.get_game().projectiles.append(projectiles.Longinus(game.get_game().player.obj.pos, self.rot, self.timer))

class XuanYuan(weapons.Blade):
    def on_start_attack(self):
        super().on_start_attack()
        for e in game.get_game().entities:
            if 'xuanyuan' not in dir(e):
                setattr(e, 'xuanyuan', 1)
                e.hp_sys.max_hp *= .85
                e.hp_sys.hp *= .85
                e.obj.MASS *= 1.5
                e.hp_sys.DODGE_RATE -= .2
                for d in e.hp_sys.defenses.defences.keys():
                    e.hp_sys.defenses[d] -= 20

class Durendal(weapons.Blade):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.c = 0
        self.sr = 0
        self.mode = True

    def on_special_attack(self, strike: int):
        self.mode = not self.mode
        super().on_special_attack(strike)

    def on_attack(self):
        super().on_attack()
        if self.c == 1:
            self.set_rotation(0)
            self.sr = min(self.sr + 10, 600 - 400 * self.mode)

    def update(self):
        self.damages[damages.DamageTypes.PHYSICAL] = int(2.5 * self.sr)
        inventory.ITEMS['durendal'].desc = '\n'.join(inventory.ITEMS['durendal'].desc.split('\n')[:-1]) + '\n' + f'MODE {2 - self.mode}, CHARGE {self.sr / 8:.1f}%'
        super().update()
        pg.draw.circle(game.get_game().displayer.canvas, (100, 255, 255),
                       position.displayed_position(game.get_game().player.obj.pos + vector.Vector2D(self.rot, 400)),
                       int(self.sr * (1 + .2 * math.sin(game.get_game().player.tick / 50 * math.pi)) / 4 / game.get_game().player.get_screen_scale()))

    def on_start_attack(self):
        super().on_start_attack()
        if self.sr < 500 - 450 * self.mode:
            self.c = 1
        elif not self.mode:
            self.c = 2
            self.sr -= 10
        else:
            self.sr = max(0, self.sr - 30)
            ps = game.get_game().player.obj.pos + vector.Vector2D(self.rot, 300)
            game.get_game().projectiles.append(projectiles.Durendal(ps,
                                                                    vector.coordinate_rotation(*(-ps + position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))))
            self.c += 1

class Bident(weapons.Spear):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tars: list[tuple] = []

    def update(self):
        super().update()
        for i, (e, r, vv, td) in enumerate(self.tars):
            e.obj.TOUCHING_DAMAGE = 0
            tp = game.get_game().player.obj.pos + vector.Vector2D(self.rot + r, 200)
            av = max(0, vv - abs(tp - e.obj.pos) - 10)
            e.hp_sys.hp -= 10
            e.obj.pos = tp
            if not av:
                e.obj.TOUCHING_DAMAGE = td
                e.obj.apply_force(vector.Vector(self.rot + r, 5000))
            self.tars[i] = (e, r, av, td)
        for e, r, vv, td in self.tars:
            if not vv:
                self.tars.remove((e, r, vv, td))

    def damage(self):
        self.rot %= 360
        rot_range = range(int(self.rot - 15), int(self.rot + 16))
        for e in game.get_game().entities:
            dps = e.obj.pos
            px = dps[0] - game.get_game().player.obj.pos[0]
            py = dps[1] - game.get_game().player.obj.pos[1]
            r = int(vector.coordinate_rotation(px, py)) % 360
            if r in rot_range or r + 360 in rot_range:
                if vector.distance(px, py) < self.img.get_width() + self.poss + (
                (e.img.get_width() + e.img.get_height()) // 2 if e.img is not None else 10):
                    if random.random() < .1 * game.get_game().player.attack * game.get_game().player.attacks[0] and not len([1 for ee, _, _, _ in self.tars if ee == e]):
                        self.tars.append((e, vector.coordinate_rotation(*(e.obj.pos - game.get_game().player.obj.pos)) - self.rot, 1000 * game.get_game().player.attack * game.get_game().player.attacks[0], e.obj.TOUCHING_DAMAGE))
                    for t, d in self.damages.items():
                        e.hp_sys.damage(d * game.get_game().player.attack * game.get_game().player.attacks[0], t)
                    if not e.hp_sys.is_immune:
                        e.obj.apply_force(vector.Vector(r, min(self.knock_back * 120000 / e.obj.MASS, e.obj.MASS * 24)))
                    if self.ENABLE_IMMUNE:
                        e.hp_sys.enable_immune()

class FeatherSword(weapons.Blade):
    def on_start_attack(self):
        super().on_start_attack()
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        game.get_game().projectiles.append(projectiles.FeatherSword(game.get_game().player.obj.pos, vector.cartesian_to_polar(mx, my)[0]))

class FeatherFeatherSword(weapons.Blade):
    def on_start_attack(self):
        super().on_start_attack()
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        game.get_game().projectiles.append(projectiles.FeatherFeatherSword(game.get_game().player.obj.pos, vector.cartesian_to_polar(mx, my)[0]))

class PoiseBlade(weapons.Blade):
    def on_attack(self):
        super().on_attack()
        self.cutting_effect(4, (200, 255, 100), (100, 150, 50))
        for e in game.get_game().entities:
            if vector.distance(*(e.obj.pos - game.get_game().player.obj.pos)) < 500:
                if not e.hp_sys.is_immune:
                    e.hp_sys.damage(self.damages[damages.DamageTypes.PHYSICAL] * .3, damages.DamageTypes.TRUE, 80)
                    e.hp_sys.enable_immune()

class LycheeBow(weapons.Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in proj.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[
            1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data(
                'ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        pj = projectiles.LycheeArrow((self.x + game.get_game().player.obj.pos[0],
                                      self.y + game.get_game().player.obj.pos[1]),
                                     self.rot + random.uniform(-self.precision, self.precision),
                                     self.spd + proj.AMMOS[game.get_game().player.ammo[0]].SPEED,
                                     self.damages[damages.DamageTypes.PIERCING] + proj.AMMOS[game.get_game().player.ammo[0]].DAMAGES)
        if self.tail_col is not None:
            pj.TAIL_COLOR = self.tail_col
            pj.TAIL_SIZE = max(pj.TAIL_SIZE, 3)
            pj.TAIL_WIDTH = max(pj.TAIL_WIDTH, 3)
        game.get_game().projectiles.append(pj)

class DarkCannon(weapons.Gun):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if not game.get_game().player.inventory.is_enough(inventory.ITEMS['dark_energy'], 40):
            self.timer = 0
            return
        if random.random() < self.ammo_save_chance + game.get_game().player.calculate_data(
                'ammo_save', False) / 100:
            game.get_game().player.inventory.remove_item(inventory.ITEMS['dark_energy'], 40)
        pj = projectiles.DarkCannon(game.get_game().player.obj.pos, self.rot)
        game.get_game().projectiles.append(pj)

class BloodyRain(weapons.Gun):
    ATTACK_SOUND = 'attack_slash'

    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo_bullet[0] not in proj.AMMOS or not game.get_game().player.ammo_bullet[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo_bullet[
            1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data(
                'ammo_save', False) / 100:
            game.get_game().player.ammo_bullet = (game.get_game().player.ammo_bullet[0], game.get_game().player.ammo_bullet[1] - 1)
        for _ in range(4):
            pj = projectiles.BloodyRains((self.x + game.get_game().player.obj.pos[0] + random.randint(-30, 30),
                                          self.y + game.get_game().player.obj.pos[1] + random.randint(-30, 30)),
                                         self.rot + random.uniform(-self.precision, self.precision),
                                         self.spd + proj.AMMOS[game.get_game().player.ammo_bullet[0]].SPEED,
                                         self.damages[damages.DamageTypes.PIERCING] + proj.AMMOS[game.get_game().player.ammo_bullet[0]].DAMAGES)
            if self.tail_col is not None:
                pj.TAIL_COLOR = self.tail_col
                pj.TAIL_SIZE = max(pj.TAIL_SIZE, 3)
                pj.TAIL_WIDTH = max(pj.TAIL_WIDTH, 3)
            game.get_game().projectiles.append(pj)

class GravitySlingshot(weapons.Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in proj.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[
            1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data(
                'ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        pj = projectiles.GravityArrow((self.x + game.get_game().player.obj.pos[0],
                                      self.y + game.get_game().player.obj.pos[1]),
                                     self.rot + random.uniform(-self.precision, self.precision),
                                     self.spd + proj.AMMOS[game.get_game().player.ammo[0]].SPEED,
                                     self.damages[damages.DamageTypes.PIERCING] + proj.AMMOS[game.get_game().player.ammo[0]].DAMAGES)
        if self.tail_col is not None:
            pj.TAIL_COLOR = self.tail_col
            pj.TAIL_SIZE = max(pj.TAIL_SIZE, 3)
            pj.TAIL_WIDTH = max(pj.TAIL_WIDTH, 3)
        game.get_game().projectiles.append(pj)

class HopeScorchBow(weapons.Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in proj.AMMOS or game.get_game().player.ammo[1] < 3:
            self.timer = 0
            return
        if game.get_game().player.ammo[
            1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data(
                'ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 3)
        for ar in [-10, 0, 10]:
            pj = projectiles.HopeScorchBow(vector.Vector2D(self.rot + 90, ar * 3) +
                                           (self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1]),
                                         self.rot + random.uniform(-self.precision, self.precision),
                                         self.spd + proj.AMMOS[game.get_game().player.ammo[0]].SPEED,
                                         self.damages[damages.DamageTypes.PIERCING] + proj.AMMOS[game.get_game().player.ammo[0]].DAMAGES)
            game.get_game().projectiles.append(pj)

class AbyssGaze(weapons.Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in proj.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[
            1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data(
                'ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        for ar in range(-40, 41, 20):
            mp = game.get_game().player.obj.pos + vector.Vector2D(self.rot + 90, ar) + (self.x, self.y) + vector.Vector2D(self.rot, -abs(ar) // 2)
            pj = proj.AMMOS[game.get_game().player.ammo[0]](mp,
                                                             self.rot + random.uniform(-self.precision, self.precision),
                                                             self.spd + proj.AMMOS[game.get_game().player.ammo[0]].SPEED,
                                                             self.damages[damages.DamageTypes.PIERCING] + proj.AMMOS[game.get_game().player.ammo[0]].DAMAGES)
            if self.tail_col is not None:
                pj.TAIL_COLOR = self.tail_col
                pj.TAIL_SIZE = max(pj.TAIL_SIZE, 3)
                pj.TAIL_WIDTH = max(pj.TAIL_WIDTH, 3)
            game.get_game().projectiles.append(pj)

class Pierce(weapons.Gun):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sk_mcd = 120

    def on_start_attack(self):
        super().on_start_attack()
        if not self.sk_cd:
            game.get_game().projectiles.append(projectiles.Pierce(game.get_game().player.obj.pos, self.rot))
            self.sk_cd = self.sk_mcd

class Gandiva(weapons.Bow):
    def on_start_attack(self):
        sr = self.rot
        for i in range(random.randint(3, 5)):
            if game.get_game().player.ammo[0] not in proj.AMMOS or not game.get_game().player.ammo[1]:
                self.timer = 0
                break
            if game.get_game().player.ammo[1] < constants.ULTIMATE_AMMO_BONUS and random.random() > self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
                game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
            pj = proj.AMMOS[game.get_game().player.ammo[0]]((self.x + game.get_game().player.obj.pos[0],
                                                                   self.y + game.get_game().player.obj.pos[1]),
                                                                  self.rot + random.uniform(-self.precision, self.precision), self.spd,
                                                                  self.damages[damages.DamageTypes.PIERCING])
            if self.tail_col is not None:
                pj.TAIL_COLOR = self.tail_col
                pj.TAIL_SIZE = max(pj.TAIL_SIZE, self.ts)
                pj.TAIL_WIDTH = max(pj.TAIL_WIDTH, self.tw)
            game.get_game().projectiles.append(pj)
        self.rot = sr

    def update(self):
        super().update()
        self.display = True
        if pg.BUTTON_LEFT in game.get_game().get_pressed_mouse():
            self.set_rotation(self.rot * 4 / 5 + 36)
            self.x, self.y = vector.Vector2D(0, 0, self.x, self.y) + (-game.get_game().player.obj.pos - (self.x, self.y + 500) + position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))) / 5
        else:
            self.x /= 2
            self.y /= 2
            self.set_rotation(self.rot * 3 / 4 + vector.coordinate_rotation(*(-game.get_game().player.obj.pos + position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))) / 4)

class UllrBow(weapons.Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in proj.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[
            1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data(
                'ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        pj = projectiles.UllrBow((self.x + game.get_game().player.obj.pos[0],
                                      self.y + game.get_game().player.obj.pos[1]),
                                     self.rot + random.uniform(-self.precision, self.precision),
                                     self.spd + proj.AMMOS[game.get_game().player.ammo[0]].SPEED,
                                     self.damages[damages.DamageTypes.PIERCING] + proj.AMMOS[game.get_game().player.ammo[0]].DAMAGES)
        if self.tail_col is not None:
            pj.TAIL_COLOR = self.tail_col
            pj.TAIL_SIZE = max(pj.TAIL_SIZE, 3)
            pj.TAIL_WIDTH = max(pj.TAIL_WIDTH, 3)
        game.get_game().projectiles.append(pj)

class SuperNova(weapons.Gun):
    ATTACK_SOUND = 'attack_quickshot'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ammo = None
        self.st = 0

    def on_start_attack(self):
        if random.random() <= .2 and game.get_game().player.ammo_bullet[1]:
            self.ammo = game.get_game().player.ammo_bullet
            game.get_game().player.ammo_bullet = ('energy_arrow', 1)
        super().on_start_attack()

    def on_end_attack(self):
        super().on_end_attack()
        if self.ammo is not None:
            game.get_game().player.ammo_bullet = self.ammo
            self.ammo = None
        self.st = 0
        self.cd = max(0, self.cd - 1)

    def on_idle(self):
        super().on_idle()
        self.st += 1
        if self.st >= 25:
            self.cd = min(self.cd + 1, 24)

class WierSwin(weapons.Gun):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.att = 0
        self.sk_mcd = 250

    def on_start_attack(self):
        if self.sk_cd:
            self.timer = 0
            return
        if self.att != 114:
            self.att = 4
            super().on_start_attack()

    def on_special_attack(self, strike: int):
        if self.sk_cd:
            self.timer = 0
            return
        super().on_special_attack(strike)
        self.att = 114
        game.get_game().projectiles.append(projectiles.WierSwin(game.get_game().player.obj.pos, self.rot))
        game.get_game().player.obj.apply_force(vector.Vector2D(self.rot, -40000))
        self.sk_cd = self.sk_mcd - min(200, strike)
        self.timer += 12

    def on_charge(self):
        if self.sk_cd:
            return
        super().on_charge()
        self.scale = 1


    def on_attack(self):
        super().on_attack()
        if self.att == 114:
            self.rotate(48)

    def on_end_attack(self):
        if self.att and self.att != 114:
            self.att -= 1
            self.timer = 5
            super().on_start_attack()
            self.display = True
        else:
            self.att = 0
            super().on_end_attack()

class StormWeaver(weapons.Gun):

    def on_end_attack(self):
        if game.get_game().player.ammo_bullet[0] not in proj.AMMOS or not game.get_game().player.ammo_bullet[1]:
            super().on_end_attack()
            return
        if game.get_game().player.ammo_bullet[
            1] < constants.ULTIMATE_AMMO_BONUS and random.random() > self.ammo_save_chance + game.get_game().player.calculate_data(
                'ammo_save', False) / 100:
            game.get_game().player.ammo_bullet = (game.get_game().player.ammo_bullet[0], game.get_game().player.ammo_bullet[1] - 1)
        pj = proj.AMMOS[game.get_game().player.ammo_bullet[0]]((self.x + game.get_game().player.obj.pos[0],
                                                         self.y + game.get_game().player.obj.pos[1]),
                                                        self.rot + random.uniform(-self.precision, self.precision),
                                                        self.spd,
                                                        self.damages[damages.DamageTypes.PIERCING])
        if self.tail_col is not None:
            pj.TAIL_COLOR = self.tail_col
            pj.TAIL_SIZE = max(pj.TAIL_SIZE, self.ts)
            pj.TAIL_WIDTH = max(pj.TAIL_WIDTH, self.tw)
        pj.dmg *= .5
        pj.DELETE = False
        pj.ENABLE_IMMUNE = 3
        game.get_game().projectiles.append(pj)
        super().on_end_attack()

class Gemini(weapons.Gun):
    ATTACK_SOUND = 'attack_quickshot'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ammo = None
        self.st = 0

    def on_start_attack(self):
        if game.get_game().player.ammo_bullet[1]:
            self.ammo = game.get_game().player.ammo_bullet
            game.get_game().player.ammo_bullet = ('energy_arrow', 1)
        super().on_start_attack()
        if self.st < 0:
            beam = projectiles.Gemini(game.get_game().player.obj.pos, self.rot)
            beam.WIDTH = abs(self.st) // 2 + 10
            beam.DMG_RATE = min(2.0, .5 + abs(self.st) / 40) / 2
            game.get_game().projectiles.append(beam)

    def on_end_attack(self):
        super().on_end_attack()
        if self.ammo is not None:
            game.get_game().player.ammo_bullet = self.ammo
            self.ammo = None
        if self.cd:
            self.st = 0
        else:
            self.st -= 2
        self.cd = max(0, self.cd - 1)

    def on_idle(self):
        super().on_idle()
        self.st += 1
        if self.st >= 25:
            self.cd = min(self.cd + 1, 18)
        if self.st < -60:
            self.st += 40

class Pollutant(weapons.Bow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sk_mcd = 20
        self.vel = vector.Vector2D()

    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in proj.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[
            1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data(
                'ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        pj = proj.AMMOS[game.get_game().player.ammo[0]]((self.x + game.get_game().player.obj.pos[0],
                                                                self.y + game.get_game().player.obj.pos[1]),
                                                               self.rot + random.uniform(-self.precision, self.precision),
                                                               self.spd + proj.AMMOS[game.get_game().player.ammo[0]].SPEED,
                                                               self.damages[damages.DamageTypes.PIERCING] + proj.AMMOS[game.get_game().player.ammo[0]].DAMAGES)
        try:
            rt = vector.coordinate_rotation(*(pj.get_closest_entity()[0].obj.pos - game.get_game().player.obj.pos - (self.x, self.y)))
            self.set_rotation(rt)
            pj = proj.AMMOS[game.get_game().player.ammo[0]]((self.x + game.get_game().player.obj.pos[0],
                                                             self.y + game.get_game().player.obj.pos[1]),
                                                            rt + random.uniform(-self.precision, self.precision),
                                                            self.spd + proj.AMMOS[game.get_game().player.ammo[0]].SPEED,
                                                            self.damages[damages.DamageTypes.PIERCING] + proj.AMMOS[
                                                                game.get_game().player.ammo[0]].DAMAGES)

        except AttributeError:
            pass
        mp = vector.Vector2D() + position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())) - game.get_game().player.obj.pos
        mp /= abs(mp)
        if self.sk_cd <= 1:
            self.vel += mp * 240
        if self.tail_col is not None:
            pj.TAIL_COLOR = self.tail_col
            pj.TAIL_SIZE = max(pj.TAIL_SIZE, 3)
            pj.TAIL_WIDTH = max(pj.TAIL_WIDTH, 3)
        game.get_game().projectiles.append(pj)

    def on_idle(self):
        super().on_idle()
        self.display = True

    def update(self):
        if pg.BUTTON_LEFT not in game.get_game().get_pressed_mouse():
            self.vel += (vector.Vector2D() - (self.x, self.y)) * .02
        elif self.sk_cd > 1:
            self.sk_cd = self.sk_mcd
        super().update()
        self.set_rotation(self.rot + 15 + vector.distance(self.x, self.y) / 100)
        self.x, self.y = vector.Vector2D(dx=self.x, dy=self.y) + self.vel
        self.vel = self.vel * 10 / 13

    def on_end_attack(self):
        if not self.sk_cd:
            self.sk_cd = self.sk_mcd
        super().on_end_attack()

class EMTrackGun(weapons.Gun):
    def on_start_attack(self):
        for _ in range(8):
            super().on_start_attack()

class NewMagicWeapon(weapons.MagicWeapon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.level = 1
        self.ddata = [self.damages, 1]

    def on_special_attack(self, strike: int):
        self.damages = copy.copy(self.ddata[0])
        self.scale = self.ddata[1]
        self.ddata = [copy.copy(self.damages), 1]
        self.scale = 5 - 4 * 1.5 ** -(self.strike / 50)
        for kk in self.damages.keys():
            self.damages[kk] *= 4 - 3 * 1.2 ** -(self.strike / 50)
        self.level = int(self.scale)

    def on_charge(self):
        super().on_charge()
        self.scale = 5 - 4 * 1.5 ** -(self.strike / 50)
        self.display = True

    def on_end_attack(self):
        self.display = False
        self.scale = 1
        self.level = 1
        super().on_end_attack()

class SpeedIncreaseMagicWeapon(NewMagicWeapon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.level = 1
        self.ddata = [self.damages, 1]

    def on_special_attack(self, strike: int):
        self.damages = copy.copy(self.ddata[0])
        self.scale = self.ddata[1]
        self.ddata = [copy.copy(self.damages), 1]
        self.scale = 5 - 4 * 1.5 ** -(self.strike / 50)
        for kk in self.damages.keys():
            self.damages[kk] *= 4 - 3 * 1.2 ** -(self.strike / 50)
        self.level = int(self.scale)

    def on_charge(self):
        super().on_charge()
        self.scale = 5 - 4 * 1.5 ** -(self.strike / 50)
        self.display = True

    def on_end_attack(self):
        self.display = False
        self.scale = 1
        self.level = 1
        super().on_end_attack()

    def on_start_attack(self):
        game.get_game().player.hp_sys.effect(effects.WeakManaI([.5, 1, 3, 6][constants.DIFFICULTY], 1))
        if constants.DIFFICULTY:
            game.get_game().player.hp_sys.effect(effects.ManaDrain([0, 3, 6, 10][constants.DIFFICULTY], 1))
        if game.get_game().player.mana < round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1):
            self.timer = 0
            return
        if self.sk_cd:
            self.timer = 0
            return
        self.sk_cd = self.sk_mcd
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        pj = self.projectile((self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1]),
                            self.rot)
        pj.obj.MASS /= self.scale ** 1.5
        game.get_game().projectiles.append(pj)
        game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)

class MysterySwiftswordSpear(weapons.Spear):
    def on_start_attack(self):
        super().on_start_attack()
        game.get_game().projectiles.append(projectiles.MysterySwiftsword(game.get_game().player.obj.pos,
                                                                         self.rot))

class IntestinalSword(weapons.Blade):
    def on_start_attack(self):
        super().on_start_attack()
        for e in game.get_game().entities:
            if vector.cartesian_to_polar(e.obj.pos[0] - self.x - game.get_game().player.obj.pos[0],
                                          e.obj.pos[1] - self.y - game.get_game().player.obj.pos[1])[1] < 500:
                r = random.randint(0, 360)
                ax, ay = vector.polar_to_cartesian(r, -150)
                game.get_game().projectiles.append(projectiles.IntestinalSword(e.obj.pos + (ax, ay), r))

class Proof(weapons.Blade):
    def on_attack(self):
        self.ENABLE_IMMUNE = False
        super().on_attack()
        self.cutting_effect(4, (200, 100, 255), (100, 50, 150))
        if pg.BUTTON_LEFT in game.get_game().get_pressed_mouse():
            self.timer = 4
            self.rot_speed *= -1
        if self.rot_speed > 0:
            mr, _ = vector.cartesian_to_polar(*position.relative_position(position.real_position(
                game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
            self.set_rotation(mr - self.st_pos // 2)

class Hell(weapons.Blade):
    def on_attack(self):
        super().on_attack()
        self.cutting_effect(10, (255, 100, 100), (255, 255, 100))

    def on_start_attack(self):
        super().on_start_attack()
        rot = vector.coordinate_rotation(*(-game.get_game().player.obj.pos +
                                           position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())) ))
        game.get_game().projectiles.append(projectiles.Hell(game.get_game().player.obj.pos, rot))

class EntrophicSword(weapons.Blade):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proj = None

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(10, (0, 0, 0), (50, 50, 50))

    def update(self):
        super().update()
        if self.proj is not None:
            self.proj.obj.pos = (game.get_game().player.obj.pos + self.proj.obj.pos * 4) / 5

    def on_start_attack(self):
        if not game.get_game().player.inventory.is_enough(inventory.ITEMS['dark_energy'], 30):
            self.timer = 0
            return
        game.get_game().player.inventory.remove_item(inventory.ITEMS['dark_energy'], 30)
        super().on_start_attack()
        mr = vector.coordinate_rotation(*(- game.get_game().player.obj.pos+
                                          position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
                                          ))
        self.proj = projectiles.EntrophicSword(game.get_game().player.obj.pos, mr)
        game.get_game().projectiles.append(self.proj)


class Observe(weapons.Blade):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sk_mcd = 100

    def on_start_attack(self):
        super().on_start_attack()
        if not self.sk_cd:
            self.sk_cd = self.sk_mcd
            for e in game.get_game().entities:
                if vector.cartesian_to_polar(e.obj.pos[0] - self.x - game.get_game().player.obj.pos[0],
                                              e.obj.pos[1] - self.y - game.get_game().player.obj.pos[1])[1] < 1200:
                    r = random.randint(0, 360)
                    ax, ay = vector.polar_to_cartesian(r, -1000)
                    game.get_game().projectiles.append(projectiles.Observe(e.obj.pos + (ax, ay), r))
            self.rotate(self.rot_speed * 2)
            self.cool += self.at_time
            self.timer = 0

class GrowthEater(weapons.LifeDevourer):
    def update(self):
        self.sk_mcd = 80
        super().update()
        if not self.timer and not self.cool and pg.K_q in game.get_game().get_keys() and not self.sk_cd:
            super().attack()
            self.sk_cd = self.sk_mcd
            for i in range(25):
                ax, ay = vector.rotation_coordinate(random.randint(0, 360))
                x, y = game.get_game().player.obj.pos[0] + ax * 600, game.get_game().player.obj.pos[1] + ay * 600
                pj = projectiles.GrowthEater((x, y), vector.coordinate_rotation(-ax, -ay) + random.randint(-5, 5))
                pj.DURATION = 16 + i // 2
                pj.WIDTH = 20
                game.get_game().projectiles.append(pj)

    def on_start_attack(self):
        super().on_start_attack()
        for i in range(random.randint(1, 3)):
            ax, ay = vector.rotation_coordinate(random.randint(0, 360))
            x, y = game.get_game().player.obj.pos[0] + ax * 600, game.get_game().player.obj.pos[1] + ay * 600
            pj = projectiles.GrowthEater((x, y), vector.coordinate_rotation(-ax, -ay) + random.randint(-2, 2))
            game.get_game().projectiles.append(pj)
        self.cutting_effect(6, (200, 255, 200), (0, 50, 0))

class AncientSwiftsword(weapons.SweepWeapon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cec = -1
        self.ct = 0

    def on_start_attack(self, *args):
        self.cec *= -1
        if self.ct == 2:
            if random.randint(0, 1):
                self.cec *= -1
            mp = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
            self.set_rotation(vector.coordinate_rotation(*mp))
            game.get_game().projectiles.append(projectiles.AncientSwiftsword(game.get_game().player.obj.pos, self.rot))
        self.ct = (self.ct + 1) % 3
        super().on_start_attack(rr=self.cec)
        if self.ct == 0:
            self.rot_speed *= 2

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(8, (50, 200, 255), (0, 255, 255))

class Confuse(weapons.Blade):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.td = 1

    def on_end_attack(self):
        super().on_end_attack()
        for k in self.damages.keys():
            self.damages[k] /= self.td
        self.td = 1

    def on_attack(self):
        super().on_attack()
        if self.x > 0:
            self.x = max(0, self.x - 10)
        else:
            self.x = min(0, self.x + 10)
        if self.y > 0:
            self.y = max(0, self.y - 10)
        else:
            self.y = min(0, self.y + 10)
        self.scale = max(1.0, self.scale / 1.01) if self.scale > 1.1 else 1

    def on_start_attack(self):
        for k in self.damages.keys():
            self.damages[k] /= self.td
        self.td = 1
        super().on_start_attack()
        f = random.random()
        if f < .01:
            game.get_game().player.hp_sys.hp -= game.get_game().player.hp_sys.max_hp * .999
        elif f < .06:
            game.get_game().player.hp_sys.damage(self.damages[damages.DamageTypes.PHYSICAL] * game.get_game().player.attack *
                                                 game.get_game().player.attacks[0], damages.DamageTypes.TOUCHING)
        elif f < .2:
            self.x = random.randint(-300, 300)
            self.y = random.randint(-300, 300)
        elif f < .25:
            self.x = random.randint(-3000, 3000)
            self.y = random.randint(-3000, 3000)
        elif f < .3:
            self.td = 0.001
        elif f < .45:
            self.td = .5
        elif f < .5:
            game.get_game().player.hp_sys.damage(self.damages[damages.DamageTypes.PHYSICAL] * game.get_game().player.attack *
                                                 game.get_game().player.attacks[0], damages.DamageTypes.TOUCHING)
            self.td = 3
        elif f < .6:
            self.td = 2
        elif f < .8:
            mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            self.x = mx - game.get_game().player.obj.pos[0]
            self.y = my - game.get_game().player.obj.pos[1]
        elif f < .9:
            game.get_game().player.hp_sys.shields.append(('confuse', 200))
            self.td = 1
        elif f < .98:
            self.scale = 3
        else:
            self.scale = 10
            self.td = 30
        for k in self.damages.keys():
            self.damages[k] *= self.td

class WVector(weapons.Blade):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.opp = False
        self.tick = 0
        self.lr = 0
        self.dd = 0

    def on_start_attack(self):
        super().on_start_attack()
        self.opp = not self.opp
        self.rot_speed = 1

    def damage(self):

        if self.rot_speed > 0:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed + 1))
        else:
            rot_range = range(int(self.rot - self.rot_speed), int(self.rot + self.rot_speed - 1), -1)
        for e in game.get_game().entities:
            dps = e.obj.pos
            px = dps[0] - self.x - game.get_game().player.obj.pos[0]
            py = dps[1] - self.y - game.get_game().player.obj.pos[1]
            r = int(vector.coordinate_rotation(px, py)) % 360
            if r in rot_range or r + 360 in rot_range or (
                    self.double_sided and ((r + 180) % 360 in rot_range or r + 180 in rot_range)):
                if vector.distance(px, py) < self.dd * self.scale + (
                        (e.img.get_width() + e.img.get_height()) // 2 if e.img is not None else 10) and not e.hp_sys.is_immune:
                    for t, d in self.damages.items():
                        e.hp_sys.damage(d * game.get_game().player.attack ** .3 * game.get_game().player.attacks[self.DMG_AS_IDX] ** .3, t)
                    e.hp_sys.enable_immune(.3)
                    self.dd = max(self.dd, 20)
                    if not e.hp_sys.is_immune:
                        rf = vector.coordinate_rotation(px + self.x, py + self.y)
                        e.obj.apply_force(vector.Vector(rf, min(self.knock_back * 120000 / e.obj.MASS, e.obj.MASS * 24)
                        if self.knock_back * 60000 < e.obj.MASS or constants.DIFFICULTY <= 1 else
                        min(self.knock_back * 600000 / e.obj.MASS, e.obj.MASS * 24)))
                    if 'matters_touch' in game.get_game().player.accessories:
                        e.obj.MASS *= 1.01
                    if 'grasp_of_the_infinite_corridor' in game.get_game().player.accessories:
                        if not e.IS_MENACE and not e.VITAL:
                            e.hp_sys.damage(e.hp_sys.max_hp / 10, damages.DamageTypes.THINKING)
                            if random.randint(0, 10) == 0:
                                e.hp_sys.hp = 0
                        else:
                            e.hp_sys.damage(max(e.hp_sys.max_hp / 1000, 10000), damages.DamageTypes.THINKING)
                    if self.ENABLE_IMMUNE:
                        if constants.DIFFICULTY > 1:
                            e.hp_sys.enable_immune()

    def on_attack(self):
        if self.rot_speed == 0:
            self.rot_speed = 1
        super().on_attack()

    def update(self):
        self.damages[damages.DamageTypes.PHYSICAL] = round(120 * (1 - math.e ** (-self.dd / 1500))) * 5
        self.tick += 1
        self.rot = vector.coordinate_rotation(*position.relative_position(position.real_position(
            game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        self.set_rotation(self.rot)
        ar = self.rot - self.lr
        if ar > 180:
            ar -= 360
        elif ar < -180:
            ar += 360
        self.rot_speed = ar if ar != 0 else 1
        self.rot_speed = int(self.rot_speed * 100 / game.get_game().clock.last_tick)
        self.lr = self.rot
        td = max(0, self.rot_speed * 15 + 120)
        if td > self.dd:
            self.dd = (self.dd * 8 + td) / 9
        else:
            self.dd = self.dd * 25 // 26
        if self.opp and self.tick % 50 == 1:
            if not game.get_game().player.inventory.is_enough(inventory.ITEMS['dark_energy']):
                self.opp = False
                return
            else:
                game.get_game().player.inventory.remove_item(inventory.ITEMS['dark_energy'])
        if not self.opp:
            self.dd = 0
            self.rot_speed = 1
            super().update()
            return
        self.display = True
        cut_effects.cut_eff(game.get_game().displayer.canvas, int(20 / game.get_game().player.get_screen_scale()),
                  *position.displayed_position(game.get_game().player.obj.pos),
                  *position.displayed_position(game.get_game().player.obj.pos + vector.Vector2D(self.rot, self.dd)),
                            (20, 20, 80))
        super().update()
        self.damage()



class AbyssRanseur(weapons.Spear):
    def on_start_attack(self):
        super().on_start_attack()
        game.get_game().projectiles.append(projectiles.AbyssRanseur(game.get_game().player.obj.pos, self.rot))

class ArcSpear(weapons.Spear):
    def on_start_attack(self):
        super().on_start_attack()
        game.get_game().projectiles.append(projectiles.ArcSpear(game.get_game().player.obj.pos, self.rot))

class Iceberg(weapons.Blade):
    def on_attack(self):
        super().on_attack()
        self.cutting_effect(4, (0, 255, 255), (100, 255, 255))
        if (self.at_time - self.timer) % 5 == 2:
            mr = vector.coordinate_rotation(*(-game.get_game().player.obj.pos + position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
            game.get_game().projectiles.append(projectiles.Iceberg(game.get_game().player.obj.pos, mr))

class Insights(weapons.Blade):
    def on_attack(self):
        super().on_attack()
        self.cutting_effect(4, (255, 255, 255), (0, 255, 255))
        mx, my = vector.Vector2D(0, 0, *position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))) - game.get_game().player.obj.pos
        self.x = self.x * 9 // 10 + mx // 10
        self.y = self.y * 9 // 10 + my // 10
        if self.timer % 2 == 0:
            game.get_game().projectiles.append(projectiles.Insights(game.get_game().player.obj.pos + (self.x, self.y), self.rot))

    def on_idle(self):
        super().on_idle()
        self.x //= 2
        self.y //= 2

class EarthsTwinblade(weapons.ThiefDoubleKnife):
    DESC = {
        'none': 'Nothing special...',
        'forest': 'Releases strong pulse hitting enemies and knocks them back',
        'desert': 'Releases strong slash and breaks enemies\' defense',
        'snowland': 'Releases phantoms and freeze enemies',
        'hell': 'Releases cutting pulse burning enemies',
        'heaven': 'Releases strong beams to pierce through enemies',
        'ancient': 'Releases shadows of sword'
    }

    CDS = {
        'none': 999,
        'forest': 30,
        'desert': 20,
        'snowland': 15,
        'hell': 45,
        'heaven': 60,
        'ancient': 10,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attr = 'none'

    def on_start_attack(self):
        super().on_start_attack()
        if self.attr == 'none':
            self.timer = 0
            self.on_end_attack()
            self.sk_cd = self.sk_mcd

    def on_special_attack(self, strike: int):
        if game.get_game().get_biome() in self.DESC:
            self.attr = game.get_game().get_biome()
            it = inventory.ITEMS['earths_twinblade']
            ss = 'ability: '
            it.desc = it.desc.split('ability: ')[0] + ss + self.DESC[self.attr]
            self.sk_mcd = self.CDS[self.attr]
            self.sk_cd = self.sk_mcd


WEAPONS = {
    'e_wooden_sword': weapons.Blade(name='e wooden sword', damages={damages.DamageTypes.PHYSICAL: 55}, kb=6,
                                    img='items_weapons_e_wooden_sword', speed=3, at_time=5, rot_speed=40,
                                    st_pos=150),
    'feather_sword': FeatherSword(name='feather sword', damages={damages.DamageTypes.PHYSICAL: 40}, kb=2,
                                    img='items_weapons_feather_sword', speed=0, at_time=3, rot_speed=100,
                                    st_pos=200),
    'lychee_sword': weapons.Blade(name='lychee sword', damages={damages.DamageTypes.PHYSICAL: 90}, kb=10,
                                   img='items_weapons_lychee_sword', speed=1, at_time=6, rot_speed=60, st_pos=200),
    'lychee_pike': weapons.Spear(name='lychee pike', damages={damages.DamageTypes.PHYSICAL: 110}, kb=12,
                                 img='items_weapons_lychee_pike', speed=3, at_time=8, forward_speed=30, st_pos=150,
                                 auto_fire=True),
    'hidden_sword': weapons.Blade(name='hidden sword', damages={damages.DamageTypes.PHYSICAL: 380}, kb=10,
                                   img='items_weapons_hidden_sword', speed=7, at_time=3, rot_speed=150, st_pos=200),
    'heaven_trident': weapons.Spear(name='heaven trident', damages={damages.DamageTypes.PHYSICAL: 220}, kb=15,
                                     img='items_weapons_heaven_trident', speed=2, at_time=12, forward_speed=30, st_pos=150,
                                    auto_fire=True),
    'corrupt_sword': CorruptSword(name='corrupt sword', damages={damages.DamageTypes.PHYSICAL: 160}, kb=10,
                                  img='items_weapons_corrupt_sword', speed=1, at_time=7, rot_speed=50, st_pos=200
                                  ),
    'arc_spear': ArcSpear(name='arc spear', damages={damages.DamageTypes.PHYSICAL: 180}, kb=12,
                           img='items_weapons_arc_spear', speed=2, at_time=5, forward_speed=70, st_pos=250, auto_fire=True),
    'iceberg': Iceberg(name='iceberg', damages={damages.DamageTypes.PHYSICAL: 140}, kb=8,
                       img='items_weapons_iceberg', speed=2, at_time=7, rot_speed=40, st_pos=120),
    'gauss_dagger': GaussDagger(name='gauss dagger', damages={damages.DamageTypes.PHYSICAL: 120}, kb=5,
                                img='items_weapons_gauss_dagger', speed=1, at_time=3, rot_speed=50, st_pos=80),
    'soulid_dagger': weapons.Blade(name='soulid dagger', damages={damages.DamageTypes.PHYSICAL: 500}, kb=8,
                                    img='items_weapons_soulid_dagger', speed=3, at_time=3, rot_speed=80, st_pos=150),
    'scar_dagger': ScarDagger(name='scar dagger', damages={damages.DamageTypes.PHYSICAL: 55}, kb=3,
                              img='items_weapons_scar_dagger', speed=1, at_time=2, rot_speed=120, st_pos=100,
                              ),
    'chaos_dagger': ChaosDagger(name='chaos_dagger', damages={damages.DamageTypes.PHYSICAL: 2000}, kb=10,
                                img='items_weapons_chaos_dagger', speed=2, at_time=2, rot_speed=160, st_pos=250,
                                ),
    'hightech_steel_sword': HighTechMetalSword(name='hightech steel sword', damages={damages.DamageTypes.PHYSICAL: 450}, kb=15,
                                               img='items_weapons_hightech_steel_sword', speed=1, at_time=5, rot_speed=80, st_pos=280,
                                                ),
    'clear_icy_prism': weapons.Blade(name='clear icy prism', damages={damages.DamageTypes.PHYSICAL: 360}, kb=15,
                                      img='items_weapons_clear_icy_prism', speed=2, at_time=8, rot_speed=25, st_pos=120),
    'turbid_icy_prism': weapons.Blade(name='turbid icy prism', damages={damages.DamageTypes.PHYSICAL: 240}, kb=10,
                                       img='items_weapons_turbid_icy_prism', speed=1, at_time=5, rot_speed=40, st_pos=120),
    'wheel_frogile_sword': WheelFrogileSword(name='wheel frogile sword', damages={damages.DamageTypes.PHYSICAL: 180}, kb=15,
                                              img='items_weapons_wheel_frogile_sword', speed=1, at_time=6, rot_speed=50, st_pos=180),
    'purple_clay_broad_blade': PurpleClayBroadBlade(name='purple clay broad blade', damages={damages.DamageTypes.PHYSICAL: 110}, kb=15,
                                                    img='items_weapons_purple_clay_broad_blade', speed=1, at_time=8,
                                                    rot_speed=40, st_pos=150),
    'starnight_broadsword': weapons.ComplexWeapon(name='starnight broadsword', damages_rot={damages.DamageTypes.PHYSICAL: 200},
                                                   damages_spear={damages.DamageTypes.PHYSICAL: 400}, kb=30, img='items_weapons_starnight_broadsword',
                                                  speed=1, at_time_rot=10, at_time_spear=15, rot_speed=30, st_pos_sweep=200, forward_speed=30,
                                                  st_pos_spear=300, auto_fire=True, combat=[1, 1, 1, 0], sweep_type=weapons.Blade),
    'wingblade': WingBlade(name='wingblade', damages={damages.DamageTypes.PHYSICAL: 500}, kb=10,
                            img='items_weapons_wingblade', speed=1, at_time=12, rot_speed=20, st_pos=150,),
    'poise_blade': PoiseBlade(name='poise blade', damages={damages.DamageTypes.PHYSICAL: 150}, kb=12,
                              img='items_weapons_poise_blade', speed=4, at_time=5, rot_speed=70, st_pos=200),
    'mystery_sword': weapons.Blade('mystery sword', {damages.DamageTypes.PHYSICAL: 190}, 20,
                                   'items_weapons_mystery_sword', 0, 7, 40, 180),
    'mystery_spear': weapons.Spear('mystery spear', {damages.DamageTypes.PHYSICAL: 100}, 35,
                                   'items_weapons_mystery_spear', 0, 4, 70, 180),
    'mystery_swiftsword': weapons.ComplexWeapon(name='mystery swiftsword', damages_rot={damages.DamageTypes.PHYSICAL: 60},
                                                damages_spear={damages.DamageTypes.PHYSICAL: 100}, kb=5, img='items_weapons_mystery_swiftsword',
                                                speed=1, at_time_rot=5, at_time_spear=8, rot_speed=70, st_pos_sweep=250, forward_speed=50,
                                                st_pos_spear=300, auto_fire=True, combat=[1, 1, 1, 0], sweep_type=weapons.Blade,
                                                spear_type=MysterySwiftswordSpear),
    'e_muramasa': Muramasa(name='e muramasa', damages={damages.DamageTypes.PHYSICAL: 360}, kb=10,
                          img='items_weapons_e_muramasa', speed=1, at_time=8, rot_speed=50, st_pos=250,
                           _type=1),
    'celestial_piercer': CelestialPiercer(name='celestial piercer', damages={damages.DamageTypes.PHYSICAL: 400}, kb=15,
                                          img='items_weapons_celestial_piercer', speed=3, at_time=5, st_pos=200,
                                          forward_speed=60, auto_fire=True),
    'substance_rend_sword': weapons.Blade('substance rend sword', {damages.DamageTypes.PHYSICAL: 1000}, 35,
                                          'items_weapons_substance_rend_sword', speed=1, at_time=4, st_pos=300,
                                          rot_speed=90),

    'proof': Proof(name='proof', damages={damages.DamageTypes.PHYSICAL: 60}, kb=2, img='items_weapons_proof',
                   speed=8, at_time=2, rot_speed=30, st_pos=15),
    'observe': Observe(name='observe', damages={damages.DamageTypes.PHYSICAL: 70}, kb=2, img='items_weapons_observe',
                       speed=1, at_time=8, rot_speed=40, st_pos=240),
    'intestinal_sword': IntestinalSword(name='intestinal sword', damages={damages.DamageTypes.PHYSICAL: 120}, kb=10,
                                        img='items_weapons_intestinal_sword', speed=1, at_time=6, rot_speed=40, st_pos=150),

    'critical_thinking': weapons.Blade(name='critical thinking', damages={damages.DamageTypes.PHYSICAL: 340}, kb=15,
                                       img='items_weapons_critical_thinking', speed=1, at_time=15, rot_speed=20, st_pos=180),

    'primordial_monument': weapons.Blade(name='primordial monument', damages={damages.DamageTypes.PHYSICAL: 260}, kb=20,
                                         img='items_weapons_primordial_monument', speed=2, at_time=4, rot_speed=100, st_pos=270),
    'ender_monument': weapons.Blade(name='ender monument', damages={damages.DamageTypes.PHYSICAL: 390}, kb=30,
                                         img='items_weapons_ender_monument', speed=2, at_time=6, rot_speed=666, st_pos=270),

    'longer_intestine': weapons.Whip(name='longer intestine', damages={damages.DamageTypes.PHYSICAL: 480}, kb=30,
                                     img='items_weapons_longer_intestine', speed=10, at_time=30, length=50,
                                     size=60, auto_fire=True),
    'e_whip': weapons.Whip(name='e whip', damages={damages.DamageTypes.PHYSICAL: 400}, kb=10,
                           img='items_weapons_e_whip', speed=2, at_time=20, length=20, size=40, auto_fire=True),

    'destroy': Destroy('destroy', {damages.DamageTypes.PHYSICAL: 120}, 35,
                       'items_weapons_destroy', 15, 25, 10, 150),
    'generate': Generate('generate', {damages.DamageTypes.PHYSICAL: 40}, 15,
                         'items_weapons_generate', 5, 10, 50, 300),
    'ancient_swiftsword': AncientSwiftsword('ancient swiftsword', {damages.DamageTypes.PHYSICAL: 110}, 20,
                                            'items_weapons_ancient_swiftsword', 2, 5, 50, 130),
    'feather_feather_sword': FeatherFeatherSword(name='feather feather sword', damages={damages.DamageTypes.PHYSICAL: 100}, kb=10,
                                                  img='items_weapons_feather_feather_sword', speed=2, at_time=3, rot_speed=80,
                                                  st_pos=180),
    'confuse': Confuse('confuse', {damages.DamageTypes.PHYSICAL: 55}, 10,
                       'items_weapons_confuse', 2, 6, 60, 250),

    'e_wooden_bow': weapons.Bow(name='e wooden bow', damages={damages.DamageTypes.PIERCING: 45}, kb=4,
                                img='items_weapons_e_wooden_bow', speed=2, at_time=5, projectile_speed=300,
                                auto_fire=True, precision=2),
    'hand_of_social': weapons.Bow(name='hand of social', damages={damages.DamageTypes.PIERCING: 240}, kb=3,
                                  img='items_null', speed=5, at_time=30, projectile_speed=800, precision=0),
    'lychee_bow': LycheeBow(name='lychee bow', damages={damages.DamageTypes.PIERCING: 60}, kb=3,
                             img='items_weapons_lychee_bow', speed=3, at_time=6, projectile_speed=500,
                             auto_fire=True, precision=1, tail_col=(255, 100, 200)),
    'pollutant': Pollutant(name='pollutant', damages={damages.DamageTypes.PIERCING: 180}, kb=15,
                           img='items_weapons_pollutant', speed=3, at_time=6, projectile_speed=900,
                           auto_fire=True, precision=0, tail_col=(200, 255, 100)),
    'em_trackgun': EMTrackGun(name='em trackgun', damages={damages.DamageTypes.PIERCING: 20}, kb=3,
                              img='items_weapons_em_trackgun', speed=8, at_time=18, projectile_speed=2000,
                              auto_fire=True, precision=5),
    'storm_weaver': StormWeaver(name='storm weaver', damages={damages.DamageTypes.PIERCING: 90}, kb=10,
                                img='items_weapons_storm_weaver', speed=3, at_time=8, projectile_speed=1000,
                                auto_fire=True, precision=2),
    'ion_beam': weapons.LazerGun(name='ion beam', damages={damages.DamageTypes.PIERCING: 250}, kb=10,
                                 img='items_weapons_ion_beam', speed=10, at_time=5, projectile_speed=500,
                                 auto_fire=True, lazer_col=(200, 200, 200), lazer_width=60),
    'bloody_rain': BloodyRain('bloody_rain', {damages.DamageTypes.PIERCING: 550}, 1, 'items_weapons_bloody_rain',
                              3, 4, 400, True, precision=3),
    'ceremony': weapons.Bow(name='ceremony', damages={damages.DamageTypes.PIERCING: 220}, kb=30,
                            img='items_weapons_ceremony', speed=2, at_time=5, projectile_speed=4000,
                            auto_fire=True, precision=1),
    'skyfire': weapons.LazerGun(name='skyfire', damages={damages.DamageTypes.PIERCING: 300}, kb=30,
                                img='items_weapons_skyfire', speed=1, at_time=10, projectile_speed=2000,
                                auto_fire=True, lazer_len=2, lazer_width=10, lazer_col=(200, 200, 200)),
    'e_pistol': weapons.Gun(name='e pistol', damages={damages.DamageTypes.PIERCING: 300}, kb=10,
                             img='items_weapons_e_pistol', speed=9, at_time=9, projectile_speed=1200,
                             auto_fire=True, precision=0),
    'sniper': weapons.Gun(name='sniper', damages={damages.DamageTypes.PIERCING: 650}, kb=30,
                          img='items_weapons_sniper', speed=8, at_time=30, projectile_speed=1500,
                          auto_fire=True, precision=0),
    'heaven_shotgun': weapons.Shotgun('heaven shotgun', {damages.DamageTypes.PIERCING: 110}, 0.1, 'items_weapons_shotgun',
                            3, 8, 1000, auto_fire=True, precision=12),
    'purple_clay_kuangkuang': weapons.KuangKuangKuang(name='purple clay kuangkuang', damages={damages.DamageTypes.PIERCING: 18}, kb=1,
                                               img='items_weapons_purple_clay_kuangkuang', speed=0, at_time=1,
                                              projectile_speed=100, auto_fire=True, precision=2, ammo_save_chance=1 / 3),
    'lychee_twinblade': weapons.ThiefDoubleKnife(name='lychee twinblade', damages={damages.DamageTypes.PIERCING: 150}, kb=8,
                                                 img='items_weapons_lychee_blade', speed=1, at_time=6,
                                                 rot_speed=30, st_pos=120, throw_interval=12, power=3000,
                                                  dcols=((255, 200, 255), (50, 0, 50))),
    'earths_twinblade': EarthsTwinblade(name='earths twinblade', damages={damages.DamageTypes.PIERCING: 350}, kb=14,
                                          img='items_weapons_earths_blade', speed=1, at_time=8,
                                          rot_speed=40, st_pos=200, throw_interval=999, power=6000,
                                          dcols=((200, 255, 100), (50, 100, 50))),
    'poise_bow': weapons.Bow('poise bow', {damages.DamageTypes.PIERCING: 80}, 10,
                             'items_weapons_poise_bow', 1, 3, 300, True, precision=5,
                             tail_col=(200, 255, 100)),
    'poise_submachine_gun': weapons.Gun('poise submachine gun', {damages.DamageTypes.PIERCING: 25}, 5,
                                          'items_weapons_poise_submachine_gun', 1, 1, 1200,
                                        True, 3, tail_col=(200, 255, 100), ammo_save_chance=1 / 4),
    'supernova': SuperNova(name='supernova', damages={damages.DamageTypes.PIERCING: 90}, kb=20,
                           img='items_weapons_supernova', speed=20, at_time=3, projectile_speed=500,
                           auto_fire=True, precision=0, tail_col=(0, 255, 255)),
    'gandiva': Gandiva(name='gandiva', damages={damages.DamageTypes.PIERCING: 125}, kb=10,
                       img='items_weapons_gandiva', speed=6, at_time=2, projectile_speed=1000,
                       auto_fire=True, precision=10),
    'ullr_bow': UllrBow(name='ullr bow', damages={damages.DamageTypes.PIERCING: 720}, kb=10,
                        img='items_weapons_ullr_bow', speed=3, at_time=10, projectile_speed=1000,
                        auto_fire=True, precision=0),
    'gravity_slingshot': GravitySlingshot(name='gravity slingshot', damages={damages.DamageTypes.PIERCING: 1200},
                                          kb=0, img='items_weapons_gravity_slingshot', speed=15, at_time=8,
                                           projectile_speed=1000, auto_fire=True, precision=0),
    'gemini': Gemini(name='gemini', damages={damages.DamageTypes.PIERCING: 240}, kb=10,
                     img='items_weapons_gemini', speed=18, at_time=4, projectile_speed=1200,
                     auto_fire=True, precision=0),
    'dark_cannon': DarkCannon(name='dark cannon', damages={damages.DamageTypes.PIERCING: 350}, kb=12,
                               img='items_weapons_dark_cannon', speed=12, at_time=15, projectile_speed=1000,
                               auto_fire=True, precision=0),
    'eden': weapons.Gun(name='eden', damages={damages.DamageTypes.PIERCING: 6500}, kb=50,
                         img='items_weapons_eden', speed=120, at_time=30, projectile_speed=300,
                         auto_fire=True, precision=0),
    'wierswin': WierSwin(name='wierswin', damages={damages.DamageTypes.PIERCING: 550}, kb=10,
                         img='items_weapons_wierswin', speed=15, at_time=3, projectile_speed=1500,
                         auto_fire=True, precision=2),


    'e_wooden_wand': weapons.MagicWeapon(name='e wooden wand', damages={damages.DamageTypes.MAGICAL: 40}, kb=2,
                                         img='items_weapons_e_wooden_wand', speed=1, at_time=6,
                                         projectile=projectiles.EWoodenWand, mana_cost=5, auto_fire=True,
                                         spell_name='Life Growth'),
    'lychee_wand': weapons.MagicWeapon(name='lychee wand', damages={damages.DamageTypes.MAGICAL: 42}, kb=0,
                                        img='items_weapons_lychee_wand', speed=1, at_time=9,
                                        projectile=projectiles.LycheeWand, mana_cost=15, auto_fire=True,
                                        spell_name='Lychee Circle'),
    'lychee_spike': NewMagicWeapon(name='lychee spike', damages={damages.DamageTypes.MAGICAL: 550}, kb=0,
                                   img='items_weapons_lychee_spike', speed=1, at_time=25,
                                   projectile=projectiles.LycheeSpike, mana_cost=30, auto_fire=True,
                                   spell_name='Lychee Spike'),
    'brainstorm': SpeedIncreaseMagicWeapon(name='brainstorm', damages={damages.DamageTypes.MAGICAL: 280}, kb=0,
                                           img='items_weapons_brainstorm', speed=15, at_time=5,
                                           projectile=projectiles.Brainstorm, mana_cost=45, auto_fire=True,
                                           spell_name='Brainstorm'),
    'poison_needle': SpeedIncreaseMagicWeapon(name='poison needle', damages={damages.DamageTypes.MAGICAL: 180}, kb=0,
                                               img='items_weapons_poison_needle', speed=3, at_time=3,
                                               projectile=projectiles.PoisonNeedle, mana_cost=12, auto_fire=True,
                                               spell_name='Poison Needle'),
    'starry_night': weapons.MagicWeapon(name='starry night', damages={damages.DamageTypes.MAGICAL: 900}, kb=0,
                                         img='items_weapons_starry_night', speed=15, at_time=10,
                                         projectile=projectiles.StarryNight, mana_cost=120, auto_fire=True,
                                         spell_name='Starry Night'),
    'wingknock': weapons.MagicWeapon(name='wingknock', damages={damages.DamageTypes.MAGICAL: 1800}, kb=0,
                                      img='items_weapons_wingknock', speed=20, at_time=5,
                                      projectile=projectiles.WingKnock, mana_cost=100, auto_fire=True,
                                      spell_name='Wingknock'),
    'nightmare_gaze': weapons.MagicWeapon(name='nightmare gaze', damages={damages.DamageTypes.MAGICAL: 3000}, kb=0,
                                          img='items_weapons_nightmare_gaze', speed=80, at_time=5,
                                          projectile=projectiles.NightmareGaze, mana_cost=450, auto_fire=True,
                                          spell_name='Nightmare Gaze'),
    'organ_wand': weapons.MagicWeapon(name='organ wand', damages={damages.DamageTypes.MAGICAL: 900}, kb=0,
                                       img='items_weapons_organ_wand', speed=4, at_time=5,
                                       projectile=projectiles.OrganWand, mana_cost=50, auto_fire=True,
                                       spell_name='Quick Organ'),
    'nyxs_dim_star_wand': weapons.MagicWeapon(name='nyxs dim star wand', damages={damages.DamageTypes.MAGICAL: 1000}, kb=0,
                                               img='items_weapons_nyxs_dim_star_wand', speed=9, at_time=9,
                                               projectile=projectiles.DimStar, mana_cost=200, auto_fire=True,
                                               spell_name='The Dim Star'),
    'merlins_wand': weapons.MagicWeapon(name='merlins wand', damages={damages.DamageTypes.MAGICAL: 650}, kb=0,
                                        img='items_weapons_merlins_wand', speed=12, at_time=16,
                                        projectile=projectiles.MerlinWand, mana_cost=350, auto_fire=True,
                                        spell_name='Merlin\'s Talent'),
    'merlins_great_wand': weapons.MagicSet(name='merlins great wand', img_index='merlins_great_wand', element_feature=lambda w: w.name in ['merlins_wand'],
                                           spell_name='Merlin\'s Great Wand'),

    'wooden_flute': weapons.PoetWeapon(name='wooden flute', damages={damages.DamageTypes.OCTAVE: 90}, kb=2,
                                       img='items_weapons_wooden_flute', speed=0, at_time=5, projectile=projectiles.WoodenFlute,
                                       gains=[effects.OctLimitlessI, effects.OctSpeedI], mana_cost=2, inspiration_cost=60,
                                       auto_fire=True, back_rate=.4, song='sanctuary', instrument='flute'),
    'the_roving_chord': weapons.PoetWeapon(name='the roving chord', damages={damages.DamageTypes.OCTAVE: 60}, kb=2,
                                           img='items_weapons_the_roving_chord', speed=0, at_time=4, projectile=projectiles.TheRovingChord,
                                           gains=[effects.OctSpeedII, effects.OctLuckyI], mana_cost=8, inspiration_cost=100,
                                            auto_fire=True, back_rate=.3, song='sanctuary', instrument='ukulele'),

    'talent_fruit': weapons.PriestHealer(name='talent fruit', amount=50, kb=3, img='items_weapons_talent_fruit',
                                         speed=200, at_time=50, mana_cost=20, karma_gain=400, auto_fire=False,
                                         spell_name='Talent Fruit'),
    'holy_condense_wand': weapons.PriestWeapon(name='holy condense wand', damages={damages.DamageTypes.HALLOW: 120}, kb=0,
                                               img='items_weapons_holy_condense_wand', speed=3, at_time=8, projectile=projectiles.HolyCondense,
                                               mana_cost=12, maximum_multiplier=3.0, auto_fire=True, spell_name='Holy Condense'),

    'lost__growth_eater': GrowthEater(name='lost  growth eater', damages={damages.DamageTypes.PHYSICAL: 130}, kb=10,
                                      img='items_weapons_life_devourer', speed=2, at_time=7, rot_speed=40,
                                      st_pos=180),
    'lost__star_broadsword': weapons.Blade(name='lost  star broadsword', damages={damages.DamageTypes.PHYSICAL: 280}, kb=1,
                                           img='items_weapons_galaxy_broadsword', speed=1, at_time=5, rot_speed=50,
                                           st_pos=150),
    'e_galaxy_broadsword': weapons.GalaxyBroadsword(name='e galaxy broadsword', damages={damages.DamageTypes.PHYSICAL: 2500}, kb=10,
                                                    img='items_weapons_galaxy_broadsword', speed=1, at_time=5, rot_speed=50,
                                                    st_pos=150),

    'abyss_ranseur': AbyssRanseur(name='abyss ranseur', damages={damages.DamageTypes.PHYSICAL: 400}, kb=50,
                                   img='items_weapons_abyss_ranseur', speed=2, at_time=6, forward_speed=80,
                                   st_pos=300, auto_fire=True),
    'abyss_gaze': AbyssGaze(name='abyss gaze', damages={damages.DamageTypes.PIERCING: 220}, kb=15,
                             img='items_weapons_abyss_gaze', speed=2, at_time=6, precision=0, projectile_speed=1000,
                            auto_fire=True),
    'abyss_fury': weapons.MagicWeapon(name='abyss fury', damages={damages.DamageTypes.MAGICAL: 170}, kb=5,
                              img='items_weapons_abyss_fury', speed=1, at_time=4, projectile=projectiles.AbyssFury,
                              mana_cost=65, auto_fire=True, spell_name='Abyss Fury'),

    'miracle_crystal_blade': MiracleCrystalBlade(name='miracle crystal blade', damages={damages.DamageTypes.PHYSICAL: 220}, kb=20,
                                                  img='items_weapons_miracle_crystal_blade', speed=1, at_time=10, rot_speed=50,
                                                  st_pos=150),
    'murakumo': MuraKumo(name='murakumo', damages={damages.DamageTypes.PHYSICAL: 470}, kb=0, img='items_weapons_murakumo',
                         speed=3, at_time=15, rot_speed=15, st_pos=180),
    'longinus': Longinus(name='longinus', damages={damages.DamageTypes.PHYSICAL: 320}, kb=10, img='items_weapons_longinus',
                         speed=8, at_time=18, rot_speed=30, st_pos=300),
    'xuanyuan': XuanYuan(name='xuanyuan', damages={damages.DamageTypes.PHYSICAL: 1800}, kb=15, img='items_weapons_xuanyuan',
                         speed=100, at_time=12, rot_speed=40, st_pos=300),
    'durendal': Durendal(name='durendal', damages={damages.DamageTypes.PHYSICAL: 0}, kb=8, img='items_weapons_durendal',
                         speed=3, at_time=15, rot_speed=20, st_pos=200),
    'bident': Bident(name='bident', damages={damages.DamageTypes.PHYSICAL: 555}, kb=10, img='items_weapons_bident',
                     speed=2, at_time=8, forward_speed=40, st_pos=150),

    'hell': Hell(name='hell', damages={damages.DamageTypes.PHYSICAL: 666}, kb=25, img='items_weapons_hell',
                 speed=2, at_time=4, rot_speed=70, st_pos=120),
    'wvector': WVector(name='wvector', damages={damages.DamageTypes.PHYSICAL: 0}, kb=20, img='items_weapons_vector_t',
                       speed=0, at_time=1, rot_speed=0, st_pos=0),
    'entrophic_broadsword': EntrophicSword(name='entrophic broadsword', damages={damages.DamageTypes.PHYSICAL: 1200}, kb=40,
                                      img='items_weapons_entrophic_broadsword', speed=6, at_time=12, rot_speed=40,
                                      st_pos=300),

    'hope_scorch_bow': HopeScorchBow(name='hope scorch bow', damages={damages.DamageTypes.PIERCING: 300}, kb=10,
                                     img='items_weapons_hope_scorch_bow', speed=3, at_time=6, projectile_speed=1000,
                                     auto_fire=True, precision=3),

    'insights': Insights(name='insights', damages={damages.DamageTypes.PHYSICAL: 320}, kb=30, img='items_weapons_insights',
                        speed=3, at_time=10, rot_speed=25, st_pos=150),
    'pierce': Pierce(name='pierce', damages={damages.DamageTypes.PIERCING: 140}, kb=10, img='items_weapons_pierce',
                     speed=2, at_time=2, precision=3, projectile_speed=1000, auto_fire=True),
    'mystery': weapons.MagicWeapon(name='mystery', damages={damages.DamageTypes.MAGICAL: 250}, kb=10, img='items_weapons_mystery',
                           speed=25, at_time=25, projectile=projectiles.Mystery, mana_cost=450, auto_fire=True),
}

for k, v in WEAPONS.items():
    weapons.WEAPONS[k] = v
