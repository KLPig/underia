import pygame as pg
import underia
import resources
import constants

class Dialogger:
    def __init__(self, font_size: int = 64, rect: pg.Rect = None, with_border: bool = False,
                 target_surface: pg.Surface = None, speed: float = 10):
        self.font = pg.font.Font(resources.get_path('assets/dtm-mono.otf' if constants.LANG != 'zh' else 'assets/fz-pixel.ttf'), font_size)
        self.word_queue = []
        self.curr_text = ''
        self.curr_idx = 0
        self.s_timer = 0
        self.auto_skip = True
        self.dialog_rect = pg.Rect(0, 0, 400, 300)
        self.with_border = False
        self.speed = speed
        if rect is not None:
            self.dialog_rect = rect
        if with_border:
            self.with_border = True
        self.size = font_size
        self.target_surface = target_surface
        if target_surface is None:
            self.target_surface = underia.get_game().displayer.canvas

    def push_dialog(self, *args: str):
        self.word_queue.extend(args)

    def dialog(self, *args: str):
        self.word_queue.clear()
        self.word_queue.extend(args)

    def update(self, buttons_down: list):
        if self.curr_idx >= len(self.curr_text):
            if pg.K_z in buttons_down or self.curr_text == '':
                if len(self.word_queue):
                    self.curr_text = self.word_queue.pop(0)
                else:
                    self.curr_text = ''
                self.curr_idx = 0
        if self.auto_skip and len(self.curr_text) <= self.curr_idx:
            if self.s_timer < int(self.speed * 45):
                self.s_timer += 1
            else:
                if len(self.word_queue):
                    self.curr_text = self.word_queue.pop(0)
                else:
                    self.curr_text = ''
                self.curr_idx = 0
                self.s_timer = 0
        elif self.s_timer > 0:
            self.s_timer -= 1
        elif self.curr_idx < len(self.curr_text):
            self.curr_idx += 1
            if self.curr_idx == len(self.curr_text):
                self.s_timer = 0
            c = self.curr_text[self.curr_idx - 1]
            if c == ' ':
                self.s_timer = int(self.speed * 3)
            elif c in ['\n', '\r', '.', '。', '!', '?', '！', '？']:
                self.s_timer = int(self.speed * 10)
            elif c in [',', '，', ';', '；', ':', '：', '、']:
                self.s_timer = int(self.speed * 5)
            else:
                self.s_timer = int(self.speed)
        if pg.K_x in buttons_down:
            self.curr_idx = len(self.curr_text)
        pg.draw.rect(self.target_surface, (0, 0, 0), self.dialog_rect)
        if self.with_border:
            pg.draw.rect(self.target_surface, (255, 255, 255), self.dialog_rect, self.size // 10)
        pre = self.font.render('*', True, (255, 255, 255))
        self.target_surface.blit(pre, (self.dialog_rect.left + self.size // 2, self.dialog_rect.top + self.size // 2))
        txts = self.curr_text[:self.curr_idx].split('\n')
        for i, txt in enumerate(txts):
            text = self.font.render(txt, True, (255, 255, 255))
            self.target_surface.blit(text, (self.dialog_rect.left + self.size * 5 // 2,
                                            self.dialog_rect.top + self.size // 2 + i * (self.size + 10)))

    def is_done(self):
        return not len(self.curr_text)