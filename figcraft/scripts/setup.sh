#!/bin/sh
# Prepara a CLI do FigCraft (macOS universal) em /tmp/fc/figcraft-cli.
set -e
DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT=/tmp/fc
mkdir -p "$OUT"
if [ ! -x "$OUT/figcraft-cli" ]; then
  cp -f "$DIR/bin/figcraft-cli" "$OUT/figcraft-cli"
  chmod +x "$OUT/figcraft-cli"
fi
"$OUT/figcraft-cli" --version | head -1
