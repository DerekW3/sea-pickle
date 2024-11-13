#!/bin/bash

echo "Building project..."
python setup.py clean --all

echo "Installing packages..."
pip install .