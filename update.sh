#!/bin/bash

BASE_DIR="$PWD/isocodes"

SHARE_DIR="$PWD"/isocodes/share

UPSTREAM_DIR=$PWD/vendor/iso-codes

rm -rf "$SHARE_DIR"

cd "$UPSTREAM_DIR" || exit

git pull

git checkout v4.15.0

./configure --prefix "$BASE_DIR"

make clean

make uninstall

make

make install
