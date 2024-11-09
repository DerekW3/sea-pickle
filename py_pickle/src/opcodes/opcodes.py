class OPCODE:
    MEMO: bytes = b"\x94"
    BINGET: bytes = b"h"
    LONG_BINGET: bytes = b"j"

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
    BININT2 = b"M"
    LONG1 = b"\x8a"
    LONG4 = b"\x8b"
    BINFLOAT = b"G"

    # BYTES TYPES
    SHORT_BINBYTES = b"C"
    BINBYTES8 = b"\x8e"
    BINBYTES = b"B"

    # ARRAY TYPES
    MARK = b"("
    APPENDS = b"e"
    APPEND = b"a"

    # DICT TYPES
    EMPTY_DICT = b"}"
    SETITEM = b"s"
    SETITEMS = b"u"

    # TUPLE TYPES
    EMPTY_TUPLE = b")"
    TUPLE1 = b"\x85"
    TUPLE2 = b"\x86"
    TUPLE3 = b"\x87"
    TUPLE = b"t"

    # LIST TYPES
    EMPTY_LIST = b"]"
