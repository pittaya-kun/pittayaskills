---
name: pdfcraft
description: Executor do PdfCraft (leitor/editor de PDF open source) via CLI. Inspeciona PDF (info JSON, fontes, camadas, tags, produtor), extrai texto em ordem de leitura, renderiza páginas em PNG, exporta imagens, faz OCR, divide, extrai, combina, gira e apaga páginas, edita metadados, protege e redige. Normalmente é chamado pela skill `design`; use direto só se o usuário pedir o PdfCraft pelo nome. Não converte PDF em layout editável (DesignCraft), não edita foto (PhotoCraft) nem vetoriza (VectorCraft).
version: 0.16.1
project_url: "https://github.com/storytold/pdfcraft"
cli_binary: "pdfcraft-cli"
version_cmd: "--version"
---

# PdfCraft (executor)

Função simples: recebe um PDF e uma tarefa, opera a CLI e devolve dados ou arquivos. Não escolhe ferramenta nem pergunta se pode usar (isso é da skill `design`).

## Contrato

- **Entrada:** caminho de um ou mais PDFs (e senha, se houver).
- **Saída:** JSON/texto no terminal (inspeção) ou só o arquivo pedido em `/mnt/user-data/outputs/` + `present_files`.
- **Relatório (sempre, curto):** o que foi lido/gerado e os avisos da CLI (`warnings`, `skipped`).
- **Não faz:** transformar PDF em documento editável com estilos e camadas, nem ler camadas que o PDF não tem.
- Versão empacotada: 0.16.1 (alpha). Projeto: https://github.com/storytold/pdfcraft

## Preparar

```bash
SK=$(ls -d /mnt/skills/*/pdfcraft | head -1); sh $SK/scripts/setup.sh   # CLI em /tmp/pdfc/pdfcraft-cli
CLI=/tmp/pdfc/pdfcraft-cli
```

## Comandos

```bash
$CLI info   arq.pdf [--password PW]       # JSON: páginas, tamanho, creator, producer, layers, tagged, fields, links, pdfa/pdfua...
$CLI text   arq.pdf [--page N]            # texto em ordem de leitura (páginas separadas por \f)
$CLI render arq.pdf --page N [--dpi 96] --out x.png    # .png .jpg .tif
$CLI extract arq.pdf --pages 1,3,5-8 --out out.pdf
$CLI split   arq.pdf (--every N | --before 3,7) [--out-dir DIR]
$CLI combine a.pdf b.pdf --out c.pdf
$CLI edit  in.pdf --out out.pdf [--rotate 1,3:90] [--delete 2,4] [--move 5:1] [--insert-blank 1] [--title T] [--author A]
$CLI batch arqs/ --steps convert,ocr,optimize --out-dir DIR [--language en] [--ocr-all-pages]
$CLI audit  arq.pdf                       # acha redação falsa
$CLI tools                                # 175 ferramentas com JSON Schema (page_render, text_extract, object_list, doc_export_images, ocr_status...)
$CLI run <ferramenta> chave=valor ... [--root DIR] [--out img.png]
$CLI run --script passos.json [--root DIR] [--report]   # [{"tool":"doc_open","args":{...}}, ...]
```

Use `--root DIR` para confinar leitura/escrita. Em dúvida sobre uma ferramenta, leia o `description` e o schema em `$CLI tools` antes de usar.

## Receitas (verificadas)

- **Raio-x do PDF (pré-voo):** `info` → `creator` (programa de origem, ex.: "Adobe InDesign 20.2"), `layers` (0 = sem camadas), `tagged` (false = sem estrutura), `fields`, `pages`, `first_page_pt`.
- **Texto por página:** `text --page N`; por região: ferramenta `text_extract` com `rect`.
- **Prévia p/ comparar:** `render --page N --dpi 50 --out x.png` (ms por página).
- **Imagens do PDF:** ferramenta `doc_export_images` exporta páginas como imagem; `Export all images` extrai as embutidas. **JPEG 2000, JBIG2 e CCITT ainda não são decodificados** (ficam em `skipped`): para esses use `pdfimages` (poppler).
- **OCR:** não vem no pacote (os modelos pesam ~11 MB). Se o usuário enviar `text-detection.rten` e `text-recognition.rten` (vêm em `share/pdfcraft/models` do release), coloque-os numa pasta e use `export PDFCRAFT_MODELS=PASTA`; `ocr_status` confirma. Os modelos do release 0.16.1 só trazem inglês: acentos do português não foram testados, confira a saída antes de confiar.

## Cuidados

- Alpha: o README lista como fracos a edição de texto existente, OCR fora do latino, PDF/X/UA e conversão para office.
- Edições ficam na memória até `doc_save`; `edit`/`extract`/`split` gravam arquivo novo e não tocam no original.
- Sem `--out` de arquivo, nada é salvo.
- Não imprima textos longos inteiros: resuma ou grave em arquivo.