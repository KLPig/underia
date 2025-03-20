import random
import time

from pygame import constants as pg

random.seed(time.time())


ELEMENT_TYPE_CONSTANT = 49034
DAMAGE_TYPE_CONSTANT = 13829

INFINITY = 2 ** 31 - 1

DEBUG = True
OS = "OSX"
TONE = True
ENTITY_NUMBER = 25
WEB_DEPLOY = False

if not WEB_DEPLOY:
    FLAGS = pg.HWSURFACE | pg.DOUBLEBUF | pg.SRCALPHA
    FULLSCREEN = False
else:
    FLAGS = 0
    FULLSCREEN = False
# Graphics
USE_ALPHA = True
EASY_BACKGROUND = False
BLADE_EFFECT_QUALITY = 1
PARTICLES = 1
DISPLAY_STYLE = 0
HEART_BAR = True
FADING_PARTICLE = True

FPS = 120

OS_NICE = -20

LIGHTING = False

MOVER_POS = 10 ** 7

ULTIMATE_AMMO_BONUS = 10000


DEBUG_SETTINGS = False
