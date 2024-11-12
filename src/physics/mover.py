from src.physics import vector

class Mover:
    MASS = 1.0
    FRICTION = 0.9

    def __init__(self, pos):
        self.pos = pos
        self.velocity = vector.Vectors()
        self.force = vector.Vectors()


    def apply_force(self, force):
        self.force.add(force)

    def on_update(self):
        pass

    def update(self):
        self.force.clear()
        self.on_update()
        self.velocity.add(self.force.get_net_vector(1 / self.MASS))
        self.velocity.reset(self.FRICTION)
        vx, vy = self.velocity.get_net_coordinates()
        self.pos = (self.pos[0] + vx, self.pos[1] + vy)
        self.on_update()