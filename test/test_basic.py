import pytest

from flock import FlockAggregator, FlockDict, FlockException


def test_flock_basic_usage():
    f = FlockDict()
    f["a"] = 1
    f["b"] = lambda: f["a"] + 1
    assert f["b"] == 2


def test_flock_aggregator_smoke():
    f1 = {"a": 1, "b": 2}
    f2 = {"a": 10, "b": 20}
    agg = FlockAggregator([f1, f2], lambda x: sum(x))
    assert agg["a"] == 11
    assert agg["b"] == 22


def test_flock_exception():
    f = FlockDict()
    f["a"] = lambda: 1 / 0
    with pytest.raises(FlockException):
        _ = f["a"]


def test_flock_check_error_formatting():
    """Verify that check() correctly formats error messages when an exception occurs."""
    f1 = {"a": 1}

    # function that raises exception
    def bad_func(values):
        raise ValueError("Bad value")

    agg = FlockAggregator([f1], bad_func)
    # This should not raise, but return a dict of errors
    errors = agg.check()
    assert "a" in errors
    # Verify the error message contains source and path info
    error_msg = str(errors["a"])
    assert "source 0" in error_msg
    assert "path ['a']" in error_msg
    assert "Bad value" in error_msg
