---
name: figcraft
description: Executor do FigCraft (ferramenta de design colaborativo estilo Figma) via CLI. Cria e edita arquivos de design, componentes, protótipos, e exporta assets. Normalmente é chamado pela skill `design`; use direto só se o usuário pedir o FigCraft pelo nome. Não faz diagramação de página (DesignCraft), edição de foto (PhotoCraft) nem vetor (VectorCraft).
version: 0.13.1
project_url: "https://github.com/storytold/figcraft"
cli_binary: "figcraft-cli"
version_cmd: "--version"
---

# FigCraft (executor)

Função simples: recebe uma tarefa de design de interface, opera a CLI e devolve arquivos + relatório. Não escolhe ferramenta nem pergunta se pode usar (isso é da skill `design`).

## Contrato

- **Entrada:** arquivo de design existente (`.figcraft`, `.fig`, `.json`) ou especificação de novo design, mais a lista de operações.
- **Saída:** só o formato pedido em `/mnt/user-data/outputs/` + `present_files`.
- **Relatório (sempre, curto):** o que foi criado/editado, componentes afetados, avisos de exportação.
- **Não faz:** diagramação de documento multipágina, edição de imagem raster, ilustração vetorial complexa.

## Preparar

```bash
SK=$(ls -d /mnt/skills/*/figcraft | head -1); sh $SK/scripts/setup.sh   # CLI em /tmp/fc/figcraft-cli
CLI=/tmp/fc/figcraft-cli
```

## Comandos

```bash
$CLI info arq.figcraft [--json]                    # metadados: páginas, componentes, estilos, fontes
$CLI new [--preset mobile|desktop|tablet] --out arq.figcraft
$CLI run [--in ARQ] --script passos.json --out saida.figcraft
$CLI export ARQ --format png|svg|pdf|jpg [--scale N] [--ids IDS] --out DIR
$CLI component list ARQ [--json]
$CLI component create ARQ --name NOME --from-selection --out ARQ
$CLI prototype link ARQ --from ID --to ID --transition TIPO --out ARQ
$CLI style create ARQ --name NOME --props '{json}' --out ARQ
$CLI style apply ARQ --ids IDS --style NOME --out ARQ
$CLI commands [--json] [--search X]
```

- Script: JSON array de passos, cada um com `command` e `params`. Sem `--out`, nada é salvo.
- IDs de objetos: use `info` ou `component list` para descobrir.
- Exportação: `--ids` filtra objetos; sem `--ids`, exporta tudo.

## Receitas (verificadas)

- **Novo arquivo:** `new --preset desktop --out projeto.figcraft` (presets: mobile, desktop, tablet, watch, custom).
- **Criar frame:** `frame.create {"name":"Tela Inicial","width":1440,"height":900,"fills":[{"type":"SOLID","color":"#FFFFFF"}]}`.
- **Texto:** `text.create {"x":100,"y":100,"text":"Título","fontSize":24,"fontFamily":"Inter","fontWeight":600,"fills":[{"type":"SOLID","color":"#1A1A2E"}]}`.
- **Retângulo:** `rectangle.create {"x","y","width","height","fills","strokes","cornerRadius"}`.
- **Auto-layout:** `frame.create {"layoutMode":"HORIZONTAL|VERTICAL","primaryAxisSpacing":16,"counterAxisSpacing":16,"padding":16}`.
- **Componentes:** `component.create {"name":"Botão/Primário","fromSelection":true}`; instanciar: `instance.create {"componentId":"...","x","y"}`.
- **Estilos de texto:** `style.createText {"name":"Heading 1","fontFamily":"Inter","fontSize":32,"fontWeight":700,"lineHeight":{"unit":"PIXELS","value":40}}`.
- **Estilos de cor:** `style.createPaint {"name":"Primary/500","paint":{"type":"SOLID","color":"#4F46E5"}}`.
- **Exportar assets:** `export ARQ --format svg --scale 2 --out assets/`.
- **Protótipo:** `prototype.link --from ID_A --to ID_B --transition "SMART_ANIMATE" --out ARQ`.

## Cuidados

- **Fontes:** FigCraft usa fontes do sistema; fontes customizadas precisam ser instaladas no ambiente.
- **Auto-layout:** alterar `layoutMode` de frame com filhos pode repositionar elementos inesperadamente.
- **Componentes:** editar o componente mestre afeta todas as instâncias; use `detachInstance` para sobrescrever localmente.
- **Alpha:** fidelidade de importação `.fig` (Figma) tem limites; efeitos complexos, máscaras vetoriais e alguns blend modes podem não importar corretamente.
- Não imprima árvores de nós grandes inteiras: resuma (contagem de páginas/componentes/estilos).