from underia import game, player

class FirstConnectData:
    def __init__(self, pid, profile):
        self.seed = game.get_game().seed
        self.fun = game.get_game().fun
        self.hallow = game.get_game().hallow_points
        self.wither = game.get_game().wither_points
        self.pid = pid
        self.profile = profile

class SinglePlayerData:
    def __init__(self, player_id, p: player.Player):
        self.player_id = player_id
        self.pos = p.obj.pos
        self.hp_sys = p.hp_sys
        self.col = p.profile.get_color()

class EntityDisplays:
    def __init__(self):
        self.display = []
        for e in game.get_game().entities:
            self.display.append(e.dump_display())
