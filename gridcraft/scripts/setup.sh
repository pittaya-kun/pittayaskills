#!/bin/sh
set -e
DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT=/tmp/gc
mkdir -p "$OUT"
if [ ! -x "$OUT/gridcraft-cli" ]; then
  cp -f "$DIR/bin/gridcraft-cli" "$OUT/gridcraft-cli"
  chmod +x "$OUT/gridcraft-cli"
fi
"$OUT/gridcraft-cli" --version | head -1
