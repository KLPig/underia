import math
import random
import pygame as pg
from . import dialog, game, weapons, styles
from src import constants
import copy

class PlayerProfile:
    SKILL_DATA = {
        'melee_demand': ('Melee Demand', '+20% melee damage\n-40% ranged damage\n-40% magic damage'),
        'ranged_demand': ('Ranged Demand', '+20% ranged damage\n-40% melee damage\n-40% magic damage'),
        'magic_demand': ('Magic Demand', '+20% magic damage\n-40% melee damage\n-40% ranged damage'),
        'the_fury': ('The Fury', 'Key: Z\nContinue for 6s:\n+50% melee damage\n+30 touching defense\n-50% speed'),
        'warrior_shield': ('Warrior Shield', 'Key: X\nSummon a shield to absorb a damage for 4s.'),
        'fast_throw': ('Fast Throw', 'Key: Z\nSprint for a distance, \nthrow 3 projectiles of 3x damage.'),
        'perfect_shot': ('Perfect Shot', 'Key: X\nShoot a energy ammo with 5x damage.'),
        'healer': ('Healer', 'Key: Z\nHeal 10% max hp & 25% max mana.'),
        'multi_user': ('Multi-User', 'Key: X\nUse the current weapon all in once for the mana cost.'),

        'melee_reinforce_i': ('Melee Reinforce I', '+10% melee damage\n-5% ranged damage\n-5% magic damage'),
        'melee_reinforce_ii': ('Melee Reinforce II', '+12% damage\n+5/sec regeneration'),
        'melee_reinforce_iii': ('Melee Reinforce III', '+25 touching defense'),
        'melee_reinforce_iv': ('Melee Reinforce IV', '+25 magic defense'),

        'ranged_reinforce_i': ('Ranged Reinforce I', '+10% ranged damage\n-5% melee damage\n-5% magic damage'),
        'ranged_reinforce_ii': ('Ranged Reinforce II', '+5% damage\n+12% critical'),
        'ranged_reinforce_iii': ('Ranged Reinforce III', '+15% speed\n+3 touching defense'),
        'ranged_reinforce_iv': ('Ranged Reinforce IV', '-5% air resistance\n+7 magic defense'),

        'magic_reinforce_i': ('Magic Reinforce I', '+10% magic damage\n-5% melee damage\n-5% ranged damage'),
        'magic_reinforce_ii': ('Magic Reinforce II', '+6% damage\n+12/sec regeneration'),
        'magic_reinforce_iii': ('Magic Reinforce III', '+40 additional maximum mana\n+5 touching defense'),
        'magic_reinforce_iv': ('Magic Reinforce IV', '+20/sec mana regeneration\n+12 magic defense'),

        'star_supporter': ('Star Supporter', 'A chance to drop stars when defeating enemies.'),
    }

    def __init__(self):
        self.avail_points = 0
        self.point_wisdom = 0
        self.point_strength = 0
        self.point_agility = 0
        self.point_melee = 0
        self.point_ranged = 0
        self.point_magic = 0
        self.stage = 0
        self.dialogger = dialog.Dialogger(36, pg.Rect(0, 0, 1600, 300), target_surface=pg.Surface((1, 1)))
        self.font: pg.font.Font | None = None
        self.font_s: pg.font.Font | None = None
        self.select_skill = []
        self.point_left = 0

    def get_color(self, w = 0, s = 0, a = 0, ml = 0, rg = 0, mg = 0):
        r, g, b = 255, 255, 255
        self.point_wisdom += w
        self.point_strength += s
        self.point_agility += a
        self.point_melee += ml
        self.point_ranged += rg
        self.point_magic += mg
        mx = max(self.point_wisdom + self.point_agility + self.point_magic // 2,
                 self.point_wisdom + self.point_strength + self.point_melee // 2,
                 self.point_strength + self.point_agility + self.point_ranged // 2) * 2
        if mx < 255:
            mx = 255
        r -= (self.point_wisdom + self.point_agility + self.point_magic // 2) * 2 * 255 // mx
        g -= (self.point_wisdom + self.point_strength + self.point_melee // 2) * 2 * 255 // mx
        b -= (self.point_strength + self.point_agility + self.point_ranged // 2) * 2 * 255 // mx
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

    def chapter_select(self):
        window = pg.display.get_surface()
        width, height = window.get_size()
        clock = pg.time.Clock()
        title = self.font.render('Chapters', True, (255, 255, 255))
        title_rect = title.get_rect(center=(width // 2, 100))
        chapter_names = ['The Soul', 'The Mottled Land', 'The Adventure',
                         'The Ancient', 'The Darkness', 'The Previous Me']
        avail_chapter = game.get_game().chapter
        image = [game.get_game().graphics['legend_route_' + str(i + 1) + '_locked'] if i < avail_chapter
                 else game.get_game().graphics['legend_route_' + str(i + 1)] if i == avail_chapter
                 else game.get_game().graphics['legend_route_locked'] for i in range(6)]
        image = [pg.transform.scale(i, (350, 466)) for i in image]
        select = avail_chapter - 1
        if select < 0:
            return
        chapter_txt = [self.font.render(name, True, (255, 255, 255)) for name in chapter_names]
        chapter_select = [self.font.render(name, True, (255, 255, 0)) for name in chapter_names]
        tk = 0
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        pg.quit()
                        exit()
                    elif event.key == pg.K_F4:
                        constants.FULLSCREEN = not constants.FULLSCREEN
                        pg.display.set_mode(pg.display.get_window_size(), (pg.FULLSCREEN if constants.FULLSCREEN else 0) | constants.FLAGS)
            window.fill((0, 0, 0))
            window.blit(title, title_rect)
            if select:
                imr = image[select - 1].get_rect(center=(width // 4, height // 2))
                window.blit(image[select - 1], imr)
                tr = chapter_txt[select - 1].get_rect(midtop=(width // 4, height * 3 // 4 + 400))
                window.blit(chapter_txt[select - 1], tr)
            if select < 5:
                imr = image[select + 1].get_rect(center=(width * 3 // 4, height // 2))
                window.blit(image[select + 1], imr)
                tr = chapter_txt[select + 1].get_rect(midtop=(width * 3 // 4, height * 3 // 4 + 400))
                window.blit(chapter_txt[select + 1], tr)
            imr = image[select].get_rect(center=(width // 2, height // 2))
            window.blit(image[select], imr)
            tr = chapter_select[select].get_rect(midtop=(width // 2, height * 3 // 4 + 400))
            window.blit(chapter_select[select], tr)
            pg.display.update()
            tk += 1
            if tk == 200:
                select += 1
            elif tk == 400:
                return
            clock.tick(40)

    def skill_display(self, pos, name, select=False, window=None):
        im = game.get_game().graphics['skill_' + name]
        im = pg.transform.scale(im, (60, 60))
        if not select:
            im = copy.copy(im)
            im.set_alpha(128)
        if window is None:
            window = pg.display.get_surface()
        window.blit(im, pos)

    def skill_mouse(self, pos, name, rc=(255, 0, 255), anchor='left', window=None, mps=None):
        rect = pg.Rect(pos, (60, 60))
        if window is None:
            window = pg.display.get_surface()
        if mps is None:
            mps = pg.mouse.get_pos()
        title, desc_split = self.SKILL_DATA[name]
        desc_split = desc_split.split('\n')
        l = len(desc_split) + 1

        if not rect.collidepoint(mps):
            return

        t = game.get_game().displayer.font.render(styles.text(title), True, rc, (0, 0, 0))

        if mps[1] > 36 * l:
            p_y = 0
        else:
            p_y = 36 * l - mps[1] + 36

        mw = t.get_width()
        mh = 36 * l
        ts = []

        for j in range(l - 1):
            ft = game.get_game().displayer.font.render(styles.text(desc_split[j]), True,
                                                      (255, 255, 255), (0, 0, 0))
            ts.append(ft)
            mw = max(mw, ft.get_width())

        mr = pg.Rect(0, 0, mw + 50, mh + 50)
        if anchor == 'left':
            mr.bottomleft = (mps[0] - 25, mps[1] - 36 + p_y + 25)
        else:
            mr.bottomright = (mps[0] - 60 + 25, mps[1] - 36 + p_y + 25)
        pg.draw.rect(window, (0, 0, 0), mr, border_radius=8)
        pg.draw.rect(window, rc, mr, 5, 8)

        for j in range(l - 1):
            ft = ts[j]
            if anchor == 'left':
                tr = ft.get_rect(bottomleft=(mps[0], mps[1] - 36 * (l - j - 1) + p_y))
            else:
                tr = ft.get_rect(bottomright=(mps[0] - 60, mps[1] - 36 * (l - j - 1) + p_y))
            window.blit(ft, tr)

        if anchor == 'left':
            tr = t.get_rect(bottomleft=(mps[0],
                                        mps[1] - 36 * l + p_y))
        else:
            tr = t.get_rect(bottomright=(mps[0] - 60,
                                         mps[1] - 36 * l + p_y))
        window.blit(t, tr)

    def add_point(self, t = 0):
        self.font = pg.font.SysFont('dtm-mono', 36)
        self.font_s = pg.font.SysFont('dtm-mono', 18)
        self.dialogger = dialog.Dialogger(36, pg.Rect(0, 0, 1600, 300), target_surface=pg.Surface((1, 1)))
        self.dialogger.target_surface = pg.display.get_surface()
        if t != self.stage:
            return
        self.stage = t + 1
        game.get_game().stage = t
        self.avail_points += 20
        dialogues = [
            ['[PRESS Z TO CONTINUE]',
             'Are you, here?', 'Are we connected?', '...', 'Nice.', 'Let\'s move on.', '...',
             'This is your soul.', 'Your essence of humanity.', 'Now, you should give this soul some \'GIFT\'',
             'Let\'s do it.'],
            ['Are you here again?', 'Why are you here?', '...', 'Well, let\'s don\'t talk about it first.',
             'Again, you will get some \'AWARD\'.', 'Let\'s do it.'],
            ['Hello, again, SOUL COLLECTOR.', 'You may find some tips before, ..', '.. but you won\'t find any now.',
             'You know why?', '.. as you are SPECIAL.', 'Nobody will process your path like YOU do.', '...',
             'However, \'CHOOSE\' for your soul.'],
            ['Heya.', 'I know your name, CHARA, right?', 'You probably killed that deformed flower.',
             'Let\'s give you a hint.', 'Original chaos leads you for another world.', '...', 'Anyway.'],
            ['Finally.', 'You\'ve been finding souls.', 'And you finally find yours.', '...',
             'Think, where are you from?', 'How did it begin?', 'How will it end?', '...', 'Make your \'CHOICE\'.'],
            ['[AFTER YOU\'VE RESET THE TIMELINE, \nEVERYTHING WILL BE GONE.]', '[PLEASE STOP AND THINK BEFORE IT ALL ENDS.]',
             '[...]', 'This expression...', 'Are you here, again?', 'Alright.', 'Lets move on.'],
            ['...', 'It\'s you.', 'Let\'s move on.', '..?', 'Wait,', 'I\'ve observed that the world is changing.',
             'The holy and the evil are coming.', '...', 'You must save this world.']
        ]
        if not t:
            self.point_wisdom = 0
            self.point_strength = 0
            self.point_agility = 0
            self.point_melee = 0
            self.point_ranged = 0
            self.point_magic = 0
        clock = pg.time.Clock()
        if t in [0, 5]:
            if t:
                game.get_game().chapter += 1
            self.chapter_select()
            game.get_game().player.hp_sys.shields.clear()
            game.get_game().player.hp_sys.max_hp = 200
            game.get_game().player.hp_sys.hp = 200
            game.get_game().player.max_mana = 30
            game.get_game().player.max_talent = 0
            game.get_game().player.inventory.items = {}
            game.get_game().player.accessories = 6 * ['null']
            game.get_game().player.weapons = 4 * [weapons.WEAPONS['null']]
            game.get_game().seed = random.randint(0, 1000000)
            game.get_game().decors.clear()
            game.get_game().entities.clear()
            game.get_game().projectiles.clear()
            game.get_game().map_ns.clear()
        dialogue = dialogues[t]
        self.dialogger.dialog(*dialogue)
        window = pg.display.get_surface()
        tick = 0
        soul_x = window.get_width() // 2
        target_soul_x = window.get_width() // 2
        stage = 0
        selected_point = 0
        points = [0, 0, 0]

        while True:
            tick += 1
            keys = []
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()
                elif event.type == pg.KEYDOWN:
                    keys.append(event.key)
                    if event.key == pg.K_F4:
                        constants.FULLSCREEN = not constants.FULLSCREEN
                        pg.display.set_mode(pg.display.get_window_size(), (pg.FULLSCREEN if constants.FULLSCREEN else 0) | constants.FLAGS)
                    elif event.key == pg.K_ESCAPE:
                        pg.quit()
                        exit()
            if pg.K_UP in keys:
                selected_point = (selected_point + 2) % 3
            if pg.K_DOWN in keys:
                selected_point = (selected_point + 1) % 3
            if pg.K_LEFT in keys or pg.K_MINUS in keys:
                points[selected_point] = max(0, points[selected_point] - 1)
            if pg.K_RIGHT in keys or pg.K_EQUALS in keys:
                points[selected_point] += min(30 - sum(points), 1)
            window.fill((0, 0, 0))
            self.dialogger.update(keys)
            if stage == 0 and self.dialogger.curr_text == '':
                stage = 1
                target_soul_x = window.get_width() // 4
                self.dialogger.push_dialog('Give this soul some traits.')
            if stage == 1:
                texts = ['%d free points', '- wisdom   + %d +%.1f%c mana reg.', '- strength + %d +%.1f%c damage   ',
                         '- agility  + %d +%.1f%c speed    ']
                if sum(points) == 30:
                    texts.append('[PRESS Z TO CONTINUE]')
                texts[0] = texts[0] % (30 - sum(points))
                for i in range(3):
                    texts[i + 1] =  (texts[i + 1] %
                                     (points[i], round((points[i] + [self.point_wisdom,
                                                                    self.point_strength,
                                                                    self.point_agility][i]) ** 1.1 / 4, 1), '%'))
                for i, t in enumerate(texts):
                    if i == selected_point + 1:
                        color = (255, 255, 0)
                    else:
                        color = (255, 255, 255)
                    text = self.font.render(t, True, color)
                    text_rect = text.get_rect(center=(soul_x + window.get_width() // 2,
                                                      window.get_height() // 2 - 200 + i * 100))
                    window.blit(text, text_rect)
            if stage == 1 and pg.K_z in keys and sum(points) == 30:
                self.skill_tree(round(stage ** 1.5) + 2)
                stage = 3
                # target_soul_x = window.get_width() * 3 // 4
                # self.dialogger.dialog('If he/she must FIGHT, how will he/she DO that?')
                self.point_wisdom += points[0]
                self.point_strength += points[1]
                self.point_agility += points[2]
                points = [0, 0, 0]
            if stage == 2:
                texts = ['%d free points', '- melee  + %d %.0f%c damage', '- ranged + %d %.0f%c damage',
                         '- magic  + %d %.0f%c damage']
                if sum(points) == 30:
                    texts.append('[PRESS Z TO CONTINUE]')
                texts[0] = texts[0] % (30 - sum(points))
                for i in range(3):
                    pt = [self.point_melee, self.point_ranged, self.point_magic][i] + points[i] - 10
                    texts[i + 1] =  (texts[i + 1] %
                                     (points[i], round((1 - 0.91 ** (-pt)) * -100 if pt < 0 else pt ** 1.1 / 4, 1),
                                      '%'))
                for i, t in enumerate(texts):
                    if i == selected_point + 1:
                        color = (255, 255, 0)
                    else:
                        color = (255, 255, 255)
                    text = self.font.render(t, True, color)
                    text_rect = text.get_rect(center=(soul_x - window.get_width() // 2,
                                                      window.get_height() // 2 - 80 + i * 40))
                    window.blit(text, text_rect)
            if stage == 2 and pg.K_z in keys and sum(points) == 30:
                stage = 3
                target_soul_x = window.get_width() * 3 // 4
                self.dialogger.dialog('Alright, alright.',
                                      ('Start' if t == 0 else 'Continue') + ' your journey, traveller.')
                self.dialogger.update([])
                self.point_melee += points[0]
                self.point_ranged += points[1]
                self.point_magic += points[2]
                points = [0, 0, 0]
            if stage == 3 and self.dialogger.curr_text == '':
                break
            if stage == 0:
                col = self.get_color()
            elif stage == 1:
                col = self.get_color(w=points[0], s=points[1], a=points[2])
            else:
                col = self.get_color(ml=points[0], rg=points[1], mg=points[2])
            soul = self.get_surface(*col)
            soul = pg.transform.scale(soul, (120, 120))
            soul_rect = soul.get_rect(center=pg.display.get_surface().get_rect().center)
            soul_rect.centerx = soul_x
            soul_rect.centery += math.sin(tick / 50) * 50
            window.blit(soul, soul_rect)
            soul_x = (target_soul_x + soul_x) // 2
            pg.display.update()
            clock.tick(40)

    def skill_tree(self, point: int):
        window = pg.display.get_surface()
        self.font = pg.font.SysFont('dtm-mono', 36)
        self.font_s = pg.font.SysFont('dtm-mono', 18)
        skills = [
            [
                ['melee_demand'],
                ['the_fury', 'warrior_shield'],
                ['melee_reinforce_i', 'melee_reinforce_ii'],
                ['melee_reinforce_iii', 'melee_reinforce_iv'],
            ],
            [
                ['ranged_demand'],
                ['fast_throw', 'perfect_shot'],
                ['ranged_reinforce_i', 'ranged_reinforce_ii'],
                ['ranged_reinforce_iii', 'ranged_reinforce_iv'],
            ],
            [
                ['magic_demand'],
                ['healer', 'multi_user'],
                ['magic_reinforce_i', 'magic_reinforce_ii'],
                ['magic_reinforce_iii', 'magic_reinforce_iv']
            ]
        ]
        select_skill = []
        colours = [(255, 0, 255), (255, 255, 0), (0, 255, 255)]
        clock = pg.time.Clock()
        self.point_left += point
        while True:
            keys = []
            mouse = []
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()
                elif event.type == pg.KEYDOWN:
                    keys.append(event.key)
                    if event.key == pg.K_F4:
                        constants.FULLSCREEN = not constants.FULLSCREEN
                        pg.display.set_mode(pg.display.get_window_size(), (pg.FULLSCREEN if constants.FULLSCREEN else 0) | constants.FLAGS)
                    elif event.key == pg.K_ESCAPE:
                        pg.quit()
                        exit()
                    elif event.key == pg.K_z:
                        self.select_skill.extend(select_skill)
                        return
                elif event.type == pg.MOUSEBUTTONDOWN:
                    mouse.append(event.button)
            window.fill((0, 0, 0))
            for i, r_c in enumerate(skills):
                sy = window.get_height() * (i + 1) / 4
                for j, c in enumerate(r_c):
                    if not j or len([1 for s in r_c[j - 1] if s in select_skill or s in self.select_skill]):
                        x = 40 + j * 100
                        for k, s in enumerate(c):
                            y = sy - (len(c) - 1) * 40 + k * 80
                            self.skill_display((x - 30, y - 30), s, select=s in select_skill + self.select_skill)
                    else:
                        for s in c:
                            if s in select_skill:
                                select_skill.remove(s)
            for i, r_c in enumerate(skills):
                sy = window.get_height() * (i + 1) / 4
                for j, c in enumerate(r_c):
                    if not j or len([1 for s in r_c[j - 1] if s in select_skill or s in self.select_skill]):
                        x = 40 + j * 100
                        for k, s in enumerate(c):
                            y = sy - (len(c) - 1) * 40 + k * 80
                            self.skill_mouse((x - 30, y - 30), s, rc=colours[i])
                            rc = pg.Rect(x - 30, y - 30, 60, 60)
                            if rc.collidepoint(pg.mouse.get_pos()):
                                if 1 in mouse:
                                    if s not in self.select_skill:
                                        if s not in select_skill and len(select_skill) < self.point_left:
                                            select_skill.append(s)
                                        elif s in select_skill:
                                            select_skill.remove(s)
            t = self.font.render('Select %d skills' % (point - len(select_skill)) if (len(select_skill) < self.point_left)
                                 else 'Press Z to continue', True, (255, 255, 255))
            t_rect = t.get_rect(center=(window.get_width() // 2, 50))
            window.blit(t, t_rect)
            pg.display.update()
            clock.tick(40)
