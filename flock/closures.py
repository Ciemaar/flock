__author__ = 'andriod'

"""
The closures module provides helper functions for creating common sorts of closures that you might need in
working with flock.

>>> def outer_func(param):
...     def closure():
...         print(param)
...     return closure
...
>>> stuffPrinter = outer_func("stuff")
>>> stuffPrinter()
stuff
>>> sgPrinter = outer_func("StarGate")
>>> stuffPrinter()
stuff
>>> sgPrinter()
StarGate

The way closures actually work is that each function in python has a table of local variables.  This is what you see
when you call locals().  When you return a function from within a function any local variables needed by the internal
function are preserved for when it is called later.

You can see these captured variables in the function's __closure__ field i.e.

>>> sgPrinter.__closure__[0].cell_contents
'StarGate'

and the names are separately at:
>>> sgPrinter.__code__.co_freevars
('param',)
"""


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


def toggle():
    store = [False]

    def inner_toggle():
        store[0] = not store[0]
        return store[0]

    return inner_toggle
