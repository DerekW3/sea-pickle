#ifndef SEAPICKLE_H
#define SEAPICKLE_H

#include <Python.h>
#include <bytesobject.h>
#include <floatobject.h>
#include <stdint.h>

typedef enum {
  MEMO = 0x94,
  BINGET = 'h',
  LONG_BINGET = 'j',

  // BOOL-LIKE TYPES
  NONE = 'N',
  TRUE = 0x88,
  FALSE = 0x89,

  // STRING TYPES
  SHORT_UNICODE = 0x8c,
  UNICODE = 'X',
  LONG_UNICODE = 0x8d,

  // NUMERIC TYPES
  BININT = 'J',
  BININT1 = 'K',
  BININT2 = 'M',
  LONG1 = 0x8a,
  LONG4 = 0x8b,
  BINFLOAT = 'G',

  // BYTES TYPES
  SHORT_BINBYTES = 'C',
  BINBYTES8 = 0x8e,
  BINBYTES = 'B',

  // ARRAY TYPES
  MARK = '(',
  APPENDS = 'e',
  APPEND = 'a',

  // DICT TYPES
  EMPTY_DICT = '}',
  SETITEM = 's',
  SETITEMS = 'u',

  // TUPLE TYPES
  EMPTY_TUPLE = ')',
  TUPLE1 = 0x85,
  TUPLE2 = 0x86,
  TUPLE3 = 0x87,
  TUPLE = 't',

  // LIST TYPES
  EMPTY_LIST = ']'
} OPCODES;

PyObject* partial_pickle(PyObject* self, PyObject* args);
PyObject* merge_partials(PyObject* self, PyObject* args);

static PyObject* get_chunks(PyBytesObject* obj);
static PyObject* get_memo(PyListObject* chunks);
static PyObject* listize(PyDictObject* memory, PyBytesObject* obj1, PyBytesObject* obj2);
static PyObject* merge_strings(PyBytesObject* str_1, PyBytesObject* identifier_1, PyBytesObject* str_2, PyBytesObject* identifier_2);
static PyObject* merge_bytes(PyBytesObject* byte_str_1, PyBytesObject* identifier_1, PyBytesObject* byte_str_2, PyBytesObject* identifier_2);
static PyObject* encode_none(PyObject* obj);
static PyObject* encode_bool(PyObject* obj);
static PyObject* encode_string(const char* obj);
static PyObject* encode_float(PyFloatObject* obj);
static PyObject* encode_long(PyObject* obj);
static PyObject* encode_bytes(PyBytesObject* obj);
static PyObject* encode_tuple(PyTupleObject* obj);
static PyObject* encode_list(PyListObject* obj);
static PyObject* encode_dict(PyDictObject* obj);
static PyObject* add_batch(PyObject* items);
static PyObject* set_batch(PyObject* items);

#endif