---
name: gridcraft
description: Executor do GridCraft (planilha open source, estilo Excel) via CLI. Cria e edita planilhas .xlsx com fórmulas, formatação, tabelas, gráficos e tabelas dinâmicas; lê .xlsx/.csv/.tsv/.json/.html e converte entre eles e PDF. Normalmente é chamado pela skill `design`; use direto só se o usuário pedir o GridCraft pelo nome. Não faz diagramação (DesignCraft), foto, vetor nem leitura de PDF.
version: 0.14.2
---

# GridCraft (executor)

Função simples: recebe uma tarefa de planilha, opera a CLI e devolve arquivos ou dados. Não escolhe ferramenta nem pergunta se pode usar (isso é da skill `design`).

## Contrato

- **Entrada:** planilha existente (`.xlsx .csv .tsv .json .html`; `.xls` e `.ods` só abrem com valores) ou dados novos, mais a lista de operações.
- **Saída:** só o formato pedido (padrão `.xlsx`) em `/mnt/user-data/outputs/` + `present_files`.
- **Relatório (sempre, curto):** o que foi escrito (nº de células/abas) e qualquer erro de fórmula (`#NAME?` etc.).
- **Não faz:** layout de página, imagem, vetor, PDF como entrada.
- Versão empacotada: 0.14.2 (alpha, ~50% pronto segundo o próprio README). Projeto: https://github.com/storytold/gridcraft

## Preparar

```bash
SK=$(ls -d /mnt/skills/*/gridcraft | head -1); sh $SK/scripts/setup.sh   # CLI em /tmp/gc/gridcraft-cli
CLI=/tmp/gc/gridcraft-cli
```

## Comandos

```bash
$CLI info arq.xlsx [--json]                       # abas, intervalo usado, tabelas, gráficos, nomes
$CLI cat arq.xlsx [--range A1:D20] [--sheet S] [--formulas] [--csv]    # lê como tabela alinhada
$CLI convert IN OUT [--sheet NOME]                # xlsx/csv/tsv/json/html/pdf pela extensão
$CLI eval '=FÓRMULA' [--in arq] [--sheet S] [--cell A1] [--json]       # testa uma fórmula
$CLI check arq.xlsx [--json]                      # confere cálculo e ida-e-volta do XLSX
$CLI run [--in ARQ | --sample sales|budget|grades] --script passos.jsonl [--cmd 'id={json}']... --out saida.xlsx [--print A1:D4]
$CLI commands [--json] [--search X]               # 353 comandos
$CLI functions [--json] [--search X]              # 514 funções
```

- Script `.jsonl`: uma linha por passo, `id={json}` ou `{"command":"id","params":{...}}`; linhas em branco e `#`/`//` são ignoradas. Sem `--out`, nada é salvo.
- **Rode `commands --json --search X` antes de usar comando novo**: o `params` mostra os campos exatos.
- `selection` e `sheet` ativos importam: muitos comandos usam `range` opcional (padrão = seleção). Passe `range` sempre.

## Receitas (verificadas)

- **Escrever dados:** `range.setValues={"range":"A1","values":[["Produto","Q1"],["A",100]]}`; textos que começam com `=` viram fórmula. `cell.set={"cell":"B2","input":"=SUM(B3:B9)"}` para uma célula.
- **Formatar:** `home.bold`, `home.fillColor={"range","color":"#E21981"}`, `home.fontColor`, `home.numberFormat={"range","format":"Currency|Percentage|Short Date|..."}` (ou `"code":"0.00"`), `home.borders={"range","preset":"all"}`, `home.wrapText`, `home.columnWidth={"cols":"A:D","width":90}` (px).
- **Abas:** `sheet.rename={"name"}`, `sheet.move`, `sheet.tabColor`. Comandos sem `sheet` agem na aba ativa (`sheet.activate={"sheet":"Nome"}`).
- **Tabela:** `insert.table={"range":"A1:D4","header":true,"style":"TableStyleMedium2"}`.
- **Gráfico:** `insert.chart={"range":"A1:C4","type":"column|line|pie|bar|...","title","at":"F2"}`; ajustes com `chart.set`.
- **Ordenar/filtrar:** `data.sort={"range","header":true,"keys":[{"column":"B","order":"desc"}]}`, `data.filterBy`.
- **Ler:** `sheet.read={"range","formulas":false,"formatted":true}` ou `cat`.
- **Exportar:** `convert in.xlsx out.pdf` (PDF da aba ativa, folha Carta por padrão), `file.exportPdf={"path","sheets":"all","range","fitToPage":true}`.
- **Importar CSV:** `convert dados.csv saida.xlsx` (separador `;` e `,` são detectados).

## Cuidados (aprendidos testando)

- **Fórmulas só em inglês e com vírgula:** `=SUM(1,2)` funciona; `=SOMA(1,2)` dá `#NAME?` e `=SUM(1;2)` é recusado. Para usuário brasileiro, escreva a fórmula em inglês e avise.
- **Números no formato brasileiro viram texto no CSV:** `1.234,50` ficou como texto na conversão. Normalize antes (troque `.`/`,`) ou escreva com `range.setValues` já como número.
- `range.setValues` interpreta strings como entrada digitada (`parse` padrão `true`): `"05.04.2026"` vira data, `"2.500"` vira número (convenção americana). Use `parse:false` para manter texto.
- Gráfico grande pode estourar para uma segunda página do PDF: confira `pages` no retorno e use `fitToPage`.
- `automate.runScript` e comandos com `path` recusam fora do que foi confiado: não dependa deles.
- Alpha: fidelidade de XLSX do mundo real, `.xls` (sem formatação) e `.ods` (só valores) têm limites. Rode `check` em arquivos importantes e avise o usuário do que não é suportado em vez de insistir.
- Não imprima planilhas grandes inteiras: use `--range` e resuma.