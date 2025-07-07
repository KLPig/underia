import math


def rotation_coordinate(rotation):
    return math.sin(math.radians(rotation)), -math.cos(math.radians(rotation))


def coordinate_rotation(x, y):
    return math.degrees(math.atan2(x, -y))

def polar_to_cartesian(theta, dt):
    dx, dy = rotation_coordinate(theta)
    return dx * dt, dy * dt

def cartesian_to_polar(dx, dy):
    return coordinate_rotation(dx, dy), distance(dx, dy)

def distance(x, y):
    return (x ** 2 + y ** 2) ** .5

class Vector2D:
    def __init__(self, dr=0, dt=0, dx=0, dy=0):
        ax, ay = polar_to_cartesian(dr, dt)
        self.x = dx + ax
        self.y = dy + ay

    def __call__(self):
        return cartesian_to_polar(self.x, self.y)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"Vector2D({self.x}, {self.y})"

    def __iter__(self):
        return iter((self.x, self.y))

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Index out of range")

    def __setitem__(self, index, value):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        else:
            raise IndexError("Index out of range")

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        return Vector2D(dx=self.x + other[0], dy=self.y + other[1])

    def __sub__(self, other):
        return Vector2D(dx=self.x - other[0], dy=self.y - other[1])

    def __mul__(self, other):
        return Vector2D(dx=self.x * other, dy=self.y * other)

    def __rmul__(self, other):
        return Vector2D(dx=self.x * other, dy=self.y * other)

    def __truediv__(self, other):
        return Vector2D(dx=self.x / other, dy=self.y / other)

    def __neg__(self):
        return Vector2D(dx=-self.x, dy=-self.y)

    def __pos__(self):
        return Vector2D(dx=+self.x, dy=+self.y)

    def __iadd__(self, other):
        self.x += other[0]
        self.y += other[1]
        return self

    def __isub__(self, other):
        self.x -= other[0]
        self.y -= other[1]
        return self

    def __imul__(self, other):
        self.x *= other
        self.y *= other
        return self

    def __idiv__(self, other):
        self.x /= other
        self.y /= other
        return self

    def __abs__(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __invert__(self):
        return Vector2D(dx=-self.x, dy=-self.y)

    # Redefine: set a value from tuple
    def __lshift__(self, other):
        self.x, self.y = other
        return self


    def restrict(self, d_min, d_max):
        self.x = max(d_min, min(d_max, self.x))
        self.y = max(d_min, min(d_max, self.y))

    def clear(self):
        self.__imul__(0)

    def add(self, other):
        self.__iadd__(other)

    def get_net_coordinates(self):
        return self.x, self.y

    def get_net_rotation(self):
        return self()[0]

    def get_net_value(self):
        return self()[1]

    def get_net_vector(self, time=1.0):
        return self * time

    def reset(self, time=1.0):
        self.__imul__(time)

class Vector(Vector2D):
    pass

class Vectors(Vector2D):
    pass