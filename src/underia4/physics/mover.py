from . import vector

class Mover:

    def __init__(self, pos, **kwargs):
        self.pos = vector.Vector(*pos)
        self.vel = vector.Vector()
        self.acc = vector.Vector()
        self.THIS_CATEGORY = 1 << 0
        self.COLLISION_CATEGORY = 0
        self.radius = 10
        self.friction = 0.01 # = k = f / -v
        for k, v in kwargs.items():
            setattr(self, k, v)

    def update(self, dt):
        self.vel += self.acc * dt - self.vel * self.friction * dt
        self.pos += self.vel * dt
        self.acc *= 0

    def collision(self, other):
        if self.THIS_CATEGORY & other.COLLISION_CATEGORY:
            pass # TODO: implement collision detection and response

