import copy
import random
import inspect

import constants
from physics import vector
from underia import game, entity, weapons, projectiles, inventory
from values import reduction, effects, damages
from visual import particle_effects as pef
from resources import log, position
import math

class DamageValue:
    def __init__(self, value: float, penetrate: float = 0.0, **kwargs):
        self.value = value
        self.penetrate = penetrate
        self.follow_penetrate = False
        self.source = 'player'

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __mul__(self, other):
        v = copy.copy(self)
        v.value *= other
        if self.follow_penetrate:
            v.penetrate *= other

        return v

    def __float__(self):
        return float(self.value)

    def __add__(self, other):
        v = copy.copy(self)
        v.value += other
        if self.follow_penetrate:
            v.penetrate += other
        return v

    def __str__(self):
        s = str(int(self.value))
        if self.penetrate > 0:
            s += f"(+{self.penetrate:.0f})"
        return s

class HPSystem:
    TRUE_DROP_SPEED_MAX_RATE = 0.1
    TRUE_DROP_SPEED_MAX_VALUE = 5

    IMMUNE = False
    IMMUNE_TIME = 5

    MINIMUM_DAMAGE = 1
    MAXIMUM_DAMAGE = constants.INFINITY

    DAMAGE_RANDOMIZE_RANGE = 0.12
    DAMAGE_TEXT_INTERVAL = 0

    PACIFY_TIME = 36

    SOUND_HURT = None

    DODGE_RATE = 0.0


    def __init__(self, hp: float):
        self.resistances = reduction.Resistances()
        self.defenses = reduction.Defenses()
        self.resistances[damages.DamageTypes.ARCANE] = 37 if constants.DIFFICULTY <= 1 else 43
        self.hp = hp
        self.displayed_hp = hp
        self.max_hp = hp
        self.pacify = 0.0
        self.is_immune = False
        self.effects: list[effects.Effect] = []
        self.pos: vector.Vector2D = vector.Vector2D()
        self.dmg_t = 0
        self.SOUND_HURT = None
        self.shields: list[tuple[str, int]] = []
        self.pacify_cd = 0
        self.is_player = False
        self.adaption = {}
        self.ADAPTABILITY = 0.0
        self.c_ele = ('', 0)
        self.spec_ele = {}

    def __del__(self):
        pass

    def __call__(self, *args, **kwargs):
        if 'op' in kwargs:
            if kwargs['op'] == 'config':
                avails = ['true_drop_speed_max_rate', 'true_drop_speed_max_value', 'immune_time',
                          'immune', 'minimum_damage', 'maximum_damage', 'damage_randomize_range',
                          'damage_text_interval', 'pacify_time']
                for k, v in kwargs.items():
                    if k in avails:
                        setattr(self, k.upper(), v)
        else:
            return self.hp

    def damage(self, damage: float | DamageValue, damage_type: int, penetrate: float = 0, sound=True, dd: vector.Vector2D | tuple[int, int] | None = None):
        if type(damage) is DamageValue:
            penetrate += damage.penetrate
            damage = damage.value
        if 'adaption' not in dir(self):
            self.adaption = {}
        if self.IMMUNE or self.is_immune:
            return

        stack = inspect.stack()
        user = stack[1].frame.f_locals['self']
        if issubclass(type(user), entity.Entities.Entity):
            ee = 0b10
            crit = 0
            c_ele = None
        elif issubclass(type(user), weapons.Weapon):
            ee = 0b1
            crit = game.get_game().player.strike + user.critical
            item = inventory.ITEMS[user.t_id]

            ele_s = [t.value for t in item.tags if t.name.startswith('magic_element_')]
            ele_v = [t.name.removeprefix('magic_lv_') for t in item.tags if t.name.startswith('magic_lv_')]

            if len(ele_s) and len(ele_v):
                c_ele = (random.choice(ele_s), float(ele_v[0]))
            else:
                c_ele = None


        elif issubclass(type(user), projectiles.Projectiles.Projectile):
            ee = 0b1
            if 'weapon' in dir(user):
                if 'critical' in dir(user.weapon):
                    crit = game.get_game().player.strike + user.weapon.critical
                else:
                    crit = game.get_game().player.strike
                    log.error(f'Wrong analyze of origin weapon of {user}, that is {user.weapon}, this may be because of inner problems!')
            else:
                crit = game.get_game().player.strike
                log.error(f'Cannot analyze original weapon of {user} - {user}, this may be because not calling Projectile.__init__() while defining a subclass' )
            user = user.weapon
            item = inventory.ITEMS[user.t_id]

            ele_s = [t.value for t in item.tags if t.name.startswith('magic_element_')]
            ele_v = [t.name.removeprefix('magic_lv_') for t in item.tags if t.name.startswith('magic_lv_')]

            if len(ele_s) and len(ele_v):
                c_ele = (random.choice(ele_s), float(ele_v[0]))
            else:
                c_ele = None
        else:
            ee = 0
            crit = 0

            c_ele = None
        try:
            d = vector.distance(self.pos[0] - game.get_game().player.obj.pos[0],
                                self.pos[1] - game.get_game().player.obj.pos[1])
            if self.SOUND_HURT is not None and sound:
                game.get_game().play_sound('hit_' + self.SOUND_HURT, vol=0.99 ** int(d / 10))
        except ValueError:
            pass
        dmm = [.3, 1.0, 1.15, 1.50][constants.DIFFICULTY]
        dm = [.31, 1.0, 1.14, 1.48][constants.DIFFICULTY]

        kd = .6 - constants.DIFFICULTY * .05 # ideal defense rate
        ct = random.random() < crit

        rs = self.resistances[damage_type]

        if self.defenses[damage_type] > 0:
            td = max(0.1, self.defenses[damage_type] - penetrate)

            rd = td / max(10 ** -9, damage * rs * kd)

            if ee & 1:
                if rd > 1.0:
                    rd **= .9 - constants.DIFFICULTY * .12
                else:
                    rd **= .5 + constants.DIFFICULTY * .03


                dmg = damage * rs * dmm * (1 - rd * kd) * dm
            else:
                dmg = damage * dmm * rs - self.defenses[damage_type] * dm
        else:
            dmg = damage * dmm * rs - self.defenses[damage_type]

        dmg *= (1 - self.DAMAGE_RANDOMIZE_RANGE + 2 *
                self.DAMAGE_RANDOMIZE_RANGE * random.random())
        dmg = max(self.MINIMUM_DAMAGE, min(self.MAXIMUM_DAMAGE, dmg))
        dodge = dmg > 1 and random.random() < self.DODGE_RATE
        if dodge:
            dmg = 0
        u_name = user.__class__.__name__
        if u_name not in self.adaption:
            self.adaption[u_name] = 0
        dmg *= math.e ** (-self.adaption[u_name])
        if c_ele and c_ele[0] in self.spec_ele:
            dmg *= self.spec_ele[c_ele[0]] ** (1 + c_ele[1] / 10)
        game.get_game().c_dmg += dmg
        if 'c_ele' not in dir(self):
            self.c_ele = ('', 0)
        if self.c_ele and c_ele:
            sl, x = self.c_ele
            el, y = c_ele
            dt = sl + '2' + el
            dp = self.pos if dd is None else dd
            ds = True
            if dt == 'fire magic2water magic':
                if x > max(2.0, y):
                    dmg *= 1 + .3 * y
                    game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(dp), n=30, col=(100, 100, 100), g=-0.5, sp=22, t=45))
                elif y > max(3.0, x):
                    game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(dp), n=30, col=(0, 255, 255), g=0, sp=12, t=60))
                    t = [0, .3, .5, .8, 1.0, 1.5, 2.5, 4.0, 12.0, 20.0][min(9, math.floor(y))] * y / min(9, math.floor(y))
                    self.effect(effects.Freezing(t * 5, 1))
                    self.effect(effects.Frozen(t, 1))
            elif dt == 'fire magic2air magic':
                if y > max(2.0, x):
                    game.get_game().displayer.effect(
                        pef.p_particle_effects(*position.displayed_position(dp), n=60, col=(255, 0, 0), g=0.01, sp=12, t=50))
                    for e in game.get_game().entities:
                        if abs(e.obj.pos - dp) < 100 * y:
                            e.hp_sys.effect(effects.Burning(5, int(dmg / 5)))
            elif dt == 'earth magic2water magic':
                if y > x > 2:
                    game.get_game().displayer.effect(
                        pef.p_particle_effects(*position.displayed_position(dp), n=40, col=(50, 50, 0), g=0.05, sp=4, t=50, r=20))
                    for e in game.get_game().entities:
                        if e.hp_sys == self:
                            e.obj.MASS *= 1 + .03 * y
            elif dt == 'earth magic2air magic':
                if y - 1 > x > 1:
                    game.get_game().displayer.effect(
                        pef.p_particle_effects(*position.displayed_position(dp), n=30, col=(0, 200, 200), g=-0.5, sp=22, t=45))
                    if self.defenses[damage_type] > dmg * max(0.0, 10 - y) / 10:
                        self.defenses[damage_type] -= dmg / 50 * y
            elif dt == 'water magic2fire magic':
                if y > x > 2:
                    game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(dp), n=30, col=(0, 100, 255), g=0.1, sp=12, t=60))
                    for e in game.get_game().entities:
                        if e.hp_sys == self and e.obj.SPEED > 1:
                            e.obj.SPEED *= 1 - .03 * y
            elif dt == 'life magic2fire magic':
                if 6 > y > x > 2:
                    game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(dp), n=30, col=(100, 100, 100), g=-0.3, sp=12, t=55))
                    self.effect(effects.Burning(5, int(dmg * y / 5)))
                elif x > y > 5:
                    game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(dp), n=90, col=(255, 0, 0), g=-0.3, sp=25, t=85, r=30))
                    dmg += .001 * y * self.max_hp
            elif dt == 'earth magic2life magic':
                if x > y > 2:
                    game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(dp), n=20, col=(200, 255, 0), g=0, sp=5, t=40))
                    if self.defenses[damage_type] > dmg:
                        self.defenses[damage_type] -= dmg / 30 * y ** 1.5
            elif dt in ['death magic2life magic', 'life magic2death magic']:
                if x == y > 2:
                    game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(dp), n=20, col=(0, 0, 0), g=0.1, sp=9, t=40))
                    game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(dp), n=20, col=(255, 255, 255), g=-0.1, sp=9, t=40))
                    if self.resistances[damage_type] < 1.0 + y * .1:
                        self.resistances[damage_type] /= 1 - y * .008
            elif dt == 'earth magic2death magic':
                if min(x, y) > 3:
                    game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(dp), n=30, col=(0, 0, 0), g=0.1, sp=14, t=40))
                    if self.resistances[damage_type] < max(1.0, .5 + y * .25):
                        self.resistances[damage_type] *= 1 - y * .003
            elif dt == 'fire magic2light magic':
                if y > x > 2:
                    game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(dp), n=30, col=(255, 255, 255), g=-0.1, sp=14, t=40))
                    for e in game.get_game().entities:
                        if abs(e.obj.pos - dp) < 80 * y:
                            e.hp_sys.damage(damage_type, dmg * y / 10)
            elif dt == 'dark magic2death magic':
                if x == y > 4:
                    game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(dp), n=20, col=(0, 0, 0), g=0.03, sp=4, t=60))
                    dmg *= max(1.0, .3 + .5 * y)
            elif dt == 'light magic2life magic':
                if x == y > 4:
                    game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(dp), n=20, col=(255, 255, 200), g=0.03, sp=4, t=60))
                    crit *= 1 + y * .3
                    ct = random.random() < crit
            elif dt == 'death magic2time magic':
                if x > 5:
                    game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(dp), n=90, col=(100, 0, 0), g=0.03, sp=20, t=60))
                    for e in game.get_game().entities:
                        e.hp_sys.damage(damage_type, dmg * (5 + y) / 25)
            elif dt == 'life magic2time magic':
                if x > 5:
                    game.get_game().displayer.effect(pef.p_particle_effects(*position.displayed_position(dp), n=90, col=(100, 255, 0), g=0.03, sp=20, t=60))
                    game.get_game().player.hp_sys.heal(dmg * (5 + y) / 25)
            else:
                 ds = False

            if ds:
                for e in game.get_game().entities:
                    if e.hp_sys == self:
                        e.play_sound('create')

        if ct:
            dmg *= 1 + (1 + crit) ** 2
        if c_ele:
            self.c_ele = copy.copy(c_ele)
        if not self.dmg_t:
            self.dmg_t = self.DAMAGE_TEXT_INTERVAL
            d = 0
            if dmg <= 1:
                if dodge:
                    t = 'MISS'
                    self.dmg_t *= 5
                elif self.resistances[damage_type] == 0:
                    t = '0'
                else:
                    t = '1'
                '''
                for i in range(len(game.get_game().damage_texts)):
                    if abs(game.get_game().damage_texts[i][2][0] - self.pos[0]) < 300 \
                            and abs(game.get_game().damage_texts[i][2][1] - self.pos[1]) < 300 and \
                            game.get_game().damage_texts[i][0] == t:
                        game.get_game().damage_texts[i] = (t, 0, (self.pos[0] + random.randint(-10, 10),
                                                                  self.pos[1] + random.randint(-10, 10)))
                        d = 1
                        break'''
                if not d:
                    if dd is None:
                        dp = self.pos
                    else:
                        dp = dd
                    game.get_game().damage_texts.append(
                        (t, 0, (dp[0] + random.randint(-30, 30), dp[1] + random.randint(-30, 30)), 0))
            else:
                '''
                for i in range(len(game.get_game().damage_texts)):
                    if abs(game.get_game().damage_texts[i][2][0] - self.pos[0]) < 300 \
                            and abs(game.get_game().damage_texts[i][2][1] - self.pos[1]) < 300 and \
                            game.get_game().damage_texts[i][0].isdecimal():
                        game.get_game().damage_texts[i] = (str(int(dmg) + int(game.get_game().damage_texts[i][0])), 0,
                                                           (self.pos[0] + random.randint(-10, 10),
                                                            self.pos[1] + random.randint(-10, 10)))
                        d = 1
                    break'''
                if not d:
                    if dd is None:
                        dp = self.pos
                    else:
                        dp = dd
                    game.get_game().damage_texts.append(
                        (str(int(dmg)), 0, (dp[0] + random.randint(-30, 30), dp[1] + random.randint(-30, 30)), ct))
        if 'ADAPTABILITY' not in dir(self):
            self.ADAPTABILITY = 0.0
        self.adaption[u_name] += damage * 1e-3 * self.ADAPTABILITY
        if len(self.shields):
            self.shields[0] = (self.shields[0][0], self.shields[0][1] - dmg)
            if self.shields[0][1] <= 0:
                self.shields.pop(0)
            return
        if damage_type == damages.DamageTypes.PACIFY:
            self.pacify = min(self.pacify + dmg, self.max_hp)
            self.pacify_cd = int(self.PACIFY_TIME * game.get_game().player.calculate_data('pacify_time', rate_data=True, rate_multiply=True))
        else:
            self.hp -= dmg
        if 'murder' not in game.get_game().player.profile.skill_points:
            game.get_game().player.profile.skill_points['murder'] = 0
        if damage_type == damages.DamageTypes.THINKING:
            game.get_game().player.hp_sys.heal(dmg * game.get_game().player.hp_sys.max_hp // 1200000)
            game.get_game().player.profile.skill_points['illusion'] += dmg / 5
        if damage_type == damages.DamageTypes.PHYSICAL:
            game.get_game().player.profile.skill_points['melee'] += damage / 10
        if damage_type == damages.DamageTypes.PIERCING:
            game.get_game().player.profile.skill_points['ranged'] += dmg / 12 + penetrate / 5
        if self is game.get_game().player.hp_sys:
            game.get_game().player.profile.skill_points['vessel'] += damage / 7
        if ee & 0b1:
            game.get_game().player.profile.skill_points['murder'] += dmg


    def enable_immune(self, t=1.0):
        if not self.is_immune:
            self.is_immune = self.IMMUNE_TIME * t

    def update(self):
        try:
            self.pacify_cd
        except AttributeError:
            self.pacify_cd = 0
            self.pacify = 0
        self.hp = min(self.hp, self.max_hp - self.pacify)
        if self.pacify_cd:
            self.pacify_cd -= 1
        else:
            self.pacify = max(self.pacify - self.max_hp / 200, 0)
        if self.dmg_t:
            self.dmg_t -= 1
        for eff in self.effects:
            eff.on_update(self)
            if eff.timer <= 0:
                eff.on_end(self)
                self.effects.remove(eff)
                del eff
        for i in range(len(self.effects)):
            for j in range(i + 1, len(self.effects)):
                if j < len(self.effects) and type(self.effects[i]) is type(self.effects[j]):
                    nef = type(self.effects[i])(self.effects[i].duration + self.effects[j].duration,
                                                max(self.effects[i].level, self.effects[j].level))
                    self.effects[i] = nef
                    self.effects.remove(self.effects[j])
                    j -= 1
        if self.is_immune:
            self.is_immune -= 1
            if self.is_immune <= 0:
                self.is_immune = False
        self.displayed_hp -= min(max(self.displayed_hp - self.hp, 0),
                                 max(self.TRUE_DROP_SPEED_MAX_RATE * (self.displayed_hp - self.hp),
                                     self.TRUE_DROP_SPEED_MAX_VALUE))
        self.displayed_hp = min(self.max_hp, self.displayed_hp + max(max(self.max_hp // 200, (self.hp - self.displayed_hp) // 5), 0))
        if self.displayed_hp < 0:
            self.displayed_hp = 0

    def effect(self, effect):
        effect.on_start(self)
        for e in self.effects:
            if type(e) is type(effect):
                if e.COMBINE == "Duration":
                    e.duration += effect.duration
                else:
                    e.duration = max(e.duration, effect.duration)
                e.level = max(e.level, effect.level)
                return
        self.effects.append(effect)

    def heal(self, val):
        self.hp = min(self.max_hp, self.hp + val)
        self.displayed_hp = max(self.displayed_hp, self.hp)


class SubHPSystem(HPSystem):

    def __init__(self, hp_sys: HPSystem):
        super().__init__(hp_sys.hp)
        self.hp_sys = hp_sys
        self.resistances = reduction.Resistances()
        self.resistances.resistances = copy.copy(hp_sys.resistances.resistances)
        self.defenses = reduction.Defenses()
        self.defenses.defenses = copy.copy(hp_sys.defenses.defences)

    def __del__(self):
        del self.hp_sys

    def update(self):
        self.hp = self.hp_sys.hp
        self.displayed_hp = self.hp_sys.displayed_hp
        self.max_hp = self.hp_sys.max_hp
        self.is_immune = self.hp_sys.is_immune
        self.hp_sys.update()

    def damage(self, *args, **kwargs):
        rr = self.hp_sys.resistances
        dd = self.hp_sys.defenses
        self.hp_sys.resistances = copy.copy(self.resistances)
        self.hp_sys.defenses = copy.copy(self.defenses)
        self.hp_sys.damage(*args, **kwargs, dd=self.pos)
        self.hp_sys.resistances = copy.copy(rr)
        self.hp_sys.defenses = copy.copy(dd)

    def enable_immune(self, t=1.0):
        self.hp_sys.enable_immune(t)

    def effect(self, effect):
        self.hp_sys.effect(effect)

    def heal(self, val):
        self.hp_sys.heal(val)
