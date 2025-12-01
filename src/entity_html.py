import pygame as pg

import underia, values
import underia3
import constants
import packs

pg.init()
pg.display.set_mode((800, 600))

recipes = underia.RECIPES
game = underia.Game()
underia.write_game(game)
game.setup()

f = "<!DOCTYPE html><html><head>\n<title>Underia Entities</title>\n" \
    "<link rel='stylesheet' type='text/css' href='styles.css'>\n" \
    "<meta charset='UTF-8'></head><body>"

f += "<h1>Underia Entities</h1>"

f += open('../docs/header.html').read()

f += "<table>"
img_str = ("<td><div class='item %s drop' id='%s-%s' onclick='location.href=\"./items.html#%s-main\"'"
           "> <img src='assets/graphics/items/%s.png'/> <p class='amount'>%s</p> </div></td>")

entity_str = "<div class='entity' id='%s'><img class='imge' src='assets/graphics/entity/%s.png'/> <p class='amount'>%s</p></div>"
entity3_str = "<div class='entity' id='%s'><img class='imge' src='assets/graphics/entity3/%s.png'/> <p class='amount'>%s</p></div>"

'''
ets = [
    'Tree', 'Cactus', 'ConiferousTree', 'HugeTree', 'TreeMonster', 'ClosedBloodflower', 'FluffBall', 'HeavenGuard',
    'Eye', 'Bloodflower', 'RedWatcher', 'Star',
    'SwordInTheStone',
    'TrueEye', 'MagmaCube', 'MagmaKing', 'RuneRock', 'SandStorm', 'AbyssEye', 'EvilMark', 'SoulFlower',
    'MechanicEye', 'Cells', 'IceCap', 'SnowDrake', 'Leaf',
    'FaithlessEye', 'TruthlessEye', 'Destroyer', 'TheCPU', 'Greed', 'EyeOfTime', 'DevilPython',
    'Jevil', 'JevilKnife', 'Plantera', 'GhostFace', 'SadFace', 'AngryFace', 'Spark', 'Holyfire',
    'TimeTrap', 'TimeFlower', 'Molecules', 'TitaniumIngot',
    'CLOCK', 'MATTER', 'SunEye', 'MoonEye', 'ScarlettPillar', 'HolyPillar',
    'ReincarnationTheWorldsTree', 'Faith', 'OmegaFlowery'
]'''

ets = dir(underia.Entities)


for entity in ets:
    try:
        e: underia.Entities.Entity = getattr(underia.Entities, entity)((0, 0))
    except Exception as _:
        continue
    try:
        ss = [k.removeprefix('entity_') for k, v in game.graphics.graphics.items() if v == e.img]
        mh = e.hp_sys.max_hp
        ddf = int(e.hp_sys.defenses[values.DamageTypes.PHYSICAL] +
                                                         e.hp_sys.defenses[values.DamageTypes.PIERCING] +
                                                         e.hp_sys.defenses[values.DamageTypes.MAGICAL] +
                                                         e.hp_sys.defenses[values.DamageTypes.ARCANE] * 2 +
                                                         e.hp_sys.defenses[values.DamageTypes.THINKING] * 4) // 9
        f += "<tr><td>%s</td>\n" % (entity_str % (entity, ss[0] if len(ss) else 'null',
                                                  e.NAME + '<br>' + f'{int(mh * .6)}/{int(mh)}/{int(mh * 1.9)}/{int(mh * 2.6)}' + ' HP<br>' +
                                                  (f'{e.obj.TOUCHING_DAMAGE} AT ' if e.obj.TOUCHING_DAMAGE else ' ') +
                                                  f'{ddf}/{ddf + int(mh * .0001)}/{ddf + int(mh * .00038)}/{ddf + int(mh * .00104)} DF<br>' +
                                                  'AI: ' + type(e.obj).__name__))
        for item in e.LOOT_TABLE.get_all_items():
            t = underia.text(underia.ITEMS[item].name)
            f += img_str % ('regular', item, 'regular', item, item, f'{underia.ITEMS[item].name} {t}')
        f += "</tr>\n"
    except AttributeError:
        pass

ee = underia3

for entity in dir(ee):
    try:
        e: underia.Entities.Entity = getattr(ee, entity)((0, 0))
    except TypeError:
        continue
    if not issubclass(type(e), ee.Entity):
        continue
    try:
        ss = [k.removeprefix('entity3_') for k, v in game.graphics.graphics.items() if v == e.img]
        print(ss)
        f += "<tr><td>%s</td>\n" % (entity3_str % (entity, ss[0] if len(ss) else 'null',
                                                  e.NAME + '<br>' + str(int()) + ' HP<br>' +
                                                  (f'{e.obj.TOUCHING_DAMAGE} AT ' if e.obj.TOUCHING_DAMAGE else ' ') +
                                                  f'{int(e.hp_sys.defenses[values.DamageTypes.PHYSICAL] +
                                                         e.hp_sys.defenses[values.DamageTypes.PIERCING] +
                                                         e.hp_sys.defenses[values.DamageTypes.MAGICAL] + 
                                                         e.hp_sys.defenses[values.DamageTypes.ARCANE] * 2 +
                                                         e.hp_sys.defenses[values.DamageTypes.THINKING] * 4) // 9} DF<br>' +
                                                  'AI: ' + type(e.obj).__name__))
        for item in e.LOOT_TABLE.get_all_items():
            t = underia.text(underia.ITEMS[item].name)
            f += img_str % ('regular', item, 'regular', item, item, f'{underia.ITEMS[item].name} {t}')
        f += "</tr>\n"
    except AttributeError:
        pass

f += "</table></body></html>"

with open("./docs/entities.html", "w", encoding='utf-8') as ff:
    ff.write(f)
