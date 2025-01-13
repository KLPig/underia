import pygame as pg

import underia

pg.init()
pg.display.set_mode((1, 1))

recipes = underia.RECIPES
img = pg.display.set_mode((800, 80 * len(recipes)))
game = underia.Game()
underia.write_game(game)
game.setup()

img.fill((255, 255, 255))

for i, recipe in enumerate(recipes):
    underia.item_display(0, i * 80, recipe.result, str(i + 1), str(recipe.crafted_amount), 1, _window=img)
    j = 0
    for item, amount in recipe.material.items():
        underia.item_display(160 + j * 80, i * 80, item, '', str(amount), 1, _window=img)
        j += 1

pg.display.flip()

pg.image.save(img, "recipes.png")
