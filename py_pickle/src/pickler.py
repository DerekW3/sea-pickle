from itertools import islice
from struct import pack
from typing import Any

from .opcodes.opcodes import OPCODE

codes = OPCODE()


def partial_dump(obj: Any) -> bytes:
    pickled_obj = b""

    memo = {}

    if obj is None:
        pickled_obj += encode_none()
    elif isinstance(obj, bool):
        pickled_obj += encode_bool(obj)
    elif isinstance(obj, str):
        pickled_obj += encode_string(obj)
    elif isinstance(obj, float):
        pickled_obj += encode_float(obj)
    elif isinstance(obj, int):
        pickled_obj += encode_long(obj)
    elif isinstance(obj, bytes):
        pickled_obj += encode_bytes(obj)
    elif isinstance(obj, bytearray):
        pickled_obj += encode_bytearray(obj)
    elif isinstance(obj, tuple):
        pickled_obj += encode_tuple(obj)  # type: ignore
    elif isinstance(obj, list):
        pickled_obj += encode_list(obj)  # type: ignore
    elif isinstance(obj, dict):
        pickled_obj += encode_dict(obj)  # type: ignore
    elif isinstance(obj, set):
        pickled_obj += encode_set(obj)  # type: ignore

    return pickled_obj


def memoize(memory: dict[Any, Any], obj: Any) -> bytes:
    memory[id(obj)] = len(memory), obj

    return codes.MEMO


def encode_none() -> bytes:
    return codes.NONE


def encode_bool(obj: bool) -> bytes:
    return codes.TRUE if obj else codes.FALSE


def encode_string(memory: dict[Any, Any], obj: str) -> bytes:
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


def encode_float(obj: float) -> bytes:
    return codes.BINFLOAT + pack(">d", obj)


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


def encode_bytes(memory: dict[Any, Any], obj: bytes) -> bytes:
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


def encode_bytearray(obj: bytearray) -> bytes:
    return codes.BYTEARRAY + pack("<Q", len(obj)) + obj


def add_batch(items: Any) -> bytes:
    it = iter(items)

    result = b""

    while True:
        temp = list(islice(it, 1000))

        n = len(temp)

        if n > 1:
            result += codes.MARK
            for itm in temp:
                result += partial_dump(itm)
            result += codes.APPENDS
        elif n:
            result += partial_dump(temp[0])
            result += codes.APPEND

        if n < 1000:
            return result


def set_batch(items: Any) -> bytes:
    it = iter(items)

    result = b""

    while True:
        temp = list(islice(it, 1000))

        n = len(temp)

        if n > 1:
            result += codes.MARK
            for key, value in temp:
                result += partial_dump(key)
                result += partial_dump(value)
            result += codes.SETITEMS
        elif n:
            key, value = temp[0]
            result += partial_dump(key)
            result += partial_dump(value)
            result += codes.SETITEM

        if n < 1000:
            return result


def encode_tuple(memory: dict[Any, Any], obj: tuple[Any]) -> bytes:
    res = b""

    if not obj:
        res += codes.EMPTY_TUPLE

    if id(obj) in memory:
        return memory[id(obj)]

    if len(obj) <= 3:
        res += codes.MARK

    for itm in obj:
        res += partial_dump(itm)

    res += codes.TUPLE

    res += memoize(memory, obj)

    return res


def encode_list(memory: dict[Any, Any], obj: list[Any]) -> bytes:
    res = b""

    res += codes.EMPTY_TUPLE

    res += memoize(memory, obj)

    res += add_batch(obj)

    return res


def encode_dict(memory: dict[Any, Any], obj: dict[Any, Any]) -> bytes:
    res = b""

    res += codes.EMPTY_DICT

    res += memoize(memory, obj)

    res += set_batch(obj.items())

    return res


def encode_set(obj: set[Any]) -> bytes:
    res = b""

    res += codes.EMPTY_SET

    it = iter(obj)
    while True:
        batch = list(islice(it, 1000))

        n = len(batch)

        if n > 0:
            res += codes.MARK
            for itm in batch:
                res += partial_dump(itm)
        if n < 1000:
            return res
