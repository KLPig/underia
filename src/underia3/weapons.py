from underia import weapons, game, inventory
from underia import projectiles as proj
from values import damages, effects
from resources import position
from physics import vector
from underia3 import projectiles
import constants
import random
import pygame as pg
import copy

from wc import w_count


class PurpleClayBroadBlade(weapons.Blade):
    def on_attack(self):
        super().on_attack()
        self.cutting_effect(8)

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
                        e.obj.apply_force(vector.Vector(rf, self.knock_back * 120000 / e.obj.MASS
                        if self.knock_back * 60000 < e.obj.MASS else
                        self.knock_back * 600000 / e.obj.MASS))
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
                            e.hp_sys.enable_immume()

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
                        e.obj.apply_force(vector.Vector(rf, self.knock_back * 120000 / e.obj.MASS
                        if self.knock_back * 60000 < e.obj.MASS else
                        self.knock_back * 600000 / e.obj.MASS))
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
                            e.hp_sys.enable_immume()

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
                    e.hp_sys.enable_immume()

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
        if game.get_game().player.mana < self.mana_cost:
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
        game.get_game().player.mana -= self.mana_cost

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

class AbyssRanseur(weapons.Spear):
    def on_start_attack(self):
        super().on_start_attack()
        game.get_game().projectiles.append(projectiles.AbyssRanseur(game.get_game().player.obj.pos, self.rot))

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
    'purple_clay_broad_blade': PurpleClayBroadBlade(name='purple clay broad blade', damages={damages.DamageTypes.PHYSICAL: 110}, kb=15,
                                                    img='items_weapons_purple_clay_broad_blade', speed=1, at_time=8,
                                                    rot_speed=40, st_pos=150),
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

    'proof': Proof(name='proof', damages={damages.DamageTypes.PHYSICAL: 60}, kb=2, img='items_weapons_proof',
                   speed=8, at_time=2, rot_speed=30, st_pos=15),
    'observe': Observe(name='observe', damages={damages.DamageTypes.PHYSICAL: 70}, kb=2, img='items_weapons_observe',
                       speed=1, at_time=8, rot_speed=40, st_pos=240),
    'intestinal_sword': IntestinalSword(name='intestinal sword', damages={damages.DamageTypes.PHYSICAL: 120}, kb=10,
                                        img='items_weapons_intestinal_sword', speed=1, at_time=6, rot_speed=40, st_pos=150),

    'critical_thinking': weapons.Blade(name='critical thinking', damages={damages.DamageTypes.PHYSICAL: 340}, kb=15,
                                       img='items_weapons_critical_thinking', speed=1, at_time=15, rot_speed=20, st_pos=180),

    'longer_intestine': weapons.Whip(name='longer intestine', damages={damages.DamageTypes.PHYSICAL: 480}, kb=30,
                                     img='items_weapons_longer_intestine', speed=10, at_time=30, length=50,
                                     size=60, auto_fire=True),

    'destroy': Destroy('destroy', {damages.DamageTypes.PHYSICAL: 800}, 35,
                       'items_weapons_destroy', 15, 25, 10, 150),
    'generate': Generate('generate', {damages.DamageTypes.PHYSICAL: 250}, 15,
                         'items_weapons_generate', 5, 10, 50, 300),
    'ancient_swiftsword': AncientSwiftsword('ancient swiftsword', {damages.DamageTypes.PHYSICAL: 900}, 20,
                                            'items_weapons_ancient_swiftsword', 2, 5, 50, 130),
    'feather_feather_sword': FeatherFeatherSword(name='feather feather sword', damages={damages.DamageTypes.PHYSICAL: 800}, kb=10,
                                                  img='items_weapons_feather_feather_sword', speed=2, at_time=3, rot_speed=80,
                                                  st_pos=180),
    'confuse': Confuse('confuse', {damages.DamageTypes.PHYSICAL: 450}, 10,
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

    'e_wooden_wand': weapons.MagicWeapon(name='e wooden wand', damages={damages.DamageTypes.MAGICAL: 40}, kb=2,
                                         img='items_weapons_e_wooden_wand', speed=1, at_time=6,
                                         projectile=projectiles.EWoodenWand, mana_cost=5, auto_fire=True,
                                         spell_name='Life Growth'),
    'lychee_wand': weapons.MagicWeapon(name='lychee wand', damages={damages.DamageTypes.MAGICAL: 42}, kb=0,
                                        img='items_weapons_lychee_wand', speed=1, at_time=9,
                                        projectile=projectiles.LycheeWand, mana_cost=15, auto_fire=True,
                                        spell_name='Lychee Circle'),
    'lychee_spike': NewMagicWeapon(name='lychee spike', damages={damages.DamageTypes.MAGICAL: 360}, kb=0,
                                   img='items_weapons_lychee_spike', speed=1, at_time=25,
                                   projectile=projectiles.LycheeSpike, mana_cost=30, auto_fire=True,
                                   spell_name='Lychee Spike'),
    'brainstorm': SpeedIncreaseMagicWeapon(name='brainstorm', damages={damages.DamageTypes.MAGICAL: 240}, kb=0,
                                           img='items_weapons_brainstorm', speed=15, at_time=5,
                                           projectile=projectiles.Brainstorm, mana_cost=45, auto_fire=True,
                                           spell_name='Brainstorm'),

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

    'abyss_ranseur': AbyssRanseur(name='abyss ranseur', damages={damages.DamageTypes.PHYSICAL: 1200}, kb=50,
                                   img='items_weapons_abyss_ranseur', speed=2, at_time=6, forward_speed=80,
                                   st_pos=300, auto_fire=True),
    'abyss_gaze': AbyssGaze(name='abyss gaze', damages={damages.DamageTypes.PIERCING: 400}, kb=15,
                             img='items_weapons_abyss_gaze', speed=2, at_time=6, precision=0, projectile_speed=1000,
                            auto_fire=True),
    'abyss_fury': weapons.MagicWeapon(name='abyss fury', damages={damages.DamageTypes.MAGICAL: 500}, kb=5,
                              img='items_weapons_abyss_fury', speed=1, at_time=4, projectile=projectiles.AbyssFury,
                              mana_cost=18, auto_fire=True, spell_name='Abyss Fury'),

    'insights': Insights(name='insights', damages={damages.DamageTypes.PHYSICAL: 2500}, kb=30, img='items_weapons_insights',
                        speed=3, at_time=10, rot_speed=25, st_pos=150),
    'pierce': Pierce(name='pierce', damages={damages.DamageTypes.PIERCING: 1200}, kb=10, img='items_weapons_pierce',
                     speed=2, at_time=2, precision=3, projectile_speed=1000, auto_fire=True),
}

for k, v in WEAPONS.items():
    weapons.WEAPONS[k] = v
