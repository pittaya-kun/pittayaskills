#!/usr/bin/env python3
"""
Update Programs Worker — Deterministic CLI binary updater for SDD ecosystem.

Usage:
    python update-programs.py --check-only [--program NAME] [--json]
    python update-programs.py --update [--program NAME] [--json] [--dry-run]
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import hashlib
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any

# ─── Config ──────────────────────────────────────────────────────────────
SKILLS_DIR = Path(__file__).parent.parent.parent
ROOT_DIR = SKILLS_DIR.parent
PROGRAMAS_DIR = ROOT_DIR / "programas"
UPDATER_CONFIG = SKILLS_DIR / "updater.json"

# Skills que NÃO são programas CLI (ignoradas)
SKIP_SKILLS = {
    "architect",
    "design-operator",
    "design-planner",
    "pittaya-indesign-scripts",
}

# ─── Data Classes ────────────────────────────────────────────────────────
@dataclass
class SkillInfo:
    name: str
    path: Path
    project_url: str
    cli_binary: str
    version_cmd: str
    owner: str
    repo: str

@dataclass
class VersionInfo:
    skill: str
    current: str
    latest: str
    asset_name: str
    asset_url: str
    asset_sha256: Optional[str]

@dataclass
class UpdateResult:
    skill: str
    old_version: str
    new_version: str
    asset_downloaded: str
    binary_path: str
    dist_path: str
    status: str  # "updated" | "skipped" | "error"

@dataclass
class ScriptOutput:
    status: str  # "success" | "partial" | "error"
    platform: str
    updated: List[Dict[str, Any]]
    skipped: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]

# ─── Utilitários ─────────────────────────────────────────────────────────
def log(msg: str, level: str = "INFO", quiet: bool = False):
    if not quiet:
        prefix = {"INFO": "→", "WARN": "⚠", "ERROR": "✗", "OK": "✓", "PROGRESS": "⟳"}.get(level, "•")
        print(f"  {prefix} {msg}", flush=True)

def run_cmd(cmd: List[str], cwd: Path = None, capture: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=capture, text=True, timeout=120)

def parse_frontmatter(skill_md: Path) -> Dict[str, str]:
    """Extrai frontmatter YAML do SKILL.md"""
    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        import yaml
        return yaml.safe_load(parts[1]) or {}
    except Exception:
        # Fallback regex para campos simples
        fm = {}
        for line in parts[1].splitlines():
            m = re.match(r'^(\w+):\s*["\']?([^"\']+)["\']?$', line.strip())
            if m:
                fm[m.group(1)] = m.group(2)
        return fm

def extract_repo_info(project_url: str) -> Optional[tuple]:
    """Extrai owner/repo de URL GitHub"""
    m = re.search(r'github\.com/([^/]+)/([^/]+?)(?:\.git)?$', project_url)
    if m:
        return m.group(1), m.group(2)
    return None

def clean_version(version_str: str) -> str:
    """Extrai apenas a versão semântica (X.Y.Z) de string ruidosa"""
    if not version_str:
        return "0.0.0"
    m = re.search(r'(\d+\.\d+\.\d+)', version_str)
    return m.group(1) if m else version_str.strip()

def get_current_version(skill: SkillInfo) -> str:
    """Detecta versão atual em cascata"""
    # 1. version.txt
    version_file = skill.path / "version.txt"
    if version_file.exists():
        return clean_version(version_file.read_text())
    # 2. binário local
    binary = skill.path / "bin" / skill.cli_binary
    if binary.exists() and binary.is_file():
        try:
            result = run_cmd([str(binary), skill.version_cmd])
            if result.returncode == 0:
                return clean_version(result.stdout)
        except Exception:
            pass
    # 3. pacote em programas/
    dist_dir = PROGRAMAS_DIR / skill.name
    if dist_dir.exists():
        for f in dist_dir.iterdir():
            if f.is_file() and (f.suffix in {".zip", ".gz", ".tar.gz"} or ".tar." in f.name):
                m = re.search(r'[\d]+\.[\d]+\.[\d]+', f.name)
                if m:
                    return m.group(0)
    return "0.0.0"

def get_latest_release(owner: str, repo: str) -> Optional[Dict]:
    """Busca release latest via gh api"""
    try:
        result = run_cmd(["gh", "api", f"repos/{owner}/{repo}/releases/latest"])
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception:
        pass
    return None

def find_matching_asset(release: Dict, platform: str, skill_name: str) -> Optional[Dict]:
    """Encontra asset compatível com o OS atual"""
    assets = release.get("assets", [])
    if not assets:
        return None

    # Padrões por plataforma
    patterns = {
        "darwin": [r"macos-universal\.zip$", r"-macos\.zip$", r"-darwin\.zip$"],
        "linux": [r"linux-x86_64\.tar\.gz$", r"-linux\.tar\.gz$", r"-linux\.tgz$"],
        "win32": [r"windows-x86_64\.zip$", r"-windows\.zip$", r"\.exe$"],
        "cygwin": [r"windows-x86_64\.zip$", r"-windows\.zip$", r"\.exe$"],
    }

    platform_patterns = patterns.get(platform, [])
    if not platform_patterns:
        return None

    # Tenta match exato primeiro
    for asset in assets:
        name = asset.get("name", "")
        for pattern in platform_patterns:
            if re.search(pattern, name, re.IGNORECASE):
                return asset

    # Fallback: primeiro asset que não seja source code
    for asset in assets:
        name = asset.get("name", "").lower()
        if not any(x in name for x in ["source", "src", ".tar.gz", ".zip"] if "source" not in name):
            # heurística fraca
            continue
        return asset

    return None

def verify_checksum(filepath: Path, expected_sha256: str) -> bool:
    """Verifica SHA256 do arquivo"""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest().lower() == expected_sha256.lower()

def download_asset(asset: Dict, dest: Path, quiet: bool = False) -> bool:
    """Baixa asset via gh api (stream)"""
    url = asset.get("browser_download_url")
    if not url:
        return False
    try:
        log(f"Baixando {asset['name']}...", "PROGRESS", quiet)
        # gh api não faz stream direto; usa curl via subprocess
        result = run_cmd(["curl", "-L", "-#", "-o", str(dest), url], capture=False)
        return result.returncode == 0 and dest.exists() and dest.stat().st_size > 0
    except Exception as e:
        log(f"Falha no download: {e}", "ERROR", quiet)
        return False

def extract_asset(asset_path: Path, dest_dir: Path, binary_name: str, quiet: bool = False) -> Optional[Path]:
    """Extrai binário do asset (zip ou tar.gz)"""
    try:
        if asset_path.suffix == ".zip":
            import zipfile
            with zipfile.ZipFile(asset_path, 'r') as zf:
                # Procura o binário dentro do zip
                for name in zf.namelist():
                    if name.endswith(binary_name) or name == binary_name:
                        zf.extract(name, dest_dir)
                        extracted = dest_dir / name
                        if extracted != dest_dir / binary_name:
                            extracted.rename(dest_dir / binary_name)
                        return dest_dir / binary_name
        elif asset_path.suffix in {".gz", ".tgz"} or ".tar." in asset_path.name:
            import tarfile
            with tarfile.open(asset_path, 'r:*') as tf:
                for member in tf.getmembers():
                    if member.name.endswith(binary_name) or os.path.basename(member.name) == binary_name:
                        tf.extract(member, dest_dir)
                        extracted = dest_dir / member.name
                        if extracted != dest_dir / binary_name:
                            extracted.rename(dest_dir / binary_name)
                        return dest_dir / binary_name
        log(f"Binário '{binary_name}' não encontrado no asset", "WARN", quiet)
    except Exception as e:
        log(f"Falha na extração: {e}", "ERROR", quiet)
    return None

def process_skill(skill: SkillInfo, args) -> Dict[str, Any]:
    """Processa uma skill: checa release, compara, baixa se necessário"""
    quiet = getattr(args, 'quiet', False)

    # Versão atual
    current_version = get_current_version(skill)

    # Release latest
    release = get_latest_release(skill.owner, skill.repo)
    if not release:
        return {"skill": skill.name, "status": "error", "error": "no_release", "details": "Nenhum release encontrado"}

    latest_tag = release.get("tag_name", "").lstrip("v")
    if not latest_tag:
        return {"skill": skill.name, "status": "error", "error": "no_tag", "details": "Release sem tag"}

    # Asset compatível
    platform = sys.platform
    asset = find_matching_asset(release, platform, skill.name)
    if not asset:
        return {"skill": skill.name, "status": "error", "error": "no_matching_asset",
                "details": f"Nenhum asset para {platform} no release {latest_tag}"}

    # Compara versões
    if current_version == latest_tag:
        return {"skill": skill.name, "status": "skipped", "version": current_version, "reason": "already_latest"}

    # Modo check-only
    if args.check_only:
        return {"skill": skill.name, "status": "update_available",
                "old_version": current_version, "new_version": latest_tag,
                "asset": asset.get("name")}

    # Baixa asset
    dist_dir = PROGRAMAS_DIR / skill.name
    dist_dir.mkdir(parents=True, exist_ok=True)
    asset_path = dist_dir / asset["name"]

    if not download_asset(asset, asset_path, quiet):
        return {"skill": skill.name, "status": "error", "error": "download_failed"}

    # Checksum se disponível
    asset_sha256 = asset.get("sha256") or asset.get("digest")
    if asset_sha256 and asset_sha256.startswith("sha256:"):
        asset_sha256 = asset_sha256[7:]
    if asset_sha256 and not verify_checksum(asset_path, asset_sha256):
        log(f"Checksum falhou para {asset['name']}", "WARN", quiet)
        asset_path.unlink(missing_ok=True)
        return {"skill": skill.name, "status": "error", "error": "checksum_mismatch"}

    # Extrai binário para skills/<skill>/bin/
    bin_dir = skill.path / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    binary_path = bin_dir / skill.cli_binary

    extracted = extract_asset(asset_path, bin_dir, skill.cli_binary, quiet)
    if not extracted or not extracted.exists():
        return {"skill": skill.name, "status": "error", "error": "binary_not_found",
                "details": f"Binário {skill.cli_binary} não extraído do asset"}

    # Torna executável
    extracted.chmod(0o755)

    # Verifica se binário roda
    test_result = run_cmd([str(extracted), skill.version_cmd])
    if test_result.returncode != 0:
        log(f"Binário extraído não executa: {test_result.stderr}", "WARN", quiet)

    # Remove asset antigo (após sucesso)
    old_assets = list(dist_dir.glob("*"))
    for old in old_assets:
        if old != asset_path:
            old.unlink(missing_ok=True)
            log(f"Removido antigo: {old.name}", "OK", quiet)

    # Grava version.txt
    (skill.path / "version.txt").write_text(latest_tag + "\n")

    log(f"{skill.name}: {current_version} → {latest_tag} ✓", "OK", quiet)

    return {
        "skill": skill.name,
        "status": "updated",
        "old_version": current_version,
        "new_version": latest_tag,
        "asset_downloaded": asset["name"],
        "binary_path": str(binary_path.relative_to(ROOT_DIR)),
        "dist_path": str(asset_path.relative_to(ROOT_DIR))
    }

# ─── Main ────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Update programs CLI binaries")
    parser.add_argument("--check-only", action="store_true", help="Só verifica, não atualiza")
    parser.add_argument("--update", action="store_true", help="Baixa e atualiza (padrão se nem --check-only)")
    parser.add_argument("--program", help="Filtrar só uma skill")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--dry-run", action="store_true", help="Simula sem baixar")
    parser.add_argument("--quiet", action="store_true", help="Menos output visual")
    args = parser.parse_args()

    if not args.check_only and not args.update:
        args.update = True

    # Carrega skills
    skills: List[SkillInfo] = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name in SKIP_SKILLS:
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        fm = parse_frontmatter(skill_md)
        project_url = fm.get("project_url", "").strip()
        if not project_url:
            continue
        repo_info = extract_repo_info(project_url)
        if not repo_info:
            continue
        owner, repo = repo_info
        skills.append(SkillInfo(
            name=skill_dir.name,
            path=skill_dir,
            project_url=project_url,
            cli_binary=fm.get("cli_binary", f"{skill_dir.name}-cli"),
            version_cmd=fm.get("version_cmd", "--version"),
            owner=owner,
            repo=repo,
        ))

    if args.program:
        skills = [s for s in skills if s.name == args.program]
        if not skills:
            print(json.dumps({"status": "error", "errors": [{"skill": args.program, "error": "not_found"}]}))
            return 1

    if not skills:
        print(json.dumps({"status": "success", "updated": [], "skipped": [], "errors": [], "warnings": []}))
        return 0

    # Processa
    updated = []
    skipped = []
    errors = []
    warnings = []

    max_workers = min(4, len(skills))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_skill, s, args): s for s in skills}
        for future in as_completed(futures):
            result = future.result()
            if result["status"] == "updated":
                updated.append(result)
            elif result["status"] == "skipped":
                skipped.append(result)
            elif result["status"] in ("update_available",):
                updated.append(result)  # no check-only, "disponível" entra em updated
            elif result["status"] == "error":
                errors.append(result)
            else:
                warnings.append(result)

    # Warnings para skills sem project_url
    for skill_dir in SKILLS_DIR.iterdir():
        if skill_dir.is_dir() and skill_dir.name in SKIP_SKILLS:
            warnings.append({"skill": skill_dir.name, "reason": "no_project_url"})

    output = ScriptOutput(
        status="success" if not errors else ("partial" if updated else "error"),
        platform=sys.platform,
        updated=updated,
        skipped=skipped,
        errors=errors,
        warnings=warnings
    )

    if args.json:
        print(json.dumps(asdict(output), indent=2, ensure_ascii=False))
    else:
        # Output humano
        print(f"\nPlatform: {sys.platform}")
        print(f"Updated: {len(updated)} | Skipped: {len(skipped)} | Errors: {len(errors)}")
        for u in updated:
            print(f"  ✓ {u['skill']}: {u.get('old_version', '?')} → {u.get('new_version', u.get('new_version', '?'))}")
        for s in skipped:
            print(f"  ○ {s['skill']}: {s.get('version')} ({s.get('reason')})")
        for e in errors:
            print(f"  ✗ {e['skill']}: {e.get('error')} - {e.get('details')}")

    return 0 if not errors else 1

if __name__ == "__main__":
    sys.exit(main())