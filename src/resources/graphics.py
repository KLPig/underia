import pygame as pg
from src.resources import path as pth

class Graphics:
    def __init__(self):
        self.graphics: dict[str, pg.Surface] = {}

    def load_graphics(self, index: str, path: str):
        self.graphics[index] = pg.image.load(pth.get_path(path)).convert_alpha()

    def get_graphics(self, index: str) -> pg.Surface:
        return self.graphics[index]

    def is_loaded(self, index: str) -> bool:
        return index in self.graphics.keys()

    def __getitem__(self, index: str) -> pg.Surface:
        return self.get_graphics(index)

    def __setitem__(self, index: str, value: pg.Surface):
        self.graphics[index] = value

    def __delitem__(self, index: str):
        del self.graphics[index]

    def __contains__(self, index: str) -> bool:
        return index in self.graphics
