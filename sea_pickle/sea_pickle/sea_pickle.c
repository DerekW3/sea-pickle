#include <Python.h>
#include <abstract.h>
#include <boolobject.h>
#include <bytesobject.h>
#include <dictobject.h>
#include <floatobject.h>
#include <listobject.h>
#include <longobject.h>
#include <methodobject.h>
#include <modsupport.h>
#include <moduleobject.h>
#include <object.h>
#include <pyerrors.h>
#include <pylifecycle.h>
#include <pyport.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <tupleobject.h>
#include <unicodeobject.h>

const unsigned char MEMO = 0x94;
const unsigned char BINGET = 'h';
const unsigned char LONG_BINGET = 'j';

// BOOL-LIKE TYPES
const unsigned char NONE = 'N';
const unsigned char TRUE = 0x88;
const unsigned char FALSE = 0x89;

// STRING TYPES
const unsigned char SHORT_UNICODE = 0x8c;
const unsigned char UNICODE = 'X';
const unsigned char LONG_UNICODE = 0x8d;

// NUMERIC TYPES
const unsigned char BININT = 'J';
const unsigned char BININT1 = 'K';
const unsigned char BININT2 = 'M';
const unsigned char LONG1 = 0x8a;
const unsigned char LONG4 = 0x8b;
const unsigned char BINFLOAT = 'G';

// BYTES TYPES
const unsigned char SHORT_BINBYTES = 'C';
const unsigned char BINBYTES8 = 0x8e;
const unsigned char BINBYTES = 'B';

// ARRAY TYPES
const unsigned char MARK = '(';
const unsigned char APPENDS = 'e';
const unsigned char APPEND = 'a';

// DICT TYPES
const unsigned char EMPTY_DICT = '}';
const unsigned char SETITEM = 's';
const unsigned char SETITEMS = 'u';

// TUPLE TYPES
const unsigned char EMPTY_TUPLE = ')';
const unsigned char TUPLE1 = 0x85;
const unsigned char TUPLE2 = 0x86;
const unsigned char TUPLE3 = 0x87;
const unsigned char TUPLE = 't';

// LIST TYPES
const unsigned char EMPTY_LIST = ']';

const unsigned char *indicators[] = {
    &NONE,         &TRUE,       &FALSE,          &SHORT_UNICODE, &UNICODE,
    &LONG_UNICODE, &BININT,     &BININT1,        &BININT2,       &LONG1,
    &LONG4,        &BINFLOAT,   &SHORT_BINBYTES, &BINBYTES,      &BINBYTES8,
    &MARK,         &EMPTY_DICT, &EMPTY_LIST,     &EMPTY_TUPLE,   &TUPLE1,
    &TUPLE2,       &TUPLE3,     &TUPLE,          &EMPTY_LIST};

int in_indicators(const char *elem) {
  for (size_t i = 0; i < 23; i++) {
    if (memcmp(elem, indicators[i], 1) == 0) {
      return 1;
    }
  }
  return 0;
}

typedef struct {
  PyTypeObject *type;
  PyObject *(*func)(PyObject *);
} DisbatchEntry;

PyObject *partial_pickle(PyObject *self, PyObject *args);
PyObject *merge_partials(PyObject *self, PyObject *args);

static PyObject *recurse_pickle(PyObject *obj);
static PyObject *get_chunks(PyObject *obj);
static PyObject *get_memo(PyObject *chunks);
static PyObject *listize(PyObject *memory, PyObject *obj1, PyObject *obj2);
int compare_length(const void *a, const void *b);
static PyObject *extract_tuple(PyObject *chunks, Py_ssize_t idx);
static PyObject *extract_sequence(PyObject *chunks, Py_ssize_t idx);
static PyObject *get(PyObject *idx);
static PyObject *merge_strings(PyObject *str_1, PyObject *identifier_1,
                               PyObject *str_2, PyObject *identifier_2);
static PyObject *merge_bytes(PyObject *byte_str_1, PyObject *identifier_1,
                             PyObject *byte_str_2, PyObject *identifier_2);
static PyObject *encode_none(void);
static PyObject *encode_bool(PyObject *obj);
static PyObject *encode_string(PyObject *obj);
static PyObject *encode_float(PyObject *obj);
static PyObject *encode_long(PyObject *obj);
static PyObject *encode_bytes(PyObject *obj);
static PyObject *encode_tuple(PyObject *obj);
static PyObject *encode_list(PyObject *obj);
static PyObject *encode_dict(PyObject *obj);

static DisbatchEntry disbatch_table[] = {{&PyBool_Type, encode_bool},
                                         {&PyUnicode_Type, encode_string},
                                         {&PyFloat_Type, encode_float},
                                         {&PyLong_Type, encode_long},
                                         {&PyBytes_Type, encode_bytes},
                                         {&PyTuple_Type, encode_tuple},
                                         {&PyList_Type, encode_list},
                                         {&PyDict_Type, encode_dict},
                                         {NULL, NULL}};

PyObject *partial_pickle(PyObject *self, PyObject *args) {
  PyObject *obj;

  if (!PyArg_ParseTuple(args, "O", &obj)) {
    PyErr_SetString(PyExc_RuntimeError, "Failed to parse argument");
    return NULL;
  }

  PyObject *pickled_obj = PyBytes_FromStringAndSize(NULL, 0);
  if (!pickled_obj) {
    return NULL;
  }

  if (obj == Py_None) {
    PyBytes_ConcatAndDel(&pickled_obj, encode_none());
    return pickled_obj;
  }

  for (int i = 0; i < sizeof(disbatch_table) / sizeof(disbatch_table[0]); i++) {
    if (disbatch_table[i].type != NULL &&
        PyObject_TypeCheck(obj, disbatch_table[i].type)) {
      PyObject *result = NULL;

      result = disbatch_table[i].func(obj);

      if (!result) {
        Py_DECREF(pickled_obj);
        return NULL;
      }

      PyBytes_ConcatAndDel(&pickled_obj, result);
      break;
    }
  }

  if (!pickled_obj) {
    PyErr_SetString(PyExc_TypeError, "Unsupported type for encoding.");
    return NULL;
  }

  return pickled_obj;
}

static PyObject *recurse_pickle(PyObject *obj) {
  PyObject *pickled_obj = PyBytes_FromStringAndSize(NULL, 0);
  if (!pickled_obj) {
    return NULL;
  }

  if (obj == Py_None) {
    PyBytes_ConcatAndDel(&pickled_obj, encode_none());
    return pickled_obj;
  }

  for (int i = 0; i < sizeof(disbatch_table) / sizeof(disbatch_table[0]); i++) {
    if (disbatch_table[i].type != NULL &&
        PyObject_TypeCheck(obj, disbatch_table[i].type)) {
      PyObject *result = NULL;

      result = disbatch_table[i].func(obj);

      if (!result) {
        Py_DECREF(pickled_obj);
        return NULL;
      }

      PyBytes_ConcatAndDel(&pickled_obj, result);
      break;
    }
  }

  if (!pickled_obj) {
    PyErr_SetString(PyExc_TypeError, "Unsupported type for encoding.");
    return NULL;
  }

  return pickled_obj;
}

PyObject *merge_partials(PyObject *self, PyObject *args) {
  PyObject *obj1, *obj2;
  int no_memo = 0;
  int frame_info = 1;

  if (!PyArg_ParseTuple(args, "O!O!|pp", &PyBytes_Type, &obj1, &PyBytes_Type,
                        &obj2, &no_memo, &frame_info)) {
    return NULL;
  }

  if (PyBytes_Size(obj1) == 0 && PyBytes_Size(obj2) == 0) {
    PyErr_SetString(PyExc_ValueError, "Invalid Input: Un-mergable objects");
    return NULL;
  }

  PyObject *result = PyBytes_FromStringAndSize(NULL, 0);
  const char *identifier_1 = PyBytes_AsString(obj1);
  const char *identifier_2 = PyBytes_AsString(obj2);
  char identifier_1_byte = identifier_1[0];
  char identifier_2_byte = identifier_2[0];

  int identifier_1_count = 0;
  for (Py_ssize_t i = 0; i < PyBytes_Size(obj1); i++) {
    if (identifier_1[i] == identifier_1_byte) {
      identifier_1_count++;
    }
  }
  int identifier_2_count = 0;
  for (Py_ssize_t i = 0; i < PyBytes_Size(obj1); i++) {
    if (identifier_2[i] == identifier_2_byte) {
      identifier_2_count++;
    }
  }

  if ((identifier_1_byte == (char)0x8c || identifier_1_byte == 'X' ||
       identifier_1_byte == (char)0x8d) &&
      identifier_1_count == 1 &&
      (identifier_2_byte == (char)0x8c || identifier_2_byte == 'X' ||
       identifier_2_byte == (char)0x8d) &&
      identifier_2_count == 1) {
    result =
        merge_strings(obj1, PyBytes_FromStringAndSize(&identifier_1_byte, 1),
                      obj2, PyBytes_FromStringAndSize(&identifier_2_byte, 1));
  } else if ((identifier_1_byte == (char)0x8e || identifier_1_byte == 'B' ||
              identifier_1_byte == 'C') &&
             identifier_1_count == 1 &&
             (identifier_2_byte == (char)0x8e || identifier_2_byte == 'B' ||
              identifier_2_byte == 'C') &&
             identifier_2_count == 1) {
    result =
        merge_bytes(obj1, PyBytes_FromStringAndSize(&identifier_1_byte, 1),
                    obj2, PyBytes_FromStringAndSize(&identifier_2_byte, 1));
  } else {
    PyObject *concatted = PyBytes_FromStringAndSize(NULL, 0);
    if (!concatted) {
      Py_DECREF(result);
      return NULL;
    }

    PyBytes_Concat(&concatted, obj1);
    PyBytes_Concat(&concatted, obj2);

    PyObject *chunks = no_memo ? PyList_New(0) : get_chunks(concatted);
    if (chunks == NULL) {
      Py_DECREF(result);
      Py_DECREF(concatted);
      return NULL;
    }
    Py_INCREF(chunks);
    PyObject *temp_memo = no_memo ? PyDict_New() : get_memo(chunks);
    Py_DECREF(chunks);
    if (!temp_memo) {
      Py_DECREF(result);
      Py_DECREF(concatted);
      Py_DECREF(chunks);
      return NULL;
    }

    PyObject_Print(concatted, stdout, 0);

    if (PyBytes_Size(obj1) > 0 && PyBytes_Size(obj2) > 0 && frame_info) {
      Py_INCREF(temp_memo);
      result = listize(temp_memo, obj1, obj2);
      Py_DECREF(temp_memo);
    } else {
      result = concatted;
      PyBytes_ConcatAndDel(&result, PyBytes_FromString("."));
    }

    Py_DECREF(concatted);
    Py_DECREF(temp_memo);
  }

  PyObject *protocol_bytes =
      frame_info ? PyBytes_FromString("\x80\x04") : PyBytes_FromString("");

  PyObject *frame_bytes;
  unsigned long long size = (unsigned long long)PyBytes_Size(result);
  if (size >= 4 && frame_info) {
    unsigned char buffer[8];

    buffer[0] = (size & 0xFF);
    buffer[1] = (size >> 8) & 0xFF;
    buffer[2] = (size >> 16) & 0xFF;
    buffer[3] = (size >> 24) & 0xFF;
    buffer[4] = (size >> 32) & 0xFF;
    buffer[5] = (size >> 40) & 0xFF;
    buffer[6] = (size >> 48) & 0xFF;
    buffer[7] = (size >> 56) & 0xFF;

    frame_bytes = PyBytes_FromString("\x95");
    PyBytes_ConcatAndDel(&frame_bytes,
                         PyBytes_FromStringAndSize((const char *)buffer, 8));
  } else {
    frame_bytes = PyBytes_FromString("");
  }

  if (!frame_info) {
    Py_ssize_t result_size = PyBytes_Size(result);
    if (result_size > 0) {
      result =
          PyBytes_FromStringAndSize(PyBytes_AsString(result), result_size - 1);
    }
  }
  PyObject *final_result = PyBytes_FromStringAndSize(NULL, 0);
  if (!final_result) {
    return NULL;
  }
  PyBytes_ConcatAndDel(&final_result, protocol_bytes);
  PyBytes_ConcatAndDel(&final_result, frame_bytes);
  PyBytes_ConcatAndDel(&final_result, result);

  return final_result;
}

static PyObject *get_chunks(PyObject *obj) {
  if (!PyBytes_Check(obj)) {
    PyErr_SetString(PyExc_TypeError, "Expected a bytes object.");
    return NULL;
  }

  Py_ssize_t length = PyBytes_Size(obj);
  const char *data = PyBytes_AsString(obj);
  PyObject *chunks = PyList_New(0);
  if (!chunks) {
    return NULL;
  }

  Py_ssize_t left = 0;
  Py_ssize_t right = 1;

  while (right < length) {
    const char *curr_byte = data + left;

    if (memcmp(curr_byte, &SHORT_UNICODE, 1) == 0 ||
        memcmp(curr_byte, &SHORT_BINBYTES, 1) == 0) {
      right += (uint8_t)(data + right)[0] + 1;
    } else if (memcmp(curr_byte, &UNICODE, 1) == 0 ||
               memcmp(curr_byte, &BINBYTES, 1) == 0) {
      uint32_t size;
      memcpy(&size, data + right, 4);
      right += size + 1;
    } else if (memcmp(curr_byte, &LONG_UNICODE, 1) == 0 ||
               memcmp(curr_byte, &BINBYTES8, 1) == 0) {
      uint64_t size;
      memcpy(&size, data + right, 8);
      right += size + 1;
    } else if (memcmp(curr_byte, &EMPTY_LIST, 1) == 0) {
      right += 2;
    }

    while (right < length && in_indicators(data + left) &&
           !in_indicators(data + right)) {
      right++;
    }

    while (right >= length) {
      right--;
    }

    PyObject *chunk = PyBytes_FromStringAndSize(data + left, right - left);
    if (!chunk) {
      Py_DECREF(chunks);
      return NULL;
    }
    PyList_Append(chunks, chunk);
    Py_DECREF(chunk);
    left = right;
    right++;
  }

  return chunks;
}

static PyObject *get_memo(PyObject *chunks) {
  if (!PyList_Check(chunks)) {
    PyErr_SetString(PyExc_TypeError, "Expected a list of byte objects.");
    return NULL;
  }

  PyObject *new_memo = PyDict_New();
  if (!new_memo) {
    return NULL;
  }

  Py_ssize_t num_chunks = PyList_Size(chunks);
  for (Py_ssize_t i = 0; i < num_chunks; i++) {
    PyObject *chunk = PyList_GetItem(chunks, i);
    if (!chunk || !PyBytes_Check(chunk)) {
      continue;
    }

    if (PyBytes_Size(chunk) > 0 &&
        memcmp(PyBytes_AsString(chunk) + PyBytes_Size(chunk) - 1, &MEMO, 1) ==
            0 &&
        memcmp(PyBytes_AsString(chunk), &EMPTY_DICT, 1) != 0) {
      if (PyBytes_Size(chunk) > 1 &&
          memcmp(PyBytes_AsString(chunk) + PyBytes_Size(chunk) - 2, &TUPLE1,
                 1) >= 0 &&
          memcmp(PyBytes_AsString(chunk) + PyBytes_Size(chunk) - 2, &TUPLE3,
                 1) <= 0) {
        Py_INCREF(chunks);
        PyObject *extracted_tuple = extract_tuple(chunks, i);
        if (!extracted_tuple) {
          Py_DECREF(new_memo);
          return NULL;
        }
        if (extracted_tuple && !PyDict_Contains(new_memo, extracted_tuple)) {
          PyObject *size = PyLong_FromSize_t(PyDict_Size(new_memo) + 1);
          PyDict_SetItem(new_memo, extracted_tuple, size);
          Py_DECREF(size);
        }
        Py_DECREF(chunks);
        Py_DECREF(extracted_tuple);
        continue;
      }

      if (PyBytes_Size(chunk) > 0 &&
          memcmp(PyBytes_AsString(chunk), &MARK, 1) == 0) {
        Py_INCREF(chunks);
        PyObject *extracted_sequence = extract_sequence(chunks, i);
        if (!extracted_sequence) {
          Py_DECREF(new_memo);
          return NULL;
        }
        if (extracted_sequence &&
            !PyDict_Contains(new_memo, extracted_sequence)) {
          PyObject *size = PyLong_FromSize_t(PyDict_Size(new_memo) + 1);
          PyDict_SetItem(new_memo, extracted_sequence, size);
          Py_DECREF(size);
        }
        Py_DECREF(chunks);
        Py_DECREF(extracted_sequence);
        continue;
      }

      if (!PyDict_Contains(new_memo, chunk)) {
        PyObject *size = PyLong_FromSize_t(PyDict_Size(new_memo) + 1);
        PyDict_SetItem(new_memo, chunk, size);
        Py_DECREF(size);
      }
    } else if (PyBytes_Size(chunk) > 1 &&
               memcmp(PyBytes_AsString(chunk) + 1, &MEMO, 1) == 0) {
      Py_INCREF(chunks);
      PyObject *extracted_sequence = extract_sequence(chunks, i);
      if (!extracted_sequence) {
        Py_DECREF(new_memo);
        return NULL;
      }
      if (extracted_sequence &&
          !PyDict_Contains(new_memo, extracted_sequence)) {
        PyObject *size = PyLong_FromSize_t(PyDict_Size(new_memo) + 1);
        PyDict_SetItem(new_memo, extracted_sequence, size);
        Py_DECREF(size);
      }
      Py_DECREF(chunks);
      Py_DECREF(extracted_sequence);
      continue;
    }
  }

  return new_memo;
}

static PyObject *listize(PyObject *memory, PyObject *obj1, PyObject *obj2) {
  if (!PyDict_Check(memory) || !PyBytes_Check(obj1) || !PyBytes_Check(obj2)) {
    PyErr_SetString(PyExc_TypeError,
                    "Expected a dictionary and two bytes objects.");
    return NULL;
  }

  PyObject *combined = PyBytes_FromStringAndSize(NULL, 0);
  if (!combined) {
    return NULL;
  }

  PyBytes_Concat(&combined, obj1);
  PyBytes_Concat(&combined, obj2);

  PyObject *keys = PyDict_Keys(memory);
  if (!keys) {
    Py_DECREF(combined);
    return NULL;
  }

  Py_ssize_t num_keys = PyList_Size(keys);
  PyObject **key_array = (PyObject **)malloc(num_keys * sizeof(PyObject *));
  if (!key_array) {
    Py_DECREF(keys);
    Py_DECREF(combined);
    return NULL;
  }

  for (Py_ssize_t i = 0; i < num_keys; i++) {
    key_array[i] = PyList_GetItem(keys, i);
    Py_INCREF(key_array[i]);
  }

  qsort(key_array, num_keys, sizeof(PyObject *), compare_length);

  PyObject *result = PyBytes_FromStringAndSize(NULL, 0);
  if (!result) {
    free(key_array);
    Py_DECREF(keys);
    Py_DECREF(combined);
    return NULL;
  }

  char *result_buffer = PyBytes_AsString(result);
  Py_ssize_t result_size = 0;

  const char *curr = PyBytes_AsString(combined);
  Py_ssize_t combined_size = PyBytes_Size(combined);

  for (Py_ssize_t i = 0; i < num_keys; i++) {
    PyObject *memoized = key_array[i];
    PyObject *idx_obj = PyDict_GetItem(memory, memoized);
    PyObject *replacement = get(idx_obj);

    if (PyBytes_Size(memoized) > 0 && memcmp(memoized, &EMPTY_DICT, 1) == 0 &&
        memcmp(memoized, &EMPTY_LIST, 1) == 0) {
      Py_DECREF(replacement);
      continue;
    }

    if (replacement) {
      const char *memoized_str = PyBytes_AsString(memoized);
      Py_ssize_t memoized_len = PyBytes_Size(memoized);

      const char *replacement_str = PyBytes_AsString(replacement);
      Py_ssize_t replacement_len = PyBytes_Size(replacement);

      const char *start = curr;

      int first_occ = 1;

      while ((start = strstr(start, memoized_str)) != NULL) {
        Py_ssize_t seg_length = start - curr;

        PyObject *new_result = PyBytes_FromStringAndSize(NULL, 0);
        if (!new_result) {
          Py_DECREF(replacement);
          free(key_array);
          Py_DECREF(keys);
          Py_DECREF(combined);
          return NULL;
        }

        PyBytes_ConcatAndDel(&new_result, PyBytes_FromString(result_buffer));
        PyBytes_ConcatAndDel(&new_result,
                             PyBytes_FromStringAndSize(curr, combined_size));

        if (!first_occ) {
          PyBytes_ConcatAndDel(
              &new_result,
              PyBytes_FromStringAndSize(replacement_str, replacement_len));
        } else {
          PyBytes_ConcatAndDel(&new_result, PyBytes_FromStringAndSize(
                                                memoized_str, memoized_len));
        }

        result = new_result;
        result_buffer = PyBytes_AsString(result);

        if (first_occ) {
          first_occ = 0;
        }
        start += memoized_len;
        curr = start;
      }
    }
    Py_DECREF(replacement);
  }

  Py_ssize_t remaining_len =
      combined_size - (curr - PyBytes_AsString(combined));
  if (remaining_len > 0) {
    PyObject *new_result = PyBytes_FromStringAndSize(NULL, 0);
    if (!new_result) {
      free(key_array);
      Py_DECREF(keys);
      Py_DECREF(combined);
      return NULL;
    }

    PyBytes_ConcatAndDel(&new_result, PyBytes_FromString(result_buffer));
    PyBytes_ConcatAndDel(&new_result,
                         PyBytes_FromStringAndSize(curr, combined_size));

    result = new_result;
  }

  free(key_array);
  Py_DECREF(keys);
  Py_DECREF(combined);
  PyObject *new_res = PyBytes_FromStringAndSize(NULL, 0);
  if (!new_res) {
    return NULL;
  }
  PyBytes_ConcatAndDel(&new_res,
                       PyBytes_FromStringAndSize((const char *)&EMPTY_LIST, 1));
  PyBytes_ConcatAndDel(&new_res,
                       PyBytes_FromStringAndSize((const char *)&MEMO, 1));
  PyBytes_ConcatAndDel(&new_res,
                       PyBytes_FromStringAndSize((const char *)&MARK, 1));
  PyBytes_ConcatAndDel(&new_res, PyBytes_FromObject(result));
  PyBytes_ConcatAndDel(&new_res,
                       PyBytes_FromStringAndSize((const char *)&APPENDS, 1));
  PyBytes_ConcatAndDel(&new_res, PyBytes_FromStringAndSize(".", 1));

  return new_res;
}

int compare_length(const void *a, const void *b) {
  PyObject *obj_a = *(PyObject **)a;
  PyObject *obj_b = *(PyObject **)b;

  Py_ssize_t len_a = PyBytes_Size(obj_a);
  Py_ssize_t len_b = PyBytes_Size(obj_b);
  Py_DECREF(obj_a);
  Py_DECREF(obj_b);

  return (len_a < len_b) - (len_a > len_b);
}

static PyObject *extract_tuple(PyObject *chunks, Py_ssize_t idx) {
  int num_remains = 1;
  int curr_idx = idx;
  PyObject *res = PyBytes_FromStringAndSize(NULL, 0);
  if (!res) {
    return NULL;
  }

  while (num_remains > 0 && curr_idx >= 0) {
    PyObject *curr_chunk = PyList_GetItem(chunks, curr_idx);
    const char *chunk_data = PyBytes_AsString(curr_chunk);
    Py_ssize_t chunk_size = PyBytes_Size(curr_chunk);

    unsigned char last_byte = (unsigned char)chunk_data[chunk_size - 2];

    if (last_byte == 0x85) {
      num_remains += 1;
    } else if (last_byte == 0x86) {
      num_remains += 2;
    } else if (last_byte == 0x87) {
      num_remains += 3;
    }

    PyObject *new_res =
        PyBytes_FromStringAndSize(NULL, PyBytes_Size(res) + chunk_size);
    if (!new_res) {
      Py_DECREF(res);
      return NULL;
    }

    PyBytes_Concat(&new_res, res);
    PyBytes_ConcatAndDel(&new_res,
                         PyBytes_FromStringAndSize(chunk_data, chunk_size));

    res = new_res;

    curr_idx -= 1;
    num_remains -= 1;
  }

  return res;
}

static PyObject *extract_sequence(PyObject *chunks, Py_ssize_t idx) {
  int num_remains = 1;
  Py_ssize_t num_chunks = PyList_Size(chunks);
  const char *ident = PyBytes_AsString(PyList_GetItem(chunks, idx));
  int curr_idx = idx;
  PyObject *res = PyBytes_FromStringAndSize(NULL, 0);
  if (!res) {
    return NULL;
  }

  while (num_remains > 0 && curr_idx < num_chunks) {
    PyObject *curr_chunk = PyList_GetItem(chunks, curr_idx);
    const char *chunk_data = PyBytes_AsString(curr_chunk);
    Py_ssize_t chunk_size = PyBytes_Size(curr_chunk);

    if (curr_idx != idx && chunk_data[0] == ident[0]) {
      num_remains += 1;
    }

    if (chunk_data[0] == EMPTY_LIST) {
      int num_reduce = 0;
      for (Py_ssize_t i = chunk_size - 1; i >= 0; i--) {
        if (chunk_data[i] == APPEND || chunk_data[i] == APPENDS) {
          num_reduce += 1;
        } else if (chunk_data[i] == SETITEM || chunk_data[i] == SETITEMS) {
          continue;
        } else {
          break;
        }
      }
      num_remains -= num_reduce;
    } else if (chunk_data[0] == EMPTY_DICT) {
      int num_reduce = 0;
      for (Py_ssize_t i = chunk_size - 1; i >= 0; i--) {
        if (chunk_data[i] == SETITEM || chunk_data[i] == SETITEMS) {
          num_reduce += 1;
        } else if (chunk_data[i] == APPEND || chunk_data[i] == APPENDS) {
          continue;
        } else {
          break;
        }
      }
      num_remains -= num_reduce;
    } else if (chunk_data[0] == MARK) {
      if (chunk_size >= 2 && chunk_data[chunk_size - 2] == TUPLE) {
        num_remains -= 1;
      }
    }

    PyObject *new_res = PyBytes_FromStringAndSize(NULL, 0);
    if (!new_res) {
      Py_DECREF(res);
      return NULL;
    }

    PyBytes_Concat(&new_res, res);
    PyBytes_ConcatAndDel(&new_res,
                         PyBytes_FromStringAndSize(chunk_data, chunk_size));

    res = new_res;

    curr_idx += 1;
  }

  if (num_remains) {
    PyObject *new_res;
    if (ident[0] == EMPTY_LIST) {
      new_res = PyBytes_FromStringAndSize(NULL, 0);
      if (!new_res) {
        Py_DECREF(res);
        return NULL;
      }
      PyBytes_Concat(&new_res, res);
      PyBytes_ConcatAndDel(&new_res, PyBytes_FromStringAndSize("]\x94", 2));
    } else {
      new_res = PyBytes_FromStringAndSize(NULL, 0);
      if (!new_res) {
        Py_DECREF(res);
        return NULL;
      }
      PyBytes_Concat(&new_res, res);
      PyBytes_ConcatAndDel(&new_res, PyBytes_FromStringAndSize("}\x94", 2));
    }

    res = new_res;
  }

  return res;
}

static PyObject *get(PyObject *idx) {
  if (!PyLong_Check(idx)) {
    PyErr_SetString(PyExc_TypeError, "Expected an integer index.");
    return NULL;
  }

  PyObject *result = PyBytes_FromStringAndSize(NULL, 0);

  long index = PyLong_AsLong(idx);
  if (index == -1 && PyErr_Occurred()) {
    return NULL;
  }

  if (index < 256) {
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((const char *)&BINGET, 1));
  } else {
    PyBytes_ConcatAndDel(
        &result, PyBytes_FromStringAndSize((const char *)&LONG_BINGET, 1));
    unsigned int long_idx = (unsigned int)index;
    PyBytes_ConcatAndDel(&result, PyBytes_FromStringAndSize((char *)&long_idx,
                                                            sizeof(long_idx)));
    return result;
  }

  unsigned char byte_idx = (unsigned char)index;
  PyBytes_ConcatAndDel(
      &result, PyBytes_FromStringAndSize((char *)&byte_idx, sizeof(byte_idx)));

  return result;
}

static PyObject *merge_strings(PyObject *str_1, PyObject *identifier_1,
                               PyObject *str_2, PyObject *identifier_2) {
  if (!PyBytes_Check(str_1) || !PyBytes_Check(identifier_1) ||
      !PyBytes_Check(str_2) || !PyBytes_Check(identifier_2)) {
    PyErr_SetString(PyExc_TypeError, "Expected bytes objects.");
    return NULL;
  }

  Py_ssize_t len_bytes_1 =
      (PyBytes_Size(identifier_1) == 1 &&
       memcmp(PyBytes_AsString(identifier_1), "\x8c", 1) == 0)
          ? 1
      : (PyBytes_Size(identifier_1) == 1 &&
         memcmp(PyBytes_AsString(identifier_1), "X", 1) == 0)
          ? 4
          : 8;

  Py_ssize_t len_bytes_2 =
      (PyBytes_Size(identifier_2) == 1 &&
       memcmp(PyBytes_AsString(identifier_2), "\x8c", 1) == 0)
          ? 1
      : (PyBytes_Size(identifier_2) == 1 &&
         memcmp(PyBytes_AsString(identifier_2), "X", 1) == 0)
          ? 4
          : 8;

  PyObject *maintain_one =
      PyBytes_FromStringAndSize(PyBytes_AsString(str_1) + len_bytes_1 + 1,
                                PyBytes_Size(str_1) - len_bytes_1 - 2);

  PyObject *maintain_two =
      PyBytes_FromStringAndSize(PyBytes_AsString(str_2) + len_bytes_2 + 1,
                                PyBytes_Size(str_2) - len_bytes_2 - 2);

  if (!maintain_one || !maintain_two) {
    Py_XDECREF(maintain_one);
    Py_XDECREF(maintain_two);
    return NULL;
  }

  PyObject *result = PyBytes_FromStringAndSize(NULL, 0);
  if (!result) {
    Py_DECREF(maintain_one);
    Py_DECREF(maintain_two);
    return NULL;
  }

  Py_ssize_t length = PyBytes_Size(maintain_one) + PyBytes_Size(maintain_two);
  if (length < 256) {
    PyBytes_ConcatAndDel(
        &result, PyBytes_FromStringAndSize((const char *)&SHORT_UNICODE, 1));
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)&length, 1));
  } else if (length <= 0xFFFFFFFF) {
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((const char *)&UNICODE, 1));
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)&length, 4));
  } else {
    PyBytes_ConcatAndDel(
        &result, PyBytes_FromStringAndSize((const char *)&LONG_UNICODE, 1));
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)&length, 8));
  }

  PyBytes_ConcatAndDel(&result, maintain_one);
  PyBytes_ConcatAndDel(&result, maintain_two);
  PyBytes_ConcatAndDel(&result,
                       PyBytes_FromStringAndSize((const char *)&MEMO, 1));

  PyBytes_ConcatAndDel(&result, PyBytes_FromStringAndSize(".", 1));

  return result;
}

static PyObject *merge_bytes(PyObject *byte_str_1, PyObject *identifier_1,
                             PyObject *byte_str_2, PyObject *identifier_2) {
  if (!PyBytes_Check(byte_str_1) || !PyBytes_Check(identifier_1) ||
      !PyBytes_Check(byte_str_2) || !PyBytes_Check(identifier_2)) {
    PyErr_SetString(PyExc_TypeError, "Expected bytes objects.");
    return NULL;
  }

  Py_ssize_t len_bytes_1 =
      (PyBytes_Size(identifier_1) == 1 &&
       memcmp(PyBytes_AsString(identifier_1), "C", 1) == 0)
          ? 1
      : (PyBytes_Size(identifier_1) == 1 &&
         memcmp(PyBytes_AsString(identifier_1), "B", 1) == 0)
          ? 4
          : 8;

  Py_ssize_t len_bytes_2 =
      (PyBytes_Size(identifier_2) == 1 &&
       memcmp(PyBytes_AsString(identifier_2), "C", 1) == 0)
          ? 1
      : (PyBytes_Size(identifier_2) == 1 &&
         memcmp(PyBytes_AsString(identifier_2), "B", 1) == 0)
          ? 4
          : 8;

  PyObject *maintain_one =
      PyBytes_FromStringAndSize(PyBytes_AsString(byte_str_1) + len_bytes_1 + 1,
                                PyBytes_Size(byte_str_1) - len_bytes_1 - 2);

  PyObject *maintain_two =
      PyBytes_FromStringAndSize(PyBytes_AsString(byte_str_2) + len_bytes_2 + 1,
                                PyBytes_Size(byte_str_2) - len_bytes_2 - 2);

  if (!maintain_one || !maintain_two) {
    Py_XDECREF(maintain_one);
    Py_XDECREF(maintain_two);
    return NULL;
  }

  PyObject *result = PyBytes_FromStringAndSize(NULL, 0);
  if (!result) {
    Py_DECREF(maintain_one);
    Py_DECREF(maintain_two);
    return NULL;
  }

  Py_ssize_t length = PyBytes_Size(maintain_one) + PyBytes_Size(maintain_two);
  if (length < 256) {
    PyBytes_ConcatAndDel(
        &result, PyBytes_FromStringAndSize((const char *)&SHORT_BINBYTES, 1));
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)&length, 1));
  } else if (length <= 0xFFFFFFFF) {
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((const char *)&BINBYTES, 1));
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)&length, 4));
  } else {
    PyBytes_ConcatAndDel(
        &result, PyBytes_FromStringAndSize((const char *)&BINBYTES8, 1));
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)&length, 8));
  }

  PyBytes_ConcatAndDel(&result, maintain_one);
  PyBytes_ConcatAndDel(&result, maintain_two);
  PyBytes_ConcatAndDel(&result,
                       PyBytes_FromStringAndSize((const char *)&MEMO, 1));

  PyBytes_ConcatAndDel(&result, PyBytes_FromStringAndSize(".", 1));

  return result;
}

static PyObject *encode_none(void) {
  return PyBytes_FromStringAndSize((const char *)&NONE, sizeof(NONE));
}

static PyObject *encode_bool(PyObject *obj) {
  if (!PyBool_Check(obj)) {
    PyErr_SetString(PyExc_TypeError, "Expected a bool type.");
    return NULL;
  };

  if (obj == Py_True) {
    return PyBytes_FromStringAndSize((const char *)&TRUE, 1);
  } else {
    return PyBytes_FromStringAndSize((const char *)&FALSE, 1);
  }
}

static PyObject *encode_string(PyObject *obj) {
  if (!PyUnicode_Check(obj)) {
    PyErr_SetString(PyExc_TypeError, "Expected a string");
    return NULL;
  }

  PyObject *utf_string_obj =
      PyUnicode_AsEncodedString(obj, "utf-8", "surrogatepass");

  if (!utf_string_obj) {
    return NULL;
  }

  Py_ssize_t length = PyBytes_Size(utf_string_obj);
  char *utf_string = PyBytes_AsString(utf_string_obj);

  PyObject *result = PyBytes_FromStringAndSize(NULL, 0);
  if (!result) {
    Py_DECREF(utf_string_obj);
    return NULL;
  }

  if (length < 256) {
    PyBytes_ConcatAndDel(
        &result, PyBytes_FromStringAndSize((const char *)&SHORT_UNICODE, 1));
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)&length, 1));
  } else if (length > 0xFFFFFFFFF) {
    PyBytes_ConcatAndDel(
        &result, PyBytes_FromStringAndSize((const char *)&LONG_UNICODE, 1));
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)&length, 8));
  } else {
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((const char *)&UNICODE, 1));
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)&length, 4));
  }

  PyBytes_ConcatAndDel(&result, PyBytes_FromStringAndSize(utf_string, length));

  PyBytes_ConcatAndDel(&result,
                       PyBytes_FromStringAndSize((const char *)&MEMO, 1));

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
  if (!result) {
    return NULL;
  }

  unsigned char packed_float[8];
  memcpy(packed_float, &value, sizeof(double));

  if (__BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__) {
    for (int i = 0; i < sizeof(double) / 2; i++) {
      unsigned char temp = packed_float[i];
      packed_float[i] = packed_float[sizeof(double) - 1 - i];
      packed_float[sizeof(double) - 1 - i] = temp;
    }
  }

  PyBytes_ConcatAndDel(&result,
                       PyBytes_FromStringAndSize((const char *)&BINFLOAT, 1));
  PyBytes_ConcatAndDel(&result,
                       PyBytes_FromStringAndSize((char *)packed_float, 8));

  return result;
}

static PyObject *encode_long(PyObject *obj) {
  if (!PyLong_Check(obj)) {
    PyErr_SetString(PyExc_TypeError, "Expected an integer.");
    return NULL;
  }

  long long value = PyLong_AsLongLong(obj);
  if (value == -1 && PyErr_Occurred()) {
    return NULL;
  }

  PyObject *result = PyBytes_FromStringAndSize(NULL, 0);
  if (!result) {
    return NULL;
  }

  if (value >= 0) {
    if (value <= 0xFF) {
      PyBytes_ConcatAndDel(
          &result, PyBytes_FromStringAndSize((const char *)&BININT1, 1));
      unsigned char byte_value = (unsigned char)value;
      PyBytes_ConcatAndDel(&result,
                           PyBytes_FromStringAndSize((char *)&byte_value, 1));
      return result;
    } else if (value <= (int)0xFFFF) {
      PyBytes_ConcatAndDel(
          &result, PyBytes_FromStringAndSize((const char *)&BININT2, 1));
      unsigned short short_value = (unsigned short)value;
      PyBytes_ConcatAndDel(&result,
                           PyBytes_FromStringAndSize((char *)&short_value, 2));
      return result;
    } else if (value <= (int)0x7FFFFFFF) {
      PyBytes_ConcatAndDel(&result,
                           PyBytes_FromStringAndSize((const char *)&BININT, 1));
      int int_value = (int)value;
      PyBytes_ConcatAndDel(&result,
                           PyBytes_FromStringAndSize((char *)&int_value, 4));
      return result;
    }
  }

  if (value < 0) {
    if (value >= (int)-0x80000000) {
      PyBytes_ConcatAndDel(&result,
                           PyBytes_FromStringAndSize((const char *)&BININT, 1));
      int int_value = (int)value;
      PyBytes_ConcatAndDel(&result,
                           PyBytes_FromStringAndSize((char *)&int_value, 4));
      return result;
    }
  }

  long abs_value = value >= 0 ? value : -value;
  int num_bytes = abs_value != 0 ? 0 : 1;

  while (abs_value > 0) {
    abs_value >>= 8;
    num_bytes++;
  }

  const char *encoded_long = PyBytes_AsString(obj);
  Py_ssize_t encoded_len = PyBytes_Size(obj);
  if (encoded_len < 0) {
    return NULL;
  }

  PyObject *long_result;
  if (value < 0 && num_bytes > 1 &&
      (encoded_long[encoded_len - 1] == (char)0xFF &&
       (encoded_long[encoded_len - 2] & (char)0x80) != 0)) {
    long_result = PyBytes_FromStringAndSize(encoded_long, encoded_len - 1);
  } else {
    long_result = PyBytes_FromStringAndSize(encoded_long, encoded_len);
  }

  if (num_bytes < 256) {
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((const char *)&LONG1, 1));
    unsigned char length_byte = (unsigned char)num_bytes;
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)&length_byte, 1));
  } else {
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((const char *)&LONG4, 1));
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)&num_bytes, 4));
  }

  PyBytes_ConcatAndDel(&result, long_result);

  return result;
}

static PyObject *encode_bytes(PyObject *obj) {
  if (!PyBytes_Check(obj)) {
    PyErr_SetString(PyExc_TypeError, "Expected a bytes type.");
    return NULL;
  }

  PyObject *bytes_obj = PyBytes_FromObject(obj);
  if (!bytes_obj) {
    return NULL;
  }

  Py_ssize_t length = PyBytes_Size(bytes_obj);
  char *bytes_str = PyBytes_AsString(bytes_obj);

  PyObject *result = PyBytes_FromStringAndSize(NULL, 0);
  if (!result) {
    Py_DECREF(bytes_obj);
    return NULL;
  }

  if (length < 256) {
    PyBytes_ConcatAndDel(
        &result, PyBytes_FromStringAndSize((const char *)&SHORT_BINBYTES, 1));
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)&length, 1));
  } else if (length > 0xFFFFFFFFF) {
    PyBytes_ConcatAndDel(
        &result, PyBytes_FromStringAndSize((const char *)&BINBYTES8, 1));
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)&length, 8));
  } else {
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((const char *)&BINBYTES, 1));
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((char *)&length, 4));
  }

  PyBytes_ConcatAndDel(&result, PyBytes_FromStringAndSize(bytes_str, length));

  PyBytes_ConcatAndDel(&result,
                       PyBytes_FromStringAndSize((const char *)&MEMO, 1));

  Py_DECREF(bytes_obj);

  return result;
}

static PyObject *encode_tuple(PyObject *obj) {
  if (!PyTuple_Check(obj)) {
    PyErr_SetString(PyExc_TypeError, "Expected a tuple.");
    return NULL;
  }

  Py_ssize_t length = PyTuple_Size(obj);

  PyObject *result = PyBytes_FromStringAndSize(NULL, 0);
  if (!result) {
    return NULL;
  }

  if (length == 0) {
    return PyBytes_FromStringAndSize((const char *)&EMPTY_TUPLE, 1);
  }

  if (length > 3) {
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((const char *)&MARK, 1));
  }

  for (Py_ssize_t i = 0; i < length; i++) {
    PyObject *item = PyTuple_GetItem(obj, i);
    Py_INCREF(item);
    PyObject *encoded = recurse_pickle(item);
    Py_DECREF(item);
    item = NULL;
    if (!encoded) {
      Py_DECREF(result);
      return NULL;
    }

    PyObject *encoded_bytes = PyBytes_FromObject(encoded);
    Py_DECREF(encoded);
    if (!encoded_bytes) {
      Py_DECREF(result);
      return NULL;
    }

    PyBytes_ConcatAndDel(&result, encoded_bytes);
  }

  switch (length) {
  case 1:
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((const char *)&TUPLE1, 1));
    break;
  case 2:
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((const char *)&TUPLE2, 1));
    break;
  case 3:
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((const char *)&TUPLE3, 1));
    break;
  default:
    PyBytes_ConcatAndDel(&result,
                         PyBytes_FromStringAndSize((const char *)&TUPLE, 1));
    break;
  }

  PyBytes_ConcatAndDel(&result,
                       PyBytes_FromStringAndSize((const char *)&MEMO, 1));

  return result;
}

static PyObject *encode_list(PyObject *obj) {
  if (!PyList_Check(obj)) {
    PyErr_SetString(PyExc_TypeError, "Expected a list");
    return NULL;
  }

  Py_ssize_t length = PyList_Size(obj);
  PyObject *result = PyBytes_FromStringAndSize(NULL, 0);
  if (!result) {
    return NULL;
  }

  PyBytes_ConcatAndDel(&result,
                       PyBytes_FromStringAndSize((const char *)&EMPTY_LIST, 1));

  PyBytes_ConcatAndDel(&result,
                       PyBytes_FromStringAndSize((const char *)&MEMO, 1));

  Py_ssize_t idx = 0;

  while (idx < length) {
    Py_ssize_t n = (length - idx > 1000) ? 1000 : (length - idx);

    if (n > 1) {
      PyBytes_ConcatAndDel(&result,
                           PyBytes_FromStringAndSize((const char *)&MARK, 1));

      for (Py_ssize_t j = 0; j < n; j++) {
        PyObject *item = PyList_GetItem(obj, idx + j);
        Py_INCREF(item);
        PyObject *encoded_item = recurse_pickle(item);
        Py_DECREF(item);
        item = NULL;
        if (!encoded_item) {
          Py_DECREF(result);
          return NULL;
        }

        PyObject *encoded = PyBytes_FromObject(encoded_item);
        Py_DECREF(encoded_item);
        if (!encoded) {
          Py_DECREF(result);
          return NULL;
        }

        PyBytes_ConcatAndDel(&result, encoded);
      }
      PyBytes_ConcatAndDel(
          &result, PyBytes_FromStringAndSize((const char *)&APPENDS, 1));
    } else if (n == 1) {
      PyObject *item = PyList_GetItem(obj, idx);
      Py_INCREF(item);
      PyObject *encoded_item = recurse_pickle(item);
      Py_DECREF(item);
      item = NULL;
      if (!encoded_item) {
        Py_DECREF(result);
        return NULL;
      }

      PyObject *encoded = PyBytes_FromObject(encoded_item);
      Py_DECREF(encoded_item);
      if (!encoded) {
        Py_DECREF(result);
        return NULL;
      }

      PyBytes_ConcatAndDel(&result, encoded);
      PyBytes_ConcatAndDel(&result,
                           PyBytes_FromStringAndSize((const char *)&APPEND, 1));
    }

    idx += n;
  }

  return result;
}

static PyObject *encode_dict(PyObject *obj) {
  if (!PyDict_Check(obj)) {
    PyErr_SetString(PyExc_TypeError, "Expected a dictionary.");
    return NULL;
  }

  PyObject *dict_items = PyDict_Items(obj);
  if (!dict_items) {
    return NULL;
  }

  Py_ssize_t length = PyList_Size(dict_items);
  PyObject *result = PyBytes_FromStringAndSize(NULL, 0);
  if (!result) {
    return NULL;
  }

  PyBytes_ConcatAndDel(&result,
                       PyBytes_FromStringAndSize((const char *)&EMPTY_DICT, 1));
  PyBytes_ConcatAndDel(&result,
                       PyBytes_FromStringAndSize((const char *)&MEMO, 1));

  Py_ssize_t idx = 0;
  while (idx < length) {
    Py_ssize_t n = (length - idx > 1000) ? 1000 : (length - idx);

    if (n > 1) {
      PyBytes_ConcatAndDel(&result,
                           PyBytes_FromStringAndSize((const char *)&MARK, 1));

      for (Py_ssize_t j = 0; j < n; j++) {
        PyObject *kv_pair = PyList_GetItem(dict_items, idx + j);
        if (!kv_pair || !PyTuple_Check(kv_pair) || PyTuple_Size(kv_pair) != 2) {
          Py_DECREF(result);
          Py_DECREF(dict_items);
          return NULL;
        }

        PyObject *key = PyTuple_GetItem(kv_pair, 0);
        PyObject *value = PyTuple_GetItem(kv_pair, 1);
        Py_DECREF(kv_pair);
        kv_pair = NULL;
        if (!key || !value) {
          Py_DECREF(result);
          Py_DECREF(dict_items);
          return NULL;
        }

        Py_INCREF(key);
        Py_INCREF(value);
        PyObject *encoded_key = recurse_pickle(key);
        PyObject *encoded_value = recurse_pickle(value);
        Py_DECREF(key);
        Py_DECREF(value);
        key = NULL;
        value = NULL;
        if (!encoded_key || !encoded_value) {
          Py_DECREF(result);
          Py_DECREF(dict_items);
          Py_XDECREF(encoded_key);
          Py_XDECREF(encoded_value);
          return NULL;
        }

        PyObject *encoded_one = PyBytes_FromObject(encoded_key);
        PyObject *encoded_two = PyBytes_FromObject(encoded_value);
        Py_DECREF(encoded_key);
        Py_DECREF(encoded_value);
        encoded_key = NULL;
        encoded_value = NULL;
        if (!encoded_one || !encoded_two) {
          Py_DECREF(result);
          Py_DECREF(dict_items);
          Py_XDECREF(encoded_one);
          Py_XDECREF(encoded_two);
          return NULL;
        }

        PyBytes_ConcatAndDel(&result, encoded_one);
        PyBytes_ConcatAndDel(&result, encoded_two);
      }
      PyBytes_ConcatAndDel(
          &result, PyBytes_FromStringAndSize((const char *)&SETITEMS, 1));
    } else if (n == 1) {
      PyObject *kv_pair = PyList_GetItem(dict_items, idx);
      if (!kv_pair || !PyTuple_Check(kv_pair) || PyTuple_Size(kv_pair) != 2) {
        Py_DECREF(result);
        Py_DECREF(dict_items);
        return NULL;
      }

      PyObject *key = PyTuple_GetItem(kv_pair, 0);
      PyObject *value = PyTuple_GetItem(kv_pair, 1);
      Py_DECREF(kv_pair);
      kv_pair = NULL;
      if (!key || !value) {
        Py_DECREF(result);
        Py_DECREF(dict_items);
        return NULL;
      }

      Py_INCREF(key);
      Py_INCREF(value);
      PyObject *encoded_key = recurse_pickle(key);
      PyObject *encoded_value = recurse_pickle(value);
      Py_DECREF(key);
      Py_DECREF(value);
      key = NULL;
      value = NULL;
      if (!encoded_key || !encoded_value) {
        Py_DECREF(result);
        Py_DECREF(dict_items);
        Py_XDECREF(encoded_key);
        Py_XDECREF(encoded_value);
        return NULL;
      }

      PyObject *encoded_one = PyBytes_FromObject(encoded_key);
      PyObject *encoded_two = PyBytes_FromObject(encoded_value);
      Py_DECREF(encoded_key);
      Py_DECREF(encoded_value);
      encoded_key = NULL;
      encoded_value = NULL;
      if (!encoded_one || !encoded_two) {
        Py_DECREF(result);
        Py_DECREF(dict_items);
        Py_XDECREF(encoded_one);
        Py_XDECREF(encoded_two);
        return NULL;
      }

      PyBytes_ConcatAndDel(&result, encoded_one);
      PyBytes_ConcatAndDel(&result, encoded_two);
      PyBytes_ConcatAndDel(
          &result, PyBytes_FromStringAndSize((const char *)&SETITEM, 1));
    }

    idx += n;
  }

  Py_DECREF(dict_items);

  return result;
}

static PyMethodDef SeaPickleMethods[] = {
    {"partial_pickle", partial_pickle, METH_VARARGS, "encode an object"},
    {"merge_partials", merge_partials, METH_VARARGS, "merge encoded objects"},
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef seapicklemodule = {PyModuleDef_HEAD_INIT,
                                             "sea_pickle", "a true sea pickle",
                                             -1, SeaPickleMethods};

PyMODINIT_FUNC PyInit_sea_pickle(void) {
  return PyModule_Create(&seapicklemodule);
}
