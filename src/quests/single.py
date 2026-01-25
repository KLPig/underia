from underia import game, inventory
import physics

QUESTS: list['QuestBlock'] = []
QUEST_NAME: dict[str, 'QuestBlock'] = {}

class QuestRequirement:
    def __init__(self, **kwargs):
        self.name = ''
        self.father = None

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __bool__(self):
        return False

class ViewRequirement(QuestRequirement):
    def __bool__(self):
        return self.father is not None and self.father.read

class ItemRequirement(QuestRequirement):
    def __bool__(self):
        num = 1 if 'num' not in dir(self) else getattr(self, 'num')
        item = 1 if 'item' not in dir(self) else getattr(self, 'item')
        for k, v in game.get_game().player.inventory.items.items():
            if v >= num and k == item:
                return True
        return False

class BiomeRequirement(QuestRequirement):
    def __bool__(self):
        biome = '' if 'biome' not in dir(self) else getattr(self, 'biome')
        return game.get_game().get_biome() == biome

class NotebookRequirement(QuestRequirement):
    def __bool__(self):
        note = '' if 'note' not in dir(self) else getattr(self, 'note')
        return note in game.get_game().player.nts

class QuestBlock:
    def __init__(self, qid: str, **kwargs):
        self.qid = qid
        self.name = 'Unknown Quest'
        self.desc = ''
        self.content = ''
        self.reqs = []
        self.comp_req = []
        self.read = False
        self.pre: list[QuestBlock] = []
        self.req_num = 1
        self.pos = physics.Vector2D()
        self.disp = 'items_recipe_book'
        self.rarity = 1

        for k, v in kwargs.items():
            setattr(self, k, v)

        for r in self.reqs:
            r.father = self

        QUEST_NAME[qid] = self

    def add_req(self, req: QuestRequirement):
        self.reqs.append(req)
        req.father = self
        return self

    def add_child(self, child: "QuestBlock"):
        QUESTS.append(child)
        child.pre.append(self)
        return self

    def add_pre(self, pre: "QuestBlock"):
        self.pre.append(pre)
        QUESTS.append(pre)
        return self

    def __bool__(self):
        return len(self.comp_req) >= self.req_num and not len([1 for p in self.pre if not p])

    def update(self):
        for r in self.reqs:
            if r not in self.comp_req and r:
                self.comp_req.append(r)

        it = inventory.Inventory.Item(self.name, self.desc, '__quest_' + self.qid, self.rarity,
                                      specify_img=self.disp.removeprefix('items_'))
        it.mod = 'Quests'
        if self:
            it.desc = 'COMPLETED'
        else:
            it.desc = f'INSTANT({len(self.comp_req)}/{self.req_num})'
        for p in self.pre:
            if not p:
                it.desc = 'LOCKED - Incompleted Pre-quest'
                break
        inventory.ITEMS['__quest_' + self.qid] = it


    def write(self):
        pass