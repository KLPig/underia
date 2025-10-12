
from resources import time
from values import hp_system, elements, damages
from underia import game, inventory


class Effect:
    CORRESPONDED_ELEMENT = elements.ElementTypes.NONE
    IMG = 'empty'
    NAME = 'Effect'
    DESC = ''
    COMBINE = 'Duration'

    def __init__(self, duration, level):
        self.timer = duration
        self.level = level
        self.duration = duration
        self.tick = 0
        self.datas = {}
        for desc in self.DESC.split('\n'):
            desc = desc.replace(' ', '').lower().replace('.', '')
            try:
                self.datas.update(inventory.Inventory.Item.handle_data(desc))
            except ValueError:
                print(f"Invalid accessory data: {desc}")

    def on_update(self, entity: hp_system.HPSystem):
        self.tick += 1
        if self.duration < 10 ** 8:
            self.timer -= 1 / 1000 * game.get_game().clock.last_tick

    def on_end(self, entity: hp_system.HPSystem):
        pass

    def on_start(self, entity: hp_system.HPSystem):
        pass


class Aberration(Effect):
    IMG = 'aberration'

    def on_update(self, entity: hp_system.HPSystem):
        super().on_update(entity)
        dmg = min(self.level + 2, max(entity.max_hp / 200, 200.0))
        if (dmg * 3  > (1000 / game.get_game().clock.last_tick) or self.tick % 9 == 0) and self.tick % 3 == 0:
            entity.damage(dmg / 1000 * game.get_game().clock.last_tick * (9 if dmg * 3 > (1000 / game.get_game().clock.last_tick) else 3),
                          getattr(damages.DamageTypes, 'ELEMENT_' + elements.NAMES[self.CORRESPONDED_ELEMENT].upper()), sound=False)


class Burning(Aberration):
    IMG = 'burning'
    NAME = 'Burning'
    DESC = 'Continuously dealing damage'
    CORRESPONDED_ELEMENT = elements.ElementTypes.FIRE

class Freezing(Effect):
    IMG = 'freezing'
    NAME = 'Freezing'
    DESC = '-60% speed'
    CORRESPONDED_ELEMENT = elements.ElementTypes.WATER

class AfterimageShadow(Effect):
    IMG = 'afterimage_shadow'
    NAME = 'Afterimage Shadow'
    DESC = 'Afterimage Shadow\n+300% damage\n+1000% critical\n+50% dodge rate'
    CORRESPONDED_ELEMENT = elements.ElementTypes.DEATH

class Darkened(Effect):
    IMG = 'darkened'
    NAME = 'Darkened'
    DESC = '-50% damage'
    CORRESPONDED_ELEMENT = elements.ElementTypes.DARK

class Enlightened(Effect):
    IMG = 'enlightened'
    NAME = 'Enlightened'
    DESC = '-100 touching defense\n-100 magic defense\n+20/sec regeneration'
    CORRESPONDED_ELEMENT = elements.ElementTypes.LIGHT

class Frozen(Effect):
    IMG = 'freezing'
    NAME = 'Frozen'
    DESC = 'Unable to move(for other mobs)'
    CORRESPONDED_ELEMENT = elements.ElementTypes.WATER

class StoneAltar(Effect):
    IMG = 'stone_altar'
    NAME = 'Stone Altar'
    DESC = 'Close to the stone altar.\nAble to summon some BOSSes.\n+6 touching defense\n+8 magic defense\n+15% damage'
    COMBINE = None

class MetalAltar(Effect):
    IMG ='metal_altar'
    NAME = 'Metal Altar'
    DESC = 'Close to the metal altar.\nAble to summon some BOSSes.\n+8 touching defense\n+12 magic defense\n+19% damage'
    COMBINE = None

class ScarlettAltar(Effect):
    IMG ='scarlett_altar'
    NAME = 'Scarlett Altar'
    DESC = 'Close to the scarlett altar.\nAble to summon some BOSSes.\n+12 touching defense\n+8 magic defense\n+16% damage\n+5% critical'
    COMBINE = None

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
    COMBINE = None


class ManaSickness(Effect):
    IMG = 'mana_sickness'
    NAME = 'Mana Sickness'
    DESC = 'Unable to use mana potion in a time\nDamage deduction\n-10% damage\n-50% magic damage'
    COMBINE = None

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

class Wither(Aberration):
    IMG = 'wither'
    NAME = 'Wither'
    DESC = 'Continuously dealing damage\n-10% speed'
    CORRESPONDED_ELEMENT = elements.ElementTypes.DEATH

class Weak(Effect):
    IMG = 'weak'
    NAME = 'Weak'
    DESC = '-99.5% melee damage\n-99.5% ranged damage\n-99.5% magic damage'
    CORRESPONDED_ELEMENT = elements.ElementTypes.DARK

class MatterDomain(Aberration):
    IMG = 'matter_domain'
    NAME = 'Matter Domain'
    DESC = 'Weights of matter press you down\nContinuously dealing damage\n-40% critical\n+300kg\n+100% air resistance'

class TimeDomain(Aberration):
    IMG = 'time_domain'
    NAME = 'Time Domain'
    DESC = 'Time is slowing you down\nContinuously dealing damage\n-25% damage\n-100 magic defense\n+50% mana cost'

class Bleeding(Effect):
    IMG = 'bleeding'
    NAME = 'Bleeding'
    DESC = '-4/sec regeneration'

class BleedingR(Aberration):
    IMG = 'bleeding'
    NAME = 'Bleeding'
    DESC = 'Continuously dealing damage'

class FlashBack(Effect):
    IMG = 'flashback'
    NAME = 'Flashback'
    DESC = 'Time is stopped\n-50% speed'

class DemonContract(Effect):
    IMG = 'demon_contract'
    NAME = 'Demon Contract'
    DESC = 'Vee hee hee!\nA good trade!\nA good trade!\n-50% damage\n-100 touching defense\n-100 magic defense'

class FateAlign(Effect):
    IMG = 'fate_align'
    NAME = 'Fate Align'
    DESC = 'Fate will guide you\n+25% damage\n+10% critical\n+10% speed'

class OctaveIncrease(Effect):
    OCTAVE_INCREASE = True

class OctSpeedI(OctaveIncrease):
    IMG = 'n_cyan'
    NAME = 'Speed I'
    DESC = '+20% speed'

class OctSpeedII(OctaveIncrease):
    IMG = 'n_cyan'
    NAME = 'Speed II'
    DESC = '+36% speed'

class OctSpeedIII(OctaveIncrease):
    IMG = 'n_cyan'
    NAME = 'Speed III'
    DESC = '+69% speed'

class OctSpeedIV(OctaveIncrease):
    IMG = 'n_cyan'
    NAME = 'Speed IV'
    DESC = '+138% speed'

class OctSpeedV(OctaveIncrease):
    IMG = 'n_cyan'
    NAME = 'Speed V'
    DESC = '+277% speed'

class OctStrengthI(OctaveIncrease):
    IMG = 'n_red'
    NAME = 'Strength I'
    DESC = '+8% damage'

class OctStrengthII(OctaveIncrease):
    IMG = 'n_red'
    NAME = 'Strength II'
    DESC = '+15% damage'

class OctStrengthIII(OctaveIncrease):
    IMG = 'n_red'
    NAME = 'Strength III'
    DESC = '+27% damage'

class OctStrengthIV(OctaveIncrease):
    IMG = 'n_red'
    NAME = 'Strength IV'
    DESC = '+55% damage'

class OctLimitlessI(OctaveIncrease):
    IMG = 'n_blue'
    NAME = 'Limitless I'
    DESC = '+50 additional maximum mana\n+200 additional maximum inspiration'

class OctLimitlessII(OctaveIncrease):
    IMG = 'n_blue'
    NAME = 'Limitless II'
    DESC = '+90 additional maximum mana\n+360 additional maximum inspiration'

class OctLimitlessIII(OctaveIncrease):
    IMG = 'n_blue'
    NAME = 'Limitless III'
    DESC = '+160 additional maximum mana\n+700 additional maximum inspiration'

class OctWisdomI(OctaveIncrease):
    IMG = 'n_green'
    NAME = 'Wisdom I'
    DESC = '+15/sec mana regeneration\n+40/sec inspiration regeneration'

class OctWisdomII(OctaveIncrease):
    IMG = 'n_green'
    NAME = 'Wisdom II'
    DESC = '+27/sec mana regeneration\n+75/sec inspiration regeneration'

class OctWisdomIII(OctaveIncrease):
    IMG = 'n_green'
    NAME = 'Wisdom III'
    DESC = '+52/sec mana regeneration\n+140/sec inspiration regeneration'

class OctLuckyI(OctaveIncrease):
    IMG = 'n_yellow'
    NAME = 'Lucky I'
    DESC = '+15% critical'

class OctLuckyII(OctaveIncrease):
    IMG = 'n_yellow'
    NAME = 'Lucky II'
    DESC = '+28% critical'

class OctLuckyIII(OctaveIncrease):
    IMG = 'n_yellow'
    NAME = 'Lucky III'
    DESC = '+55% critical'

class OctToughnessI(OctaveIncrease):
    IMG = 'n_purple'
    NAME = 'Toughness I'
    DESC = '+9 touching defense\n+3 magic defense'

class OctToughnessII(OctaveIncrease):
    IMG = 'n_purple'
    NAME = 'Toughness II'
    DESC = '+16 touching defense\n+7 magic defense'

class OctToughnessIII(OctaveIncrease):
    IMG = 'n_purple'
    NAME = 'Toughness III'
    DESC = '+30 touching defense\n+15 magic defense'

class OctToughnessIV(OctaveIncrease):
    IMG = 'n_purple'
    NAME = 'Toughness IV'
    DESC = '+55 touching defense\n+28 magic defense'

class OctToughnessV(OctaveIncrease):
    IMG = 'n_purple'
    NAME = 'Toughness V'
    DESC = '+105 touching defense\n+55 magic defense'

class SkillReinforce(Effect):
    pass

class RuneAltar(Effect):
    IMG = 'rune_altar'
    NAME = 'Rune Altar'
    DESC = 'Able to learn thaumaturgies.'

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
    DESC = 'Sprinting\n+200% ranged damage\n+20% dodge rate'

class StormThrow(Effect):
    IMG = 'fast_throw'
    NAME = 'Storm Throw'
    DESC = 'Sprinting\n+400% ranged damage\n+40% dodge rate'

class TheFury(Effect):
    IMG = 'the_fury'
    NAME = 'The Fury'
    DESC = '+50% melee damage\n+30 touching defense\n-50% speed'

class TheWraith(Effect):
    IMG = 'the_fury'
    NAME = 'The Wraith'
    DESC = '+80% melee damage\n+100 touching defense\n-100% speed'

class WarriorShield(Effect):
    IMG = 'warrior_shield'
    NAME = 'Warrior Shield'
    DESC = 'Allows to summon a shield to absorb damage'

class Guard(Effect):
    IMG = 'warrior_shield'
    NAME = 'Guard'
    DESC = 'Allows to summon a shield to absorb 1000 damage'

class Healer(Effect):
    IMG = 'healer'
    NAME = 'Heals'
    DESC = '+20/sec regeneration\n+50/sec mana regeneration'

class CurseSnow(Effect):
    IMG = 'curse_snow'
    NAME = 'Curse of Snow'
    DESC = 'Cursed\n-5/sec regeneration'
    CORRESPONDED_ELEMENT = elements.ElementTypes.WATER

class CurseHell(Effect):
    IMG = 'curse_hell'
    NAME = 'Curse of Hell'
    DESC = 'Cursed\n-10% damage'
    CORRESPONDED_ELEMENT = elements.ElementTypes.FIRE

class CurseSand(Effect):
    IMG = 'curse_sand'
    NAME = 'Curse of Sand'
    DESC = 'Cursed\n-10 touching defense\n-10 magic defense'
    CORRESPONDED_ELEMENT = elements.ElementTypes.EARTH

class CurseHeaven(Effect):
    IMG = 'curse_heaven'
    NAME = 'Curse of Heaven'
    DESC = 'Cursed\n-20% critical'
    CORRESPONDED_ELEMENT = elements.ElementTypes.LIGHT

class CurseTree(Effect):
    IMG = 'curse_tree'
    NAME = 'Curse of Tree'
    DESC = 'Cursed\n-25% speed\n+50% air resistance'

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

class ExtremeTerror(Effect):
    NAME = 'Extreme Terror'
    IMG = 'extreme_terror'
    DESC = 'You are terrified.\nChaos attack deducts your maximum HP'

class BalancedSheathAttack(Effect):
    NAME = 'Balanced Sheath: Attack'
    IMG = 'balanced_sheath_attack'
    DESc = '-100% dodge rate\n-50 touching defense\n+100% melee damage\n+100% critical'

class LogosThaumaturgy(Effect):
    NAME = 'Logos Thaumaturgy'
    IMG = 'logos_thaumaturgy'
    DESC = '+100% critical'

class WeakManaI(Effect):
    NAME = 'Weak Mana'
    IMG = 'weak_mana'
    DESC = 'Decreased mana regeneration'

class ManaDrain(Effect):
    NAME = 'Mana Drain'
    IMG = 'weak_mana'
    DESC = 'Decreased mana regeneration'
    COMBINE = None
