# Pittaya Skills — Ecossistema SDD de Design

Coleção de skills para automação de design baseada em **SDD (Spec-Driven Development)**: planejamento → pacote → operação → retorno → próximo pacote.

## Visão Geral do Ecossistema

```
┌─────────────────────┐     pacote.md     ┌──────────────────────┐
│   PLANEJADOR        │ ─────────────────▶ │    OPERADOR         │
│   (sdd-handoff)     │                    │  (design-operator)   │
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
```

### Fluxo Principal

1. **Planejador** (`sdd-handoff`) — Conversa com o usuário, gera:
   - `brief.md` — objetivo, entregáveis, critérios de aceite, perguntas abertas
   - `plano.md` — tarefas sequenciais com dependências, custo estimado, checks
   - `pacote.md` — tarefas da rodada atual (dependências satisfeitas)

2. **Operador** (`design-operator`) — Recebe o pacote, executa:
   - Abre só a skill do programa necessário por tarefa
   - Roda comando/script + check automatizado
   - Aplica política de desvio (N1 = correção mínima, N2 = para e pergunta)
   - Devolve `retorno.md` curto

3. **Próxima rodada** — Planejador lê retorno, atualiza plano, libera próximo pacote

---

## Skills do Ecossistema

### Core (SDD)
| Skill | Papel |
|-------|-------|
| `sdd-handoff` | Planejador — converte conversa em brief/plano/pacote |
| `design-operator` | Operador — executa pacote, verifica checks, devolve retorno |

### Program Skills (ferramentas que o operador chama)
| Skill | Função | Programa CLI |
|-------|--------|--------------|
| `designcraft` | Layout, composição, tipografia | `designcraft` |
| `gridcraft` | Sistemas de grid, alinhamento | `gridcraft` |
| `pdfcraft` | Manipulação/export PDF/X | `pdfcraft` |
| `photocraft` | Tratamento de imagem, cor | `photocraft` |
| `vectorcraft` | Vetores, SVG, ilustração | `vectorcraft` |
| `vectorcraft-bin` | Binários/fonts do Vectorcraft | — |
| `figcraft` | Sync com Figma | `figcraft` |
| `deckcraft` | Apresentações/slides | `deckcraft` |

### Suporte
| Skill | Função |
|-------|--------|
| `design-planner` | Planejamento auxiliar de design |

> **Nota:** `pittaya-indesign-scripts` **não** faz parte deste ecossistema — é um conjunto separado de scripts para Adobe InDesign.

---

## Estrutura do Repositório

```
skills/
├── sdd-handoff/           # Planejador SDD
├── design-operator/       # Operador SDD
├── designcraft/           # Layout/composição
├── gridcraft/             # Grid systems
├── pdfcraft/              # PDF/X export
├── photocraft/            # Imagem/cor
├── vectorcraft/           # Vetores/SVG
├── vectorcraft-bin/       # Assets do Vectorcraft
├── figcraft/              # Figma sync
├── deckcraft/             # Slides
└── design-planner/        # Planejamento auxiliar
```

Cada skill contém:
- `SKILL.md` — definição da skill (prompt para o agente)
- `assets/` — templates (brief.md, plano.md, pacote.md, etc.)
- `references/` — constituição, formato de retorno, exemplos
- `scripts/` — automações CLI (quando aplicável)

---

## Como Usar

### 1. Iniciar um projeto (Planejador)
```
"Quero criar um convite A5 para lançamento de livro, tenho a foto da capa"
→ sdd-handoff gera brief + plano + pacote da rodada 1
```

### 2. Executar rodada (Operador)
```
Usuário leva pacote.md ao operador
→ design-operator executa tarefas, roda checks, devolve retorno.md
```

### 3. Continuar
```
Usuário leva retorno.md ao planejador
→ sdd-handoff atualiza plano, libera próximo pacote
```

### 4. Programas CLI
Cada program skill expõe um CLI instalável via `programas/` (versões Mac + Linux):
```bash
designcraft --help
photocraft convert --cmyk input.jpg output.tif
pdfcraft export --pdfx4 layout.indd output.pdf
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

## Instalação das Skills

No Claude Code:
```bash
# Cada skill é uma pasta em .claude/agents/ ou carregada via skill system
# Consulte a documentação de cada skill em skills/<nome>/
```

## Licença

MIT