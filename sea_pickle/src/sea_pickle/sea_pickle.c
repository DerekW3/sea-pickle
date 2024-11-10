#include "sea_pickle.h"
#include <modsupport.h>
#include <object.h>

PyObject *partial_pickle(PyObject *self, PyObject *args) {
  PyObject *obj;

  if (!PyArg_ParseTuple(args, "O", &obj)) {
    return NULL;
  }

  Py_RETURN_NONE;
}