# Underia
# Copyright (c) KLpig 2025, under the BSD 2-Clause License
# For more information, see ./LICENSE
import os
import pickle
import pygame as pg 
import random
import time
import datetime
import asyncio
import resources, underia, mods, constants
from underia import good_words
import underia3
import modloader
import packs
from resources import log

pg.init()
random.seed(time.time())
pg.display.set_mode((1600, 900), constants.FLAGS)
pg.display.set_caption(f'Underia - {random.choice(good_words.WORDS)}')
pg.display.set_icon(pg.image.load(resources.get_path('assets/graphics/entity/chicken.png')))

tt_dmg = []

_, load_mods = modloader.load_mod()
updates = []
setups = []

mod_dir = resources.get_save_path('mods')

for m in load_mods:
    info: mods.UnderiaModData = pickle.load(open(os.path.join(mod_dir, m, 'data.umod'), "rb"))
    data: mods.UnderiaMod = pickle.load(open(os.path.join(mod_dir, m, 'mod.umod'), "rb"))
    for item in data.items.values():
        item.mod = info.name
        underia.ITEMS[item.id] = item
    for recipe in data.recipes:
        underia.RECIPES.append(recipe)
    if data.setup_func is not None:
        setups.append(data.setup_func)
    if data.update_func is not None:
        updates.append(data.update_func)

pg.display.get_surface().fill((0, 0, 0))
underia.inventory.setup()

game = underia.Game()
game.seed = 0

pg.display.set_caption('Underia')
game.save = 'none.sb'''
if constants.WEB_DEPLOY:
    sfd = ''
else:
    sfd = game.save.replace('.pkl', '.data.pkl')
underia.write_game(game)
game.setup()
pg.display.get_surface().fill((100, 100, 100))
for m in load_mods:
    game.gcnt = 0
    game.load_graphics(os.path.join(mod_dir, m, 'assets/assets/graphics'),
                       cnt=game.cnt_graphics(os.path.join(mod_dir, m, 'assets/assets/graphics')))
game.map = pg.PixelArray(game.graphics['background_map'])
underia.set_weapons()
game.player.weapons = 7 * [underia.WEAPONS['null']]
game.player.sel_weapon = 1

game.world_events.clear()

game.entities.append(underia.Entities.Entity((100, 0)))
game.player.hp_sys.max_hp = constants.INFINITY
game.player.hp_sys.hp = constants.INFINITY
game.player.max_mana = constants.INFINITY
game.player.mana = constants.INFINITY
game.player.inspiration = constants.INFINITY
game.player.max_inspiration = constants.INFINITY
game.player.talent = constants.INFINITY
game.player.max_talent = constants.INFINITY

for s in setups: 
    exec(s)

fpss = []
game.player.inventory.items = {'_developer_tool__sight': 1, '_developer_tool__speed': 1}
game.player.tutorial_step = 1000
op = True

@game.update_function
def update():
    global op
    tt_dmg.append(game.c_dmg)
    if len(tt_dmg) > 1000:
        tt_dmg.pop(0)
    if pg.K_p in game.get_keys():
        op = not op

    if op:
        game.dialog.curr_text = str(round(sum(tt_dmg) * 1000 / len(tt_dmg) / game.clock.last_tick, 1)) + 'DPS'
        game.dialog.curr_idx = len(game.dialog.curr_text)

    fpss.append(round(1000 / game.clock.last_tick, 2))
    for u in updates:
        exec(u)


start_time = datetime.datetime.now()
try:
    log.info('Running game...')
    asyncio.run(game.run())
except Exception as err:
    raise err