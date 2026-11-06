---
name: craftanything
description: Executor do Craft Anything (engine de engenharia reversa + recriação via AI agents) via CLI. Estuda qualquer software (sites, apps, jogos, arquivos) e recria do zero no stack solicitado. Use para recriar interfaces, migrar código, entender sistemas legados, ou prototipar a partir de referências visuais. Normalmente é chamado pela skill `architect`; use direto só se o usuário pedir o Craft Anything pelo nome. Não decide qual stack usar, não faz edição de imagem (PhotoCraft), vetor (VectorCraft) nem diagramação (DesignCraft).
version: 0.1.0
project_url: "https://github.com/storytold/craft-anything"
cli_binary: "craft-anything-cli"
version_cmd: "--version"
---

# Craft Anything (executor)

Função simples: recebe um alvo (URL, arquivo, pasta) e uma especificação do que recriar, opera a CLI e devolve o projeto gerado + relatório de comparação. Não escolhe ferramenta nem pergunta se pode usar (isso é da skill `architect`).

## Contrato

- **Entrada:** alvo (URL, caminho local, ou `-` para descrição textual) + especificação do que construir ("Recria este site em React + Tailwind", "Transforma este jogo em Rust/Bevy")
- **Saída:** pasta do projeto gerado em `/mnt/user-data/outputs/<nome>/` + `present_files` com os arquivos principais
- **Relatório (sempre, curto):** o que foi recriado, mismatches encontrados no check, sugestões de refinamento
- **Não faz:** decisão de arquitetura, edição de assets, geração de imagem por IA

## Preparar

```bash
SK=$(ls -d /mnt/skills/*/craftanything | head -1); sh $SK/scripts/setup.sh   # CLI em /tmp/ca/craft-anything-cli
CLI=/tmp/ca/craft-anything-cli
```

## Comandos

```bash
$CLI doctor                                    # checa install, coding agents, engines
$CLI rebuild https://exemplo.com "Recria em React + Tailwind"
$CLI rebuild - "Snake game em Rust/Bevy" --rounds 1
$CLI rebuild https://exemplo.com "Header azul" --continue-in pasta_projeto
$CLI commands                                  # lista 300+ tools por toolset
$CLI mcp                                       # serve tools via MCP para qualquer agent
$CLI setup                                     # conecta Craft Anything a coding-agent apps
```

- `--rounds N`: número de iterações build→check→refine (padrão: 3)
- `--continue-in`: continua refinando projeto existente
- Saída vai para pasta com timestamp; use `--out` se quiser caminho fixo

## Fluxo típico (4 passos)

1. **Study** — `$CLI rebuild <alvo> <spec>` inicia inspeção: páginas em 3 larguras, código, arquivos, runtime
2. **Build** — Coding agent (Claude Code, Codex, Copilot, etc.) cria projeto na stack pedida
3. **Check** — Compara build vs original; lista mismatches visuais/funcionais
4. **Ready** — Abre/roda/previa resultado; pede ajustes → refina até "pronto"

## Receitas (verificadas)

- **Site → React:** `rebuild https://site.com "Recria em React 18 + Tailwind + Vite"`
- **Site → Next.js:** `rebuild https://site.com "Recria em Next.js 14 App Router + Tailwind"`
- **App desktop → Tauri:** `rebuild /caminho/app.exe "Recria em Rust + Tauri + React"`
- **Jogo Unity → Godot:** `rebuild /caminho/jogo.unity "Recria em Godot 4 + GDScript"`
- **Legado → Moderno:** `rebuild /caminho/legacy "Migra para Python 3.12 + FastAPI + SQLAlchemy"`
- **Prototipar:** `rebuild - "Dashboard admin com sidebar, tabela, gráficos — React + Recharts"`

## Cuidados

- **Rust 1.97+** obrigatório (`rustup update`)
- **Clean room** (default): só observa output visível; para Deep mode (leitura de binário/código), passa `--deep` e opcional `--ghidra`
- **Coding agent**: precisa ter `claude`, `codex`, `copilot` ou outro configurado (`$CLI doctor` mostra quais estão OK)
- **Early alpha**: se build falhar ou check der mismatch estranho, rode `commands --json --filter <toolset>` pra achar tool alternativa e explique limitação ao usuário
- **Tamanho**: projetos grandes geram muitos arquivos — resuma (contagem de arquivos, LOC, mismatches principais), não despeje árvore inteira
- **Licença**: recriação é código novo; assets (imagens, fontes, sons) do original **não** são copiados — usuário deve prover ou autorizar substituição