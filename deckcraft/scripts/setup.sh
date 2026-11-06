#!/bin/sh
set -e
DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT=/tmp/deck
mkdir -p "$OUT"
if [ ! -x "$OUT/deckcraft-cli" ]; then
  cp -f "$DIR/bin/deckcraft-cli" "$OUT/deckcraft-cli"
  chmod +x "$OUT/deckcraft-cli"
fi
"$OUT/deckcraft-cli" --version | head -1
