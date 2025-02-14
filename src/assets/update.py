import os

import pygame as pg

os.chdir("src/assets/graphics/items")
import src.assets.graphics.items.convert_weapon as convert_weapon

os.chdir("../../..")
import src.item_html as item_html
import src.recipe_html as recipe_html
import src.entity_html as entity_html
import src.magic_html as magic_html

pg.quit()
print(f"Done. Modules {convert_weapon, item_html, recipe_html, entity_html, magic_html} updated.")

print('Removing old files from docs/assets')
path = os.path.dirname(__file__)
os.system(f'rm -rf {os.path.join(path, './docs/assets')}')
print('Copying assets to docs/assets')
os.system(f'cp -r {os.path.join(path, 'src/assets')} {os.path.join(path, './docs/assets')}')
print('Done.')
