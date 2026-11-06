# Pittaya Skills — Ecossistema SDD de Design

Coleção de skills para automação de design baseada em **SDD (Spec-Driven Development)**: planejamento → pacote → operação → retorno → próximo pacote.

## Visão Geral do Ecossistema

```
┌─────────────────────┐     pacote.md     ┌──────────────────────┐
│   ARQUITETO         │ ─────────────────▶ │    OPERADOR         │
│   (architect)       │                    │  (design-operator)   │
│                     │ ◀───────────────── │                     │
│ • Brief (o quê/porquê)                   │ • Executa tarefas   │
│ • Plano (como)                           │ • Verifica checks   │
│ • Pacote (rodada atual)                  │ • Retorno curto     │
└─────────────────────┘   retorno.md       └──────────────────────┘
         │                                          │
         ▼                                          ▼
┌─────────────────────┐                    ┌──────────────────────┐
│  PROGRAM SKILLS     │                    │  CONSTITUIÇÃO        │
│  (ferramentas)      │                    │  (regras fixas)      │
└─────────────────────┘                    └──────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────────┐
│  ZELADOR — mantém binários atualizados cross-platform           │
└────────────────────────────────────────────────────────────────┘
```

### Fluxo Principal

1. **Arquiteto** (`architect`) — Conversa com o usuário, gera:
   - `brief.md` — objetivo, entregáveis, critérios de aceite, perguntas abertas
   - `plano.md` — tarefas sequenciais com dependências, custo estimado, checks
   - `pacote.md` — tarefas da rodada atual (dependências satisfeitas)

2. **Operador** (`design-operator`) — Recebe o pacote, executa:
   - Abre só a skill do programa necessário por tarefa
   - Roda comando/script + check automatizado
   - Aplica política de desvio (N1 = correção mínima, N2 = para e pergunta)
   - Devolve `retorno.md` curto

3. **Próxima rodada** — Arquiteto lê retorno, atualiza plano, libera próximo pacote

4. **Zelador** (`zelador`) — Mantém binários CLI sempre na última versão:
   - `check-only` — lista updates disponíveis sem baixar
   - `update` — baixa, extrai, testa, limpa assets antigos
   - Detecta OS (macOS/Linux/Windows) e baixa só o asset correto

---

## Skills do Ecossistema

### Core (SDD)
| Skill | Papel |
|-------|-------|
| `architect` | Arquiteto — converte conversa em brief/plano/pacote |
| `design-operator` | Operador — executa pacote, verifica checks, devolve retorno |

### Program Skills (ferramentas que o operador chama)
| Skill | Função | Programa CLI |
|-------|--------|--------------|
| `designcraft` | Layout, composição, tipografia | `designcraft-cli` |
| `gridcraft` | Sistemas de grid, alinhamento | `gridcraft-cli` |
| `pdfcraft` | Manipulação/export PDF/X | `pdfcraft-cli` |
| `photocraft` | Tratamento de imagem, cor | `photocraft-cli` |
| `vectorcraft` | Vetores, SVG, ilustração | `vectorcraft-cli` |
| `figcraft` | Design colaborativo estilo Figma | `figcraft-cli` |
| `deckcraft` | Apresentações/slides | `deckcraft-cli` |
| `wordcraft` | Processamento de texto .docx | `wordcraft-cli` |
| `craftanything` | Engenharia reversa + recriação via AI | `craft-anything-cli` |

### Infraestrutura
| Skill | Função |
|-------|--------|
| `zelador` | Atualiza binários dos programas (cross-platform) |

### Suporte
| Skill | Função |
|-------|--------|
| `design-planner` | Planejamento auxiliar de design |

> **Nota:** `pittaya-indesign-scripts` **não** faz parte deste ecossistema — é um conjunto separado de scripts para Adobe InDesign.

---

## Estrutura do Repositório

```
skills/
├── architect/             # Arquiteto SDD
├── design-operator/       # Operador SDD
├── zelador/               # Zelador de binários
│   ├── SKILL.md
│   └── scripts/update-programs.py
├── designcraft/           # Layout/composição
├── gridcraft/             # Grid systems
├── pdfcraft/              # PDF/X export
├── photocraft/            # Imagem/cor
├── vectorcraft/           # Vetores/SVG
├── figcraft/              # Figma sync
├── deckcraft/             # Slides
├── wordcraft/             # Texto .docx
├── craftanything/         # Engenharia reversa + AI
└── design-planner/        # Planejamento auxiliar
```

Cada skill contém:
- `SKILL.md` — definição da skill (prompt para o agente)
- `assets/` — templates (brief.md, plano.md, pacote.md, etc.)
- `references/` — constituição, formato de retorno, exemplos
- `scripts/` — automações CLI (quando aplicável)

> **Binários NÃO estão no repo** — são baixados sob demanda pelo **zelador** para `bin/` e versão salva em `version.txt`.

---

## Primeira Vez / Instalação

### 1. Clone e instale as skills
```bash
git clone https://github.com/pittaya-kun/pittayaskills.git
# Copie as pastas das skills para ~/.claude/skills/
cp -r pittayaskills/skills/* ~/.claude/skills/
```

### 2. Baixe os binários (Zelador)
```bash
# Opção A: Via skill zelador (no chat)
"atualiza os programas"

# Opção B: Direto via script
python3 ~/.claude/skills/zelador/scripts/update-programs.py --update --json
```

O zelador vai:
- Detectar seu OS (macOS/Linux/Windows)
- Baixar o asset correto de cada release no GitHub
- Extrair o binário para `~/.claude/skills/<skill>/bin/`
- Gravar `version.txt` com a versão instalada
- Deixar o zip em `~/programas/<skill>/` para redistribuição

### 3. Verifique
```bash
python3 ~/.claude/skills/zelador/scripts/update-programs.py --check-only --json
```
Todas devem aparecer como `"status": "skipped", "reason": "already_latest"`.

---

## Como Usar

### 1. Iniciar um projeto (Arquiteto)
```
"Quero criar um convite A5 para lançamento de livro, tenho a foto da capa"
→ architect gera brief + plano + pacote da rodada 1
```

### 2. Executar rodada (Operador)
```
Usuário leva pacote.md ao operador
→ design-operator executa tarefas, roda checks, devolve retorno.md
```

### 3. Continuar
```
Usuário leva retorno.md ao arquiteto
→ architect atualiza plano, libera próximo pacote
```

### 4. Atualizar programas (Zelador)
```
"atualiza os programas"
→ zelador roda script, baixa updates, resume o que mudou

"checa updates"
→ só lista o que tem disponível, não baixa

"atualiza craftanything"
→ atualiza só uma skill específica
```

### 5. Programas CLI
Após instalar via zelador, cada CLI fica em `~/.claude/skills/<skill>/bin/`:
```bash
# Exemplo via setup.sh de cada skill
sh ~/.claude/skills/designcraft/scripts/setup.sh
designcraft-cli --help

sh ~/.claude/skills/photocraft/scripts/setup.sh
photocraft-cli convert --cmyk input.jpg output.tif

sh ~/.claude/skills/pdfcraft/scripts/setup.sh
pdfcraft-cli export --pdfx4 layout.indd output.pdf

sh ~/.claude/skills/craftanything/scripts/setup.sh
craft-anything-cli rebuild https://site.com "Recria em React + Tailwind"
```

---

## Princípios SDD

| Princípio | Prática |
|-----------|---------|
| **Brief ≠ Plano** | Brief = o quê/porquê; Plano = como. Mudar método não quebra o brief. |
| **Uma suposição = uma rodada perdida** | Nunca suponha respostas de `abertas`. Pergunte (até 3 por vez). |
| **Pacote = dados, não regras** | Comportamento do operador está em `design-operator` + `constituicao.md`. |
| **Autonomia baixa de propósito** | Usuário aprovou plano e custo. Desvio N1 = correção mínima; N2 = para e pergunta. |
| **Tokens mínimos** | Carrega skill do programa só na tarefa dela. Pacote curto, prefixo estável. |

---

## Licença

MIT