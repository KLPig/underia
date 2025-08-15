class DamageTypes:
    """
    This class contains the different types of damages that can be applied to a unit.
    """
    PHYSICAL = 0
    MAGIC = 1
    TRUE = 2

class DamageElements:
    """
    This class contains the different elements that can be damaged by a unit.
    """
    NONE = 0
    AIR = 1
    EARTH = 2
    FIRE = 3
    WATER = 4
    LIGHT = 5
    DARK = 6
    LIFE = 7
    DEATH = 8
    HALLOW = 9
    ENERGY = 10
    CHAOS = 11

class Damage:
    """
    This class represents single damage applied to a unit.
    """
    def __init__(self, value: float, _type: int, element: int = 0, penetration: int = 0, **kwargs):
        self.value = value
        self.type = _type
        self.element = element
        self.penetration = penetration
        self.kwargs = kwargs