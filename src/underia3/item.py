from underia import inventory

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
    'magic_fur': inventory.Inventory.Item('Magic Fur', 'Fur that can cast spells.', 'e_magic_fur', 1,
                                           [inventory.TAGS['item']]),
    'purple_clay': inventory.Inventory.Item('Purple Clay', 'Susan, or grab tight purple clay.', 'purple_clay', 2,
                                  [inventory.TAGS['item']]),
    'brainrot': inventory.Inventory.Item('Brainrot', 'You feel your brain rotting.', 'brainrot', 1, [inventory.TAGS['item']]),
    'mystery_shard': inventory.Inventory.Item('Mystery Shard', '', 'mystery_shard', 1, [inventory.TAGS['item']]),
    'mystery_soul': inventory.Inventory.Item('Mystery Soul', '', 'mystery_soul', 1, [inventory.TAGS['item']]),
    'carrion': inventory.Inventory.Item('Carrion', '', 'carrion', 2, [inventory.TAGS['item']]),

    'lychee_core_shard': inventory.Inventory.Item('Lychee Core Shard', '', 'lychee_core_shard', 3, [inventory.TAGS['item']]),

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
                                                    'Using mana to gain regeneration.[cmd]\n'
                                                    'When MP > 25%, -5/sec mana regeneration\n'
                                                    'When MP > 50%, -5/sec mana regeneration\n'
                                                    'When MP > 75%, -5/sec mana regeneration\n'
                                                    'When MP > 100%, -5/sec mana regeneration\n'
                                                    'When MP > 25%, +10/sec regeneration\n'
                                                    'When MP > 50%, +10/sec regeneration\n'
                                                    'When MP > 75%, +10/sec regeneration\n'
                                                    'When MP > 100%, +10/sec regeneration',
                                                      'clear_crystal__snow', 2, [inventory.TAGS['item'], inventory.TAGS['accessory']]),

    'lychee_core': inventory.Inventory.Item('Lychee Core',
                                            'Using mana to gain speed and critical.[cmd]\n'
                                            'When MP > 25%, -5/sec mana regeneration\n'
                                            'When MP > 50%, -5/sec mana regeneration\n'
                                            'When MP > 75%, -5/sec mana regeneration\n'
                                            'When MP > 100%, -5/sec mana regeneration\n'
                                            'When MP > 25%, +30% speed\n'
                                            'When MP > 50%, +30% speed\n'
                                            'When MP > 75%, +30% speed\n'
                                            'When MP > 100%, +30% speed\n'
                                            'When MP > 25%, +8% critical\n'
                                            'When MP > 50%, +8% critical\n'
                                            'When MP > 75%, +8% critical\n'
                                            'When MP > 100%, +8% critical', 'lychee_core', 3,
                                            [inventory.TAGS['item'], inventory.TAGS['accessory']]),

    'purple_clay_sheath': inventory.Inventory.Item('Purple Clay Sheath',
                                                   'Resistant to tree curse.\n50kg\n'
                                                   '+20% speed\n+50 touching defense\n+80 magic defense\n'
                                                   '+25% melee damage', 'purple_clay_sheath', 2,
                                                    [inventory.TAGS['item'], inventory.TAGS['accessory'], inventory.TAGS['major_accessory']]),
    'poison_quiver': inventory.Inventory.Item('Poison Quiver',
                                              'Resistant to snow curse.\n+20 touching defense\n'
                                              '+30 magic defense\n+20% ranged damage\n+10% critical\n+50% speed', 'poison_quiver', 2,
                                              [inventory.TAGS['item'], inventory.TAGS['accessory'], inventory.TAGS['major_accessory']]),

    'e_wooden_hammer': inventory.Inventory.Item('Wooden Hammer', '', 'e_wooden_hammer',
                                                0, [inventory.TAGS['item'], inventory.TAGS['workstation']]),
    'hammer_of_rational': inventory.Inventory.Item('Hammer of Rational', '', 'hammer_of_rational',
                                                   2, [inventory.TAGS['item'], inventory.TAGS['workstation']]),

    'book': inventory.Inventory.Item('Book', '', 'book', 0,
                                     [inventory.TAGS['item']]),
    'magic_pen': inventory.Inventory.Item('Magic Pen', 'Write on books',
                                           'magic_pen', 1, [inventory.TAGS['item']]),

    'e_wooden_sword': inventory.Inventory.Item('Wooden Sword', '', 'e_wooden_sword',
                                               0, [inventory.TAGS['item'], inventory.TAGS['weapon'],
                                                   inventory.TAGS['melee_weapon']]),
    'feather_sword': inventory.Inventory.Item('Feather Sword', 'Shoots small feathers, deal 12% damage, penetrate 18 defense.',
                                               'feather_sword', 2,
                                               [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['melee_weapon']]),
    'lychee_sword': inventory.Inventory.Item('Lychee Sword', 'Tough sword.',
                                               'lychee_sword', 1,
                                               [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['melee_weapon']]),
    'lychee_pike': inventory.Inventory.Item('Lychee Pike', '', 'lychee_pike', 1,
                                             [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['melee_weapon']]),
    'purple_clay_broad_blade': inventory.Inventory.Item('Purple Clay Broad Blade', '', 'purple_clay_broad_blade', 2,
                                                        [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['melee_weapon']]),
    'poise_blade': inventory.Inventory.Item('Poise Blade', 'Give nearby enemies poisoned.', 'poise_blade', 2,
                                            [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['melee_weapon']]),

    'mystery_sword': inventory.Inventory.Item('Mystery Sword', '', 'mystery_sword', 1,
                                              [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['melee_weapon']]),
    'mystery_swiftsword': inventory.Inventory.Item('Mystery Swiftsword', '', 'mystery_swiftsword', 2,
                                                   [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['melee_weapon']]),
    'mystery_spear': inventory.Inventory.Item('Mystery Spear', '', 'mystery_spear', 1,
                                              [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['melee_weapon']]),


    'intestinal_sword': inventory.Inventory.Item('Intestinal Sword', '', 'intestinal_sword', 3,
                                                  [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['melee_weapon']]),
    'proof': inventory.Inventory.Item('Proof', 'That\'s why it comes true.', 'proof', 3,
                                      [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['melee_weapon']]),
    'observe': inventory.Inventory.Item('Observe', 'Watch, and check.', 'observe', 3,
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
    'lychee_piercer': inventory.Inventory.Item('Lychee Piercer', 'Freeze nearby entities.', 'lychee_piercer', 3,
                                               [inventory.TAGS['item']]),
    'lychee_twinblade': inventory.Inventory.Item('Lychee Twinblade', 'SEALED[I]', 'lychee_twinblade', 3,
                                                 [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['knife']]),
    'poise_bow': inventory.Inventory.Item('Poise Bow', '', 'poise_bow', 1,
                                           [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['bow']]),
    'poise_submachine_gun': inventory.Inventory.Item('Poise Submachine Gun', '', 'poise_submachine_gun', 1,
                                                     [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['gun']]),

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
    'lychee_spike': inventory.Inventory.Item('Lychee Spike', 'Summon a lychee spike', 'lychee_spike', 1,
                                              [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['magic_weapon'],
                                               inventory.TAGS['magic_element_water'], inventory.TAGS['magic_lv_1']]),

    'lychee': inventory.Inventory.Item('Lychee', '...even if you don\'t know how it was made.\n'
                                                 'Under the "bless" of the trees, summon the lychee king.\n'
                                                 'Suggested level: 2(uncommon)', 'lychee', 2,
                                       [inventory.TAGS['item']]),
    'intestine': inventory.Inventory.Item('Intestine', '...if you want it to be a natural taste.\n'
                                                       'Under the "bless" of the snows, summon the large intestine.\n'
                                                       'Suggested level: 2(uncommon)', 'intestine', 2,
                                       [inventory.TAGS['item']]),

    'hoverplume_headgear': inventory.Inventory.Item('Hoverplume Head Gear', '5 armor\n+18% speed', 'hoverplume_headgear', 1,
                                                       [inventory.TAGS['item'], inventory.TAGS['head'], inventory.TAGS['accessory']]),
    'hoverplume_back': inventory.Inventory.Item('Hoverplume Back', '6 armor\n+12% speed', 'hoverplume_back', 1,
                                                  [inventory.TAGS['item'], inventory.TAGS['body'], inventory.TAGS['accessory']]),
    'hoverplume_kneepads': inventory.Inventory.Item('Hoverplume Kneepads', '4 armor\n+25% speed', 'hoverplume_kneepads', 1,
                                                      [inventory.TAGS['item'], inventory.TAGS['leg'], inventory.TAGS['accessory']]),
    '_hoverplume_set_bonus': inventory.Inventory.Item('Hoverplume Armor Set Bonus', '-20% air resistance\n+5% dodge rate', '_hoverplume_set_bonus',
                                                      1, [inventory.TAGS['item'], inventory.TAGS['accessory']], specify_img='null'),

    'thaumaturgy': inventory.Inventory.Item('Thaumaturgy', 'Ring of spirit.', 'thaumaturgy', 1,
                                            [inventory.TAGS['item'], inventory.TAGS['accessory']]),
    'pluma_thaumaturgy': inventory.Inventory.Item('Pluma Thaumaturgy', '+8% dodge rate\nReleases feather according to speed, deal melee damage.',
                                                  'pluma_thaumaturgy', 2,
                                         [inventory.TAGS['item'], inventory.TAGS['accessory']]),

    '_rune_altar': inventory.Inventory.Item('Rune Altar', 'Require to be close to rune altar.', '_rune_altar', 1,
                                            [inventory.TAGS['item']]),

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
    inventory.Recipe({'e_wooden_hammer': 1, 'magic_feather': 7}, 'magic_pen', 3),

    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 40, 'e_feather': 20}, 'hoverplume_headgear'),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 20, 'e_feather': 45}, 'hoverplume_back'),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 30, 'e_feather': 30}, 'hoverplume_kneepads'),

    inventory.Recipe({'book': 1, 'magic_pen': 1, 'lychee_shard': 8}, 'lychee_spike'),

    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 6, 'e_feather': 5, 'lychee_shard': 2}, 'lychee_sword'),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 12, 'lychee_shard': 3}, 'lychee_pike'),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 3, 'e_feather': 10, 'wooden_rope': 5, 'lychee_shard': 2}, 'lychee_bow'),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 8, 'lychee_shard': 4}, 'lychee_wand'),

    inventory.Recipe({'e_wooden_hammer': 1, 'lychee_shard': 4, 'purple_clay': 8}, 'purple_clay_broad_blade'),
    inventory.Recipe({'e_wooden_hammer': 1, 'lychee_shard': 1, 'purple_clay': 2}, 'e_bullet', 200),
    inventory.Recipe({'e_wooden_hammer': 1, 'lychee_shard': 2, 'purple_clay': 6, 'e_feather': 2}, 'e_pistol'),
    inventory.Recipe({'e_wooden_hammer': 1, 'lychee_shard': 4, 'purple_clay': 5, 'e_feather': 10}, 'purple_clay_kuangkuang'),
    inventory.Recipe({'e_wooden_hammer': 1, 'lychee_shard': 15, 'purple_clay': 15}, 'purple_clay_sheath'),

    inventory.Recipe({'e_wooden_hammer': 1, 'lychee_shard': 5, 'e_poison_powder': 30, 'carrion': 10}, 'poison_quiver'),
    inventory.Recipe({'e_wooden_hammer': 1, 'lychee_shard': 8, 'e_poison_powder': 10, 'carrion': 5}, 'poison_shackle'),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_poison_powder': 40, 'carrion': 10}, 'healthy_product'),
    inventory.Recipe({'e_wooden_hammer': 1, 'lychee_shard': 20, 'e_poison_powder': 10}, 'toxic_wing'),
    inventory.Recipe({'e_wooden_hammer': 1, 'lychee_shard': 20, 'purple_clay': 20, 'e_poison_powder': 50, 'carrion': 10}, 'clear_crystal__snow'),

    inventory.Recipe({'e_wooden_hammer': 1, 'lychee_shard': 20, 'e_poison_powder': 20}, 'poise_bow'),
    inventory.Recipe({'e_wooden_hammer': 1, 'lychee_shard': 20, 'e_poison_powder': 40, 'carrion': 10}, 'poise_submachine_gun'),

    inventory.Recipe({'e_wooden_hammer': 1, 'mystery_shard': 45, 'brainrot': 20}, 'mystery_sword'),
    inventory.Recipe({'e_wooden_hammer': 1, 'mystery_shard': 75, 'brainrot': 10}, 'mystery_spear'),
    inventory.Recipe({'e_wooden_hammer': 1, 'mystery_shard': 35, 'brainrot': 25, 'mystery_soul': 50}, 'mystery_swiftsword'),

    inventory.Recipe({'hammer_of_rational': 1, 'lychee_core_shard': 15, 'lychee_shard': 15}, 'lychee_core'),
    inventory.Recipe({'hammer_of_rational': 1, 'lychee_core_shard': 5, 'lychee_shard': 30, 'purple_clay': 10}, 'lychee_twinblade'),
    inventory.Recipe({'hammer_of_rational': 1, 'lychee_core_shard': 5, 'lychee_shard': 10}, 'proof'),
    inventory.Recipe({'hammer_of_rational': 1, 'lychee_core_shard': 5, 'lychee_shard': 10}, 'observe'),

    inventory.Recipe({'e_wooden_hammer': 1, 'lychee_shard': 15, 'purple_clay': 10, 'e_feather': 10}, 'lychee'),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_poison_powder': 15, 'carrion': 20}, 'intestine'),

    inventory.Recipe({'_rune_altar': 1, 'thaumaturgy': 1, 'hoverplume_headgear': 1, 'hoverplume_back': 1, 'hoverplume_kneepads': 1,
                      'feather_sword': 1, 'feather_amulet': 1, 'toxic_wing': 1}, 'pluma_thaumaturgy'),
]

inventory.RECIPES.extend(RECIPES)