from src import constants
from src.values import elements


class DamageTypes:
    PHYSICAL: int = 0
    MAGICAL: int = 0
    TRUE: int = 0
    PIERCING: int = 0
    ARCANE: int = 0
    TOUCHING: int = 0


for element in dir(elements.ElementTypes):
    if not element.startswith('__'):
        setattr(DamageTypes, 'ELEMENT_' + elements.NAMES[getattr(elements.ElementTypes, element)].upper(), 0)

dirs = [d if d[0] != '_' else None for d in dir(DamageTypes)]

while None in dirs:
    dirs.remove(None)

for i in range(len(dirs)):
    setattr(DamageTypes, dirs[i], i + constants.DAMAGE_TYPE_CONSTANT * len(dirs))

NAMES = {}

for i in range(len(dirs)):
    NAMES[getattr(DamageTypes, dirs[i])] = dirs[i].lower()
