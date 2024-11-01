import pickle
import pickletools


def encode_str(input_string: str):
    print("hello")


def main():
    pickled_str = pickle.dumps("This is a test string")

    print(pickled_str)
    pickletools.dis(pickled_str)


if __name__ == "__main__":
    main()
