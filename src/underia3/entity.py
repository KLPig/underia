from underia import entity, game
from physics import vector
from values import damages, effects
import random

class ChickenAI(entity.MonsterAI):
    IDLE_SPEED = 500
    IDLE_TIME = 30
    IDLE_CHANGER = 50

    TOUCHING_DAMAGE = 90
    SIGHT_DISTANCE = 2500

    MASS = 100
    FRICTION = 0.98

    def on_update(self):
        super().on_update()
        if self.cur_target is not None:
            px, py = self.cur_target.pos
            if self.time_touched_player < 120:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px - self.pos[0], py - self.pos[1]),
                                               -250))
            self.apply_force(vector.Vector(vector.coordinate_rotation(px - self.pos[0], py - self.pos[1]),
                                           150))
        else:
            if self.time_touched_player > 120:
                self.idle()

class CentipedeAI(entity.MonsterAI):
    IDLE_SPEED = 1000
    IDLE_TIME = 80
    IDLE_CHANGER = 10

    TOUCHING_DAMAGE = 110
    SIGHT_DISTANCE = 1200

    MASS = 200
    FRICTION = 0.9

    def on_update(self):
        super().on_update()
        if self.cur_target is not None:
            px, py = self.cur_target.pos
            if self.time_touched_player < 200:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px - self.pos[0], py - self.pos[1]) + 90,
                                               300))
            self.apply_force(vector.Vector(vector.coordinate_rotation(px - self.pos[0], py - self.pos[1]),
                                           400))
        else:
            if self.time_touched_player > 120:
                self.idle()

class LycheeAI(CentipedeAI):
    IDLE_SPEED = 0
    MASS = 80
    SIGHT_DISTANCE = 800
    TOUCHING_DAMAGE = 130

class PotAI(entity.MonsterAI):
    IDLE_SPEED = 800
    IDLE_TIME = 80
    IDLE_CHANGER = 10

    TOUCHING_DAMAGE = 160
    SIGHT_DISTANCE = 1600

    MASS = 100
    FRICTION = 0.95

    def on_update(self):
        super().on_update()
        if self.cur_target is not None:
            px, py = self.cur_target.pos
            if self.time_touched_player < 100:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px - self.pos[0], py - self.pos[1]) + 180,
                                               360000 / vector.distance(px - self.pos[0], py - self.pos[1])))
            self.apply_force(vector.Vector(vector.coordinate_rotation(px - self.pos[0], py - self.pos[1]),
                                           600))
        else:
            if self.time_touched_player > 300:
                self.idle()

class PoiseWalkerAI(entity.MonsterAI):
    IDLE_SPEED = 800
    IDLE_TIME = 20
    IDLE_CHANGER = 10
    MASS = 400
    SIGHT_DISTANCE = 3000
    TOUCHING_DAMAGE = 240
    FRICTION = 0.6

    def __init__(self, *args):
        super().__init__(*args)
        self.tick = 0
        self.tx, self.ty = 0, 0

    def on_update(self):
        super().on_update()
        if self.time_touched_player < 200:
            return
        if self.cur_target is not None:
            px, py = self.cur_target.pos
            self.tick += 1
            if random.randint(0, self.tick) > 140:
                self.tick = 0
            ax, ay = vector.rotation_coordinate(random.randint(0, 360))
            if self.tick < 70:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px - self.pos[0], py - self.pos[1]),
                                               1200))
            elif self.tick == 70:
                self.tx = ax * 1000 + px
                self.ty = ay * 1000 + py
            elif self.tick < 80:
                self.pos = ((self.pos[0] * 5 + self.tx) // 6, (self.pos[1] * 5 + self.ty) // 6)
                self.IS_OBJECT = False
            elif self.tick == 80:
                self.IS_OBJECT = True
            else:
                self.apply_force(vector.Vector(vector.coordinate_rotation(px - self.pos[0], py - self.pos[1]),
                                               1800))
        else:
            self.idle()

class BonecaAmbalabuAI(entity.MonsterAI):
    MASS = 250
    FRICTION = 0.9
    IDLE_SPEED = 4000
    IDLE_TIME = 100
    IDLE_CHANGER = 180

    def on_update(self):
        super().on_update()
        if self.cur_target is None:
            self.idle()
            return
        pv = self.cur_target.pos - self.pos
        if self.time_touched_player < 100:
            self.apply_force(vector.Vector2D(0, 0, pv[0] * -1, pv[1] * -.3))
        else:
            self.apply_force(vector.Vector2D(0, 0, pv[0] * 2, pv[1] * .6))

class Entity(entity.Entities.Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Tree(Entity):
    NAME = 'Tree'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_wood', 1, 5, 25),
    ])
    SOUND_DEATH = 'ore'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics[f'entity3_tree{random.randint(1, 3)}'],
                         entity.BuildingAI, hp=12)

class DeadTree(Entity):
    NAME = 'Dead Tree'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_wood', 1, 15, 30),
    ])
    SOUND_DEATH = 'ore'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics[f'entity3_dead_tree{random.randint(1, 2)}'],
                         entity.BuildingAI, hp=16)

class Chicken(Entity):
    NAME = 'Chicken'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_feather', 1, 5, 25)
    ])
    SOUND_HURT = 'dragon'
    SOUND_DEATH = 'dragon'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics[f'entity3_chicken'],
                         ChickenAI, hp=540)

    def on_update(self):
        super().on_update()
        self.set_rotation(-self.obj.velocity.get_net_rotation())

class PoisonChicken(Chicken):
    NAME = 'Poison Chicken'
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_poison_powder', 1, 10, 20),
        entity.SelectionLoot([('e_feather', 3, 8), ('carrion', 1, 4)], 0, 1)
    ])

    def __init__(self, pos):
        super(Chicken, self).__init__(pos, game.get_game().graphics[f'entity3_poison_chicken'],
                                       ChickenAI, hp=1000)
        self.obj.MASS *= 2
        self.tick = 0

    def on_update(self):
        self.tick += 1
        super().on_update()
        px, py = self.obj.cur_target.pos
        if vector.distance(px - self.obj.pos[0], py - self.obj.pos[1]) < 500:
            game.get_game().player.hp_sys.effect(effects.CurseSnow(2, 1))
            if self.tick % 5 == 0:
                game.get_game().player.hp_sys.effect(effects.Poison(5, 1))

class BonecaAmbalabu(entity.Entities.Entity):
    NAME = 'Boneca Ambalabu'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
    ])

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity3_boneca_ambalabu'],
                         BonecaAmbalabuAI, hp=1200)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 40
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 30
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 35
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 35
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 25
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 10

    def on_update(self):
        super().on_update()
        px, py = self.obj.cur_target.pos - self.obj.pos
        self.set_rotation(-vector.cartesian_to_polar(px, py)[0])

class PoisonCentipede(entity.Entities.WormEntity):
    NAME = 'Poison Centipede'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_poison_powder', 1, 10, 20),
    ])
    SOUND_HURT = 'crystal'
    SOUND_DEATH = 'monster'

    def __init__(self, pos):
        super().__init__(pos, random.randint(9, 16), game.get_game().graphics[f'entity3_poison_centipede_head'],
                         game.get_game().graphics[f'entity3_poison_centipede_body'], CentipedeAI, hp=2000,
                         body_length=100, body_touching_damage=100)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 20
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 10
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 25
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 25
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 15
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 20

class Lychee(entity.Entities.Entity):
    NAME = 'Lychee'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('lychee_shard', 0.3, 1, 4),
        ])
    SOUND_HURT = 'crystal'
    SOUND_DEATH = 'dragon'
    
    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity3_lychee'], LycheeAI, hp=400)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 30
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 20
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 35
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 35
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 25
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 30

class PurpleClayPot(entity.Entities.Entity):
    NAME = 'Purple Clay Pot'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('purple_clay', .7, 2, 3),
        ])
    SOUND_HURT = 'crystal'
    SOUND_DEATH = 'ore'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity3_purple_clay_pot'], PotAI, hp=300)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 40
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 45
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 45
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 45
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 40
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 45


class PoiseWalker(entity.Entities.Entity):
    NAME = 'Poise Walker'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_poison_powder', 1, 5, 25),
        entity.SelectionLoot([('poise_blade', 1, 1)], 1, 1),
    ])
    IS_MENACE = True
    BOSS_NAME = ''

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity3_poise_walker'], PoiseWalkerAI, hp=1200)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 250
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 250
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 250
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 250
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 250
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 250
        self.tick = 0

    def on_update(self):
        super().on_update()
        self.set_rotation(-self.obj.velocity.get_net_rotation())
        px, py = self.obj.cur_target.pos
        if vector.distance(px - self.obj.pos[0], py - self.obj.pos[1]) < 500:
            game.get_game().player.hp_sys.effect(effects.CurseSnow(2, 1))
            if self.tick % 5 == 0:
                game.get_game().player.hp_sys.effect(effects.Poison(5, 2))
                game.get_game().player.hp_sys.effect(effects.Freezing(20, 1))
        self.tick += 1
