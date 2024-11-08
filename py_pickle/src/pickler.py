from itertools import islice
from struct import pack
from typing import Any, Callable, Dict, List, Tuple, Type

from .opcodes.opcodes import OPCODE

codes = OPCODE()


EncodeFunction = Callable[[Any], bytes]
disbatch_table: Dict[Type[Any], EncodeFunction] = {}


indicators = [
    codes.NONE,
    codes.TRUE,
    codes.FALSE,
    codes.SHORT_UNICODE,
    codes.UNICODE,
    codes.LONG_UNICODE,
    codes.BININT,
    codes.BININT1,
    codes.BININT2,
    codes.LONG1,
    codes.LONG4,
    codes.BINFLOAT,
    codes.SHORT_BINBYTES,
    codes.BINBYTES8,
    codes.BINBYTES,
    codes.MARK,
    codes.EMPTY_DICT,
    codes.EMPTY_TUPLE,
    codes.TUPLE1,
    codes.TUPLE2,
    codes.TUPLE3,
    # codes.TUPLE,
    codes.EMPTY_LIST,
]


def partial_pickle(obj: Any) -> bytes:
    pickled_obj = b""

    obj_type: Any = type(obj)

    if obj_type in disbatch_table:
        func = disbatch_table[obj_type]
        pickled_obj += func(obj)
    else:
        raise ValueError("Non-pickleable objecty")

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
        case _:
            chunks = get_chunks(obj1 + obj2)

            temp_memo: dict[bytes, int] = get_memo(chunks)

            result = listize(temp_memo, obj1, obj2)

    frame_bytes = b"\x95" + pack("<Q", len(result)) if len(result) >= 4 else b""
    return b"\x80\x04" + frame_bytes + result


def get_chunks(obj: bytes) -> list[bytes]:
    chunks: list[bytes] = []
    left, right = 0, 1
    while right < len(obj):
        while (
            right < len(obj)
            and obj[left : left + 1] in indicators
            and obj[right : right + 1] not in indicators
        ):
            right += 1

        chunks.append(obj[left:right])
        left = right
        right += 1

    return chunks


def get_memo(chunks: list[bytes]) -> dict[bytes, int]:
    new_memo: dict[bytes, int] = {}

    for i, chunk in enumerate(chunks):
        if chunk[-1:] == codes.MEMO:
            if chunk[-2:-1] in [b"\x85", b"\x86", b"\x87"]:
                extracted_tuple = extract_tuple(chunks, i)
                if extracted_tuple not in new_memo:
                    new_memo[extracted_tuple] = len(new_memo) + 1
                continue
            if chunk not in new_memo:
                new_memo[chunk] = len(new_memo) + 1

    return new_memo


def listize(memory: dict[bytes, int], obj1: bytes, obj2: bytes) -> bytes:
    combined = obj1 + obj2
    sorted_memo = reversed(sorted(memory.keys(), key=len))

    for memoized in sorted_memo:
        first_idx = combined.find(memoized) + len(memoized)

        combined = combined[:first_idx] + combined[first_idx:].replace(
            memoized, get(memory[memoized])
        )

    return codes.EMPTY_LIST + codes.MEMO + codes.MARK + combined + codes.APPENDS + b"."


def extract_tuple(chunks: list[bytes], idx: int) -> bytes:
    num_remains = 1
    curr_idx = idx
    res = b""

    while num_remains > 0:
        if chunks[curr_idx][-2:-1] == b"\x85":
            num_remains += 1
        elif chunks[curr_idx][-2:-1] == b"\x86":
            num_remains += 2
        elif chunks[curr_idx][-2:-1] == b"\x87":
            num_remains += 3

        res = chunks[curr_idx] + res

        curr_idx -= 1
        num_remains -= 1

    return res


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


def memoize():
    return codes.MEMO


def get(idx: int) -> bytes:
    if idx < 256:
        return codes.BINGET + pack("<B", idx)
    else:
        return codes.LONG_BINGET + pack("<I", idx)


def encode_none(obj: None) -> bytes:
    if obj is None:
        return codes.NONE


disbatch_table[type(None)] = encode_none


def encode_bool(obj: bool) -> bytes:
    return codes.TRUE if obj else codes.FALSE


disbatch_table[bool] = encode_bool


def encode_string(obj: str) -> bytes:
    res = b""
    utf_string: bytes = obj.encode("utf-8", "surrogatepass")
    length: int = len(utf_string)
    if length < 256:
        res += codes.SHORT_UNICODE + pack("<B", length) + utf_string
    elif length > 0xFFFFFFFF:
        res += codes.LONG_UNICODE + pack("<Q", length) + utf_string
    else:
        res += codes.UNICODE + pack("<I", length) + utf_string

    res += memoize()

    return res


disbatch_table[str] = encode_string


def encode_float(obj: float) -> bytes:
    return codes.BINFLOAT + pack(">d", obj)


disbatch_table[float] = encode_float


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


disbatch_table[int] = encode_long


def encode_bytes(obj: bytes) -> bytes:
    res = b""
    n = len(obj)

    if n < 256:
        res += codes.SHORT_BINBYTES + pack("<B", n) + obj
    elif n > 0xFFFFFFFF:
        res += codes.BINBYTES8 + pack("<Q", n) + obj
    else:
        res += codes.BINBYTES + pack("<I", n) + obj

    res += memoize()

    return res


disbatch_table[bytes] = encode_bytes


def add_batch(items: Any) -> bytes:
    it = iter(items)

    result = b""

    while True:
        temp = list(islice(it, 1000))

        n = len(temp)

        if n > 1:
            result += codes.MARK
            for itm in temp:
                result += partial_pickle(itm)
            result += codes.APPENDS
        elif n:
            result += partial_pickle(temp[0])
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
                result += partial_pickle(key)
                result += partial_pickle(value)
            result += codes.SETITEMS
        elif n:
            key, value = temp[0]
            result += partial_pickle(key)
            result += partial_pickle(value)
            result += codes.SETITEM

        if n < 1000:
            return result


def encode_tuple(obj: Tuple[Any, ...]) -> bytes:
    res = b""

    if not obj:
        return codes.EMPTY_TUPLE

    if len(obj) > 3:
        res += codes.MARK

    for itm in obj:
        res += partial_pickle(itm)

    match len(obj):
        case 1:
            res += codes.TUPLE1
        case 2:
            res += codes.TUPLE2
        case 3:
            res += codes.TUPLE3
        case _:
            res += codes.TUPLE

    res += memoize()

    return res


disbatch_table[tuple] = encode_tuple


def encode_list(obj: List[Any]) -> bytes:
    res = b""

    res += codes.EMPTY_LIST

    res += memoize()

    res += add_batch(obj)

    return res


disbatch_table[list] = encode_list


def encode_dict(obj: Dict[Any, Any]) -> bytes:
    res = b""

    res += codes.EMPTY_DICT

    res += memoize()

    res += set_batch(obj.items())

    return res


disbatch_table[dict] = encode_dict
