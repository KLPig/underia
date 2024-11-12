from src import constants
from src.values import reduction, effects

import random

class HPSystem:

    TRUE_DROP_SPEED_MAX_RATE = 0.1
    TRUE_DROP_SPEED_MAX_VALUE = 5

    IMMUNE = False
    IMMUNE_TIME = 10

    MINIMUM_DAMAGE = 1
    MAXIMUM_DAMAGE = constants.INFINITY

    DAMAGE_RANDOMIZE_RANGE = 0.12

    def __init__(self, hp: float):
        self.resistances = reduction.Resistances()
        self.defenses = reduction.Defenses()
        self.hp = hp
        self.displayed_hp = hp
        self.max_hp = hp
        self.is_immune = False
        self.effects: list[effects.Effect] = []

    def __call__(self, *args, **kwargs):
        if 'op' in kwargs:
            if kwargs['op'] == 'config':
                avails = ['true_drop_speed_max_rate', 'true_drop_speed_max_value', 'immune_time','minimum_damage','maximum_damage', 'damage_randomize_range']
                for k, v in kwargs.items():
                    if k in avails:
                        setattr(self, k.upper(), v)
        else:
            return self.hp

    def damage(self, damage: float, damage_type: int):
        if self.IMMUNE or self.is_immune:
            return
        dmg = damage * self.resistances[damage_type] - self.defenses[damage_type]
        dmg *= (1 - self.DAMAGE_RANDOMIZE_RANGE + 2 * round(self.DAMAGE_RANDOMIZE_RANGE * random.random(), 1))
        dmg = max(self.MINIMUM_DAMAGE, min(self.MAXIMUM_DAMAGE, dmg))
        self.hp -= dmg
        if self.hp <= 0:
            self.hp = 0
        self.is_immune = self.IMMUNE_TIME

    def update(self):
        for eff in self.effects:
            eff.on_update(self)
            if eff.timer <= 0:
                eff.on_end(self)
                self.effects.remove(eff)
        if self.is_immune:
            self.is_immune -= 1
            if self.is_immune <= 0:
                self.is_immune = False
        self.displayed_hp -= min(self.displayed_hp - self.hp, max(self.TRUE_DROP_SPEED_MAX_RATE * (self.displayed_hp - self.hp), self.TRUE_DROP_SPEED_MAX_VALUE))
        if self.displayed_hp < 0:
            self.displayed_hp = 0

    def effect(self, effect):
        effect.on_start(self)
        self.effects.append(effect)
