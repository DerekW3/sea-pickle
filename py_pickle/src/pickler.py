import pickle
import pickletools

NONE: bytes = b"N"
TRUE: bytes = b"\x88"
FALSE: bytes = b"\x89"


class Pickler:
    def __init__(self):
        print("Pickler prepared, starting now...")

    def encode_none(self) -> bytes:
        return NONE


def encode_str(input_string: str):
    print("hello")


def main():
    pickled_str = pickle.dumps("This is a test string")

    print(pickled_str)
    pickletools.dis(pickled_str)


if __name__ == "__main__":
    main()
