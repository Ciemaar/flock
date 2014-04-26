import pickle
import csv
from collections import defaultdict
from fractions import Fraction

from pprint import pprint
import sys
from flock.core import FlockDict, Aggregator, MetaAggregator
from flock.closures import lookup, reference

#set the recursion limit low for safety
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
    character['bonuses'] = Aggregator([character['Attribute_Bonuses']], sum)


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
    character['points'].setdefault('total', FlockDict())
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


def apply_heroics(character):
    character['Heroic Bonuses'] = MetaAggregator(
        lambda: (skill.bonuses for skill in character['skills'] if skill.isHeroic), sum)
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
    return character


def load_character(filename):
    sheet = pickle.load(open(filename, 'rb'))
    ret = FlockDict(sheet)
    return apply_rules(ret)


def save_character(character, filename):
    pickle.dump(character.shear(), open(filename, 'wb'))


if __name__ == "__main__":
    # char = load_character("Mondavite2.pkl")
    char = FlockDict()
    char['base_stats'] = {'Combat Skill': 13, 'Dexterity': 16, 'Health': 11, 'Intelligence': 18, 'Magic': 17,
                          'Perception': 20, 'Presence': 11, 'Speed': 13, 'Spirit': 10, 'Strength': 10, 'Luck': 10}
    char['Race'] = "Human"

    apply_rules(char)
    char.check()
    pprint(char.shear())
    char['level'] = 8
    pprint(char.shear())
