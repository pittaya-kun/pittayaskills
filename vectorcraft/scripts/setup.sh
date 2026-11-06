#!/bin/sh
# Prepara a CLI do VectorCraft (macOS universal) em /tmp/vc/vectorcraft-cli.
set -e
DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT=/tmp/vc
mkdir -p "$OUT"
if [ ! -x "$OUT/vectorcraft-cli" ]; then
  cp -f "$DIR/bin/vectorcraft-cli" "$OUT/vectorcraft-cli"
  chmod +x "$OUT/vectorcraft-cli"
fi
cp -f "$DIR/scripts/cmds.py" "$OUT/cmds.py"
"$OUT/vectorcraft-cli" --version
