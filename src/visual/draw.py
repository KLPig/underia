import pygame as pg

def line(window, color, start_pos, end_pos, width=1):
    if start_pos == end_pos:
        pg.draw.circle(window, color, start_pos, width)
        return
    gradient = (end_pos[1] - start_pos[1] + 10 ** -5) / (end_pos[0] - start_pos[0] + 10 ** -5)
    if (start_pos[0] < 0 or start_pos[0] > window.get_width()) and (end_pos[0] < 0 or end_pos[0] > window.get_width()) and \
        (start_pos[1] < 0 or start_pos[1] > window.get_height()) and (end_pos[1] < 0 or end_pos[1] > window.get_height()):
        return
    if start_pos[0] < 0:
        start_pos = (0, int(start_pos[1] - gradient * start_pos[0]))
    if end_pos[0] < 0:
        end_pos = (0, int(end_pos[1] - gradient * end_pos[0]))
    if start_pos[0] > window.get_width():
        start_pos = (window.get_width(), int(start_pos[1] + (gradient * (window.get_width() - start_pos[0]))))
    if end_pos[0] > window.get_width():
        end_pos = (window.get_width(), int(end_pos[1] + (gradient * (window.get_width() - end_pos[0]))))
    gradient = (end_pos[1] - start_pos[1] + 10 ** -5) / (end_pos[0] - start_pos[0] + 10 ** -5)
    if start_pos[1] < 0:
        start_pos = (int(start_pos[0] - (1 / gradient) * start_pos[1]), 0)
    if end_pos[1] < 0:
        end_pos = (int(end_pos[0] - (1 / gradient) * end_pos[1]), 0)
    if start_pos[1] > window.get_height():
        start_pos = (int(start_pos[0] + ((1 / gradient) * (window.get_height() - start_pos[1]))), window.get_height())
    if end_pos[1] > window.get_height():
        end_pos = (int(end_pos[0] + ((1 / gradient) * (window.get_height() - end_pos[1]))), window.get_height())
    start_pos = (max(0, min(window.get_width(), start_pos[0])), max(0, min(window.get_height(), start_pos[1])))
    end_pos = (max(0, min(window.get_width(), end_pos[0])), max(0, min(window.get_height(), end_pos[1])))
    pg.draw.line(window, color, start_pos, end_pos, int(width))

def l_rect(window, color, st_pos, en_pos, width=1):
    sx, sy = st_pos
    ex, ey = en_pos
    line(window, color, (sx, sy), (sx, ey), width)
    line(window, color, (sx, ey), (ex, ey), width)
    line(window, color, (ex, ey), (ex, sy), width)
    line(window, color, (sx, sy), (ex, sy), width)