class Inventory:
    COMMON = 0
    UNCOMMON = 1
    RARE = 2
    VERY_RARE = 3
    EPIC = 4
    LEGENDARY = 5
    MYTHIC = 6
    SUPER_MYTHIC = 7
    GODLIKE = 8
    SUPER_GODLIKE = 9
    UNKNOWN = 114

    Rarity_Colors = [(255, 255, 255), (255, 255, 127), (150, 255, 127), (127, 255, 255), (255, 127, 127), (255, 165, 64), (128, 64, 128), (255, 200, 255), (255, 127, 255), (255, 200, 255), (255, 255, 255)]
    Rarity_Names = ["Common", "Uncommon", "Rare", "Very Rare", "Epic", "Legendary", "Mythic", "Super Mythic", "Godlike", "Super Godlike", "Unknown"]

    class Item:
        class Tag:
            def __init__(self, name: str, value: str):
                self.name = name
                self.value = value

            def get_all_items(self):
                return [item for item in ITEMS.values() if self.name in [tag.name for tag in item.tags]]

        def __init__(self, name, description, identifier: str, rarity: int = 0, tags: list = []):
            self.name = name
            self.desc = description
            self.id = identifier
            self.rarity = rarity
            self.tags = tags
            self.inner_id = 0

        def __str__(self):
            return f"#{self.inner_id}: {self.name} - {self.desc}"

TAGS = {
    'item': Inventory.Item.Tag('item', 'item'),
    'weapon': Inventory.Item.Tag('weapon', 'weapon'),
}
ITEMS = {
    'wooden_sword': Inventory.Item('Wooden Sword', '', 'wooden_sword', 0, [TAGS['item'], TAGS['weapon']]),
}

def setup():
    for i, item in enumerate(ITEMS.values()):
        item.inner_id = i

def get_item_by_id(item_id: int):
    return [item for item in ITEMS.values() if item.inner_id == item_id][0]

setup()
