
# Table of Contents
- [Table of Contents](#table-of-contents)
  - [sea-pickle](#sea-pickle)
  - [Setup](#setup)
    - [py\_pickle](#py_pickle)
    - [sea\_pickle](#sea_pickle)
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
> ```sh
>python setup.py clean --all # clean all previous setuptools binaries
>
>rm -rf ./build ./sea_pickle.egg-info # remove previous build directories
>
>python setup.py build # build the extension with setuptools
>
>pip install . # install the extension locally
> ```

## Design Decisions

## Algorithm Analysis

## Future Possibilities