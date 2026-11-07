# ECOSYSTEM_TEMPLATE.md — Template de Organização de Projetos Multi-Skill

> **Objetivo**: Estrutura replicável para ecossistemas de skills/ferramentas com versionamento cross-platform, documentação dual (humano + LLM), e instalação modular.

---

## 1. ESTRUTURA DE DIRETÓRIOS (padrão)

```
<project-root>/
├── AGENTS.md           # Documentação para LLMs/agentes (YAML-structured)
├── README.md           # Documentação para humanos
├── .gitignore          # Ignora bin/, version.txt, .DS_Store, .bugs/
├── <config>.json       # Configs compartilhadas (ex: updater.json, zelador.json)
├── skills/             # OU agents/, plugins/, tools/ — pasta principal
│   ├── core/           # Orquestração (opcional)
│   │   ├── <planner>/  # Ex: architect, planner
│   │   └── <executor>/ # Ex: design-operator, runner
│   ├── programs/       # Ferramentas autônomas (zero deps entre si)
│   │   ├── <tool-1>/
│   │   ├── <tool-2/>
│   │   └── ...
│   ├── infra/          # Infraestrutura compartilhada
│   │   └── <manager>/  # Ex: zelador, updater, sync
│   └── support/        # Auxiliares (opcional)
│       └── <helper>/
├── programas/          # Distribuição de binários (local, ignorado no git)
│   ├── <tool-1>/
│   └── ...
└── .bugs/              # Relatórios de bug (agent-facing, local only)
```

**Regra**: `skills/` = source of truth. `~/.claude/skills/` (ou equivalent) = instalado (cópia, não link).

---

## 2. CONVENÇÃO DE SKILL (padrão obrigatório)

Cada skill em `skills/<name>/` **DEVE** ter:

```
skills/<name>/
├── SKILL.md            # Definição completa (frontmatter + prompt)
├── scripts/
│   └── setup.sh        # Idempotente: copia bin/ → /tmp/<sigla>/ ; roda --version
├── bin/                # Gitignored — binários locais
├── version.txt         # Gitignored — versão instalada (gerado pelo manager)
├── assets/             # Templates (brief.md, plano.md, etc.) — opcional
└── references/         # Constituição, exemplos, schemas — opcional
```

### Frontmatter Obrigatório (SKILL.md)

```yaml
---
name: <folder-name>           # Deve igualar nome da pasta
description: <one-line>       # Para indexação/descoberta
version: <semver>             # Versão da skill (não do binary)
project_url: "https://github.com/owner/repo"  # OBRIGATÓRIO se tem binary
cli_binary: "<name>-cli"      # Nome do binário dentro do zip
version_cmd: "--version"      # Comando para extrair versão
---
```

**Skills sem binary** (core, support, infra): `project_url: null`, `cli_binary: null`, `version_cmd: null`.

---

## 3. MANAGER DE BINÁRIOS (Zelador/Updater)

### Responsabilidades
- Descoberta dinâmica de skills via `project_url` no frontmatter
- Busca release latest no GitHub (via `gh` CLI)
- Match de asset por platform (`sys.platform`)
- Download → extração → teste → atomicidade → cleanup
- Grava `version.txt` + mantém zip em `programas/<skill>/`

### Interface (CLI padrão)
```bash
# Checa updates
python <manager>/scripts/update.py --check-only --json

# Atualiza todos
python <manager>/scripts/update.py --update --json

# Atualiza um
python <manager>/scripts/update.py --update --program <name> --json

# Dry-run
python <manager>/scripts/update.py --update --dry-run --json
```

### Output Schema (JSON)
```yaml
status: "success|partial|error"
platform: "darwin|linux|win32|cygwin"
updated:  "[{skill, old_version, new_version, asset_downloaded, binary_path, dist_path}]"
skipped:  "[{skill, version, reason}]"
errors:   "[{skill, error, details}]"
warnings: "[{skill, reason}]"
```

### Asset Matching (padrão)
```yaml
darwin:  ["macos-universal.zip", "-macos.zip", "-darwin.zip"]
linux:   ["linux-x86_64.tar.gz", "-linux.tar.gz", "-linux.tgz"]
win32:   ["windows-x86_64.zip", "-windows.zip", ".exe"]
cygwin:  ["windows-x86_64.zip", "-windows.zip", ".exe"]
```
**Override**: `<config>.json` com `asset_patterns` por skill se naming for não-padrão.

---

## 4. AGENTS.md (Documentação para LLMs)

**Princípio**: Estruturado para parsing programático, não leitura humana.

### Blocos Obrigatórios (YAML code blocks)

| Bloco | Conteúdo |
|-------|----------|
| `ECOSYSTEM_META` | name, type, version, repo, license |
| `LAYER_DEFINITIONS` | layers: id, skills[], role, depends_on, optional, standalone |
| `INSTALLATION_MATRIX` | options A/B/C com commands[] + decision_required + prompt_user |
| `MANAGER_API` | script, requires, platform_detection, asset_matching, commands{}, output_schema, behavior |
| `SKILL_CONTRACT` | required_frontmatter, directory_structure, setup_sh_pattern, usage |
| `FRONTMATTER_REGISTRY` | Mapeamento completo skill → {project_url, cli_binary, version_cmd} |
| `AGENT_DECISION_TREE` | ON_REPO_DISCOVERY, ON_USER_REQUEST, ON_ERROR (pseudo-código) |
| `REPO_STRUCTURE` | Tree ASCII + NOT_IN_REPO list |
| `KEY_INVARIANTS` | Lista de verdades imutáveis do ecossistema |

### PARSE_HINT
```markdown
#PARSE_HINT: Extract LAYER_DEFINITIONS, INSTALLATION_MATRIX, MANAGER_API, 
SKILL_CONTRACT, FRONTMATTER_REGISTRY, AGENT_DECISION_TREE for programmatic use.
```

---

## 5. README.md (Documentação Humana)

**Estrutura mínima**:
1. Visão geral + diagrama ASCII do ecossistema
2. Fluxo principal (passos numerados)
3. Tabela de skills por camada (Core | Programs | Infra | Support)
4. Estrutura do repositório
5. **Primeira Vez / Instalação** (comandos copy-paste)
6. Como usar (por camada: standalone vs orquestrado)
7. Princípios/filosofia
8. Licença

---

## 6. .gitignore (Padrão)

```gitignore
# Binários locais (gerados pelo manager)
**/bin/

# Versões instaladas (geradas pelo manager)
**/version.txt

# macOS metadata
**/.DS_Store

# Relatórios de bug (agent-facing, local only)
.bugs/

# Projetos/skills externos não parte do ecossistema
<external-folder>/

# Configs locais sensíveis (se houver)
*.local.json
.local.env
```

---

## 7. BUG TRACKING (.bugs/)

**Local-only**, agent-facing, não commitado.

```
.bugs/
├── <skill-name>/
│   ├── <bug-id>.md       # Relatório estruturado
│   └── ...
└── index.json            # Índice para busca rápida
```

### Formato de Bug Report (markdown + frontmatter)
```markdown
---
id: "BUG-<skill>-<timestamp>"
skill: <skill-name>
severity: "critical|high|medium|low"
status: "open|investigating|fixed|wontfix"
created: "ISO8601"
updated: "ISO8601"
tags: ["binary", "platform", "asset-match", "checksum", "permission"]
---

## Summary
<one-line>

## Reproduction
```bash
<commands to reproduce>
```

## Expected vs Actual
- Expected: ...
- Actual: ...

## Context
- Platform: `sys.platform`
- Skill version: `version.txt`
- Binary version: `<cli> --version`
- Manager output: `<json snippet>`

## Investigation
<notes>

## Fix
<resolution or workaround>
```

---

## 8. INSTALAÇÃO MODULAR (3 Níveis)

| Nível | Comando Base | Para Quem |
|-------|--------------|-----------|
| **A: Completo** | `cp -r skills/* <target>/` | Quer orquestração SDD completa |
| **B: Tools Only** | `for s in <list>; do cp -r skills/$s <target>/; done` | Quer só CLIs (padrão) |
| **C: Single** | `cp -r skills/<name> <target>/` | Precisa de uma ferramenta só |

**Sempre**: `cp -r skills/<manager> <target>/` + `python <manager>/scripts/update.py --update --json`

---

## 9. CHECKLIST DE REPLICAÇÃO (para novo projeto)

### Setup Inicial
- [ ] Criar estrutura `skills/{core,programs,infra,support}/`
- [ ] Definir `LAYER_DEFINITIONS` no AGENTS.md
- [ ] Criar `README.md` com diagrama + instalação
- [ ] Configurar `.gitignore` com padrões acima
- [ ] Criar manager (copiar zelador + adaptar `asset_patterns` se needed)

### Por Skill
- [ ] Pasta `skills/<name>/` com SKILL.md (frontmatter completo)
- [ ] `scripts/setup.sh` idempotente
- [ ] `bin/` vazio (gitignored)
- [ ] Testar: `sh scripts/setup.sh` → roda `--version`

### Manager
- [ ] `project_url` aponta pro repo correto no GitHub
- [ ] Releases têm assets com naming padrão (ou override no config)
- [ ] `gh auth login` funciona
- [ ] Testar: `--check-only --json` → lista skills
- [ ] Testar: `--update --json` → baixa + extrai + testa

### Documentação
- [ ] `AGENTS.md` com todos blocos YAML preenchidos
- [ ] `README.md` humano completo
- [ ] `FRONTMATTER_REGISTRY` sincronizado com skills reais

### Validação Final
- [ ] `git status` limpo (só .gitignore, docs, skills)
- [ ] Clone limpo → instalação A/B/C → zelador → tudo `already_latest`
- [ ] Skill standalone funciona: `setup.sh` → `/tmp/<sigla>/<cli> --help`

---

## 10. O QUE IGNORAR EM PROJETOS PARALELOS

| Item | Replicar? | Nota |
|------|-----------|------|
| Estrutura `skills/` | ✅ Sempre | Adapte camadas conforme necessidade |
| Convenção SKILL.md + frontmatter | ✅ Sempre | Contrato do manager |
| Manager (zelador) | ✅ Sempre | Copie + ajuste `asset_patterns` |
| AGENTS.md (estrutura YAML) | ✅ Sempre | Preencha blocos pro projeto |
| README.md (estrutura) | ✅ Sempre | Reescreva conteúdo |
| .gitignore | ✅ Sempre | Adicione pastas externas do projeto |
| .bugs/ | ✅ Sempre | Local-only |
| Skills específicas (designcraft, etc.) | ❌ Não | São do domínio "design" |
| `programas/` (distribuição) | ⚠️ Opcional | Se quiser redistribuir binários |
| `assets/` templates | ⚠️ Opcional | Se o domínio precisar |
| `references/` | ⚠️ Opcional | Se houver constituição/schemas |

---

## 11. ECOSYSTEM SENSE (Manter coerência entre projetos)

### Princípios Compartilhados
1. **Skills autônomas** — zero deps entre programs
2. **Manager único** — single source of truth para binários
3. **Instalação por cópia** — nunca symlink, nunca link
4. **Documentação dual** — AGENTS.md (machine) + README.md (human)
5. **Gitignore first** — bin/, version.txt, .bugs/ sempre ignorados
5. **Frontmatter = contrato** — manager lê, não adivinha
6. **Modularidade real** — usuário instala só o que precisa

### Sync de Melhorias
Quando melhorar o template (ex: novo padrão no manager, bloco novo no AGENTS.md):
1. Atualiza `ECOSYSTEM_TEMPLATE.md` (este arquivo)
2. Aplica no projeto ativo
3. Propaga pros outros projetos na próxima manutenção

---

## 12. QUICK START (Novo Projeto em 5 min)

```bash
# 1. Clone template base (ou copie pasta skills/ vazia com estrutura)
mkdir -p meu-projeto/skills/{core,programs,infra,support}
cd meu-projeto

# 2. Copie manager (zelador) + adapte asset_patterns se needed
cp -r /path/to/template/skills/infra/zelador skills/infra/

# 3. Crie AGENTS.md com LAYER_DEFINITIONS do seu projeto
#    (copie template, preencha skills reais)

# 4. Crie README.md seguindo estrutura

# 5. Configure .gitignore

# 6. Para cada skill: mkdir skills/programs/<name>; crie SKILL.md + setup.sh

# 7. Teste: git clone → instalação B → zelador update → verify
```

---

## CHANGELOG DO TEMPLATE

| Data | Versão | Mudança |
|------|--------|---------|
| 2026-11 | 1.0 | Estrutura base: skills/, zelador, AGENTS.md, README.md, .gitignore, .bugs/ |
| 2026-11 | 1.1 | Adicionado: asset_patterns override, FRONTMATTER_REGISTRY, INSTALLATION_MATRIX, PARSE_HINT |

---

*Este template vive em `<project-root>/ECOSYSTEM_TEMPLATE.md` e deve ser versionado junto ao projeto. Para projetos novos, copie e adapte.*