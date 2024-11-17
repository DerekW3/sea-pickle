
# Table of Contents

- [Table of Contents](#table-of-contents)
  - [sea-pickle](#sea-pickle)
  - [Setup](#setup)
    - [py\_pickle](#py_pickle)
    - [sea\_pickle](#sea_pickle)
  - [Usage Instructions](#usage-instructions)
    - [Testing](#testing)
    - [General Usage](#general-usage)
  - [Design Decisions](#design-decisions)
  - [Algorithm Analysis](#algorithm-analysis)
  - [Future Possibilities](#future-possibilities)

## sea-pickle

A C implementation of the python pickle serialization function. This includes two implementations, one in pure python under the py_pickle/ directory and one with a C-Python interface under the sea_pickle/ directory.

## Setup

To setup and run the modules follow the following instructions:

### py_pickle

1. Ensure that Python >= 3.8 is installed
2. Ensure that pip is installed
3. run the following commands

    ```sh
    cd py_pickle
    pip install .
    ```

### sea_pickle

1. Ensure that Python >= 3.8 is installed
2. Ensure that pip is installed
3. Ensure that the *clang* compiler version 10 or later is installed, check with the following command

    ```sh
    clang --version
    ```

4. Ensure that the Python header files are within your $PATH. If on mac, these come with xcode tools but you may need to export them in your .zshrc, .bash etc. file. Refer to [this page](https://stackoverflow.com/questions/74419576/python-h-file-not-found-on-macosx-how-to-fix-this) for help if needed.
5. Run the following commands to get setup

    ```sh
    cd sea_pickle # enter the sea_pickle directory
    pip install . # install base requirements (pytest, setuptools)
    ./scripts/build_script.sh # run setuptools building protocol
    ```

>[!WARNING]
> If the setup script fails due to an access permission, run the following command ```chmod +x scripts/build_script.sh``` and run the third command again. If once again failing, default to the following base commands of which the script consists
>
> ```sh
>python setup.py clean --all # clean all previous setuptools binaries
>
>rm -rf ./build ./sea_pickle.egg-info # remove previous build directories
>
>python setup.py build # build the extension with setuptools
>
>pip install . # install the extension locally
> ```

## Usage Instructions

### Testing

Testing is operated with pytest, with the tests being under the tests/ directory. Tests can be run in the console with the following command

```sh
pytest -vv ./tests/test_sea_pickle.py
```

>[!NOTE]
> Ensure that pytest is installed and if using a venv ensure that it is activated in the terminal.

### General Usage

This API consists of two functions, those being *partial_pickle* and *merge_partials*. These can be imported from the C module with the following code

```python
from typing import Callable

import sea_pickle

partial_pickle: Callable = sea_pickle.partial_pickle
merge_partials: Callable = sea_pickle.merge_partials
```

These functions have the following signatures

```python
partial_pickle(Any) -> bytes

merge_partials(bytes, bytes, Optional[bool]) -> bytes
```

partial_pickle accepts any type of python object besides sets, bytearrays and custom types. This is due to memoization constrictions which limit the algorithm and its speed. partial_pickle does *NOT* return a result equivalent to that of pickle.dumps, as it is of a special un-memoized form fit for merging.

merge_partials accepts two bytes objects, which each *must* be the result of a call to partial_pickle, and a boolean frame_info which defaults to True. If frame_info is true, the output of the function will be equivalent to that of pickle.dumps, however, if it is set to false it is assumed that this is an intermediary phase and will be merged again in the future. Below are the two use cases displayed

```python
# correct base case usage
assert merge_partials(
    partial_pickle((1, "a", (2, "b"))), partial_pickle((3, "c", (4, "d")))
) == pickle.dumps([(1, "a", (2, "b")), (3, "c", (4, "d"))])

# incorrect usage of frame_info
assert merge_partials(partial_pickle((300, 400)), partial_pickle([500, 600]), False) == pickle.dumps([(300, 400), [500, 600]])

# correct usage of frame_info, which allows for divide and conquer algorithm usage.
assert merge_partials(
    partial_pickle([100, 200]),
    merge_partials(partial_pickle((300, 400)), partial_pickle([500, 600]), False),
) == pickle.dumps([[100, 200], (300, 400), [500, 600]])
```

Default behavior depends on the type of pickled objects:

- Two Strings/Two Bytes Objects: Merge strings into one

    ```python
    assert merge_partials(
        partial_pickle("Test string with spaces"), partial_pickle(" and more text.")
    ) == pickle.dumps("Test string with spaces and more text.")
    
    assert merge_partials(
        partial_pickle(b"Byte string with spaces "), partial_pickle(b"and more bytes.")
    ) == pickle.dumps(b"Byte string with spaces and more bytes.")
    ```

- Two Inhomogenous Types/Two Non-Stringlike Types: Merge into a list containing the two objects

    ```python
    assert merge_partials(
        partial_pickle(1.23456789), partial_pickle(9.87654321)
    ) == pickle.dumps([1.23456789, 9.87654321])
    
    assert merge_partials(
        partial_pickle([1, 2.5, 3]), partial_pickle([4.0, 5, 6])
    ) == pickle.dumps([[1, 2.5, 3], [4.0, 5, 6]])
    ```

>[!WARNING]
> merge_partials does *NOT* support memoization. A lot of time was dedicated to it, and I might implement it in the future, but memoization is not very memory safe and is actually slower than the base pickle algorithm. This is explained further in [Algorithm Analysis](#algorithm-analysis). What does this mean for the end user? You cannot merge_partials for the following objects:
> ```python
> # sequences with repetitive string-like entries (this applies recursively as well)
> ["hello", "I", "dont", "repeat"] -> correct usage
> ["hello", "I", "want", "to", "be", "memoized", "to", "bytes"] -> incorrect usage
>                         ^ first usage           ^ second usage
> 
> # sequences with repetitive tuple entries (lists and dictionaries are fine though)
> [(1, 2, 3), (4, 5, 6)] -> correct usage
> [(1, 2, 3), (1, 2, 3)] -> incorrect usage
> ```
## Design Decisions
The current implementation utilizes setuptools (which is the standard), pytest for testing (cleaner than unittest), and C for the extension module. The module was designed in such a way to favor parallel programming capabilities, hence the *frame_info* tuple which allows for a large list to be subdivided, and then sequentially merged, all in $O(n)$ complexity, allowing for quick matrix encoding. String-like objects are automatically merged, meaning that the efficiency is essentially equal to that of the base pickle module, but large strings can be divided into smaller units and disbatched accordingly. To learn more about the specifics of the algorithm refer to [Algorithm Analysis](#algorithm-analysis).

## Algorithm Analysis
The partial_pickle algorithm follows the same steps as the base pickling algorithm, however it is automatically defaulted to the pickling protocol 4 and is without memoization, meaning that the runtime of both of these algorithms is $O(n)$, however the memory on partial_pickle is $O(1)$ while the memory of pickle.dumps can be as large as $O(n)$ due to the underlying dictionary.

merge_partials runs in $O(1)$ time complexity and memory due to the lack of need for memoization. To implement the memoization process, the passed encoded objects would need to be parsed into individual objects ($O(n)$), saved into a dictionary ($O(n)$), sorted by size as to allow for proper encoding ($O(nlog(n))$), and encoded into the final product $O(n)/O(n^2)$. This alone costs a whopping $O(n + nlog(n))$ and $O(n)$ memory, both with unfavorable coefficients giving us a *best case* runtime of $O(3n + log(n))$, but going as extreme as $O(n^2 + nlog(n))$ in the case that all of the objects are memoizable and repetitive, thus costing a large amount of time in the looping process where the memoized objects would be switched with their encoded alternatives. Therefore this algorithm, even in parallel, is extremely ill-conditioned and should not be switched out for the base pickling algorithm which would run in $O(n)$ time and complexity.

Therefore, I made the decision to leave that type of encoding to the base pickling algorithm, and instead focus on the encoding where this algorithm offers major efficiency boosts with parallelization, those of large string-likes and sequences of 2D or greater.

## Future Possibilities
I would like to implement a future mediary method which could take in any type of python object, determine it's type and size, and disbatch the work out either to partial_pickle and merge_partials with an optimized number of threads/processes or to the base pickling algorithm (where it is more efficient), allowing for a simpler interface for users just to import that one function and to expect it to work the same way that pickle.dumps does.