import pygame as pg

from src.resources import path as pth
from src.resources import strings

noticed = []


class Graphics:
    def __init__(self):
        self.graphics: dict[str, pg.Surface] = {}

    def load_graphics(self, index: str, path: str):
        self.graphics[index] = pg.image.load(pth.get_path(path)).convert_alpha()

    def get_graphics(self, index: str) -> pg.Surface:
        global noticed
        try:
            return self.graphics[index]
        except KeyError:
            if index not in noticed:
                noticed.append(index)
                mean_str = 'no matched graphics found'
                for key in self.graphics.keys():
                    if strings.similarity(key, index) >= strings.similarity(mean_str, index):
                        mean_str = key
                print(f"Graphics with index {index} is not loaded, do you mean {mean_str}?")
            return self.graphics['items_invalid']

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
