import math
import random
import tracemalloc

import pygame as pg

from src.physics import mover, vector
from src.resources import time, position, cursors, errors
from src.underia import game, styles, inventory, weapons, entity, projectiles, player_profile
from src.values import hp_system, damages, effects
from src import constants


class PlayerObject(mover.Mover):
    MASS = 20
    FRICTION = 0.8
    SPEED = 20

    def on_update(self):
        keys = game.get_game().get_pressed_keys()
        if pg.K_w in keys:
            self.apply_force(vector.Vector(0, self.SPEED))
        elif pg.K_s in keys:
            self.apply_force(vector.Vector(180, self.SPEED))
        if pg.K_a in keys:
            self.apply_force(vector.Vector(270, self.SPEED))
        elif pg.K_d in keys:
            self.apply_force(vector.Vector(90, self.SPEED))


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
    ]

    def __init__(self):
        self.obj = PlayerObject((400, 300))
        self.hp_sys = hp_system.HPSystem(200)
        self.ax, self.ay = 0, 0
        self.weapons = 4 * [weapons.WEAPONS['null']]
        self.sel_weapon = 0
        self.inventory = inventory.Inventory()
        self.accessories = 6 * ['null']
        self.sel_accessory = 0
        self.open_inventory = False
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
        if 'patience_amulet' in self.accessories and self.hp_sys.hp <= self.hp_sys.max_hp * 0.5:
            dmg *= 3
        return dmg

    def calculate_speed(self):
        spd = 1.0
        spd *= 1.0 + int(self.profile.point_agility ** 1.1) / 400
        if 'patience_amulet' in self.accessories and self.hp_sys.hp > self.hp_sys.max_hp * 0.5:
            spd *= 1.8
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

    def calculate_air_resistance(self):
        air_res = 1.0
        return air_res

    def calculate_data(self, data_idx, rate_data, rate_plus = False, rate_multiply = False):
        if rate_plus == rate_multiply and rate_data:
            raise ValueError('Rate only chooses a strategy.')
        if rate_data:
            val = 1.0
        else:
            val = 0.0
        for i in range(len(self.accessories)):
            if data_idx in inventory.ITEMS[self.accessories[i]].accessory_data.keys():
                if rate_plus:
                    val += inventory.ITEMS[self.accessories[i]].accessory_data[data_idx] / 100
                elif rate_multiply:
                    val *= (inventory.ITEMS[self.accessories[i]].accessory_data[data_idx] + 100) / 100
                else:
                    val += inventory.ITEMS[self.accessories[i]].accessory_data[data_idx]
        for e in self.hp_sys.effects:
            if data_idx in e.datas.keys():
                if rate_plus:
                    val += e.datas[data_idx] / 100
                elif rate_multiply:
                    val *= (e.datas[data_idx] + 100) / 100
                else:
                    val += e.datas[data_idx]
        return val

    def get_max_screen_scale(self):
        ACCESSORY_SIZE = {'aimer': 1.5, 'winds_necklace': 1.1, 'cowboy_hat': 1.4, 'photon_aimer': 4.5, 'cloudy_glasses': 1.2}
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
        self.ntcs = []
        self.p_data = []
        self.top_notice = ''
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
        self.talent = min(self.talent + 0.005 + math.sqrt(self.max_talent) / 2000 + (self.max_talent - self.talent) / 1000, self.max_talent)
        self.hp_sys.pos = self.obj.pos
        self.attack = self.calculate_damage() * self.calculate_data('damage', rate_data=True, rate_multiply=True)
        self.strike = 0.08 + self.calculate_data('crit', False) / 100
        self.attacks = [self.calculate_melee_damage() * self.calculate_data('melee_damage', rate_data=True, rate_plus=True),
                        self.calculate_ranged_damage() * self.calculate_data('ranged_damage', rate_data=True, rate_plus=True),
                        self.calculate_magic_damage() * self.calculate_data('magic_damage', rate_data=True, rate_plus=True),
                        self.calculate_data('octave_damage', rate_data=True, rate_multiply=True),
                        self.calculate_data('hallow_damage', rate_data=True, rate_multiply=True),
                        self.calculate_data('pacify_damage', rate_data=True, rate_multiply=True)]
        self.attack *= 1 + (random.random() < self.strike)
        self.p_data.append(f'Memory use: {tracemalloc.get_traced_memory()[1] / 1024 / 1024:.2f}MB {1000 / game.get_game().clock.last_tick:.2f}fps')
        self.p_data.append(f'Magic Damage: {int(self.attacks[2] * self.attack * 100) / 100}x')
        self.p_data.append(f'Ranged Damage: {int(self.attacks[1] * self.attack * 100) / 100}x')
        self.p_data.append(f'Melee Damage: {int(self.attacks[0] * self.attack * 100) / 100}x')
        self.obj.SPEED = self.calculate_data('speed', rate_data=True, rate_multiply=True) * 80 * self.calculate_speed()
        self.obj.FRICTION = max(0, 1 - 0.2 * self.calculate_data('air_res', rate_data=True, rate_multiply=True))
        self.obj.MASS = max(40, 80 + self.calculate_data('mass', False))
        self.p_data.append(f'Agility {int(self.obj.SPEED / 2) / 10}N')
        self.splint_distance = self.calculate_data('splint', False)
        if self.splint_distance:
            self.p_data.append(f'Splint distance {self.splint_distance}')
        self.splint_cd = self.calculate_data('splint_cd', True, rate_multiply=True) * 80
        if self.splint_distance:
            self.p_data.append(f'Splint cd {self.splint_cd}s')
            if self.splint_t > 0:
                self.splint_t -= 1
            elif self.splint_t == 0:
                for d in [pg.K_w, pg.K_a, pg.K_s, pg.K_d]:
                    if d in game.get_game().get_keys():
                        self.splint_t = -1
            elif self.splint_t > -10:
                self.splint_t -= 1
                for i, d in enumerate([pg.K_w, pg.K_a, pg.K_s, pg.K_d]):
                    if d in game.get_game().get_keys():
                        self.splint_t = self.splint_cd
                        rt = [0, 90, 180, 270]
                        self.obj.apply_force(vector.Vector(rt[i], self.splint_distance * 120))
            else:
                self.splint_t = 0
        self.p_data.append(f'Speed {int(self.obj.velocity.get_net_value() / 2) / 10}ms^-1 '
                           f'{int(self.obj.velocity.get_net_rotation())}deg')
        self.p_data.append(f'Friction {-int(100 - self.obj.FRICTION * 100)}%')
        self.p_data.append(f'Mass {int(self.obj.MASS)}kg')
        for w in weapons.WEAPONS.values():
            try:
                if w.domain_open:
                    self.ntcs.append(f'{w.name} is open.')
                    self.obj.FRICTION = 0
            except AttributeError:
                pass
        self.domain_size = self.calculate_data('domain_size', True, rate_multiply=True)
        mtp_regen = self.calculate_data('mentality_regen', False)
        self.REGENERATION = 0.015 + self.calculate_regeneration() + self.calculate_data('regen', rate_data=False) / 40.0
        self.MAGIC_REGEN = self.calculate_magic_regeneration() * (0.04 + self.calculate_data('mana_regen', rate_data=False) / 120.0)
        ins_regen = (.8 + self.calculate_data('ins_regen', rate_data=False) / 40.0) * self.calculate_magic_regeneration()
        max_ins = self.calculate_data('max_ins', False)
        max_mana = self.calculate_data('max_mana', False)
        karma_reduce = 5 * self.calculate_data('karma_reduce', True, rate_multiply=True)
        if self.domain_size > 1:
            self.p_data.append(f'Domain Size x{int(self.domain_size * 100)}%')
        if self.hp_sys.max_hp > 1000:
            self.p_data.append(f'Mentality: {int(mtp_regen)}/s')
            self.talent = min(self.talent + mtp_regen / 40, self.max_talent)
        self.p_data.append(f'Regeneration: {int(self.REGENERATION * 400) / 10}/s')
        self.p_data.append(f'Mana Regeneration: {int(self.MAGIC_REGEN * 400) / 10}/s')
        if ins_regen:
            self.p_data.append(f'Inspiration Regeneration: {int(ins_regen * 400) / 10}/s')
        if max_ins:
            self.p_data.append(f'Additional Maximum Inspiration: {int(max_ins)}')
        if self.good_karma != 0 or karma_reduce != 5:
            self.p_data.append(f'Karma Reduction: -{int(karma_reduce * 40)}/s')
            self.p_data.append(f'Good Karma: {int(self.good_karma)}')
        self.good_karma = max(0, self.good_karma - karma_reduce)
        self.inspiration = min(self.inspiration + ins_regen, self.max_inspiration + max_ins)
        self.hp_sys.defenses[damages.DamageTypes.TOUCHING] = self.calculate_data('touch_def', False)
        self.hp_sys.defenses[damages.DamageTypes.PHYSICAL] = self.calculate_data('phys_def', False)
        self.hp_sys.defenses[damages.DamageTypes.MAGICAL] = self.calculate_data('mag_def', False)
        self.p_data.append(f'Magical Defense: {int(self.hp_sys.defenses[damages.DamageTypes.MAGICAL])}')
        self.p_data.append(f'Touch Defense: {int(self.hp_sys.defenses[damages.DamageTypes.TOUCHING])}')
        if len([1 for eff in self.hp_sys.effects if eff.NAME == 'Gravity']):
            self.obj.apply_force(vector.Vector(180, 200))
        if pg.K_e in game.get_game().get_keys():
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
        self.hp_sys.heal(self.REGENERATION)
        self.mana = min(self.mana + self.MAGIC_REGEN, self.max_mana + max_mana)
        displayer = game.get_game().displayer
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
        self.hp_sys.update()
        w = self.weapons[self.sel_weapon]
        if pg.K_EQUALS in game.get_game().get_pressed_keys():
            self.scale = min(self.scale + 0.05, self.get_max_screen_scale())
        if pg.K_MINUS in game.get_game().get_pressed_keys():
            self.scale = max(self.scale - 0.05, 0.8)
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
        if self.hp_sys.hp <= 1 + self.REGENERATION:
            self.hp_sys.hp = self.hp_sys.max_hp
            self.mana = self.max_mana
            self.talent = self.max_talent
            self.obj.velocity.clear()
            self.hp_sys.effects = []
            game.get_game().entities = []
            game.get_game().projectiles = []
            game.get_game().damage_texts = []
            self.obj.pos = (0, 0)

    def ui(self):
        self.in_ui = False
        self.touched_item = ''
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

            hp_img = pg.transform.scale(hp_img, (40, 40))
            sh_img = pg.transform.scale(sh_img, (40, 40))
            mana_img = pg.transform.scale(mana_img, (40, 40))
            tal_img = pg.transform.scale(tal_img, (40, 40))
            out_img = pg.transform.scale(out_img, (40, 40))
            ins_img = pg.transform.scale(ins_img, (40, 40))
            ins_out_img = pg.transform.scale(ins_out_img, (40, 40))

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
        else:
            hp_l = min(300.0, self.hp_sys.max_hp // 2)
            mp_l = min(300.0 - mt * 200.0, self.max_mana)
            tp_l = min(200.0 + mt * 300.0, 8 * self.max_talent)
            is_l = min(500.0, self.inspiration // 2)
            hp_p = self.hp_sys.hp / self.hp_sys.max_hp
            mp_p = self.mana / self.max_mana
            tp_p = self.talent / self.max_talent if self.max_talent else 0
            sd_p = min(1, sum([v for n, v in game.get_game().player.hp_sys.shields]) / game.get_game().player.hp_sys.max_hp)
            is_p = self.inspiration / self.max_inspiration
            pg.draw.rect(displayer.canvas, (80, 0, 0), (10, 10, hp_l, 25))
            pg.draw.rect(displayer.canvas, (0, 0, 80), (10 + hp_l, 10, mp_l, 25))
            pg.draw.rect(displayer.canvas, (0, 80, 0), (10 + hp_l + mp_l, 10, tp_l, 25))
            pg.draw.rect(displayer.canvas, (255, 0, 0), (10, 10, hp_l * hp_p, 25))
            pg.draw.rect(displayer.canvas, (255, 255, 0), (10, 10, hp_l * sd_p, 25))
            pg.draw.rect(displayer.canvas, (0, 0, 255), (10 + hp_l + mp_l - mp_l * mp_p, 10, mp_l * mp_p, 25))
            pg.draw.rect(displayer.canvas, (0, 255, 0) if not mt else (200, 255, 127), (10 + hp_l + mp_l, 10, tp_l * tp_p, 25))
            pg.draw.rect(displayer.canvas, (255, 255, 255), (10, 10, hp_l + mp_l + tp_l, 25), width=2)
            pg.draw.rect(displayer.canvas, (80, 0, 80), (game.get_game().displayer.SCREEN_WIDTH - 35, 10, 25, is_l))
            pg.draw.rect(displayer.canvas, (255, 0, 255), (game.get_game().displayer.SCREEN_WIDTH - 35, 10, 25, is_l * is_p))
            pg.draw.rect(displayer.canvas, (255, 255, 255), (game.get_game().displayer.SCREEN_WIDTH - 35, 10, 25, is_l), width=2)

            rc = pg.Rect(10, 10, hp_l + mp_l + tp_l, 25)
            ic = pg.Rect(game.get_game().displayer.SCREEN_WIDTH - 35, 10, 25, is_l)
        for i in range(len(self.hp_sys.effects)):
            img = pg.transform.scale(game.get_game().graphics['effect_' + self.hp_sys.effects[i].IMG], (72, 72))
            imr = img.get_rect(
                topright=(game.get_game().displayer.SCREEN_WIDTH - 10 - 80 * len(self.hp_sys.effects) + 80 * i, 10))
            displayer.canvas.blit(img, imr)
        for i in range(len(self.hp_sys.effects)):
            img = pg.transform.scale(game.get_game().graphics['effect_' + self.hp_sys.effects[i].IMG], (72, 72))
            imr = img.get_rect(
                topright=(game.get_game().displayer.SCREEN_WIDTH - 10 - 80 * len(self.hp_sys.effects) + 80 * i, 10))
            if imr.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
                f = displayer.font.render(f"{self.hp_sys.effects[i].NAME} ({self.hp_sys.effects[i].timer}s)", True,
                                          (255, 255, 255))
                fr = f.get_rect(topright=game.get_game().displayer.reflect(*pg.mouse.get_pos()))
                displayer.canvas.blit(f, fr)
        for _entity in game.get_game().entities:
            _entity.obj.touched_player = False
            _entity.obj.object_collision(self.obj, (_entity.img.get_width() + _entity.img.get_height()) // 4 + 50)
            if self.obj.object_collision(_entity.obj, (_entity.img.get_width() + _entity.img.get_height()) // 4 + 50):
                _entity.obj.touched_player = True
                _entity.on_damage_player()
                if _entity.obj.TOUCHING_DAMAGE and not self.hp_sys.is_immune:
                    self.hp_sys.damage(_entity.obj.TOUCHING_DAMAGE, damages.DamageTypes.TOUCHING)
                    self.hp_sys.enable_immume()
            self.obj.object_gravitational(_entity.obj)
            _entity.obj.object_gravitational(self.obj)
        if rc.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
            f = displayer.font.render(
                f"HP: {int(self.hp_sys.hp) + int(sum([v for n, v in game.get_game().player.hp_sys.shields]))}/{self.hp_sys.max_hp} MP: {int(self.mana)}/{self.max_mana}"
                f" {'TP' if not mt else 'MTP'}: {int(self.talent)}/{int(self.max_talent)}",
                True, (255, 255, 255))
            displayer.canvas.blit(f, game.get_game().displayer.reflect(*pg.mouse.get_pos()))
        if ic.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
            f = displayer.font.render(f"IP: {int(self.inspiration)}/{int(self.max_inspiration)}", True,
                                      (255, 255, 255))
            displayer.canvas.blit(f, game.get_game().displayer.reflect(*pg.mouse.get_pos()))
        for i in range(len(self.weapons)):
            styles.item_display(10 + i * 60, 80,
                                self.weapons[i].name.replace(' ', '_'), str(i + 1),
                                '1', 0.75, selected=i == self.sel_weapon)
            if self.weapons[i].sk_mcd:
                pg.draw.rect(displayer.canvas, (255, 0, 0), (10 + i * 60, 140, 60, 10))
                pg.draw.rect(displayer.canvas, (255, 255, 0), (10 + i * 60, 140,
                                                               60 * self.weapons[i].sk_cd // self.weapons[i].sk_mcd, 10))
                f = displayer.font.render(f"{int(100 * (1 - self.weapons[i].sk_cd / self.weapons[i].sk_mcd))}%", True,
                                          (255, 255, 255), (0, 0, 0))
                f = pg.transform.scale(f, (f.get_width() * 30 // f.get_height(), 30))
                fr = f.get_rect(center=(10 + i * 60 + 30, 140 + 25))
                displayer.canvas.blit(f, fr)
                if self.weapons[i].sk_cd:
                    self.weapons[i].sk_cd -= 1
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
        if self.open_inventory:
            for i in range(len(self.accessories)):
                styles.item_display(10 + i * 90, game.get_game().displayer.SCREEN_HEIGHT - 90,
                                    self.accessories[i].replace(' ', '_'), str(i), '1', 1,
                                    selected=i == self.sel_accessory)
            l = 12
            lr = 4
            for i in range(lr):
                for j in range(l):
                    if i + j * lr < len(self.inventory.items):
                        item, amount = list(self.inventory.items.items())[i + j * lr]
                    else:
                        item, amount = 'null', ''
                    item = inventory.ITEMS[item]
                    styles.item_display(10 + i * 85, game.get_game().displayer.SCREEN_HEIGHT - 180 - j * 85,
                                        item.id, '', str(amount), 1)
            for i in range(lr):
                for j in range(l):
                    if i + j * lr < len(self.inventory.items):
                        item, amount = list(self.inventory.items.items())[i + j * lr]
                    else:
                        item, amount = 'null', ''
                    item = inventory.ITEMS[item]
                    styles.item_mouse(10 + i * 85, game.get_game().displayer.SCREEN_HEIGHT - 180 - j * 85, item.id,
                                      '', str(amount), 1)
                    rect = pg.Rect(10 + i * 85, game.get_game().displayer.SCREEN_HEIGHT - 180 - j * 85, 80, 80)
                    if rect.collidepoint(game.get_game().displayer.reflect(*pg.mouse.get_pos())):
                        if pg.K_q in game.get_game().get_keys():
                            if item.id != 'null':
                                del self.inventory.items[item.id]
                    if rect.collidepoint(game.get_game().displayer.reflect(
                            *pg.mouse.get_pos())) and 1 in game.get_game().get_mouse_press():
                        if inventory.TAGS['accessory'] in item.tags:
                            if self.tutorial_step == 4:
                                self.tutorial_process += 15
                            self.inventory.remove_item(item)
                            if self.accessories[self.sel_accessory] != 'null':
                                self.inventory.add_item(inventory.ITEMS[self.accessories[self.sel_accessory]])
                            self.accessories[self.sel_accessory] = item.id
                        elif inventory.TAGS['weapon'] in item.tags:
                            if self.tutorial_step == 4:
                                self.tutorial_process += 15
                            self.inventory.remove_item(item)
                            if self.weapons[self.sel_weapon].name != 'null':
                                self.inventory.add_item(
                                    inventory.ITEMS[self.weapons[self.sel_weapon].name.replace(' ', '_')])
                            self.weapons[self.sel_weapon] = weapons.WEAPONS[item.id]
                        elif item.id == 'mana_crystal':
                            if self.max_mana < 120:
                                self.max_mana += 15
                                self.inventory.remove_item(item)
                        elif item.id == 'white_guard':
                            self.hp_sys.shields.append(('W.Guard', 20))
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
                        elif item.id == 'life_fruit':
                            if self.hp_sys.max_hp >= 600 and self.max_mana >= 300 and self.max_talent >= 10:
                                self.hp_sys.max_hp = 1000
                                self.max_mana = 800
                                self.max_talent = 50
                                self.inventory.remove_item(item)
                                self.profile.add_point(2)
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
                                entity.spawn_sandstorm()
                                self.inventory.remove_item(item)
                        elif item.id == 'blood_substance':
                            if not len([1 for e in game.get_game().player.hp_sys.effects if
                                        type(e) is effects.StoneAltar]):
                                game.get_game().dialog.dialog('Unable to summon Abyss Eye.',
                                                              'There is no Stone Altar nearby.')
                            else:
                                entity.entity_spawn(entity.Entities.AbyssEye, 1600, 1600, 0, 1145, 100000)
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
                            if not len([1 for e in game.get_game().player.hp_sys.effects if
                                        type(e) is effects.MetalAltar]):
                                game.get_game().dialog.dialog('Unable to summon Jevil.',
                                                              'There is no Metal Altar nearby.')
                            else:
                                entity.entity_spawn(entity.Entities.Jevil, 2000, 2000, 0, 1145, 100000)
                                self.inventory.remove_item(item)
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
                                game.get_game().dialog.dialog('Unable to summon Faithless and Truthless Eyes.',
                                                               'There is no Scarlett Altar nearby.')
                            else:
                                entity.entity_spawn(entity.Entities.MechanicalMedusa, 2000, 2000, 0, 1145, 100000)
                                self.inventory.remove_item(item)

                        elif item.id == 'my_soul':
                            self.profile.add_point(4)
                            if sum([v for _, v in self.hp_sys.shields]) + self.hp_sys.hp > self.hp_sys.max_hp:
                                entity.entity_spawn(entity.Entities.ReincarnationTheWorldsTree, 2000, 2000, 0, 1145, 100000)
                            else:
                                entity.entity_spawn(entity.Entities.Faith, 2000, 2000, 0, 1145, 100000)
                        elif item.id == 'finale__soul':
                            game.get_game().dialog.dialog('Looks like you\'ve completed this timelines.',
                                                          'A reminder is that,\nyour journey is not yet completed.',
                                                          'Reset this timeline to start another chapter.',
                                                          'If you can\'t afford to reset, [QUIT] now.\n'
                                                          'Then copy your archive.',
                                                          '...', 'Anyway, thank you for playing Underia!\nA game by KLPIG.',
                                                          'Chapter 1: [The Soul] - [Ended]\nChapter 2')
                            while game.get_game().dialog.curr_text != '' and len(game.get_game().dialog.word_queue):
                                keys = []
                                for event in pg.event.get():
                                    if event.type == pg.QUIT:
                                        raise errors.Interrupt()
                                    elif event.type == pg.KEYDOWN:
                                        if event.key == pg.K_ESCAPE:
                                            raise errors.Interrupt()
                                        elif event.key == pg.K_F4:
                                            constants.FULLSCREEN = not constants.FULLSCREEN
                                            pg.display.set_mode(pg.display.get_window_size(), (pg.FULLSCREEN if constants.FULLSCREEN else 0) | constants.FLAGS)
                                        else:
                                            keys.append(event.key)
                                game.get_game().dialog.update(keys)
                                game.get_game().displayer.update()
                                pg.display.update()
                                game.get_game().clock.update()
                            self.profile.add_point(5)

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
                            if not self.inventory.is_enough(inventory.ITEMS['tip0']):
                                self.inventory.add_item(inventory.ITEMS['tip0'])
                            if not self.inventory.is_enough(inventory.ITEMS['tip1']):
                                self.inventory.add_item(inventory.ITEMS['tip1'])
                            lft = pg.font.SysFont('dtm-mono', 96)
                            lss = pg.font.SysFont('dtm-mono', 56)
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
                                pg.draw.rect(window, (255, 255, 255), (wx - 1200, wy - 750, 2400, 1600))
                                pg.draw.rect(window, (0, 0, 0), (wx - 1200, wy - 750, 2400, 1600), 18)
                                f = lss.render(f"{sel + 1}/{len(rep)}", True, (0, 0, 0))
                                fr = f.get_rect(midbottom=(wx, wy + 800))
                                window.blit(f, fr)
                                cr = rep[sel]
                                styles.item_display(wx - 1120, wy - 460, cr.result, '',
                                                    str(cr.crafted_amount), 4, _window=window)
                                j = 0
                                ml = 6
                                for it, qt in cr.material.items():
                                    styles.item_display(wx + 80 + 170 * (j % ml), wy - 460 + 170 * (j // ml), it, '', str(qt),
                                                        2, _window=window, red=not self.inventory.is_enough(inventory.ITEMS[it], qt))
                                    j += 1
                                tt = lft.render(inventory.ITEMS[cr.result].name if len(inventory.ITEMS[cr.result].name) < 20 \
                                                    else inventory.ITEMS[cr.result].name[:16] + '...',True, (0, 0, 0))
                                window.blit(tt, (wx - 1120, wy - 660))
                                tr = lft.render(f"Materials: ", True, (0, 0, 0))
                                window.blit(tr, (wx + 80, wy - 660))
                                desc = inventory.ITEMS[cr.result].get_full_desc().split('\n')
                                for ii in range(len(desc)):
                                    if len(desc[ii]) > 30:
                                        s = desc[ii]
                                        desc.remove(s)
                                        desc.insert(ii, s[30:])
                                        desc.insert(ii, s[:30] + '-')
                                        ii -= 1
                                for j, d in enumerate(desc):
                                    td = lss.render(d, True, (0, 0, 0))
                                    window.blit(td, (wx - 1120, wy - 100 + 60 * j))
                                j = 0
                                for it, qt in cr.material.items():
                                    r = pg.Rect(wx + 80 + 170 * (j % ml), wy - 460 + 170 * (j // ml), 160, 160)
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
                                            td = lss.render(d, True, (0, 0, 0))
                                            window.blit(td, (wx + 80, wy - 100 + 60 * j + \
                                                             max(0, len(cr.material) // ml - 1) * 170))
                                        break
                                    j += 1
                                pg.display.update((wx - 1200, wy - 800, 2400, 1600))
                            game.get_game().pressed_keys = []
                            game.get_game().pressed_mouse = []
                        self.in_ui = True
            for i in range(len(self.accessories)):
                styles.item_mouse(10 + i * 90, game.get_game().displayer.SCREEN_HEIGHT - 90,
                                  self.accessories[i].replace(' ', '_'), str(i), '1', 1)
                rect = pg.Rect(10 + i * 90, game.get_game().displayer.SCREEN_HEIGHT - 90, 90, 90)
                if rect.collidepoint(game.get_game().displayer.reflect(
                        *pg.mouse.get_pos())) and 1 in game.get_game().get_mouse_press():
                    self.sel_accessory = i

            self.recipes = [r for r in inventory.RECIPES if r.is_valid(self.inventory)]
            if len(self.recipes):
                self.sel_recipe %= len(self.recipes)
                if pg.K_UP in game.get_game().get_keys():
                    self.sel_recipe = (self.sel_recipe - 1) % len(self.recipes)
                if pg.K_DOWN in game.get_game().get_keys():
                    self.sel_recipe = (self.sel_recipe + 1) % len(self.recipes)
                cur_recipe = self.recipes[self.sel_recipe]
                styles.item_display(game.get_game().displayer.SCREEN_WIDTH - 260,
                                    game.get_game().displayer.SCREEN_HEIGHT - 170,
                                    cur_recipe.result, str(self.sel_recipe + 1), str(cur_recipe.crafted_amount), 2)
                i = 0
                for item, amount in cur_recipe.material.items():
                    styles.item_display(
                        game.get_game().displayer.SCREEN_WIDTH - 20 - 80 * (1 + len(cur_recipe.material)) + 80 * i,
                        game.get_game().displayer.SCREEN_HEIGHT - 250, item, '', str(amount), 1)
                    i += 1
                if pg.Rect(game.get_game().displayer.SCREEN_WIDTH - 260, game.get_game().displayer.SCREEN_HEIGHT - 170,
                           160, 160).collidepoint(game.get_game().displayer.reflect(
                        *pg.mouse.get_pos())) and 1 in game.get_game().get_mouse_press():
                    rc = cur_recipe
                    cur_recipe.make(self.inventory)
                    self.recipes = [r for r in inventory.RECIPES if r.is_valid(self.inventory)]
                    res = [i for i, r in enumerate(self.recipes) if r is rc]
                    self.sel_recipe = res[0] if res else 0
                    if self.tutorial_step == 3:
                        self.tutorial_process += 20
                if len(self.recipes):
                    for i in range(-10, 10):
                        s = (self.sel_recipe + i + len(self.recipes)) % len(self.recipes)
                        cur_recipe = self.recipes[s]
                        styles.item_display(displayer.SCREEN_WIDTH - 90, displayer.SCREEN_HEIGHT // 2 + i * 80 - 40,
                                            cur_recipe.result, str(s + 1), str(cur_recipe.crafted_amount), 1)
                        i += 1
                cur_recipe = self.recipes[self.sel_recipe]
                styles.item_mouse(game.get_game().displayer.SCREEN_WIDTH - 260,
                                  game.get_game().displayer.SCREEN_HEIGHT - 170,
                                  cur_recipe.result, str(self.sel_recipe + 1), str(cur_recipe.crafted_amount), 2,
                                  anchor='right')
                i = 0
                for item, amount in cur_recipe.material.items():
                    styles.item_mouse(
                        game.get_game().displayer.SCREEN_WIDTH - 20 - 80 * (1 + len(cur_recipe.material)) + 80 * i,
                        game.get_game().displayer.SCREEN_HEIGHT - 250, item, '', str(amount), 1, anchor='right')
                    i += 1
                for i in range(-10, 10):
                    s = (self.sel_recipe + i + len(self.recipes)) % len(self.recipes)
                    cur_recipe = self.recipes[s]
                    styles.item_mouse(displayer.SCREEN_WIDTH - 90, displayer.SCREEN_HEIGHT // 2 + i * 80 - 40,
                                      cur_recipe.result, str(s + 1), str(cur_recipe.crafted_amount), 1, anchor='right')
                    r = pg.Rect(displayer.SCREEN_WIDTH - 90, displayer.SCREEN_HEIGHT // 2 + i * 80 - 40, 80, 80)
                    if r.collidepoint(game.get_game().displayer.reflect(
                            *pg.mouse.get_pos())) and 1 in game.get_game().get_mouse_press():
                        self.sel_recipe = s
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
            for i in range(len(self.ntcs)):
                t = game.get_game().displayer.font.render(self.ntcs[-i - 1], True, (255, 255, 255), (0, 0, 0))
                game.get_game().displayer.canvas.blit(t, (10, game.get_game().displayer.SCREEN_HEIGHT - 50 - i * 30))
            for i in range(len(self.p_data)):
                t = game.get_game().displayer.font.render(self.p_data[i], True, (255, 255, 255), (0, 0, 0))
                game.get_game().displayer.canvas.blit(t, (game.get_game().displayer.SCREEN_WIDTH - 10 - t.get_width(),
                                                          game.get_game().displayer.SCREEN_HEIGHT - 50 - i * 30))
        if len(self.top_notice) and self.t_ntc_timer > 0:
            nt = game.get_game().displayer.font.render(self.top_notice, True, (255, 255, 0))
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
            pg.mouse.set_cursor(cursors.arrow_cursor_cursor)
        else:
            self.weapons[self.sel_weapon].update()
            w = self.weapons[self.sel_weapon]
            if inventory.TAGS['magic_weapon'] in inventory.ITEMS[w.name.replace(' ', '_')].tags or \
                    inventory.TAGS['bow'] in inventory.ITEMS[w.name.replace(' ', '_')].tags or \
                    inventory.TAGS['gun'] in inventory.ITEMS[w.name.replace(' ', '_')].tags:
                pg.mouse.set_cursor(cursors.target_cursor_cursor)
            else:
                pg.mouse.set_cursor(cursors.sword_cursor_cursor)
