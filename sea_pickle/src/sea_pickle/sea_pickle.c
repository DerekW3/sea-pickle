#include "sea_pickle.h"
#include <bytesobject.h>
#include <listobject.h>
#include <modsupport.h>
#include <object.h>

PyObject *partial_pickle(PyObject *self, PyObject *args) {
  PyObject *obj;

  if (!PyArg_ParseTuple(args, "O", &obj)) {
    return NULL;
  }

  Py_RETURN_NONE;
}

PyObject *merge_partials(PyObject *self, PyObject *args) {
  const char *obj1;
  const char *obj2;
  int no_memo = 0;
  int frame_info = 1;

  if (!PyArg_ParseTuple(args, "ss|ii", &obj1, &obj2, &no_memo, &frame_info)) {
    return NULL;
  }

  Py_RETURN_NONE;
}

static PyListObject *get_chunks(PyBytesObject *obj) { Py_RETURN_NONE; }

static PyDictObject *get_memo(PyListObject *chunks) { Py_RETURN_NONE; }

static PyBytesObject *listize(PyDictObject *memory, PyBytesObject *obj1,
                              PyBytesObject *obj2) {
  Py_RETURN_NONE;
}

static PyBytesObject *extract_tuple(PyListObject *chunks, PyObject *idx) {
  Py_RETURN_NONE;
}

static PyBytesObject *extract_sequence(PyListObject *chunks, PyObject *idx) {
  Py_RETURN_NONE;
}

static PyBytesObject *length_packer(PyObject *length) { Py_RETURN_NONE; }

static PyBytesObject *get(PyObject *idx) { Py_RETURN_NONE; }

static PyBytesObject *merge_strings(PyBytesObject *str_1,
                                    PyBytesObject *identifier_1,
                                    PyBytesObject *str_2,
                                    PyBytesObject *identifier_2) {
  Py_RETURN_NONE;
}

static PyBytesObject *merge_bytes(PyBytesObject *byte_str_1,
                                  PyBytesObject *identifier_1,
                                  PyBytesObject *byte_str_2,
                                  PyBytesObject *identifier_2) {
  Py_RETURN_NONE;
}

static PyBytesObject *encode_none(PyObject *obj) { Py_RETURN_NONE; }

static PyBytesObject *encode_bool(PyObject *obj) { Py_RETURN_NONE; }

static PyBytesObject *encode_string(const char *obj) { Py_RETURN_NONE; }

static PyBytesObject *encode_float(PyFloatObject *obj) { Py_RETURN_NONE; }

static PyBytesObject *encode_long(PyObject *obj) { Py_RETURN_NONE; }

static PyBytesObject *encode_bytes(PyBytesObject *obj) { Py_RETURN_NONE; }

static PyBytesObject *encode_tuple(PyTupleObject *obj) { Py_RETURN_NONE; }

static PyBytesObject *encode_list(PyListObject *obj) { Py_RETURN_NONE; }

static PyBytesObject *encode_dict(PyDictObject *obj) { Py_RETURN_NONE; }

static PyBytesObject *add_batch(PyObject *items) { Py_RETURN_NONE; }

static PyBytesObject *set_batch(PyObject *items) { Py_RETURN_NONE; }