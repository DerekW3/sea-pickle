#ifndef SEAPICKLE_H
#define SEAPICKLE_H

#include <Python.h>
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

#endif