import pygame as pg

import underia
import underia3
import values
from string import Template
import packs
import os

pg.init()
pg.display.set_mode((800, 600))

with open('./src/it_temp.html', 'r') as t:
    temp = t.read()
    t.close()

recipes = underia.RECIPES
game = underia.Game()
underia.write_game(game)
game.setup()


f = "<!DOCTYPE html><html><head>\n<title>Underia Items</title>\n" \
    "<link rel='stylesheet' type='text/css' href='styles.css'>\n" \
    "<meta charset='UTF-8'></head><body>"

f += "<h1>Underia Items</h1>"

f += open('./docs/header.html').read()

f += "<table id='item-table'>"
img_str = "<span class='item %s' id='%s-%s'> <img src='assets/graphics/items/%s.png' style='width: 50px; height: 50px'/></span>"
item_str = "<p style='color: rgb%s'>%s</p>" # <p class='desc' style='color: rgb%s'>%s</p>"

kw = [(k, v) for k, v in underia.ITEMS.items()]

for _, item in kw:
    f += f"<tr onclick='location.href=\"./items/{item.id}.html\"' class='item-row' id='{item.id}-filter' style='max-height: 100px'>\n"
    f += "<td>" + img_str % ('main', item.id, 'main', item.id) + "</td>\n"
    c = underia.Inventory.Rarity_Colors[item.rarity]
    t = underia.text(item.name)
    if t is None:
        t = ''
    f += "<td>" + item_str % (
    c, f'(#{item.inner_id}){item.name} {t}',
    )+ "</td>\n" #item.get_full_desc().replace('\n', '<br/>') +
    #f'<a href=\'./recipes.html?filter={item.id}-res-filt\'>Recipes as Result</a>'
    #f'<br/><a href=\'./recipes.html?filter={item.id}-mat-filt\'>Recipes as Material</a>') + "</td>\n"


    dc = ''

    tp = 'non-game item'

    r_mat = [r for r in underia.RECIPES if item.id in r.material]
    r_res = [r for r in underia.RECIPES if item.id == r.result]
    d_drop = []
    for s in dir(underia.Entities):
        e = getattr(underia.Entities, s)
        if 'LOOT_TABLE' in dir(e):
            lt: underia.LootTable = getattr(e, 'LOOT_TABLE')
            if item.id in lt.get_all_items():
                d_drop.append(e)

    if underia.TAGS['melee_weapon'] in item.tags:
        tp = 'melee weapon'
    elif underia.TAGS['arcane_weapon'] in item.tags:
        tp = 'arcane weapon'
    elif underia.TAGS['magic_weapon'] in item.tags:
        tp = 'magic weapon'
    elif underia.TAGS['bow'] in item.tags:
        tp = 'bow'
    elif underia.TAGS['gun'] in item.tags:
        tp = 'gun'
    elif underia.TAGS['lazer_gun'] in item.tags:
        tp = 'lazer gun'
    elif underia.TAGS['knife'] in item.tags:
        tp = 'assassin ranged weapon'
    elif underia.TAGS['pickaxe'] in item.tags:
        tp = 'pickaxe'
    elif underia.TAGS['head'] in item.tags:
        tp = 'head-positioned armor'
    elif underia.TAGS['body'] in item.tags:
        tp = 'body-positioned armor'
    elif underia.TAGS['leg'] in item.tags:
        tp = 'leg-positioned armor'
    elif underia.TAGS['major_accessory'] in item.tags:
        tp = 'armory accessory'
    elif underia.TAGS['wings'] in item.tags:
        tp = 'accessory'
    elif r_mat:
        tp = 'material'
    elif r_res or d_drop:
        tp = 'trophy'
    elif underia.TAGS['item'] in item.tags:
        tp = 'item'


    dc += (f'{str.upper(item.name)} is a {tp} with id #{item.inner_id}. '
           f'Its rarity value is {item.rarity}({underia.Inventory.Rarity_Names[item.rarity]}).')
    ds = 2 * bool(r_mat) + bool(r_res)
    if ds == 3:
        dc += 'It is craftable and involves further crafting recipes.'
    elif ds == 2:
        dc += 'It involves further crafting recipes but cannot be directly crafted.'
    elif ds == 1:
        dc += 'It can be directly crafted.'
    else:
        dc += 'It does not involve any crafting actions.'
    if d_drop:
        dc += 'It can '
        if r_res:
            dc += 'also '
        dc += f'be dropped by entities.'
    if d_drop or r_mat:
        dc += '</p><p class="h">'
        if r_mat:
            dc += 'It involves as a material of '
            for r in r_mat[:15]:
                dc += f'<a href=\'./{r.result}.html\'>{underia.ITEMS[r.result].name}</a>'
                if r is not r_mat[-1]:
                    dc += ', '
                else:
                    dc += '. '
            if len(r_mat) > 15:
                dc += f' and {len(r_mat)-15} more.'
        if d_drop:
            dc += 'It can be dropped by '
            for s in d_drop[:15]:
                dc += f'<a href=\'.,/entities/{s.NAME}.html\'>{s.NAME}</a>'
                if s is not d_drop[-1]:
                    dc += ', '
                else:
                    dc += '.'
            if len(d_drop) > 15:
                dc += f' and {len(d_drop)-15} more.'

    if item.id in underia.WEAPONS:
        dc += f'</p><p class="h">{item.name.upper()} is also a weapon. '
        w = underia.WEAPONS[item.id]
        if w.damages:
            dc += f'It deals '
            ds = [(d, dv) for d, dv in w.damages.items()]
            for d, dv in ds:
                dc += f'{dv} {values.DamageKeys[d]} damage'
                if d is not ds[-1][0]:
                    dc += ', '
                else:
                    dc += '. '
        dc += f'It acts as a '
        if type(w) is underia.SweepWeapon or type(w) is underia.AutoSweepWeapon:
            dc += 'simple melee weapon.'
        elif type(w) is underia.Blade:
            dc += 'simple melee blade.'
        elif type(w) is underia.Spear:
            dc += 'simple melee spear.'
        elif type(w) is underia.Gun:
            dc += 'simple ranged gun.'
        elif type(w) is underia.LazerGun:
            dc += 'simple ranged lazer gun.'
        elif type(w) is underia.Bow:
            dc += 'simple ranged bow.'
        elif type(w) is underia.ThiefWeapon or type(w) is underia.ThiefDoubleKnife:
            dc += 'simple ranged assassin knife.'
        elif type(w) is underia.ThrowerThiefWeapon:
            dc += 'simple ranged thrower weapon.'
        elif type(w) is underia.Weapon:
            dc += 'basic weapon.'
        else:
            dc += 'complex weapon.'
        dt = w.at_time + w.cd + 1
        dc += f' It attacks every {dt} ticks, i.e {round(80 / dt, 2)} per second. '
        dc += f'It\'s "dashboard" dpm is {round(sum([v for _, v in w.damages.items()]) * 80 / dt, 1)}. '

    rf = ''
    if r_mat:
        rf += f"<h1 style='color: rgb{c}'>As Material For:</h1>"
        rf += "<table id='item-table' class='spes-table'>"
        dimg_str = ("<div class='item %s %s-%s' onclick='location.href=\"./%s.html\"'"
                   "> <img src='../assets/graphics/items/%s.png'/> <p class='amount'>%s</p> </div>")

        for recipe in r_mat:
            t = underia.text(underia.ITEMS[recipe.result].name)
            rf += "<tr class='item-row %s'><td class='rec'>%s</td>\n" % (
                ' '.join([f'{k}-mat-filt' for k in recipe.material.keys()]) +
            f' {recipe.result}-res-filt',
                dimg_str % ('main', recipe.result, 'main', recipe.result, recipe.result,
                       f'{underia.ITEMS[recipe.result].name} {t}*{recipe.crafted_amount}'))
            j = 0
            for it, amount in recipe.material.items():
                t = underia.text(underia.ITEMS[it].name)
                rf += "<td class='rec'>%s</td>\n" % (dimg_str % ('regular', it, 'regular', it, it,
                                                               f'{underia.ITEMS[it].name} {t}*{amount}'))
                j += 1
            rf += "</tr>\n"
        rf += "</table>\n<script src='recipe_js.js'></script>\n</body></html>"
    if r_res:
        rf += f"<h1 style='color: rgb{c}'>As Results From:</h1>"
        rf += "<table id='item-table' class='spes-table'>"
        dimg_str = ("<div class='item %s %s-%s' onclick='location.href=\"./%s.html\"'"
                   "> <img src='../assets/graphics/items/%s.png'/> <p class='amount'>%s</p> </div>")

        for recipe in r_res:
            t = underia.text(underia.ITEMS[recipe.result].name)
            rf += "<tr class='item-row %s'><td class='rec'>%s</td>\n" % (
                ' '.join([f'{k}-mat-filt' for k in recipe.material.keys()]) +
                f' {recipe.result}-res-filt',
                dimg_str % ('main', recipe.result, 'main', recipe.result, recipe.result,
                           f'{underia.ITEMS[recipe.result].name} {t}*{recipe.crafted_amount}'))
            j = 0
            for it, amount in recipe.material.items():
                t = underia.text(underia.ITEMS[it].name)
                rf += "<td class='rec'>%s</td>\n" % (dimg_str % ('regular', it, 'regular', it, it,
                                                                f'{underia.ITEMS[it].name} {t}*{amount}'))
                j += 1
            rf += "</tr>\n"
        rf += "</table>"

    if not os.path.exists(f'./docs/items/{item.id}.html'):
        ap = ''
    else:
        with open(f'./docs/items/{item.id}.html', 'r', encoding='utf-8') as af:
            ap = af.read().split('<span id="wtw">')[1].split('</span>')[0]
            af.close()
    nt = Template(temp).substitute({
        'name': item.name,
        'id': item.id,
        'inner_id': item.inner_id,
        'rarity': item.rarity,
        'desc': item.get_full_desc().replace('\n', '<br/>'),
        'col': 'rgb' + str(underia.Inventory.Rarity_Colors[item.rarity]),
        'init_desc': dc,
        'rf': rf,
        'ap': ap
    })
    with open(f'./docs/items/{item.id}.html', 'w') as af:
        af.write(nt)
        af.close()

f += "</table>\n<script src='./item_js.js'></script>\n</body></html>"

with open("./docs/items.html", "w", encoding='utf-8') as ff:
    ff.write(f)
