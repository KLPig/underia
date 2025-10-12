from values import damages


class Resistances:
    def __init__(self, overall: float = 1.0):
        self.resistances: dict[int, float] = {}
        for damage_id in damages.NAMES.keys():
            self.resistances[damage_id] = overall

    def set_resistance(self, damage_id: int, resistance: float):
        self.resistances[damage_id] = resistance

    def get_resistance(self, damage_id: int) -> float:
        try:
            return self.resistances[damage_id]
        except KeyError:
            self.resistances[damage_id] = 1.0
            return 1.0

    def get_resistances(self) -> dict[int, float]:
        return self.resistances

    def __getitem__(self, damage_id: int) -> float:
        return self.get_resistance(damage_id)

    def __setitem__(self, damage_id: int, resistance: float):
        self.set_resistance(damage_id, resistance)

    def __iter__(self):
        return iter(self.resistances.items())

    def __str__(self):
        return str(self.resistances)


class Defenses:
    def __init__(self, overall: float = 0.0):
        self.defences: dict[int, float] = {}
        for damage_id in damages.NAMES.keys():
            self.defences[damage_id] = overall

    def set_defense(self, damage_id: int, defense: float):
        self.defences[damage_id] = defense

    def get_defense(self, damage_id: int) -> float:
        return self.defences[damage_id]

    def get_defences(self) -> dict[int, float]:
        return self.defences

    def __getitem__(self, damage_id: int) -> float:
        try:
            return self.get_defense(damage_id)
        except KeyError:
            self.defences[damage_id] = 0.0
            return 0.0

    def __setitem__(self, damage_id: int, defense: float):
        self.set_defense(damage_id, defense)

    def __iter__(self):
        return iter(self.defences.items())

    def __str__(self):
        return str(self.defences)
