#!/bin/sh
set -e
DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT=/tmp/ca
mkdir -p "$OUT"
if [ ! -x "$OUT/craft-anything-cli" ]; then
  cp -f "$DIR/bin/craft-anything-cli" "$OUT/craft-anything-cli"
  chmod +x "$OUT/craft-anything-cli"
fi
"$OUT/craft-anything-cli" --version | head -1