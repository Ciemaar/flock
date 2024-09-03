from closure_collector.tags import AttributeTagset


class TestObj:
    class_attr = "test_class_attr"

    def __init__(self):
        self.instance_attr = "test_instance_attr"


def test_empty_tagset():
    tagset = AttributeTagset(None)
    assert not tagset
    assert 0 == len(tagset)

    # For consideration
    # assert not tagset["test"]
    # assert 0 == len(tagset["test"])

    tagset["test"].add(".test")
    assert tagset
    assert 1 == len(tagset)
    assert tagset["test"]
    assert 1 == len(tagset["test"])

    tagset["test"].remove(".test")
    assert tagset
    assert 1 == len(tagset)
    assert not tagset["test"]
    assert 0 == len(tagset["test"])

    del tagset["test"]
    assert not tagset
    assert 0 == len(tagset)


def test_basic_tagset():
    test_obj = TestObj()
    tagset = AttributeTagset(test_obj)
    assert not tagset
    assert 0 == len(tagset)

    tagset["test"].add("class_attr")
    assert tagset
    assert 1 == len(tagset)
    assert tagset["test"]
    assert 1 == len(tagset["test"])
    for t in tagset["test"]:
        assert t == test_obj.class_attr == "test_class_attr"

    tagset["test"].add("class_attr")
    assert tagset
    assert 1 == len(tagset)
    assert tagset["test"]
    assert 1 == len(tagset["test"])
    for t in tagset["test"]:
        assert t == test_obj.class_attr == "test_class_attr"

    tagset["test"].add("instance_attr")
    assert tagset
    assert 1 == len(tagset)
    assert tagset["test"]
    assert 2 == len(tagset["test"])
    for t in tagset["test"]:
        assert t in {
            test_obj.class_attr,
            "test_class_attr",
            test_obj.instance_attr,
            "test_instance_attr",
        }

    tagset["test"].remove("class_attr")
    assert tagset
    assert 1 == len(tagset)
    assert tagset["test"]
    assert 1 == len(tagset["test"])
    for t in tagset["test"]:
        assert t == test_obj.instance_attr == "test_instance_attr"
