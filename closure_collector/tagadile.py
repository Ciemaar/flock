class Tagadile:
    """
    Aggregate across parallel maps.

    :type sources: one of:
        - list of sources to aggregate across, each source should be a map, generally a dict, or FlockDict, not all keys need to be present in all sources.
        - Mapping the values in sources are used as the list above, keys are ignored
        - a callable that returns the list of sources

        Precedence is Mapping, callable, then list

    :type fn: function must take a generator, there is no constraint on the return value
    """

    def __init__(self, sources, fn, keys=None):
        self.sources = sources
        self.function = fn
        if keys is not None and not callable(keys):
            keys = set(keys)
        self.source_keys = keys
