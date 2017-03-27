import logging

log = logging.getLogger(__name__)

__author__ = 'andriod'

def patch(map, key_list, val):
    for key in key_list[0:-1]:
        try:
             map = map[key]
        except KeyError:
             map[key] = {}
             map = map[key]
    map[key_list[-1]] = val
