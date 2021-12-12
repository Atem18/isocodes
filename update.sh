#!/bin/bash

BASE_DIR=$PWD/vendor/iso-codes

cd "$BASE_DIR" || exit

git pull origin main

./configure "$BASE_DIR"

make clean

make uninstall

make

make install