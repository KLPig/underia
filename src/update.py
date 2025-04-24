import os

import pygame as pg

import assets.graphics.items.convert_weapon as convert_weapon

os.chdir('src')

import item_html, recipe_html, entity_html, magic_html

pg.quit()
print(f"Done. Modules {convert_weapon, item_html, recipe_html, entity_html, magic_html} updated.")

print('Removing old files from docs/assets')
path = os.path.dirname(__file__)
os.system(f'rm -rf {os.path.join(path, './docs/assets')}')
print('Copying assets to docs/assets')
os.system(f'cp -r {os.path.join(path, 'src/assets')} {os.path.join(path, './docs/assets')}')
print('Done.')
