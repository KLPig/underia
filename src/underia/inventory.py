from src.underia import weapons, projectiles, game
from src.values import damages


class Inventory:
    DEFAULT = 0
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    VERY_RARE = 4
    PROFICIENCY_MADE = 5
    EPIC = 6
    LEGENDARY = 7
    MASTERWORK = 8
    SUPREME = 9
    MYTHIC = 10
    SUPER_MYTHIC = 11
    GODLIKE = 12
    SUPER_GODLIKE = 13
    UNKNOWN = 114

    Rarity_Colors = [(127, 127, 127), (255, 255, 255), (180, 180, 255), (150, 255, 127), (127, 255, 255), (255, 127, 127),
                     (64, 255, 200), (255, 200, 64), (127, 64, 64), (255, 64, 64), (127, 20, 127), (255, 127, 255),
                     (200, 200, 64), (255, 255, 127), (0, 0, 0)]
    Rarity_Names = ["Default", "Common", "Uncommon", "Rare", "Very Rare", "Proficiency-Made", "Epic", "Legendary", "Masterwork",
                    "Supreme", "Mythic", "Super Mythic", "Godlike", "Super Godlike", "Unknown"]

    class Item:
        class Tag:
            def __init__(self, name: str, value: str):
                self.name = name
                self.value = value

            def get_all_items(self):
                return [item for item in ITEMS.values() if self.name in [tag.name for tag in item.tags]]

        def __init__(self, name, description, identifier: str, rarity: int = 0, tags: list[Tag] = [],
                     specify_img: str = None):
            self.name = name
            self.desc = description
            self.id = identifier
            self.rarity = rarity
            self.tags = tags
            self.inner_id = 0
            self.mod = 'Underia'
            self.img = specify_img if specify_img else self.id
            self.accessory_data = {}
            if TAGS['accessory'] in self.tags:
                for desc in self.desc.split('\n'):
                    desc = desc.replace(' ', '').lower().replace('.', '')
                    try:
                        if desc.endswith('kg'):
                            self.accessory_data['mass'] = float(desc.removesuffix('kg'))
                        elif desc.endswith('touchingdefense'):
                            self.accessory_data['touch_def'] = int(desc.removesuffix('touchingdefense'))
                        elif desc.endswith('physicaldefense'):
                            self.accessory_data['phys_def'] = int(desc.removesuffix('physicaldefense'))
                        elif desc.endswith('magicdefense'):
                            self.accessory_data['mag_def'] = int(desc.removesuffix('magicdefense'))
                        elif desc.endswith('%speed'):
                            self.accessory_data['speed'] = int(desc.removesuffix('%speed'))
                        elif desc.endswith('%critical'):
                            self.accessory_data['crit'] = int(desc.removesuffix('%critical'))
                        elif desc.endswith('/secregeneration'):
                            self.accessory_data['regen'] = float(desc.removesuffix('/secregeneration'))
                        elif desc.endswith('/secmanaregeneration'):
                            self.accessory_data['mana_regen'] = float(desc.removesuffix('/secmanaregeneration'))
                        elif desc.endswith('%damage'):
                            self.accessory_data['damage'] = int(desc.removesuffix('%damage'))
                        elif desc.endswith('%meleedamage'):
                            self.accessory_data['melee_damage'] = int(desc.removesuffix('%meleedamage'))
                        elif desc.endswith('%rangeddamage'):
                            self.accessory_data['ranged_damage'] = int(desc.removesuffix('%rangeddamage'))
                        elif desc.endswith('%magicdamage') or desc.endswith('%magicaldamage'):
                            self.accessory_data['magic_damage'] = int(desc.split('%magic')[0])
                        elif desc.endswith('%airresistance'):
                            self.accessory_data['air_res'] = int(desc.removesuffix('%airresistance'))
                        elif desc.endswith('%domainsize'):
                            self.accessory_data['domain_size'] = int(desc.removesuffix('%domainsize'))
                        elif desc.endswith('/secmentalityregeneration'):
                            self.accessory_data['mentality_regen'] = float(desc.removesuffix('/secmentalityregeneration'))
                        elif desc.endswith('%poisondamagereceived'):
                            self.accessory_data['poison_res'] = float(desc.removesuffix('%poisondamagereceived'))
                        elif desc[0] in ['+', '-']:
                            print(f"Unknown accessory data: {desc}")
                    except ValueError:
                        print(f"Invalid accessory data: {desc}")


        def __str__(self):
            return f"#{self.inner_id}: {self.name} - {self.desc}"

        def get_full_desc(self):
            d = self.desc
            if TAGS['major_accessory'] in self.tags:
                d = 'Can only be placed in the first slot.\n' + d
            if TAGS['wings'] in self.tags:
                d = 'Can only be placed in the second slot.\n' + d
            if TAGS['accessory'] in self.tags:
                d = 'Accessory\n' + d

            if TAGS['magic_weapon'] in self.tags:
                weapon: weapons.MagicWeapon = weapons.WEAPONS[self.id]
                d = f"{[t.value.upper() for t in self.tags if t.name.startswith('magic_element_')][0]} "\
                    f"{[t.value for t in self.tags if t.name.startswith('magic_lv_')][0]}: {weapon.spell_name}"
                d = f"{weapon.mana_cost} mana cost\n" + d
            if TAGS['arcane_weapon'] in self.tags:
                weapon = weapons.WEAPONS[self.id]
                d = f"{weapon.talent_cost} talent cost\n" + d
                if weapon.mana_cost:
                    d = f"{weapon.mana_cost} mana cost\n" + d
            if TAGS['bow'] in self.tags or TAGS['gun'] in self.tags:
                weapon = weapons.WEAPONS[self.id]
                d = f"{weapon.spd} projectile speed\n" + d
            if TAGS['weapon'] in self.tags:
                weapon = weapons.WEAPONS[self.id]
                d = f"{round(100 / (weapon.at_time + weapon.cd), 1)}% speed\n" + d
                d = f"{weapon.knock_back} knockback\n" + d
                for dmg, val in weapon.damages.items():
                    _dmg = val * game.get_game().player.calculate_damage()
                    if TAGS['magic_weapon'] in self.tags:
                        _dmg *= game.get_game().player.calculate_magic_damage()
                    elif TAGS['bow'] in self.tags or TAGS['gun'] in self.tags:
                        _dmg *= game.get_game().player.calculate_ranged_damage()
                    else:
                        _dmg *= game.get_game().player.calculate_melee_damage()
                    d = f"{int(_dmg)} {damages.NAMES[dmg]} damage\n" + d
            elif TAGS['ammo'] in self.tags:
                ammo = projectiles.AMMOS[self.id]
                d = f"{ammo.DAMAGES} piercing damage\n" + d
            d = f"{Inventory.Rarity_Names[self.rarity]}\n" + d
            d = f"Mod: {self.mod}\n" + d
            return d

    def __init__(self):
        self.items = {}

    def add_item(self, item: Item, number: int = 1):
        if item.id in self.items:
            self.items[item.id] += number
        else:
            self.items[item.id] = number
        self.sort()

    def remove_item(self, item: Item, number: int = 1):
        if item.id in self.items:
            self.items[item.id] -= number
            self.items = {k: v for k, v in self.items.items() if v > 0}
        else:
            pass

    def is_enough(self, item: Item, number: int = 1):
        if item.id in self.items:
            return self.items[item.id] >= number
        else:
            return False

    def get_all_items(self):
        return self.items.values()

    def get_item_by_name(self, name: str):
        return [item for item in self.items.values() if item.name == name][0]

    def get_item_by_id(self, item_id: int):
        return self.items[item_id]

    def get_item_by_tag(self, tag_name: str):
        return [item for item in self.items.values() if tag_name in [tag.name for tag in item.tags]]

    def get_item_by_rarity(self, rarity: int):
        return [item for item in self.items.values() if item.rarity == rarity]

    def get_item_by_rarity_name(self, rarity_name: str):
        return [item for item in self.items.values() if Inventory.Rarity_Names[item.rarity] == rarity_name]

    def get_item_by_rarity_color(self, rarity_color: tuple):
        return [item for item in self.items.values() if Inventory.Rarity_Colors[item.rarity] == rarity_color]

    def sort(self):
        self.items = {k: v for k, v in
                      sorted(self.items.items(), key=lambda item: ITEMS[item[0]].inner_id, reverse=True) if k != 'null'}


TAGS = {
    'item': Inventory.Item.Tag('item', 'item'),
    'weapon': Inventory.Item.Tag('weapon', 'weapon'),
    'magic_weapon': Inventory.Item.Tag('magic_weapon', 'magic_weapon'),
    'arcane_weapon': Inventory.Item.Tag('arcane_weapon', 'arcane_weapon'),
    'accessory': Inventory.Item.Tag('accessory', 'accessory'),
    'major_accessory': Inventory.Item.Tag('major_accessory', 'major_accessory'),
    'wings': Inventory.Item.Tag('wings', 'wings'),
    'healing_potion': Inventory.Item.Tag('healing_potion', 'healing_potion'),
    'magic_potion': Inventory.Item.Tag('magic_potion', 'magic_potion'),
    'workstation': Inventory.Item.Tag('workstation', 'workstation'),
    'light_source': Inventory.Item.Tag('light_source', 'light_source'),
    'night_vision': Inventory.Item.Tag('night_vision', 'night_vision'),
    'bow': Inventory.Item.Tag('bow', 'bow'),
    'gun': Inventory.Item.Tag('gun', 'gun'),
    'lazer_gun': Inventory.Item.Tag('lazer_gun', 'lazer_gun'),
    'knife': Inventory.Item.Tag('knife', 'knife'),
    'ammo': Inventory.Item.Tag('ammo', 'ammo'),
    'ammo_arrow': Inventory.Item.Tag('ammo_arrow', 'ammo_arrow'),
    'ammo_bullet': Inventory.Item.Tag('ammo_bullet', 'ammo_bullet'),

    'magic_element_fire': Inventory.Item.Tag('magic_element_fire', 'fire magic'),
    'magic_element_water': Inventory.Item.Tag('magic_element_water', 'water magic'),
    'magic_element_air': Inventory.Item.Tag('magic_element_air', 'air magic'),
    'magic_element_earth': Inventory.Item.Tag('magic_element_earth', 'earth magic'),
    'magic_element_light': Inventory.Item.Tag('magic_element_light', 'light magic'),
    'magic_element_dark': Inventory.Item.Tag('magic_element_dark', 'dark magic'),
    'magic_element_life': Inventory.Item.Tag('magic_element_life', 'life magic'),
    'magic_element_death': Inventory.Item.Tag('magic_element_death', 'death magic'),
    'magic_element_energy': Inventory.Item.Tag('magic_element_energy', 'energy magic'),
    'magic_element_time': Inventory.Item.Tag('magic_element_time', 'time magic'),
    'magic_element_space': Inventory.Item.Tag('magic_element_space', 'space magic'),

    'magic_lv_1': Inventory.Item.Tag('magic_lv_1', 'LV.I'),
    'magic_lv_2': Inventory.Item.Tag('magic_lv_2', 'LV.II'),
    'magic_lv_3': Inventory.Item.Tag('magic_lv_3', 'LV.III'),
    'magic_lv_4': Inventory.Item.Tag('magic_lv_4', 'LV.IV'),
    'magic_lv_5': Inventory.Item.Tag('magic_lv_5', 'LV.V'),
    'magic_lv_6': Inventory.Item.Tag('magic_lv_6', 'LV.VI'),
    'magic_lv_7': Inventory.Item.Tag('magic_lv_7', 'LV.VII'),
    'magic_lv_forbidden_curse': Inventory.Item.Tag('magic_lv_forbidden_curse', 'LV.XX'),
    'magic_lv_primal_magic': Inventory.Item.Tag('magic_lv_primal_magic', 'LV.NULLA'),
    'magic_lv_bible': Inventory.Item.Tag('magic_lv_bible', 'LV.XXV'),
}
items_dict: dict[str, Inventory.Item] = {
    'null': Inventory.Item('null', '', 'null', 0, [TAGS['item']]),

    'recipe_book': Inventory.Item('Recipe Book', 'Find related recipes', 'recipe_book', 0, [TAGS['item']]),

    'tip0': Inventory.Item('Paper tip', 'Trap a star-shaped monster, '
                                        'it\'ll help you to enhance your intelligence.',
                           'tip0', 0, [TAGS['item']]),
    'tip1': Inventory.Item('Paper tip', 'Get bloods from sanguinary creatures,\n'
                                        'and attract a dreadfully huge one.', 'tip1', 0, [TAGS['item']]),
    'tip2': Inventory.Item('Paper tip', 'Go to the hell, use scorching lava to attract their king.\n'
                                        'They contain a good to make you stronger.', 'tip2', 0, [TAGS['item']]),
    'tip3': Inventory.Item('Paper tip', 'When you\'re strong enough, a mystery rock will appear.\n'
                                        'Their smell may attract a sandstorm.', 'tip3', 0,
                           [TAGS['item']]),
    'tip4': Inventory.Item('Paper tip', 'Sandstorms have cores, use them also for combining several '
                                        'weapons to one.\nThey can be also used for summon an otherworldly being.', 'tip4', 0, [TAGS['item']]),
    'tip5': Inventory.Item('Paper tip', 'Use your strength to break a evil mark.\nUse some souls to '
                                        'make a heart...\nIt will expose another world for you.', 'tip5', 0,
                           [TAGS['item']]),
    'tip61': Inventory.Item('Paper tip', '(This tip is teared at the bottom)\nStrong flying creatures '
                                         'helps you to go to the sky.', 'tip61', 0, [TAGS['item']]),
    'tip62': Inventory.Item('Paper tip', '(This tip is teared both at the top and at the bottom)\n'
                                         'Get strongest materials from the new world.\nDefeat:\n-A twin of \'untrustworthy\''
                                         ' metal eyes\n-A \'terrified\' worm.\n-A \'unkind\' metal brain.',
                            'tip62', 0, [TAGS['item']]),
    'tip63': Inventory.Item('Paper tip', '(This tip is teared at the top)\nFrozen souls are good materials.',
                            'tip63', 0, [TAGS['item']]),
    'tip71': Inventory.Item('Paper tip', 'Use your honest, summon a existence who overwatch the river of time.\n'
                                         'Use three sou...(The rest of the tip is missing)',
                            'tip71', 0, [TAGS['item']]),
    'tip72': Inventory.Item('Paper tip', 'Use your kindness, summon a group of existences.\n'
                                         '...ls and the the strongest weapon you\'ve made to en...(The beginning and the'
                                         'rest of the tip are missing)\n',
                            'tip72', 0, [TAGS['item']]),
    'tip73': Inventory.Item('Paper tip', 'Use your courage, summon a existence who eat people for food.\n'
                                         '...hance it to a unbelievable weapon.(The beginning of the tip is missing)',
                            'tip73', 0, [TAGS['item']]),
    'tip8': Inventory.Item('Paper tip', 'Use photosynthesis, create photon, plant plants, open a new age.',
                            'tip8', 0, [TAGS['item']]),
    'tip9': Inventory.Item('Paper tip', 'Use light to summon a dangerous devil of joker.\n',
                           'tip9', 0, [TAGS['item']]),

    'wood': Inventory.Item('Wood', '', 'wood', 0, [TAGS['item']]),
    'leaf': Inventory.Item('Leaf', '', 'leaf', 0, [TAGS['item']]),
    'copper': Inventory.Item('Copper', '', 'copper', 0, [TAGS['item']]),
    'copper_ingot': Inventory.Item('Copper Ingot', '', 'copper_ingot', 0, [TAGS['item']]),
    'iron': Inventory.Item('Iron', '', 'iron', 0, [TAGS['item']]),
    'iron_ingot': Inventory.Item('Iron Ingot', '', 'iron_ingot', 0, [TAGS['item']]),
    'steel': Inventory.Item('Steel', '', 'steel', 0, [TAGS['item']]),
    'steel_ingot': Inventory.Item('Steel Ingot', '', 'steel_ingot', 0, [TAGS['item']]),
    'cell_organization': Inventory.Item('Cell Organization', '', 'cell_organization', 1, [TAGS['item']]),
    'platinum': Inventory.Item('Platinum', '', 'platinum', 1, [TAGS['item']]),
    'platinum_ingot': Inventory.Item('Platinum Ingot', '', 'platinum_ingot', 1, [TAGS['item']]),
    'magic_stone': Inventory.Item('Magic Stone', '', 'magic_stone', 1, [TAGS['item']]),
    'blood_ingot': Inventory.Item('Blood Ingot', '', 'blood_ingot', 2, [TAGS['item']]),
    'firite_ingot': Inventory.Item('Firite Ingot', '', 'firite_ingot', 2, [TAGS['item']]),
    'mysterious_substance': Inventory.Item('Mysterious Substance', '', 'mysterious_substance', 2, [TAGS['item']]),
    'mysterious_ingot': Inventory.Item('Mysterious Ingot', '', 'mysterious_ingot', 2, [TAGS['item']]),
    'storm_core': Inventory.Item('Storm Core', '', 'storm_core', 2, [TAGS['item']]),
    'soul': Inventory.Item('Soul', 'Something left after death.', 'soul', 4, [TAGS['item']]),
    'evil_ingot': Inventory.Item('Evil Ingot', 'Endless evil.', 'evil_ingot', 5, [TAGS['item']]),
    'soul_of_flying': Inventory.Item('Soul of Flying', 'Soul of strong flying creatures.', 'soul_of_flying', 5,
                                     [TAGS['item']]),
    'soul_of_coldness': Inventory.Item('Soul of Coldness', 'Soul of strong chilling creatures.', 'soul_of_coldness', 5,
                                       [TAGS['item']]),
    'soul_of_growth': Inventory.Item('Soul of Growth', 'Soul of strong growing creatures.', 'soul_of_growth', 7, [TAGS['item']]),
    'palladium': Inventory.Item('Palladium', '', 'palladium', 5, [TAGS['item']]),
    'mithrill': Inventory.Item('Mithrill', '', 'mithrill', 5, [TAGS['item']]),
    'titanium': Inventory.Item('Titanium', '', 'titanium', 5, [TAGS['item']]),
    'palladium_ingot': Inventory.Item('Palladium Ingot', '', 'palladium_ingot', 5, [TAGS['item']]),
    'mithrill_ingot': Inventory.Item('Mithrill Ingot', '', 'mithrill_ingot', 5, [TAGS['item']]),
    'titanium_ingot': Inventory.Item('Titanium Ingot', '', 'titanium_ingot', 5, [TAGS['item']]),
    'saint_steel_ingot': Inventory.Item('Saint Steel Ingot', '', 'saint_steel_ingot', 6, [TAGS['item']]),
    'daedalus_ingot': Inventory.Item('Daedalus\' Ingot', '', 'daedalus_ingot', 6, [TAGS['item']]),
    'dark_ingot': Inventory.Item('Dark Ingot', '', 'dark_ingot', 6, [TAGS['item']]),
    'soul_of_integrity': Inventory.Item('Soul of Integrity', 'Power of the honest being.', 'soul_of_integrity', 6,
                                        [TAGS['item']]),
    'soul_of_bravery': Inventory.Item('Soul of Bravery', 'Power of fearless.', 'soul_of_bravery', 6, [TAGS['item']]),
    'soul_of_kindness': Inventory.Item('Soul of Kindness', 'Power of mercy.', 'soul_of_kindness', 6, [TAGS['item']]),
    'mystery_core': Inventory.Item('Mystery Core', 'Knowledge\n+1 max talent\n+5 talent', 'mystery_core', 7,
                                   [TAGS['item']]),
    'soul_of_perseverance': Inventory.Item('Soul of Perseverance', 'Power of hope.', 'soul_of_perseverance', 6,
                                           [TAGS['item']]),
    'soul_of_patience': Inventory.Item('Soul of Patience', 'Power of endurance.', 'soul_of_patience', 6,
                                       [TAGS['item']]),
    'soul_of_justice': Inventory.Item('Soul of Justice', 'Power of fairness.', 'soul_of_justice', 6, [TAGS['item']]),
    'photon': Inventory.Item('Photon', 'Light energy', 'photon', 7, [TAGS['item']]),
    'chlorophyte_ingot': Inventory.Item('Chlorophyte Ingot', '', 'chlorophyte_ingot', 7, [TAGS['item']]),

    'chaos_ingot': Inventory.Item('Chaos Ingot', 'Power of disarray.', 'chaos_ingot', 7, [TAGS['item']]),
    'origin': Inventory.Item('Origin', 'Seed of laws.', 'origin', 9, [TAGS['item']]),
    'willpower_shard': Inventory.Item('Willpower Shard', 'Essence of continuing.', 'willpower_shard', 9,
                                       [TAGS['item']]),
    'soul_of_determination': Inventory.Item('Soul of Determination', 'Willpower of non-regretted chooses.\n'
                                                                     '20% chance to reach the limit of human souls.\n'
                                                                     'Change talent to mentality.\n'
                                                                     'When mana < 100, use mentality. instead.'
                                            , 'soul_of_determination', 9,
                                            [TAGS['item']]),
    'chaos_heart': Inventory.Item('Chaos Heart', 'The inner\'s heart.\nProbably have to destroy it.', 'chaos_heart', 9, [TAGS['item']]),
    'wierd_essence': Inventory.Item('Wierd Essence', 'Something strange.', 'wierd_essence', 9, [TAGS['item']]),
    'time_essence': Inventory.Item('Time Essence', 'Minutes and hours.', 'time_essence', 9, [TAGS['item']]),

    'torch': Inventory.Item('Torch', 'Ignite the darkness.', 'torch', 0,
                            [TAGS['item'], TAGS['accessory'], TAGS['light_source']]),
    'night_visioner': Inventory.Item('Night Visioner', 'See in the dark.', 'night_visioner', 0,
                                     [TAGS['item'], TAGS['accessory'], TAGS['light_source'], TAGS['night_vision']]),

    'wooden_hammer': Inventory.Item('Wooden Hammer', '', 'wooden_hammer', 0, [TAGS['item'], TAGS['workstation']]),
    'furnace': Inventory.Item('Furnace', '', 'furnace', 0, [TAGS['item'], TAGS['workstation']]),
    'anvil': Inventory.Item('Anvil', '', 'anvil', 0, [TAGS['item'], TAGS['workstation']]),
    'mithrill_anvil': Inventory.Item('Mithrill Anvil', '', 'mithrill_anvil', 4, [TAGS['item'], TAGS['workstation']]),
    'chlorophyll': Inventory.Item('Chlorophyll', 'Carry out photosynthesis.', 'chlorophyll', 7,
                                  [TAGS['item'], TAGS['workstation']]),
    'time_fountain': Inventory.Item('Time Fountain', 'Origin of time.', 'time_fountain', 9, [TAGS['item'], TAGS['workstation']]),

    'wooden_sword': Inventory.Item('Wooden Sword', '', 'wooden_sword', 0, [TAGS['item'], TAGS['weapon']]),
    'copper_sword': Inventory.Item('Copper Sword', '', 'copper_sword', 0, [TAGS['item'], TAGS['weapon']]),
    'iron_sword': Inventory.Item('Iron Sword', '', 'iron_sword', 0, [TAGS['item'], TAGS['weapon']]),
    'iron_blade': Inventory.Item('Iron Blade', '', 'iron_blade', 0, [TAGS['item'], TAGS['weapon']]),
    'steel_sword': Inventory.Item('Steel Sword', '', 'steel_sword', 0, [TAGS['item'], TAGS['weapon']]),
    'platinum_sword': Inventory.Item('Platinum Sword', '', 'platinum_sword', 1, [TAGS['item'], TAGS['weapon']]),
    'platinum_blade': Inventory.Item('Platinum Blade', '', 'platinum_blade', 1, [TAGS['item'], TAGS['weapon']]),
    'life_wooden_sword': Inventory.Item('Life Wooden Sword', '', 'life_wooden_sword', 2, [TAGS['item'], TAGS['weapon']]),
    'magic_sword': Inventory.Item('Magic Sword', '', 'magic_sword', 2, [TAGS['item'], TAGS['weapon']]),
    'magic_blade': Inventory.Item('Magic Blade', '', 'magic_blade', 2, [TAGS['item'], TAGS['weapon']]),
    'bloody_sword': Inventory.Item('Bloody Sword', 'When sweeping, press Q to sprint.', 'bloody_sword', 2,
                                   [TAGS['item'], TAGS['weapon']]),
    'volcano': Inventory.Item('Volcano', 'Gives target to fire.', 'volcano', 2, [TAGS['item'], TAGS['weapon']]),
    'sand_sword': Inventory.Item('Sand Sword', 'When sweeping, press Q to sprint.', 'sand_sword', 2,
                                 [TAGS['item'], TAGS['weapon']]),
    'nights_edge': Inventory.Item('Night\'s Edge', 'The sunset has gone, it now night...', 'nights_edge', 4,
                                  [TAGS['item'], TAGS['weapon']]),
    'storm_swift_sword': Inventory.Item('Storm Swift Sword', 'Press Q to sprint.\n0 mana cost', 'storm_swift_sword', 4,
                                          [TAGS['item'], TAGS['weapon']]),
    'spiritual_stabber': Inventory.Item('Spiritual Stabber', '\n\'Destroy the mark to enhance\'', 'spiritual_stabber',
                                        4, [TAGS['item'], TAGS['weapon']]),
    'palladium_sword': Inventory.Item('Palladium Sword', '', 'palladium_sword', 5, [TAGS['item'], TAGS['weapon']]),
    'mithrill_sword': Inventory.Item('Mithrill Sword', '', 'mithrill_sword', 5, [TAGS['item'], TAGS['weapon']]),
    'titanium_sword': Inventory.Item('Titanium Sword', '', 'titanium_sword', 5, [TAGS['item'], TAGS['weapon']]),
    'balanced_stabber': Inventory.Item('Balanced Stabber',
                                       'The power of the evil and the hallow are balanced.\n\n\'Make it under the hallow to enhance\'',
                                       'balanced_stabber', 5, [TAGS['item'], TAGS['weapon']]),
    'excalibur': Inventory.Item('Excalibur', 'The legendary sword of hallow.', 'excalibur', 6,
                                [TAGS['item'], TAGS['weapon']]),
    'true_excalibur': Inventory.Item('True Excalibur', 'Inviolable hallow.', 'true_excalibur', 7,
                                     [TAGS['item'], TAGS['weapon']]),
    'remote_sword': Inventory.Item('Remote Sword', '', 'remote_sword', 6,
                                    [TAGS['item'], TAGS['weapon']]),
    'true_nights_edge': Inventory.Item('True Night\'s Edge', 'Inviolable dark.', 'true_nights_edge', 7,
                                       [TAGS['item'], TAGS['weapon']]),
    'muramasa': Inventory.Item('Muramasa', 'Ghost\'s blade.', 'muramasa', 7, [TAGS['item'], TAGS['weapon']]),
    'perseverance_sword': Inventory.Item('Perseverance Sword', 'Ignore the distance.', 'perseverance_sword', 6,
                                         [TAGS['item'], TAGS['weapon']]),
    'black_hole_sword': Inventory.Item('The Black Hole Sword', 'Attracts enemies.', 'black_hole_sword', 6,
                                       [TAGS['item'], TAGS['weapon']]),
    'life_devourer': Inventory.Item('Life Devourer', 'Cuts lifeless lines.', 'life_devourer', 7,
                                    [TAGS['item'], TAGS['weapon']]),
    'jevil_knife': Inventory.Item('Jevil Knife', 'Full in chaos', 'jevil_knife', 7,
                                   [TAGS['item'], TAGS['weapon']]),
    'the_blade': Inventory.Item('The Blade', 'The mighty of this blade is not necessary to say.',
                                'the_blade', 8, [TAGS['item'], TAGS['weapon']]),
    'demon_blade__muramasa': Inventory.Item('Demon Blade: Muramasa', 'The terror of this blade is not necessary to say.',
                                             'demon_blade__muramasa', 8, [TAGS['item'], TAGS['weapon']]),
    'uncanny_valley': Inventory.Item('Uncanny Valley', 'Closer, scarier.', 'uncanny_valley', 9,
                                      [TAGS['item'], TAGS['weapon']]),
    'hour_hand': Inventory.Item('Hour Hand', 'A spin, a time.', 'hour_hand', 9,
                                 [TAGS['item'], TAGS['weapon']]),

    'spikeflower': Inventory.Item('Spikeflower', '', 'spikeflower', 0,
                                  [TAGS['item'], TAGS['weapon']]),
    'spear': Inventory.Item('Spear', '', 'spear', 0, [TAGS['item'], TAGS['weapon']]),
    'platinum_spear': Inventory.Item('Platinum Spear', '', 'platinum_spear', 1, [TAGS['item'], TAGS['weapon']]),
    'blood_pike': Inventory.Item('Blood Pike', '', 'blood_pike', 2, [TAGS['item'], TAGS['weapon']]),
    'firite_spear': Inventory.Item('Firite Spear', '', 'firite_spear', 2, [TAGS['item'], TAGS['weapon']]),
    'nights_pike': Inventory.Item('Night\'s Pike', 'The sunset has gone, it now night...', 'nights_pike', 4,
                                  [TAGS['item'], TAGS['weapon']]),
    'energy_spear': Inventory.Item('Energy Spear', 'Contained unparalleled energy.', 'energy_spear', 6,
                                   [TAGS['item'], TAGS['weapon']]),
    'millennium_persists': Inventory.Item('Millennium Persists', 'Thousands of years non-stopping.',
                                          'millennium_persists', 7, [TAGS['item'], TAGS['weapon']]),
    'metal_hand': Inventory.Item('Metal Hand', 'A stab with time passing.', 'energy_spear', 9,
                                  [TAGS['item'], TAGS['weapon']]),

    'arrow_thrower': Inventory.Item('Arrow Thrower', '', 'arrow_thrower', 0,
                                    [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'bow': Inventory.Item('Bow', '', 'bow', 0, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'copper_bow': Inventory.Item('Copper Bow', '', 'copper_bow', 0, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'iron_bow': Inventory.Item('Iron Bow', '', 'iron_bow', 0, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'steel_bow': Inventory.Item('Steel Bow', '', 'steel_bow', 0, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'platinum_bow': Inventory.Item('Platinum Bow', '', 'platinum_bow', 1, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'bloody_bow': Inventory.Item('Bloody Bow', '', 'bloody_bow', 2, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'forests_bow': Inventory.Item('Forest\'s Bow', '', 'forests_bow', 2, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'recurve_bow': Inventory.Item('Recurve Bow', '', 'recurve_bow', 3, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'spiritual_piercer': Inventory.Item('Spiritual Piercer', '\n\'Destroy the mark to enhance\'', 'spiritual_piercer',
                                        4, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'discord_storm': Inventory.Item('Discord Storm',
                                    'Evil corrupted, all in chaos.\n\n\'Find that old god to enhance\'',
                                    'discord_storm', 5, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'daedalus_stormbow': Inventory.Item('Daedalus\' Stormbow', '', 'daedalus_stormbow', 6,
                                        [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'forward_bow': Inventory.Item('Forward Bow', '', 'forward_bow', 6, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'true_daedalus_stormbow': Inventory.Item('True Daedalus\' Stormbow', '', 'true_daedalus_stormbow', 7,
                                             [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'bow_of_sanction': Inventory.Item('Bow of Sanction', '', 'bow_of_sanction', 7,
                                      [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'lazer_rain': Inventory.Item('Lazer Rain', '', 'lazer_rain', 8, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'accelerationism': Inventory.Item('Accelerationism', 'Increase of speed.', 'accelerationism', 9,
                                       [TAGS['item'], TAGS['weapon'], TAGS['bow']]),

    'pistol': Inventory.Item('pistol', '', 'pistol', 0, [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'rifle': Inventory.Item('rifle', '', 'rifle', 0, [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'submachine_gun': Inventory.Item('Submachine Gun', '', 'submachine_gun', 2,
                                     [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'magma_assaulter': Inventory.Item('Magma Assaulter', 'When shooting, press Q to sprint back.', 'magma_assaulter', 2,
                                      [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'shadow': Inventory.Item('shadow', 'When there\'s light, there\'s dark.', 'shadow', 4,
                             [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'palladium_gun': Inventory.Item('Palladium Gun', '', 'palladium_gun', 5,
                                    [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'mithrill_gun': Inventory.Item('Mithrill Gun', '', 'mithrill_gun', 5, [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'titanium_gun': Inventory.Item('Titanium Gun', '', 'titanium_gun', 5, [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'true_shadow': Inventory.Item('True Shadow', 'Not the others, \'Pong! Nobody left.\'', 'true_shadow', 7,
                                  [TAGS['item'], TAGS['weapon'], TAGS['gun']]),

    'lazer_gun': Inventory.Item('Lazer Gun', '', 'lazer_gun', 7,
                                [TAGS['item'], TAGS['weapon'], TAGS['gun'], TAGS['lazer_gun']]),
    'lazer_sniper': Inventory.Item('Lazer Sniper', '', 'lazer_sniper', 7,
                                   [TAGS['item'], TAGS['weapon'], TAGS['gun'], TAGS['lazer_gun']]),

    'copper_knife': Inventory.Item('Copper Knife', '', 'copper_knife', 0,
                                   [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'dagger': Inventory.Item('Dagger', '', 'dagger', 1, [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'platinum_doubleknife': Inventory.Item('Platinum Double Knife', '', 'platinum_doubleknife', 2,
                                            [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'twilight_shortsword': Inventory.Item('Twilight Shortsword', '', 'twilight_shortsword', 2,
                                           [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'bloody_shortsword': Inventory.Item('Bloody Shortsword', '', 'bloody_shortsword', 3,
                                          [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'dawn_shortsword': Inventory.Item('Dawn Shortsword', '', 'dawn_shortsword', 3,
                                       [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'night_twinsword': Inventory.Item('Night Twinsword', 'Before night, after night.', 'night_twinsword', 4,
                                       [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'storm_stabber': Inventory.Item('Storm Stabber', '', 'storm_stabber', 4,
                                     [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'spiritual_knife': Inventory.Item('Spiritual Knife', '\n\'Destroy the mark to enhance\'', 'spiritual_knife', 4,
                                       [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'daedalus_knife': Inventory.Item('Daedalus Knife', '', 'daedalus_knife', 4,
                                      [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'daedalus_twinknife': Inventory.Item('Daedalus Twinknife', '', 'daedalus_twinknife', 5,
                                         [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'true_twinblade': Inventory.Item('True Twinblade', '', 'true_twinblade', 6,
                                       [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'chaos_chaos': Inventory.Item('Chaos Chaos', '', 'chaos_chaos', 8,
                                  [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'time_flies': Inventory.Item('Time Flies', 'Hours and hours are flying by.', 'time_flies', 9,
                                  [TAGS['item'], TAGS['weapon'], TAGS['knife']]),

    'arrow': Inventory.Item('Arrow', '', 'arrow', 0, [TAGS['item'], TAGS['ammo'], TAGS['ammo_arrow']]),
    'coniferous_leaf': Inventory.Item('Coniferous Leaf', '', 'coniferous_leaf', 0,
                                      [TAGS['item'], TAGS['ammo'], TAGS['ammo_arrow']]),
    'magic_arrow': Inventory.Item('Magic Arrow', '', 'magic_arrow', 1,
                                  [TAGS['item'], TAGS['ammo'], TAGS['ammo_arrow']]),
    'blood_arrow': Inventory.Item('Blood Arrow', '', 'blood_arrow', 2,
                                  [TAGS['item'], TAGS['ammo'], TAGS['ammo_arrow']]),
    'bullet': Inventory.Item('Bullet', '', 'bullet', 0, [TAGS['item'], TAGS['ammo'], TAGS['ammo_bullet']]),
    'platinum_bullet': Inventory.Item('Platinum Bullet', '', 'platinum_bullet', 1,
                                      [TAGS['item'], TAGS['ammo'], TAGS['ammo_bullet']]),
    'plasma': Inventory.Item('Plasma', '', 'plasma', 2, [TAGS['item'], TAGS['ammo'], TAGS['ammo_bullet']]),
    'rock_bullet': Inventory.Item('Rock Bullet', '', 'rock_bullet', 2,
                                  [TAGS['item'], TAGS['ammo'], TAGS['ammo_bullet']]),
    'shadow_bullet': Inventory.Item('Shadow Bullet', '', 'shadow_bullet', 3,
                                    [TAGS['item'], TAGS['ammo'], TAGS['ammo_bullet']]),
    'quick_arrow': Inventory.Item('Quick Arrow', '', 'quick_arrow', 5,
                                  [TAGS['item'], TAGS['ammo'], TAGS['ammo_arrow']]),
    'quick_bullet': Inventory.Item('Quick Bullet', '', 'quick_bullet', 5,
                                   [TAGS['item'], TAGS['ammo'], TAGS['ammo_bullet']]),
    'chloro_arrow': Inventory.Item('Chloro Arrow', 'Always face to the target.', 'chloro_arrow', 7,
                                   [TAGS['item'], TAGS['ammo'], TAGS['ammo_arrow']]),
    'space_jumper': Inventory.Item('Space Jumper', '', 'space_jumper', 7,
                                    [TAGS['item'], TAGS['ammo'], TAGS['ammo_bullet']]),

    'glowing_splint': Inventory.Item('Glowing Splint', 'Shoots glows.', 'glowing_splint', 0,
                                     [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                      TAGS['magic_element_fire'], TAGS['magic_lv_1']]),
    'copper_wand': Inventory.Item('Copper Wand', '', 'copper_wand', 0,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_air'],
                                   TAGS['magic_lv_1']]),
    'iron_wand': Inventory.Item('Iron Wand', '', 'iron_wand', 0,
                                [TAGS['item'],  TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_air'],
                                 TAGS['magic_lv_1']]),
    'cactus_wand': Inventory.Item('Cactus Wand', '', 'cactus_wand', 1,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                   TAGS['magic_lv_1']]),
    'watcher_wand': Inventory.Item('Watcher Wand', '', 'watcher_wand', 1,
                                   [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_light'],
                                    TAGS['magic_lv_1']]),
    'platinum_wand': Inventory.Item('Platinum Wand', '', 'platinum_wand', 1,
                                    [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                     TAGS['magic_element_energy'], TAGS['magic_lv_1']]),
    'life_wooden_wand': Inventory.Item('Life-Wooden Wand', '', 'life_wooden_wand', 2,
                                        [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_earth'],
                                         TAGS['magic_lv_1']]),
    'burning_book': Inventory.Item('Burning Book', 'Burns enemies.', 'burning_book', 2,
                                   [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_fire'],
                                     TAGS['magic_lv_2']]),
    'talent_book': Inventory.Item('Talent Book', '', 'talent_book', 2,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_light'],
                                   TAGS['magic_lv_2']]),
    'blood_wand': Inventory.Item('Blood Wand', '', 'blood_wand', 2,
                                 [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                   TAGS['magic_lv_2']]),
    'hematology': Inventory.Item('Hematology', 'Recovers 30 HP.', 'hematology', 3,
                                 [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                   TAGS['magic_lv_3']]),
    'fire_magic_sword': Inventory.Item('Fire Magic Sword', '', 'fire_magic_sword', 3,
                                       [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_fire'],
                                        TAGS['magic_lv_3']]),
    'rock_wand': Inventory.Item('Rock Wand', '', 'rock_wand', 3,
                                [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_earth'],
                                 TAGS['magic_lv_3']]),
    'tornado': Inventory.Item('Tornado', '', 'tornado', 3,
                               [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_air'],
                                TAGS['magic_lv_3']]),
    'midnights_wand': Inventory.Item('Midnight\'s Wand', 'All darkness...', 'midnights_wand', 4,
                                     [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_dark'],
                                      TAGS['magic_lv_4']]),
    'spiritual_destroyer': Inventory.Item('Spiritual Destroyer', '\n\'Destroy the mark to enhance\'',
                                          'spiritual_destroyer', 4,
                                          [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                           TAGS['magic_element_energy'], TAGS['magic_lv_4']]),
    'evil_book': Inventory.Item('Evil Book', 'Full of corruption\n\n\'Change to enhance\'', 'evil_book', 5,
                                [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_death'],
                                  TAGS['magic_lv_4']]),
    'blood_sacrifice': Inventory.Item('Blood Sacrifice', '24 HP Cost.',
                                       'blood_sacrifice', 5,
                                       [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_death'],
                                        TAGS['magic_lv_5']]),
    'blade_wand': Inventory.Item('Blade Wand', '', 'blade_wand', 5,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_air'],
                                   TAGS['magic_lv_5']]),
    'curse_book': Inventory.Item('Curse Book', 'Curse...', 'curse_book', 6,
                                 [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_dark'],
                                   TAGS['magic_lv_4']]),
    'shield_wand': Inventory.Item('Shield Wand', '+1145114 defense\n-100% speed', 'shield_wand', 6,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_water'],
                                    TAGS['magic_lv_4']]),
    'gravity_wand': Inventory.Item('Gravity Wand', 'Simulates gravity.', 'gravity_wand', 6,
                                   [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_earth'],
                                     TAGS['magic_lv_3']]),
    'double_watcher_wand': Inventory.Item('Double Watcher Wand', '', 'double_watcher_wand', 6,
                                           [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                            TAGS['magic_element_light'], TAGS['magic_element_fire'], TAGS['magic_lv_4']]),
    'forbidden_curse__spirit': Inventory.Item('Forbidden Curse: Spirit', '', 'forbidden_curse__spirit', 7,
                                              [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                               TAGS['arcane_weapon'], TAGS['magic_element_energy'],
                                               TAGS['magic_lv_forbidden_curse']]),
    'forbidden_curse__evil': Inventory.Item('Forbidden Curse: Evil', '', 'forbidden_curse__evil', 7,
                                            [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                             TAGS['arcane_weapon'], TAGS['magic_element_death'],
                                              TAGS['magic_lv_forbidden_curse']]),
    'forbidden_curse__time': Inventory.Item('Forbidden Curse: Time', 'Adjust the rate of time.',
                                            'forbidden_curse__time', 7,
                                            [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                             TAGS['arcane_weapon'], TAGS['magic_element_time'],
                                              TAGS['magic_lv_forbidden_curse']]),
    'prism': Inventory.Item('Prism', 'Releases light beams.', 'prism', 6,
                            [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_light'],
                             TAGS['magic_lv_4']]),
    'prism_wand': Inventory.Item('Prism Wand', 'Releases light beams.', 'prism_wand', 7,
                                 [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                   TAGS['magic_element_light'], TAGS['magic_lv_5']]),
    'light_purify': Inventory.Item('Light Purify', '', 'light_purify', 7,
                                    [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_light'],
                                     TAGS['magic_lv_5']]),
    'astigmatism': Inventory.Item('Astigmatism', 'Releases light beams.', 'astigmatism', 7,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_light'],
                                    TAGS['magic_lv_6']]),
    'life_wand': Inventory.Item('Life Wand', 'Heal you back to life.', 'life_wand', 7,
                                [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                 TAGS['magic_lv_6']]),
    'chaos_teleporter': Inventory.Item('Chaos Teleporter', 'Teleport within 1000 ps.', 'chaos_teleporter', 8,
                                        [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_space'],
                                         TAGS['magic_lv_3']]),
    'chaos_killer': Inventory.Item('Chaos Killer', 'Kills enemies.', 'chaos_killer', 8,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_space'],
                                   TAGS['magic_lv_4']]),
    'skyfire__meteor': Inventory.Item('Skyfire: Meteor', '', 'skyfire__meteor', 8,
                                       [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_fire'],
                                        TAGS['magic_lv_7']]),
    'azure_guard': Inventory.Item('Azure Guard', 'Adds a 100HP shield', 'azure_guard', 8,
                                   [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_water'],
                                    TAGS['magic_lv_7']]),
    'storm': Inventory.Item('Storm', '', 'storm', 8,
                            [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_air'],
                             TAGS['magic_lv_7']]),
    'earth_wall': Inventory.Item('Earth Wall', '', 'earth_wall', 8,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_earth'],
                                   TAGS['magic_lv_7']]),
    'lifebringer': Inventory.Item('Lifebringer', 'Heal 120HP/sec.', 'lifebringer', 8,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                   TAGS['magic_lv_7']]),
    'target_dummy': Inventory.Item('Target Dummy', '', 'target_dummy', 8,
                                    [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                     TAGS['magic_lv_7']]),
    'judgement_light': Inventory.Item('Judgement Light', '', 'judgement_light', 8,
                                       [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_light'],
                                        TAGS['magic_lv_7']]),
    'dark_restrict': Inventory.Item('Dark Restrict', '', 'dark_restrict', 8,
                                     [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_dark'],
                                      TAGS['magic_lv_7']]),
    'forbidden_curse__fire': Inventory.Item('Forbidden Curse: Fire', '', 'forbidden_curse__fire', 8,
                                             [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                              TAGS['arcane_weapon'], TAGS['magic_element_fire'],
                                               TAGS['magic_lv_forbidden_curse']]),
    'death_note': Inventory.Item('Death Note', 'Write down it, then erase it.', 'death_note', 8,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_death'],
                                   TAGS['magic_lv_forbidden_curse']]),
    'stop': Inventory.Item('Stop', '', 'stop', 8,
                            [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_time'],
                             TAGS['magic_lv_5']]),

    'lights_bible': Inventory.Item('Light\'s Bible', 'Bright makes light', 'lights_bible', 7,
                                 [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                  TAGS['magic_element_light'], TAGS['magic_lv_bible'], TAGS['workstation']]),
    'energy_bible': Inventory.Item('Energy\'s Bible', 'Energy makes light', 'energy_bible', 7,
                                 [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                  TAGS['magic_element_energy'], TAGS['magic_lv_bible'], TAGS['workstation']]),

    'primal__winds_wand': Inventory.Item('Primal: Wind\'s Wand', '', 'primal__winds_wand', 8,
                                        [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_air'],
                                         TAGS['magic_lv_primal_magic']]),
    '_circulates_domain': Inventory.Item('Circulates Domain', '', '_circulates_domain', 8,
                                        [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_air'],
                                         TAGS['magic_lv_primal_magic']]),
    '_wd_circulate_clockwise': Inventory.Item('Circulate Clockwise', '', '_wd_circulate_clockwise', 8,
                                               [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_air'],
                                                TAGS['magic_lv_primal_magic']]),
    '_wd_circulate_anticlockwise': Inventory.Item('Circulate Anticlockwise', '', '_wd_circulate_anticlockwise', 8,
                                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_air'],
                                                   TAGS['magic_lv_primal_magic']]),
    '_wd_circulate_attract': Inventory.Item('Circulate Attract', '', '_wd_circulate_attract', 8,
                                             [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_air'],
                                              TAGS['magic_lv_primal_magic']]),
    '_wd_circulate_repel': Inventory.Item('Circulate Repel', '', '_wd_circulate_repel', 8,
                                           [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_air'],
                                            TAGS['magic_lv_primal_magic']]),
    '_wd_strong_wind': Inventory.Item('Strong Wind', '', '_wd_strong_wind', 8,
                                       [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_air'],
                                        TAGS['magic_lv_primal_magic']]),
    '_wd_extinct': Inventory.Item('Extinct', '', '_wd_extinct', 8,
                                   [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_air'],
                                    TAGS['magic_lv_primal_magic']]),

    'primal__life_wand': Inventory.Item('Primal: Life\'s Wand', '', 'primal__life_wand', 8,
                                        [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                         TAGS['magic_lv_primal_magic']]),
    '_life_domain': Inventory.Item('Life Domain', '', '_life_domain', 8,
                                    [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                     TAGS['magic_lv_primal_magic']]),
    '_ld_summon_tree': Inventory.Item('Summon: Tree', '', '_ld_summon_tree', 8,
                                      [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                       TAGS['magic_lv_primal_magic']], specify_img='_ld_summon'),
    '_ld_summon_cactus': Inventory.Item('Summon: Cactus', '', '_ld_summon_cactus', 8,
                                        [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                         TAGS['magic_lv_primal_magic']], specify_img='_ld_summon'),
    '_ld_summon_coniferous_tree': Inventory.Item('Summon: Coniferous Tree', '', '_ld_summon_coniferous_tree', 8,
                                                   [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                                    TAGS['magic_lv_primal_magic']], specify_img='_ld_summon'),
    '_ld_summon_huge_tree': Inventory.Item('Summon: Huge Tree', '', '_ld_summon_huge_tree', 8,
                                             [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                              TAGS['magic_lv_primal_magic']], specify_img='_ld_summon'),
    '_ld_summon_tree_monster': Inventory.Item('Summon: Tree Monster', '', '_ld_summon_tree_monster', 8,
                                               [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                                TAGS['magic_lv_primal_magic']], specify_img='_ld_summon'),
    '_ld_summon_bloodflower': Inventory.Item('Summon: Bloodflower', '', '_ld_summon_bloodflower', 8,
                                              [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                               TAGS['magic_lv_primal_magic']], specify_img='_ld_summon'),
    '_ld_summon_soulflower': Inventory.Item('Summon: Soulflower', '', '_ld_summon_soulflower', 8,
                                              [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                               TAGS['magic_lv_primal_magic']], specify_img='_ld_summon'),
    '_ld_heal': Inventory.Item('Heal', '', '_ld_heal', 8,
                               [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                TAGS['magic_lv_primal_magic']]),

    'natural_necklace': Inventory.Item('Natural Necklace', '0.2kg\n+4/sec mana regeneration', 'natural_necklace', 0,
                                       [TAGS['item'], TAGS['accessory']]),
    'copper_traveller_boots': Inventory.Item('Copper Traveller Boots', '30kg\n+60% speed\n+3 touching defense', 'copper_traveller_boots', 1,
                                              [TAGS['item'], TAGS['accessory']]),
    'thiefs_charm': Inventory.Item('Thief\'s Charm', '-60kg\n+300% ranged damage\n-50% damage\n+50% speed\n+40% critical', 'thiefs_charm', 1,
                                    [TAGS['item'], TAGS['accessory']]),
    'metal_traveller_boots': Inventory.Item('Metal Traveller Boots', '40kg\n+90% speed\n+5 touching defense',
                                             'metal_traveller_boots', 1, [TAGS['item'], TAGS['accessory']]),
    'shield': Inventory.Item('Small Shield', '8kg\n+12 touching defense', 'shield', 1,
                             [TAGS['item'], TAGS['accessory']]),
    'tower_shield': Inventory.Item('Tower Shield', '50kg\n+32 touching defense', 'tower_shield', 1,
                                   [TAGS['item'], TAGS['accessory']]),
    'soul_bottle': Inventory.Item('Soul Bottle', '1kg\n+0.5/sec regeneration', 'soul_bottle', 1,
                                  [TAGS['item'], TAGS['accessory']]),
    'dangerous_necklace': Inventory.Item('Dangerous Necklace', '0.2kg\n+12% damage', 'dangerous_necklace', 1,
                                         [TAGS['item'], TAGS['accessory']]),
    'terrified_necklace': Inventory.Item('Terrified Necklace', '0.2kg\nWhen hp < 60%:\n+40% speed\n-0.5/sec regeneration',
                                         'terrified_necklace', 1, [TAGS['item'], TAGS['accessory']]),
    'magic_anklet': Inventory.Item('Magic Anklet', '25kg\n+4/sec mana regeneration\n+40% speed',
                                   'magic_anklet', 1, [TAGS['item'], TAGS['accessory']]),
    'purple_ring': Inventory.Item('Purple Ring', '+50% melee damage\n-20% damage\n+6% critical', 'purple_ring', 1,
                                   [TAGS['item'], TAGS['accessory']]),
    'cyan_ring': Inventory.Item('Cyan Ring', '+50% ranged damage\n-20% damage\n+12% critical', 'cyan_ring', 1,
                                [TAGS['item'], TAGS['accessory']]),
    'yellow_ring': Inventory.Item('Yellow Ring', '+50% magic damage\n-20% damage\n+6% critical', 'yellow_ring', 1,
                                   [TAGS['item'], TAGS['accessory']]),
    'gorgeous_ring': Inventory.Item('Gorgeous Ring', '+80% damage\n+22% critical',
                                     'gorgeous_ring', 1, [TAGS['item'], TAGS['accessory']]),
    'platinum_traveller_boots': Inventory.Item('Platinum Traveller Boots', '50kg\n+120% speed\n+9 touching defense',
                                                'platinum_traveller_boots', 2, [TAGS['item'], TAGS['accessory']]),
    'sheath': Inventory.Item('Sheath', '20kg\n+18% melee damage\n+16 touching defense\n+0.5/sec regeneration\n+20% speed', 'sheath', 0,
                             [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'quiver': Inventory.Item('Quiver', '5kg\n+10% ranged damage\n+25% speed\n+8 touching defense', 'quiver', 0,
                             [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'hat': Inventory.Item('Hat',
                          '1kg\n+30% magical damage\n+6/sec mana regeneration\n+1/sec regeneration\n+2 touching defense\n+10% speed',
                          'hat', 0, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'firite_helmet': Inventory.Item('Firite Helmet',
                                    'Enable night vision\n30kg\n+30% melee damage\n+28 touching defense\n+19 magic defense\n+1.5/sec regeneration\n+24% speed',
                                    'firite_helmet', 3,
                                    [TAGS['item'], TAGS['accessory'], TAGS['night_vision'], TAGS['major_accessory']]),
    'firite_cloak': Inventory.Item('Firite Cloak',
                                   'Enable night vision\n10kg\n+32% ranged damage\n+14 touching defense\n+7 magic defense\n+0.5/sec regeneration\n+50% speed',
                                   'firite_cloak', 3,
                                   [TAGS['item'], TAGS['accessory'], TAGS['night_vision'], TAGS['major_accessory']]),
    'firite_pluvial': Inventory.Item('Firite Pluvial',
                                     'Enable night vision\n5kg\n+44% magical damage\n+6 touching defense\n+12 magic defense\n+2.5/sec regeneration\n+16/sec mana regeneration',
                                     'firite_pluvial', 3, [TAGS['item'], TAGS['accessory'], TAGS['night_vision'],
                                                           TAGS['major_accessory']]),
    'orange_ring': Inventory.Item('Orange Ring', 'Not afraid.\n+32% speed\n-2 touching defense', 'orange_ring', 3,
                                  [TAGS['item'], TAGS['accessory']]),
    'green_ring': Inventory.Item('Green Ring', 'Mercy.\n+18 touching defense\n+8 magic defense\n-40% speed', 'green_ring', 3,
                                 [TAGS['item'], TAGS['accessory']]),
    'blue_ring': Inventory.Item('Blue Ring',
                                'Never lies.\n+8/sec mana regeneration\n+5 magic defense\n-1/sec regeneration',
                                'blue_ring', 3, [TAGS['item'], TAGS['accessory']]),
    'magnificent_ring': Inventory.Item('Magnificent Ring', '+40% speed\n+22 touching defense\n'
                                                           '+10 magic defense\n+12/sec mana regeneration\n+6% critical',
                                       'magnificent_ring', 3, [TAGS['item'], TAGS['accessory']]),
    'bloody_traveller_boots': Inventory.Item('Bloody Traveller Boots', '60kg\n+150% speed\n+12 touching defense',
                                              'bloody_traveller_boots', 4, [TAGS['item'], TAGS['accessory']]),
    'fire_eye': Inventory.Item('Fire Eye', '1kg\n+30% ranged damage\n+10 magic defense', 'fire_eye', 2,
                                [TAGS['item'], TAGS['accessory'], TAGS['light_source']]),
    'aimer': Inventory.Item('Aimer', 'Enables aiming to menaces.\n1kg', 'aimer', 2,
                            [TAGS['item'], TAGS['accessory'], TAGS['light_source']]),
    'photon_aimer': Inventory.Item('Photon Aimer', 'Enables aiming to menaces.\n1.5kg', 'photon_aimer', 3,
                                    [TAGS['item'], TAGS['accessory'], TAGS['light_source']]),
    'winds_necklace': Inventory.Item('Winds Necklace', '+50% speed.\n-35% damage.\n+20% ranged damage.\n.5kg',
                                     'winds_necklace', 2, [TAGS['item'], TAGS['accessory']]),
    'windstorm_swordman_mark': Inventory.Item('Windstorm Swordman\'s Mark',
                                              '5kg\n+45% melee damage\n-12% damage\n+32 touching defense\n+34 magic defense\n+3/sec regeneration\nNight vision\nY: sweep the weapon and dealing 3 times the damage\n80 mana cost',
                                              'windstorm_swordman_mark', 4,
                                              [TAGS['item'], TAGS['accessory'], TAGS['night_vision'],
                                               TAGS['light_source'], TAGS['major_accessory']]),
    'windstorm_assassin_mark': Inventory.Item('Windstorm Assassin\'s Mark',
                                              '5kg\n+56% ranged damage\n-12% damage\n+17 touching defense\n+18 magic defense\n+1/sec regeneration\nNight vision\nY: use the weapon and sprint\n60 mana cost',
                                              'windstorm_assassin_mark', 4,
                                              [TAGS['item'], TAGS['accessory'], TAGS['night_vision'],
                                               TAGS['light_source'], TAGS['major_accessory']]),
    'windstorm_warlock_mark': Inventory.Item('Windstorm Warlock\'s Mark',
                                             '5kg\n+60% magical damage\n-12% damage\n+5 touching defense\n+12 magic defense\n+6/sec regeneration\n+15/sec mana regeneration\nNight vision\nY: use 20 times of the mana cost, summon 25 projectiles to the enemies',
                                             'windstorm_warlock_mark', 4,
                                             [TAGS['item'], TAGS['accessory'], TAGS['night_vision'],
                                              TAGS['light_source'], TAGS['major_accessory']]),
    'palladium_glove': Inventory.Item('Palladium Glove',
                                      '32kg\n+25% damage\n+32% speed\n+18/sec regeneration\n+8/sec mana regeneration\n+90 touching defense\n+65 magic defense\nNight vision',
                                      'palladium_glove', 5,
                                      [TAGS['item'], TAGS['accessory'], TAGS['night_vision'], TAGS['major_accessory']]),
    'mithrill_glove': Inventory.Item('Mithrill Glove',
                                     '32kg\n+32% damage\n+120% speed\n+3/sec regeneration\n+40/sec mana regeneration\n85 touching defense\n+95 magic defense\nNight vision',
                                     'mithrill_glove', 5,
                                     [TAGS['item'], TAGS['accessory'], TAGS['night_vision'], TAGS['major_accessory']]),
    'titanium_glove': Inventory.Item('Titanium Glove',
                                     '32 kg\n+50% damage\n+45% speed\n+10/sec regeneration\n+32/sec mana regeneration\n+108 touching defense\n+40 magic defense\nNight vision',
                                     'titanium_glove', 5,
                                     [TAGS['item'], TAGS['accessory'], TAGS['night_vision'], TAGS['major_accessory']]),
    'paladins_mark': Inventory.Item('Paladin\'s Mark',
                                    '80kg\n+100% speed\n+66% melee damage\n-15% damage\n+85 touching defense\n+70 magic defense\n+5/sec regeneration\nNight vision\nY: deal hallow stab\n40 mana cost',
                                    'paladins_mark', 5,
                                    [TAGS['item'], TAGS['accessory'], TAGS['night_vision'], TAGS['light_source'],
                                     TAGS['major_accessory']]),
    'daedalus_mark': Inventory.Item('Daedalus\'s Mark',
                                    '40kg\n+60% speed\n+72% ranged damage\n-15% damage\n+55 touching defense\n+45 magic defense\n+2/sec regeneration\nNight vision\nY: summon daedalus storm\n1200 piercing damage\n600 projectile speed\n60 mana cost',
                                    'daedalus_mark', 5,
                                    [TAGS['item'], TAGS['accessory'], TAGS['night_vision'], TAGS['light_source'],
                                     TAGS['major_accessory']]),
    'necklace_of_life': Inventory.Item('Necklace of Life', '0.2kg\n+30/sec regeneration\n+60/sec mana regeneration',
                                       'necklace_of_life', 7, [TAGS['item'], TAGS['accessory']]),
    'thorn_ring': Inventory.Item('Thorn Ring', '+120% magic damage\n-36/sec regeneration\n+200/sec mana regeneration',
                                 'thorn_ring', 7, [TAGS['item'], TAGS['accessory']]),
    'jevils_tail': Inventory.Item('Jevil\'s Tail', '+130 touching defense\n+280 magic defense\n-50% damage',
                                 'jevils_tail', 7, [TAGS['item'], TAGS['accessory']]),
    'cloudy_glasses': Inventory.Item('Cloudy Glasses', '50kg\n-20% damage\n+150% melee damage\n'
                                                       '80% speed\n+188 touching defense\n+128 magic defense\nNight vision\n'
                                                       'Y: Kill all projectiles.\n600 mana cost', 'cloudy_glasses', 7,
                                      [TAGS['item'], TAGS['accessory'], TAGS['night_vision']]),
    'cowboy_hat': Inventory.Item('Cowboy Hat', '20kg\n-20% damage\n+110% ranged damage\n+100% speed\n+10/sec '
                                               'regeneration\n+120 touching defense\n+150 magic defense\nNight '
                                               'vision\nY: Justice Time\n400 mana '
                                               'cost', 'cowboy_hat', 7, [TAGS['item'], TAGS['accessory'],
                                                                         TAGS['night_vision'],
                                                                         TAGS['major_accessory']]),
    'magicians_hat': Inventory.Item('Magician\'s Hat', '40kg\n-20% damage\n+210% magical damage\n+100% speed\n+40/sec '
                                                  'regeneration\n+100 touching defense\n+240 magic defense\n+200/sec mana regeneration\n'
                                                       'Night vision','magicians_hat', 7, [TAGS['item'], TAGS['accessory'],
                                                                               TAGS['night_vision'], TAGS['major_accessory']]),
    'great_magicians_hat': Inventory.Item('Great Magician\'s Hat', '60kg\n-20% damage\n+320% magical damage\n+100% speed\n+60/sec '
                                                                    'regeneration\n+120 touching defense\n+280 magic defense\n+240/sec mana regeneration\n'
                                                                     '+80% domain size\n+20/sec mentality regeneration', 'great_magicians_hat', 8, [TAGS['item'], TAGS['accessory'],
                                                                                           TAGS['night_vision'], TAGS['major_accessory']]),
    'gods_necklace': Inventory.Item('God\'s Necklace', '+50% domain size\n+6/sec talent regeneration', 'gods_necklace', 9, [TAGS['item'], TAGS['accessory']]),
    'magisters_hat': Inventory.Item('Magister\'s Hat', '80kg\n-20% damage\n+420% magical damage\n+100% speed\n+80/sec '
                                                 'regeneration\n+140 touching defense\n+320 magic defense\n+280/sec mana regeneration\n'
                                                  '+220% domain size\n+50/sec mentality regeneration','magisters_hat', 9, [TAGS['item'], TAGS['accessory'],
                                                                             TAGS['night_vision'], TAGS['major_accessory']]),
    'bezoar_necklace': Inventory.Item('Bezoar Necklace', '-25% poison damage received\n+20 poison defense', 'bezoar_necklace', 7,
                                       [TAGS['item'], TAGS['accessory']]),

    'wings': Inventory.Item('Wings', 'The perseverance to fly.\n80kg\n-60% air resistance\n+240% speed', 'wings', 4,
                            [TAGS['item'], TAGS['accessory'], TAGS['wings']]),
    'honest_flyer': Inventory.Item('Honest Flyer', 'The perseverance to fly.\n280kg\n-80% air resistance\n+480% speed',
                                   'honest_flyer', 5, [TAGS['item'], TAGS['accessory'], TAGS['wings']]),

    'weak_healing_potion': Inventory.Item('Weak Healing Potion', 'Recover 50 HP\nCausing potion sickness.',
                                          'weak_healing_potion', 0, [TAGS['item'], TAGS['healing_potion']]),
    'weak_magic_potion': Inventory.Item('Weak Magic Potion', 'Recover 60 MP\nCausing potion sickness.',
                                        'weak_magic_potion', 0, [TAGS['item'], TAGS['magic_potion']]),
    'crabapple': Inventory.Item('Crabapple', 'Heals 120 HP', 'crabapple', 2, [TAGS['item'], TAGS['healing_potion']]),
    'butterscotch_pie': Inventory.Item('Butterscotch Pie', 'Heals 240 HP', 'butterscotch_pie', 4,
                                       [TAGS['item'], TAGS['healing_potion']]),
    'seatea': Inventory.Item('Seatea', 'Recovers 150 MP', 'seatea', 4, [TAGS['item'], TAGS['magic_potion']]),

    'mana_crystal': Inventory.Item('Mana Crystal', '+15 maximum mana.', 'mana_crystal', 2, [TAGS['item']]),
    'firy_plant': Inventory.Item('Firy Plant', '+20 maximum hp', 'firy_plant', 3, [TAGS['item']]),
    'spiritual_heart': Inventory.Item('Spiritual Heart',
                                      '+100 maximum hp\n+180 maximum mana\nSomething perseverance happen.',
                                      'spiritual_heart', 4, [TAGS['item']]),
    'life_fruit': Inventory.Item('Life Fruit', '+400 maximum HP\n+500 maximum MP\n+40 maximum talent', 'life_fruit', 4,
                                 [TAGS['item'], TAGS['healing_potion']]),

    'ballet_shoes': Inventory.Item('Ballet Shoes', '', 'ballet_shoes', 6,
                                   [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_water'], TAGS['magic_lv_3']]),
    'tough_gloves': Inventory.Item('Tough Gloves', 'Shoots arrows by your hand.', 'tough_gloves', 6,
                                   [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'burnt_pan': Inventory.Item('Burnt Pan', 'Press Q to stab.', 'burnt_pan', 6, [TAGS['item'], TAGS['weapon']]),
    'toy_knife': Inventory.Item('Toy Knife', 'Deal damage to enemies in range.', 'toy_knife', 7,
                                [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_water'], TAGS['magic_lv_5']]),
    'worn_notebook': Inventory.Item('Worn Notebook', '', 'worn_notebook', 7, [TAGS['item'], TAGS['weapon']]),
    'empty_gun': Inventory.Item('Empty Gun', '', 'empty_gun', 7, [TAGS['item'], TAGS['weapon'], TAGS['gun']]),

    'suspicious_eye': Inventory.Item('Suspicious Eye', 'Summon the true eye', 'suspicious_eye', 0, [TAGS['item']]),
    'fire_slime': Inventory.Item('Fire Slime', 'Summon the magma king', 'fire_slime', 0, [TAGS['item']]),
    'wind': Inventory.Item('Wind', 'Summon the sandstorm', 'wind', 0, [TAGS['item']]),
    'blood_substance': Inventory.Item('Blood Substance', 'Summon the Abyss Eye', 'blood_substance', 0, [TAGS['item']]),
    'mechanic_eye': Inventory.Item('Mechanic Eye', 'Summon the twin eyes', 'mechanic_eye', 0, [TAGS['item']]),
    'mechanic_worm': Inventory.Item('Mechanic Worm', 'Summon the destroyer', 'mechanic_worm', 0, [TAGS['item']]),
    'electric_unit': Inventory.Item('Electric Unit', 'Summon the CPU', 'electric_unit', 0, [TAGS['item']]),
    'mechanic_spider': Inventory.Item('Electric Spider', 'Summon the Greed', 'mechanic_spider', 0, [TAGS['item']]),
    'watch': Inventory.Item('Watch', 'Summon the eye of time', 'watch', 0, [TAGS['item']]),
    'metal_food': Inventory.Item('Metal Food', 'Summon the devil python', 'metal_food', 0, [TAGS['item']]),
    'joker': Inventory.Item('JOKER', 'Summon the Joker Evil', 'joker', 0, [TAGS['item']]),
    'plantera_bulb': Inventory.Item('Plantera Bulb', 'Summon Plantera', 'plantera_bulb', 0, [TAGS['item']]),

    'invalid': Inventory.Item('Invalid Item', 'Invalid item', 'invalid', 0, []),
}


class Items:
    ITEMS = items_dict

    def __getitem__(self, item):
        try:
            return self.ITEMS[item]
        except KeyError:
            self.ITEMS[item] = Inventory.Item('Invalid Item', 'Invalid item: ' + item.replace('_', ' '), item, 0, [])
            return self.ITEMS[item]

    def __setitem__(self, key, value):
        self.ITEMS[key] = value

    def values(self):
        return self.ITEMS.values()

    def keys(self):
        return self.ITEMS.keys()

    def items(self):
        return self.ITEMS.items()


ITEMS = Items()


class Recipe:
    def __init__(self, material: dict[str, int], result: str, crafted_amount: int = 1):
        self.material = material
        self.result = result
        self.crafted_amount = crafted_amount

    def make(self, inv: Inventory):
        for it, qt in self.material.items():
            if TAGS['workstation'] not in ITEMS[it].tags:
                inv.remove_item(ITEMS[it], qt)
        inv.add_item(ITEMS[self.result], self.crafted_amount)

    def is_valid(self, inv: Inventory):
        if not len(self.material):
            return True
        for it, qt in self.material.items():
            if not inv.is_enough(ITEMS[it], qt):
                return False
        return True

    def is_related(self, inv: Inventory):
        if not len(self.material):
            return True
        mr = max([ITEMS[it].rarity for it, _ in self.material.items()])
        for it, _ in self.material.items():
            if ITEMS[it].rarity == mr and inv.is_enough(ITEMS[it]):
                return True
        return False


RECIPES = [
    Recipe({'wood': 15}, 'wooden_hammer'),
    Recipe({'wood': 35, 'wooden_hammer': 1}, 'wooden_sword'),
    Recipe({'wood': 40, 'copper': 1}, 'torch'),
    Recipe({'wood': 20, 'leaf': 8}, 'natural_necklace'),
    Recipe({'wood': 25, 'leaf': 1, 'wooden_hammer': 1}, 'glowing_splint'),
    Recipe({'wood': 55, 'wooden_hammer': 1}, 'bow'),
    Recipe({'wood': 1, 'wooden_hammer': 1}, 'arrow', 10),
    Recipe({'wood': 30, 'copper': 5, 'glowing_splint': 1, 'wooden_hammer': 1}, 'furnace'),
    Recipe({'copper': 3, 'furnace': 1}, 'copper_ingot'),
    Recipe({'copper_ingot': 8}, 'anvil'),
    Recipe({'copper_ingot': 16, 'anvil': 1}, 'copper_traveller_boots'),
    Recipe({'copper_ingot': 12, 'wood': 10, 'anvil': 1}, 'copper_sword'),
    Recipe({'copper_ingot': 15, 'anvil': 1}, 'copper_wand'),
    Recipe({'copper_ingot': 22, 'anvil': 1}, 'copper_bow'),
    Recipe({'copper_ingot': 32, 'wood': 12, 'anvil': 1}, 'copper_knife'),
    Recipe({'iron': 4}, 'iron_ingot'),
    Recipe({'iron_ingot': 1, 'steel_ingot': 1, 'copper_ingot': 24, 'anvil': 1}, 'thiefs_charm'),
    Recipe({'iron_ingot': 15, 'wood': 10, 'anvil': 1}, 'iron_sword'),
    Recipe({'steel_ingot': 10, 'iron_ingot': 5, 'anvil': 1}, 'steel_sword'),
    Recipe({'iron_ingot': 12, 'steel_ingot': 6}, 'spear'),
    Recipe({'iron_ingot': 12, 'steel_ingot': 12, 'anvil': 1}, 'iron_blade'),
    Recipe({'iron_ingot': 15, 'anvil': 1}, 'iron_wand'),
    Recipe({'iron_ingot': 20, 'anvil': 1}, 'iron_bow'),
    Recipe({'iron_ingot': 12, 'steel_ingot': 10, 'anvil': 1}, 'dagger'),
    Recipe({'iron_ingot': 25, 'steel_ingot': 2, 'anvil': 1}, 'pistol'),
    Recipe({'iron_ingot': 5, 'steel_ingot': 20, 'anvil': 1}, 'rifle'),
    Recipe({'steel_ingot': 24, 'iron_ingot': 6, 'anvil': 1}, 'steel_bow'),
    Recipe({'steel': 4}, 'steel_ingot'),
    Recipe({'steel_ingot': 1, 'iron_ingot': 1}, 'bullet', 50),
    Recipe({'steel': 10, 'anvil': 1}, 'shield'),
    Recipe({'steel_ingot': 24, 'iron_ingot': 12, 'anvil': 1}, 'tower_shield'),
    Recipe({'iron_ingot': 8, 'steel_ingot': 8, 'anvil': 1}, 'metal_traveller_boots'),
    Recipe({'cell_organization': 3}, 'soul_bottle'),
    Recipe({'cell_organization': 1}, 'weak_healing_potion', 10),
    Recipe({'cell_organization': 5, 'iron_ingot': 8}, 'terrified_necklace'),
    Recipe({'torch': 10, 'steel': 5, 'iron': 5, 'anvil': 1}, 'burning_book'),
    Recipe({'platinum': 3}, 'platinum_ingot'),
    Recipe({'purple_ring': 1, 'cyan_ring': 1, 'yellow_ring': 1}, 'gorgeous_ring'),
    Recipe({'platinum_ingot': 10, 'anvil': 1}, 'platinum_traveller_boots'),
    Recipe({'platinum_ingot': 15, 'steel_ingot': 10, 'anvil': 1}, 'platinum_sword'),
    Recipe({'platinum_ingot': 21, 'iron_ingot': 8, 'anvil': 1}, 'platinum_blade'),
    Recipe({'platinum_ingot': 20, 'anvil': 1}, 'platinum_spear'),
    Recipe({'platinum_ingot': 15, 'magic_stone': 8, 'anvil': 1}, 'platinum_wand'),
    Recipe({'wood': 60, 'magic_stone': 15, 'leaf': 5, 'platinum': 24, 'anvil': 1}, 'life_wooden_sword'),
    Recipe({'wood': 60, 'mana_crystal': 2, 'leaf': 10, 'anvil': 1}, 'life_wooden_wand'),
    Recipe({'platinum_ingot': 20, 'anvil': 1}, 'platinum_bow'),
    Recipe({'platinum_ingot': 30, 'magic_stone': 5, 'anvil': 1}, 'submachine_gun'),
    Recipe({'platinum_ingot': 54, 'magic_stone': 16, 'anvil': 1}, 'platinum_doubleknife'),
    Recipe({'bullet': 100, 'platinum_ingot': 1, 'anvil': 1}, 'platinum_bullet', 100),
    Recipe({'magic_stone': 10}, 'mana_crystal'),
    Recipe({'magic_stone': 15, 'wood': 10, 'anvil': 1}, 'magic_arrow', 100),
    Recipe({'magic_stone': 25, 'platinum': 60}, 'talent_book'),
    Recipe({'magic_stone': 5, 'platinum_ingot': 6}, 'magic_anklet'),
    Recipe({'magic_stone': 1}, 'weak_magic_potion', 25),
    Recipe({'magic_blade': 2}, 'magic_sword'),
    Recipe({'magic_sword': 2}, 'magic_blade'),
    Recipe({'magic_stone': 40, 'anvil': 1}, 'night_visioner'),
    Recipe({'platinum_ingot': 3, 'magic_blade': 1}, 'sheath'),
    Recipe({'platinum_ingot': 3, 'magic_sword': 1}, 'sheath'),
    Recipe({'platinum_ingot': 3, 'magic_arrow': 100}, 'quiver'),
    Recipe({'orange_ring': 1, 'blue_ring': 1, 'green_ring': 1}, 'magnificent_ring'),
    Recipe({'platinum': 9, 'mana_crystal': 3}, 'hat'),
    Recipe({'blood_ingot': 18, 'anvil': 1}, 'bloody_traveller_boots'),
    Recipe({'platinum_ingot': 10, 'blood_ingot': 20, 'anvil': 1}, 'bloody_sword'),
    Recipe({'platinum_ingot': 12, 'blood_ingot': 32, 'anvil': 1}, 'blood_pike'),
    Recipe({'platinum_ingot': 6, 'blood_ingot': 24, 'anvil': 1}, 'bloody_bow'),
    Recipe({'wood': 20, 'leaf': 20, 'coniferous_leaf': 50, 'blood_ingot': 32, 'anvil': 1}, 'forests_bow'),
    Recipe({'platinum_ingot': 8, 'blood_ingot': 16, 'mana_crystal': 1, 'anvil': 1}, 'blood_wand'),
    Recipe({'blood_ingot': 5, 'platinum_ingot': 5, 'anvil': 1}, 'blood_arrow', 100),
    Recipe({'blood_ingot': 2, 'platinum_ingot': 1, 'anvil': 1}, 'plasma', 50),
    Recipe({'blood_ingot': 8, 'firite_ingot': 22, 'anvil': 1}, 'firite_spear'),
    Recipe({'firy_plant': 1, 'firite_ingot': 24, 'anvil': 1}, 'fire_eye'),
    Recipe({'blood_ingot': 5, 'firite_ingot': 30, 'anvil': 1}, 'magma_assaulter'),
    Recipe({'firite_ingot': 25, 'platinum': 20, 'anvil': 1}, 'volcano'),
    Recipe({'firite_ingot': 64, 'platinum_ingot': 16, 'anvil': 1}, 'firite_helmet'),
    Recipe({'firite_ingot': 64, 'platinum_ingot': 16, 'anvil': 1}, 'firite_cloak'),
    Recipe({'firite_ingot': 64, 'platinum_ingot': 16, 'anvil': 1}, 'firite_pluvial'),
    Recipe({'platinum': 24, 'blood_ingot': 16, 'magic_stone': 10, 'firy_plant': 1, 'anvil': 1}, 'hematology'),
    Recipe({'platinum': 24, 'magic_stone': 6, 'firite_ingot': 8, 'firy_plant': 2, 'anvil': 1}, 'fire_magic_sword'),
    Recipe({'magic_stone': 10, 'firy_plant': 1}, 'crabapple', 5),
    Recipe({'blood_ingot': 12, 'cell_organization': 6, 'firy_plant': 6}, 'twilight_shortsword'),
    Recipe({'mysterious_substance': 4, 'furnace': 1}, 'mysterious_ingot'),
    Recipe({'mysterious_ingot': 12, 'magic_stone': 6, 'mana_crystal': 6}, 'dawn_shortsword'),
    Recipe({'platinum_ingot': 30, 'mysterious_ingot': 5, 'anvil': 1}, 'winds_necklace'),
    Recipe({'mysterious_ingot': 12, 'anvil': 1}, 'recurve_bow'),
    Recipe({'mysterious_ingot': 10, 'blood_ingot': 8, 'anvil': 1}, 'sand_sword'),
    Recipe({'mysterious_ingot': 1, 'blood_ingot': 2, 'anvil': 1}, 'rock_bullet', 200),
    Recipe({'mysterious_ingot': 11, 'blood_ingot': 20, 'mana_crystal': 2}, 'rock_wand'),
    Recipe({'platinum_sword': 1, 'magic_sword': 1, 'bloody_sword': 1, 'volcano': 1, 'sand_sword': 1, 'storm_core': 1},
           'nights_edge'),
    Recipe({'platinum_ingot': 32, 'blood_ingot': 20, 'firite_ingot': 20, 'mysterious_ingot': 20, 'storm_core': 1},
           'nights_pike'),
    Recipe({'mysterious_ingot': 12, 'storm_core': 1}, 'storm_swift_sword'),
    Recipe({'platinum_wand': 1, 'burning_book': 1, 'talent_book': 1, 'blood_wand': 1, 'rock_wand': 1, 'storm_core': 1},
           'midnights_wand'),
    Recipe({'platinum_bow': 1, 'submachine_gun': 1, 'bloody_bow': 1, 'magma_assaulter': 1, 'recurve_bow': 1,
            'storm_core': 1}, 'shadow'),
    Recipe({'twilight_shortsword': 1, 'dawn_shortsword': 1, 'storm_core': 1}, 'night_twinsword'),
    Recipe({'platinum_ingot': 12, 'storm_core': 3}, 'storm_stabber'),
    Recipe({'platinum_ingot': 10, 'blood_ingot': 5, 'firite_ingot': 5, 'mysterious_ingot': 5, 'storm_core': 1},
           'shadow_bullet', 500),
    Recipe({'storm_core': 3}, 'windstorm_warlock_mark'),
    Recipe({'storm_core': 3}, 'windstorm_assassin_mark'),
    Recipe({'storm_core': 3}, 'windstorm_swordman_mark'),
    Recipe({'soul': 60}, 'spiritual_heart'),
    Recipe({'soul': 30, 'firy_plant': 5}, 'butterscotch_pie', 20),
    Recipe({'soul': 10, 'magic_stone': 5}, 'seatea', 20),
    Recipe({'palladium': 4}, 'palladium_ingot'),
    Recipe({'mithrill': 4}, 'mithrill_ingot'),
    Recipe({'titanium': 4}, 'titanium_ingot'),
    Recipe({'mithrill_ingot': 10}, 'mithrill_anvil'),
    Recipe({'palladium_ingot': 12, 'mithrill_anvil': 1}, 'palladium_sword'),
    Recipe({'mithrill_ingot': 12, 'mithrill_anvil': 1}, 'mithrill_sword'),
    Recipe({'titanium_ingot': 12, 'mithrill_anvil': 1}, 'titanium_sword'),
    Recipe({'palladium_ingot': 15, 'mithrill_anvil': 1}, 'palladium_gun'),
    Recipe({'mithrill_ingot': 15, 'mithrill_anvil': 1}, 'mithrill_gun'),
    Recipe({'titanium_ingot': 15, 'mithrill_anvil': 1}, 'titanium_gun'),
    Recipe({'palladium_ingot': 45, 'mithrill_anvil': 1}, 'palladium_glove'),
    Recipe({'mithrill_ingot': 45, 'mithrill_anvil': 1}, 'mithrill_glove'),
    Recipe({'titanium_ingot': 45, 'mithrill_anvil': 1}, 'titanium_glove'),
    Recipe({'spiritual_stabber': 1, 'evil_ingot': 20, 'soul': 120, 'mithrill_anvil': 1}, 'balanced_stabber'),
    Recipe({'spiritual_piercer': 1, 'evil_ingot': 20, 'soul': 120, 'mithrill_anvil': 1}, 'discord_storm'),
    Recipe({'spiritual_piercer': 1, 'evil_ingot': 20, 'soul': 120, 'mithrill_anvil': 1}, 'spiritual_knife'),
    Recipe({'spiritual_destroyer': 1, 'evil_ingot': 20, 'soul': 120, 'mithrill_anvil': 1}, 'evil_book'),
    Recipe({'soul': 30, 'palladium_ingot': 8, 'evil_ingot': 10}, 'blood_sacrifice'),
    Recipe({'soul': 10, 'mithrill_ingot': 15}, 'blade_wand'),
    Recipe({'soul_of_flying': 20, 'soul': 100, 'mithrill_anvil': 1}, 'wings'),
    Recipe({'palladium_ingot': 1, 'mithrill_ingot': 1, 'soul': 5, 'mithrill_anvil': 1}, 'saint_steel_ingot'),
    Recipe({'mithrill_ingot': 1, 'titanium_ingot': 1, 'soul': 5, 'mithrill_anvil': 1}, 'daedalus_ingot'),
    Recipe({'palladium_ingot': 1, 'titanium_ingot': 1, 'soul': 5, 'mithrill_anvil': 1}, 'dark_ingot'),
    Recipe({'balanced_stabber': 1, 'saint_steel_ingot': 8, 'mithrill_anvil': 1}, 'excalibur'),
    Recipe({'windstorm_swordman_mark': 1, 'saint_steel_ingot': 5, 'mithrill_anvil': 1}, 'paladins_mark'),
    Recipe({'discord_storm': 1, 'daedalus_ingot': 8, 'mithrill_anvil': 1}, 'daedalus_stormbow'),
    Recipe({'daedalus_ingot': 12, 'mithrill_anvil': 1}, 'daedalus_knife'),
    Recipe({'daedalus_knife': 1, 'spiritual_knife': 1}, 'daedalus_twinknife'),
    Recipe({'windstorm_assassin_mark': 1, 'daedalus_ingot': 5, 'mithrill_anvil': 1}, 'daedalus_mark'),
    Recipe({'evil_book': 1, 'dark_ingot': 8, 'mithrill_anvil': 1}, 'curse_book'),
    Recipe({'saint_steel_ingot': 6, 'soul_of_integrity': 20, 'mithrill_anvil': 1}, 'ballet_shoes'),
    Recipe({'palladium_ingot': 24, 'soul_of_integrity': 10, 'mithrill_anvil': 1}, 'gravity_wand'),
    Recipe({'wings': 1, 'soul_of_integrity': 10, 'mithrill_anvil': 1}, 'honest_flyer'),
    Recipe({'soul_of_integrity': 2, 'soul': 1, 'mithrill_anvil': 1}, 'quick_arrow', 200),
    Recipe({'daedalus_ingot': 6, 'soul_of_bravery': 20, 'mithrill_anvil': 1}, 'tough_gloves'),
    Recipe({'soul_of_bravery': 2, 'soul': 1, 'mithrill_anvil': 1}, 'quick_bullet', 200),
    Recipe({'mithrill_ingot': 12, 'soul_of_bravery': 18, 'soul_of_integrity': 12, 'mithrill_anvil': 1},
           'forward_bow'),
    Recipe({'mithrill_ingot': 24, 'soul_of_kindness': 10, 'mithrill_anvil': 1}, 'shield_wand'),
    Recipe({'mithrill_ingot': 20, 'soul_of_kindness': 24}, 'energy_spear'),
    Recipe({'dark_ingot': 6, 'soul_of_kindness': 20}, 'burnt_pan'),
    Recipe(
        {'excalibur': 1, 'soul_of_integrity': 10, 'soul_of_bravery': 10, 'soul_of_kindness': 10, 'mithrill_anvil': 1},
        'true_excalibur'),
    Recipe(
        {'nights_edge': 1, 'soul_of_integrity': 10, 'soul_of_bravery': 10, 'soul_of_kindness': 10, 'mithrill_anvil': 1},
        'true_nights_edge'),
    Recipe(
        {'saint_steel_ingot': 24, 'evil_ingot': 24, 'soul_of_integrity': 10, 'soul_of_bravery': 10, 'soul_of_kindness': 10,
         'mithrill_anvil': 1}, 'muramasa'),
    Recipe({'shadow': 1, 'soul_of_integrity': 10, 'soul_of_bravery': 10, 'soul_of_kindness': 10, 'mithrill_anvil': 1},
           'true_shadow'),
    Recipe({'daedalus_twinknife': 1, 'soul_of_integrity': 10, 'soul_of_bravery': 10, 'soul_of_kindness': 10, 'mithrill_anvil': 1},
           'true_twinblade'),
    Recipe({'soul_of_integrity': 2, 'soul_of_bravery': 1, 'soul_of_kindness': 1, 'mana_crystal': 1},
           'mystery_core'),
    Recipe({'mithrill_ingot': 30, 'mystery_core': 3, 'soul': 300}, 'forbidden_curse__spirit'),
    Recipe({'mithrill_ingot': 30, 'mystery_core': 3, 'evil_ingot': 100}, 'forbidden_curse__evil'),
    Recipe({'daedalus_stormbow': 1, 'soul_of_integrity': 10, 'soul_of_bravery': 10, 'soul_of_kindness': 10,
            'mithrill_anvil': 1}, 'true_daedalus_stormbow'),
    Recipe({'soul_of_perseverance': 15, 'saint_steel_ingot': 18}, 'perseverance_sword'),
    Recipe({'soul_of_perseverance': 32, 'saint_steel_ingot': 8}, 'black_hole_sword'),
    Recipe({'saint_steel_ingot': 18, 'soul_of_perseverance': 12}, 'worn_notebook'),
    Recipe({'mithrill_ingot': 30, 'mystery_core': 3, 'soul_of_patience': 10}, 'forbidden_curse__time'),
    Recipe({'dark_ingot': 18, 'soul_of_patience': 12}, 'toy_knife'),
    Recipe({'saint_steel_ingot': 20, 'soul_of_patience': 12, 'soul_of_perseverance': 18}, 'millennium_persists'),
    Recipe({'daedalus_ingot': 18, 'soul_of_justice': 12}, 'empty_gun'),
    Recipe({'daedalus_ingot': 24, 'soul_of_justice': 22, 'soul_of_patience': 8, 'soul_of_bravery': 8}, 'bow_of_sanction'),
    Recipe({'chlorophyll': 1, 'weak_healing_potion': 1}, 'photon'),
    Recipe({'chlorophyll': 1, 'crabapple': 1}, 'photon', 2),
    Recipe({'chlorophyll': 1, 'butterscotch_pie': 1}, 'photon', 3),
    Recipe({'dark_ingot': 10, 'photon': 20}, 'prism'),
    Recipe({'chlorophyll': 1, 'photon': 5, 'soul_of_perseverance': 1, 'soul_of_patience': 1,
            'soul_of_justice': 1, 'soul_of_growth': 1}, 'chlorophyte_ingot', 3),
    Recipe({'chlorophyte_ingot': 16, 'soul_of_perseverance': 12, 'soul_of_patience': 3, 'soul_of_justice': 3},
           'life_devourer'),
    Recipe({'chlorophyte_ingot': 24, 'soul_of_justice': 18, 'soul_of_patience': 6, 'photon': 6},
           'lazer_rain'),
    Recipe({'chlorophyte_ingot': 18, 'soul_of_justice': 12, 'soul_of_patience': 3, 'soul_of_perseverance': 3},
           'lazer_gun'),
    Recipe({'chlorophyte_ingot': 32, 'soul_of_justice': 18, 'soul_of_patience': 2, 'soul_of_perseverance': 2},
           'lazer_sniper'),
    Recipe({'chlorophyte_ingot': 12, 'photon': 32, 'soul_of_patience': 10, 'soul_of_perseverance': 2,
            'soul_of_justice': 2}, 'prism_wand'),
    Recipe({'chlorophyte_ingot': 15, 'photon': 60, 'soul_of_patience': 10, 'soul_of_perseverance': 3,
            'soul_of_justice': 3}, 'astigmatism'),
    Recipe({'chlorophyte_ingot': 2, 'photon': 5}, 'chloro_arrow', 200),
    Recipe({'chlorophyte_ingot': 16}, 'necklace_of_life'),
    Recipe({'chlorophyte_ingot': 16}, 'thorn_ring'),
    Recipe({'soul_of_growth': 32, 'chlorophyte_ingot': 1, 'butterscotch_pie': 1}, 'life_fruit'),
    Recipe({'aimer': 1, 'photon': 32}, 'photon_aimer'),
    Recipe({'soul_of_growth': 24, 'chlorophyte_ingot': 8}, 'life_wand'),
    Recipe({'chlorophyte_ingot': 5, 'soul_of_justice': 32, 'soul_of_patience': 1, 'soul_of_perseverance': 1}, 'cowboy_hat'),
    Recipe({'chlorophyte_ingot': 5, 'soul_of_perseverance': 32, 'soul_of_patience': 1, 'soul_of_justice': 1}, 'cloudy_glasses'),
    Recipe({'chlorophyte_ingot': 5, 'soul_of_patience': 32, 'soul_of_perseverance': 1, 'soul_of_justice': 1}, 'magicians_hat'),
    Recipe({'chaos_ingot': 3}, 'space_jumper', 100),
    Recipe({'chaos_ingot': 32}, 'chaos_teleporter'),
    Recipe({'chaos_ingot': 36}, 'chaos_killer'),
    Recipe({'chaos_ingot': 64}, 'gods_necklace'),
    Recipe({'chaos_ingot': 12, 'firite_ingot': 1}, 'skyfire__meteor'),
    Recipe({'chaos_ingot': 12, 'magic_stone': 1}, 'azure_guard'),
    Recipe({'chaos_ingot': 12, 'storm_core': 1}, 'storm'),
    Recipe({'chaos_ingot': 12, 'iron_ingot': 1}, 'earth_wall'),
    Recipe({'chaos_ingot': 15, 'leaf': 1}, 'lifebringer'),
    Recipe({'chaos_ingot': 15, 'cell_organization': 1}, 'target_dummy'),
    Recipe({'chaos_ingot': 15, 'photon': 1}, 'judgement_light'),
    Recipe({'chaos_ingot': 1, 'photon': 1}, 'dark_restrict'),
    Recipe({'chaos_ingot': 32, 'firite_ingot': 1}, 'forbidden_curse__fire'),
    Recipe({'true_nights_edge': 1, 'true_excalibur': 1, 'perseverance_sword': 1,
            'life_devourer': 1, 'jevil_knife': 1}, 'the_blade'),
    Recipe({'muramasa': 1, 'remote_sword': 1, 'black_hole_sword': 1, 'chaos_ingot': 12}, 'demon_blade__muramasa'),
    Recipe({'chaos_ingot': 88, 'jevil_knife': 1}, 'chaos_chaos'),
    Recipe({'chaos_ingot': 128, 'soul_of_patience': 64}, 'great_magicians_hat'),

    Recipe({'chaos_ingot': 128, 'storm_core': 32}, 'primal__winds_wand'),
    Recipe({'chaos_ingot': 128, 'blood_ingot': 512, 'cell_organization': 128}, 'primal__life_wand'),

    Recipe({'photon': 100, 'chlorophyll': 1}, 'lights_bible'),
    Recipe({'lights_bible': 1,' photon': 1}, 'light_purify'),
    Recipe({'soul': 20, 'chlorophyll': 1, 'soul_of_patience': 10}, 'energy_bible'),

    Recipe({'soul': 1, 'soul_of_flying': 1, 'soul_of_coldness': 1, 'soul_of_growth': 1, 'soul_of_bravery': 1,
            'soul_of_kindness': 1, 'soul_of_integrity': 1, 'soul_of_perseverance': 1, 'soul_of_patience': 1,
            'soul_of_justice': 1, 'willpower_shard': 1}, 'soul_of_determination'),
    Recipe({'chaos_ingot': 200, 'soul_of_determination': 12, 'origin': 1}, 'magisters_hat'),
    Recipe({'origin': 1, 'chaos_ingot': 25}, 'chaos_heart'),
    Recipe({'chaos_ingot': 500, 'soul_of_determination': 8, 'wierd_essence': 36}, 'uncanny_valley'),
    Recipe({'chaos_ingot': 300, 'soul_of_determination': 12, 'wierd_essence': 32}, 'death_note'),
    Recipe({'chaos_ingot': 500, 'soul_of_determination': 8, 'time_essence': 36}, 'hour_hand'),
    Recipe({'chaos_ingot': 300, 'soul_of_determination': 12, 'time_essence': 32}, 'stop'),
    Recipe({'chaos_ingot': 600, 'soul_of_determination': 8, 'time_essence': 36, 'time_fountain': 1}, 'metal_hand'),
    Recipe({'chaos_ingot': 720, 'soul_of_determination': 6, 'time_essence': 40, 'time_fountain': 1}, 'time_flies'),
    Recipe({'chaos_ingot': 720, 'soul_of_determination': 6, 'time_essence': 40, 'time_fountain': 1}, 'accelerationism'),

    Recipe({'cell_organization': 10}, 'suspicious_eye'),
    Recipe({'cell_organization': 5, 'firite_ingot': 1}, 'fire_slime'),
    Recipe({'cell_organization': 5, 'mysterious_substance': 3}, 'wind'),
    Recipe({'cell_organization': 30, 'storm_core': 3}, 'blood_substance'),
    Recipe({'palladium_ingot': 1, 'mithrill_ingot': 1, 'titanium_ingot': 1, 'soul': 10}, 'mechanic_eye'),
    Recipe({'mithrill_ingot': 1, 'titanium_ingot': 1, 'palladium_ingot': 1, 'soul': 10}, 'mechanic_worm'),
    Recipe({'titanium_ingot': 1, 'palladium_ingot': 1, 'mithrill_ingot': 1, 'soul': 10}, 'electric_unit'),
    Recipe({'palladium_ingot': 2, 'soul_of_kindness': 1}, 'mechanic_spider'),
    Recipe({'mithrill_ingot': 2, 'soul_of_integrity': 1}, 'watch'),
    Recipe({'titanium_ingot': 2, 'soul_of_bravery': 1}, 'metal_food'),
    Recipe({'chlorophyte_ingot': 1, 'photon': 4}, 'joker'),

]


def setup():
    for i, item in enumerate(ITEMS.values()):
        item.inner_id = i


def get_item_by_id(item_id: int):
    return [item for item in ITEMS.values() if item.inner_id == item_id][0]


setup()
