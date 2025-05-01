from underia import weapons
from values import damages
from underia3 import projectiles

WEAPONS = {
    'e_wooden_sword': weapons.Blade(name='e wooden sword', damages={damages.DamageTypes.PHYSICAL: 48}, kb=0.5,
                                    img='items_weapons_e_wooden_sword', speed=3, at_time=5, rot_speed=40,
                                    st_pos=150),

    'e_wooden_bow': weapons.Bow(name='e wooden bow', damages={damages.DamageTypes.PIERCING: 45}, kb=1,
                                img='items_weapons_e_wooden_bow', speed=2, at_time=5, projectile_speed=300,
                                auto_fire=True, precision=2),

    'e_wooden_wand': weapons.MagicWeapon(name='e wooden wand', damages={damages.DamageTypes.MAGICAL: 40}, kb=0.5,
                                         img='items_weapons_e_wooden_wand', speed=1, at_time=6,
                                         projectile=projectiles.EWoodenWand, mana_cost=4, auto_fire=True,
                                         spell_name='Life Growth')
}

for k, v in WEAPONS.items():
    weapons.WEAPONS[k] = v
