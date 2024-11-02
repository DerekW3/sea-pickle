class OPCODE:
    # BOOL-LIKE TYPES
    NONE: bytes = b"N"
    TRUE: bytes = b"\x88"
    FALSE: bytes = b"\x89"

    # STRING TYPES
    SHORT_UNICODE: bytes = b"\x8c"
    UNICODE: bytes = b"X"
    LONG_UNICODE: bytes = b"\x8d"

    # NUMERIC TYPES
    BININT = b"J"
    BININT1 = b"K"
    BININT2 = b"K"
    LONG1 = b"\x8a"
    LONG4 = b"\x8b"
