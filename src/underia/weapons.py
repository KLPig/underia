import copy
import math
import random

import pygame as pg

import constants
from physics import vector
from resources import position, tone
from underia import game, projectiles, inventory, entity
from values import damages as dmg, DamageTypes
from values import effects
from visual import effects as eff, particle_effects as pef, fade_circle as fc, draw

import perlin_noise
import functools

class Weapon:
    ENABLE_IMMUNE = True
    ATTACK_SOUND: str | None = None
    _EFF_NOISES = []

    def __init__(self, name, damages: dict[int, float], kb: float, img_index: str, speed: int, at_time: int,
                 auto_fire: bool = False):
        self.name = name
        self.damages = damages
        self.img_index = img_index
        self.img = pg.Surface((10, 10))
        self.d_img = pg.Surface((10, 10))
        self.timer = 0
        self.cool = 0
        self.knock_back = kb
        self.cd = speed * 2
        self.at_time = at_time * 2
        self.rot = 0
        self.x = 0
        self.y = 0
        self.display = False
        self.auto_fire = auto_fire
        self.key = 1
        self.keys = None
        self.combo = 0
        self.sk_cd = 0
        self.sk_mcd = 0
        self.lrot = 0
        self.poss = [(0, 0) for _ in range(10)]
        self.aposs = [[] for _ in range(400)]
        self.noises = []
        self.lx, self.ly = 0, 0
        self.strike = 0
        self.scale = 1.0

    def re_init(self):
        pass

    def attack(self):
        self.timer = self.at_time + 1
        self.on_start_attack()
        if self.timer:
            if self.ATTACK_SOUND is not None:
                d = vector.distance(self.x, self.y)
                game.get_game().play_sound(self.ATTACK_SOUND, 0.99 ** int(d / 10) / 3, False)

    def on_special_attack(self, strike: int):
        pass

    def on_charge(self):
        pass

    def on_start_attack(self):
        pass

    def on_attack(self):
        self.display = True

    def forward(self, step: int):
        dx, dy = vector.rotation_coordinate(self.rot)
        self.x += dx * step
        self.y += dy * step

    def rotate(self, angle: int):
        self.set_rotation((self.rot + angle) % 360)

    def set_rotation(self, angle: int):
        self.img = pg.transform.rotate(pg.transform.scale_by(game.get_game().graphics[self.img_index.replace('items_weapons_', 'items_')],
                                                             self.scale / game.get_game().player.get_screen_scale()), -45)

        self.d_img = pg.Surface((2 * self.img.get_width(), self.img.get_height()), pg.SRCALPHA)
        self.d_img.blit(self.img, (self.img.get_width(), 0))
        self.d_img = pg.transform.rotate(self.d_img, 90 - angle)
        self.rot = angle

    def face_to(self, x: int, y: int):
        dx, dy = x - self.x, y - self.y
        self.set_rotation(vector.coordinate_rotation(dx, dy))

    def on_end_attack(self):
        self.display = False

    def on_idle(self):
        pass

    def draw(self):
        imr = self.d_img.get_rect(center=position.displayed_position(
            (self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1])))
        game.get_game().displayer.canvas.blit(self.d_img, imr)

    def update(self):
        if self.display:
            self.draw()
        if self.timer > 1:
            self.on_attack()
            self.combo += 1
            self.timer -= 1
            self.cool = 1
        elif self.timer == 1:
            if self.strike:
                self.strike = 0
            self.timer = 0
            self.cool = max(0, self.cd + game.get_game().player.calculate_data('atk_speed', False) // 3)
            self.on_end_attack()
            self.on_idle()
        else:
            self.on_idle()
        if not self.timer:
            if self.cool:
                self.cool -= 1
            else:
                if self.keys is None:
                    b = self.key in game.get_game().get_mouse_press() or (
                                self.auto_fire and self.key in game.get_game().get_pressed_mouse())
                else:
                    b = len([1 for k in self.keys if k in game.get_game().get_keys()]) or \
                        (self.auto_fire and len([1 for k in self.keys if k in game.get_game().get_pressed_keys()]))
                if pg.BUTTON_RIGHT in game.get_game().get_pressed_mouse():
                    self.strike += 1 if constants.DIFFICULTY <= 1 else 2
                    self.on_charge()
                elif b or self.strike:
                    self.attack()
                    if self.strike:
                        self.on_special_attack(self.strike)
                        self.strike = 0
                    if 'mana_cost' in dir(self) and ('fluffy_pluvial' in game.get_game().player.accessories or
                            'moonflower' in game.get_game().player.accessories):
                        self.attack()
                        if random.random() < 0.25:
                            game.get_game().player.mana = min(game.get_game().player.max_mana,
                                                              game.get_game().player.mana + round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1) / 2)
                else:
                    self.combo = -1

    def cutting_effect(self, size=4, col1=(100, 0, 100), col2=(255, 100, 255)):
        self.rot %= 360
        self.lrot %= 360
        if self.rot - self.lrot > 180:
            self.lrot += 360
        if self.lrot - self.rot > 180:
            self.rot += 360
        arot = self.rot - self.lrot
        self.lrot = self.rot
        if abs(arot) > 5:
            sf = Weapon.get_cut_surf(round(arot / 20) * 20, size, col1, col2, self.scale)
            sf = pg.transform.scale_by(pg.transform.rotate(sf, -self.rot), 1 / game.get_game().player.get_screen_scale())
            sfr = sf.get_rect(center=position.displayed_position((self.x + game.get_game().player.obj.pos[0],
                                                                  self.y + game.get_game().player.obj.pos[1])))
            game.get_game().displayer.canvas.blit(sf, sfr)
        game.get_game().displayer.point_light(col1, position.displayed_position((self.x + game.get_game().player.obj.pos[0],
                                                                                    self.y + game.get_game().player.obj.pos[1])),
                                              1.5, size * 30 / game.get_game().player.get_screen_scale())
        game.get_game().displayer.point_light(col2,
                                              position.displayed_position((self.x + game.get_game().player.obj.pos[0],
                                                                           self.y + game.get_game().player.obj.pos[1])),
                                              1.5, size * 30 / game.get_game().player.get_screen_scale())

    @staticmethod
    @functools.lru_cache(maxsize=int(constants.MEMORY_USE * .08))
    def get_cut_surf(arot, size, col1, col2, scale):
        if not len(Weapon._EFF_NOISES):
            noises = perlin_noise.PerlinNoise(octaves=2, seed=random.randint(0, 1000000))
            Weapon._EFF_NOISES = [noises(i / 100) for i in range(1000)]
        mx = max(Weapon._EFF_NOISES)
        mn = min(Weapon._EFF_NOISES)
        sz = {3: 32, 4: 40, 6: 64, 8: 80, 10: 100, 16: 160, 32: 320}[size]
        dst = {3: 100, 4: 130, 6: 200, 8: 260, 10: 350, 16: 520, 32: 1080}[size]
        sz = sz
        dst = int(dst * scale)
        gdt = int(23 * scale)
        sz //= constants.BLADE_EFFECT_QUALITY
        gdt *= constants.BLADE_EFFECT_QUALITY
        surf = pg.Surface((dst * 2 + 10, dst * 2 + 10), pg.SRCALPHA)
        for j in range(sz):
            i = j / 10
            d = (dst - i * gdt)
            dt = (sz - j) * arot / sz * ((Weapon._EFF_NOISES[j * 999 // sz] - mn) / (mx - mn) * 8 / 5 + .2)
            adt = (sz - j) * arot / sz * ((Weapon._EFF_NOISES[j * 999 // sz] - mn) / (mx - mn) * 2) / 8
            rots = [vector.rotation_coordinate( -(dt + adt) * i / 9 + adt) for i in range(9, -1, -1)]
            eff.pointed_curve((int(col1[0] + (col2[0] - col1[0]) / sz * j),
                               int(col1[1] + (col2[1] - col1[1]) / sz * j),
                               int(col1[2] + (col2[2] - col1[2]) / sz * j)), [(vx * d + surf.get_width() // 2, vy * d + surf.get_height() // 2)
                                                                              for vx, vy in rots],
                              int(3 * constants.BLADE_EFFECT_QUALITY * scale), salpha=int(255 * (1 - j / sz / 6)),
                              target=surf)
        return surf

    def activated_cutting_effect(self, size=4, col1=(100, 0, 100), col2=(255, 100, 255), length=3):
        self.rot %= 360
        self.lrot %= 360
        if self.rot - self.lrot > 180:
            self.lrot += 360
        if self.lrot - self.rot > 180:
            self.rot += 360
        sz = {3: 32, 4: 40, 6: 64, 8: 80, 10: 100, 16: 160, 32: 320}[size]
        dst = {3: 100, 4: 130, 6: 200, 8: 260, 10: 350, 16: 520, 32: 1080}[size]
        d = dst
        ax, ay = vector.rotation_coordinate(self.rot)
        self.aposs[0].append((self.x + ax * d + game.get_game().player.obj.pos[0],
                              self.y + ay * d + game.get_game().player.obj.pos[1]))
        if len(self.aposs[0]) > length:
            self.aposs[0].pop(0)
        eff.pointed_curve(col1, self.aposs[0][-length:],
                          5, salpha=127)
        d -= 5
        self.aposs[1].append((self.x + ax * d + game.get_game().player.obj.pos[0],
                              self.y + ay * d + game.get_game().player.obj.pos[1]))
        if len(self.aposs[1]) > length:
            self.aposs[1].pop(0)
        eff.pointed_curve(col2, self.aposs[1][-length:],
                          5, salpha=127)
        self.lrot = self.rot
        self.lx = self.x
        self.ly = self.y

class SweepWeapon(Weapon):
    DMG_AS_IDX = 0
    ATTACK_SOUND = 'attack_sweep'

    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False, auto_fire: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, auto_fire)
        self.rot_speed = rot_speed // 2
        self.st_pos = st_pos
        self.double_sided = double_sided
        self.lrot = 0
        self.noises = []
        self.ddata = [copy.copy(self.damages), 1, self.rot_speed]

    def on_damage(self, target):
        pass

    def on_idle(self):
        super().on_idle()
        mx = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))[0] - self.x - game.get_game().player.obj.pos[0]
        if mx > 0:
            mx = 1
        else:
            mx = -1
        self.set_rotation(90 + mx * int(5 + self.img.get_width() / 20) + self.rot // 2)
        self.display = True

    def on_special_attack(self, strike: int):
        self.damages = copy.copy(self.ddata[0])
        self.scale = self.ddata[1]
        self.rot_speed = self.ddata[2]
        self.ddata = [copy.copy(self.damages), 1, self.rot_speed]
        self.scale = 5 - 4 * 1.5 ** -(self.strike / 50)
        for k in self.damages.keys():
            self.damages[k] *= 4 - 3 * 1.2 ** -(self.strike / 50)
        self.rot_speed = int(self.rot_speed / self.scale)
        self.timer = int(self.at_time * self.scale ** 1.5)

    def on_start_attack(self, rr=None):
        if rr is None:
            r = random.choice([-1, 1])
        else:
            r = rr
        px, py = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        self.face_to(px, py)
        self.rotate(abs(self.st_pos) * r)
        self.rot_speed = abs(self.rot_speed) * -r

    def on_attack(self):
        self.rotate(self.rot_speed)
        self.rotate(int(-(self.timer - self.at_time / 2) * abs(self.rot_speed) // self.rot_speed *
                        (25 + self.strike * 35) * (3 if constants.DIFFICULTY > 1 else 1) // self.at_time) if self.timer <= self.at_time else 0)
        super().on_attack()
        self.damage()

    def on_end_attack(self):
        super().on_end_attack()
        self.damages = copy.copy(self.ddata[0])
        self.scale = self.ddata[1]
        self.rot_speed = self.ddata[2]

    def on_charge(self):
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        self.set_rotation(180 + vector.cartesian_to_polar(mx, my)[0])
        self.display = True
        self.scale = 5 - 4 * 1.2 ** -(self.strike / 50)

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
                if vector.distance(px, py) < self.img.get_width() * 1.414 * self.scale + (
                (e.img.get_width() + e.img.get_height()) // 2 if e.img is not None else 10):
                    self.on_damage(e)
                    for t, d in self.damages.items():
                        e.hp_sys.damage(d * game.get_game().player.attack * game.get_game().player.attacks[self.DMG_AS_IDX], t)
                    if not e.hp_sys.is_immune:
                        rf = vector.coordinate_rotation(px + self.x, py + self.y)
                        e.obj.apply_force(vector.Vector(rf, min(self.knock_back * 120000 / e.obj.MASS, e.obj.MASS * 24)
                                                        if self.knock_back * 60000 < e.obj.MASS or constants.DIFFICULTY <= 1 else
                                                        min(min(self.knock_back * 600000 / e.obj.MASS, e.obj.MASS * 24), e.obj.MASS * 24)))
                    if 'matters_touch' in game.get_game().player.accessories:
                        e.obj.MASS *= 1.01
                    if 'grasp_of_the_infinite_corridor' in game.get_game().player.accessories:
                        if not e.IS_MENACE and not e.VITAL:
                            e.hp_sys.damage(e.hp_sys.max_hp / 10, dmg.DamageTypes.THINKING)
                            if random.randint(0, 10) == 0:
                                e.hp_sys.hp = 0
                        else:
                            e.hp_sys.damage(max(e.hp_sys.max_hp / 1000, 10000), dmg.DamageTypes.THINKING)
                    if self.ENABLE_IMMUNE:
                        if constants.DIFFICULTY > 1:
                            e.hp_sys.enable_immune()

class MurderersKnife(SweepWeapon):
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
                if vector.distance(px, py) < self.img.get_width() + (
                (e.img.get_width() + e.img.get_height()) // 2 if e.img is not None else 10):
                    e.hp_sys.damage(e.hp_sys.max_hp * 0.4, dmg.DamageTypes.PHYSICAL)
                    if not e.hp_sys.is_immune:
                        rf = vector.coordinate_rotation(px + self.x, py + self.y)
                        e.obj.apply_force(vector.Vector(rf, min(self.knock_back * 120000 / e.obj.MASS, e.obj.MASS * 24)))
                    e.hp_sys.enable_immune()

class RemoteWeapon(SweepWeapon):
    def update(self):
        mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
        px, py = game.get_game().player.obj.pos
        self.x = (mx - px + self.x) // 2
        self.y = (my - py + self.y) // 2
        if not self.timer:
            self.face_to(mx - px, my - py)
        self.display = True
        super().update()

class ThiefWeapon(SweepWeapon):
    DMG_AS_IDX = 1

    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, throw_interval: int, power: int):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, auto_fire=True)
        self.sk_mcd = throw_interval * 2
        self.throwing = False
        self.pow = power
        self.auto_throw = False

    def on_special_attack(self, strike: int):
        super().on_special_attack(strike)
        mp = vector.Vector2D()
        mp << position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        mp /= abs(mp)
        game.get_game().player.obj.velocity += mp * self.pow * (self.scale - 1) / 7

    def on_start_attack(self):
        super().on_start_attack()
        self.throwing = False
        if not self.throwing and not self.sk_cd:
            f = 0
            for e in game.get_game().entities:
                if vector.distance(e.obj.pos[0] - self.x - game.get_game().player.obj.pos[0],
                                    e.obj.pos[1] - self.y - game.get_game().player.obj.pos[1]) \
                    < self.img.get_width() * 1.414 * self.scale + (e.img.get_width() + e.img.get_height()) // 2:
                    f = 1
                    break
            if not f:
                self.throwing = True
                self.sk_cd = self.sk_mcd
                self.timer = abs(self.st_pos // self.rot_speed)

    def update(self):
        super().update()
        if pg.K_q in game.get_game().get_keys():
            self.auto_throw = not self.auto_throw

    def on_end_attack(self):
        if self.throwing:
            mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
            self.rot = vector.coordinate_rotation(mx, my)
            self.skill()
        super().on_end_attack()

    def skill(self):
        proj = projectiles.THIEF_WEAPONS[self.name.replace(' ', '_')]((self.x + game.get_game().player.obj.pos[0],
                                                                       self.y + game.get_game().player.obj.pos[1]),
                                                                      self.rot, self.pow)
        proj.obj.velocity.add(game.get_game().player.obj.velocity.get_net_vector())
        game.get_game().projectiles.append(proj)

class ThrowerThiefWeapon(SweepWeapon):
    DMG_AS_IDX = 1

    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, throw_interval: int, power: int, stack_size: int):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, auto_fire=True)
        self.stack_size = stack_size
        self.amount = 0
        self.throwing = False
        self.auto_throw = False
        self.sk_mcd = throw_interval
        self.pow = power

    def on_start_attack(self):
        super().on_start_attack()
        self.throwing = False
        if self.amount:
            self.throwing = True
            self.timer = abs(self.st_pos // self.rot_speed)
            self.amount -= 1

    def update(self):
        super().update()
        if not self.sk_cd:
            if self.amount < self.stack_size:
                self.amount += 1
                self.sk_cd = self.sk_mcd

    def on_end_attack(self):
        if self.throwing:
            mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
            self.rot = vector.coordinate_rotation(mx, my)
            self.skill()
        super().on_end_attack()

    def skill(self):
        proj = projectiles.THIEF_WEAPONS[self.name.replace(' ', '_')]((self.x + game.get_game().player.obj.pos[0],
                                                                       self.y + game.get_game().player.obj.pos[1]),
                                                                      self.rot, self.pow)
        proj.obj.velocity.add(game.get_game().player.obj.velocity.get_net_vector())
        game.get_game().projectiles.append(proj)

class ThiefDoubleKnife(ThiefWeapon):
    HAND_INTERVAL = 20

    def __init__(self, name, damages: dict[int, float], kb: float, img: str | tuple[str, str], speed: int, at_time: int, rot_speed: int,
                 st_pos: int, throw_interval: int, power: int, dcols: tuple[tuple[int, int, int], tuple[int, int, int]] |
                                 tuple[tuple[tuple[int, int, int], tuple[int, int, int]], tuple[tuple[int, int, int], tuple[int, int, int]]] | None = None,
                 dsz: int = 4):
        super().__init__(name, damages, kb, 'items_weapons_null', speed, at_time, rot_speed, st_pos, throw_interval, power)
        self.double_sided = True
        self.hand_timer = 0
        self.same_direction = False
        self.display = False
        self.weapons = [Weapon(name, damages, kb, img if type(img) is str else img[_], speed, at_time, auto_fire=True) for _ in range(2)]
        for i in range(2):
            self.weapons[i].x = [-1, 1][i] * self.HAND_INTERVAL
            self.weapons[i].keys = []
        if dcols is not None:
            self.dcol1 = dcols[0] if type(dcols[0][0]) is tuple else dcols
            self.dcol2 = dcols[1] if type(dcols[1][0]) is tuple else dcols
        else:
            self.dcol1 = None
            self.dcol2 = None
        self.dsz = dsz

    def update(self):
        super().update()
        for w in self.weapons:
            w.update()
        self.display = False

    def on_idle(self):
        self.display = False
        for w in self.weapons:
            mx = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))[0] - w.x - \
                 game.get_game().player.obj.pos[0]
            if mx > 0:
                mx = 1
            else:
                mx = -1
            w.set_rotation(90 + mx * int(5 + w.img.get_width() / 20) + w.rot // 2)
            w.display = True

    def on_charge(self):
        super().on_charge()
        for w in self.weapons:
            w.scale = self.scale
            w.display = self.display
            mp = vector.Vector2D()
            mp << position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
            mp /= abs(mp)
            mp.x -= self.x
            mp.y -= self.y
            w.set_rotation(180 + vector.cartesian_to_polar(*mp)[0])

    def on_start_attack(self):
        if random.random() < 0.5:
            self.weapons.append(self.weapons[0])
            self.weapons.pop(0)
        self.same_direction = random.random() < 0.5
        super().on_start_attack()

    def on_attack(self):
        super().on_attack()
        self.weapons[0].set_rotation(self.rot)
        self.weapons[1].set_rotation(self.rot + 180 * (not self.same_direction))
        self.weapons[0].scale = self.scale
        self.weapons[1].scale = self.scale
        if self.dcol1 is not None:
            self.weapons[0].cutting_effect(self.dsz, self.dcol1[0], self.dcol1[1])
            self.weapons[1].cutting_effect(self.dsz, self.dcol2[0], self.dcol2[1])
        self.rot += 180
        super().damage()
        self.rot -= 180
        self.weapons[0].display = True
        self.weapons[1].display = True

    def on_end_attack(self):
        super().on_end_attack()
        self.weapons[0].scale = 1
        self.weapons[1].scale = 1

class GenerationI(ThiefDoubleKnife):
    def on_end_attack(self):
        s = self.scale > 1
        super().on_end_attack()
        if s:
            game.get_game().player.weapons[game.get_game().player.sel_weapon] = WEAPONS['generation_ii']

class StormStabber(ThiefWeapon):
    def on_start_attack(self):
        super().on_start_attack()
        self.rot += int(self.rot_speed * 4.5)

    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, throw_interval: int, power: int):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, throw_interval, power)
        self.lp = (0, 0 )

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(4, (0, 0, 255), (200, 200, 255))
        if self.throwing:

            game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(self.lp),
                                                                col=(100, 100, 255)))
            self.lp = game.get_game().player.obj.pos
            for i in range(9):
                self.rot += 40
                self.damage()
            self.rot -= 360
            mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
            if self.timer < self.at_time // 2:
                game.get_game().player.obj.velocity.add(vector.Vector(vector.coordinate_rotation(mx, my), -120))
            else:
                game.get_game().player.obj.velocity.add(vector.Vector(vector.coordinate_rotation(mx, my),
                                                                      vector.distance(mx, my) // 4))

class Whip(Weapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, length: int, size: int, auto_fire: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, auto_fire)
        self.size = size
        self.length = length
        self.st_pos = 800 // self.length
        self.tgt_pos = 0
        self.collides = []

    def draw(self):
        super().draw()
        self.collides.clear()
        pos = vector.Vector2D()
        ar = self.st_pos * (1 - math.sin((1 - self.timer / self.at_time) * math.pi) ** 3) * (-1 if self.timer > self.at_time / 2 else 1)
        rot = self.tgt_pos
        size = self.size - abs(ar) / self.st_pos * self.size / 3
        for i in range(self.length):
            rot += ar
            pos += vector.Vector2D(dr=rot, dt=size - size * 2 * i / self.length // 5)
            self.collides.append(pos)
            sf = game.get_game().graphics['items_' + self.name.replace(' ', '_') + '_whip']
            sf = projectiles.projectile_get_surface(rot, 1 / (size - size * i / self.length * .8) * 50 * game.get_game().player.get_screen_scale(), sf)
            sr = sf.get_rect(center=position.displayed_position(pos + game.get_game().player.obj.pos))
            game.get_game().displayer.canvas.blit(sf, sr)

    def on_start_attack(self):
        super().on_start_attack()
        tp = vector.Vector2D(0, 0, *position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))) - game.get_game().player.obj.pos
        self.tgt_pos = vector.coordinate_rotation(*tp)

    def on_attack(self):
        ar = self.st_pos * math.sin(self.timer / self.at_time * math.pi) * (-1 if self.timer > self.at_time / 2 else 1)
        self.set_rotation(int(self.tgt_pos + ar))
        super().on_attack()
        self.damage()

    def on_damage(self, target):
        pass

    def damage(self):
        for p_pos in self.collides:
            pos = game.get_game().player.obj.pos + p_pos
            for e in game.get_game().entities:
                if vector.distance(*(pos - e.obj.pos)) < self.size * 10:
                    for t, d in self.damages.items():
                        e.hp_sys.damage(d * game.get_game().player.attack * game.get_game().player.attacks[0], t)
                    if not e.hp_sys.is_immune:
                        e.obj.apply_force(vector.Vector(self.tgt_pos, min(self.knock_back * 120000 / e.obj.MASS, e.obj.MASS * 24)))
                    self.on_damage(e)
                    if self.ENABLE_IMMUNE:
                        e.hp_sys.enable_immune()

class Spear(Weapon):
    ATTACK_SOUND = 'attack_sweep'

    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, forward_speed: int,
                 st_pos: int, auto_fire: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, auto_fire)
        self.st_pos = st_pos
        self.forward_speed = forward_speed
        self.poss = 0
        self.ddata = [copy.copy(damages), 1, forward_speed]
        self.tgt_pos = 0

    def on_idle(self):
        super().on_idle()
        mx = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))[0] - self.x - game.get_game().player.obj.pos[0]
        if mx > 0:
            mx = 1
        else:
            mx = -1
        self.set_rotation(90 + mx * int(5 + self.img.get_width() / 20) + self.rot // 2)
        self.display = True
        self.x /= 2
        self.y /= 2

    def on_start_attack(self):
        self.x = 0
        self.y = 0
        px, py = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        self.face_to(px, py)
        self.forward(-self.st_pos / 2)
        self.poss =  -self.st_pos / 2
        self.tgt_pos = self.rot

    def on_end_attack(self):
        super().on_end_attack()
        self.damages = copy.copy(self.ddata[0])
        self.scale = self.ddata[1]
        self.forward_speed = self.ddata[2]

    def on_charge(self):
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        self.x, self.y = 0, 0
        self.set_rotation(vector.cartesian_to_polar(mx, my)[0])
        self.scale = 5 - 4 * 1.2 ** -(self.strike / 50)
        self.forward(-self.st_pos / 2 - self.st_pos / 16 * (self.scale ** 2 - 1))
        self.display = True

    def on_special_attack(self, strike: int):
        self.damages = copy.copy(self.ddata[0])
        self.scale = self.ddata[1]
        self.forward_speed = self.ddata[2]
        self.ddata = [copy.copy(self.damages), 1, self.forward_speed]
        self.scale = 5 - 4 * 1.5 ** -(self.strike / 50)
        self.forward(-self.st_pos / 16 * (self.scale ** 2 - 1))
        for k in self.damages.keys():
            self.damages[k] *= 4 - 3 * 1.2 ** -(self.strike / 50)
        self.forward_speed = int(self.forward_speed / self.scale)
        self.timer = int(self.at_time * self.scale ** 1.5)

    def on_attack(self):
        self.forward(self.timer - self.at_time // 2)
        self.forward(self.forward_speed // 2 * (1 if self.timer > self.at_time // 2 else -1))
        self.set_rotation(self.tgt_pos + int(10 * math.sin(self.timer / self.at_time * math.pi * 2)))
        self.poss += self.forward_speed // 2
        super().on_attack()
        self.damage()

    def on_damage(self, target):
        pass

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
                    for t, d in self.damages.items():
                        e.hp_sys.damage(d * game.get_game().player.attack * game.get_game().player.attacks[0], t)
                    self.on_damage(e)
                    if not e.hp_sys.is_immune:
                        e.obj.apply_force(vector.Vector(r, min(self.knock_back * 120000 / e.obj.MASS, e.obj.MASS * 24)))
                    if self.ENABLE_IMMUNE:
                        e.hp_sys.enable_immune()

class SwiftSword(Spear):
    def update(self):
        self.sk_mcd = 10
        super().update()
        if not self.timer and not self.cool:
            if pg.K_q in game.get_game().get_keys() and (game.get_game().player.mana >= 20 or not self.sk_cd):
                mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
                px, py = game.get_game().player.obj.pos
                game.get_game().player.obj.apply_force(vector.Vector(vector.coordinate_rotation(mx - px, my - py), 3600))
                if not self.sk_cd:
                    self.sk_cd = self.sk_mcd
                else:
                    game.get_game().player.mana -= 20
                self.attack()


class ComplexWeapon(Weapon):
    def __init__(self, name, damages_rot: dict[int, float], damages_spear: dict[int, float],
                 kb: float, img, speed: int, at_time_rot: int, at_time_spear: int,
                 rot_speed: int, st_pos_sweep: int, forward_speed: int, st_pos_spear: int,
                 auto_fire: bool = False, combat: list[int] = [0, 0, 1], sweep_type = SweepWeapon,
                 spear_type = Spear):
        super().__init__(name, damages_rot, kb, img, speed, at_time_rot, auto_fire)
        self.forward_speed = forward_speed
        self.st_pos_spear = st_pos_spear
        self.sweep = sweep_type(name, damages_rot, kb, img, speed, at_time_rot, rot_speed, st_pos_sweep, auto_fire)
        self.spear = spear_type(name, damages_spear, kb, img, speed, at_time_spear, forward_speed, st_pos_spear, auto_fire)
        self.sweep.keys = []
        self.spear.keys = []
        self.combat = combat
        self.cb = 0

    def on_start_attack(self):
        self.cb = (self.cb + 1) % len(self.combat)
        if self.combat[self.cb]:
            self.sweep.attack()
        else:
            self.spear.attack()

    def update(self):
        self.spear.update()
        self.sweep.update()
        super().update()

    def on_idle(self):
        self.spear.display = False
        self.sweep.display = True

    def on_attack(self):
        if self.spear.timer:
            self.sweep.display = False
        if self.sweep.timer:
            self.spear.display = True
        super().on_attack()

class AutoSweepWeapon(SweepWeapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, double_sided, True)


class BloodySword(SweepWeapon):
    def on_attack(self):
        super().on_attack()
        if pg.K_q in game.get_game().get_keys():
            mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            px, py = game.get_game().player.obj.pos
            game.get_game().player.obj.apply_force(vector.Vector(vector.coordinate_rotation(mx - px, my - py), 600))


class SandSword(SweepWeapon):
    def on_attack(self):
        super().on_attack()
        if pg.K_q in game.get_game().get_keys():
            mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            px, py = game.get_game().player.obj.pos
            game.get_game().player.obj.apply_force(vector.Vector(vector.coordinate_rotation(mx - px, my - py), 900))


class Blade(AutoSweepWeapon):
    def on_start_attack(self):
        px, py = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        r = -1 if px > 0 else 1
        self.face_to(px, py)
        self.rotate(abs(self.st_pos) * r)
        self.rot_speed = abs(self.rot_speed) * -r

class Pickaxe(AutoSweepWeapon):
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
                if vector.distance(px, py) < self.img.get_width() + (
                (e.img.get_width() + e.img.get_height()) // 2 if e.img is not None else 10):
                    for t, d in self.damages.items():
                        e.hp_sys.damage(d, t)
                    if not e.hp_sys.is_immune:
                        rf = vector.coordinate_rotation(px + self.x, py + self.y)
                        e.obj.apply_force(vector.Vector(rf, min(self.knock_back * 120000 / e.obj.MASS, e.obj.MASS * 24)))
                    e.hp_sys.enable_immune()

class LifeWoodenSword(Blade):
    def on_start_attack(self):
        super().on_start_attack()
        mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
        px, py = game.get_game().player.obj.pos
        game.get_game().projectiles.append(projectiles.Projectiles.LifeWoodenSword(game.get_game().player.obj.pos,
                                                                                   vector.coordinate_rotation(mx - px, my - py)))

class BloodPike(Spear):
    def on_start_attack(self):
        super().on_start_attack()
        mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
        px, py = game.get_game().player.obj.pos
        game.get_game().player.obj.apply_force(vector.Vector(vector.coordinate_rotation(mx - px, my - py), 800))

class FurSpear(Spear):
    def on_end_attack(self):
        super().on_end_attack()
        for _ in range(random.randint(8, 18)):
            r = self.rot + random.randint(-10, 10)
            p = random.randint(50, 180)
            f = projectiles.Projectiles.Fur((self.x + game.get_game().player.obj.pos[0],
                                              self.y + game.get_game().player.obj.pos[1]), r)
            f.obj.apply_force(vector.Vector(r, p))
            game.get_game().projectiles.append(f)

class PerseveranceSword(Blade):
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
                for t, d in self.damages.items():
                    e.hp_sys.damage(d * game.get_game().player.attack * game.get_game().player.attacks[0], t)
                if not e.hp_sys.is_immune:
                    e.obj.apply_force(vector.Vector(r, min(self.knock_back * 120000 / e.obj.MASS, e.obj.MASS * 24)))
                e.hp_sys.enable_immune()


class BlackHoleSword(Blade):
    def on_start_attack(self):
        super().on_start_attack()
        game.get_game().player.obj.MASS = 10 ** 9

    def on_end_attack(self):
        super().on_end_attack()
        game.get_game().player.obj.MASS = 20

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(6, (0, 0, 0), (50, 50, 50))

    def damage(self):
        super().damage()
        game.get_game().player.obj.FRICTION = 0

class Swwwword(Blade):
    def on_attack(self):
        super().on_attack()
        self.cutting_effect(4, (255, 255, 255), (200, 255, 255))

class TearBlade(Blade):
    def on_damage(self, target: entity.Entities.Entity):
        target.hp_sys.effect(effects.BleedingR(2, 9))

class Sunrise(Blade):
    def on_start_attack(self):
        mr = vector.coordinate_rotation(*(-game.get_game().player.obj.pos + position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        game.get_game().projectiles.append(projectiles.Projectiles.Sunrise(game.get_game().player.obj.pos, mr))
        super().on_start_attack()

class Mantle(Blade):
    def on_attack(self):
        super().on_attack()
        game.get_game().projectiles.append(projectiles.Projectiles.Mantle(game.get_game().player.obj.pos + (self.x, self.y) + vector.Vector2D(self.rot, self.img.get_width()),
                                                                          self.rot + self.rot_speed * 3))

class ChaosReap(Blade):
    def __init__(self, *args):
        self.t_scale = 1
        self.vel = vector.Vector2D(0, 0)
        super().__init__(*args)
        self.tr = 0

    def update(self):
        self.img = game.get_game().graphics[self.img_index]
        super().update()
        self.t_scale = [2.5, 3.5, 4, 4.5, 5][min(4, game.get_game().stage)]
        self.damages[dmg.DamageTypes.PHYSICAL] = [200, 350, 500, 1000, 9000][min(4, game.get_game().stage)]
        self.vel += (-self.x / 100, -self.y / 100)
        self.vel *= .9
        self.x, self.y = self.vel + (self.x, self.y)

    def on_damage(self, target):
        target.hp_sys.effect(effects.Frozen([.1, .15, .2, .23, .25][min(4, game.get_game().stage)], 1))
        target.hp_sys.effect(effects.Wither(5, [10, 30, 60, 100, 500][min(4, game.get_game().stage)]))
        target.hp_sys.effect(effects.BleedingR(5, [10, 30, 60, 100, 500][min(4, game.get_game().stage)]))

    def on_attack(self):
        super().on_attack()
        self.scale = (self.scale * 7 + self.t_scale * (5 - 4 * 1.2 ** -(self.tr / 50))) / 8
        self.rotate(4 * (1 - 1.2 ** -(self.tr / 50)) * self.rot_speed)

    def on_special_attack(self, strike: int):
        super().on_special_attack(strike)
        pr = - game.get_game().player.obj.pos + position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
        if abs(pr):
            self.vel += pr / 10 / abs(pr) * min(abs(pr), [500, 1200, 3000, 5000, constants.INFINITY][min(4, game.get_game().stage)])
        self.tr = strike

    def on_idle(self):
        super().on_idle()
        self.scale = 2
        self.tr = 0

class MagicBlade(Blade):
    def on_start_attack(self):
        r = self.rot_speed // abs(self.rot_speed)
        px, py = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        self.face_to(px, py)
        self.rotate(abs(self.st_pos) * r)
        self.rot_speed = abs(self.rot_speed) * -r

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(4, (255, 255, 0), (255, 255, 255))


class Volcano(Blade):
    def on_start_attack(self):
        for e in game.get_game().entities:
            px, py = e.obj.pos
            if vector.distance(px - game.get_game().player.obj.pos[0], py - game.get_game().player.obj.pos[1]) < 300:
                e.hp_sys.effect(effects.Burning(5, 15))

class Guardian(Blade):
    def __init__(self, *args):
        super().__init__(*args)
        self.tt = 0
        self.at = 0

    def update(self):
        super().update()
        self.tt += 1
        if self.tt % 15 == 0:
            self.at = max(0, self.at - 1)
        self.damages[dmg.DamageTypes.PHYSICAL] = 100 + 5 * self.at

    def on_damage(self, target):
        super().on_damage(target)
        self.at = min(60, self.at + 1)


class JevilKnife(Blade):
    def on_attack(self):
        self.rotate(-int((self.timer - self.at_time / 2) * 10))
        super().on_attack()
        self.cutting_effect(10, (0, 0, 0), (200, 255, 100))

class NightsEdge(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, double_sided)
        self.rots = []
        self.lrot = 0
        self.sc = 0

    def on_start_attack(self):
        if self.strike < 50:
            self.img_index = 'items_weapons_nights_edge'
        else:
            self.img_index = 'items_weapons_nights_edge_charged'
        self.sc = (self.sc + 1) % 4
        self.rots = []
        super().on_start_attack()
        if game.get_game().day_time > 0.75 or game.get_game().day_time < 0.2:
            self.at_time = 10
            self.rot_speed = 36
            spd = 1600
            self.damages = {dmg.DamageTypes.PHYSICAL: 140}
        else:
            self.at_time = 18
            self.rot_speed = 40
            spd = 4000
            self.damages = {dmg.DamageTypes.PHYSICAL: 90}
        if self.sc == 3:
            spd *= 1.5
        px, py = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        r = -1 if px > 0 else 1
        vx, vy = vector.rotation_coordinate(self.rot - 100 * r)
        ne = projectiles.Projectiles.NightsEdge if self.sc != 3 and self.strike < 50 else projectiles.Projectiles.BNightsEdge
        n = ne((self.x + game.get_game().player.obj.pos[0] + vx * 200, self.y + game.get_game().player.obj.pos[1] + vy * 200),
               self.rot - r * 100)
        n.obj.apply_force(vector.Vector(self.rot - 100 * r, spd))
        n.set_rotation(self.rot)
        game.get_game().projectiles.append(n)
        if self.strike >= 50:
            for ar in range(90, 361, 90):
                n = ne(game.get_game().player.obj.pos + (self.x, self.y) + vector.polar_to_cartesian(self.rot - 100 * r + ar, 200),
                       self.rot - r * 100 + ar)
                n.obj.apply_force(vector.Vector2D(self.rot - 100 * r, spd))
                n.set_rotation(self.rot)
                game.get_game().projectiles.append(n)
        self.lrot = self.rot
        if self.sc == 3:
            self.timer *= 2


    def on_attack(self):
        self.rotate(int(-(self.timer - self.at_time / 2) * -5))
        super().on_attack()
        self.cutting_effect(4, (100, 0, 100), (255, 100, 255))

class Valkyrien(Spear):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ht = 0
        self.sr = 0

    def on_start_attack(self):
        super().on_start_attack()
        self.ht = 1
        self.sr = self.rot

    def on_damage(self, target):
        self.ht = 0

    def on_attack(self):
        super().on_attack()
        game.get_game().player.obj.apply_force(vector.Vector2D(self.sr, game.get_game().player.obj.SPEED * 3 * [-1, 1][self.ht]))

class Poseidon(Spear):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ht = 0
        self.sr = 0

    def on_start_attack(self):
        super().on_start_attack()
        self.ht = 1
        self.sr = self.rot

    def on_special_attack(self, strike: int):
        super().on_special_attack(strike)
        if self.strike > 50:
            self.ht += 1

    def on_damage(self, target):
        self.ht = max(0, self.ht - 1)
        dt = 1
        if game.get_game().get_biome() in ['ocean', 'fallen_sea', 'hot_spring']:
            dt *= 2
        target.hp_sys.effect(effects.Poison(4, 40 * dt - 25))
        if dt > 1:
            target.hp_sys.effect(effects.Freezing(.1, 1))
        game.get_game().player.hp_sys.enable_immune(3 * dt - 1)

    def on_attack(self):
        super().on_attack()
        dt = 1
        if game.get_game().get_biome() in ['ocean', 'fallen_sea', 'hot_spring']:
            dt *= 2
        game.get_game().player.obj.apply_force(vector.Vector2D(self.sr, game.get_game().player.obj.SPEED * dt * 3 * [-1, .5, 1][self.ht]))


class Seaprick(Spear):
    def on_damage(self, target):
        target.hp_sys.effect(effects.Poison(4, 15))

class SpiritualStabber(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, double_sided)
        self.rots = []
        self.lrot = 0

    def on_attack(self):
        self.rotate(int(-(self.timer - self.at_time / 2) * -1))
        super().on_attack()
        """
        for i in range(5):
            self.rot %= 360
            self.lrot %= 360
            if self.rot - self.lrot > 180:
                self.lrot += 360
            if self.lrot - self.rot > 180:
                self.rot += 360
            r = self.lrot + (self.rot - self.lrot) * i // 4
            vx, vy = vector.rotation_coordinate(r)
            self.rots.append((vx, vy))
            if len(self.rots) > 20:
                self.rots.pop(0)
        for j in range(64):
            i = j / 10
            d = (200 - i * 23) / game.get_game().player.get_screen_scale()
            eff.pointed_curve((100 + int(i * 12), 200, 200),
                              [(vx * d + game.get_game().player.obj.pos[0], vy * d + game.get_game().player.obj.pos[1])
                               for vx, vy in self.rots[:-3]], 3, salpha=int(120 - i * 15))
            self.lrot = self.rot 
        """
        self.cutting_effect(6, (100, 100, 255), (255, 255, 255))

class BalancedStabber(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, double_sided)
        self.rots = []
        self.lrot = 0

    def on_attack(self):
        self.rotate(int(-(self.timer - self.at_time / 2) * -1))
        super().on_attack()
        self.cutting_effect(6, (50, 0, 50), (100, 255, 100))

class DoctorExpeller(Blade):
    def on_start_attack(self):
        super().on_start_attack()
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        rot = vector.coordinate_rotation(mx, my)
        game.get_game().projectiles.append(projectiles.Projectiles.Apple(game.get_game().player.obj.pos, rot))
        game.get_game().projectiles.append(projectiles.Projectiles.Apple(game.get_game().player.obj.pos, rot - 20))
        game.get_game().projectiles.append(projectiles.Projectiles.Apple(game.get_game().player.obj.pos, rot + 20))

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(8, (255, 0, 0), (0, 127, 0))

class VirusDefeater(Blade):
    def on_start_attack(self):
        super().on_start_attack()
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        rot = vector.coordinate_rotation(mx, my)
        game.get_game().projectiles.append(projectiles.Projectiles.FApple(game.get_game().player.obj.pos, rot))
        game.get_game().projectiles.append(projectiles.Projectiles.FApple(game.get_game().player.obj.pos, rot - 20))
        game.get_game().projectiles.append(projectiles.Projectiles.FApple(game.get_game().player.obj.pos, rot + 20))

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(16, (0, 0, 255), (100, 255, 255))

class Excalibur(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, double_sided)
        self.rots = []
        self.lrot = 0
        self.cnt = 0

    def on_start_attack(self):
        self.rots = []
        super().on_start_attack()
        px, py = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        r = -1 if px > 0 else 1
        vx, vy = vector.rotation_coordinate(self.rot - 180 * r)
        for ar in range(-30, 31, 10 if not self.cnt else 30):
            n = projectiles.Projectiles.Excalibur((self.x + game.get_game().player.obj.pos[0] + vx * 200,
                                                   self.y + game.get_game().player.obj.pos[1] + vy * 200),
                                                  self.rot - r * 180 + ar)
            n.obj.apply_force(vector.Vector(self.rot - 180 * r + ar, 1500 if self.cnt else 2500))
            n.set_rotation(self.rot)
            game.get_game().projectiles.append(n)
        if self.cnt == 0:
            self.cnt = 2
        else:
            self.cnt -= 1
            self.timer //= 2

    def on_attack(self):
        self.rotate(int(-(self.timer - self.at_time / 2) * -15))
        super().on_attack()
        self.cutting_effect(8, (255, 180, 127), (255, 200, 200))


class TrueExcalibur(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, double_sided)
        self.rots = []
        self.lrot = 0
        self.cnt = 0

    def on_start_attack(self):
        self.rots = []
        super().on_start_attack()
        px, py = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        r = -1 if px > 0 else 1
        vx, vy = vector.rotation_coordinate(self.rot - 180 * r)
        if self.cnt == 0:
            self.cnt = 3
        else:
            self.cnt -= 1
        for ar in range(-80, 81, 8 if not self.cnt else 20):
            n = projectiles.Projectiles.TrueExcalibur((self.x + game.get_game().player.obj.pos[0] + vx * 200,
                                                       self.y + game.get_game().player.obj.pos[1] + vy * 200),
                                                      self.rot - r * 180 + ar)
            n.obj.apply_force(vector.Vector(self.rot - 180 * r + ar, 2000 if self.cnt else 3500))
            n.set_rotation(self.rot)
            game.get_game().projectiles.append(n)

    def on_attack(self):
        self.rotate(int(-(self.timer - self.at_time / 2) * -15))
        super().on_attack()
        self.cutting_effect(8, (255, 180, 127), (255, 200, 200))


class TrueNightsEdge(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, double_sided)
        self.rots = []
        self.lrot = 0

    def on_start_attack(self):
        self.rots = []
        super().on_start_attack()
        if game.get_game().day_time > 0.75 or game.get_game().day_time < 0.2:
            self.at_time = 32
            self.rot_speed = 60
            spd = 1600
            self.damages = {dmg.DamageTypes.PHYSICAL: 90, dmg.DamageTypes.MAGICAL: 90}
        else:
            self.at_time = 32
            self.rot_speed = 40
            spd = 4000
            self.damages = {dmg.DamageTypes.PHYSICAL: 180, dmg.DamageTypes.MAGICAL: 120}
        px, py = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        r = -1 if px > 0 else 1
        vx, vy = vector.rotation_coordinate(self.rot - 100 * r)
        n = projectiles.Projectiles.TrueNightsEdge((self.x + game.get_game().player.obj.pos[0] + vx * 200,
                                                    self.y + game.get_game().player.obj.pos[1] + vy * 200),
                                                   self.rot - r * 100)
        n.obj.apply_force(vector.Vector(self.rot - 100 * r, spd))
        n.set_rotation(self.rot)
        game.get_game().projectiles.append(n)
        self.lrot = self.rot

    def on_attack(self):
        self.rotate(int(-(self.timer - self.at_time / 2) * -5))
        super().on_attack()
        self.cutting_effect(8, (100, 0, 100), (255, 100, 127))

class WilsonKnifeBlade(Blade):
    def on_start_attack(self):
        super().on_start_attack()
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        rot = vector.coordinate_rotation(mx, my)
        game.get_game().projectiles.append(projectiles.Projectiles.WilsonKnifeCut(game.get_game().player.obj.pos, rot))

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(8, (50, 50, 50), (200, 255, 100))

class WilsonKnifeSpear(Spear):
    def on_start_attack(self):
        super().on_start_attack()
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        rot = vector.coordinate_rotation(mx, my)
        game.get_game().projectiles.append(projectiles.Projectiles.WilsonKnife(game.get_game().player.obj.pos, rot))


class MillenniumPersistSweep(SweepWeapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, double_sided)
        self.rr = False

    def on_start_attack(self):
        self.rr = not self.rr
        super().on_start_attack(rr=[-1, 1][self.rr])

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(16, (255, 100, 255), (100, 200, 255))

class Muramasa(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False, _type = 0):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, double_sided)
        self.ppos = [[] for _ in range(80)]
        self.wt = 0
        self.at_r = 0
        self.t = _type
        self.sk_mcd = 30 - _type * 18
        self.lrot = 0

    def on_start_attack(self):
        self.at_r = (self.at_r + 1) % 3
        self.wt = 0
        super().on_start_attack()

    def update(self, f=0):
        self.display = True
        if self.t:
            self.cutting_effect(8, (255, 20, 20), (50, 20, 20))
        else:
            self.cutting_effect(8, (0, 0, 90), (150, 150, 255))
        super().update()
        if pg.K_q in game.get_game().get_pressed_keys() and not f and not self.sk_cd:
            window = pg.display.get_surface()
            if constants.USE_ALPHA:
                sf = pg.Surface((window.get_width(), window.get_height()))
                sf.fill((255, 0, 0) if self.t else (0, 255, 0))
                sf.set_alpha(128)
                window.blit(sf, (0, 0))
            pg.display.update()
            for __ in range(2):
                self.attack()
                for _ in range(self.at_time):
                    self.update(1)
            self.sk_cd = self.sk_mcd

    def on_idle(self):
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        rot = vector.coordinate_rotation(mx, my)
        rot = (360 + rot % 360) % 360
        if rot > 270:
            rot = 180 - rot
        if rot < 90:
            rot = 180 - rot
        rot = 360 - rot
        self.set_rotation((self.rot + rot) // 2)
        self.x //= 2
        self.y //= 2
        super().on_idle()

    def on_attack(self):
        if self.at_r == 0:
            self.x //= 2
            self.y //= 2
            self.rotate(int(-(self.timer - self.at_time / 2) * -12))
        else:
            mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
            dt = math.sqrt(mx ** 2 + my ** 2) if self.t else 500
            mx /= math.sqrt(mx ** 2 + my ** 2) / dt / game.get_game().player.get_screen_scale()
            my /= math.sqrt(mx ** 2 + my ** 2) / dt / game.get_game().player.get_screen_scale()
            rr = 4 if self.t else 1
            self.x = (self.x + mx * rr) // (1 + rr)
            self.y = (self.y + my * rr) // (1 + rr)
        super().on_attack()

class TheBlade(Blade):
    ATTACK_SOUND = 'attack_energy'

    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, double_sided)
        self.ppos = [[] for _ in range(80)]
        self.wt = 0
        self.at_r = 0
        self.sk_mcd = 80
        self.lrot = 0

    def on_start_attack(self):
        if self.sk_cd:
            self.at_r = (self.at_r + 1) % 16
        else:
            self.at_r = 14
        self.sk_cd = self.sk_mcd
        self.wt = 0
        super().on_start_attack()

    def update(self):
        self.display = True
        self.cutting_effect(8, (0, 80, 0), (200, 255, 200))
        """
        for j in range(80):
            i = j / 10
            d = 260 - i * 23
            ax, ay = vector.rotation_coordinate(self.rot)
            self.ppos[j].append((ax * d + game.get_game().player.obj.pos[0] + self.x,
                                 ay * d + game.get_game().player.obj.pos[1] + self.y))
            if len(self.ppos[j]) > 6:
                self.ppos[j].pop(0)
            eff.pointed_curve((int(i * 25), 80 + int(i * 20), int(i * 25)), self.ppos[j], 3,
                              salpha=int(120 - i * 15))
        """
        super().update()

    def on_idle(self):
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        rot = vector.coordinate_rotation(mx, my)
        rot = (360 + rot % 360) % 360
        if rot > 270:
            rot = 180 - rot
        if rot < 90:
            rot = 180 - rot
        rot = 360 - rot
        self.set_rotation((self.rot + rot) // 2)
        self.x //= 2
        self.y //= 2
        super().on_idle()

    def on_attack(self):
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        if self.at_r == 14:
            self.x //= 3
            self.y //= 3
            self.rotate(int(-(self.timer - self.at_time / 2) * -32))
        elif self.at_r == 15:
            self.x //= 5
            self.y //= 5
            self.rotate(int(-(self.timer - self.at_time / 2) * 32))
        elif self.at_r % 4 < 2:
            self.x //= 2
            self.y //= 2
            self.rotate(int(-(self.timer - self.at_time / 2) * -16))
        else:
            self.x = (self.x + mx) // 2
            self.y = (self.y + my) // 2
        if 4 <= self.wt and self.at_r % 4 > 1 and self.at_r <= 13:
            if self.wt % 2 == 0:
                for _ in range(self.wt // 3 + 1):
                    game.get_game().projectiles.append(
                        projectiles.Projectiles.BladeBeamSmall((self.x + game.get_game().player.obj.pos[0],
                                                                self.y + game.get_game().player.obj.pos[1]),
                                                               random.randint(0, 360)))
        if self.wt == 4:
            rot = vector.coordinate_rotation(mx, my)
            if self.at_r == 13:
                for r in range(-30, 31, 15):
                    game.get_game().projectiles.append(
                        projectiles.Projectiles.BladeBeam((self.x + game.get_game().player.obj.pos[0],
                                                            self.y + game.get_game().player.obj.pos[1]),
                                                           rot + r))
            elif self.at_r == 15:
                for r in range(-180, 181, 18):
                    game.get_game().projectiles.append(
                        projectiles.Projectiles.BladeBeam((self.x + game.get_game().player.obj.pos[0],
                                                            self.y + game.get_game().player.obj.pos[1]),
                                                           rot + r))
            elif self.at_r > 13:
                pass
            elif self.at_r % 4 == 0:
                game.get_game().projectiles.append(
                    projectiles.Projectiles.BladeBeam((self.x + game.get_game().player.obj.pos[0],
                                                        self.y + game.get_game().player.obj.pos[1]),
                                                       rot))
            elif self.at_r % 4 == 1:
                game.get_game().projectiles.append(
                    projectiles.Projectiles.BladeBeam((self.x + game.get_game().player.obj.pos[0],
                                                        self.y + game.get_game().player.obj.pos[1]),
                                                       rot - 10))
                game.get_game().projectiles.append(
                    projectiles.Projectiles.BladeBeam((self.x + game.get_game().player.obj.pos[0],
                                                        self.y + game.get_game().player.obj.pos[1]),
                                                       rot))
                game.get_game().projectiles.append(
                    projectiles.Projectiles.BladeBeam((self.x + game.get_game().player.obj.pos[0],
                                                        self.y + game.get_game().player.obj.pos[1]),
                                                       rot + 10))
        self.wt += 1
        super().on_attack()

class UncannyValley(Blade):
    def on_start_attack(self):
        super().on_start_attack()
        if not self.sk_cd:
            self.sk_cd = self.sk_mcd
            game.get_game().displayer.effect(pef.p_particle_effects(*game.get_game().displayer.reflect(*pg.mouse.get_pos()),
                                                                    col=(100, 255, 100)))
            mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
            self.x, self.y = mx * game.get_game().player.get_screen_scale(), my * game.get_game().player.get_screen_scale()

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(8, (100, 255, 100), (0, 0, 0))

    def update(self):
        super().update()
        self.sk_mcd = 12
        self.x = self.x * 48 // 49
        self.y = self.y * 48 // 49

class HourHand(Blade):
    def on_attack(self):
        super().on_attack()
        self.cutting_effect(16, (255, 180, 100), (255, 255, 255))
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        self.x = (self.x + mx * game.get_game().player.get_screen_scale()) // 2
        self.y = (self.y + my * game.get_game().player.get_screen_scale()) // 2

    def on_start_attack(self):
        super().on_start_attack()
        if not self.sk_cd:
            self.sk_cd = self.sk_mcd
            self.timer *= 2

    def update(self):
        super().update()
        self.sk_mcd = 200

    def on_idle(self):
        self.x //= 2
        self.y //= 2
        super().on_idle()

class Starfury(Blade):
    def on_start_attack(self):
        super().on_start_attack()
        t = 1 + (not self.sk_cd) * 2
        for _ in range(t):
            game.get_game().projectiles.append(projectiles.Projectiles.Starfury((0, 0),
                                                                                self.rot))
        if t > 1:
            self.sk_cd = self.sk_mcd

    def update(self):
        super().update()
        self.sk_mcd = 30

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(4, (255, 255, 0), (255, 255, 255))

class StarWrath(Blade):
    def on_start_attack(self):
        super().on_start_attack()
        t = 3 + (not self.sk_cd) * 6
        for _ in range(t):
            game.get_game().projectiles.append(projectiles.Projectiles.StarWrath((random.randint(-200, 200),
                                                                                 random.randint(-200, 200)),
                                                                                self.rot))
        if t > 3:
            self.sk_cd = self.sk_mcd

    def update(self):
        super().update()
        self.sk_mcd = 20

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(8, (255, 255, 0), (255, 255, 255))

class Deconstruction(Blade):
    def on_start_attack(self):
        super().on_start_attack()
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        game.get_game().projectiles.append(projectiles.Projectiles.Deconstruction((self.x + game.get_game().player.obj.pos[0],
                                                                                   self.y + game.get_game().player.obj.pos[1]),
                                                                                  vector.coordinate_rotation(mx, my)))

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(8, (20, 0, 50), (0, 0, 255))

class Lysis(Blade):
    def on_start_attack(self):
        super().on_start_attack()
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        game.get_game().projectiles.append(projectiles.Projectiles.Lysis((self.x + game.get_game().player.obj.pos[0],
                                                                                self.y + game.get_game().player.obj.pos[1]),
                                                                                vector.coordinate_rotation(mx, my)))

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(8, (200, 200, 255), (0, 0, 255))

class QuarkRusher(Blade):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.st = 0

    def on_start_attack(self):
        self.st = 0
        super().on_start_attack()

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(8, (0, 255, 255), (127, 200, 200))
        mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
        mx -= game.get_game().player.obj.pos[0]
        my -= game.get_game().player.obj.pos[1]
        self.x = (self.x + mx) // 2
        self.y = (self.y + my) // 2
        if self.st < 10:
            pass
        elif self.st < 25:
            self.rotate(self.rot_speed)
        elif self.st == 25:
            qb = projectiles.Projectiles.QuarkBeam(game.get_game().player.obj.pos, vector.coordinate_rotation(mx, my))
            qb.LENGTH = vector.distance(mx, my)
            game.get_game().projectiles.append(qb)
            game.get_game().player.obj.pos << position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            game.get_game().player.obj.velocity.add(vector.Vector(vector.coordinate_rotation(mx, my), 20))
        self.st += 1

class EHighlight(Spear):
    ENABLE_IMMUNE = False

    def on_start_attack(self):
        self.img.set_alpha(120)
        super().on_start_attack()

class Highlight(Spear):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, forward_speed: int,
                 st_pos: int, auto_fire: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, forward_speed, st_pos, auto_fire)
        ss = [EHighlight(name, damages, kb, 'projectiles_highlight_' + c, speed, at_time, forward_speed * 2, 0, auto_fire)
               for c in ['r', 'o', 'y', 'g', 'c', 'b', 'p'] for _ in range(9)]
        self.es = ss
        for s in ss:
            s.keys = []

    def on_attack(self):
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        rot = vector.coordinate_rotation(mx, my)
        super().on_attack()
        self.set_rotation(rot + random.randint(-10, 10))
        flow = random.randint(1, 3)
        for c in self.es[:flow]:
            c.attack()
            c.forward(10)
            c.set_rotation(rot + random.randint(-10, 10))
        for _ in range(flow):
            self.es.append(self.es.pop(0))

    def update(self):
        super().update()
        for c in self.es:
            c.update()

class EGalaxyBroadsword(Blade):
    def on_attack(self):
        super().on_attack()
        self.display = False
        self.cutting_effect(16, (255, 191, 63), (255, 0, 0))

class GalaxyBroadsword(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, double_sided)
        self.effs = []
        self.ci = None

    def update(self):
        super().update()
        for e in self.effs:
            e.update()
            if not e.timer:
                self.effs.remove(e)

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(16, (255, 191, 63), (255, 0, 0))

    def on_end_attack(self):
        if self.ci is None:
            self.ci = copy.copy(self.img)
            self.ci.set_alpha(100)
            game.get_game().graphics['weff_' + self.name] = self.ci
        super().on_end_attack()
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        md = vector.distance(mx, my)
        weff = EGalaxyBroadsword(self.name, self.damages, self.knock_back * 2,
                                'weff_' + self.name, 0, self.at_time,
                                abs(self.rot_speed), abs(self.st_pos))
        weff.x = mx * game.get_game().player.get_screen_scale() - 50 * mx / md
        weff.y = my * game.get_game().player.get_screen_scale() - 50 * my / md
        weff.attack()
        weff.keys = []
        self.effs.append(weff)

class EEternalEcho(Blade):
    def on_attack(self):
        super().on_attack()
        self.display = False
        self.cutting_effect(16, (200, 255, 255), (255, 0, 0))
        if self.timer > self.at_time * 2 / 3:
            mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
            mx *= game.get_game().player.get_screen_scale()
            my *= game.get_game().player.get_screen_scale()
            self.x = (self.x + mx) / 2
            self.y = (self.y + my) / 2
        else:
            self.x /= 2
            self.y /= 2

    def damage(self):
        for e in game.get_game().entities:
            dps = e.obj.pos
            px = dps[0] - self.x - game.get_game().player.obj.pos[0]
            py = dps[1] - self.y - game.get_game().player.obj.pos[1]
            if vector.distance(px, py) < self.img.get_width() + (
            (e.img.get_width() + e.img.get_height()) // 2 if e.img is not None else 10):
                for t, d in self.damages.items():
                    e.hp_sys.damage(d * game.get_game().player.attack * game.get_game().player.attacks[self.DMG_AS_IDX], t)
                if not e.hp_sys.is_immune:
                    rf = vector.coordinate_rotation(px + self.x, py + self.y)
                    e.obj.apply_force(vector.Vector(rf, min(self.knock_back * 120000 / e.obj.MASS, e.obj.MASS * 24)))
                if 'matters_touch' in game.get_game().player.accessories:
                    e.obj.MASS *= 1.01
                if 'grasp_of_the_infinite_corridor' in game.get_game().player.accessories:
                    if not e.IS_MENACE:
                        e.hp_sys.damage(e.hp_sys.max_hp / 10, dmg.DamageTypes.THINKING)
                        if random.randint(0, 10) == 0:
                            e.hp_sys.hp = 0
                    else:
                        e.hp_sys.damage(max(e.hp_sys.max_hp / 1000, 10000), dmg.DamageTypes.THINKING)
                if self.ENABLE_IMMUNE:
                    e.hp_sys.enable_immune()

class EternalEcho(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time * 5, rot_speed, st_pos, double_sided)
        self.effs = []
        self.ci = None
        self.tt = 0

    def update(self):
        super().update()
        for e in self.effs:
            e.update()
            if not e.timer:
                self.effs.remove(e)

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(16, (200, 255, 255), (255, 0, 0))

    def on_end_attack(self):
        self.tt = (self.tt + 1) % 3
        if self.ci is None:
            self.ci = copy.copy(self.img)
            self.ci.set_alpha(100)
            game.get_game().graphics['weff_' + self.name] = self.ci
        super().on_end_attack()
        if self.tt == 1:
            weff = EEternalEcho(self.name, self.damages, self.knock_back * 2,
                                    'weff_' + self.name, 0, self.at_time * 2,
                                    abs(self.rot_speed), abs(self.st_pos))
            weff.attack()
            weff.keys = []
            self.effs.append(weff)

class EStarOfDevotion(Blade):
    def on_attack(self):
        super().on_attack()
        self.display = False
        self.cutting_effect(16, (255, 255, 180), (255, 0, 0))

class StarOfDevotion(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, double_sided: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, double_sided)
        self.effs = []
        self.ci = None

    def update(self):
        super().update()
        for e in self.effs:
            e.update()
            if not e.timer:
                self.effs.remove(e)

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(16, (255, 255, 180), (255, 0, 0))

    def on_end_attack(self):
        if self.ci is None:
            self.ci = copy.copy(self.img)
            self.ci.set_alpha(100)
            game.get_game().graphics['weff_' + self.name] = self.ci
        super().on_end_attack()
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        weff = EStarOfDevotion(self.name, self.damages, self.knock_back * 2,
                                'weff_' + self.name, 0, self.at_time,
                                abs(self.rot_speed), abs(self.st_pos))
        weff.x = mx / (mx ** 2 + my ** 2) ** .5 * 480
        weff.y = my / (mx ** 2 + my ** 2) ** .5 * 480
        weff.attack()
        weff.keys = []
        self.effs.append(weff)

class TurningPointSweep(Blade):
    def on_attack(self):
        super().on_attack()
        self.cutting_effect(16, (255, 191, 63), (255, 0, 0))

    def on_start_attack(self):
        super().on_start_attack()
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        self.face_to(mx, my)
        for ar in range(-30, 31, 15):
            game.get_game().projectiles.append(projectiles.Projectiles.TurningPoint((self.x + game.get_game().player.obj.pos[0],
                                                                                     self.y + game.get_game().player.obj.pos[1]),
                                                                                     self.rot + ar))

class TurningPointSpear(Spear):
    def on_start_attack(self):
        super().on_start_attack()
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        self.face_to(mx, my)
        game.get_game().projectiles.append(projectiles.Projectiles.TurningPoint((self.x + game.get_game().player.obj.pos[0],
                                                                                 self.y + game.get_game().player.obj.pos[1]),
                                                                                 self.rot))

class EZenith(Blade):
    ENABLE_IMMUNE = False

    NAMES = ['copper_sword', 'platinum_sword', 'magic_sword', 'volcano', 'doctor_expeller', 'sand_sword', 'nights_edge',
             'spiritual_stabber', 'balanced_stabber', 'excalibur', 'remote_sword', 'muramasa', 'perseverance_sword', 'black_hole_sword',
             'true_nights_edge', 'true_excalibur', 'life_devourer', 'jevil_knife', 'demon_blade__muramasa', 'the_blade',
             'uncanny_valley', 'star_wrath', 'lysis', 'galaxy_broadsword', 'turning_point', 'zenith']
    COLS = [[(127, 100, 100), (50, 0, 20)], [(200, 200, 255), (100, 100, 127)], [(200, 255, 255), (0, 50, 50)],
            [(255, 0, 0), (50, 0, 0)], [(255, 0, 0), (0, 127, 0)], [(255, 255, 200), (50, 50, 0)],
            [(255, 200, 255), (50, 0, 50)], [(200, 200, 255), (0, 0, 50)], [(0, 0, 255), (50, 0, 50)],
            [(255, 255, 100), (100, 100, 0)], [(200, 200, 200), (50, 50, 50)], [(0, 0, 255), (0, 0, 50)],
            [(255, 0, 255), (50, 0, 50)], [(255, 0, 255), (0, 0, 0)], [(255, 100, 255), (50, 0, 50)],
            [(255, 255, 100), (100, 100, 0)], [(100, 255, 100), (0, 255, 0)], [(0, 0, 0), (255, 255, 255)],
            [(255, 0, 0), (50, 0, 0)], [(100, 255, 100), (0, 255, 0)], [(200, 255, 200), (0, 255, 0)],
            [(255, 100, 200), (100, 0, 50)], [(0, 0, 255), (0, 0, 50)], [(255, 0, 0), (200, 200, 100)],
            [(255, 200, 200), (255, 0, 0)], [(200, 200, 255), (0, 0, 50)]]

    def __init__(self, name, damages: dict[int, float], kb: float, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, idx: int):
        self.idx = idx
        self.arc = 0.5
        self.tick = 0
        self.ueff = True
        super().__init__(name, damages, kb, 'items_weapons_' + self.NAMES[idx] + '_zenith', speed, at_time, rot_speed, st_pos)

    def on_start_attack(self):
        super().on_start_attack()
        self.tick = 0
        self.arc = (0.1 + random.random() * 0.3) * random.choice([-1, 1])
        if (self.arc < 0) != (self.rot_speed > 0):
            self.rot_speed *= -1
            self.rot = (self.rot + self.st_pos * 2) % 360
        for a in self.aposs:
            a.clear()

    def on_attack(self):
        super().on_attack()
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        mx *= game.get_game().player.get_screen_scale()
        my *= game.get_game().player.get_screen_scale()
        dt = vector.distance(mx, my)
        rt = vector.coordinate_rotation(mx, my)
        ax, ay = vector.rotation_coordinate(rt)
        dax, day = vector.rotation_coordinate(rt + 90)
        self.tick += 1
        if self.tick < 5:
            sc = math.sin(math.pi * self.tick / 5)
            self.x = ax * dt * self.tick / 5 + sc * dax * self.arc * dt
            self.y = ay * dt * self.tick / 5 + sc * day * self.arc * dt
        else:
            self.x = ax * dt
            self.y = ay * dt
        if self.ueff:
            self.activated_cutting_effect(8, self.COLS[self.idx][0], self.COLS[self.idx][1], 4)

    def on_idle(self):
        self.x //= 2
        self.y //= 2
        super().on_idle()
        self.display = abs(self.x) > 50 or abs(self.y) > 50

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
                        e.hp_sys.damage(d * game.get_game().player.attack * game.get_game().player.attacks[self.DMG_AS_IDX], t)
                    if not e.hp_sys.is_immune:
                        rf = vector.coordinate_rotation(px + self.x, py + self.y)
                        e.obj.apply_force(vector.Vector(rf, min(self.knock_back * 120000 / e.obj.MASS, e.obj.MASS * 24)
                                                        if self.knock_back * 60000 < e.obj.MASS or constants.DIFFICULTY <= 1 else
                                                        min(self.knock_back * 600000 / e.obj.MASS, e.obj.MASS * 24)))
                    if 'matters_touch' in game.get_game().player.accessories:
                        e.obj.MASS *= 1.01
                    if 'grasp_of_the_infinite_corridor' in game.get_game().player.accessories:
                        if not e.IS_MENACE and not e.VITAL:
                            e.hp_sys.damage(e.hp_sys.max_hp / 10, dmg.DamageTypes.THINKING)
                            if random.randint(0, 10) == 0:
                                e.hp_sys.hp = 0
                        else:
                            e.hp_sys.damage(max(e.hp_sys.max_hp / 1000, 10000), dmg.DamageTypes.THINKING)
                    if self.ENABLE_IMMUNE:
                        if constants.DIFFICULTY > 1:
                            e.hp_sys.enable_immune()


class Zenith(Blade):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos)
        self.zeniths = [EZenith(name, damages, kb, speed, at_time, rot_speed, st_pos, i) for i in range(len(EZenith.NAMES))]
        for z in self.zeniths:
            z.keys = []
        self.tick = 0
        self.zeniths = self.zeniths[1::2] + self.zeniths[::2]
        random.shuffle(self.zeniths)
        self.sk_mcd = 80

    def on_start_attack(self):
        if self.sk_cd >= self.sk_mcd - self.at_time:
            self.timer = 0
        if not game.get_game().graphics.is_loaded('items_weapons_' + EZenith.NAMES[0] + '_zenith'):
            for n in EZenith.NAMES:
                game.get_game().graphics['items_weapons_' + n + '_zenith'] = pg.transform.scale(game.get_game().graphics['items_weapons_' + n], (416, 203))
        super().on_start_attack()

    def on_attack(self):
        for z in self.zeniths:
            z.ueff = self.sk_cd < self.sk_mcd - self.at_time
        super().on_attack()
        self.tick += 1
        self.cutting_effect(8, *EZenith.COLS[self.zeniths[0].idx])
        if self.tick % 2 == 0:
            self.zeniths[0].attack()
            self.zeniths[0].damages = self.damages
            self.zeniths.append(self.zeniths.pop(0))

    def update(self):
        self.damages[dmg.DamageTypes.PHYSICAL] = 45 * game.get_game().player.attack ** 2 * game.get_game().player.attacks[0]
        self.damages[dmg.DamageTypes.THINKING] = 15 * game.get_game().player.attack ** 3 * game.get_game().player.attacks[0]
        super().update()
        for z in self.zeniths:
            z.update()
        if not self.sk_cd and pg.K_q in game.get_game().get_keys():
            for z in random.choices(self.zeniths, k=random.randint(12, 25)):
                z.attack()
            self.attack()
            self.sk_cd = self.sk_mcd

class ProphecyI(Blade):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stars: list[vector.Vector2D] = []

    def update(self):
        super().update()
        r = math.sin(game.get_game().day_time / game.get_game().TIME_SPEED / 12) * 40 + 80
        r /= game.get_game().player.get_screen_scale() * 2
        for sr in self.stars:
            pg.draw.circle(game.get_game().displayer.canvas, (255, 255, 127), position.displayed_position(sr), r)

    def on_start_attack(self):
        super().on_start_attack()
        if random.randint(0, len(self.stars)) > 2:
            for sr in self.stars:
                for rr in range(0, 360, 90):
                    b = projectiles.Projectiles.GenerationBeam(sr, rr + random.randint(-10, 10))
                    b.WIDTH = 20
                    b.COLOR = (255, 255, 127)
                    b.DAMAGE_AS = 'prophecy'
                    b.DMG_TYPE = dmg.DamageTypes.PHYSICAL
                    game.get_game().projectiles.append(b)
                game.get_game().displayer.effect(fc.p_fade_circle(*position.displayed_position(sr), col=(255, 255, 127),
                                                                  sp=20, t=30, follow_map=True))
            self.stars.clear()
            self.timer *= 2
            return
        np = vector.Vector2D()
        if not len(self.stars) or not random.randint(0, 2):
            np.x = game.get_game().player.obj.pos[0] + random.randint(-800, 800)
            np.y = game.get_game().player.obj.pos[1] + random.randint(-800, 800)
        else:
            rp = random.choice(self.stars)
            pp = game.get_game().player.obj.pos
            rr = vector.cartesian_to_polar(*(pp - rp))[0] + random.randint(-30, 30)
            np = pp + vector.Vector2D(rr, random.randint(500, 1500))
        for sr in self.stars:
            b = projectiles.Projectiles.GenerationBeam(sr, vector.cartesian_to_polar(*(np - sr))[0])
            b.WIDTH = 50
            b.COLOR = (255, 255, 127)
            b.DAMAGE_AS = 'prophecy'
            b.DMG_TYPE = dmg.DamageTypes.PHYSICAL
            game.get_game().projectiles.append(b)
        self.stars.append(np)

    def on_end_attack(self):
        if self.scale > 1:
            for sr in self.stars:
                for rr in range(0, 360, 72):
                    b = projectiles.Projectiles.GenerationBeam(sr, rr + random.randint(-10, 10))
                    b.WIDTH = 30
                    b.COLOR = (255, 255, 127)
                    b.DAMAGE_AS = 'prophecy'
                    b.DMG_TYPE = dmg.DamageTypes.PHYSICAL
                    game.get_game().projectiles.append(b)
                game.get_game().displayer.effect(fc.p_fade_circle(*position.displayed_position(sr), col=(255, 255, 127),
                                                                  sp=20, t=40, follow_map=True))
            self.stars.clear()
            WEAPONS['prophecy_ii'].stars = self.stars
            game.get_game().player.weapons[game.get_game().player.sel_weapon] = WEAPONS['prophecy_ii']
        super().on_end_attack()

class ProphecyII(Spear):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stars: list[vector.Vector2D] = []

    def update(self):
        super().update()
        r = math.sin(game.get_game().day_time / game.get_game().TIME_SPEED / 12) * 40 + 80
        r /= game.get_game().player.get_screen_scale() * 2
        for sr in self.stars:
            pg.draw.circle(game.get_game().displayer.canvas, (255, 255, 127), position.displayed_position(sr), r)

    def on_start_attack(self):
        super().on_start_attack()
        if not len(self.stars):
            for i in range(4):
                sr = game.get_game().player.obj.pos + vector.Vector2D(random.randint(-1000, 1000), random.randint(-1000, 1000))
                self.stars.append(sr)
                game.get_game().displayer.effect(fc.p_fade_circle(*position.displayed_position(sr), col=(255, 255, 127),
                                                                  sp=20, t=45, follow_map=True))
            self.timer *= 3
            return
        i = random.randint(0, len(self.stars) - 1)
        for j, sr in enumerate(self.stars):
            b = projectiles.Projectiles.GenerationBeam(sr, self.rot)
            b.WIDTH = 50
            b.COLOR = (255, 255, 127)
            b.DAMAGE_AS = 'prophecy'
            b.DMG_TYPE = dmg.DamageTypes.PHYSICAL
            if j == i:
                b.WIDTH *= 3
                b.DURATION *= 2
            game.get_game().projectiles.append(b)
        self.stars.pop(i)

    def on_end_attack(self):
        if self.scale > 1:
            for i in range(max(0, 6 - len(self.stars))):
                sr = game.get_game().player.obj.pos + vector.Vector2D(random.randint(-1000, 1000), random.randint(-1000, 1000))
                self.stars.append(sr)
                game.get_game().displayer.effect(fc.p_fade_circle(*position.displayed_position(sr), col=(255, 255, 127),
                                                                  sp=20, t=45, follow_map=True))
            WEAPONS['prophecy'].stars = self.stars
            game.get_game().player.weapons[game.get_game().player.sel_weapon] = WEAPONS['prophecy']
        super().on_end_attack()

class LifeDevourer(Blade):
    def update(self):
        self.sk_mcd = 40
        super().update()
        if not self.timer and not self.cool and pg.K_q in game.get_game().get_keys() and not self.sk_cd:
            super().attack()
            self.sk_cd = self.sk_mcd
            for i in range(32):
                ax, ay = vector.rotation_coordinate(random.randint(0, 360))
                x, y = game.get_game().player.obj.pos[0] + ax * 1200, game.get_game().player.obj.pos[1] + ay * 1200
                pj = projectiles.Projectiles.LifeDevourer((x, y),
                                                          vector.coordinate_rotation(-ax, -ay) + random.randint(-5, 5))
                pj.DURATION = 16 + i // 2
                pj.WIDTH = 20
                game.get_game().projectiles.append(pj)

    def on_start_attack(self):
        super().on_start_attack()
        for i in range(random.randint(1, 3)):
            ax, ay = vector.rotation_coordinate(random.randint(0, 360))
            x, y = game.get_game().player.obj.pos[0] + ax * 1200, game.get_game().player.obj.pos[1] + ay * 1200
            pj = projectiles.Projectiles.LifeDevourer((x, y),
                                                      vector.coordinate_rotation(-ax, -ay) + random.randint(-2, 2))
            game.get_game().projectiles.append(pj)
        self.cutting_effect(6, (200, 255, 200), (0, 50, 0))


class MagicSword(AutoSweepWeapon):
    def on_end_attack(self):
        super().on_end_attack()
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        game.get_game().projectiles.append(projectiles.Projectiles.MagicSword(
            (self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1]), self.rot))

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(4, (0, 0, 100), (0, 100, 0))

class Glacier(Blade):
    def on_end_attack(self):
        super().on_end_attack()
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        for ar in range(-10, 1, 10):
            game.get_game().projectiles.append(projectiles.Projectiles.Glacier(
                (self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1]), self.rot + ar))

class FieryIceberg(Blade):
    def on_end_attack(self):
        super().on_end_attack()
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        for ar in range(-10, 11, 10):
            game.get_game().projectiles.append(projectiles.Projectiles.FieryIceberg(
                (self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1]), self.rot + ar))

class ForbiddenOath(Blade):
    def on_end_attack(self):
        super().on_end_attack()
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        for ar in range(-5, 6, 5):
            game.get_game().projectiles.append(projectiles.Projectiles.ForbiddenOath(
                (self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1]), self.rot + ar))

class RuneBlade(AutoSweepWeapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, rot_speed: int,
                 st_pos: int, auto_fire: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, auto_fire)
        self.sk_mcd = 50
        self.t = 0

    def on_end_attack(self):
        super().on_end_attack()
        self.t = not self.t
        if not self.t:
            return
        for _ in range(1 + (not self.sk_cd) * 2):
            mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            ax, ay = vector.rotation_coordinate(random.randint(0, 360))
            ax *= 250
            ay *= 250
            game.get_game().projectiles.append(projectiles.Projectiles.RuneBladeProjectile(
                (mx + ax, my + ay), vector.coordinate_rotation(-ax, -ay)))
        if not self.sk_cd:
            self.sk_cd = self.sk_mcd

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(4, (0, 0, 200), (0, 200, 200))

class FireQuenchSword(Blade):
    def on_attack(self):
        super().on_attack()
        self.cutting_effect(8, (255, 0, 0), (255, 255, 0))
        game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position((self.x + game.get_game().player.obj.pos[0],
                                                                                              self.y + game.get_game().player.obj.pos[1])),
                                                                n=6, sp=30 / game.get_game().player.get_screen_scale(),
                                                                t=20, col=(255, 0, 0)))
        for e in game.get_game().entities:
            if vector.distance(e.obj.pos[0] - self.x - game.get_game().player.obj.pos[0],
                               e.obj.pos[1] - self.y - game.get_game().player.obj.pos[1]) < 600:
                e.hp_sys.effect(effects.Burning(10, self.damages[dmg.DamageTypes.PHYSICAL] // 20))

class IceQuenchSword(Blade):
    def on_attack(self):
        super().on_attack()
        self.cutting_effect(8, (0, 100, 255), (0, 255, 255))
        game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position((self.x + game.get_game().player.obj.pos[0],
                                                                                              self.y + game.get_game().player.obj.pos[1])),
                                                                n=6, sp=30 / game.get_game().player.get_screen_scale(),
                                                                t=20, col=(0, 255, 255)))
        for e in game.get_game().entities:
            if vector.distance(e.obj.pos[0] - self.x - game.get_game().player.obj.pos[0],
                               e.obj.pos[1] - self.y - game.get_game().player.obj.pos[1]) < 600:
                e.hp_sys.effect(effects.Frozen(2, self.damages[dmg.DamageTypes.PHYSICAL] // 20))

class DarkQuenchSword(Blade):
    def on_attack(self):
        super().on_attack()
        self.cutting_effect(8, (0, 0, 0), (50, 0, 50))
        game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position((self.x + game.get_game().player.obj.pos[0],
                                                                                              self.y + game.get_game().player.obj.pos[1])),
                                                                n=6, sp=30 / game.get_game().player.get_screen_scale(),
                                                                t=20, col=(0, 0, 0)))
        for e in game.get_game().entities:
            if vector.distance(e.obj.pos[0] - self.x - game.get_game().player.obj.pos[0],
                               e.obj.pos[1] - self.y - game.get_game().player.obj.pos[1]) < 600 and random.randint(0, 15) == 0:
                e.obj.TOUCHING_DAMAGE *= .99

class LightQuenchSword(Blade):
    def on_attack(self):
        super().on_attack()
        self.cutting_effect(8, (255, 255, 200), (50, 50, 0))
        game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position((self.x + game.get_game().player.obj.pos[0],
                                                                                              self.y + game.get_game().player.obj.pos[1])),
                                                                n=6, sp=30 / game.get_game().player.get_screen_scale(),
                                                                t=20, col=(255, 255, 200)))
        for e in game.get_game().entities:
            if vector.distance(e.obj.pos[0] - self.x - game.get_game().player.obj.pos[0],
                               e.obj.pos[1] - self.y - game.get_game().player.obj.pos[1]) < 600:
                e.hp_sys.defenses[DamageTypes.PHYSICAL] -= 3.5

class EFireRulingSword(FireQuenchSword):
    def on_attack(self):
        self.x += self.ax * self.timer ** 2 / 15
        self.y += self.ay * self.timer ** 2 / 15
        super().on_attack()

class EIceRulingSword(IceQuenchSword):
    def on_attack(self):
        self.x += self.ax * self.timer ** 2 / 15
        self.y += self.ay * self.timer ** 2 / 15
        super().on_attack()

class EDarkRulingSword(DarkQuenchSword):
    def on_attack(self):
        self.x += self.ax * self.timer ** 2 / 15
        self.y += self.ay * self.timer ** 2 / 15
        super().on_attack()

class ELightRulingSword(LightQuenchSword):
    def on_attack(self):
        self.x += self.ax * self.timer ** 2 / 15
        self.y += self.ay * self.timer ** 2 / 15
        super().on_attack()

class TheRulingSword(Blade):
    counter = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.effs = []

    def on_start_attack(self):
        self.counter = (self.counter + 1) % 4
        super().on_start_attack()
        e = [EFireRulingSword, EIceRulingSword, EDarkRulingSword, ELightRulingSword][self.counter]
        en = ['img_weapons_fire_ruling_sword', 'img_weapons_ice_ruling_sword', 'img_weapons_dark_ruling_sword', 'img_weapons_light_ruling_sword'][self.counter]
        r = vector.coordinate_rotation(*position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))

        for ar in range(-30, 31, 30):
            ax, ay = vector.rotation_coordinate(r + ar)
            ee = e(self.name, self.damages, self.knock_back, en, self.cd, self.at_time, self.rot_speed, self.st_pos, self.auto_fire)
            ee.ax = ax
            ee.ay = ay
            ee.keys = []
            ee.attack()
            self.effs.append(ee)

    def update(self):
        super().update()
        self.effs = [e for e in self.effs if e.timer > 0]
        for e in self.effs:
            e.update()

    def on_attack(self):
        super().on_attack()
        self.cutting_effect(8, [(255, 0, 0), (0, 255, 255), (127, 0, 127), (255, 255, 100)][self.counter],
                            (255, 181, 112))
        game.get_game().displayer.effect(
            pef.p_particle_effects(*position.displayed_position((self.x + game.get_game().player.obj.pos[0],
                                                                 self.y + game.get_game().player.obj.pos[1])),
                                   n=3, sp=10 / game.get_game().player.get_screen_scale(),
                                   t=60, col=[(255, 0, 0), (0, 255, 255), (127, 0, 127), (255, 255, 100)][self.counter], g=.02))
        for e in game.get_game().entities:
            if vector.distance(e.obj.pos[0] - self.x - game.get_game().player.obj.pos[0],
                               e.obj.pos[1] - self.y - game.get_game().player.obj.pos[1]) < 600:
                if self.counter == 0:
                    e.hp_sys.effect(effects.Burning(30, self.damages[dmg.DamageTypes.PHYSICAL] // 15))
                elif self.counter == 1:
                    e.hp_sys.effect(effects.Frozen(self.damages[dmg.DamageTypes.PHYSICAL] / 1200, 1))
                elif self.counter == 2:
                    e.obj.TOUCHING_DAMAGE *= .96
                else:
                    e.hp_sys.defenses[DamageTypes.PHYSICAL] -= 5

class MagicWeapon(Weapon):
    ATTACK_SOUND = 'attack_magic'

    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int,
                 projectile: type(projectiles.Projectiles.Projectile), mana_cost: int, auto_fire: bool = False, spell_name = '',
                 arcane_sound=0):
        if arcane_sound:
            self.ATTACK_SOUND = 'attack_arcane'
        if speed + at_time > 3:
            super().__init__(name, damages, kb, img, 0, at_time, auto_fire)
        else:
            super().__init__(name, damages, kb, img, speed, at_time, auto_fire)
        self.projectile = projectile
        self.spell_name = spell_name
        self.mana_cost = mana_cost
        if speed > 3:
            self.sk_mcd = speed

    def on_start_attack(self):
        if game.get_game().player.mana < round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1):
            self.timer = 0
            return
        if self.sk_cd:
            self.timer = 0
            return
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)
        game.get_game().player.hp_sys.effect(effects.WeakManaI([.5, 1, 3, 6][constants.DIFFICULTY], 1))
        if constants.DIFFICULTY:
            game.get_game().player.hp_sys.effect(effects.ManaDrain([0, 3, 6, 10][constants.DIFFICULTY], 1))


    def on_attack(self):
        super().on_attack()
        if self.sk_mcd:
            self.sk_cd = (self.at_time - self.timer) * self.sk_mcd / self.at_time
            pg.draw.circle(game.get_game().displayer.canvas, self.projectile.COL if 'COL' in dir(self.projectile) else (255, 255, 255),
                            position.displayed_position((self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1])),
                           int(150 * (self.timer / self.at_time) ** .7 / game.get_game().player.get_screen_scale()), 3)

    def on_end_attack(self):
        self.sk_cd = self.sk_mcd
        super().on_end_attack()
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        game.get_game().projectiles.append(
            self.projectile((self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1]),
                            self.rot))

class PoetWeapon(MagicWeapon):
    ATTACK_SOUND = None
    SONG = 'his_theme'
    INSTRUMENT = 'piano'
    SONGS = {
        'his_theme': [('G4', 2), ('D5', 2), ('C5', 2), ('G4', 2), ('B4', 3), ('B4', 3), ('C5', 2),
                      ('00', 2), ('G4', 2), ('C5', 2), ('G4', 2), ('B4', 3), ('B4', 3), ('C5', 2),
                      ('G4', 2), ('D5', 2), ('C5', 2), ('G4', 2), ('B4', 3), ('B4', 3), ('C5', 2),
                      ('00', 2), ('G4', 2), ('C5', 2), ('E5', 2), ('D5', 3), ('C5', 3), ('D5', 2)],
        'true_hero': [('A4', 1), ('E5', 1), ('D5', 1), ('E5', 1), ('C5', 1), ('E5', 1),
                      ('B4', 2), ('B4', 1), ('C5', 1), ('B4', 1), ('C5', 1),
                      ('B4', 3), ('D5', 3), ('A4', 3), ('G4', 3),
                      ('A4', 1), ('E5', 1), ('D5', 1), ('E5', 1), ('C5', 1), ('E5', 1),
                      ('B4', 2), ('B4', 1), ('C5', 1), ('B4', 1), ('C5', 1),
                      ('B4', 2), ('D5', 2), ('G5', 2), ('E5', 6)],
        'beat': [('C5', 4), ('C5', 4), ('C5', 2), ('C5', 2), ('C5', 1), ('C5', 1), ('C5', 2),
                 ('C5', 1), ('C5', 1), ('C5', 1), ('C5', 1), ('C5', 1), ('C5', 1), ('C5', 1), ('C5', 1),
                 ('C5', 1), ('C5', 1), ('C5', 2), ('C5', 1), ('C5', 1), ('C5', 2)],
        'legend': [('00', 2), ('B5', 1), ('C6', 1), ('B5', 1), ('A5', 1),
                   ('E5', 2), ('C5', 2), ('E5', 2),
                   ('00', 2), ('B5', 1), ('C6', 1), ('B5', 1), ('A5', 1),
                   ('D6', 6),
                   ('00', 2), ('B5', 1), ('C6', 1), ('B5', 1), ('A5', 1),
                   ('A5', 4), ('C6', 6),
                   ('G5', 2), ('G5', 1), ('F5', 1), ('E5', 1), ('F5', 1),
                   ('E5', 6)],
        'apple_smells_good': [('A4', 2), ('A4', 2), ('A4', 1), ('C5', 1), ('B4', 2), ('A4', 2), ('A4', 1), ('C5', 1),
                              ('E4', 8),
                              ('D5', 1), ('E5', 1), ('E5', 2), ('E5', 2), ('C6', 1), ('B5', 1), ('A5', 8)],
        'quiet': [('A4', 2), ('D5', 2), ('F#5', 2), ('D5', 2), ('E5', 1), ('F#5', 1), ('G#5', 1), ('D5', 1),
                  ('F5', 4)],
        'spear_of_justice': [('D5', 3), ('D5', 2), ('F5', 1), ('E5', 2), ('B5', 2), ('D5', 2)],
        'sanctuary': [('C#6', 1), ('G#5', 1), ('F#5', 1), ('G#5', 1), ('C#6', 1), ('C#6', 1), ('G#5', 1), ('F#5', 1), ('G#5', 2)]
    }
    SONGS_S = {
        'his_theme_s': [[('F4', 16)]] + [[]] * 6 +
                       [[('G4', 16)]] + [[]] * 6 +
                       [[('A4', 16)]] + [[]] * 6 +
                       [[('C5', 16)]] + [[]] * 6,
        'true_hero_s': [[('G4', 6), ('C4', 6), ('A3', 6), ('F3', 6)]] + [[]] * 5 +
                       [[('A4', 6), ('D4', 6), ('B3', 6), ('G3', 6)]] + [[]] * 4 +
                       [[('E4', 6), ('D4', 6), ('A3', 6), ('E3', 6)]] + [[]] +
                       [[('E4', 3), ('C4', 3), ('A3', 3)], [('B3', 3)]] +
                       [[('G4', 6), ('C4', 6), ('A3', 6), ('F3', 6)]] + [[]] * 5 +
                       [[('A4', 6), ('D4', 6), ('B3', 6), ('G3', 6)]] + [[]] * 4 +
                       [[('B4', 6), ('E4', 6), ('D4', 6), ('A3', 6)]] + [[]] * 2 +
                       [[('C5', 2), ('E4', 2), ('C4', 2)], [('B4', 2)], [('G4', 2)]],
        'beat_s': [[]] * 21,
        'legend_s': [[]] * 27,
        'apple_smells_good_s': [[]] * 16,
        'quiet_s': [[]] * 9,
        'spear_of_justice_s': [[]] * 7,
        'sanctuary_s': [[]] * 9
    }

    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int,
                 projectile: type(projectiles.Projectiles.Projectile), gains: list[type(effects.OctaveIncrease)],
                 mana_cost: int, inspiration_cost: int,
                 auto_fire: bool = False, back_rate: float = 0.5,
                 song: str = 'his_theme', instrument: str = 'piano',
                 heavy: bool = False):
        super().__init__(name, damages, kb, img, speed, at_time, projectile, mana_cost, auto_fire, '')
        self.gains = gains
        self.inspiration_cost = inspiration_cost
        self.back_rate = back_rate
        self.s_t = 0
        self.at_t = 0
        self.SONG = song
        self.INSTRUMENT = instrument
        self.heavy = heavy

    def on_start_attack(self):
        if game.get_game().player.mana < round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1) or game.get_game().player.inspiration < self.inspiration_cost:
            self.timer = 0
            return
        if self.sk_cd:
            self.timer = 0
            return
        tones = self.SONGS[self.SONG]
        tones_s = self.SONGS_S[self.SONG + '_s']
        if not self.s_t:
            self.at_t = 0
        else:
            self.at_t = (self.at_t + 1) % len(tones)
        t = tones[self.at_t][0]
        if t != '00':
            tone.play_note(self.INSTRUMENT, tone.note_to_frequency(t), tones[self.at_t][1] * self.at_time / 19 * 2)
        tone.play_notes('piano', [(t, d * self.at_time / 19 * 2) for t, d in tones_s[self.at_t]])
        self.sk_cd = self.sk_mcd

        game.get_game().projectiles.append(
            self.projectile((self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1]),
                            vector.coordinate_rotation(*position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        )))
        game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)
        game.get_game().player.inspiration -= self.inspiration_cost
        if self.timer:
            self.timer = self.at_time * tones[self.at_t][1] * 2 - 1
        self.s_t = self.cd + self.timer + 2

    def on_end_attack(self):
        self.display = True

    def on_idle(self):
        if self.s_t > 0:
            self.s_t -= 1
        super().on_idle()

    def update(self):
        super().update()
        self.display = True
        if self.heavy:
            self.x, self.y = 0, 60
            self.face_to(60, 0)
        else:
            self.x, self.y = -30, -10
            self.face_to(0, -10)

class PriestHealer(MagicWeapon):
    def __init__(self, name, amount, kb: float, img, speed: int, at_time: int, mana_cost: int, karma_gain: int,
                 auto_fire: bool = False, spell_name = ''):
        super().__init__(name, {}, kb, img, speed, at_time, projectiles.Projectiles.Projectile, mana_cost,
                         auto_fire, spell_name)
        self.amount = amount
        self.karma_gain = karma_gain

    def on_start_attack(self):
        game.get_game().player.hp_sys.effect(effects.WeakManaI([.5, 1, 3, 6][constants.DIFFICULTY], 1))
        if constants.DIFFICULTY:
            game.get_game().player.hp_sys.effect(effects.ManaDrain([0, 6, 12, 20][constants.DIFFICULTY], 1))
        if game.get_game().player.mana < round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1):
            self.timer = 0
            return
        if self.sk_cd:
            self.timer = 0
            return
        self.sk_cd = self.sk_mcd
        game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)
        game.get_game().player.good_karma = min(game.get_game().player.good_karma + self.karma_gain, self.karma_gain * 30 // (self.at_time + self.cd + 1))
        game.get_game().player.hp_sys.heal(self.amount + game.get_game().player.calculate_data('heal_amount', False))

class PriestWeapon(MagicWeapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int,
                 projectile: type(projectiles.Projectiles.Projectile), mana_cost: int, maximum_multiplier: float,
                 auto_fire: bool = False, spell_name = ''):
        super().__init__(name, damages, kb, img, speed, at_time, projectile, mana_cost, auto_fire, spell_name)
        self.max_mult = maximum_multiplier

class PacifistWeapon(Weapon):
    DMG_AS_IDX = 5
    ATTACK_SOUND = 'attack_magic'

    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, attack_range: int,
                 attack_distance: int, auto_fire: bool = False, col=(0, 255, 255)):
        super().__init__(name, damages, kb, img, speed, at_time, auto_fire)
        self.attack_range = attack_range
        self.attack_distance = attack_distance
        self.ccol = col

    def on_attack(self):
        super().on_attack()
        self.damage()

    def on_end_attack(self):
        super().on_end_attack()

    def damage(self):
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        self.set_rotation(vector.coordinate_rotation(mx, my))
        game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position((self.x + game.get_game().player.obj.pos[0],
                                                                                             self.y + game.get_game().player.obj.pos[1])),
                                                                sp=self.attack_distance / game.get_game().player.get_screen_scale() / 30, t=30,
                                                                col=self.ccol, n=8))
        ax, ay = vector.rotation_coordinate(self.rot)
        game.get_game().displayer.effect(
            pef.p_particle_effects(*position.displayed_position((self.x + game.get_game().player.obj.pos[0] + ax * self.attack_distance / 2,
                                                                 self.y + game.get_game().player.obj.pos[1] + ay * self.attack_distance / 2)),
                                   sp=self.attack_distance / game.get_game().player.get_screen_scale() / 60, t=30,
                                   col=self.ccol, n=8))
        for e in game.get_game().entities:
            dps = e.obj.pos
            px = dps[0] - self.x - game.get_game().player.obj.pos[0]
            py = dps[1] - self.y - game.get_game().player.obj.pos[1]
            if vector.distance(px, py) < self.attack_distance + (
            (e.img.get_width() + e.img.get_height()) // 2 if e.img is not None else 10):
                for t, d in self.damages.items():
                    e.hp_sys.damage(d * game.get_game().player.attack * game.get_game().player.attacks[self.DMG_AS_IDX], t)
                if not e.hp_sys.is_immune:
                    rf = vector.coordinate_rotation(px + self.x, py + self.y)
                    e.obj.apply_force(vector.Vector(rf, min(self.knock_back * 120000 / e.obj.MASS, e.obj.MASS * 24)))
                if self.ENABLE_IMMUNE:
                    e.hp_sys.enable_immune()

class SummonerWeapon(MagicWeapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int,
                 projectile: type(projectiles.Projectiles.Projectile), mana_cost: int, tag_damage: int,
                 auto_fire: bool = False, spell_name = ''):
        self.tag_damage = tag_damage
        super().__init__(name, damages, kb, img, speed, at_time, projectile, mana_cost, auto_fire, spell_name)

class TargetDummy(MagicWeapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int,
                 projectile: type(projectiles.Projectiles.Projectile), mana_cost: int, auto_fire: bool = False, spell_name = ''):
        super().__init__(name, damages, kb, img, speed, at_time, projectile, mana_cost, auto_fire, spell_name)
        self.dm = None

    def on_start_attack(self):
        game.get_game().player.hp_sys.effect(effects.WeakManaI([.5, 1, 3, 6][constants.DIFFICULTY], 1))
        if constants.DIFFICULTY:
            game.get_game().player.hp_sys.effect(effects.ManaDrain([0, 3, 6, 10][constants.DIFFICULTY], 1))
        if game.get_game().player.mana < round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1):
            self.timer = 0
            return
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)

    def on_attack(self):
        if self.dm is None:
            self.dm = entity.Entities.Dummy((0, 0))
        self.dm.obj.pos << position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
        self.dm.update()
        if self.dm.obj not in game.get_game().p_obj:
            game.get_game().p_obj.append(self.dm.obj)

    def on_end_attack(self):
        if self.dm.obj in game.get_game().p_obj:
            game.get_game().p_obj.remove(self.dm.obj)

class Teleporter(MagicWeapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int,
                 teleport_range: int, mana_cost: int, auto_fire: bool = False, spell_name = ''):
        super().__init__(name, damages, kb, img, speed, at_time, projectiles.Projectiles.Projectile, mana_cost, auto_fire, spell_name)
        self.teleport_range = teleport_range

    def on_start_attack(self):
        game.get_game().player.hp_sys.effect(effects.WeakManaI([.5, 1, 3, 6][constants.DIFFICULTY], 1))
        if constants.DIFFICULTY:
            game.get_game().player.hp_sys.effect(effects.ManaDrain([0, 6, 12, 20][constants.DIFFICULTY], 1))
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        if vector.distance(mx, my) > self.teleport_range:
            self.timer = 0
            return
        if game.get_game().player.mana < round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1):
            self.timer = 0
            return
        game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)
        game.get_game().player.obj.pos << (game.get_game().player.obj.pos[0] + mx, game.get_game().player.obj.pos[1] + my)

class ChaosKiller(MagicWeapon):
    def on_start_attack(self):
        game.get_game().player.hp_sys.effect(effects.WeakManaI([.5, 1, 3, 6][constants.DIFFICULTY], 1))
        if constants.DIFFICULTY:
            game.get_game().player.hp_sys.effect(effects.ManaDrain([0, 3, 6, 10][constants.DIFFICULTY], 1))
        if game.get_game().player.mana < round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1):
            self.timer = 0
            return
        game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)
        els = [e for e in game.get_game().entities if e.obj.IS_OBJECT]
        els.extend([e for e in game.get_game().entities if e.IS_MENACE])
        el = len(els)
        for e in els:
            e.hp_sys.damage(self.damages[dmg.DamageTypes.MAGICAL] * game.get_game().player.attack *
                            game.get_game().player.attacks[2] / el, dmg.DamageTypes.MAGICAL)

class EvilMagicWeapon(MagicWeapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int,
                 projectile: type(projectiles.Projectiles.Projectile), mana_cost: int, hp_cost: float,
                 auto_fire: bool = False, spell_name = ''):
        super().__init__(name, damages, kb, img, speed, at_time, projectile, mana_cost, auto_fire, spell_name)
        self.hp_cost = hp_cost

    def on_start_attack(self):
        game.get_game().player.hp_sys.effect(effects.WeakManaI([.5, 1, 3, 6][constants.DIFFICULTY], 1))
        if constants.DIFFICULTY:
            game.get_game().player.hp_sys.effect(effects.ManaDrain([0, 3, 6, 10][constants.DIFFICULTY], 1))
        if game.get_game().player.mana < round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1) or game.get_game().player.hp_sys.hp <= self.hp_cost or self.sk_cd:
            self.timer = 0
            return
        self.sk_cd = self.sk_mcd
        game.get_game().player.hp_sys.hp -= self.hp_cost
        game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)
        self.face_to(*position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        game.get_game().projectiles.append(
            self.projectile((self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1]),
                            self.rot))

class Tornado(MagicWeapon):
    def on_start_attack(self):
        game.get_game().player.hp_sys.effect(effects.WeakManaI([.5, 1, 3, 6][constants.DIFFICULTY], 1))
        if constants.DIFFICULTY:
            game.get_game().player.hp_sys.effect(effects.ManaDrain([0, 3, 6, 10][constants.DIFFICULTY], 1))
        if game.get_game().player.mana >= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1) and not self.sk_cd:
            self.sk_cd = self.sk_mcd
            game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)
            for e in game.get_game().entities:
                ex = e.obj.pos[0] - game.get_game().player.obj.pos[0]
                ey = e.obj.pos[1] - game.get_game().player.obj.pos[1]
                e.obj.velocity.add(vector.Vector(vector.coordinate_rotation(ex, ey),
                                                 1000000 / vector.distance(ex, ey) ** 2 * game.get_game().player.attack * game.get_game().player.attacks[2]))
        else:
            self.timer = 0

class SweepMagicWeapon(SweepWeapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int,
                 rot_speed: int, st_pos: int, double_sided: bool, mana_cost: int, auto_fire: bool = False, spell_name = ''):
        super().__init__(name, damages, kb, img, speed, at_time, rot_speed, st_pos, double_sided, auto_fire)
        self.spell_name = spell_name
        self.mana_cost = mana_cost

    def on_start_attack(self):
        if game.get_game().player.mana < round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1):
            self.timer = 0
            return
        game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)
        super().on_start_attack()

class MagicSet(Weapon):
    PRESET_KEY_SET = 'uiopghjklbnm,.'

    def __init__(self, name, img_index, element_feature, spell_name, style=0):
        super().__init__(name, {dmg.DamageTypes.MAGICAL: 540}, 0, img_index, 1, 0, False)
        self.weapons = []
        self.element_feature = element_feature
        self.at_in: MagicWeapon | None = None
        self.spell_name = spell_name
        self.mana_cost = 10
        self.talent_cost = 0.2
        self.style = style
        self.sz = 0
        self.tick = 0
        self.sel = 0

    def update(self):
        self.tick += 1
        if self.style == 0:
            px, py = position.displayed_position(game.get_game().player.obj.pos)
            tk_wave = self.tick % 20 / 20
            tk_wk = math.cos(tk_wave * 2 * math.pi)
            pg.draw.circle(game.get_game().displayer.canvas, (255, 220, 180),
                           (px, py - self.sz * 3 // 2 - 20), int(self.sz * (tk_wk * 0.3 + 1)))
            if random.randint(0, int(2000 - 1800 * tk_wave)) < self.sz:
                for _ in range(random.randint(1, 2 + int(math.sqrt(self.sz)))):
                    game.get_game().projectiles.append(
                        projectiles.Projectiles.LightsBeam(position.real_position((px, py - self.sz * 3 // 2 - 20)),
                                                           random.randint(0, 360)))
        elif self.style == 1:
            px, py = position.displayed_position(game.get_game().player.obj.pos)
            zq = int(4 + 56 / (math.sqrt(self.sz) + 1))
            tk_wave = self.tick % zq / zq
            tk_wk = math.cos(tk_wave * 2 * math.pi)
            for e in game.get_game().entities:
                if vector.distance(e.obj.pos[0] - game.get_game().player.obj.pos[0],
                                   e.obj.pos[1] - game.get_game().player.obj.pos[1]) < int((tk_wk + 1) * self.sz * 3):
                    e.hp_sys.damage(self.damages[dmg.DamageTypes.MAGICAL] * game.get_game().player.attack *
                                    game.get_game().player.attacks[2], dmg.DamageTypes.MAGICAL)
            pg.draw.circle(game.get_game().displayer.canvas, (100, 100, 255), (px, py),
                           int((tk_wk + 1) * self.sz * 3 / game.get_game().player.get_screen_scale()),
                           width=2)
            pg.draw.circle(game.get_game().displayer.canvas, (100, 100, 255), (px, py),
                           int((-tk_wk + 1) * self.sz * 3 / game.get_game().player.get_screen_scale()),
                           width=2)
        super().update()
        self.weapons = [w for w in WEAPONS.values() if
                        self.element_feature(w)] #and
                        #w.name in game.get_game().player.inventory.items.keys()]
        self.sel = min(self.sel, len(self.weapons) - 1)
        if self.weapons[self.sel] is not self:
            self.weapons[self.sel].update()
        for w in self.weapons:
            if w.sk_cd:
                w.sk_cd -= 1
        if self.at_in is not None:
            if not self.at_in.cool and not self.at_in.timer:
                self.at_in = None
            else:
                lv = [t for t in inventory.ITEMS[self.at_in.name.replace(' ', '_')].tags if t.name.startswith('magic_lv_')]
                lvs = {'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7, 'xx': 8, 'xxv': 12, 'nulla': 50}
                sz = lvs[lv[0].value.removeprefix('LV.').lower()]
                self.sz = (self.sz * 49 + sz ** 2 * 3) // 50
        if self.at_in is None:
            self.sz *= 8
            self.sz //= 9
            for i, w in enumerate(self.weapons):
                if pg.key.key_code(self.PRESET_KEY_SET[i]) in game.get_game().pressed_keys or\
                        (self.sel == i and pg.mouse.get_pressed()[0]):
                    self.sel = i
                    self.at_in = w
                    w.re_init()
                    w.attack()
                    lv = [t for t in inventory.ITEMS[self.at_in.name.replace(' ', '_')].tags if t.name.startswith('magic_lv_')]
                    lvs = {'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7, 'xx': 8, 'xxv': 12, 'nulla': 50}
                    sz = lvs[lv[0].value.removeprefix('LV.').lower()]
                    self.sz = (self.sz * 5 + sz ** 2 * 3) // 6
                    if sz == 12:
                        if game.get_game().player.mana > round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1):
                            game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)
                        else:
                            self.at_in = None
                            self.sz = 0
                        if game.get_game().player.talent > self.talent_cost:
                            game.get_game().player.talent -= self.talent_cost
                        else:
                            self.at_in = None
                            self.sz = 0


class ArcaneWeapon(MagicWeapon):
    ATTACK_SOUND = 'attack_arcane'

    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int,
                 projectile: type(projectiles.Projectiles.Projectile), mana_cost: int, talent_cost: float,
                 auto_fire: bool = False, spell_name = ''):
        super().__init__(name, damages, kb, img, speed, at_time, projectile, mana_cost, auto_fire, spell_name)
        self.talent_cost = talent_cost

    def on_attack(self):
        super().on_attack()
        game.get_game().player.talent -= self.talent_cost / self.at_time
        if game.get_game().player.talent < 0:
            self.timer = 0
            game.get_game().player.talent = 0
            return

    def on_end_attack(self):
        super(MagicWeapon, self).on_end_attack()
        if game.get_game().player.talent < 0:
            self.timer = 0
            return
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        game.get_game().projectiles.append(
            self.projectile((self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1]),
                            self.rot))
        self.sk_cd = self.sk_mcd

class Domain(ArcaneWeapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, mana_cost: int,
                 talent_cost: float, domain_color: tuple[int, int, int], domain_size: int = 600,
                 auto_fire: bool = False, spell_name = ''):
        super().__init__(name, damages, kb, img, speed, at_time, projectiles.Projectiles.Projectile, mana_cost,
                         talent_cost, auto_fire, spell_name)
        self.domain_color = domain_color
        self.domain_size = domain_size
        self.domain_open = False
        self.domain_tick = 0

    def on_start_attack(self):
        if self.sk_cd:
            self.timer = 0
            return
        self.sk_cd = self.sk_mcd
        self.domain_open = not self.domain_open
        self.domain_tick = 0
        self.face_to(*position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))

    def update(self):
        self.domain_tick += 1
        if self.domain_open:
            lm, lt = round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1), self.talent_cost
            self.mana_cost *= game.get_game().player.domain_size
            self.talent_cost *= game.get_game().player.domain_size
            if game.get_game().player.mana < round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1) or game.get_game().player.talent < self.talent_cost:
                self.domain_open = False
                self.domain_tick = 0
                return
            game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)
            game.get_game().player.talent -= self.talent_cost
            self.mana_cost, self.talent_cost = lm, lt
            pg.draw.circle(game.get_game().displayer.canvas, self.domain_color,
                           position.displayed_position(game.get_game().player.obj.pos),
                           min(self.domain_size * game.get_game().player.domain_size,
                               self.domain_tick ** 2 * 8) / game.get_game().player.get_screen_scale(),
                           width=5)
            game.get_game().player.obj.FRICTION = 0
        elif self.domain_tick ** 2 * 8 <= self.domain_size * game.get_game().player.domain_size:
            pg.draw.circle(game.get_game().displayer.canvas, self.domain_color,
                           position.displayed_position(game.get_game().player.obj.pos),
                           max(0, self.domain_size * game.get_game().player.domain_size - self.domain_tick ** 2 * 8)
                           / game.get_game().player.get_screen_scale(),
                           width=5)
        super().update()

class DomainWeapons(Weapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int,
                 projectile: type(projectiles.Projectiles.Projectile), domain_name: str,
                 auto_fire: bool = False, spell_name = ''):
        super().__init__(name, damages, kb, img, speed, at_time, auto_fire)
        self.domain_name = domain_name
        self.spell_name = spell_name
        self.mana_cost = 0
        self.projectile = projectile

    def on_start_attack(self):
        if self.sk_cd:
            self.timer = 0
            return
        self.sk_cd = self.sk_mcd
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        if vector.distance(mx, my) <= WEAPONS[self.domain_name].domain_size * game.get_game().player.domain_size and \
            WEAPONS[self.domain_name].domain_open:
            self.face_to(*position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
            super().on_start_attack()
            game.get_game().player.hp_sys.heal(4)
        else:
            self.timer = 0
            return

    def update(self):
        super().update()
        WEAPONS[self.domain_name].update()

class WdCirculateClockwise(DomainWeapons):
    def on_start_attack(self):
        super().on_start_attack()
        if self.timer:
            for e in game.get_game().entities:
                ex = e.obj.pos[0] - game.get_game().player.obj.pos[0]
                ey = e.obj.pos[1] - game.get_game().player.obj.pos[1]
                if vector.distance(ex, ey) > WEAPONS[self.domain_name].domain_size * game.get_game().player.domain_size:
                    continue
                mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
                ex = e.obj.pos[0] - mx
                ey = e.obj.pos[1] - my
                e.obj.velocity.add(vector.Vector(vector.coordinate_rotation(ex, ey) + 90,
                                                 1000000 / vector.distance(ex, ey) ** 2 *
                                                 game.get_game().player.attack * game.get_game().player.attacks[2] *
                                                 game.get_game().player.domain_size))

class WdCirculateAntiClockwise(DomainWeapons):
    def on_start_attack(self):
        super().on_start_attack()
        if self.timer:
            for e in game.get_game().entities:
                ex = e.obj.pos[0] - game.get_game().player.obj.pos[0]
                ey = e.obj.pos[1] - game.get_game().player.obj.pos[1]
                if vector.distance(ex, ey) > WEAPONS[self.domain_name].domain_size * game.get_game().player.domain_size:
                    continue
                mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
                ex = e.obj.pos[0] - mx
                ey = e.obj.pos[1] - my
                e.obj.velocity.add(vector.Vector(vector.coordinate_rotation(ex, ey) - 90,
                                                 1000000 / vector.distance(ex, ey) ** 2 *
                                                 game.get_game().player.attack * game.get_game().player.attacks[2] *
                                                 game.get_game().player.domain_size))

class WdCirculateAttract(DomainWeapons):
    def on_start_attack(self):
        super().on_start_attack()
        if self.timer:
            for e in game.get_game().entities:
                ex = e.obj.pos[0] - game.get_game().player.obj.pos[0]
                ey = e.obj.pos[1] - game.get_game().player.obj.pos[1]
                if vector.distance(ex, ey) > WEAPONS[self.domain_name].domain_size * game.get_game().player.domain_size:
                    continue
                mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
                ex = e.obj.pos[0] - mx
                ey = e.obj.pos[1] - my
                e.obj.velocity.add(vector.Vector(vector.coordinate_rotation(ex, ey) + 180,
                                                 800000 / vector.distance(ex, ey) ** 2 *
                                                 game.get_game().player.attack * game.get_game().player.attacks[2] *
                                                 game.get_game().player.domain_size))

class WdCirculateRepel(DomainWeapons):
    def on_start_attack(self):
        super().on_start_attack()
        if self.timer:
            for e in game.get_game().entities:
                ex = e.obj.pos[0] - game.get_game().player.obj.pos[0]
                ey = e.obj.pos[1] - game.get_game().player.obj.pos[1]
                if vector.distance(ex, ey) > WEAPONS[self.domain_name].domain_size * game.get_game().player.domain_size:
                    continue
                mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
                ex = e.obj.pos[0] - mx
                ey = e.obj.pos[1] - my
                e.obj.velocity.add(vector.Vector(vector.coordinate_rotation(ex, ey),
                                                 800000 / vector.distance(ex, ey) ** 2 *
                                                 game.get_game().player.attack * game.get_game().player.attacks[2] *
                                                 game.get_game().player.domain_size))

class WdStrongWind(DomainWeapons):
    def on_start_attack(self):
        super().on_start_attack()
        if self.timer:
            for e in game.get_game().entities:
                ex = e.obj.pos[0] - game.get_game().player.obj.pos[0]
                ey = e.obj.pos[1] - game.get_game().player.obj.pos[1]
                if vector.distance(ex, ey) > WEAPONS[self.domain_name].domain_size * game.get_game().player.domain_size:
                    continue
                mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
                ex = e.obj.pos[0] - mx
                ey = e.obj.pos[1] - my
                if vector.distance(ex, ey) < 100:
                    e.hp_sys.damage(self.damages[dmg.DamageTypes.ARCANE] * game.get_game().player.attack *
                                     game.get_game().player.attacks[2] * game.get_game().player.domain_size,
                                    dmg.DamageTypes.ARCANE)

class WdExtinct(DomainWeapons):
    def on_start_attack(self):
        super().on_start_attack()
        if self.timer:
            for e in game.get_game().entities:
                ex = e.obj.pos[0] - game.get_game().player.obj.pos[0]
                ey = e.obj.pos[1] - game.get_game().player.obj.pos[1]
                if vector.distance(ex, ey) > WEAPONS[self.domain_name].domain_size * game.get_game().player.domain_size:
                    continue
                e.hp_sys.damage(self.damages[dmg.DamageTypes.ARCANE] * game.get_game().player.attack *
                                 game.get_game().player.attacks[2] * game.get_game().player.domain_size,
                                dmg.DamageTypes.ARCANE)

class LdSpawn(DomainWeapons):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int,
                 projectile: type(projectiles.Projectiles.Projectile), domain_name: str,
                 auto_fire: bool = False, spell_name = '', spawn_entity: type(entity.Entities.Entity) = entity.Entities.Entity):
        super().__init__(name, damages, kb, img, speed, at_time, projectile, domain_name, auto_fire, spell_name)
        self.spawn_entity = spawn_entity

    def on_start_attack(self):
        super().on_start_attack()
        if self.timer:
            mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            if (vector.distance(mx - game.get_game().player.obj.pos[0],
                               my - game.get_game().player.obj.pos[1]) <= WEAPONS[self.domain_name].domain_size *
                    game.get_game().player.domain_size and WEAPONS[self.domain_name].domain_open):
                self.face_to(*position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
                m: entity.Entities.Entity = self.spawn_entity((mx, my))
                m.LOOT_TABLE = entity.LootTable([])
                game.get_game().entities.append(m)

class LdHeal(DomainWeapons):
    def on_start_attack(self):
        super().on_start_attack()
        if self.timer:
            am = len(game.get_game().entities) * game.get_game().player.domain_size
            game.get_game().player.hp_sys.heal(max(10, min(am, 100 * game.get_game().player.domain_size)))

class ForbiddenCurseTime(ArcaneWeapon):
    def on_start_attack(self):
        if game.get_game().player.talent < self.talent_cost:
            self.timer = 0
            return
        if game.get_game().player.mana < round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1):
            self.timer = 0
            return
        if self.sk_cd:
            self.timer = 0
            return
        self.sk_cd = self.sk_mcd
        game.get_game().player.talent -= self.talent_cost
        game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        fps = constants.FPS
        if fps == 120:
            fps = 20
        else:
            fps = 120
        constants.FPS = fps


class ToyKnife(MagicWeapon):
    def on_start_attack(self):
        game.get_game().player.hp_sys.effect(effects.WeakManaI([.5, 1, 3, 6][constants.DIFFICULTY], 1))
        if constants.DIFFICULTY:
            game.get_game().player.hp_sys.effect(effects.ManaDrain([0, 3, 6, 10][constants.DIFFICULTY], 1))
        if game.get_game().player.mana < round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1):
            self.timer = 0
            return
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)
        pg.draw.circle(game.get_game().displayer.canvas, (0, 255, 255),
                       position.displayed_position(game.get_game().player.obj.pos), 600, width=5)
        for e in game.get_game().entities:
            if vector.distance(e.obj.pos[0] - game.get_game().player.obj.pos[0],
                               e.obj.pos[1] - game.get_game().player.obj.pos[1]) < 600:
                e.hp_sys.damage(self.damages[dmg.DamageTypes.MAGICAL] * game.get_game().player.attack *
                                game.get_game().player.attacks[2], dmg.DamageTypes.MAGICAL)


class MidnightsWand(MagicWeapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int,
                 projectile: type(projectiles.Projectiles.Projectile), mana_cost: int, auto_fire: bool = False,
                 add_pos: int = 0):
        super().__init__(name, damages, kb, img, speed, at_time, projectile, mana_cost, auto_fire,
                         'Midnight Spell')
        self.add_pos = add_pos
        self.pts = []

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
        if game.get_game().day_time > 0.75 or game.get_game().day_time < 0.2:
            self.at_time = 8
            k = 5
            self.damages = {dmg.DamageTypes.MAGICAL: 110}
        else:
            self.at_time = 6
            k = 3
            self.damages = {dmg.DamageTypes.MAGICAL: 80}
        player = game.get_game().player
        self.pts = [(player.obj.pos[0] + self.x, player.obj.pos[1] + self.y)]
        for i in range(k):
            self.x, self.y = random.randint(-self.add_pos, self.add_pos), random.randint(-self.add_pos, self.add_pos)
            self.face_to(*position.relative_position(
                position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
            p = self.projectile(
                (self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1]), self.rot)
            p.obj.apply_force(vector.Vector(self.rot, 1000))
            game.get_game().projectiles.append(p)
            self.pts.append((player.obj.pos[0] + self.x, player.obj.pos[1] + self.y))
        self.x, self.y = 0, 0
        game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)

    def on_attack(self):
        super().on_attack()
        eff.pointed_curve((127, 0, 127), self.pts, 5, salpha=255)

class Hematology(MagicWeapon):
    def __init__(self, name, img, speed: int, at_time: int, auto_fire: bool = False):
        super().__init__(name, {}, 0, img, speed, at_time, projectiles.Projectiles.Projectile,
                         30, auto_fire, 'Blood Regeneration')

    def on_start_attack(self):
        game.get_game().player.hp_sys.effect(effects.WeakManaI([.5, 1, 3, 6][constants.DIFFICULTY], 1))
        if constants.DIFFICULTY:
            game.get_game().player.hp_sys.effect(effects.ManaDrain([0, 9, 18, 30][constants.DIFFICULTY], 1))
        if game.get_game().player.mana < round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1):
            self.timer = 0
            return
        game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        game.get_game().player.hp_sys.heal(30)

class Savior(ArcaneWeapon):
    def on_start_attack(self):
        if game.get_game().player.mana < round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1) or game.get_game().player.talent < self.talent_cost:
            self.timer = 0
            return
        game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)
        game.get_game().player.talent -= self.talent_cost
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        game.get_game().player.hp_sys.shields.append(('sor', game.get_game().player.hp_sys.max_hp))


class LifeWand(MagicWeapon):
    def __init__(self, name, img, speed: int, at_time: int, auto_fire: bool = False):
        super().__init__(name, {}, 0, img, speed, at_time, projectiles.Projectiles.Projectile,
                         0, auto_fire, 'Heal Prayer')

    def update(self):
        super().update()
        self.mana_cost = min(game.get_game().player.mana,
                             int(game.get_game().player.hp_sys.max_hp - game.get_game().player.hp_sys.hp) * 2)

    def on_start_attack(self):
        game.get_game().player.hp_sys.effect(effects.WeakManaI([.5, 1, 3, 6][constants.DIFFICULTY], 1))
        if constants.DIFFICULTY:
            game.get_game().player.hp_sys.effect(effects.ManaDrain([0, 3, 6, 10][constants.DIFFICULTY], 1))
        hp_lft = game.get_game().player.hp_sys.max_hp - game.get_game().player.hp_sys.hp
        mana_avail = game.get_game().player.mana
        game.get_game().player.mana -= min(mana_avail // 2, hp_lft) * 2
        game.get_game().player.hp_sys.heal(min(mana_avail // 2, hp_lft))

class AzureGuard(MagicWeapon):
    def update(self):
        super().update()
        aw = [v for n, v in game.get_game().player.hp_sys.shields if n == 'azure_guard']
        if len(aw):
            v = aw[0]
            pg.draw.circle(game.get_game().displayer.canvas, (int(255 - v * 2), int(255 - v * 2), 255),
                           position.displayed_position(game.get_game().player.obj.pos),
                           width=int(1 + v // 20), radius=240)

    def on_start_attack(self):
        game.get_game().player.hp_sys.effect(effects.WeakManaI([.5, 1, 3, 6][constants.DIFFICULTY], 1))
        if constants.DIFFICULTY:
            game.get_game().player.hp_sys.effect(effects.ManaDrain([0, 3, 6, 10][constants.DIFFICULTY], 1))
        if game.get_game().player.mana < round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1):
            self.timer = 0
            return
        if len([v for n, v in game.get_game().player.hp_sys.shields if n == 'azure_guard']):
            self.timer = 0
            return
        game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)
        game.get_game().player.hp_sys.shields.append(('azure_guard', 100))

class EarthWall(MagicWeapon):
    def on_start_attack(self):
        game.get_game().player.hp_sys.effect(effects.WeakManaI([.5, 1, 3, 6][constants.DIFFICULTY], 1))
        if constants.DIFFICULTY:
            game.get_game().player.hp_sys.effect(effects.ManaDrain([0, 3, 6, 10][constants.DIFFICULTY], 1))
        if game.get_game().player.mana < round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1):
            self.timer = 0
            return
        game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)
        e_w = 256
        for ar in [15, 18, 20, 30]:
            w = e_w / 2 / math.sin(math.radians(ar / 2))
            for r in range(0, 360, ar):
                ax, ay = vector.rotation_coordinate(r)
                game.get_game().entities.append(entity.Entities.HugeTree((self.x + game.get_game().player.obj.pos[0] + ax * w,
                                                                          self.y + game.get_game().player.obj.pos[1] + ay * w)))

class Bow(Weapon):
    ATTACK_SOUND = 'attack_bow'
    TRANS_AMMO = None

    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, projectile_speed: int,
                 auto_fire: bool = False, tail_col: tuple[int, int, int] | None = None, ammo_save_chance: float = 0.0, precision: float = 0.0, tw=3, ts=3):
        super().__init__(name, damages, kb, img, speed, at_time, auto_fire)
        self.spd = projectile_speed
        self.tail_col = tail_col
        self.ammo_save_chance = ammo_save_chance
        self.precision = precision
        self.ddata = [self.precision, self.spd]
        self.tw = tw
        self.ts = ts

    def on_charge(self):
        self.precision = self.ddata[0]
        self.spd = self.ddata[1]
        self.ddata = [self.precision, self.spd]
        self.scale = 3 - 2 * 1.2 ** (-self.strike / 50)
        self.precision = int(self.ddata[0] / self.scale ** 3)
        self.spd = int(self.ddata[1] * self.scale ** 5)
        self.display = True
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        rot = vector.cartesian_to_polar(mx, my)[0]
        self.set_rotation(rot)

        dt = 400 * self.scale ** 1.5

        px, py = position.displayed_position(game.get_game().player.obj.pos)

        sx, sy = vector.polar_to_cartesian(rot + self.precision, dt)
        ex, ey = vector.polar_to_cartesian(rot + self.precision, -dt)
        draw.line(game.get_game().displayer.canvas, (255, 0, 0), (sx + px, sy + py), (ex + px, ey + py),
                  max(1, int(5 / game.get_game().player.get_screen_scale())))

        sx, sy = vector.polar_to_cartesian(rot - self.precision, dt)
        ex, ey = vector.polar_to_cartesian(rot - self.precision, -dt)
        draw.line(game.get_game().displayer.canvas, (255, 0, 0), (sx + px, sy + py), (ex + px, ey + py),
                  max(1, int(5 / game.get_game().player.get_screen_scale())))

    def on_end_attack(self):
        self.display = False
        self.precision = self.ddata[0]
        self.spd = self.ddata[1]
        self.scale = 1

    def on_start_attack(self):
        self.face_to(
            *position.relative_position(-vector.Vector2D(0, 0, self.x, self.y) + position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < constants.ULTIMATE_AMMO_BONUS and random.random() > self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        pt = projectiles.AMMOS[game.get_game().player.ammo[0]]
        if self.TRANS_AMMO:
            pt = self.TRANS_AMMO
        pj = pt((self.x + game.get_game().player.obj.pos[0],
                 self.y + game.get_game().player.obj.pos[1]),
                self.rot + random.uniform(-self.precision, self.precision), self.spd,
                self.damages[dmg.DamageTypes.PIERCING], self.knock_back)
        if self.tail_col is not None:
            pj.TAIL_COLOR = self.tail_col
            pj.TAIL_SIZE = max(pj.TAIL_SIZE, self.ts)
            pj.TAIL_WIDTH = max(pj.TAIL_WIDTH, self.tw)
        game.get_game().projectiles.append(pj)

class GenerationII(Bow):
    def on_end_attack(self):
        s = self.scale > 1
        super().on_end_attack()
        if s:
            game.get_game().player.weapons[game.get_game().player.sel_weapon] = WEAPONS['generation']

class ForestsBow(Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        game.get_game().projectiles.append(
            projectiles.AMMOS[game.get_game().player.ammo[0]]((self.x + game.get_game().player.obj.pos[0],
                                                               self.y + game.get_game().player.obj.pos[1]),
                                                              self.rot, self.spd,
                                                              self.damages[dmg.DamageTypes.PIERCING] *
                                                              (1 + (game.get_game().player.ammo[0] == 'coniferous_leaf'))))

    def update(self):
        super().update()
        self.sk_mcd = 60
        if game.get_game().player.ammo[0] in projectiles.AMMOS and game.get_game().player.ammo[1] and \
                pg.K_q in game.get_game().get_pressed_keys() and not self.sk_cd:
            if game.get_game().player.ammo[1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
                game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
            self.sk_cd = self.sk_mcd
            ax, ay = vector.rotation_coordinate(self.rot)
            for aac in [0, 1]:
                for ar in range(-15, 16, 15):
                    x, y = (self.x + game.get_game().player.obj.pos[0] + aac * ax * 200,
                            self.y + game.get_game().player.obj.pos[1] + aac * ay * 200)
                    p = projectiles.AMMOS[game.get_game().player.ammo[0]]((x, y), self.rot + ar, self.spd,
                                                                          self.damages[dmg.DamageTypes.PIERCING])
                    game.get_game().projectiles.append(p)

class WorldBow(Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        for ar in range(-15, 16, 15):
            pj = projectiles.AMMOS[game.get_game().player.ammo[0]]((self.x + game.get_game().player.obj.pos[0],
                                                                   self.y + game.get_game().player.obj.pos[1]),
                                                                  self.rot + ar + random.uniform(-self.precision, self.precision), self.spd,
                                                                  self.damages[dmg.DamageTypes.PIERCING])
            b = game.get_game().get_biome()
            if b.endswith('forest'):
                inventory.ITEMS['world_bow'].desc = 'col00ff00Forests: +200% projectile speed, +20% damage'
                pj.obj.velocity *= 3
                pj.DAMAGES *= 1.2
            elif b in ['desert', 'hell']:
                inventory.ITEMS['world_bow'].desc = 'col00ff00Desert/Hell: -30% damage, pierce'
                pj.DAMAGES *= .7
                pj.DELETE = False
                pj.ENABLE_IMMUNE = 3
            elif b in ['snowland', 'heaven']:
                inventory.ITEMS['world_bow'].desc = 'col00ff00Snow/Heaven: -60% speed, 50% aim'
                pj.obj.velocity *= .4
                pj.AIMING = .5
            game.get_game().projectiles.append(pj)

class Aiolos(Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        for ar in range(-5, 6, 5):
            pj = projectiles.AMMOS[game.get_game().player.ammo[0]]((self.x + game.get_game().player.obj.pos[0],
                                                                   self.y + game.get_game().player.obj.pos[1]),
                                                                  self.rot + ar + random.uniform(-self.precision, self.precision), self.spd,
                                                                  self.damages[dmg.DamageTypes.PIERCING])
            pj.DELETE = False
            pj.ENABLE_IMMUNE = 4.5
            pj.TAIL_COLOR = (0, 255, 255)
            pj.TAIL_SIZE = 5
            pj.TAIL_WIDTH = 8

            game.get_game().projectiles.append(pj)


class HeavyBow(Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[
            1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data(
                'ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)

        pj = projectiles.AMMOS[game.get_game().player.ammo[0]]((self.x + game.get_game().player.obj.pos[0],
                                                                self.y + game.get_game().player.obj.pos[1]),
                                                               self.rot + random.uniform(-self.precision,
                                                                                              self.precision), self.spd,
                                                               self.damages[dmg.DamageTypes.PIERCING])
        pj.obj.velocity *= 1.5
        pj.obj.FRICTION **= 2
        pj.DELETE = False
        pj.DECAY_RATE = 1
        pj.ENABLE_IMMUNE = 4
        game.get_game().projectiles.append(pj)

class WForget(Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        for ar in range(-4, 5, 4):
            pj = projectiles.AMMOS[game.get_game().player.ammo[0]]((self.x + game.get_game().player.obj.pos[0],
                                                                   self.y + game.get_game().player.obj.pos[1]),
                                                                  self.rot + ar + random.uniform(-self.precision, self.precision), self.spd,
                                                                  self.damages[dmg.DamageTypes.PIERCING])
            pj.img = game.get_game().graphics['entity_null']
            pj.TAIL_WIDTH = 0
            game.get_game().projectiles.append(pj)

class WSky(Bow):
    def update(self):
        super().update()
        tf = math.cos(2 * math.pi * game.get_game().day_time) ** 2
        if .25 < game.get_game().day_time < .75:
            self.at_time = 40
            self.damages[dmg.DamageTypes.PIERCING] = int(80 * (1 + tf))
        else:
            self.at_time = max(1, int(40 / (1 + tf)))
            self.damages[dmg.DamageTypes.PIERCING] = 80

class KuangKuangKuang(Bow):
    def on_start_attack(self):
        super().on_start_attack()
        if self.timer:
            mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
            self.face_to(mx, my)
            game.get_game().player.obj.apply_force(vector.Vector(self.rot + 180, 200))

class ForwardBow(Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        if self.sk_cd:
            game.get_game().projectiles.append(projectiles.Projectiles.ForwardBow(game.get_game().player.obj.pos,
                                                                                  self.rot))
        else:
            game.get_game().projectiles.append(
                projectiles.Projectiles.ForwardBowHuge(game.get_game().player.obj.pos, self.rot))
            self.sk_cd = self.sk_mcd

    def update(self):
        super().update()
        self.sk_mcd = 30
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        self.face_to(mx, my)

class LazerRain(Bow):
    def update(self):
        super().update()
        self.sk_mcd = 80

    def on_start_attack(self):
        if not self.sk_cd:
            for _ in range(25):
                mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
                dt = random.randint(0, 500)
                ax, ay = vector.rotation_coordinate(random.randint(0, 360))
                lazer = projectiles.Projectiles.LazerRain((mx + ax * dt,
                                                           my + ay * dt - 2200), vector.coordinate_rotation(0, 1))
                game.get_game().projectiles.append(lazer)
            self.sk_cd = self.sk_mcd
        super().on_start_attack()

class DiscordStorm(Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        for r in range(-30, 31, 15):
            game.get_game().projectiles.append(
                projectiles.AMMOS[game.get_game().player.ammo[0]]((self.x + game.get_game().player.obj.pos[0],
                                                                   self.y + game.get_game().player.obj.pos[1]),
                                                                  self.rot + r, self.spd,
                                                                  self.damages[dmg.DamageTypes.PIERCING]))

class Accelerationism(Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        sax, say = vector.rotation_coordinate(self.rot + 90)
        for i in [-1, 1]:
            x, y = (self.x + game.get_game().player.obj.pos[0] + sax * 20 * i,
                    self.y + game.get_game().player.obj.pos[1] + say * 20 * i)
            p = projectiles.Projectiles.Accelerationism((x, y), self.rot,
                                                        self.spd + projectiles.AMMOS[game.get_game().player.ammo[0]].SPEED,
                                                        self.damages[dmg.DamageTypes.PIERCING] +
                                                        projectiles.AMMOS[game.get_game().player.ammo[0]].DAMAGES)
            game.get_game().projectiles.append(p)

class FireQuenchBow(Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        sax, say = vector.rotation_coordinate(self.rot + 90)
        for i in [0]:
            x, y = (self.x + game.get_game().player.obj.pos[0] + sax * 20 * i,
                    self.y + game.get_game().player.obj.pos[1] + say * 20 * i)
            p = projectiles.Projectiles.FireQuenchArrow((x, y), self.rot,
                                                        self.spd + projectiles.AMMOS[game.get_game().player.ammo[0]].SPEED,
                                                        self.damages[dmg.DamageTypes.PIERCING] +
                                                        projectiles.AMMOS[game.get_game().player.ammo[0]].DAMAGES)
            game.get_game().projectiles.append(p)

class IceQuenchBow(Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        sax, say = vector.rotation_coordinate(self.rot + 90)
        for i in [0]:
            x, y = (self.x + game.get_game().player.obj.pos[0] + sax * 20 * i,
                    self.y + game.get_game().player.obj.pos[1] + say * 20 * i)
            p = projectiles.Projectiles.IceQuenchArrow((x, y), self.rot,
                                                        self.spd + projectiles.AMMOS[game.get_game().player.ammo[0]].SPEED,
                                                        self.damages[dmg.DamageTypes.PIERCING] +
                                                        projectiles.AMMOS[game.get_game().player.ammo[0]].DAMAGES)
            game.get_game().projectiles.append(p)

class DarkQuenchBow(Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        sax, say = vector.rotation_coordinate(self.rot + 90)
        for i in [0]:
            x, y = (self.x + game.get_game().player.obj.pos[0] + sax * 20 * i,
                    self.y + game.get_game().player.obj.pos[1] + say * 20 * i)
            p = projectiles.Projectiles.DarkQuenchArrow((x, y), self.rot,
                                                        self.spd + projectiles.AMMOS[game.get_game().player.ammo[0]].SPEED,
                                                        self.damages[dmg.DamageTypes.PIERCING] +
                                                        projectiles.AMMOS[game.get_game().player.ammo[0]].DAMAGES)
            game.get_game().projectiles.append(p)

class LightQuenchBow(Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        sax, say = vector.rotation_coordinate(self.rot + 90)
        for i in [0]:
            x, y = (self.x + game.get_game().player.obj.pos[0] + sax * 20 * i,
                    self.y + game.get_game().player.obj.pos[1] + say * 20 * i)
            p = projectiles.Projectiles.LightQuenchArrow((x, y), self.rot,
                                                        self.spd + projectiles.AMMOS[game.get_game().player.ammo[0]].SPEED,
                                                        self.damages[dmg.DamageTypes.PIERCING] +
                                                        projectiles.AMMOS[game.get_game().player.ammo[0]].DAMAGES)
            game.get_game().projectiles.append(p)

class TheFairyBow(Bow):
    counter = 0

    def on_start_attack(self):
        self.counter = (self.counter + 1) % 4
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        sax, say = vector.rotation_coordinate(self.rot + 90)
        c = self.counter
        for i in range(-4, 4, 1):
            x, y = (self.x + game.get_game().player.obj.pos[0] + sax * 20 * i,
                    self.y + game.get_game().player.obj.pos[1] + say * 20 * i)
            tt = [projectiles.Projectiles.FireQuenchArrow,
                  projectiles.Projectiles.IceQuenchArrow,
                  projectiles.Projectiles.DarkQuenchArrow,
                  projectiles.Projectiles.LightQuenchArrow]
            p = tt[c]((x, y), self.rot + random.uniform(-self.precision, self.precision),
                      self.spd + projectiles.AMMOS[game.get_game().player.ammo[0]].SPEED,
                      self.damages[dmg.DamageTypes.PIERCING] + projectiles.AMMOS[game.get_game().player.ammo[0]].DAMAGES)
            c = (c + 1) % 4
            game.get_game().projectiles.append(p)

class Resolution(Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        sax, say = vector.rotation_coordinate(self.rot + 90)
        ppx, ppy = vector.rotation_coordinate(self.rot)
        aas = [-4, -3, -1, 1, 3, 4]
        cols = ((255, 255, 0), (255, 127, 0), (0, 255, 0), (0, 0, 255), (255, 0, 255), (0, 255, 255))
        for i in range(6):
            for j in range(0, 1 + 80 * (not self.sk_cd), 40):
                x, y = (self.x + game.get_game().player.obj.pos[0] + sax * 20 * aas[i] - ppx * j,
                        self.y + game.get_game().player.obj.pos[1] + say * 20 * aas[i] - ppy * j)
                p = projectiles.AMMOS[game.get_game().player.ammo[0]]((x, y), self.rot,
                                                            self.spd + projectiles.AMMOS[game.get_game().player.ammo[0]].SPEED,
                                                            self.damages[dmg.DamageTypes.PIERCING])
                p.TAIL_COLOR = cols[i]
                p.TAIL_SIZE = 2
                p.TAIL_WIDTH = 6
                game.get_game().projectiles.append(p)
        if not self.sk_cd:
            self.sk_cd = self.sk_mcd

    def update(self):
        super().update()
        self.sk_mcd = 40

class GaiaPaladinSpear(Spear):
    def update(self):
        super().update()
        akb = 1 - math.e ** (-abs(game.get_game().player.obj.velocity) / 500)
        self.damages[dmg.DamageTypes.PHYSICAL] = int(akb * 300) + 100
        self.knock_back = .5 + int(akb * 90) / 20

class DaedelusStormbow(Bow):
    def on_start_attack(self):
        self.face_to(*position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        mx, my = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        for i in range(random.randint(0, 2)):
            x, y = mx + random.randint(-500, 500), -game.get_game().displayer.SCREEN_HEIGHT // 2 - 200
            p = projectiles.AMMOS[game.get_game().player.ammo[0]]((x + game.get_game().player.obj.pos[0],
                                                                   y + game.get_game().player.obj.pos[1]),
                                                                  vector.coordinate_rotation(mx - x,
                                                                                             my - y) + random.randint(
                                                                      -1, 1), self.spd,
                                                                  self.damages[dmg.DamageTypes.PIERCING])
            game.get_game().projectiles.append(p)
        self.face_to(mx, - 1200)


class TrueDaedalusStormbow(Bow):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo[0] not in projectiles.AMMOS or not game.get_game().player.ammo[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo[1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
            game.get_game().player.ammo = (game.get_game().player.ammo[0], game.get_game().player.ammo[1] - 1)
        mx, my = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        for i in range(random.randint(0, 2)):
            x, y = mx + random.randint(-800, 800), -game.get_game().displayer.SCREEN_HEIGHT // 2 - 200
            p = projectiles.AMMOS[game.get_game().player.ammo[0]]((x + game.get_game().player.obj.pos[0],
                                                                   y + game.get_game().player.obj.pos[1]),
                                                                  vector.coordinate_rotation(mx - x,
                                                                                             my - y) + random.randint(
                                                                      -1, 1), self.spd,
                                                                  self.damages[dmg.DamageTypes.PIERCING])
            game.get_game().projectiles.append(p)
        self.face_to(mx, -1200)


class Gun(Bow):
    ATTACK_SOUND = 'attack_shoot'

    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, projectile_speed: int,
                 auto_fire: bool = False, precision: int = 0, tail_col: tuple[int, int, int] | None = None, ammo_save_chance: float = 0.0):
        super().__init__(name, damages, kb, img, speed, at_time, projectile_speed, auto_fire, tail_col)
        self.precision = precision
        self.ammo_save_chance = ammo_save_chance
        self.ddata = [self.precision, self.spd]

    def on_charge(self):
        self.precision = self.ddata[0]
        self.spd = self.ddata[1]
        self.ddata = [self.precision, self.spd]
        sc = 3 - 2 * 1.2 ** (-self.strike / 50)
        self.scale = 1
        self.precision = int(self.ddata[0] / sc ** 1.5)
        self.spd = int(self.ddata[1] * sc ** 3)
        self.display = True
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        rot = vector.cartesian_to_polar(mx, my)[0]
        self.set_rotation(rot)

        dt = 400 * sc ** 1.5

        px, py = position.displayed_position(game.get_game().player.obj.pos)

        sx, sy = vector.polar_to_cartesian(rot + self.precision, dt)
        ex, ey = vector.polar_to_cartesian(rot + self.precision, -dt)
        draw.line(game.get_game().displayer.canvas, (255, 0, 0), (sx + px, sy + py), (ex + px, ey + py),
                  max(1, int(5 / game.get_game().player.get_screen_scale())))

        sx, sy = vector.polar_to_cartesian(rot - self.precision, dt)
        ex, ey = vector.polar_to_cartesian(rot - self.precision, -dt)
        draw.line(game.get_game().displayer.canvas, (255, 0, 0), (sx + px, sy + py), (ex + px, ey + py),
                  max(1, int(5 / game.get_game().player.get_screen_scale())))

    def on_end_attack(self):
        self.display = False
        self.precision = self.ddata[0]
        self.spd = self.ddata[1]
        self.scale = 1

    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo_bullet[0] not in projectiles.AMMOS or not game.get_game().player.ammo_bullet[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo_bullet[1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
            game.get_game().player.ammo_bullet = (
            game.get_game().player.ammo_bullet[0], game.get_game().player.ammo_bullet[1] - 1)
        pj = projectiles.AMMOS[game.get_game().player.ammo_bullet[0]]((self.x + game.get_game().player.obj.pos[0],
                                                                self.y + game.get_game().player.obj.pos[1]),
                                                               self.rot + random.randint(-self.precision, self.precision), self.spd,
                                                               self.damages[dmg.DamageTypes.PIERCING])
        if self.tail_col is not None:
            pj.TAIL_COLOR = self.tail_col
            pj.TAIL_SIZE = max(pj.TAIL_SIZE, 3)
            pj.TAIL_WIDTH = max(pj.TAIL_WIDTH, 6)
        game.get_game().projectiles.append(pj)

class RocketLauncher(Gun):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, projectile_speed: int,
                 auto_fire: bool = False, precision: int = 0, ammo_save_chance: float = 0.0, m_range: int = 0, mode=0):
        super().__init__(name, damages, kb, img, speed, at_time, projectile_speed, auto_fire, precision,
                         ammo_save_chance=ammo_save_chance)
        self.mode = mode
        self.mr = 600 - m_range

    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo_bullet[0] not in projectiles.AMMOS or game.get_game().player.ammo_bullet[1] < 4:
            self.timer = 0
            return
        if game.get_game().player.ammo_bullet[1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
            game.get_game().player.ammo_bullet = (
            game.get_game().player.ammo_bullet[0], game.get_game().player.ammo_bullet[1] - 4)
        if self.mode == 0:
            k = 1
        elif self.mode == 2:
            k = max(4, random.randint(2, 13))
        elif self.mode == 3:
            k = random.randint(8, 16)
        else:
            k = max(1, random.randint(-2, 6))
        for _ in range(k):
            ammo = random.choice([projectiles.Projectiles.RocketRed, projectiles.Projectiles.RocketOrange,
                                   projectiles.Projectiles.RocketYellow, projectiles.Projectiles.RocketGreen,
                                  projectiles.Projectiles.RocketCyan, projectiles.Projectiles.RocketBlue,
                                  projectiles.Projectiles.RocketPurple])
            pj = ammo((self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1]),
                      self.rot + random.randint(-self.precision, self.precision), self.spd,
                      self.damages[dmg.DamageTypes.PIERCING], self.mr)
            pj.TAIL_COLOR = pj.COL
            game.get_game().projectiles.append(pj)

class DarkExploder(Gun):
    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo_bullet[0] not in projectiles.AMMOS or not game.get_game().player.ammo_bullet[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo_bullet[1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
            game.get_game().player.ammo_bullet = (
            game.get_game().player.ammo_bullet[0], game.get_game().player.ammo_bullet[1] - 1)
        pj = projectiles.AMMOS[game.get_game().player.ammo_bullet[0]]
        am = projectiles.Projectiles.Exploder((self.x + game.get_game().player.obj.pos[0],
                                                 self.y + game.get_game().player.obj.pos[1]),
                                                self.rot + random.randint(-self.precision, self.precision), self.spd + pj.SPEED,
                                                self.damages[dmg.DamageTypes.PIERCING] + pj.DAMAGES)
        game.get_game().projectiles.append(am)

class Gaze(Gun):
    def on_start_attack(self):
        super().on_start_attack()
        if not self.sk_cd:
            self.sk_mcd = 120
            self.sk_cd = self.sk_mcd
            game.get_game().projectiles.append(projectiles.Projectiles.Gaze(game.get_game().player.obj.pos, self.rot))

class Witness(Gun):
    def on_start_attack(self):
        super().on_start_attack()
        if not self.sk_cd:
            self.sk_mcd = 30
            self.sk_cd = self.sk_mcd
            game.get_game().projectiles.append(projectiles.Projectiles.Witness(game.get_game().player.obj.pos, self.rot))


class Shotgun(Gun):
    def on_start_attack(self):
        for _ in range(3):
            super().on_start_attack()

class LazerGun(Gun):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, projectile_speed: int,
                 auto_fire: bool = False, lazer_len: float = 1.2, lazer_width: int = 30,
                 lazer_col: tuple[int, int, int] = (255, 255, 150), ammo_save_chance: float = 0.0):
        super().__init__(name, damages, kb, img, speed, at_time, projectile_speed, auto_fire)
        self.lazer_len = lazer_len
        self.lazer_width = lazer_width
        self.lazer_col = lazer_col
        self.ammo_save_chance = ammo_save_chance

    def on_start_attack(self):
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        if game.get_game().player.ammo_bullet[0] not in projectiles.AMMOS or not game.get_game().player.ammo_bullet[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo_bullet[1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
            game.get_game().player.ammo_bullet = (
            game.get_game().player.ammo_bullet[0], game.get_game().player.ammo_bullet[1] - 1)
        wp: projectiles.Projectiles.Bullet = projectiles.AMMOS[game.get_game().player.ammo_bullet[0]]
        ps = (self.x + game.get_game().player.obj.pos[0], self.y + game.get_game().player.obj.pos[1])
        b = projectiles.Projectiles.Beam(ps, self.rot)
        b.LENGTH = (wp.SPEED + self.spd) * self.lazer_len
        b.WIDTH = self.lazer_width
        b.DURATION = self.at_time
        b.DMG = self.damages[dmg.DamageTypes.PIERCING] + wp.DAMAGES
        b.COLOR = self.lazer_col
        b.DMG_TYPE = dmg.DamageTypes.PIERCING
        b.FACE_TO_MOUSE = True
        game.get_game().projectiles.append(b)

    def update(self):
        super().update()
        mx, my = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        self.face_to(mx, my)


class MagmaAssaulter(Gun):
    def on_attack(self):
        super().on_attack()
        if pg.K_q in game.get_game().get_keys():
            mx, my = position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            px, py = game.get_game().player.obj.pos
            game.get_game().player.obj.apply_force(vector.Vector(vector.coordinate_rotation(mx - px, my - py), -800))

class PhoenixExploder(Gun):
    def on_attack(self):
        super().on_attack()
        if self.at_time - self.timer in [3, 6]:
            self.face_to(
                *position.relative_position(
                    position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
            if game.get_game().player.ammo_bullet[0] not in projectiles.AMMOS or not game.get_game().player.ammo_bullet[
                1]:
                self.timer = 0
                return
            if game.get_game().player.ammo_bullet[
                1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data(
                    'ammo_save', False) / 100:
                game.get_game().player.ammo_bullet = (
                    game.get_game().player.ammo_bullet[0], game.get_game().player.ammo_bullet[1] - 1)
            pj = projectiles.AMMOS[game.get_game().player.ammo_bullet[0]]((self.x + game.get_game().player.obj.pos[0],
                                                                           self.y + game.get_game().player.obj.pos[1]),
                                                                          self.rot + random.randint(-self.precision,
                                                                                                    self.precision),
                                                                          self.spd,
                                                                          self.damages[dmg.DamageTypes.PIERCING])
            if self.tail_col is not None:
                pj.TAIL_COLOR = self.tail_col
                pj.TAIL_SIZE = max(pj.TAIL_SIZE, 3)
                pj.TAIL_WIDTH = max(pj.TAIL_WIDTH, 6)
            game.get_game().projectiles.append(pj)

class Demolisher(Gun):
    def on_start_attack(self):
        super().on_start_attack()
        game.get_game().projectiles.append(projectiles.Projectiles.Demolisher(game.get_game().player.obj.pos, self.rot))

class Shadow(Gun):
    def on_start_attack(self):
        mx, my = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        self.x, self.y = mx, my
        self.face_to(0, 0)
        self.rotate(random.randint(-10, 10))
        self.forward(300)
        self.face_to(mx, my)
        if game.get_game().player.ammo_bullet[0] not in projectiles.AMMOS or not game.get_game().player.ammo_bullet[1]:
            self.timer = 0
            return
        if game.get_game().player.ammo_bullet[1] < constants.ULTIMATE_AMMO_BONUS and random.random() < self.ammo_save_chance + game.get_game().player.calculate_data('ammo_save', False) / 100:
            game.get_game().player.ammo_bullet = (
                game.get_game().player.ammo_bullet[0], game.get_game().player.ammo_bullet[1] - 1)
        game.get_game().projectiles.append(
            projectiles.AMMOS[game.get_game().player.ammo_bullet[0]]((self.x + game.get_game().player.obj.pos[0],
                                                                      self.y + game.get_game().player.obj.pos[1]),
                                                                     self.rot, self.spd,
                                                                     self.damages[dmg.DamageTypes.PIERCING]))

class Climax(Gun):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, projectile_speed: int,
                 auto_fire: bool = False, precision: int = 0, tail_col: tuple[int, int, int] | None = None, ammo_save_chance: float = 0.0):
        super().__init__(name, damages, kb, img, speed, at_time, projectile_speed, auto_fire, precision, tail_col, ammo_save_chance)
        cols = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255),
                (255, 0, 0)]
        self.cols = []
        for i in range(1, 8):
            s_c = cols[i - 1]
            e_c = cols[i]
            for j in range(1, 11):
                self.cols.append((s_c[0] + (e_c[0] - s_c[0]) * j / 10, s_c[1] + (e_c[1] - s_c[1]) * j / 10,
                                  s_c[2] + (e_c[2] - s_c[2]) * j / 10))

    def on_start_attack(self):
        self.tail_col = self.cols[0]
        if game.get_game().player.ammo_bullet[0] not in projectiles.AMMOS or not game.get_game().player.ammo_bullet[
            1]:
            self.timer = 0
            return
        mx, my = position.relative_position(
            position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        mx *= game.get_game().player.get_screen_scale()
        my *= game.get_game().player.get_screen_scale()
        for i in range(3):
            super().on_start_attack()
        self.x, self.y = random.randint(-1000, 1000), random.randint(-1000, 1000)
        sz = int(4 - math.floor(math.sqrt(random.randint(1, 9))))
        game.get_game().displayer.effect(fc.p_fade_circle(*position.displayed_position((game.get_game().player.obj.pos[0] + self.x,
                                                                                        game.get_game().player.obj.pos[1] + self.y)),
                                                          col=self.cols[0], sp=sz * 10,
                                                          t=6))
        self.face_to(mx, my)
        for i in range(sz):
            pj = projectiles.AMMOS[game.get_game().player.ammo_bullet[0]]((self.x + game.get_game().player.obj.pos[0],
                                                                           self.y + game.get_game().player.obj.pos[1]),
                                                                          self.rot + random.randint(-self.precision,
                                                                                                    self.precision),
                                                                          0,
                                                                          self.damages[dmg.DamageTypes.PIERCING])
            if self.tail_col is not None:
                pj.TAIL_COLOR = self.cols[0]
                pj.TAIL_SIZE = max(pj.TAIL_SIZE, 3)
                pj.TAIL_WIDTH = max(pj.TAIL_WIDTH, 6)
            game.get_game().projectiles.append(pj)
        self.x, self.y = 0, 0
        self.face_to(mx, my)
        self.cols.append(self.cols.pop(0))




class Astigmatism(Weapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, mana_cost: int,
                 auto_fire: bool = False, spell_name: str = ''):
        super().__init__(name, damages, kb, img, speed, at_time, auto_fire)
        self.pre_beams = [projectiles.Projectiles.BeamLight((0, 0), 0) for _ in range(8)]
        self.using_beam = projectiles.Projectiles.Beam((0, 0), 0)
        self.spell_name = spell_name
        i = 0
        for b in self.pre_beams:
            b.COLOR = (i * 8, 255 - i * 8, i * 8)
            b.DAMAGE_AS = self.name
            b.WIDTH = 20
            b.FOLLOW_PLAYER = True
            b.DURATION = 100
            b.DMG = self.damages[dmg.DamageTypes.MAGICAL] // 4
            i += 1
        self.using_beam.COLOR = (100, 255, 0)
        self.using_beam.DAMAGE_AS = self.name
        self.using_beam.WIDTH = 240
        self.using_beam.DURATION = 100
        self.mana_cost = mana_cost
        self.cb = 0

    def re_init(self):
        pass

    def on_end_attack(self):
        super().on_end_attack()
        self.cb = 0

    def on_attack(self):
        super().on_attack()
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        self.display = True
        if self.cb < 30:
            rts = self.cb ** 3 // 10
            for b in self.pre_beams:
                b.pos << game.get_game().player.obj.pos
                b.tick = 50
                b.rot = self.rot + math.sin(math.radians(rts)) * (30 - self.cb)
                b.update()
                rts += 45
        else:
            self.using_beam.pos << game.get_game().player.obj.pos
            self.using_beam.tick = 50
            self.using_beam.rot = self.rot
            self.using_beam.update()
        self.cb += 1
        if (game.get_game().player.mana >= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1) and
                1 in game.get_game().get_pressed_mouse()):
            self.timer = 5
            game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)


    def on_start_attack(self):
        super().on_start_attack()
        self.cb = 0
        if game.get_game().player.mana < round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1):
            self.timer = 0
            return
        game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)

class GreatForbiddenCurseLight(Weapon):
    def __init__(self, name, damages: dict[int, float], kb: float, img, speed: int, at_time: int, mana_cost: int,
                 talent_cost: float,
                 auto_fire: bool = False, spell_name: str = ''):
        super().__init__(name, damages, kb, img, speed, at_time, auto_fire)
        self.pre_beams = [projectiles.Projectiles.BeamLight((0, 0), 0) for _ in range(6)]
        self.using_beam = projectiles.Projectiles.Beam((0, 0), 0)
        self.spell_name = spell_name
        i = 0
        cols = ((255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255))
        for b in self.pre_beams:
            b.COLOR = cols[i]
            b.DAMAGE_AS = self.name.replace(' ', '_')
            b.WIDTH = 32
            b.FOLLOW_PLAYER = True
            b.DURATION = 100
            b.DMG = self.damages[dmg.DamageTypes.ARCANE] // 4
            b.DMG_TYPE = dmg.DamageTypes.ARCANE
            i += 1
        self.using_beam.COLOR = (255, 0, 0)
        self.using_beam.DAMAGE_AS = self.name.replace(' ', '_')
        self.using_beam.WIDTH = 320
        self.using_beam.DURATION = 100
        self.using_beam.DMG_TYPE = dmg.DamageTypes.ARCANE
        self.mana_cost = mana_cost
        self.talent_cost = talent_cost
        self.cb = 0

    def re_init(self):
        pass

    def on_end_attack(self):
        super().on_end_attack()
        self.cb = 0

    def on_attack(self):
        super().on_attack()
        self.face_to(
            *position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos()))))
        self.display = True
        if self.cb < 30:
            rts = self.cb ** 3 // 10
            for b in self.pre_beams:
                b.pos << game.get_game().player.obj.pos
                b.tick = 50
                b.rot = self.rot + math.sin(math.radians(rts)) * (30 - self.cb)
                b.update()
                rts += 60
        else:
            self.using_beam.pos << game.get_game().player.obj.pos
            self.using_beam.tick = 50
            self.using_beam.rot = self.rot
            self.using_beam.update()
        self.cb += 1
        if (game.get_game().player.mana >= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)
                and game.get_game().player.talent >= self.talent_cost and
                1 in game.get_game().get_pressed_mouse()):
            self.timer = 5
            game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)
            game.get_game().player.talent -= self.talent_cost


    def on_start_attack(self):
        super().on_start_attack()
        self.cb = 0
        if game.get_game().player.mana < round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1) or game.get_game().player.talent < self.talent_cost:
            self.timer = 0
            return
        game.get_game().player.mana -= round(self.mana_cost * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)
        game.get_game().player.talent -= self.talent_cost


WEAPONS = {}


def set_weapons():
    global WEAPONS
    weapons = {
        'null': SweepWeapon('null', {dmg.DamageTypes.PHYSICAL: 0}, 0,
                            'items_weapons_null', 0,
                            1, 40, 20),
        'arrow_thrower': Bow('arrow thrower', {dmg.DamageTypes.PIERCING: 3}, 0.3,
                             'items_weapons_arrow_thrower', 1,
                             4, 100, auto_fire=True),
        'wooden_sword': SweepWeapon('wooden sword', {dmg.DamageTypes.PHYSICAL: 8}, 0.1,
                                    'items_weapons_wooden_sword', 5,
                                    5, 18, 45),
        'copper_sword': SweepWeapon('copper sword', {dmg.DamageTypes.PHYSICAL: 10}, 0.3,
                                    'items_weapons_copper_sword', 8,
                                    8, 15, 60),
        'iron_sword': SweepWeapon('iron sword', {dmg.DamageTypes.PHYSICAL: 16}, 0.25,
                                  'items_weapons_iron_sword', 6,
                                  4, 27, 54),
        'cobalt_sword': SweepWeapon('cobalt sword', {dmg.DamageTypes.PHYSICAL: 15}, 0.3,
                                  'items_weapons_cobalt_sword', 4,
                                  5, 35, 120),
        'iron_blade': Blade('iron blade', {dmg.DamageTypes.PHYSICAL: 12}, 0.15,
                            'items_weapons_iron_blade', 4,
                            8, 30, 120),
        'cobalt_blade': Blade('cobalt blade', {dmg.DamageTypes.PHYSICAL: 14}, 0.2,
                            'items_weapons_cobalt_blade', 3,
                            7, 40, 160),
        'steel_sword': SweepWeapon('steel sword', {dmg.DamageTypes.PHYSICAL: 22}, 0.4,
                                   'items_weapons_steel_sword', 10,
                                   10, 16, 80),
        'silver_sword': SweepWeapon('silver sword', {dmg.DamageTypes.PHYSICAL: 26}, 0.4,
                                   'items_weapons_silver_sword', 8,
                                   8, 25, 120),
        'platinum_sword': SweepWeapon('platinum sword', {dmg.DamageTypes.PHYSICAL: 52}, 0.6,
                                      'items_weapons_platinum_sword', 0,
                                      15, 16, 120),
        'zirconium_sword': SweepWeapon('zirconium sword', {dmg.DamageTypes.PHYSICAL: 46}, 1,
                                      'items_weapons_zirconium_sword', 1,
                                      10, 25, 160),
        'platinum_blade': Blade('platinum blade', {dmg.DamageTypes.PHYSICAL: 28}, 0.1,
                                'items_weapons_platinum_blade', 10,
                                12, 30, 180),
        'e_wingblade': Blade('e wingblade', {dmg.DamageTypes.PHYSICAL: 36}, 0.4,
                             'items_weapons_e_wingblade', 2,
                             5, 50, 180),
        'tearblade': TearBlade('tearblade', {dmg.DamageTypes.PHYSICAL: 44}, 0.2,
                               'items_weapons_tearblade', 3, 9, 25, 160),
        'life_wooden_sword': LifeWoodenSword('life wooden sword', {dmg.DamageTypes.PHYSICAL: 22}, 1.2,
                                             'items_weapons_life_wooden_sword', 3,
                                             5, 36, 110),
        'magic_sword': MagicSword('magic sword', {dmg.DamageTypes.PHYSICAL: 50}, 0.7,
                                  'items_weapons_magic_sword', 0,
                                  16, 12, 96),
        'magic_blade': MagicBlade('magic blade', {dmg.DamageTypes.PHYSICAL: 25}, 0.5,
                                  'items_weapons_magic_blade', 0,
                                  1, 30, 15),
        'bloody_sword': BloodySword('bloody sword', {dmg.DamageTypes.PHYSICAL: 60}, 0.2,
                                    'items_weapons_bloody_sword', 2,
                                    10, 20, 100, auto_fire=True),
        'sunrise': Sunrise('sunrise', {dmg.DamageTypes.PHYSICAL: 70}, 0.3,
                           'items_weapons_sunrise', 1,
                           8, 40, 250),
        'mantle': Mantle('mantle', {dmg.DamageTypes.PHYSICAL: 45}, 0.2,
                         'items_weapons_mantle', 1,
                         9, 25, 150),
        'obsidian_sword': Blade('obsidian sword', {dmg.DamageTypes.PHYSICAL: 40}, 0.3,
                                'items_weapons_obsidian_sword', 2, 8, 40, 180),
        'swwwword': Swwwword('swwwword', {dmg.DamageTypes.PHYSICAL: 60}, 0.4,
                             'items_weapons_swwwword', 2, 8, 40, 200),
        'volcano': Volcano('volcano', {dmg.DamageTypes.PHYSICAL: 90}, 0.5, 'items_weapons_volcano',
                           2, 18, 20, 200),
        'doctor_expeller': DoctorExpeller('doctor expeller', {dmg.DamageTypes.PHYSICAL: 50}, 0.2,
                                            'items_weapons_doctor_expeller', 1,
                                            5, 50, 150),
        'virus_defeater': VirusDefeater('virus defeater', {dmg.DamageTypes.PHYSICAL: 100}, 2,
                                        'items_weapons_virus_defeater', 2,
                                        3, 100, 200),
        'sand_sword': SandSword('sand_sword', {dmg.DamageTypes.PHYSICAL: 110}, 0.3,
                                'items_weapons_sand_sword', 0,
                                6, 50, 120, auto_fire=True),
        'dim_heavysword': Blade('dim heavysword', {dmg.DamageTypes.PHYSICAL: 180}, 4,
                                'items_weapons_dim_heavysword', 7, 12, 30, 250),
        'nights_edge': NightsEdge('nights edge', {dmg.DamageTypes.PHYSICAL: 90}, 0.6,
                                  'items_weapons_nights_edge',
                                  1, 18, 20, 100),
        'chaos_reap': ChaosReap('chaos reap', {dmg.DamageTypes.PHYSICAL: 200}, 3,
                                 'items_weapons_chaos_reap', 7, 11, 30, 180),
        'storm_swift_sword': SwiftSword('storm swift sword', {dmg.DamageTypes.PHYSICAL: 75}, 0.8,
                                               'items_weapons_storm_swift_sword',
                                               0, 3, 100, 180, auto_fire=True),
        'spiritual_stabber': SpiritualStabber('spiritual stabber', {dmg.DamageTypes.PHYSICAL: 120}, 0.5,
                                              'items_weapons_spiritual_stabber',
                                              2, 6, 40, 170),
        'palladium_sword': Blade('palladium sword', {dmg.DamageTypes.PHYSICAL: 120}, 1,
                                 'items_weapons_palladium_sword', 1, 4, 50, 80),
        'mithrill_sword': Blade('mithrill sword', {dmg.DamageTypes.PHYSICAL: 240}, 2,
                                'items_weapons_mithrill_sword', 1, 8, 30, 160),
        'titanium_sword': Blade('titanium sword', {dmg.DamageTypes.PHYSICAL: 320}, 2.5,
                                'items_weapons_titanium_sword', 1, 10, 40, 200),
        'rune_blade': RuneBlade('rune blade', {dmg.DamageTypes.PHYSICAL: 95}, 0.5,
                                'items_weapons_rune_blade', 1, 5, 50, 150, True),
        'glacier': Glacier('glacier', {dmg.DamageTypes.PHYSICAL: 125}, 2,
                           'items_weapons_glacier',
                           2, 7, 40, 100),
        'balanced_stabber': BalancedStabber('balanced stabber', {dmg.DamageTypes.PHYSICAL: 144}, 2,
                                            'items_weapons_balanced_stabber',
                                            1, 7, 50, 150),
        'excalibur': Excalibur('excalibur', {dmg.DamageTypes.PHYSICAL: 140}, 0.8,
                               'items_weapons_excalibur',
                               1, 12, 59, 180),
        'guardian': Guardian('guardian', {dmg.DamageTypes.PHYSICAL: 100}, 3,
                             'items_weapons_guardian',
                             4, 8, 30, 120,),
        'remote_sword': RemoteWeapon('remote sword', {dmg.DamageTypes.PHYSICAL: 144}, 0.8,
                                      'items_weapons_remote_sword',
                                      1, 5, 72, 180, auto_fire=True),
        'gaia_paladin_spear': GaiaPaladinSpear('gaia paladin spear', {dmg.DamageTypes.PHYSICAL: 100}, .5,
                                               'items_weapons_gaia_paladin_spear',
                                               2, 8, 40, 250, auto_fire=True),
        'true_excalibur': TrueExcalibur('true excalibur',
                                        {dmg.DamageTypes.PHYSICAL: 155}, 1,
                                        'items_weapons_true_excalibur',
                                        1, 4, 88, 180),
        'true_nights_edge': TrueNightsEdge('true nights edge',
                                           {dmg.DamageTypes.PHYSICAL: 180, dmg.DamageTypes.MAGICAL: 130}, 2,
                                           'items_weapons_true_nights_edge',
                                           1, 32, 60, 100),
        'wooden_club': Blade('wooden club', {dmg.DamageTypes.PHYSICAL: 480}, 5,
                             'items_weapons_wooden_club', 2, 5, 50, 140),
        'muramasa': Muramasa('muramasa', {dmg.DamageTypes.PHYSICAL: 222}, 3.2,
                             'items_weapons_muramasa',
                             0, 6, 36, 120),
        'forbidden_oath': ForbiddenOath('forbidden oath', {dmg.DamageTypes.PHYSICAL: 190}, 2.5,
                                         'items_weapons_forbidden_oath',
                                        4, 7, 30, 100),
        'fiery_iceberg': FieryIceberg('fiery iceberg', {dmg.DamageTypes.PHYSICAL: 160}, 1.5,
                                       'items_weapons_fiery_iceberg',
                                       2, 8, 30, 150),
        'perseverance_sword': PerseveranceSword('perseverance sword', {dmg.DamageTypes.PHYSICAL: 140}, 2,
                                                'items_weapons_perseverance_sword',
                                                1, 6, 28, 90),
        'black_hole_sword': BlackHoleSword('black hole sword', {dmg.DamageTypes.PHYSICAL: 130}, 0,
                                           'items_weapons_black_hole_sword',
                                           0, 6, 60, 90),
        'life_devourer': LifeDevourer('life devourer', {dmg.DamageTypes.PHYSICAL: 320, dmg.DamageTypes.MAGICAL: 288},
                                      0.8, 'items_weapons_life_devourer',
                                      1, 5, 70, 150),
        'jevil_knife': JevilKnife('jevil knife', {dmg.DamageTypes.PHYSICAL: 720}, 0.5, 'items_weapons_jevil_knife',
                                  2, 20, 30, 120),
        'the_blade': TheBlade('the blade', {dmg.DamageTypes.PHYSICAL: 500}, 7.2, 'items_weapons_the_blade',
                              4, 8, 60, 180),
        'demon_blade__muramasa': Muramasa('demon blade  muramasa', {dmg.DamageTypes.PHYSICAL: 540}, 12,
                                          'items_weapons_demon_blade__muramasa',
                                          0, 4, 110, 280, _type=1),
        'uncanny_valley': UncannyValley('uncanny valley', {dmg.DamageTypes.PHYSICAL: 560}, 18, 'items_weapons__uncanny_valley',
                                         0, 10, 100, 110),
        'hour_hand': HourHand('hour hand', {dmg.DamageTypes.PHYSICAL: 880}, 12, 'items_weapons_hour_hand',
                              0, 40, 9, 0),
        'deconstruction': Deconstruction('deconstruction', {dmg.DamageTypes.PHYSICAL: 600}, 12, 'items_weapons_deconstruction',
                                         0, 6, 50, 150),
        'starfury': Starfury('starfury', {dmg.DamageTypes.PHYSICAL: 400}, 8, 'items_weapons_starfury',
                             0, 5, 60, 120),
        'lysis': Lysis('lysis', {dmg.DamageTypes.PHYSICAL: 888}, 12, 'items_weapons_lysis',
                       6, 6, 20, 120),
        'star_wrath': StarWrath('star wrath', {dmg.DamageTypes.PHYSICAL: 540}, 16, 'items_weapons_star_wrath',
                                0, 5, 60, 120),
        'galaxy_broadsword': GalaxyBroadsword('galaxy broadsword', {dmg.DamageTypes.PHYSICAL: 4500, dmg.DamageTypes.THINKING: 3500}, 38,
                                               'items_weapons_galaxy_broadsword',
                                               0, 8, 45, 200),
        'eternal_echo': EternalEcho('eternal echo', {dmg.DamageTypes.PHYSICAL: 4500, dmg.DamageTypes.THINKING: 4000}, 45,
                                               'items_weapons_eternal_echo',
                                               0, 8, 45, 200),
        'star_of_devotion': StarOfDevotion('star of devotion', {dmg.DamageTypes.PHYSICAL: 5500, dmg.DamageTypes.THINKING: 3500}, 45,
                                             'items_weapons_star_of_devotion',
                                             0, 6, 60, 200),
        'quark_rusher': QuarkRusher('quark rusher', {dmg.DamageTypes.PHYSICAL: 4800, dmg.DamageTypes.THINKING: 2400}, 15,
                                       'items_weapons_quark_rusher',
                                       5, 45, 30, 200),

        'highlight': Highlight('highlight', {dmg.DamageTypes.PHYSICAL: 1600, dmg.DamageTypes.THINKING: 1600}, 16, 'items_weapons_highlight',
                               0, 3, 30, 60, auto_fire=True),
        'turning_point': ComplexWeapon('turning point', {dmg.DamageTypes.PHYSICAL: 5000, dmg.DamageTypes.THINKING: 6000},
                                       {dmg.DamageTypes.PHYSICAL: 5000}, 45, 'items_weapons_turning_point',
                                       1, 3, 2, 130, 280, 400, 400,
                                       True, [0, 0, 0, 0, 1, 1], TurningPointSweep, TurningPointSpear),

        'spikeflower': Spear('spikeflower', {dmg.DamageTypes.PHYSICAL: 5}, 1.8, 'items_weapons_spikeflower',
                             1, 3, 30, 60, auto_fire=True),
        'spear': Spear('spear', {dmg.DamageTypes.PHYSICAL: 15}, 0.5, 'items_weapons_spear',
                       2, 6, 15, 60, auto_fire=True),
        'ranseur': Spear('ranseur', {dmg.DamageTypes.PHYSICAL: 18}, 0.8, 'items_weapons_spear',
                       3, 5, 25, 70, auto_fire=True),
        'platinum_spear': Spear('platinum spear', {dmg.DamageTypes.PHYSICAL: 35}, 3, 'items_weapons_platinum_spear',
                                2, 4, 30, 80, auto_fire=True),
        'zirconium_spear': Spear('zirconium spear', {dmg.DamageTypes.PHYSICAL: 45}, 5, 'items_weapons_zirconium_spear',
                                  3, 5, 30, 90, auto_fire=True),
        'blood_pike': BloodPike('blood pike', {dmg.DamageTypes.PHYSICAL: 60}, 5.4, 'items_weapons_blood_pike',
                                1, 5, 50, 150, auto_fire=True),
        'fur_spear': FurSpear('fur spear', {dmg.DamageTypes.PHYSICAL: 48}, 1.7, 'items_weapons_fur_spear',
                              0, 4, 50, 120, auto_fire=True),
        'firite_spear': Spear('firite spear', {dmg.DamageTypes.PHYSICAL: 75}, 0.7, 'items_weapons_firite_spear',
                              2, 10, 20, 100, auto_fire=True),
        'valkyrien': Valkyrien('valkyrien', {dmg.DamageTypes.PHYSICAL: 70}, 1.2, 'items_weapons_valkyrien',
                               4, 9, 40, 240, auto_fire=True),
        'aerialite_shortsword': Spear('aerialite shortsword', {dmg.DamageTypes.PHYSICAL: 90}, 1, 'items_weapons_aerialite_shortsword',
                                      6, 6, 20, 60, auto_fire=True),
        'forgotten_shortsword': Spear('forgotten shortsword', {dmg.DamageTypes.PHYSICAL: 110}, 1, 'items_weapons_forgotten_shortsword',
                                      6, 7, 20, 80, auto_fire=True),
        'seaprick': Seaprick('seaprick', {dmg.DamageTypes.PHYSICAL: 60}, .6, 'items_weapons_seaprick',
                             2, 6, 50, 160, auto_fire=True),
        'poseidon': Poseidon('poseidon', {dmg.DamageTypes.PHYSICAL: 90}, 3, 'items_weapons_poseidon',
                               5, 11, 30, 240, auto_fire=True),
        'nights_pike': Spear('nights pike', {dmg.DamageTypes.PHYSICAL: 125}, 1.8, 'items_weapons_nights_pike',
                             2, 5, 60, 160, auto_fire=True),
        'energy_spear': ComplexWeapon('energy spear', {dmg.DamageTypes.PHYSICAL: 180},
                                      {dmg.DamageTypes.PHYSICAL: 220}, 2, 'items_weapons_energy_spear',
                                      2, 8, 6, 40, 120, 80,
                                      250, auto_fire=True, combat=[0, 0, 0, 0, 1]),
        'millennium_persists': ComplexWeapon('millennium persists', {dmg.DamageTypes.PHYSICAL: 250},
                                             {dmg.DamageTypes.PHYSICAL: 200}, 2, 'items_weapons_millennium_persists',
                                             0, 6, 3, 60, 180, 160,
                                             300, auto_fire=True, combat=[0, 0, 0, 0, 1, 1], sweep_type=MillenniumPersistSweep),
        'metal_hand': Spear('metal hand', {dmg.DamageTypes.PHYSICAL: 3200}, 1.2, 'items_weapons_metal_hand',
                            2, 8, 80, 400, auto_fire=True),
        'wilson_knife': ComplexWeapon('wilson knife', {dmg.DamageTypes.PHYSICAL: 120}, {dmg.DamageTypes.PHYSICAL: 450},
                                      3, 'items_weapons_wilson_knife', 1, 7, 7, 50, 200, 60, 200,
                                      auto_fire=True, combat=[1, 1, 1, 1, 0], sweep_type=WilsonKnifeBlade, spear_type=WilsonKnifeSpear),

        'prophecy': ProphecyI('prophecy', {dmg.DamageTypes.PHYSICAL: 1200, dmg.DamageTypes.THINKING: 4800}, 8, 'items_weapons_prophecy',
                              2, 8, 50, 280),
        'prophecy_ii': ProphecyII('prophecy ii', {dmg.DamageTypes.PHYSICAL: 4500, dmg.DamageTypes.THINKING: 1500}, 15, 'items_weapons_prophecy_ii',
                                1, 7, 70, 300, auto_fire=True),

        'zenith': Zenith('zenith', {dmg.DamageTypes.PHYSICAL: 0, dmg.DamageTypes.THINKING: 0}, .01, 'items_weapons_zenith',
                        0, 6, 50, 200),

        'bow': Bow('bow', {dmg.DamageTypes.PIERCING: 3}, 0.1, 'items_weapons_bow',
                   3, 8, 10),
        'copper_bow': Bow('copper bow', {dmg.DamageTypes.PIERCING: 10}, 0.2, 'items_weapons_copper_bow',
                          4, 6, 18),
        'iron_bow': Bow('iron bow', {dmg.DamageTypes.PIERCING: 6}, 0.15, 'items_weapons_iron_bow',
                        3, 5, 40, auto_fire=True),
        'sky_bow': Bow('sky bow', {dmg.DamageTypes.PIERCING: 14}, 0.4, 'items_weapons_sky_bow',
                        4, 7, 120, auto_fire=True),
        'steel_bow': Bow('steel bow', {dmg.DamageTypes.PIERCING: 35}, 0.3, 'items_weapons_steel_bow',
                         9, 12, 70),
        'bone_bow': Bow('bone bow', {dmg.DamageTypes.PIERCING: 28}, 0.3, 'items_weapons_bone_bow',
                         5, 9, 240),
        'platinum_bow': Bow('platinum bow', {dmg.DamageTypes.PIERCING: 12}, 0.4, 'items_weapons_platinum_bow',
                            2, 6, 50, auto_fire=True),
        'bloody_bow': Bow('bloody bow', {dmg.DamageTypes.PIERCING: 45}, 0.5, 'items_weapons_bloody_bow',
                          5, 9, 120, auto_fire=True),
        'aerialite_bow': Bow('aerialite bow', {dmg.DamageTypes.PIERCING: 35}, 0.3, 'items_weapons_aerialite_bow',
                             3, 8, 300, auto_fire=True),
        'forgotten_bow': Bow('forgotten bow', {dmg.DamageTypes.PIERCING: 70}, 0.4, 'items_weapons_forgotten_bow',
                             7, 12, 120, auto_fire=True),
        'forests_bow': ForestsBow('forests bow', {dmg.DamageTypes.PIERCING: 22}, 3, 'items_weapons_forests_boew',
                                  1, 2, 220, auto_fire=True),
        'world_bow': WorldBow('world bow', {dmg.DamageTypes.PIERCING: 32}, 0.5, 'items_weapons_world_bow',
                               3, 4, 400, auto_fire=True, precision=2),
        'forget': WForget('forget', {dmg.DamageTypes.PIERCING: 35}, 3, 'items_weapons_forget',
                          0, 10, 400, auto_fire=True),
        'sky': WSky('sky', {dmg.DamageTypes.PIERCING: 80}, 3, 'items_null',
                    0, 40, 600, auto_fire=True, tail_col=(255, 255, 0), tw=5),
        'heavybow': HeavyBow('heavybow', {dmg.DamageTypes.PIERCING: 70}, 2, 'items_weapons_heavybow',
                             10, 5, 0, auto_fire=True),
        'kuangkuangkuang': KuangKuangKuang('kuangkuangkuang', {dmg.DamageTypes.PIERCING: 6}, 0.5, 'items_weapons_kuangkuangkuang',
                                            0, 1, 550, auto_fire=True, tail_col=(200, 255, 255), ammo_save_chance=1 / 3),
        'recurve_bow': Bow('recurve bow', {dmg.DamageTypes.PIERCING: 100}, 0.6, 'items_weapons_recurve_bow',
                           6, 2, 500, auto_fire=True),
        'aiolos': Aiolos('aiolos', {dmg.DamageTypes.PIERCING: 90}, 1.5, 'items_weapons_aiolos',
                         2, 4, 800, auto_fire=True),
        'spiritual_piercer': Bow('spiritual piercer', {dmg.DamageTypes.PIERCING: 110}, 0.5,
                                 'items_weapons_spiritual_piercer',
                                 1, 4, 650, auto_fire=True),
        'discord_storm': DiscordStorm('discord storm', {dmg.DamageTypes.PIERCING: 98}, 0.5,
                                      'items_weapons_discord_storm',
                                      1, 7, 200, auto_fire=True),
        'daedalus_stormbow': DaedelusStormbow('daedalus stormbow', {dmg.DamageTypes.PIERCING: 66}, 0.5,
                                              'items_weapons_daedalus_stormbow',
                                              0, 2, 500, auto_fire=True, ammo_save_chance=1 / 4),
        'forward_bow': ForwardBow('forward bow', {dmg.DamageTypes.PIERCING: 160}, 0.5, 'items_weapons_forward_bow',
                                  0, 7, 150, auto_fire=True, ammo_save_chance=1 / 2),
        'true_daedalus_stormbow': TrueDaedalusStormbow('true daedalus stormbow', {dmg.DamageTypes.PIERCING: 88}, 0.5,
                                                       'items_weapons_true_daedalus_stormbow',
                                                       0, 3, 1000, auto_fire=True, ammo_save_chance=1 / 3),
        'bow_of_sanction': Bow('bow of sanction', {dmg.DamageTypes.PIERCING: 1800}, 0.5, 'items_weapons_bow_of_sanction',
                               7, 5, 2000, auto_fire=True, tail_col=(255, 255, 0)),
        'lazer_rain': LazerRain('lazer rain', {dmg.DamageTypes.PIERCING: 500}, 0.5, 'items_weapons_lazer_rain',
                                1, 3, 500, auto_fire=True, tail_col=(127, 127, 255), ammo_save_chance=1 / 2),
        'accelerationism': Accelerationism('accelerationism', {dmg.DamageTypes.PIERCING: 420}, 0.5,
                                           'items_weapons_accelerationism',
                                           0, 2, 320, True, ammo_save_chance=2 / 3),
        'resolution': Resolution('resolution', {dmg.DamageTypes.PIERCING: 720}, 0.5, 'items_weapons_resolution',
                                  0, 2, 2200, True, ammo_save_chance=3 / 4),

        'pistol': Gun('pistol', {dmg.DamageTypes.PIERCING: 24}, 0.1, 'items_weapons_pistol',
                      3, 15, 15, precision=2),
        'rifle': Gun('rifle', {dmg.DamageTypes.PIERCING: 14}, 0.2, 'items_weapons_rifle',
                     6, 6, 20, auto_fire=True, precision=4),
        'submachine_gun': Gun('submachine gun', {dmg.DamageTypes.PIERCING: 2}, 0.15, 'items_weapons_submachine_gun',
                              0, 2, 50, auto_fire=True, precision=3, ammo_save_chance=1 / 3),
        'magma_assaulter': MagmaAssaulter('magma assaulter', {dmg.DamageTypes.PIERCING: 30}, 0.5,
                                          'items_weapons_magma_assaulter',
                                          2, 5, 100, auto_fire=True, precision=2, ammo_save_chance=1 / 5),
        'aerialite_pulse': Gun('aerialite pulse', {dmg.DamageTypes.PIERCING: 70}, 3,
                               'items_weapons_aerialite_pulse', 7, 15,
                               400, auto_fire=True, precision=1),
        'forgotten_assaulter': Gun('forgotten assaulter', {dmg.DamageTypes.PIERCING: 55}, 0.5,
                                   'items_weapons_forgotten_assaulter',
                                   3, 7, 200, auto_fire=True, precision=3, ammo_save_chance=1 / 5),
        'gaze': Gaze('gaze', {dmg.DamageTypes.PIERCING: 7}, 0.5, 'items_weapons_gaze',
                     2, 3, 100, auto_fire=True, precision=3),
        'witness': Witness('witness', {dmg.DamageTypes.PIERCING: 35}, 2, 'items_weapons_witness',
                     4, 5, 100, auto_fire=True, precision=2),
        'phoenix_exploder': PhoenixExploder('phoenix exploder', {dmg.DamageTypes.PIERCING: 70}, 0.5,
                                             'items_weapons_phoenix_exploder', 8, 10, 500, True, 2,
                                            tail_col=(255, 0, 0), ammo_save_chance=1 / 5),
        'minishark': Gun('minishark', {dmg.DamageTypes.PIERCING: 45}, 0.5, 'items_weapons_minishark',
                         0, 1, 300, auto_fire=True, precision=1),
        'shadow': Shadow('shadow', {dmg.DamageTypes.PIERCING: 90}, 1.2, 'items_weapons_shadow',
                         2, 3, 200, auto_fire=True, precision=3, ammo_save_chance=1 / 4),
        'palladium_gun': Gun('palladium gun', {dmg.DamageTypes.PIERCING: 120}, 0.2, 'items_weapons_palladium_gun',
                             1, 2, 300, auto_fire=True, precision=3),
        'mithrill_gun': Gun('mithrill gun', {dmg.DamageTypes.PIERCING: 200}, 0.3, 'items_weapons_mithrill_gun',
                            1, 5, 800, auto_fire=True, precision=1),
        'titanium_gun': Gun('titanium gun', {dmg.DamageTypes.PIERCING: 800}, 0.4, 'items_weapons_titanium_gun',
                            3, 20, 1500, auto_fire=True, precision=1),
        'dark_exploder': DarkExploder('dark exploder', {dmg.DamageTypes.PIERCING: 400}, 0.5, 'items_weapons_dark_exploder',
                                      6, 8, 100, auto_fire=True, precision=1),
        'demolisher': Demolisher('demolisher', {dmg.DamageTypes.PIERCING: 80}, 0.5, 'items_weapons_demolisher',
                                  2, 5, 300, auto_fire=True, precision=1),
        'true_shadow': Gun('true shadow', {dmg.DamageTypes.PIERCING: 1800}, 0.5, 'items_weapons_true_shadow',
                           5, 10, 5000, auto_fire=True, precision=2),
        'shotgun': Shotgun('shotgun', {dmg.DamageTypes.PIERCING: 540}, 0.1, 'items_weapons_shotgun',
                            3, 8, 1000, auto_fire=True, precision=12, ammo_save_chance=2 / 3),
        'justice_shotgun': Shotgun('justice shotgun', {dmg.DamageTypes.PIERCING: 120}, 0.1, 'items_weapons_justice_shotgun',
                                   2, 2, 500, auto_fire=True, precision=25, ammo_save_chance=3 / 4),
        'climax': Climax('climax', {dmg.DamageTypes.PIERCING: 240}, 0.5, 'items_weapons_climax',
                      0, 0, 8000, auto_fire=True, precision=1, tail_col=(255, 0, 0), ammo_save_chance=4 / 5),

        'lazer_gun': LazerGun('lazer gun', {dmg.DamageTypes.PIERCING: 280}, 0.5, 'items_weapons_lazer_gun',
                              1, 12, 380, auto_fire=True, ammo_save_chance=1 / 2),
        'lazer_sniper': LazerGun('lazer sniper', {dmg.DamageTypes.PIERCING: 1800}, 0.5, 'items_weapons_lazer_sniper',
                                60, 12, 800, lazer_len=2, auto_fire=True),
        'matter_disintegrator': LazerGun('matter disintegrator', {dmg.DamageTypes.PIERCING: 560}, 0.5,
                                          'items_weapons_matter_disintegrator',
                                          3, 7, 1000, lazer_len=5, auto_fire=True, lazer_width=120,
                                         lazer_col=(180, 255, 150)),

        'rocket_launcher': RocketLauncher('rocket launcher', {dmg.DamageTypes.PIERCING: 24}, 0.5,
                                          'items_weapons_rocket_launcher', 12, 6, 200,
                                          auto_fire=True, ammo_save_chance=1 / 10, precision=15),
        'rapid_rocket_launcher': RocketLauncher('rapid rocket launcher', {dmg.DamageTypes.PIERCING: 45}, 0.5,
                                                'items_weapons_rapid_rocket_launcher', 2, 3, 150,
                                                 auto_fire=True, ammo_save_chance=1 / 8, precision=10, m_range=300),
        'rocket_launcher_v2': RocketLauncher('rocket launcher v2', {dmg.DamageTypes.PIERCING: 144}, 0.5,
                                             'items_weapons_rocket_launcher_v2', 4, 6, 500,
                                             auto_fire=True, ammo_save_chance=1 / 10, precision=5, m_range=-200),
        'rapid_rocket_launcher_v2': RocketLauncher('rapid rocket launcher v2', {dmg.DamageTypes.PIERCING: 125}, 0.5,
                                                    'items_weapons_rapid_rocket_launcher_v2', 1, 3, 720,
                                                     auto_fire=True, ammo_save_chance=1 / 5, precision=8, m_range=100),
        'rocket_launcher_v3': RocketLauncher('rocket launcher v3', {dmg.DamageTypes.PIERCING: 648}, 0.5,
                                             'items_weapons_rocket_launcher_v3', 3, 8, 1000,
                                             auto_fire=True, precision=2, m_range=-900, mode=1),
        'rapid_rocket_launcher_v3': RocketLauncher('rapid rocket launcher v3', {dmg.DamageTypes.PIERCING: 288}, 0.5,
                                                    'items_weapons_rapid_rocket_launcher_v3', 0, 2, 1500,
                                                     auto_fire=True, ammo_save_chance=1 / 4, precision=9, m_range=-100, mode=1),
        'rocket_launcher_v4': RocketLauncher('rocket launcher v4', {dmg.DamageTypes.PIERCING: 1024}, 0.5,
                                             'items_weapons_rocket_launcher_v4', 3, 8, 2000,
                                             auto_fire=True, precision=0, m_range=-1900, mode=2),
        'rapid_rocket_launcher_max': RocketLauncher('rapid rocket launcher max', {dmg.DamageTypes.PIERCING: 880}, 0.5,
                                                    'items_weapons_rapid_rocket_launcher_max', 0, 1, 4000,
                                                    auto_fire=True, precision=2, ammo_save_chance=4 / 5, m_range=-1000, mode=2),



        'copper_knife': ThiefWeapon('copper knife', {dmg.DamageTypes.PIERCING: 9}, 0.3, 'items_weapons_copper_knife',
                                     5, 10, 18, 72, 20, 240),
        'dagger': ThiefWeapon('dagger', {dmg.DamageTypes.PIERCING: 12}, 0.2, 'items_weapons_dagger',
                               1, 5, 36, 108, 10, 560),
        'platinum_doubleknife': ThiefDoubleKnife('platinum doubleknife', {dmg.DamageTypes.PIERCING: 24}, 0.3,
                                                  'items_weapons_platinum_doubleknife', 1, 6, 54, 216,
                                                 8, 720),
        'bloody_shortsword': ThiefWeapon('bloody shortsword', {dmg.DamageTypes.PIERCING: 36}, 0.2,
                                          'items_weapons_bloody_shortsword', 1, 3, 90, 180, 12, 1800),
        'obsidian_knife': ThiefWeapon('obsidian knife', {dmg.DamageTypes.PIERCING: 66}, 0.3,
                                       'items_weapons_obsidian_knife', 1, 4, 50, 150, 10, 1800),
        'twilight_shortsword': ThiefWeapon('twilight shortsword', {dmg.DamageTypes.PIERCING: 66}, 0.3,
                                            'items_weapons_twilight_shortsword', 1, 8, 48, 144, 18, 1200),
        'apple_knife': ThiefWeapon('apple knife', {dmg.DamageTypes.PIERCING: 58}, 0.3, 'items_weapons_apple_knife',
                                    1, 4, 80, 240, 7, 1000),
        'grenade': ThrowerThiefWeapon('grenade', {dmg.DamageTypes.PIERCING: 188}, 0.2, 'items_weapons_grenade',
                               7, 10, 2, 2, 18, 1600, 10),
        'dawn_shortsword': ThiefWeapon('dawn shortsword', {dmg.DamageTypes.PIERCING: 88}, 0.6,
                                        'items_weapons_dawn_shortsword', 1, 8, 48, 144, 16, 1800),
        'night_twinsword': ThiefDoubleKnife('night twinsword', {dmg.DamageTypes.PIERCING: 108}, 0.4,
                                             ('items_weapons_twilight_shortsword', 'items_weapons_dawn_shortsword'),
                                            0, 10, 24, 168, 12, 2400),
        'storm_stabber': StormStabber('storm stabber', {dmg.DamageTypes.PIERCING: 98}, 0.3,
                                       'items_weapons_storm_stabber', 1, 12, 40, 360,
                                      10, 5600),
        'jade_grenade': ThrowerThiefWeapon('jade grenade', {dmg.DamageTypes.PIERCING: 158}, 0.2, 'items_weapons_jade_grenade',
                                    5, 10, 2, 1, 15, 1800, 16),
        'spiritual_knife': ThiefWeapon('spiritual knife', {dmg.DamageTypes.PIERCING: 118}, 0.5,
                                         'items_weapons_spiritual_knife', 0, 6, 48, 144, 8, 2000),
        'daedalus_knife': ThiefWeapon('daedalus knife', {dmg.DamageTypes.PIERCING: 132}, 0.5,
                                       'items_weapons_daedalus_knife', 0, 4, 50, 150, 4, 2000),
        'daedalus_twinknife': ThiefDoubleKnife('daedalus twinknife', {dmg.DamageTypes.PIERCING: 100}, 0.5,
                                               ('items_weapons_spiritual_knife', 'items_weapons_daedalus_knife'),
                                               0, 5, 40, 120, 6, 1800,
                                               (((200, 200, 200), (100, 100, 255)), ((255, 100, 100), (100, 100, 255))), 3),
        'true_twinblade': ThiefDoubleKnife('true twinblade', {dmg.DamageTypes.PIERCING: 320}, 0.5,
                                             ('items_weapons_true_twinblade_1', 'items_weapons_true_twinblade_2'),
                                             0, 6, 50, 250, 6, 100,
                                           (((0, 0, 100), (200, 100, 100)), ((0, 100, 0), (100, 200, 150))), 6),
        'chaos_chaos': ThiefDoubleKnife('chaos chaos', {dmg.DamageTypes.PIERCING: 320}, 0.5,
                                        ('items_weapons_chaos_chaos1', 'items_weapons_chaos_chaos2'), 0,
                                        8, 60, 300, 10, 12000,
                                   (((0, 0, 0), (255, 255, 255)), ((255, 255, 255), (0, 0, 0))), 6),
        'time_flies': ThiefDoubleKnife('time flies', {dmg.DamageTypes.PIERCING: 200}, 0.5,
                                        'items_weapons_time_flies', 0, 5, 40, 120,
                                       4, 1800, dcols=((255, 200, 150), (255, 255, 255))),
        'generation': GenerationI('generation', {dmg.DamageTypes.PIERCING: 16000, dmg.DamageTypes.THINKING: 4000}, 3,
                                       ('items_weapons_generation_l', 'items_weapons_generation_r'), 0, 9, 30, 200,
                                       30, 4500, dcols=(((143, 222, 93), (207, 255, 112)), ((0, 255, 255), (127, 255, 255))), dsz=16),
        'generation_ii': GenerationII('generation ii', {dmg.DamageTypes.PIERCING: 80000}, 10,
                                      'items_weapons_generation_ii', 5, 25, 5000, auto_fire=True, precision=0,
                                      tail_col=(71, 239, 174), tw=40, ts=5),

        'shuriken': ThrowerThiefWeapon('shuriken', {dmg.DamageTypes.PIERCING: 5}, 0, 'items_weapons_shuriken',
                                      1, 1, 2, 1, 15, 1200, 20),
        'spikeball': ThrowerThiefWeapon('spikeball', {dmg.DamageTypes.PIERCING: 120}, 0, 'items_weapons_spikeball',
                                       10, 10, 2, 1, 35, 800, 4),

        'glowing_splint': MagicWeapon('glowing splint', {dmg.DamageTypes.MAGICAL: 3}, 0.1,
                                      'items_weapons_glowing_splint', 6,
                                      10, projectiles.Projectiles.Glow, 4, spell_name='Glow Spawn'),
        'copper_wand': MagicWeapon('copper wand', {dmg.DamageTypes.MAGICAL: 12}, 0.2,
                                   'items_weapons_copper_wand', 8,
                                   8, projectiles.Projectiles.CopperWand, 5, spell_name='Copper Bomb'),
        'iron_wand': MagicWeapon('iron wand', {dmg.DamageTypes.MAGICAL: 18}, 0.1,
                                 'items_weapons_iron_wand', 2,
                                 6, projectiles.Projectiles.IronWand, 4, spell_name='Iron Bomb'),
        'sky_wand': MagicWeapon('sky wand', {dmg.DamageTypes.MAGICAL: 12}, 0.2,
                                 'items_weapons_sky_wand', 2,
                                 2, projectiles.Projectiles.IronWand, 3, spell_name='Sky Energy'),
        'cactus_wand': MagicWeapon('cactus wand', {dmg.DamageTypes.MAGICAL: 4}, 0.2,
                                    'items_weapons_cactus_wand', 2,
                                    10, projectiles.Projectiles.CactusWand, 18, spell_name='Cactus Spawning'),
        'watcher_wand': MagicWeapon('watcher wand', {dmg.DamageTypes.MAGICAL: 12}, 0.2,
                                    'items_weapons_watcher_wand', 8,
                                    2, projectiles.Projectiles.WatcherWand, 10, spell_name='Watch'),
        'blood_watcher_wand': MagicWeapon('blood watcher wand', {dmg.DamageTypes.MAGICAL: 40}, 0.2,
                                    'items_weapons_blood_watcher_wand', 12,
                                    5, projectiles.Projectiles.BloodWatcherWand, 20, spell_name='Scarlett Watch'),
        'platinum_wand': MagicWeapon('platinum wand', {dmg.DamageTypes.MAGICAL: 32}, 0.3,
                                     'items_weapons_platinum_wand', 2,
                                     5, projectiles.Projectiles.PlatinumWand, 9, True,
                                     'Energy Bomb'),
        'mana_wand': MagicWeapon('mana wand', {dmg.DamageTypes.MAGICAL: 66}, 0.2,
                                 'items_weapons_mana_wand', 3,
                                 7, projectiles.Projectiles.ManaWand, 14, True,
                                  'Mana Erupt'),

        'life_wooden_wand': MagicWeapon('life wooden wand', {dmg.DamageTypes.MAGICAL: 28}, 0.4,
                                        'items_weapons_life_wooden_wand', 1,
                                        4, projectiles.Projectiles.LifeWoodenWand, 18, True,
                                    'Earth\'s Lazer'),
        'burning_book': MagicWeapon('burning book', {dmg.DamageTypes.MAGICAL: 50}, 0.5,
                                    'items_weapons_burning_book', 5,
                                    10, projectiles.Projectiles.BurningBook, 9, True,
                                    'Flame'),
        'talent_book': MagicWeapon('talent book', {dmg.DamageTypes.MAGICAL: 25}, 0.7,
                                   'items_weapons_talent_book', 0,
                                   2, projectiles.Projectiles.TalentBook, 2, True,
                                   'Smart Ball'),
        'furfur': MagicWeapon('furfur', {dmg.DamageTypes.MAGICAL: 40}, 0.5,
                               'items_weapons_furfur', 1,
                               1, projectiles.Projectiles.Furfur, 5, True,
                               'Furious Fury'),
        'dydy': MagicWeapon('dydy', {dmg.DamageTypes.MAGICAL: 80}, 0.5,
                            'items_weapons_dydy', 2, 2,
                            projectiles.Projectiles.Dydy, 13, True,
                            'Expected death'),
        'hematology': Hematology('hematology', 'items_weapons_hematology', 2, 3,
                                 True),
        'air_float': MagicWeapon('air float', {}, 0,
                                  'items_weapons_air_float', 0,
                                  1, projectiles.Projectiles.AirFloat, 3, True,
                                  'Float'),
        'blood_wand': MagicWeapon('blood wand', {dmg.DamageTypes.MAGICAL: 80}, 0.1,
                                  'items_weapons_blood_wand', 4,
                                  8, projectiles.Projectiles.BloodWand, 13, True,
                                  'Blood Condense'),
        'fireball_magic': MagicWeapon('fireball magic', {dmg.DamageTypes.MAGICAL: 70}, 0.1,
                                       'items_weapons_fireball_magic', 6,
                                       4, projectiles.Projectiles.FireBall, 11, True,
                                       'Fireball'),
        'sunfire': MagicWeapon('sunfire', {dmg.DamageTypes.MAGICAL: 110}, 0.1,
                                'items_weapons_sunfire', 12,
                                10, projectiles.Projectiles.Sunfire, 28, True,
                                'Sunfire'),
        'obsidian_wand': MagicWeapon('obsidian wand', {dmg.DamageTypes.MAGICAL: 70}, 0.1,
                                     'items_weapons_obsidian_wand', 1,
                                     8, projectiles.Projectiles.ObsidianWand, 15, True,
                                     'Obsidian Blast'),
        'ice_shard': MagicWeapon('ice shard', {dmg.DamageTypes.MAGICAL: 40}, 0.1,
                                  'items_weapons_ice_shard', 3,
                                  15, projectiles.Projectiles.IceShard, 24, True,
                                  'Ice Blast'),
        'nameless_fire': MagicWeapon('nameless fire', {dmg.DamageTypes.MAGICAL: 20}, 0.1,
                                     'items_weapons_nameless_fire', 3,
                                     5, projectiles.Projectiles.NamelessFire, 12, True,
                                     'Noname Fire'),
        'fire_magic_sword': SweepMagicWeapon('fire magic sword', {dmg.DamageTypes.MAGICAL: 76}, 0.1,
                                              'items_weapons_fire_magic_sword', 1,
                                              4, 30, 60, False, 5, True,
                                             spell_name='Fire Sword'),
        'fruit_wand': MagicWeapon('fruit wand', {dmg.DamageTypes.MAGICAL: 66}, 0.1,
                                   'items_weapons_fruit_wand', 1,
                                   1, projectiles.Projectiles.FallingApple, 4, True,
                                   'Newton\'s Apple'),
        'rock_wand': MagicWeapon('rock wand', {dmg.DamageTypes.MAGICAL: 88}, 0.6,
                                 'items_weapons_rock_wand', 0,
                                 4, projectiles.Projectiles.RockWand, 7, True,
                                 'Rock Storm'),
        'isobar': MagicWeapon('isobar', {dmg.DamageTypes.MAGICAL: 80}, 0.1,
                               'items_weapons_isobar', 18,
                            12, projectiles.Projectiles.Isobar, 25, True,
                               'Pressure'),
        'tropical_cyclone': MagicWeapon('tropical cyclone', {dmg.DamageTypes.MAGICAL: 110}, 0.1,
                                         'items_weapons_tropical_cyclone', 18,
                                         18, projectiles.Projectiles.TropicalCyclone, 38, True,
                                         'Tropical Cyclone'),
        'tornado': Tornado('tornado', {}, 0.1, 'items_weapons_tornado',
                           2, 18, projectiles.Projectiles.Projectile, 25, spell_name='Tornado'),
        'dark_spider_lily': MagicWeapon('dark spider lily', {dmg.DamageTypes.MAGICAL: 70}, 3,
                                        'items_weapons_dark_spider_lily', 12,
                                        15, projectiles.Projectiles.DarkSpiderLily, 32, True,
                                        'Sealed Oath'),
        'midnights_wand': MidnightsWand('midnights wand', {dmg.DamageTypes.MAGICAL: 98}, 0.3,
                                        'items_weapons_midnights_wand', 2,
                                        12, projectiles.Projectiles.MidnightsWand, 4, True,
                                        80),
        'spiritual_destroyer': MagicWeapon('spiritual destroyer', {dmg.DamageTypes.MAGICAL: 108}, 0.5,
                                           'items_weapons_spiritual_destroyer', 1,
                                           5, projectiles.Projectiles.SpiritualDestroyer, 6,
                                           True, 'Energy Destroy'),
        'blood_sacrifice': EvilMagicWeapon('blood sacrifice', {dmg.DamageTypes.MAGICAL: 108}, 0.5,
                                            'items_weapons_blood_sacrifice', 3,
                                            12, projectiles.Projectiles.BloodSacrifice, 20, 24, True,
                                            spell_name='Blood Sacrifice'),
        'blade_wand': MagicWeapon('blade wand', {dmg.DamageTypes.MAGICAL: 118}, 0.3,
                                  'items_weapons_blade_wand', 1,
                                  5, projectiles.Projectiles.WindBlade, 12, True,
                                  'Wind Blade'),
        'evil_book': MagicWeapon('evil book', {dmg.DamageTypes.MAGICAL: 128}, 0.8,
                                 'items_weapons_evil_book', 1,
                                 4, projectiles.Projectiles.EvilBook, 15, True,
                                 'Evil Curse'),
        'water_of_disability': MagicWeapon('water of disability', {dmg.DamageTypes.MAGICAL: 88}, 0.5,
                                            'items_weapons_water_of_disability', 4,
                                            1, projectiles.Projectiles.WaterOfDisability, 18, True,
                                            'Water of Disability'),
        'curse_book': MagicWeapon('curse book', {dmg.DamageTypes.MAGICAL: 144}, 0.6,
                                  'items_weapons_curse_book', 20,
                                  10, projectiles.Projectiles.CurseBook, 40, True,
                                  'Dark Magic Circle'),
        'gravity_wand': MagicWeapon('gravity wand', {dmg.DamageTypes.MAGICAL: 100}, 0.8,
                                    'items_weapons_gravity_wand', 80,
                                    10, projectiles.Projectiles.GravityWand, 160, True,
                                    'Gravity'),
        'double_watcher_wand': MagicWeapon('double watcher wand', {dmg.DamageTypes.MAGICAL: 70}, 0.8,
                                            'items_weapons_double_watcher_wand', 1,
                                            4, projectiles.Projectiles.BeamPair, 12, True,
                                            'Double Watch'),
        'shield_wand': MagicWeapon('shield wand', {dmg.DamageTypes.MAGICAL: 100}, 0.8,
                                   'items_weapons_shield_wand', 80,
                                   10, projectiles.Projectiles.ShieldWand, 100, True,
                                   'Water Shield'),
        'forbidden_curse__spirit': ArcaneWeapon('forbidden curse  spirit', {dmg.DamageTypes.ARCANE: 7}, 0.8,
                                                'items_weapons_forbidden_curse__spirit', 360,
                                                80, projectiles.Projectiles.ForbiddenCurseSpirit, 300, 7, True,
                                                'Energy Magic Circle'),
        'forbidden_curse__evil': ArcaneWeapon('forbidden curse  evil', {dmg.DamageTypes.ARCANE: 2}, 0.8,
                                              'items_weapons_forbidden_curse__evil', 45,
                                              25, projectiles.Projectiles.ForbiddenCurseEvil, 150, 4.5, True,
                                              'Dark\'s Curse'),
        'forbidden_curse__time': ForbiddenCurseTime('forbidden curse  time', {}, 0.8,
                                                    'items_weapons_forbidden_curse__time', 10,
                                                    50, projectiles.Projectiles.Projectile, 300, 5, True,
                                                    'Time Adjust'),
        'prism': MagicWeapon('prism', {dmg.DamageTypes.MAGICAL: 250}, 0.8,
                             'items_weapons_prism', 20,
                             5, projectiles.Projectiles.Beam, 54, True,
                             'Light Focus(Primarily)'),
        'prism_wand': MagicWeapon('prism wand', {dmg.DamageTypes.MAGICAL: 360}, 0.8,
                                  'items_weapons_prism_wand', 2,
                                  5, projectiles.Projectiles.BeamLight, 24, True,
                                  'Light Focus(Secondarily)'),
        'light_purify': MagicWeapon('light purify', {dmg.DamageTypes.MAGICAL: 320}, 0.8,
                                     'items_weapons_light_purify', 1,
                                     11, projectiles.Projectiles.LightPurify, 50, True,
                                     'Light Purify'),
        'astigmatism': Astigmatism('astigmatism', {dmg.DamageTypes.MAGICAL: 320}, 0.1, 'items_weapons_astigmatism',
                                   0, 1, 5, True,
                                   'Energetic Light Focus'),
        'life_wand': LifeWand('life_wand', 'item_weapons_life_wand', 2, 8, True),

        'lights_bible': MagicSet('lights_bible', 'items_weapons_lights_bible',
                                 lambda w: (inventory.TAGS['magic_element_light'] in inventory.ITEMS[w.name.replace(' ', '_')].tags) and game.get_game().player.inventory.is_enough(inventory.ITEMS[w.name.replace(' ', '_')]),
                                 'Pseudo Sun'),
        'energy_bible': MagicSet('energy_bible', 'items_weapons_energy_bible',
                                 lambda w: (inventory.TAGS['magic_element_energy'] in inventory.ITEMS[w.name.replace(' ', '_')].tags) and game.get_game().player.inventory.is_enough(inventory.ITEMS[w.name.replace(' ', '_')]),
                                 'Energy Pulse', 1),
        'chaos_teleporter': Teleporter('chaos_teleporter', {}, 1, 'items_weapons_chaos_teleporter',
                                       19, 1, 1000, 300, False, 'Chaos Teleport'),
        'chaos_killer': ChaosKiller('chaos_killer', {dmg.DamageTypes.MAGICAL: 3200}, 1, 'items_weapons_chaos_killer',
                                     9, 1, projectiles.Projectiles.Projectile, 40, False, 'Chaos Kill'),
        'skyfire__meteor': MagicWeapon('skyfire__meteor', {dmg.DamageTypes.MAGICAL: 480}, 1, 'items_weapons_skyfire__meteor',
                                       1, 2, projectiles.Projectiles.Meteor, 8, True, 'Skyfire Meteor'),
        'azure_guard': AzureGuard('azure_guard', {}, 1, 'items_weapons_azure_guard',
                                  35, 1, projectiles.Projectiles.Projectile, 300, False, 'Azure Guard'),

        'great_forbidden_curse__fire': ArcaneWeapon('great forbidden curse  fire', {dmg.DamageTypes.ARCANE: 28}, 0.8,
                                               'items_weapons_forbidden_curse__fire', 190,
                                              10, projectiles.Projectiles.Seraph, 600, 24, True,
                                               'The Fire Seraph'),
        'great_forbidden_curse__light': GreatForbiddenCurseLight('great forbidden curse  light', {dmg.DamageTypes.ARCANE: 36}, 0.8,
                                               'items_weapons_forbidden_curse__light', 10,
                                               5, 10, 0.2, True,
                                               'Seven souls\' light'),
        'great_forbidden_curse__water': ArcaneWeapon('great forbidden curse  water', {dmg.DamageTypes.ARCANE: 200}, 0.8,
                                               'items_weapons_forbidden_curse__water', 40,
                                              10, projectiles.Projectiles.AcidRain, 500, 10, True,
                                               'Acid Rain'),
        'storm': MagicWeapon('storm', {dmg.DamageTypes.MAGICAL: 200}, 1, 'items_weapons_storm',
                             9, 1, projectiles.Projectiles.Storm, 120, True, 'Storm', 1),
        'earth_wall': EarthWall('earth_wall', {}, 1, 'items_weapons_earth_wall',
                                12, 1, projectiles.Projectiles.Projectile, 600, False, 'Earth Wall', 1),
        'lifebringer': MagicWeapon('lifebringer', {}, 1, 'items_weapons_lifebringer',
                                   110, 10, projectiles.Projectiles.LifeBringer, 500, True, 'Life Bringer', 1),
        'target_dummy': TargetDummy('target_dummy', {}, 1, 'items_weapons_target_dummy',
                                     0, 10, projectiles.Projectiles.Projectile, 15, True, 'Target Dummy'),
        'judgement_light': MagicWeapon('judgement light', {dmg.DamageTypes.MAGICAL: 450}, 1, 'items_weapons_judgement_light',
                                       220, 10, projectiles.Projectiles.JudgementLight, 800, True, 'Judgement Light', 1),
        'dark_restrict': MagicWeapon('dark restrict', {}, 1, 'items_weapons_dark_restrict',
                                      1, 14, projectiles.Projectiles.DarkRestrict, 200, True, 'Dark Restrict', 1),
        'death_note': ArcaneWeapon('death note', {dmg.DamageTypes.ARCANE: 45}, 1, 'items_weapons_death_note',
                                   10, 10, projectiles.Projectiles.DeathNote, 120, 8, True, 'Death Note'),
        'great_forbidden_curse__dark': ArcaneWeapon('great forbidden curse  dark', {dmg.DamageTypes.ARCANE: 24}, 0.8,
                                               'items_weapons_forbidden_curse__darks_wield', 230,
                                              10, projectiles.Projectiles.ForbiddenCurseDarkWield, 600, 15, True,
                                               'Dark\'s Wield'),
        'great_forbidden_curse__evil': ArcaneWeapon('great forbidden curse  evil', {dmg.DamageTypes.ARCANE: 12}, 0.8,
                                               'items_weapons_forbidden_curse__blood moon', 590,
                                              10, projectiles.Projectiles.ForbiddenCurseBloodMoon, 800, 32, True,
                                               'Blood Moon',),
        'stop': MagicWeapon('stop', {}, 1, 'items_weapons_stop', 240, 1,
                            projectiles.Projectiles.Stop, 800, True, 'Stop', 1),
        'sun_pearl': MagicWeapon('sun pearl', {dmg.DamageTypes.MAGICAL: 660}, 1, 'items_weapons_sun_pearl',
                                  8, 8, projectiles.Projectiles.SunPearl, 88, True, 'Sun Guard', 1),
        'falling_action': MagicWeapon('falling action', {dmg.DamageTypes.MAGICAL: 400, dmg.DamageTypes.THINKING: 400}, 1, 'items_weapons_falling_action',
                                       1, 1, projectiles.Projectiles.FallingAction, 25, True, 'Falling Action', 1),
        'rising_action': MagicWeapon('rising action', {dmg.DamageTypes.MAGICAL: 360, dmg.DamageTypes.THINKING: 800}, 1, 'items_weapons_rising_action',
                                       1, 8, projectiles.Projectiles.RisingAction, 188, True, 'Rising Action', 1),
        'relevation_of_cycles': MagicWeapon('relevation of cycles', {dmg.DamageTypes.MAGICAL: 60, dmg.DamageTypes.THINKING: 500}, 1, 'items_weapons_relevation_of_cycles',
                                             1, 2, projectiles.Projectiles.RelevationOfCycles, 64, True, 'Relevation of Cycles', 1),

        'primal__winds_wand': MagicSet('primal  winds wand', 'items_weapons_primal__winds_wand',
                                       lambda w: w.name in [' circulates domain', ' wd circulate clockwise',
                                                            ' wd circulate anticlockwise', ' wd circulate attract',
                                                            ' wd circulate repel', ' wd strong wind', ' wd extinct'], 'Circulate\'s Domain',
                                          -1, ),

        '_circulates_domain': Domain(' circulates domain', {}, 1, 'items_weapons__circulates_domain',
                                     1, 19, 4, 0.02, (150, 250, 230),
                                     1200, True, 'Circulate\'s Domain'),
        '_wd_circulate_clockwise': WdCirculateClockwise(' wd circulate clockwise', {}, 1,
                                                        'items_weapons__wd_circulate_clockwise',
                                          0, 1, projectiles.Projectiles.Projectile, '_circulates_domain',
                                                        True, 'Circulate\'s Domain: Clockwise'),
        '_wd_circulate_anticlockwise': WdCirculateAntiClockwise(' wd circulate anticlockwise', {}, 1,
                                                              'items_weapons__wd_circulate_anticlockwise',
                                          0, 1, projectiles.Projectiles.Projectile, '_circulates_domain',
                                                              True, 'Circulate\'s Domain: Anticlockwise'),
        '_wd_circulate_attract': WdCirculateAttract(' wd circulate attract', {}, 1,
                                                    'items_weapons__wd_circulate_attract',
                                          0, 1, projectiles.Projectiles.Projectile, '_circulates_domain',
                                                    True, 'Circulate\'s Domain: Attract'),
        '_wd_circulate_repel': WdCirculateRepel(' wd circulate repel', {}, 1,
                                                 'items_weapons__wd_circulate_repel',
                                          0, 1, projectiles.Projectiles.Projectile, '_circulates_domain',
                                                 True, 'Circulate\'s Domain: Repel'),
        '_wd_strong_wind': WdStrongWind(' wd strong wind', {dmg.DamageTypes.ARCANE: 3}, 1, 'items_weapons__wd_strong_wind', 0, 1,
                                        projectiles.Projectiles.Projectile, '_circulates_domain', True,
                                        'Circulate\'s Domain: Strong Wind'),
        '_wd_extinct': WdExtinct(' wd extinct', {dmg.DamageTypes.ARCANE: 2}, 1, 'items_weapons__wd_extinct', 0, 1,
                                 projectiles.Projectiles.Projectile, '_circulates_domain', True,
                                 'Circulate\'s Domain: Extinct'),

        'primal__life_wand': MagicSet('primal  life wand', 'items_weapons_primal__life_wand',
                                      lambda w: w.name in [' life domain', ' ld summon tree', ' ld summon cactus',
                                                           ' ld summon coniferous tree', ' ld summon huge tree',
                                                           ' ld summon tree monster', ' ld summon bloodflower',
                                                           ' ld summon soulflower', ' ld heal'],
                                      'Life\'s Domain', style=-1),
        '_life_domain': Domain(' life domain', {}, 1, 'items_weapons__life_domain',
                               1, 19, 4, 0.02, (200, 255, 200),
                               1200, True, 'Life\'s Domain'),
        '_ld_summon_tree': LdSpawn(' ld summon tree', {}, 1, 'items_weapons__ld_summon_tree', 0, 2,
                                    entity.Entities.Tree, '_life_domain', True, 'Life\'s Domain: Tree',
                                   entity.Entities.Tree),
        '_ld_summon_cactus': LdSpawn(' ld summon cactus', {}, 1, 'items_weapons__ld_summon', 0, 2,
                                     entity.Entities.Cactus, '_life_domain', True, 'Life\'s Domain: Cactus',
                                      entity.Entities.Cactus),
        '_ld_summon_coniferous_tree': LdSpawn(' ld summon coniferous tree', {}, 1, 'items_weapons__ld_summon', 0, 2,
                                              entity.Entities.ConiferousTree, '_life_domain', True, 'Life\'s Domain: Coniferous Tree',
                                               entity.Entities.ConiferousTree),
        '_ld_summon_huge_tree': LdSpawn(' ld summon huge tree', {}, 1, 'items_weapons__ld_summon', 0, 2,
                                        entity.Entities.HugeTree, '_life_domain', True, 'Life\'s Domain: Huge Tree',
                                         entity.Entities.HugeTree),
        '_ld_summon_tree_monster': LdSpawn(' ld summon tree monster', {}, 1, 'items_weapons__ld_summon', 0, 2,
                                           entity.Entities.TreeMonster, '_life_domain', True, 'Life\'s Domain: Tree Monster',
                                            entity.Entities.TreeMonster),
        '_ld_summon_bloodflower': LdSpawn(' ld summon bloodflower', {}, 1, 'items_weapons__ld_summon', 0, 2,
                                          entity.Entities.Bloodflower, '_life_domain', True, 'Life\'s Domain: Bloodflower',
                                           entity.Entities.Bloodflower),
        '_ld_summon_soulflower': LdSpawn(' ld summon soulflower', {}, 1, 'items_weapons__ld_summon', 0, 2,
                                          entity.Entities.SoulFlower, '_life_domain', True, 'Life\'s Domain: Soulflower',
                                           entity.Entities.SoulFlower),
        '_ld_heal': LdHeal(' ld heal', {}, 1, 'items_weapons__ld_heal', 0, 1,
                            projectiles.Projectiles.Projectile, '_life_domain', True, 'Life\'s Domain: Heal'),

        'gold_fine': PoetWeapon('gold fine', {dmg.DamageTypes.OCTAVE: 388}, 1, 'items_weapons_gold_fine',
                                0, 5, projectiles.Projectiles.GoldFine, [effects.OctLuckyI, effects.OctSpeedII, effects.OctLimitlessI],
                                10, 140, auto_fire=True, instrument='trumpet'),
        'ancient_flute': PoetWeapon('ancient flute', {dmg.DamageTypes.OCTAVE: 108}, 1, 'items_weapons_ancient_flute',
                                   0, 3, projectiles.Projectiles.AncientFlute, [effects.OctLuckyII, effects.OctLimitlessII, effects.OctStrengthII,
                                                                                effects.OctStrengthI],
                                   4, 90, auto_fire=True, instrument='flute'),
        'storm_harp': PoetWeapon('storm harp', {dmg.DamageTypes.OCTAVE: 78}, 1, 'items_weapons_storm_harp',
                                 0, 4, projectiles.Projectiles.StormHarp, [effects.OctSpeedI, effects.OctWisdomI,
                                                                         effects.OctLimitlessI, effects.OctToughnessII],
                                 2, 80, auto_fire=True, song='true_hero', back_rate=0.65, heavy=True),
        'snare': PoetWeapon('snare', {dmg.DamageTypes.OCTAVE: 256}, 1, 'items_weapons_snare',
                           0, 5, projectiles.Projectiles.Snare, [effects.OctLimitlessII, effects.OctSpeedI, effects.OctStrengthIII],
                           8, 240, auto_fire=True, instrument='snare', back_rate=0.8, heavy=True, song='beat'),
        'watcher_bell': PoetWeapon('watcher bell', {dmg.DamageTypes.OCTAVE: 72}, 1, 'items_weapons_watcher_bell',
                                   0, 4, projectiles.Projectiles.WatcherBell, [effects.OctLuckyIII, effects.OctSpeedIII, effects.OctToughnessI],
                                   3, 60, auto_fire=True, instrument='bell', back_rate=0.7, heavy=True, song='legend'),
        'apple_smells_good': PoetWeapon('apple smells good', {dmg.DamageTypes.OCTAVE: 188}, 1, 'items_weapons_apple_smells_good',
                                        0, 4, projectiles.Projectiles.AppleSmellsGood, [effects.OctStrengthI, effects.OctLuckyIII,
                                                                                     effects.OctLimitlessIII, effects.OctStrengthIII, effects.OctLuckyII],
                                        3, 100, auto_fire=True, instrument='flute', back_rate=0.55, song='apple_smells_good'),
        'holy_stormer': PoetWeapon('holy stormer', {dmg.DamageTypes.OCTAVE: 256}, 1, 'items_weapons_holy_stormer',
                                   0, 1, projectiles.Projectiles.HolyStormer, [effects.OctLuckyI, effects.OctLuckyII, effects.OctSpeedI,
                                                                             effects.OctSpeedII, effects.OctSpeedIII, effects.OctStrengthI, effects.OctStrengthII,
                                                                                effects.OctStrengthIII],
                                   1, 40, auto_fire=True, back_rate=0.3, song='beat'),
        'wither_oboe': PoetWeapon('wither oboe', {dmg.DamageTypes.OCTAVE: 325}, 1, 'items_weapons_wither_oboe',
                                  0, 6, projectiles.Projectiles.WitherOboe, [effects.OctStrengthI, effects.OctLuckyII,
                                                                             effects.OctLimitlessII],
                                  7, 250, auto_fire=True, back_rate=0.06, song='quiet', instrument='oboe'),

        'dragon_flute': PoetWeapon('dragon flute', {dmg.DamageTypes.OCTAVE: 488}, 1, 'items_weapons_dragon_flute',
                                   0, 5, projectiles.Projectiles.DragonFlute, [effects.OctLuckyI, effects.OctLuckyII, effects.OctSpeedI,
                                                                             effects.OctStrengthI, effects.OctStrengthII, effects.OctStrengthIII, effects.OctLimitlessII],
                                   12, 180, auto_fire=True, instrument='flute', back_rate=0.5, song='beat'),
        'the_song_of_ice_and_fire': PoetWeapon('the song of ice and fire', {dmg.DamageTypes.OCTAVE: 488}, 1, 'items_weapons_the_song_of_ice_and_fire',
                                                0, 8, projectiles.Projectiles.TheSongOfIceAndFire, [effects.OctLimitlessIII, effects.OctStrengthIII],
                                                32, 240, auto_fire=True, back_rate=0.5, song='beat'),
        'dance_of_fire': PoetWeapon('dance of fire', {dmg.DamageTypes.OCTAVE: 488}, 1, 'items_weapons_dance_of_fire',
                                    0, 2, projectiles.Projectiles.DanceOfFire, [effects.OctStrengthI, effects.OctStrengthII, effects.OctStrengthIII,
                                                                                effects.OctStrengthIV],
                                    25, 200, auto_fire=True, back_rate=0.8, song='spear_of_justice', instrument='flute'),
        'dance_of_frost': PoetWeapon('dance of frost', {dmg.DamageTypes.OCTAVE: 488}, 1, 'items_weapons_dance_of_frost',
                                     0, 2, projectiles.Projectiles.DanceOfFrost, [effects.OctLimitlessI, effects.OctLimitlessII, effects.OctLimitlessIII,],
                                     25, 200, auto_fire=True, back_rate=0.8, song='spear_of_justice', instrument='flute'),
        'dance_of_shadow': PoetWeapon('dance of shadow', {dmg.DamageTypes.OCTAVE: 488}, 1, 'items_weapons_dance_of_shadow',
                                      0, 2, projectiles.Projectiles.DanceOfShadow, [effects.OctToughnessI, effects.OctToughnessII, effects.OctToughnessIII,
                                                                                    effects.OctToughnessIV, effects.OctToughnessV],
                                      25, 200, auto_fire=True, back_rate=0.8, song='spear_of_justice', instrument='flute'),
        'dance_of_shine': PoetWeapon('dance of shine', {dmg.DamageTypes.OCTAVE: 488}, 1, 'items_weapons_dance_of_shine',
                                     0, 2, projectiles.Projectiles.DanceOfShine, [effects.OctLuckyI, effects.OctLuckyII, effects.OctLuckyIII,],
                                     25, 200, auto_fire=True, back_rate=0.8, song='spear_of_justice', instrument='flute'),
        'the_godfall_poem': PoetWeapon('the godfall poem', {dmg.DamageTypes.OCTAVE: 888}, 1, 'items_weapons_the_godfall_poem',
                                       0, 1, projectiles.Projectiles.TheGodfallPoem, [effects.OctStrengthIV,  effects.OctLuckyIII,  effects.OctSpeedV, effects.OctToughnessIV,
                                                                                       effects.OctLimitlessIII, effects.OctWisdomIII], 30,
                                       3200, auto_fire=True, back_rate=0.9, song='his_theme', instrument='flute'),

        'saint_healer': PriestHealer('saint healer', 50, 1, 'items_weapons_saint_healer',
                                    9, 1, 15, 80,
                                    True, 'Saint Healer'),
        'holy_shine': PriestWeapon('holy shine', {dmg.DamageTypes.HALLOW: 128}, 1, 'items_weapons_holy_shine',
                                    3, 1, projectiles.Projectiles.HolyShine, 7, 8,
                                    True, 'Holy Shine'),
        'the_gods_penalty': PriestWeapon('the gods penalty', {dmg.DamageTypes.HALLOW: 68}, 1,
                                         'items_weapons_the_gods_penalty', 29, 1,
                                         projectiles.Projectiles.TheGodsPenalty, 60, 12,
                                         True, 'The God\'s Penalty'),
        'great_heal': PriestHealer('great heal', 60, 1, 'items_weapons_great_heal',
                                   0, 1, 10, 70,
                                   True, 'Great Healer'),
        'the_prayer': PriestHealer('the prayer', 400, 1, 'items_weapons_the_prayer',
                                   11, 1, 60, 500,
                                   True, 'The Prayer'),
        'the_true_gods_penalty': PriestWeapon('the true gods penalty', {dmg.DamageTypes.HALLOW: 88}, 1,
                                              'items_weapons_the_true_gods_penalty', 49, 1,
                                              projectiles.Projectiles.TheTrueGodsPenalty, 80, 25,
                                              True, 'The True God\'s Penalty'),
        'holy_light': PriestWeapon('holy light', {dmg.DamageTypes.HALLOW: 128}, 1,
                                   'items_weapons_holy_light', 9, 1,
                                   projectiles.Projectiles.HolyLight, 25, 3,
                                   True, 'Holy Light'),

        'mystery_watch': PacifistWeapon('mystery watch', {dmg.DamageTypes.PACIFY: 188}, 1,
                                       'items_weapons_mystery_watch', 8, 3,
                                        40, 200, True),
        'hand_of_pacify': PacifistWeapon('hand of pacify', {dmg.DamageTypes.PACIFY: 255}, 1,
                                        'items_weapons_hand_of_pacify', 15, 5,
                                        60, 600, True, col=(255, 255, 100)),
        'sleep_splint': PacifistWeapon('sleep splint', {dmg.DamageTypes.PACIFY: 180}, 1,
                                       'items_weapons_sleep_splint', 4, 3,
                                       20, 400, True, (100, 100, 255)),
        'sleep_eye': PacifistWeapon('sleep eye', {dmg.DamageTypes.PACIFY: 180}, 1,
                                       'items_weapons_sleep_eye', 2, 3,
                                       10, 1600, True, (100, 100, 255)),
        'good_dream': PacifistWeapon('good dream', {dmg.DamageTypes.PACIFY: 440}, 1,
                                     'items_weapons_good_dream', 5, 5,
                                     90, 1200, True, (50, 255, 255)),
        'nightmare': PacifistWeapon('nightmare', {dmg.DamageTypes.PACIFY: 640}, 1,
                                    'items_weapons_nightmare', 8, 12,
                                    50, 800, True, (50, 0, 0)),


        'wooden_pickaxe': Pickaxe('wooden pickaxe', {dmg.DamageTypes.MINE_POWER: 1}, 0.1,
                                    'items_weapons_wooden_pickaxe', 5, 10, 36, 200),
        'copper_pickaxe': Pickaxe('copper pickaxe', {dmg.DamageTypes.MINE_POWER: 3}, 0.1,
                                   'items_weapons_copper_pickaxe', 5, 10, 36, 200),
        'heavy_pickaxe': Pickaxe('heavy pickaxe', {dmg.DamageTypes.MINE_POWER: 6}, 0.1,
                                 'items_weapons_heavy_pickaxe', 5, 10, 36, 200),
        'platinum_pickaxe': Pickaxe('platinum pickaxe', {dmg.DamageTypes.MINE_POWER: 12}, 0.1,
                                    'items_weapons_platinum_pickaxe', 5, 10, 36, 200),
        'bloody_pickaxe': Pickaxe('bloody pickaxe', {dmg.DamageTypes.MINE_POWER: 22}, 0.1,
                                  'items_weapons_bloody_pickaxe', 5, 10, 36, 200),
        'firite_pickaxe': Pickaxe('firite pickaxe', {dmg.DamageTypes.MINE_POWER: 36}, 0.1,
                                  'items_weapons_firite_pickaxe', 5, 10, 36, 200),
        'mystery_pickaxe': Pickaxe('mystery pickaxe', {dmg.DamageTypes.MINE_POWER: 48}, 0.1,
                                   'items_weapons_mystery_pickaxe', 5, 10, 36, 200),
        'spiritual_pickaxe': Pickaxe('spiritual pickaxe', {dmg.DamageTypes.MINE_POWER: 66}, 0.1,
                                     'items_weapons_spiritual_pickaxe', 5, 10, 36, 200),
        'evil_pickaxe': Pickaxe('evil pickaxe', {dmg.DamageTypes.MINE_POWER: 88}, 0.1,
                                'items_weapons_evil_pickaxe', 5, 10, 36, 200),
        'tough_pickaxe': Pickaxe('tough pickaxe', {dmg.DamageTypes.MINE_POWER: 114}, 0.1,
                                 'items_weapons_tough_pickaxe', 5, 10, 36, 200),
        'true_pickaxe': Pickaxe('true pickaxe', {dmg.DamageTypes.MINE_POWER: 144}, 0.1,
                                'items_weapons_true_pickaxe', 5, 10, 36, 200),
        'light_pickaxe': Pickaxe('light pickaxe', {dmg.DamageTypes.MINE_POWER: 256}, 0.1,
                                 'items_weapons_light_pickaxe', 5, 10, 36, 200),
        'destruct_thoughts': Pickaxe('destruct thoughts', {dmg.DamageTypes.THINKING: 5999,
                                                           dmg.DamageTypes.MINE_POWER: 999}, 0.1,
                                     'items_weapons_destruct_thoughts', 5, 10, 36, 200),

        'ballet_shoes': MagicWeapon('ballet shoes', {dmg.DamageTypes.MAGICAL: 120}, 0.1,
                                    'items_weapons_ballet_shoes', 1,
                                    8, projectiles.Projectiles.BalletShoes, 20, True,
                                    'Water Bomb'),
        'tough_gloves': Bow('tough gloves', {dmg.DamageTypes.PIERCING: 180}, 0.1, 'items_weapons_tough_glove',
                            3, 12, 5000, auto_fire=True),
        'burnt_pan': ComplexWeapon('burnt pan', {dmg.DamageTypes.PHYSICAL: 150}, {dmg.DamageTypes.PHYSICAL: 6000}, 3,
                                   'items_weapons_burnt_pan', 2, 12, 6, 20, 120, 80, 300,
                                   True, [0, 0, 1]),
        'toy_knife': ToyKnife('toy knife', {dmg.DamageTypes.MAGICAL: 160}, 0.1,
                              'items_weapons_toy_knife', 0, 1, projectiles.Projectiles.Projectile,
                              3, True, 'Water Gather'),
        'worn_notebook': Blade('worn notebook', {dmg.DamageTypes.PHYSICAL: 190}, 0.1,
                               'items_weapons_worn_notebook', 1, 3, 60, 120),
        'empty_gun': Gun('empty gun', {dmg.DamageTypes.PIERCING: 200}, 0.1,
                         'items_weapons_empty_gun', 1, 4, 800, auto_fire=True,
                         ammo_save_chance=1.0),

        'dragon_swift_sword': Blade('dragon swift sword', {dmg.DamageTypes.PHYSICAL: 1280}, 0.1,
                                     'items_weapons_dragon_swift_sword', 1, 6, 70, 240),
        'dragon_bow': Bow('dragon bow', {dmg.DamageTypes.PIERCING: 800}, 0.1, 'items_weapons_dragon_bow',
                          0, 1, 1200, auto_fire=True, ammo_save_chance=0.6, precision=4),

        'fire_quench__dragon_sword': FireQuenchSword('fire quench  dragon sword', {dmg.DamageTypes.PHYSICAL: 1280}, 0.1,
                                                      'items_weapons_fire_quench__dragon_sword', 1, 6, 70, 240),
        'ice_quench__dragon_sword': IceQuenchSword('ice quench  dragon sword', {dmg.DamageTypes.PHYSICAL: 1280}, 0.1,
                                                    'items_weapons_ice_quench__dragon_sword', 1, 6, 70, 240),
        'dark_quench__dragon_sword': DarkQuenchSword('dark quench  dragon sword', {dmg.DamageTypes.PHYSICAL: 1280}, 0.1,
                                                      'items_weapons_dark_quench__dragon_sword', 1, 6, 70, 240),
        'light_quench__dragon_sword': LightQuenchSword('light quench  dragon sword', {dmg.DamageTypes.PHYSICAL: 1280}, 0.1,
                                                       'items_weapons_light_quench__dragon_sword', 1, 6, 70, 240),
        'the_ruling_sword': TheRulingSword('the ruling sword', {dmg.DamageTypes.PHYSICAL: 2500}, 8,
                                             'items_weapons_the_ruling_sword', 1, 9, 30, 150),

        'fire_quench__dragon_bow': FireQuenchBow('fire quench  dragon bow', {dmg.DamageTypes.PIERCING: 800}, 0.1,
                                                'items_weapons_fire_quench__dragon_bow', 0, 1, 200,
                                                 auto_fire=True, ammo_save_chance=0.4, precision=0),
        'ice_quench__dragon_bow': IceQuenchBow('ice quench  dragon bow', {dmg.DamageTypes.PIERCING: 800}, 0.1,
                                               'items_weapons_ice_quench__dragon_bow', 0, 1, 200,
                                               auto_fire=True, ammo_save_chance=0.4, precision=0),
        'dark_quench__dragon_bow': DarkQuenchBow('dark quench  dragon bow', {dmg.DamageTypes.PIERCING: 800}, 0.1,
                                                'items_weapons_dark_quench__dragon_bow', 0, 1, 200,
                                                 auto_fire=True, ammo_save_chance=0.4, precision=0),
        'light_quench__dragon_bow': LightQuenchBow('light quench  dragon bow', {dmg.DamageTypes.PIERCING: 800}, 0.1,
                                                 'items_weapons_light_quench__dragon_bow', 0, 1, 200,
                                                 auto_fire=True, ammo_save_chance=0.4, precision=0),
        'the_fairy_bow': TheFairyBow('the fairy bow', {dmg.DamageTypes.PIERCING: 400}, 8,
                                     'items_weapons_the_fairy_bow', 1, 1, 1200, auto_fire=True,
                                     ammo_save_chance=0.1, precision=8),


        'fire_dragon_breath_wand': MagicWeapon('fire dragon breath wand', {dmg.DamageTypes.MAGICAL: 600}, 0.1,
                                               'items_weapons_fire_dragon_breath_wand', 0, 1,
                                               projectiles.Projectiles.FireDragonBreath, 18, True,
                                               'Fire Dragon\'s Breath', 1),
        'ice_dragon_breath_wand': MagicWeapon('ice dragon breath wand', {dmg.DamageTypes.MAGICAL: 600}, 0.1,
                                               'items_weapons_ice_dragon_breath_wand', 0, 1,
                                               projectiles.Projectiles.IceDragonBreath, 18, True,
                                               'Ice Dragon\'s Breath', 1),
        'dark_dragon_breath_wand': ArcaneWeapon('dark dragon breath wand', {dmg.DamageTypes.MAGICAL: 600}, 0.1,
                                                 'items_weapons_dark_dragon_breath_wand', 0, 1,
                                                 projectiles.Projectiles.DarkDragonBreath, 24, .15,  True,
                                                 'Dark Dragon\'s Breath'),
        'light_dragon_breath_wand': ArcaneWeapon('light dragon breath wand', {dmg.DamageTypes.MAGICAL: 600}, 0.1,
                                                  'items_weapons_light_dragon_breath_wand', 0, 1,
                                                  projectiles.Projectiles.LightDragonBreath, 24, .15,  True,
                                                  'Light Dragon\'s Breath'),
        'the_magisters_wand': ArcaneWeapon('the magisters wand', {dmg.DamageTypes.MAGICAL: 800}, 8,
                                            'items_weapons_the_magisters_wand', 2, 5,
                                            projectiles.Projectiles.MagistersWand, 45, .5,  True,
                                            'The Magister\'s Magic'),


        'murders_knife': MurderersKnife('murders knife', {}, 0, 'items_weapons_murders_knife',
                              0, 12, 30, 180, auto_fire=True),
        'savior': Savior('savior', {}, 0, 'items_weapons_savior', 80, 5,
                         projectiles.Projectiles.Projectile, 600, 20, True, 'Shield of Recovery'),
    }
    print(len(WEAPONS), len(weapons))
    for k, v in weapons.items():
        WEAPONS[k] = v

set_weapons()
