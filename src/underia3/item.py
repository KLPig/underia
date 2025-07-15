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
    'magic_feather': inventory.Inventory.Item('Magic Feather', 'Feather that can cast spells.', 'magic_feather', 1,
                                           [inventory.TAGS['item']]),
    'purple_clay': inventory.Inventory.Item('Purple Clay', 'Susan, or grab tight purple clay.', 'purple_clay', 2,
                                  [inventory.TAGS['item']]),
    'brainrot': inventory.Inventory.Item('Brainrot', 'You feel your brain rotting.', 'brainrot', 1, [inventory.TAGS['item']]),
    'mystery_shard': inventory.Inventory.Item('Mystery Shard', '', 'mystery_shard', 1, [inventory.TAGS['item']]),
    'mystery_soul': inventory.Inventory.Item('Mystery Soul', '', 'mystery_soul', 1, [inventory.TAGS['item']]),
    'carrion': inventory.Inventory.Item('Carrion', '', 'carrion', 2, [inventory.TAGS['item']]),
    'heaven_wood': inventory.Inventory.Item('Heaven Wood', '', 'heaven_wood', 1, [inventory.TAGS['item']]),

    'lychee_core_shard': inventory.Inventory.Item('Lychee Core Shard', '', 'lychee_core_shard', 3, [inventory.TAGS['item']]),

    'wooden_rope': inventory.Inventory.Item('Wooden Rope', '', 'wooden_rope', 0, [inventory.TAGS['item']]),

    'enchanted_book': inventory.Inventory.Item('Enchanted Book', '+30 maximum MP forever', 'enchanted_book', 2, [inventory.TAGS['item']]),

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

    'brainrot_necklace': inventory.Inventory.Item('Brainrot Necklace', 'Resistant to sand curse.\n+8 touching defense',
                                                   'brainrot_necklace', 2, [inventory.TAGS['item'], inventory.TAGS['accessory']]),
    'mind_anchor': inventory.Inventory.Item('Mind Anchor', '100kg\n+150% speed\n-50% karma reduce\nWhen MP < 10%, +50/sec mana regeneration',
                                            'mind_anchor', 2, [inventory.TAGS['item'], inventory.TAGS['accessory']]),
    'mystery_glove': inventory.Inventory.Item('Mystery Glove', '+20% melee damage\n+5% critical',
                                             'mystery_glove', 2, [inventory.TAGS['item'], inventory.TAGS['accessory']]),
    'tuner': inventory.Inventory.Item('Tuner', '+300 additional maximum inspiration\n+1 poet bonus time',
                                       'tuner', 2, [inventory.TAGS['item'], inventory.TAGS['accessory']]),

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
                                                   '+20% speed\n+75 touching defense\n+80 magic defense\n'
                                                   '+25% melee damage', 'purple_clay_sheath', 2,
                                                    [inventory.TAGS['item'], inventory.TAGS['accessory'], inventory.TAGS['major_accessory']]),
    'poison_quiver': inventory.Inventory.Item('Poison Quiver',
                                              'Resistant to snow curse.\n+30 touching defense\n'
                                              '+30 magic defense\n+20% ranged damage\n+10% critical\n+50% speed', 'poison_quiver', 2,
                                              [inventory.TAGS['item'], inventory.TAGS['accessory'], inventory.TAGS['major_accessory']]),
    'moonflower': inventory.Inventory.Item('Moonflower', 'Rarely drops from tree/mana chicken/la vaca saturno saturnita\nReference: Plant vs. Zombies 2\n+25 touching defense\n+30 magic defense\n-10% magic damage\n+20% karma reduce\n'
                                                         'Magic & Priest weapon will be used twice, 25% chance to recover 50% of the mana cost\n+20/sec mana regeneration',
                                            'moonflower', 3, [inventory.TAGS['item'], inventory.TAGS['accessory'], inventory.TAGS['major_accessory']]),
    'e_wooden_hammer': inventory.Inventory.Item('Wooden Hammer', '', 'e_wooden_hammer',
                                                0, [inventory.TAGS['item'], inventory.TAGS['workstation']]),
    'hammer_of_rational': inventory.Inventory.Item('Hammer of Rational', '', 'hammer_of_rational',
                                                   2, [inventory.TAGS['item'], inventory.TAGS['workstation']]),

    'chisel': inventory.Inventory.Item('Chisel', '', 'chisel', 1, [inventory.TAGS['item'],
                                                                   inventory.TAGS['workstation']]),

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
    'poise_blade': inventory.Inventory.Item('Poise Blade', 'Deal 30% damage to nearby enemies, penetrate 80 defense.', 'poise_blade', 2,
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
    'heaven_shotgun': inventory.Inventory.Item('Heaven Shotgun', 'Shoots 3 bullets at once.', 'heaven_shotgun', 2,
                                                [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['gun']], specify_img='shotgun'),

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
    'brainstorm': inventory.Inventory.Item('Brainstorm', 'Summon an attractive storm', 'brainstorm', 2,
                                            [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['magic_weapon'],
                                             inventory.TAGS['magic_element_air'], inventory.TAGS['magic_lv_1']]),

    'wooden_flute': inventory.Inventory.Item('Wooden Flute', '', 'wooden_flute', 1,
                                              [inventory.TAGS['item'], inventory.TAGS['weapon'],
                                               inventory.TAGS['poet_weapon']]),
    'the_roving_chord': inventory.Inventory.Item('The Roving Chord', '', 'the_roving_chord', 1,
                                                  [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['poet_weapon']]),

    'talent_fruit': inventory.Inventory.Item('Talent Fruit', 'Rarely drops from tree/dead tree.\nUpon the talent tree, the talent fruit,\nUnder the talent tree, you and me.', 'talent_fruit', 1,
                                              [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['priest_healer'],
                                               inventory.TAGS['magic_element_hallow'], inventory.TAGS['magic_lv_1']]),
    'holy_condense_wand': inventory.Inventory.Item('Holy Condense Wand', 'Condense a holy-ball', 'holy_condense_wand', 2,
                                                   [inventory.TAGS['item'], inventory.TAGS['weapon'], inventory.TAGS['priest_weapon'],
                                                     inventory.TAGS['magic_element_hallow'], inventory.TAGS['magic_lv_2']]),

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

    'life_hood': inventory.Inventory.Item('Life Hood', '3 armor\n+5/sec regeneration', 'life_hood', 1,
                                          [inventory.TAGS['item'], inventory.TAGS['head'], inventory.TAGS['accessory']]),
    'life_cloak': inventory.Inventory.Item('Life Cloak', '4 armor\n+80 additional maximum mana', 'life_cloak', 1,
                                            [inventory.TAGS['item'], inventory.TAGS['body'], inventory.TAGS['accessory']]),
    'life_hboots': inventory.Inventory.Item('Life Boots', '2 armor\n+20/sec mana regeneration', 'life_hboots', 1,
                                             [inventory.TAGS['item'], inventory.TAGS['leg'], inventory.TAGS['accessory']]),
    '_life_set_bonus': inventory.Inventory.Item('Life Armor Set Bonus', '+120 additional maximum mana\nWhen MP < 20%, +40/sec mana regeneration', '_life_set_bonus',
                                                1, [inventory.TAGS['item'], inventory.TAGS['accessory']], specify_img='null'),

    'concept_hat': inventory.Inventory.Item('Concept Hat', '4 armor\n+6% octave damage\n+50/sec inspiration regeneration', 'concept_hat', 2,
                                             [inventory.TAGS['item'], inventory.TAGS['head'], inventory.TAGS['accessory']]),
    'concept_mask': inventory.Inventory.Item('Concept Mask', '13 armor\n+12% pacify damage', 'concept_mask', 2,
                                              [inventory.TAGS['item'], inventory.TAGS['body'], inventory.TAGS['accessory']]),
    'concept_chestplate': inventory.Inventory.Item('Concept Chestplate', '6 armor\n+3% damage\n+50 additional maximum mana', 'concept_chestplate', 2,
                                                    [inventory.TAGS['item'], inventory.TAGS['body'], inventory.TAGS['accessory']]),
    'concept_boots': inventory.Inventory.Item('Concept Boots', '3 armor\n+10% speed\n+8 critical', 'concept_boots', 2,
                                     [inventory.TAGS['item'], inventory.TAGS['leg'], inventory.TAGS['accessory']]),
    '_concept_set_bonus_hat': inventory.Inventory.Item('Concept Armor Set Bonus', '+1% dodge rate\n+1 poet bonus time', '_concept_set_bonus_hat',
                                                        1, [inventory.TAGS['item'], inventory.TAGS['accessory']], specify_img='null'),
    '_concept_set_bonus_mask': inventory.Inventory.Item('Concept Mask Set Bonus', '+1% dodge rate\n+20% pacify time', '_concept_set_bonus_mask',
                                                1, [inventory.TAGS['item'], inventory.TAGS['accessory']], specify_img='null'),

    'ration_helmet': inventory.Inventory.Item('Ration Helmet', '5 armor\n+15% damage\n+80 additional maximum mana', 'ration_helmet', 2,
                                              [inventory.TAGS['item'], inventory.TAGS['head'], inventory.TAGS['accessory']]),
    'ration_chestplate': inventory.Inventory.Item('Ration Chestplate', '6 armor\n+12% critical\n+40% hallow damage\n+500 additional maximum inspiration', 'ration_chestplate', 2,
                                                  [inventory.TAGS['item'], inventory.TAGS['body'], inventory.TAGS['accessory']]),
    'ration_boots': inventory.Inventory.Item('Ration Boots', '5 armor\n+15% speed\n+10% pacify damage\n+20/sec mana regeneration', 'ration_boots', 2,
                                   [inventory.TAGS['item'], inventory.TAGS['leg'], inventory.TAGS['accessory']]),
    '_ration_set_bonus': inventory.Inventory.Item('Ration Armor Set Bonus', 'Ration makes wings.\n-20% air resistance\n+30% wing control', '_ration_set_bonus',
                                                  1, [inventory.TAGS['item'], inventory.TAGS['accessory']], specify_img='null'),

    'heaven_metal_helmet': inventory.Inventory.Item('Heaven Metal Helmet', '8 armor\n6kg\n+10% melee damage', 'heaven_metal_helmet', 2,
                                                    [inventory.TAGS['item'], inventory.TAGS['head'], inventory.TAGS['accessory']]),
    'heaven_metal_plate_mail': inventory.Inventory.Item('Heaven Metal Plate Mail', '11 armor\n13kg\n+10 magic defense', 'heaven_metal_plate_mail', 2,
                                                         [inventory.TAGS['item'], inventory.TAGS['body'], inventory.TAGS['accessory']]),
    'heaven_metal_leggings': inventory.Inventory.Item('Heaven Metal Leggings', '8 armor\n7kg\n+40% speed', 'heaven_metal_leggings', 2,
                                                      [inventory.TAGS['item'], inventory.TAGS['leg'], inventory.TAGS['accessory']]),
    '_heaven_metal_set_bonus': inventory.Inventory.Item('Heaven Metal Armor Set Bonus', '-10 attack speed', '_heaven_metal_set_bonus',
                                                        2, [inventory.TAGS['item'], inventory.TAGS['accessory']], specify_img='null'),

    'heaven_wooden_headgear': inventory.Inventory.Item('Heaven Wooden Headgear', '1 armor\n+30% hallow damage', 'heaven_wooden_headgear', 2,
                                                         [inventory.TAGS['item'], inventory.TAGS['head'], inventory.TAGS['accessory']]),
    'heaven_wooden_chestplate': inventory.Inventory.Item('Heaven Wooden Chestplate', '2 armor\n+40/sec mana regeneration', 'heaven_wooden_chestplate', 2,
                                                          [inventory.TAGS['item'], inventory.TAGS['body'], inventory.TAGS['accessory']]),
    'heaven_wooden_leggings': inventory.Inventory.Item('Heaven Wooden Leggings', '1 armor\n+30% hallow damage', 'heaven_wooden_leggings', 2,
                                                    [inventory.TAGS['item'], inventory.TAGS['leg'], inventory.TAGS['accessory']]),
    '_heaven_wooden_set_bonus': inventory.Inventory.Item('Heaven Wooden Armor Set Bonus', '-30% karma reduce', '_heaven_wooden_set_bonus',
                                                2, [inventory.TAGS['item'], inventory.TAGS['accessory']], specify_img='null'),

    'thaumaturgy': inventory.Inventory.Item('Thaumaturgy', 'Ring of spirit.', 'thaumaturgy', 1,
                                            [inventory.TAGS['item'], inventory.TAGS['accessory']]),
    'pluma_thaumaturgy': inventory.Inventory.Item('Pluma Thaumaturgy', '+8% dodge rate\nReleases feather according to speed, deal melee damage.',
                                                  'pluma_thaumaturgy', 2,
                                         [inventory.TAGS['item'], inventory.TAGS['accessory']]),
    'bioic_thaumaturgy': inventory.Inventory.Item('Bioic Thaumaturgy', 'Summon a slowly-regenerating shield.', 'bioic_thaumaturgy', 2,
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

    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 30, 'lychee_shard': 2}, 'life_hood'),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 50, 'lychee_shard': 3}, 'life_cloak'),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 20, 'lychee_shard': 2}, 'life_hboots'),

    inventory.Recipe({'book': 1, 'magic_pen': 1}, 'enchanted_book'),
    inventory.Recipe({'book': 1, 'magic_pen': 1, 'lychee_shard': 8}, 'lychee_spike'),
    inventory.Recipe({'book': 1, 'magic_pen': 1, 'brainrot': 20, 'mystery_soul': 8}, 'brainstorm'),

    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 6, 'e_feather': 5, 'lychee_shard': 2}, 'lychee_sword'),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 12, 'lychee_shard': 3}, 'lychee_pike'),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 3, 'e_feather': 10, 'wooden_rope': 5, 'lychee_shard': 2}, 'lychee_bow'),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 8, 'lychee_shard': 4}, 'lychee_wand'),

    inventory.Recipe({'e_wooden_hammer': 1, 'e_wood': 20, 'lychee_shard': 3}, 'chisel'),
    inventory.Recipe({'e_wooden_hammer': 1, 'chisel': 1, 'e_wood': 32}, 'wooden_flute'),
    inventory.Recipe({'e_wooden_hammer': 1, 'chisel': 1, 'e_wood': 44, 'lychee_shard': 3}, 'the_roving_chord'),

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

    inventory.Recipe({'e_wooden_hammer': 1, 'wooden_rope': 10, 'mystery_shard': 20, 'brainrot': 20}, 'brainrot_necklace'),
    inventory.Recipe({'e_wooden_hammer': 1, 'mystery_shard': 10, 'brainrot': 30, 'mystery_soul': 80}, 'mind_anchor'),

    inventory.Recipe({'e_wooden_hammer': 1, 'mystery_shard': 70, 'brainrot': 20}, 'concept_hat'),
    inventory.Recipe({'e_wooden_hammer': 1, 'mystery_shard': 70, 'brainrot': 20}, 'concept_mask'),
    inventory.Recipe({'e_wooden_hammer': 1, 'mystery_shard': 120, 'brainrot': 40}, 'concept_chestplate'),
    inventory.Recipe({'e_wooden_hammer': 1, 'mystery_shard': 70, 'brainrot': 20}, 'concept_boots'),

    inventory.Recipe({'hammer_of_rational': 1, 'lychee_core_shard': 15, 'lychee_shard': 15}, 'lychee_core'),
    inventory.Recipe({'hammer_of_rational': 1, 'lychee_core_shard': 5, 'lychee_shard': 30, 'purple_clay': 10}, 'lychee_twinblade'),
    inventory.Recipe({'hammer_of_rational': 1, 'lychee_core_shard': 5, 'lychee_shard': 10}, 'proof'),
    inventory.Recipe({'hammer_of_rational': 1, 'lychee_core_shard': 5, 'lychee_shard': 10}, 'observe'),

    inventory.Recipe({'hammer_of_rational': 1, 'lychee_core_shard': 10, 'purple_clay': 25}, 'ration_helmet'),
    inventory.Recipe({'hammer_of_rational': 1, 'lychee_core_shard': 15, 'purple_clay': 45}, 'ration_chestplate'),
    inventory.Recipe({'hammer_of_rational': 1, 'lychee_core_shard': 10, 'purple_clay': 20}, 'ration_boots'),

    inventory.Recipe({'e_wooden_hammer': 1, 'heaven_wood': 30}, 'heaven_wooden_headgear'),
    inventory.Recipe({'e_wooden_hammer': 1, 'heaven_wood': 40}, 'heaven_wooden_chestplate'),
    inventory.Recipe({'e_wooden_hammer': 1, 'heaven_wood': 30}, 'heaven_wooden_leggings'),

    inventory.Recipe({'e_wooden_hammer': 1, 'lychee_shard': 15, 'purple_clay': 10, 'e_feather': 10}, 'lychee'),
    inventory.Recipe({'e_wooden_hammer': 1, 'e_poison_powder': 15, 'carrion': 20}, 'intestine'),

    inventory.Recipe({'_rune_altar': 1, 'thaumaturgy': 1, 'hoverplume_headgear': 1, 'hoverplume_back': 1, 'hoverplume_kneepads': 1,
                      'feather_sword': 1, 'feather_amulet': 1, 'toxic_wing': 1}, 'pluma_thaumaturgy'),
    inventory.Recipe({'_rune_altar': 1, 'thaumaturgy': 1, 'life_hood': 1, 'life_cloak': 1, 'life_hboots': 1,
                      'poise_necklace': 1, 'talent_fruit': 1, 'moonflower': 1}, 'bioic_thaumaturgy'),
]

inventory.RECIPES.extend(RECIPES)