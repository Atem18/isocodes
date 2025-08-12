#!/bin/bash

BASE_DIR="$PWD/isocodes"

SHARE_DIR="$PWD"/isocodes/share

UPSTREAM_DIR=$PWD/iso-codes

rm -rf "$SHARE_DIR"

rm -rf "$UPSTREAM_DIR"

git clone https://salsa.debian.org/iso-codes-team/iso-codes.git

cd "$UPSTREAM_DIR" || exit

git checkout v4.18.0

./configure --prefix "$BASE_DIR"

make clean

make uninstall

make

make install

rm -rf $UPSTREAM_DIR

rm -rf "$SHARE_DIR/json/schema-*"

rm -rf "$SHARE_DIR/pkgconfig"

rm -rf "$SHARE_DIR/xml"