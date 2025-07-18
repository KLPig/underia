import random

import constants
from physics import vector
from underia import game
from values import reduction, effects, damages


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

    def damage(self, damage: float, damage_type: int, penetrate: float = 0):
        if self.IMMUNE or self.is_immune:
            return
        try:
            d = vector.distance(self.pos[0] - game.get_game().player.obj.pos[0],
                                self.pos[1] - game.get_game().player.obj.pos[1])
            if self.SOUND_HURT is not None:
                game.get_game().play_sound('hit_' + self.SOUND_HURT, vol=0.99 ** int(d / 10))
        except ValueError:
            pass
        dmm = [.3, 1.0, 1.25, 1.90][constants.DIFFICULTY]
        dm = [.31, 1.0, 1.24, 1.88][constants.DIFFICULTY]
        dmg = (damage * self.resistances[damage_type] * dmm -
               (max(0.0, self.defenses[damage_type] - penetrate) if self.defenses[damage_type] > 0 else
                min(0.0, self.defenses[damage_type] + penetrate)) * dm)
        dmg *= (1 - self.DAMAGE_RANDOMIZE_RANGE + 2 *
                self.DAMAGE_RANDOMIZE_RANGE * random.random())
        dmg = max(self.MINIMUM_DAMAGE, min(self.MAXIMUM_DAMAGE, dmg))
        dodge = dmg > 1 and random.random() < self.DODGE_RATE
        if dodge:
            dmg = 0
        if not self.dmg_t:
            self.dmg_t = self.DAMAGE_TEXT_INTERVAL
            d = 0
            if dmg <= 1:
                if dodge:
                    t = 'MISS'
                elif self.resistances[damage_type] == 0:
                    t = 'IMMUNE'
                else:
                    t = 'RESISTED'
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
                    game.get_game().damage_texts.append(
                        (t, 0, (self.pos[0] + random.randint(-30, 30), self.pos[1] + random.randint(-30, 30))))
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
                    game.get_game().damage_texts.append(
                        (str(int(dmg)), 0, (self.pos[0] + random.randint(-30, 30), self.pos[1] + random.randint(-30, 30))))
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
        if damage_type == damages.DamageTypes.THINKING:
            game.get_game().player.hp_sys.heal(dmg * game.get_game().player.hp_sys.max_hp // 1200000)
        if self.hp <= 0:
            self.hp = 0

    def enable_immume(self):
        self.is_immune = self.IMMUNE_TIME

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
                    nef = type(self.effects[i])(max(self.effects[i].duration, self.effects[j].duration),
                                                self.effects[i].level + self.effects[j].level)
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
        self.effects.append(effect)

    def heal(self, val):
        self.hp = min(self.max_hp, self.hp + val)
        self.displayed_hp = max(self.displayed_hp, self.hp)


class SubHPSystem(HPSystem):

    def __init__(self, hp_sys: HPSystem):
        super().__init__(hp_sys.hp)
        self.hp_sys = hp_sys

    def __del__(self):
        del self.hp_sys

    def update(self):
        self.hp = self.hp_sys.hp
        self.displayed_hp = self.hp_sys.displayed_hp
        self.max_hp = self.hp_sys.max_hp
        self.is_immune = self.hp_sys.is_immune
        self.hp_sys.update()

    def damage(self, *args, **kwargs):
        self.hp_sys.damage(*args, **kwargs)

    def enable_immume(self):
        self.hp_sys.enable_immume()

    def effect(self, effect):
        self.hp_sys.effect(effect)

    def heal(self, val):
        self.hp_sys.heal(val)
