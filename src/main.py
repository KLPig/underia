import os
import pickle
import pygame as pg
import random
import time

from src import resources, visual, physics, saves_chooser, modloader, underia, mods, legend, constants
from src.underia import good_words

pg.init()
random.seed(time.time())
pg.display.set_mode((1600, 900), constants.FLAGS)
pg.display.set_caption(f'Underia - {random.choice(good_words.WORDS)}')
pg.display.set_icon(pg.image.load(resources.get_path('assets/graphics/items/the_final_ingot.png')))

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

_, file = saves_chooser.choose_save()
try:
    if os.path.exists(resources.get_save_path(file)):
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
        game.player.t_ntc_timer = 200
    else:
        game = underia.Game()
except Exception as e:
    raise e

pg.display.set_caption('Underia')
game.save = file
sfd = game.save.replace('.pkl', '.data.pkl')
underia.write_game(game)

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
game.player.sel_weapon = 0
game.player.inventory.sort()
game.player.inventory.items['recipe_book'] = 1
game.player.inventory.items['arrow_thrower'] = 1
game.player.hp_sys(op='config', immune_time=10, true_drop_speed_max_value=1, immune=False)
game.player.hp_sys.shields = []

for s in setups:
    exec(s)

@game.update_function
def update():
    for u in updates:
        exec(u)
    bm = 'blood moon' in game.world_events
    for entity in game.entities:
        d = physics.distance(entity.obj.pos[0] - game.player.obj.pos[0], entity.obj.pos[1] - game.player.obj.pos[1])
        if d > 8000 + entity.IS_MENACE * 8000 or (d > 1200 + (entity.IS_MENACE or entity.VITAL) * 1200 and
                                                  not entity.is_suitable(game.get_biome())):
            game.entities.remove(entity)
            del entity
    for entity in game.drop_items:
        d = physics.distance(entity.obj.pos[0] - game.player.obj.pos[0], entity.obj.pos[1] - game.player.obj.pos[1])
        if d > 2000:
            game.drop_items.remove(entity)
            del entity
    if game.get_biome() == 'forest':
        underia.entity_spawn(underia.Entities.Tree, target_number=40, to_player_max=5000, to_player_min=800, rate=5)
        underia.entity_spawn(underia.Entities.TreeMonster, target_number=10, to_player_max=5000, to_player_min=800,
                             rate=5)
        underia.entity_spawn(underia.Entities.ClosedBloodflower, target_number=22, to_player_max=5000,
                             to_player_min=800, rate=1)
        if 6 > game.stage > 0:
            underia.entity_spawn(underia.Entities.SoulFlower, target_number=42 + bm * 36, to_player_max=5000, to_player_min=800,
                                 rate=1)
        underia.entity_spawn(underia.Entities.GreenChest, target_number=1, to_player_max=5000, to_player_min=4000,
                             rate=50, number_factor=4)
    elif game.get_biome() == 'rainforest':
        underia.entity_spawn(underia.Entities.Tree, target_number=10, to_player_max=5000, to_player_min=1000, rate=5)
        underia.entity_spawn(underia.Entities.HugeTree, target_number=40, to_player_max=5000, to_player_min=1000,
                             rate=1)
        underia.entity_spawn(underia.Entities.TreeMonster, target_number=10, to_player_max=5000, to_player_min=1000,
                             rate=5)
        underia.entity_spawn(underia.Entities.ClosedBloodflower, target_number=35, to_player_max=5000,
                             to_player_min=800, rate=1)
        if 6 != game.stage > 0:
            if game.stage < 6:
                underia.entity_spawn(underia.Entities.SoulFlower, target_number=45 + bm * 40, to_player_max=5000, to_player_min=800,
                                     rate=1)
            underia.entity_spawn(underia.Entities.Leaf, target_number=50, to_player_max=5000, to_player_min=1000,
                                 rate=2)
        underia.entity_spawn(underia.Entities.GreenChest, target_number=1, to_player_max=5000, to_player_min=4000,
                             rate=50, number_factor=3.5)
    elif game.get_biome() == 'desert':
        underia.entity_spawn(underia.Entities.Cactus, target_number=15, to_player_max=5000, to_player_min=1000, rate=5)
        if game.player.hp_sys.max_hp >= 500:
            underia.entity_spawn(underia.Entities.RuneRock, target_number=12, to_player_max=2000, to_player_min=1000,
                                 rate=0.8)
        underia.entity_spawn(underia.Entities.OrangeChest, target_number=1, to_player_max=5000, to_player_min=4000,
                             rate=50, number_factor=3.5)
    elif game.get_biome() == 'hell':
        underia.entity_spawn(underia.Entities.MagmaCube, target_number=12, to_player_max=2000, to_player_min=1000,
                             rate=0.8)
        underia.entity_spawn(underia.Entities.RedChest, target_number=1, to_player_max=5000, to_player_min=4000,
                             rate=50, number_factor=4.5)
        if 6 > game.stage > 3:
            underia.entity_spawn(underia.Entities.ScarlettPillar, target_number=2, to_player_max=5000, to_player_min=4000,
                                 rate=50, number_factor=1.9)
    elif game.get_biome() == 'heaven':
        underia.entity_spawn(underia.Entities.HeavenGuard, target_number=7 + bm * 12, to_player_max=2000, to_player_min=1000,
                             rate=0.4 + bm * 2)
        if 6 != game.stage > 0:
            underia.entity_spawn(underia.Entities.Cells, target_number=6, to_player_max=2000, to_player_min=1500,
                                 rate=0.8)
        underia.entity_spawn(underia.Entities.BlueChest, target_number=1, to_player_max=5000, to_player_min=4000,
                             rate=50, number_factor=4.5)
        if 6 > game.stage > 3:
            underia.entity_spawn(underia.Entities.HolyPillar, target_number=2, to_player_max=5000, to_player_min=4000,
                                 rate=50, number_factor=1.9)
    elif game.get_biome() == 'snowland':
        underia.entity_spawn(underia.Entities.ConiferousTree, target_number=15, to_player_max=5000, to_player_min=1000, rate=5)
        underia.entity_spawn(underia.Entities.FluffBall, target_number=5, to_player_max=5000, to_player_min=1000, rate=.8)
        if 6 != game.stage > 0:
            underia.entity_spawn(underia.Entities.SnowDrake, target_number=12, to_player_max=5000, to_player_min=1000,
                                 rate=.9)
            underia.entity_spawn(underia.Entities.IceCap, target_number=15, to_player_max=5000, to_player_min=1000,
                                 rate=.2)
        underia.entity_spawn(underia.Entities.WhiteChest, target_number=1, to_player_max=5000, to_player_min=4000,
                             rate=50, number_factor=3.5)
    underia.entity_spawn(underia.Entities.SwordInTheStone, target_number=1, to_player_max=5000, to_player_min=4000,
                         rate=50, number_factor=3)
    underia.entity_spawn(underia.Entities.StoneAltar, target_number=3, to_player_max=5000, to_player_min=4000,
                         rate=50, number_factor=3)
    underia.entity_spawn(underia.Entities.RawOre, target_number=3, to_player_max=5000, to_player_min=1000,
                         rate=.2, number_factor=300)
    if 6 > game.stage > 0:
        underia.entity_spawn(underia.Entities.MetalAltar, target_number=3, to_player_max=5000, to_player_min=4000,
                             rate=50, number_factor=3)
    if game.stage > 6:
        underia.entity_spawn(underia.Entities.ScarlettAltar, target_number=3, to_player_max=5000, to_player_min=4000,
                             rate=50, number_factor=3)
    if game.get_biome() not in ['inner']:
        if 6 > game.stage > 0:
            underia.entity_spawn(underia.Entities.EvilMark, target_number=3, to_player_max=5000, to_player_min=4000,
                                 rate=50, number_factor=1.9)
        if game.day_time > 0.75 or game.day_time < 0.2:
            underia.entity_spawn(underia.Entities.Eye, target_number=4 + bm * 12, to_player_max=2000, to_player_min=1500,
                                 rate=0.4 + bm * 0.8)
            underia.entity_spawn(underia.Entities.Bloodflower, target_number=5 + bm * 24, to_player_max=2000, to_player_min=1500,
                                 rate=0.5 + bm * 1.2)
            underia.entity_spawn(underia.Entities.RedWatcher, target_number=2 + bm * 17, to_player_max=2000, to_player_min=1800,
                                 rate=0.2 + bm * 0.7)
            if game.stage == 1:
                underia.entity_spawn(underia.Entities.MechanicEye, target_number=1 + bm * 8, to_player_max=2000, to_player_min=1500,
                                     rate=0.2 + bm * 0.9)

                underia.entity_spawn(underia.Entities.Destroyer, target_number=1, to_player_max=6000, to_player_min=5000,
                                     rate=0.001 + bm * 0.06, number_factor=1.5)
                underia.entity_spawn(underia.Entities.TheCPU, target_number=1, to_player_max=6000, to_player_min=5000,
                                     rate=0.001 + bm * 0.06, number_factor=1.5)
                underia.entity_spawn(underia.Entities.TruthlessEye, target_number=1, to_player_max=6000, to_player_min=5000,
                                     rate=0.0005 + bm * 0.03, number_factor=1.5)
                underia.entity_spawn(underia.Entities.FaithlessEye, target_number=1, to_player_max=6000, to_player_min=5000,
                                     rate=0.0005 + bm * 0.03, number_factor=1.5)
            elif game.stage == 0:
                underia.entity_spawn(underia.Entities.TrueEye, target_number=1, to_player_max=6000, to_player_min=5000,
                                     rate=0.0008 + bm * 0.02, number_factor=1.5)
        underia.entity_spawn(underia.Entities.Star, target_number=12 + bm * 10, to_player_max=2000, to_player_min=1500, rate=0.7)
    elif game.get_biome() == 'inner':
        underia.entity_spawn(underia.Entities.PlanteraBulb, target_number=5, to_player_max=5000, to_player_min=1000, rate=5)
        if 6 > game.stage > 3:
            underia.entity_spawn(underia.Entities.GhostFace, target_number=5, to_player_max=5000, to_player_min=2000, rate=0.3)
            underia.entity_spawn(underia.Entities.SadFace, target_number=5, to_player_max=5000, to_player_min=2000, rate=0.3)
            underia.entity_spawn(underia.Entities.AngryFace, target_number=5, to_player_max=5000, to_player_min=2000, rate=0.3)
            underia.entity_spawn(underia.Entities.TimeTrap, target_number=5, to_player_max=5000, to_player_min=2000, rate=0.4)
            underia.entity_spawn(underia.Entities.TimeFlower, target_number=5, to_player_max=5000, to_player_min=2000, rate=0.4)
            underia.entity_spawn(underia.Entities.Molecules, target_number=5, to_player_max=5000, to_player_min=2000, rate=0.4)
            underia.entity_spawn(underia.Entities.TitaniumIngot, target_number=5, to_player_max=5000, to_player_min=2000, rate=0.4)
            underia.entity_spawn(underia.Entities.Spark, target_number=5, to_player_max=5000, to_player_min=2000, rate=0.4)
            underia.entity_spawn(underia.Entities.Holyfire, target_number=5, to_player_max=5000, to_player_min=2000, rate=0.4)
        if 6 > game.stage > 4:
            underia.entity_spawn(underia.Entities.HolyPillar, target_number=2, to_player_max=3000, to_player_min=1000,
                                 rate=50, number_factor=1.9)
            underia.entity_spawn(underia.Entities.ScarlettPillar, target_number=2, to_player_max=3000, to_player_min=1000,
                                 rate=50, number_factor=1.9)


try:
    game.run()



except Exception as err:
    def try_delete_attribute(obj, attr):
        try:
            delattr(obj, attr)
        except AttributeError:
            print(f"Attribute {attr} not found in object {obj}")


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
    try_delete_attribute(game.player.profile, 'font')
    try_delete_attribute(game.player.profile, 'dialogger')
    game.events = []
    game.projectiles = []
    game.entities = []
    for w in game.player.weapons:
        game.player.inventory.add_item(underia.ITEMS[w.name.replace(" ", "_")])
    game.player.weapons = []
    with open(resources.get_save_path(game.save), 'wb') as w:
        w.write(pickle.dumps(game))
        w.close()
    with open(resources.get_save_path(sfd), 'wb') as w:
        w.write(pickle.dumps(underia.GameData(game.player.profile)))
        w.close()
    pg.quit()
    if type(err) not in [resources.Interrupt, KeyboardInterrupt]:
        raise resources.UnderiaError(f"An error occurred while running the game:\n{err}") from err
