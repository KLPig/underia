import math
import random
import datetime

import pygame as pg

from physics import mover, vector
from resources import position, cursors, errors, path
from underia import game, styles, inventory, weapons, entity, projectiles, player_profile, notebook
from values import hp_system, damages, effects, WeakManaI, ManaDrain
import constants
from visual import draw, fade_circle as fc
import underia3

status = []

class PlayerObject(mover.Mover):
    MASS = 20
    FRICTION = 0.9
    SPEED = 20

    def __init__(self, *args):
        super().__init__(*args)
        self.lt = self.pos.to_value()

    def on_update(self):
        keys = game.get_game().get_pressed_keys()
        dt = self.pos - self.lt
        self.lt = self.pos.to_value()
        game.get_game().player.profile.skill_points['traveler'] += abs(dt) / 30
        if pg.K_w in keys:
            self.apply_force(vector.Vector(0, self.SPEED / 2))
        elif pg.K_s in keys:
            self.apply_force(vector.Vector(180, self.SPEED / 2))
        if pg.K_a in keys:
            self.apply_force(vector.Vector(270, self.SPEED / 2))
        elif pg.K_d in keys:
            self.apply_force(vector.Vector(90, self.SPEED / 2))

THAUMATURGY_RECIPES = [
    (['feather_sword', 'hoverplume_headgear', 'hoverplume_back', 'hoverplume_kneepads', 'feather_amulet', 'toxic_wing'],
     inventory.Recipe({'thaumaturgy': 1, 'feather_sword': 1, 'hoverplume_headgear': 1, 'hoverplume_back': 1,
                       'hoverplume_kneepads': 1, 'feather_amulet': 1, 'toxic_wing': 1}, 'pluma_thaumaturgy')),
    (['life_hood', 'life_cloak', 'life_hboots', 'talent_fruit', 'poise_necklace', 'moonflower'],
     inventory.Recipe({'thaumaturgy': 1, 'life_hood': 1, 'life_cloak': 1, 'life_hboots': 1, 'talent_fruit': 1,
                       'poise_necklace': 1,'moonflower': 1}, 'bioic_thaumaturgy')),
    (['ration_helmet', 'ration_chestplate', 'ration_boots', 'proof', 'winds_anklet', 'cute_watch'],
     inventory.Recipe({'ration_helmet': 1, 'ration_chestplate': 1, 'ration_boots': 1,
                      'proof': 1, 'winds_anklet': 1, 'cute_watch': 1}, 'logos_thaumaturgy'),),
    (['heaven_wooden_headgear', 'heaven_wooden_chestplate', 'heaven_wooden_leggings', 'heaven_shotgun',
      'holy_condense_wand', 'the_roving_chord'],
     inventory.Recipe(
         {'heaven_wooden_headgear': 1, 'heaven_wooden_chestplate': 1, 'heaven_wooden_leggings': 1,
          'heaven_shotgun': 1, 'holy_condense_wand': 1, 'the_roving_chord': 1}, 'dendro_thaumaturgy'),
     )
]


class Player:
    REGENERATION = 0.015
    MAGIC_REGEN = 0.04
    TASKS = [
        ('Get tips from recipe book', ['tip0', 'tip1'], 2),
        ('Get a wooden item', ['wooden_sword', 'bow', 'glowing_splint'], 1),
        ('Find a furnace and some copper', ['furnace', 'copper'], 2),
        ('Melt a copper ingot and craft an anvil', ['copper_ingot', 'anvil'], 2),
        ('Get better ingots', ['iron', 'steel', 'iron_ingot', 'steel_ingot'], 4),
        ('Use better metal tools', ['iron_sword', 'steel_sword', 'spear',
                                    'iron_blade', 'iron_wand', 'iron_bow',
                                    'pistol', 'rifle', 'steel_bow', 'bullet',
                                    'shield'], 3),
        ('Get cell organizations from bloody creatures', ['cell_organization',
                                                          'soul_bottle', 'weak_healing_potion',
                                                          'terrified_necklace'], 2),
        ('Get well improved by new materials', ['platinum', 'platinum_ingot',
                                                'platinum_sword', 'platinum_blade',
                                                'platinum_spear', 'platinum_wand',
                                                'life_wooden_sword', 'life_wooden_wand',
                                                'platinum_bow', 'submachine_gun',
                                                'platinum_bullet', 'magic_stone',
                                                'mana_crystal', 'magic_arrow',
                                                'burning_book', 'talent_book',
                                                'magic_anklet', 'weak_magic_potion',
                                                'magic_sword', 'magic_blade',
                                                'night_visioner'], 7),
        ('Summon and kill The Eye', ['suspicious_eye', 'tip2', 'blood_ingot'], 3),
        ('Summon and kill The Magma King', ['fire_slime', 'tip3', 'firite_ingot', 'firy_plant'], 4),
        ('Get mysterious things', ['mysterious_substance', 'mysterious_ingot'], 2),
        ('Summon and kill The Storm', ['wind', 'tip4', 'storm_core'], 3),
        ('Summon and kill The Abyss Eye', ['blood_substance', 'tip5', 'soul',
                                           'spiritual_stabber', 'spiritual_piercer',
                                           'spiritual_destroyer'], 4),
        ('Change the world', ['spiritual_heart'], 1),
        ('Adapt the new world', ['tip61', 'tip62', 'tip63', 'soul_of_flying', 'soul_of_coldness', 'soul_of_growth',
                                 'evil_ingot', 'balanced_stabber', 'discord_storm', 'evil_book', 'palladium',
                                 'mithrill', 'titanium'], 8),
        ('Advance', ['mithrill_ingot', 'palladium_ingot', 'titanium_ingot', 'saint_steel_ingot',
                     'daedalus_ingot', 'dark_ingot', 'mithrill_anvil'], 4),
        ('Collect souls', ['soul_of_integrity', 'soul_of_bravery', 'soul_of_kindness',
                           'soul_of_perseverance', 'soul_of_patience', 'soul_of_justice',
                           'tip71', 'tip72', 'tip73', 'tip8', 'tip9'], 11),
        ('Make photosynthesis', ['chlorophyll', 'photon', 'chlorophyte_ingot'], 3),
        ('Get a plantera bulb from the inner world', ['joker', 'plantera_bulb', 'chaos_ingot'], 3),
        ('Kill a plantera', ['plantera_bulb', 'origin', 'willpower_shard'], 3),
        ('Become a legend', ['soul_of_determination'], 1),
        ('Go to the inner world', ['chaos_heart'], 1),
        ('Collect essences', ['time_essence', 'substance_essence', 'wierd_essence', 'light_essence',
                              'time_fountain', 'substance_fountain', 'celestial_fountain'], 7),
        ('Find MYSELF', ['my_soul'], 1),
        ('Find the karma', ['reason', 'result'], 2),
        ('Merge the final ingot', ['the_final_ingot'], 1),
        ('Collect the final...', ['death_fountain', 'no_fountain'], 2)

    ]

    def __init__(self):
        self.obj = PlayerObject((400, 300))
        self.hp_sys = hp_system.HPSystem(200)
        self.ax, self.ay = 0, 0
        self.weapons = 4 * [weapons.WEAPONS['null']]
        self.sel_weapon = 0
        self.inventory = inventory.Inventory()
        self.accessories = 10 * ['null']
        self.sel_accessory = 0
        self.open_inventory = False
        self.open_chest = None
        self.attack = 0
        self.mana = 0
        self.max_mana = 30
        self.recipes = []
        self.sel_recipe = 0
        self.light_level = 0
        self.ammo = ('null', 0)
        self.ammo_bullet = ('null', 0)
        self.attacks = [1, 1, 1, 1, 1]
        self.in_ui = False
        self.touched_item = ''
        self.hp_sys(op='config', immune_time=10, true_drop_speed_max_value=1)
        self.talent = 0
        self.max_talent = 0
        self.strike = 0
        self.scale = 1.0
        self.profile = player_profile.PlayerProfile()
        self.ntcs = []
        self.tutorial_step = 0
        self.tutorial_process = 0
        self.top_notice = ''
        self.owned_items = []
        self.t_ntc_timer = 200
        self.p_data = []
        self.domain_size = 1.0
        self.splint_distance = 0
        self.splint_t = 0
        self.splint_cd = 0
        self.max_inspiration = 0
        self.inspiration = 0
        self.good_karma = 0
        self.ui_tasks = False
        self.ui_attributes = False
        self.ui_recipes = False
        self.ui_recipe_overlook = False
        self.ui_recipe_view = False
        self.mouse: tuple[str, int] = ('null', 0)
        self.cd_z = 0
        self.cd_x = 0
        self.cd_c = 0
        self.z = 0
        self.boot_footprints: list[vector.Vector2D] = []
        self.covered_items = []
        self.major_usage = 0.0
        self.afterimage_shadow = 0
        self.inv_capacity = 48
        self.tick = 0
        self.inv_pos = 0
        self.shield_break = 0.0
        self.nts = []
        self.cc_t = 0

    def calculate_regeneration(self):
        ACCESSORY_REGEN = {}
        if self.hp_sys.hp < self.hp_sys.max_hp * 0.6:
            ACCESSORY_REGEN['terrified_necklace'] = -0.0075
        regen = 0
        for i in range(len(self.accessories)):
            if self.accessories[i] in ACCESSORY_REGEN.keys():
                regen += ACCESSORY_REGEN[self.accessories[i]]
        return regen

    def calculate_magic_regeneration(self):
        regen = 1
        regen *= 1.0 + int(self.profile.point_wisdom ** 1.1) / 400
        return regen

    def calculate_damage(self):
        dmg = 1.0 + int(self.profile.point_strength ** 1.1) / 400
        return dmg

    def calculate_speed(self):
        spd = 1.0
        spd *= 1.0 + int(self.profile.point_agility ** 1.1) / 400
        return spd

    def calculate_melee_damage(self):
        dmg = 1.0
        if self.profile.point_melee <= 0:
            dmg *= 0.91 ** abs(self.profile.point_melee)
        else:
            dmg *= 1 + self.profile.point_melee ** 1.1 / 400
        return dmg

    def calculate_ranged_damage(self):
        dmg = 1.0
        if self.profile.point_ranged <= 0:
            dmg *= 0.91 ** abs(self.profile.point_ranged)
        else:
            dmg *= 1 + self.profile.point_ranged ** 1.1 / 400
        return dmg

    def calculate_magic_damage(self):
        dmg = 1.0
        if self.profile.point_magic <= 0:
            dmg *= 0.91 ** abs(self.profile.point_magic)
        else:
            dmg *= 1 + self.profile.point_magic ** 1.1 / 400
        return dmg

    def friction_mult(self):
        nf = 1
        b = game.get_game().get_biome()
        if b == 'fallen_sea':
            nf *= 3
        if b == 'hot_spring':
            nf *= 4
        if b == 'inner':
            nf *= 2.5
        if b in ['heaven', 'hell']:
            nf *= .5
        if b in ['sea', 'ocean']:
            nf *= 1.75
        if nf > 1:
            anf = nf - 1
            anf *= self.calculate_data('bio_fric', True, rate_multiply=True)
            nf = 1 + anf
        return nf

    def calculate_data(self, data_idx, rate_data, rate_plus = False, rate_multiply = False):
        if rate_plus == rate_multiply and rate_data:
            raise ValueError('Rate chooses exactly one strategy.')
        if rate_data:
            val = 1.0
        else:
            val = 0.0
        for i in range(len(self.accessories)):
            inventory.ITEMS[self.accessories[i]].update_data()
            if data_idx in inventory.ITEMS[self.accessories[i]].accessory_data.keys():
                d_r = self.major_usage if not data_idx == 'armor' and inventory.TAGS['major_accessory'] in inventory.ITEMS[self.accessories[i]].tags else 1.0
                if d_r != 1 and data_idx == 'touch_def':
                    d_r = 1
                if rate_plus:
                    val += inventory.ITEMS[self.accessories[i]].accessory_data[data_idx] * d_r / 100
                elif rate_multiply:
                    val *= (inventory.ITEMS[self.accessories[i]].accessory_data[data_idx] * d_r + 100) / 100
                else:
                    val += inventory.ITEMS[self.accessories[i]].accessory_data[data_idx] * d_r
        for e in self.hp_sys.effects:
            if data_idx in e.datas.keys():
                if rate_plus:
                    val += e.datas[data_idx] / 100
                elif rate_multiply:
                    val *= (e.datas[data_idx] + 100) / 100
                else:
                    val += e.datas[data_idx]
        if 'shield' in status:
            if data_idx.endswith('def'):
                val += val // 5
        if 'un-shield' in status:
            if data_idx.endswith('def'):
                val -= 9999
        if 'strength' in data_idx:
            if data_idx == 'damage':
                val *= 5
        if 'critical' in data_idx:
            if data_idx == 'crit':
                val += 1000
        if 'un-strength' in data_idx:
            if data_idx == 'damage':
                val = 0
        if 'un-mana' in data_idx:
            if data_idx == 'max_mana':
                val = -self.max_mana + 1
        if 'mana-regen' in data_idx:
            if data_idx == 'mana_regen':
                val = self.max_mana
        if 'un-mana-regen' in data_idx:
            if data_idx == 'mana_regen':
                val = -self.max_mana
        if data_idx == 'mana_cost':
            val *= .5437
        return val

    def get_max_screen_scale(self):
        ACCESSORY_SIZE = {'aimer': 1.5, 'winds_necklace': 1.1, 'cowboy_hat': 1.4, 'photon_aimer': 4.5,
                          'cloudy_glasses': 1.2, 'chaos_evileye': 8, 'horizon_goggles': 20,
                          'fate_alignment_amulet': 30, '_developer_tool__sight': 999}
        t = 1.0
        for i in range(len(self.accessories)):
            if self.accessories[i] in ACCESSORY_SIZE.keys():
                t *= ACCESSORY_SIZE[self.accessories[i]]
        t *= 1 + 0.01 * self.profile.point_agility
        return t

    def get_screen_scale(self):
        return self.scale

    def get_light_level(self):
        if len([1 for e in game.get_game().entities if type(e) is entity.Entities.AbyssEye]):
            return 0
        if len([1 for accessory in self.accessories if
                inventory.TAGS['light_source'] in inventory.ITEMS[accessory].tags]):
            b = 5
        else:
            b = 0
        if self.weapons[self.sel_weapon] is weapons.WEAPONS['nights_edge']:
            b = max(0, b - 4)
        if self.weapons[self.sel_weapon] is weapons.WEAPONS['true_nights_edge']:
            b = max(0, b - 4)
        return b

    def get_night_vision(self):
        if len([1 for accessory in self.accessories if
                inventory.TAGS['night_vision'] in inventory.ITEMS[accessory].tags]):
            b = 50
        else:
            b = 0
        if self.weapons[self.sel_weapon] is weapons.WEAPONS['nights_edge']:
            b = max(0, b - 20)
        if self.weapons[self.sel_weapon] is weapons.WEAPONS['true_nights_edge']:
            b = max(0, b - 10)
        return b

    def calculate_strike_chance(self):
        return 0.08

    def update(self):
        self.shield_break *= [.6, .9, .96, .99][constants.DIFFICULTY]
        try:
            self.inv_pos
        except AttributeError:
            self.inv_pos = 0
        if self.open_inventory or self.open_chest is not None:
            self.inv_pos = self.inv_pos * 5 // 6
        elif self.inv_pos < 900:
            self.inv_pos = (self.inv_pos * 9 + 1000) // 10
        else:
            self.inv_pos = (self.inv_pos * 9 + 2000) // 10
        self.tick += 1
        self.ntcs = []
        self.p_data = []
        self.top_notice = ''
        if 'melee_demand' in self.profile.select_skill:
            self.hp_sys.effect(effects.MeleeDemand(5, 1))
        if 'ranged_demand' in self.profile.select_skill:
            self.hp_sys.effect(effects.RangedDemand(5, 1))
        if 'magic_demand' in self.profile.select_skill:
            self.hp_sys.effect(effects.MagicDemand(5, 1))
        if 'melee_reinforce_i' in self.profile.select_skill:
            self.hp_sys.effect(effects.MeleeReinforceI(5, 1))
        if 'melee_reinforce_ii' in self.profile.select_skill:
            self.hp_sys.effect(effects.RangedReinforceII(5, 1))
        if 'melee_reinforce_iii' in self.profile.select_skill:
            self.hp_sys.effect(effects.MeleeReinforceIII(5, 1))
        if 'melee_reinforce_iv' in self.profile.select_skill:
            self.hp_sys.effect(effects.MeleeReinforceIV(5, 1))
        if 'ranged_reinforce_i' in self.profile.select_skill:
            self.hp_sys.effect(effects.RangedReinforceI(5, 1))
        if 'ranged_reinforce_ii' in self.profile.select_skill:
            self.hp_sys.effect(effects.RangedReinforceII(5, 1))
        if 'ranged_reinforce_iii' in self.profile.select_skill:
            self.hp_sys.effect(effects.RangedReinforceIII(5, 1))
        if 'ranged_reinforce_iv' in self.profile.select_skill:
            self.hp_sys.effect(effects.RangedReinforceIV(5, 1))
        if 'magic_reinforce_i' in self.profile.select_skill:
            self.hp_sys.effect(effects.MagicReinforceI(5, 1))
        if 'magic_reinforce_ii' in self.profile.select_skill:
            self.hp_sys.effect(effects.MagicReinforceII(5, 1))
        if 'magic_reinforce_iii' in self.profile.select_skill:
            self.hp_sys.effect(effects.MagicReinforceIII(5, 1))
        if 'magic_reinforce_iv' in self.profile.select_skill:
            self.hp_sys.effect(effects.MagicReinforceIV(5, 1))
        am = self.calculate_data('wing_control', False) / 100
        if pg.K_SPACE in game.get_game().get_pressed_keys():
            self.z = (self.z * 2 - am) / 3
        elif pg.K_LSHIFT in game.get_game().get_pressed_keys():
            self.z = (self.z * 2 + am) / 3
        else:
            self.z *= 2 / 3
        if self.t_ntc_timer > 0:
            self.t_ntc_timer -= 1
        if self.tutorial_step < 5:
            self.t_ntc_timer = 200
            self.top_notice = 'Tutorial: ' + [
                'Move with WASD',
                'Open your inventory with E',
                'Attack with mouse',
                'Craft items by clicking in the right',
                'Equip accessories and weapons'
            ][self.tutorial_step] + f'({round(self.tutorial_process)}%)'
            if self.tutorial_process >= 100:
                self.tutorial_step += 1
                self.tutorial_process = 0
        elif self.tutorial_step < len(self.TASKS) + 5:
            notice, items, items_num = self.TASKS[self.tutorial_step - 5]
            cnt = sum([1 for i in items if i in self.owned_items])
            if self.tutorial_process != cnt / items_num * 100:
                self.t_ntc_timer = 200
            self.tutorial_process = cnt / items_num * 100
            if self.tutorial_process >= 100:
                self.tutorial_step += 1
                self.tutorial_process = 0
                self.t_ntc_timer = 400
            self.top_notice = f'Task: {notice}({round(self.tutorial_process)}%)'
            self.ntcs.append('Item collection: ' + notice)
            self.ntcs.append(f'Required any {items_num} out of {len(items)}.')
            self.ntcs.append(f'Entity image saving: {entity.entity_get_surface.cache_info().hits}/'
                             f'{entity.entity_get_surface.cache_info().hits + entity.entity_get_surface.cache_info().misses}'
                             f'({entity.entity_get_surface.cache_info().hits * 100 / 
                                 (entity.entity_get_surface.cache_info().hits + entity.entity_get_surface.cache_info().misses)
                             if entity.entity_get_surface.cache_info().currsize else 0:.2f}%)'
                             f', MEM: {entity.entity_get_surface.cache_info().currsize}')
            self.ntcs.append(f'Projectile image saving: {projectiles.projectile_get_surface.cache_info().hits}/'
                             f'{projectiles.projectile_get_surface.cache_info().hits + projectiles.projectile_get_surface.cache_info().misses}'
                             f'({projectiles.projectile_get_surface.cache_info().hits * 100 / 
                                 (projectiles.projectile_get_surface.cache_info().hits + projectiles.projectile_get_surface.cache_info().misses)
                             if projectiles.projectile_get_surface.cache_info().currsize else 0:.2f}%)'
                             f', MEM: {projectiles.projectile_get_surface.cache_info().currsize}')
            self.ntcs.append(f'Weapon sweep image: {weapons.Weapon.get_cut_surf.cache_info().hits}/'
                             f'{weapons.Weapon.get_cut_surf.cache_info().hits + weapons.Weapon.get_cut_surf.cache_info().misses}'
                             f'({weapons.Weapon.get_cut_surf.cache_info().hits * 100 / 
                                 (weapons.Weapon.get_cut_surf.cache_info().hits + weapons.Weapon.get_cut_surf.cache_info().misses)
                             if weapons.Weapon.get_cut_surf.cache_info().currsize else 0:.2f}%)'
                             f', MEM: {weapons.Weapon.get_cut_surf.cache_info().currsize}')
            self.ntcs.append(f'Map image: {game.get_game().get_chunked_images.cache_info().hits}/'
                             f'{game.get_game().get_chunked_images.cache_info().hits + game.get_game().get_chunked_images.cache_info().misses}'
                             f'({game.get_game().get_chunked_images.cache_info().hits * 100 / 
                                (game.get_game().get_chunked_images.cache_info().hits + game.get_game().get_chunked_images.cache_info().misses)
                             if game.get_game().get_chunked_images.cache_info().currsize else 0:.2f}%)')

            for i in items:
                if i not in self.owned_items:
                    self.ntcs.append(f'->{i.replace('_', ' ')}')
                else:
                    self.ntcs.append(f'->{i.replace('_', ' ')}(Done)')
        for i in self.inventory.items.keys():
            if i not in self.owned_items:
                self.owned_items.append(i)
        if self.tutorial_step == 0:
            if len([1 for k in [pg.K_w, pg.K_a, pg.K_s, pg.K_d] if k in game.get_game().get_pressed_keys()]):
                self.tutorial_process += .2
        if self.tutorial_step == 1:
            if pg.K_e in game.get_game().get_keys():
                self.tutorial_process += 100
        if pg.K_t in game.get_game().get_keys():
            self.t_ntc_timer = 200
        if self.tutorial_step == 2:
            if 1 in game.get_game().get_mouse_press():
                self.tutorial_process += 10
        maj_def = inventory.ITEMS[self.accessories[3]].accessory_data['touch_def'] / 2 \
            if 'touch_def' in inventory.ITEMS[self.accessories[3]].accessory_data.keys()  else 0
        arm = self.calculate_data('armor', rate_data=False)
        self.major_usage = arm / maj_def if maj_def else 0
        if self.major_usage > 1.5:
            self.major_usage = 0
        self.p_data.append(f'{arm} armor={int(self.major_usage * 100)}%')
        self.talent = min(self.talent + 0.005 + math.sqrt(self.max_talent) / 2000 + (self.max_talent - self.talent) / 1000, self.max_talent * (1 + int(self.profile.point_wisdom ** 1.1) / 800))
        self.hp_sys.pos = self.obj.pos
        self.attack = math.sqrt(self.calculate_damage() * self.calculate_data('damage', rate_data=True, rate_multiply=True))

        mn = self.mana / self.max_mana
        if mn <= 1:
            self.attack *= 1 - (1 - mn) ** 2
        self.strike = 0.08 + math.sqrt(max(0, self.calculate_data('crit', False))) / 100
        self.attacks = [self.calculate_melee_damage() * self.calculate_data('melee_damage', rate_data=True, rate_multiply=True),
                        self.calculate_ranged_damage() * self.calculate_data('ranged_damage', rate_data=True, rate_multiply=True),
                        self.calculate_magic_damage() * self.calculate_data('magic_damage', rate_data=True, rate_multiply=True),
                        self.calculate_data('octave_damage', rate_data=True, rate_multiply=True),
                        self.calculate_data('hallow_damage', rate_data=True, rate_multiply=True),
                        self.calculate_data('pacify_damage', rate_data=True, rate_multiply=True)]
        dr = .5
        if game.get_game().stage > 1:
            dr = 1.0
        elif game.get_game().stage == 1:
            dr = .8
        for i in range(len(self.attacks)):
            self.attacks[i] = max(0.001, self.attacks[i]) ** dr
        if 'black_hole_pluvial' in self.accessories:
            for e in game.get_game().entities:
                px, py = self.obj.pos[0] - e.obj.pos[0], self.obj.pos[1] - e.obj.pos[1]
                e.obj.velocity.add(vector.Vector(vector.coordinate_rotation(px, py), self.obj.velocity.get_net_value() / 40))

        if 'karmic_trail_boots' in self.accessories:
            self.boot_footprints.append((self.obj.pos[0], self.obj.pos[1]))
            if len(self.boot_footprints) > 63:
                self.boot_footprints.pop(0)
            cols = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 255, 255), (0, 0, 255),
                    (255, 0, 255), (255, 0, 0)]
            ccols = []
            for i in range(1, 8):
                s_c = cols[i - 1]
                e_c = cols[i]
                for j in range(1, 10):
                    ccols.append((s_c[0] + (e_c[0] - s_c[0]) * j // 9, s_c[1] + (e_c[1] - s_c[1]) * j // 9,
                                  s_c[2] + (e_c[2] - s_c[2]) * j // 9))
            for i in range(len(self.boot_footprints) - 1, 1, -1):
                s_p = position.displayed_position(self.boot_footprints[i])
                e_p = position.displayed_position(self.boot_footprints[i - 1])
                draw.line(game.get_game().displayer.canvas, ccols[(len(self.boot_footprints) - 1 - 1 - i)], s_p, e_p,
                          int(i / self.get_screen_scale()))
                e_p = self.boot_footprints[i - 1]
                for e in game.get_game().entities:
                    if vector.distance(e.obj.pos[0] - e_p[0], e.obj.pos[1] - e_p[1]) < 80 and not e.hp_sys.is_immune:
                        e.hp_sys.damage(1500, damages.DamageTypes.THINKING)
                        e.obj.apply_force(
                            vector.Vector(vector.coordinate_rotation(e_p[0] - e.obj.pos[0], e_p[1] - e.obj.pos[1]),
                                          1000))
                        e.hp_sys.enable_immune()

        self.ntcs.append(f'{1000 / game.get_game().clock.last_tick:.2f}fps')
        self.p_data.append(f'{int(self.attacks[2] * self.attack * 100)}% magic')
        self.p_data.append(f'{int(self.attacks[1] * self.attack * 100)}% range')
        self.p_data.append(f'{int(self.attacks[0] * self.attack * 100)}% melee')
        if game.get_game().chapter >= 1:
            self.p_data.append(f'{int(self.attacks[3] * self.attack * 100)}% octave')
            self.p_data.append(f'{int(self.attacks[4] * self.attack * 100)}% hallow')
            self.p_data.append(f'{int(self.attacks[5] * self.attack * 100)}% pacify')
        self.attack *= 1 + (random.random() < self.strike) * (1 + self.strike) ** 2
        self.hp_sys.resistances[damages.DamageTypes.TOUCHING] = .8 / (self.calculate_data('damage_absorb', rate_data=True, rate_multiply=True) - .2)
        self.hp_sys.resistances[damages.DamageTypes.MAGICAL] = .8 / (self.calculate_data('damage_absorb', rate_data=True, rate_multiply=True) - .2)
        self.p_data.append(f'{100 - self.hp_sys.resistances[damages.DamageTypes.TOUCHING] * 100:.2f}% res.')
        self.p_data.append(f'{self.hp_sys.DODGE_RATE * 100:.2f}% dodge')
        self.p_data.append(f'->{int((1 + (1 + self.strike) ** 2) * 10000) / 100}% dmg.')
        self.p_data.append(f'{int(self.strike * 10000) / 100}% crit')
        self.obj.SPEED = self.calculate_data('speed', rate_data=True, rate_multiply=True) * 80 * self.calculate_speed()
        self.hp_sys.DODGE_RATE = max(0, 1 - 1 / (((self.calculate_speed() - 1) * 100) ** .7 / 100 + self.calculate_data('dodge_rate', rate_data=True, rate_multiply=True)) + bool(self.afterimage_shadow))
        nf = self.friction_mult()
        b = game.get_game().get_biome()
        d_t = constants.DIFFICULTY * 2 + constants.DIFFICULTY2 * 3 - 3
        nk = 'naturalify_necklace' in self.accessories
        if b == 'inner':
            if not nk:
                game.get_game().player.hp_sys.effect(effects.Wither(1, d_t * 3 + 5))
                game.get_game().player.hp_sys.effect(effects.Freezing(1, 1))
            if nk:
                game.get_game().player.hp_sys.effect(effects.SDarkened(1, 1))
            else:
                game.get_game().player.hp_sys.effect(effects.Darkened(1, 1))
        if b == 'hot_spring':
            game.get_game().player.hp_sys.effect(effects.Burning(1, d_t * 2 + 5 - nk * (5 * d_t)))
            if not nk:
                game.get_game().player.hp_sys.effect(effects.SDarkened(1, 1))
        if not nk:
            if b == 'hell':
                game.get_game().player.hp_sys.effect(effects.Burning(1, d_t + 1))
            if b == 'heaven':
                if constants.DIFFICULTY >= 1:
                    game.get_game().player.hp_sys.effect(effects.SEnlightened(1, 1))
            if b == 'desert':
                if constants.DIFFICULTY >= 2:
                    game.get_game().player.hp_sys.effect(effects.BleedingR(1, 1))
            if b == 'snow':
                if constants.DIFFICULTY >= 2:
                    game.get_game().player.hp_sys.effect(effects.SFreezing(1, 1))
        self.obj.FRICTION = max(0, 1 - nf * 0.1 * self.calculate_data('air_res', rate_data=True, rate_multiply=True) * (20 ** self.z))
        self.obj.MASS = max(40, 80 + self.calculate_data('mass', False))
        self.p_data.append(f'{int(self.obj.SPEED / 2) / 10} speed')
        if self.obj.velocity.get_net_value() / 20 > 500:
            entity.entity_spawn(entity.Entities.QuarkGhost, 2000, 2000, 0, 1145, 100000)
            self.obj.velocity.clear()
            game.get_game().dialog.dialog('The Quark Ghost prevents you from accelerating!')
        self.p_data.append(f'{self.calculate_data("mana_cost", True, rate_multiply=True) * 100:.0f}% mana cost')
        self.splint_distance = self.calculate_data('splint', False)
        self.splint_cd = self.calculate_data('splint_cd', True, rate_multiply=True) * 80
        if self.splint_distance:
            self.p_data.append(f'cd {self.splint_cd}s')
            self.splint_t = int(self.splint_t)
            if self.splint_t > 0:
                self.splint_t -= 1
            elif self.splint_t == 0:
                for i, d in enumerate([pg.K_w, pg.K_a, pg.K_s, pg.K_d]):
                    if d in game.get_game().get_keys():
                        self.splint_t = -1 - i
                        break
            elif self.splint_t > -10:
                f = 0
                for d in [pg.K_w, pg.K_a, pg.K_s, pg.K_d]:
                    if d in game.get_game().get_keys():
                        f = 1
                if not f:
                    self.splint_t -= 10
            else:
                i = (9 - self.splint_t % 10) % 10
                if self.splint_t < -400:
                    self.splint_t = 11
                rt = [0, 270, 180, 90]
                i = max(0, min(3, i))
                d = [pg.K_w, pg.K_a, pg.K_s, pg.K_d][i]
                if d in game.get_game().get_keys():
                    self.splint_t = self.splint_cd
                    self.obj.velocity += vector.Vector(rt[i], self.splint_distance * 4)
                    if 'logos_thaumaturgy' in self.accessories:
                        self.hp_sys.effect(effects.LogosThaumaturgy(3, 3))
                else:
                    self.splint_t -= 10
            self.p_data.append(f'{self.splint_distance} sprint')
        self.p_data.append(f'vel. {int(self.obj.velocity.get_net_value() / 2) / 10}('
                           f'{int(self.obj.velocity.get_net_rotation())}deg)')
        self.p_data.append(f'{-int(100 - self.obj.FRICTION * 100)}% air res.')
        self.p_data.append(f'{int(self.obj.MASS)} weight')
        if 'dendro_thaumaturgy' in self.accessories:
            self.hp_sys.MAXIMUM_DAMAGE = self.hp_sys.max_hp * .99
        else:
            self.hp_sys.MAXIMUM_DAMAGE = constants.INFINITY
        for w in weapons.WEAPONS.values():
            try:
                if w.domain_open:
                    self.ntcs.append(f'{w.name} is open.')
                    self.obj.FRICTION = 0
            except AttributeError:
                pass
        if 'beyond_horizon' in self.accessories and self.tick % 40 == 0:
            for e in game.get_game().entities:
                if 'd_byh' not in dir(e):
                    e.d_byh = 1
                    e.obj.SPEED *= .2
        self.domain_size = self.calculate_data('domain_size', True, rate_multiply=True)
        mtp_regen = self.calculate_data('mentality_regen', False)
        self.REGENERATION = 0.015 + self.calculate_regeneration() + self.calculate_data('regen', rate_data=False) / 1000 * game.get_game().clock.last_tick
        self.MAGIC_REGEN = self.calculate_magic_regeneration() * (0.04 + self.calculate_data('mana_regen', rate_data=False) / 120.0)
        if len([1 for ef in self.hp_sys.effects if type(ef) is WeakManaI]):
            self.MAGIC_REGEN *= 0.5
        if len([1 for ef in self.hp_sys.effects if type(ef) is ManaDrain]):
            self.MAGIC_REGEN *= 0.5
        mn = self.mana / self.max_mana
        if mn <= 1:
            self.MAGIC_REGEN *= mn
            self.REGENERATION *= 1 - (1 - mn) ** 2
            self.domain_size *= 1 - (1 - mn) ** 3
            self.ntcs.append(f'Low Mana: Power -{int(100 * (1 - mn) ** 2)}%')
        ins_regen = (.8 + self.calculate_data('ins_regen', rate_data=False) / 1000 * game.get_game().clock.last_tick) * self.calculate_magic_regeneration()
        max_ins = self.calculate_data('max_ins', False)
        max_mana = self.calculate_data('max_mana', False)
        karma_reduce = 5 * self.calculate_data('karma_reduce', True, rate_multiply=True)
        if self.domain_size != 1:
            self.p_data.append(f'{int(self.domain_size * 100)}% domain')
        if self.hp_sys.max_hp > 1000:
            self.p_data.append(f'mtp. {int(mtp_regen)}/s')
            self.talent = min(self.talent + mtp_regen / 1000 * game.get_game().clock.last_tick, self.max_talent)
        self.p_data.append(f'regen. {int(self.REGENERATION * 600) / 10}/s')
        self.p_data.append(f'mana. {int(self.MAGIC_REGEN * 600) / 10}/s')
        if max_ins:
            self.p_data.append(f'{int(max_ins)} additional')
        if ins_regen:
            self.p_data.append(f'ins. {int(ins_regen * 600) / 10}/s')
        if self.good_karma != 0 or karma_reduce != 5:
            self.p_data.append(f'karma. {int(self.good_karma)} -{int(karma_reduce * 60)}/s')
        self.good_karma = max(0, self.good_karma - karma_reduce)
        self.inspiration = min(self.inspiration + ins_regen, self.max_inspiration + max_ins)
        self.hp_sys.defenses[damages.DamageTypes.TOUCHING] = (self.calculate_data('touch_def', False) + arm * 2) * (1 - self.shield_break / 100) ** .8
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = self.calculate_data('phys_def', False) * (1 - self.shield_break / 100) ** .5
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = self.calculate_data('mag_def', False) * (1 - self.shield_break / 100) ** 1.0
        self.p_data.append(f'break {self.shield_break:.1f}%')
        self.p_data.append(f'magic def. {int(self.hp_sys.defenses[damages.DamageTypes.MAGICAL])}')
        self.p_data.append(f'phy.  def. {int(self.hp_sys.defenses[damages.DamageTypes.TOUCHING])}')
        if len([1 for eff in self.hp_sys.effects if eff.NAME == 'Gravity']):
            self.obj.apply_force(vector.Vector(180, 200))
        if pg.K_e in game.get_game().get_keys():
            if self.open_chest is not None:
                self.open_chest = None
            else:
                self.open_inventory = not self.open_inventory

        tp_r = self.talent / self.max_talent if self.max_talent else 1
        if tp_r < .8:
            self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] *= tp_r * 1.25
            self.hp_sys.defenses[damages.DamageTypes.MAGICAL] *= tp_r * 1.25
            self.hp_sys.defenses[damages.DamageTypes.TOUCHING] *= tp_r * 1.25
            self.ntcs.append(f'Low Talent: Defense -{int(100 * (.8 - tp_r) * 1.25)}%')
        if tp_r < .5:
            self.attack *= tp_r * 2
            self.ntcs.append(f'Low Talent: Attack -{int(100 * (.5 - tp_r) * 2)}%')
        if tp_r < .4:
            self.obj.SPEED *= tp_r * 2.5
            self.ntcs.append(f'Low Talent: Speed -{int(100 * (.4 - tp_r) * 2.5)}%')
        if tp_r < .2:
            self.MAGIC_REGEN = 0
            self.REGENERATION = 0
            self.ntcs.append(f'Low Talent: Disable Regen.')
        if game.get_game().server is not None:
            self.ntcs.append(f'Server on {game.get_game().server.host}, port {game.get_game().server.port}.')
        if datetime.datetime.now() - game.get_game().save_time < datetime.timedelta(minutes=30):
            self.ntcs.append(f'Save {int((datetime.datetime.now() - game.get_game().save_time).seconds / 60)} minutes before.')
        self.hp_sys.heal(self.REGENERATION)
        self.mana = min(self.mana + self.MAGIC_REGEN, self.max_mana + max_mana + int(self.profile.point_wisdom ** 1.1) / 2)
        displayer = game.get_game().displayer
        tx, ty = self.obj.pos + self.obj.velocity
        if game.get_game().get_biome((int(tx) // game.get_game().CHUNK_SIZE + 120,
                                       int(ty) // game.get_game().CHUNK_SIZE + 120)) == 'ancient_wall':
            self.obj.SPEED /= 10
            self.obj.velocity *= 0
            self.ntcs.append('u r stuck bro')
        self.obj.update()
        self.ax, self.ay = game.get_game().get_anchor()
        pos = position.displayed_position(self.obj.pos)
        sf = self.profile.get_surface(*self.profile.get_color())
        sz = int(40 / self.get_screen_scale())
        sf = pg.transform.scale(sf, (sz, sz))
        ef = [e for e in self.hp_sys.effects if 'OCTAVE_INCREASE' in dir(e)]
        rt = game.get_game().clock.tick * 5 % 360
        effs = []
        for i in range(len(ef)):
            r = rt + 360 / len(ef) * i
            ax, az = vector.rotation_coordinate(r)
            im = pg.transform.scale_by(game.get_game().graphics['effect_' + ef[i].IMG], (6 + az / 2) / self.get_screen_scale())
            imr = im.get_rect(center=position.displayed_position((self.obj.pos[0] + ax * 200, self.obj.pos[1])))
            effs.append((ef[i], im, imr, ax, az))
        effs.sort(key=lambda y: y[4])
        for e, im, imr, ax, az in effs:
            if az < 0:
                game.get_game().displayer.canvas.blit(im, imr)
        displayer.canvas.blit(sf, (pos[0] - sz // 2, pos[1] - sz // 2))
        for e, im, imr, ax, az in effs:
            if az > 0:
                game.get_game().displayer.canvas.blit(im, imr)

        if 'twin_glasses' in self.accessories:
            rs = self.tick % 360
            img = entity.entity_get_surface(1, -rs, 2 * self.get_screen_scale(),
                                            game.get_game().graphics['entity_mechanic_eye'])
            img_r = img.get_rect(center=position.displayed_position(self.obj.pos + vector.Vector2D(rs, -200)))
            game.get_game().displayer.canvas.blit(img, img_r)
            img = entity.entity_get_surface(1, -rs + 180, 2 * self.get_screen_scale(),
                                            game.get_game().graphics['entity_mechanic_eye'])
            img_r = img.get_rect(center=position.displayed_position(self.obj.pos + vector.Vector2D(rs, 200)))
            game.get_game().displayer.canvas.blit(img, img_r)
            if pg.BUTTON_LEFT in game.get_game().get_pressed_mouse() and self.tick % 4 == 0 and self.mana >= round(7 * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1):
                self.mana -= round(7 * game.get_game().player.calculate_data('mana_cost', rate_data=True, rate_multiply=True),1)
                game.get_game().projectiles.append(projectiles.Projectiles.TwinGlasses(self.obj.pos + vector.Vector2D(rs, -200), rs))
                game.get_game().projectiles.append(projectiles.Projectiles.TwinGlasses(self.obj.pos + vector.Vector2D(rs, 200), 180 + rs))


        self.hp_sys.update()
        w = self.weapons[self.sel_weapon]
        if pg.K_EQUALS in game.get_game().get_pressed_keys():
            self.scale = min(self.scale + 0.05, self.get_max_screen_scale())
            entity.entity_get_surface.cache_clear()
            projectiles.projectile_get_surface.cache_clear()
        if pg.K_MINUS in game.get_game().get_pressed_keys():
            self.scale = max(self.scale - 0.05, 0.1)
            entity.entity_get_surface.cache_clear()
            projectiles.projectile_get_surface.cache_clear()
        if inventory.TAGS['magic_weapon'] in inventory.ITEMS[w.name.replace(' ', '_')].tags:
            if pg.K_y in game.get_game().get_keys():
                if 'windstorm_warlock_mark' in self.accessories:
                    if self.mana >= w.mana_cost * 20 and type(w.projectile) is not projectiles.Projectiles.Projectile:
                        self.mana -= w.mana_cost * 20
                        for i in range(25):
                            x, y = self.obj.pos
                            x += random.randint(-200, 200)
                            y += random.randint(-200, 200)
                            mx, my = position.real_position(displayer.reflect(*pg.mouse.get_pos()))
                            pj = w.projectile((x, y), vector.coordinate_rotation(mx - x, my - y))
                            game.get_game().projectiles.append(pj)
                elif 'kindness_amulet' in self.accessories:
                    v = self.hp_sys.max_hp - self.hp_sys.hp
                    self.hp_sys.heal(v)
                    for e in game.get_game().entities:
                        e.hp_sys.heal(v * 20)
                elif 'bravery_amulet' in self.accessories:
                    t = 0
                    w = self.weapons[self.sel_weapon]
                    for i in range(10):
                        w.attack()
                        if w.timer:
                            t += 2
                        else:
                            break
                    for tt, v in w.damages.items():
                        for e in game.get_game().entities:
                            if e.IS_MENACE:
                                e.hp_sys.damage(tt, v * t)
                elif 'integrity_amulet' in self.accessories:
                    try:
                        tc = w.talent_cost
                    except AttributeError:
                        tc = 0
                    if self.talent >= w.mana_cost * 4 + tc * 32 and type(w.projectile) is not projectiles.Projectiles.Projectile:
                        self.talent -= w.mana_cost * 4 + tc * 32
                        for i in range(50):
                            x, y = self.obj.pos
                            x += random.randint(-200, 200)
                            y += random.randint(-200, 200)
                            mx, my = position.real_position(displayer.reflect(*pg.mouse.get_pos()))
                            pj = w.projectile((x, y), vector.coordinate_rotation(mx - x, my - y))
                            game.get_game().projectiles.append(pj)
        elif inventory.TAGS['bow'] in inventory.ITEMS[w.name.replace(' ', '_')].tags or inventory.TAGS['gun'] in \
                inventory.ITEMS[w.name.replace(' ', '_')].tags:
            if pg.K_y in game.get_game().get_keys():

                if 'windstorm_assassin_mark' in self.accessories:
                    if self.mana >= 60:
                        self.mana -= 60
                        mx, my = position.real_position(displayer.reflect(*pg.mouse.get_pos()))
                        self.obj.apply_force(
                            vector.Vector(vector.coordinate_rotation(mx - self.obj.pos[0], my - self.obj.pos[1]), 3000))
                elif 'daedalus_mark' in self.accessories:
                    if self.mana >= 60:
                        self.mana -= 60
                        if inventory.TAGS['bow'] in inventory.ITEMS[w.name.replace(' ', '_')].tags:
                            ammo = self.ammo[0]
                        else:
                            ammo = self.ammo_bullet[0]
                        ammo = projectiles.AMMOS[ammo]
                        mx, my = position.real_position(displayer.reflect(*pg.mouse.get_pos()))
                        for i in range(40):
                            x, y = mx + random.randint(-100 - i * 20,
                                                       100 + i * 20), my - game.get_game().displayer.SCREEN_HEIGHT // 2 - i * 12
                            pj = ammo((x, y), vector.coordinate_rotation(mx - x, my - y) + random.randint(-2, 2), 600,
                                      1200)
                            game.get_game().projectiles.append(pj)
                elif 'cowboy_hat' in self.accessories:
                    if self.mana >= 400:
                        self.mana -= 400
                        self.hp_sys.effect(effects.JusticeTime(2, 5))
                elif 'justice_amulet' in self.accessories:
                    mx, my = position.real_position(displayer.reflect(*pg.mouse.get_pos()))
                    self.obj.velocity.add(vector.Vector(vector.coordinate_rotation(mx - self.obj.pos[0], my - self.obj.pos[1]),
                                                        vector.distance(mx - self.obj.pos[0], my - self.obj.pos[1])))
        elif inventory.TAGS['poet_weapon'] in inventory.ITEMS[w.name.replace(' ', '_')].tags:
            if pg.K_y in game.get_game().get_keys():
                if 'windstorm_musicians_mark' in self.accessories:
                    if self.inspiration >= 500:
                        self.inspiration -= 500
                        self.hp_sys.effect(effects.OctSpeedII(12, 2))
                        self.hp_sys.effect(effects.OctLimitlessIII(12, 2))
                        self.hp_sys.effect(effects.OctStrengthII(12, 2))
        else:
            if pg.K_y in game.get_game().get_keys():
                if 'windstorm_swordman_mark' in self.accessories:
                    if not w.cool and self.mana >= 80:
                        self.mana -= 80
                        w.attack()
                        px, py = self.obj.pos
                        for e in game.get_game().entities:
                            ax = e.obj.pos[0] - px
                            ay = e.obj.pos[1] - py
                            if vector.distance(ax, ay) < 500:
                                e.hp_sys.damage(w.damages[damages.DamageTypes.PHYSICAL] * 3,
                                                damages.DamageTypes.PHYSICAL)
                                e.obj.apply_force(vector.Vector(vector.coordinate_rotation(ax, ay), 4000))
                elif 'bravery_amulet' in self.accessories:
                    t = 0
                    w = self.weapons[self.sel_weapon]
                    for i in range(10):
                        w.attack()
                        if w.timer:
                            t += 2
                        else:
                            break
                    for tt, v in w.damages.items():
                        for e in game.get_game().entities:
                            if e.IS_MENACE:
                                e.hp_sys.damage(tt, v * t)
                elif 'kindness_amulet' in self.accessories:
                    v = self.hp_sys.max_hp - self.hp_sys.hp
                    self.hp_sys.heal(v)
                    for e in game.get_game().entities:
                        e.hp_sys.heal(v * 20)
                elif 'paladins_mark' in self.accessories:
                    if not w.cool and self.mana >= 40:
                        self.mana -= 40
                        w.attack()
                        w.timer = 30
                        px, py = self.obj.pos
                        for e in game.get_game().entities:
                            ax = e.obj.pos[0] - px
                            ay = e.obj.pos[1] - py
                            if vector.distance(ax, ay) < 500:
                                e.hp_sys.damage(w.damages[damages.DamageTypes.PHYSICAL] * 10,
                                                damages.DamageTypes.PHYSICAL)
                                e.obj.velocity.add(vector.Vector(vector.coordinate_rotation(ax, ay), 15))
                elif 'perseverance_amulet' in self.accessories:
                    if self.mana >= 800:
                        window = pg.display.get_surface()
                        s = pg.Surface(window.get_size(), pg.SRCALPHA)
                        s.fill((0, 255, 255))
                        s.set_alpha(100)
                        window.blit(s, (0, 0))
                        pg.display.update()
                        self.mana -= 800
                        for i in range(50):
                            w.update()
                elif 'cloudy_glasses' in self.accessories:
                    if self.mana >= 600:
                        self.mana -= 600
                        for e in game.get_game().entities:
                            if not e.obj.IS_OBJECT:
                                e.hp_sys.hp = 0
        if self.tick % 60 == 1 and 'pluma_thaumaturgy' in self.accessories:
            ss = int(abs(self.obj.velocity) / 10)
            for i in range(ss):
                game.get_game().projectiles.append(underia3.FeatherThaumaturgy(self.obj.pos, random.randint(0, 360)))
        if 'bioic_thaumaturgy' in self.accessories:
            if not len([1 for n, hp in self.hp_sys.shields if n == 'bth']):
                if self.tick % 60 == 1:
                    self.hp_sys.shields.append(('bth', 0))
                    f = 1
                else:
                    f = 0
            else:
                f = 1
            if f:
                if [hp for n, hp in self.hp_sys.shields if n == 'bth'][0] < self.hp_sys.max_hp:
                    self.hp_sys.shields = [(n, min(hp + self.REGENERATION / 10, self.hp_sys.max_hp)) if n == 'bth' else (n, hp) for n, hp in self.hp_sys.shields]
        if self.hp_sys.hp <= 1 + self.REGENERATION:
            if 'flashback' in self.accessories and not len([1 for e in self.hp_sys.effects if type(e) is effects.FlashBack]):
                self.hp_sys(op='config', immune=True)
                self.hp_sys.hp = 2 + self.REGENERATION
                game.get_game().player.hp_sys.effect(effects.TimeStop(duration=1000000, level=1))
                game.get_game().player.hp_sys.effect(effects.FlashBack(duration=50, level=1))
                for i in range(80):
                    game.get_game().handle_events()
                    game.get_game().player.update()
                    self.hp_sys.hp += self.REGENERATION * 40
                    for e in game.get_game().entities:
                        e.draw()
                        e.hp_sys.is_immune = 0
                    for p in game.get_game().projectiles:
                        p.draw()
                    game.get_game().player.ui()
                    if constants.USE_ALPHA:
                        game.get_game().displayer.canvas.set_alpha(i * 2 + 15)
                    game.get_game().displayer.update()
                    pg.display.update()
                    game.get_game().clock.update(40)
                self.hp_sys(op='config', immune=False)
                game.get_game().player.hp_sys.effects = \
                    [e for e in game.get_game().player.hp_sys.effects if type(e) is not effects.TimeStop]
                return
            if 'fate_alignment_amulet' in self.accessories and not len([1 for e in self.hp_sys.effects if type(e) is effects.FateAlign]):
                self.hp_sys.heal(2000)
                game.get_game().player.hp_sys.effect(effects.FateAlign(duration=100, level=1))
                return
            if 'demon_contract' in self.accessories and not len([1 for e in self.hp_sys.effects if type(e) is effects.DemonContract]):
                self.hp_sys.heal(2000)
                game.get_game().player.hp_sys.effect(effects.DemonContract(duration=30, level=1))
                sr = random.randint(-1, 6)
                if sr > 0:
                    for _ in range(sr):
                        self.inventory.remove_item(random.choice(self.inventory.items.keys()), random.randint(1, 30))
                self.talent = max(0, self.talent - random.randint(0, 1000))
                self.mana = max(0, self.mana - random.randint(0, 1000))
                if random.random() > 0.5:
                    self.cd_z = random.randint(500, 5000)
                if random.random() > 0.5:
                    self.cd_x = random.randint(500, 5000)
                if random.random() > 0.5:
                    self.cd_c = random.randint(500, 5000)
                return
            sz = int(40 / self.get_screen_scale())
            game.get_game().dialog.with_border = False
            tck = 0
            px, py = displayer.SCREEN_WIDTH // 2, displayer.SCREEN_HEIGHT // 2
            game.get_game().dialog.dialog(
                'Looks like you\'ve reached the end.',
                'Would you like to continue?',
                '...',
                'I see.',
                'Then, the future is in your hands.'
            )
            shards = []
            if game.get_game().cur_music:
                m = game.get_game().musics[game.get_game().cur_music]
                if m:
                    m.stop()
            while tck < 300 or game.get_game().dialog.curr_text != "":
                sz = (160 + sz * 15) / 16
                r, g, b = self.profile.get_color()
                if tck > 140:
                    r, g, b = (255, 255, 255)
                elif tck > 40:
                    r = (r + (250 - r) * (tck - 40) / 100)
                    g = (g + (250 - g) * (tck - 40) / 100)
                    b = (b + (250 - b) * (tck - 40) / 100)
                tck += 1
                sf = self.profile.get_surface(r, g, b)
                sf = pg.transform.scale(sf, (sz, sz))
                displayer.canvas.fill((0, 0, 0))
                if tck < 200:
                    displayer.canvas.blit(sf, (px - sz // 2, py - sz // 2))
                elif tck == 200:
                    shards = [mover.Mover((px, py)) for _ in range(20)]
                    for s in shards:
                        s.FRICTION = 0.98
                        s.apply_force(vector.Vector(random.randint(0, 360), random.randint(80, 120) * 3))
                else:
                    for s in shards:
                        s.update()
                        s.apply_force(vector.Vector(vector.coordinate_rotation(0, 1), 20))
                        im = pg.transform.rotate(game.get_game().graphics['background_shard'], random.randint(0, 360))
                        displayer.canvas.blit(im, im.get_rect(center=s.pos()))
                game.get_game().handle_events()
                game.get_game().dialog.update(game.get_game().pressed_keys)
                game.get_game().clock.update()
                displayer.update()
                pg.display.update()
            game.get_game().dialog.with_border = True
            self.hp_sys.hp = self.hp_sys.max_hp
            self.mana = self.max_mana
            self.talent = self.max_talent
            self.obj.velocity.clear()
            self.hp_sys.effects = []
            game.get_game().entities = []
            game.get_game().projectiles = []
            game.get_game().damage_texts = []
            self.obj.pos << (0, 0)
        self.weapons[self.sel_weapon].update()

    def ui(self):
        self.in_ui = False
        self.touched_item = ''
        mouse_text = False
        displayer = game.get_game().displayer
        displayer.SCREEN_WIDTH = displayer.canvas.get_width()
        displayer.SCREEN_HEIGHT = displayer.canvas.get_height()
        mt = self.hp_sys.max_hp > 1000
        if mt and self.mana < 100:
            v = min(self.max_mana - self.mana, self.talent * 8)
            self.mana += v
            self.talent -= v / 8
        if constants.HEART_BAR:
            hp_p = self.hp_sys.hp / self.hp_sys.max_hp
            mp_p = self.mana / self.max_mana
            tp_p = self.talent / self.max_talent if self.max_talent else 0
            sd_p = min(1, sum([v for n, v in game.get_game().player.hp_sys.shields]) / game.get_game().player.hp_sys.max_hp)

            hp_img = game.get_game().graphics['background_ui_heart']
            sh_img = game.get_game().graphics['background_ui_heart_shield']
            mana_img = game.get_game().graphics['background_ui_mana']
            tal_img = game.get_game().graphics['background_ui_talent']
            out_img = game.get_game().graphics['background_ui_heart_outline']
            ins_img = game.get_game().graphics['background_ui_inspiration']
            ins_out_img = game.get_game().graphics['background_ui_inspiration_outline']
            shh_img = game.get_game().graphics['background_ui_break']
            sh_out_img = game.get_game().graphics['background_ui_break_outline']

            hp_img = pg.transform.scale(hp_img, (40, 40))
            sh_img = pg.transform.scale(sh_img, (40, 40))
            mana_img = pg.transform.scale(mana_img, (40, 40))
            tal_img = pg.transform.scale(tal_img, (40, 40))
            out_img = pg.transform.scale(out_img, (40, 40))
            ins_img = pg.transform.scale(ins_img, (40, 40))
            ins_out_img = pg.transform.scale(ins_out_img, (40, 40))
            shh_img = pg.transform.scale(shh_img, (40, 40))
            sh_out_img = pg.transform.scale(sh_out_img, (40, 40))

            hp_no = min(self.hp_sys.max_hp // 30, 10)
            mana_no = min(self.max_mana // 50, 10 - mt * 8)
            tal_no = min(self.max_talent, 1 + mt * 5)
            ins_no = min(self.max_inspiration // 200, 10)

            for i in range(int(hp_no)):
                if hp_p < i / hp_no:
                    break
                elif hp_p >= (i + 1) / hp_no:
                    hr = hp_img.get_rect(center=(50 + i * 50, 40))
                    displayer.canvas.blit(hp_img, hr)
                else:
                    n_img = pg.transform.scale_by(hp_img, (hp_p - i / hp_no) / (1 / hp_no))
                    hr = n_img.get_rect(center=(50 + i * 50, 40))
                    displayer.canvas.blit(n_img, hr)
            for i in range(int(hp_no)):
                if sd_p < i / hp_no:
                    break
                elif sd_p >= (i + 1) / hp_no:
                    hr = sh_img.get_rect(center=(50 + i * 50, 40))
                    displayer.canvas.blit(sh_img, hr)
                else:
                    n_img = pg.transform.scale_by(sh_img, (sd_p - i / hp_no) / (1 / hp_no))
                    hr = n_img.get_rect(center=(50 + i * 50, 40))
                    displayer.canvas.blit(n_img, hr)
            for i in range(int(hp_no)):
                otr = out_img.get_rect(center=(50 + i * 50, 40))
                displayer.canvas.blit(out_img, otr)
            for i in range(int(mana_no)):
                if mp_p < i / mana_no:
                    break
                elif mp_p >= (i + 1) / mana_no:
                    mr = mana_img.get_rect(center=(50 + i * 50 + hp_no * 50, 40))
                    displayer.canvas.blit(mana_img, mr)
                else:
                    n_img = pg.transform.scale_by(mana_img, (mp_p - i / mana_no) / (1 / mana_no))
                    mr = n_img.get_rect(center=(50 + i * 50 + hp_no * 50, 40))
                    displayer.canvas.blit(n_img, mr)
            for i in range(int(mana_no)):
                otr = out_img.get_rect(center=(50 + i * 50 + hp_no * 50, 40))
                displayer.canvas.blit(out_img, otr)
            for i in range(int(tal_no)):
                if tp_p < i / tal_no:
                    break
                elif tp_p >= (i + 1) / tal_no:
                    tr = tal_img.get_rect(center=(50 + i * 50 + hp_no * 50 + mana_no * 50, 40))
                    displayer.canvas.blit(tal_img, tr)
                else:
                    n_img = pg.transform.scale_by(tal_img, (tp_p - i / tal_no) / (1 / tal_no))
                    tr = n_img.get_rect(center=(50 + i * 50 + hp_no * 50 + mana_no * 50, 40))
                    displayer.canvas.blit(n_img, tr)
            for i in range(int(tal_no)):
                otr = out_img.get_rect(center=(50 + i * 50 + hp_no * 50 + mana_no * 50, 40))
                displayer.canvas.blit(out_img, otr)
            for i in range(int(ins_no)):
                if self.inspiration < i * 200:
                    break
                elif self.inspiration >= (i + 1) * 200:
                    ir = ins_img.get_rect(center=(game.get_game().displayer.SCREEN_WIDTH - 50, 40 + i * 50))
                    displayer.canvas.blit(ins_img, ir)
                else:
                    n_img = pg.transform.scale_by(ins_img, (self.inspiration - i * 200) / 200)
                    ir = n_img.get_rect(center=(game.get_game().displayer.SCREEN_WIDTH - 50, 40 + i * 50))
                    displayer.canvas.blit(n_img, ir)
            for i in range(int(ins_no)):
                otr = ins_out_img.get_rect(center=(game.get_game().displayer.SCREEN_WIDTH - 50, 40 + i * 50))
                displayer.canvas.blit(ins_out_img, otr)


            rc = pg.Rect(30, 20, (hp_no + mana_no + tal_no) * 50 - 10, 40)
            ic = pg.Rect(game.get_game().displayer.SCREEN_WIDTH - 70, 20, 40, ins_no * 50 - 10)

            ns_img = pg.transform.scale_by(shh_img, 1 - self.shield_break / 100)
            s_img = ns_img.get_rect(center=(50 + hp_no * 50 + mana_no * 50 + tal_no * 50, 40))
            displayer.canvas.blit(ns_img, s_img)
            s_img = sh_out_img.get_rect(center=(50 + hp_no * 50 + mana_no * 50 + tal_no * 50, 40))
            displayer.canvas.blit(sh_out_img, s_img)
            sc = pg.Rect(30 + hp_no * 50 + mana_no * 50 + tal_no * 50, 20, 40, 40)
        else:
            hp_l = min(300.0, self.hp_sys.max_hp // 2)
            mp_l = min(300.0 - mt * 200.0, self.max_mana)
            tp_l = min(200.0 + mt * 300.0, 8 * self.max_talent)
            is_l = min(500.0, self.inspiration // 2)
            hp_p = min(1.0, self.hp_sys.hp / self.hp_sys.max_hp)
            mp_p = min(1.0, self.mana / self.max_mana)
            tp_p = self.talent / self.max_talent if self.max_talent else 0
            sd_p = min(1.0, sum([v for n, v in self.hp_sys.shields]) / self.hp_sys.max_hp)
            sd_p2 = max(0.0, min(1.0, sum([v for n, v in self.hp_sys.shields]) / self.hp_sys.max_hp - 1))
            sd_p3 = max(0.0, min(1.0, sum([v for n, v in self.hp_sys.shields]) / self.hp_sys.max_hp - 2))
            sd_p4 = max(0.0, min(1.0, sum([v for n, v in self.hp_sys.shields]) / self.hp_sys.max_hp - 3))
            md_p = min(1.0, max(0, self.mana - self.max_mana) / self.max_mana)
            md_p2 = min(1.0, max(0, self.mana - self.max_mana * 2) / self.max_mana)
            md_p3 = min(1.0, max(0, self.mana - self.max_mana * 3) / self.max_mana)
            md_p4 = min(1.0, max(0, self.mana - self.max_mana * 4) / self.max_mana)
            pg.draw.rect(displayer.canvas, (80, 0, 0), (10, 10, hp_l, 40))
            pg.draw.rect(displayer.canvas, (0, 0, 80), (10 + hp_l, 10, mp_l, 40))
            pg.draw.rect(displayer.canvas, (0, 80, 0), (10 + hp_l + mp_l, 10, tp_l, 40))
            pg.draw.rect(displayer.canvas, (255, 0, 0), (10, 10, hp_l * hp_p, 40))
            pg.draw.rect(displayer.canvas, (255, 127, 0), (10, 10, hp_l * sd_p, 40))
            pg.draw.rect(displayer.canvas, (255, 255, 0), (10, 10, hp_l * sd_p2, 40))
            pg.draw.rect(displayer.canvas, (127, 255, 0), (10, 10, hp_l * sd_p3, 40))
            pg.draw.rect(displayer.canvas, (127, 255, 127), (10, 10, hp_l * sd_p4, 40))
            pg.draw.rect(displayer.canvas, (0, 0, 255), (10 + hp_l + mp_l - mp_l * mp_p, 10, mp_l * mp_p, 40))
            pg.draw.rect(displayer.canvas, (0, 127, 255), (10 + hp_l + mp_l - mp_l * md_p, 10, mp_l * md_p, 40))
            pg.draw.rect(displayer.canvas, (0, 255, 255), (10 + hp_l + mp_l - mp_l * md_p2, 10, mp_l * md_p2, 40))
            pg.draw.rect(displayer.canvas, (0, 255, 127), (10 + hp_l + mp_l - mp_l * md_p3, 10, mp_l * md_p3, 40))
            pg.draw.rect(displayer.canvas, (127, 255, 127), (10 + hp_l + mp_l - mp_l * md_p4, 10, mp_l * md_p4, 40))
            pg.draw.rect(displayer.canvas, (0, 255, 0) if not mt else (200, 255, 127), (10 + hp_l + mp_l, 10, tp_l * tp_p, 40))
            pg.draw.rect(displayer.canvas, (207, 255, 112), (10, 10, hp_l + mp_l + tp_l, 40), width=6)

            if self.max_inspiration:
                is_p = self.inspiration / self.max_inspiration
                pg.draw.rect(displayer.canvas, (80, 0, 80), (game.get_game().displayer.SCREEN_WIDTH - 50, 10, 40, is_l))
                pg.draw.rect(displayer.canvas, (255, 0, 255), (game.get_game().displayer.SCREEN_WIDTH - 50, 10, 40, is_l * is_p))
                pg.draw.rect(displayer.canvas, (207, 255, 112), (game.get_game().displayer.SCREEN_WIDTH - 50, 10, 40, is_l), width=6)

            rc = pg.Rect(10, 10, hp_l + mp_l + tp_l, 40)
            ic = pg.Rect(game.get_game().displayer.SCREEN_WIDTH - 50, 10, 40, is_l)

            shh_img = game.get_game().graphics['background_ui_break']
            sh_out_img = game.get_game().graphics['background_ui_break_outline']
            shh_img = pg.transform.scale(shh_img, (40, 40))
            sh_out_img = pg.transform.scale(sh_out_img, (40, 40))
            ns_img = pg.transform.scale_by(shh_img, 1 - self.shield_break / 100)
            s_img = ns_img.get_rect(center=(50 + hp_l + mp_l + tp_l, 40))
            displayer.canvas.blit(ns_img, s_img)
            s_img = sh_out_img.get_rect(center=(50 + hp_l + mp_l + tp_l, 40))
            displayer.canvas.blit(sh_out_img, s_img)
            sc = pg.Rect(30 + hp_l + mp_l + tp_l, 20, 40, 40)
        eff = self.hp_sys.effects
        if not self.ui_attributes:
            eff = [e for e in eff if not issubclass(type(e), effects.OctaveIncrease) and not issubclass(type(e), effects.SkillReinforce)]
        for i in range(len(eff)):
            img = pg.transform.scale(game.get_game().graphics['effect_' + eff[i].IMG], (72, 72))
            imr = img.get_rect(
                topright=(game.get_game().displayer.SCREEN_WIDTH - 10 - 80 * len(eff) + 80 * i, 10))
            displayer.canvas.blit(img, imr)
        for i in range(len(eff)):
            img = pg.transform.scale(game.get_game().graphics['effect_' + eff[i].IMG], (72, 72))
            imr = img.get_rect(
                topright=(game.get_game().displayer.SCREEN_WIDTH - 10 - 80 * len(eff) + 80 * i, 10))
            if imr.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
                self.in_ui = True
                mouse_text = True
                f = displayer.font.render(f"{styles.text(eff[i].NAME)} ({int(eff[i].timer)}s)", True,
                                          (255, 255, 255))
                fb = displayer.font.render(f"{styles.text(eff[i].NAME)} ({int(eff[i].timer)}s)", True,
                                               (0, 0, 0))
                ffr = f.get_rect(topright=game.get_game().displayer.reflect(*pg.mouse.get_pos()))
                ffr.y += 3
                displayer.canvas.blit(fb, ffr)
                ffr.x -= 3
                ffr.y -= 3
                displayer.canvas.blit(f, ffr)
                for j, d in enumerate(eff[i].DESC.split('\n')):
                    f = displayer.font.render(d, True, (255, 255, 255))
                    fb = displayer.font.render(d, True, (0, 0, 0))
                    ffr = f.get_rect(topright=game.get_game().displayer.reflect(*pg.mouse.get_pos()))
                    ffr.y += 3 + 30 * j + 30
                    displayer.canvas.blit(fb, ffr)
                    ffr.x -= 3
                    ffr.y -= 3
                    displayer.canvas.blit(f, ffr)
        for _entity in game.get_game().entities:
            _entity.obj.touched_player = False
            _entity.obj.object_collision(self.obj, ((_entity.img.get_width() + _entity.img.get_height()) if _entity.img is not None else 0) // 4 + 50)
            if self.obj.object_collision(_entity.obj, (_entity.img.get_width() + _entity.img.get_height() if _entity.img is not None else 0) // 4 + 50):
                _entity.obj.touched_player = True
                _entity.on_damage_player()
                if 'lt' in dir(_entity) and self.tick - getattr(_entity, 'lt') <= self.hp_sys.IMMUNE_TIME * 5:
                    continue
                setattr(_entity, 'lt', self.tick)
                if _entity.obj.TOUCHING_DAMAGE and not self.hp_sys.is_immune:
                    s_hp = self.hp_sys.hp
                    self.hp_sys.damage(_entity.obj.TOUCHING_DAMAGE, damages.DamageTypes.TOUCHING)
                    self.shield_break = min(100, self.shield_break + _entity.obj.TOUCHING_DAMAGE /
                                            max(20, self.hp_sys.defenses[damages.DamageTypes.TOUCHING]) *
                                            self.hp_sys.resistances[damages.DamageTypes.TOUCHING] ** .5 * 20)
                    _entity.on_hit(self)
                    e_hp = self.hp_sys.hp
                    self.hp_sys.enable_immune()
                    px, py = _entity.obj.pos
                    px -= self.obj.pos[0]
                    py -= self.obj.pos[1]
                    if e_hp - s_hp < -1:
                        game.get_game().play_sound('player_hit_1', stop_if_need=True)
                    elif e_hp - s_hp < -self.hp_sys.max_hp / 5:
                        game.get_game().play_sound('player_hit_2', stop_if_need=True)
                    self.obj.velocity.add(vector.Vector(vector.coordinate_rotation(px, py), min(0.0, e_hp - s_hp) / self.hp_sys.max_hp * 250))
            self.obj.object_gravitational(_entity.obj)
            _entity.obj.object_gravitational(self.obj)
        nx = 10 + 30 + 10
        tsk_rect = pg.Rect(nx - 30, 140, 60, 60)
        im = game.get_game().graphics['background_ui_tasks']
        if not tsk_rect.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
            im = pg.transform.scale(im, (54, 54))
        imr = im.get_rect(center=(nx, 170))
        displayer.canvas.blit(im, imr)
        nx = 10 + 30 + 10 + 60
        att_rect = pg.Rect(nx - 30, 140, 60, 60)
        im = game.get_game().graphics['background_ui_attributes']
        if not att_rect.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
            im = pg.transform.scale(im, (54, 54))
        imr = im.get_rect(center=(nx, 170))
        displayer.canvas.blit(im, imr)
        nx = 10 + 30 + 10 + 60 * 2
        inv_rect = pg.Rect(nx - 30, 140, 60, 60)
        im = game.get_game().graphics['background_ui_inventory']
        if not inv_rect.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
            im = pg.transform.scale(im, (54, 54))
        imr = im.get_rect(center=(nx, 170))
        displayer.canvas.blit(im, imr)
        if tsk_rect.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
            self.in_ui = True
            mouse_text = True
            if 1 in game.get_game().get_mouse_press():
                self.ui_tasks = not self.ui_tasks
            f = displayer.font.render(styles.text(f"Task & Event"), True, (255, 255, 255))
            fb = displayer.font.render(styles.text(f"Task & Event"), True, (0, 0, 0))
            mx, my = game.get_game().displayer.reflect(*pg.mouse.get_pos())
            game.get_game().displayer.canvas.blit(fb, (mx + 3, my + 3))
            game.get_game().displayer.canvas.blit(f, (mx, my))
        if att_rect.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
            if 1 in game.get_game().get_mouse_press():
                self.ui_attributes = not self.ui_attributes
            f = displayer.font.render(styles.text(f"Player Attributes"), True, (255, 255, 255))
            fb = displayer.font.render(styles.text(f"Player Attributes"), True, (0, 0, 0))
            mx, my = game.get_game().displayer.reflect(*pg.mouse.get_pos())
            game.get_game().displayer.canvas.blit(fb, (mx + 3, my + 3))
            game.get_game().displayer.canvas.blit(f, (mx, my))
            self.in_ui = True
            mouse_text = True
        if inv_rect.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
            if 1 in game.get_game().get_mouse_press():
                self.open_inventory = not self.open_inventory
            f = displayer.font.render(styles.text(f"Inventory"), True, (255, 255, 255))
            fb = displayer.font.render(styles.text(f"Inventory"), True, (0, 0, 0))
            mx, my = game.get_game().displayer.reflect(*pg.mouse.get_pos())
            game.get_game().displayer.canvas.blit(fb, (mx + 3, my + 3))
            game.get_game().displayer.canvas.blit(f, (mx, my))
            self.in_ui = True
            mouse_text = True

        if rc.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
            self.in_ui = True
            mouse_text = True
            f = displayer.font.render(
                f"HP: {int(self.hp_sys.hp) + int(sum([v for n, v in game.get_game().player.hp_sys.shields]))}/{self.hp_sys.max_hp} MP: {int(self.mana)}/{self.max_mana}"
                f" {'TP' if not mt else 'MTP'}: {int(self.talent)}/{int(self.max_talent)}",
                True, (255, 255, 255))
            fb = displayer.font.render(
                f"HP: {int(self.hp_sys.hp) + int(sum([v for n, v in game.get_game().player.hp_sys.shields]))}/{self.hp_sys.max_hp} MP: {int(self.mana)}/{self.max_mana}"
                f" {'TP' if not mt else 'MTP'}: {int(self.talent)}/{int(self.max_talent)}",
                True, (0, 0, 0))
            mx, my = game.get_game().displayer.reflect(*pg.mouse.get_pos())
            displayer.canvas.blit(fb, (mx + 3, my + 3))
            displayer.canvas.blit(f, (mx, my))
        if ic.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
            self.in_ui = True
            mouse_text = True
            f = displayer.font.render(f"IP: {int(self.inspiration)}/{int(self.max_inspiration)}", True,
                                      (255, 255, 255))
            fb = displayer.font.render(f"IP: {int(self.inspiration)}/{int(self.max_inspiration)}", True, (0, 0, 0))
            ffr = f.get_rect(topright=game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            ffr.y += 3
            displayer.canvas.blit(fb, ffr)
            ffr.x -= 3
            ffr.y -= 3
            displayer.canvas.blit(f, ffr)
        if sc.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
            self.in_ui = True
            mouse_text = True
            f = displayer.font.render(f"Break: {self.shield_break:.2f}%", True,
                                      (255, 255, 255))
            fb = displayer.font.render(f"Break: {self.shield_break:.2f}%", True, (0, 0, 0))
            ffr = f.get_rect(topright=game.get_game().displayer.reflect(*pg.mouse.get_pos()))
            ffr.y += 3
            displayer.canvas.blit(fb, ffr)
            ffr.x -= 3
            ffr.y -= 3
            displayer.canvas.blit(f, ffr)
        for i in range(len(self.weapons)):
            try:
                am = f'{self.weapons[i].amount}/{self.weapons[i].stack_size}'
            except AttributeError:
                am = '1'
            styles.item_display(10 + i * 60, 80,
                                self.weapons[i].name.replace(' ', '_'), str(i + 1),
                                am, 0.75, selected=i == self.sel_weapon)
            if self.weapons[i].sk_mcd:
                pg.draw.rect(displayer.canvas, (255, 0, 0), (10 + i * 60, 140, 60, 10))
                pg.draw.rect(displayer.canvas, (255, 255, 0), (10 + i * 60, 140,
                                                               60 * self.weapons[i].sk_cd // self.weapons[i].sk_mcd, 10))
                if self.weapons[i].sk_cd:
                    self.weapons[i].sk_cd -= 1
        w = self.weapons[self.sel_weapon]
        if len([1 for e in self.hp_sys.effects if type(e) is effects.RuneAltar]):
            if not game.get_game().player.inventory.is_enough(inventory.ITEMS['thaumaturgy']):
                game.get_game().player.inventory.add_item(inventory.ITEMS['thaumaturgy'])
            for s, e in THAUMATURGY_RECIPES:
                f = 1
                for ss in s:
                    if not game.get_game().player.inventory.is_enough(inventory.ITEMS[ss]) and not ss in self.accessories:
                        f = 0
                        break
                if f and e not in inventory.RECIPES:
                    inventory.RECIPES.append(e)
                    for ee in game.get_game().entities:
                        if ee.NAME == 'Rune Altar':
                            ee.hp_sys.hp = 0
                    game.get_game().dialog.push_dialog('You have learnt a new recipe!')
        if inventory.TAGS['magic_weapon'] in inventory.ITEMS[w.name.replace(' ', '_')].tags:
            sk_z = 'healer' if 'healer' in self.profile.select_skill else None
            sk_x = 'multi_user' if'multi_user' in self.profile.select_skill else None
            sk_c = None
            cdd = 500, 320, 0
            rc = (255, 0, 255)
        elif inventory.TAGS['bow'] in inventory.ITEMS[w.name.replace(' ', '_')].tags or inventory.TAGS['gun'] in \
             inventory.ITEMS[w.name.replace(' ', '_')].tags or inventory.TAGS['knife'] in inventory.ITEMS[w.name.replace(' ', '_')].tags:
            sk_z = 'storm_throw' if 'storm_throw' in self.profile.select_skill else ('fast_throw' if 'fast_throw' in self.profile.select_skill else None)
            sk_x = 'energy_shot' if 'energy_shot' in self.profile.select_skill else 'perfect_shot' if 'perfect_shot' in self.profile.select_skill else None
            sk_c = 'afterimage_shadow' if 'afterimage_shadow' in self.profile.select_skill else None
            cdd = 80, 30, 500
            rc = (255, 255, 0)
        elif inventory.TAGS['melee_weapon'] in inventory.ITEMS[w.name.replace(' ', '_')].tags:
            sk_z = 'the_wraith' if 'the_wraith' in self.profile.select_skill else ('the_fury' if 'the_fury' in self.profile.select_skill else None)
            sk_x = 'warrior_shield' if 'warrior_shield' in self.profile.select_skill else None
            sk_c = None
            cdd = 360, 250, 0
            rc = (0, 255, 255)
        else:
            sk_z = None
            sk_x = None
            sk_c = None
            cdd = 0, 0, 0
            rc = (255, 255, 255)
        if sk_z is not None:
            ps = (250, 80)
            self.profile.skill_display(ps, sk_z, select=True, window=game.get_game().displayer.canvas)
            sf = pg.Surface((60, 60 * self.cd_z // cdd[0]), pg.SRCALPHA)
            sf.fill((0, 0, 0, 255))
            sf.set_alpha(64)
            game.get_game().displayer.canvas.blit(sf, ps)
        if sk_x is not None:
            ps = (310, 80)
            self.profile.skill_display(ps, sk_x, select=True, window=game.get_game().displayer.canvas)
            sf = pg.Surface((60, 60 * self.cd_x // cdd[1]), pg.SRCALPHA)
            sf.fill((0, 0, 0, 255))
            sf.set_alpha(64)
            game.get_game().displayer.canvas.blit(sf, ps)
        if sk_c is not None:
            ps = (370, 80)
            self.profile.skill_display(ps, sk_c, select=True, window=game.get_game().displayer.canvas)
            sf = pg.Surface((60, 60 * self.cd_c // cdd[2]), pg.SRCALPHA)
            sf.fill((0, 0, 0, 255))
            sf.set_alpha(64)
            game.get_game().displayer.canvas.blit(sf, ps)
        if sk_z is not None:
            ps = (250, 80)
            self.profile.skill_mouse(ps, sk_z, rc=rc, window=game.get_game().displayer.canvas,
                                     mps=game.get_game().displayer.reflect(*pg.mouse.get_pos()))
        if sk_x is not None:
            ps = (310, 80)
            self.profile.skill_mouse(ps, sk_x, rc=rc, window=game.get_game().displayer.canvas,
                                     mps=game.get_game().displayer.reflect(*pg.mouse.get_pos()))
        if sk_c is not None:
            ps = (370, 80)
            self.profile.skill_mouse(ps, sk_c, rc=rc, window=game.get_game().displayer.canvas,
                                     mps=game.get_game().displayer.reflect(*pg.mouse.get_pos()))
        if 'direct_bullet' in self.profile.select_skill:
            if rc == (255, 255, 0) and game.get_game().clock.tick % (3 * (self.weapons[self.sel_weapon].at_time + self.weapons[self.sel_weapon].cd - 1)) == 0:
                es = [e for e in game.get_game().entities if vector.distance(e.obj.pos[0] -  self.obj.pos[0],
                                                                             e.obj.pos[1] - self.obj.pos[1]) < 1500]
                if len(es):
                    e = random.choice(es)
                    rt = vector.coordinate_rotation(e.obj.pos[0] - self.obj.pos[0], e.obj.pos[1] - self.obj.pos[1])
                    game.get_game().projectiles.append(projectiles.Projectiles.DirectBullet(self.obj.pos, rt, 0,
                                                                                            self.weapons[self.sel_weapon].damages[damages.DamageTypes.PIERCING] * 2))
        if 'sweeper' in self.profile.select_skill:
            if (rc == (0, 255, 255) and not self.weapons[self.sel_weapon].cool and not self.open_inventory and
                    0 not in game.get_game().get_pressed_mouse()):
                self.weapons[self.sel_weapon].attack()
        if self.cd_z:
            self.cd_z -= 1
        elif sk_z is not None and pg.K_z in game.get_game().get_keys():
            if sk_z == 'fast_throw':
                self.hp_sys.effect(effects.FastThrow(.4, 1))
                self.obj.velocity.add(vector.Vector(self.obj.velocity.get_net_rotation(), 200 / self.obj.FRICTION))
            elif sk_z == 'storm_throw':
                self.hp_sys.effect(effects.StormThrow(.5, 1))
                self.obj.velocity.add(vector.Vector(self.obj.velocity.get_net_rotation(), 500 / self.obj.FRICTION))
            elif sk_z == 'the_fury':
                self.hp_sys.effect(effects.TheFury(6, 1))
            elif sk_z == 'the_wraith':
                self.hp_sys.effect(effects.TheWraith(8, 1))
            elif sk_z == 'healer':
                self.hp_sys.heal(self.hp_sys.max_hp / 10)
                self.mana = max(min(self.mana + self.max_mana / 4, self.max_mana), self.mana)
                self.hp_sys.effect(effects.Healer(2, 1))
            self.cd_z = cdd[0]
        if self.cd_x:
            self.cd_x -= 1
        elif sk_x is not None and pg.K_x in game.get_game().get_keys():
            if sk_x == 'perfect_shot':
                am1 = self.ammo
                am2 = self.ammo_bullet
                self.ammo = ('energy_arrow', 1)
                self.ammo_bullet = ('energy_arrow', 1)
                w.attack()
                self.ammo = am1
                self.ammo_bullet = am2
            elif sk_x == 'energy_shot':
                am1 = self.ammo
                am2 = self.ammo_bullet
                self.ammo = ('eenergy_arrow', 1)
                self.ammo_bullet = ('eenergy_arrow', 1)
                w.attack()
                self.ammo = am1
                self.ammo_bullet = am2
            elif sk_x == 'warrior_shield':
                self.hp_sys.effect(effects.WarriorShield(4, 1))
                self.hp_sys.shields.append(('war', 1))
            elif sk_x == 'guard':
                self.hp_sys.effect(effects.Guard(3, 1))
                self.hp_sys.shields.append(('gua', 1))
            elif sk_x == 'multi_user':
                mc = self.mana
                mmc = self.max_mana // 2 // w.mana_cost
                for _ in range(mmc):
                    self.mana = self.max_mana
                    w.attack()
                    w.sk_cd = 0
                self.mana = mc
            self.cd_x = cdd[1]
        if self.cd_c:
            self.cd_c -= 1
        elif sk_c is not None and pg.K_c in game.get_game().get_keys():
            if sk_c == 'afterimage_shadow':
                self.afterimage_shadow = 1500
                game.get_game().play_sound('bullet', .5, fadeout=500)
            self.cd_c = cdd[2]
        if 1500 > self.afterimage_shadow > 1 and pg.K_c in game.get_game().get_keys():
            self.afterimage_shadow = 1
        if self.afterimage_shadow > 1:
            self.cd_c = cdd[2] - self.afterimage_shadow / 1500 * cdd[2]
            self.afterimage_shadow -= 1
        elif self.afterimage_shadow == 1:
            self.cd_c = cdd[2]
            self.afterimage_shadow -= 1
            self.hp_sys.effect(effects.AfterimageShadow(.5, 1))
            self.weapons[self.sel_weapon].strike = constants.INFINITY
            self.weapons[self.sel_weapon].attack()
            self.weapons[self.sel_weapon].on_special_attack(constants.INFINITY)
            game.get_game().displayer.effect(fc.p_fade_circle(*position.displayed_position(self.obj.pos), sp=20, t=20,
                                                              col=(100, 0, 100)))
            game.get_game().play_sound('create', .5)
        te = [e for e in self.hp_sys.effects if type(e) is effects.FastThrow]
        if len(te):
            if te[0].tick in [4, 8, 12] and sk_z == 'fast_throw':
                if 'throwing' in dir(w):
                    w.throwing = True
                w.attack()
            for e in game.get_game().entities:
                if vector.distance(self.obj.pos[0] - e.obj.pos[0], self.obj.pos[1] - e.obj.pos[1]) < 200:
                    if not e.hp_sys.is_immune:
                        e.hp_sys.damage(w.damages[damages.DamageTypes.PIERCING] * self.attack * self.attacks[1], damages.DamageTypes.PIERCING)
                        e.hp_sys.enable_immune()
            vr = 180 - self.obj.velocity.get_net_rotation()
            sp = int(te[0].tick * 50 * self.obj.SPEED / self.obj.MASS)
            ps1 = []
            ps2 = []
            for i in range(0, sp, 1):
                d = i / 5
                vx, vy = vector.rotation_coordinate(-vr)
                vdx, vdy = vector.rotation_coordinate(90 - vr)
                ar = te[0].tick / 3 + d / 20
                ps1.append((self.obj.pos[0] + vx * d + math.sin(ar) * vdx * (sp / 4.5 - d) / 8,
                            self.obj.pos[1] + vy * d + math.sin(ar) * vdy * (sp / 4.5 - d) / 8))
                ps2.append((self.obj.pos[0] + vx * d - math.sin(ar) * vdx * (sp / 4.5 - d) / 8,
                            self.obj.pos[1] + vy * d - math.sin(ar) * vdy * (sp / 4.5 - d) / 8))
            for i in range(len(ps1) - 1):
                draw.line(game.get_game().displayer.canvas, self.profile.get_color(),
                             position.displayed_position(ps1[i]),
                             position.displayed_position(ps1[i + 1]),
                             width=int((30 - i * 20 / len(ps1)) / self.get_screen_scale()))
                draw.line(game.get_game().displayer.canvas, self.profile.get_color(),
                             position.displayed_position(ps2[i]),
                             position.displayed_position(ps2[i + 1]),
                             width=int((30 - i * 20 / len(ps1)) / self.get_screen_scale()))
        te = [e for e in self.hp_sys.effects if type(e) is effects.StormThrow]
        if len(te):
            if te[0].tick in [3, 6, 9, 12] and sk_z == 'storm_throw':
                if 'throwing' in dir(w):
                    w.throwing = True
                w.attack()
            for e in game.get_game().entities:
                if vector.distance(self.obj.pos[0] - e.obj.pos[0], self.obj.pos[1] - e.obj.pos[1]) < 500:
                    if not e.hp_sys.is_immune:
                        e.hp_sys.damage(w.damages[damages.DamageTypes.PIERCING] * self.attack * self.attacks[1],
                                        damages.DamageTypes.PIERCING)
                        e.hp_sys.enable_immune()
            vr = 180 - self.obj.velocity.get_net_rotation()
            sp = int(te[0].tick * 50 * self.obj.SPEED / self.obj.MASS)
            ps1 = []
            ps2 = []
            for i in range(0, sp, 1):
                d = i / 5
                vx, vy = vector.rotation_coordinate(-vr)
                vdx, vdy = vector.rotation_coordinate(90 - vr)
                ar = te[0].tick / 3 + d / 20
                ps1.append((self.obj.pos[0] + vx * d + math.sin(ar) * vdx * (sp / 4.5 - d) / 8,
                            self.obj.pos[1] + vy * d + math.sin(ar) * vdy * (sp / 4.5 - d) / 8))
                ps2.append((self.obj.pos[0] + vx * d - math.sin(ar) * vdx * (sp / 4.5 - d) / 8,
                            self.obj.pos[1] + vy * d - math.sin(ar) * vdy * (sp / 4.5 - d) / 8))
            for i in range(len(ps1) - 1):
                draw.line(game.get_game().displayer.canvas, self.profile.get_color(),
                          position.displayed_position(ps1[i]),
                          position.displayed_position(ps1[i + 1]),
                          width=int((30 - i * 20 / len(ps1)) / self.get_screen_scale()))
                draw.line(game.get_game().displayer.canvas, self.profile.get_color(),
                          position.displayed_position(ps2[i]),
                          position.displayed_position(ps2[i + 1]),
                          width=int((30 - i * 20 / len(ps1)) / self.get_screen_scale()))
        if len([1 for e in self.hp_sys.effects if type(e) is effects.WarriorShield]):
            if len([1 for s, t in self.hp_sys.shields if s == 'war']):
                pg.draw.circle(game.get_game().displayer.canvas, (0, 255, 255),
                               position.displayed_position(self.obj.pos),
                               int(5 / self.get_screen_scale()),
                               int(100 / self.get_screen_scale()))
        else:
            self.hp_sys.shields = [(s, t) for s, t in self.hp_sys.shields if s != 'war']
        if len([1 for e in self.hp_sys.effects if type(e) is effects.Guard]):
            if len([1 for s, t in self.hp_sys.shields if s == 'gua']):
                pg.draw.circle(game.get_game().displayer.canvas, (0, 255, 255),
                               position.displayed_position(self.obj.pos),
                               int(5 / self.get_screen_scale()),
                               int(100 / self.get_screen_scale()))
        else:
            self.hp_sys.shields = [(s, t) for s, t in self.hp_sys.shields if s != 'gua']
        for i in range(len(self.weapons)):
            if i % len(self.weapons) == 0 and i:
                break
            styles.item_mouse(10 + i * 60, 80,
                              self.weapons[i % len(self.weapons)].name.replace(' ', '_'), str(i),
                              '1', 0.75)
            rect = pg.Rect(10 + i * 60, 80, 60, 60)
            if rect.collidepoint(
                    game.get_game().displayer.reflect(*pg.mouse.get_pos())) and 1 in game.get_game().get_mouse_press():
                self.sel_weapon = i % len(self.weapons)
        try:
            for i, ww in enumerate(self.weapons[self.sel_weapon].weapons):
                styles.item_display(10 + i * 60, 190, ww.name.replace(' ', '_'), self.weapons[self.sel_weapon].PRESET_KEY_SET[i], '1', 0.75)
            for i, ww in enumerate(self.weapons[self.sel_weapon].weapons):
                styles.item_mouse(10 + i * 60, 190, ww.name.replace(' ', '_'), str(i), '1', 0.75)
        except AttributeError:
            pass

        if self.open_inventory or self.open_chest is not None or self.inv_pos < 1500:
            if self.open_inventory:
                for i in range(len(self.accessories)):
                    styles.item_display(10 + i * 90 - self.inv_pos, game.get_game().displayer.SCREEN_HEIGHT - 90,
                                        self.accessories[i].replace(' ', '_'), str(i), '1', 1,
                                        selected=i == self.sel_accessory)
            l = 12
            lr = 4 + {0: 0, 1: 1, 2: 2, 3: 4, 4: 6, 5: 1, 6: 2, 7: 3, 8: 4, 9: 4, 10: 6}[game.get_game().stage]
            while lr * l > len(self.inventory.items) + 2 * lr:
                l -= 1
            self.inv_capacity = lr * l
            for i in range(lr):
                for j in range(l):
                    if i + j * lr < len(self.inventory.items):
                        item, amount = list(self.inventory.items.items())[i + j * lr]
                    else:
                        item, amount = 'null', ''
                    item = inventory.ITEMS[item]
                    styles.item_display(10 + i * 85 - self.inv_pos, game.get_game().displayer.SCREEN_HEIGHT - 180 - j * 85,
                                        item.id, '', str(amount), 1)

            if self.open_chest is not None:
                chest: inventory.Inventory.Chest = self.open_chest
                lw = 12
                for jj in range(chest.n):
                    lx = jj % lw
                    ly = jj // lw
                    ni, nn = chest.items[jj]
                    styles.item_display(displayer.SCREEN_WIDTH - 300 - 80 * (lw - lx),
                                        ly * 80 + 200, ni, '', str(nn), 1,
                                        selected=chest.sel == jj)
                    styles.item_mouse(displayer.SCREEN_WIDTH - 300 - 80 * (lw - lx),
                                      ly * 80 + 200, ni, '', str(nn), 1)
                    rect = pg.Rect(displayer.SCREEN_WIDTH - 300 - 80 * (lw - lx), ly * 80 + 200, 80, 80)
                    if rect.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())) and 1 in game.get_game().get_mouse_press():
                        if chest.sel == jj:
                            nn = chest.items[jj]
                            self.inventory.add_item(inventory.ITEMS[nn[0]], nn[1])
                            chest.items[chest.sel] = ('null', 1)
                        chest.sel = jj
            for i in range(lr):
                for j in range(l):
                    if i + j * lr < len(self.inventory.items):
                        item, amount = list(self.inventory.items.items())[i + j * lr]
                    else:
                        item, amount = 'null', ''
                    item = inventory.ITEMS[item]
                    styles.item_mouse(10 + i * 85 - self.inv_pos, game.get_game().displayer.SCREEN_HEIGHT - 180 - j * 85, item.id,
                                      '', str(amount), 1)
                    rect = pg.Rect(10 + i * 85 - self.inv_pos, game.get_game().displayer.SCREEN_HEIGHT - 180 - j * 85, 80, 80)
                    if rect.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
                        if pg.K_q in game.get_game().get_keys():
                            if item.id != 'null':
                                del self.inventory.items[item.id]
                    if rect.collidepoint(game.get_game().displayer.reflect(
                            *pg.mouse.get_pos())) and 1 in game.get_game().get_mouse_press():
                        if self.open_chest is not None:
                            chest: inventory.Inventory.Chest = self.open_chest
                            nt, ni = chest.items[chest.sel]
                            self.inventory.add_item(inventory.ITEMS[nt], ni)

                            if i + j * lr < len(self.inventory.items):
                                item, amount = list(self.inventory.items.items())[i + j * lr]
                            else:
                                item, amount = 'null', 1
                            self.inventory.remove_item(inventory.ITEMS[item], amount)
                            chest.items[chest.sel] = (item, amount)
                        elif inventory.TAGS['accessory'] in item.tags:
                            if self.tutorial_step == 4:
                                self.tutorial_process += 15
                            self.inventory.remove_item(item)
                            if inventory.TAGS['major_accessory'] in item.tags:
                                self.sel_accessory = 3
                            elif inventory.TAGS['head'] in item.tags:
                                self.sel_accessory = 0
                            elif inventory.TAGS['body'] in item.tags:
                                self.sel_accessory = 1
                            elif inventory.TAGS['leg'] in item.tags:
                                self.sel_accessory = 2
                            elif inventory.TAGS['wings'] in item.tags:
                                self.sel_accessory = 4
                            for ii, a in enumerate(self.accessories):
                                if a == item.id:
                                    self.sel_accessory = ii
                            tt = [['ring'], ['glove', 'gloves'], ['eye'], ['cross'], ['boots'], ['shield'], ['amulet', 'charm']]
                            for t in tt:
                                f = 0
                                for tf in t:
                                    if item.id.endswith(tf):
                                        f = 1
                                        break
                                if f:
                                    ct = 0
                                    for ii, a in enumerate(self.accessories):
                                        for tf in t:
                                            if a.endswith(tf):
                                                ct += 1
                                                if ct >= 1 + (tf == 'ring'):
                                                    self.sel_accessory = ii
                            if self.accessories[self.sel_accessory] != 'null':
                                self.inventory.add_item(inventory.ITEMS[self.accessories[self.sel_accessory]])
                            self.sel_accessory = min(10, self.sel_accessory)
                            self.accessories[self.sel_accessory] = item.id
                            if self.sel_accessory < 3:
                                acc = self.accessories[:3]
                                if not len([1 for a in acc if not str.startswith(a, 'hoverplume')]):
                                    s_b = '_hoverplume_set_bonus'
                                elif not len([1 for a in acc if not str.startswith(a, 'life')]):
                                    s_b = '_life_set_bonus'
                                elif not len([1 for a in acc if not str.startswith(a, 'concept')]):
                                    if self.accessories[0].endswith('hat'):
                                        s_b = '_concept_set_bonus_hat'
                                    else:
                                        s_b = '_concept_set_bonus_mask'
                                elif not len([1 for a in acc if not str.startswith(a, 'ration')]):
                                    s_b = '_ration_set_bonus'
                                elif not len([1 for a in acc if not str.startswith(a, 'evil')]):
                                    s_b = '_evil_set_bonus'
                                elif not len([1 for a in acc if not str.startswith(a, 'nightmare')]):
                                    s_b = '_nightmare_set_bonus'
                                elif not len([1 for a in acc if not str.startswith(a, 'heaven_metal')]):
                                    s_b = '_heaven_metal_set_bonus'
                                elif not len([1 for a in acc if not str.startswith(a, 'heaven_wooden')]):
                                    s_b = '_heaven_wooden_set_bonus'
                                elif not len([1 for a in acc if not str.startswith(a, 'destroy')]):
                                    s_b = '_destroy_set_bonus'
                                elif not len([1 for a in acc if not str.startswith(a, 'create')]):
                                    s_b = '_create_set_bonus'
                                elif not len([1 for a in acc if not str.startswith(a, 'ancient')]):
                                    if self.accessories[0].endswith('helmet'):
                                        s_b = '_ancient_set_bonus_helmet'
                                    elif self.accessories[0].endswith('headgear'):
                                         s_b = '_ancient_set_bonus_headgear'
                                    else:
                                        s_b = '_ancient_set_bonus_hood'
                                elif not len([1 for a in acc[1:] if not str.startswith(a, 'purple_clay')]):
                                    s_b = '_purple_clay_set_bonus'
                                elif not len([1 for a in acc if not str.startswith(a, 'performance')]):
                                    s_b = '_performance_set_bonus'
                                elif not len([1 for a in acc if not str.startswith(a, 'surviving')]):
                                    s_b = '_surviving_set_bonus'
                                elif not len([1 for a in acc if not str.startswith(a, 'assassin')]):
                                    s_b = '_assassin_set_bonus'
                                elif not len([1 for a in acc if not str.startswith(a, 'doomsday_spread')]):
                                    s_b = '_doomsday_spread_set_bonus'
                                elif not len([1 for a in acc if not str.startswith(a, 'primal_galaxy')]):
                                    s_b = '_primal_galaxy_set_bonus'
                                else:
                                    s_b = 'null'
                                if len(self.accessories) < 11:
                                    self.accessories.append('null')
                                self.accessories[10] = s_b
                        elif inventory.TAGS['weapon'] in item.tags:
                            if self.tutorial_step == 4:
                                self.tutorial_process += 15
                            self.inventory.remove_item(item)
                            if self.weapons[self.sel_weapon].name != 'null':
                                self.inventory.add_item(
                                    inventory.ITEMS[self.weapons[self.sel_weapon].name.replace(' ', '_')])
                            self.weapons[self.sel_weapon] = weapons.WEAPONS[item.id]
                        elif item.id == 'mana_crystal':
                            if self.max_mana < 180:
                                self.max_mana = min(self.max_mana + 15, 180)
                                self.inventory.remove_item(item)
                        elif item.id == 'regenerative_crystal':
                            if self.max_mana < 320:
                                self.max_mana = min(self.max_mana + 35, 320)
                                self.inventory.remove_item(item)
                        elif item.id == 'enchanted_book':
                            if self.max_mana < 300:
                                self.max_mana += 30
                                self.inventory.remove_item(item)
                        elif item.id == 'chaos_ingot':
                            r = random.randint(1, 9)
                            if r == 1:
                                t = 'soul_of_flying'
                            elif r == 2:
                                t = 'soul_of_growth'
                            elif r == 3:
                                t = 'soul_of_coldness'
                            elif r == 4:
                                t = 'soul_of_integrity'
                            elif r == 5:
                                t = 'soul_of_kindness'
                            elif r == 6:
                                t = 'soul_of_bravery'
                            elif r == 7:
                                t = 'soul_of_perseverance'
                            elif r == 8:
                                t = 'soul_of_justice'
                            else:
                                t = 'soul_of_patience'
                            self.inventory.remove_item(item)
                            self.inventory.add_item(inventory.ITEMS[t], random.randint(1, 3))
                        elif item.id == 'white_guard':
                            self.hp_sys.shields.append(('W.Guard', 20))
                            self.inventory.remove_item(item)
                        elif item.id == 'apple':
                            self.hp_sys.shields.append(('Apple', 200))
                            self.hp_sys.heal(99999)
                            self.inventory.remove_item(item)
                        elif item.id == 'firy_plant':
                            if self.hp_sys.max_hp < 500:
                                self.hp_sys.max_hp += 20
                                self.inventory.remove_item(item)
                        elif item.id == 'spiritual_heart':
                            if self.hp_sys.max_hp >= 500 and self.max_mana >= 120:
                                self.hp_sys.max_hp = 600
                                self.max_mana = 300
                                self.inventory.remove_item(item)
                            self.profile.add_point(1)
                            self.profile.add_point(6)
                            b = 0
                            if not 'L3' in game.get_game().player.nts:
                                game.get_game().player.nts.append('L3')
                                b = 1
                            if b:
                                game.get_game().dialog.push_dialog('Notebook Updated!', "The otherworld invasion have stopped!")
                                if game.get_game().player.inventory.is_enough(inventory.ITEMS['otherworld_stone']):
                                    game.get_game().player.inventory.items['otherworld_stone'] = 0
                        elif item.id == 'life_fruit':
                            if self.hp_sys.max_hp >= 600 and self.max_mana >= 300 and self.max_talent >= 10:
                                self.hp_sys.max_hp = 1000
                                self.max_mana = 800
                                self.max_talent = 50
                                self.inventory.remove_item(item)
                                self.profile.add_point(2)
                        elif item.id == 'saint_apple':
                            if self.hp_sys.max_hp >= 600 and self.max_mana >= 300:
                                self.hp_sys.max_hp = 1500
                                self.max_mana = 1000
                                self.max_talent = 30
                                self.inventory.remove_item(item)
                                self.profile.add_point(7)
                        elif item.id == 'mind_ball':
                            if self.hp_sys.max_hp >= 1500 and self.max_mana >= 1000 and self.max_talent >= 30:
                                self.hp_sys.max_hp = 3000
                                self.max_talent = 100
                                self.inventory.remove_item(item)
                                self.profile.add_point(8)
                        elif item.id == 'soul_of_determination':
                            if self.hp_sys.max_hp == 1000 and self.max_mana == 800 and self.max_talent == 50 and \
                                random.randint(0, 4) == 0:
                                self.hp_sys.max_hp = 1500
                                self.max_talent = 1500
                                self.inventory.remove_item(item)
                                self.profile.add_point(3)
                            else:
                                self.hp_sys.damage(random.randint(500, 1000), damages.DamageTypes.MAGICAL)

                        elif item.id == 'nice_cream':
                            self.hp_sys.effect(effects.Agility(36, 1))

                        elif item.id == 'note':
                            if self.max_inspiration < 2000:
                                self.max_inspiration += 200
                                self.inventory.remove_item(item)

                        elif item.id == 'mystery_core':
                            if self.max_talent < 10:
                                self.max_talent += 1
                            else:
                                self.talent = min(self.talent + 5, self.max_talent)
                            self.inventory.remove_item(item)
                        elif item.id == 'toilet_paper':
                            self.talent = self.max_talent
                            self.inventory.remove_item(item)
                        elif inventory.TAGS['ammo_arrow'] in item.tags:
                            self.ammo = (item.id, self.inventory.items[item.id])
                            self.inventory.items[item.id] = 0
                            self.inventory.add_item(inventory.ITEMS[self.ammo[0]], self.ammo[1])
                        elif inventory.TAGS['ammo_bullet'] in item.tags:
                            self.ammo_bullet = (item.id, self.inventory.items[item.id])
                            self.inventory.items[item.id] = 0
                            self.inventory.add_item(inventory.ITEMS[self.ammo_bullet[0]], self.ammo_bullet[1])


                        elif item.id == 'chest':
                            self.inventory.remove_item(item)
                            ee = entity.Entities.Chest(self.obj.pos, 1)
                            ee.sm = False
                            # game.get_game().furniture.append(ee)
                        elif item.id == 'suspicious_eye':
                            if not len([1 for e in game.get_game().player.hp_sys.effects if type(e) is effects.StoneAltar]):
                                game.get_game().dialog.dialog('Unable to summon True Eye.', 'There is no Stone Altar nearby.')
                            else:
                                entity.entity_spawn(entity.Entities.TrueEye, 2000, 2000, 0, 1145, 100000)
                                self.inventory.remove_item(item)
                        elif item.id == 'wild_fluffball':
                            if not len([1 for e in game.get_game().player.hp_sys.effects if
                                        type(e) is effects.StoneAltar]):
                                game.get_game().dialog.dialog('Unable to summon Fluffff.',
                                                              'There is no Stone Altar nearby.')
                            else:
                                entity.entity_spawn(entity.Entities.Fluffff, 2000, 2000, 0, 1145, 100000)
                                self.inventory.remove_item(item)
                        elif item.id == 'fire_slime':
                            if not len([1 for e in game.get_game().player.hp_sys.effects if
                                        type(e) is effects.StoneAltar]):
                                game.get_game().dialog.dialog('Unable to summon Magma King.',
                                                              'There is no Stone Altar nearby.')
                            else:
                                entity.entity_spawn(entity.Entities.MagmaKing, 2000, 2000, 0, 1145, 100000)
                                entity.entity_spawn(entity.Entities.MagmaKingCounter, 2000, 2000, 0, 1145, 100000)
                                self.inventory.remove_item(item)
                        elif item.id == 'monument':
                            if not len([1 for e in game.get_game().player.hp_sys.effects if
                                        type(e) is effects.StoneAltar]):
                                game.get_game().dialog.dialog('Unable to summon Azure Stele.',
                                                              'There is no Stone Altar nearby.')
                            else:
                                entity.entity_spawn(entity.Entities.AzureStele, 2000, 2000, 0, 1145, 100000)
                                self.inventory.remove_item(item)
                        elif item.id == 'red_apple':
                            if not len([1 for e in game.get_game().player.hp_sys.effects if
                                        type(e) is effects.StoneAltar]):
                                game.get_game().dialog.dialog('Unable to summon the World\'s Fruit.',
                                                              'There is no Stone Altar nearby.')
                            else:
                                entity.entity_spawn(entity.Entities.TheWorldsFruit, 2000, 2000, 0, 1145, 100000)
                                self.inventory.remove_item(item)
                        elif item.id == 'wind':
                            if not len([1 for e in game.get_game().player.hp_sys.effects if
                                        type(e) is effects.StoneAltar]):
                                game.get_game().dialog.dialog('Unable to summon Sandstorm.',
                                                              'There is no Stone Altar nearby.')
                            else:
                                entity.entity_spawn(entity.Entities.SandStorm, 2000, 2000, 0, 1145, 100000)
                                self.inventory.remove_item(item)
                        elif item.id == 'blood_substance':
                            if not len([1 for e in game.get_game().player.hp_sys.effects if
                                        type(e) is effects.StoneAltar]):
                                game.get_game().dialog.dialog('Unable to summon Abyss Eye.',
                                                              'There is no Stone Altar nearby.')
                            else:
                                entity.entity_spawn(entity.Entities.AbyssEye, 1600, 1600, 0, 1145, 100000)
                                self.inventory.remove_item(item)
                        elif item.id == 'legend_soul':
                            if not self.inventory.is_enough(inventory.ITEMS['soulfeather']) and game.get_game().stage == 0:
                                entity.entity_spawn(entity.Entities.Ray, 1600, 1600, 0, 1145, 100000)
                                self.inventory.remove_item(item)
                        elif item.id == 'sky_painting':
                            if not len([1 for e in game.get_game().player.hp_sys.effects if
                                        type(e) is effects.MetalAltar]):
                                game.get_game().dialog.dialog('Unable to summon the Sky Cubes.',
                                                              'There is no Metal Altar nearby.')
                            else:
                                entity.entity_spawn(entity.Entities.SkyCubeFighter, 2000, 2000, 0, 1145, 100000)
                                entity.entity_spawn(entity.Entities.SkyCubeRanger, 2000, 2000, 0, 1145, 100000)
                                entity.entity_spawn(entity.Entities.SkyCubeBlocker, 2000, 2000, 0, 1145, 100000)
                        elif item.id == 'green_thing':
                            if not len([1 for e in game.get_game().player.hp_sys.effects if
                                        type(e) in [effects.MetalAltar, effects.ScarlettAltar]]):
                                game.get_game().dialog.dialog('Unable to summon the Heaven Goblins.',
                                                              'There is no Metal Altar nearby.')
                            elif game.get_game().chapter == 1:
                                entity.entity_spawn(entity.Entities.GoblinWaveEP2, 2000, 2000, 0, 1145, 100000)
                            else:
                                entity.entity_spawn(entity.Entities.GoblinWave, 2000, 2000, 0, 1145, 100000)
                        elif item.id == 'mechanic_eye':
                            if not len([1 for e in game.get_game().player.hp_sys.effects if
                                        type(e) is effects.MetalAltar]):
                                game.get_game().dialog.dialog('Unable to summon Faithless and Truthless Eyes.',
                                                               'There is no Metal Altar nearby.')
                            else:
                                entity.entity_spawn(entity.Entities.FaithlessEye, 2000, 2000, 0, 1145, 100000)
                                entity.entity_spawn(entity.Entities.TruthlessEye, 2000, 2000, 0, 1145, 100000)
                                self.inventory.remove_item(item)
                        elif item.id == 'mechanic_worm':
                            if not len([1 for e in game.get_game().player.hp_sys.effects if
                                        type(e) is effects.MetalAltar]):
                                game.get_game().dialog.dialog('Unable to summon Destroyer.',
                                                              'There is no Metal Altar nearby.')
                            else:
                                entity.entity_spawn(entity.Entities.Destroyer, 4000, 4000, 0, 1145, 100000)
                                self.inventory.remove_item(item)
                        elif item.id == 'electric_unit':
                            if not len([1 for e in game.get_game().player.hp_sys.effects if
                                        type(e) is effects.MetalAltar]):
                                game.get_game().dialog.dialog('Unable to summon The CPU.',
                                                              'There is no Metal Altar nearby.')
                            else:
                                entity.entity_spawn(entity.Entities.TheCPU, 2000, 2000, 0, 1145, 100000)
                                self.inventory.remove_item(item)
                        elif item.id == 'mechanic_spider':
                            if not len([1 for e in game.get_game().player.hp_sys.effects if
                                        type(e) is effects.MetalAltar]):
                                game.get_game().dialog.dialog('Unable to summon Greed.',
                                                              'There is no Metal Altar nearby.')
                            else:
                                entity.entity_spawn(entity.Entities.Greed, 2000, 2000, 0, 1145, 100000)
                                self.inventory.remove_item(item)
                        elif item.id == 'watch':
                            if not len([1 for e in game.get_game().player.hp_sys.effects if
                                        type(e) is effects.MetalAltar]):
                                game.get_game().dialog.dialog('Unable to summon Clock.',
                                                               'There is no Metal Altar nearby.')
                            else:
                                entity.entity_spawn(entity.Entities.EyeOfTime, 2000, 2000, 0, 1145, 100000)
                                self.inventory.remove_item(item)
                        elif item.id == 'metal_food':
                            if not len([1 for e in game.get_game().player.hp_sys.effects if
                                        type(e) is effects.MetalAltar]):
                                game.get_game().dialog.dialog('Unable to summon Devil Python.',
                                                              'There is no Metal Altar nearby.')
                            else:
                                entity.entity_spawn(entity.Entities.DevilPython, 2000, 2000, 0, 1145, 100000)
                                self.inventory.remove_item(item)
                        elif item.id == 'joker':
                            if len([1 for e in game.get_game().player.hp_sys.effects if
                                        type(e) is effects.MetalAltar]):
                                entity.entity_spawn(entity.Entities.Jevil, 2000, 2000, 0, 1145, 100000)
                                self.inventory.remove_item(item)
                            elif len([1 for e in game.get_game().player.hp_sys.effects if
                                        type(e) is effects.ScarlettAltar]):
                                entity.entity_spawn(entity.Entities.Jevil2, 2000, 2000, 0, 1145, 100000)
                                self.inventory.remove_item(item)
                            else:
                                game.get_game().dialog.dialog('Unable to summon Jevil.',
                                                              'There is no Metal Altar nearby.')

                        elif item.id == 'plantera_bulb':
                            self.inventory.remove_item(item)
                            entity.entity_spawn(entity.Entities.Plantera, 2000, 2000, 0, 1145, 100000)
                            self.inventory.remove_item(item)
                        elif item.id == 'origin':
                            if len([1 for e in self.hp_sys.effects if type(e) == effects.TimeStop]):
                                entity.entity_spawn(entity.Entities.CLOCK, 2000, 2000, 0, 1145, 100000)
                            elif game.get_game().get_biome() == 'heaven':
                                entity.entity_spawn(entity.Entities.GodsEye, 2000, 2000, 0, 1145, 100000)
                            elif self.inventory.is_enough(inventory.ITEMS['suspicious_substance']):
                                entity.entity_spawn(entity.Entities.MATTER, 2000, 2000, 0, 1145, 100000)
                        elif item.id == 'mechanical':
                            if not len([1 for e in game.get_game().player.hp_sys.effects if
                                        type(e) is effects.ScarlettAltar]):
                                game.get_game().dialog.dialog('Unable to summon the Mechanical Medusa.',
                                                               'There is no Scarlett Altar nearby.')
                            else:
                                entity.entity_spawn(entity.Entities.MechanicalMedusa, 2000, 2000, 0, 1145, 100000)
                                self.inventory.remove_item(item)
                        elif item.id == 'dark_skull':
                            if not len([1 for e in game.get_game().player.hp_sys.effects if
                                        type(e) is effects.ScarlettAltar]):
                                game.get_game().dialog.dialog('Unable to summon the Wither.',
                                                               'There is no Scarlett Altar nearby.')
                            else:
                                entity.entity_spawn(entity.Entities.TheWither, 2000, 2000, 0, 1145, 100000)
                                self.inventory.remove_item(item)
                        elif item.id == 'plastic_flower':
                            if not len([1 for e in game.get_game().player.hp_sys.effects if
                                        type(e) is effects.ScarlettAltar]):
                                game.get_game().dialog.dialog('Unable to summon the Life Watcher.',
                                                               'There is no Scarlett Altar nearby.')
                            else:
                                entity.entity_spawn(entity.Entities.LifeWatcher, 2000, 2000, 0, 1145, 100000)
                                self.inventory.remove_item(item)
                        elif item.id == 'huge_snowball':
                            if not len([1 for e in game.get_game().player.hp_sys.effects if
                                        type(e) is effects.ScarlettAltar]):
                                game.get_game().dialog.dialog('Unable to summon the Polar Cube.',
                                                               'There is no Scarlett Altar nearby.')
                            else:
                                entity.entity_spawn(entity.Entities.PolarCube, 2000, 2000, 0, 1145, 100000)
                                self.inventory.remove_item(item)
                        elif item.id == 'dragon_horn':
                            if game.get_game().get_biome() == 'hell':
                                entity.entity_spawn(entity.Entities.Ignis, 2000, 2000, 0, 1145, 100000)
                            elif game.get_game().get_biome() == 'snowland':
                                entity.entity_spawn(entity.Entities.Northrend, 2000, 2000, 0, 1145, 100000)
                            elif game.get_game().get_biome() == 'wither':
                                entity.entity_spawn(entity.Entities.Nefarian, 2000, 2000, 0, 1145, 100000)
                            elif game.get_game().get_biome() == 'hallow':
                                entity.entity_spawn(entity.Entities.Olivia, 2000, 2000, 0, 1145, 100000)
                            elif game.get_game().get_biome() == 'desert':
                                entity.entity_spawn(entity.Entities.Cybress, 2000, 2000, 0, 1145, 100000)
                            elif game.get_game().get_biome() == 'heaven':
                                entity.entity_spawn(entity.Entities.Eonar, 2000, 2000, 0, 1145, 100000)
                            else:
                                game.get_game().dialog.dialog('...', 'But nothing happened.')
                        elif item.id == 'poison_horn':
                            if game.get_game().get_biome() == 'rainforest':
                                entity.entity_spawn(entity.Entities.Naga, 2000, 2000, 0, 1145, 100000)
                            else:
                                game.get_game().dialog.dialog('...', 'But nothing happened.')
                        elif item.id == 'ends_sphere':
                            entity.entity_spawn(entity.Entities.OblivionAnnihilator, 2000, 2000, 0, 1145, 100000)
                            self.inventory.remove_item(item)
                        elif item.id == 'my_soul':
                            self.profile.add_point(4)
                            if sum([v for _, v in self.hp_sys.shields]) + self.hp_sys.hp > self.hp_sys.max_hp:
                                entity.entity_spawn(entity.Entities.ReincarnationTheWorldsTree, 2000, 2000, 0, 1145, 100000)
                            else:
                                entity.entity_spawn(entity.Entities.Faith, 2000, 2000, 0, 1145, 100000)
                        elif item.id == 'finale__soul':
                            self.covered_items.extend(self.accessories)
                            self.covered_items.extend([i for i in self.inventory.items.keys() if inventory.TAGS['ce_item'] in inventory.ITEMS[i].tags])
                            self.profile.add_point(5)
                        elif item.id == 'finale__earth_core':
                            self.covered_items.extend(self.accessories)
                            self.covered_items.extend([i for i in self.inventory.items.keys() if inventory.TAGS['ce_item'] in inventory.ITEMS[i].tags])
                            self.profile.add_point(9)


                        elif item.id == 'biocooler':
                            if self.inventory.is_enough(inventory.ITEMS['mechanic_workstation']):
                                self.inventory.remove_item(inventory.ITEMS['mechanic_workstation'])
                                self.inventory.remove_item(item)
                                self.inventory.add_item(inventory.ITEMS['mechanic_workstation2'])
                        elif item.id == 'atomic_heater':
                            if self.inventory.is_enough(inventory.ITEMS['mechanic_workstation2']):
                                self.inventory.remove_item(inventory.ITEMS['mechanic_workstation2'])
                                self.inventory.remove_item(item)
                                self.inventory.add_item(inventory.ITEMS['mechanic_workstation3'])
                        elif item.id == 'precised_mechanical_hand':
                            if self.inventory.is_enough(inventory.ITEMS['mechanic_workstation3']):
                                self.inventory.remove_item(inventory.ITEMS['mechanic_workstation3'])
                                self.inventory.remove_item(item)
                                self.inventory.add_item(inventory.ITEMS['mechanic_workstation4'])

                        elif item.id == 'lychee':
                            if len([1 for e in game.get_game().player.hp_sys.effects if type(e) is effects.CurseTree]):
                                entity.entity_spawn(underia3.LycheeKing, 2000, 2000, 0, 1145, 100000)
                        elif item.id == 'intestine':
                            if len([1 for e in game.get_game().player.hp_sys.effects if type(e) is effects.CurseSnow]):
                                entity.entity_spawn(underia3.ToxicLargeIntestine, 2000, 2000, 0, 1145, 100000)
                        elif item.id == 'bombombomb':
                            if len([1 for e in game.get_game().player.hp_sys.effects if type(e) is effects.CurseSand]):
                                entity.entity_spawn(underia3.BombardinoCrocodilo, 2000, 2000, 0, 1145, 100000)
                        elif item.id == 'suspicious_rune_eye':
                            entity.entity_spawn(underia3.PetrifiedWitness, 2000, 2000, 0, 1145, 100000)
                        elif item.id == 'dark_distortion':
                            entity.entity_spawn(underia3.DeathWhisperChicken, 2000, 2000, 0, 1145, 100000)
                        elif item.id == 'nike_shoes':
                            entity.entity_spawn(underia3.TralaleroTralala, 2000, 2000, 0, 1145, 100000)

                        elif item.id == 'hope_sign':
                            its = {'karmic_helmet': 'e_karmic_helmet', 'karmic_chestplate': 'e_karmic_chestplate', 'karmic_greaves': 'e_karmic_greaves',
                                     'galaxy_broadsword': 'e_galaxy_broadsword'}
                            '''
                                                  , 'turning_point': 'e_turning_point', 'climax': 'e_climax', 
                             'resolution': 'e_resolution', 'rising_action': 'e_rising_action', 'falling_action': 'e_falling_action'}
                             '''
                            if len(self.covered_items):
                                it = random.choice(self.covered_items)
                                if it in its:
                                    self.inventory.add_item(inventory.ITEMS[its[it]])
                                    self.covered_items.remove(it)
                                    self.inventory.remove_item(item)
                                else:
                                    game.get_game().dialog.dialog('...', 'But nothing happened.')
                            else:
                                game.get_game().dialog.dialog('...', 'But nothing happened.')

                        elif item.id == 'muse_core':
                            if self.max_inspiration < 800:
                                self.max_inspiration = 800
                                self.profile.add_point(6)
                                self.hp_sys.effect(effects.Weak(10 ** 9, 1))
                        elif item.id == 'yellow_flower':
                            entity.entity_spawn(entity.Entities.OmegaFlowery, 2000, 2000, 0, 1145, 100000)
                            self.inventory.remove_item(item)
                        elif item.id == 'recipe_book':
                            rep = [r for r in inventory.RECIPES if r.is_related(self.inventory)]
                            window_opened = bool(len(rep))
                            sel = 0
                            window = pg.display.get_surface()
                            wx = window.get_width() // 2
                            wy = window.get_height() // 2
                            lft = pg.font.Font(path.get_path('assets/dtm-mono.otf' if constants.LANG != 'zh' else 'assets/fz-pixel.ttf'), 45)
                            lss = pg.font.Font(path.get_path('assets/dtm-mono.otf' if constants.LANG != 'zh' else 'assets/fz-pixel.ttf'), 24)
                            while window_opened:
                                for event in pg.event.get():
                                    if event.type == pg.QUIT:
                                        window_opened = False
                                    if event.type == pg.KEYDOWN:
                                        if event.key == pg.K_ESCAPE:
                                            window_opened = False
                                        elif event.key == pg.K_F4:
                                            constants.FULLSCREEN = not constants.FULLSCREEN
                                            pg.display.set_mode(pg.display.get_window_size(), (pg.FULLSCREEN if constants.FULLSCREEN else 0) | constants.FLAGS)
                                        if event.key == pg.K_UP:
                                            sel = (sel - 1 + len(rep)) % len(rep)
                                        if event.key == pg.K_DOWN:
                                            sel = (sel + 1) % len(rep)
                                pg.draw.rect(window, (255, 255, 255), (wx - 480, wy - 300, 960, 640))
                                pg.draw.rect(window, (0, 0, 0), (wx - 480, wy - 300, 960, 640), 18)
                                f = lss.render(f"{sel + 1}/{len(rep)}", True, (0, 0, 0))
                                fr = f.get_rect(midbottom=(wx, wy + 320))
                                window.blit(f, fr)
                                cr = rep[sel]
                                styles.item_display(wx - 448, wy - 184, cr.result, '',
                                                    str(cr.crafted_amount), 1.6, _window=window,
                                                    mp=pg.mouse.get_pos())
                                j = 0
                                ml = 6
                                for it, qt in cr.material.items():
                                    styles.item_display(wx + 32 + 68 * (j % ml), wy - 184 + 68 * (j // ml), it, '', str(qt),
                                                        .8, _window=window, red=not self.inventory.is_enough(inventory.ITEMS[it], qt),
                                                        mp=pg.mouse.get_pos())
                                    j += 1
                                tt = lft.render(inventory.ITEMS[cr.result].name if len(inventory.ITEMS[cr.result].name) < 20 \
                                                    else inventory.ITEMS[cr.result].name[:16] + '...',True, (0, 0, 0))
                                window.blit(tt, (wx - 448, wy - 264))
                                tr = lft.render(styles.text(f"Materials: "), True, (0, 0, 0))
                                window.blit(tr, (wx + 32, wy - 264))
                                desc = inventory.ITEMS[cr.result].get_full_desc().split('\n')
                                for ii in range(len(desc)):
                                    if len(desc[ii]) > 30:
                                        s = desc[ii]
                                        desc.remove(s)
                                        desc.insert(ii, s[30:])
                                        desc.insert(ii, s[:30] + '-')
                                        ii -= 1
                                for j, d in enumerate(desc):
                                    td = lss.render(styles.text(d), True, (0, 0, 0))
                                    window.blit(td, (wx - 448, wy - 40 + 24 * j))
                                j = 0
                                for it, qt in cr.material.items():
                                    r = pg.Rect(wx + 32 + 68 * (j % ml), wy - 184 + 68 * (j // ml), 64, 64)
                                    if r.collidepoint(pg.mouse.get_pos()):
                                        try:
                                            am = self.inventory.items[it]
                                        except KeyError:
                                            am = 0
                                        desc = inventory.ITEMS[it].get_full_desc().split('\n')
                                        desc = [f'{inventory.ITEMS[it].name}({am}/{qt})'] + desc
                                        for ii in range(len(desc)):
                                            if len(desc[ii]) > 30:
                                                s = desc[ii]
                                                desc.remove(s)
                                                desc.insert(ii, s[30:])
                                                desc.insert(ii, s[:30] + '-')
                                                ii -= 1
                                        for j, d in enumerate(desc):
                                            td = lss.render(styles.text(d), True, (0, 0, 0))
                                            window.blit(td, (wx + 32, wy - 40 + 24 * j + \
                                                             max(0, len(cr.material) // ml - 1) * 68))
                                        break
                                    j += 1
                                pg.display.update()
                            game.get_game().pressed_keys = []
                            game.get_game().pressed_mouse = []

                        if len(status) >= 10:
                            game.get_game().dialog.dialog('Ten status in row!', 'Status clear!')
                            status.clear()

                        if random.random() < 0.8 and constants.APRIL_FOOL:
                            game.get_game().dialog.dialog('A lucky selection!', 'You get the effect...')
                            s = random.randint(1, 6)
                            if s == 1:
                                game.get_game().dialog.push_dialog('Shielded!')
                                ef = random.choices(['shield', 'un-shield', 'more_hp'], [.5, .3, .2])[0]
                                if ef == 'more_hp':
                                    self.hp_sys.shields.append(('April Fool', self.hp_sys.max_hp // 2))
                                status.append(ef)
                            elif s == 2:
                                game.get_game().dialog.push_dialog('Strength!')
                                ef = random.choices(['strength', 'critical', 'un-strength'], [.3, .3, .4])[0]
                                status.append(ef)
                            elif s == 3:
                                game.get_game().dialog.push_dialog('Unlimited mana!')
                                ef = random.choices(['un-mana', 'mana-regen', 'un-mana-regen'], [.6, .1, .3])[0]
                                status.append(ef)
                            elif s == 4:
                                game.get_game().dialog.push_dialog('Random Item!')
                                if random.random() < 0.6:
                                    self.inventory.add_item(inventory.ITEMS[random.choice(['wood', 'leaf'])])
                                elif random.random() < 0.5:
                                    self.inventory.add_item(inventory.ITEMS['magic_shard_' + str(random.randint(1, 127))])
                                else:
                                    self.inventory.add_item(random.choice(inventory.ITEMS.values()))
                                status.append('random_item')
                            elif s == 5:
                                game.get_game().dialog.push_dialog('Text-ture!')
                                graphics = game.get_game().graphics

                                font = pg.font.SysFont('papyrus', 180)

                                for k, v in graphics.graphics.items():
                                    if random.random() > .05:
                                        continue
                                    sx, sy = 128, 128
                                    fr = font.render(k.split('_')[-1], True, (255, 255, 255), (0, 0, 0))
                                    fr = pg.transform.scale(fr, (sx, fr.get_height() * sx / fr.get_width()))
                                    surf = pg.Surface((sx, sy), pg.SRCALPHA)
                                    frr = fr.get_rect()
                                    frr.center = surf.get_rect().center
                                    surf.blit(fr, frr)
                                    graphics.graphics[k] = surf

                                status.append('text-ture')
                            elif s == 6:
                                game.get_game().dialog.push_dialog('Computer crash!')
                                constants.FPS = min(30, constants.FPS - 6)
                                status.append('crash')
                        self.in_ui = True
            for i in range(len(self.accessories)):
                styles.item_mouse(10 + i * 90 - self.inv_pos, game.get_game().displayer.SCREEN_HEIGHT - 90,
                                  self.accessories[i].replace(' ', '_'), str(i), '1', 1)
                rect = pg.Rect(10 + i * 90 - self.inv_pos, game.get_game().displayer.SCREEN_HEIGHT - 90, 90, 90)
                if rect.collidepoint(game.get_game().displayer.reflect(
                        *pg.mouse.get_pos())) and 1 in game.get_game().get_mouse_press():
                    self.sel_accessory = i


            nx = displayer.canvas.get_width() - 180
            ny = displayer.canvas.get_height() / 2

            note_rect = pg.Rect(nx - 100 + self.inv_pos // 3, ny - 180, 60, 60)
            for i in range(game.get_game().chapter + 1):
                im = game.get_game().graphics['background_ui_note']
                if not note_rect.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
                    im = pg.transform.scale(im, (54, 54))
                imr = im.get_rect(center=note_rect.center)
                displayer.canvas.blit(im, imr)
                if note_rect.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
                    t = f'Notebook {"ABCDEF"[i]}'
                    f = displayer.font.render(styles.text(t), True, (255, 255, 255))
                    fb = displayer.font.render(styles.text(t), True, (0, 0, 0))
                    mx, my = game.get_game().displayer.reflect(*pg.mouse.get_pos())
                    mx -= f.get_width()
                    game.get_game().displayer.canvas.blit(fb, (mx + 3, my + 3))
                    game.get_game().displayer.canvas.blit(f, (mx, my))
                    if 1 in game.get_game().get_mouse_press():
                        game.get_game().play_sound('grab')
                        notebook.show_notebook(i)
                note_rect.y += 60

            nx = displayer.canvas.get_width() - 180 + self.inv_pos // 3
            ny = displayer.canvas.get_height() / 2

            rec_rect = pg.Rect(nx - 30, ny - 30, 60, 60)
            im = game.get_game().graphics['background_ui_recipes']
            if not rec_rect.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
                im = pg.transform.scale(im, (54, 54))
            imr = im.get_rect(center=(nx, ny))
            displayer.canvas.blit(im, imr)
            ny += 60
            rco_rect = pg.Rect(nx - 30, ny - 30, 60, 60)
            im = game.get_game().graphics['background_ui_recipe_overlook']
            if not rco_rect.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
                im = pg.transform.scale(im, (54, 54))
            imr = im.get_rect(center=(nx, ny))
            if self.ui_recipes:
                displayer.canvas.blit(im, imr)
            ny += 60
            rcv_rect = pg.Rect(nx - 30, ny - 30, 60, 60)
            im = game.get_game().graphics['background_ui_recipe_view']
            if not rcv_rect.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
                im = pg.transform.scale(im, (54, 54))
            imr = im.get_rect(center=(nx, ny))
            if self.ui_recipes:
                displayer.canvas.blit(im, imr)
            if rec_rect.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
                self.in_ui = True
                mouse_text = True
                if 1 in game.get_game().get_mouse_press():
                    self.ui_recipes = not self.ui_recipes
                    if not self.ui_recipes:
                        self.ui_recipe_overlook = False
                f = displayer.font.render(styles.text(f"Crafting"), True, (255, 255, 255))
                fb = displayer.font.render(styles.text(f"Crafting"), True, (0, 0, 0))
                mx, my = game.get_game().displayer.reflect(*pg.mouse.get_pos())
                mx -= f.get_width()
                game.get_game().displayer.canvas.blit(fb, (mx + 3, my + 3))
                game.get_game().displayer.canvas.blit(f, (mx, my))
            if self.ui_recipes and rco_rect.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
                self.in_ui = True
                mouse_text = True
                if 1 in game.get_game().get_mouse_press():
                    self.ui_recipe_overlook = not self.ui_recipe_overlook
                f = displayer.font.render(styles.text(f"Recipes"), True, (255, 255, 255))
                fb = displayer.font.render(styles.text(f"Recipes"), True, (0, 0, 0))
                mx, my = game.get_game().displayer.reflect(*pg.mouse.get_pos())
                mx -= f.get_width()
                game.get_game().displayer.canvas.blit(fb, (mx + 3, my + 3))
                game.get_game().displayer.canvas.blit(f, (mx, my))
            if self.ui_recipes and rcv_rect.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
                self.in_ui = True
                mouse_text = True
                if 1 in game.get_game().get_mouse_press():
                    self.ui_recipe_view = not self.ui_recipe_view
                f = displayer.font.render(styles.text(f"Recipes: " + ("All" if self.ui_recipe_view else "Craftable")), True, (255, 255, 255))
                fb = displayer.font.render(styles.text(f"Recipes: " + ("All" if self.ui_recipe_view else "Craftable")), True, (0, 0, 0))
                mx, my = game.get_game().displayer.reflect(*pg.mouse.get_pos())
                mx -= f.get_width()
                game.get_game().displayer.canvas.blit(fb, (mx + 3, my + 3))
                game.get_game().displayer.canvas.blit(f, (mx, my))
            self.recipes = [r for r in inventory.RECIPES if r.is_valid(self.inventory) or (self.ui_recipe_view and r.is_related(self.inventory))]
            if len(self.recipes) and self.ui_recipes:
                self.sel_recipe %= len(self.recipes)
                if pg.K_UP in game.get_game().get_keys():
                    self.sel_recipe = (self.sel_recipe - 1) % len(self.recipes)
                if pg.K_DOWN in game.get_game().get_keys():
                    self.sel_recipe = (self.sel_recipe + 1) % len(self.recipes)
                cur_recipe = self.recipes[self.sel_recipe]
                styles.item_display(game.get_game().displayer.SCREEN_WIDTH - 260 + self.inv_pos // 3,
                                    game.get_game().displayer.SCREEN_HEIGHT - 170,
                                    cur_recipe.result, str(self.sel_recipe + 1), str(cur_recipe.crafted_amount), 2,
                                    red= not cur_recipe.is_valid(self.inventory))
                i = 0
                for item, amount in cur_recipe.material.items():
                    styles.item_display(
                        game.get_game().displayer.SCREEN_WIDTH - 20 - 80 * (1 + len(cur_recipe.material)) + 80 * i + self.inv_pos // 3,
                        game.get_game().displayer.SCREEN_HEIGHT - 250, item, '', str(amount), 1)
                    i += 1
                if pg.Rect(game.get_game().displayer.SCREEN_WIDTH - 260 + self.inv_pos // 3, game.get_game().displayer.SCREEN_HEIGHT - 170,
                           160, 160).collidepoint(game.get_game().displayer.reflect(
                        *pg.mouse.get_pos())) and 1 in game.get_game().get_mouse_press() and cur_recipe.is_valid(self.inventory):
                    rc = cur_recipe
                    cur_recipe.make(self.inventory)
                    game.get_game().play_sound('grab')
                    if len(self.inventory.items) > self.inv_capacity:
                        k, v = self.inventory.items.popitem()
                        game.get_game().drop_items.append(entity.Entities.DropItem(self.obj.pos, k, v))
                    self.recipes = [r for r in inventory.RECIPES if r.is_valid(self.inventory) or (self.ui_recipe_view and r.is_related(self.inventory))]
                    res = [i for i, r in enumerate(self.recipes) if r is rc]
                    self.sel_recipe = res[0] if res else 0
                    if self.tutorial_step == 3:
                        self.tutorial_process += 20
                    if rc.result == 'chest':
                        self.cc_t += 1
                        if self.cc_t == 1:
                            tr = inventory.Recipe({'iron_ingot': 10, 'cobalt_ingot': 10, 'silver_ingot': 7, 'steel_ingot': 7, 'anvil': 1}, 'chest')
                        elif self.cc_t == 2:
                            tr = inventory.Recipe({'zirconium_ingot': 15, 'platinum_ingot': 15, 'anvil': 1}, 'chest')
                        elif self.cc_t == 3:
                            tr = inventory.Recipe({'firite_ingot': 15, 'aerialite_ingot': 15, 'anvil': 1}, 'chest')
                        elif self.cc_t == 4:
                            tr = inventory.Recipe({'mysterious_ingot': 10, 'storm_core': 2, 'anvil': 1}, 'chest')
                        elif self.cc_t == 5:
                            tr = inventory.Recipe({'soul': 20, 'evil_ingot': 30, 'mithrill_anvil': 1}, 'chest')
                        elif self.cc_t == 6:
                            tr = inventory.Recipe({'mystery_core': 3, 'soul': 50, 'mithrill_anvil': 1}, 'chest')
                        elif self.cc_t == 7:
                            tr = inventory.Recipe({'chaos_ingot': 30, 'chlororphyte_ingot': 10, 'chlorophyll': 1}, 'chest')
                        elif self.cc_t == 8:
                            tr = inventory.Recipe({'chaos_ingot': 150, 'substance_fountain': 1}, 'chest')
                        else:
                            tr = inventory.Recipe({'the_final_ingot': 1, 'my_soul': 1}, 'chest')
                        inventory.RECIPES[0] = tr
                if len(self.recipes):
                    for i in range(-10, 10):
                        s = (self.sel_recipe + i + len(self.recipes)) % len(self.recipes)
                        cur_recipe = self.recipes[s]
                        styles.item_display(displayer.SCREEN_WIDTH - 10 - 80 + self.inv_pos // 3, displayer.SCREEN_HEIGHT // 2 + i * 90 - 40,
                                            cur_recipe.result, str(s + 1), str(cur_recipe.crafted_amount), 1 if i else 1.2, red=not cur_recipe.is_valid(self.inventory))
                        i += 1
                    cur_recipe = self.recipes[self.sel_recipe]
                    styles.item_mouse(game.get_game().displayer.SCREEN_WIDTH - 260 + self.inv_pos // 3,
                                      game.get_game().displayer.SCREEN_HEIGHT - 170,
                                      cur_recipe.result, str(self.sel_recipe + 1), str(cur_recipe.crafted_amount), 2,
                                      anchor='right')
                    i = 0
                    for item, amount in cur_recipe.material.items():
                        styles.item_mouse(
                            game.get_game().displayer.SCREEN_WIDTH - 20 - 80 * (1 + len(cur_recipe.material)) + 80 * i + self.inv_pos // 3,
                            game.get_game().displayer.SCREEN_HEIGHT - 250, item, '', str(amount), 1, anchor='right')
                        i += 1
                    for i in range(-10, 10):
                        s = (self.sel_recipe + i + len(self.recipes)) % len(self.recipes)
                        cur_recipe = self.recipes[s]
                        styles.item_mouse(displayer.SCREEN_WIDTH - 10 - 80 + self.inv_pos // 3, displayer.SCREEN_HEIGHT // 2 + i * 90 - 40,
                                          cur_recipe.result, str(s + 1), str(cur_recipe.crafted_amount), 1, anchor='right')
                        r = pg.Rect(displayer.SCREEN_WIDTH - 10 - 80 + self.inv_pos // 3, displayer.SCREEN_HEIGHT // 2 + i * 90 - 40, 80, 80)
                        if r.collidepoint(game.get_game().displayer.reflect(
                                *pg.mouse.get_pos())) and 1 in game.get_game().get_mouse_press():
                            self.sel_recipe = s
            if len(self.recipes) and self.ui_recipe_overlook:
                ts = (len(self.recipes) + 255) // 256
                if pg.K_LEFT in game.get_game().get_keys():
                    self.ui_recipe_overlook = (self.ui_recipe_overlook + ts - 2) % ts + 1
                if pg.K_RIGHT in game.get_game().get_keys():
                    self.ui_recipe_overlook = self.ui_recipe_overlook % ts + 1
                self.ui_recipe_overlook = max(1, min(ts, self.ui_recipe_overlook))
                self.recipes = self.recipes[self.ui_recipe_overlook * 256 - 256:self.ui_recipe_overlook * 256]
                w = 16
                l = len(self.recipes) // w + (1 if len(self.recipes) % w else 0)
                for i, r in enumerate(self.recipes):
                    x = i % w * 80 - w * 80 / 2 + displayer.SCREEN_WIDTH // 2
                    y = i // w * 80 - l * 80 / 2 + displayer.SCREEN_HEIGHT // 2
                    styles.item_display(x, y, r.result, str(i + 1), str(r.crafted_amount), 1, red=not r.is_valid(self.inventory))
                for i, r in enumerate(self.recipes):
                    x = i % w * 80 - w * 80 / 2 + displayer.SCREEN_WIDTH // 2
                    y = i // w * 80 - l * 80 / 2 + displayer.SCREEN_HEIGHT // 2
                    styles.item_mouse(x, y, r.result, str(i + 1), str(r.crafted_amount), 1, anchor='right')
                    r = pg.Rect(x, y, 80, 80)
                    if r.collidepoint(game.get_game().displayer.reflect(
                            *pg.mouse.get_pos())) and 1 in game.get_game().get_mouse_press():
                        self.sel_recipe = i + (self.ui_recipe_overlook - 1) * 256
                        self.ui_recipe_overlook = False
            if pg.K_i in game.get_game().get_pressed_keys():
                ammo, amount = self.ammo
                styles.item_display(10, 10, ammo, '', str(amount), 2)
                styles.item_mouse(10, 10, ammo, '', str(amount), 2)
                ammo, amount = self.ammo_bullet
                styles.item_display(10, 170, ammo, '', str(amount), 2)
                styles.item_mouse(10, 170, ammo, '', str(amount), 2)
        else:
            t = (game.get_game().day_time % 1 * 24 * 60)
            for e in game.get_game().world_events:
                self.ntcs.append(f"Event: {e}")
            self.ntcs.append(f"{self.obj.pos[0] / 1000:.1f}, {self.obj.pos[1] / 1000:.1f}")
            self.ntcs.append(f"{int(t // 60)}:{'0' if int(t % 60) < 10 else ''}{int(t % 60)}")
            if self.ui_tasks:
                for i in range(len(self.ntcs)):
                    t = game.get_game().displayer.font.render(styles.text(self.ntcs[-i - 1]), True, (255, 255, 255))
                    tb = game.get_game().displayer.font.render(styles.text(self.ntcs[-i - 1]), True, (0, 0, 0))
                    game.get_game().displayer.canvas.blit(tb, (13, game.get_game().displayer.SCREEN_HEIGHT - 50 - i * 30))
                    game.get_game().displayer.canvas.blit(t, (10, game.get_game().displayer.SCREEN_HEIGHT - 53 - i * 30))
            if self.ui_attributes:
                for i in range(len(self.p_data)):
                    t = game.get_game().displayer.font.render(styles.text(self.p_data[i]), True, (255, 255, 255))
                    tb = game.get_game().displayer.font.render(styles.text(self.p_data[i]), True, (0, 0, 0))
                    game.get_game().displayer.canvas.blit(tb, (game.get_game().displayer.SCREEN_WIDTH - 7 - tb.get_width(),
                                                               game.get_game().displayer.SCREEN_HEIGHT - 50 - i * 30))
                    game.get_game().displayer.canvas.blit(t, (game.get_game().displayer.SCREEN_WIDTH - 10 - t.get_width(),
                                                              game.get_game().displayer.SCREEN_HEIGHT - 53 - i * 30))
        if len(self.top_notice) and self.t_ntc_timer > 0:
            nt = game.get_game().displayer.font.render(styles.text(self.top_notice), True, (255, 255, 0))
            nt = pg.transform.scale(nt, (game.get_game().displayer.SCREEN_WIDTH // 2,
                                         game.get_game().displayer.SCREEN_WIDTH // 2 / nt.get_width() * nt.get_height()))
            game.get_game().displayer.canvas.blit(nt, (game.get_game().displayer.SCREEN_WIDTH // 2 - nt.get_width() // 2,
                                                     150))
        if len([1 for a in self.accessories if a == 'aimer']):
            for menace in [e for e in game.get_game().entities if e.IS_MENACE]:
                if type(menace) is entity.Entities.TheCPU:
                    continue
                px = menace.obj.pos[0] - self.obj.pos[0]
                py = menace.obj.pos[1] - self.obj.pos[1]
                dis = vector.distance(px, py)
                pg.draw.circle(displayer.canvas, (255, 0, 0), position.displayed_position(
                    (px * 300 // dis + self.obj.pos[0], py * 300 // dis + self.obj.pos[1])),
                               max(30, int(300 - dis // 30)) // 15)
        if len([1 for a in self.accessories if a == 'photon_aimer']):
            for menace in [e for e in game.get_game().entities if e.IS_MENACE]:
                if type(menace) is entity.Entities.TheCPU:
                    continue
                px = menace.obj.pos[0] - self.obj.pos[0]
                py = menace.obj.pos[1] - self.obj.pos[1]
                dis = vector.distance(px, py)
                if dis < 1000:
                    pg.draw.circle(displayer.canvas, (0, 255, 0), position.displayed_position(menace.obj.pos),
                                   20)
                else:
                    dr = min(1, max(0, dis / 9000))
                    pg.draw.circle(displayer.canvas, (int((1 - dr) ** 2 * 255), int(dr ** 2 * 255), 0), position.displayed_position(
                        (px * 300 // dis + self.obj.pos[0], py * 300 // dis + self.obj.pos[1])),
                                   max(30, int(300 - dis // 30)) // 15)
        if len([1 for a in self.accessories if a == 'chaos_evileye']):
            esf = game.get_game().graphics['background_chaos_eye']
            if esf.get_width() != 64:
                game.get_game().graphics['background_chaos_eye'] = pg.transform.scale(esf, (64, 64))
                esf = game.get_game().graphics['background_chaos_eye']
            for menace in [e for e in game.get_game().entities if e.IS_MENACE]:
                px = menace.obj.pos[0] - self.obj.pos[0]
                py = menace.obj.pos[1] - self.obj.pos[1]
                dis = vector.distance(px, py)
                if dis < 1500:
                    displayer.canvas.blit(esf, position.displayed_position((menace.obj.pos[0] - 32,
                                                                             menace.obj.pos[1] - 32)))
                else:
                    dr = min(1, max(0, dis / 9000))
                    pg.draw.circle(displayer.canvas, (int((1 - dr) ** 2 * 255), 0, int(dr ** 2 * 255)),
                                   position.displayed_position(
                                       (px * 300 // dis + self.obj.pos[0], py * 300 // dis + self.obj.pos[1])),
                                   max(30, int(300 - dis // 30)) // 15)
        if len([1 for a in self.accessories if a in ['horizon_goggles', 'fate_alignment_amulet']]):
            esf = game.get_game().graphics['background_horizon']
            if esf.get_width() != 64:
                game.get_game().graphics['background_horizon'] = pg.transform.scale(esf, (64, 64))
                esf = game.get_game().graphics['background_horizon']
            for menace in [e for e in game.get_game().entities if e.IS_MENACE]:
                px = menace.obj.pos[0] - self.obj.pos[0]
                py = menace.obj.pos[1] - self.obj.pos[1]
                dis = vector.distance(px, py)
                if dis < 2000:
                    displayer.canvas.blit(esf, position.displayed_position((menace.obj.pos[0] - 32,
                                                                             menace.obj.pos[1] - 32)))
                else:
                    dr = min(1, max(0, dis / 9000))
                    pg.draw.circle(displayer.canvas, (int((1 - dr) ** 2 * 255), 0, int(dr ** 2 * 255)),
                                   position.displayed_position(
                                       (px * 300 // dis + self.obj.pos[0], py * 300 // dis + self.obj.pos[1])),
                                   max(30, int(300 - dis // 30)) // 15)
        if pg.K_h in game.get_game().get_keys():
            potions = [inventory.ITEMS['legendary_hero'],
                       inventory.ITEMS['butterscotch_pie'], inventory.ITEMS['crabapple'],
                       inventory.ITEMS['weak_healing_potion']]
            for p in potions:
                if p.id in self.inventory.items:
                    if not len([1 for eff in self.hp_sys.effects if eff.NAME == 'Potion Sickness']):
                        self.inventory.remove_item(p)
                        self.hp_sys.heal({'legendary_hero': 500, 'weak_healing_potion': 50,
                                          'crabapple': 120, 'butterscotch_pie': 240}[p.id])
                        if p.id == 'legendary_hero':
                            if not len([1 for s, i in self.hp_sys.shields if s == 'l.hero']):
                                self.hp_sys.shields.append(('l.hero', 800))
                            else:
                                ii = [i for s, i in self.hp_sys.shields if s == 'l.hero'][0]
                                self.hp_sys.shields = [(s, i) for s, i in self.hp_sys.shields if s != 'l.hero']
                                self.hp_sys.shields.append(('l.hero', min(ii // 100 * 100 + 200, 1000)))
                        self.hp_sys.effect(effects.PotionSickness(20, 1))
                        game.get_game().play_sound('heal')
                        break
        if pg.K_m in game.get_game().get_keys():
            potions = [ inventory.ITEMS['snowman_piece'], inventory.ITEMS['tension_bit'],
                        inventory.ITEMS['seatea'],  inventory.ITEMS['weak_magic_potion']]
            for p in potions:
                if p.id in self.inventory.items:
                    if not len([1 for eff in self.hp_sys.effects if eff.NAME == 'Mana Sickness']):
                        self.inventory.remove_item(p)
                        self.mana = min(self.mana + {'weak_magic_potion': 80, 'seatea': 150,
                                                     'tension_bit': 400, 'snowman_piece': 10000}[p.id], self.max_mana)
                        self.hp_sys.effect(effects.ManaSickness(3, 1))
                        game.get_game().play_sound('mana')
                        break
        if self.touched_item != '':
            styles.item_display(displayer.SCREEN_WIDTH - 330, 10, self.touched_item, '', '', 4)
        if pg.K_1 in game.get_game().get_keys():
            self.sel_weapon = 0
        if pg.K_2 in game.get_game().get_keys():
            self.sel_weapon = 1
        if pg.K_3 in game.get_game().get_keys():
            self.sel_weapon = 2
        if pg.K_4 in game.get_game().get_keys():
            self.sel_weapon = 3
        if self.in_ui:
            pg.mouse.set_visible(not mouse_text)
        else:
            pg.mouse.set_visible(self.weapons[self.sel_weapon].name in ['null', 'arrow_thrower'])
