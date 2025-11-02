import pygame as pg

import underia

img = pg.Surface((2000, 1500))

game = underia.Game()
underia.write_game(game)

YCOLS = {'hell': (255, 0, 0), 'desert': (255, 191, 63), 'forest': (0, 255, 0), 'rainforest': (127, 255, 0),
                'snowland': (255, 255, 255), 'heaven': (127, 127, 255), 'inner': (0, 0, 0), 'none': (0, 0, 0),
                'hallow': (0, 255, 255), 'wither': (50, 0, 0), 'life_forest': (50, 127, 0), 'ancient': (50, 0, 0),
                'ancient_city': (255, 200, 128), 'ancient_wall': (100, 50, 0), 'ocean': (0, 0, 255),
                'fallen_sea': (0, 100, 255), 'hot_spring': (50, 0, 0)}
game.setup()
game.stage = 1

for x in range(2000):
    if x % 10 == 0:
        print('\rDone', x // 20, '%', end='')
    for y in range(1500):
        tx = x * 5 + 120 - 5000
        ty = y * 5 + 120 - 3000
        col = YCOLS[game.get_biome((tx, ty))]
        img.set_at((x, y), col)

pg.image.save(img, "map.png")
