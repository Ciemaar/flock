from collections import UserDict


class TagView:
    """A view to return the attribute values."""

    def __init__(self, tag):
        self.tag = tag
        self.items = set(tag)

    def __iter__(self):
        return self

    def __next__(self):
        if not self.items:
            raise StopIteration
        ret_attr = self.items.pop()
        return getattr(self.tag.tagged_obj, ret_attr)


class Tag(set):
    """A Specialized Set that returns the value of the attributes when iterated."""

    def __init__(self, tagged_obj):
        super().__init__()
        self.tagged_obj = tagged_obj

    def __iter__(self):
        return TagView(self)


class AttributeTagset(UserDict):
    """A class for adding sets of tagged attributes for an object

    Each item in this map is a set of tagged attributes.  Attribute names may be added via .add() or .remove() and
    checked for membership as normal, but if the Tag is iterated the attribute values are returned.
    """

    def __init__(self, tagged_obj):
        super().__init__()
        self.tagged_obj = tagged_obj

    def __missing__(self, key):
        self[key] = s = Tag(self.tagged_obj)
        return s
