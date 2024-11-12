from src.resources import time
from src.values import hp_system, elements, damages


class Effect:
    CORRESPONDED_ELEMENT = elements.ElementTypes.NONE

    def __init__(self, duration, level):
        self.timer = duration
        self.level = level
        self.duration = duration
        self.tick = 0

    def on_update(self, entity: hp_system.HPSystem):
        self.tick += 1
        if time.time_interval(time.get_time(self.tick), 1, 0):
            entity.damage(self.level * 5 + 10, getattr(damages.DamageTypes, 'ELEMENT_' + elements.NAMES[self.CORRESPONDED_ELEMENT].upper()))
            self.timer -= 1

    def on_end(self, entity: hp_system.HPSystem):
        pass

    def on_start(self, entity: hp_system.HPSystem):
        pass

class Aberration(Effect):
    pass
