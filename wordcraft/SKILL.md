---
name: wordcraft
description: Executor do WordCraft (processador de texto open source, estilo Word) via CLI. Cria e edita documentos .docx com formatação, estilos, tabelas, imagens, cabeçalhos/rodapés, numeração, referências e mail merge. Normalmente é chamado pela skill `design`; use direto só se o usuário pedir o WordCraft pelo nome. Não faz diagramação avançada (DesignCraft), planilhas (GridCraft) nem PDF (PdfCraft).
version: 0.13.2
project_url: "https://github.com/storytold/wordcraft"
cli_binary: "wordcraft-cli"
version_cmd: "--version"
---

# WordCraft (executor)

Função simples: recebe uma tarefa de documento de texto, opera a CLI e devolve arquivos + relatório. Não escolhe ferramenta nem pergunta se pode usar (isso é da skill `design`).

## Contrato

- **Entrada:** documento existente (`.docx`, `.doc`, `.rtf`, `.txt`, `.md`) ou conteúdo novo, mais a lista de operações.
- **Saída:** só o formato pedido (padrão `.docx`) em `/mnt/user-data/outputs/` + `present_files`.
- **Relatório (sempre, curto):** o que foi escrito (nº de parágrafos/páginas), estilos aplicados, avisos de conversão.
- **Não faz:** layout de página complexo, planilhas, edição de PDF, vetor.
- Versão empacotada: 0.13.2 (alpha). Projeto: https://github.com/storytold/wordcraft

## Preparar

```bash
SK=$(ls -d /mnt/skills/*/wordcraft | head -1); sh $SK/scripts/setup.sh   # CLI em /tmp/wc/wordcraft-cli
CLI=/tmp/wc/wordcraft-cli
```

## Comandos

```bash
$CLI info arq.docx [--json]                        # metadados: páginas, palavras, estilos, seções
$CLI new [--template ARQ] --out arq.docx
$CLI run [--in ARQ] --script passos.jsonl --out saida.docx [--print-range INI:FIM]
$CLI convert IN OUT [--format docx|pdf|txt|md|html]  # pela extensão se omitido
$CLI style list ARQ [--json]                       # estilos de parágrafo/caractere/tabela
$CLI style create ARQ --name NOME --type paragraph|character|table --based-on BASE --props '{json}' --out ARQ
$CLI style apply ARQ --range INI:FIM --style NOME --out ARQ
$CLI commands [--json] [--search X]
```

- Script `.jsonl`: uma linha por passo, `{"command":"id","params":{...}}`; linhas em branco e `#` são ignoradas. Sem `--out`, nada é salvo.
- Range: `"0:10"` = parágrafos 0 a 10; `"section:1"` = seção 1; `"all"` = documento todo.

## Receitas (verificadas)

- **Novo documento:** `new --out relatorio.docx`; com template: `new --template modelo.docx --out relatorio.docx`.
- **Escrever texto:** `paragraph.add {"text":"Conteúdo do parágrafo","style":"Normal"}`; adiciona no final. `paragraph.insert {"at":5,"text":"Inserido","style":"Heading 1"}`.
- **Formatar:** `paragraph.setStyle {"range":"0:5","style":"Heading 1"}`; `run.setStyle {"range":"0:5","style":"Strong"}` (estilo de caractere).
- **Estilo de parágrafo:** `style.create {"name":"Corpo Personalizado","type":"paragraph","basedOn":"Normal","props":{"spacing":{"after":120,"line":276,"lineRule":"auto"},"indent":{"firstLine":720}}}` (unidades: twips = 1/1440 pol).
- **Tabela:** `table.create {"rows":5,"cols":3,"style":"Table Grid"}`; preencher: `table.setCell {"row":0,"col":0,"text":"Cabeçalho","style":"Table Header"}`.
- **Imagem:** `picture.add {"path":"img.png","width":3600000,"height":2400000,"wrap":"square"}` (unidades: EMU = 1/914400 pol).
- **Cabeçalho/Rodapé:** `header.add {"section":1,"type":"default","paragraphs":[{"text":"Relatório Anual","style":"Header"}]}`.
- **Numeração:** `numbering.create {"abstractNumId":0,"levels":[{"level":0,"format":"decimal","text":"%1."}]}`; aplicar: `paragraph.setNumbering {"range":"0:10","numId":1}`.
- **Mail merge:** `mailmerge.connect {"source":"dados.csv","delimiter":","}`; `mailmerge.execute {"records":"all","outDir":"cartas/"}`.
- **Sumário:** `toc.insert {"at":0,"title":"Sumário","levels":3,"style":"TOC 1"}`.
- **Exportar PDF:** `convert relatorio.docx relatorio.pdf` (requer LibreOffice headless no ambiente).

## Cuidados

- **Unidades:** twips (1/1440 pol) para espaçamento/indentação; EMU (1/914400 pol) para imagens/tabelas. Converta: 1 pt = 20 twips = 12700 EMU.
- **Estilos:** sempre use `basedOn` para herdar de estilos existentes; criar do zero é propenso a erro.
- **Fonts:** fontes não instaladas no ambiente caem em substituição; confira `warnings` no retorno.
- **Conversão PDF:** depende de LibreOffice; layout complexo pode divergir. Para PDF de impressão, prefira DesignCraft.
- **Alpha:** importação `.doc` (legado) e `.rtf` tem fidelidade limitada; `.md` e `.txt` entram como texto plano.
- Não imprima documentos grandes inteiros: use `--print-range` e resuma.