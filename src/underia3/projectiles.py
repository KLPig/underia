from underia import projectiles, game, weapons
from values import damages, effects
from physics import vector
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

