from src import constants
from pygame import time as tm

fps = constants.FPS
spf = 1 / fps

def get_time(tick: int):
    return tick / fps

def tick_interval(tick: int, interval_tick: int, tick_target: int):
    return tick % interval_tick == tick_target

def time_interval(time: float, interval_time: float, time_target: float):
    res1 = time % interval_time
    res2 = (time + spf) % interval_time
    return res1 <= time_target < res2 or res2 <= res1


class Clock:
    def __init__(self):
        self.clock = tm.Clock()
        self.tick = 0
        self.time = 0

    def update(self):
        self.tick += 1
        self.time = self.tick * spf
        self.clock.tick(fps)

