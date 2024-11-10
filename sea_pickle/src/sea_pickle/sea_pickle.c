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

static PyObject *get_chunks(PyObject *obj) { Py_RETURN_NONE; }

static PyObject *get_memo(PyObject *chunks) { Py_RETURN_NONE; }

static PyObject *listize(PyObject *memory, PyObject *obj1, PyObject *obj2) {
  Py_RETURN_NONE;
}

static PyObject *extract_tuple(PyObject *chunks, PyObject *idx) {
  Py_RETURN_NONE;
}

static PyObject *extract_sequence(PyObject *chunks, PyObject *idx) {
  Py_RETURN_NONE;
}

static PyObject *length_packer(PyObject *length) { Py_RETURN_NONE; }

static PyObject *get(PyObject *idx) { Py_RETURN_NONE; }

static PyObject *merge_strings(PyObject *str_1, PyObject *identifier_1,
                               PyObject *str_2, PyObject *identifier_2) {
  Py_RETURN_NONE;
}

static PyObject *merge_bytes(PyObject *byte_str_1, PyObject *identifier_1,
                             PyObject *byte_str_2, PyObject *identifier_2) {
  Py_RETURN_NONE;
}

static PyObject *encode_none() {
  return PyBytes_FromStringAndSize((const char *)NONE, sizeof(NONE));
}

static PyObject *encode_bool(PyObject *obj) { Py_RETURN_NONE; }

static PyObject *encode_string(PyObject *obj) { Py_RETURN_NONE; }

static PyObject *encode_float(PyObject *obj) { Py_RETURN_NONE; }

static PyObject *encode_long(PyObject *obj) { Py_RETURN_NONE; }

static PyObject *encode_bytes(PyObject *obj) { Py_RETURN_NONE; }

static PyObject *encode_tuple(PyObject *obj) { Py_RETURN_NONE; }

static PyObject *encode_list(PyObject *obj) { Py_RETURN_NONE; }

static PyObject *encode_dict(PyObject *obj) { Py_RETURN_NONE; }

static PyObject *add_batch(PyObject *items) { Py_RETURN_NONE; }

static PyObject *set_batch(PyObject *items) { Py_RETURN_NONE; }