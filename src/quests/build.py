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
                          .add_child(single.QuestBlock(qid='magic_sword', name='A Magic Sword',
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
                                            content='BLOODLUST SCYTHE - Quicker increase BLOOD VALUE, \ndamage increase within progress.',
                                            reqs=[single.ItemRequirement(item='bloodlust_scythe', num=1),],
                                            disp='bloodlust_scythe', pos=(1200, 600), rarity=5),))


single.QUEST_NAME["wind"].add_child(single.QuestBlock(qid="abyss_eye", name="Abyss Eye", desc="", content="Take otherworld stone from True Eye, Worlds Fruit and Fluffff.\nCraft blood substance.\nKill abyss eye and get an important material: soul\n\nNOW REQUIRE: \n- Blood Substance*1\n- Notebook D4\n- Soul * 50", reqs=[single.ItemRequirement(item='blood_substance', num=1), single.ItemRequirement(item='soul', num=50)], req_num=2, pos=(1800, 0), disp="spiritual_stabber"))
single.QUEST_NAME["magic_sword"].add_child(single.QuestBlock(qid="nights_edge", name="Nights Edge", desc="", content="Use storm core and several strong weapons to craft nights edge.\n Night edge shoots strong energy.\n\nNOW REQUIRE: \n -Nights edge*1", reqs=[single.ItemRequirement(item='nights_edge', num=1)], req_num=1, pos=(1200, -1100), disp="nights_edge", rarity=5))
single.QUEST_NAME["class-melee"].add_child(single.QuestBlock(qid="spiritual_stabber", name="Spiritual Stabber", desc="", content="Abyss Eye may drop spiritual stabber.\n\nNOW REQUIRE: \n -Spiritual Stabber*1", reqs=[single.ItemRequirement(item='spiritual_stabber', num=1)], req_num=1, pos=(1200, -1300), disp="spiritual_stabber"))
single.QUEST_NAME["spiritual_stabber"].add_child(single.QuestBlock(qid="excalibur", name="EX! Calibur!", desc="", content="", reqs=[single.ItemRequirement(item='excalibur', num=1)], req_num=1, pos=(1500, -1300), disp="excalibur"))
single.QUEST_NAME["abyss_eye"].add_child(single.QuestBlock(qid="spiritual_heart", name="Spiritual Heart", desc="", content="Use SPIRITUAL HEART and start an entire journey - the stage 2, while also reinforcing you.\nNew life based on soul will be generated.\n\nNOW REQUIRE: \n- Spiritual Heart*1", reqs=[single.ItemRequirement(item='spiritual_heart', num=1)], req_num=1, pos=(2100, 0), disp="spiritual_heart"))
single.QUEST_NAME["class-melee"].add_child(single.QuestBlock(qid="demon_blade__muramasa", name="Muramasa: The Demon\'s Blade", desc="", content="Muramasa deals strong damage.\n[Q]: quick stab.", reqs=[single.ItemRequirement(item='demon_blade__muramasa', num=1)], req_num=1, pos=(900, -1300), disp="demon_blade__muramasa", pre=[], rarity=5))
single.QUEST_NAME["spiritual_heart"].add_child(single.QuestBlock(qid="twin_eye", name="The Twin Eye", desc="", content="You feel like something\'s staring at you...\n\nUse Mechanic Eye in Metal Altar.", reqs=[single.ItemRequirement(item='mechanic_eye', num=1), single.NotebookRequirement(note='D5A')], req_num=2, pos=(2400, -200), disp="mechanic_eye", pre=[],))
single.QUEST_NAME["spiritual_heart"].add_child(single.QuestBlock(qid="destroyer", name="The Destroyer", desc="", content="Earth below you is starting to quake...\n\nUse Mechanic Worm in Metal Altar.", reqs=[single.ItemRequirement(item='mechanic_worm', num=1), single.NotebookRequirement(note='D5B')], req_num=2, pos=(2400, 0), disp="mechanic_worm", pre=[],))
single.QUEST_NAME["spiritual_heart"].add_child(single.QuestBlock(qid="cpu", name="The CPU", desc="", content="Air is about to condense...\n\nUse Electric Unit in Metal Altar.", reqs=[single.ItemRequirement(item='electric_unit', num=1), single.NotebookRequirement(note='D5C')], req_num=2, pos=(2400, 200), disp="electric_unit", pre=[],))
single.QUEST_NAME["twin_eye"].add_child(single.QuestBlock(qid="spirit_essence", name="Spirit Essence: The Combinator", desc="", content="Use souls get from the bosses to craft Spirit Essence.\nSpirit essence merges and upgrade things.\n\nNOW REQUIRE: \n- Spirit Essence*3", reqs=[single.ItemRequirement(item='spirit_essence', num=3)], req_num=1, pos=(2700, 0), disp="spirit_essence", pre=[single.QUEST_NAME['destroyer'], single.QUEST_NAME['cpu']],))
single.QUEST_NAME["excalibur"].add_child(single.QuestBlock(qid="true_excalibur", name="True Excalibur", desc="", content="A strong melee weapon which strong large range of projectiles.", reqs=[single.ItemRequirement(item='true_excalibur', num=1)], req_num=1, pos=(1800, -1300), disp="true_excalibur", pre=[single.QUEST_NAME['spirit_essence']], rarity=6))
single.QUEST_NAME["nights_edge"].add_child(single.QuestBlock(qid="true_nights_edge", name="True Nights Edge", desc="", content="A strong melee weapon which shoots energy.", reqs=[single.ItemRequirement(item='true_nights_edge', num=1)], req_num=1, pos=(1800, -1100), disp="true_nights_edge", pre=[single.QUEST_NAME['spirit_essence']], rarity=6))
single.QUEST_NAME["true_nights_edge"].add_child(single.QuestBlock(qid="the_blade", name="The Blade", desc="", content="The blade can be thrown out and gives strong beams.", reqs=[single.ItemRequirement(item='the_blade', num=1)], req_num=1, pos=(2100, -1200), disp="the_blade", pre=[single.QUEST_NAME['true_excalibur']], rarity=7))
single.QUEST_NAME["spiritual_heart"].add_child(single.QuestBlock(qid="eternity", name="Embracing Eternity!", desc="", content="Now, for difficulties higher than normal, \nenable ETERNAL for difficulty 2.\n\nETERNAL MODE increases enemies\' HP and \nadd bosses attack logic.",
                                                                 reqs=[single.ConstantRequirement(tr='DIFFICULTY2',tv=2), single.ViewRequirement()], req_num=2, pos=(2100, 500), disp="eternal_pocket_watch", pre=[], rarity=5))
single.QUEST_NAME["eternity"].add_child(single.QuestBlock(qid="demise", name="Even More?", desc="", content="For difficulties higher than mastery, \nenable DEMISE for difficulty 2.\n\nDEMISE MODE increases enemies\' HP and \nadd even more bosses attack logic.", reqs=[single.ViewRequirement(), single.ConstantRequirement(tr='DIFFICULTY2',tv=3)], req_num=2, pos=(2300, 500),
                                                          disp="dark_matter", pre=[], rarity=8))
single.QUEST_NAME["the_blade"].add_child(single.QuestBlock(qid="zenith", name="Zenith", desc="", content="Deals rapid damage - the final melee weapon.", reqs=[single.ItemRequirement(item='zenith', num=1)], req_num=1, pos=(1200, -1500), disp="zenith", pre=[single.QUEST_NAME['demon_blade__muramasa'], single.QUEST_NAME['class-melee']], rarity=9))
single.QUEST_NAME["cpu"].add_child(single.QuestBlock(qid="greed", name="Greed", desc="", content="Whispers flow to your mind...\n\nUse Electric Spider in Metal Altar.", reqs=[single.ItemRequirement(item='electric_spider', num=1), single.NotebookRequirement(note='D6C')], req_num=2, pos=(3000, 200), disp="electric_spider", pre=[single.QUEST_NAME['spirit_essence']],))
single.QUEST_NAME["destroyer"].add_child(single.QuestBlock(qid="devil_python", name="Devil Python - The Demon", desc="", content="Nameless worm is ready to attack you now...\n\nUse Metal Food in Metal Altar.", reqs=[single.ItemRequirement(item='metal_food', num=1), single.NotebookRequirement(note='D6B')], req_num=2, pos=(3000, 0), disp="metal_food", pre=[single.QUEST_NAME['spirit_essence']],))
single.QUEST_NAME["twin_eye"].add_child(single.QuestBlock(qid="eye_of_time", name="The Eye of Time", desc="", content="Time is about to stop...\n\nUse Watch in Metal Altar.", reqs=[single.ItemRequirement(item='watch', num=1), single.NotebookRequirement(note='D6A')], req_num=2, pos=(3000, -200), disp="watch", pre=[single.QUEST_NAME['spirit_essence']],))
single.QUEST_NAME["greed"].add_child(single.QuestBlock(qid="incremental", name="Spirit Essence: Incremental", desc="", content="A much stronger combinator.\n\nNOW REQUIRE: \n - Incremental Spirit Essence *5", reqs=[single.ItemRequirement(item='incremental_spirit_essence', num=5)], req_num=1, pos=(3300, 0), disp="incremental_spirit_essence", pre=[single.QUEST_NAME['eye_of_time'], single.QUEST_NAME['devil_python']],))
single.QUEST_NAME["incremental"].add_child(single.QuestBlock(qid="chlorophyte", name="Chlorophyte and Photosynthesis", desc="", content="Get chlorophyll from LEAF.\nCraft Photon with chlorophyll and healing potion.\nCraft chlorophyte ingot.\n\nNOW REQUIRE: \n - Chlorophyll * 1 \n - Photon * 20 \n - Chlorophyte Ingot * 3", reqs=[single.ItemRequirement(item='chlorophyll', num=1), single.ItemRequirement(item='photon', num=20), single.ItemRequirement(item='chlorophyte_ingot', num=3)], req_num=3, pos=(3600, 0), disp="chlorophyte_ingot", pre=[],))
single.QUEST_NAME["chlorophyte"].add_child(single.QuestBlock(qid="abyss_sever", name="Abyss Sever", desc="", content="Challenge yourself, before eating LIFE FRUIT, summon and defeat \nJEVIL by ATRRACTION CEREMONY.\n\nATTRACTION CEREMONY\nMATERIAL: Photon *6\nSTARTER: JOKER\n\"And what will happen?\"\n\nNOW REQUIRE:\n- Abyss sever *1", reqs=[single.ItemRequirement(item='abyss_sever', num=1)], req_num=1, pos=(1600, 600), disp="abyss_sever", rarity=12, pre=[single.QUEST_NAME['path_altar']],))
single.QUEST_NAME["chlorophyte"].add_child(single.QuestBlock(qid="life_fruit", name="Yummy!", desc="", content="Consume life fruit till it increase your \n soul level again.\n\nNOW REQUIRE: \n - Life Fruit *7", reqs=[single.ItemRequirement(item='life_fruit', num=7)], req_num=1, pos=(3900, 0), disp="life_fruit", pre=[],))
single.QUEST_NAME["life_fruit"].add_child(single.QuestBlock(qid="jevil", name="Back to Chaos!", desc="", content="Summon jevil using JOKER after consuming all life fruits \n   OR    \n get a abyss sever.\n\nNOW REQUIRE: \n - JOKER * 1 \n - Notebook D7", reqs=[single.ItemRequirement(item='joker', num=1), single.NotebookRequirement(note='D7')], req_num=2, pos=(4200, 0), disp="chaos_ingot", pre=[], rarity=5))
single.QUEST_NAME["jevil"].add_child(single.QuestBlock(qid="plantera", name="The Start of a Godkiller", desc="", content="Obtain a Plantera Bulb in inner.\n\nUse it anywhere.", reqs=[single.ItemRequirement(item='plantera_bulb', num=1), single.NotebookRequirement(note='D8')], req_num=2, pos=(3900, -400), disp="plantera_bulb", pre=[single.QUEST_NAME['inner'], single.QUEST_NAME['chlorophyte'], single.QUEST_NAME['life_fruit']], rarity=5))
single.QUEST_NAME["plantera"].add_child(single.QuestBlock(qid="determine", name="Combine!", desc="", content="Do DETERMINIZE CEREMONY.\n\nDETERMINIZE CEREMONY\nMATERIAL: Soul of Integrity, Soul of Kindness, Soul of Bravery, \n  Soul of Perseverance, Soul of Patience, Soul of Justice\nSTARTER: Willpower shard.\n\nNOW REQUIRE: \n - Soul of determination*7", reqs=[single.ItemRequirement(item='soul_of_determination', num=1)], req_num=1, pos=(3900, -800), disp="soul_of_determination", pre=[single.QUEST_NAME['path_altar']], rarity=6))
single.QUEST_NAME["class-melee"].add_child(single.QuestBlock(qid="ark_of_elements", name="The Ark: Elements", desc="", content="Ark of Elements have 3 states, switching states \n deal more damage.\n\nFIRE: Summon fireball; \nAIR: Air cuts; \nICE: Ice beams.", reqs=[single.ItemRequirement(item='ark_of_elements', num=1)], req_num=0, pos=(600, -1300), disp="ark_of_elements", pre=[single.QUEST_NAME['determine']], rarity=7))
single.QUEST_NAME["determine"].add_child(single.QuestBlock(qid="final_improve", name="Final Improve", desc="", content="Craft origin by seed of origin.\n\nDo GODIFY CEREMONY.\n\nGODIFY CEREMONY\nMATERIAL: Soul of determination*6\nSTARTER: Origin\n\nFace the Challenge!\n\nNOW REQUIRE: \n Origin *1", reqs=[single.ItemRequirement(item='origin', num=1)], req_num=1, pos=(3900, -1000), disp="origin", pre=[single.QUEST_NAME['path_altar']], rarity=6))
single.QUEST_NAME["final_improve"].add_child(single.QuestBlock(qid="time_essence", name="The Time", desc="", content="Certain entities in INNER drops this essence.\n\nNOW REQUIRE:\n - Time essence*6", reqs=[single.ItemRequirement(item='time_essence', num=6)], req_num=1, pos=(3700, -1500), disp="time_essence", pre=[single.QUEST_NAME['inner']], rarity=4))
single.QUEST_NAME["final_improve"].add_child(single.QuestBlock(qid="substance_essence", name="The Matters", desc="", content="Certain entities in INNER drops this essence.\n\nNOW REQUIRE:\n - Substance essence*6", reqs=[single.ItemRequirement(item='substance_essence', num=6)], req_num=1, pos=(4100, -1500), disp="substance_essence", pre=[single.QUEST_NAME['inner']], rarity=4))
single.QUEST_NAME["final_improve"].add_child(single.QuestBlock(qid="wierd_essence", name="The Horror", desc="", content="Certain entities in INNER drops this essence.\n\nNOW REQUIRE:\n - Wierd essence*6", reqs=[single.ItemRequirement(item='wierd_essence', num=6)], req_num=1, pos=(3700, -1700), disp="wierd_essence", pre=[single.QUEST_NAME['inner']], rarity=4))
single.QUEST_NAME["final_improve"].add_child(single.QuestBlock(qid="light_essence", name="The Lights", desc="", content="Certain entities in INNER drops this essence.\n\nNOW REQUIRE:\n - Light essence*6", reqs=[single.ItemRequirement(item='light_essence', num=6)], req_num=1, pos=(4100, -1700), disp="light_essence", pre=[single.QUEST_NAME['inner']], rarity=4))
single.QUEST_NAME["final_improve"].add_child(single.QuestBlock(qid="origin_feather", name="The Eternal Feather", desc="", content="In chaos abyss (red or blue), RAVEN drops origin feather.\n\nNOW REQUIRE: \n - Origin Feather*1", reqs=[single.ItemRequirement(item='origin_feather', num=1)], req_num=1, pos=(3500, -1500), disp="origin_feather", pre=[single.QUEST_NAME['chaos_abyss']], rarity=4))
single.QUEST_NAME["time_essence"].add_child(single.QuestBlock(qid="clock", name="God of Time", desc="", content="DO CLOCK CEREMONY:\nMATERIAL: Time Essence*3, Chaos Ingot*1, Soul of Determination*1,\n  Incremental Spirit Essence*1\nSTARTER: Origin\n\nNOW REQUIRE: \n - Notebook D9A", reqs=[single.NotebookRequirement(note='D9A')], req_num=1, pos=(3500, -2000), disp="soul_of_patience", pre=[single.QUEST_NAME['path_altar']], rarity=7))
single.QUEST_NAME["substance_essence"].add_child(single.QuestBlock(qid="matter", name="God of Matters", desc="", content="DO SUBSTANCE CEREMONY:\nMATERIAL: Substance Essence*3, Chaos Ingot*1, Soul of Determination*1,\n  Incremental Spirit Essence*1\nSTARTER: Origin\n\nNOW REQUIRE: \n - Notebook D9B", reqs=[single.NotebookRequirement(note='D9B')], req_num=1, pos=(4300, -2000), disp="soul_of_integrity", pre=[single.QUEST_NAME['path_altar']], rarity=7))
single.QUEST_NAME["wierd_essence"].add_child(single.QuestBlock(qid="gods_eye", name="God of Matters", desc="", content="DO CELESTIC CEREMONY:\nMATERIAL: Wierd Essence*2, Light Essence*2, Origin Spirit Essence*2\nSTARTER: Origin\n\nNOW REQUIRE: \n - Notebook D9C", reqs=[single.NotebookRequirement(note='D9C')], req_num=1, pos=(3900, -2000), disp="scorch_core", pre=[single.QUEST_NAME['path_altar'], single.QUEST_NAME['light_essence']], rarity=7))
single.QUEST_NAME["clock"].add_child(single.QuestBlock(qid="my_soul", name="The Soul Combines", desc="", content="Craft MY SOUL, an important craft tool.\nUSE it to improve.", reqs=[single.ItemRequirement(item='my_soul', num=1)], req_num=1, pos=(3900, -2400), disp="my_soul", pre=[single.QUEST_NAME['matter'], single.QUEST_NAME['gods_eye']], rarity=8))
single.QUEST_NAME["my_soul"].add_child(single.QuestBlock(qid="the_final_ingot", name="When the Final Ingot is Made", desc="", content="Craft DESTRUCT THOUGHTS, a pickaxe.\n\nMine Holy Pillar and Scarlett Pillar.\n\nCraft with REASON and RESULT, to blow out the grand \n power of KARMA.\n\nNOW REQUIRE:\n - Destruct Thoughts\n - Reason*30\n - Result*30\n - The Final Ingot*3", reqs=[single.ItemRequirement(item='destruct_thoughts', num=1), single.ItemRequirement(item='reason', num=30), single.ItemRequirement(item='result', num=30), single.ItemRequirement(item='the_final_ingot', num=3)], req_num=4, pos=(3750, -2400), disp="the_final_ingot", pre=[], rarity=8))
single.QUEST_NAME["my_soul"].add_child(single.QuestBlock(qid="ascendant_spirit_essence", name="The Spirit Essence: Ascendance", desc="", content="Craft ASCENDANT SPIRIT ESSENCE.\n\nNow Require:\n - Ascendant Spirit Essence*3", reqs=[single.ItemRequirement(item='ascendant_spirit_essence', num=3)], req_num=1, pos=(4050, -2400), disp="ascendant_spirit_essence", pre=[], rarity=8))
single.QUEST_NAME["my_soul"].add_child(single.QuestBlock(qid="wtree", name="Shadow of Reincartion", desc="", content="DO REINCARNATE CEREMONY:\nMATERIALS: REASON*3, CURSE CORE, THE FINAL INGOT, \n ASCENDANT SPIRIT ESSENCE\nSTARTER: MY SOUL\n\nNOW REQUIRE:\n - Notebook D10A", reqs=[single.NotebookRequirement(note='D10A')], req_num=1, pos=(3500, -2800), disp="soul_of_kindness", pre=[single.QUEST_NAME['the_final_ingot'], single.QUEST_NAME['ascendant_spirit_essence']], rarity=8))
single.QUEST_NAME["my_soul"].add_child(single.QuestBlock(qid="faith", name="Void Faith", desc="", content="DO FAITH CEREMONY:\nMATERIALS: RESULT*3, SCORCH CORE, THE FINAL INGOT, \n ASCENDANT SPIRIT ESSENCE\nSTARTER: MY SOUL\n\nNOW REQUIRE:\n - Notebook D10B", reqs=[single.NotebookRequirement(note='D10B')], req_num=1, pos=(4300, -2800), disp="soul_of_justice", pre=[single.QUEST_NAME['the_final_ingot'], single.QUEST_NAME['ascendant_spirit_essence']], rarity=8))
single.QUEST_NAME["my_soul"].add_child(single.QuestBlock(qid="omega_flowey", name="Finale", desc="", content="DO OMEGA CEREMONY:\nMATERIALS: TIME FOUNTAIN, SUBSTANCE FOUNTAIN, CELESTIC FOUNTAIN, \n NO FOUNTAIN, DEATH FOUNTAIN\nSTARTER: YELLOW FLOWER\n\nNOW REQUIRE:\n - Notebook D11", reqs=[single.NotebookRequirement(note='D11')], req_num=1, pos=(3900, -3000), disp="soul_of_determination", pre=[single.QUEST_NAME['the_final_ingot'], single.QUEST_NAME['ascendant_spirit_essence'], single.QUEST_NAME['faith'], single.QUEST_NAME['wtree']], rarity=9))
# insert

for q in single.QUESTS:
    q.write()