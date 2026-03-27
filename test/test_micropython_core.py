from flock.core import FlockDict


def test_flockdict_basic():
    my_flock = FlockDict()
    my_flock["a"] = 10
    my_flock["b"] = 20
    my_flock["c"] = lambda: my_flock["a"] + my_flock["b"]

    assert my_flock["a"] == 10
    assert my_flock["b"] == 20
    assert my_flock["c"] == 30


def test_flockdict_nested():
    my_flock = FlockDict()
    my_flock["nested"] = {"a": 1}
    my_flock["derived"] = lambda: my_flock["nested"]["a"] + 1

    assert my_flock["nested"]["a"] == 1
    assert my_flock["derived"] == 2


def test_flockdict_update():
    my_flock = FlockDict()
    my_flock["a"] = 1
    my_flock["b"] = lambda: my_flock["a"] * 2

    assert my_flock["b"] == 2
    my_flock["a"] = 5
    assert my_flock["b"] == 10


def run_all_tests():
    tests = [test_flockdict_basic, test_flockdict_nested, test_flockdict_update]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
            print(f"PASS: {test.__name__}")
        except Exception as e:
            failed += 1
            print(f"FAIL: {test.__name__}")
            try:
                import sys

                sys.print_exception(e)
            except Exception:
                print(e)

    print(f"\nResults: {passed} passed, {failed} failed")
    if failed > 0:
        import sys

        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
