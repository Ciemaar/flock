import argparse
import csv
import logging
import pickle
import sys
import yaml
from collections import defaultdict, Counter
from fractions import Fraction
from functools import reduce
from itertools import chain
from operator import add
from pprint import pprint

from flock.closures import lookup, reference
from flock.core import FlockDict, Aggregator, MetaAggregator

#set the recursion limit low for safety
GENERAL = 'General'
HEROIC = "Heroic"
MENTAL = "Mental"
SPELL = "Spell"
PHYSICAL = "Physical"
WEAPON = "Weapon"
sys.setrecursionlimit(100)

_attribute_table = None


def get_attribute_table():
    global _attribute_table
    if _attribute_table:
        return _attribute_table
    _attribute_table = defaultdict(dict)
    table_file = open("mythica/Attribute Tables.csv")
    plainReader = csv.reader(table_file)
    fieldNames = list(zip(plainReader.__next__(), plainReader.__next__()))
    dReader = csv.DictReader(table_file, fieldnames=fieldNames)
    table = [x for x in dReader]
    for row in table:
        for lookup, value in row.items():
            if lookup == ('', ''):
                continue
            try:
                value = float(Fraction(value))
            except ValueError:
                if value[-1] == '%':
                    value = float(value[:-1]) / 100
                elif value[-4:] == "/day":
                    value = float(value[:-4])
                elif value[-5:] == "/hour":
                    value = float(value[:-5])
            _attribute_table[lookup][int(row[('', '')])] = value
    return _attribute_table


def apply_attribute_table(character):
    if 'Attribute_Bonuses' not in character:
        character['Attribute_Bonuses'] = FlockDict()
    for (attribute, bonus), table in get_attribute_table().items():
        character['Attribute_Bonuses'][bonus] = lookup(character, attribute, table)
    character['base_bonuses'] = {'Spell Points Multiple': {'General': 1}}
    character['bonuses'] = Aggregator([character['Attribute_Bonuses'], character['base_bonuses']], cross_total)



def apply_attribs(character):
    for attribute in character['base_stats']:
        character[attribute] = reference(character, 'base_stats', attribute)


def apply_racial_bonuses(character):
    if character["Race"] == "Human":
        preVal = character["Spirit"]
        character["Spirit"] = lambda: preVal + 2
        character.setdefault('Racial Bonuses', FlockDict())
        character['Racial Bonuses']['heroics'] = 1
    # print("character bonuses {ct_type} sources {sources} bonuses {rb_type}".format(
    #     ct_type=type(character.promises['bonuses']), rb_type=type(character.promises['Racial Bonuses']),
    #     sources=character.promises['bonuses'].sources))
    character.promises['bonuses'].sources.append(character['Racial Bonuses'])


def apply_level_allotments(character):
    if 'level' not in character:
        character['level'] = 1
    character.setdefault('points', FlockDict())
    character['points'].setdefault('total', FlockDict({'universal': 10}))
    character['points']['total']['mental'] = lambda: character['level'] * character['bonuses']['Mental Skill Points']

    character['points']['total']['physical'] = lambda: character['level'] * character['bonuses']['Phy Skill Points']
    character['points']['total']['heroic'] = lambda: character['level'] * (
        character['level'] + 1 + character['bonuses']['heroics'])


def apply_skills(character):
    character.setdefault('skills', [])
    for skill in list(character['skills']):
        pass
        #character['skills'] = ......

    character['points'].setdefault('spent', FlockDict())
    character['points'].setdefault('available', FlockDict())

    character['points']['spent']['mental'] = lambda: sum(skill.cost for skill in character['skills'] if skill.isMental)
    character['points']['available']['mental'] = lambda: character['points']['total']['mental'] - \
                                                         character['points']['spent']['mental']
    character['points']['spent']['physical'] = lambda: sum(
        skill.cost for skill in character['skills'] if skill.isPhysical)
    character['points']['available']['physical'] = lambda: character['points']['total']['physical'] - \
                                                           character['points']['spent']['physical']
    character['points']['spent']['heroic'] = lambda: sum(skill.cost for skill in character['skills'] if skill.isHeroic)
    character['points']['available']['heroic'] = lambda: character['points']['total']['heroic'] - \
                                                         character['points']['spent']['heroic']
    character['points']['spent']['universal'] = lambda: -sum(
        min(0, character['points']['available'][pt_type]) for pt_type in character['points']['available'] if
        pt_type != 'universal')
    character['points']['available']['universal'] = lambda: character['points']['total']['universal'] - \
                                                            character['points']['spent']['universal']


def cross_total(inputs):
    inputs = list(inputs)
    if len(inputs) == 1:
        return inputs[0]
    try:
        return sum(inputs)
    except TypeError:
        return dict(reduce(add, (Counter(y) for y in inputs), Counter()))


def apply_heroics(character):
    character['Heroic Bonuses'] = MetaAggregator(
        lambda: (skill.bonuses for skill in character['skills'] if skill.isHeroic), cross_total)
    character.promises['bonuses'].sources.append(character['Heroic Bonuses'])


def apply_rules(character):
    # pprint(ret.resolve())
    apply_attribs(character)
    # pprint(ret.resolve())
    apply_attribute_table(character)
    # pprint(ret.check())
    # pprint(ret.resolve())
    apply_racial_bonuses(character)
    # pprint(ret.resolve())
    apply_level_allotments(character)
    # pprint(ret.resolve())
    apply_skills(character)
    # pprint(ret.resolve())
    apply_heroics(character)
    # pprint(ret.resolve())
    character['Spell Points'] = Aggregator([character['bonuses']['Spell Points Multiple']],
                                           lambda x: sum(x) * character['bonuses']['Spell Points'])
    return character



def load_character(filename):
    sheet = pickle.load(open(filename, 'rb'))
    ret = FlockDict(sheet)
    return apply_rules(ret)


def save_character(character, filename):
    pickle.dump(character.shear(), open(filename, 'wb'))

class Skill(object):
    def __init__(self, name, skill_type, cost=1, xp=0, level=1):
        self.name = name
        self.skill_type = skill_type
        self.cost = cost
        self.xp = xp
        self.level = max(level,cost)

    def __repr__(self):
        return "Skill('{name}', {skill_type}, {cost}, {xp}, {level})".format(name=self.name, skill_type=self.skill_type,
                                                                           cost=self.cost, xp=self.xp, level=self.level)

    @property
    def isPhysical(self):
         return self.skill_type == PHYSICAL or self.skill_type == WEAPON

    @property
    def isMental(self):
        return self.skill_type == MENTAL or self.skill_type == SPELL

    @property
    def isHeroic(self):
        return self.skill_type == HEROIC


class HeroicSkill(Skill):
    def __init__(self, name, skill_type=HEROIC, cost=1, level=1, bonuses={}):
        assert skill_type == HEROIC
        super(HeroicSkill, self).__init__(name, skill_type, cost, xp=None, level=level)
        self.bonuses = bonuses

    def __repr__(self):
        return "{cls_name}('{name}', '{skill_type}', {cost}, {level}, {bonuses})".format(name=self.name,
                                                                                         skill_type=self.skill_type,
                                                                                         cost=self.cost, xp=self.xp,
                                                                                         level=self.level,
                                                                                         bonuses=self.bonuses,
                                                                                         cls_name=self.__class__.__name__)

    @property
    def xp(self):
        return None

    xp = xp.setter(lambda x, y: None)


class Conduit(HeroicSkill):
    def __init__(self, skill_type=HEROIC, cost=1, level=1, spell_type=''):
        if not spell_type:
            spell_type = 'General'
        self.spell_type = spell_type
        super().__init__(self.name, skill_type, cost, level, None)

    def __repr__(self):
        return "{cls_name}('{skill_type}', {cost}, {level}, {spell_type})".format(name=self.name,
                                                                                  skill_type=self.skill_type,
                                                                                  spell_type=self.spell_type,
                                                                                  cost=self.cost, xp=self.xp,
                                                                                  level=self.level,
                                                                                  bonuses=self.bonuses,
                                                                                  cls_name=self.__class__.__name__)

    def __str__(self):
        return "{name} x{cost} {bonuses})".format(name=self.name, skill_type=self.skill_type,
                                                  spell_type=self.spell_type,
                                                  cost=self.cost, xp=self.xp, level=self.level, bonuses=self.bonuses,
                                                  cls_name=self.__class__.__name__)

    @property
    def bonuses(self):
        return {'Spell Points Multiple': {self.spell_type: self.cost}}

    @bonuses.setter
    def bonuses(self, value):
        return

    @property
    def name(self):
        if self.spell_type == GENERAL:
            return 'Conduit'
        else:
            return 'Conduit -- %s' % self.spell_type

    @name.setter
    def name(self, value):
        return

    @staticmethod
    def representer(dumper, data):
        return dumper.represent_scalar(u'!conduit', '{cost} {spt}'.format(cost=data.cost, spt=data.spell_type))

    @classmethod
    def constructor(cls, loader, node):
        value = loader.construct_scalar(node)
        parsed = value.split(' ')
        cost = int(parsed[0])
        spell_type = ' '.join(parsed[1:])
        return cls(cost=cost, spell_type=spell_type)


yaml.add_representer(Conduit, Conduit.representer)
yaml.add_constructor(u'!conduit', Conduit.constructor)

def get_parser():
    parser = argparse.ArgumentParser(description='Mythica Character manager', )

    parser.add_argument("--infile", type=argparse.FileType('r'), default=None, help="File to read character from.")
    parser.add_argument("--outfile", type=argparse.FileType('w'), default=None, help="File to read character from.")
    return parser

if __name__ == "__main__":
    logging.basicConfig()
    parser = get_parser()
    opt = parser.parse_args()

    # char = load_character("Mondavite2.pkl")
    char = FlockDict()

    if not opt.infile:
        char['base_stats'] = {'Combat Skill': 13, 'Dexterity': 16, 'Health': 11, 'Intelligence': 18, 'Magic': 17,
                              'Perception': 20, 'Presence': 11, 'Speed': 13, 'Spirit': 10, 'Strength': 10, 'Luck': 10}
        char['practice_sessions'] = {'Combat Skill': 9, 'Dexterity': 2}
        char['skills'] = [
            Skill('Read Common', MENTAL),
            Skill('Bargaining', MENTAL),
            Skill('Begging', MENTAL, 2),
            Skill('Appraisal', MENTAL),
            Skill('Local History', MENTAL),
            Skill('Endow Plants', MENTAL),
            Skill('Fishing', MENTAL),
            Skill('Artificer', MENTAL, 2),
            Skill('Stiletto', WEAPON, 2),
            Skill('Pick Pockets', PHYSICAL, 2),
            Skill('Tumbling', PHYSICAL),
            Skill('Disguise', PHYSICAL, 2),
            Skill('Armor', PHYSICAL, xp=4),
            Skill('Ranged Spell', WEAPON, 4, 1),
            Skill('Rope Use', PHYSICAL),
            Skill('Scattershot', SPELL),
            Skill('Spell Craft', MENTAL, 2, xp=2, level=3),
            Skill('Spell Theory', MENTAL, 2, xp=2, level=3),
            Skill('Smithing', PHYSICAL, 2, 4),
            Skill('Weapon Smithing', MENTAL, 2),
            Skill('Dust Bolt', SPELL),
            Skill('Deep Bolt', SPELL, xp=1),
            Skill('Armor', SPELL, xp=4),
            Skill('Jewel Smithing', MENTAL, cost=1, level=2),
            Skill('Research', MENTAL),
            Skill('Cartography', MENTAL, xp=1),
            Skill('Ice Bolt', SPELL, cost=0, xp=4),
            Skill('Geomancy', SPELL, cost=0, xp=2, level=2),
            Skill('Detect Magic', SPELL, cost=0, xp=11),
            Skill('Ice Bolt', SPELL, cost=0, xp=4),
            Skill('Endow with Element', SPELL, level=2, xp=5, cost=0),
            Skill('Imposing Image', SPELL, level=1),
            Skill('Reality Leak', SPELL, level=2, cost=0),

            HeroicSkill('First Circle Access', HEROIC, 1),
            HeroicSkill('Nimble', HEROIC, 2, bonuses={'Dodge': 1, 'Parry': 1}),
            HeroicSkill('First Tier Arcane', HEROIC, 1),
            HeroicSkill('Second Tier Arcane', HEROIC, 3),
            Conduit(cost=5),
            HeroicSkill('Uncanny Strike', HEROIC, 1, bonuses={'Hit Bonus': 1}),
            HeroicSkill('Grevious Blow', HEROIC, 8, bonuses={'Base Damage': 1}),
            HeroicSkill('Rapidity', HEROIC, 6, bonuses={'Initiative': -1}),
            HeroicSkill('Vicous Blow', HEROIC, 1, bonuses={'Damage': 1}),
            HeroicSkill('Stealth Strike', HEROIC, 3),
            HeroicSkill('Aura Extension', HEROIC, 1),
            HeroicSkill('3rd Tier', HEROIC, 5),
            HeroicSkill('Nimble', HEROIC, 4, bonuses={'Dodge': 1, 'Parry': 1}),
            HeroicSkill('Flurry', HEROIC, 6),
            HeroicSkill('2nd Circle', HEROIC, 10),
            HeroicSkill('4th Tier', HEROIC, 10),

        ]
        char['Race'] = "Human"
        char['level'] = 8
    else:
        for key, value in yaml.load(opt.infile).items():
            char[key] = value

    apply_rules(char)
    char.check()
    # pprint(char.shear())
    sheared = char.shear()
    for attribute in chain([], sheared['base_stats'].keys()):
        print("%s: %s" % (attribute, sheared.pop(attribute)))
    pprint(sheared)
    if opt.outfile:
        # sheared['skills'] = []
        # for skill in sheared.skill:
        yaml.dump(sheared, opt.outfile, width=80)
