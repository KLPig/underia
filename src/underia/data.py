from underia import player_profile, game

class GameData:
    def __init__(self, pf: player_profile.PlayerProfile, time=None):
        self.lv = pf.stage
        self.col = pf.get_color()
        self.time = game.get_game().game_time if time is None else time
