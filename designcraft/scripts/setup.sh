#!/bin/sh
# Prepara a CLI do DesignCraft (macOS universal) em /tmp/dc/designcraft-cli.
set -e
DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT=/tmp/dc
mkdir -p "$OUT"
if [ ! -x "$OUT/designcraft-cli" ]; then
  cp -f "$DIR/bin/designcraft-cli" "$OUT/designcraft-cli"
  chmod +x "$OUT/designcraft-cli"
fi
"$OUT/designcraft-cli" --version | head -1
