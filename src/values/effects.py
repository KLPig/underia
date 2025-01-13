from src.resources import time
from src.values import hp_system, elements, damages


class Effect:
    CORRESPONDED_ELEMENT = elements.ElementTypes.NONE
    IMG = 'empty'
    NAME = 'Effect'

    def __init__(self, duration, level):
        self.timer = duration
        self.level = level
        self.duration = duration
        self.tick = 0

    def on_update(self, entity: hp_system.HPSystem):
        self.tick += 1
        if time.time_interval(time.get_time(self.tick), 1, 0):
            self.timer -= 1

    def on_end(self, entity: hp_system.HPSystem):
        pass

    def on_start(self, entity: hp_system.HPSystem):
        pass


class Aberration(Effect):
    IMG = 'aberration'

    def on_update(self, entity: hp_system.HPSystem):
        super().on_update(entity)
        if time.time_interval(time.get_time(self.tick), 1, 0):
            entity.damage(self.level + 2,
                          getattr(damages.DamageTypes, 'ELEMENT_' + elements.NAMES[self.CORRESPONDED_ELEMENT].upper()))


class Burning(Aberration):
    IMG = 'burning'
    NAME = 'Burning'
    CORRESPONDED_ELEMENT = elements.ElementTypes.FIRE

class Poison(Aberration):
    IMG = 'poisoned'
    NAME = 'Poison'
    CORRESPONDED_ELEMENT = elements.ElementTypes.POISON

class PotionSickness(Effect):
    IMG = 'potion_sickness'
    NAME = 'Potion Sickness'
    CORRESPONDED_ELEMENT = elements.ElementTypes.POISON


class ManaSickness(Effect):
    IMG = 'mana_sickness'
    NAME = 'Mana Sickness'


class TruthlessCurse(Aberration):
    IMG = 'truthless_curse'
    NAME = 'Truthless Curse'
    CORRESPONDED_ELEMENT = elements.ElementTypes.DARK


class FaithlessCurse(Effect):
    IMG = 'faithless_curse'
    NAME = 'Faithless Curse'


class Shield(Effect):
    IMG = 'shield'
    NAME = 'Shield'

class TimeStop(Effect):
    IMG = 'timestop'
    NAME = 'Time-Stopped'

class Gravity(Effect):
    IMG = 'gravity'
    NAME = 'Gravity'

class JusticeTime(Effect):
    IMG = 'justice_time'
    NAME = 'Justice Time'
