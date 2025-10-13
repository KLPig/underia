import pygame as pg

import underia
import underia3

pg.init()
pg.display.set_mode((800, 600))

recipes = underia.RECIPES
game = underia.Game()
underia.write_game(game)
game.setup()

f = "<!DOCTYPE html><html><head>\n<title>Underia Items</title>\n" \
    "<link rel='stylesheet' type='text/css' href='styles.css'>\n" \
    "<meta charset='UTF-8'></head><body>"

f += "<h1>Underia Items</h1>"

f += open('../docs/header.html').read()

f += "<table id='item-table'>"
img_str = "<div class='item %s' id='%s-%s'> <img src='assets/graphics/items/%s.png'/></div>"
item_str = "<h2 style='color: rgb%s'>%s</h2><p class='desc' style='color: rgb%s'>%s</p>"

for _, item in underia.ITEMS.items():
    f += f"<tr onclick='location.href=\"./recipes.html#{item.id}-main\"' class='item-row' id='{item.id}-filter'>\n"
    f += "<td>" + img_str % ('main', item.id, 'main', item.id) + "</td>\n"
    c = underia.Inventory.Rarity_Colors[item.rarity]
    c = (c[0] // 2, c[1] // 2, c[2] // 2)
    t = underia.text(item.name)
    if t is None:
        t = ''
    f += "<td>" + item_str % (
    c, f'(#{item.inner_id}){item.name} {t}', c,
    item.get_full_desc().replace('\n', '<br/>') +
    f'<br/><a href=\'./recipes.html?filter={item.id}-res-filt\'>Recipes as Result</a>'
    f'<br/><a href=\'./recipes.html?filter={item.id}-mat-filt\'>Recipes as Material</a>') + "</td>\n"

f += "</table>\n<script src='./item_js.js'></script>\n</body></html>"

with open("../docs/items.html", "w", encoding='utf-8') as ff:
    ff.write(f)
