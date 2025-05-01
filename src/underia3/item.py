from underia import inventory

ITEMS = {
    'e_wood': inventory.Inventory.Item('Wood', description='', identifier='e_wood',
                                       rarity=0, tags=[inventory.TAGS['item']]),
    'e_feather': inventory.Inventory.Item('Feather', '', 'e_feather', 0,
                                          [inventory.TAGS['item']]),

    'e_wooden_hammer': inventory.Inventory.Item('Wooden Hammer', '', 'e_wooden_hammer',
                                                0, [inventory.TAGS['item'], inventory.TAGS['workstation']]),

    'e_wooden_sword': inventory.Inventory.Item('Wooden Sword', '', 'e_wooden_sword',
                                               0, [inventory.TAGS['item'], inventory.TAGS['weapon'],
                                                   inventory.TAGS['melee_weapon']]),

    'e_wooden_bow': inventory.Inventory.Item('Wooden Bow', '', 'e_wooden_bow', 0,
                                             [inventory.TAGS['item'], inventory.TAGS['weapon'],
                                              inventory.TAGS['bow']]),

    'e_wooden_arrow': inventory.Inventory.Item('Wooden Arrow', '', 'e_wooden_arrow', 0,
                                               [inventory.TAGS['item'], inventory.TAGS['ammo'],
                                                inventory.TAGS['ammo_arrow']]),

    'e_wooden_wand': inventory.Inventory.Item('Wooden Wand', '', 'e_wooden_wand', 0,
                                              [inventory.TAGS['item'], inventory.TAGS['weapon'],
                                               inventory.TAGS['magic_weapon'], inventory.TAGS['magic_element_life'],
                                               inventory.TAGS['magic_lv_1']]),
}

for k, v in ITEMS.items():
    inventory.ITEMS[k] = v

RECIPES = [
    inventory.Recipe({'e_wood': 12}, 'e_wooden_hammer'),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 16}, 'e_wooden_sword'),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 16}, 'e_wooden_bow'),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 3}, 'e_wooden_arrow', 20),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 16}, 'e_wooden_wand'),
]

inventory.RECIPES.extend(RECIPES)