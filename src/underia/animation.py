from underia import game

class Animation:
    def __init__(self, target: str, frames: list[int], nt: int = 10):
        self.target = target
        self.frames = frames
        self.cur = 0
        self.nt = nt
        self.tick = 0
        self.setup = False
        assert len(self.frames) > 0, "No frames provided for animation"

    def update(self):
        if not self.setup:
            self.setup = True
            game.get_game().graphics[self.target] = game.get_game().graphics[self.target + str(self.frames[0])]
        if self.tick >= self.nt:
            self.tick = 0
            self.cur = (self.cur + 1) % len(self.frames)
            game.get_game().graphics[self.target] = game.get_game().graphics[self.target + str(self.frames[self.cur])]
        else:
            self.tick += 1

ANIMATIONS = [
    Animation("items_spot", [1, 2, 3, 4], 15),
    Animation("items_dark_matter", [1, 2], 30),
    Animation("items_stone_of_faith", [1, 2, 3], 20),
    Animation("items_chaos_diamond", [1, 2, 3, 4, 5, 6, 7, 8], 15),
]