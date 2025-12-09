import os


import pygame as pg
import item_html, entity_html, recipe_html, magic_html

pg.quit()
print(f"Done. Modules {item_html, recipe_html, entity_html, magic_html} updated.")

print('Removing old files from docs/assets')
path = os.path.dirname(os.path.dirname(__file__))
os.system(f'rm -rf {os.path.join(path, './docs/assets')}')
print('Copying assets to docs/assets')
os.system(f'cp -r {os.path.join(path, 'src/assets')} {os.path.join(path, './docs/assets')}')
print('Done.')
