from underia import weapons, game
from underia import projectiles as proj
from values import damages, effects
from resources import position
from physics import vector
from underia3 import projectiles
import constants
import random
import pygame as pg
import copy

class PurpleClayBroadBlade(weapons.Blade):
    def on_attack(self):
        super().on_attack()
        self.cutting_effect(8)

class FeatherSword(weapons.Blade):
    def on_start_attack(self):
        super().on_start_attack()
        mx, my = position.relative_position(position.real_position(game.get_game().displayer.reflect(*pg.mouse.get_pos())))
        game.get_game().projectiles.append(projectiles.FeatherSword(game.get_game().player.obj.pos, vector.cartesian_to_polar(mx, my)[0]))

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

    'e_wooden_bow': weapons.Bow(name='e wooden bow', damages={damages.DamageTypes.PIERCING: 45}, kb=4,
                                img='items_weapons_e_wooden_bow', speed=2, at_time=5, projectile_speed=300,
                                auto_fire=True, precision=2),
    'lychee_bow': LycheeBow(name='lychee bow', damages={damages.DamageTypes.PIERCING: 60}, kb=3,
                             img='items_weapons_lychee_bow', speed=3, at_time=6, projectile_speed=500,
                             auto_fire=True, precision=1, tail_col=(255, 100, 200)),
    'e_pistol': weapons.Gun(name='e pistol', damages={damages.DamageTypes.PIERCING: 150}, kb=10,
                             img='items_weapons_e_pistol', speed=9, at_time=9, projectile_speed=1200,
                             auto_fire=True, precision=0),
    'heaven_shotgun': weapons.Shotgun('shotgun', {damages.DamageTypes.PIERCING: 120}, 0.1, 'items_weapons_shotgun',
                            3, 8, 1000, auto_fire=True, precision=12),
    'purple_clay_kuangkuang': weapons.KuangKuangKuang(name='purple clay kuangkuang', damages={damages.DamageTypes.PIERCING: 18}, kb=1,
                                               img='items_weapons_purple_clay_kuangkuang', speed=0, at_time=1,
                                              projectile_speed=100, auto_fire=True, precision=2, ammo_save_chance=1 / 3),
    'lychee_twinblade': weapons.ThiefDoubleKnife(name='lychee twinblade', damages={damages.DamageTypes.PIERCING: 150}, kb=8,
                                                 img='items_weapons_lychee_blade', speed=1, at_time=6,
                                                 rot_speed=30, st_pos=120, throw_interval=12, power=3000,
                                                  dcols=((255, 200, 255), (50, 0, 50))),
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
                                               mana_cost=12, maximum_multiplier=3.0, auto_fire=True, spell_name='Holy Condense')
}

for k, v in WEAPONS.items():
    weapons.WEAPONS[k] = v
