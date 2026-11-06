# AGENTS.md — Pittaya Skills Ecosystem (LLM-Optimized)

## ECOSYSTEM_META
```yaml
name: "pittaya-skills"
type: "sdd-design-automation"
version: "2026-11"
repo: "https://github.com/pittaya-kun/pittayaskills.git"
license: "MIT"
```

## LAYER_DEFINITIONS
```yaml
layers:
  - id: core
    skills: [architect, design-operator]
    role: "sdd-orchestration"
    depends_on: [programs]
    optional: true
    description: "Brief→Plano→Pacote→Operador→Retorno loop"

  - id: programs
    skills:
      - designcraft   # layout/composition/typography
      - gridcraft     # grid systems/alignment
      - pdfcraft      # PDF/X export/manipulation
      - photocraft    # image processing/color
      - vectorcraft   # vectors/SVG/illustration
      - figcraft      # Figma-style design collab
      - deckcraft     # presentations/slides
      - wordcraft     # .docx text processing
      - craftanything # reverse-engineering + AI recreation
    role: "cli-tools"
    depends_on: []
    optional: false
    standalone: true
    each:
      provides: "CLI binary via zelador"
      pattern: "setup.sh → /tmp/<sigla>/<cli>"

  - id: infra
    skills: [zelador]
    role: "binary-management"
    depends_on: []
    optional: false
    standalone: true
    provides: "cross-platform binary downloader/updater"
```

## INSTALLATION_MATRIX
```yaml
options:
  A_full:
    label: "Core + Programs + Zelador"
    use_when: "user wants SDD workflow (brief→plan→execute→iterate)"
    commands:
      - "git clone https://github.com/pittaya-kun/pittayaskills.git"
      - "cp -r pittayaskills/skills/* ~/.claude/skills/"
      - "python3 ~/.claude/skills/zelador/scripts/update-programs.py --update --json"

  B_programs_only:
    label: "Programs + Zelador (recommended default)"
    use_when: "user wants CLI design tools without SDD orchestration"
    commands:
      - "git clone https://github.com/pittaya-kun/pittayaskills.git"
      - "for s in designcraft gridcraft pdfcraft photocraft vectorcraft figcraft deckcraft wordcraft craftanything zelador; do cp -r pittayaskills/skills/$s ~/.claude/skills/; done"
      - "python3 ~/.claude/skills/zelador/scripts/update-programs.py --update --json"

  C_single:
    label: "Single Program + Zelador"
    use_when: "user needs only one specific tool"
    template:
      - "git clone https://github.com/pittaya-kun/pittayaskills.git"
      - "cp -r pittayaskills/skills/<SKILL_NAME> ~/.claude/skills/"
      - "cp -r pittayaskills/skills/zelador ~/.claude/skills/"
      - "python3 ~/.claude/skills/zelador/scripts/update-programs.py --update --program <SKILL_NAME> --json"

decision_required: true
prompt_user: "Choose installation: A (full SDD), B (tools only), or C (single tool)?"
```

## ZELADOR_API
```yaml
script: "~/.claude/skills/zelador/scripts/update-programs.py"
requires: ["gh auth login", "python3", "curl"]
platform_detection: "sys.platform (darwin|linux|win32|cygwin)"
asset_matching:
  darwin: ["macos-universal.zip", "-macos.zip", "-darwin.zip"]
  linux:  ["linux-x86_64.tar.gz", "-linux.tar.gz", "-linux.tgz"]
  win32:  ["windows-x86_64.zip", "-windows.zip", ".exe"]
commands:
  check:    "--check-only --json"
  update:   "--update --json"
  single:   "--update --program <NAME> --json"
  dry_run:  "--update --dry-run --json"
output_schema:
  status: "success|partial|error"
  platform: "string"
  updated:  "[{skill, old_version, new_version, asset_downloaded, binary_path, dist_path}]"
  skipped:  "[{skill, version, reason}]"
  errors:   "[{skill, error, details}]"
  warnings: "[{skill, reason}]"
behavior:
  atomic: true
  cleanup_old_after_verify: true
  verify_checksum: true
  parallel_downloads: 4
```

## PROGRAM_SKILL_CONTRACT
```yaml
required_frontmatter:
  name: "folder_name"
  project_url: "https://github.com/owner/repo"
  cli_binary: "binary-name"
  version_cmd: "--version"
directory_structure:
  ~/.claude/skills/<skill>/
    SKILL.md          # agent prompt definition
    scripts/setup.sh  # copies bin/ → /tmp/<sigla>/ ; runs --version
    bin/<cli>         # created by zelador
    version.txt       # created by zelador
setup_sh_pattern:
  - "DIR=$(cd $(dirname $0)/.. && pwd)"
  - "OUT=/tmp/<sigla>"
  - "mkdir -p $OUT"
  - "cp -f $DIR/bin/<cli> $OUT/<cli>"
  - "chmod +x $OUT/<cli>"
  - "$OUT/<cli> --version | head -1"
usage_standalone:
  - "sh ~/.claude/skills/<skill>/scripts/setup.sh"
  - "/tmp/<sigla>/<cli> <command>"
usage_via_agent: "agent loads skill → skill invokes setup.sh internally"
```

## FRONTMATTER_REGISTRY
```yaml
skills:
  designcraft:   {project_url: "https://github.com/storytold/designcraft",   cli_binary: "designcraft-cli",   version_cmd: "--version"}
  gridcraft:     {project_url: "https://github.com/storytold/gridcraft",     cli_binary: "gridcraft-cli",     version_cmd: "--version"}
  pdfcraft:      {project_url: "https://github.com/storytold/pdfcraft",      cli_binary: "pdfcraft-cli",      version_cmd: "--version"}
  photocraft:    {project_url: "https://github.com/storytold/photocraft",    cli_binary: "photocraft-cli",    version_cmd: "--version"}
  vectorcraft:   {project_url: "https://github.com/storytold/vectorcraft",   cli_binary: "vectorcraft-cli",   version_cmd: "--version"}
  figcraft:      {project_url: "https://github.com/storytold/figcraft",      cli_binary: "figcraft-cli",      version_cmd: "--version"}
  deckcraft:     {project_url: "https://github.com/storytold/deckcraft",     cli_binary: "deckcraft-cli",     version_cmd: "--version"}
  wordcraft:     {project_url: "https://github.com/storytold/wordcraft",     cli_binary: "wordcraft-cli",     version_cmd: "--version"}
  craftanything: {project_url: "https://github.com/storytold/craft-anything", cli_binary: "craft-anything-cli", version_cmd: "--version"}
  architect:     {project_url: null, cli_binary: null, version_cmd: null}  # core, no binary
  design-operator: {project_url: null, cli_binary: null, version_cmd: null} # core, no binary
  design-planner:  {project_url: null, cli_binary: null, version_cmd: null} # support, no binary
  zelador:       {project_url: null, cli_binary: null, version_cmd: null}  # infra, no binary
  pittaya-indesign-scripts: {project_url: null, cli_binary: null, version_cmd: null} # external
```

## AGENT_DECISION_TREE
```
ON_REPO_DISCOVERY:
  1. READ this AGENTS.md
  2. PARSE LAYER_DEFINITIONS, INSTALLATION_MATRIX
  3. ASK_USER: installation_option (A|B|C) + target_skills[]
  4. EXECUTE commands from INSTALLATION_MATRIX[option]
  5. RUN zelador check → confirm all latest
  6. CONFIRM ready

ON_USER_REQUEST:
  IF request ∈ [design, layout, image, vector, pdf, slides, doc, spreadsheet, figma, reverse-engineer]:
    IF skill_installed(request):
      USE skill directly (standalone or via core)
    ELSE:
      SUGGEST install option B or C for that skill
  IF request ∈ [plan, architect, brief, orchestrate]:
    REQUIRE core (architect + design-operator) + programs
    SUGGEST option A
  IF request == "update" OR "check versions":
    RUN zelador API

ON_ERROR:
  zelador errors → present to user with fallback options (per ZELADOR_API.output_schema.errors)
  missing binary → run zelador update for that skill
  gh auth missing → instruct "gh auth login"
```

## REPO_STRUCTURE
```
skills/
├── AGENTS.md           # THIS FILE
├── README.md           # human docs
├── architect/          # core
├── design-operator/    # core
├── zelador/            # infra
│   ├── SKILL.md
│   └── scripts/update-programs.py
├── designcraft/        # program
├── gridcraft/
├── pdfcraft/
├── photocraft/
├── vectorcraft/
├── figcraft/
├── deckcraft/
├── wordcraft/
├── craftanything/
└── design-planner/     # support
NOT_IN_REPO: bin/, version.txt, *.zip (generated by zelador)
```

## KEY_INVARIANTS
- Programs + Zelador = fully functional WITHOUT Core
- Each Program Skill = autonomous, zero dependencies
- Zelador = single source of truth for binaries
- Binaries never in repo (too large, platform-specific)
- Frontmatter `project_url` = required for zelador auto-detection
- `gh` CLI = required for zelador (GitHub API auth)
- Setup.sh = idempotent, safe to re-run

## CHANGELOG
- 2026-11: Added craftanything, renamed updater→zelador, removed binaries from repo, added AGENTS.md

---

#PARSE_HINT: This file uses YAML code blocks for structured data. Extract LAYER_DEFINITIONS, INSTALLATION_MATRIX, ZELADOR_API, PROGRAM_SKILL_CONTRACT, FRONTMATTER_REGISTRY, AGENT_DECISION_TREE for programmatic use.