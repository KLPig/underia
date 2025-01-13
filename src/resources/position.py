from src.underia import game


def absolute_position(pos):
    ax, ay = game.get_game().get_anchor()
    return (pos[0] * game.get_game().player.get_screen_scale() + ax,
            pos[1] * game.get_game().player.get_screen_scale() + ay)


def relative_position(pos):
    ax, ay = game.get_game().get_anchor()
    return ((pos[0] - ax) / game.get_game().player.get_screen_scale(),
            (pos[1] - ay) / game.get_game().player.get_screen_scale())


def displayed_position(pos):
    ax, ay = game.get_game().get_anchor()
    dis = game.get_game().displayer
    return ((pos[0] - ax) / game.get_game().player.get_screen_scale() + dis.SCREEN_WIDTH // 2,
            (pos[1] - ay) / game.get_game().player.get_screen_scale() + dis.SCREEN_HEIGHT // 2)


def real_position(pos):
    ax, ay = game.get_game().get_anchor()
    dis = game.get_game().displayer
    return ((pos[0] - dis.SCREEN_WIDTH // 2) * game.get_game().player.get_screen_scale() + ax,
            (pos[1] - dis.SCREEN_HEIGHT // 2) * game.get_game().player.get_screen_scale() + ay)
