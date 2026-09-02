#!/bin/bash
#
# Refresh the bundled ISO data from Debian's upstream iso-codes repository.
#
# Upstream dropped autotools in 4.19.0 and builds with meson now, so this
# script needs meson and ninja rather than ./configure && make.
#
# Requires: git, meson, ninja
# Usage:    ./update.sh [tag]        # defaults to the version pinned below

set -euo pipefail

ISO_CODES_VERSION="${1:-v4.20.1}"
UPSTREAM_URL="https://salsa.debian.org/iso-codes-team/iso-codes.git"

BASE_DIR="$PWD/isocodes"
SHARE_DIR="$BASE_DIR/share"

if [ ! -d "$BASE_DIR" ]; then
    echo "error: run this from the repository root (no $BASE_DIR directory)" >&2
    exit 1
fi

for tool in git meson ninja; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "error: '$tool' is required but not installed" >&2
        exit 1
    fi
done

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

echo "==> Cloning iso-codes $ISO_CODES_VERSION"
git -c advice.detachedHead=false clone --quiet --depth 1 \
    --branch "$ISO_CODES_VERSION" "$UPSTREAM_URL" "$WORK_DIR/iso-codes"

echo "==> Configuring build"
meson setup "$WORK_DIR/build" "$WORK_DIR/iso-codes" --prefix "$BASE_DIR" >/dev/null

echo "==> Replacing $SHARE_DIR"
rm -rf "$SHARE_DIR"
meson install -C "$WORK_DIR/build" >/dev/null

# Drop what the Python package does not ship: JSON schemas, the pkg-config
# file, and the deprecated XML representations of the same data.
echo "==> Pruning unshipped files"
rm -f  "$SHARE_DIR"/iso-codes/json/schema-*.json
rm -rf "$SHARE_DIR/pkgconfig"
rm -rf "$SHARE_DIR/xml"

# Upstream also installs each catalogue a second time under an obsolete name
# (iso_3166.mo -> iso_3166-1.mo and friends). They are symlinks here, but a
# wheel materialises them into full copies, which doubled the package size.
find "$SHARE_DIR/locale" -type l -delete

echo "==> Done: $(find "$SHARE_DIR/iso-codes/json" -name '*.json' | wc -l | tr -d ' ') data files, $(find "$SHARE_DIR/locale" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ') locales"
