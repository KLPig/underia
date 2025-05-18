from underia import projectiles, game
from values import damages, effects

class EWoodenWand(projectiles.Projectiles.PlatinumWand):
    COL = (200, 255, 100)
    DAMAGE_AS = 'e_wooden_wand'
    IMG = 'projectiles_u3_wooden_wand'

class LycheeWand(projectiles.Projectiles.MagicCircle):
    DAMAGE_AS = 'lychee_wand'
    IMG = 'lychee_wand'
    DURATION = 12
    ALPHA = 50
    ROT_SPEED = 1

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
                    center=entity.obj.pos).collidepoint(x, y) and entity not in cd:
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

