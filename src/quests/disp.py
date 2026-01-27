import pygame as pg
from quests import single, build
from underia import styles, game
from physics import vector

class QuestDisplayer:
    def __init__(self):
        self.scroll = vector.Vector2D()
        self.instant = None
        self.gf = None

    def start(self):
        window = pg.display.get_surface()
        presence = True
        width, height = window.get_size()
        self.gf = game.get_game().graphics['background_stars']
        self.gf = pg.transform.scale(self.gf, (120, 120))

        while presence:

            mouse = False
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    presence = False
                elif event.type == pg.MOUSEWHEEL:
                    self.scroll += (event.x * 5, event.y * -5)
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == pg.BUTTON_LEFT:
                        mouse = True
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        presence = False

            window.fill((0, 0, 0))

            ax, ay = int(-self.scroll[0] % 120), int(-self.scroll[1] % 120)
            for dx in range(-400 + ax, 400 + width, 120):
                for dy in range(-400 + ay, 400 + height, 120):
                    window.blit(self.gf, (dx, dy))

            for q in single.QUESTS:
                q.update()
                rct = pg.Rect(*(-self.scroll + q.pos), 80, 80)
                if rct.collidepoint(pg.mouse.get_pos()):
                    for dq in single.QUESTS:
                        if dq in q.pre:
                            pg.draw.line(window, (100, 0, 0), (-self.scroll + q.pos + (40, 40)).to_value(),
                                         (-self.scroll + dq.pos + (40, 40)).to_value(), 10)
                        if q in dq.pre:
                            pg.draw.line(window, (0, 100, 0), (-self.scroll + q.pos + (40, 40)).to_value(),
                                         (-self.scroll + dq.pos + (40, 40)).to_value(), 10)

            for q in single.QUESTS:
                styles.item_display(*(-self.scroll + q.pos), '__quest_' + q.qid, '', '', 1, bool(q),
                                    window, )

            for q in single.QUESTS:
                styles.item_mouse(*(-self.scroll + q.pos), '__quest_' + q.qid, '', '', 1, 'left',
                                    window, mp=pg.mouse.get_pos())


            if self.instant is not None:
                pg.draw.rect(window, (0, 0, 0), (width // 8, height // 8, width * 6 // 8, height * 6 // 8))
                pg.draw.rect(window, (255, 255, 255), (width // 8, height // 8, width * 6 // 8, height * 6 // 8),
                            10)

                ft = game.get_game().displayer.font.render(self.instant.name, True, (255, 255, 255))
                ftr = ft.get_rect(center=(width / 2, height // 8 + 50))
                window.blit(ft, ftr)

                for i, ln in enumerate(self.instant.content.split('\n')):
                    ft = game.get_game().displayer.font.render(ln, True, (255, 255, 255))
                    ftr = ft.get_rect(midleft=(width // 8 + 50, height // 8 + 100 + 40 * i))
                    window.blit(ft, ftr)

                if mouse:
                    self.instant = None
                    continue

            for q in single.QUESTS:
                rct = pg.Rect(*(-self.scroll + q.pos), 80, 80)
                if rct.collidepoint(pg.mouse.get_pos()):
                    if mouse:
                        q.read = True
                        self.instant = q

            pg.display.update()

DISP = QuestDisplayer()
