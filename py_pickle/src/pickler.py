from struct import pack

from .opcodes.opcodes import OPCODE


class Pickler:
    def __init__(self) -> None:
        self.pickled = b""
        self.byte_count: int = 0
        self.codes = OPCODE()
        print("Pickler prepared, starting now...")

    def write(self, obj: bytes):
        self.pickled += obj
        self.byte_count = len(self.pickled)

    def encode_none(self):
        self.write(self.codes.NONE)

    def encode_bool(self, obj: bool):
        self.write(self.codes.TRUE if obj else self.codes.FALSE)

    def encode_string(self, obj: str):
        utf_string: bytes = obj.encode("utf-8", "surrogatepass")
        length: int = len(utf_string)
        if length < 256:
            self.write(self.codes.SHORT_UNICODE + pack("<B", length) + utf_string)
        elif length > 0xFFFFFFFF:
            self.write(self.codes.LONG_UNICODE + pack("<Q", length) + utf_string)
        else:
            self.write(self.codes.UNICODE + pack("<I", length) + utf_string)

    def encode_long(self, obj: int):
        if obj >= 0:
            if obj <= 0xFF:
                self.write(self.codes.BININT1 + pack("<B", obj))
                return
            elif obj <= 0xFFFF:
                self.write(self.codes.BININT2 + pack("<H", obj))
                return

        if -0x80000000 <= obj <= 0x7FFFFFFF:
            self.write(self.codes.BININT + pack("<i", obj))
            return

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
            self.write(self.codes.LONG1 + pack("<B", n) + encoded_long)
        else:
            self.write(self.codes.LONG4 + pack("<i", n) + encoded_long)
