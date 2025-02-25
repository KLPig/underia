from underia import player_profile

class GameData:
    def __init__(self, pf: player_profile.PlayerProfile):
        self.lv = pf.stage
        self.col = pf.get_color()
