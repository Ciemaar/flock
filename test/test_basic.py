import pytest
from flock import FlockDict, Aggregator, FlockAggregator, FlockException

def test_flock_basic_usage():
    f = FlockDict()
    f['a'] = 1
    f['b'] = lambda: f['a'] + 1
    assert f['b'] == 2

def test_flock_aggregator_smoke():
    f1 = {'a': 1, 'b': 2}
    f2 = {'a': 10, 'b': 20}
    agg = FlockAggregator([f1, f2], lambda x: sum(x))
    assert agg['a'] == 11
    assert agg['b'] == 22

def test_flock_exception():
    f = FlockDict()
    f['a'] = lambda: 1/0
    with pytest.raises(FlockException):
        _ = f['a']
