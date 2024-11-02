from struct import pack
from typing import Any

from .opcodes.opcodes import OPCODE


class Pickler:
    def __init__(self) -> None:
        self.byte_count: int = 0
        self.codes = OPCODE()
        print("Pickler prepared, starting now...")

    def pack_n_serve(self, pack_arg: str, bin_code: bytes, obj: Any) -> bytes:
        packed: bytes = pack(pack_arg, obj)
        concat: bytes = bin_code + packed
        self.byte_count += len(concat)
        return concat

    def encode_none(self) -> bytes:
        self.byte_count += 1
        return self.codes.NONE

    def encode_bool(self, obj: bool) -> bytes:
        self.byte_count += 1
        return self.codes.TRUE if obj else self.codes.FALSE

    def encode_string(self, obj: str) -> bytes:
        utf_string: bytes = obj.encode("utf-8", "surrogatepass")
        length: int = len(utf_string)
        if length < 256:
            return self.pack_n_serve("<B", self.codes.SHORT_UNICODE, length)
        elif length > 0xFFFFFFFF:
            return self.pack_n_serve("<Q", self.codes.LONG_UNICODE, length)
        else:
            return self.pack_n_serve("<I", self.codes.UNICODE, length)

    def encode_long(self, obj: int) -> bytes:
        if obj >= 0:
            if obj <= 0xFF:
                return self.pack_n_serve("<B", self.codes.BININT1, obj)
            elif obj <= 0xFFFF:
                return self.pack_n_serve("<H", self.codes.BININT2, obj)

        if -0x80000000 <= obj <= 0x7FFFFFFF:
            return self.pack_n_serve("<i", self.codes.BININT, obj)

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
            return self.pack_n_serve("<B", self.codes.LONG1, n) + encoded_long
        else:
            return self.pack_n_serve("<i", self.codes.LONG4, n) + encoded_long
