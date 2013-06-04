__author__ = 'andriod'


def lookup(mapping, index, table):
    """
    Create a closure that looks up the specified value from the table
    :type mapping: Mapping the FlockDict or other Mapping to look up from
    :type index: str the index in the Mapping to check
    :type table: Mapping the table to lookup from
    :return:the 0 parameter lambada-closure that returns value as found in the table
    """
    return lambda: table.get(mapping[index], None)


def reference(flock, *indexes):
    """
    return closure that references values stored elsewhere in the Flock
    :type flock: flock.core.FlockDict
    :param indexes: lambdas to be resolved in order
    :return: 0 parameter function with all parameters included as a closure, returns referenced value
    """

    def de_ref():
        currObj = flock

        # recursively resolve indexes
        for index in indexes:
            currObj = currObj[index]
        return currObj

    return de_ref