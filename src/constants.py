import random
import time

random.seed(time.time())

ELEMENT_TYPE_CONSTANT = int(random.random() * 1000)
DAMAGE_TYPE_CONSTANT = int(random.random() * 1000)

INFINITY = 2 ** 31 - 1

FPS = 60