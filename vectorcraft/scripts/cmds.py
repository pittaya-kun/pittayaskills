#!/usr/bin/env python3
"""Filtra o catálogo de comandos do VectorCraft sem despejar os 400 KB.

Uso: cmds.py PADRAO [--params] [--full] [--max N]
  PADRAO    regex (sem diferenciar maiúsculas) aplicada ao id e ao nome
  --params  mostra também os parâmetros (cortados em 500 caracteres)
  --full    parâmetros completos
  --max N   limite de linhas (padrão 25)
"""
import json, os, re, subprocess, sys

CLI = os.environ.get("VC", "/tmp/vc/vectorcraft-cli")
CACHE = "/tmp/vc/commands.json"

def catalog():
    if not os.path.exists(CACHE):
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        out = subprocess.run([CLI, "commands"], capture_output=True, text=True, check=True).stdout
        with open(CACHE, "w") as f:
            f.write(out)
    with open(CACHE) as f:
        return json.load(f)

def main(argv):
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    pat = re.compile(argv[0], re.I)
    full = "--full" in argv
    show = full or "--params" in argv
    mx = int(argv[argv.index("--max") + 1]) if "--max" in argv else 25
    hits = [c for c in catalog() if pat.search(c["id"]) or pat.search(c.get("label", ""))]
    for c in hits[:mx]:
        line = f'{c["id"]} | {c.get("label", "")}'
        if show:
            p = (c.get("params") or "").replace("\n", " ")
            line += " | " + (p if full else p[:500])
        print(line)
    if len(hits) > mx:
        print(f"... +{len(hits) - mx} (use --max ou um padrão mais específico)")
    if not hits:
        print("nenhum comando encontrado")

main(sys.argv[1:])
