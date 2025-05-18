from underia import weapons, game, KuangKuangKuang
from underia import projectiles as proj
from values import damages, effects
from resources import position
from physics import vector
from underia3 import projectiles
import constants
import random
import pygame as pg

class PurpleClayBroadBlade(weapons.Blade):
    def on_attack(self):
        super().on_attack()
        self.cutting_effect(8)

class PoiseBlade(weapons.Blade):
    def on_attack(self):
        super().on_attack()
        self.cutting_effect(4, (200, 100, 255), (100, 50, 150))
        for e in game.get_game().entities:
            if vector.distance(e.obj.pos[0] - self.x - game.get_game().player.obj.pos[0],
                               e.obj.pos[1] - self.y - game.get_game().player.obj.pos[1]) < 800:
                e.hp_sys.effect(effects.Poison(20, 5))

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

WEAPONS = {
    'e_wooden_sword': weapons.Blade(name='e wooden sword', damages={damages.DamageTypes.PHYSICAL: 48}, kb=6,
                                    img='items_weapons_e_wooden_sword', speed=3, at_time=5, rot_speed=40,
                                    st_pos=150),
    'lychee_sword': weapons.Blade(name='lychee sword', damages={damages.DamageTypes.PHYSICAL: 88}, kb=10,
                                   img='items_weapons_lychee_sword', speed=1, at_time=6, rot_speed=60, st_pos=200),
    'lychee_pike': weapons.Spear(name='lychee pike', damages={damages.DamageTypes.PHYSICAL: 110}, kb=12,
                                 img='items_weapons_lychee_pike', speed=3, at_time=8, forward_speed=30, st_pos=150,
                                 auto_fire=True),
    'purple_clay_broad_blade': PurpleClayBroadBlade(name='purple clay broad blade', damages={damages.DamageTypes.PHYSICAL: 110}, kb=15,
                                                    img='items_weapons_purple_clay_broad_blade', speed=1, at_time=8,
                                                    rot_speed=40, st_pos=150),
    'poise_blade': PoiseBlade(name='poise blade', damages={damages.DamageTypes.PHYSICAL: 80}, kb=12,
                              img='items_weapons_poise_blade', speed=1, at_time=5, rot_speed=70, st_pos=200),

    'e_wooden_bow': weapons.Bow(name='e wooden bow', damages={damages.DamageTypes.PIERCING: 45}, kb=4,
                                img='items_weapons_e_wooden_bow', speed=2, at_time=5, projectile_speed=300,
                                auto_fire=True, precision=2),
    'lychee_bow': LycheeBow(name='lychee bow', damages={damages.DamageTypes.PIERCING: 60}, kb=3,
                             img='items_weapons_lychee_bow', speed=3, at_time=6, projectile_speed=500,
                             auto_fire=True, precision=1, tail_col=(255, 100, 200)),
    'e_pistol': weapons.Gun(name='e pistol', damages={damages.DamageTypes.PIERCING: 150}, kb=10,
                             img='items_weapons_e_pistol', speed=9, at_time=9, projectile_speed=1200,
                             auto_fire=True, precision=0),
    'purple_clay_kuangkuang': KuangKuangKuang(name='purple clay kuangkuang', damages={damages.DamageTypes.PIERCING: 18}, kb=1,
                                               img='items_weapons_purple_clay_kuangkuang', speed=0, at_time=1,
                                              projectile_speed=100, auto_fire=True, precision=2),

    'e_wooden_wand': weapons.MagicWeapon(name='e wooden wand', damages={damages.DamageTypes.MAGICAL: 40}, kb=2,
                                         img='items_weapons_e_wooden_wand', speed=1, at_time=6,
                                         projectile=projectiles.EWoodenWand, mana_cost=4, auto_fire=True,
                                         spell_name='Life Growth'),
    'lychee_wand': weapons.MagicWeapon(name='lychee wand', damages={damages.DamageTypes.MAGICAL: 42}, kb=0,
                                        img='items_weapons_lychee_wand', speed=1, at_time=9,
                                        projectile=projectiles.LycheeWand, mana_cost=12, auto_fire=True,
                                        spell_name='Lychee Circle')
}

for k, v in WEAPONS.items():
    weapons.WEAPONS[k] = v
