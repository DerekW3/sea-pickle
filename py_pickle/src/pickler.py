from struct import pack

# BOOL-LIKE TYPES
NONE: bytes = b"N"
TRUE: bytes = b"\x88"
FALSE: bytes = b"\x89"

# STRING TYPES
SHORT_UNICODE: bytes = b"\x8c"
UNICODE: bytes = b"X"
LONG_UNICODE: bytes = b"\x8d"


class Pickler:
    def __init__(self) -> None:
        self.byte_count: int = 0
        print("Pickler prepared, starting now...")

    def encode_none(self) -> bytes:
        self.byte_count += 1
        return NONE

    def encode_bool(self, obj: bool) -> bytes:
        self.byte_count += 1
        return TRUE if obj else FALSE

    def encode_string(self, obj: str) -> bytes:
        utf_string: bytes = obj.encode("utf-8", "surrogatepass")
        length: int = len(utf_string)
        if length < 256:
            packed: bytes = pack("<B", length)
            concat: bytes = SHORT_UNICODE + packed + utf_string
        elif length > 0xFFFFFFFF:
            packed: bytes = pack("<Q", length)
            concat: bytes = LONG_UNICODE + packed + utf_string
        else:
            packed: bytes = pack("<I", length)
            concat: bytes = UNICODE + packed + utf_string

        self.byte_count += len(concat)
        return concat
