from . import damages

class HPBar:
    def __init__(self, hp: float, **kwargs):
        self.hp = hp
        self.max_hp = hp
        self.min_hp = hp
        self.supers = []
        self.kwargs = kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)

    def is_dead(self):
        return self.hp <= 0

class HPSystem:
    def __init__(self, **kwargs):
        self.bar: HPBar | None = None
        self.resistances = {}
        self.defenses = {}
        self.min_dmg = 1.0
        self.max_dmg = 2147483647.0
        if 'hp' in kwargs:
            self.bar = HPBar(kwargs['hp'], **kwargs)
            self.bar.supers.append(self)
        elif 'bar' in kwargs:
            assert isinstance(kwargs['bar'], HPBar)
            self.bar = kwargs['bar']
            self.bar.supers.append(self)
        if 'resistances' in kwargs:
            assert isinstance(kwargs['resistances'], dict)
            self.resistances.update(kwargs['resistances'])
        if 'defenses' in kwargs:
            assert isinstance(kwargs['defenses'], dict)
            self.defenses.update(kwargs['defenses'])
        for k, v in kwargs.items():
            setattr(self, k, v)

    def on_damage(self, value: float, **kwargs):
        if self.bar is None:
            return
        self.bar.hp -= value
        self.bar.hp = max(self.bar.hp, self.bar.min_hp)

    def on_heal(self, value: float, **kwargs):
        if self.bar is None:
            return
        self.bar.hp += value
        self.bar.hp = min(self.bar.hp, self.bar.max_hp)

    def damage(self, dmg: damages.Damage, **kwargs):
        _type = dmg.type
        _ele = dmg.element
        _dmg = dmg.value
        if _type in self.resistances:
            _dmg *= 1 - self.resistances[_type]
        if _ele in self.resistances:
            _dmg *= 1 - self.resistances[_ele]
        _def = 0
        if _type in self.defenses:
            _def += self.defenses[_type]
        if _ele in self.defenses:
            _def += self.defenses[_ele]
        if _def > 0:
            _def = max(0, _def - dmg.penetration)
        elif _def < 0:
            _def = min(0, _def + dmg.penetration)
        assert self.min_dmg <= self.max_dmg
        _dmg = max(self.min_dmg, min(self.max_dmg, _dmg - _def))
        self.on_damage(_dmg, **kwargs)
        return _dmg

    def heal(self, value: float, **kwargs):
        if self.bar is None:
            return
        self.on_heal(value, **kwargs)
        self.bar.hp = min(self.bar.hp, self.bar.max_hp)
