import pickle
import pickletools

# BOOL-LIKE TYPES
NONE: bytes = b"N"
TRUE: bytes = b"\x88"
FALSE: bytes = b"\x89"

# STRING TYPES
SHORT_UNICODE: bytes = b"\x8c"
UNICODE: bytes = b"X"
LONG_UNICODE: bytes = b"\x8d"


class Pickler:
    def __init__(self):
        print("Pickler prepared, starting now...")

    def encode_none(self) -> bytes:
        return NONE

    def encode_bool(self, obj: bool) -> bytes:
        return TRUE if obj else FALSE

    def encode_string(self, obj: str) -> bytes:
        return TRUE


def main():
    pickled_str = pickle.dumps("This is a test string")

    print(pickled_str)
    pickletools.dis(pickled_str)


if __name__ == "__main__":
    main()
