import math

def cart2pol(x, y):
    r = math.sqrt(x**2 + y**2)
    theta = math.atan2(y, x)
    return r, theta

def pol2cart(r, theta):
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    return x, y