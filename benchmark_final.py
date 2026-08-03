import time
from collections import defaultdict
from flock.core import FlockAggregator, Aggregator

def dummy_func(vals):
    return True

sources = [{i: i for i in range(j, j+1000)} for j in range(0, 10000, 100)]

def benchmark_aggregator():
    agg = Aggregator(sources, dummy_func)
    start = time.time()
    for _ in range(10):
        agg.check()
    end = time.time()
    print(f"Aggregator Baseline (10 runs): {end - start:.4f} seconds")

def benchmark_flock_aggregator():
    agg = FlockAggregator(sources, dummy_func)
    start = time.time()
    for _ in range(10):
        agg.check()
    end = time.time()
    print(f"FlockAggregator Baseline (10 runs): {end - start:.4f} seconds")

if __name__ == "__main__":
    benchmark_aggregator()
    benchmark_flock_aggregator()
