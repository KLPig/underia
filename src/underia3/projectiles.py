from underia import projectiles

class EWoodenWand(projectiles.Projectiles.PlatinumWand):
    COL = (200, 255, 100)
    DAMAGE_AS = 'e_wooden_wand'
    IMG = 'projectiles_u3_wooden_wand'


class EWoodenArrow(projectiles.Projectiles.Arrow):
    DAMAGES = 10
    SPEED = 300
    IMG = 'u3_wooden_arrow'

AMMO = {
    'e_wooden_arrow': EWoodenArrow,
}

for k, v in AMMO.items():
    projectiles.AMMOS[k] = v

