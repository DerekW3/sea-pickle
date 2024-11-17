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
    assert partial_pickle([(0,), (1,)]) in pickle.dumps([(0,), (1,)])

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
    assert partial_pickle((1, "text", 3.14)) in pickle.dumps((1, "text", 3.14))


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


def test_encode_int():
    assert merge_partials(partial_pickle(-100), partial_pickle(200)) == pickle.dumps(
        [-100, 200]
    )

    assert merge_partials(partial_pickle(0), partial_pickle(1)) == pickle.dumps([0, 1])

    assert merge_partials(
        partial_pickle(123456789), partial_pickle(987654321)
    ) == pickle.dumps([123456789, 987654321])

    assert merge_partials(partial_pickle(-1), partial_pickle(1)) == pickle.dumps(
        [-1, 1]
    )

    assert merge_partials(partial_pickle(42), partial_pickle(0)) == pickle.dumps(
        [42, 0]
    )

    assert merge_partials(partial_pickle(1000), partial_pickle(2000)) == pickle.dumps(
        [1000, 2000]
    )

    assert merge_partials(partial_pickle(0), partial_pickle(-1)) == pickle.dumps(
        [0, -1]
    )


def test_encode_float():
    assert merge_partials(
        partial_pickle(-1.090934), partial_pickle(10000000.0101)
    ) == pickle.dumps([-1.090934, 10000000.0101])

    assert merge_partials(partial_pickle(0.0), partial_pickle(1.5)) == pickle.dumps(
        [0.0, 1.5]
    )

    assert merge_partials(
        partial_pickle(3.14159), partial_pickle(2.71828)
    ) == pickle.dumps([3.14159, 2.71828])

    assert merge_partials(
        partial_pickle(-100.0), partial_pickle(100.0)
    ) == pickle.dumps([-100.0, 100.0])

    assert merge_partials(partial_pickle(1.0), partial_pickle(0.0)) == pickle.dumps(
        [1.0, 0.0]
    )

    assert merge_partials(
        partial_pickle(1.23456789), partial_pickle(9.87654321)
    ) == pickle.dumps([1.23456789, 9.87654321])

    assert merge_partials(
        partial_pickle(float("inf")), partial_pickle(float("-inf"))
    ) == pickle.dumps([float("inf"), float("-inf")])

    assert merge_partials(
        partial_pickle(float("nan")), partial_pickle(42.0)
    ) == pickle.dumps([float("nan"), 42.0])

    assert merge_partials(partial_pickle(0.1), partial_pickle(0.2)) == pickle.dumps(
        [0.1, 0.2]
    )

    assert merge_partials(partial_pickle(-0.5), partial_pickle(0.5)) == pickle.dumps(
        [-0.5, 0.5]
    )


def test_encode_bytes():
    byte_str1 = b"101010"
    byte_str2 = b"Hello, World!"
    empty_byte_str = b""
    long_byte_str = b"A" * 1000
    special_byte_str = b"\x00\x01\x02\x03"

    assert merge_partials(
        partial_pickle(byte_str1[:3]), partial_pickle(byte_str1[3:])
    ) == pickle.dumps(byte_str1)

    assert merge_partials(
        partial_pickle(byte_str2[:5]), partial_pickle(byte_str2[5:])
    ) == pickle.dumps(byte_str2)

    assert merge_partials(
        partial_pickle(empty_byte_str), partial_pickle(empty_byte_str)
    ) == pickle.dumps(empty_byte_str)

    assert merge_partials(
        partial_pickle(long_byte_str[:500]), partial_pickle(long_byte_str[500:])
    ) == pickle.dumps(long_byte_str)

    assert merge_partials(
        partial_pickle(special_byte_str[:10]), partial_pickle(special_byte_str[10:])
    ) == pickle.dumps(special_byte_str)

    assert merge_partials(
        partial_pickle(b"Byte string with spaces "), partial_pickle(b"and more bytes.")
    ) == pickle.dumps(b"Byte string with spaces and more bytes.")

    assert merge_partials(
        partial_pickle(b"Single"), partial_pickle(b"ByteString")
    ) == pickle.dumps(b"SingleByteString")

    assert merge_partials(
        partial_pickle(b"Leading space"), partial_pickle(b"Trailing space ")
    ) == pickle.dumps(b"Leading spaceTrailing space ")

    assert merge_partials(
        partial_pickle(empty_byte_str), partial_pickle(b"Non-empty")
    ) == pickle.dumps(b"Non-empty")

    assert merge_partials(
        partial_pickle(b"Non-empty"), partial_pickle(empty_byte_str)
    ) == pickle.dumps(b"Non-empty")


def test_encode_tuple():
    assert merge_partials(
        partial_pickle((1, "Yeah man")), partial_pickle((-1, "No man"))
    ) == pickle.dumps([(1, "Yeah man"), (-1, "No man")])

    assert merge_partials(partial_pickle((1,)), partial_pickle((0,))) == pickle.dumps(
        [(1,), (0,)]
    )

    assert merge_partials(
        partial_pickle((1, 2, 3)), partial_pickle((4, 5, 6))
    ) == pickle.dumps([(1, 2, 3), (4, 5, 6)])

    assert merge_partials(
        partial_pickle(("a", "b")), partial_pickle(("c", "d"))
    ) == pickle.dumps([("a", "b"), ("c", "d")])

    assert merge_partials(
        partial_pickle((1, "text", 3.14)), partial_pickle((2, "more text", 2.71))
    ) == pickle.dumps([(1, "text", 3.14), (2, "more text", 2.71)])

    assert merge_partials(
        partial_pickle((None,)), partial_pickle((True,))
    ) == pickle.dumps([(None,), (True,)])

    assert merge_partials(
        partial_pickle((1, (2, 3))), partial_pickle((4, (5, 6)))
    ) == pickle.dumps([(1, (2, 3)), (4, (5, 6))])

    assert merge_partials(
        partial_pickle((1, "single", 1, 2)), partial_pickle(())
    ) == pickle.dumps([(1, "single", 1, 2), ()])

    assert merge_partials(partial_pickle(()), partial_pickle((1, 2))) == pickle.dumps(
        [(), (1, 2)]
    )

    assert merge_partials(
        partial_pickle((1,)), partial_pickle((2, 3, 4))
    ) == pickle.dumps([(1,), (2, 3, 4)])

    assert merge_partials(
        partial_pickle((1, "a", (2, "b"))), partial_pickle((3, "c", (4, "d")))
    ) == pickle.dumps([(1, "a", (2, "b")), (3, "c", (4, "d"))])

    assert merge_partials(
        partial_pickle((1,)), partial_pickle((None,))
    ) == pickle.dumps([(1,), (None,)])

    assert merge_partials(
        partial_pickle((1, 2, 3)), partial_pickle((4, 5))
    ) == pickle.dumps([(1, 2, 3), (4, 5)])

    assert merge_partials(
        partial_pickle((1, "text", (2, "nested"))),
        partial_pickle((3, "more", (4, "deep"))),
    ) == pickle.dumps([(1, "text", (2, "nested")), (3, "more", (4, "deep"))])


def test_encode_dict():
    assert merge_partials(
        partial_pickle({"key1": "value1"}), partial_pickle({"key2": "value2"})
    ) == pickle.dumps([{"key1": "value1"}, {"key2": "value2"}])

    assert merge_partials(
        partial_pickle({"a": 1}), partial_pickle({"b": 2})
    ) == pickle.dumps([{"a": 1}, {"b": 2}])

    assert merge_partials(
        partial_pickle({"x": [1, 2]}), partial_pickle({"y": [3, 4]})
    ) == pickle.dumps([{"x": [1, 2]}, {"y": [3, 4]}])

    assert merge_partials(
        partial_pickle({"name": "Alice", "age": 30}),
        partial_pickle({"city": "Wonderland"}),
    ) == pickle.dumps([{"name": "Alice", "age": 30}, {"city": "Wonderland"}])

    assert merge_partials(
        partial_pickle({"key": None}), partial_pickle({"another_key": True})
    ) == pickle.dumps([{"key": None}, {"another_key": True}])

    assert merge_partials(
        partial_pickle({"nested": {"inner_key": "inner_value"}}),
        partial_pickle({"outer_key": "outer_value"}),
    ) == pickle.dumps(
        [{"nested": {"inner_key": "inner_value"}}, {"outer_key": "outer_value"}]
    )

    assert merge_partials(
        partial_pickle({}), partial_pickle({"only_key": "only_value"})
    ) == pickle.dumps([{}, {"only_key": "only_value"}])

    assert merge_partials(
        partial_pickle({"single": 1}), partial_pickle({})
    ) == pickle.dumps([{"single": 1}, {}])

    assert merge_partials(
        partial_pickle({"a": 1, "b": 2}), partial_pickle({"c": 3, "d": 4})
    ) == pickle.dumps([{"a": 1, "b": 2}, {"c": 3, "d": 4}])

    assert merge_partials(
        partial_pickle({"key1": "value1", "key2": "value2"}),
        partial_pickle({"key3": "value3"}),
    ) == pickle.dumps([{"key1": "value1", "key2": "value2"}, {"key3": "value3"}])

    assert merge_partials(
        partial_pickle({"a": {"b": 2}}), partial_pickle({"c": {"d": 4}})
    ) == pickle.dumps([{"a": {"b": 2}}, {"c": {"d": 4}}])

    assert merge_partials(
        partial_pickle({"list": [1, 2, 3]}),
        partial_pickle({"dict": {"nested_key": "nested_value"}}),
    ) == pickle.dumps([{"list": [1, 2, 3]}, {"dict": {"nested_key": "nested_value"}}])


def test_no_memo():
    assert merge_partials(
        partial_pickle([2, 3, 4]), partial_pickle([5, 6, 7])
    ) == pickle.dumps([[2, 3, 4], [5, 6, 7]])

    assert merge_partials(
        partial_pickle({"a": 1, "b": 2}), partial_pickle({"c": 3, "d": 4})
    ) == pickle.dumps([{"a": 1, "b": 2}, {"c": 3, "d": 4}])

    assert merge_partials(
        partial_pickle([[1, 2], [3, 4]]),
        partial_pickle([[5, 6], [7, 8]]),
    ) == pickle.dumps([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])

    assert merge_partials(
        partial_pickle([1, 2.5, 3]), partial_pickle([4.0, 5, 6])
    ) == pickle.dumps([[1, 2.5, 3], [4.0, 5, 6]])

    assert merge_partials(
        partial_pickle(b"foo"), partial_pickle(b"bar")
    ) == pickle.dumps(b"foobar")

    assert merge_partials(partial_pickle(42), partial_pickle(3.14)) == pickle.dumps(
        [42, 3.14]
    )
