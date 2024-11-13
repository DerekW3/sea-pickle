import pickle
from typing import Callable

import sea_pickle

partial_pickle: Callable = sea_pickle.partial_pickle


def test_partial_pickle():
    # assert partial_pickle(None) == b"N"
    # assert partial_pickle(True) == b"\x88"
    # assert partial_pickle(False) == b"\x89"
    # assert partial_pickle("hello") in pickle.dumps("hello")
    # assert partial_pickle(b"hello") in pickle.dumps(b"hello")
    # assert partial_pickle(1) in pickle.dumps(1)
    # assert partial_pickle(100000000) in pickle.dumps(100000000)
    # assert partial_pickle(-100) in pickle.dumps(-100)
    # assert partial_pickle(1.05) in pickle.dumps(1.05)
    # assert partial_pickle(-1.05) in pickle.dumps(-1.05)

    # assert partial_pickle("hello there") in pickle.dumps("hello there")
    # assert partial_pickle("hi my name is") in pickle.dumps("hi my name is")
    # multiline_str = """
    # This is a multiline string
    # which tests my pickles capability to encode
    # unicode characters like the newline
    # """
    # assert partial_pickle(multiline_str) in pickle.dumps(multiline_str)
    # assert partial_pickle("") in pickle.dumps("")
    # assert partial_pickle("a" * 255) in pickle.dumps("a" * 255)
    # assert partial_pickle("a" * 256) in pickle.dumps("a" * 256)

    # assert partial_pickle(1.0101) in pickle.dumps(1.0101)
    # assert partial_pickle(101.5) in pickle.dumps(101.5)

    # assert partial_pickle(100) in pickle.dumps(100)
    # assert partial_pickle(-100) in pickle.dumps(-100)
    # assert partial_pickle(0) in pickle.dumps(0)
    # assert partial_pickle(-0) in pickle.dumps(-0)
    # assert partial_pickle(100000000) in pickle.dumps(100000000)

    # assert partial_pickle((1, 100)) in pickle.dumps((1, 100))
    # assert partial_pickle((1, "a")) in pickle.dumps((1, "a"))
    # assert partial_pickle((1, "a", 1.0)) in pickle.dumps((1, "a", 1.0))
    # assert partial_pickle((1, "a", 1, 1)) in pickle.dumps((1, "a", 1, 1))

    assert partial_pickle([1, 100]) in pickle.dumps([1, 100])
    assert partial_pickle([1, "a"]) in pickle.dumps([1, "a"])
    assert partial_pickle([1, "a", 1.0]) in pickle.dumps([1, "a", 1.0])
    assert partial_pickle([1, "a", 1, 1, "helloooo"]) in pickle.dumps(
        [1, "a", 1, 1, "helloooo"]
    )
