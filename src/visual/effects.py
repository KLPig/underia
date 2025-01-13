import pygame as pg

from src.resources import position
from src.underia import game


class Effect:
    def update(self, window) -> bool:
        return False


def pointed_curve(colour: tuple[int, int, int], pts: list[tuple[int, int]], width: int = 10, salpha: int = 255):
    displayer = game.get_game().displayer
    num_points = len(pts)

    if num_points < 2:
        return

    for i in range(num_points - 1):
        alpha = salpha
        current_colour = (colour[0], colour[1], colour[2], 255)
        sx, sy = position.displayed_position(pts[i])
        ex, ey = position.displayed_position(pts[i + 1])
        if (ex - sx) ** 2 + (ey - sy) ** 2 > 1000000:
            continue
        s = pg.Surface((abs(ex - sx) + width, abs(ey - sy) + width), pg.SRCALPHA)
        ax, ay = min(sx, ex), min(sy, ey)
        for aax in range(-width // 2, width // 2 + 1, 1):
            for aay in range(-width // 2, width // 2 + 1, 1):
                pg.draw.aaline(s, current_colour, (aax + sx + width // 2 - ax, aay + sy + width // 2 - ay),
                               (aax + ex + width // 2 - ax, aay + ey + width // 2 - ay))
        s.set_alpha(alpha)
        displayer.canvas.blit(s, (min(sx, ex), min(sy, ey)))
