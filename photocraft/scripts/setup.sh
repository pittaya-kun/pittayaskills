#!/bin/sh
set -e
DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT=/tmp/pc
mkdir -p "$OUT"
if [ ! -x "$OUT/photocraft-cli" ]; then
  cp -f "$DIR/bin/photocraft-cli" "$OUT/photocraft-cli"
  chmod +x "$OUT/photocraft-cli"
fi
"$OUT/photocraft-cli" --version | head -1
