import pickle

from src.pickler import partial_dump


def test_encode_str():
    assert partial_dump("hello there") in pickle.dumps("hello there")


def test_encode_float():
    assert partial_dump(1.0101) in pickle.dumps(1.0101)


def test_encode_int():
    assert partial_dump(100) in pickle.dumps(100)


def test_encode_bytes():
    assert partial_dump(b"101010") in pickle.dumps(b"101010")


def test_encode_tuple():
    assert partial_dump((1, 100)) in pickle.dumps((1, 100))
    assert partial_dump((1, "a")) in pickle.dumps((1, "a"))


def test_encode_list():
    assert partial_dump([1, 100]) in pickle.dumps([1, 100])
    assert partial_dump([1, "a"]) in pickle.dumps([1, "a"])


def test_encode_dict():
    assert partial_dump({1: "hello", 100: "hello"}) in pickle.dumps(
        {1: "hello", 100: "hello"}
    )
    assert partial_dump({1: "hello", "h": True}) in pickle.dumps(
        {1: "hello", "h": True}
    )
