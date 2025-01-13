import copy

import pygame as pg

from src.underia import game, inventory, word_dict
from src.values import hp_system


def hp_bar(hp: hp_system.HPSystem, midtop: tuple, size: float):
    displayer = game.get_game().displayer
    width = int(size * 0.8)
    height = int(size * 0.1)
    rect = pg.Rect(midtop[0] - width // 2, midtop[1] - height - size // 3, width, height)
    hp_rate = hp.hp / hp.max_hp
    hp_dis_rate = hp.displayed_hp / hp.max_hp
    hp_rate = max(0.0, min(1.0, hp_rate))
    if hp_dis_rate >= 1.0:
        return
    hp_dis_rate = max(0.0, min(1.0, hp_dis_rate))
    color = (255 - hp_rate * 255, hp_rate * 255, 0)
    color_dis = (255 - hp_dis_rate * 255, hp_dis_rate * 255, 0)
    pg.draw.rect(displayer.canvas, color_dis, (rect.left, rect.top, int(width * hp_dis_rate), height))
    pg.draw.rect(displayer.canvas, color, (rect.left, rect.top, int(width * hp_rate), height))
    pg.draw.rect(displayer.canvas, (0, 0, 0), rect, 2)


LANG = 'en'
Dictionary = word_dict.en_cn


def text(txt: str) -> str:
    word = txt
    if LANG != 'zh-cn':
        return word
    s = ''
    word = str.lower(word)
    if word in Dictionary.keys():
        return Dictionary[word]
    i = 0
    items = list(Dictionary.items())
    items.sort(key=lambda x: len(x[0]), reverse=True)
    while i < len(word):
        f = False
        for k, v in items:
            if not len(k):
                continue
            k = str.lower(k)
            if word[i:].startswith(k):
                s += v
                i += len(k)
                if i < len(word) and word[i] == ' ':
                    i += 1
                f = True
                break
        if not f:
            s += word[i]
            i += 1
    if word not in Dictionary.keys() and len(word) < 50:
        Dictionary[word] = s
    return s


def item_mouse(x, y, name, no, amount, scale, anchor='left', _window=None, mp=None):
    if name == 'null':
        return
    if _window is None:
        window = game.get_game().displayer.canvas
    else:
        window = _window
    r = (x, y, 80 * scale, 80 * scale)
    if mp is not None:
        mps = mp
    else:
        mps = game.get_game().displayer.reflect(*pg.mouse.get_pos())
    if pg.Rect(r).collidepoint(mps):
        game.get_game().player.in_ui = True
        game.get_game().player.touched_item = name
        desc_split = inventory.ITEMS[name].get_full_desc().split('\n')
        l = len(desc_split) + 1
        t = game.get_game().displayer.font.render(text(
            f"(#{inventory.ITEMS[name].inner_id})" + f"{inventory.ITEMS[name].name}{'(' + amount + ')' if amount not in ['1', ''] else ''}"),
                                                  True,
                                                  inventory.Inventory.Rarity_Colors[inventory.ITEMS[name].rarity],
                                                  (0, 0, 0))
        if mps[1] > 36 * l:
            p_y = 0
        else:
            p_y = 36 * l - mps[1] + 36
        if anchor == 'left':
            tr = t.get_rect(bottomleft=(mps[0],
                                        mps[1] - 36 * l + p_y))
        else:
            tr = t.get_rect(bottomright=(mps[0] - 80 * scale,
                                         mps[1] - 36 * l + p_y))
        window.blit(t, tr)

        for j in range(l - 1):
            t = game.get_game().displayer.font.render(text(desc_split[j]), True,
                                                      (255, 255, 255), (0, 0, 0))
            if anchor == 'left':
                tr = t.get_rect(bottomleft=(mps[0], mps[1] - 36 * (l - j - 1) + p_y))
            else:
                tr = t.get_rect(bottomright=(mps[0] - 80 * scale, mps[1] - 36 * (l - j - 1) + p_y))
            window.blit(t, tr)


def item_display(x, y, name, no, amount, scale, selected=False, _window=None, mp=None):
    if _window is None:
        window = game.get_game().displayer.canvas
    else:
        window = _window
    r = (x, y, 80 * scale, 80 * scale)
    if mp is not None:
        mps = mp
    else:
        mps = game.get_game().displayer.reflect(*pg.mouse.get_pos())
    if pg.Rect(r).collidepoint(mps):
        pg.draw.rect(window, (160, 160, 160), r)
    else:
        pg.draw.rect(window, (127, 127, 127), r)
    pg.draw.rect(window, (0, 0, 0), r, 3)
    im = game.get_game().graphics['items_' + inventory.ITEMS[name].img]
    im = copy.copy(pg.transform.scale(im, (64 * scale, 64 * scale)))
    imr = im.get_rect(center=(x + 40 * scale, y + 40 * scale))
    window.blit(im, imr)
    if amount not in ['1', '']:
        t = game.get_game().displayer.font_s.render(amount, True, (0, 0, 0))
        tr = t.get_rect(topleft=(x + 10, y + 5))
        window.blit(t, tr)
    t = game.get_game().displayer.font_s.render(no.split('/')[0], True, (0, 0, 0))
    tr = t.get_rect(topright=(x + 80 * scale - 10, y + 5))
    window.blit(t, tr)
    if selected:
        pg.draw.rect(window, (255, 255, 0), (x, y, 80 * scale, 80 * scale), 6)
