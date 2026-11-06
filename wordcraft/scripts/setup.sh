#!/bin/sh
set -e
DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT=/tmp/wc
mkdir -p "$OUT"
if [ ! -x "$OUT/wordcraft-cli" ]; then
  cp -f "$DIR/bin/wordcraft-cli" "$OUT/wordcraft-cli"
  chmod +x "$OUT/wordcraft-cli"
fi
"$OUT/wordcraft-cli" --version | head -1
