import pickle
from typing import Callable

import sea_pickle

partial_pickle: Callable = sea_pickle.partial_pickle
merge_partials: Callable = sea_pickle.merge_partials


def test_partial_pickle():
    assert partial_pickle(None) == b"N"
    assert partial_pickle(True) == b"\x88"
    assert partial_pickle(False) == b"\x89"
    assert partial_pickle("hello") in pickle.dumps("hello")
    assert partial_pickle(b"hello") in pickle.dumps(b"hello")
    assert partial_pickle(1) in pickle.dumps(1)
    assert partial_pickle(100000000) in pickle.dumps(100000000)
    assert partial_pickle(-100) in pickle.dumps(-100)
    assert partial_pickle(1.05) in pickle.dumps(1.05)
    assert partial_pickle(-1.05) in pickle.dumps(-1.05)

    assert partial_pickle("hello there") in pickle.dumps("hello there")
    assert partial_pickle("hi my name is") in pickle.dumps("hi my name is")
    multiline_str = """
    This is a multiline string
    which tests my pickles capability to encode
    unicode characters like the newline
    """
    assert partial_pickle(multiline_str) in pickle.dumps(multiline_str)
    assert partial_pickle("") in pickle.dumps("")
    assert partial_pickle("a" * 255) in pickle.dumps("a" * 255)
    assert partial_pickle("a" * 256) in pickle.dumps("a" * 256)

    assert partial_pickle(1.0101) in pickle.dumps(1.0101)
    assert partial_pickle(101.5) in pickle.dumps(101.5)

    assert partial_pickle(100) in pickle.dumps(100)
    assert partial_pickle(-100) in pickle.dumps(-100)
    assert partial_pickle(0) in pickle.dumps(0)
    assert partial_pickle(-0) in pickle.dumps(-0)
    assert partial_pickle(100000000) in pickle.dumps(100000000)

    assert partial_pickle((1, 100)) in pickle.dumps((1, 100))
    assert partial_pickle((1, "a")) in pickle.dumps((1, "a"))
    assert partial_pickle((1, "a", 1.0)) in pickle.dumps((1, "a", 1.0))
    assert partial_pickle((1, "a", 1, 1)) in pickle.dumps((1, "a", 1, 1))

    assert partial_pickle([1, 100]) in pickle.dumps([1, 100])
    assert partial_pickle([1, "a"]) in pickle.dumps([1, "a"])
    assert partial_pickle([1, "a", 1.0]) in pickle.dumps([1, "a", 1.0])
    assert partial_pickle([1, "a", 1, 1, "helloooo"]) in pickle.dumps(
        [1, "a", 1, 1, "helloooo"]
    )


def test_encode_str():
    multiline_str = """
    This is a multiline string
    which tests my pickles capability to encode
    unicode characters like the newline
    """
    long_str = "A" * 1000
    special_char_str = "!@#$%^&*()_+[]{}|;:',.<>?/~`"
    assert merge_partials(
        partial_pickle(multiline_str[:100]), partial_pickle(multiline_str[100:])
    ) == pickle.dumps(multiline_str)

    assert merge_partials(partial_pickle(""), partial_pickle("")) == pickle.dumps("")

    assert merge_partials(
        partial_pickle(long_str[:500]), partial_pickle(long_str[500:])
    ) == pickle.dumps(long_str)

    assert merge_partials(
        partial_pickle(special_char_str[:10]), partial_pickle(special_char_str[10:])
    ) == pickle.dumps(special_char_str)

    assert merge_partials(
        partial_pickle("Test string with spaces"), partial_pickle(" and more text.")
    ) == pickle.dumps("Test string with spaces and more text.")

    assert merge_partials(
        partial_pickle("Single"), partial_pickle("String")
    ) == pickle.dumps("SingleString")

    assert merge_partials(
        partial_pickle("Leading space"), partial_pickle("Trailing space ")
    ) == pickle.dumps("Leading spaceTrailing space ")
