from src import resources, visual
from src.underia import player
import os
import pygame

class Game:
    def __init__(self):
        self.displayer = visual.Displayer()
        self.graphics = resources.Graphics()
        self.events = []
        self.player = player.Player()
        self.pressed_keys = []
        self.monsters = []
        self.clock = resources.Clock()

    def load_graphics(self, directory, index=''):
        for file in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, file)):
                print('Loading', os.path.join(directory, file))
                if file.endswith(".png"):
                    self.graphics.load_graphics(index + file.removesuffix(".png"), os.path.join(directory, file))
            else:
                self.load_graphics(os.path.join(directory, file), index + file + '_')

    def setup(self):
        self.load_graphics(resources.get_path('assets/graphics'))

    def update(self):
        self.clock.update()
        self.events = pygame.event.get()
        for event in self.events:
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                else:
                    self.pressed_keys.append(event.key)
            elif event.type == pygame.KEYUP:
                if event.key in self.pressed_keys:
                    self.pressed_keys.remove(event.key)
        bg_size = 120
        bg_ax = self.player.ax % bg_size
        bg_ay = self.player.ay % bg_size
        for i in range(-bg_size, self.displayer.SCREEN_WIDTH + bg_size, bg_size):
            for j in range(-bg_size, self.displayer.SCREEN_HEIGHT + bg_size, bg_size):
                self.displayer.canvas.blit(self.graphics.get_graphics('background_grassland'), (i - bg_ax, j - bg_ay))
        self.player.update()
        for monster in self.monsters:
            monster.update()
        self.displayer.update()
        return True

    def get_keys(self):
        return [event.key for event in self.events if event.type == pygame.KEYDOWN]

    def get_pressed_keys(self):
        return self.pressed_keys

    def run(self):
        self.setup()
        while self.update():
            pass

GAME: Game | None = None

def write_game(game: Game):
    global GAME
    GAME = game

def get_game() -> Game:
    global GAME
    if GAME is None:
        raise ValueError("Game not initialized")
    return GAME
