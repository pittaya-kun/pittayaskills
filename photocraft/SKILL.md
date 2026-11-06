---
name: photocraft
description: Executor do PhotoCraft (editor de imagem open source, estilo Photoshop) via CLI. Camadas, máscaras, ajustes de cor, filtros, texto sobre imagem, PSD, e processamento em lote (redimensionar, converter, ajustar). Normalmente é chamado pela skill `design`; use direto só se o usuário pedir o PhotoCraft pelo nome. Não decide qual programa usar, não faz diagramação (DesignCraft), vetor (VectorCraft) nem imagem por IA.
version: 0.18.0
---

# PhotoCraft (executor)

Função simples: recebe uma tarefa de imagem, opera a CLI e devolve arquivos + relatório. Não escolhe ferramenta nem pergunta se pode usar (isso é da skill `design`).

## Contrato

- **Entrada:** imagem(ns) no disco (`.psd .png .jpg .webp ...`) ou tamanho do canvas novo, mais a lista de operações.
- **Saída:** só o formato pedido em `/mnt/user-data/outputs/` + `present_files` (padrão PNG; foto sem transparência: JPG). Sem intermediários.
- **Relatório (sempre, curto):** o campo `warnings` da CLI (fonte em fallback, `flattened`, comando desabilitado).
- **Não faz:** layout de página, vetor puro, geração de imagem por IA.

## Preparar

```bash
SK=$(ls -d /mnt/skills/*/photocraft | head -1); sh $SK/scripts/setup.sh   # CLI em /tmp/pc/photocraft-cli
CLI=/tmp/pc/photocraft-cli
```

## Uso

```bash
$CLI run entrada.psd|.png|... --cmd ID --params '{json}' [--cmd ID --params '{json}' ...] --out saida.png
$CLI run --new '{"width":800,"height":600,"background":"#1b4d3e"}' --cmd ... --out saida.png
$CLI batch --actions acoes.json --in pasta --out pasta2 [--format webp] [--quality 80]
$CLI convert in.psd out.png [--quality 1-100]
$CLI info arq [--compact]      # JSON: tamanho, modo, árvore de camadas
```

- Cada `--params` vale para o `--cmd` anterior; os comandos rodam em ordem e a CLI imprime o JSON de cada um (traz `layer` = id da camada criada).
- `batch`: `acoes.json` = `[["image.imageSize",{"width":300}],["id",{...}]]` (também `.atn` + `--action nome`). `--out` igual a `--in` é recusado (use `--in-place`).
- Formato pela extensão do `--out`. Plano (png/jpg/webp) achata as camadas (aviso `flattened`); para manter camadas salve `.psd` ou `.pcraft`.
- Avisos `lossy compression` e `resolution not supported` são normais.

## Descobrir comandos (900+)

```bash
$CLI commands --filter curves          # lista id, nome, menu
$CLI commands --json --filter curves   # inclui "params" (tipos e padrões)
```

Leia o `params` antes de usar comando novo. Prefixos: `file` `image` `layer` `filter` `type` `select` `edit` `path` `shape` `paint` `channel`.

## Receitas (px; origem no canto superior esquerdo)

- **Novo:** `file.new {"width","height","background":"white|black|transparent|#rrggbb","resolution":72,"mode":"rgb"}`.
- **Texto:** `type.create {"x","y","text","font","size":pt,"color","align","box":[x,y,w,h]}`. `x,y` = linha de base; `box` = parágrafo. Fontes: `type.fonts` lista; **Arial não existe**, use Inter, Carlito (≈Calibri), Caladea (≈Cambria), DejaVu, FreeSans/FreeSerif, JetBrains Mono.
- **Colocar imagem:** `file.placeEmbedded {"path","scale":%,"center":[x,y],"fit":bool}` (vira smart object).
- **Redimensionar:** `image.imageSize {"width"|"height"|"percent","resample":"lanczos"}`; **canvas:** `image.canvasSize`; **recorte:** `image.crop {"x","y","width","height"}`.
- **Ajustes (não destrutivos):** `layer.newAdjustmentLayer.curves {"points":[[0,0],[64,48],[255,255]]}` (também levels, vibrance, hueSaturation). Direto nos pixels: `image.adjustments.*`, `image.autoTone`.
- **Filtros:** `filter.blur.gaussianBlur {"radius"}`, `filter.sharpen.smartSharpen {"amount"}`.
- **Camadas:** `layer.new.layer`, `layer.duplicate`, `layer.delete`, `layer.mergeDown`, `layer.moveTo`, `layer.translate`; `layer.setProps {"layer":id,"opacity":0..1,"visible","blend"}`.
- **Seleção/máscara:** `select.*`, `layer.layerMask.revealSelection`.
- **Modo:** `image.mode.rgb|cmyk|grayscale`, `image.mode.bits8|16`.

## Cuidados

- Sem `--out` nada é salvo.
- Fonte inexistente cai em fallback com aviso: confira `warnings`.
- Early alpha: se houver erro ou comando desabilitado, rode `commands --json --filter ID` (`disabledReason`/`needsDocument`), procure outro caminho em https://github.com/storytold/photocraft ou explique a limitação em vez de insistir.