#include "sea_pickle.h"
#include <boolobject.h>
#include <bytesobject.h>
#include <floatobject.h>
#include <listobject.h>
#include <longobject.h>
#include <modsupport.h>
#include <object.h>
#include <pyerrors.h>
#include <pyport.h>
#include <string.h>
#include <unicodeobject.h>

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

static PyObject *encode_bool(PyObject *obj) {
  if (!PyBool_Check(obj)) {
    PyErr_SetString(PyExc_TypeError, "Expected a bool type.");
    return NULL;
  };

  if (obj == Py_True) {
    return PyBytes_FromStringAndSize((char *)TRUE, sizeof(TRUE));
  } else {
    return PyBytes_FromStringAndSize((char *)FALSE, sizeof(FALSE));
  }
}

static PyObject *encode_string(PyObject *obj) {
  if (!PyUnicode_Check(obj)) {
    PyErr_SetString(PyExc_TypeError, "Expected a string");
    return NULL;
  }

  PyObject *utf_string_obj =
      PyUnicode_AsEncodedString(obj, "utf-8", "surrogatepass");

  if (utf_string_obj == NULL) {
    return NULL;
  }

  Py_ssize_t length = PyBytes_Size(utf_string_obj);
  char *utf_string = PyBytes_AsString(utf_string_obj);

  PyObject *result = PyBytes_FromStringAndSize(NULL, 0);
  if (result == NULL) {
    Py_DECREF(utf_string_obj);
    return NULL;
  }

  if (length < 256) {
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)SHORT_UNICODE, 1));
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)&length, 1));
  } else if (length > 0xFFFFFFFFF) {
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)LONG_UNICODE, 1));
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)&length, 8));
  } else {
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)UNICODE, 1));
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)&length, 4));
  }

  PyBytes_ConcatAndDel(&result, PyBytes_FromStringAndSize(utf_string, length));

  PyBytes_ConcatAndDel(&result, PyBytes_FromStringAndSize((char *)MEMO, 1));

  Py_DECREF(utf_string_obj);

  return result;
}

static PyObject *encode_float(PyObject *obj) {
  if (!PyFloat_Check(obj)) {
    PyErr_SetString(PyExc_TypeError, "Expected a float object");
    return NULL;
  }

  double value = PyFloat_AsDouble(obj);
  if (value == -1.0 && PyErr_Occurred()) {
    return NULL;
  }

  PyObject *result = PyBytes_FromStringAndSize(NULL, 0);
  if (result == NULL) {
    return NULL;
  }

  unsigned char packed_float[8];
  memcpy(packed_float, &value, sizeof(double));

  PyBytes_ConcatAndDel(&result, PyBytes_FromStringAndSize((char *)BINFLOAT, 1));
  PyBytes_ConcatAndDel(&result,
                       PyBytes_FromStringAndSize((char *)packed_float, 8));

  return result;
}

static PyObject *encode_long(PyObject *obj) {
  if (!PyLong_Check(obj)) {
    PyErr_SetString(PyExc_TypeError, "Expected an integer.");
    return NULL;
  }

  long value = PyLong_AsLong(obj);
  if (value == -1 && PyErr_Occurred()) {
    return NULL;
  }

  PyObject *result = PyBytes_FromStringAndSize(NULL, 0);
  if (result == NULL) {
    return NULL;
  }

  if (value >= 0) {
    if (value <= 0xFF) {
      PyBytes_ConcatAndDel(&result,
                           PyBytes_FromStringAndSize((char *)BININT1, 1));
      unsigned char byte_value = (unsigned char)value;
      PyBytes_ConcatAndDel(&result,
                           PyBytes_FromStringAndSize((char *)&byte_value, 1));
      return result;
    } else if (value <= 0xFFFF) {
      PyBytes_ConcatAndDel(&result,
                           PyBytes_FromStringAndSize((char *)BININT2, 1));
      unsigned short short_value = (unsigned short)value;
      PyBytes_ConcatAndDel(&result,
                           PyBytes_FromStringAndSize((char *)&short_value, 2));
    }
  }

  if (-0x80000000 <= value && value <= 0x7FFFFFFF) {
    PyBytes_ConcatAndDel(&result, PyBytes_FromStringAndSize((char *)BININT, 1));
    int int_value = (int)value;
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)&int_value, 4));
  }

  long abs_value = value >= 0 ? value : -value;
  int num_bytes = abs_value != 0 ? 0 : 1;

  while (abs_value > 0) {
    abs_value >>= 8;
    num_bytes++;
  }

  unsigned char *encoded_long = (unsigned char *)malloc(num_bytes);
  if (encoded_long == NULL) {
    Py_DECREF(result);
    return NULL;
  }

  for (int i = 0; i < num_bytes; i++) {
    encoded_long[i] = (value >> (i * 8)) & 0xFF;
  }

  PyObject *long_result =
      PyBytes_FromStringAndSize((char *)encoded_long, num_bytes);
  free(encoded_long);

  if (num_bytes < 256) {
    PyBytes_ConcatAndDel(&result, PyBytes_FromStringAndSize((char *)LONG1, 1));
    unsigned char length_byte = (unsigned char)num_bytes;
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)&length_byte, 1));
  } else {
    PyBytes_ConcatAndDel(&result, PyBytes_FromStringAndSize((char *)LONG4, 1));
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)&num_bytes, 4));
  }

  PyBytes_ConcatAndDel(&result, long_result);
  return result;
}

static PyObject *encode_bytes(PyObject *obj) { Py_RETURN_NONE; }

static PyObject *encode_tuple(PyObject *obj) { Py_RETURN_NONE; }

static PyObject *encode_list(PyObject *obj) { Py_RETURN_NONE; }

static PyObject *encode_dict(PyObject *obj) { Py_RETURN_NONE; }

static PyObject *add_batch(PyObject *items) { Py_RETURN_NONE; }

static PyObject *set_batch(PyObject *items) { Py_RETURN_NONE; }