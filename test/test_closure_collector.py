import unittest

from pytest import raises

from closure_collector.closures import attr_reference, toggle
from closure_collector.core import (
    ClosureCollector,
    DynamicClosureCollector,
    ShearedBase,
)
from closure_collector.util import ClosureCollectorException
from flock import FlockDict

__author__ = "Andy Fundinger"

TEST_LIST = [True, False, None]


def test_dynamic_cc():
    test_obj = ClosureCollector()
    assert not test_obj.get_relatives()
    for i in TEST_LIST:
        test_obj.peers.add(i)
    assert all(i in DynamicClosureCollector.get_relatives(test_obj) for i in TEST_LIST)
    rep = repr(test_obj)
    assert rep
    assert "ClosureCollector" in rep


class BasicClosureCollectorTestCase(unittest.TestCase):
    """
    Tests of the basic operations of a closureCollector
    """

    def setUp(self):
        super().setUp()
        self.closure_collector = ClosureCollector()

    def test_simple_values(self):
        """
        Test that simple(non-dict, non-callable) values are stored and retrieved transparently.
        """
        self.closure_collector.three = 3
        assert self.closure_collector.three == 3

        setattr(self.closure_collector, "Shepherd", "Mary")

        self.assertEqual(getattr(self.closure_collector, "Shepherd"), "Mary")
        setattr(self.closure_collector, "Management", ["Mary", "Joshua", "Isaac"])

        self.assertEqual(
            getattr(self.closure_collector, "Management"), ["Mary", "Joshua", "Isaac"]
        )
        setattr(self.closure_collector, "Shepherd", "John")
        self.assertEqual(getattr(self.closure_collector, "Shepherd"), "John")
        assert hasattr(self.closure_collector, "Shepherd")
        assert not hasattr(self.closure_collector, "missing")

        delattr(self.closure_collector, "Shepherd")
        assert not hasattr(self.closure_collector, "Shepherd")

    def test_simple_dict(self):
        """
        Test that nested dicts still look like dicts.
        """
        self.closure_collector.Management = {"Mary": {"lambs": 1, "size": "little"}}
        assert self.closure_collector.Management["Mary"]["lambs"] == 1
        assert self.closure_collector.Management["Mary"]["size"] == "little"

    def test_simple_closure(self):
        """
        Test that simple closures are stored without mangling and evaluated on retrieval
        """
        setattr(self.closure_collector, "lamb", lambda: "little")
        self.assertEqual(getattr(self.closure_collector, "lamb"), "little")

    def test_callable_with_arguments(self):
        """
        Test that callables with arguments are passed transparently and never called
        """
        setattr(self.closure_collector, "func", lambda x, y: x + y)
        self.assertEqual(getattr(self.closure_collector, "func")(1, 2), 3)

        def test2(x, y):
            assert False

        setattr(self.closure_collector, "test2", test2)
        assert test2 == getattr(
            self.closure_collector, "test2"
        )  # Testing that this is not called

    def test_error(self):
        setattr(self.closure_collector, "bad", lambda: 1 / 0)
        with raises(ClosureCollectorException) as exc_info:
            self.closure_collector.bad
        assert isinstance(exc_info.value.__cause__, ZeroDivisionError)
        assert not hasattr(self.closure_collector, "bad")

        with raises(ClosureCollectorException) as exc_info:
            assert getattr(self.closure_collector, "bad") != (
                lambda: 1 / 0
            ), "This should not be called at all as the exception should be raised"
        assert isinstance(exc_info.value.__cause__, ZeroDivisionError)

        with raises(ClosureCollectorException) as exc_info:
            self.closure_collector.shear()
        assert isinstance(exc_info.value.__cause__, ZeroDivisionError)

        error = self.closure_collector.shear(record_errors=True).bad
        assert isinstance(error, ClosureCollectorException)
        assert isinstance(error.__cause__, ZeroDivisionError)

    def test_shear(self):
        """
        Test trivial shear operation
        """
        self.closure_collector.three = 15
        assert not self.closure_collector.check()
        sheared = self.closure_collector.shear()

        assert sheared.three == 15

        setattr(self.closure_collector, "cat", lambda: "Abbey")
        assert not self.closure_collector.check()
        sheared = self.closure_collector.shear()
        assert sheared.cat == "Abbey"
        assert sheared.three == 15

        ds = self.closure_collector.dataset()
        assert ds.cat == "Abbey"
        assert ds.three == 15
        assert len(self.closure_collector.ruleset().promises) == len(
            ClosureCollector().promises
        )
        assert not self.closure_collector.ruleset()

        self.closure_collector.mimi = ClosureCollector(species="cat", rank=2)
        sheared = self.closure_collector.shear()
        assert self.closure_collector.mimi.species == sheared.mimi.species == "cat"
        assert self.closure_collector.mimi.rank == sheared.mimi.rank == 2

    def test_consistent_shear(self):
        t = toggle()
        self.closure_collector.toggle = t
        self.closure_collector.toggle2 = t
        sheared = self.closure_collector.shear()
        self.assertEqual(sheared.toggle, not sheared.toggle2)

        assert len(self.closure_collector.dataset().__dict__) == len(
            ShearedBase().__dict__
        )
        assert not self.closure_collector.dataset()
        assert len(self.closure_collector.ruleset().promises) == 2 + len(
            ClosureCollector().promises
        )

    def test_ruleset_rebind(self):
        self.closure_collector.value = 42
        self.closure_collector.reference = attr_reference(
            self.closure_collector, "value"
        )
        assert self.closure_collector.reference == 42
        rs = self.closure_collector.ruleset()
        assert not hasattr(rs, "value")
        with raises(AttributeError):
            assert (
                rs.reference != 42
            ), "Got value rather than expected error resolving reference"
        rs.value = 38
        assert rs.reference == 38


class ClosureCollectorCacheTestCase(unittest.TestCase):
    """
    Tests of the basic operations of a closureCollector
    """

    def setUp(self):
        super().setUp()
        self.closure_collector = ClosureCollector()
        setattr(self.closure_collector, "source", "Original Value")
        setattr(
            self.closure_collector,
            "nested_source",
            ClosureCollector(source="Original Value"),
        )

    def test_nested_cache(self):
        setattr(
            self.closure_collector,
            "dest",
            attr_reference(self.closure_collector, "source"),
        )
        setattr(
            self.closure_collector,
            "nested_dest",
            ClosureCollector(
                dest=attr_reference(self.closure_collector, "nested_source", "source")
            ),
        )
        setattr(
            self.closure_collector,
            "jump_dest",
            FlockDict(
                {
                    "dest": attr_reference(
                        getattr(self.closure_collector, "nested_source"), "source"
                    )
                },
            ),
        )
        assert self.closure_collector.dest == "Original Value"
        assert self.closure_collector.nested_dest.dest == "Original Value"
        setattr(self.closure_collector, "source", "1st New Value")
        assert getattr(self.closure_collector, "dest") == "1st New Value"
        assert getattr(self.closure_collector, "nested_dest").dest == "Original Value"
        assert getattr(self.closure_collector, "jump_dest")["dest"] == "Original Value"
        self.closure_collector.nested_source.source = "2nd New Value"
        assert getattr(self.closure_collector, "dest") == "1st New Value"
        assert getattr(self.closure_collector, "nested_dest").dest == "2nd New Value"
        assert getattr(self.closure_collector, "jump_dest")["dest"] == "2nd New Value"

    def test_split_cache(self):
        self.closure_collector2 = ClosureCollector()
        self.closure_collector2.dest = attr_reference(self.closure_collector, "source")
        self.closure_collector2.nested_dest = ClosureCollector(
            dest=attr_reference(self.closure_collector, "nested_source", "source")
        )

        self.closure_collector2.jump_dest = FlockDict(
            {
                "dest": attr_reference(
                    getattr(self.closure_collector, "nested_source"), "source"
                )
            }
        )
        assert self.closure_collector2.dest == "Original Value"
        assert self.closure_collector2.nested_dest.dest == "Original Value"

        setattr(self.closure_collector, "source", "1st New Value")
        assert getattr(self.closure_collector2, "dest") == "1st New Value"
        assert getattr(self.closure_collector2, "nested_dest").dest == "Original Value"
        assert getattr(self.closure_collector2, "jump_dest")["dest"] == "Original Value"

        self.closure_collector.nested_source.source = "2nd New Value"
        assert self.closure_collector2.dest == "1st New Value"
        assert self.closure_collector2.nested_dest.dest == "2nd New Value"
        assert self.closure_collector2.jump_dest["dest"] == "2nd New Value"


class ShearTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.closure_collector = ClosureCollector()
        setattr(self.closure_collector, "A", "Original Value")
        self.closure_collector.b = ClosureCollector(I="Original value", ii=42)
        setattr(self.closure_collector, "c", [1, 2, 3])
        setattr(self.closure_collector, "d", set("ABC"))
        setattr(self.closure_collector, "e", {"I": "Original value", "ii": 42})

    def test_consistent_types(self):
        for collection in "bcd":
            pre_shear_type = type(getattr(self.closure_collector, collection))
            self.closure_collector.shear()
            post_shear_type = type(getattr(self.closure_collector, collection))
            assert pre_shear_type is post_shear_type

    def test_edit_post_shear(self):
        self.closure_collector.shear()
        self.closure_collector.b.I = "New Value"
        self.closure_collector.e["I"] = "New Value"
        getattr(self.closure_collector, "c").append(4)
        getattr(self.closure_collector, "d").add("D")
        assert getattr(self.closure_collector, "c") == [1, 2, 3, 4]
        assert getattr(self.closure_collector, "b").I == "New Value"
        assert getattr(self.closure_collector, "e")["I"] == "New Value"
        assert "D" in getattr(self.closure_collector, "d")

        setattr(self.closure_collector, "Unreleated", "Something")
        assert getattr(self.closure_collector, "b").I == "New Value"
        assert getattr(self.closure_collector, "e")["I"] == "New Value"
        assert getattr(self.closure_collector, "c") == [1, 2, 3, 4]
        assert "D" in getattr(self.closure_collector, "d")


if __name__ == "__main__":
    unittest.main()
