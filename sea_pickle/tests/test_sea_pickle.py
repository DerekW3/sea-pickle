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
    assert partial_pickle(-1.090934) in pickle.dumps(-1.090934)

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


def test_encode_float():
    assert merge_partials(
        partial_pickle(-1.090934), partial_pickle(10000000.0101), False, True
    ) == pickle.dumps([-1.090934, 10000000.0101])

    # assert merge_partials(partial_pickle(0.0), partial_pickle(1.5)) == pickle.dumps(
    #     [0.0, 1.5]
    # )

    # assert merge_partials(
    #     partial_pickle(3.14159), partial_pickle(2.71828)
    # ) == pickle.dumps([3.14159, 2.71828])

    # assert merge_partials(
    #     partial_pickle(-100.0), partial_pickle(100.0)
    # ) == pickle.dumps([-100.0, 100.0])

    # assert merge_partials(partial_pickle(1.0), partial_pickle(0.0)) == pickle.dumps(
    #     [1.0, 0.0]
    # )

    # assert merge_partials(
    #     partial_pickle(1.23456789), partial_pickle(9.87654321)
    # ) == pickle.dumps([1.23456789, 9.87654321])

    # assert merge_partials(
    #     partial_pickle(float("inf")), partial_pickle(float("-inf"))
    # ) == pickle.dumps([float("inf"), float("-inf")])

    # assert merge_partials(
    #     partial_pickle(float("nan")), partial_pickle(42.0)
    # ) == pickle.dumps([float("nan"), 42.0])

    # assert merge_partials(partial_pickle(0.1), partial_pickle(0.2)) == pickle.dumps(
    #     [0.1, 0.2]
    # )

    # assert merge_partials(partial_pickle(-0.5), partial_pickle(0.5)) == pickle.dumps(
    #     [-0.5, 0.5]
    # )


def test_no_memo():
    assert merge_partials(
        partial_pickle([1, 1, 1]), partial_pickle([1, 1, 1]), True, True
    ) == pickle.dumps([[1, 1, 1], [1, 1, 1]])

    assert merge_partials(
        partial_pickle([2, 3, 4]), partial_pickle([5, 6, 7]), True, True
    ) == pickle.dumps([[2, 3, 4], [5, 6, 7]])

    assert merge_partials(
        partial_pickle({"a": 1, "b": 2}), partial_pickle({"c": 3, "d": 4}), True, True
    ) == pickle.dumps([{"a": 1, "b": 2}, {"c": 3, "d": 4}])

    assert merge_partials(
        partial_pickle([[1, 2], [3, 4]]),
        partial_pickle([[5, 6], [7, 8]]),
        True,
        True,
    ) == pickle.dumps([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])

    assert merge_partials(
        partial_pickle([1, 2.5, 3]), partial_pickle([4.0, 5, 6]), True
    ) == pickle.dumps([[1, 2.5, 3], [4.0, 5, 6]])

    assert merge_partials(
        partial_pickle(b"foo"), partial_pickle(b"bar"), True
    ) == pickle.dumps(b"foobar")

    assert merge_partials(
        partial_pickle(42), partial_pickle(3.14), True
    ) == pickle.dumps([42, 3.14])
