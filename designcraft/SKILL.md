---
name: designcraft
description: Executor do DesignCraft (editor de diagramação open source, estilo InDesign) via CLI. Cria e edita documentos .designcraft/.idml/.indd, aplica estilos, camadas, páginas, imagens e exporta PDF/PNG/EPUB/IDML. Normalmente é chamado pela skill `design`; use direto só se o usuário pedir o DesignCraft pelo nome. Não decide qual programa usar, não faz edição de foto nem vetor.
version: 0.15.2
project_url: "https://github.com/storytold/designcraft"
cli_binary: "designcraft-cli"
version_cmd: "--version"
---

# DesignCraft (executor)

Função simples: recebe uma tarefa de layout, opera a CLI e devolve arquivos + relatório. Não escolhe ferramenta, não pergunta se pode usar (isso é da skill `design`).

## Contrato

- **Entrada:** conteúdo (texto, imagens no disco, cores, medidas) ou arquivo existente (`.designcraft`, `.idml`, `.indd`).
- **Saída:** só o formato pedido (padrão PDF) em `/mnt/user-data/outputs/` + `present_files`. Sem `.dcs` nem prévias, salvo se pedido.
- **Relatório (sempre, curto):** nº de erros da CLI, fontes não resolvidas, quadros com texto estourado.
- **Não faz:** foto (PhotoCraft), vetor/vetorização (VectorCraft), ler/OCR de PDF (PdfCraft), documentos comuns (Word).
- **PDF não abre como documento** (`file.open` recusa). PDF só entra por `file.place {pdfPage}` como imagem, sem camadas, texto nem estilos.

## Preparar

```bash
SK=$(ls -d /mnt/skills/*/designcraft | head -1); sh $SK/scripts/setup.sh   # CLI em /tmp/dc/designcraft-cli
```

Fontes do usuário (.ttf): instale em `~/.fonts`, rode `font.reload {}` e confira com `font.list` (`matchStatus: exact`). **Fonte variável não exporta bem** (sai no peso Thin): gere instâncias estáticas com `fontTools.varLib.instancer` e instale-as.

## Fluxo

1. Monte o script com `scripts/dcs.py` (`from dcs import Script`; `add()` devolve o índice N do passo, então `"$%d.id" % n` nunca erra).
2. `rodar(...)` com `exportar=` (formato pela extensão) e, se pedido, `salvar=` (`.designcraft`).
3. Confira `erros` e `document.inspect` (stories com `overset`).
4. Copie só o pedido para `outputs/` e use `present_files`.

Comandos: `$CLI commands <filtro>` e `$CLI describe <comando>`. **Rode `describe` antes de comando novo**: parâmetro desconhecido é ignorado em silêncio.

## Receitas

- **Novo:** `file.new {"preset":"A4","pages":1,"margins":40}` (ou `width`/`height`, `columns`, `gutter`, `bleed`, `facingPages`). A4 = 595x842 pt. Página de tamanho diferente: `layout.pageSize {"pages":[1],"width","height"}`.
- **Texto:** `frame.create {"rect":[x0,y0,x1,y1],"content":"text","text":"L1\nL2","spread":N}`. Pontos, origem no canto superior esquerdo; `spread` = índice da página/spread (0-based; com `facingPages:false` cada página tem origem própria).
- **Formatar:** `text.select {"story","anchor","focus"}` (**bytes UTF-8**) e depois `style.paragraph.apply {"name","clearOverrides":true}` ou `style.character.apply {"name"}`.
- **Estilos:** `style.paragraph.create {"name":"Grupo/Nome","para":{...},"chars":{"fontFamily","fontStyle","size","leading":{"kind":"points","value"},"fill":"<swatch>"}}`. Cor de texto = nome de swatch (`swatch.create`). Ponha `"hyphenate":false` em `para` se não quiser hifenização. Estilos com `/` viram grupos. `fontStyle` válidos incluem `Regular`, `SemiBold`, `Bold`, `Italic`, `Medium Italic`.
- **Camadas:** `file.new` já tem a camada 1 (renomeie com `layer.set {"id":1,"name"}`); `layer.new` entra **no topo**; `layer.activate {"id"}` antes de criar objetos nela; `object.setLayer` move.
- **Formas:** `frame.create {"shape":"ellipse|rectangle","content":"graphic"}`, `path.create {"anchors":[{"p":[x,y],"in":[..],"out":[..]}],"closed":true}`, `object.fill`/`object.stroke {"swatch"|"[None]"}`, `object.cornerOptions {"shape":"rounded","size"}`. Furos: `object.makeCompoundPath {"ids"}` e **inverta o sentido** do subcaminho interno, senão não fura.
- **Organizar:** `object.rename {"id","name"}`, `object.group {"ids"}`.
- **Imagem:** `file.place {"path","frame":id}` + `object.fit {"mode":"fillProportionally","ids"}`.
- **Colunas/encadeado:** `story.placeAndLink`; `columns`/`gutter` no `file.new`.
- **Mala direta:** `data.source.select`, `data.placeholder.add`, `data.merge {"records":"all"}`.
- **Exportar:** `file.exportPdf` (aceita `pages`), `file.exportEpub`, `file.exportPptx`; PDF/X-4: `$CLI validate-pdf arq.pdf`.
- **Abrir existente:** `--in arq.designcraft|.idml|.indd` (é o caminho mais fiel quando o usuário tem o fonte).

## Cuidados

- `"$N"` conta **passos do script** (0-based), não linhas de comentário. Use `dcs.py`.
- Sem estilo o texto sai pequeno: defina tamanho e cor.
- Texto longo estoura a caixa: confira `overset` e aumente o `rect`.
- Preenchimento de padrão de PDF importado não existe como objeto: recrie por grade de elipses.
- Não imprima listas grandes de resultados; resuma (contagem de erros + primeiros 3).
- Pré-alpha: se um comando falhar, tente outro via `commands`, consulte https://github.com/storytold/designcraft ou explique a limitação.