from underia import inventory, Recipe

# items

ITEMS = {
    'e_wood': inventory.Inventory.Item('Wood', description='', identifier='e_wood',
                                       rarity=0, tags=[inventory.TAGS['item']]),
    'e_feather': inventory.Inventory.Item('Feather', '', 'e_feather', 0,
                                          [inventory.TAGS['item']]),
    'e_poison_powder': inventory.Inventory.Item('Poison Powder', '', 'e_poison_powder', 0,
                                        [inventory.TAGS['item']]),
    'lychee_shard': inventory.Inventory.Item('Lychee Shard', 'Lychee? How can I lychee!', 'lychee_shard',
                                             1, [inventory.TAGS['item']]),
    'purple_clay': inventory.Inventory.Item('Purple Clay', 'Susan, or grab tight purple clay.', 'purple_clay', 2,
                                  [inventory.TAGS['item']]),
    'carrion': inventory.Inventory.Item('Carrion', '', 'carrion', 2, [inventory.TAGS['item']]),

    'wooden_rope': inventory.Inventory.Item('Wooden Rope', '', 'wooden_rope', 0, [inventory.TAGS['item']]),

    'feather_amulet': inventory.Inventory.Item('Feather Amulet', 'Resistant to tree curse.\n-20% air resistance\n-10kg\n+20% speed',
                                               'feather_amulet', 1, [inventory.TAGS['item'], inventory.TAGS['accessory']]),
    'poise_necklace': inventory.Inventory.Item('Poise Necklace', 'Resistant to snow curse.\n+60 additional maximum mana\n+10 magic defense',
                                               'poise_necklace', 1, [inventory.TAGS['item'], inventory.TAGS['accessory']]),
    'poison_shackle': inventory.Inventory.Item('Poison Shackle', '200kg\n-10/sec regeneration\n+50% damage\n+40 touching defense',
                                                'poison_shackle', 2, [inventory.TAGS['item'], inventory.TAGS['accessory']]),
    'healthy_product': inventory.Inventory.Item('Healthy Product', '+15/sec regeneration\nWhen HP < 50%, -30/sec regeneration.',
                                                'healthy_product', 2,
                                               [inventory.TAGS['item'], inventory.TAGS['accessory']]),
    'toxic_wing': inventory.Inventory.Item('Toxic Wing', '+80% speed\n-20% air resistance\n50% wing control\n-10/sec regeneration',
                                 'toxic_wing', 2, [inventory.TAGS['item'], inventory.TAGS['accessory']]),
    'clear_crystal__snow': inventory.Inventory.Item('Clear Crystal: Snow',
                                                    'When MP > 25%, -5/sec mana regeneration\n'
                                                    'When MP > 50%, -5/sec mana regeneration\n'
                                                    'When MP > 75%, -5/sec mana regeneration\n'
                                                    'When MP > 100%, -5/sec mana regeneration\n'
                                                    'When MP > 25%, +3/sec regeneration\n'
                                                    'When MP > 50%, +3/sec regeneration\n'
                                                    'When MP > 75%, +3/sec regeneration\n'
                                                    'When MP > 100%, +3/sec regeneration',
                                                      'clear_crystal__snow', 2, [inventory.TAGS['item'], inventory.TAGS['accessory']]),

    'poison_quiver': inventory.Inventory.Item('Poison Quiver',
                                              'Resistant to snow curse.\n+20 touching defense\n'
                                              '+30 magic defense\n+20% ranged damage\n+10% critical\n+50% speed', 'poison_quiver', 2,
                                              [inventory.TAGS['item'], inventory.TAGS['accessory'], inventory.TAGS['major_accessory']]),

    'e_wooden_hammer': inventory.Inventory.Item('Wooden Hammer', '', 'e_wooden_hammer',
                                                0, [inventory.TAGS['item'], inventory.TAGS['workstation']]),

    'e_wooden_sword': inventory.Inventory.Item('Wooden Sword', '', 'e_wooden_sword',
                                               0, [inventory.TAGS['item'], inventory.TAGS['weapon'],
                                                   inventory.TAGS['melee_weapon']]),
    'lychee_sword': inventory.Inventory.Item('Lychee Sword', 'Tough sword.',
                                               'lychee_sword', 1,
                                               [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['melee_weapon']]),
    'lychee_pike': inventory.Inventory.Item('Lychee Pike', '', 'lychee_pike', 1,
                                             [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['melee_weapon']]),
    'purple_clay_broad_blade': inventory.Inventory.Item('Purple Clay Broad Blade', '', 'purple_clay_broad_blade', 2,
                                                        [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['melee_weapon']]),
    'poise_blade': inventory.Inventory.Item('Poise Blade', 'Give nearby enemies poisoned.', 'poise_blade', 2,
                                            [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['melee_weapon']]),


    'e_wooden_bow': inventory.Inventory.Item('Wooden Bow', '', 'e_wooden_bow', 0,
                                             [inventory.TAGS['item'], inventory.TAGS['weapon'],
                                              inventory.TAGS['bow']]),
    'lychee_bow': inventory.Inventory.Item('Lychee Bow', 'Bow with lychee arrows.', 'lychee_bow', 1,
                                           [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['bow']]),
    'e_pistol': inventory.Inventory.Item('Pistol', '', 'e_pistol', 2, [inventory.TAGS['item'], inventory.TAGS['weapon'],
                                                                       inventory.TAGS['gun']]),
    'purple_clay_kuangkuang': inventory.Inventory.Item('Purple Clay Kuangkuang', '', 'purple_clay_kuangkuang', 2,
                                                         [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['bow']]),

    'e_wooden_arrow': inventory.Inventory.Item('Wooden Arrow', '', 'e_wooden_arrow', 0,
                                               [inventory.TAGS['item'], inventory.TAGS['ammo'],
                                                inventory.TAGS['ammo_arrow']]),
    'e_bullet': inventory.Inventory.Item('Bullet', '', 'e_bullet', 0, [inventory.TAGS['item'], inventory.TAGS['ammo'],
                                                                     inventory.TAGS['ammo_bullet']]),

    'e_wooden_wand': inventory.Inventory.Item('Wooden Wand', '', 'e_wooden_wand', 0,
                                              [inventory.TAGS['item'], inventory.TAGS['weapon'],
                                               inventory.TAGS['magic_weapon'], inventory.TAGS['magic_element_life'],
                                               inventory.TAGS['magic_lv_1']]),
    'lychee_wand': inventory.Inventory.Item('Lychee Wand', '', 'lychee_wand', 1,
                                  [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['magic_weapon'],
                                   inventory.TAGS['magic_element_life'], inventory.TAGS['magic_lv_1']]),
}

for k, v in ITEMS.items():
    inventory.ITEMS[k] = v

RECIPES = [
    inventory.Recipe({'e_wood': 12}, 'e_wooden_hammer'),
    inventory.Recipe({'e_wood': 3, 'e_wooden_hammer': 1}, 'wooden_rope'),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 16}, 'e_wooden_sword'),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 8, 'wooden_rope': 3}, 'e_wooden_bow'),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 3}, 'e_wooden_arrow', 20),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 16}, 'e_wooden_wand'),
    inventory.Recipe({'e_wooden_hammer': 1, 'wooden_rope': 2, 'e_feather': 10}, 'feather_amulet'),
    inventory.Recipe({'e_wooden_hammer': 1, 'wooden_rope': 2, 'e_poison_powder': 20}, 'poise_necklace'),

    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 6, 'e_feather': 5, 'lychee_shard': 2}, 'lychee_sword'),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 12, 'lychee_shard': 3}, 'lychee_pike'),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 3, 'e_feather': 10, 'wooden_rope': 5, 'lychee_shard': 2}, 'lychee_bow'),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 8, 'lychee_shard': 4}, 'lychee_wand'),

    inventory.Recipe({'e_wooden_hammer': 1, 'lychee_shard': 4, 'purple_clay': 8}, 'purple_clay_broad_blade'),
    inventory.Recipe({'e_wooden_hammer': 1, 'lychee_shard': 1, 'purple_clay': 2}, 'e_bullet', 200),
    inventory.Recipe({'e_wooden_hammer': 1, 'lychee_shard': 2, 'purple_clay': 6, 'e_feather': 2}, 'e_pistol'),
    inventory.Recipe({'e_wooden_hammer': 1, 'lychee_shard': 4, 'purple_clay': 5, 'e_feather': 10}, 'purple_clay_kuangkuang'),

    inventory.Recipe({'e_wooden_hammer': 1, 'lychee_shard': 5, 'poison_powder': 30, 'carrion': 10}, 'poison_quiver'),
    inventory.Recipe({'e_wooden_hammer': 1, 'lychee_shard': 8, 'poison_powder': 10, 'carrion': 5}, 'poison_shackle'),
    inventory.Recipe({'e_wooden_hammer': 1, 'poison_powder': 40, 'carrion': 10}, 'healthy_product'),
    inventory.Recipe({'e_wooden_hammer': 1, 'lychee_shard': 20, 'poison_powder': 10}, 'toxic_wing'),
    inventory.Recipe({'e_wooden_hammer': 1, 'lychee_shard': 20, 'purple_clay': 20, 'poison_powder': 50, 'carrion': 10}, 'clear_crystal__snow'),

]

inventory.RECIPES.extend(RECIPES)