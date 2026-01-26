from quests import single

base = single.QuestBlock(qid='begin', name='Since Everything Starts',
                         content='UNDERIA by KLPIG\n'
                                 '> You eventually appears in a strange world, what will happen?\n'
                                 'Basic Controls\n'
                                 '> [W][A][S][D] - Move\n'
                                 '> [E] - Inventory\n'
                                 '> [LEFT-MOUSE] - Attack\n'
                                 '> [RIGHT-MOUSE] - Charge for Attack', reqs=[single.ViewRequirement()],
                         pos=(0, 0))
single.QUESTS.append(base)

base.add_child(single.QuestBlock(qid='class', name='Classes!',
                                 content='Basis of this game focuses on WEAPONS.\n'
                                         'Generally, we have 3 classes, MELEE, RANGED and MAGIC.\n'
                                         'Each class has unique armor & accessories that focuses '
                                         'on specified damage addon.',
                                 reqs=[single.ViewRequirement()], pos=(300, -800), disp='items_platinum_sword')
               .add_child(single.QuestBlock(qid='class-melee', name='Melee',
                                            content='Melee has properties of shortest attack range and strong '
                                                    'damage\n'
                                                    'Attack of melee won\'t require any cost.\n'
                                                    'A stronger melee weapon will generate high-ranged projectiles '
                                                    'with NO COST.\n\n'
                                                    'Melee contains SWORD/BLADE and SPEAR.\nNow, craft a wooden '
                                                    'sword.\n\nNOW REQUIRE: \n-Wooden Sword *1.',
                                            reqs=[single.ItemRequirement(item='wooden_sword')],
                                            pos=(600, -1100), disp='items_wooden_sword',
                                            )
                          .add_child(single.QuestBlock(qid='magic-sword', name='A Magic Sword',
                                                       content='Magic Sword or Magic Blade can be dropped by mining '
                                                               'Sword in the Stone.\n'
                                                               'Sword in the Stone summons almost every biome.\n'
                                                               'It can be mine with minepower 2(copper pickaxe).\n\n'
                                                               'MAGIC SWORD: Summon a sword projectile.\n'
                                                               'MAGIC BLADE: Frequent damage and strong knockback.\n\n'
                                                               'They are interchange-able.\n\n'
                                                               'NOW REQUIRE(any 1): \n-Magic sword*1\n-Magic blade*1',
                                                       reqs=[single.ItemRequirement(item='magic_sword'),
                                                             single.ItemRequirement(item='magic_blade')],
                                                       pos=(900, -1100), disp='items_magic_sword',
                                                       ),

                                     )
                          )
               .add_child(single.QuestBlock(qid='class-magic', name='Magic',
                                            content='Magic has properties of elemental reaction \n'
                                                    'Attack of magic often require MANA.\n'
                                                    'MANA can be regenerated and increasing MAX VALUE.\n\n'
                                                    'Magic contains WAND/BOOK and ARCANE.\nNow, craft a '
                                                    'glowing splint.\n\nNOW REQUIRE: \n-Glowing Splint *1.',
                                            reqs=[single.ItemRequirement(item='glowing_splint')],
                                            pos=(600, -900), disp='glowing_splint',
                                            ))
               .add_child(single.QuestBlock(qid='class-ranged', name='Ranged',
                                            content='Ranged has properties of high attack range and complex damage. \n'
                                                    'Attack of ranged often require ammo.\n'
                                                    'Ammo can be crafted or found. \n\n'
                                                    'Ranged contains BOW, GUN and KNIFE.\nNow, craft a '
                                                    'wooden bow.\n\nNOW REQUIRE: \n-Bow *1.',
                                            reqs=[single.ItemRequirement(item='bow')],
                                            pos=(600, -700), disp='bow',
                                            ))
               )

biomes = single.QuestBlock(qid='biome', name='Biomes',
                           content='Let\'s learn for the map.\n'
                                   'The mainland in UNDERIA is an elliptical shape, \n surrounding by ocean.\n'
                                   'After some progress, some specifies biome will be generated.\n',
                           reqs=[single.ViewRequirement()], pos=(300, -400),
                           disp='traveller_boots')
base.add_child(biomes)
biomes.add_child(single.QuestBlock(qid='hell', name='Hell',
                                   content='Hell is very dangerous.\nIt is suggested to be '
                                           'explored\n after True Eye is defeated.',
                                   reqs=[single.BiomeRequirement(biome='hell')], pos=(400, -500),
                                   disp='obsidian_ingot'))
biomes.add_child(single.QuestBlock(qid='heaven', name='Heaven',
                                   content='Heaven is quite dangerous.\nUseful foods may be found in '
                                           'the chest.',
                                   reqs=[single.BiomeRequirement(biome='heaven')], pos=(400, -400),
                                   disp='floatstone'))
biomes.add_child(single.QuestBlock(qid='desert', name='Desert',
                                   content='Desert is moderate.\nIt riches in iron/cobalt.',
                                   reqs=[single.BiomeRequirement(biome='desert')], pos=(400, -300),
                                   disp='iron'))
biomes.add_child(single.QuestBlock(qid='snowland', name='Snows',
                                   content='Snows is moderate.\nIt riches in steel/silver.',
                                   reqs=[single.BiomeRequirement(biome='snowland')], pos=(500, -500),
                                   disp='steel'))
biomes.add_child(single.QuestBlock(qid='rainforest', name='Rainforest',
                                   content='Rainforest is safe.\nA bit difference is here from forest.',
                                   reqs=[single.BiomeRequirement(biome='rainforest')], pos=(500, -400),
                                   disp='wood'))
biomes.add_child(single.QuestBlock(qid='forest', name='Forest',
                                   content='Forest is safe.',
                                   reqs=[single.BiomeRequirement(biome='forest')], pos=(500, -300),
                                   disp='leaf'))
biomes.add_child(single.QuestBlock(qid='ocean', name='Ocean',
                                   content='Ocean appears between biomes(as river) or away from mainland.',
                                   reqs=[single.BiomeRequirement(biome='ocean')], pos=(600, -500),
                                   disp='tropical_cyclone'))
biomes.add_child(single.QuestBlock(qid='fallen_sea', name='Fallen Sea',
                                   content='Ask for GUIDE, it\'s position is unique.',
                                   reqs=[single.BiomeRequirement(biome='fallen_sea')], pos=(600, -400),
                                   disp='coral_reef'))
biomes.add_child(single.QuestBlock(qid='hot_spring', name='Hot Spring',
                                   content='After SPIRITUAL SOUL is used, \nhot spring appeared at the south of the world.',
                                   reqs=[single.BiomeRequirement(biome='hot_spring')], pos=(600, -300),
                                   disp='thermal_ingot'))
biomes.add_child(single.QuestBlock(qid='inner', name='Inner',
                                   content='After LIfE FRUIT is used, \nINNER appeared at the south of the world.',
                                   reqs=[single.BiomeRequirement(biome='inner')], pos=(700, -450),
                                   disp='chaos_heart'))
biomes.add_child(single.QuestBlock(qid='chaos_abyss', name='Chaos Abyss',
                                   content='After CHALLENGE is defeated, \nCHAOS ABYSS appeared at the south of the world.',
                                   reqs=[single.BiomeRequirement(biome='chaos_abyss_red'),
                                         single.BiomeRequirement(biome='chaos_abyss_blue')],
                                   req_num=2, pos=(700, -350),
                                   disp='origin_feather'))
biomes.add_child(single.QuestBlock(qid='path', name='And the Most Mysterious...',
                                   content='Use POTION OF SANCTUARY or COMPASS to \nteleport to PATH.\n'
                                           'PATH has no entity spawn.',
                                   reqs=[single.BiomeRequirement(biome='path'), ],
                                   req_num=1, pos=(900, -400),
                                   disp='path_altar')
                 .add_child(single.QuestBlock(qid='path_altar', name='CEREMONY',
                                              content='Go south in PATH to find ALTAR.\n\n'
                                                      'Put the materials in BASE and the starter \n'
                                                      'on the altar to start the CEREMONY', pos=(1500, -400),
                                              reqs=[single.ViewRequirement()],
                                              disp='path_altar')))

blood = single.QuestBlock(qid='bloods', name='Bloods',
                     content='At night, EYE will summon, dropping large amounts of\n '
                             'cell organization.\n'
                             'Bloodflower will also drop it.\n\n'
                             'Cell organization can craft soul bottle, increasing life\n '
                             'regen.\n\nNOW REQUIRE: \n-Cell organization*20',
                     reqs=[single.ItemRequirement(item='cell_organization', num=20)],
                     pos=(300, 0), disp='cell_organization',)
base.add_child(blood)
blood.add_child(single.QuestBlock(qid='true_eye', name='Dangerous Eye',
                                  content='Craft the suspicious eye and use it near the STONE ALTAR.\n\n'
                                          'TRUE EYE\nFor difficulty higher than NORMAL, \n'
                                          'it gains damage absorb from the small eye within.\nIts defense will '
                                          'decrease within phases.\n\nNOW REQUIRE: \n-Suspicious Eye*1\n'
                                          '-Notebook: D1 - True Eye - The watcher of Terror',
                                  reqs=[single.ItemRequirement(item='suspicious_eye', num=1),
                                        single.NotebookRequirement(note='D1')],
                                  req_num=2, pos=(600, 0), disp='suspicious_eye', rarity=2)
                .add_child(single.QuestBlock(qid='firy_slime', name='Firy Slime',
                                             content='Craft the fire slime and use it near the STONE ALTAR.\n\n'
                                                     'MAGMA KING\nSeperate to smaller one\'s after death.\n\n'
                                                     'NOW REQUIRE: \n-Firy Slime*1\n'
                                          '-Notebook: D2 - Magma King - The fire monster',
                                  reqs=[single.ItemRequirement(item='fire_slime', num=1),
                                        single.NotebookRequirement(note='D2')],
                                  req_num=2, pos=(900, 0), disp='fire_slime', rarity=2,
                                  pre=[single.QUEST_NAME['hell']]))
                .add_child(single.QuestBlock(qid='azure_stele', name='Azure Stele',
                                             content='Craft the monument and use it near the STONE ALTAR.\n\n'
                                                     'NOW REQUIRE: \n-Monument*1\n'
                                          '-Notebook: D2B',
                                  reqs=[single.ItemRequirement(item='monument', num=1),
                                        single.NotebookRequirement(note='D2B')],
                                  req_num=2, pos=(900, -200), disp='monument', rarity=2,
                                  pre=[single.QUEST_NAME['heaven']]))
                )
blood.add_child(single.QuestBlock(qid='python', name='Python',
                                             content='Craft the delicious seedling and use it near the STONE ALTAR.\n\n'
                                                     'NOW REQUIRE: \n-Delicious Seedling*1\n'
                                          '-Notebook: D0',
                                  reqs=[single.ItemRequirement(item='delicious_seedling', num=1),
                                        single.NotebookRequirement(note='D0')],
                                  req_num=2, pos=(300, 200), disp='delicious_seedling', rarity=2,
                                  pre=[single.QUEST_NAME['rainforest']]))
single.QUEST_NAME['firy_slime'].add_child(single.QuestBlock(qid='wind', name='Desert Wind!',
                                                            content='When HP rises to 500, mystery substance can be got \n'
                                                                    'through entity in desert.\n'
                                                                    'Craft the wind and summon sandstorm in stone altar!\n\n'
                                                                    'NOW REQUIRE: \n-Mysterious substance*20\n'
                                                                    '-Notebook: D3 \n-Wind*1\n',
                                                            reqs=[single.ItemRequirement(item='wind', num=1),
                                                                  single.ItemRequirement(item='mysterious_substance', num=20),
                                                                  single.NotebookRequirement(note='D3')],
                                                            req_num=3, pos=(1200, 0), disp='wind', rarity=2)
                                          .add_child(single.QuestBlock(qid='otherworld', name='Otherworld Invasion!',
                                                                       content='After sandstorm is defeated, \n'
                                                                               'True Eye, Worlds Fruit, Fluffff becomes stronger.\n\n'
                                                                               'NOW REQUIRE: \n-Otherworld Stone*100',
                                                                       pos=(1500, 0), disp='otherworld_stone')
                                                     .add_child(single.QuestBlock(qid='chaos_reap', name='Chaos Reap',
                                                                                  content='Do KARMA CEREMONY.\n'
                                                                                          'MATERIALS: Otherworld Stone*3, Eye Lens*1, '
                                                                                          'Worm Scarf*1, Worlds Seed*1\n'
                                                                                          'STARTER: Storm Core*1\n\n'
                                                                                          'Let RAY satisfy your performance, buy CHAOS REAP.\n\n'
                                                                                          'NOW REQUIRE: \n-Chaos Reap*1',
                                                                                  disp='chaos_reap', reqs=[single.ItemRequirement(item='chaos_reap', num=1),],
                                                                                  pos=(1400, 600), rarity=4, pre=[single.QUEST_NAME['path_altar']], ))))

base.add_child(single.QuestBlock(qid='murder', name='MURDER START!',
                                 desc='br_chaosConsider carefully!',
                                 content='Do BLOOD CEREMONY (OPTIONAL and IRREVERSIBLE!)\n'
                                         'MATERIALS: Blood Ingot, Life Core, Bloodstone, \n'
                                         'Cell Organization, Watcher Wand, War necklace\n'
                                         'STARTER: Bloodstone Amulet\n\nDeal damage to earn BLOOD VALUE and enable more STATS.',
                                 pre=[single.QUEST_NAME['path_altar'], blood], pos=(600, 600),
                                 disp='murders_knife', reqs=[
        single.ItemRequirement(item='blood_ingot', num=1),
        single.ItemRequirement(item='life_core', num=1),
        single.ItemRequirement(item='bloodstone', num=1),
        single.ItemRequirement(item='cell_organization', num=1),
        single.ItemRequirement(item='watcher_wand', num=1),
        single.ItemRequirement(item='war_necklace', num=1),
        single.ItemRequirement(item='bloodstone_amulet', num=1),
    ], req_num=7, rarity=4)
               .add_child(single.QuestBlock(qid='bloodlust_scythe', name='A Good Weapon',
                                            content='BLOOD SCYTHE - Quicker increase BLOOD VALUE, \ndamage increase within progress.',
                                            reqs=[single.ItemRequirement(item='bloodlust_scythe', num=1),],
                                            disp='bloodlust_scythe', pos=(1200, 600), rarity=5),))

# insert
single.QUEST_NAME["wind"].add_child(single.QuestBlock(qid="abyss_eye", name="Abyss Eye", desc="", content="Take otherworld stone from True Eye, Worlds Fruit and Fluffff.\nCraft blood substance.\nKill abyss eye and get an important material: soul\n\nNOW REQUIRE: \n- Blood Substance*1\n- Notebook D4\n- Soul * 50", reqs=[single.ItemRequirement(item='blood_substance', num=1), single.ItemRequirement(item='soul', num=50)], req_num=2, pos=(1800, 0), disp="spiritual_stabber"))
single.QUEST_NAME["magic_sword"].add_child(single.QuestBlock(qid="nights_edge", name="Nights Edge", desc="", content="Use storm core and several strong weapons to craft nights edge.\n Night edge shoots strong energy.\n\nNOW REQUIRE: \n -Nights edge*1", reqs=[single.ItemRequirement(item='nights_edge', num=1)], req_num=1, pos=(1200, -1100), disp="nights_edge"))
single.QUEST_NAME["spiritual_stabber"].add_child(single.QuestBlock(qid="excalibur", name="EX! Calibur!", desc="", content="", reqs=[single.ItemRequirement(item='excalibur', num=1)], req_num=1, pos=(1200, -1300), disp="excalibur"))
single.QUEST_NAME["nights_edge"].add_child(single.QuestBlock(qid="spiritual_stabber", name="Spiritual Stabber", desc="", content="Abyss Eye may drop spiritual stabber.\n\nNOW REQUIRE: \n -Spiritual Stabber*1", reqs=[single.ItemRequirement(item='spiritual_stabber', num=1)], req_num=1, pos=(1200, -1300), disp="spiritual_stabber"))
single.QUEST_NAME["abyss_eye"].add_child(single.QuestBlock(qid="spiritual_heart", name="Spiritual Heart", desc="", content="Use SPIRITUAL HEART and start an entire journey - the stage 2, while also reinforcing you.\nNew life based on soul will be generated.\n\nNOW REQUIRE: \n- Spiritual Heart*1", reqs=[single.ItemRequirement(item='spiritual_heart', num=1)], req_num=1, pos=(2100, 0), disp="spiritual_heart"))

for q in single.QUESTS:
    q.write()