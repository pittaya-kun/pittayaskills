# AGENTS.md — Guia para LLMs/Agentes: Ecossistema Pittaya Skills

> **Para LLMs lendo este repo:** este documento explica como instalar, configurar e usar o ecossistema SDD de design. Leia completo antes de sugerir instalação ao usuário.

---

## Visão Rápida (TL;DR)

```
┌─────────────────────────────────────────────────────────────┐
│  ECOSSESTEMA SDD (Spec-Driven Development)                   │
├─────────────────────────────────────────────────────────────┤
│  CORE (opcional, gestão)          │  PROGRAMAS (ferramentas) │
│  ├── architect                    │  ├── designcraft         │
│  └── design-operator              │  ├── gridcraft           │
│                                   │  ├── pdfcraft            │
│  INFRA                            │  ├── photocraft          │
│  └── zelador                      │  ├── vectorcraft         │
│                                   │  ├── figcraft            │
│                                   │  ├── deckcraft           │
│                                   │  ├── wordcraft           │
│                                   │  └── craftanything       │
└─────────────────────────────────────────────────────────────┘
```

**Ponto chave:** As **Program Skills + Zelador funcionam 100% independentes** do Core (architect/design-operator). Um usuário pode instalar só os programas + zelador e usar cada CLI direto.

---

## O que cada camada faz

| Camada | Skills | Função | Dependências |
|--------|--------|--------|--------------|
| **Core (SDD)** | `architect`, `design-operator` | Planejamento → execução → retorno → próxima rodada | Requer Program Skills |
| **Programas** | 9 skills (ver tabela) | CLIs de design: layout, imagem, vetor, PDF, slides, texto, planilha, Figma, engenharia reversa | **Zero** — cada uma é autônoma |
| **Infra** | `zelador` | Baixa/atualiza binários cross-platform (macOS/Linux/Windows) | **Zero** — roda sozinho |

---

## Instalação Modular (pergunte ao usuário)

### Opção A — Completa (Core + Programas + Zelador)
```bash
# Para quem quer o fluxo SDD completo: planeja → executa → itera
git clone https://github.com/pittaya-kun/pittayaskills.git
cp -r pittayaskills/skills/* ~/.claude/skills/
python3 ~/.claude/skills/zelador/scripts/update-programs.py --update --json
```
**Use quando:** usuário quer automação de design com planejamento estruturado, brief/plano/pacote, checks automatizados.

### Opção B — Só Programas + Zelador (recomendado p/ maioria)
```bash
# Para quem quer só as ferramentas CLI, sem gestão SDD
git clone https://github.com/pittaya-kun/pittayaskills.git
cp -r pittayaskills/skills/designcraft ~/.claude/skills/
cp -r pittayaskills/skills/gridcraft ~/.claude/skills/
cp -r pittayaskills/skills/pdfcraft ~/.claude/skills/
cp -r pittayaskills/skills/photocraft ~/.claude/skills/
cp -r pittayaskills/skills/vectorcraft ~/.claude/skills/
cp -r pittayaskills/skills/figcraft ~/.claude/skills/
cp -r pittayaskills/skills/deckcraft ~/.claude/skills/
cp -r pittayaskills/skills/wordcraft ~/.claude/skills/
cp -r pittayaskills/skills/craftanything ~/.claude/skills/
cp -r pittayaskills/skills/zelador ~/.claude/skills/
python3 ~/.claude/skills/zelador/scripts/update-programs.py --update --json
```
**Use quando:** usuário quer CLIs de design diretas, sem arquiteto/operador. Cada skill tem `setup.sh` que copia o binário pra `/tmp/<sigla>/`.

### Opção C — Programa único + Zelador
```bash
# Ex: só vectorcraft
cp -r pittayaskills/skills/vectorcraft ~/.claude/skills/
cp -r pittayaskills/skills/zelador ~/.claude/skills/
python3 ~/.claude/skills/zelador/scripts/update-programs.py --update --program vectorcraft --json
```

---

## Como o Zelador funciona (auto-explicativo)

```bash
# Checa updates disponíveis (não baixa)
python3 ~/.claude/skills/zelador/scripts/update-programs.py --check-only --json

# Atualiza tudo
python3 ~/.claude/skills/zelador/scripts/update-programs.py --update --json

# Atualiza só um
python3 ~/.claude/skills/zelador/scripts/update-programs.py --update --program designcraft --json

# Dry-run (simula)
python3 ~/.claude/skills/zelador/scripts/update-programs.py --update --dry-run --json
```

- Detecta `sys.platform` (darwin/linux/win32) → baixa asset correto
- Usa `gh` CLI autenticado (precisa `gh auth login`)
- Extrai binário pra `~/.claude/skills/<skill>/bin/<skill>-cli`
- Grava `version.txt` na skill
- Guarda zip em `~/programas/<skill>/` p/ redistribuição
- **Atômico:** só remove asset antigo após novo baixado + testado

---

## Como usar uma Program Skill (standalone)

Toda program skill segue o mesmo padrão:

```
~/.claude/skills/<skill>/
├── SKILL.md          # Definição (prompt p/ agente)
├── scripts/setup.sh  # Copia bin/ → /tmp/<sigla>/ e roda --version
├── bin/<skill>-cli   # Binário (criado pelo zelador)
└── version.txt       # Versão atual (criado pelo zelador)
```

**Uso direto (sem Core):**
```bash
# 1. Setup (faz uma vez por sessão)
sh ~/.claude/skills/designcraft/scripts/setup.sh
# Cria /tmp/dc/designcraft-cli

# 2. Usa o CLI
/tmp/dc/designcraft-cli --help
/tmp/dc/designcraft-cli new --out doc.designcraft
/tmp/dc/designcraft-cli export doc.designcraft --format pdf --out out.pdf
```

**Via skill (quando agente carrega a skill):**
- A skill `designcraft` já sabe chamar o CLI via `setup.sh`
- Não precisa saber caminho — a skill encapsula

---

## Convenções de Frontmatter (p/ Zelador detectar)

Toda Program Skill **DEVE** ter no `SKILL.md`:

```yaml
---
name: designcraft           # nome da pasta = nome da skill
description: ...
version: 0.17.2
project_url: "https://github.com/storytold/designcraft"  # OBRIGATÓRIO
cli_binary: "designcraft-cli"  # nome do binário dentro do zip
version_cmd: "--version"       # comando p/ extrair versão
---
```

O zelador lê `project_url` → extrai `owner/repo` → busca release latest no GitHub → matcha asset por platform.

---

## Estrutura do Repo (source)

```
skills/
├── AGENTS.md              # ← ESTE ARQUIVO
├── README.md              # Documentação humana
├── architect/             # Core SDD
├── design-operator/       # Core SDD
├── zelador/               # Infra
│   ├── SKILL.md
│   └── scripts/update-programs.py
├── designcraft/           # Programa
├── gridcraft/
├── pdfcraft/
├── photocraft/
├── vectorcraft/
├── figcraft/
├── deckcraft/
├── wordcraft/
├── craftanything/
└── design-planner/        # Suporte (auxiliar)
```

**NÃO estão no repo:** `bin/`, `version.txt`, zips — gerados pelo zelador.

---

## Checklist para LLM sugerir instalação

- [ ] Perguntou: "Quer o fluxo SDD completo (architect + operator) ou só as ferramentas CLI?"
- [ ] Explicou que programas + zelador funcionam **sem** architect/operator
- [ ] Mostrou comando de instalação modular (Opção A, B ou C)
- [ ] Avisou que precisa `gh auth login` pro zelador baixar releases
- [ ] Confirmou que binários ficam em `~/.claude/skills/<skill>/bin/` (não no repo)
- [ ] Deixou claro: cada skill é autônoma, pode instalar só a que precisa

---

## Exemplos de uso por camada

### Só Programas (sem Core)
> Usuário: "Converte esta imagem pra CMYK"
> → LLM carrega skill `photocraft` → roda `photocraft-cli convert --cmyk in.jpg out.tif`

### Com Core (SDD completo)
> Usuário: "Quero criar um convite A5, tenho a foto da capa"
> → `architect` gera brief + plano + pacote
> → `design-operator` executa: `photocraft` pra tratar foto, `designcraft` pra layout, `pdfcraft` pra export
> → Retorna `retorno.md` → próxima rodada

### Engenharia reversa (craftanything)
> Usuário: "Recria este site em React + Tailwind"
> → `craftanything` → `craft-anything-cli rebuild https://site.com "Recria em React + Tailwind"`

---

## Notas para LLM

- **Não assuma** que o usuário quer o Core. A maioria quer só ferramentas.
- **Sempre pergunte** qual nível de instalação (A/B/C acima).
- **O zelador é opcional mas recomendado** — sem ele, binários não existem.
- **Skills não se comunicam** entre si — o Core (architect/operator) orquestra; standalone, cada uma é isolada.
- **Setup.sh** é idempotente — pode rodar múltiplas vezes.
- **Binários são grandes** (50-100MB cada) — por isso não estão no repo.

---

## Atualizando este guia

Se o ecossistema mudar (novas skills, mudança no zelador, etc.), atualize este `AGENTS.md` junto. Ele é a "interface" pros agentes futuros.

---

*Este arquivo segue a convenção `AGENTS.md` para documentação consumível por agentes de código/LLMs. Veja também `README.md` para documentação humana.*