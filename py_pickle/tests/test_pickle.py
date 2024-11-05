import pickle

from src.pickler import partial_dump


def test_encode_str():
    assert partial_dump("hello there") in pickle.dumps("hello there")
    assert partial_dump("hi my name is") in pickle.dumps("hi my name is")
    multiline_str = """
    This is a multiline string
    which tests my pickles capability to encode
    unicode characters like the newline
    """
    assert partial_dump(multiline_str) in pickle.dumps(multiline_str)
    assert partial_dump("") in pickle.dumps("")
    assert partial_dump("a" * 255) in pickle.dumps("a" * 255)
    assert partial_dump("a" * 256) in pickle.dumps("a" * 256)


def test_encode_float():
    assert partial_dump(1.0101) in pickle.dumps(1.0101)
    assert partial_dump(101.5) in pickle.dumps(101.5)


def test_encode_int():
    assert partial_dump(100) in pickle.dumps(100)
    assert partial_dump(-100) in pickle.dumps(-100)
    assert partial_dump(0) in pickle.dumps(0)
    assert partial_dump(-0) in pickle.dumps(-0)
    assert partial_dump(100000000) in pickle.dumps(100000000)


def test_encode_bytes():
    assert partial_dump(b"101010") in pickle.dumps(b"101010")


def test_encode_tuple():
    assert partial_dump((1, 100)) in pickle.dumps((1, 100))
    assert partial_dump((1, "a")) in pickle.dumps((1, "a"))
    assert partial_dump((1, "a", 1.0)) in pickle.dumps((1, "a", 1.0))
    assert partial_dump((1, "a", 1, 1)) in pickle.dumps((1, "a", 1, 1))


def test_encode_list():
    assert partial_dump([1, 100]) in pickle.dumps([1, 100])
    assert partial_dump([1, "a"]) in pickle.dumps([1, "a"])
    assert partial_dump([1, "a", 1.0]) in pickle.dumps([1, "a", 1.0])
    assert partial_dump([1, "a", 1, 1, "helloooo"]) in pickle.dumps(
        [1, "a", 1, 1, "helloooo"]
    )


def test_encode_dict():
    assert partial_dump({1: "hello", 100: "hello"}) in pickle.dumps(
        {1: "hello", 100: "hello"}
    )
    assert partial_dump({1: "hello", "h": True}) in pickle.dumps(
        {1: "hello", "h": True}
    )


def test_mixed_types():
    assert partial_dump(([1, 1, "wah"], [True, "hello there"])) in pickle.dumps(
        ([1, 1, "wah"], [True, "hello there"])
    )

    assert partial_dump({"first": [1, 2, 3]}) in pickle.dumps({"first": [1, 2, 3]})
