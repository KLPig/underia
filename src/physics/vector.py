import math


def rotation_coordinate(rotation):
    return math.sin(math.radians(rotation)), -math.cos(math.radians(rotation))


def coordinate_rotation(x, y):
    return math.degrees(math.atan2(x, -y))


def distance(x, y):
    return math.sqrt(x ** 2 + y ** 2)


class Vector:
    def __init__(self, rotation, value):
        self.rotation = rotation
        self.value = value

    def __call__(self):
        x, y = rotation_coordinate(self.rotation)
        return x * self.value, y * self.value


class Vectors:
    def __init__(self):
        self.vectors = []

    def clear(self):
        self.vectors = []

    def add(self, vector):
        self.vectors.append(vector)

    def get_net_coordinates(self):
        x, y = 0, 0
        for vector in self.vectors:
            vx, vy = vector()
            x += vx
            y += vy
        return x, y

    def get_net_rotation(self):
        x, y = self.get_net_coordinates()
        return coordinate_rotation(x, y)

    def get_net_value(self):
        x, y = self.get_net_coordinates()
        return math.sqrt(x ** 2 + y ** 2)

    def get_net_vector(self, time=1.0):
        return Vector(self.get_net_rotation(), self.get_net_value() * time)

    def reset(self, time=1.0):
        v = self.get_net_vector(time)
        self.clear()
        self.add(v)
