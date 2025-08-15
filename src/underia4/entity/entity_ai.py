from underia4.physics import mover

class EntityAI:
    THIS_CATEGORY = 1 << 0
    NEUTRAL_CATEGORY = 0
    ENEMY_CATEGORY = 0

    SPEED = 20
    SIGHT_RADIUS = 100

    def get_category(self, target_category):
        return [] # TODO: Implement getting targets

    def choose_target(self, targets):
        return None # TODO: Implement choosing target

    def __init__(self, pos, **kwargs):
        self.obj = mover.Mover(pos)
        for k, v in kwargs.items():
            setattr(self, k, v)


