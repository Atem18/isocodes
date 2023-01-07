#!/bin/bash

python -m piptools compile --resolver=backtracking \
    --extra dev \
    -o dev-requirements.txt \
    pyproject.toml

python -m piptools compile --resolver=backtracking \
    --extra doc \
    -o doc-requirements.txt \
    pyproject.toml

python -m piptools compile --resolver=backtracking \
    --extra doc \
    -o test-requirements.txt \
    pyproject.toml

python -m piptools compile --resolver=backtracking \
    --extra doc \
    -o requirements.txt \
    pyproject.toml

BASE_DIR="$PWD/isocodes"

SHARE_DIR="$PWD"/isocodes/share

UPSTREAM_DIR=$PWD/vendor/iso-codes

rm -rf "$SHARE_DIR"

cd "$UPSTREAM_DIR" || exit

git pull

git checkout v4.12.0

./configure --prefix "$BASE_DIR"

make clean

make uninstall

make

make install
