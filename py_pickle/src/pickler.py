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
        print("Pickler prepared, starting now...")

    def encode_none(self) -> bytes:
        return NONE

    def encode_bool(self, obj: bool) -> bytes:
        return TRUE if obj else FALSE

    def encode_string(self, obj: str) -> bytes:
        utf_string: bytes = obj.encode("utf-8", "surrogatepass")
        length: int = len(utf_string)
        if length < 256:
            return SHORT_UNICODE + pack("<B", length) + utf_string
        elif length > 0xFFFFFFFF:
            return LONG_UNICODE + pack("<Q", length) + utf_string
        else:
            return UNICODE + pack("<I", length) + utf_string
