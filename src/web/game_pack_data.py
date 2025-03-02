from underia import game

class FirstConnectData:
    def __init__(self):
        self.seed = game.get_game().seed
        self.hallow = game.get_game().hallow_points