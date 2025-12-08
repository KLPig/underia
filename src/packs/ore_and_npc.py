from underia import entity, game, inventory, player_profile, notebook
from values import damages, effects
from resources import position
from physics import vector
import constants
from underia import notebook

import copy
import random
import pygame as pg
import math

"""
This pack define:
## Entities
- Ore(s)
- Chest(s)
- NPC: Checkpoint
- NPC: Guide
- NPC: Ray 
"""

@entity.Entities.entity_type
class Ore(entity.Entities.Entity):
    IMG = 'entity_ore'
    DISPLAY_MODE = 3
    NAME = 'Ore'
    TOUGHNESS = 0
    HP = 10
    SOUND_HURT = 'ore'
    SOUND_DEATH = 'ore'
    DIVERSITY = False

    def __init__(self, pos, hp=0):
        super().__init__(pos, game.get_game().graphics[self.IMG], entity.BuildingAI, self.HP if not hp else hp)
        self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 0
        self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 0
        self.hp_sys.resistances[damages.DamageTypes.ARCANE] = 0
        self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = 0
        self.hp_sys.resistances[damages.DamageTypes.THINKING] = 0
        self.hp_sys.resistances[damages.DamageTypes.MINE_POWER] = 12
        self.hp_sys.defenses[damages.DamageTypes.MINE_POWER] = self.TOUGHNESS * 12
        self.hp_sys(op='config', minimum_damage=0, maximum_damage=20)

@entity.Entities.entity_type
class RawOre(entity.Entities.Entity):
    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity_null'], entity.BuildingAI, 1)
        self.hp_sys.hp = 0
        stage = game.get_game().stage
        biome = game.get_game().get_biome()
        self.obj.IS_OBJECT = False
        if biome == 'heaven':
            return
        ore_chances = {
            CopperOre: 11,
            IronOre: 9,
            SteelOre: 9,
            PlatinumOre: 3,
            MagicOre: 5,
            BloodOre: 1,
            FiriteOre: 1,
            FiryOre: 0,
            MysteriousOre: 0,
        }
        new_world_chances = {
            SpiritualOre: 15,
            EvilOre: 15,
            PalladiumOre: 10,
            MithrillOre: 10,
            TitaniumOre: 10,
            TalentOre: 7,
            ChlorophyteOre: 0,
        }
        if biome == 'desert':
            ore_chances[IronOre] += 4
            ore_chances[PlatinumOre] += 2
        elif biome == 'snowland':
            ore_chances[SteelOre] += 4
            ore_chances[PlatinumOre] += 2
        elif biome == 'rainforest':
            ore_chances[PlatinumOre] += 5
            ore_chances[MagicOre] += 2
        elif biome == 'hell':
            ore_chances[BloodOre] += 2
            ore_chances[FiriteOre] += 2
        if game.get_game().player.hp_sys.max_hp >= 500:
            ore_chances[MysteriousOre] += 2
            if biome == 'desert':
                ore_chances[MysteriousOre] += 8
        if stage > 0:
            for k, v in new_world_chances.items():
                ore_chances[k] = v
            if stage > 5:
                ore_chances[SpiritualOre] = 0
            if biome == 'rainforest':
                ore_chances[ChlorophyteOre] += 20
        ore_type = random.choices(list(ore_chances.keys()), weights=list(ore_chances.values()), k=1)[0]
        game.get_game().entities.append(ore_type(self.obj.pos))

@entity.Entities.entity_type
class Chest(Ore):
    IMG = 'entity_chest'
    DISPLAY_MODE = 3
    NAME = 'Chest'
    BIOMES = []
    HP = 30
    TOUGHNESS = 2

    def __init__(self, pos, hp=0):
        super().__init__(pos, self.HP if not hp else hp)
        self.chest = inventory.Inventory.Chest()
        sr = self.LOOT_TABLE()
        ni = 0
        for ns, ni in sr:
            if not ni:
                continue
            nn = min(10, max(ni, 1))
            np = [0 for _ in range(nn)]
            for _ in range(ni):
                np[random.randint(0, nn - 1)] += 1
            for n in np:
                if n:
                    while ni >= self.chest.n:
                        self.chest.n += 1
                        self.chest.items.append(('null', 1))
                    self.chest.items[ni] = (ns, n)
                    ni += 1
        random.shuffle(self.chest.items)
        self.hp_sys.IMMUNE = True
        self.sm = True

    def get_shown_txt(self):
        return self.NAME, 'Press [E] to open'

    @staticmethod
    def is_suitable(biome: str):
        return biome in []

    def on_update(self):
        super().on_update()
        rd = random.randint(1, 2)
        self.hp_sys(op='config', minimum_damage=rd, maximum_damage=rd + 3)

    def t_draw(self):
        d_rect = self.d_img.get_rect(center=position.displayed_position(self.obj.pos))
        if d_rect.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
            if pg.K_e in game.get_game().get_keys() and game.get_game().player.open_inventory:
                game.get_game().player.open_chest = self.chest
        super().t_draw()
        if not self.sm:
            return
        for n, _ in self.chest.items:
            if n != 'null':
                return
        self.LOOT_TABLE = entity.LootTable([])
        self.hp_sys.hp = 0
        game.get_game().player.open_chest = None

@entity.Entities.entity_type
class HolyPillar(Ore):
    NAME = 'Holy Pillar'
    DISPLAY_MODE = 1
    TOUGHNESS = 400
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('result', 1, 10, 20),
    ])
    IMG = 'entity_holy_pillar'

    def __init__(self, pos):
        super().__init__(pos, 100)
        self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = 0
        self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 0
        self.hp_sys.resistances[damages.DamageTypes.ARCANE] = 0
        self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 0
        self.hp_sys(op='config', minimum_damage=0)

@entity.Entities.entity_type
class ScarlettPillar(Ore):
    NAME = 'Scarlett Pillar'
    DISPLAY_MODE = 1
    TOUGHNESS = 400
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('reason', 1, 10, 20),
    ])
    IMG = 'entity_scarlett_pillar'

    def __init__(self, pos):
        super().__init__(pos, 100)
        self.hp_sys.resistances[damages.DamageTypes.PHYSICAL] = 0
        self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = 0
        self.hp_sys.resistances[damages.DamageTypes.ARCANE] = 0
        self.hp_sys.resistances[damages.DamageTypes.PIERCING] = 0
        self.hp_sys(op='config', minimum_damage=0)
@entity.Entities.entity_type
class Checkpoint(Chest):
    IMG = 'entity_checkpoint'
    DISPLAY_MODE = 1
    NAME = 'Checkpoint'

    def __init__(self, *args):
        super().__init__(*args)
        self.tick = 0

    def on_update(self):
        super().on_update()
        self.tick += 1
        if self.tick % 20 == 0:
            self.rotate(45)
            tn = game.get_game().player.cc_t * 48 + 48
            if self.chest.n < tn:
                an = tn - self.chest.n
                self.chest.items.extend([('null', 1) for _ in range(an)])
                self.chest.n = tn

    def get_shown_txt(self):
        return self.NAME, 'Press [E] for storage'

    def t_draw(self):
        game.get_game().displayer.point_light((255, 255, 150), position.displayed_position(self.obj.pos), 2.5,
                                              80 / game.get_game().player.get_screen_scale())
        super().t_draw()

@entity.Entities.entity_type
class NPCGuide(Chest):
    NAMES = [
        'Bowen',
        'Eric',
        'Johnson',
        'Wilson',
        'Andy',
        'Jack',
        'Jackson'
    ]

    def __init__(self, pos):
        if 'guide' not in game.get_game().npc_data:
            self.name = random.choice(self.NAMES)
            game.get_game().npc_data['guide'] = {'name': self.name }
        else:
            self.name = game.get_game().npc_data['guide']['name']
        super().__init__(pos)
        nh = 0
        for c in self.name:
            nh = (nh * 43349191 + ord(c) * 3834119) % 2147483648
        self.img = pg.transform.scale_by(player_profile.PlayerProfile.get_surface(r=nh // 65536 % 256,
                                                                                  g=nh // 256 % 256,
                                                                                  b=nh % 256), 8)


        self.ii_set = False

        self.ct1 = [('npc_gd_f', 1), ('npc_gd_p', 1), ('npc_gd_c', 1)]
        self.ct2 = [('npc_gd_home', 1),
                    ('npc_gd_furnace', 1),
                    ('npc_gd_anvil', 1),
                    ('npc_gd_weak_healing_potion', 1),
                    ('npc_gd_weak_magic_potion', 1),
                    ('npc_gd_potion_of_memory', 1),
                    ('npc_gd_watcher_wand', 1),
                    ('npc_gd_cactus_wand', 1),
                    ('npc_gd_blood_ingot', 5), ('npc_gd_aimer', 1),
                    ('npc_gd_bloodstone_amulet', 1),
                    ('npc_gd_traveller_boots', 1), ('npc_gd_the_desert_eagle', 1),
                    ('npc_gd_rock_ball', 1)]
        self.ct2_a = [('npc_gd_mithrill_anvil', 1),
                      ('npc_gd_life_core', 10), ('npc_gd_wildsands', 1), ('npc_gd_soul_resonancer', 1),
                      ]
        self.ct3 =[('npc_gd_home', 1), ('npc_gd_c_1', 1), ('npc_gd_c_2', 1), ('npc_gd_c_4', 1),
                    ('npc_gd_c_3', 1), ]
        self.state = 0

        self.chest.items = self.ct1
        self.chest.n = len(self.ct1)
        self.chest.locked = True
        self.sm = False

    def get_shown_txt(self):
        return self.name, 'Press [E] to talk'

    def t_draw(self):
        if not self.ii_set:
            self.ii_set = True
            inventory.ITEMS['npc_gd_home'] = inventory.Inventory.Item(
                'Back',
                '',
                'npc_gd_home',
                0, [],
                specify_img='checkpoint'
            )
            inventory.ITEMS['npc_gd_f'] = inventory.Inventory.Item(
                'World Analyse',
                'col00ffffEmm, this is an interesting world...\n'
                'col00ffffThe type of this world is: ' + str('A234567890JQK'[game.get_game().fun - 1]) +
                '\ncol00ffffOnce upon a time, a massive part of ocean is buried...\n' +
                'col00ffffIt\'s located at.. ' + str(
                    ['N', 'N', 'NNE', 'NE', 'SE', 'SW', 'NNW', 'NE', 'N', 'W', 'WNW', 'W', 'NE'][
                        game.get_game().fun - 1]) +  # direction=fun ^ 3
                '\ncol00ffffWait, you know what these "compass bearing" means, don\'t you?',
                'npc_gd_f',
                0, [],
                specify_img='wood'
            )
            inventory.ITEMS['npc_gd_p'] = inventory.Inventory.Item(
                'Purchase',
                '',
                'npc_gd_p',
                0, [],
                specify_img='nature'
            )
            inventory.ITEMS['npc_gd_c'] = inventory.Inventory.Item(
                'Chat',
                '',
                'npc_gd_c',
                0, [],
                specify_img='soul'
            )

            inventory.ITEMS['npc_gd_c_1'] = inventory.Inventory.Item(
                'Who are you?',
                '',
                'npc_gd_c_1',
                0, [],
                specify_img='soul'
            )
            inventory.ITEMS['npc_gd_c_2'] = inventory.Inventory.Item(
                'About this world',
                '',
                'npc_gd_c_2',
                0, [],
                specify_img='leaf'
            )
            inventory.ITEMS['npc_gd_c_4'] = inventory.Inventory.Item(
                'Notebook',
                '',
                'npc_gd_c_4',
                0, [],
                specify_img='worn_notebook'
            )
            inventory.ITEMS['npc_gd_c_3'] = inventory.Inventory.Item(
                'Angel?',
                '',
                'npc_gd_c_3',
                0, [],
                specify_img='chaos_reap'
            )
            inventory.ITEMS['npc_gd_c_5'] = inventory.Inventory.Item(
                'Happiness',
                '',
                'npc_gd_c_5',
                0, [],
                specify_img='weak_healing_potion'
            )
            inventory.ITEMS['npc_gd_c_cm'] = inventory.Inventory.Item(
                'Christmas!',
                'cmMerry christmas!',
                'npc_gd_c_cm',
                0, [],
                specify_img='snowball'
            )

            inventory.ITEMS['npc_gd_furnace'] = inventory.Inventory.Item(
                'Furnace',
                'col00ff00Cost: 100 NATURE.',
                'npc_gd_furnace',
                1, [],
                specify_img='furnace'
            )
            inventory.ITEMS['npc_gd_anvil'] = inventory.Inventory.Item(
                'Anvil',
                'col00ff00Cost: 100 NATURE.',
                'npc_gd_anvil',
                1, [],
                specify_img='anvil'
            )
            inventory.ITEMS['npc_gd_weak_healing_potion'] = inventory.Inventory.Item(
                'Weak Healing Potion',
                'col00ff00Cost: 120 NATURE.',
                'npc_gd_weak_healing_potion',
                1, [],
                specify_img='weak_healing_potion'
            )
            inventory.ITEMS['npc_gd_weak_magic_potion'] = inventory.Inventory.Item(
                'Weak Magic Potion',
                'col00ff00Cost: 80 NATURE.',
                'npc_gd_weak_magic_potion',
                1, [],
                specify_img='weak_magic_potion'
            )
            inventory.ITEMS['npc_gd_potion_of_memory'] = inventory.Inventory.Item(
                'Potion of Memory',
                'col00ff00Cost: 250 NATURE.',
                'npc_gd_potion_of_memory',
                1, [],
                specify_img='potion_of_memory'
            )
            inventory.ITEMS['npc_gd_watcher_wand'] = inventory.Inventory.Item(
                'Watcher Wand',
                'col00ffffSummon a sudden beam.\ncol00ff00Cost: 300 NATURE.',
                'npc_gd_watcher_wand',
                2, [],
                specify_img='watcher_wand'
            )
            inventory.ITEMS['npc_gd_cactus_wand'] = inventory.Inventory.Item(
                'Cactus Wand',
                'col00ffffSummon a stationary cactus.\ncol00ff00Cost: 300 NATURE.',
                'npc_gd_cactus_wand',
                2, [],
                specify_img='cactus_wand'
            )
            inventory.ITEMS['npc_gd_blood_ingot'] = inventory.Inventory.Item(
                'Blood Ingot',
                'col00ffffStrong condense of blood.\ncol00ff00Cost: 800 NATURE.',
                'npc_gd_blood_ingot',
                2, [],
                specify_img='blood_ingot'
            )
            inventory.ITEMS['npc_gd_aimer'] = inventory.Inventory.Item(
                'Aimer',
                'col00ffffIt targets to the bosses.\ncol00ff00Cost: 500 NATURE.',
                'npc_gd_aimer',
                2, [],
                specify_img='aimer'
            )
            inventory.ITEMS['npc_gd_bloodstone_amulet'] = inventory.Inventory.Item(
                'Bloodstone Amulet',
                'col00ffffBleeding is meaningless to you.\ncol00ff00Cost: 1200 NATURE.',
                'npc_gd_bloodstone_amulet',
                4, [],
                specify_img='bloodstone_amulet'
            )
            inventory.ITEMS['npc_gd_traveller_boots'] = inventory.Inventory.Item(
                'Traveller boots',
                'col00ffffSpeeds you up quickly.\ncol00ff00Cost: 1200 NATURE.',
                'npc_gd_traveller_boots',
                4, [],
                specify_img='traveller_boots'
            )
            inventory.ITEMS['npc_gd_the_desert_eagle'] = inventory.Inventory.Item(
                'The Desert Eagle',
                'col00ffffBiu biu biu!\ncol00ff00Cost: 4000 NATURE.',
                'npc_gd_the_desert_eagle',
                4, [],
                specify_img='the_desert_eagle'
            )
            inventory.ITEMS['npc_gd_rock_ball'] = inventory.Inventory.Item(
                'Rock Ball',
                'col00ffffA slow but strong magic!\ncol00ff00Cost: 4000 NATURE.',
                'npc_gd_rock_ball',
                4, [],
                specify_img='rock_ball'
            )
            inventory.ITEMS['npc_gd_mithrill_anvil'] = inventory.Inventory.Item(
                'Mithrill Anvil',
                'col00ff00Cost: 1000 NATURE.',
                'npc_gd_mithrill_anvil',
                5, [],
                specify_img='mithrill_anvil'
            )
            inventory.ITEMS['npc_gd_life_core'] = inventory.Inventory.Item(
                'Life core',
                'col00ffffSo much life!\ncol00ff00Cost: 6000 NATURE.',
                'npc_gd_life_core',
                6, [],
                specify_img='life_core',
            )
            inventory.ITEMS['npc_gd_wildsands'] = inventory.Inventory.Item(
                'Wildsands',
                'col00ffffSummon more sands!\ncol00ff00Cost: 18000 NATURE.',
                'npc_gd_wildsands',
                7, [],
                specify_img='wildsands',
            )
            inventory.ITEMS['npc_gd_soul_resonancer'] = inventory.Inventory.Item(
                'Soul Resonancer',
                'col00ff00Cost: 12000 NATURE.',
                'npc_gd_soul_resonancer',
                7, [],
                specify_img='soul_resonancer',
            )
        self.obj.pos << vector.Vector2D(game.get_game().player.tick / 8, 200)
        super().t_draw()

        player = game.get_game().player

        if player.open_chest == self.chest:
            while player.inventory.is_enough(inventory.ITEMS['npc_gd_p']):
                self.state = 1
                player.inventory.remove_item(inventory.ITEMS['npc_gd_p'])
            while player.inventory.is_enough(inventory.ITEMS['npc_gd_c']):
                self.state = 2
                player.inventory.remove_item(inventory.ITEMS['npc_gd_c'])
            while player.inventory.is_enough(inventory.ITEMS['npc_gd_home']):
                self.state = 0
                player.inventory.remove_item(inventory.ITEMS['npc_gd_home'])

            while player.inventory.is_enough(inventory.ITEMS['npc_gd_c_1']):
                self.state = 0
                game.get_game().dialog.dialog(self.name + ', \nthis is my name.', 'I\'m a "guidance"?\nI forgot.')
                player.inventory.remove_item(inventory.ITEMS['npc_gd_c_1'])
            while player.inventory.is_enough(inventory.ITEMS['npc_gd_c_2']):
                self.state = 0
                words = [
                    ['What, you\'re unhealthy?\n "go hell"!', 'I mean, \ngo hell...?'],
                    ["Healthy enough?\nThe ancient desert may be useful..."],
                    ["Heaven is a good place...", "But also dangerous..."],
                    ["Rainforest?", "Is'nt it also a forest?"]
                ]
                game.get_game().dialog.dialog(*random.choice(words))
                player.inventory.remove_item(inventory.ITEMS['npc_gd_c_2'])
            while player.inventory.is_enough(inventory.ITEMS['npc_gd_c_3']):
                self.state = 0
                game.get_game().dialog.dialog(
                    'Angel?\nHa, that\'s a legend...',
                    'In the myth, when the world is still in chaos...\n'
                    'An angel saved us..?',
                    'Ridiculous, \nright?'
                )
                if 'ray' in game.get_game().npc_data:
                    game.get_game().dialog.push_dialog(
                        'What?\nHe is right there?!!',
                        'Where?\nYou must be kidding.'
                    )
                if 'MS1' not in game.get_game().player.nts:
                    game.get_game().player.nts.append('MS1')
                    game.get_game().dialog.push_dialog(
                        'Anyway, take this.',
                        '[Notebook Updated!]'
                    )
                player.inventory.remove_item(inventory.ITEMS['npc_gd_c_3'])
            while player.inventory.is_enough(inventory.ITEMS['npc_gd_c_4']):
                self.state = 0
                game.get_game().dialog.dialog(
                    'Em....\nYour notebook seems mysterious...',
                    'You have to check it rapidly, okay?'
                )
                player.inventory.remove_item(inventory.ITEMS['npc_gd_c_4'])
            while player.inventory.is_enough(inventory.ITEMS['npc_gd_c_5']):
                self.state = 0
                game.get_game().dialog.dialog(
                    'This place is great for me.'
                )
                if 'ray' in game.get_game().npc_data:
                    game.get_game().dialog.push_dialog(
                        'Ray?\nWho is he?'
                    )
                if 'jevil' in game.get_game().npc_data:
                    game.get_game().dialog.push_dialog(
                        '...and that crazy joker...\nCan you stop him from jumping around?',
                        'He just messed all up...'
                    )
                player.inventory.remove_item(inventory.ITEMS['npc_gd_c_5'])
            while player.inventory.is_enough(inventory.ITEMS['npc_gd_c_cm']):
                self.state = 0

                if not 'TS' in player.nts:
                    player.nts.append('TS')
                    player.nts.append('MSC1')
                    notebook.start_write()
                    game.get_game().dialog.push_dialog('...?', 'What happened to you?\nYou\'ve been staring at me for an hour!!', 'Anyway, ')
                game.get_game().dialog.push_dialog(
                    'Merry christmas!',
                    'Em...\nIs the world a bit unusual now?'
                )
                player.inventory.remove_item(inventory.ITEMS['npc_gd_c_cm'])


            tars = [
                ('npc_gd_furnace', 'furnace', 100),
                ('npc_gd_anvil', 'anvil', 100),
                ('npc_gd_weak_healing_potion', 'weak_healing_potion', 120),
                ('npc_gd_weak_magic_potion', 'weak_magic_potion', 80),
                ('npc_gd_potion_of_memory', 'potion_of_memory', 250),
                ('npc_gd_watcher_wand', 'watcher_wand', 300),
                ('npc_gd_cactus_wand', 'cactus_wand', 300),
                ('npc_gd_blood_ingot', 'blood_ingot', 160),
                ('npc_gd_aimer', 'aimer', 500),
                ('npc_gd_bloodstone_amulet', 'bloodstone_amulet', 1200),
                ('npc_gd_traveller_boots', 'traveller_boots', 1200),
                ('npc_gd_the_desert_eagle', 'the_desert_eagle', 4000),
                ('npc_gd_rock_ball', 'rock_ball', 4000),
                ('npc_gd_mithrill_anvil', 'mithrill_anvil', 1000),
                ('npc_gd_life_core', 'life_core', 600),
                ('npc_gd_wildsands', 'wildsands', 18000),
                ('npc_gd_soul_resonancer', 'soul_resonancer', 12000),
            ]

            for it, tt, nn in tars:
                while player.inventory.is_enough(inventory.ITEMS[it]):
                    player.inventory.remove_item(inventory.ITEMS[it])
                    if player.inventory.is_enough(inventory.ITEMS['nature'], nn):
                        player.inventory.remove_item(inventory.ITEMS['nature'], nn)
                        player.inventory.add_item(inventory.ITEMS[tt])
                    else:
                        break

            if self.state == 0:
                self.chest.items = copy.copy(self.ct1)
                self.chest.n = len(self.ct1)
            elif self.state == 1:
                self.chest.items = copy.copy(self.ct2)
                self.chest.n = len(self.ct2)
                if game.get_game().stage > 0:
                    self.chest.items.extend(copy.copy(self.ct2_a))
                    self.chest.n += len(self.ct2_a)
            elif self.state == 2:
                self.chest.items = copy.copy(self.ct3)
                self.chest.n = len(self.ct3)

@entity.Entities.entity_type
class Ray(entity.Entities.Entity):
    NAME = 'Ray'
    BOSS_NAME = '"Spirit Angel"'
    DISPLAY_MODE = 3
    IS_MENACE = True
    LOOT_TABLE = entity.LootTable([
    ])

    SOUND_SPAWN = 'boss'
    SOUND_HURT = 'crystal'

    DR = 0

    def __init__(self, pos):
        super().__init__(pos, game.get_game().graphics['entity_ray'], entity.BuildingAI, 500)
        self.dr = .7
        self.dl = 1
        self.lhp = self.hp_sys.hp
        self.dhp = self.hp_sys.max_hp * (40 + self.DR * 120)
        self.hp_sys.IMMUNE = True
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = 120
        self.hp_sys.defenses[damages.DamageTypes.PIERCING] = 120
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = 120
        self.tick = 0
        self.state = 0
        self.projs = []
        self.dp = 0
        self.obj.MASS = 100
        self.obj.TOUCHING_DAMAGE = 100 + self.DR * 400
        self.obj.FRICTION = .95
        self.obj.SPEED *= 1 + self.DR * .8
        self.tr = 0
        game.get_game().dialog.dialog('I see...', 'It\'s you...')

    def t_draw(self):
        if self.hp_sys.IMMUNE:
            if game.get_game().dialog.is_done():
                self.hp_sys.IMMUNE = False
            return
        cw = ''
        self.hp_sys.heal(.08)
        ah = self.lhp - self.hp_sys.hp
        self.dl -= ah / self.dhp
        if self.dl < self.dr and self.dr >= .1:
            self.dl += .2
            self.dr -= .1
            game.get_game().player.hp_sys.heal(.2 * self.hp_sys.max_hp)
            self.tick = -100
        self.hp_sys.hp = (1 + self.hp_sys.max_hp) * self.dl - 1

        if self.hp_sys.hp <= 10:
            cw = 'items_weapons_chaos_teleporter'
            self.hp_sys.IMMUNE = True
            self.hp_sys.hp -= .05
        else:
            self.lhp = self.hp_sys.hp
        ar = math.sin(self.tick / 60 * math.pi) * 20 + 20
        iml = entity.entity_get_surface(1, -ar, game.get_game().player.get_screen_scale(),
                                 game.get_game().graphics['entity_ray_lwing'])
        imlr = iml.get_rect(center=position.displayed_position(self.obj.pos - vector.Vector2D(dx=50)))
        game.get_game().displayer.canvas.blit(iml, imlr)
        imr = entity.entity_get_surface(1, ar, game.get_game().player.get_screen_scale(),
                                 game.get_game().graphics['entity_ray_rwing'])
        imrr = imr.get_rect(center=position.displayed_position(self.obj.pos + vector.Vector2D(dx=50)))
        game.get_game().displayer.canvas.blit(imr, imrr)
        self.tick += 1

        if self.tick > 360:
            self.state = (self.state + 1) % 5
            self.tick = 0

        if self.hp_sys.hp <= 10:
            if self.obj.MASS < 120000:
                if self.DR:
                    game.get_game().dialog.dialog('Good.')
                    if 'ray' in game.get_game().npc_data:
                        game.get_game().npc_data['ray']['acc'] += self.DR * 3
                else:
                    game.get_game().dialog.dialog('Great.', 'Results as expected.', 'And here, is your reward.')
                self.hp_sys.hp = 0
                if 'ray' not in game.get_game().npc_data:
                    game.get_game().furniture.append(NPCRay((0,0)))
                else:
                    game.get_game().npc_data['ray']['acc'] = max(game.get_game().npc_data['ray']['acc'], 2)
                sf = 0
                if 'T1' not in game.get_game().player.nts:
                    game.get_game().player.nts.append('T1')
                    sf = 1
                if 'T2' not in game.get_game().player.nts:
                    game.get_game().player.nts.append('T2')
                    sf = 1
                if sf:
                    notebook.start_write()
                f = 0
                if 'MD1' not in game.get_game().player.nts:
                    game.get_game().player.nts.append('MD1')
                    f = 1
                if f and not sf:
                    game.get_game().dialog.push_dialog(
                        '[Notebook Updated!]'
                    )

            self.obj.MASS += 1500000

        elif self.tick < 0:
            cw = 'items_weapons_life_wand'
        elif self.state == 0:
            ap = self.obj.pos - game.get_game().player.obj.pos

            l = ap.x < 0
            u = ap.y < 0

            if self.tick % 200 < 66:
                tp = game.get_game().player.obj.pos - vector.Vector2D(dx=1000) * [-1, 1][l]
            elif self.tick % 200 < 133:
                tp = game.get_game().player.obj.pos - vector.Vector2D(dy=1000) * [-1, 1][u]
            else:
                tp = game.get_game().player.obj.pos - vector.Vector2D(dx=700) * [-1, 1][l] - vector.Vector2D(dy=700) * [-1, 1][u]

            self.obj.apply_force((tp - self.obj.pos) / 7)

            if self.tick % 40 <= 30:
                cw = 'items_weapons_fireball_magic'
                if self.tick % 3 == 0:
                    fb = entity.Entities.MagmaKingFireball(self.obj.pos, random.randint(0, 360))
                    fb.DMG = 120 + self.DR * 200
                    fb.show_bar = False
                    self.projs.append(fb)
            self.dp = game.get_game().player.obj.pos.to_value()
        elif self.state == 1:
            for p in self.projs:
                p.obj.SPEED = 0
            adp = game.get_game().player.obj.pos - self.dp
            game.get_game().player.obj.velocity -= adp / 200
            pg.draw.line(game.get_game().displayer.canvas, (0, 0, 0),
                         position.displayed_position(game.get_game().player.obj.pos),
                         position.displayed_position(self.dp), 5)
            pg.draw.line(game.get_game().displayer.canvas, (0, 0, 0),
                         position.displayed_position(game.get_game().player.obj.pos),
                         position.displayed_position(self.obj.pos), 5)
            if self.tick < 40:
                cw = 'items_weapons_dark_restrict'
                dr = self.tick * 40
                pg.draw.circle(game.get_game().displayer.canvas, (0, 0, 0),
                                position.displayed_position(self.dp),
                               dr / game.get_game().player.get_screen_scale(), 5)
            else:
                if self.tick % 60 == 1:
                    self.tr = random.randint(0, 360)
                elif self.tick % 60 < 40:
                    tp = game.get_game().player.obj.pos - vector.Vector2D(self.tr, 600)
                    self.obj.IS_OBJECT = False
                    self.obj.TOUCHING_DAMAGE = 50 + self.DR * 300
                    self.obj.apply_force((tp - self.obj.pos) / 3)

                    cw = 'items_weapons_fruit_wand'
                    if self.tick % 12 == 0:
                        fb = entity.Entities.FallingApple(game.get_game().player.obj.pos + (random.randint(-1000, 1000), -1000), random.randint(0, 360))
                        fb.DMG = 120 + self.DR * 200
                        fb.show_bar = False
                        self.projs.append(fb)
                else:
                    self.obj.TOUCHING_DAMAGE = 150 + self.DR * 400
                    cw = 'items_weapons_valkyrien'
                    self.obj.IS_OBJECT = True
                    self.obj.apply_force(vector.Vector(self.tr, 3000))
                pg.draw.circle(game.get_game().displayer.canvas, (0, 0, 0),
                                position.displayed_position(self.dp),
                               1600 / game.get_game().player.get_screen_scale(), 5)
        elif self.state == 2:
            cw = 'items_weapons_starfury'
            tp = game.get_game().player.obj.pos
            self.obj.apply_force((tp - self.obj.pos) / 10)
            if self.tick % 40 == 0:
                for ar in range(0, 360, 60 - (constants.DIFFICULTY // 2 + 1) * 15):
                    self.projs.append(entity.Entities.RStarfury(game.get_game().player.obj.pos + vector.Vector2D(ar + self.tick // 2, 400), 0))
        elif self.state == 3:
            ap = self.obj.pos - game.get_game().player.obj.pos

            l = ap.x < 0
            u = ap.y < 0



            if self.tick % 70 <= 30:
                self.obj.TOUCHING_DAMAGE = 50 + self.DR * 200
                if self.tick % 200 < 66:
                    tp = game.get_game().player.obj.pos - vector.Vector2D(dx=500) * [-1, 1][l]
                elif self.tick % 200 < 133:
                    tp = game.get_game().player.obj.pos - vector.Vector2D(dy=500) * [-1, 1][u]
                else:
                    tp = game.get_game().player.obj.pos - vector.Vector2D(dx=350) * [-1, 1][l] - vector.Vector2D(
                        dy=700) * [-1, 1][u]
                cw = 'items_weapons_fireball_magic'
                if self.tick % 15 == 0:
                    for ar in range(0, 360, 60 - (constants.DIFFICULTY + 1) // 2 * 15):
                        fb = entity.Entities.MagmaKingFireball(self.obj.pos, ar + self.tick // 2)
                        fb.DMG = 100 + self.DR * 200
                        fb.show_bar = False
                        self.projs.append(fb)
            else:
                tp = game.get_game().player.obj.pos
                cw = 'items_weapons_starfury'
                self.obj.TOUCHING_DAMAGE = 150
                if self.tick % 15 == 0:
                    fb = entity.Entities.RStarfury(game.get_game().player.obj.pos, 0)
                    fb.DMG = 160 + self.DR * 200
                    fb.show_bar = False
                    self.projs.append(fb)

            self.obj.apply_force((tp - self.obj.pos) / 7)
            self.dp = game.get_game().player.obj.pos.to_value()
        elif self.state == 4:
            dr = self.tick * 2 // 3
            tp = vector.Vector2D(dr, 1500) + self.dp
            self.obj.apply_force((tp - self.obj.pos) / 3)

            self.obj.IS_OBJECT = True
            if self.tick % 200 < 150:
                self.obj.TOUCHING_DAMAGE = 50
                cw = 'items_weapons_fireball_magic'
                if self.tick % 5 == 0:
                    sr = dr + 20 - constants.DIFFICULTY * 5
                    for ar in range(0, 360, 90):
                        fb = entity.Entities.MagmaKingFireball(self.obj.pos, ar + sr)
                        fb.DMG = 100 + self.DR * 200
                        fb.show_bar = False
                        self.projs.append(fb)
            elif self.tick % 200 < 160:
                cw = 'items_weapons_dark_restrict'
                pg.draw.line(game.get_game().displayer.canvas, (0, 0, 0),
                             position.displayed_position(self.dp),
                             position.displayed_position(game.get_game().player.obj.pos),
                             5)
            else:
                self.obj.TOUCHING_DAMAGE = 150 + self.DR * 400
                cw = 'items_weapons_star_wrath'
                pg.draw.line(game.get_game().displayer.canvas, (0, 0, 0),
                             position.displayed_position(self.dp),
                             position.displayed_position(game.get_game().player.obj.pos),
                             5)
                if self.tick % 10 == 0:
                    for ar in range(0, 360, 60 - (constants.DIFFICULTY + 1) // 2 * 15):
                        for dt in range(100, 1000, 150):
                            fb = entity.Entities.RStarfury(vector.Vector2D(ar + dr, dt) + self.dp, 0)
                            fb.DMG = 120 + self.DR * 200
                            fb.show_bar = False
                            self.projs.append(fb)
                ap = self.obj.pos - game.get_game().player.obj.pos

                l = ap.x < 0
                u = ap.y < 0

                if self.tick % 200 < 66:
                    tp = game.get_game().player.obj.pos - vector.Vector2D(dx=1000) * [-1, 1][l]
                elif self.tick % 200 < 133:
                    tp = game.get_game().player.obj.pos - vector.Vector2D(dy=1000) * [-1, 1][u]
                else:
                    tp = game.get_game().player.obj.pos - vector.Vector2D(dx=700) * [-1, 1][l] - vector.Vector2D(
                        dy=700) * [-1, 1][u]

                self.obj.apply_force((tp - self.obj.pos) / 10)

        if len(cw):
            ar = vector.coordinate_rotation(*(game.get_game().player.obj.pos - self.obj.pos))
            wp = pg.transform.scale_by(game.get_game().graphics[cw], 1 / game.get_game().player.get_screen_scale())
            wp = pg.transform.rotate(wp, 90 - ar)
            wpr = wp.get_rect(center=position.displayed_position(self.obj.pos))
            game.get_game().displayer.canvas.blit(wp, wpr)

        for p in self.projs:
            p.t_draw()
            if p.hp_sys.hp <= 0:
                self.projs.remove(p)

        super().t_draw()

    def on_update(self):
        super().on_update()
        for p in self.projs:
            p.on_update()

class Ray1(Ray):
    DR = 1
class Ray2(Ray):
    DR = 2.5
class Ray3(Ray):
    DR = 5.5

@entity.Entities.entity_type
class NPCRay(Chest):

    def __init__(self, pos):
        if 'ray' not in game.get_game().npc_data:
            self.name = 'Ray'
            game.get_game().npc_data['ray'] = {'name': self.name, 'acc': 3}
        else:
            self.name = game.get_game().npc_data['ray']['name']
        if not 'pc' in game.get_game().npc_data['ray']:
            game.get_game().npc_data['ray']['pc'] = []
        self.purchase = game.get_game().npc_data['ray']['pc']
        self.datas = game.get_game().npc_data['ray']
        super().__init__(pos)
        self.tick = 0
        self.img = copy.copy(game.get_game().graphics['entity_ray'])

        self.ii_set = False

        self.ct1 = [('npc_ray_f', 1), ('npc_ray_p', 1), ('npc_ray_c', 1)]
        self.ct2 = [('npc_ray_home', 1), ('npc_ray_chaos_reap', 1), ('npc_ray_fate', 1), ('npc_ray_chaos_vocalist_headgear', 1), ('npc_ray_chaos_vocalist_crown', 1),
                    ('npc_ray_chaos_vocalist_shabby_cloak', 1), ('npc_ray_chaos_vocalist_traveller_boots', 1),
                    ('npc_ray_soulfeather', 81)]
        self.state = 0

        self.chest.items = self.ct1
        self.chest.n = len(self.ct1)
        self.chest.locked = True
        self.sm = False

    def get_shown_txt(self):
        return self.name, 'Press [E] to talk'

    def t_draw(self):

        if not self.ii_set:
            self.ii_set = True
            inventory.ITEMS['npc_ray_home'] = inventory.Inventory.Item(
                'Back',
                '',
                'npc_ray_home',
                0, [],
                specify_img='checkpoint'
            )
            inventory.ITEMS['npc_ray_f'] = inventory.Inventory.Item(
                'Curse',
                'col600000You will never want this.',
                'npc_ray_f',
                0, [],
                specify_img='platinum_sword'
            )
            inventory.ITEMS['npc_ray_p'] = inventory.Inventory.Item(
                'Purchase',
                '',
                'npc_ray_p',
                0, [],
                specify_img='nature'
            )
            inventory.ITEMS['npc_ray_c'] = inventory.Inventory.Item(
                'Chat',
                '',
                'npc_ray_p',
                0, [],
                specify_img='chaos_reap'
            )

            inventory.ITEMS['npc_ray_chaos_reap'] = inventory.Inventory.Item(
                'Chaos Reap',
                'rainbowThe reward you deserve.\ncol00ff00Cost: 0 NATURE',
                'npc_ray_chaos_reap',
                12, [],
                specify_img='chaos_reap'
            )
            inventory.ITEMS['npc_ray_fate'] = inventory.Inventory.Item(
                'Fate',
                'rainbowA quick time magic.\ncol00ff00Cost: 24000 NATURE',
                'npc_ray_fate',
                6, [],
                specify_img='fate'
            )
            inventory.ITEMS['npc_ray_forbidden_curse__water'] = inventory.Inventory.Item(
                'Forbidden Curse: Water',
                'rainbowPowerful magic.\ncol00ff00Cost: 35000 NATURE\ncol00ff00Require: 10 talent',
                'npc_ray_forbidden_curse__water',
                7, [],
                specify_img='forbidden_curse__water'
            )
            inventory.ITEMS['npc_ray_chaos_vocalist_shabby_cloak'] = inventory.Inventory.Item(
                'Chaos Vocalist Shabby Cloak',
                'rainbowPerfect for all magisters.\ncol00ff00Cost: 40000 NATURE',
                'npc_ray_chaos_vocalist_shabby_cloak',
                9, [],
                specify_img='chaos_vocalist_shabby_cloak'
            )
            inventory.ITEMS['npc_ray_chaos_vocalist_traveller_boots'] = inventory.Inventory.Item(
                'Chaos Vocalist Traveller Boots',
                'rainbowPerfect for all magisters.\ncol00ff00Cost: 40000 NATURE',
                'npc_ray_chaos_vocalist_traveller_boots',
                9, [],
                specify_img='chaos_vocalist_traveller_boots'
            )
            inventory.ITEMS['npc_ray_chaos_vocalist_headgear'] = inventory.Inventory.Item(
                'Chaos Vocalist Headgear',
                'rainbowPerfect for all magisters.\ncol00ff00Cost: 40000 NATURE',
                'npc_ray_chaos_vocalist_headgear',
                9, [],
                specify_img='chaos_vocalist_headgear'
            )
            inventory.ITEMS['npc_ray_chaos_vocalist_crown'] = inventory.Inventory.Item(
                'Chaos Vocalist Crown',
                'rainbowFor those who seek to overcome the darkness.\ncol00ff00Cost: 60000 NATURE',
                'npc_ray_chaos_vocalist_crown',
                11, [],
                specify_img='chaos_vocalist_crown'
            )
            inventory.ITEMS['npc_ray_soulfeather'] = inventory.Inventory.Item(
                'Soulfeather',
                'rainbowAccelerate until nobody will ever faster than you.\ncol00ff00Cost: 818181 NATURE',
                'npc_ray_soulfeather',
                13, [],
                specify_img='soulfeather'
            )

        if len([1 for e in game.get_game().entities if issubclass(type(e), Ray)]):
            return

        player = game.get_game().player
        self.set_rotation(self.rot)

        if player.open_chest == self.chest:

            while player.inventory.is_enough(inventory.ITEMS['npc_ray_f']):
                rs = Ray
                entity.entity_spawn(rs, 1600, 1600, 0, 1145, 100000)
                self.datas['acc'] = max(self.datas['acc'], 1)
                player.inventory.remove_item(inventory.ITEMS['npc_ray_f'])
            while player.inventory.is_enough(inventory.ITEMS['npc_ray_p']):
                self.state = 1
                player.inventory.remove_item(inventory.ITEMS['npc_ray_p'])
            while player.inventory.is_enough(inventory.ITEMS['npc_ray_home']):
                self.state = 0
                player.inventory.remove_item(inventory.ITEMS['npc_ray_home'])

            ps = [
                ('npc_ray_chaos_reap', 'chaos_reap', 0, 3, None),
                ('npc_ray_fate', 'fate', 24000, 1, None),
                ('npc_ray_fate', 'forbidden_curse__water', 35000, 1, lambda: player.max_talent >= 10),
                ('npc_ray_chaos_vocalist_shabby_cloak', 'chaos_vocalist_shabby_cloak', 40000, 2, None),
                ('npc_ray_chaos_vocalist_traveller_boots', 'chaos_vocalist_traveller_boots', 40000, 2, None),
                ('npc_ray_chaos_vocalist_headgear', 'chaos_vocalist_headgear', 40000, 2, None),
                ('npc_ray_chaos_vocalist_crown', 'chaos_vocalist_crown', 60000, 3, None),
                ('npc_ray_soulfeather', 'soulfeather', 10101, 3, None),
            ]

            for it, tt, nn, rac, rq in ps:
                while player.inventory.is_enough(inventory.ITEMS[it]):
                    player.inventory.remove_item(inventory.ITEMS[it])
                    if rq is not None and not rq():
                        continue
                    if player.inventory.is_enough(inventory.ITEMS['nature'], nn) and self.datas['acc'] >= rac:
                        player.inventory.remove_item(inventory.ITEMS['nature'], nn)
                        player.inventory.add_item(inventory.ITEMS[tt])
                    else:
                        break

            ni = 1
            if game.get_game().stage > 4:
                ni = 9
            elif game.get_game().stage > 1:
                ni = 7
            elif game.get_game().stage > 0:
                ni = 3

            if self.state == 0:
                self.chest.items = copy.copy(self.ct1)
                self.chest.n = len(self.ct1)
            if self.state == 1:
                self.chest.items = copy.copy(self.ct2)
                self.chest.n = len(self.ct2)

        self.obj.pos << (0, min(0, max(-300, game.get_game().player.obj.pos[1] - 100)))
        ap = max(0, 255 - int(abs(game.get_game().player.obj.pos - self.obj.pos) / 6))
        self.img.set_alpha(ap)
        ar = math.sin(self.tick / 60 * math.pi) * 20 + 20
        iml = entity.entity_get_surface(1, -ar, game.get_game().player.get_screen_scale(),
                                 game.get_game().graphics['entity_ray_lwing'], alpha=ap)
        imlr = iml.get_rect(center=position.displayed_position(self.obj.pos - vector.Vector2D(dx=50)))
        game.get_game().displayer.canvas.blit(iml, imlr)
        imr = entity.entity_get_surface(1, ar, game.get_game().player.get_screen_scale(),
                                 game.get_game().graphics['entity_ray_rwing'], alpha=ap)
        imrr = imr.get_rect(center=position.displayed_position(self.obj.pos + vector.Vector2D(dx=50)))
        game.get_game().displayer.canvas.blit(imr, imrr)
        self.tick += 1
        super().t_draw()

@entity.Entities.entity_type
class NPCJevil(Chest):
    def __init__(self, pos):
        if 'jevil' not in game.get_game().npc_data:
            self.name = 'Jevil'
            game.get_game().npc_data['jevil'] = {'name': self.name}
        else:
            self.name = game.get_game().npc_data['jevil']['name']
        self.datas = game.get_game().npc_data['jevil']
        super().__init__(pos)
        self.tick = 0
        self.img = copy.copy(game.get_game().graphics['entity_jevil'])

        self.ii_set = False

        self.ct1 = [('npc_jevil_f', 1), ('npc_jevil_p', 1), ('npc_jevil_c', 1), ('npc_jevil_tp', 1)]
        self.ct2 = [('npc_jevil_home', 1), ('npc_jevil_chaos_chaos', 1), ('npc_jevil_chaos_ingot', 200),
                    ('npc_jevil_arrayed_amulet', 1)]
        self.ct4 = [('npc_jevil_home', 1), ('npc_jevil_tp_0', 1),
                    ('npc_jevil_tp_1', 1), ('npc_jevil_tp_2', 1),
                    ('npc_jevil_tp_3', 1)]
        self.state = 0

        self.chest.items = self.ct1
        self.chest.n = len(self.ct1)
        self.chest.locked = True
        self.obj.pos << (math.sin(game.get_game().player.tick / 60 * math.pi) * 800, -400)
        self.sm = False

    def get_shown_txt(self):
        return self.name, 'Press [E] to talk'

    def t_draw(self):
        super().t_draw()
        self.obj.pos << (math.sin(game.get_game().player.tick / 60 * math.pi) * 800, -400)

        if not self.ii_set:
            self.ii_set = True
            inventory.ITEMS['npc_jevil_home'] = inventory.Inventory.Item(
                'Back',
                '',
                'npc_jevil_home',
                0, [],
                specify_img='checkpoint'
            )
            inventory.ITEMS['npc_jevil_f'] = inventory.Inventory.Item(
                'Curse',
                'SOME FUN, SOME FUN!',
                'npc_jevil_f',
                0, [],
                specify_img='platinum_sword'
            )
            inventory.ITEMS['npc_jevil_p'] = inventory.Inventory.Item(
                'Purchase',
                '',
                'npc_jevil_p',
                0, [],
                specify_img='nature'
            )
            inventory.ITEMS['npc_jevil_c'] = inventory.Inventory.Item(
                'Chat',
                '',
                'npc_jevil_c',
                0, [],
                specify_img='jevils_tail'
            )
            inventory.ITEMS['npc_jevil_tp'] = inventory.Inventory.Item(
                'Teleport',
                '',
                'npc_jevil_tp',
                0, [],
                specify_img='chaos_teleporter'
            )
            inventory.ITEMS['npc_jevil_tp_0'] = inventory.Inventory.Item(
                'Teleport: Ocean',
                '4000 NATURE',
                'npc_jevil_tp_0',
                0, [],
                specify_img='forgotten_shard'
            )
            inventory.ITEMS['npc_jevil_tp_1'] = inventory.Inventory.Item(
                'Teleport: Shallow Abyss - Hot Spring',
                '5000 NATURE',
                'npc_jevil_tp_1',
                0, [],
                specify_img='thermal_ingot'
            )
            inventory.ITEMS['npc_jevil_tp_2'] = inventory.Inventory.Item(
                'Teleport: Middle Abyss - Inner Chaos',
                '8000 NATURE',
                'npc_jevil_tp_2',
                0, [],
                specify_img='chaos_ingot'
            )
            inventory.ITEMS['npc_jevil_tp_3'] = inventory.Inventory.Item(
                'Teleport: Abyss - True Chaos',
                '12000 NATURE',
                'npc_jevil_tp_3',
                0, [],
                specify_img='origin_feather'
            )

            inventory.ITEMS['npc_jevil_chaos_chaos'] = inventory.Inventory.Item(
                'Chaos Chaos',
                'THESE CURTAINS ARE REALLY ON FIRE!\nCost: 75000 NATURE',
                'npc_jevil_chaos_chaos',
                0, [],
                specify_img='chaos_chaos'
            )
            inventory.ITEMS['npc_jevil_arrayed_amulet'] = inventory.Inventory.Item(
                'Arrayed Amulet',
                'VEE HEE HEE!\nCost: 100000 NATURE',
                'npc_jevil_arrayed_amulet',
                0, [],
                specify_img='arrayed_amulet'
            )
            inventory.ITEMS['npc_jevil_chaos_ingot'] = inventory.Inventory.Item(
                'Chaos Ingot',
                'SO MUCH FUN, MUCH FUN!\nCost: 15000 NATURE',
                'npc_jevil_chaos_ingot',
                0, [],
                specify_img='chaos_ingot'
            )


        player = game.get_game().player
        self.set_rotation(self.rot)

        if player.open_chest == self.chest:
            while player.inventory.is_enough(inventory.ITEMS['npc_jevil_f']):
                entity.entity_spawn(entity.Entities.Jevil, 1600, 1600, 0, 1145, 100000)
                player.inventory.remove_item(inventory.ITEMS['npc_jevil_f'])
            while player.inventory.is_enough(inventory.ITEMS['npc_jevil_p']):
                self.state = 1
                player.inventory.remove_item(inventory.ITEMS['npc_jevil_p'])
            while player.inventory.is_enough(inventory.ITEMS['npc_jevil_tp']):
                self.state = 3
                player.inventory.remove_item(inventory.ITEMS['npc_jevil_tp'])
            while player.inventory.is_enough(inventory.ITEMS['npc_jevil_home']):
                self.state = 0
                player.inventory.remove_item(inventory.ITEMS['npc_jevil_home'])

            pcs = [
                ('npc_jevil_chaos_chaos', 'chaos_chaos', 75000),
                ('npc_jevil_arrayed_amulet', 'arrayed_amulet', 100000),
                ('npc_jevil_chaos_ingot', 'chaos_ingot', 75)
            ]


            for it, tt, cs in pcs:
                while player.inventory.is_enough(inventory.ITEMS[it]):
                    player.inventory.remove_item(inventory.ITEMS[it])
                    if player.inventory.is_enough(inventory.ITEMS['nature'], cs):
                        player.inventory.remove_item(inventory.ITEMS['nature'], cs)
                        player.inventory.add_item(inventory.ITEMS[tt])
                    else:
                        break


            tps = [
                ('npc_jevil_tp_0', (0, 180000), 4000),
                ('npc_jevil_tp_1', (0, 270000), 5000),
                ('npc_jevil_tp_2', (0, 360000), 8000),
                ('npc_jevil_tp_3', (0, 500000), 12000),
            ]

            for it, tp, cs in tps:
                while player.inventory.is_enough(inventory.ITEMS[it]):
                    player.inventory.remove_item(inventory.ITEMS[it])
                    if player.inventory.is_enough(inventory.ITEMS['nature'], cs):
                        player.inventory.remove_item(inventory.ITEMS['nature'], cs)
                        player.obj.pos = vector.Vector2D(0, 0, *tp)
                        player.open_chest = None
                    else:
                        break

            if self.state == 0:
                self.chest.items = copy.copy(self.ct1)
                self.chest.n = len(self.ct1)
            if self.state == 1:
                self.chest.items = copy.copy(self.ct2)
                self.chest.n = len(self.ct2)
            if self.state == 3:
                self.chest.items = copy.copy(self.ct4)
                self.chest.n = len(self.ct4)


@entity.Entities.entity_type
class GreenChest(Chest):
    IMG = 'entity_green_chest'
    LOOT_TABLE = entity.LootTable([
        entity.SelectionLoot([('iron', 16, 22), ('steel', 16, 22), ('cobalt', 16, 22), ('silver', 16, 22), ('platinum', 6, 10), ('zirconium', 6, 10)], 1, 2),
        entity.IndividualLoot('leaf', 1, 10, 12),
        entity.SelectionLoot([('mana_flower', 1, 1), ('life_flower', 0, 1), ('star_amulet', 1, 1)], 1, 1),
        entity.SelectionLoot([('hermes_boots', 0, 1), ('lucky_clover', 1, 1), ('seed_amulet', 1, 1)], 1, 2),
        entity.IndividualLoot('fairy_wings', 0.1, 1, 1),
        entity.SelectionLoot([('purple_ring', 0, 1), ('cyan_ring', 0, 1), ('yellow_ring', 0, 1),
                        ('green_ring', 0, 1), ('blue_ring', 0, 1), ('orange_ring', 0, 1)], 1, 3),
        entity.IndividualLoot('potion_of_memory', .3, 1, 3),
    ])
    BIOMES = ['forest', 'rainforest']

    @staticmethod
    def is_suitable(biome: str):
        return biome in ['forest', 'rainforest']

@entity.Entities.entity_type
class RedChest(Chest):
    IMG = 'entity_red_chest'
    LOOT_TABLE = entity.LootTable([
        entity.SelectionLoot([('platinum', 5, 7), ('zirconium', 5, 7), ('magic_stone', 10, 12)], 1, 2),
        entity.IndividualLoot('firite_ingot', 0.5, 10, 12),
        entity.IndividualLoot('firy_plant', 0.4, 1, 4),
        entity.IndividualLoot('fireball_magic', 0.1, 1, 1),
        entity.SelectionLoot([('fire_gloves', 1, 1), ('quenched_cross', 1, 1), ('lava_walker', 1, 1)], 0, 2),
        entity.IndividualLoot('obsidian_ingot', 1, 22, 30),
        entity.IndividualLoot('potion_of_memory', .3, 1, 3),
    ])
    BIOMES = ['hell']
    TOUGHNESS = 7
    HP = 50

    @staticmethod
    def is_suitable(biome: str):
        return biome in ['hell']

@entity.Entities.entity_type
class WhiteChest(Chest):
    IMG = 'entity_white_chest'
    LOOT_TABLE = entity.LootTable([
        entity.SelectionLoot([('silver', 10, 12), ('steel', 10, 12), ('magic_stone', 10, 12)], 1, 2),
        entity.SelectionLoot([('coniferous_leaf', 100, 200), ('snowball', 100, 200)], 1, 1),
        entity.SelectionLoot([('white_guard', 1, 2), ('snowstorm_bottle', 1, 1), ('snow_wings', 0, 1)], 1, 1),
        entity.SelectionLoot([('purple_ring', 0, 1), ('cyan_ring', 0, 1), ('yellow_ring', 0, 1),
                        ('green_ring', 0, 1), ('blue_ring', 0, 1), ('orange_ring', 0, 1)], 1, 3),
        entity.IndividualLoot('potion_of_memory', .2, 1, 2),
    ])
    BIOMES = ['snowland']
    TOUGHNESS = 4
    HP = 40

    @staticmethod
    def is_suitable(biome: str):
        return biome in ['snowland']

@entity.Entities.entity_type
class OrangeChest(Chest):
    IMG = 'entity_orange_chest'
    LOOT_TABLE = entity.LootTable([
        entity.SelectionLoot([('platinum', 10, 12), ('zirconium', 10, 12), ('mana_crystal', 1, 3)], 1, 2),
        entity.IndividualLoot('copper', 1, 10, 12),
        entity.IndividualLoot('mysterious_substance', 0.1, 10, 30),
        entity.SelectionLoot([('rune_cross', 1, 1), ('rune_eye', 1, 1), ('rune_gloves', 1, 1)], 0, 1),
        entity.IndividualLoot('nice_cream', 0.3, 5, 12),
        entity.IndividualLoot('potion_of_memory', .2, 1, 2),
        ])
    BIOMES = ['desert']
    TOUGHNESS = 4
    HP = 40

    @staticmethod
    def is_suitable(biome: str):
        return biome in ['desert']

@entity.Entities.entity_type
class BlueChest(Chest):
    IMG = 'entity_blue_chest'
    LOOT_TABLE = entity.LootTable([
        entity.SelectionLoot([('platinum', 20, 32), ('zirconium', 20, 32), ('magic_stone', 10, 12)], 1, 2),
        entity.SelectionLoot([('iron_donut', 1, 3), ('heart_pie', 1, 3)], 1, 1),
        entity.IndividualLoot('floatstone', 1, 12, 20),
        entity.IndividualLoot('potion_of_memory', .3, 1, 3),
    ])
    BIOMES = ['heaven']
    TOUGHNESS = 7
    HP = 50

    @staticmethod
    def is_suitable(biome: str):
        return biome in ['heaven']

@entity.Entities.entity_type
class StoneAltar(Ore):
    DISPLAY_MODE = 3
    NAME = 'Stone Altar'
    IMG = 'entity_stone_altar'
    TOUGHNESS = 60

    def __init__(self, pos):
        super().__init__(pos, 100)

    def on_update(self):
        super().on_update()
        px = game.get_game().player.obj.pos[0] - self.obj.pos[0]
        py = game.get_game().player.obj.pos[1] - self.obj.pos[1]
        if vector.distance(px, py) < 1000:
            if not len([1 for e in game.get_game().player.hp_sys.effects if type(e) is effects.StoneAltar]):
                game.get_game().player.hp_sys.effect(effects.StoneAltar(5, 1))

@entity.Entities.entity_type
class MetalAltar(Ore):
    DISPLAY_MODE = 3
    NAME = 'Metal Altar'
    IMG = 'entity_metal_altar'
    TOUGHNESS = 88

    def __init__(self, pos):
        super().__init__(pos, 280)

    def on_update(self):
        super().on_update()
        px = game.get_game().player.obj.pos[0] - self.obj.pos[0]
        py = game.get_game().player.obj.pos[1] - self.obj.pos[1]
        if vector.distance(px, py) < 1500:
            if not len([1 for e in game.get_game().player.hp_sys.effects if type(e) is effects.MetalAltar]):
                game.get_game().player.hp_sys.effect(effects.MetalAltar(8, 1))

@entity.Entities.entity_type
class ScarlettAltar(Ore):
    DISPLAY_MODE = 3
    NAME = 'Scarlett Altar'
    IMG = 'entity_scarlett_altar'
    TOUGHNESS = 89

    def __init__(self, pos):
        super().__init__(pos, 400)

    def on_update(self):
        super().on_update()
        px = game.get_game().player.obj.pos[0] - self.obj.pos[0]
        py = game.get_game().player.obj.pos[1] - self.obj.pos[1]
        if vector.distance(px, py) < 1800:
            if not len([1 for e in game.get_game().player.hp_sys.effects if type(e) is effects.ScarlettAltar]):
                game.get_game().player.hp_sys.effect(effects.ScarlettAltar(10, 1))

@entity.Entities.entity_type
class CopperOre(Ore):
    IMG = 'entity_copper_ore'
    NAME = 'Copper Ore'
    TOUGHNESS = 0
    HP = 10
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('copper', 1, 20, 32),
        ])

@entity.Entities.entity_type
class IronOre(Ore):
    IMG = 'entity_iron_ore'
    NAME = 'Iron Ore'
    TOUGHNESS = 2
    HP = 12
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('iron', 1, 20, 25),
        ])
    def __init__(self, *args):
        super().__init__(*args)
        if game.get_game().fun in [1, 3, 4, 6, 11, 12]:
            self.NAME = 'Cobalt Ore'
            self.LOOT_TABLE = entity.LootTable([
                entity.IndividualLoot('cobalt', 1, 20, 25),
            ])

@entity.Entities.entity_type
class SteelOre(Ore):
    IMG = 'entity_steel_ore'
    NAME = 'Steel Ore'
    TOUGHNESS = 2
    HP = 12
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('steel', 1, 20, 25),
        ])
    def __init__(self, *args):
        super().__init__(*args)
        if game.get_game().fun in [1, 4, 7, 8, 9, 12]:
            self.NAME = 'Silver Ore'
            self.LOOT_TABLE = entity.LootTable([
                entity.IndividualLoot('silver', 1, 20, 25),
            ])

@entity.Entities.entity_type
class PlatinumOre(Ore):
    IMG = 'entity_platinum_ore'
    NAME = 'Platinum Ore'
    TOUGHNESS = 5
    HP = 16
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('platinum', 1, 28, 36),
        ])
    def __init__(self, *args):
        super().__init__(*args)
        if game.get_game().fun in [2, 3, 4, 6, 10, 12]:
            self.NAME = 'Zirconium Ore'
            self.LOOT_TABLE = entity.LootTable([
                entity.IndividualLoot('zirconium', 1, 28, 36),
            ])

@entity.Entities.entity_type
class MagicOre(Ore):
    IMG = 'entity_magic_ore'
    NAME = 'Magic Ore'
    TOUGHNESS = 7
    HP = 20
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('magic_stone', 1, 15, 18),
        ])

@entity.Entities.entity_type
class BloodOre(Ore):
    IMG = 'entity_blood_ore'
    NAME = 'Blood Ore'
    TOUGHNESS = 8
    HP = 35
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('cell_organization', 1, 12, 18),
        ])

@entity.Entities.entity_type
class FiriteOre(Ore):
    IMG = 'entity_firite_ore'
    NAME = 'Firite Ore'
    TOUGHNESS = 14
    HP = 50
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('firite_ingot', 1, 10, 12),
        ])

@entity.Entities.entity_type
class FiryOre(Ore):
    IMG = 'entity_firy_ore'
    NAME = 'Firy Ore'
    TOUGHNESS = 25
    HP = 72
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('firy_plant', 1, 1, 2),
        ])

@entity.Entities.entity_type
class MysteriousOre(Ore):
    IMG = 'entity_mysterious_ore'
    NAME = 'Mysterious Ore'
    TOUGHNESS = 30
    HP = 80
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('mysterious_substance', 1, 10, 12),
        ])

@entity.Entities.entity_type
class SpiritualOre(Ore):
    IMG = 'entity_spiritual_ore'
    NAME = 'Spiritual Ore'
    TOUGHNESS = 65
    HP = 200
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('soul', 1, 20, 24),
        ])

@entity.Entities.entity_type
class EvilOre(Ore):
    IMG = 'entity_evil_ore'
    NAME = 'Evil Ore'
    TOUGHNESS = 80
    HP = 240
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('evil_ingot', 1, 10, 12),
        ])

@entity.Entities.entity_type
class PalladiumOre(Ore):
    IMG = 'entity_palladium_ore'
    NAME = 'Palladium Ore'
    TOUGHNESS = 84
    HP = 300
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('palladium', 1, 20, 24),
        ])

@entity.Entities.entity_type
class MithrillOre(Ore):
    IMG = 'entity_mithrill_ore'
    NAME = 'Mithrill Ore'
    TOUGHNESS = 84
    HP = 300
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('mithrill', 1, 20, 24),
        ])

@entity.Entities.entity_type
class TitaniumOre(Ore):
    IMG = 'entity_titanium_ore'
    NAME = 'Titanium Ore'
    TOUGHNESS = 84
    HP = 300
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('titanium', 1, 20, 24),
        ])

@entity.Entities.entity_type
class TalentOre(Ore):
    IMG = 'entity_talent_ore'
    NAME = 'Talent Ore'
    TOUGHNESS = 128
    HP = 500
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('mystery_core', 1, 1, 3),
        ])

@entity.Entities.entity_type
class ChlorophyteOre(Ore):
    IMG = 'entity_chlorophyte_ore'
    NAME = 'Chlorophyte Ore'
    TOUGHNESS = 200
    HP = 1000
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('chlorophyte_ingot', 1, 2, 3),
        ])

@entity.Entities.entity_type
class SwordInTheStone(Ore):
    NAME = 'Sword in the Stone'
    DISPLAY_MODE = 3
    LOOT_TABLE = entity.LootTable([
       entity.SelectionLoot([('magic_sword', 1, 1), ('magic_blade', 1, 1)], 1, 1)
    ])
    IMG = 'entity_sword_in_the_stone'
    TOUGHNESS = 2

    def __init__(self, pos):
        super().__init__(pos, 100)

@entity.Entities.entity_type
class EvilMark(Ore):
    NAME = 'Evil Mark'
    DISPLAY_MODE = 3
    LOOT_TABLE = entity.LootTable([
        entity.IndividualLoot('soul', 0.9, 6, 7),
        entity.IndividualLoot('evil_ingot', 1, 10, 12),
    ])
    TOUGHNESS = 50
    IMG = 'entity_evil_mark'

    def __init__(self, pos):
        super().__init__(pos, 80)