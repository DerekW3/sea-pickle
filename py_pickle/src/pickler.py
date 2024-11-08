from itertools import islice
from struct import pack
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from .opcodes.opcodes import OPCODE

codes = OPCODE()


class Memo:
    def __init__(self) -> None:
        self.memory: dict[Any, Any] = {}

    def __repr__(self) -> str:
        return str(self.memory)

    def __getitem__(self, obj: Any) -> Any:
        return self.memory[id(obj)][0]

    def __contains__(self, obj: Any) -> bool:
        return id(obj) in self.memory

    def memoize(self, obj: Any) -> bytes:
        self.memory[id(obj)] = len(self.memory) + 1, obj

        return codes.MEMO


NonMemoizedFunction = Callable[[Any], bytes]
MemoizedFunction = Callable[[Memo, Any], bytes]

disbatch_table_memo: Dict[Type[Any], MemoizedFunction] = {}
disbatch_table_no_memo: Dict[Type[Any], NonMemoizedFunction] = {}


def partial_pickle(obj: Any, memory: Optional[Memo] = None) -> bytes:
    pickled_obj = b""

    memory = memory or Memo()

    if obj in memory:
        return get(memory[obj])

    obj_type: Any = type(obj)

    if obj_type in disbatch_table_memo:
        func = disbatch_table_memo[obj_type]
        pickled_obj += func(memory, obj)
    elif obj_type in disbatch_table_no_memo:
        func = disbatch_table_no_memo[obj_type]
        pickled_obj += func(obj)

    print(memory)

    return pickled_obj


def merge_partials(obj1: bytes, obj2: bytes) -> bytes:
    result = b""
    identifier_1 = obj1[:1] if len(obj1) else b""
    identifier_2 = obj2[:1] if len(obj2) else b""
    identifier_1_count = obj1.count(
        identifier_1
    )  # tuples can be unmarked and thus they need to be determined from a string in some way
    identifier_2_count = obj2.count(identifier_2)

    # TODO: ADD checks for memoization when similar elements are shared

    match (identifier_1, identifier_1_count, identifier_2, identifier_2_count):
        case (b"\x8c" | b"X" | b"\x8d", 1, b"\x8c" | b"X" | b"\x8d", 1):
            result = merge_strings(obj1, identifier_1, obj2, identifier_2)
        case (b"\x8e" | b"B" | b"C", 1, b"\x8e" | b"B" | b"C", 1):
            result = merge_bytes(obj1, identifier_1, obj2, identifier_2)
        case (b"", _, b"", _):
            raise ValueError("Invalid Input: Un-mergable objects")
        case (b"", *_) | (*_, b"", _):
            result = (obj1 or obj2) + b"."
        case _:
            temp_memo = {}
            split_obj_1 = obj1.split(codes.MEMO)

            print(split_obj_1)
            print(obj1, "---------->", obj2)
            result = (
                codes.EMPTY_LIST
                + codes.MEMO
                + codes.MARK
                + obj1
                + obj2
                + codes.APPENDS
                + b"."
            )

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
        codes.SHORT_UNICODE
        if len(maintain_one + maintain_two) < 256
        else codes.UNICODE
        if len(maintain_one + maintain_two) <= 0xFFFFFFFF
        else codes.LONG_UNICODE
    )

    return (
        identifier
        + length_packer(len(maintain_one) + len(maintain_two))
        + result
        + b"."
    )


def merge_bytes(
    byte_str_1: bytes, identifier_1: bytes, byte_str_2: bytes, identifier_2: bytes
) -> bytes:
    result = b""
    len_bytes_1 = (
        1
        if identifier_1 == codes.SHORT_BINBYTES
        else 4
        if identifier_1 == codes.BINBYTES
        else 8
    )
    len_bytes_2 = (
        1
        if identifier_2 == codes.SHORT_BINBYTES
        else 4
        if identifier_2 == codes.BINBYTES
        else 8
    )

    maintain_one = byte_str_1[len_bytes_1 + 1 : -1]
    maintain_two = byte_str_2[len_bytes_2 + 1 : -1]

    result = maintain_one + maintain_two + codes.MEMO
    identifier = (
        codes.SHORT_BINBYTES
        if len(maintain_one + maintain_two) < 256
        else codes.BINBYTES
        if len(maintain_one + maintain_two) <= 0xFFFFFFFF
        else codes.BINBYTES8
    )

    return (
        identifier
        + length_packer(len(maintain_one) + len(maintain_two))
        + result
        + b"."
    )


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


def encode_string(memory: Memo, obj: str) -> bytes:
    res = b""
    utf_string: bytes = obj.encode("utf-8", "surrogatepass")
    length: int = len(utf_string)
    if length < 256:
        res += codes.SHORT_UNICODE + pack("<B", length) + utf_string
    elif length > 0xFFFFFFFF:
        res += codes.LONG_UNICODE + pack("<Q", length) + utf_string
    else:
        res += codes.UNICODE + pack("<I", length) + utf_string

    res += memory.memoize(obj)

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


def encode_bytes(memory: Memo, obj: bytes) -> bytes:
    res = b""
    n = len(obj)

    if n < 256:
        res += codes.SHORT_BINBYTES + pack("<B", n) + obj
    elif n > 0xFFFFFFFF:
        res += codes.BINBYTES8 + pack("<Q", n) + obj
    else:
        res += codes.BINBYTES + pack("<I", n) + obj

    res += memory.memoize(obj)

    return res


disbatch_table_memo[bytes] = encode_bytes


def add_batch(memory: Memo, items: Any) -> bytes:
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


def set_batch(memory: Memo, items: Any) -> bytes:
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


def encode_tuple(memory: Memo, obj: Tuple[Any, ...]) -> bytes:
    res = b""

    if not obj:
        return codes.EMPTY_TUPLE

    if obj in memory:
        return get(memory[obj])

    if len(obj) > 3:
        res += codes.MARK

    for itm in obj:
        res += partial_pickle(itm, memory)

    match len(obj):
        case 1:
            res += codes.TUPLE1
        case 2:
            res += codes.TUPLE2
        case 3:
            res += codes.TUPLE3
        case _:
            res += codes.TUPLE

    res += memory.memoize(obj)

    return res


disbatch_table_memo[tuple] = encode_tuple


def encode_list(memory: Memo, obj: List[Any]) -> bytes:
    res = b""

    res += codes.EMPTY_LIST

    res += memory.memoize(obj)

    res += add_batch(memory, obj)

    return res


disbatch_table_memo[list] = encode_list


def encode_dict(memory: Memo, obj: Dict[Any, Any]) -> bytes:
    res = b""

    res += codes.EMPTY_DICT

    res += memory.memoize(obj)

    res += set_batch(memory, obj.items())

    return res


disbatch_table_memo[dict] = encode_dict
