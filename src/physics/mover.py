import math
from underia import game
import constants
from physics import vector


class Mover:
    MASS = 1.0
    FRICTION = 0.9
    TOUCHING_DAMAGE = 0
    IS_OBJECT = True
    BOUNCY = False

    def __init__(self, pos):
        self.pos = pos
        self.velocity = vector.Vectors()
        self.force = vector.Vectors()

    def __del__(self):
        del self.pos
        del self.velocity
        del self.force

    def apply_force(self, force):
        self.force.add(force)

    def on_update(self):
        pass

    def update(self):
        self.on_update()
        if not self.MASS:
            self.MASS = 1.0
        self.velocity.add(self.force.get_net_vector(1 / self.MASS))
        self.force.clear()
        vx, vy = self.velocity.get_net_coordinates()
        self.pos = (self.pos[0] + vx / 50 * game.get_game().clock.last_tick,
                    self.pos[1] + vy / 50 * game.get_game().clock.last_tick)
        self.pos = (max(-constants.MOVER_POS, min(constants.MOVER_POS, self.pos[0])),
                    max(-constants.MOVER_POS, min(constants.MOVER_POS, self.pos[1])))
        self.velocity.reset(self.FRICTION)
        self.on_update()

    def momentum(self, rot):
        return self.velocity.get_net_value() * self.MASS  # * math.cos(math.radians(rot - self.velocity.get_net_rotation()))

    def object_gravitational(self, other: 'Mover'):
        if other is self:
            return
        if self.MASS > other.MASS:
            return False
        if not self.IS_OBJECT or not other.IS_OBJECT:
            return False
        r = (other.pos[0] - self.pos[0]) ** 2 + (other.pos[1] - self.pos[1]) ** 2
        G = .012
        if not r:
            return False
        self.force.add(vector.Vector(vector.coordinate_rotation(other.pos[0] - self.pos[0], other.pos[1] - self.pos[1]),
                                     G * self.MASS * other.MASS / r))
        return False

    def object_collision(self, other: 'Mover', required_distance: float):
        if other is self:
            return False
        if self.MASS > other.MASS:
            return False
        if not self.IS_OBJECT or not other.IS_OBJECT:
            return False
        r = (other.pos[0] - self.pos[0]) ** 2 + (other.pos[1] - self.pos[1]) ** 2
        d = math.sqrt(r)
        rot = vector.coordinate_rotation(other.pos[0] - self.pos[0], other.pos[1] - self.pos[1])
        if d <= required_distance:
            non_bounce = not self.BOUNCY and not other.BOUNCY
            u1 = self.velocity.get_net_value() * math.cos(math.radians(rot - self.velocity.get_net_rotation())) * self.FRICTION
            u2 = other.velocity.get_net_value() * math.cos(math.radians(rot - other.velocity.get_net_rotation())) * other.FRICTION
            if u1 < 0 or u2 > 0:
                return True
            self.velocity.add(vector.Vector(rot, -u1))
            m1 = self.MASS
            m2 = other.MASS
            if non_bounce:
                v1 = (m1 * u1 + m2 * u2) / (m1 + m2)
            else:
                v1 = (u1 * (m1 - m2) + 2 * m2 * u2) / (m1 + m2)
            self.velocity.add(vector.Vector(rot, v1))
            return True
        return False
