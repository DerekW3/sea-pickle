import pickle

from src.pickler import merge_partials, partial_pickle


def test_encode_str():
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
    assert partial_pickle(1.0101) in pickle.dumps(1.0101)
    assert partial_pickle(101.5) in pickle.dumps(101.5)


def test_encode_int():
    assert partial_pickle(100) in pickle.dumps(100)
    assert partial_pickle(-100) in pickle.dumps(-100)
    assert partial_pickle(0) in pickle.dumps(0)
    assert partial_pickle(-0) in pickle.dumps(-0)
    assert partial_pickle(100000000) in pickle.dumps(100000000)


def test_encode_bytes():
    assert partial_pickle(b"101010") in pickle.dumps(b"101010")

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
    assert partial_pickle((1, 100)) in pickle.dumps((1, 100))
    assert partial_pickle((1, "a")) in pickle.dumps((1, "a"))
    assert partial_pickle((1, "a", 1.0)) in pickle.dumps((1, "a", 1.0))
    assert partial_pickle((1, "a", 1, 1)) in pickle.dumps((1, "a", 1, 1))


def test_encode_list():
    assert partial_pickle([1, 100]) in pickle.dumps([1, 100])
    assert partial_pickle([1, "a"]) in pickle.dumps([1, "a"])
    assert partial_pickle([1, "a", 1.0]) in pickle.dumps([1, "a", 1.0])
    assert partial_pickle([1, "a", 1, 1, "helloooo"]) in pickle.dumps(
        [1, "a", 1, 1, "helloooo"]
    )


def test_encode_dict():
    assert partial_pickle({1: "hello", 100: "hello"}) in pickle.dumps(
        {1: "hello", 100: "hello"}
    )
    assert partial_pickle({1: "hello", "h": True}) in pickle.dumps(
        {1: "hello", "h": True}
    )


def test_mixed_types():
    assert partial_pickle(([1, 1, "wah"], [True, "hello there"])) in pickle.dumps(
        ([1, 1, "wah"], [True, "hello there"])
    )

    assert partial_pickle({"first": [1, 2, 3]}) in pickle.dumps({"first": [1, 2, 3]})
