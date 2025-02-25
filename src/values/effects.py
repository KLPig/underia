from resources import time
from values import hp_system, elements, damages
import constants


class Effect:
    CORRESPONDED_ELEMENT = elements.ElementTypes.NONE
    IMG = 'empty'
    NAME = 'Effect'
    DESC = ''

    def __init__(self, duration, level):
        self.timer = duration
        self.level = level
        self.duration = duration
        self.tick = 0
        self.datas = {}
        for desc in self.DESC.split('\n'):
            desc = desc.replace(' ', '').lower().replace('.', '')
            try:
                if desc.endswith('touchingdefense'):
                    self.datas['touch_def'] = int(desc.removesuffix('touchingdefense'))
                elif desc.endswith('physicaldefense'):
                    self.datas['phys_def'] = int(desc.removesuffix('physicaldefense'))
                elif desc.endswith('magicdefense'):
                    self.datas['mag_def'] = int(desc.removesuffix('magicdefense'))
                elif desc.endswith('%speed'):
                    self.datas['speed'] = int(desc.removesuffix('%speed'))
                elif desc.endswith('%critical'):
                    self.datas['crit'] = int(desc.removesuffix('%critical'))
                elif desc.endswith('/secregeneration'):
                    self.datas['regen'] = float(desc.removesuffix('/secregeneration'))
                elif desc.endswith('/secmanaregeneration'):
                    self.datas['mana_regen'] = float(desc.removesuffix('/secmanaregeneration'))
                elif desc.endswith('/secinspirationregeneration'):
                    self.datas['ins_regen'] = float(desc.removesuffix('/secinspirationregeneration'))
                elif desc.endswith('%damage'):
                    self.datas['damage'] = int(desc.removesuffix('%damage'))
                elif desc.endswith('%meleedamage'):
                    self.datas['melee_damage'] = int(desc.removesuffix('%meleedamage'))
                elif desc.endswith('%rangeddamage'):
                    self.datas['ranged_damage'] = int(desc.removesuffix('%rangeddamage'))
                elif desc.endswith('%magicdamage') or desc.endswith('%magicaldamage'):
                    self.datas['magic_damage'] = int(desc.split('%magic')[0])
                elif desc.endswith('%airresistance'):
                    self.datas['air_res'] = int(desc.removesuffix('%airresistance'))
                elif desc.endswith('%domainsize'):
                    self.datas['domain_size'] = int(desc.removesuffix('%domainsize'))
                elif desc.endswith('/secmentalityregeneration'):
                    self.datas['mentality_regen'] = float(desc.removesuffix('/secmentalityregeneration'))
                elif desc.endswith('%poisondamagereceived'):
                    self.datas['poison_res'] = float(desc.removesuffix('%poisondamagereceived'))
                elif desc.endswith('additionalmaximummana'):
                    self.datas['max_mana'] = int(desc.removesuffix('additionalmaximummana'))
                elif desc.endswith('additionalmaximuminspiration'):
                    self.datas['max_ins'] = int(desc.removesuffix('additionalmaximuminspiration'))
                elif desc[0] in ['+', '-']:
                    print(f"Unknown accessory data: {desc}")
            except ValueError:
                print(f"Invalid accessory data: {desc}")

    def on_update(self, entity: hp_system.HPSystem):
        self.tick += 1
        if self.duration < 10 ** 8:
            self.timer -= 1 / constants.FPS

    def on_end(self, entity: hp_system.HPSystem):
        pass

    def on_start(self, entity: hp_system.HPSystem):
        pass


class Aberration(Effect):
    IMG = 'aberration'

    def on_update(self, entity: hp_system.HPSystem):
        super().on_update(entity)
        if time.time_interval(time.get_time(self.tick), 1, 0):
            entity.damage(self.level + 2,
                          getattr(damages.DamageTypes, 'ELEMENT_' + elements.NAMES[self.CORRESPONDED_ELEMENT].upper()))


class Burning(Aberration):
    IMG = 'burning'
    NAME = 'Burning'
    DESC = 'Continuously dealing damage'
    CORRESPONDED_ELEMENT = elements.ElementTypes.FIRE

class StoneAltar(Effect):
    IMG = 'stone_altar'
    NAME = 'Stone Altar'
    DESC = 'Close to the stone altar.\nAble to summon some BOSSes.\n+6 touching defense\n+8 magic defense\n+15% damage'

class MetalAltar(Effect):
    IMG ='metal_altar'
    NAME = 'Metal Altar'
    DESC = 'Close to the metal altar.\nAble to summon some BOSSes.\n+8 touching defense\n+12 magic defense\n+19% damage'

class ScarlettAltar(Effect):
    IMG ='scarlett_altar'
    NAME = 'Scarlett Altar'
    DESC = 'Close to the scarlett altar.\nAble to summon some BOSSes.\n+12 touching defense\n+8 magic defense\n+16% damage\n+5% critical'

class Poison(Aberration):
    IMG = 'poisoned'
    NAME = 'Poison'
    DESC = 'Continuously dealing damage'
    CORRESPONDED_ELEMENT = elements.ElementTypes.POISON

class PotionSickness(Effect):
    IMG = 'potion_sickness'
    NAME = 'Potion Sickness'
    DESC = 'Unable to use healing potion in a time'
    CORRESPONDED_ELEMENT = elements.ElementTypes.POISON


class ManaSickness(Effect):
    IMG = 'mana_sickness'
    NAME = 'Mana Sickness'
    DESC = 'Unable to use mana potion in a time\nDamage deduction\n-10% damage\n-50% magic damage'

class TruthlessCurse(Aberration):
    IMG = 'truthless_curse'
    NAME = 'Truthless Curse'
    CORRESPONDED_ELEMENT = elements.ElementTypes.DARK
    DESC = 'Continuously dealing damage'

class FaithlessCurse(Effect):
    IMG = 'faithless_curse'
    NAME = 'Faithless Curse'
    DESC = 'Cursed\n-80% damage'

class Sticky(Aberration):
    IMG = 'sticky'
    NAME = 'Sticky'
    DESC = 'Continuously dealing damage\n-50% speed'
    CORRESPONDED_ELEMENT = elements.ElementTypes.POISON

class Shield(Effect):
    IMG = 'shield'
    NAME = 'Shield'
    DESC = 'Protected\n+114514 touching defense\n+114514 physical defense\n+114514 magic defense'

class TimeStop(Effect):
    IMG = 'timestop'
    NAME = 'Time-Stopped'
    DESC = 'Time is stoped'

class Gravity(Effect):
    IMG = 'gravity'
    NAME = 'Gravity'
    DESC = 'Gravitated downward'

class JusticeTime(Effect):
    IMG = 'justice_time'
    NAME = 'Justice Time'
    DESC = 'Protected\n+114514 touching defense\n+114514 physical defense\n+114514 magic defense\n+500% damage\n+100% speed'

class Agility(Effect):
    IMG = 'agility'
    NAME = 'Agility'
    DESC = '+100% speed'

class IronSkin(Effect):
    IMG = 'iron_skin'
    NAME = 'Iron Skin'
    DESC = '+32 touching defense'

class Life(Effect):
    IMG = 'life'
    NAME = 'Life'
    DESC = '+40/sec regeneration'

class CurseFire(Aberration):
    IMG = 'curse_fire'
    NAME = 'Curse of Fire'
    DESC = 'Cursed\n-60% damage\nContinuously dealing damage'
    CORRESPONDED_ELEMENT = elements.ElementTypes.POISON

class Faith(Aberration):
    IMG = 'faith'
    NAME = 'Faith'
    DESC = 'Lord will forgive you\n-10% damage\nContinuously being better'
    CORRESPONDED_ELEMENT = elements.ElementTypes.DARK

class Polluted(Effect):
    IMG = 'polluted'
    NAME = 'Polluted'
    DESC = '-65% speed\n-10% critical'
    CORRESPONDED_ELEMENT = elements.ElementTypes.DEATH

class Weak(Effect):
    IMG = 'weak'
    NAME = 'Weak'
    DESC = '-99.5% melee damage\n-99.5% ranged damage\n-99.5% magic damage'
    CORRESPONDED_ELEMENT = elements.ElementTypes.DARK

class OctaveIncrease(Effect):
    OCTAVE_INCREASE = True

class OctSpeedI(OctaveIncrease):
    IMG = 'n_cyan'
    NAME = 'Speed I'
    DESC = '+5% speed'

class OctSpeedII(OctaveIncrease):
    IMG = 'n_cyan'
    NAME = 'Speed II'
    DESC = '+10% speed'

class OctSpeedIII(OctaveIncrease):
    IMG = 'n_cyan'
    NAME = 'Speed III'
    DESC = '+20% speed'

class OctSpeedIV(OctaveIncrease):
    IMG = 'n_cyan'
    NAME = 'Speed IV'
    DESC = '+35% speed'

class OctSpeedV(OctaveIncrease):
    IMG = 'n_cyan'
    NAME = 'Speed V'
    DESC = '+50% speed'

class OctStrengthI(OctaveIncrease):
    IMG = 'n_red'
    NAME = 'Strength I'
    DESC = '+5% damage'

class OctStrengthII(OctaveIncrease):
    IMG = 'n_red'
    NAME = 'Strength II'
    DESC = '+10% damage'

class OctStrengthIII(OctaveIncrease):
    IMG = 'n_red'
    NAME = 'Strength III'
    DESC = '+20% damage'

class OctStrengthIV(OctaveIncrease):
    IMG = 'n_red'
    NAME = 'Strength IV'
    DESC = '+35% damage'

class OctLimitlessI(OctaveIncrease):
    IMG = 'n_blue'
    NAME = 'Limitless I'
    DESC = '+20 additional maximum mana\n+30 additional maximum inspiration'

class OctLimitlessII(OctaveIncrease):
    IMG = 'n_blue'
    NAME = 'Limitless II'
    DESC = '+30 additional maximum mana\n+50 additional maximum inspiration'

class OctLimitlessIII(OctaveIncrease):
    IMG = 'n_blue'
    NAME = 'Limitless III'
    DESC = '+50 additional maximum mana\n+90 additional maximum inspiration'

class OctWisdomI(OctaveIncrease):
    IMG = 'n_green'
    NAME = 'Wisdom I'
    DESC = '+12/sec mana regeneration\n+15/sec inspiration regeneration'

class OctWisdomII(OctaveIncrease):
    IMG = 'n_green'
    NAME = 'Wisdom II'
    DESC = '+18/sec mana regeneration\n+24/sec inspiration regeneration'

class OctWisdomIII(OctaveIncrease):
    IMG = 'n_green'
    NAME = 'Wisdom III'
    DESC = '+28/sec mana regeneration\n+40/sec inspiration regeneration'

class OctLuckyI(OctaveIncrease):
    IMG = 'n_yellow'
    NAME = 'Lucky I'
    DESC = '+4% critical'

class OctLuckyII(OctaveIncrease):
    IMG = 'n_yellow'
    NAME = 'Lucky II'
    DESC = '+8% critical'

class OctLuckyIII(OctaveIncrease):
    IMG = 'n_yellow'
    NAME = 'Lucky III'
    DESC = '+15% critical'

class OctToughnessI(OctaveIncrease):
    IMG = 'n_purple'
    NAME = 'Toughness I'
    DESC = '+15 touching defense'

class OctToughnessII(OctaveIncrease):
    IMG = 'n_purple'
    NAME = 'Toughness II'
    DESC = '+25 touching defense'

class OctToughnessIII(OctaveIncrease):
    IMG = 'n_purple'
    NAME = 'Toughness III'
    DESC = '+40 touching defense'

class OctToughnessIV(OctaveIncrease):
    IMG = 'n_purple'
    NAME = 'Toughness IV'
    DESC = '+60 touching defense'

class OctToughnessV(OctaveIncrease):
    IMG = 'n_purple'
    NAME = 'Toughness V'
    DESC = '+85 touching defense'

class SkillReinforce(Effect):
    pass

class MeleeDemand(SkillReinforce):
    IMG = 'melee_demand'
    NAME = 'Melee Demand'
    DESC = '+20% melee damage\n-10% ranged damage\n-10% magic damage'

class RangedDemand(SkillReinforce):
    IMG = 'ranged_demand'
    NAME = 'Ranged Demand'
    DESC = '+20% ranged damage\n-10% melee damage\n-10% magic damage'

class MagicDemand(SkillReinforce):
    IMG = 'magic_demand'
    NAME = 'Magic Demand'
    DESC = '+20% magic damage\n-10% melee damage\n-10% ranged damage'

class FastThrow(Effect):
    IMG = 'fast_throw'
    NAME = 'Fast Throw'
    DESC = 'Sprinting\n+200% ranged damage'

class TheFury(Effect):
    IMG = 'the_fury'
    NAME = 'The Fury'
    DESC = '+50% melee damage\n+30 touching defense\n-50% speed'

class WarriorShield(Effect):
    IMG = 'warrior_shield'
    NAME = 'Warrior Shield'
    DESC = 'Allows to summon a shield to absorb damage'

class Healer(Effect):
    IMG = 'healer'
    NAME = 'Heals'
    DESC = '+20/sec regeneration\n+50/sec mana regeneration'

class MeleeReinforceI(SkillReinforce):
    IMG = 'melee_reinforce'
    NAME = 'Melee Reinforce'
    DESC = '+10% melee damage\n-5% ranged damage\n-5% magic damage'

class MeleeReinforceII(MeleeReinforceI):
    DESC = '12% damage\n+5/sec regeneration'

class MeleeReinforceIII(MeleeReinforceI):
    DESC = '+25 touching defense'

class MeleeReinforceIV(MeleeReinforceI):
    DESC = '+25 magic defense'

class RangedReinforceI(SkillReinforce):
    IMG = 'ranged_reinforce'
    NAME = 'Ranged Reinforce'
    DESC = '+10% ranged damage\n-5% melee damage\n-5% magic damage'

class RangedReinforceII(RangedReinforceI):
    DESC = '5% damage\n+12% critical'

class RangedReinforceIII(RangedReinforceI):
    DESC = '+15% speed\n+3 touching defense'

class RangedReinforceIV(RangedReinforceI):
    DESC = '-5% air resistance\n+7 magic defense'

class MagicReinforceI(SkillReinforce):
    IMG = 'magic_reinforce'
    NAME = 'Magic Reinforce'
    DESC = '+10% magic damage\n-5% melee damage\n-5% ranged damage'

class MagicReinforceII(MagicReinforceI):
    DESC = '+6% damage\n+12/sec regeneration'

class MagicReinforceIII(MagicReinforceI):
    DESC = '+40 additional maximum mana\n+5 touching defense'

class MagicReinforceIV(MagicReinforceI):
    DESC = '+20/sec mana regeneration\n+12 magic defense'
