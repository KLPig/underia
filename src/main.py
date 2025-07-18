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
import resources, visual, physics, underia, mods, legend, constants, web
import values
from underia import good_words
import underia3
if not constants.WEB_DEPLOY:
    import saves_chooser, modloader

if os.path.exists(resources.get_save_path('settings.uset')):
    with open(resources.get_save_path('settings.uset'), 'rb') as f:
        constants.load_settings(pickle.load(f))

pg.init()
random.seed(time.time())
pg.display.set_mode((1600, 900), constants.FLAGS)
pg.display.set_caption(f'Underia - {random.choice(good_words.WORDS)}')
pg.display.set_icon(pg.image.load(resources.get_path('assets/graphics/entity/chicken.png')))

if not constants.WEB_DEPLOY:
    legend.show_legend()

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

    cmds, file = saves_chooser.choose_save()
else:
    cmds, file = '', None
    load_mods = []
    setups = []
    updates = []

if 'client' in cmds:
    addr = ''
    inp = True
    window = pg.display.get_surface()
    font = pg.font.Font(resources.get_path('assets/dtm-mono.otf' if constants.LANG != 'zh' else 'assets/fz-pixel.ttf'), 48)
    while inp:
        window.fill((0, 0, 0))
        tx = f'Server address: {addr}'
        txt = font.render(tx, True, (255, 255, 255))
        window.blit(txt, (200, 200))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_BACKSPACE:
                    addr = addr[:-1]
                elif '0' <= pg.key.name(event.key) <= '9' or event.key == pg.K_PERIOD:
                    addr += pg.key.name(event.key)
                elif event.key == pg.K_RETURN:
                    inp = False
                    break
        pg.display.flip()

else:
    addr = None

try:
    if file is not None and os.path.exists(resources.get_save_path(file)):
        game = pickle.load(open(resources.get_save_path(file), "rb"))
        game.chunk_pos = (0, 0)
        game.player.obj = underia.PlayerObject((0, 0))
        game.displayer = visual.Displayer()
        game.graphics = resources.Graphics()
        game.clock = resources.Clock()
        game.pressed_keys = []
        game.pressed_mouse = []
        game.drop_items = []
        game.last_biome = ('forest', 0)
        game.player.hp_sys.dmg_t = 0
        game.player.scale = 1.0
        try:
            game.player.talent
        except AttributeError:
            game.player.talent = 0
            game.player.max_talent = 0
        try:
            game.player.inspiration
        except AttributeError:
            game.player.inspiration = 0
            game.player.max_inspiration = 0
        try:
            game.player.good_karma
        except AttributeError:
            game.player.good_karma = 0
        try:
            game.player.profile
        except AttributeError:
            game.player.profile = underia.PlayerProfile()
        try:
            game.player.tutorial_step
        except AttributeError:
            game.player.tutorial_step = 0
        try:
            game.player.tutorial_process
        except AttributeError:
            game.player.tutorial_process = 0
        try:
            game.player.owned_items
        except AttributeError:
            game.player.owned_items = []
        try:
            game.player.profile.stage
        except AttributeError:
            game.player.profile.stage = 0
        try:
            game.player.splint_t
        except AttributeError:
            game.player.splint_t = 0
            game.player.splint_distance = 0
            game.player.splint_cd = 80
        try:
            game.chapter
        except AttributeError:
            game.chapter = 0
        try:
            game.seed
        except AttributeError:
            game.seed = random.randint(0, 1000000)
        try:
            game.player.ui_tasks
        except AttributeError:
            game.player.ui_tasks = False
            game.player.ui_attributes = False
        try:
            game.player.ui_recipes
        except AttributeError:
            game.player.ui_recipes = False
            game.player.ui_recipe_overlook = False
        try:
            game.hallow_points
        except AttributeError:
            game.hallow_points = []
        try:
            game.wither_points
        except AttributeError:
            game.wither_points = []
        try:
            game.player.profile.select_skill
        except AttributeError:
            game.player.profile.select_skill = []
        try:
            game.player.profile.point_left
        except AttributeError:
            game.player.profile.point_left = 0
        try:
            game.player.cd_z
        except AttributeError:
            game.player.cd_z = 0
            game.player.cd_x = 0
            game.player.cd_c = 0
        try:
            game.player.z
        except AttributeError:
            game.player.z = 0
        try:
            game.player.covered_items
        except AttributeError:
            game.player.covered_items = []
        try:
            game.game_time
        except AttributeError:
            game.game_time = 0
        try:
            game.player.afterimage_shadow
        except AttributeError:
            game.player.afterimage_shadow = 0
        while len(game.player.accessories) < 9:
            game.player.accessories.insert(0, 'null')
        while len(game.player.accessories) < 10:
            game.player.accessories.append('null')
        game.player.boot_footprints = []
        game.player.t_ntc_timer = 200
        game.player.tick = 0
    else:
        game = underia.Game()
except Exception as e:
    raise e

pg.display.set_caption('Underia')
game.save = file
if constants.WEB_DEPLOY:
    sfd = ''
else:
    sfd = game.save.replace('.pkl', '.data.pkl')
print('Writing game...')
underia.write_game(game)
print('Setup game...')
game.setup()
if not game.player.profile.stage:
    game.player.profile.add_point(0)
pg.display.get_surface().fill((100, 100, 100))
for m in load_mods:
    game.gcnt = 0
    game.load_graphics(os.path.join(mod_dir, m, 'assets/assets/graphics'),
                       cnt=game.cnt_graphics(os.path.join(mod_dir, m, 'assets/assets/graphics')))
game.map = pg.PixelArray(game.graphics['background_map'])
underia.set_weapons()
game.player.weapons = 4 * [underia.WEAPONS['null']]
game.player.sel_weapon = 1
game.player.inventory.sort()
game.player.inventory.items['recipe_book'] = 1
game.player.inventory.items['arrow_thrower'] = 1
game.player.hp_sys(op='config', immune_time=10, true_drop_speed_max_value=1, immune=False)
game.player.hp_sys.shields = []

game.player.profile.point_melee = 0
game.player.profile.point_ranged = 0
game.player.profile.point_magic = 0
print('Presets...')

game.world_events.clear()

if constants.APRIL_FOOL:
    for item in underia.ITEMS.values():
        for __ in range(5):
            mat = {}
            for _ in range(item.rarity + 1):
                mat[f'magic_shard_{random.randint(0, 127)}'] = 1
            underia.RECIPES.append(underia.Recipe(mat, item.id))
        underia.RECIPES.append(underia.Recipe({item.id: 1}, f'magic_shard_{random.randint(0, 127)}', item.rarity))

    for i in range(128):
        it_s = pg.Surface((5, 5))
        r = random.randint(0, 240)
        g = random.randint(max(0, 105 - r), min(360 - r, 255))
        b = 360 - r - g
        for x, y in [(1, 1), (1, 2), (2, 2), (2, 3), (3, 1), (3, 2)]:
            it_s.set_at((x, y), (r, g, b))
        game.graphics['items_magic_shard_' + str(i)] = it_s
        underia.ITEMS['magic_shard_' + str(i)] = underia.Inventory.Item(f'Magic Shard(#{i})',
                                                                         'Magic Shard #' + str(i), 'magic_shard_' + str(i),
                                                                        12, [underia.TAGS['item']])
        underia.RECIPES.append(underia.Recipe({'magic_shard_' + str(i): 2}, 'magic_shard_' + str((i + 1) % 128)))

for s in setups:
    exec(s)

fpss = []

@game.update_function
def update():
    if addr is not None:
        return
    fpss.append(round(1000 / game.clock.last_tick, 2))
    if game.player.inventory.is_enough(underia.ITEMS['star']):
        game.player.inventory.remove_item(underia.ITEMS['star'])
        game.player.mana = max(game.player.mana, min(game.player.max_mana, game.player.mana + 40))
    for u in updates:
        exec(u)
    bm = 'blood moon' in game.world_events
    if game.chapter == 1:
        if len(game.hallow_points) > 5:
            game.hallow_points.pop(0)
        if len(game.wither_points) > 5:
            game.wither_points.pop(0)
        f = 0
        for pp, r in game.hallow_points:
            if physics.distance(pp[0] - game.player.obj.pos[0], pp[1] - game.player.obj.pos[1]) < r * 7.5:
                f = 1
        if not f:
            td = (2.25 + random.random() * 0.5) * 2500
            ax, ay = physics.rotation_coordinate(random.randint(0, 360))
            game.hallow_points.append(((game.player.obj.pos[0] + ax * td,
                                        game.player.obj.pos[1] + ay * td), random.randint( 1600, 2000)))
        f = 0
        for pp, r in game.wither_points:
            if physics.distance(pp[0] - game.player.obj.pos[0], pp[1] - game.player.obj.pos[1]) < r * 7.5:
                f = 1
        if not f:
            td = (2.25 + random.random() * 0.5) * 2500
            ax, ay = physics.rotation_coordinate(random.randint(0, 360))
            game.wither_points.append(((game.player.obj.pos[0] + ax * td,
                                        game.player.obj.pos[1] + ay * td), random.randint(1600, 2000)))
    for entity in game.entities:
        d = physics.distance(entity.obj.pos[0] - game.player.obj.pos[0], entity.obj.pos[1] - game.player.obj.pos[1])
        if d > 8000 + (entity.VITAL or entity.IS_MENACE) * 8000 or (d > 1200 + (entity.IS_MENACE or entity.VITAL) * 1200 and
                                                  not entity.is_suitable(game.get_biome())):
            game.entities.remove(entity)
            del entity
    for entity in game.drop_items:
        d = physics.distance(entity.obj.pos[0] - game.player.obj.pos[0], entity.obj.pos[1] - game.player.obj.pos[1])
        if d > 2000 + entity.rarity * 1000:
            game.drop_items.remove(entity)
            del entity
    if game.chapter <= 1:
        if game.get_biome() == 'forest':
            if 5 > game.stage > 1:
                underia.entity_spawn(underia.Entities.Tree, target_number=20, to_player_max=2500, to_player_min=800, rate=25)
                underia.entity_spawn(underia.Entities.TreeMonster, target_number=15, to_player_max=2500, to_player_min=800,
                                     rate=25)
                underia.entity_spawn(underia.Entities.LifeTree, target_number=32, to_player_max=2500, to_player_min=2000,
                                     rate=15)
            else:
                underia.entity_spawn(underia.Entities.Tree, target_number=40, to_player_max=2500, to_player_min=800, rate=50)
                underia.entity_spawn(underia.Entities.TreeMonster, target_number=20, to_player_max=2500, to_player_min=800,
                                     rate=50)
            underia.entity_spawn(underia.Entities.ClosedBloodflower, target_number=30, to_player_max=2500,
                                 to_player_min=800, rate=35)
            if 5 > game.stage > 0:
                underia.entity_spawn(underia.Entities.SoulFlower, target_number=30 + bm * 16, to_player_max=2500, to_player_min=800,
                                     rate=50)
            underia.entity_spawn(underia.Entities.GreenChest, target_number=1, to_player_max=2500, to_player_min=1000,
                                 rate=50, number_factor=4)
        elif game.get_biome() == 'rainforest':
            if 5 > game.stage > 1:
                underia.entity_spawn(underia.Entities.Tree, target_number=5, to_player_max=2500, to_player_min=1000, rate=2.5)
                underia.entity_spawn(underia.Entities.HugeTree, target_number=20, to_player_max=2500, to_player_min=1000,
                                     rate=30)
                underia.entity_spawn(underia.Entities.TreeMonster, target_number=15, to_player_max=2500, to_player_min=1000,
                                     rate=25)
                underia.entity_spawn(underia.Entities.LifeTree, target_number=25, to_player_max=2500, to_player_min=2500,
                                     rate=15)
            else:
                underia.entity_spawn(underia.Entities.Tree, target_number=10, to_player_max=2500, to_player_min=1000, rate=50)
                underia.entity_spawn(underia.Entities.HugeTree, target_number=40, to_player_max=2500, to_player_min=1000,
                                     rate=45)
                underia.entity_spawn(underia.Entities.TreeMonster, target_number=20, to_player_max=2500, to_player_min=1000,
                                     rate=15)
            underia.entity_spawn(underia.Entities.ClosedBloodflower, target_number=25, to_player_max=2500,
                                 to_player_min=800, rate=40)
            if 5 != game.stage > 0:
                if game.stage < 5:
                    underia.entity_spawn(underia.Entities.SoulFlower, target_number=25 + bm * 20, to_player_max=2500, to_player_min=800,
                                         rate=15)
                underia.entity_spawn(underia.Entities.Leaf, target_number=50, to_player_max=2500, to_player_min=1000,
                                     rate=55)
            underia.entity_spawn(underia.Entities.GreenChest, target_number=1, to_player_max=2500, to_player_min=1000,
                                 rate=50, number_factor=3.5)
        elif game.get_biome() == 'life_forest':
            pass
        elif game.get_biome() == 'desert':
            underia.entity_spawn(underia.Entities.Cactus, target_number=25, to_player_max=2500, to_player_min=1000, rate=5)
            if game.player.hp_sys.max_hp >= 500:
                underia.entity_spawn(underia.Entities.RuneRock, target_number=10, to_player_max=2000, to_player_min=1000,
                                     rate=30)
            underia.entity_spawn(underia.Entities.OrangeChest, target_number=1, to_player_max=2500, to_player_min=1000,
                                 rate=50, number_factor=3.5)
            if 5 > game.stage > 2:
                underia.entity_spawn(underia.Entities.AncientDebris, target_number=5, to_player_max=2000, to_player_min=1000,
                                     rate=1.3)
        elif game.get_biome() == 'hallow':
            underia.entity_spawn(underia.Entities.UniSaur, target_number=15, to_player_max=2500, to_player_min=1000, rate=5)
            underia.entity_spawn(underia.Entities.LightFly, target_number=24, to_player_max=2500, to_player_min=1000, rate=4)
            underia.entity_spawn(underia.Entities.GreenChest, target_number=1, to_player_max=2500, to_player_min=2000,
                                 rate=50, number_factor=3.5)
        elif game.get_biome() == 'wither':
            underia.entity_spawn(underia.Entities.RedCorruption, target_number=30, to_player_max=2500, to_player_min=1000, rate=4.5)
            underia.entity_spawn(underia.Entities.PurpleCorruption, target_number=30, to_player_max=2500, to_player_min=1000, rate=4.5)
            underia.entity_spawn(underia.Entities.GreenChest, target_number=1, to_player_max=2500, to_player_min=2000,
                                 rate=50, number_factor=3.5)
        elif game.get_biome() == 'hell':
            underia.entity_spawn(underia.Entities.MagmaCube, target_number=15, to_player_max=2000, to_player_min=1000,
                                 rate=10)
            underia.entity_spawn(underia.Entities.RedChest, target_number=1, to_player_max=2500, to_player_min=1000,
                                 rate=50, number_factor=4.5)
            if 5 > game.stage > 3:
                underia.entity_spawn(underia.Entities.ScarlettPillar, target_number=12, to_player_max=2500, to_player_min=2000,
                                     rate=50)
        elif game.get_biome() == 'heaven':
            underia.entity_spawn(underia.Entities.HeavenGuard, target_number=9 + bm * 24, to_player_max=2000, to_player_min=1000,
                                 rate=2 + bm * 2)
            if 5 != game.stage > 0:
                underia.entity_spawn(underia.Entities.Cells, target_number=15, to_player_max=2000, to_player_min=1500,
                                     rate=8)
            underia.entity_spawn(underia.Entities.BlueChest, target_number=1, to_player_max=2500, to_player_min=1000,
                                 rate=50, number_factor=4.5)
            if 5 > game.stage > 3:
                underia.entity_spawn(underia.Entities.HolyPillar, target_number=12, to_player_max=2500, to_player_min=2000,
                                     rate=50)
        elif game.get_biome() == 'snowland':
            underia.entity_spawn(underia.Entities.ConiferousTree, target_number=25, to_player_max=2500, to_player_min=1000, rate=5)
            underia.entity_spawn(underia.Entities.FluffBall, target_number=15, to_player_max=2500, to_player_min=1000, rate=.8)
            if 5 != game.stage > 0:
                underia.entity_spawn(underia.Entities.SnowDrake, target_number=12, to_player_max=2500, to_player_min=1000,
                                     rate=12)
                underia.entity_spawn(underia.Entities.IceCap, target_number=15, to_player_max=2500, to_player_min=1000,
                                     rate=20)
            if 5 > game.stage > 1:
                underia.entity_spawn(underia.Entities.IceThorn, target_number=18, to_player_max=2500, to_player_min=1000,
                                     rate=10)
            if 5 > game.stage > 2:
                underia.entity_spawn(underia.Entities.CurseGhost, target_number=3, to_player_max=2000, to_player_min=1000,
                                     rate=30)
            if game.stage > 5:
                underia.entity_spawn(underia.Entities.PolarSnowman, target_number=3, to_player_max=2000, to_player_min=1000,
                                     rate=30)
            underia.entity_spawn(underia.Entities.WhiteChest, target_number=1, to_player_max=2500, to_player_min=1000,
                                 rate=50, number_factor=3.5)
        underia.entity_spawn(underia.Entities.SwordInTheStone, target_number=1, to_player_max=2500, to_player_min=2000,
                             rate=50)
        underia.entity_spawn(underia.Entities.StoneAltar, target_number=3, to_player_max=2500, to_player_min=2000,
                             rate=50)
        underia.entity_spawn(underia.Entities.RawOre, target_number=30, to_player_max=3000, to_player_min=1000,
                             rate=15)
        if 5 > game.stage > 0:
            underia.entity_spawn(underia.Entities.MetalAltar, target_number=3, to_player_max=2500, to_player_min=2000,
                                 rate=50, number_factor=3)
        if game.stage > 5:
            underia.entity_spawn(underia.Entities.ScarlettAltar, target_number=3, to_player_max=2500, to_player_min=2000,
                                 rate=50, number_factor=3)
        if game.get_biome() not in ['inner']:
            if 5 > game.stage > 0:
                underia.entity_spawn(underia.Entities.EvilMark, target_number=3, to_player_max=2500, to_player_min=2000,
                                     rate=50, number_factor=1.9)
            if game.day_time > 0.75 or game.day_time < 0.2:
                underia.entity_spawn(underia.Entities.Eye, target_number=18 + bm * 12, to_player_max=2000, to_player_min=1500,
                                     rate=20 + bm * 30)
                underia.entity_spawn(underia.Entities.Bloodflower, target_number=12 + bm * 24, to_player_max=2000, to_player_min=1500,
                                     rate=25 + bm * 20)
                underia.entity_spawn(underia.Entities.RedWatcher, target_number=15 + bm * 17, to_player_max=2000, to_player_min=1800,
                                     rate=10 + bm * 20)

                if game.stage == 1:
                    underia.entity_spawn(underia.Entities.MechanicEye, target_number=12 + bm * 18, to_player_max=3000, to_player_min=1500,
                                         rate=50 + bm * 20)

                    underia.entity_spawn(underia.Entities.Destroyer, target_number=1, to_player_max=3500, to_player_min=1000,
                                         rate=0.001 + bm * 0.006, number_factor=0)
                    underia.entity_spawn(underia.Entities.TheCPU, target_number=1, to_player_max=3500, to_player_min=1000,
                                         rate=0.001 + bm * 0.006, number_factor=0)
                    underia.entity_spawn(underia.Entities.TruthlessEye, target_number=1, to_player_max=3500, to_player_min=1000,
                                         rate=0.0005 + bm * 0.003, number_factor=0)
                    underia.entity_spawn(underia.Entities.FaithlessEye, target_number=1, to_player_max=3500, to_player_min=1000,
                                         rate=0.0005 + bm * 0.003, number_factor=0)
                elif game.stage == 0:
                    underia.entity_spawn(underia.Entities.TrueEye, target_number=1, to_player_max=3500, to_player_min=1000,
                                         rate=0.0008 + bm * 0.002, number_factor=0)
            underia.entity_spawn(underia.Entities.Star, target_number=12 + bm * 10, to_player_max=2000, to_player_min=1500, rate=30)
        elif game.get_biome() == 'inner':
            underia.entity_spawn(underia.Entities.PlanteraBulb, target_number=5, to_player_max=2500, to_player_min=1000, rate=50)
            if 5 > game.stage > 2:
                underia.entity_spawn(underia.Entities.GhostFace, target_number=5, to_player_max=2500, to_player_min=2000, rate=23)
                underia.entity_spawn(underia.Entities.SadFace, target_number=5, to_player_max=2500, to_player_min=2000, rate=23)
                underia.entity_spawn(underia.Entities.AngryFace, target_number=5, to_player_max=2500, to_player_min=2000, rate=23)
                underia.entity_spawn(underia.Entities.TimeTrap, target_number=5, to_player_max=2500, to_player_min=2000, rate=24)
                underia.entity_spawn(underia.Entities.TimeFlower, target_number=5, to_player_max=2500, to_player_min=2000, rate=24)
                underia.entity_spawn(underia.Entities.Molecules, target_number=5, to_player_max=2500, to_player_min=2000, rate=24)
                underia.entity_spawn(underia.Entities.TitaniumIngot, target_number=5, to_player_max=2500, to_player_min=2000, rate=24)
                underia.entity_spawn(underia.Entities.Spark, target_number=5, to_player_max=2500, to_player_min=2000, rate=24)
                underia.entity_spawn(underia.Entities.Holyfire, target_number=5, to_player_max=2500, to_player_min=2000, rate=24)
            if 5 > game.stage > 3:
                underia.entity_spawn(underia.Entities.HolyPillar, target_number=12, to_player_max=3000, to_player_min=1000,
                                     rate=50,)
                underia.entity_spawn(underia.Entities.ScarlettPillar, target_number=12, to_player_max=3000, to_player_min=1000,
                                     rate=50)
    elif game.chapter == 2:
        if game.get_biome().endswith('forest'):
            if not game.player.calculate_data('tree_curse', rate_data=False):
                game.player.hp_sys.effect(values.CurseTree(5, 5))
        elif game.get_biome() == 'desert':
            game.player.hp_sys.effect(values.CurseSand(5, 5))
        elif game.get_biome() == 'snowland':
            if not game.player.calculate_data('snow_curse', rate_data=False):
                game.player.hp_sys.effect(values.CurseSnow(5, 5))
        elif game.get_biome() == 'hell':
            game.player.hp_sys.effect(values.CurseHell(5, 5))
        elif game.get_biome() == 'heaven':
            game.player.hp_sys.effect(values.CurseHeaven(5, 5))

        biome = game.get_biome()
        night = game.day_time > 0.75 or game.day_time < 0.2

        underia.entity_spawn(underia3.Chicken, 3000, 5000, target_number=12 - night * 5, rate=4)
        underia.entity_spawn(underia3.ManaChicken, 3000, 5000, target_number=1 + night * 3, rate=2)

        underia.entity_spawn(underia3.RuneAltar, 3000, 5000, target_number=1, rate=.1)
        if night:
            underia.entity_spawn(underia3.PurpleClayPot, 3200, 5000, target_number=18, rate=.1)
        if biome == 'forest':
            underia.entity_spawn(underia3.Tree, 1000, 2000, target_number=25, rate=6)
        elif biome == 'rainforest':
            underia.entity_spawn(underia3.Lychee, 1500, 4500, target_number=8, rate=6)
            underia.entity_spawn(underia3.Tree, 1000, 2000, target_number=28, rate=6)
        elif biome == 'desert':
            underia.entity_spawn(underia3.DeadTree, 1000, 2000, target_number=18, rate=6)
            underia.entity_spawn(underia3.BonecaAmbalabu, 2000, 4000, target_number=17, rate=2)
            underia.entity_spawn(underia3.LaVacaSaturnoSaturnita, 2000, 4000, target_number=3, rate=.02 * night)
        elif biome == 'snowland':
            underia.entity_spawn(underia3.PoisonCentipede, 2000, 2500, target_number=2, rate=3)
            underia.entity_spawn(underia3.PoisonChicken, 1000, 4000, target_number=4, rate=8)
            underia.entity_spawn(underia3.PoiseWalker, 3000, 4000, target_number=1, rate=.01 * night)
        elif biome == 'heaven':
            underia.entity_spawn(underia3.HGoblinFighter, 1000, 2000, target_number=8, rate=6)
            underia.entity_spawn(underia3.HGoblinRanger, 3000, 5000, target_number=15, rate=6)
            underia.entity_spawn(underia3.HGoblinThief, 2000, 4000, target_number=5, rate=6)

if addr is not None:
    game.client = web.Client(addr, 1145)
    print('Connected: ', addr, game.client)
    t, start_data = pickle.loads(game.client.recv())
    game.seed = start_data.seed
    game.hallow_points = start_data.hallow
    game.wither_points = start_data.wither
    game.player.profile.load(start_data.profile)
    r = random.randint(0, 240)
    g = random.randint(max(0, 105 - r), min(360 - r, 255))
    b = 360 - r - g
    game.client.player_id = start_data.pid


if constants.WEB_DEPLOY:
    import asyncio
    async def run():
        while True:
            game.update()
            await asyncio.sleep(0)
    asyncio.run(run())
else:
    start_time = datetime.datetime.now()
    try:
        print('Running game...')
        asyncio.run(game.run())
    except Exception as err:
        def try_delete_attribute(obj, attr):
            try:
                delattr(obj, attr)
            except AttributeError:
                print(f"Attribute {attr} not found in object {obj}")
        with open(resources.get_save_path('settings.uset'), 'wb') as f:
            f.write(pickle.dumps(constants.dump_settings()))
        end_time = datetime.datetime.now()
        game.game_time += (end_time - start_time).total_seconds()
        if not constants.WEB_DEPLOY:
            try_delete_attribute(game, "displayer")
            try_delete_attribute(game, "graphics")
            try_delete_attribute(game, "clock")
            try_delete_attribute(game, "on_update")
            try_delete_attribute(game, "drop_items")
            try_delete_attribute(game, "map")
            try_delete_attribute(game, "musics")
            try_delete_attribute(game, "channel")
            try_delete_attribute(game, 'sounds')
            try_delete_attribute(game, 'dialog')
            try_delete_attribute(game, 'bl_bg')
            try_delete_attribute(game.player.profile, 'font')
            try_delete_attribute(game.player.profile, 'font_s')
            try_delete_attribute(game.player.profile, 'dialogger')
            game.events = []
            game.projectiles = []
            game.entities = []
            for w in game.player.weapons:
                game.player.inventory.add_item(underia.ITEMS[w.name.replace(" ", "_")])
            game.player.weapons = []
            del game.server
            del game.client
            game_pickle = pickle.dumps(game)
            with open(resources.get_save_path(game.save), 'wb') as w:
                w.write(game_pickle)
                w.close()
            game_data_pickle = pickle.dumps(underia.GameData(game.player.profile))
            with open(resources.get_save_path(game.save.replace('.pkl', '.data.pkl')), 'wb') as w:
                w.write(game_data_pickle)
                w.close()
            print(f"Game saved to {resources.get_save_path(game.save)}")

        raise err