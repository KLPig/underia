import pygame as pg
from underia import game, inventory, word_dict
from values import hp_system
import constants


def hp_bar(hp: hp_system.HPSystem, midtop: tuple, size: float):
    displayer = game.get_game().displayer
    p = bool(hp.pacify)
    width = 250 / game.get_game().player.get_screen_scale()
    height = (50 + p * 20) / game.get_game().player.get_screen_scale()
    size = size / game.get_game().player.get_screen_scale()
    rect = pg.Rect(midtop[0] - width // 2, midtop[1] - height - size // 5, width, height)
    hp_rate = hp.hp / hp.max_hp
    hp_dis_rate = hp.displayed_hp / hp.max_hp
    hp_rate = max(0.0, min(1.0, hp_rate))
    pacify_rate = hp.pacify / hp.max_hp
    if hp.hp >= hp.max_hp * 999999 / 1000000 and not p:
        return
    hp_dis_rate = max(0.0, min(1.0, hp_dis_rate))
    color = (255 - hp_rate * 255, hp_rate * 255, 0)
    color_dis = (255 - hp_dis_rate * 255, hp_dis_rate * 255, 0)
    if constants.USE_ALPHA:
        surf = pg.Surface((width, height), pg.SRCALPHA)
        pg.draw.rect(surf, color_dis, (0, 0, int(width * hp_dis_rate), height), border_radius=2)
        pg.draw.rect(surf, color, (0, 0, int(width * hp_rate), height), border_radius=2)
        if p:
            pg.draw.rect(surf, (0, 127, 255), (0, 50 / game.get_game().player.get_screen_scale(),
                                               int(width * pacify_rate), 20 / game.get_game().player.get_screen_scale()), border_radius=2)
        pg.draw.rect(surf, (255, 255, 255), (0, 0, width, height), 5, border_radius=2)
        surf.set_alpha(180)
        displayer.canvas.blit(surf, (rect.left, rect.top))
    else:
        pg.draw.rect(displayer.canvas, color_dis, (rect.left, rect.top, int(width * hp_dis_rate), height), border_radius=5)
        pg.draw.rect(displayer.canvas, color, (rect.left, rect.top, int(width * hp_rate), height), border_radius=5)
        if p:
            pg.draw.rect(displayer.canvas, (0, 255, 255), (rect.left, rect.top + 25 / game.get_game().player.get_screen_scale(),
                                                           int(width * pacify_rate), 10 / game.get_game().player.get_screen_scale()), border_radius=5)
        pg.draw.rect(displayer.canvas, (255, 255, 255), rect, 2, border_radius=5)


Dictionary = word_dict.en_cn

un_trans = []


def text(txt: str) -> str:
    word = txt
    if constants.LANG != 'zh':
        return word
    for i, c in enumerate(word):
        if str.isdecimal(c):
            return text(word[:i]) + c + text(word[i + 1:])
    s = ''
    word = str.lower(word)
    if word in Dictionary.keys():
        return Dictionary[word]
    i = 0
    items = list(Dictionary.items())
    items.sort(key=lambda x: len(x[0]), reverse=True)
    wc = ''
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
            if str.isalpha(word[i]) or wc in [' ', '-', ]:
                wc += word[i]
            s += word[i]
            i += 1
        else:
            if wc not in un_trans and wc:
                un_trans.append(wc)
                print(f"Untranslated word: {wc}")
                wc = ''
    if wc not in un_trans and wc:
        un_trans.append(wc)
        print(f"Untranslated word: {wc}")
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

        mw = t.get_width()
        mh = 36 * l
        ts = []

        for j in range(l - 1):
            col = (255, 255, 255)
            ds = desc_split[j]
            if str.startswith(ds, 'col'):
                col = (int('0x' + ds[3:5], 16), int('0x' + ds[5:7], 16), int('0x' + ds[7:9], 16))
                ds = ds[9:]
            ft = game.get_game().displayer.font.render(text(ds), True,
                                                      col, (0, 0, 0))
            ts.append(ft)
            mw = max(mw, ft.get_width())

        mr = pg.Rect(0, 0, mw + 50, mh + 50)
        if anchor == 'left':
            mr.bottomleft = (mps[0] - 25, mps[1] - 36 + p_y + 25)
        else:
            mr.bottomright = (mps[0] - 80 * scale + 25, mps[1] - 36 + p_y + 25)
        pg.draw.rect(window, (0, 0, 0), mr, border_radius=8)
        rc = inventory.Inventory.Rarity_Colors[inventory.ITEMS[name].rarity]
        pg.draw.rect(window, rc, mr, 5, 8)

        for j in range(l - 1):
            ft = ts[j]
            if anchor == 'left':
                tr = ft.get_rect(bottomleft=(mps[0], mps[1] - 36 * (l - j - 1) + p_y))
            else:
                tr = ft.get_rect(bottomright=(mps[0] - 80 * scale, mps[1] - 36 * (l - j - 1) + p_y))
            window.blit(ft, tr)

        if anchor == 'left':
            tr = t.get_rect(bottomleft=(mps[0],
                                        mps[1] - 36 * l + p_y))
        else:
            tr = t.get_rect(bottomright=(mps[0] - 80 * scale,
                                         mps[1] - 36 * l + p_y))
        window.blit(t, tr)


def item_display(x, y, name, no, amount, scale, selected=False, _window=None, mp=None, red=False):
    if _window is None:
        window = game.get_game().displayer.canvas
    else:
        window = _window
    r = (x, y, 80 * scale, 80 * scale)
    if mp is not None:
        mps = mp
    else:
        mps = game.get_game().displayer.reflect(*pg.mouse.get_pos())
    rc = inventory.Inventory.Rarity_Colors[inventory.ITEMS[name].rarity]
    if red:
        rc = (255, 0, 0)
    sf = pg.Surface(pg.Rect(r).size, pg.SRCALPHA)
    if pg.Rect(r).collidepoint(mps):
        pg.draw.rect(sf, (rc[0] * 2 // 3, rc[1] * 2 // 3, rc[2] * 2 // 3), ((0, 0), (sf.get_size())), border_radius=5)
    elif red:
        pg.draw.rect(sf, (255, 200, 200), ((0, 0), (sf.get_size())), border_radius=5)
    else:
        pg.draw.rect(sf, (200, 200, 200), ((0, 0), (sf.get_size())), border_radius=5)
    # pg.draw.rect(sf, (0, 0, 0), r, 3, 5)
    sf.set_alpha(128 + (name != 'null') * 64)
    window.blit(sf, r)
    im = game.get_game().graphics['items_' + inventory.ITEMS[name].img]
    im = pg.transform.scale(im, (64 * scale, 64 * scale))
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
        pg.draw.rect(window, (255, 255, 0), (x, y, 80 * scale, 80 * scale), 6, 5)
