#ifndef SEAPICKLE_H
#define SEAPICKLE_H

#include <Python.h>
#include <bytesobject.h>
#include <floatobject.h>
#include <listobject.h>
#include <object.h>
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

static PyListObject* get_chunks(PyBytesObject* obj);
static PyDictObject* get_memo(PyListObject* chunks);
static PyBytesObject* listize(PyDictObject* memory, PyBytesObject* obj1, PyBytesObject* obj2);
static PyBytesObject* extract_tuple(PyListObject* chunks, PyObject* idx);
static PyBytesObject* extract_sequence(PyListObject* chunks, PyObject* idx);
static PyBytesObject* length_packer(PyObject* length);
static PyBytesObject* get(PyObject* idx);
static PyBytesObject* merge_strings(PyBytesObject* str_1, PyBytesObject* identifier_1, PyBytesObject* str_2, PyBytesObject* identifier_2);
static PyBytesObject* merge_bytes(PyBytesObject* byte_str_1, PyBytesObject* identifier_1, PyBytesObject* byte_str_2, PyBytesObject* identifier_2);
static PyBytesObject* encode_none(PyObject* obj);
static PyBytesObject* encode_bool(PyObject* obj);
static PyBytesObject* encode_string(const char* obj);
static PyBytesObject* encode_float(PyFloatObject* obj);
static PyBytesObject* encode_long(PyObject* obj);
static PyBytesObject* encode_bytes(PyBytesObject* obj);
static PyBytesObject* encode_tuple(PyTupleObject* obj);
static PyBytesObject* encode_list(PyListObject* obj);
static PyBytesObject* encode_dict(PyDictObject* obj);
static PyBytesObject* add_batch(PyObject* items);
static PyBytesObject* set_batch(PyObject* items);

#endif