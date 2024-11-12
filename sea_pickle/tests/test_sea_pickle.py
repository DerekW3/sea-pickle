import pickle

import sea_pickle


def test_partial_pickle():
    assert sea_pickle.partial_pickle(None) == b"N"
    assert sea_pickle.partial_pickle(True) == b"\x88"
    assert sea_pickle.partial_pickle(False) == b"\x89"
    assert sea_pickle.partial_pickle("hello") in pickle.dumps("hello")
    assert sea_pickle.partial_pickle(b"hello") in pickle.dumps(b"hello")
    assert sea_pickle.partial_pickle(1) in pickle.dumps(1)
    assert sea_pickle.partial_pickle(100000000) in pickle.dumps(100000000)
    assert sea_pickle.partial_pickle(-100) in pickle.dumps(-100)
    assert sea_pickle.partial_pickle(1.05) in pickle.dumps(1.05)
    assert sea_pickle.partial_pickle(-1.05) in pickle.dumps(-1.05)
