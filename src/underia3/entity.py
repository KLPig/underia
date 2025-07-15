import copy
import math
import numpy
from underia import entity, game
from physics import vector
from values import damages, effects, hp_system
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
                self.pos << ((self.pos[0] * 5 + self.tx) // 6, (self.pos[1] * 5 + self.ty) // 6)
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
    TOUCHING_DAMAGE = 100
    SIGHT_DISTANCE = 4000

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

class LaVacaSaturnoSaturnitaAI(entity.MonsterAI):
    MASS = 2000
    FRICTION = 0.9
    IDLE_CHANGER = 10
    IDLE_TIME = 10
    IDLE_SPEED = 8000
    SIGHT_DISTANCE = 2000
    TOUCHING_DAMAGE = 180

    def on_update(self):
        super().on_update()
        if self.cur_target is None:
            self.idle()
            return
        pv = self.cur_target.pos - self.pos + vector.Vector2D(dy=-600)
        self.apply_force(pv * 8)

class PredictAI(entity.MonsterAI):
    MASS = 2000
    FRICTION = .9
    IDLE_SPEED = 3000
    IDLE_TIME = 10
    IDLE_CHANGER = 180
    SIGHT_DISTANCE = 2000
    TOUCHING_DAMAGE = 200
    PREFER_DISTANCE = 8

    def __init__(self, *args):
        super().__init__(*args)
        self.tick = 0
        self.p_posx = []
        self.p_posy = []

    def on_update(self):
        super().on_update()
        self.tick += 1
        if self.tick % 10 == 0:
            self.p_posx.append(self.pos[0])
            self.p_posy.append(self.pos[1])
            if len(self.p_posx) > 10:
                self.p_posx.pop(0)
                self.p_posy.pop(0)
            px = numpy.polyfit(numpy.array([self.tick + a for a in range(-len(self.p_posx) * 10 + 10, 1, 10)]),
                               numpy.array(self.p_posx), 5)
            py = numpy.polyfit(numpy.array([self.tick + a for a in range(-len(self.p_posx) * 10 + 10, 1, 10)]),
                               numpy.array(self.p_posy), 5)
            self.apply_force((vector.Vector(px[self.tick + 50], py[self.tick + 50]) - self.pos) / 40)



class Entity(entity.Entities.Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Tree(Entity):
    NAME = 'Tree'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_wood', 1, 5, 25),
        entity.IndividualLoot('talent_fruit', .04, 1, 1),
        entity.IndividualLoot('moonflower', .01, 1, 1)
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
        entity.IndividualLoot('talent_fruit', .02, 1, 1),
    ])
    SOUND_DEATH = 'ore'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics[f'entity3_dead_tree{random.randint(1, 2)}'],
                         entity.BuildingAI, hp=16)

class Chicken(Entity):
    NAME = 'Chicken'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_feather', 1, 5, 25),
        entity.IndividualLoot('feather_sword', .08, 1, 1),
    ])
    SOUND_HURT = 'dragon'
    SOUND_DEATH = 'dragon'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics[f'entity3_chicken'],
                         ChickenAI, hp=540)

    def on_update(self):
        super().on_update()
        self.set_rotation(-self.obj.velocity.get_net_rotation())

class ManaChicken(Entity):
    NAME = 'Mana Chicken'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_feather', .5, 5, 25),
        entity.IndividualLoot('magic_feather', 1, 5, 25),
        entity.IndividualLoot('book', .3, 1, 2),
        entity.IndividualLoot('feather_sword', .08, 1, 1),
        entity.IndividualLoot('moonflower', .02, 1, 1)
    ])
    SOUND_HURT = 'dragon'
    SOUND_DEATH = 'dragon'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics[f'entity3_mana_chicken'],
                         ChickenAI, hp=1200)
        self.obj.MASS /= 3
        self.obj.TOUCHING_DAMAGE += 50

    def on_update(self):
        super().on_update()
        self.set_rotation(-self.obj.velocity.get_net_rotation())


class PoisonChicken(Chicken):
    NAME = 'Poison Chicken'
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_poison_powder', 1, 10, 20),
        entity.SelectionLoot([('e_feather', 3, 8), ('carrion', 3, 9)], 1, 2),
        entity.IndividualLoot('feather_sword', .08, 1, 1),
    ])

    def __init__(self, pos):
        super(Chicken, self).__init__(pos, game.get_game().graphics[f'entity3_poison_chicken'],
                                       ChickenAI, hp=1000)
        self.obj.MASS *= 2
        self.tick = 0

    def on_update(self):
        self.tick += 1
        super().on_update()
        if self.obj.cur_target is None:
            self.obj.idle()
            return
        px, py = self.obj.cur_target.pos
        if vector.distance(px - self.obj.pos[0], py - self.obj.pos[1]) < 500:
            game.get_game().player.hp_sys.effect(effects.CurseSnow(2, 1))
            if self.tick % 5 == 0:
                game.get_game().player.hp_sys.effect(effects.Poison(5, 1))

class BonecaAmbalabu(entity.Entities.Entity):
    NAME = 'Boneca Ambalabu'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('brainrot', 1, 10, 12),
        entity.IndividualLoot('mystery_shard', 1, 30, 32),
        entity.IndividualLoot('mystery_glove', .03, 1, 1)
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
        if self.obj.cur_target is None:
            self.obj.idle()
            return
        px, py = self.obj.cur_target.pos - self.obj.pos
        self.set_rotation(-vector.cartesian_to_polar(px, py)[0])

class LaVacaSaturnoSaturnita(entity.Entities.Entity):
    NAME = 'La Vaca Saturno Saturnita'
    IS_MENACE = True
    BOSS_NAME = ''
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('brainrot', 1, 30, 32),
        entity.IndividualLoot('mystery_shard', 1, 30, 32),
        entity.IndividualLoot('mystery_soul', .4, 6, 12),
        entity.IndividualLoot('moonflower', .08, 1, 1),
        entity.IndividualLoot('tuner', 1, 1, 1),
    ])

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity3_la_vaca_saturno_saturnita'],
                         LaVacaSaturnoSaturnitaAI, hp=18000)
        self.hp_sys.DODGE_RATE = 0.1

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
        entity.SelectionLoot([('e_feather', 3, 8), ('carrion', 2, 8)], 1, 2)
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
        if self.obj.cur_target is None:
            self.obj.idle()
            return
        px, py = self.obj.cur_target.pos
        if vector.distance(px - self.obj.pos[0], py - self.obj.pos[1]) < 500:
            game.get_game().player.hp_sys.effect(effects.CurseSnow(2, 1))
            if self.tick % 5 == 0:
                game.get_game().player.hp_sys.effect(effects.Poison(5, 2))
                game.get_game().player.hp_sys.effect(effects.Freezing(20, 1))
        self.tick += 1

class LycheeGuard(Lychee):
    DIVERSITY = False

    def __init__(self, pos):
        super().__init__(pos)
        self.tick = int(int(pos[0] + pos[1]) // 25 % 96)
        self.obj.TOUCHING_DAMAGE = 300
        self.hp_sys.max_hp *= 5
        self.hp_sys.hp *= 5

    def t_draw(self):
        if self.hp_sys.hp < 1:
            self.hp_sys.hp = 1
            self.hp_sys.IMMUNE = True
            self.img = copy.copy(self.img)
            self.img.set_alpha(50)
            self.set_rotation(0)
            self.obj.IS_OBJECT = False
        else:
            self.hp_sys.IMMUNE = False
        super().t_draw()
        
    def on_update(self):
        super().on_update()
        self.tick = int(self.tick + 1)
        if self.hp_sys.hp <= 1:
            if self.tick % 192 == 1:
                lychee = Lychee(self.obj.pos)
                lychee.obj.SIGHT_DISTANCE *= 5
                lychee.VITAL = True
                lychee.hp_sys.max_hp /= 2
                lychee.hp_sys.hp /= 2
                game.get_game().entities.append(lychee)
            elif self.tick % 12 == 1:
                game.get_game().entities.append(LycheeKok(self.obj.pos,
                                                          vector.cartesian_to_polar(
                                                              *game.get_game().player.obj.pos - self.obj.pos)[0]))
        else:
            if self.tick % 48 == 1:
                game.get_game().entities.append(LycheeKok(self.obj.pos,
                                                          vector.cartesian_to_polar(*game.get_game().player.obj.pos - self.obj.pos)[0]))

class LycheeKing(entity.Entities.Entity):
    NAME = 'Lychee King'
    BOSS_NAME = 'Irrational at All'
    DISPLAY_MODE = 2
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('lychee_core_shard', 1, 20, 30),
        entity.IndividualLoot('lychee_shard', .8, 40, 60),
        entity.IndividualLoot('hammer_of_rational', 1, 1, 1),
    ])
    PHASE_SEGMENTS = []
    IS_MENACE = True

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity3_lychee_king'], entity.BuildingAI, hp=18000)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 150
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 150
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 150
        self.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 150
        self.hp_sys.defenses[damages.DamageTypes.HALLOW] = 150
        self.hp_sys.defenses[damages.DamageTypes.PACIFY] = 150
        self.tick = 0
        self.phase = 0
        self.o_hp = self.hp_sys.hp
        self.obj.TOUCHING_DAMAGE = 200
        self.lychees = [LycheeGuard((i * 200 + self.obj.pos[0], i * 200 + self.obj.pos[1])) for i in range(12)]
        for lychee in self.lychees:
            game.get_game().entities.append(lychee)
        self.hp_sys.max_hp += sum([l.hp_sys.max_hp for l in self.lychees])
        self.PHASE_SEGMENTS.append(self.o_hp / self.hp_sys.max_hp)

    def t_draw(self):
        super().t_draw()
        self.tick += 1
        if self.phase == 0 and self.hp_sys.hp < self.o_hp:
            self.phase = 1
            for l in self.lychees:
                l.hp_sys.max_hp = 1
            self.tick = -80
        for i in range(12):
            lychee = self.lychees[i]
            av = vector.Vector2D(i * 30 + self.tick * 2,
                                 600 + self.tick ** 2 / 6400 * 1400 if self.tick < 0 else
                                 2000 + 500 * math.sin(self.tick / 60 * math.pi + math.pi * i)
                                 if self.hp_sys.hp < self.o_hp else 600)
            av.x *= (1 + .5 * math.sin(self.tick / 40))
            av.y *= (1 + .5 * math.cos(self.tick / 40))
            lychee.obj.pos = self.obj.pos + av
        l_hp = sum([l.hp_sys.hp for l in self.lychees])
        if l_hp > 20:
            self.hp_sys.hp = self.o_hp + l_hp
        else:
            self.hp_sys.hp = min(self.hp_sys.hp, self.o_hp - 1)
        if self.hp_sys.hp <= 1:
            for l in self.lychees:
                if l in game.get_game().entities:
                    game.get_game().entities.remove(l)
            self.lychees.clear()

class LycheeKok(entity.Entities.Lazer):
    NAME = 'Lai Chi Kok'
    SOUND_SPAWN = None

    def __init__(self, pos, rot):
        super(entity.Entities.Lazer, self).__init__(pos, game.get_game().graphics['entity3_lychee_kok'],
                                                    entity.AbyssRuneShootAI, 500000)
        self.obj.rot = rot
        self.set_rotation(90 - rot)
        self.obj.MASS /= 4
        self.obj.apply_force(vector.Vector(rot + random.randint(60, 130) * random.choice([-1, 1]),
                                           random.randint(80000, 120000)))
        self.obj.FRICTION = 1
        self.ex_t = 0

    def on_update(self):
        super().on_update()

    def damage(self):
        self.ex_t += 1
        if vector.distance(self.obj.pos[0] - game.get_game().player.obj.pos[0],
                           self.obj.pos[1] - game.get_game().player.obj.pos[1]) < 300:
            game.get_game().player.hp_sys.damage(150, damages.DamageTypes.MAGICAL)
            game.get_game().player.hp_sys.enable_immume()
            self.hp_sys.hp = 0

class ToxicIntestine(entity.Entities.WormEntity):
    NAME = 'Toxic Intestine'

    def __init__(self, pos, length=15):
        super().__init__(pos, length, game.get_game().graphics['entity3_intestine'],
                         game.get_game().graphics['entity3_intestine'], entity.DestroyerAI, length * 400,
                         60, 140)
        self.obj.SPEED *= 1.5
        self.obj.MASS /= 1.5

class ToxicLargeIntestine(entity.Entities.WormEntity):
    NAME = 'Toxic Large Intestine'
    IS_MENACE = True
    BOSS_NAME = 'Pure Natural'
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('e_poison_powder', 1, 10, 20),
    ])

    def __init__(self, pos, length=30):
        super().__init__(pos, length, game.get_game().graphics['entity3_large_intestine'],
                         game.get_game().graphics['entity3_large_intestine'], entity.DestroyerAI, length * 7000,
                         120, 220)
        s = 0
        self.obj.SPEED *= 1.5
        for e in self.body:
            e.hp_sys = hp_system.HPSystem(7000)
            e.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 60
            e.hp_sys.defenses[damages.DamageTypes.PIERCING] = 60
            e.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 60
            e.hp_sys.defenses[damages.DamageTypes.OCTAVE] = 100
            e.hp_sys.defenses[damages.DamageTypes.HALLOW] = 100
            e.hp_sys.defenses[damages.DamageTypes.PACIFY] = 100
            e.show_bar = True
        self.body[0].hp_sys.max_hp = 1
        self.body[0].hp_sys.hp = 1
        for e in self.body:
            s += e.hp_sys.max_hp
        self.hp_sys.max_hp = s
        self.hp_sys.hp = s

    def on_update(self):
        super().on_update()
        s = 0
        for i, b in enumerate(self.body):
            s += b.hp_sys.hp
            if 2 < b.hp_sys.hp < b.hp_sys.max_hp * .2:
                b.hp_sys.damage(9999, damages.DamageTypes.TRUE)
                ax, ay = vector.polar_to_cartesian(random.randint(0, 360), 100)
                game.get_game().entities.append(ToxicIntestine((b.obj.pos[0] + ax, b.obj.pos[1] + ay)))
                b.show_bar = False
            b.hp_sys.hp = max(2, b.hp_sys.hp)
        self.hp_sys.hp = s if s > 70 else 0

class HGoblinFighter(entity.Entities.HeavenGoblinFighter):
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('heaven_wood', .3, 10, 20),
        entity.IndividualLoot('heaven_metal_helmet', .06, 1, 1),
        entity.IndividualLoot('heaven_metal_plate_mail', .06, 1, 1),
        entity.IndividualLoot('heaven_metal_leggings', .06, 1, 1),
        entity.IndividualLoot('shotgun', 0.04, 1, 1),
        entity.IndividualLoot('holy_condense_wand', 0.03, 1, 1),
        entity.IndividualLoot('holy_shine', 0.03, 1, 1),
    ])

    def __init__(self, pos):
        super().__init__(pos)
        self.hp_sys.max_hp *= 5
        self.hp_sys.hp *= 5
        for k in self.hp_sys.resistances.resistances.keys():
            self.hp_sys.resistances[k] *= .8
            self.hp_sys.defenses[k] += 30
        self.obj.TOUCHING_DAMAGE += 80

class HGoblinRanger(entity.Entities.HeavenGoblinRanger):
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('heaven_wood', .3, 10, 20),
        entity.IndividualLoot('heaven_metal_helmet', .03, 1, 1),
        entity.IndividualLoot('heaven_metal_plate_mail', .03, 1, 1),
        entity.IndividualLoot('heaven_metal_leggings', .03, 1, 1),
        entity.IndividualLoot('shotgun', 0.08, 1, 1),
        entity.IndividualLoot('holy_condense_wand', 0.03, 1, 1),
        entity.IndividualLoot('holy_shine', 0.03, 1, 1),
    ])

    def __init__(self, pos):
        super().__init__(pos)
        self.hp_sys.max_hp *= 5
        self.hp_sys.hp *= 5
        for k in self.hp_sys.resistances.resistances.keys():
            self.hp_sys.resistances[k] *= .8
        self.obj.SIGHT_DISTANCE *= 4

class HGoblinThief(entity.Entities.HeavenGoblinThief):
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('heaven_wood', .3, 10, 20),
        entity.IndividualLoot('heaven_metal_helmet', .03, 1, 1),
        entity.IndividualLoot('heaven_metal_plate_mail', .03, 1, 1),
        entity.IndividualLoot('heaven_metal_leggings', .03, 1, 1),
        entity.IndividualLoot('shotgun', 0.04, 1, 1),
        entity.IndividualLoot('holy_condense_wand', 0.03, 1, 1),
        entity.IndividualLoot('holy_shine', 0.03, 1, 1),
    ])

    def __init__(self, pos):
        super().__init__(pos)
        self.hp_sys.max_hp *= 5
        self.hp_sys.hp *= 5
        for k in self.hp_sys.resistances.resistances.keys():
            self.hp_sys.resistances[k] *= .8
        self.obj.SIGHT_DISTANCE *= 2
        self.obj.SPEED *= 1.5
        self.obj.TOUCHING_DAMAGE += 30

class RuneAltar(entity.Entities.Entity):
    DIVERSITY = False
    DISPLAY_MODE = 2
    NAME = 'Rune Altar'

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity3_rune_altar'], entity.BuildingAI, hp=1000000)
        self.hp_sys.IMMUNE = True

    def on_update(self):
        super().on_update()
        if vector.distance(*(game.get_game().player.obj.pos - self.obj.pos)) < 400:
            game.get_game().player.hp_sys.effect(effects.RuneAltar(1, 1))

