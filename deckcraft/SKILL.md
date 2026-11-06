---
name: deckcraft
description: Executor do DeckCraft (apresentação open source, estilo PowerPoint) via CLI. Cria e edita apresentações .pptx com slides, layouts, mestres, animações, transições, notas do apresentador e exporta PDF/imagens. Normalmente é chamado pela skill `design`; use direto só se o usuário pedir o DeckCraft pelo nome. Não faz diagramação de documento (DesignCraft), planilhas (GridCraft) nem texto corrido (WordCraft).
version: 0.13.1
---

# DeckCraft (executor)

Função simples: recebe uma tarefa de apresentação, opera a CLI e devolve arquivos + relatório. Não escolhe ferramenta nem pergunta se pode usar (isso é da skill `design`).

## Contrato

- **Entrada:** apresentação existente (`.pptx`, `.ppt`, `.odp`) ou especificação nova, mais a lista de operações.
- **Saída:** só o formato pedido (padrão `.pptx`) em `/mnt/user-data/outputs/` + `present_files`.
- **Relatório (sempre, curto):** nº de slides, layouts usados, animações/transições aplicadas, avisos de fonte/mídia.
- **Não faz:** documento de texto contínuo, planilhas, edição de PDF, vetor complexo.
- Versão empacotada: 0.13.1 (alpha). Projeto: https://github.com/storytold/deckcraft

## Preparar

```bash
SK=$(ls -d /mnt/skills/*/deckcraft | head -1); sh $SK/scripts/setup.sh   # CLI em /tmp/dkc/deckcraft-cli
CLI=/tmp/dkc/deckcraft-cli
```

## Comandos

```bash
$CLI info arq.pptx [--json]                        # metadados: slides, layouts, mestres, fontes, mídia
$CLI new [--template ARQ] --out arq.pptx
$CLI run [--in ARQ] --script passos.jsonl --out saida.pptx [--print-slide N]
$CLI convert IN OUT [--format pptx|pdf|png|jpg]    # pela extensão se omitido
$CLI layout list ARQ [--json]                      # layouts do mestre ativo
$CLI master get ARQ [--json]                       # XML do mestre
$CLI master set ARQ --xml MESTRE.xml --out ARQ
$CLI commands [--json] [--search X]
```

- Script `.jsonl`: uma linha por passo, `{"command":"id","params":{...}}`; linhas em branco e `#` são ignoradas. Sem `--out`, nada é salvo.
- Slide index: 0-based. `--print-slide N` mostra XML do slide N.

## Receitas (verificadas)

- **Nova apresentação:** `new --out apresentacao.pptx`; com template: `new --template modelo.pptx --out apresentacao.pptx`.
- **Adicionar slide:** `slide.add {"layout":"Title and Content","master":0}`; layouts comuns: `Title Slide`, `Title and Content`, `Section Header`, `Two Content`, `Comparison`, `Title Only`, `Blank`, `Content with Caption`, `Picture with Caption`.
- **Texto no placeholder:** `placeholder.setText {"slide":0,"placeholder":1,"text":"Título da Apresentação"}`; `placeholder.setText {"slide":0,"placeholder":2,"text":"Subtítulo\nCom quebra de linha"}`.
- **Formatar texto:** `placeholder.setStyle {"slide":0,"placeholder":1,"fontSize":44,"fontFamily":"Montserrat","fontWeight":700,"color":"#1A1A2E","alignment":"center"}`.
- **Imagem:** `placeholder.setImage {"slide":1,"placeholder":1,"path":"foto.jpg"}`; ou livre: `shape.addImage {"slide":1,"x":100,"y":100,"width":400,"height":300,"path":"img.png"}`.
- **Formas:** `shape.addRectangle {"slide":1,"x","y","width","height","fill":"#4F46E5","line":"none"}`; `shape.addEllipse`, `shape.addLine`, `shape.addConnector`.
- **Tabela:** `table.add {"slide":2,"rows":4,"cols":3,"x":50,"y":100,"width":800,"height":300,"style":"Medium Style 2"}`; `table.setCell {"slide":2,"table":0,"row":0,"col":0,"text":"Cabeçalho"}`.
- **Animação:** `animation.add {"slide":1,"target":"placeholder:1","effect":"fade","trigger":"onClick","duration":0.5,"delay":0.2}`; efeitos: `fade`, `flyIn`, `wipe`, `zoom`, `pulse`, `emphasis`.
- **Transição:** `transition.set {"slide":1,"type":"morph","duration":0.8}`; tipos: `none`, `fade`, `push`, `wipe`, `split`, `reveal`, `morph`, `zoom`.
- **Notas do apresentador:** `notes.set {"slide":0,"text":"Lembrar de citar a fonte dos dados."}`.
- **Mestre/Layout:** `layout.duplicate {"source":"Title and Content","name":"Meu Layout"}`; edite o XML via `master.get`/`master.set` para mudanças avançadas.
- **Exportar PDF:** `convert apresentacao.pptx apresentacao.pdf` (slides + notas opcional: `--include-notes`).
- **Exportar imagens:** `convert apresentacao.pptx slides/ --format png --scale 2` (pasta com slide_0.png, slide_1.png...).

## Cuidados

- **Unidades:** pontos (1/72 pol) para posição/tamanho; EMU (1/914400 pol) internamente. 1 pt = 12700 EMU.
- **Fonts:** fontes não instaladas caem em substituição; confira `warnings` e use fontes web-safe (Arial, Calibri, Roboto, Inter via Google Fonts) ou embuta no template.
- **Morph transition:** requer objetos com mesmo `objectId` entre slides consecutivos; use `layout.duplicate` para manter IDs.
- **Mídia:** vídeos/áudios não são embutidos no `.pptx` exportado por enquanto; apenas link (precisa copiar arquivos junto).
- **Alpha:** importação `.ppt` (legado) e `.odp` tem fidelidade limitada; animações complexas e SmartArt podem não importar.
- Não imprima XML de slides/mestres inteiros: resuma (nº de slides, layouts, animações).