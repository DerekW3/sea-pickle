from itertools import islice
from struct import pack
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from .opcodes.opcodes import OPCODE

codes = OPCODE()

NonMemoizedFunction = Callable[[Any], bytes]
MemoizedFunction = Callable[[Dict[Any, Any], Any], bytes]

disbatch_table_memo: Dict[Type[Any], MemoizedFunction] = {}
disbatch_table_no_memo: Dict[Type[Any], NonMemoizedFunction] = {}


def partial_pickle(obj: Any, memory: Optional[Dict[Any, Any]] = None) -> bytes:
    pickled_obj = b""

    memory = memory or {}

    if id(obj) in memory:
        return get(memory[id(obj)][0])

    obj_type: Any = type(obj)

    if obj_type in disbatch_table_memo:
        func = disbatch_table_memo[obj_type]
        pickled_obj += func(memory, obj)
    elif obj_type in disbatch_table_no_memo:
        func = disbatch_table_no_memo[obj_type]
        pickled_obj += func(obj)

    return pickled_obj


def merge_partials(obj1: bytes, obj2: bytes) -> bytes:
    result = b""
    identifier_1 = obj1[:1] if len(obj1) else b""
    identifier_2 = obj2[:1] if len(obj2) else b""

    match (identifier_1, identifier_2):
        case (b"\x8c" | b"X" | b"\x8d", b"\x8c" | b"X" | b"\x8d"):
            result = merge_strings(obj1, identifier_1, obj2, identifier_2)
        case (
            b"J"
            | b"K"
            | b"\x8a"
            | b"\x8b"
            | b"G",
            b"J"
            | b"K"
            | b"\x8a"
            | b"\x8b"
            | b"G",
        ):
            print("Two numerics found")
        case (b"\x8e" | b"B" | b"C", b"\x8e" | b"B" | b"C"):
            print("bytes detected")
        case (b"}" | b"]" | b")" | b"(", b"}" | b"]" | b")" | b"("):
            print("sequence identified")
        case (b"", b""):
            raise ValueError("Invalid Input: Un-mergable objects")
        case (_, b"") | (b"", _):
            print("single item wrapping")
        case _:
            # TODO: merge into a list
            print("2 objects found")

    frame_bytes = b"\x95" + pack("<Q", len(result)) if len(result) >= 4 else b""
    return b"\x80\x04" + frame_bytes + result


def length_packer(length: int) -> bytes:
    if length < 256:
        return pack("<B", length)
    elif length > 0xFFFFFFFF:
        return pack("<Q", length)
    else:
        return pack("<I", length)


def merge_strings(
    str_1: bytes, identifier_1: bytes, str_2: bytes, identifier_2: bytes
) -> bytes:
    result = b""
    len_bytes_1 = 1 if identifier_1 == b"\x8c" else 4 if identifier_1 == b"X" else 8
    len_bytes_2 = 1 if identifier_2 == b"\x8c" else 4 if identifier_2 == b"X" else 8

    maintain_one = str_1[len_bytes_1 + 1 : -1]
    maintain_two = str_2[len_bytes_2 + 1 : -1]

    result = maintain_one + maintain_two + codes.MEMO
    identifier = (
        b"\x8c"
        if len(maintain_one + maintain_two) < 256
        else b"X"
        if len(maintain_one + maintain_two) <= 0xFFFFFFFF
        else b"\x8d"
    )

    return (
        identifier
        + length_packer(len(maintain_one) + len(maintain_two))
        + result
        + b"."
    )


def memoize(memory: Dict[Any, Any], obj: Any) -> bytes:
    memory[id(obj)] = len(memory), obj

    return codes.MEMO


def get(idx: int) -> bytes:
    if idx < 256:
        return codes.BINGET + pack("<B", idx)
    else:
        return codes.LONG_BINGET + pack("<I", idx)


def encode_none(obj: None) -> bytes:
    if obj is None:
        return codes.NONE


disbatch_table_no_memo[type(None)] = encode_none


def encode_bool(obj: bool) -> bytes:
    return codes.TRUE if obj else codes.FALSE


disbatch_table_no_memo[bool] = encode_bool


def encode_string(memory: Dict[Any, Any], obj: str) -> bytes:
    res = b""
    utf_string: bytes = obj.encode("utf-8", "surrogatepass")
    length: int = len(utf_string)
    if length < 256:
        res += codes.SHORT_UNICODE + pack("<B", length) + utf_string
    elif length > 0xFFFFFFFF:
        res += codes.LONG_UNICODE + pack("<Q", length) + utf_string
    else:
        res += codes.UNICODE + pack("<I", length) + utf_string

    res += memoize(memory, obj)

    return res


disbatch_table_memo[str] = encode_string


def encode_float(obj: float) -> bytes:
    return codes.BINFLOAT + pack(">d", obj)


disbatch_table_no_memo[float] = encode_float


def encode_long(obj: int) -> bytes:
    if obj >= 0:
        if obj <= 0xFF:
            return codes.BININT1 + pack("<B", obj)
        elif obj <= 0xFFFF:
            return codes.BININT2 + pack("<H", obj)

    if -0x80000000 <= obj <= 0x7FFFFFFF:
        return codes.BININT + pack("<i", obj)

    encoded_long: bytes = b""

    if obj != 0:
        num_bytes: int = (obj.bit_length() >> 3) + 1

        encoded_long = obj.to_bytes(num_bytes, byteorder="little", signed=True)

        if (
            obj < 0
            and num_bytes > 1
            and (encoded_long[-1] == 0xFF and (encoded_long[-2] & 0x80) != 0)
        ):
            encoded_long = encoded_long[:-1]

    n = len(encoded_long)

    if n < 256:
        return codes.LONG1 + pack("<B", n) + encoded_long
    else:
        return codes.LONG4 + pack("<i", n) + encoded_long


disbatch_table_no_memo[int] = encode_long


def encode_bytes(memory: Dict[Any, Any], obj: bytes) -> bytes:
    res = b""
    n = len(obj)

    if n < 256:
        res += codes.SHORT_BINBYTES + pack("<B", n) + obj
    elif n > 0xFFFFFFFF:
        res += codes.BINBYTES8 + pack("<Q", n) + obj
    else:
        res += codes.BINBYTES + pack("<I", n) + obj

    res += memoize(memory, obj)

    return res


disbatch_table_memo[bytes] = encode_bytes


def add_batch(memory: Dict[Any, Any], items: Any) -> bytes:
    it = iter(items)

    result = b""

    while True:
        temp = list(islice(it, 1000))

        n = len(temp)

        if n > 1:
            result += codes.MARK
            for itm in temp:
                result += partial_pickle(itm, memory)
            result += codes.APPENDS
        elif n:
            result += partial_pickle(temp[0], memory)
            result += codes.APPEND

        if n < 1000:
            return result


def set_batch(memory: Dict[Any, Any], items: Any) -> bytes:
    it = iter(items)

    result = b""

    while True:
        temp = list(islice(it, 1000))

        n = len(temp)

        if n > 1:
            result += codes.MARK
            for key, value in temp:
                result += partial_pickle(key, memory)
                result += partial_pickle(value, memory)
            result += codes.SETITEMS
        elif n:
            key, value = temp[0]
            result += partial_pickle(key, memory)
            result += partial_pickle(value, memory)
            result += codes.SETITEM

        if n < 1000:
            return result


def encode_tuple(memory: Dict[Any, Any], obj: Tuple[Any, ...]) -> bytes:
    res = b""

    if not obj:
        res += codes.EMPTY_TUPLE

    if id(obj) in memory:
        return get(memory[id(obj)][0])

    res += codes.MARK

    for itm in obj:
        res += partial_pickle(itm)

    if len(obj) <= 3:
        match len(obj):
            case 1:
                res += codes.TUPLE1
            case 2:
                res += codes.TUPLE2
            case _:
                res += codes.TUPLE3
    else:
        res += codes.TUPLE

    res += memoize(memory, obj)

    return res


disbatch_table_memo[tuple] = encode_tuple


def encode_list(memory: Dict[Any, Any], obj: List[Any]) -> bytes:
    res = b""

    res += codes.EMPTY_LIST

    res += memoize(memory, obj)

    res += add_batch(memory, obj)

    return res


disbatch_table_memo[list] = encode_list


def encode_dict(memory: Dict[Any, Any], obj: Dict[Any, Any]) -> bytes:
    res = b""

    res += codes.EMPTY_DICT

    res += memoize(memory, obj)

    res += set_batch(memory, obj.items())

    return res


disbatch_table_memo[dict] = encode_dict
