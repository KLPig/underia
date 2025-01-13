import pygame as pg

from src import underia

pg.init()
pg.display.set_mode((800, 600))

recipes = underia.RECIPES
game = underia.Game()
underia.write_game(game)
game.setup()

f = "<!DOCTYPE html><html><head>\n<title>Underia Items</title>\n" \
    "<link rel='stylesheet' type='text/css' href='styles.css'>\n" \
    "<meta charset='UTF-8'></head><body>"

f += "<h1>Underia Magics</h1>"

f += open('../docs/header.html').read()

f += "<table>"
img_str = "<div class='item %s' id='%s-%s'> <img src='assets/graphics/items/%s.png'/></div>"
item_str = "<h2 style='color: rgb%s'>%s</h2><p class='desc' style='color: rgb%s'>%s</p>"

magics = [t.name.removeprefix('magic_element_') for t in underia.TAGS.values() if t.name.startswith('magic_element_')]

for magic in magics:
    f += f"<tr><td colspan='2'><h2>{magic.upper()} MAGIC</h2></td></tr>"
    for _, item in underia.ITEMS.items():
        if underia.TAGS['magic_element_' + magic] not in item.tags:
            continue
        f += f"<tr onclick='location.href=\"./recipes.html#{item.id}-main\"'>\n"
        f += "<td>" + img_str % ('main', item.id, 'main', item.id) + "</td>\n"
        c = underia.Inventory.Rarity_Colors[item.rarity]
        c = (c[0] // 2, c[1] // 2, c[2] // 2)
        t = underia.text(item.name)
        if t is None:
            t = ''
        f += "<td>" + item_str % (
        c, [t.value.upper() for t in item.tags if t.name.startswith('magic_lv_')][0] +
        f': {underia.WEAPONS[item.id].spell_name.upper()}', c, item.get_full_desc().replace('\n', '<br/>')) + "</td>\n"

f += "</table></body></html>"

with open("../docs/magic.html", "w") as ff:
    ff.write(f)
