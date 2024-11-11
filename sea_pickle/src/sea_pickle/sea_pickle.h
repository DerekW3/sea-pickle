#ifndef SEAPICKLE_H
#define SEAPICKLE_H

#include <Python.h>
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

static PyObject* get_chunks(PyObject* obj);
static PyObject* get_memo(PyObject* chunks);
static PyObject* listize(PyObject* memory, PyObject* obj1, PyObject* obj2);
static PyObject* extract_tuple(PyObject* chunks, PyObject* idx);
static PyObject* extract_sequence(PyObject* chunks, PyObject* idx);
static PyObject* length_packer(PyObject* length);
static PyObject* get(PyObject* idx);
static PyObject* merge_strings(PyObject* str_1, PyObject* identifier_1, PyObject* str_2, PyObject* identifier_2);
static PyObject* merge_bytes(PyObject* byte_str_1, PyObject* identifier_1, PyObject* byte_str_2, PyObject* identifier_2);
static PyObject* encode_none();
static PyObject* encode_bool(PyObject* obj);
static PyObject* encode_string(PyObject* obj);
static PyObject* encode_float(PyObject* obj);
static PyObject* encode_long(PyObject* obj);
static PyObject* encode_bytes(PyObject* obj);
static PyObject* encode_tuple(PyObject* self, PyObject* obj);
static PyObject* encode_list(PyObject* self, PyObject* obj);
static PyObject* encode_dict(PyObject* self, PyObject* obj);

#endif