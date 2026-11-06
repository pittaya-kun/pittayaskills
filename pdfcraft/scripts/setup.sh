#!/bin/sh
# Prepara a CLI do PdfCraft (macOS universal) em /tmp/pdfc/pdfcraft-cli.
set -e
DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT=/tmp/pdfc
mkdir -p "$OUT"
if [ ! -x "$OUT/pdfcraft-cli" ]; then
  cp -f "$DIR/bin/pdfcraft-cli" "$OUT/pdfcraft-cli"
  chmod +x "$OUT/pdfcraft-cli"
fi
"$OUT/pdfcraft-cli" --version | head -1
