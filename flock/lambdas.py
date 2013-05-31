__author__ = 'andriod'


def lookup(character, attribute, table):
    return lambda: table.get(character[attribute], None)


def reference(obj, *indexes):
    def de_ref():
        currObj = obj
        for index in indexes:
            currObj = currObj[index]
        return currObj

    return de_ref