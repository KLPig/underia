class Weapon:
    def __init__(self, name, damage, ac):
        self.name = name
        self.damage = damage
        self.tick = 0
        self.t = 0
        self.r = 0
        self.spd = 0
        self.type = ''

    def attack(self, rotation):
        pass

    def sweep(self, st_rotation, spd, t):
        self.type = 'Sweep'
        self.spd = spd
        self.t = t
        self.r = st_rotation
        self.tick = 0