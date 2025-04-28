from underia import weapons, projectiles, game
from values import damages


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
                        elif desc.endswith('armor'):
                            self.accessory_data['armor'] = float(desc.removesuffix('armor'))
                        elif desc.endswith('%wingcontrol'):
                            self.accessory_data['wing_control'] = int(desc.removesuffix('%wingcontrol'))
                        elif desc.endswith('touchingdefense'):
                            self.accessory_data['touch_def'] = int(desc.removesuffix('touchingdefense'))
                        elif desc.endswith('physicaldefense'):
                            self.accessory_data['phys_def'] = int(desc.removesuffix('physicaldefense'))
                        elif desc.endswith('magicdefense'):
                            self.accessory_data['mag_def'] = int(desc.removesuffix('magicdefense'))
                        elif desc.endswith('%speed'):
                            self.accessory_data['speed'] = int(desc.removesuffix('%speed'))
                        elif desc.endswith('%ammosavechance'):
                            self.accessory_data['ammo_save'] = int(desc.removesuffix('%ammosavechance'))
                        elif desc.endswith('attackspeed'):
                            self.accessory_data['atk_speed'] = int(desc.removesuffix('attackspeed'))
                        elif desc.endswith('%critical'):
                            self.accessory_data['crit'] = int(desc.removesuffix('%critical'))
                        elif desc.endswith('/secregeneration'):
                            self.accessory_data['regen'] = float(desc.removesuffix('/secregeneration'))
                        elif desc.endswith('/secmanaregeneration'):
                            self.accessory_data['mana_regen'] = float(desc.removesuffix('/secmanaregeneration'))
                        elif desc.endswith('/secinspirationregeneration'):
                            self.accessory_data['ins_regen'] = float(desc.removesuffix('/secinspirationregeneration'))
                        elif desc.endswith('%damage'):
                            self.accessory_data['damage'] = int(desc.removesuffix('%damage'))
                        elif desc.endswith('%meleedamage'):
                            self.accessory_data['melee_damage'] = int(desc.removesuffix('%meleedamage'))
                        elif desc.endswith('%rangeddamage'):
                            self.accessory_data['ranged_damage'] = int(desc.removesuffix('%rangeddamage'))
                        elif desc.endswith('%magicdamage') or desc.endswith('%magicaldamage'):
                            self.accessory_data['magic_damage'] = int(desc.split('%magic')[0])
                        elif desc.endswith('%octavedamage'):
                            self.accessory_data['octave_damage'] = int(desc.removesuffix('%octavedamage'))
                        elif desc.endswith('%hallowdamage'):
                            self.accessory_data['hallow_damage'] = int(desc.removesuffix('%hallowdamage'))
                        elif desc.endswith('%pacifydamage'):
                            self.accessory_data['pacify_damage'] = int(desc.removesuffix('%pacifydamage'))
                        elif desc.endswith('%airresistance'):
                            self.accessory_data['air_res'] = int(desc.removesuffix('%airresistance'))
                        elif desc.endswith('%domainsize'):
                            self.accessory_data['domain_size'] = int(desc.removesuffix('%domainsize'))
                        elif desc.endswith('%karmareduce'):
                            self.accessory_data['karma_reduce'] = int(desc.removesuffix('%karmareduce'))
                        elif desc.endswith('%pacifytime'):
                            self.accessory_data['pacify_time'] = int(desc.removesuffix('%pacifytime'))
                        elif desc.endswith('/secmentalityregeneration'):
                            self.accessory_data['mentality_regen'] = float(desc.removesuffix('/secmentalityregeneration'))
                        elif desc.endswith('%poisondamagereceived'):
                            self.accessory_data['poison_res'] = float(desc.removesuffix('%poisondamagereceived'))
                        elif desc.endswith('splint'):
                            self.accessory_data['splint'] = int(desc.removesuffix('splint'))
                        elif desc.endswith('%splintcooldown'):
                            self.accessory_data['splint_cd'] = int(desc.removesuffix('%splintcooldown'))
                        elif desc.endswith('additionalmaximummana'):
                            self.accessory_data['max_mana'] = int(desc.removesuffix('additionalmaximummana'))
                        elif desc.endswith('additionalmaximuminspiration'):
                            self.accessory_data['max_ins'] = int(desc.removesuffix('additionalmaximuminspiration'))
                        elif desc.endswith('grenadescattering'):
                            self.accessory_data['grenade_scat'] = 1
                        elif desc.endswith('spoetbonustime'):
                            self.accessory_data['gain_duration'] = int(desc.removesuffix('spoetbonustime'))
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

            if TAGS['magic_weapon'] in self.tags or TAGS['priest_weapon'] in self.tags or TAGS['priest_healer'] in self.tags:
                weapon: weapons.MagicWeapon = weapons.WEAPONS[self.id]
                d = f"{[t.value.upper() for t in self.tags if t.name.startswith('magic_element_')][0]} "\
                    f"{[t.value for t in self.tags if t.name.startswith('magic_lv_')][0]}: {weapon.spell_name}"
                d = f"{weapon.mana_cost} mana cost\n" + d
            if TAGS['arcane_weapon'] in self.tags:
                weapon = weapons.WEAPONS[self.id]
                d = f"{weapon.talent_cost} talent cost\n" + d
                if weapon.mana_cost:
                    d = f"{weapon.mana_cost} mana cost\n" + d
            if TAGS['poet_weapon'] in self.tags:
                weapon: weapons.PoetWeapon = weapons.WEAPONS[self.id]
                for gain in weapon.gains:
                    e = gain(5, 5)
                    d = f"{e.NAME}\n" + d
                d = f"Gain ally with the following effect:\n" + d
                d = f"Get back {int(weapon.back_rate * 100)}% of the inspiration cost\n" + d
                d = f"When first hit," + d
                d = f"{weapon.mana_cost} mana cost\n" + d
                d = f"{weapon.inspiration_cost} inspiration cost\n" + d
            if TAGS['bow'] in self.tags or TAGS['gun'] in self.tags:
                weapon = weapons.WEAPONS[self.id]
                d = f"{weapon.spd} projectile speed\n" + d
                try:
                    d = f"{int(getattr(weapon, 'ammo_save_chance') * 100)}% chance to save ammo\n" + d
                except AttributeError:
                    print(weapon.name, "has no ammo save chance attribute")
            if TAGS['priest_weapon'] in self.tags:
                weapon: weapons.PriestWeapon = weapons.WEAPONS[self.id]
                d = f"Damage up to {weapon.max_mult}x for enough good karma\n" + d
            if TAGS['priest_healer'] in self.tags:
                healer: weapons.PriestHealer = weapons.WEAPONS[self.id]
                d = f"Increase good karma by {healer.karma_gain}/maximum {healer.karma_gain * 30 // (healer.at_time + healer.cd + 1)}\n" + d
                d = f"Heals {healer.amount} HP\n" + d
            if TAGS['weapon'] in self.tags:
                weapon = weapons.WEAPONS[self.id]
                d = f"{round(100 / (weapon.at_time + weapon.cd + 1), 1)}% speed\n" + d
                d = f"{weapon.knock_back} knockback\n" + d
                for dmg, val in weapon.damages.items():
                    dt = 'damage'
                    _dmg = (val * game.get_game().player.calculate_damage() *
                            game.get_game().player.calculate_data('damage', rate_data=True, rate_multiply=True))
                    if TAGS['magic_weapon'] in self.tags:
                        _dmg *= game.get_game().player.attacks[2]
                    elif TAGS['poet_weapon'] in self.tags:
                        _dmg *= game.get_game().player.attacks[3]
                    elif TAGS['priest_weapon'] in self.tags or TAGS['priest_healer'] in self.tags:
                        _dmg *= game.get_game().player.attacks[4]
                    elif TAGS['bow'] in self.tags or TAGS['gun'] in self.tags:
                        _dmg *= game.get_game().player.attacks[1]
                    elif TAGS['pickaxe'] in self.tags:
                        dt = ''
                        _dmg = val
                    else:
                        _dmg *= game.get_game().player.attacks[0]
                    d = f"{int(_dmg)} {damages.NAMES[dmg]} {dt}\n" + d
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
    'melee_weapon': Inventory.Item.Tag('melee_weapon','melee_weapon'),
    'magic_weapon': Inventory.Item.Tag('magic_weapon', 'magic_weapon'),
    'poet_weapon': Inventory.Item.Tag('poet_weapon', 'poet_weapon'),
    'hypnotist_weapon': Inventory.Item.Tag('hypnotist_weapon', 'hypnotist_weapon'),
    'arcane_weapon': Inventory.Item.Tag('arcane_weapon', 'arcane_weapon'),
    'priest_healer': Inventory.Item.Tag('priest_healer', 'priest_healer'),
    'priest_weapon': Inventory.Item.Tag('priest_weapon', 'priest_weapon'),
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
    'pickaxe': Inventory.Item.Tag('pickaxe', 'pickaxe'),
    'see': Inventory.Item.Tag('see', 'see'),
    'see2': Inventory.Item.Tag('see2', 'see2'),

    'head': Inventory.Item.Tag('head', 'head'),
    'body': Inventory.Item.Tag('body', 'body'),
    'leg': Inventory.Item.Tag('leg', 'leg'),

    'ce_item': Inventory.Item.Tag('ce_item', 'ce_item'),

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
    'magic_element_hallow': Inventory.Item.Tag('magic_element_hallow', 'hallow magic'),

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

    'star': Inventory.Item('Star', 'It suppose to recover you 40 mp.', 'star', 0, [TAGS['item']]),

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

    'obsidian_ingot': Inventory.Item('Obsidian Ingot', 'Unbelievable toughness.', 'obsidian_ingot', 1, [TAGS['item']]),
    'floatstone': Inventory.Item('Floatstone', 'A stone that floats.', 'floatstone', 1, [TAGS['item']]),
    'flufffur': Inventory.Item('Flufffur', 'A fluffy fur.', 'flufffur', 1, [TAGS['item']]),
    'starlight_shard': Inventory.Item('Starlight Shard', 'Glowing in the dark.', 'starlight_shard', 4, [TAGS['item']]),

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
    'substance_essence': Inventory.Item('Substance Essence', 'It\'s still here.', 'substance_essence', 9, [TAGS['item']]),
    'light_essence': Inventory.Item('Light Essence', 'A spark of light.', 'light_essence', 9, [TAGS['item']]),
    'scorch_core': Inventory.Item('Scorch Core', 'Controller of Temperature', 'scorch_core', 9, [TAGS['item']]),
    'curse_core': Inventory.Item('Curse Core', 'Controller of Demon', 'curse_core', 9, [TAGS['item']]),
    'my_soul': Inventory.Item('MY Soul', 'MY soul, MY will.\nYou cannot be improved then.', 'my_soul', 9, [TAGS['item'], TAGS['workstation']]),
    'reason': Inventory.Item('Reason', 'Where it starts.', 'reason', 10, [TAGS['item']]),
    'result': Inventory.Item('Result', 'How it ends.', 'result', 10, [TAGS['item']]),
    'the_final_ingot': Inventory.Item('The Final Ingot',
                                      'Looks rainbow in color, glows with the power of cause and effect.', 'the_final_ingot', 11, [TAGS['item']]),
    'the_final_soul': Inventory.Item('The Final Soul', 'Your finale of THIS journey.\nThe power better than everything.', 'the_final_soul', 12, [TAGS['item']]),
    'murders_knife': Inventory.Item('Murder\'s Knife', 'Deal physical damage of 10% maximum hp\nIt means of a start of a genocide.', 'murders_knife', 13, [TAGS['item'], TAGS['weapon']]),
    'savior': Inventory.Item('Savior', 'Make a shield of 100% maximum hp\nIt means a start of pacifier', 'savior', 13, [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                                                                         TAGS['arcane_weapon'], TAGS['magic_lv_primal_magic'], TAGS['magic_element_time']]),

    'wooden_pickaxe': Inventory.Item('Wooden Pickaxe', 'Able to mine a few ore.', 'wooden_pickaxe', 1, [TAGS['item'], TAGS['weapon'], TAGS['pickaxe']]),
    'copper_pickaxe': Inventory.Item('Copper Pickaxe', 'Able to mine metal ores.', 'copper_pickaxe', 1, [TAGS['item'], TAGS['weapon'], TAGS['pickaxe']]),
    'heavy_pickaxe': Inventory.Item('Heavy Pickaxe', 'Able to mine platinum ore.', 'heavy_pickaxe', 1, [TAGS['item'], TAGS['weapon'], TAGS['pickaxe']]),
    'platinum_pickaxe': Inventory.Item('Platinum Pickaxe', 'Able to mine some ore.', 'platinum_pickaxe', 1, [TAGS['item'], TAGS['weapon'], TAGS['pickaxe']]),
    'bloody_pickaxe': Inventory.Item('Bloody Pickaxe', 'Able to mine firite ore.', 'bloody_pickaxe', 2, [TAGS['item'], TAGS['weapon'], TAGS['pickaxe']]),
    'firite_pickaxe': Inventory.Item('Firite Pickaxe', 'Able to mine mystery ore.', 'firite_pickaxe', 2, [TAGS['item'], TAGS['weapon'], TAGS['pickaxe']]),
    'mystery_pickaxe': Inventory.Item('Mystery Pickaxe', 'Able to mine ore.', 'mystery_pickaxe', 3, [TAGS['item'], TAGS['weapon'], TAGS['pickaxe']]),
    'spiritual_pickaxe': Inventory.Item('Spiritual Pickaxe', 'Able to destroy the evil mark.', 'spiritual_pickaxe', 4, [TAGS['item'], TAGS['weapon'], TAGS['pickaxe']]),
    'evil_pickaxe': Inventory.Item('Evil Pickaxe', 'Able to destroy the new metal ores.', 'evil_pickaxe', 5, [TAGS['item'], TAGS['weapon'], TAGS['pickaxe']]),
    'tough_pickaxe': Inventory.Item('Tough Pickaxe', 'Able to mine talent ore.', 'tough_pickaxe', 5, [TAGS['item'], TAGS['weapon'], TAGS['pickaxe']]),
    'true_pickaxe': Inventory.Item('True Pickaxe', 'Able to mine chlorophyte ore.', 'true_pickaxe', 6, [TAGS['item'], TAGS['weapon'], TAGS['pickaxe']]),
    'light_pickaxe': Inventory.Item('Light Pickaxe', 'What is it used for?', 'light_pickaxe', 6, [TAGS['item'], TAGS['weapon'], TAGS['pickaxe']]),
    'destruct_thoughts': Inventory.Item('Destruct Thoughts', 'I think, I do.', 'destruct_thoughts', 10,
                                        [TAGS['item'], TAGS['weapon'], TAGS['pickaxe']]),

    'suspicious_substance': Inventory.Item('Suspicious Substance', '', 'suspicious_substance', 9, [TAGS['item']]),

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
    'substance_fountain': Inventory.Item('Substance Fountain', 'Origin of matters.', 'substance_fountain', 9, [TAGS['item'], TAGS['workstation']]),
    'celestial_fountain': Inventory.Item('Celestial Fountain', 'Origin of the stars.', 'celestial_fountain', 9, [TAGS['item'], TAGS['workstation']]),
    'death_fountain': Inventory.Item('Death Fountain', 'Death isn\'t the end of anything.', 'death_fountain', 11, [TAGS['item'], TAGS['workstation']]),
    'no_fountain': Inventory.Item('No Fountain', 'Fountain not found(bushi', 'no_fountain', 11, [TAGS['item'], TAGS['workstation']]),

    'wooden_sword': Inventory.Item('Wooden Sword', '', 'wooden_sword', 0, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'copper_sword': Inventory.Item('Copper Sword', '', 'copper_sword', 0, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'iron_sword': Inventory.Item('Iron Sword', '', 'iron_sword', 0, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'iron_blade': Inventory.Item('Iron Blade', '', 'iron_blade', 0, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'steel_sword': Inventory.Item('Steel Sword', '', 'steel_sword', 0, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'platinum_sword': Inventory.Item('Platinum Sword', '', 'platinum_sword', 1, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'platinum_blade': Inventory.Item('Platinum Blade', '', 'platinum_blade', 1, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'life_wooden_sword': Inventory.Item('Life Wooden Sword', '', 'life_wooden_sword', 2, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'magic_sword': Inventory.Item('Magic Sword', '', 'magic_sword', 2, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'magic_blade': Inventory.Item('Magic Blade', '', 'magic_blade', 2, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'bloody_sword': Inventory.Item('Bloody Sword', 'When sweeping, press Q to sprint.', 'bloody_sword', 2,
                                   [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'volcano': Inventory.Item('Volcano', 'Gives target to fire.', 'volcano', 2, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'obsidian_sword': Inventory.Item('Obsidian Sword', '', 'obsidian_sword', 2, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'swwwword': Inventory.Item('Swwwword', '', 'swwwword', 2, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'sand_sword': Inventory.Item('Sand Sword', 'When sweeping, press Q to sprint.', 'sand_sword', 2,
                                 [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'doctor_expeller': Inventory.Item('Doctor Expeller', 'Daily apple, daily non-doctor.', 'doctor_expeller', 3,
                                       [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'nights_edge': Inventory.Item('Night\'s Edge', 'The sunset has gone, it now night...', 'nights_edge', 4,
                                  [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'storm_swift_sword': Inventory.Item('Storm Swift Sword', 'Press Q to sprint.\n0 mana cost', 'storm_swift_sword', 4,
                                          [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'spiritual_stabber': Inventory.Item('Spiritual Stabber', '\n\'Destroy the mark to enhance\'', 'spiritual_stabber',
                                        4, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'rune_blade': Inventory.Item('Rune Blade', '', 'rune_blade', 4, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'palladium_sword': Inventory.Item('Palladium Sword', '', 'palladium_sword', 5, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'mithrill_sword': Inventory.Item('Mithrill Sword', '', 'mithrill_sword', 5, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'titanium_sword': Inventory.Item('Titanium Sword', '', 'titanium_sword', 5, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'balanced_stabber': Inventory.Item('Balanced Stabber',
                                       'The power of the evil and the hallow are balanced.\n\n\'Make it under the hallow to enhance\'',
                                       'balanced_stabber', 5, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'excalibur': Inventory.Item('Excalibur', 'The legendary sword of hallow.', 'excalibur', 6,
                                [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'true_excalibur': Inventory.Item('True Excalibur', 'Inviolable hallow.', 'true_excalibur', 7,
                                     [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'wooden_club': Inventory.Item('Wooden Club', '', 'wooden_club', 6, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'remote_sword': Inventory.Item('Remote Sword', '', 'remote_sword', 6,
                                    [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'true_nights_edge': Inventory.Item('True Night\'s Edge', 'Inviolable dark.', 'true_nights_edge', 7,
                                       [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'muramasa': Inventory.Item('Muramasa', 'Ghost\'s blade.', 'muramasa', 7, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'perseverance_sword': Inventory.Item('Perseverance Sword', 'Ignore the distance.', 'perseverance_sword', 6,
                                         [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'black_hole_sword': Inventory.Item('The Black Hole Sword', 'Attracts enemies.', 'black_hole_sword', 6,
                                       [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'life_devourer': Inventory.Item('Life Devourer', 'Cuts lifeless lines.', 'life_devourer', 7,
                                    [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'jevil_knife': Inventory.Item('Jevil Knife', 'Full in chaos', 'jevil_knife', 7,
                                   [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'wilson_knife': Inventory.Item('Wilson Knife', 'Designed by wilson', 'wilson_knife', 8,
                                   [TAGS['item'], TAGS['weapon'],  TAGS['melee_weapon']]),
    'the_blade': Inventory.Item('The Blade', 'The mighty of this blade is not necessary to say.',
                                'the_blade', 8, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'demon_blade__muramasa': Inventory.Item('Demon Blade: Muramasa', 'The terror of this blade is not necessary to say.',
                                             'demon_blade__muramasa', 8, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'uncanny_valley': Inventory.Item('Uncanny Valley', 'Closer, scarier.', 'uncanny_valley', 9,
                                      [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'hour_hand': Inventory.Item('Hour Hand', 'A spin, a time.', 'hour_hand', 9,
                                 [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'quark_rusher': Inventory.Item('Quark Rusher', 'The power of the quarks is unlimited.', 'quark_rusher', 9,
                                   [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),

    'spikeflower': Inventory.Item('Spikeflower', '', 'spikeflower', 0,
                                  [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'spear': Inventory.Item('Spear', '', 'spear', 0, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'platinum_spear': Inventory.Item('Platinum Spear', '', 'platinum_spear', 1, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'fur_spear': Inventory.Item('Fur Spear', 'Shoots several fur, each dealing 8% damage.', 'fur_spear', 2, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'blood_pike': Inventory.Item('Blood Pike', '', 'blood_pike', 2, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'firite_spear': Inventory.Item('Firite Spear', '', 'firite_spear', 2, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'nights_pike': Inventory.Item('Night\'s Pike', 'The sunset has gone, it now night...', 'nights_pike', 4,
                                  [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'energy_spear': Inventory.Item('Energy Spear', 'Contained unparalleled energy.', 'energy_spear', 6,
                                   [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'millennium_persists': Inventory.Item('Millennium Persists', 'Thousands of years non-stopping.',
                                          'millennium_persists', 7, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'metal_hand': Inventory.Item('Metal Hand', 'A stab with time passing.', 'metal_hand', 9,
                                  [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'deconstruction': Inventory.Item('Deconstruction', 'When it is constructed.', 'deconstruction', 9,
                                     [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'starfury': Inventory.Item('Starfury', 'The anger from the starry sky.', 'starfury', 9,
                                [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'lysis': Inventory.Item('Lysis', 'Unbelievable explosion.', 'lysis', 9, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'star_wrath': Inventory.Item('Star Wrath', 'The wingdings from the starry sky.', 'star_wrath', 9,
                                  [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'galaxy_broadsword': Inventory.Item('Galaxy Broadsword', 'Bring this sword to mastery the galaxy.', 'galaxy_broadsword', 11,
                                          [TAGS['item'], TAGS['weapon'], TAGS['ce_item'], TAGS['melee_weapon']]),
    'eternal_echo': Inventory.Item('Eternal Echo', 'The galaxy\'s fallen to an end, remaining endless echo.', 'eternal_echo', 12,
                                   [TAGS['item'], TAGS['weapon'], TAGS['ce_item'], TAGS['melee_weapon']]),
    'star_of_devotion': Inventory.Item('Star of Devotion', 'Under the star, is all in faith.', 'star_of_devotion', 12,
                                        [TAGS['item'], TAGS['weapon'], TAGS['ce_item'], TAGS['melee_weapon']]),
    'highlight': Inventory.Item('Highlight', 'The unforgettable moment.', 'highlight', 11,
                                 [TAGS['item'], TAGS['weapon'], TAGS['ce_item'], TAGS['melee_weapon']]),
    'turning_point': Inventory.Item('Turning Point', 'The conflict will happen.', 'turning_point', 11,
                                     [TAGS['item'], TAGS['weapon'], TAGS['ce_item'], TAGS['melee_weapon']]),

    'zenith': Inventory.Item('Zenith', 'Where the sky is.', 'zenith', 12,
                             [TAGS['item'], TAGS['weapon'], TAGS['ce_item'], TAGS['melee_weapon']]),

    'arrow_thrower': Inventory.Item('Arrow Thrower', '', 'arrow_thrower', 0,
                                    [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'bow': Inventory.Item('Bow', '', 'bow', 0, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'copper_bow': Inventory.Item('Copper Bow', '', 'copper_bow', 0, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'iron_bow': Inventory.Item('Iron Bow', '', 'iron_bow', 0, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'steel_bow': Inventory.Item('Steel Bow', '', 'steel_bow', 0, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'platinum_bow': Inventory.Item('Platinum Bow', '', 'platinum_bow', 1, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'bloody_bow': Inventory.Item('Bloody Bow', '', 'bloody_bow', 2, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'forests_bow': Inventory.Item('Forest\'s Bow', '', 'forests_bow', 2, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'kuangkuangkuang': Inventory.Item('Kuangkuangkuang', 'Sometimes you cannot handle this.', 'kuangkuangkuang', 2, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
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
    'resolution': Inventory.Item('Resolution', 'The bow is solved.', 'resolution', 11,
                                  [TAGS['item'], TAGS['weapon'], TAGS['bow'], TAGS['ce_item']]),

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
    'dark_exploder': Inventory.Item('Dark Exploder', '', 'dark_exploder', 5,
                                     [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'true_shadow': Inventory.Item('True Shadow', 'Not the others, \'Pong! Nobody left.\'', 'true_shadow', 7,
                                  [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'shotgun': Inventory.Item('Shotgun', 'Why a ranger should stand close?\nShoot three times.', 'shotgun', 6, [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'justice_shotgun': Inventory.Item('Justice Shotgun', 'Stand closer?', 'justice_shotgun', 7,
                                       [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'climax': Inventory.Item('Climax', 'When it reaches the highest point, everyone is surprised! Everyone is dead.', 'climax', 11,
                             [TAGS['item'], TAGS['weapon'], TAGS['gun'], TAGS['ce_item']]),

    'lazer_gun': Inventory.Item('Lazer Gun', '', 'lazer_gun', 7,
                                [TAGS['item'], TAGS['weapon'], TAGS['gun'], TAGS['lazer_gun']]),
    'lazer_sniper': Inventory.Item('Lazer Sniper', '', 'lazer_sniper', 7,
                                   [TAGS['item'], TAGS['weapon'], TAGS['gun'], TAGS['lazer_gun']]),
    'matter_disintegrator': Inventory.Item('Matter Disintegrator', 'Matter came, matter gone.', 'matter_disintegrator', 9,
                                            [TAGS['item'], TAGS['weapon'], TAGS['gun'], TAGS['lazer_gun']]),

    'rocket_launcher': Inventory.Item('Rocket Launcher', '', 'rocket_launcher', 2,
                                      [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'rapid_rocket_launcher': Inventory.Item('Rapid Rocket Launcher', '', 'rapid_rocket_launcher', 4,
                                            [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'rocket_launcher_v2': Inventory.Item('Rocket Launcher v2.0', '', 'rocket_launcher_v2', 5,
                                          [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'rapid_rocket_launcher_v2': Inventory.Item('Rapid Rocket Launcher v2.0', '', 'rapid_rocket_launcher_v2', 5,
                                                [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'rocket_launcher_v3': Inventory.Item('Rocket Launcher v3.0', '', 'rocket_launcher_v3', 7,
                                          [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'rapid_rocket_launcher_v3': Inventory.Item('Rapid Rocket Launcher v3.0', '', 'rapid_rocket_launcher_v3', 8,
                                                [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'rocket_launcher_v4': Inventory.Item('Rocket Launcher v4.0', '', 'rocket_launcher_v4', 10,
                                          [TAGS['item'], TAGS['weapon'], TAGS['gun']]),
    'rapid_rocket_launcher_max': Inventory.Item('Rapid Rocket Launcher v4.0 pro max', '', 'rapid_rocket_launcher_max', 12,
                                                [TAGS['item'], TAGS['weapon'], TAGS['gun']]),

    'copper_knife': Inventory.Item('Copper Knife', '', 'copper_knife', 0,
                                   [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'dagger': Inventory.Item('Dagger', '', 'dagger', 1, [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'platinum_doubleknife': Inventory.Item('Platinum Double Knife', '', 'platinum_doubleknife', 2,
                                            [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'obsidian_knife': Inventory.Item('Obsidian Knife', '', 'obsidian_knife', 2, [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'twilight_shortsword': Inventory.Item('Twilight Shortsword', '', 'twilight_shortsword', 2,
                                           [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'bloody_shortsword': Inventory.Item('Bloody Shortsword', '', 'bloody_shortsword', 3,
                                          [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'dawn_shortsword': Inventory.Item('Dawn Shortsword', '', 'dawn_shortsword', 3,
                                       [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'apple_knife': Inventory.Item('Apple Knife', 'Explode to pieces in air.', 'apple_knife', 3, [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
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

    'shuriken': Inventory.Item('Shuriken', '', 'shuriken', 0, [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'spikeball': Inventory.Item('Spikeball', '', 'spikeball', 6, [TAGS['item'], TAGS['weapon'], TAGS['knife']]),

    'grenade': Inventory.Item('Grenade', '', 'grenade', 2, [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'jade_grenade': Inventory.Item('Jade Grenade', '', 'jade_grenade', 4, [TAGS['item'], TAGS['weapon'], TAGS['knife']]),
    'grenade_kings_jade_mask': Inventory.Item('Grenade King\'s Jade Mask', 'The jade-masked grenade king.\nHalf the damage range of grenades\nEnable grenade scattering', 'grenade_kings_jade_mask', 4,
                                               [TAGS['item'], TAGS['accessory']]),

    'arrow': Inventory.Item('Arrow', '', 'arrow', 0, [TAGS['item'], TAGS['ammo'], TAGS['ammo_arrow']]),
    'coniferous_leaf': Inventory.Item('Coniferous Leaf', '', 'coniferous_leaf', 0,
                                      [TAGS['item'], TAGS['ammo'], TAGS['ammo_arrow']]),
    'magic_arrow': Inventory.Item('Magic Arrow', '', 'magic_arrow', 1,
                                  [TAGS['item'], TAGS['ammo'], TAGS['ammo_arrow']]),
    'snowball': Inventory.Item('Snowball', 'You probably even cannot see it.', 'snowball',
                               1, [TAGS['item'], TAGS['ammo'], TAGS['ammo_bullet']]),
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
    'scorching_arrow': Inventory.Item('Scorching Arrow', '', 'scorching_arrow', 10,
                                       [TAGS['item'], TAGS['ammo'], TAGS['ammo_arrow']]),
    'seperator': Inventory.Item('Seperator', '', 'seperator', 10, [TAGS['item'], TAGS['ammo'], TAGS['ammo_bullet']]),

    'glowing_splint': Inventory.Item('Glowing Splint', 'Shoots glows.', 'glowing_splint', 0,
                                     [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                      TAGS['magic_element_fire'], TAGS['magic_lv_1']]),
    'copper_wand': Inventory.Item('Copper Wand', 'Shoots copper bomb.', 'copper_wand', 0,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_air'],
                                   TAGS['magic_lv_1']]),
    'iron_wand': Inventory.Item('Iron Wand', 'Shoots iron bomb.', 'iron_wand', 0,
                                [TAGS['item'],  TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_air'],
                                 TAGS['magic_lv_1']]),
    'cactus_wand': Inventory.Item('Cactus Wand', 'Shoots a unmoved cactus on the ground.', 'cactus_wand', 1,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                   TAGS['magic_lv_1']]),
    'watcher_wand': Inventory.Item('Watcher Wand', 'Shoots a short lazer.', 'watcher_wand', 1,
                                   [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_light'],
                                    TAGS['magic_lv_1']]),
    'platinum_wand': Inventory.Item('Platinum Wand', 'Shoots a energy pulse.', 'platinum_wand', 1,
                                    [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                     TAGS['magic_element_energy'], TAGS['magic_lv_1']]),
    'life_wooden_wand': Inventory.Item('Life-Wooden Wand', 'Shoots a medium-sized beam.', 'life_wooden_wand', 2,
                                        [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_earth'],
                                         TAGS['magic_lv_1']]),
    'burning_book': Inventory.Item('Burning Book', 'Shoots fire pulse to burns enemies.', 'burning_book', 2,
                                   [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_fire'],
                                     TAGS['magic_lv_2']]),
    'talent_book': Inventory.Item('Talent Book', 'Shoots smart bomb trace for enemies.', 'talent_book', 2,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_light'],
                                   TAGS['magic_lv_2']]),
    'blood_wand': Inventory.Item('Blood Wand', 'Shoots a blood bomb.', 'blood_wand', 2,
                                 [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                   TAGS['magic_lv_2']]),
    'fireball_magic': Inventory.Item('Fireball Magic(Genuine)', 'Shoots a fireball.', 'fireball_magic', 3,
                                     [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_fire'],
                                      TAGS['magic_lv_4']]),
    'obsidian_wand': Inventory.Item('Obsidian Wand', 'Shoots a obsidian bomb.', 'obsidian_wand', 3,
                                     [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_earth'],
                                      TAGS['magic_lv_2']]),
    'ice_shard': Inventory.Item('Ice Shard', 'Shoots pieces of ice shards.', 'ice_shard', 2,
                                 [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_water'],
                                  TAGS['magic_lv_2']]),
    'hematology': Inventory.Item('Hematology', 'Recovers 30 HP.', 'hematology', 3,
                                 [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                   TAGS['magic_lv_3']]),
    'fire_magic_sword': Inventory.Item('Fire Magic Sword', 'Attack using a enormous sword.', 'fire_magic_sword', 3,
                                       [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_fire'],
                                        TAGS['magic_lv_3']]),
    'fruit_wand': Inventory.Item('Fruit Wand', 'Makes apple fall from the sky.', 'fruit_wand', 3,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                   TAGS['magic_lv_3']]),
    'rock_wand': Inventory.Item('Rock Wand', 'Shoots a rock bomb.', 'rock_wand', 3,
                                [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_earth'],
                                 TAGS['magic_lv_3']]),
    'tornado': Inventory.Item('Tornado', 'Pops out enemy nearby.', 'tornado', 3,
                               [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_air'],
                                TAGS['magic_lv_3']]),
    'midnights_wand': Inventory.Item('Midnight\'s Wand', 'All darkness...\nShoots several night energy.', 'midnights_wand', 4,
                                     [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_dark'],
                                      TAGS['magic_lv_4']]),
    'spiritual_destroyer': Inventory.Item('Spiritual Destroyer', 'Shoots a stronger energy pulse.\n\'Destroy the mark to enhance\'',
                                          'spiritual_destroyer', 4,
                                          [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                           TAGS['magic_element_energy'], TAGS['magic_lv_4']]),
    'evil_book': Inventory.Item('Evil Book', 'Shoots a dark pulse.\nFull of corruption\n\n\'Change to enhance\'', 'evil_book', 5,
                                [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_death'],
                                  TAGS['magic_lv_4']]),
    'blood_sacrifice': Inventory.Item('Blood Sacrifice', 'Shoots a blood beam.\n24 HP Cost.',
                                       'blood_sacrifice', 5,
                                       [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_death'],
                                        TAGS['magic_lv_5']]),
    'blade_wand': Inventory.Item('Blade Wand', 'Shoots wind blades.', 'blade_wand', 5,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_air'],
                                   TAGS['magic_lv_5']]),
    'water_of_disability': Inventory.Item('Water of Disability', 'Shoots a water beam decreasing enemies\' defense by 8, can be effected for 10 times.',
                                           'water_of_disability', 5,
                                           [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_water'],
                                            TAGS['magic_lv_5']]),
    'curse_book': Inventory.Item('Curse Book', 'Summon a dark magic circle.\nCurse...', 'curse_book', 6,
                                 [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_dark'],
                                   TAGS['magic_lv_4']]),
    'shield_wand': Inventory.Item('Shield Wand', 'Summon a magic circle and protect the player in a few seconds.\n+1145114 defense\n-100% speed', 'shield_wand', 6,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_water'],
                                    TAGS['magic_lv_4']]),
    'gravity_wand': Inventory.Item('Gravity Wand', 'Summon a magic circle that simulates gravity.', 'gravity_wand', 6,
                                   [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_earth'],
                                     TAGS['magic_lv_3']]),
    'double_watcher_wand': Inventory.Item('Double Watcher Wand', 'Summon two lazer beams in different positions.', 'double_watcher_wand', 6,
                                           [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                            TAGS['magic_element_light'], TAGS['magic_element_fire'], TAGS['magic_lv_4']]),
    'forbidden_curse__spirit': Inventory.Item('Forbidden Curse: Spirit', 'Shoots a magic circle.', 'forbidden_curse__spirit', 7,
                                              [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                               TAGS['arcane_weapon'], TAGS['magic_element_energy'],
                                               TAGS['magic_lv_forbidden_curse']]),
    'forbidden_curse__evil': Inventory.Item('Forbidden Curse: Evil', 'Shoots a strong evil pulse.', 'forbidden_curse__evil', 7,
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
    'light_purify': Inventory.Item('Light Purify', 'Summon a magic circle that purify enemies.', 'light_purify', 7,
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
    'chaos_killer': Inventory.Item('Chaos Killer', 'Kills all enemies.', 'chaos_killer', 8,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_space'],
                                   TAGS['magic_lv_4']]),
    'skyfire__meteor': Inventory.Item('Skyfire: Meteor', 'Summon a destructive meteor.', 'skyfire__meteor', 8,
                                       [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_fire'],
                                        TAGS['magic_lv_7']]),
    'azure_guard': Inventory.Item('Azure Guard', 'Adds a 100HP shield', 'azure_guard', 8,
                                   [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_water'],
                                    TAGS['magic_lv_7']]),
    'storm': Inventory.Item('Storm', 'Summon a tornado which appeal and damage enemies.', 'storm', 8,
                            [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_air'],
                             TAGS['magic_lv_7']]),
    'earth_wall': Inventory.Item('Earth Wall', 'Summon several trees on earth to sometimes block attacks.', 'earth_wall', 8,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_earth'],
                                   TAGS['magic_lv_7']]),
    'lifebringer': Inventory.Item('Lifebringer', 'Heal 120HP/sec.', 'lifebringer', 8,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                   TAGS['magic_lv_7']]),
    'target_dummy': Inventory.Item('Target Dummy', 'Summon a dummy that some enemies can attack.', 'target_dummy', 8,
                                    [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_life'],
                                     TAGS['magic_lv_7']]),
    'judgement_light': Inventory.Item('Judgement Light', 'Summon a circle that restrict the enemy in it and then deal great damage.', 'judgement_light', 8,
                                       [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_light'],
                                        TAGS['magic_lv_7']]),
    'dark_restrict': Inventory.Item('Dark Restrict', 'Restrict the enemy in circle for a few seconds.', 'dark_restrict', 8,
                                     [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_dark'],
                                      TAGS['magic_lv_7']]),
    'great_forbidden_curse__fire': Inventory.Item('Great Forbidden Curse: Fire', 'Summon the fire seraph to damage a large area of enemies.', 'great_forbidden_curse__fire', 8,
                                             [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                              TAGS['arcane_weapon'], TAGS['magic_element_fire'],
                                               TAGS['magic_lv_forbidden_curse']]),
    'great_forbidden_curse__light': Inventory.Item('Great Forbidden Curse: Light', 'Summon 6 beams and deal larger damage when then coincide.', 'great_forbidden_curse__light', 8,
                                                   [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                                    TAGS['arcane_weapon'], TAGS['magic_element_light'],
                                                     TAGS['magic_lv_forbidden_curse']]),
    'great_forbidden_curse__water': Inventory.Item('Great Forbidden Curse: Water', 'Summon a acid rain.', 'great_forbidden_curse__water', 8,
                                                    [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                                     TAGS['arcane_weapon'], TAGS['magic_element_water'],
                                                      TAGS['magic_lv_forbidden_curse']]),
    'death_note': Inventory.Item('Great Forbidden Curse: Death', 'Deal great damage to an enemy.\nWrite down it, then erase it.', 'death_note', 8,
                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_death'],
                                   TAGS['magic_lv_forbidden_curse']]),
    'great_forbidden_curse__dark': Inventory.Item('Great Forbidden Curse: Dark', 'Summon a dark magic circle and deal great damage.', 'great_forbidden_curse__dark', 9,
                                                  [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                                   TAGS['arcane_weapon'], TAGS['magic_element_dark'],
                                                    TAGS['magic_lv_forbidden_curse']], specify_img='forbidden_curse__darks_wield'),
    'great_forbidden_curse__evil': Inventory.Item('Great Forbidden Curse: Evil', 'Summon a blood moon to deal damage to all enemies in world, including a chance to kill them.', 'great_forbidden_curse__evil', 9,
                                                   [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'],
                                                     TAGS['arcane_weapon'], TAGS['magic_element_death'],
                                                      TAGS['magic_lv_forbidden_curse']], specify_img='forbidden_curse__blood_moon'),
    'sun_pearl': Inventory.Item('Sun Pearl', 'Summon pearls around you.', 'sun_pearl', 9,
                                 [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_fire'],
                                  TAGS['magic_lv_7']]),
    'stop': Inventory.Item('Stop', 'Stops the time for you.', 'stop', 9,
                            [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_time'],
                             TAGS['magic_lv_5']]),
    'falling_action': Inventory.Item('Falling Action', 'Deal damage to an enemy.', 'falling_action', 11,
                                      [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_space'],
                                       TAGS['magic_lv_5'], TAGS['ce_item']]),
    'rising_action': Inventory.Item('Rising Action', 'Summon 5 strong colourful projectiles.', 'rising_action', 11,
                                     [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_space'],
                                      TAGS['magic_lv_6'], TAGS['ce_item']]),
    'relevation_of_cycles': Inventory.Item('Relevation of Cycles', 'Summon 3 strong projectiles', 'relevation_of_cycles', 11,
                                             [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_time'],
                                              TAGS['magic_lv_7'], TAGS['ce_item']]),

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

    'muse_core': Inventory.Item('Muse Core', 'The core of Art', 'muse_core', 4,
                                 [TAGS['item'], TAGS['workstation']]),
    'note': Inventory.Item('Note', 'The basic unit of music.\n+200 maximum inspiration', 'note', 4,
                            [TAGS['item'], TAGS['workstation']]),

    'gold_fine': Inventory.Item('Golden Fine', 'Shoot a quick sound wave', 'gold_fine', 4,
                                [TAGS['item'], TAGS['weapon'], TAGS['poet_weapon']]),
    'ancient_flute': Inventory.Item('Ancient Flute', 'Rapidly shoot sound waves.', 'ancient_flute', 4,
                                    [TAGS['item'], TAGS['weapon'], TAGS['poet_weapon']]),
    'storm_harp': Inventory.Item('Storm Harp', 'Continuously shoot sound waves, dealing continuous damage.', 'storm_harp', 5,
                                  [TAGS['item'], TAGS['weapon'], TAGS['poet_weapon']]),
    'snare': Inventory.Item('Snare', 'Deal strong damage to enemy nearby.', 'snare', 5,
                            [TAGS['item'], TAGS['weapon'], TAGS['poet_weapon']]),
    'watcher_bell': Inventory.Item('Watcher Bell', 'Summon ball following the enemy.', 'watcher_bell', 5,
                                    [TAGS['item'], TAGS['weapon'], TAGS['poet_weapon']]),
    'apple_smells_good': Inventory.Item('Apple Smells Good', 'Rapidly shoot sound waves.', 'apple_smells_good', 5,
                                          [TAGS['item'], TAGS['weapon'], TAGS['poet_weapon']]),
    'holy_stormer': Inventory.Item('Holy Stormer', 'Summon a storm of sound waves.', 'holy_stormer', 5,
                                    [TAGS['item'], TAGS['weapon'], TAGS['poet_weapon']]),
    'wither_oboe': Inventory.Item('Wither Oboe', 'Shoots series of sound waves.', 'wither_oboe', 5,
                                  [TAGS['item'], TAGS['weapon'], TAGS['poet_weapon']]),

    'bible': Inventory.Item('Bible', 'The god says...', 'bible', 4,
                            [TAGS['item'], TAGS['workstation']]),
    'saint_healer': Inventory.Item('Saint Healer', 'Heals ally.', 'saint_healer', 3,
                                   [TAGS['item'], TAGS['weapon'], TAGS['priest_healer'], TAGS['magic_element_hallow'],
                                    TAGS['magic_lv_1']]),
    'holy_shine': Inventory.Item('Holy Shine', 'Summon a holy circle following the enemy.', 'holy_shine', 5,
                                  [TAGS['item'], TAGS['weapon'], TAGS['priest_weapon'], TAGS['magic_element_hallow'],
                                   TAGS['magic_lv_2']]),
    'the_gods_penalty': Inventory.Item('The God\'s Penalty', 'Summon a holy lightning bolt.', 'the_gods_penalty', 5,
                                        [TAGS['item'], TAGS['weapon'], TAGS['priest_weapon'], TAGS['magic_element_hallow'],
                                         TAGS['magic_lv_3']]),
    'great_heal': Inventory.Item('Great Heal', 'Heal continuously.', 'great_heal', 5,
                                  [TAGS['item'], TAGS['weapon'], TAGS['priest_healer'], TAGS['magic_element_hallow'],
                                   TAGS['magic_lv_4']]),
    'the_prayer': Inventory.Item('The Prayer', 'Heals ally.', 'the_prayer', 5,
                                  [TAGS['item'], TAGS['weapon'], TAGS['priest_healer'], TAGS['magic_element_hallow'],
                                   TAGS['magic_lv_2']]),
    'the_true_gods_penalty': Inventory.Item('The True God\'s Penalty', 'Summon a continous holy lightning bolt.', 'the_true_gods_penalty', 5,
                                             [TAGS['item'], TAGS['weapon'], TAGS['priest_weapon'], TAGS['magic_element_hallow'],
                                              TAGS['magic_lv_4']]),
    'holy_light': Inventory.Item('Holy Light', 'Summon an area of light, dealing damage.', 'holy_light', 5,
                                 [TAGS['item'], TAGS['weapon'], TAGS['priest_weapon'], TAGS['magic_element_hallow'],
                                              TAGS['magic_lv_5']]),

    'z': Inventory.Item('\'Z\'', 'Z..z..Z..\nThey always say it as they fall asleep.', 'z', 4,
                        [TAGS['item'], TAGS['workstation']]),
    'mystery_watch': Inventory.Item('Mystery Watch', 'Swinging and swinging, and then fall asleep.', 'mystery_watch', 4,
                                    [TAGS['item'], TAGS['weapon'], TAGS['hypnotist_weapon']]),
    'hand_of_pacify': Inventory.Item('Hand of Pacify', 'Pacify the enemy.', 'hand_of_pacify', 4,
                                      [TAGS['item'], TAGS['weapon'], TAGS['hypnotist_weapon']]),
    'sleep_splint': Inventory.Item('Sleep Splint', 'Pacify the enemy.', 'sleep_splint', 4,
                                    [TAGS['item'], TAGS['weapon'], TAGS['hypnotist_weapon']]),
    'sleep_eye': Inventory.Item('Sleep Eye', 'Pacify for a long distance', 'sleep_eye', 5,
                                [TAGS['item'], TAGS['weapon'], TAGS['hypnotist_weapon']]),
    'good_dream': Inventory.Item('Good Dream', 'Anyway, good dream!', 'good_dream', 5,
                                 [TAGS['item'], TAGS['weapon'], TAGS['hypnotist_weapon']]),
    'nightmare': Inventory.Item('Nightmare', 'You cannot leave that.', 'nightmare', 5,
                                [TAGS['item'], TAGS['weapon'], TAGS['hypnotist_weapon']]),

    'colourful_substance': Inventory.Item('Colourful Substance', 'It\'s too good.', 'colourful_substance', 5,
                                          [TAGS['item']]),
    'dark_substance': Inventory.Item('Dark Substance', 'It\'s too evil.', 'dark_substance', 5,
                                     [TAGS['item']]),
    'cold_substance': Inventory.Item('Cold Substance', 'It\'s too cold', 'cold_substance', 5,
                                     [TAGS['item']]),

    'visual_resonancer': Inventory.Item('Visual Resonancer', '+22% ranged damage\n+6% critical\n+200 additional maximum inspiration\n+150 additional maximum mana',
                                        'visual_resonancer', 5, [TAGS['item'], TAGS['accessory']]),
    'strength_resonancer': Inventory.Item('Strength Resonancer', '+14% damage\n+12% melee damage\n+10% critical\n+20% karma reduce\n+36% hallow damage\n+10/sec regeneration',
                                          'strength_resonancer', 5, [TAGS['item'], TAGS['accessory']]),
    'photon_resonancer': Inventory.Item('Photon Resonancer', '+25% magic damage\n+5% critical\n+40/sec mana regeneration\n+50% pacify time\n-15% karma reduce\n-10% damage',
                                        'photon_resonancer', 5, [TAGS['item'], TAGS['accessory']]),
    'hallow_resonancer': Inventory.Item('Hallow Resonancer', '+15% hallow damage\n+10% critical\n-10% karma reduce\n+20 magic defense',
                                         'hallow_resonancer', 7, [TAGS['item'], TAGS['accessory']]),
    'life_resonancer': Inventory.Item('Life Resonancer', '+30/sec regeneration\n+10/sec mentality regeneration\n+5% critical',
                                       'life_resonancer', 5, [TAGS['item'], TAGS['accessory']]),

    'worldsaver_necklace': Inventory.Item('WorldSaver Necklace', 'It can save the world.\n+22% ranged damage\n+6% critical\n+200 additional maximum inspiration\n+500 additional maximum mana\n'
                                                                 '+14% damage\n+18% melee damage\n+45% critical\n-10% karma reduce\n+42% hallow damage\n+40/sec regeneration\n'
                                                                 '+25% magic damage\n+100/sec mana regeneration\n+50% pacify time\n+10/sec mentality regeneration\n+5s poet bonus time',
                                          'worldsaver_necklace', 10, [TAGS['item'], TAGS['accessory']]),

    'wooden_helmet': Inventory.Item('Wooden Helmet', '2 armor', 'wooden_helmet', 0, [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'wooden_mask': Inventory.Item('Wooden Mask', '0 armor\n+1% speed', 'wooden_mask', 0, [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'wooden_chestplate': Inventory.Item('Wooden Chestplate', '1 armor', 'wooden_chestplate', 0, [TAGS['item'], TAGS['accessory'], TAGS['body']]),
    'wooden_greaves': Inventory.Item('Wooden Greaves', '0 armor\n+1% speed', 'wooden_greaves', 0, [TAGS['item'], TAGS['accessory'], TAGS['leg']]),

    'copper_helmet': Inventory.Item('Copper Helmet', '3 armor', 'copper_helmet', 0, [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'copper_mask': Inventory.Item('Copper Mask', '1 armor\n+2% speed', 'copper_mask', 0, [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'copper_chestplate': Inventory.Item('Wooden Chestplate', '4 armor', 'wooden_chestplate', 0, [TAGS['item'], TAGS['accessory'], TAGS['body']]),
    'copper_greaves': Inventory.Item('Copper Greaves', '0 armor\n+3% speed', 'copper_greaves', 0, [TAGS['item'], TAGS['accessory'], TAGS['leg']]),

    'iron_helmet': Inventory.Item('Iron Helmet', '5 armor\n+1% speed', 'iron_helmet', 1, [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'iron_mask': Inventory.Item('Iron Helmet', '1 armor\n+4% speed', 'iron_mask', 1, [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'iron_chestplate': Inventory.Item('Iron Chestplate', '6 armor\n+1% speed', 'iron_chestplate', 1, [TAGS['item'], TAGS['accessory'], TAGS['body']]),
    'iron_greaves': Inventory.Item('Iron Greaves', '2 armor\n+5% speed', 'iron_greaves', 1, [TAGS['item'], TAGS['accessory'], TAGS['leg']]),

    'steel_helmet': Inventory.Item('Steel Helmet', '8 armor\n+2kg', 'steel_helmet', 1, [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'steel_mask': Inventory.Item('Steel Mask', '2 armor\n+1kg', 'steel_mask', 1, [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'steel_chestplate': Inventory.Item('Steel Chestplate', '7 armor\n+4kg', 'steel_chestplate', 1, [TAGS['item'], TAGS['accessory'], TAGS['body']]),
    'steel_greaves': Inventory.Item('Steel Greaves', '4 armor\n+2kg', 'steel_greaves', 1, [TAGS['item'], TAGS['accessory'], TAGS['leg']]),

    'platinum_helmet': Inventory.Item('Platinum Helmet', '9 armor', 'platinum_helmet', 2, [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'platinum_mask': Inventory.Item('Platinum Mask', '4 armor\n-1% air resistance', 'platinum_mask', 2, [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'platinum_chestplate': Inventory.Item('Platinum Chestplate', '8 armor\n-2% air resistance', 'platinum_chestplate', 2, [TAGS['item'], TAGS['accessory'], TAGS['body']]),
    'platinum_greaves': Inventory.Item('Platinum Greaves', '6 armor\n-2% air resistance', 'platinum_greaves', 2, [TAGS['item'], TAGS['accessory'], TAGS['leg']]),

    'bloody_helmet': Inventory.Item('Bloody Helmet', '7 armor', 'bloody_helmet', 2, [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'bloody_mask': Inventory.Item('Bloody Mask', '2 armor\n+2/sec regeneration', 'bloody_mask', 2, [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'bloody_chestplate': Inventory.Item('Bloody Chestplate', '8 armor\n+4/sec regeneration', 'bloody_chestplate', 2, [TAGS['item'], TAGS['accessory'], TAGS['body']]),
    'bloody_greaves': Inventory.Item('Bloody Greaves', '3 armor\n+1/sec regeneration', 'bloody_greaves', 2, [TAGS['item'], TAGS['accessory'], TAGS['leg']]),

    'firy_helmet': Inventory.Item('Firy Helmet', '9 armor\n+8% damage', 'firy_helmet', 2, [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'firy_mask': Inventory.Item('Firy Mask', '4 armor\n+5% damage', 'firy_mask', 2, [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'firy_chestplate': Inventory.Item('Firy Chestplate', '9 armor\n+9% damage', 'firy_chestplate', 2, [TAGS['item'], TAGS['accessory'], TAGS['body']]),
    'firy_greaves': Inventory.Item('Firy Greaves', '5 armor\n+9% damage', 'firy_greaves', 2, [TAGS['item'], TAGS['accessory'], TAGS['leg']]),

    'mysterious_helmet': Inventory.Item('Mysterious Helmet', '12 armor\n+2% critical', 'mysterious_helmet', 3, [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'mysterious_mask': Inventory.Item('Mysterious Mask', '6 armor\n+8% critical', 'mysterious_mask', 3, [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'mysterious_chestplate': Inventory.Item('Mysterious Chestplate', '14 armor\n+9% critical', 'mysterious_chestplate', 3, [TAGS['item'], TAGS['accessory'], TAGS['body']]),
    'mysterious_greaves': Inventory.Item('Mysterious Greaves', '8 armor\n+5% critical', 'mysterious_greaves', 3, [TAGS['item'], TAGS['accessory'], TAGS['leg']]),

    'merged_metal_helmet': Inventory.Item('Merged Metal Helmet', '25 armor\n+15% damage', 'merged_metal_helmet', 5, [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'merged_metal_mask': Inventory.Item('Merged Metal Mask', '16 armor\n+15/sec regeneration', 'merged_metal_mask', 5, [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'merged_metal_headgear': Inventory.Item('Merged Metal Mask', '8 armor\n+20% critical', 'merged_metal_headgear', 5,
                                        [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'merged_metal_chestplate': Inventory.Item('Merged Metal Chestplate', '28 armor\n+20kg', 'merged_metal_chestplate', 5, [TAGS['item'], TAGS['accessory'],
                                                                                   TAGS['body']]),
    'merged_metal_greaves': Inventory.Item('Merged Metal Greaves', '10 armor\n+30% speed', 'merged_metal_greaves', 5, [TAGS['item'], TAGS['accessory'],
                                                                                   TAGS['leg']]),

    'chloro_formal_hat': Inventory.Item('Chloro. Formal Hat', '19 armor\n+10/sec regeneration\n+30/sec mana regeneration', 'chloro_formal_hat',
                                         7, [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'chloro_chestplate': Inventory.Item('Chloro. Chestplate', '35 armor\n+20/sec regeneration\n+50/sec mana regeneration', 'chloro_chestplate', 7,
                                        [TAGS['item'], TAGS['accessory'], TAGS['body']]),
    'chloro_leggings': Inventory.Item('Chloro. Leggings', '13 armor\n+30% speed\n+50/sec mana regeneration', 'chloro_leggings', 7,
                                     [TAGS['item'], TAGS['accessory'], TAGS['leg']]),

    'chaos_hood': Inventory.Item('Chaos Hood', '27 armor\n+15% critical\n+30% speed', 'chaos_hood', 8, [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'chaos_chestplate': Inventory.Item('Chaos Chestplate', '47 armor\n+25% critical\n+50% speed', 'chaos_chestplate', 8,
                                        [TAGS['item'], TAGS['accessory'], TAGS['body']]),
    'chaos_leggings': Inventory.Item('Chaos Leggings', '22 armor\n+40% speed\n+100/sec mana regeneration', 'chaos_leggings', 8,
                                      [TAGS['item'], TAGS['accessory'], TAGS['leg']]),

    'godkiller_helmet': Inventory.Item('Godkiller Helmet', '38 armor\n+20% damage\n+20% critical\n+20% speed', 'godkiller_helmet', 9,
                                        [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'godkiller_chestplate': Inventory.Item('Godkiller Chestplate', '64 armor\n+30% damage\n+30% critical\n+30% speed', 'godkiller_chestplate', 9,
                                            [TAGS['item'], TAGS['accessory'], TAGS['body']]),
    'godkiller_leggings': Inventory.Item('Godkiller Leggings', '32 armor\n+15% damage\n+15% critical\n+15% speed', 'godkiller_leggings', 9,
                                         [TAGS['item'], TAGS['accessory'], TAGS['leg']]),

    'karmic_helmet': Inventory.Item('Karmic Helmet', '120 armor\n+15% damage\n+15%critical\n+15% speed\n+15/sec regeneration\n+30/sec mana regeneration\n'
                                                     '+30/sec mentality regeneration\n+15% domain size\n+15% speed\n+150 additonal maximum mana', 'karmic_helmet', 11,
                                        [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'karmic_chestplate': Inventory.Item('Karmic Chestplate', '160 armor\n+20% damage\n+20% critical\n+20% speed\n+20/sec regeneration\n+40/sec mana regeneration\n'
                                                       '+40/sec mentality regeneration\n+20% domain size\n+20% speed\n+200 additonal maximum mana', 'karmic_chestplate', 11,
                                        [TAGS['item'], TAGS['accessory'], TAGS['body']]),
    'karmic_leggings': Inventory.Item('Karmic Leggings', '80 armor\n+10% damage\n+10% critical\n+10% speed\n+10/sec regeneration\n+20/sec mana regeneration\n'
                                                     '+20/sec mentality regeneration\n+10% domain size\n+10% speed\n+100 additonal maximum mana', 'karmic_leggings', 11,
                                        [TAGS['item'], TAGS['accessory'], TAGS['leg']]),

    'hallowed_helmet': Inventory.Item('Hallowed Helmet', '22 armor\n+10% pacify time\n+10% melee damage', 'hallowed_helmet', 7,
                                        [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'hallowed_mask': Inventory.Item('Hallowed Mask', '13 armor\n+100/sec inspiration regeneration\n+10% critical', 'hallowed_mask', 7,
                                        [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'hallowed_headgear': Inventory.Item('Hallowed Mask', '7 armor\n-10% karma reduce\n+100 additional maximum mana', 'hallowed_headgear', 7,
                                        [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'hallowed_plate_mail': Inventory.Item('Hallowed Plate Mail', '23 armor\n10kg\n+10% damage', 'hallowed_plate_mail', 7,
                                        [TAGS['item'], TAGS['accessory'], TAGS['body']]),
    'hallowed_greaves': Inventory.Item('Hallowed Greaves', '13 armor\n+10% speed\n-10% air resistance', 'hallowed_greaves', 7,
                                        [TAGS['item'], TAGS['accessory'], TAGS['leg']]),

    'worldsaver_hood': Inventory.Item('WorldSaver Hood', '14 armor\n+20 touching defense\n+10/sec regeneration', 'worldsaver_hood', 10,
                                        [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'worldsaver_chestplate': Inventory.Item('WorldSaver Chestplate', '21 armor\n+30 touching defense\n+15/sec regeneration', 'worldsaver_chestplate', 10,
                                            [TAGS['item'], TAGS['accessory'], TAGS['body']]),
    'worldsaver_leggings': Inventory.Item('WorldSaver Leggings', '11 armor\n+15 touching defense\n+7.5/sec regeneration', 'worldsaver_leggings', 10,
                                           [TAGS['item'], TAGS['accessory'], TAGS['leg']]),

    #300 2:3:1
    'dragon_helmet_red': Inventory.Item('Dragon Helmet (Red)', '100 armor\n+100 magic defense\n+10% melee damage', 'dragon_helmet_red', 10,
                                          [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'dragon_chestplate_red': Inventory.Item('Dragon Chestplate (Red)', '150 armor\n+150 magic defense\n+15% melee damage', 'dragon_chestplate_red', 10,
                                             [TAGS['item'], TAGS['accessory'], TAGS['body']]),
    'dragon_leggings_red': Inventory.Item('Dragon Leggings (Red)', '50 armor\n+50 magic defense\n+5% melee damage', 'dragon_leggings_red', 10,
                                            [TAGS['item'], TAGS['accessory'], TAGS['leg']]),

    #150 2:3:1
    'dragon_helmet_blue': Inventory.Item('Dragon Helmet (Blue)', '50 armor\n+50 magic defense\n+10% critical', 'dragon_helmet_blue', 10,
                                           [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'dragon_chestplate_blue': Inventory.Item('Dragon Chestplate (Blue)', '75 armor\n+75 magic defense\n+15% critical', 'dragon_chestplate_blue', 10,
                                              [TAGS['item'], TAGS['accessory'], TAGS['body']]),
    'dragon_leggings_blue': Inventory.Item('Dragon Leggings (Blue)', '25 armor\n+25 magic defense\n+5% critical', 'dragon_leggings_blue', 10,
                                             [TAGS['item'], TAGS['accessory'], TAGS['leg']]),

    #100 7:10:3
    'dragon_helmet_black': Inventory.Item('Dragon Helmet (Black)', '35 armor\n+35 magic defense\n+300 additional maximum mana', 'dragon_helmet_black', 10,
                                            [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'dragon_chestplate_black': Inventory.Item('Dragon Chestplate (Black)', '50 armor\n+50 magic defense\n+450 additional maximum mana', 'dragon_chestplate_black', 10,
                                               [TAGS['item'], TAGS['accessory'], TAGS['body']]),
    'dragon_leggings_black': Inventory.Item('Dragon Leggings (Black)', '15 armor\n+15 magic defense\n+150 additional maximum mana', 'dragon_leggings_black', 10,
                                              [TAGS['item'], TAGS['accessory'], TAGS['leg']]),

    #150 2:3:1
    'dragon_helmet_yellow': Inventory.Item('Dragon Helmet (Yellow)', '50 armor\n+50 magic defense\n+50% pacify time', 'dragon_helmet_yellow', 10,
                                             [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'dragon_chestplate_yellow': Inventory.Item('Dragon Chestplate (Yellow)', '75 armor\n+75 magic defense\n+75% pacify time', 'dragon_chestplate_yellow', 10,
                                                [TAGS['item'], TAGS['accessory'], TAGS['body']]),
    'dragon_leggings_yellow': Inventory.Item('Dragon Leggings (Yellow)', '25 armor\n+25 magic defense\n+25% pacify time', 'dragon_leggings_yellow', 10,
                                               [TAGS['item'], TAGS['accessory'], TAGS['leg']]),

    #100 7:10:3
    'dragon_helmet_gray': Inventory.Item('Dragon Helmet (Gray)', '35 armor\n+35 magic defense\n+1050 additional maximum inspiration', 'dragon_helmet_gray', 10,
                                           [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'dragon_chestplate_gray': Inventory.Item('Dragon Chestplate (Gray)', '50 armor\n+50 magic defense\n+1500 additional maximum inspiration', 'dragon_chestplate_gray', 10,
                                              [TAGS['item'], TAGS['accessory'], TAGS['body']]),
    'dragon_leggings_gray': Inventory.Item('Dragon Leggings (Gray)', '15 armor\n+15 magic defense\n+450 additional maximum inspiration', 'dragon_leggings_gray', 10,
                                             [TAGS['item'], TAGS['accessory'], TAGS['leg']]),

    #50 9:11:5
    'dragon_helmet_green': Inventory.Item('Dragon Helmet (Green)', '18 armor\n+18 magic defense\n-10% karma reduce', 'dragon_helmet_green', 10,
                                            [TAGS['item'], TAGS['accessory'], TAGS['head']]),
    'dragon_chestplate_green': Inventory.Item('Dragon Chestplate (Green)', '22 armor\n+22 magic defense\n-15% karma reduce', 'dragon_chestplate_green', 10,
                                               [TAGS['item'], TAGS['accessory'], TAGS['body']]),
    'dragon_leggings_green': Inventory.Item('Dragon Leggings (Green)', '10 armor\n+10 magic defense\n-5% karma reduce', 'dragon_leggings_green', 10,
                                              [TAGS['item'], TAGS['accessory'], TAGS['leg']]),

'natural_necklace': Inventory.Item('Natural Necklace', '0.2kg\n+4/sec mana regeneration', 'natural_necklace', 0,
                                       [TAGS['item'], TAGS['accessory']]),
    'copper_traveller_boots': Inventory.Item('Copper Traveller Boots', '30kg\n+60% speed\n+3 touching defense', 'copper_traveller_boots', 1,
                                              [TAGS['item'], TAGS['accessory']]),
    'thiefs_charm': Inventory.Item('Thief\'s Charm', '-40kg\n+120% ranged damage\n-50% damage\n+50% speed\n+40% critical', 'thiefs_charm', 1,
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
    'mana_flower': Inventory.Item('Mana Flower', '0.2kg\n+50 additional maximum mana\n+30/sec mana regeneration\n+10% magic damage', 'mana_flower', 1,
                                   [TAGS['item'], TAGS['accessory']]),
    'life_flower': Inventory.Item('Life Flower', '0.2kg\n+3/sec regeneration\n+1% critical', 'life_flower', 1,
                                   [TAGS['item'], TAGS['accessory']]),
    'magic_anklet': Inventory.Item('Magic Anklet', '25kg\n+4/sec mana regeneration\n+40% speed',
                                   'magic_anklet', 1, [TAGS['item'], TAGS['accessory']]),
    'purple_ring': Inventory.Item('Purple Ring', '+50% melee damage\n-20% damage\n+6% critical', 'purple_ring', 1,
                                   [TAGS['item'], TAGS['accessory']]),
    'cyan_ring': Inventory.Item('Cyan Ring', '+50% ranged damage\n-20% damage\n+12% critical', 'cyan_ring', 1,
                                [TAGS['item'], TAGS['accessory']]),
    'yellow_ring': Inventory.Item('Yellow Ring', '+50% magic damage\n-20% damage\n+6% critical', 'yellow_ring', 1,
                                   [TAGS['item'], TAGS['accessory']]),
    'gorgeous_ring': Inventory.Item('Gorgeous Ring', '+50% damage\n+22% critical',
                                     'gorgeous_ring', 1, [TAGS['item'], TAGS['accessory']]),
    'hermes_boots': Inventory.Item('Herme\'s Boots', '10kg\n+120% speed', 'hermes_boots', 2,
                                   [TAGS['item'], TAGS['accessory']]),
    'lucky_clover': Inventory.Item('Lucky Clover', '0.2kg\n+18% critical', 'lucky_clover', 2,
                                   [TAGS['item'], TAGS['accessory']]),
    'fairy_wings': Inventory.Item('Fairy Wings', '30kg\n-20% air resistance\n+50% speed\n+20% magic damage', 'fairy_wings', 3,
                                   [TAGS['item'], TAGS['accessory']]),
    'seed_amulet': Inventory.Item('Seed Amulet', '0.2kg\n-40% damage\n+15 magic defense', 'seed_amulet', 2,
                                   [TAGS['item'], TAGS['accessory']]),
    'snowstorm_bottle': Inventory.Item('Snowstorm Bottle', '1kg\n-80% damage\n+200% speed',
                                        'snowstorm_bottle', 2, [TAGS['item'], TAGS['accessory']]),
    'snow_wings': Inventory.Item('Snow Wings', '30kg\n-40% air resistance\n+150% speed',
                                 'snow_wings', 2, [TAGS['item'], TAGS['accessory']]),
    'fairy_boots': Inventory.Item('Fairy Boots', '40kg\n-24% air resistance\n+230% speed\n+20% magic damage\n+18% critical\n+50 splint', 'fairy_boots', 4,
                                   [TAGS['item'], TAGS['accessory']]),
    'platinum_traveller_boots': Inventory.Item('Platinum Traveller Boots', '50kg\n+120% speed\n+9 touching defense',
                                                'platinum_traveller_boots', 2, [TAGS['item'], TAGS['accessory']]),
    'sheath': Inventory.Item('Sheath', '20kg\n+18% melee damage\n+16 touching defense\n+0.5/sec regeneration\n+20% speed', 'sheath', 1,
                             [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'quiver': Inventory.Item('Quiver', '5kg\n+10% ranged damage\n+25% speed\n+8 touching defense', 'quiver', 1,
                             [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'hat': Inventory.Item('Hat',
                          '1kg\n+30% magical damage\n+6/sec mana regeneration\n+1/sec regeneration\n+2 touching defense\n+10% speed\n+10 additional maximum mana',
                          'hat', 1, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'fire_gloves': Inventory.Item('Fire Gloves', '1kg\n+16% melee damage\n+10% critical',
                                   'fire_gloves', 1, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'quenched_cross': Inventory.Item('Quenched Cross', '0.2kg\n+18% magic damage\n+12 magic defense',
                                      'quenched_cross', 1, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'lava_walker': Inventory.Item('Lava Walker', '20kg\n+140% speed\n+15 touching defense',
                                   'lava_walker', 2, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'firite_helmet': Inventory.Item('Firite Helmet',
                                    'Enable night vision\n30kg\n+30% melee damage\n+28 touching defense\n+19 magic defense\n+1.5/sec regeneration\n+24% speed',
                                    'firite_helmet', 3,
                                    [TAGS['item'], TAGS['accessory'], TAGS['night_vision'], TAGS['major_accessory']]),
    'firite_cloak': Inventory.Item('Firite Cloak',
                                   'Enable night vision\n10kg\n+32% ranged damage\n+14 touching defense\n+7 magic defense\n+0.5/sec regeneration\n+50% speed',
                                   'firite_cloak', 3,
                                   [TAGS['item'], TAGS['accessory'], TAGS['night_vision'], TAGS['major_accessory']]),
    'firite_pluvial': Inventory.Item('Firite Pluvial',
                                     'Enable night vision\n5kg\n+44% magical damage\n+6 touching defense\n+12 magic defense\n+2.5/sec regeneration\n'
                                     '+16/sec mana regeneration\n+20 additional maximum mana',
                                     'firite_pluvial', 3, [TAGS['item'], TAGS['accessory'], TAGS['night_vision'],
                                                           TAGS['major_accessory']]),
    'fluffy_pluvial': Inventory.Item('Fluffy Pluvial',
                                     '2kg\n+38% magical damage\n+3 touching defense\n+18 magic defense\n+6/sec regeneration\n+22/sec mana regeneration\n'
                                     'Magic weapon will be used twice, 25% chance to recover 50% of the mana cost\n+40 additional maximum mana',
                                     'fluffy_pluvial', 3, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
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
    'fire_eye': Inventory.Item('Fire Eye', '1kg\n+8% ranged damage\n+10 magic defense', 'fire_eye', 2,
                                [TAGS['item'], TAGS['accessory'], TAGS['light_source']]),
    'aimer': Inventory.Item('Aimer', 'Enables aiming to menaces.\n1kg', 'aimer', 2,
                            [TAGS['item'], TAGS['accessory'], TAGS['light_source'], TAGS['see']]),
    'photon_aimer': Inventory.Item('Photon Aimer', 'Enables aiming to menaces.\n1.5kg', 'photon_aimer', 5,
                                    [TAGS['item'], TAGS['accessory'], TAGS['light_source'], TAGS['see']]),
    'winds_necklace': Inventory.Item('Winds Necklace', '+50% speed.\n-35% damage.\n+20% ranged damage.\n.5kg',
                                     'winds_necklace', 2, [TAGS['item'], TAGS['accessory']]),
    'rune_cross': Inventory.Item('Rune Cross', '2kg\n+12% magic damage\n+12/sec mana regeneration',
                                  'rune_cross', 3, [TAGS['item'], TAGS['accessory']]),
    'rune_gloves': Inventory.Item('Rune Gloves', '5kg\n+12% melee damage\n+12% critical\n+22 touching defense',
                                  'rune_gloves', 3, [TAGS['item'], TAGS['accessory']]),
    'rune_eye': Inventory.Item('Rune Eye', '10kg\n+12% ranged damage\n+80% speed',
                                'rune_eye', 3, [TAGS['item'], TAGS['accessory']]),
    'star_amulet': Inventory.Item('Star Amulet', '+30 additional maximum mana',
                                  'star_amulet', 1, [TAGS['item'], TAGS['accessory']]),
    'starstorm_bottle': Inventory.Item('Star-Storm Bottle', '+40 additional maximum mana\n+100% speed\n+18% magic damage',
                                       'starstorm_bottle', 1, [TAGS['item'], TAGS['accessory']]),
    'windstorm_swordman_mark': Inventory.Item('Windstorm Swordman\'s Mark',
                                              '5kg\n+24% melee damage\n-12% damage\n+32 touching defense\n+34 magic defense\n+3/sec regeneration\nNight vision\nY: sweep the weapon and dealing 3 times the damage\n80 mana cost',
                                              'windstorm_swordman_mark', 4,
                                              [TAGS['item'], TAGS['accessory'], TAGS['night_vision'],
                                               TAGS['light_source'], TAGS['major_accessory']]),
    'windstorm_assassin_mark': Inventory.Item('Windstorm Assassin\'s Mark',
                                              '5kg\n+26% ranged damage\n-12% damage\n+17 touching defense\n+18 magic defense\n+1/sec regeneration\nNight vision\nY: use the weapon and sprint\n60 mana cost',
                                              'windstorm_assassin_mark', 4,
                                              [TAGS['item'], TAGS['accessory'], TAGS['night_vision'],
                                               TAGS['light_source'], TAGS['major_accessory']]),
    'windstorm_warlock_mark': Inventory.Item('Windstorm Warlock\'s Mark',
                                             '5kg\n+25% magical damage\n-12% damage\n+5 touching defense\n+12 magic defense\n+6/sec regeneration\n+15/sec mana regeneration\nNight vision\nY: use 20 times of the mana cost, summon 25 projectiles to the enemies',
                                             'windstorm_warlock_mark', 4,
                                             [TAGS['item'], TAGS['accessory'], TAGS['night_vision'],
                                              TAGS['light_source'], TAGS['major_accessory']]),
    'storm_charm': Inventory.Item('Storm Charm', '-30kg\n+100% speed\n-60% damage\n+180% ranged damage',
                                   'storm_charm', 4, [TAGS['item'], TAGS['accessory'], TAGS['light_source']]),
    'soarer_bottle': Inventory.Item('Soarer Bottle', '+50 additional maximum mana\n+240% speed\n-40% air resistance\n+22% magic damage',
                                     'soarer_bottle', 4, [TAGS['item'], TAGS['accessory']]),
    'red_ring': Inventory.Item('Red Ring', '+40% speed\n+22 touching defense\n+10 magic defense\n+12/sec mana regeneration\n+19% critical\n+40% damage',
                               'red_ring', 3, [TAGS['item'], TAGS['accessory']]),

    'palladium_glove': Inventory.Item('Palladium Glove',
                                      '32kg\n+28% damage\n+32% speed\n+18/sec regeneration\n+8/sec mana regeneration\n+90 touching defense\n+65 magic defense\nNight vision',
                                      'palladium_glove', 5,
                                      [TAGS['item'], TAGS['accessory'], TAGS['night_vision'], TAGS['major_accessory']]),
    'mithrill_glove': Inventory.Item('Mithrill Glove',
                                     '32kg\n+30% damage\n+120% speed\n+3/sec regeneration\n+40/sec mana regeneration\n85 touching defense\n+95 magic defense\nNight vision',
                                     'mithrill_glove', 5,
                                     [TAGS['item'], TAGS['accessory'], TAGS['night_vision'], TAGS['major_accessory']]),
    'titanium_glove': Inventory.Item('Titanium Glove',
                                     '32 kg\n+32% damage\n+45% speed\n+10/sec regeneration\n+32/sec mana regeneration\n+108 touching defense\n+40 magic defense\nNight vision',
                                     'titanium_glove', 5,
                                     [TAGS['item'], TAGS['accessory'], TAGS['night_vision'], TAGS['major_accessory']]),
    'soul_resonancer': Inventory.Item('Soul Resonancer', '+15% critical', 'soul_resonancer',
                                      5, [TAGS['item'], TAGS['accessory']]),
    'broken_copper_boots': Inventory.Item('Broken Copper Boots', '-60% speed', 'broken_copper_boots',
                                          5, [TAGS['item'], TAGS['accessory']]),
    'paladins_mark': Inventory.Item('Paladin\'s Mark',
                                    '80kg\n+100% speed\n+32% melee damage\n-15% damage\n+85 touching defense\n+70 magic defense\n+5/sec regeneration\nNight vision\nY: deal hallow stab\n40 mana cost',
                                    'paladins_mark', 5,
                                    [TAGS['item'], TAGS['accessory'], TAGS['night_vision'], TAGS['light_source'],
                                     TAGS['major_accessory']]),
    'daedalus_mark': Inventory.Item('Daedalus\'s Mark',
                                    '40kg\n+60% speed\n+36% ranged damage\n-15% damage\n+55 touching defense\n+45 magic defense\n+2/sec regeneration\nNight vision\nY: summon daedalus storm\n1200 piercing damage\n600 projectile speed\n60 mana cost',
                                    'daedalus_mark', 5,
                                    [TAGS['item'], TAGS['accessory'], TAGS['night_vision'], TAGS['light_source'],
                                     TAGS['major_accessory']]),
    'unregretted_heart': Inventory.Item('Unregretted Heart', 'My choice is right.\n+35% damage\n-18 touching defense\n+12% critical\n+10/sec regeneration',
                                        'unregretted_heart', 5,
                                        [TAGS['item'], TAGS['accessory']]),
    'critically': Inventory.Item('Critically', '-90% damage\n+1200% ranged damage\n+50% critical\n-60 attack speed', 'critically',
                                 5, [TAGS['item'], TAGS['accessory']]),
    'star_wings': Inventory.Item('Star Wings', '80kg\n-50% air resistance\n50% wing control', 'star_wings', 5,
                                  [TAGS['item'], TAGS['accessory'], TAGS['wings']]),
    'guardian_necklace': Inventory.Item('Guardian Necklace', '10kg\n+25 magic damage\n+20/sec regeneration', 'guardian_necklace', 5,
                                        [TAGS['item'], TAGS['accessory']]),
    'red_spirit_ring': Inventory.Item('Red Spirit Ring', '+45% speed\n+28 touching defense\n+16 magic defense\n+25/sec mana regeneration\n+24% critical\n+45% damage',
                                   'red_spirit_ring', 5, [TAGS['item'], TAGS['accessory']]),

    'necklace_of_life': Inventory.Item('Necklace of Life', '0.2kg\n+30/sec regeneration\n+60/sec mana regeneration',
                                       'necklace_of_life', 7, [TAGS['item'], TAGS['accessory']]),
    'thorn_ring': Inventory.Item('Thorn Ring', '+60% magic damage\n-36/sec regeneration\n+200/sec mana regeneration',
                                 'thorn_ring', 7, [TAGS['item'], TAGS['accessory']]),
    'jevils_tail': Inventory.Item('Jevil\'s Tail', '+130 touching defense\n+280 magic defense\n-30% damage',
                                 'jevils_tail', 7, [TAGS['item'], TAGS['accessory']]),
    'cloudy_glasses': Inventory.Item('Cloudy Glasses', '50kg\n-20% damage\n+66% melee damage\n'
                                                       '80% speed\n+188 touching defense\n+128 magic defense\nNight vision\n'
                                                       'Y: Kill all projectiles.\n600 mana cost', 'cloudy_glasses', 7,
                                      [TAGS['item'], TAGS['accessory'], TAGS['night_vision']]),
    'cowboy_hat': Inventory.Item('Cowboy Hat', '20kg\n-20% damage\n+64% ranged damage\n+100% speed\n+10/sec '
                                               'regeneration\n+120 touching defense\n+150 magic defense\nNight '
                                               'vision\nY: Justice Time\n400 mana '
                                               'cost', 'cowboy_hat', 7, [TAGS['item'], TAGS['accessory'],
                                                                         TAGS['night_vision'],
                                                                         TAGS['major_accessory']]),
    'magicians_hat': Inventory.Item('Magician\'s Hat', '40kg\n-20% damage\n+68% magical damage\n+100% speed\n+40/sec '
                                                  'regeneration\n+100 touching defense\n+240 magic defense\n+200/sec mana regeneration\n'
                                                       'Night vision','magicians_hat', 7, [TAGS['item'], TAGS['accessory'],
                                                                               TAGS['night_vision'], TAGS['major_accessory']]),
    'life_boots': Inventory.Item('Life Boots', '42kg\n-26% air resistance\n+250% speed\n+12% damage\n+22% critical\n+120 splint', 'life_boots', 7,
                                   [TAGS['item'], TAGS['accessory']]),
    'great_magicians_hat': Inventory.Item('Great Magician\'s Hat', '60kg\n-20% damage\n+72% magical damage\n+100% speed\n+60/sec '
                                                                    'regeneration\n+120 touching defense\n+280 magic defense\n+240/sec mana regeneration\n'
                                                                     '+80% domain size\n+20/sec mentality regeneration', 'great_magicians_hat', 8, [TAGS['item'], TAGS['accessory'],
                                                                                           TAGS['night_vision'], TAGS['major_accessory']]),
    'the_chaos_flower_vase': Inventory.Item('The Chaos Flower Vase', '120kg\n+200 additipnal maximum mana\n+270% speed\n-38% air resistance\n+32% magic damage\n+80/sec mana regeneration\n+20% domain size\n+20 touching defense',
                                             'the_chaos_flower_vase', 8, [TAGS['item'], TAGS['accessory']]),
    'gods_necklace': Inventory.Item('God\'s Necklace', '+50% domain size\n+6/sec talent regeneration', 'gods_necklace', 9, [TAGS['item'], TAGS['accessory']]),
    'chaos_sheath': Inventory.Item('Chaos Sheath', '150kg\n+88% melee damage\n+28% critical\n+440 touching defense\n+420 magic defense'
                                                   '\n+30/sec regeneration\n+70/sec mana regeneration\n+120% speed', 'chaos_sheath',
                                   9, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'chaos_quiver': Inventory.Item('Chaos Quiver', '10kg\n+90% ranged damage\n+45% critical\n+280 touching defense\n+360 magic defense'
                                                   '\n+50/sec regeneration\n+110/sec mana regeneration\n+220% speed', 'chaos_quiver',
                                   9, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'chaos_evileye': Inventory.Item('Chaos Evileye', '-10 attack speed\n+40% critical\n+100 additonal maximum mana',
                                    'chaos_evileye', 9, [TAGS['item'], TAGS['accessory'], TAGS['see2']]),
    'starnight_gloves': Inventory.Item('Starnight Gloves', '+50% melee damage\n+40% magic damage\n-10 attack speed\n+20/sec mana regeneration\n+10/sec regeneration\n+15% critical',
                                       'starnight_gloves', 9, [TAGS['item'], TAGS['accessory']]),
    'corrupt_boots': Inventory.Item('Corrupt Boots', '80kg\n+180% speed\n+14% critical\n+25 magic defense\n+8% damage\n+12/sec mana regeneration\n+150 splint\n-80% splint cd',
                                    'corrupt_boots', 9, [TAGS['item'], TAGS['accessory']]),
    'magisters_hat': Inventory.Item('Magister\'s Hat', '80kg\n-20% damage\n+77% magical damage\n+80% speed\n+80/sec '
                                                 'regeneration\n+140 touching defense\n+480 magic defense\n+280/sec mana regeneration\n'
                                                  '+220% domain size\n+50/sec mentality regeneration','magisters_hat', 9, [TAGS['item'], TAGS['accessory'],
                                                                             TAGS['night_vision'], TAGS['major_accessory']]),
    'bezoar_necklace': Inventory.Item('Bezoar Necklace', '-25% poison damage received\n+20 poison defense', 'bezoar_necklace', 7,
                                       [TAGS['item'], TAGS['accessory']]),
    'rudder': Inventory.Item('Rudder', 'That\'s how to control.\n+114514% air resistance\n+800% speed', 'rudder', 10,
                              [TAGS['item'], TAGS['accessory']]),
    'determined_ring': Inventory.Item('Determined Ring', '+55% speed\n+45 touching defense\n+36 magic defense\n+150 additional maximum mana\n+28% critical\n+55% damage',
                                       'determined_ring', 9, [TAGS['item'], TAGS['accessory']]),

    'altitude': Inventory.Item('Altitude', 'No need to say.\n40kg\n-65% air resistance\n-20% speed\n80% wing control', 'altitude',
                               9, [TAGS['item'], TAGS['accessory'], TAGS['wings']]),
    'horizon_goggles': Inventory.Item('Horizon Goggles', '12kg\n+80% ranged damage\n+25% critical\nAlmost see everything.',
    'horizon_goggles', 9,
    [TAGS['item'], TAGS['accessory'], TAGS['night_vision'], TAGS['light_source'], TAGS['see2']]),

    'time_shackle': Inventory.Item('Time Shackle', 'You\'ll be trapped in time\n1600kg\n+80 touching defense\n+100 magic defense\n-100% damage\n-100/sec regeneration',
                                   'time_shackle', 10, [TAGS['item'], TAGS['accessory']]),
    'flashback': Inventory.Item('Flashback', 'When near to death, stop the time.\n50s CD\n-40 touching defense\n-20/sec regeneration', 'flashback',
                                10, [TAGS['item'], TAGS['accessory']]),
    'time_wheel': Inventory.Item('Time Wheel', 'The spin and the time.\n200kg\n-15% air resistance\n+500% speed\n20% wing control', 'time_wheel',
                               10, [TAGS['item'], TAGS['accessory'], TAGS['wings']]),
    'ultradense_shield': Inventory.Item('Ultradense Shield', 'Ultimate toughness of matter\n+120 touching defense\n-400/sec mana regeneration\n-20% damage',
                                        'ultradense_shield', 10, [TAGS['item'], TAGS['accessory']]),
    'matter_floatboard': Inventory.Item('Matter Float System', 'Within controller system\n-30% air resistance\n80% speed\n85% wing control',
                                         'matter_floatboard', 10, [TAGS['item'], TAGS['accessory'], TAGS['wings']]),
    'matters_touch': Inventory.Item('Matter\'s Touch', 'When using melee weapons, increase target mass by 1%\n-10% melee damage\n+20% damage\n+10% critical',
                                     'matters_touch', 10, [TAGS['item'], TAGS['accessory']]),
    'black_hole_pluvial': Inventory.Item('Black Hole Pluvial', 'Appeal entities.\n200kg\n+100% speed\n-20% air resistance\n50% wing control',
                                           'black_hole_pluvial', 10, [TAGS['item'], TAGS['accessory'], TAGS['wings']]),
    'star_statue': Inventory.Item('Star Statue', 'The most beautiful statue.\n+140 touching defense\n+110 magic defense\n+15/sec regeneration',
                                   'star_statue', 10, [TAGS['item'], TAGS['accessory']]),
    'demon_contract': Inventory.Item('Demon Contract', 'Save you back to life, but curse you. 30CD',
                                      'demon_contract', 10, [TAGS['item'], TAGS['accessory']]),
    'demon_wings': Inventory.Item('Demon Wings', '100kg\n-200% speed\n-60% air resistance\n+50% wing control', 'demon_wings', 10,
                                    [TAGS['item'], TAGS['accessory'], TAGS['wings']]),

    'ultra_lightspeed': Inventory.Item('Ultra-Lightspeed', 'Some says the time will be reversed when the speed is fast enough.\nAllow acceleration to infinite speed.\n'
                                                         '-50% air resistance\n+100% wing control', 'ultra_lightspeed', 10, [TAGS['item'], TAGS['accessory'], TAGS['wings']]),
    'grasp_of_the_infinite_corridor': Inventory.Item('Grasp of the Infinite Corridor', 'A world, a planet, is all in my hand.\n+72% damage\n+180 touching defense\n+120 magic defense\n'
                                                                                       '+50/sec regeneration\n+500% domain size\n+10/sec mentality regeneration\n+80% speed\n+400 additional maximum mana\n'
                                                                                       '+36% critical\nWhen using melee to hit enemy, deal additionally 1% thinking damage, 0.5% chance to kill it.', 'grasp_of_the_infinite_corridor',
                                                     10, [TAGS['item'], TAGS['accessory']]),
    'karmic_trail_boots': Inventory.Item('Karmic Trail Boots', 'Prints down the path of karma.\n188kg\n-25% air resistance\n+450% speed\n+18% damage\n+32% critical\n+500 splint\n-95% splint cd\n'
                                                               '+15/sec regeneration\nYour footprint will deal damage to enemies.',
                                          'karmic_trail_boots', 10, [TAGS['item'], TAGS['accessory']]),
    'fate_alignment_amulet': Inventory.Item('Fate Alignment Amulet', 'The path of destiny.\n+50% speed\n+88% critical\n+80 touching defense\n120 magic defense\n'
                                                           '+40/sec regeneration\n+180/sec mana regeneration\nRevive after death.100CD',
                                             'fate_alignment_amulet', 10, [TAGS['item'], TAGS['accessory']]),

    'patience_amulet': Inventory.Item('Patience Amulet', 'Cool it down, and wait.\n100kg\n+300% speed\n+94% melee damage\n+94% ranged damage\n'
                                                    '+28% damage\n+60% critical\n+320 touching defense\n320 magic defense\n'
                                                    '+50/sec regeneration\n+250/sec mana regeneration\n+80% domain size\n'
                                                         '+10/sec mentality regeneration\nWhen HP > 50%, +80% speed\n'
                                                         'When HP < 50%, +200% damage', 'patience_amulet', 10,
                                       [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'integrity_amulet': Inventory.Item('Integrity Amulet',
                                       'Say the right words, do the right thing.\n90kg\n+120 touching defense\n+330 magic defense\n'
                                       '+320/sec mana regeneration\n+180% domain size\n+30/sec mentality regeneration\n+120% speed\n'
                                       '+30% damage\n+108% magic damage\n+200% speed\n+90/sec regeneration\n+25% critical\n+800 splint\n'
                                       '-50% splint cooldown\nY: Use 32x of mana cost of current weapon, summoning 50 projectiles',
                                       'integrity_amulet', 10, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'perseverance_amulet': Inventory.Item('Perseverance Amulet', 'Never give up.\n200kg\n+350% speed\n+110% melee damage\n+35% damage\n'
                                                                 '+18% critical\n+480 touching defense\n+360 magic defense\n+50/sec regeneration\n'
                                                                 '+110/sec mana regeneration\n+30% domain size\n+5/sec mentality regeneration\n'
                                                                 'Y: 50x the speed of the current weapon for a moment, 800 mana cost', 'perseverance_amulet', 11,
                                           [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'bravery_amulet': Inventory.Item('Bravery Amulet', 'The willpower of courage.\n-20kg\n+180% speed\n+105% ranged damage\n+28% damage\n'
                                                 '+96% magic damage\n+36% critical\n+360 touching defense\n+388 magic defense\n+80/sec regeneration\n'
                                                 '+250/sec mana regeneration\n+180% domain size\n+36/sec mentality regeneration\n'
                                                 'Y: Attack for 10 times, deal 20x of damage to any menace', 'bravery_amulet', 11,
                                     [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'kindness_amulet': Inventory.Item('Kindness Amulet', 'The friendliest mercy.\n+100kg\n+240% speed\n+102% melee damage\n+33% damage\n'
                                                         '+112% magic damage\n+24% critical\n+450 touching defense\n+325 magic defense\n+240/sec regeneration\n'
                                                         '+400/sec mana regeneration\n+380% domain size\n+50/sec mentality regeneration\n'
                                                         'Y: Heal everyone until your hp max out', 'kindness_amulet', 11,
                                       [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'justice_amulet': Inventory.Item('Justice Amulet', 'The righteousness of the law.\n-80kg\n+300% speed\n+120% ranged damage\n+25% damage\n'
                                                       '+100% critical\n+240 touching defense\n+450 magic defense\n+30/sec regeneration\n'
                                                       '+200/sec mana regeneration\n+80% domain size\n+15/sec mentality regeneration\n'
                                                       'Y: Teleport, 800 mana cost', 'justice_amulet', 11,
                                       [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'my_ring': Inventory.Item('My Ring', '+80% speed\n+65 touching defense\n+55 magic defense\n+400 additional maximum mana\n+32% critical\n+66% damage',
                              'my_ring', 11, [TAGS['item'], TAGS['accessory']]),
    'heart_locket': Inventory.Item('Heart Locket', 'You can feel it beating\n+300% speed\n+200% damage\n+100% critical\n'
                                                   '+600 touching defense\n+600 magic defense\n+120/sec regeneration\n600/sec mana regeneration\n'
                                                   '+360% domain size\n+120/sec mentality regeneration', 'heart_locket', 12,
                                     [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),

    'wings': Inventory.Item('Wings', 'The will to fly.\n80kg\n-60% air resistance\n+240% speed\n20% wing control', 'wings', 4,
                            [TAGS['item'], TAGS['accessory'], TAGS['wings']]),
    'honest_flyer': Inventory.Item('Honest Flyer', 'The perseverance to fly.\n280kg\n-80% air resistance\n+480% speed\n10% wing control',
                                   'honest_flyer', 5, [TAGS['item'], TAGS['accessory'], TAGS['wings']]),

    'note_sheet': Inventory.Item('Note Sheet', 'A book of musical notes you might find useful.\n+80/sec inspiration regeneration', 'note_sheet', 3, [TAGS['item'], TAGS['accessory']]),
    'red_formal_hat': Inventory.Item('Red Formal Hat', '5kg\nLooks both free and elegant.\n+100/sec inspiration regeneration\n+28% octave damage\n+20% speed\n'
                                                       '+18/sec mana regeneration\n+8% critical\n+55 touching defense\n+88 magic defense', 'red_formal_hat', 4, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'windstorm_musicians_mark': Inventory.Item('Windstorm Musician\'s Mark', '10kg\n+90/sec inspiration regeneration\n+38% octave damage\n+30% speed\n'
                                                              '+20/sec mana regeneration\n+17% critical\n+48 touching defense\n+96 magic defense\nY: Directly own gains for 12s:\nSpeed II\nLimitless III\nStrength III\n500 inspiration cost', 'windstorm_musicians_mark',
                                               4, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'instrument_belt': Inventory.Item('Instrument Belt', '15kg\n+200/sec inspiration regeneration\n+18% octave damage\n+40% speed\n'
                                                      '+20/sec mana regeneration\n+22% critical\n+80 touching defense\n+128 magic defense\n+12% critical', 'instrument_belt', 7,
                                      [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),


    'cross_amulet': Inventory.Item('Cross Amulet', '-10% karma reduce\n+20 additional maximum mana',
                                   'cross_amulet', 3, [TAGS['item'], TAGS['accessory']]),
    'grey_hood': Inventory.Item('Grey Hood', '12kg\n-30% karma reduce\n+12% hallow damage\n+40% speed\n'
                                                    '+20/sec mana regeneration\n+20/sec regeneration\n+8% critical\n'
                                             '+48 touching defense\n+26 magic defense', 'grey_hood',
                                5, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'windstorm_churchs_mark': Inventory.Item('Windstorm Church\'s Mark', '15kg\n-12% karma reduce\n+20% hallow damage\n+30% speed\n'
                                                              '+12/sec mana regeneration\n+54 touching defense\n+38 magic defense\n'
                                                                         'Y: Increase karma by 120.', 'windstorm_churchs_mark',
                                               5, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'cross_pluvial': Inventory.Item('Cross Pluvial', '+18% hallow damage\n-40% karma reduce\n+100 additional maximum mana\n+10% speed\n'
                                                     '-5/sec regeneration\n+10/sec mana regeneration\n+90 touching defense\n+60 magic defense', 'cross_pluvial', 7,
                                      [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),

    'eye_of_sleep': Inventory.Item('Eye of Sleep', '+15% pacify time', 'eye_of_sleep', 4,
                                   [TAGS['item'], TAGS['accessory']]),
    'hypnotists_tie': Inventory.Item('Hypnotist\'s Tie', '+18% pacify time\n+10% speed\n+10/sec regeneration\n+10/sec mana regeneration\n'
                                                         '+84 touching defense\n+48 magic defense', 'hypnotists_tie', 3,
                                      [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'windstorm_pacifiers_mark': Inventory.Item('Windstorm Pacifier\'s Mark', '10kg\n+8% pacify time\n+18% pacify damage\n+20% speed\n'
                                                              '+10/sec mana regeneration\n+10/sec regeneration\n+12% critical\n'
                                                                         '+96 touching defense\n+40 magic defense\nY: Increase enemies\' pacify time by 10s.\n400 mana cost', 'windstorm_pacifiers_mark',
                                               5, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'talent_cloat': Inventory.Item('Talent Cloat', '20kg\n+30% pacify time\n+120 touching defense\n+70 magic defense\n+20% speed\n'
                                                   '+10/sec regeneration', 'talent_cloat', 7,
                                     [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),

    'sight_ingot': Inventory.Item('Sight Ingot', 'Essence of a watcher.', 'sight_ingot', 5, [TAGS['item']]),
    'strength_ingot': Inventory.Item('Strength Ingot', 'Essence of a warrior.', 'strength_ingot', 5, [TAGS['item']]),
    'phantom_ingot': Inventory.Item('Phantom Ingot', 'Essence of a lie.', 'phantom_ingot', 5, [TAGS['item']]),
    'wither_rib': Inventory.Item('Wither Rib', '', 'wither_rib', 6, [TAGS['item']]),
    'iris_shard': Inventory.Item('Iris Shard', '', 'iris_shard', 6, [TAGS['item']]),
    'freezing_ice': Inventory.Item('Freezing Ice', '', 'freezing_ice', 6, [TAGS['item']]),
    'hallow_ingot': Inventory.Item('Hallow Ingot', 'The power scaring all the darks', 'hallow_ingot', 7,
                                   [TAGS['item']]),

    'dragon_bone': Inventory.Item('Dragon Bone', 'Incredibly strong and tough', 'dragon_bone', 9, [TAGS['item']]),
    'dragon_skull': Inventory.Item('Dragon Skull', 'Staring at it makes you feel a bit uneasy.', 'dragon_skull', 9, [TAGS['item']]),
    'dragon_scale_red': Inventory.Item('Dragon Scale (Red)', 'A red dragon\'s scales.\nEspecially resistant to magic attacks.', 'dragon_scale_red', 9, [TAGS['item']]),
    'dragon_scale_blue': Inventory.Item('Dragon Scale (Blue)', 'A blue dragon\'s scales.\nEspecially resistant to magic attacks.', 'dragon_scale_blue', 9, [TAGS['item']]),
    'dragon_scale_black': Inventory.Item('Dragon Scale (Black)', 'A black dragon\'s scales.\nEspecially resistant to magic attacks.', 'dragon_scale_black', 9, [TAGS['item']]),
    'dragon_scale_yellow': Inventory.Item('Dragon Scale (Yellow)', 'A yellow dragon\'s scales.\nEspecially resistant to magic attacks.', 'dragon_scale_yellow', 9, [TAGS['item']]),
    'dragon_scale_gray': Inventory.Item('Dragon Scale (Gray)', 'A gray dragon\'s scales.\nEspecially resistant to magic attacks.', 'dragon_scale_gray', 9, [TAGS['item']]),
    'dragon_scale_green': Inventory.Item('Dragon Scale (Green)', 'A green dragon\'s scales.\nEspecially resistant to magic attacks.', 'dragon_scale_green', 9, [TAGS['item']]),
    'naga_scale': Inventory.Item('Naga Scale', 'A naga\'s scales.\nEspecially resistant to magic attacks.', 'naga_scale', 9, [TAGS['item']]),

    'fire_dragon_blood': Inventory.Item('Fire Dragon Blood', 'What an essence of a dragon of fire is.', 'fire_dragon_blood', 9, [TAGS['item']]),
    'ice_dragon_blood': Inventory.Item('Ice Dragon Blood', 'What an essence of a dragon of ice is.', 'ice_dragon_blood', 9, [TAGS['item']]),
    'dark_dragon_blood': Inventory.Item('Dark Dragon Blood', 'What an essence of a dragon of darkness is.', 'dark_dragon_blood', 9, [TAGS['item']]),
    'light_dragon_blood': Inventory.Item('Light Dragon Blood', 'What an essence of a dragon of light is.', 'light_dragon_blood', 9, [TAGS['item']]),
    'mechanic_dragon_blood': Inventory.Item('Mechanic Dragon Blood', 'What an essence of a dragon of mechanics is.', 'mechanic_dragon_blood', 9, [TAGS['item']]),
    'mind_dragon_blood': Inventory.Item('Mind Dragon Blood', 'What an essence of a dragon of mind is.', 'mind_dragon_blood', 9, [TAGS['item']]),

    'fire_dragon_heart': Inventory.Item('Fire Dragon Heart', 'The true core of a dragon of fire.', 'fire_dragon_heart', 9, [TAGS['item']]),
    'ice_dragon_heart': Inventory.Item('Ice Dragon Heart', 'The true core of a dragon of ice.', 'ice_dragon_heart', 9, [TAGS['item']]),
    'dark_dragon_heart': Inventory.Item('Dark Dragon Heart', 'The true core of a dragon of darkness.', 'dark_dragon_heart', 9, [TAGS['item']]),
    'light_dragon_heart': Inventory.Item('Light Dragon Heart', 'The true core of a dragon of light.', 'light_dragon_heart', 9, [TAGS['item']]),
    'mechanic_dragon_heart': Inventory.Item('Mechanic Dragon Heart', 'The true core of a dragon of mechanics.', 'mechanic_dragon_heart', 9, [TAGS['item']]),
    'mind_dragon_heart': Inventory.Item('Mind Dragon Heart', 'The true core of a dragon of mind.', 'mind_dragon_heart', 9, [TAGS['item']]),

    'dragon_swift_sword': Inventory.Item('Dragon Swift Sword', '', 'dragon_swift_sword', 9, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'dragon_bow': Inventory.Item('Dragon Bow', '', 'dragon_bow', 9, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'dragon_flute': Inventory.Item('Dragon Flute', '', 'dragon_flute', 9, [TAGS['item'], TAGS['weapon'], TAGS['poet_weapon']]),

    'fire_quench__dragon_sword': Inventory.Item('Fire Quench: Dragon Swift Sword', '', 'fire_quench__dragon_sword', 10, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'fire_quench__dragon_bow': Inventory.Item('Fire Quench: Dragon Bow', '', 'fire_quench__dragon_bow', 10, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'ice_quench__dragon_sword': Inventory.Item('Ice Quench: Dragon Swift Sword', '', 'ice_quench__dragon_sword', 10, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'ice_quench__dragon_bow': Inventory.Item('Ice Quench: Dragon Bow', '', 'ice_quench__dragon_bow', 10, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'dark_quench__dragon_sword': Inventory.Item('Dark Quench: Dragon Swift Sword', '', 'dark_quench__dragon_sword', 10, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'dark_quench__dragon_bow': Inventory.Item('Dark Quench: Dragon Bow', '', 'dark_quench__dragon_bow', 10, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'light_quench__dragon_sword': Inventory.Item('Light Quench: Dragon Swift Sword', '', 'light_quench__dragon_sword', 10, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'light_quench__dragon_bow': Inventory.Item('Light Quench: Dragon Bow', '', 'light_quench__dragon_bow', 10, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'the_song_of_ice_and_fire': Inventory.Item('The Song of Ice and Fire', '', 'the_song_of_ice_and_fire', 10, [TAGS['item'], TAGS['weapon'], TAGS['poet_weapon']]),
    'fire_dragon_breath_wand': Inventory.Item('Fire Dragon Breath Wand', '', 'fire_dragon_breath_wand', 10, [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_fire'], TAGS['magic_lv_7']]),
    'ice_dragon_breath_wand': Inventory.Item('Ice Dragon Breath Wand', '', 'ice_dragon_breath_wand', 10, [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_water'], TAGS['magic_lv_7']]),
    'dark_dragon_breath_wand': Inventory.Item('Dark Dragon Breath Wand', '', 'dark_dragon_breath_wand', 10, [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_dark'], TAGS['magic_lv_7']]),
    'light_dragon_breath_wand': Inventory.Item('Light Dragon Breath Wand', '', 'light_dragon_breath_wand', 10, [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_light'], TAGS['magic_lv_7']]),
    'dance_of_fire': Inventory.Item('Dance of Fire', '', 'dance_of_fire', 10, [TAGS['item'], TAGS['weapon'], TAGS['poet_weapon']]),
    'dance_of_frost': Inventory.Item('Dance of Frost', '', 'dance_of_frost', 10, [TAGS['item'], TAGS['weapon'], TAGS['poet_weapon']]),
    'dance_of_shadow': Inventory.Item('Dance of Shadow', '', 'dance_of_shadow', 10, [TAGS['item'], TAGS['weapon'], TAGS['poet_weapon']]),
    'dance_of_shine': Inventory.Item('Dance of Shine', '', 'dance_of_shine', 10, [TAGS['item'], TAGS['weapon'], TAGS['poet_weapon']]),

    'dragon_reactor': Inventory.Item('Dragon Reactor', 'A reactor that is tough enough and resistant to dragon breaths.', 'dragon_reactor', 10, [TAGS['item'], TAGS['workstation']]),
    'fire_heating_unit': Inventory.Item('Fire Heating Unit', 'A unit that can heat up fire.', 'fire_heating_unit', 10, [TAGS['item'], TAGS['workstation']]),
    'ice_heating_unit': Inventory.Item('Ice Heating Unit', 'A unit that can heat up ice.', 'ice_heating_unit', 10, [TAGS['item'], TAGS['workstation']]),
    'dark_heating_unit': Inventory.Item('Dark Heating Unit', 'A unit that can heat up darkness.', 'dark_heating_unit', 10, [TAGS['item'], TAGS['workstation']]),
    'light_heating_unit': Inventory.Item('Light Heating Unit', 'A unit that can heat up light.', 'light_heating_unit', 10, [TAGS['item'], TAGS['workstation']]),
    'mind_cooling_unit': Inventory.Item('Mind Cooling Unit', 'A unit that can cool down minds.', 'mind_cooling_unit', 10, [TAGS['item'], TAGS['workstation']]),

    'fire_dragon_ingot': Inventory.Item('Fire Dragon Ingot', 'Endless power of fire.', 'fire_dragon_ingot', 11, [TAGS['item']]),
    'ice_dragon_ingot': Inventory.Item('Ice Dragon Ingot', 'Endless power of ice.', 'ice_dragon_ingot', 11, [TAGS['item']]),
    'dark_dragon_ingot': Inventory.Item('Dark Dragon Ingot', 'Endless power of darkness.', 'dark_dragon_ingot', 11, [TAGS['item']]),
    'light_dragon_ingot': Inventory.Item('Light Dragon Ingot', 'Endless power of light.', 'light_dragon_ingot', 11, [TAGS['item']]),

    'the_ruling_sword': Inventory.Item('The Ruling Sword', 'The superior power to give justice to all.', 'the_ruling_sword', 12, [TAGS['item'], TAGS['weapon'], TAGS['melee_weapon']]),
    'the_fairy_bow': Inventory.Item('The Fairy Bow', 'Shoots a row of magical arrows.', 'the_fairy_bow', 12, [TAGS['item'], TAGS['weapon'], TAGS['bow']]),
    'the_magisters_wand': Inventory.Item('The Magister\'s Wand', 'A wand that can control the elements.', 'the_magisters_wand', 12,
                                         [TAGS['item'], TAGS['weapon'], TAGS['magic_weapon'], TAGS['magic_element_fire'], TAGS['magic_element_water'], TAGS['magic_element_dark'], TAGS['magic_element_light'],
                                         TAGS['magic_lv_forbidden_curse']]),
    'the_godfall_poem': Inventory.Item('The Godfall Poem', 'A line\'s start, a god\'s fall.', 'the_godfall_poem', 12, [TAGS['item'], TAGS['weapon'], TAGS['poet_weapon']]),

    'eternal_hush': Inventory.Item('Eternal Hush', '-80% air resistance\n+100% wing control\nYour move cause your surrounding will be frozen.', 'eternal_hush', 12, [TAGS['item'], TAGS['accessory'], TAGS['wings']]),
    'voidstride_treads': Inventory.Item('Voidstride Treads', '+200% speed\n+5% critical\n+80 magic defense\n+120/sec mana regeneration\n+10% domain size\n+1s poet bonus time\nYour footprint weakens the enemies.', 'voidstride_treads', 12, [TAGS['item'], TAGS['accessory']]),
    'vermillion_sigil_palms': Inventory.Item('Vermillion Sigil Palms', '+80% damage\n+15% critical\n+50/sec regeneration\n+100% pacify time\nYour attack will be with fire.', 'vermillion_sigil_palms', 12, [TAGS['item'], TAGS['accessory']]),
    'aurora_dawn': Inventory.Item('Aurora Dawn', '+600/sec mana regeneration\n+10/sec mentality regeneration\n+50% domain size\n+1000 additional maximum mana.\n+200/sec inspiration regeneration\n-50% karma reduce.\nYour body protects you from death.', 'aurora_dawn', 12, [TAGS['item'], TAGS['accessory']]),

    'fire_dragon_cross': Inventory.Item('Fire Dragon Cross', '+400 touching defense\n+300 magic defense\n+120% melee damage\n+20/sec regeneration\n+5% critical', 'fire_dragon_cross', 11, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'ice_dragon_cross': Inventory.Item('Ice Dragon Cross', '+200 touching defense\n+200 magic defense\n+100% ranged damage\n+30/sec regeneration\n+25% critical\n+50% speed', 'ice_dragon_cross', 11, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'dark_dragon_cross': Inventory.Item('Dark Dragon Cross', '+150 touching defense\n+250 magic defense\n+80% magic damage\n+45/sec regeneration\n+800/sec mana regeneration\n+10/sec mentality regeneration\n+50% domain size\n+400 additional maximum mana', 'dark_dragon_cross', 11, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'light_dragon_cross': Inventory.Item('Light Dragon Cross', '+300 touching defense\n+100 magic defense\n+150% pacify damage\n+120% pacify time', 'light_dragon_cross', 11, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']]),
    'true_cyber_dragon_cross': Inventory.Item('True: Cyber Dragon Cross', '+200 touching defense\n+200 magic defense\n+100% octave damage\n+2000 additional maximum inspiration\n+600/sec inspiration regeneration\n+5s poet bonus time', 'true_cyber_dragon_cross', 12, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']], 'cyber_dragon_cross'),
    'true_mind_dragon_cross': Inventory.Item('True: Mind Dragon Cross', '+50 touching defense\n+30 magic defense\n+150% hallow damage\n+200/sec mana regeneration\n-50% karma reduce', 'true_mind_dragon_cross', 12, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']], 'mind_dragon_cross'),
    # true +20%
    'true_fire_dragon_cross': Inventory.Item('True: Fire Dragon Cross', '+480 touching defense\n+360 magic defense\n+140% melee damage\n+28/sec regeneration\n+6% critical',
                                             'true_fire_dragon_cross', 12, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']], 'fire_dragon_cross'),
    'true_ice_dragon_cross': Inventory.Item('True: Ice Dragon Cross', '+240 touching defense\n+240 magic defense\n+120% ranged damage\n+36/sec regeneration\n+30% critical\n+50% speed',
                                            'true_ice_dragon_cross', 12, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']], 'ice_dragon_cross'),
    'true_dark_dragon_cross': Inventory.Item('True: Dark Dragon Cross', '+180 touching defense\n+300 magic defense\n+100% magic damage\n+52/sec regeneration\n+220/sec mana regeneration\n'
                                                                        '+12/sec mentality regeneration\n+50% domain size\n+480 additional maximum mana', 'true_dark_dragon_cross', 12,
                                             [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']], 'dark_dragon_cross'),
    'true_light_dragon_cross': Inventory.Item('True: Light Dragon Cross', '+360 touching defense\n+120 magic defense\n+180% pacify damage\n+140% pacify time',
                                              'true_light_dragon_cross', 12, [TAGS['item'], TAGS['accessory'], TAGS['major_accessory']], 'light_dragon_cross'),

    'nice_cream': Inventory.Item('Nice Cream', 'Increase your speed.\nDuration: 36s', 'nice_cream', 4, [TAGS['item']]),
    'iron_donut': Inventory.Item('Iron Donut', 'Increase your defense by 32.\nDuration: 54s', 'iron_donut', 4, [TAGS['item']]),
    'heart_pie': Inventory.Item('Heart Pie', 'Increase regeneration.\nDuration: 15s', 'heart_pie', 4, [TAGS['item']]),

    'weak_healing_potion': Inventory.Item('Weak Healing Potion', 'Recover 50 HP\nCausing potion sickness.',
                                          'weak_healing_potion', 0, [TAGS['item'], TAGS['healing_potion']]),
    'weak_magic_potion': Inventory.Item('Weak Magic Potion', 'Recover 60 MP\nCausing potion sickness.',
                                        'weak_magic_potion', 0, [TAGS['item'], TAGS['magic_potion']]),
    'crabapple': Inventory.Item('Crabapple', 'Heals 120 HP', 'crabapple', 2, [TAGS['item'], TAGS['healing_potion']]),
    'butterscotch_pie': Inventory.Item('Butterscotch Pie', 'Heals 240 HP', 'butterscotch_pie', 4,
                                       [TAGS['item'], TAGS['healing_potion']]),
    'seatea': Inventory.Item('Seatea', 'Recovers 150 MP', 'seatea', 4, [TAGS['item'], TAGS['magic_potion']]),
    'tension_bit': Inventory.Item('Tension Bit', 'Recover 400 MP', 'tension_bit', 6, [TAGS['item'], TAGS['magic_potion']]),
    'snowman_piece': Inventory.Item('Snowman Piece', 'Recover all MP', 'snowman_piece', 6, [TAGS['item'], TAGS['healing_potion']]),
    'toilet_paper': Inventory.Item('Toilet Paper', 'Recover all TP', 'toilet_paper', 7, [TAGS['item'], TAGS['healing_potion']]),
    'legendary_hero': Inventory.Item('Legendary Hero', 'Hero shaped sandwich.\nRecover 500 HP and adds a 800 HP shield', 'legendary_hero', 8, [TAGS['item'], TAGS['healing_potion']]),

    'mana_crystal': Inventory.Item('Mana Crystal', '+15 maximum mana.', 'mana_crystal', 2, [TAGS['item']]),
    'firy_plant': Inventory.Item('Firy Plant', '+20 maximum hp', 'firy_plant', 3, [TAGS['item']]),
    'white_guard': Inventory.Item('White Guard', 'Add a 20 hp shield', 'white_guard', 2, [TAGS['item']]),
    'spiritual_heart': Inventory.Item('Spiritual Heart',
                                      '+100 maximum hp\n+180 maximum mana\nSomething perseverance happen.',
                                      'spiritual_heart', 4, [TAGS['item']]),
    'life_fruit': Inventory.Item('Life Fruit', '+400 maximum HP\n+500 maximum MP\n+40 maximum talent', 'life_fruit', 4,
                                 [TAGS['item']]),
    'saint_apple': Inventory.Item('Life Fruit', '+900 maximum HP\n700 maximum MP\n+20 maximum talent', 'saint_apple', 7,
                                 [TAGS['item']]),
    'mind_ball': Inventory.Item('Mind Ball', '+1500 maximum HP\n+50 maximum mentality', 'mind_ball', 10,
                                 [TAGS['item']]),

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
    'wild_fluffball': Inventory.Item('Wild Fluffball', 'Summon the fluffff', 'wild_fluffball', 0, [TAGS['item']]),
    'fire_slime': Inventory.Item('Fire Slime', 'Summon the magma king', 'fire_slime', 0, [TAGS['item']]),
    'red_apple': Inventory.Item('Red Apple', 'Summon the world\'s fruit', 'red_apple', 0, [TAGS['item']]),
    'wind': Inventory.Item('Wind', 'Summon the sandstorm', 'wind', 0, [TAGS['item']]),
    'blood_substance': Inventory.Item('Blood Substance', 'Summon the Abyss Eye', 'blood_substance', 0, [TAGS['item']]),
    'sky_painting': Inventory.Item('Sky Painting', 'Summon the sky tri-kubes', 'sky_painting', 0, [TAGS['item']]),
    'green_thing': Inventory.Item('Green Thing', 'Summon the heaven goblins.', 'green_thing', 0, [TAGS['item']]),
    'mechanic_eye': Inventory.Item('Mechanic Eye', 'Summon the twin eyes', 'mechanic_eye', 0, [TAGS['item']]),
    'mechanic_worm': Inventory.Item('Mechanic Worm', 'Summon the destroyer', 'mechanic_worm', 0, [TAGS['item']]),
    'electric_unit': Inventory.Item('Electric Unit', 'Summon the CPU', 'electric_unit', 0, [TAGS['item']]),
    'mechanic_spider': Inventory.Item('Electric Spider', 'Summon the Greed', 'mechanic_spider', 0, [TAGS['item']]),
    'watch': Inventory.Item('Watch', 'Summon the eye of time', 'watch', 0, [TAGS['item']]),
    'metal_food': Inventory.Item('Metal Food', 'Summon the devil python', 'metal_food', 0, [TAGS['item']]),
    'joker': Inventory.Item('JOKER', 'Summon the Joker Evil', 'joker', 0, [TAGS['item']]),
    'plantera_bulb': Inventory.Item('Plantera Bulb', 'Summon Plantera', 'plantera_bulb', 0, [TAGS['item']]),
    'yellow_flower': Inventory.Item('Yellow Flower', 'Final.', 'yellow_flower', 12, [TAGS['item']]),

    'mechanical': Inventory.Item('Mechanical',
                                 'This is just made by metals combining together.\nSummon the mechanic medusa.',
                                 'mechanical', 0, [TAGS['item']]),
    'dark_skull': Inventory.Item('Dark Skull', 'Summon the Wither', 'dark_skull', 0, [TAGS['item']]),
    'plastic_flower': Inventory.Item('Plastic Flower', 'Summon the Life Watcher', 'plastic_flower', 0, [TAGS['item']]),
    'huge_snowball': Inventory.Item('Huge Snowball', 'Summon the Polar Cube', 'huge_snowball', 0, [TAGS['item']]),

    'dragon_horn': Inventory.Item('Dragon Horn', 'Summon dragons around the world.', 'dragon_horn', 8, [TAGS['item']]),
    'poison_horn': Inventory.Item('Poison Horn', 'Summon the naga', 'poison_horn', 9, [TAGS['item']]),
    'ends_sphere': Inventory.Item('End\'s Sphere', 'Final', 'ends_sphere', 12, [TAGS['item']]),

    'finale__soul': Inventory.Item('Finale: Soul', 'The finale is the the start.\nStart Chapter 2.', 'finale__soul', 13, [TAGS['item']]),

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
                return not self.is_valid(inv)
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
    Recipe({'iron_ingot': 6, 'steel_ingot': 6, 'anvil': 1}, 'shuriken'),
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
    Recipe({'platinum_ingot': 25, 'mana_crystal': 12}, 'star_amulet'),
    Recipe({'star_amulet': 1, 'snowstorm_bottle': 1}, 'starstorm_bottle'),

    Recipe({'blood_ingot': 18, 'anvil': 1}, 'bloody_traveller_boots'),
    Recipe({'platinum_ingot': 10, 'blood_ingot': 20, 'anvil': 1}, 'bloody_sword'),
    Recipe({'platinum_ingot': 12, 'blood_ingot': 32, 'anvil': 1}, 'blood_pike'),
    Recipe({'platinum_ingot': 6, 'blood_ingot': 24, 'anvil': 1}, 'bloody_bow'),
    Recipe({'platinum_ingot': 6, 'flufffur': 8, 'anvil': 1}, 'fluffy_pluvial'),
    Recipe({'platinum_ingot': 12, 'flufffur': 7, 'anvil': 1}, 'fur_spear'),
    Recipe({'platinum_ingot': 6, 'flufffur': 12, 'anvil': 1}, 'ice_shard'),
    Recipe({'wood': 20, 'leaf': 20, 'coniferous_leaf': 50, 'blood_ingot': 32, 'anvil': 1}, 'forests_bow'),
    Recipe({'platinum_ingot': 8, 'blood_ingot': 16, 'mana_crystal': 1, 'anvil': 1}, 'blood_wand'),
    Recipe({'blood_ingot': 5, 'platinum_ingot': 5, 'anvil': 1}, 'blood_arrow', 100),
    Recipe({'blood_ingot': 2, 'platinum_ingot': 1, 'anvil': 1}, 'plasma', 50),
    Recipe({'blood_ingot': 8, 'firite_ingot': 22, 'anvil': 1}, 'firite_spear'),
    Recipe({'firy_plant': 1, 'firite_ingot': 24, 'anvil': 1}, 'fire_eye'),
    Recipe({'blood_ingot': 5, 'firite_ingot': 30, 'anvil': 1}, 'magma_assaulter'),
    Recipe({'firite_ingot': 25, 'platinum': 20, 'anvil': 1}, 'volcano'),
    Recipe({'firite_ingot': 18, 'platinum': 28, 'anvil': 1}, 'grenade'),
    Recipe({'firite_ingot': 64, 'platinum_ingot': 16, 'anvil': 1}, 'firite_helmet'),
    Recipe({'firite_ingot': 64, 'platinum_ingot': 16, 'anvil': 1}, 'firite_cloak'),
    Recipe({'firite_ingot': 64, 'platinum_ingot': 16, 'anvil': 1}, 'firite_pluvial'),
    Recipe({'fairy_wings': 1, 'hermes_boots': 1, 'lucky_clover': 2}, 'fairy_boots'),
    Recipe({'obsidian_ingot': 28}, 'obsidian_sword'),
    Recipe({'obsidian_ingot': 24}, 'obsidian_wand'),
    Recipe({'obsidian_ingot': 32}, 'obsidian_knife'),
    Recipe({'platinum': 24, 'blood_ingot': 16, 'magic_stone': 10, 'firy_plant': 1, 'anvil': 1}, 'hematology'),
    Recipe({'platinum': 24, 'magic_stone': 6, 'firite_ingot': 8, 'firy_plant': 2, 'anvil': 1}, 'fire_magic_sword'),
    Recipe({'magic_stone': 10, 'firy_plant': 1}, 'crabapple', 5),
    Recipe({'blood_ingot': 12, 'cell_organization': 6, 'firy_plant': 6}, 'twilight_shortsword'),
    Recipe({'mysterious_substance': 4, 'furnace': 1}, 'mysterious_ingot'),
    Recipe({'mysterious_ingot': 12, 'magic_stone': 6, 'mana_crystal': 6}, 'dawn_shortsword'),
    Recipe({'platinum_ingot': 30, 'mysterious_ingot': 5, 'anvil': 1}, 'winds_necklace'),
    Recipe({'mysterious_ingot': 12, 'anvil': 1}, 'recurve_bow'),
    Recipe({'mysterious_ingot': 10, 'blood_ingot': 8, 'anvil': 1}, 'sand_sword'),
    Recipe({'mysterious_ingot': 18, 'platinum': 28, 'anvil': 1, 'grenade': 1}, 'jade_grenade'),
    Recipe({'mysterious_ingot': 32, 'platinum': 16, 'anvil': 1}, 'grenade_kings_jade_mask'),
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
    Recipe({'storm_core': 1, 'starstorm_bottle': 1, 'snow_wings': 1}, 'soarer_bottle'),
    Recipe({'storm_core': 1, 'thiefs_charm': 1, 'winds_necklace': 1}, 'storm_charm'),
    Recipe({'gorgeous_ring': 1, 'magnificent_ring': 1, 'storm_core': 1}, 'red_ring'),

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
    Recipe({'palladium_ingot': 15, 'mithrill_anvil': 1}, 'palladium_glove'),
    Recipe({'mithrill_ingot': 15, 'mithrill_anvil': 1}, 'mithrill_glove'),
    Recipe({'titanium_ingot': 15, 'mithrill_anvil': 1}, 'titanium_glove'),
    Recipe({'mithrill_ingot': 18, 'mithrill_anvil': 1}, 'soul_resonancer'),
    Recipe({'red_ring': 1, 'palladium_ingot': 20, 'mithrill_ingot': 20, 'titanium_ingot': 20,
            'soul': 50, 'mithrill_anvil': 1}, 'red_spirit_ring'),
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
    Recipe({'wings': 1, 'starlight_shard': 5}, 'star_wings'),
    Recipe({'terrified_necklace': 1, 'starlight_shard': 5}, 'guardian_necklace'),
    Recipe({'copper_traveller_boots': 1, 'starlight_shard': 12}, 'broken_copper_boots'),
    Recipe({'windstorm_assassin_mark': 1, 'daedalus_ingot': 5, 'mithrill_anvil': 1}, 'daedalus_mark'),
    Recipe({'evil_book': 1, 'dark_ingot': 8, 'mithrill_anvil': 1}, 'curse_book'),
    Recipe({'saint_steel_ingot': 6, 'soul_of_integrity': 20, 'mithrill_anvil': 1}, 'ballet_shoes'),
    Recipe({'soul_bottle': 1, 'soul_resonancer': 1, 'soul_of_integrity': 18, 'mithrill_anvil': 1}, 'unregretted_heart'),
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
    Recipe({'mystery_core': 2, 'soul_of_integrity': 1}, 'tension_bit', 20),
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
    Recipe({'shotgun': 1, 'daedalus_ingot': 15, 'soul_of_justice': 25, 'soul_of_bravery': 10},
           'justice_shotgun'),
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
    Recipe({'fairy_boots': 1, 'chlorophyte_ingot': 12, 'photon': 24}, 'life_boots'),
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
    Recipe({'chaos_ingot': 32, 'firite_ingot': 100}, 'great_forbidden_curse__fire'),
    Recipe({'chaos_ingot': 32, 'photon': 100, 'soul_of_integrity': 8,
            'soul_of_bravery': 8, 'soul_of_kindness': 8, 'soul_of_perseverance': 8,
            'soul_of_patience': 8, 'soul_of_justice': 8}, 'great_forbidden_curse__light'),
    Recipe({'true_nights_edge': 1, 'true_excalibur': 1, 'perseverance_sword': 1,
            'life_devourer': 1, 'jevil_knife': 1}, 'the_blade'),
    Recipe({'remote_sword': 1, 'soul_of_preseverence': 10}, 'wilson_knife'),
    Recipe({'muramasa': 1, 'remote_sword': 1, 'black_hole_sword': 1, 'chaos_ingot': 12}, 'demon_blade__muramasa'),
    Recipe({'chaos_ingot': 88, 'jevil_knife': 1}, 'chaos_chaos'),
    Recipe({'chaos_ingot': 128, 'soul_of_patience': 64}, 'great_magicians_hat'),
    Recipe({'chaos_ingot': 128, 'soul_of_justice': 64, 'quiver': 1}, 'chaos_quiver'),
    Recipe({'chaos_ingot': 128, 'soul_of_perseverance': 64, 'sheath': 1}, 'chaos_sheath'),
    Recipe({'chaos_ingot': 32, 'soarer_bottle': 1, 'magic_anklet': 1, 'mana_flower': 1}, 'the_chaos_flower_vase'),
    Recipe({'chaos_ingot': 50, 'fire_eye': 1, 'rune_eye': 1, 'photon_aimer': 1, 'photon': 24}, 'chaos_evileye'),
    Recipe({'chaos_ingot': 50, 'fire_gloves': 1, 'rune_gloves': 1, 'palladium_gloves': 1, 'mithrill_gloves': 1,
            'titanium_gloves': 1, 'tough_gloves': 1, 'guardian_necklace': 1}, 'starnight_gloves'),
    Recipe({'chaos_ingot': 50, 'broken_copper_boots': 1, 'lava_walker': 1,
            'life_boots': 1, 'guardian_necklace': 1}, 'corrupt_boots'),

    Recipe({'chaos_ingot': 128, 'storm_core': 32}, 'primal__winds_wand'),
    Recipe({'chaos_ingot': 128, 'blood_ingot': 512, 'cell_organization': 128}, 'primal__life_wand'),

    Recipe({'photon': 100, 'chlorophyll': 1}, 'lights_bible'),
    Recipe({'lights_bible': 1,'photon': 1}, 'light_purify'),
    Recipe({'soul': 20, 'chlorophyll': 1, 'soul_of_patience': 10}, 'energy_bible'),

    Recipe({'soul': 1, 'soul_of_flying': 1, 'soul_of_coldness': 1, 'soul_of_growth': 1, 'soul_of_bravery': 1,
            'soul_of_kindness': 1, 'soul_of_integrity': 1, 'soul_of_perseverance': 1, 'soul_of_patience': 1,
            'soul_of_justice': 1, 'willpower_shard': 1}, 'soul_of_determination'),
    Recipe({'soul_of_determination': 1, 'photon': 10}, 'legendary_hero', 36),
    Recipe({'soul_of_determination': 1, 'soul_of_coldness': 10}, 'snowman_piece', 50),
    Recipe({'chaos_ingot': 200, 'soul_of_determination': 12, 'origin': 1}, 'magisters_hat'),
    Recipe({'origin': 1, 'chaos_ingot': 25}, 'chaos_heart'),
    Recipe({'chaos_ingot': 240, 'red_spirit_ring': 1, 'soul_of_determination': 20}, 'determined_ring'),
    Recipe({'chaos_ingot': 500, 'soul_of_determination': 8, 'wierd_essence': 36}, 'uncanny_valley'),
    Recipe({'chaos_ingot': 300, 'soul_of_determination': 12, 'wierd_essence': 32}, 'death_note'),
    Recipe({'chaos_ingot': 300, 'soul_of_determination': 12, 'wierd_essence': 32}, 'great_forbidden_curse__dark'),
    Recipe({'chaos_ingot': 300, 'soul_of_determination': 12, 'wierd_essence': 32}, 'great_forbidden_curse__evil'),
    Recipe({'chaos_ingot': 1200, 'soul_of_determination': 20, 'wierd_essence': 20}, 'demon_contract'),
    Recipe({'chaos_ingot': 1200, 'soul_of_determination': 20, 'wierd_essence': 20}, 'demon_wings'),
    Recipe({'chaos_ingot': 500, 'soul_of_determination': 8, 'time_essence': 36}, 'hour_hand'),
    Recipe({'chaos_ingot': 300, 'soul_of_determination': 12, 'time_essence': 32}, 'stop'),
    Recipe({'chaos_ingot': 250, 'time_essence': 54, 'soul_of_determination': 20,
            'wings': 1, 'fairy_wings': 1, 'snow_wings': 1, 'star_wings': 1}, 'altitude'),
    Recipe({'chaos_ingot': 1200, 'soul_of_determination': 20, 'time_essence': 20}, 'time_shackle'),
    Recipe({'chaos_ingot': 1200, 'soul_of_determination': 20, 'time_essence': 20}, 'time_wheel'),
    Recipe({'chaos_ingot': 500, 'soul_of_determination': 8, 'substance_essence': 36}, 'deconstruction'),
    Recipe({'chaos_ingot': 600, 'soul_of_determination': 6, 'substance_essence': 40}, 'matter_disintegrator'),
    Recipe({'chaos_ingot': 1200, 'soul_of_determination': 20, 'substance_essence': 20}, 'ultradense_shield'),
    Recipe({'chaos_ingot': 1200, 'soul_of_determination': 20, 'substance_essence': 20}, 'matters_touch'),
    Recipe({'chaos_ingot': 500, 'soul_of_determination': 8, 'light_essence': 36}, 'starfury'),
    Recipe({'chaos_ingot': 250, 'soul_of_determination': 16, 'light_essence': 54,
            'chaos_evileye': 1}, 'horizon_goggles'),
    Recipe({'chaos_ingot': 1200, 'soul_of_determination': 20, 'light_essence': 20}, 'black_hole_pluvial'),
    Recipe({'chaos_ingot': 1200, 'soul_of_determination': 20, 'light_essence': 20}, 'star_statue'),
    Recipe({'chaos_ingot': 600, 'soul_of_determination': 8, 'time_essence': 36, 'time_fountain': 1}, 'metal_hand'),
    Recipe({'chaos_ingot': 720, 'soul_of_determination': 6, 'time_essence': 40, 'time_fountain': 1}, 'time_flies'),
    Recipe({'chaos_ingot': 720, 'soul_of_determination': 6, 'time_essence': 40, 'time_fountain': 1}, 'accelerationism'),
    Recipe({'chaos_ingot': 2400, 'soul_of_determination': 15, 'time_essence': 60, 'time_fountain': 1}, 'flashback'),
    Recipe({'chaos_ingot': 600, 'soul_of_determination': 8, 'substance_essence': 36, 'substance_fountain': 1},
           'lysis'),
    Recipe({'chaos_ingot': 2400, 'soul_of_determination': 15, 'substance_essence': 60, 'substance_fountain': 1}, 'matter_floatboard'),
    Recipe({'chaos_ingot': 600, 'soul_of_determination': 8, 'light_essence': 36, 'celestial_fountain': 1}, 'star_wrath'),
    Recipe({'chaos_ingot': 360, 'soul_of_determination': 12, 'light_essence': 32, 'celestial_fountain': 1}, 'sun_pearl'),
    Recipe({'chaos_ingot': 30, 'soul_of_determination': 1, 'light_essence': 2}, 'scorching_arrow', 100),
    Recipe({'chaos_ingot': 30, 'soul_of_determination': 1, 'substance_essence': 2, 'substance_fountain': 1}, 'seperator', 100),
    Recipe({'chaos_ingot': 360, 'soul_of_determination': 12, 'wierd_essence': 32, 'celestial_fountain': 1}, 'great_forbidden_curse__water'),

    Recipe({'soul_of_determination': 25, 'time_fountain': 1, 'substance_fountain': 1, 'celestial_fountain': 1}, 'my_soul'),
    Recipe({'my_soul': 1, 'wings': 1}, 'rudder'),
    Recipe({'chaos_ingot': 200, 'soul_of_determination': 20, 'my_soul': 1,
            'time_fountain': 1, 'substance_fountain': 1, 'celestial_fountain': 1}, 'destruct_thoughts'),
    Recipe({'copper_ingot': 1, 'iron_ingot': 1, 'steel_ingot': 1, 'platinum_ingot': 1, 'blood_ingot': 1,
            'firite_ingot': 1, 'mysterious_ingot': 1, 'palladium_ingot': 1, 'mithrill_ingot': 1,
            'titanium_ingot': 1, 'chlorophyte_ingot': 1, 'chaos_ingot': 1, 'wooden_hammer': 1,
            'anvil': 1, 'furnace': 1, 'mithrill_anvil': 1, 'chlorophyll': 1, 'time_fountain': 1,
            'substance_fountain': 1, 'celestial_fountain': 1, 'my_soul': 1, 'reason': 4, 'result': 4},
           'the_final_ingot'),
    Recipe({'the_final_ingot': 32, 'determined_ring': 1, 'my_soul': 1}, 'my_ring'),
    Recipe({'the_final_ingot': 18, 'my_soul': 1}, 'galaxy_broadsword'),
    Recipe({'the_final_ingot': 16, 'my_soul': 1}, 'highlight'),
    Recipe({'the_final_ingot': 22, 'my_soul': 1}, 'turning_point'),
    Recipe({'the_final_ingot': 25, 'my_soul': 1}, 'resolution'),
    Recipe({'the_final_ingot': 21, 'my_soul': 1}, 'climax'),
    Recipe({'the_final_ingot': 15, 'my_soul': 1}, 'falling_action'),
    Recipe({'the_final_ingot': 19, 'my_soul': 1}, 'rising_action'),

    Recipe({'galaxy_broadsword': 1, 'my_soul': 1, 'death_fountain': 1, 'the_final_ingot': 6}, 'eternal_echo'),
    Recipe({'galaxy_broadsword': 1, 'my_soul': 1, 'no_fountain': 1, 'the_final_ingot': 6}, 'star_of_devotion'),
    Recipe({'rising_action': 1, 'my_soul': 1, 'death_fountain': 1, 'the_final_ingot': 6}, 'relevation_of_cycles'),

    Recipe({'altitude': 1, 'demon_wings': 1, 'time_wheel': 1, 'black_hole_pluvial': 1, 'matter_floatboard': 1,
            'daedalus_mark': 1, 'soul_of_flying': 99, 'my_soul': 1, 'the_final_ingot': 5}, 'ultra_lightspeed'),
    Recipe({'starnight_gloves': 1, 'flashback': 1, 'matters_touch': 1, 'thorn_ring': 1, 'my_ring': 1,
            'origin': 9, 'my_soul': 1, 'the_final_ingot': 5}, 'grasp_of_the_infinite_corridor'),
    Recipe({'corrupt_boots': 1, 'ultradense_shield': 1, 'time_shackle': 1, 'magic_anklet': 1,
            'rudder': 1, 'mysterious_ingot': 99, 'my_soul': 1, 'the_final_ingot': 5}, 'karmic_trail_boots'),
    Recipe({'the_chaos_flower_vase': 1, 'horizon_goggles': 1, 'flashback': 1, 'demon_contract': 1, 'seed_amulet': 1,
            'lucky_clover': 9, 'my_soul': 1, 'the_final_ingot': 5}, 'fate_alignment_amulet'),

    Recipe({'copper_sword': 1, 'doctor_expeller': 1, 'demon_blade__muramasa': 1, 'the_blade': 1, 'uncanny_valley': 1,
            'star_wrath': 1, 'lysis': 1, 'galaxy_broadsword': 1, 'turning_point': 1}, 'zenith'),
    Recipe({'bravery_amulet': 1, 'kindness_amulet': 1, 'integrity_amulet': 1, 'perseverance_amulet': 1,
            'patience_amulet': 1, 'justice_amulet': 1, 'the_final_ingot': 10, 'my_soul': 1}, 'heart_locket'),
    Recipe({'the_final_ingot': 6, 'time_fountain': 1, 'substance_fountain': 1, 'celestial_fountain': 1,
            'death_fountain': 1, 'no_fountain': 1, 'my_soul': 1, 'plantera_bulb': 1}, 'yellow_flower'),

    Recipe({'wood': 36, 'wooden_hammer': 1}, 'wooden_pickaxe'),
    Recipe({'copper_ingot': 28, 'anvil': 1}, 'copper_pickaxe'),
    Recipe({'iron_ingot': 22, 'steel_ingot': 22, 'anvil': 1}, 'heavy_pickaxe'),
    Recipe({'platinum_ingot': 32, 'magic_stone': 12, 'anvil': 1}, 'platinum_pickaxe'),
    Recipe({'blood_ingot': 28, 'platinum_ingot': 16, 'anvil': 1}, 'bloody_pickaxe'),
    Recipe({'firite_ingot': 32, 'blood_ingot': 16, 'anvil': 1}, 'firite_pickaxe'),
    Recipe({'mysterious_ingot': 20, 'anvil': 1}, 'mystery_pickaxe'),
    Recipe({'evil_ingot': 20, 'soul': 24}, 'evil_pickaxe'),
    Recipe({'palladium_ingot': 24, 'mithrill_ingot': 20, 'titanium_ingot': 24, 'mithrill_anvil': 1, 'soul': 40},
           'tough_pickaxe'),
    Recipe({'tough_pickaxe': 1, 'soul_of_integrity': 20, 'soul_of_bravery': 20, 'soul_of_kindness': 20},
           'true_pickaxe'),
    Recipe({'chlorophyte_ingot': 28, 'anvil': 1}, 'light_pickaxe'),

    Recipe({'mana_crystal': 1, 'seatea': 15, 'muse_core': 1}, 'note'),
    Recipe({'platinum_ingot': 56, 'note': 1}, 'gold_fine'),
    Recipe({'mysterious_ingot': 24, 'note': 1}, 'ancient_flute'),
    Recipe({'storm_core': 2, 'mysterious_substance': 20, 'note': 1}, 'storm_harp'),
    Recipe({'mysterious_substance': 30, 'note': 1}, 'note_sheet'),
    Recipe({'firite_ingot': 40, 'firy_plant': 18, 'note': 1}, 'red_formal_hat'),
    Recipe({'storm_core': 4, 'note': 1}, 'windstorm_musicians_mark'),
    Recipe({'strength_ingot': 18, 'note': 1}, 'snare'),
    Recipe({'sight_ingot': 18, 'note': 1}, 'watcher_bell'),
    Recipe({'phantom_ingot': 17, 'apple_knife': 1, 'note': 1}, 'apple_smells_good'),
    Recipe({'phantom_ingot': 24, 'strength_ingot': 24, 'sight_ingot': 24, 'storm_core': 12, 'note': 1}, 'holy_stormer'),
    Recipe({'strength_ingot': 18, 'dark_substance': 5, 'note': 1}, 'wither_oboe'),
    Recipe({'note': 1, 'phantom_ingot': 30, 'strength_ingot': 30}, 'instrument_belt'),

    Recipe({'blood_ingot': 44, 'bible': 1}, 'saint_healer'),
    Recipe({'mysterious_substance': 12, 'torch': 1, 'bible': 1}, 'holy_shine'),
    Recipe({'mysterious_substance': 32, 'mana_flower': 1, 'bible': 1}, 'the_gods_penalty'),
    Recipe({'blood_ingot': 64, 'life_flower': 1, 'bible': 1}, 'great_heal'),
    Recipe({'mysterious_ingot': 32, 'bible': 1, 'mana_crystal': 2, 'seed_amulet': 1}, 'cross_amulet'),
    Recipe({'iron_ingot': 32, 'steel_ingot': 32, 'bible': 1}, 'grey_hood'),
    Recipe({'storm_core': 4, 'bible': 1}, 'windstorm_churchs_mark'),
    Recipe({'sight_ingot': 18, 'bible': 1}, 'the_prayer'),
    Recipe({'strength_ingot': 18, 'bible': 1}, 'the_true_gods_penalty'),
    Recipe({'sight_ingot': 28, 'strength_ingot': 24, 'bible': 1}, 'holy_light'),
    Recipe({'bible': 1, 'strength_ingot': 30, 'sight_ingot': 30}, 'cross_pluvial'),

    Recipe({'z': 1, 'mysterious_ingot': 12, 'platinum_ingot': 48}, 'mystery_watch'),
    Recipe({'z': 1, 'mysterious_ingot': 25, 'blood_ingot': 25}, 'hand_of_pacify'),
    Recipe({'z': 1, 'mysterious_ingot': 32, 'glowing_splint': 1}, 'sleep_splint'),
    Recipe({'z': 1, 'blood_ingot': 32, 'rune_eye': 1}, 'eye_of_sleep'),
    Recipe({'z': 1, 'mysterious_substance': 10, 'cell_organization': 12}, 'hypnotists_tie'),
    Recipe({'z': 1, 'storm_core': 4}, 'windstorm_pacifiers_mark'),
    Recipe({'z': 1, 'sight_ingot': 18, 'mysterious_ingot': 20}, 'sleep_eye'),
    Recipe({'z': 1, 'sight_ingot': 25, 'colourful_substance': 4}, 'good_dream'),
    Recipe({'z': 1, 'strength_ingot': 25, 'dark_substance': 4}, 'nightmare'),
    Recipe({'z': 1, 'phantom_ingot': 30, 'sight_ingot': 30}, 'talent_cloat'),

    Recipe({'soul_resonancer': 1, 'sight_ingot': 24}, 'vision_resonancer'),
    Recipe({'soul_resonancer': 1, 'strength_ingot': 24}, 'strength_resonancer'),
    Recipe({'soul_resonancer': 1, 'phantom_ingot': 24}, 'photon_resonancer'),
    Recipe({'wither_rib': 3, 'iris_shard': 3, 'freezing_ice': 3,
            'dark_substance': 1, 'colourful_substance': 1, 'cold_substance': 1,
            'strength_ingot': 5, 'sight_ingot': 5, 'phantom_ingot': 5}, 'hallow_ingot', 5),
    Recipe({'hallow_ingot': 12}, 'saint_apple'),

    Recipe({'hallow_ingot': 3, 'chlorophyll': 1}, 'chlorophyte_ingot', 2),
    Recipe({'soul_resonancer': 1, 'hallow_ingot': 12}, 'hallow_resonancer'),
    Recipe({'soul_resonancer': 1, 'chlorophyte_ingot': 12}, 'life_resonancer'),

    Recipe({'vision_resonancer': 1, 'strength_resonancer': 1, 'photon_resonancer': 1,
            'hallow_resonancer': 1, 'life_resonancer': 1, 'willpower_shard': 6}, 'worldsaver_necklace', 4),

    Recipe({'dragon_bone': 36}, 'dragon_swift_sword'),
    Recipe({'dragon_skull': 1, 'dragon_bow': 18}, 'dragon_bow'),
    Recipe({'dragon_bone': 28}, 'dragon_flute'),

    Recipe({'dragon_scale_gray': 16, 'dragon_scale_red': 10, 'dragon_scale_blue': 10,
            'dragon_scale_black': 10, 'dragon_scale_yellow': 10, 'dragon_scale_green': 10,
            'mechanic_dragon_heart': 2, 'mechanic_dragon_blood': 8, 'dragon_bone': 300}, 'dragon_reactor'),
    Recipe({'dragon_skull': 1, 'fire_dragon_heart': 1, 'fire_dragon_blood': 8}, 'fire_heating_unit'),
    Recipe({'dragon_skull': 1, 'ice_dragon_heart': 1, 'ice_dragon_blood': 8}, 'ice_heating_unit'),
    Recipe({'dragon_skull': 1, 'dark_dragon_heart': 1, 'dark_dragon_blood': 8}, 'dark_heating_unit'),
    Recipe({'dragon_skull': 1, 'light_dragon_heart': 1, 'light_dragon_blood': 8}, 'light_heating_unit'),
    Recipe({'dragon_skull': 1, 'mind_dragon_heart': 1, 'mind_dragon_blood': 8}, 'mind_cooling_unit'),

    Recipe({'dragon_swift_sword': 1, 'fire_dragon_blood': 12}, 'fire_quench__dragon_sword'),
    Recipe({'dragon_bow': 1, 'fire_dragon_blood': 12}, 'fire_quench__dragon_bow'),
    Recipe({'dragon_swift_sword': 1, 'ice_dragon_blood': 12}, 'ice_quench__dragon_sword'),
    Recipe({'dragon_bow': 1, 'ice_dragon_blood': 12}, 'ice_quench__dragon_bow'),
    Recipe({'dragon_swift_sword': 1, 'dark_dragon_blood': 12}, 'dark_quench__dragon_sword'),
    Recipe({'dragon_bow': 1, 'dark_dragon_blood': 12}, 'dark_quench__dragon_bow'),
    Recipe({'dragon_swift_sword': 1, 'light_dragon_blood': 12}, 'light_quench__dragon_sword'),
    Recipe({'dragon_bow': 1, 'light_dragon_blood': 12}, 'light_quench__dragon_bow'),
    Recipe({'dragon_flute': 1, 'fire_dragon_blood': 15}, 'dance_of_fire'),
    Recipe({'dragon_flute': 1, 'ice_dragon_blood': 15}, 'dance_of_frost'),
    Recipe({'dragon_flute': 1, 'dark_dragon_blood': 15}, 'dance_of_shadow'),
    Recipe({'dragon_flute': 1, 'light_dragon_blood': 15}, 'dance_of_shine'),
    Recipe({'dragon_flute': 1, 'fire_dragon_blood': 6, 'ice_dragon_blood': 6}, 'the_song_of_ice_and_fire'),

    Recipe({'fire_dragon_heart': 1, 'fire_dragon_blood': 4, 'dragon_bone': 20}, 'fire_dragon_breath_wand'),
    Recipe({'ice_dragon_heart': 1, 'ice_dragon_blood': 4, 'dragon_bone': 20}, 'ice_dragon_breath_wand'),
    Recipe({'dark_dragon_heart': 1, 'dark_dragon_blood': 4, 'dragon_bone': 20}, 'dark_dragon_breath_wand'),
    Recipe({'light_dragon_heart': 1, 'light_dragon_blood': 4, 'dragon_bone': 20}, 'light_dragon_breath_wand'),

    Recipe({'fire_dragon_heart': 1, 'dragon_bone': 50, 'fire_dragon_blood': 8}, 'fire_dragon_cross'),
    Recipe({'ice_dragon_heart': 1, 'dragon_bone': 50, 'ice_dragon_blood': 8}, 'ice_dragon_cross'),
    Recipe({'dark_dragon_heart': 1, 'dragon_bone': 50, 'dark_dragon_blood': 8}, 'dark_dragon_cross'),
    Recipe({'light_dragon_heart': 1, 'dragon_bone': 50, 'light_dragon_blood': 8}, 'light_dragon_cross'),
    Recipe({'mechanic_dragon_heart': 1, 'dragon_bone': 50, 'mechanic_dragon_blood': 8}, 'true_cyber_dragon_cross'),
    Recipe({'mind_dragon_heart': 1, 'dragon_bone': 50,'mind_dragon_blood': 8}, 'true_mind_dragon_cross'),
    Recipe({'fire_dragon_cross': 1, 'fire_dragon_ingot': 12}, 'true_fire_dragon_cross'),
    Recipe({'ice_dragon_cross': 1, 'ice_dragon_ingot': 12}, 'true_ice_dragon_cross'),
    Recipe({'dark_dragon_cross': 1, 'dark_dragon_ingot': 12}, 'true_dark_dragon_cross'),
    Recipe({'light_dragon_cross': 1, 'light_dragon_ingot': 12}, 'true_light_dragon_cross'),
    Recipe({'mind_dragon_blood': 2}, 'mind_ball'),

    Recipe({'dragon_reactor': 1, 'fire_heating_unit': 1, 'mind_cooling_unit': 1, 'chaos_ingot': 1, 'hallow_ingot': 1, 'fire_dragon_blood': 1},
           'fire_dragon_ingot'),
    Recipe({'dragon_reactor': 1, 'ice_heating_unit': 1, 'mind_cooling_unit': 1, 'chaos_ingot': 1, 'hallow_ingot': 1, 'ice_dragon_blood': 1},
           'ice_dragon_ingot'),
    Recipe({'dragon_reactor': 1, 'dark_heating_unit': 1, 'mind_cooling_unit': 1, 'chaos_ingot': 1, 'hallow_ingot': 1, 'dark_dragon_blood': 1},
           'dark_dragon_ingot'),
    Recipe({'dragon_reactor': 1, 'light_heating_unit': 1, 'mind_cooling_unit': 1, 'chaos_ingot': 1, 'hallow_ingot': 1, 'light_dragon_blood': 1},
           'light_dragon_ingot'),

    Recipe({'fire_dragon_ingot': 8, 'ice_dragon_ingot': 8, 'dark_dragon_ingot': 8, 'light_dragon_ingot': 8, 'dragon_bone': 400},
           'the_ruling_sword'),
    Recipe({'fire_dragon_ingot': 8, 'ice_dragon_ingot': 8, 'dark_dragon_ingot': 8, 'light_dragon_ingot': 8, 'dragon_bone': 400},
           'the_fairy_bow'),
    Recipe({'fire_dragon_ingot': 8, 'ice_dragon_ingot': 8, 'dark_dragon_ingot': 8, 'light_dragon_ingot': 8, 'dragon_bone': 400},
           'the_magisters_wand'),
    Recipe({'fire_dragon_ingot': 8, 'ice_dragon_ingot': 8, 'dark_dragon_ingot': 8, 'light_dragon_ingot': 8, 'dragon_bone': 400},
           'the_godfall_poem'),

    Recipe({'ice_dragon_ingot': 18}, 'eternal_hush'),
    Recipe({'dark_dragon_ingot': 18}, 'voidstride_treads'),
    Recipe({'fire_dragon_ingot': 18}, 'vermillion_sigil_palms'),
    Recipe({'light_dragon_ingot': 18}, 'aurora_dawn'),

    Recipe({'fire_dragon_ingot': 3, 'ice_dragon_ingot': 3, 'dark_dragon_ingot': 3, 'light_dragon_ingot': 3}, 'ends_sphere'),

    Recipe({'palladium_ingot': 6, 'mithrill_ingot': 6, 'titanium_ingot': 6,
            'note': 1, 'bible': 1, 'z': 1}, 'mechanical'),
    Recipe({'strength_ingot': 20, 'dark_substance': 3}, 'dark_skull'),
    Recipe({'sight_ingot': 20, 'colourful_substance': 3}, 'plastic_flower'),
    Recipe({'phantom_ingot': 20, 'cold_substance': 3}, 'huge_snowball'),
    Recipe({'chaos_ingot': 100, 'willpower_shard': 5}, 'dragon_horn'),
    Recipe({'dragon_horn': 1, 'origin': 1}, 'poison_horn'),

    Recipe({'the_final_soul': 15, 'murders_knife': 1, 'savior': 1}, 'finale__soul'),

    Recipe({'platinum_ingot': 36, 'mana_crystal': 1, 'anvil': 1}, 'rocket_launcher'),
    Recipe({'mysterious_ingot': 18, 'storm_core': 1}, 'rapid_rocket_launcher'),
    Recipe({'soul': 16, 'mithrill_ingot': 24, 'mithrill_anvil': 1}, 'rocket_launcher_v2'),
    Recipe({'note': 1, 'mithrill_ingot': 24, 'mithrill_anvil': 1}, 'rocket_launcher_v2'),
    Recipe({'soul_of_integrity': 12, 'daedalus_ingot': 24, 'mithrill_anvil': 1}, 'rapid_rocket_launcher_v2'),
    Recipe({'strength_ingot': 24, 'mithrill_anvil': 1}, 'rapid_rocket_launcher_v2'),
    Recipe({'hallow_ingot': 24}, 'rocket_launcher_v3'),
    Recipe({'daedalus_ingot': 20, 'soul_of_justice': 8}, 'rocket_launcher_v3'),
    Recipe({'chlorophyte_ingot': 18, 'shotgun': 1}, 'rapid_rocket_launcher_v3'),
    Recipe({'chaos_ingot': 120, 'willpower_shard': 12}, 'rocket_launcher_v4'),
    Recipe({'the_final_ingot': 15}, 'rapid_rocket_launcher_max'),
    Recipe({'fire_dragon_ingot': 6, 'ice_dragon_ingot': 6, 'dark_dragon_ingot': 6, 'light_dragon_ingot': 6, 'dragon_bone': 200},
           'rapid_rocket_launcher_max'),

    Recipe({'wood': 10}, 'wooden_helmet'),
    Recipe({'wood': 6}, 'wooden_mask'),
    Recipe({'wood': 24}, 'wooden_chestplate'),
    Recipe({'wood': 15}, 'wooden_greaves'),

    Recipe({'copper_ingot': 15}, 'copper_helmet'),
    Recipe({'copper_ingot': 9}, 'copper_mask'),
    Recipe({'copper_ingot': 36}, 'copper_chestplate'),
    Recipe({'copper_ingot': 23}, 'copper_greaves'),

    Recipe({'iron_ingot': 12}, 'iron_helmet'), 
    Recipe({'iron_ingot': 11}, 'iron_mask'),
    Recipe({'iron_ingot': 29}, 'iron_chestplate'),
    Recipe({'iron_ingot': 18}, 'iron_greaves'),

    Recipe({'steel_ingot': 12}, 'steel_helmet'),
    Recipe({'steel_ingot': 11}, 'steel_mask'),
    Recipe({'steel_ingot': 27}, 'steel_chestplate'),
    Recipe({'steel_ingot': 18}, 'steel_greaves'),

    Recipe({'platinum_ingot': 11}, 'platinum_helmet'),
    Recipe({'platinum_ingot': 7}, 'platinum_mask'),
    Recipe({'platinum_ingot': 27}, 'platinum_chestplate'),
    Recipe({'platinum_ingot': 18}, 'platinum_greaves'),

    Recipe({'blood_ingot': 6}, 'bloody_helmet'),
    Recipe({'blood_ingot': 5}, 'bloody_mask'),
    Recipe({'blood_ingot': 27}, 'bloody_chestplate'),
    Recipe({'blood_ingot': 14}, 'bloody_greaves'),

    Recipe({'firite_ingot': 7}, 'firy_helmet'),
    Recipe({'firite_ingot': 6}, 'firy_mask'),
    Recipe({'firite_ingot': 26}, 'firy_chestplate'),
    Recipe({'firite_ingot': 16}, 'firy_greaves'),

    Recipe({'mysterious_ingot': 4}, 'mysterious_helmet'),
    Recipe({'mysterious_ingot': 3}, 'mysterious_mask'),
    Recipe({'mysterious_ingot': 11}, 'mysterious_chestplate'),
    Recipe({'mysterious_ingot': 7}, 'mysterious_greaves'),

    Recipe({'titanium_ingot': 7, 'palladium_ingot': 7}, 'merged_metal_helmet'),
    Recipe({'palladium_ingot': 7, 'mithrill_ingot': 7}, 'merged_metal_mask'),
    Recipe({'mithrill_ingot': 7, 'titanium_ingot': 7}, 'merged_metal_headgear'),
    Recipe({'palladium_ingot': 16, 'mithrill_ingot': 16, 'titanium_ingot': 16}, 'merged_metal_chestplate'),
    Recipe({'palladium_ingot': 5, 'mithrill_ingot': 5, 'titanium_ingot': 5}, 'merged_metal_greaves'),

    Recipe({'chlorophyte_ingot': 8}, 'chloro_formal_hat'),
    Recipe({'mysterious_ingot': 12}, 'chloro_chestplate'),
    Recipe({'mysterious_ingot': 6}, 'chloro_leggings'),

    Recipe({'chaos_ingot': 20}, 'chaos_hood'),
    Recipe({'chaos_ingot': 30}, 'chaos_chestplate'),
    Recipe({'chaos_ingot': 15}, 'chaos_leggings'),

    Recipe({'chaos_ingot': 120, 'willpower_shard': 3}, 'godkiller_helmet'),
    Recipe({'chaos_ingot': 180, 'willpower_shard': 5}, 'godkiller_chestplate'),
    Recipe({'chaos_ingot': 100, 'willpower_shard': 2}, 'godkiller_leggings'),

    Recipe({'the_final_ingot': 8, 'my_soul': 1}, 'karmic_helmet'),
    Recipe({'the_final_ingot': 12, 'my_soul': 1}, 'karmic_chestplate'),
    Recipe({'the_final_ingot': 6, 'my_soul': 1}, 'karmic_leggings'),

    Recipe({'hallow_ingot': 12}, 'hallowed_helmet'),
    Recipe({'hallow_ingot': 12}, 'hallowed_mask'),
    Recipe({'hallow_ingot': 12}, 'hallowed_headgear'),
    Recipe({'hallow_ingot': 16}, 'hallowed_plate_mail'),
    Recipe({'hallow_ingot': 8}, 'hallowed_greaves'),

    Recipe({'worldsaver_necklace': 1, 'hallow_ingot': 8, 'chaos_ingot': 100, 'willpower_shard': 2}, 'worldsaver_hood'),
    Recipe({'worldsaver_necklace': 1, 'hallow_ingot': 12, 'chaos_ingot': 150, 'willpower_shard': 3}, 'worldsaver_chestplate'),
    Recipe({'worldsaver_necklace': 1, 'hallow_ingot': 6, 'chaos_ingot': 80, 'willpower_shard': 1}, 'worldsaver_leggings'),

    Recipe({'dragon_scale_red': 16}, 'dragon_helmet_red'),
    Recipe({'dragon_scale_red': 24}, 'dragon_chestplate_red'),
    Recipe({'dragon_scale_red': 8}, 'dragon_leggings_red'),

    Recipe({'dragon_scale_blue': 16}, 'dragon_helmet_blue'),
    Recipe({'dragon_scale_blue': 24}, 'dragon_chestplate_blue'),
    Recipe({'dragon_scale_blue': 8}, 'dragon_leggings_blue'),

    Recipe({'dragon_scale_black': 16}, 'dragon_helmet_black'),
    Recipe({'dragon_scale_black': 24}, 'dragon_chestplate_black'),
    Recipe({'dragon_scale_black': 8}, 'dragon_leggings_black'),

    Recipe({'dragon_scale_yellow': 16}, 'dragon_helmet_yellow'),
    Recipe({'dragon_scale_yellow': 24}, 'dragon_chestplate_yellow'),
    Recipe({'dragon_scale_yellow': 8}, 'dragon_leggings_yellow'),

    Recipe({'dragon_scale_gray': 16}, 'dragon_helmet_gray'),
    Recipe({'dragon_scale_gray': 24}, 'dragon_chestplate_gray'),
    Recipe({'dragon_scale_gray': 8}, 'dragon_leggings_gray'),

    Recipe({'dragon_scale_green': 16}, 'dragon_helmet_green'),
    Recipe({'dragon_scale_green': 24}, 'dragon_chestplate_green'),
    Recipe({'dragon_scale_green': 8}, 'dragon_leggings_green'),

    Recipe({'cell_organization': 20}, 'suspicious_eye'),
    Recipe({'cell_organization': 2, 'flufffur': 12}, 'wild_fluffball'),
    Recipe({'cell_organization': 10, 'firite_ingot': 25}, 'fire_slime'),
    Recipe({'cell_organization': 10, 'leaf': 20}, 'red_apple'),
    Recipe({'cell_organization': 10, 'mysterious_substance': 20}, 'wind'),
    Recipe({'cell_organization': 20, 'storm_core': 3}, 'blood_substance'),
    Recipe({'palladium_ingot': 5, 'mithrill_ingot': 5, 'titanium_ingot': 5, 'soul_of_flying': 5}, 'sky_painting'),
    Recipe({'palladium_ingot': 5, 'mithrill_ingot': 5, 'titanium_ingot': 5, 'soul_of_flying': 5}, 'green_thing'),
    Recipe({'palladium_ingot': 5, 'mithrill_ingot': 5, 'titanium_ingot': 5, 'bible': 1}, 'green_thing'),
    Recipe({'palladium_ingot': 5, 'mithrill_ingot': 5, 'titanium_ingot': 5, 'soul': 10}, 'mechanic_eye'),
    Recipe({'mithrill_ingot': 5, 'titanium_ingot': 5, 'palladium_ingot': 5, 'soul': 10}, 'mechanic_worm'),
    Recipe({'titanium_ingot': 5, 'palladium_ingot': 5, 'mithrill_ingot': 5, 'soul': 10}, 'electric_unit'),
    Recipe({'palladium_ingot': 2, 'soul_of_kindness': 12}, 'mechanic_spider'),
    Recipe({'mithrill_ingot': 2, 'soul_of_integrity': 12}, 'watch'),
    Recipe({'titanium_ingot': 2, 'soul_of_bravery': 12}, 'metal_food'),
    Recipe({'chlorophyte_ingot': 10, 'photon': 4}, 'joker'),
    Recipe({'hallow_ingot': 10, 'strength_ingot': 4}, 'joker'),
    Recipe({'substance_essence': 50}, 'suspicious_substance'),

]


def setup():
    for i, item in enumerate(ITEMS.values()):
        item.inner_id = i


def get_item_by_id(item_id: int):
    return [item for item in ITEMS.values() if item.inner_id == item_id][0]


setup()
