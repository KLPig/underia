from src import constants

class ElementTypes:
    NONE: int = 0

    FIRE: int = 0
    WATER: int = 0
    EARTH: int = 0
    WIND: int = 0

    LIGHT: int = 0
    DARK: int = 0

    POISON: int = 0
    LIFE: int = 0
    DEATH: int = 0

    ACID: int = 0
    COLD: int = 0

dirs = [d if d[0] != '_' else None for d in dir(ElementTypes)]
while None in dirs:
    dirs.remove(None)

for i in range(len(dirs)):
    setattr(ElementTypes, dirs[i], i + constants.ELEMENT_TYPE_CONSTANT * len(dirs))

NAMES = {}

for i in range(len(dirs)):
    NAMES[getattr(ElementTypes, dirs[i])] = dirs[i].lower()
