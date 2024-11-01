import pickle

from src.pickler import encode_str


def test_encode_str():
    assert pickle.dumps("hello there") == encode_str("hello")
