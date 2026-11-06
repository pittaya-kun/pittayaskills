---
name: "vectorcraft"
description: Ilustração vetorial estilo Illustrator com o VectorCraft (open source) via CLI. Use para criar ou editar logos, ícones, ilustrações, formas, texto e pranchetas, converter entre SVG, PDF, AI, EPS, PNG e outros formatos, exportar arte vetorial e inspecionar arquivos vetoriais. Antes de usar, pergunte ao usuário em uma linha se quer o VectorCraft; só execute se autorizar. Não use para edição de foto (PhotoCraft), diagramação de página (DesignCraft) nem edição de PDF (PdfCraft).
version: 0.19.0
---

# VectorCraft (CLI)

Projeto: https://github.com/storytold/vectorcraft (docs em `docs/`: `typography-lettering.md`, `print-tiling.md`, `mcp.md`). Em dúvida de como fazer algo, consulte o catálogo de comandos (abaixo) antes do repositório.

## Regras

1. Pergunte antes de usar ("Isso fica melhor no VectorCraft, quer que eu use?"). Sem autorização, siga o caminho normal. Se o pacote do operador já lista o VectorCraft em `autorizacoes`, não pergunte de novo.
2. Entregue só os formatos pedidos (padrão: PDF). Sem intermediários.

## Preparar

```bash
sh PASTA_DESTA_SKILL/scripts/setup.sh   # copia a CLI para /tmp/vc/vectorcraft-cli (v0.19.0) e cmds.py
CLI=/tmp/vc/vectorcraft-cli
```

`PASTA_DESTA_SKILL` é a pasta onde está este `SKILL.md` (as skills ficam em `/mnt/skills/user` ou `/mnt/skills/plugins`, conforme o ambiente).

**macOS Universal:** a CLI agora vem completa num único binário nativo — não precisa mais da skill `vectorcraft-bin`.

## Uso

```bash
$CLI run [--in arq] --cmd ID --params '{json}' [--cmd ...] --export saida.ext [--scale N]
$CLI run --commands passos.json --export a.svg --export b.pdf   # passos em JSON; '-' lê do stdin
$CLI convert ENTRADA SAIDA [--artboard I | --range 1-3] [--outline-text] [--scale N]
$CLI info arq        # JSON: pranchetas, objetos por tipo, fontes, avisos de importação
```

- Os comandos rodam em ordem e cada um imprime um JSON (o objeto criado vem em `result.id`). Cada `run` começa do zero: agrupe os passos num único `run`.
- Sem `--in`, começa um documento novo; defina o tamanho com `file.new`.
- O objeto recém-criado fica selecionado: `paint.*` e `object.*` sem `ids` agem nele; passe `"ids":[...]` para agir em outro.
- O formato sai pela extensão do `--export`. Escreve: svg, svgz, pdf, ai, eps, png, jpg, gif, webp, tif, bmp, psd, dxf, emf, wmf, tga, txt e o nativo `.vectorcraft`. Lê também ait, psd, afdesign e outros.
- PDF leva todas as pranchetas; os demais formatos, só a primeira (use `--artboard` ou `--range` no `convert`).
- Sem `--export`, nada é salvo.

## Descobrir comandos (800+)

```bash
python3 /tmp/vc/cmds.py shape              # id e nome
python3 /tmp/vc/cmds.py '^text\.' --params # com parâmetros
```

Leia o `params` antes de usar um comando novo. Nunca despeje `$CLI commands` inteiro (400 KB). Prefixos úteis: `object` `shape` `path` `text` `paint` `file` `document` `artboard` `layer` `select` `edit`.

## Receitas testadas (pt; origem no canto superior esquerdo; 1 pt = 1/72 pol)

- **Novo:** `file.new {"width":"148 mm","height":"210 mm","name":"x"}` (aceita pt, texto com unidade, `preset`, `artboards`). **Prancheta extra:** `artboard.new {"width","height","name"}`.
- **Formas:** `shape.rectangle {x,y,width,height,radius?}`, `shape.ellipse`, `shape.polygon {cx,cy,radius,sides}`, `shape.star`, `shape.line {x1,y1,x2,y2}`.
- **Cor:** `paint.setFill {"color":"#rrggbb"}` (também `{c,m,y,k}` ou `"none":true`); `paint.setStroke` igual. **Toda forma nova nasce com traço preto**: use `paint.setStroke {"none":true}` quando não quiser contorno.
- **Texto:** `text.create {x,y,text,size,font,color}`; `x,y` é a linha de base; `area:{width,height}` cria texto em parágrafo. `text.fonts` mostra o estado das fontes do documento (`exact`, `substitute`, `missing`).
- **Texto como contorno** (logos e arquivos de impressão, sem depender de fonte): `convert in.svg out.svg --outline-text`.
- **Colocar arquivo:** `file.place {"path":"img.png","link":true}` (PNG, JPG, SVG, PDF; sem `link`, vetores entram como cópia editável).
- **Alinhar e organizar:** `object.align {"horizontal":"center","vertical":"center","to":"artboard"}`, `object.group`, `object.move {dx,dy}`, `object.scale {sx,sy}`.
- **Converter:** `$CLI convert in.svg out.pdf` (SVG, PDF, AI, EPS, PNG e outros).
- **Exportar vários tamanhos ou pranchetas:** `document.exportForScreens` (veja o `params`).
- **Conferir sem olhar:** `$CLI info arq`; para ver o resultado, exporte um PNG com `--scale 0.5` e abra uma vez.

## Cuidados

- Confira o `warnings` de cada export. Aviso de estilo de fonte (`Regular` desenhada como `Book`) é normal; fonte `missing` ou `substitute` muda o desenho: converta o texto em contorno ou troque a fonte.
- Erros citam o número do passo, contando a partir de 0.
- Versão 0.19: se um comando falhar ou não existir, procure outro caminho no catálogo e explique a limitação ao usuário em vez de insistir.