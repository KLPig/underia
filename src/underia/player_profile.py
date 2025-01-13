import pygame as pg
import time
from . import game

class PlayerProfile:
    def __init__(self):
        self.avail_points = 0
        self.point_wisdom = 0
        self.point_strength = 0
        self.point_agility = 0
        self.point_melee = 0
        self.point_ranged = 0
        self.point_magic = 0
        self.stage = 0

    def get_color(self, w = 0, s = 0, a = 0, ml = 0, rg = 0, mg = 0):
        r, g, b = 255, 255, 255
        self.point_wisdom += w
        self.point_strength += s
        self.point_agility += a
        self.point_melee += ml
        self.point_ranged += rg
        self.point_magic += mg
        r -= (self.point_wisdom + self.point_agility + self.point_magic // 2) * 2
        g -= (self.point_wisdom + self.point_strength + self.point_melee // 2) * 2
        b -= (self.point_strength + self.point_agility + self.point_ranged // 2) * 2
        self.point_wisdom -= w
        self.point_strength -= s
        self.point_agility -= a
        self.point_melee -= ml
        self.point_ranged -= rg
        self.point_magic -= mg
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        return r, g, b

    def get_surface(self, r = 255, g = 255, b = 255):
        sl = [
            [0, 1, 1, 0, 0, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
        ]
        surface = pg.Surface((8, 8), pg.SRCALPHA)
        for i in range(8):
            for j in range(8):
                surface.set_at((i, j), (r, g, b, 255 * sl[j][i]))
        return surface

    def add_point(self, t = 0):
        if t != self.stage:
            return
        self.stage = t + 1
        font = pg.font.SysFont('dtm-mono', 32)
        self.avail_points += 20
        dialogues = [
            ['So, it\'s you.', '...', 'This, is your soul.(Use arrows)', 'Your essence of your whole life, is here.',
             'It\'s now white.', 'Depends on your choice, it will change it\'s color.', '(Swap: Z)',
             '...Make your choice...', '..And, when you\'re ready, press enter...'],
            ['You again.', 'You defeat the thing watching at you, so you get here.', '...',
             'Make your choice.'],
            ['Again', 'Looks like you collect those souls.', '...', 'Make your choice.'],
            ['...'],
        ]
        if not t:
            self.point_wisdom = 0
            self.point_strength = 0
            self.point_agility = 0
            self.point_melee = 0
            self.point_ranged = 0
            self.point_magic = 0
        dialogue = dialogues[t]
        cur_dialogue_flow = 0
        cur_dialogue_index = 0
        window = pg.display.get_surface()
        timer = 0
        sf = pg.transform.scale(self.get_surface(), (80, 80))
        sfr = sf.get_rect(center=window.get_rect().center)
        while True:
            cd = dialogue[cur_dialogue_index]
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE and cur_dialogue_flow >= len(cd) and timer:
                        cur_dialogue_index += 1
                        cur_dialogue_flow = 0
                        timer = 0
                    elif event.key == pg.K_RETURN:
                        cur_dialogue_index = len(dialogue)
                        cur_dialogue_flow = 0
            if cur_dialogue_index >= len(dialogue):
                break
            cd = dialogue[cur_dialogue_index]
            if timer:
                timer -= 1
                time.sleep(0.01)
            else:
                cur_dialogue_flow = min(cur_dialogue_flow + 1, len(cd))
                if cd[cur_dialogue_flow - 1] == ',':
                    timer = 60
                elif cd[cur_dialogue_flow - 1] == '.':
                    timer = 100
                else:
                    timer = 20
                window.fill((0, 0, 0))
                t = font.render(cd[:cur_dialogue_flow], True, (255, 255, 255))
                window.blit(t, (100, 100))
                if cur_dialogue_index > 1:
                    window.blit(sf, sfr)
                pg.display.update()
        rp, lp = 20, 10
        sel_p = 0
        done = False
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_z:
                        sel_p = not sel_p
                    elif event.key == pg.K_RIGHT:
                        hl = 30 if not sel_p else rp
                        if not sel_p:
                            rp = min(rp + 1, hl)
                        else:
                            lp = min(lp + 1, hl)
                    elif event.key == pg.K_LEFT:
                        hl = lp if not sel_p else 0
                        if not sel_p:
                            rp = max(rp - 1, hl)
                        else:
                            lp = max(lp - 1, hl)
                    elif event.key == pg.K_RETURN:
                        self.point_wisdom += lp
                        self.point_strength += rp - lp
                        self.point_agility += 30 - rp
                        done = True
            if done:
                break
            sf = self.get_surface(*self.get_color(lp, rp - lp, 30 - rp))
            sf = pg.transform.scale(sf, (80, 80))
            window.fill((0, 0, 0))
            t = font.render(f'Wisdom: {self.point_wisdom} +{lp} (+{int(lp ** 1.5) // 3}% mana regen)', True, (255, 255, 255))
            window.blit(t, (100, 100))
            t = font.render(f'Strength: {self.point_strength} +{rp - lp} (+{int((rp - lp) ** 1.5) // 3}% damage)', True, (255, 255, 255))
            window.blit(t, (100, 150))
            t = font.render(f'Agility: {self.point_agility} +{30 - rp} (+{int((30 - rp) ** 1.5) // 3}% speed)', True, (255, 255, 255))
            window.blit(t, (100, 200))
            pg.draw.rect(window, (0, 0, 255), (100, 300, 10 * lp, 30))
            pg.draw.rect(window, (255, 0, 0), (100 + 10 * lp, 300, 10 * (rp - lp), 30))
            pg.draw.rect(window, (0, 255, 0), (100 + 10 * rp, 300, 10 * (30 - rp), 30))
            if sel_p:
                pg.draw.rect(window, (255, 255, 0), (100 + 10 * lp - 5, 300, 10, 30))
            else:
                pg.draw.rect(window, (255, 255, 0), (100 + 10 * rp - 5, 300, 10, 30))
            window.blit(sf, sfr)
            pg.display.update()
        done = False
        lp, rp = 10, 20
        sel_p = 0
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_z:
                        sel_p = not sel_p
                    elif event.key == pg.K_RIGHT:
                        hl = 30 if not sel_p else rp
                        if not sel_p:
                            rp = min(rp + 1, hl)
                        else:
                            lp = min(lp + 1, hl)
                    elif event.key == pg.K_LEFT:
                        hl = lp if not sel_p else 0
                        if not sel_p:
                            rp = max(rp - 1, hl)
                        else:
                            lp = max(lp - 1, hl)
                    elif event.key == pg.K_RETURN:
                        self.point_melee += lp - 10
                        self.point_ranged += rp - lp - 10
                        self.point_magic += 30 - rp - 10
                        done = True
            if done:
                break
            sf = self.get_surface(*self.get_color(self.point_wisdom, self.point_strength, self.point_agility,
                                                  lp, rp - lp, 30 - rp))
            sf = pg.transform.scale(sf, (80, 80))
            window.fill((0, 0, 0))
            t = font.render(f'Melee: {self.point_melee} {lp - 10}', True, (255, 255, 255))
            window.blit(t, (100, 100))
            t = font.render(f'Ranged: {self.point_ranged} {rp - lp - 10}', True, (255, 255, 255))
            window.blit(t, (100, 150))
            t = font.render(f'Magic: {self.point_magic} {30 - rp - 10}', True, (255, 255, 255))
            window.blit(t, (100, 200))
            pg.draw.rect(window, (255, 0, 255), (100, 300, 10 * lp, 30))
            pg.draw.rect(window, (255, 255, 0), (100 + 10 * lp, 300, 10 * (rp - lp), 30))
            pg.draw.rect(window, (0, 255, 255), (100 + 10 * rp, 300, 10 * (30 - rp), 30))
            if sel_p:
                pg.draw.rect(window, (255, 255, 0), (100 + 10 * lp - 5, 300, 10, 30))
            else:
                pg.draw.rect(window, (255, 255, 0), (100 + 10 * rp - 5, 300, 10, 30))
            window.blit(sf, sfr)
            pg.display.update()
        try:
            game.get_game().pressed_keys = []
            game.get_game().pressed_mouse = []
        except ValueError:
            pass
