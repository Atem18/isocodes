#!/bin/bash

BASE_DIR="$PWD/isocodes"

SHARE_DIR="$PWD"/isocodes/share

UPSTREAM_DIR=$PWD/vendor/iso-codes

rm -rf "$SHARE_DIR"

rm -rf "$UPSTREAM_DIR"

git submodule update --init --recursive

cd "$UPSTREAM_DIR" || exit

git checkout v4.16.0

./configure --prefix "$BASE_DIR"

make clean

make uninstall

make

make install
