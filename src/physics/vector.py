import math

# Old Methods
def rotation_coordinate(rotation):
    return math.sin(math.radians(rotation)), -math.cos(math.radians(rotation))

def coordinate_rotation(x, y):
    return math.degrees(math.atan2(x, -y))

def distance(x, y):
    return math.sqrt(x ** 2 + y ** 2)

# New Methods

def polar_to_cartesian(dt, theta):
    dx, dy = rotation_coordinate(theta)
    return dt * dx, dt * dy

def cartesian_to_polar(dx, dy):
    dt = distance(dx, dy)
    theta = coordinate_rotation(dx, dy)
    return dt, theta


class Vector2D:
    def __init__(self, dt: float=0, theta: float=0, dx: float=0, dy: float=0):
        ax, ay = polar_to_cartesian(dt, theta)
        self.x = dx + ax
        self.y = dy + ay

    def __call__(self):
        return cartesian_to_polar(self.x, self.y)

    def __iter__(self):
        return iter((self.x, self.y))

    def __set__(self, instance, value):
        self.x, self.y = value

    def __mul__(self, value: float=1.0):
        return Vector2D(dx=self.x * value, dy=self.y * value)

    def __add__(self, other: 'Vector2D'):
        return Vector2D(dx=self.x + other.x, dy=self.y + other.y)

    def __sub__(self, other: 'Vector2D'):
        return Vector2D(dx=self.x - other.x, dy=self.y - other.y)

    def __truediv__(self, value: float):
        return Vector2D(dx=self.x / value, dy=self.y / value)

    def __iadd__(self, other: 'Vector2D'):
        self.x += other.x
        self.y += other.y

    def __isub__(self, other: 'Vector2D'):
        self.x -= other.x
        self.y -= other.y

    def __imul__(self, value: float):
        self.x *= value
        self.y *= value

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y

    # Old Methods
    def clear(self):
        self.__imul__(0)

    def add(self, vector):
        self.__iadd__(vector)

    def get_net_coordinates(self):
        return self.x, self.y

    def get_net_rotation(self):
        return cartesian_to_polar(self.x, self.y)[0]

    def get_net_value(self):
        return cartesian_to_polar(self.x, self.y)[1]

    def get_net_vector(self, time=1.0):
        return self * time

    def reset(self, time=1.0):
        self.__imul__(time)

    def restrict(self, llx, ulx, lly, uly):
        self.x = max(llx, min(ulx, self.x))
        self.y = max(lly, min(uly, self.y))

class Vector(Vector2D):
    pass

class Vectors(Vector2D):
    pass
