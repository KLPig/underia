import pygame as pg

from resources import position
from underia import game
import constants
from visual import draw


class Effect:
    def update(self, window) -> bool:
        return False


def pointed_curve(colour: tuple[int, int, int], pts: list[tuple[int, int]], width: int = 10, salpha: int = 255,
                  target: pg.Surface = None):
    if target is None:
        displayer = game.get_game().displayer.canvas
    else:
        displayer = target
    num_points = len(pts)

    if num_points < 2:
        return

    for i in range(num_points - 1):
        alpha = salpha
        current_colour = (colour[0], colour[1], colour[2], 255)
        sx, sy = position.displayed_position(pts[i]) if target is None else pts[i]
        ex, ey = position.displayed_position(pts[i + 1]) if target is None else pts[i + 1]
        if (ex - sx) ** 2 + (ey - sy) ** 2 > 1000000:
            continue
        if constants.USE_ALPHA and alpha < 255:
            s = pg.Surface((abs(ex - sx) + width, abs(ey - sy) + width), pg.SRCALPHA)
            ax, ay = min(sx, ex), min(sy, ey)
            draw.line(s, current_colour, (sx + width // 2 - ax, sy + width // 2 - ay),
                      (ex + width // 2 - ax, ey + width // 2 - ay), width=width)
            s.set_alpha(alpha)
            displayer.blit(s, (min(sx, ex), min(sy, ey)))
        else:
            draw.line(displayer, current_colour, (sx, sy), (ex, ey), width)
