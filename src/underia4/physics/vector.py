from . import coordinates as coor

class Vector:
    def __init__(self, x: float=0, y: float=0, r: float=0, theta: float=0):
        self.x = x
        self.y = y
        ax, ay = coor.pol2cart(r, theta)
        self.x += ax
        self.y += ay

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

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

    def __add__(self, other):
        return Vector(self.x + other[0], self.y + other[1])

    def __sub__(self, other):
        return Vector(self.x - other[0], self.y - other[1])

    def __mul__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x * other[0] + self.y * other[1], self.x * other[1] + self.y * other[0])
        else:
            return Vector(self.x * other, self.y * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x / other[0] + self.y / other[1], self.x / other[1] + self.y / other[0])
        else:
            return Vector(self.x / other, self.y / other)

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __abs__(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def __eq__(self, other):
        return self.x == other[0] and self.y == other[1]

    def __ne__(self, other):
        return not self.__eq__(other)

    def __bool__(self):
        return self.x != 0 or self.y != 0

    def __iter__(self):
        return iter((self.x, self.y))
    
    def __len__(self):
        return 2

    def __hash__(self):
        return hash((self.x, self.y))

    def __iadd__(self, other):
        self.x += other[0]
        self.y += other[1]
        return self

    def __isub__(self, other):
        self.x -= other[0]
        self.y -= other[1]
        return self

    def __imul__(self, other):
        if isinstance(other, Vector):
            self.x, self.y = self.x * other[0] + self.y * other[1], self.x * other[1] + self.y * other[0]
        else:
            self.x *= other
            self.y *= other
        return self

    def __itruediv__(self, other):
        if isinstance(other, Vector):
            self.x, self.y = self.x / other[0] + self.y / other[1], self.x / other[1] + self.y / other[0]
        else:
            self.x /= other
            self.y /= other
        return self

