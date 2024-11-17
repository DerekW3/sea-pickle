#!/bin/bash

echo "Cleaning project..."
python setup.py clean --all

echo "Deleting dirs..."
rm -rf ./build ./sea_pickle.egg-info

echo "Building project..."
python setup.py build

echo "Installing packages..."
pip install .